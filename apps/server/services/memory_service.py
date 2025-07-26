from typing import List, Dict, Any, Optional
from utils.database import DatabaseManager
from utils.logger import logger
import json


class MemoryService:
    def __init__(self):
        # Remove in-memory storage - now everything is persisted in database
        self.max_short_term_messages = 10

    async def get_chat_history(
        self, chat_id: str, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get chat history from database (long-term memory)"""
        try:

            async def operation(db):
                messages = await db.message.find_many(
                    where={"chatId": chat_id},
                    order={"createdAt": "desc"},
                    take=limit,
                    skip=offset,
                    include={"documents": {"include": {"file": True}}},
                )
                
                count = await db.message.count(where={"chatId": chat_id})

                # Reverse to get chronological order
                messages.reverse()

                formatted_messages = []
                for message in messages:
                    formatted_message = {
                        "id": message.id,
                        "content": message.content,
                        "role": message.role,
                        "created_at": message.createdAt.isoformat(),
                        "retrieved_chunks": message.retrievedChunks,
                        "grounding_score": message.groundingScore,
                        "rag_metadata": message.ragMetadata,
                        "response_time": message.responseTime,
                        "documents": (
                            [
                                {
                                    "id": doc.id,
                                    "title": doc.title,
                                    "language": doc.language,
                                    "file_name": (
                                        doc.file.fileName if doc.file else None
                                    ),
                                }
                                for doc in message.documents
                            ]
                            if message.documents
                            else []
                        ),
                    }
                    formatted_messages.append(formatted_message)

                return {
                    "messages": formatted_messages,
                    "count": count,
                }

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error getting chat history for chat {chat_id}: {str(e)}")
            raise

    async def get_short_term_memory(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get short-term memory for a chat session from database"""
        try:

            async def operation(db):
                chat = await db.chat.find_unique(where={"id": chat_id})

                if not chat or not chat.shortTermMemory:
                    return []

                # Parse JSON to list if it's stored as JSON string
                if isinstance(chat.shortTermMemory, str):
                    try:
                        return json.loads(chat.shortTermMemory)
                    except json.JSONDecodeError:
                        logger.warning(
                            f"Invalid JSON in shortTermMemory for chat {chat_id}"
                        )
                        return []
                elif isinstance(chat.shortTermMemory, list):
                    return chat.shortTermMemory
                else:
                    # If it's already a dict/object, return as list
                    return [chat.shortTermMemory] if chat.shortTermMemory else []

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(
                f"Error getting short-term memory for chat {chat_id}: {str(e)}"
            )
            return []

    async def update_short_term_memory(self, chat_id: str, message: Dict[str, Any]):
        """Update short-term memory in database with new message"""
        try:
            # Get current short-term memory
            current_memory = await self.get_short_term_memory(chat_id)

            # Add new message
            current_memory.append(message)

            # Keep only recent messages
            if len(current_memory) > self.max_short_term_messages:
                current_memory = current_memory[-self.max_short_term_messages :]

            # Update in database - store as JSON
            async def operation(db):
                await db.chat.update(
                    where={"id": chat_id},
                    data={"shortTermMemory": json.dumps(current_memory)},
                )
                return current_memory

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(
                f"Error updating short-term memory for chat {chat_id}: {str(e)}"
            )

    async def clear_short_term_memory(self, chat_id: str):
        """Clear short-term memory for a chat session in database"""
        try:

            async def operation(db):
                await db.chat.update(
                    where={"id": chat_id}, data={"shortTermMemory": json.dumps([])}
                )

            await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(
                f"Error clearing short-term memory for chat {chat_id}: {str(e)}"
            )

    async def create_chat_session(
        self, user_id: str, first_query: str
    ) -> Dict[str, Any]:
        """Create a new chat session with an appropriate title"""
        try:
            # Generate a concise title from the first query
            title = self._generate_chat_title(first_query)

            async def operation(db):
                # Create chat using the userId directly (not profile.id)
                chat = await db.chat.create(
                    data={
                        "name": title,
                        "userId": user_id,
                    }
                )

                return {
                    "id": chat.id,
                    "name": chat.name,
                    "created_at": chat.createdAt.isoformat(),
                    "user_id": chat.userId,
                }

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error creating chat session: {str(e)}")
            raise

    def _generate_chat_title(self, query: str) -> str:
        """Generate a concise title from the first query"""
        # Remove extra whitespace and limit length
        cleaned_query = " ".join(query.strip().split())

        # If query is too long, take first few words
        words = cleaned_query.split()
        if len(words) > 6:
            title = " ".join(words[:6]) + "..."
        else:
            title = cleaned_query

        # Limit to 50 characters
        if len(title) > 50:
            title = title[:47] + "..."

        return title

    async def store_message(
        self,
        chat_id: str,
        content: str,
        role: str,
        retrieved_chunks: Optional[List[Dict]] = None,
        grounding_score: Optional[float] = None,
        document_ids: Optional[List[str]] = None,
        rag_metadata: Optional[Dict[str, Any]] = None,
        response_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Store message in database (long-term memory)"""
        try:

            async def operation(db):
                message_data = {"content": content, "chatId": chat_id, "role": role}

                if retrieved_chunks:
                    message_data["retrievedChunks"] = retrieved_chunks

                if grounding_score is not None:
                    message_data["groundingScore"] = grounding_score

                if rag_metadata is not None:
                    message_data["ragMetadata"] = (
                        json.dumps(rag_metadata) if rag_metadata else "{}"
                    )

                if response_time is not None:
                    message_data["responseTime"] = response_time

                message = await db.message.create(data=message_data)

                # Connect documents if provided
                if document_ids:
                    for doc_id in document_ids:
                        await db.document.update(
                            where={"id": doc_id}, data={"messageId": message.id}
                        )

                return {
                    "id": message.id,
                    "content": message.content,
                    "role": message.role,
                    "created_at": message.createdAt.isoformat(),
                    "chat_id": message.chatId,
                }

            result = await DatabaseManager.execute(operation)

            # Update short-term memory asynchronously
            await self.update_short_term_memory(
                chat_id,
                {
                    "id": result["id"],
                    "content": content,
                    "role": role,
                    "retrieved_chunks": retrieved_chunks,
                    "grounding_score": grounding_score,
                    "rag_metadata": rag_metadata,
                    "response_time": response_time,
                },
            )

            return result

        except Exception as e:
            logger.error(f"Error storing message: {str(e)}")
            raise

    async def get_relevant_context(
        self, chat_id: str, current_query: str
    ) -> Dict[str, Any]:
        """Get relevant context combining short-term and long-term memory"""
        try:
            # Get short-term memory (recent messages in current session)
            short_term = await self.get_short_term_memory(chat_id)

            # Get recent chat history from database
            long_term = await self.get_chat_history(chat_id, limit=5)

            # Combine and format context - return recent messages for conversation context
            recent_messages = short_term + [
                {
                    "id": msg["id"],
                    "content": msg["content"],
                    "role": msg["role"],
                    "created_at": msg["created_at"],
                }
                for msg in long_term
            ]

            return {
                "recent_messages": recent_messages[-10:],  # Last 10 messages
                "current_query": current_query,
            }

        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            raise

    async def get_user_chats(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's chat sessions"""
        try:

            async def operation(db):
                chats = await db.chat.find_many(
                    where={"userId": user_id},
                    order={"updatedAt": "desc"},
                    take=limit,
                    skip=offset,
                )

                return [
                    {
                        "id": chat.id,
                        "name": chat.name,
                        "created_at": chat.createdAt.isoformat(),
                        "updated_at": chat.updatedAt.isoformat(),
                    }
                    for chat in chats
                ]

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error getting user chats: {str(e)}")
            raise
