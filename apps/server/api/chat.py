from fastapi import APIRouter, Depends, Request,  HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from middleware.auth import verify_session
from services.rag_service import RAGService
from services.document_service import DocumentService
from utils.logger import logger
from prisma import Prisma
from config.limiter import limiter

router = APIRouter(prefix="/chat", tags=["Chat"])


class MessageCreate(BaseModel):
    content: str
    chat_id: Optional[str] = None
    document_ids: Optional[List[str]] = None


class ChatResponse(BaseModel):
    message: Dict[str, Any]
    rag_metadata: Optional[Dict[str, Any]] = None
    chat_id: str
    created_new_chat: bool = False


async def ensure_user_profile(user_id: str, email: str, username: str = None):
    """Ensure user profile exists in database"""
    try:
        async with Prisma() as db:
            profile = await db.profile.find_unique(where={"id": user_id})

            if not profile:
                # Create profile if it doesn't exist
                await db.profile.create(
                    data={
                        "userId": user_id,
                        "email": email,
                        "userName": username or email.split("@")[0],
                    }
                )
                logger.info(f"Created profile for user {user_id}")

    except Exception as e:
        logger.error(f"Error ensuring user profile: {str(e)}")


@router.post("/message", response_model=ChatResponse)
@limiter.limit("10/minute")
async def send_message(
    request: Request,
    content: str = Form(...),
    chat_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    user=Depends(verify_session),
):
    """Enhanced chat endpoint with RAG integration"""
    try:
        from services.memory_service import MemoryService

        rag_service = RAGService()
        memory_service = MemoryService()
        document_ids = None
        created_new_chat = False

        # Ensure user profile exists
        await ensure_user_profile(user.id, user.email)

        # Process uploaded files if any
        if files:
            document_service = DocumentService()
            document_ids = []

            for file in files:
                if file.filename:
                    file_content = await file.read()
                    file_type = file.filename.split(".")[-1].lower()

                    result = await document_service.upload_document(
                        file_content=file_content,
                        filename=file.filename,
                        file_type=file_type,
                        user_id=user.id,
                    )
                    document_ids.append(result["document_id"])

        # Create new chat if needed
        if not chat_id:
            chat_session = await memory_service.create_chat_session(user.id, content)
            chat_id = chat_session["id"]
            created_new_chat = True

        response = await rag_service.generate_answer(
            question=content,
            chat_id=chat_id,
            document_ids=document_ids,
            user_id=user.id,
        )
        return ChatResponse(
            message={
                "content": response["answer"],
                "role": "ai",
                "created_at": "now",
            },
            rag_metadata={
                "approach": response.get("approach_used", "rag"),
                "sources_used": len(response["sources"]),
                "confidence": response["confidence"],
                "language": response["language"],
                "response_time": response["response_time"],
                "chunks_retrieved": response["chunks_retrieved"],
            },
            chat_id=chat_id,
            created_new_chat=created_new_chat,
        )

    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing message: {str(e)}"
        )


async def handle_regular_chat(
    content: str,
    chat_id: str,
    user,
    document_ids: Optional[List[str]],
    created_new_chat: bool,
) -> ChatResponse:
    """Handle regular chat without RAG"""
    try:
        from services.memory_service import MemoryService

        memory_service = MemoryService()
        # Store user message
        await memory_service.store_message(
            chat_id=chat_id, content=content, role="user", document_ids=document_ids
        )

        # Generate simple response (you can integrate a different LLM here)
        simple_response = (
            f"I received your message: {content}. This is a regular chat response."
        )

        # Store AI response
        ai_message = await memory_service.store_message(
            chat_id=chat_id, content=simple_response, role="ai"
        )

        return ChatResponse(
            message={
                "content": simple_response,
                "role": "ai",
                "created_at": ai_message["created_at"],
            },
            chat_id=chat_id,
            created_new_chat=created_new_chat,
        )

    except Exception as e:
        logger.error(f"Error in regular chat: {str(e)}")
        raise


@router.get("/")
@limiter.limit("10/minute")
async def get_user_chats(
    request: Request, 
    limit: int = 20, 
    offset: int = 0,
    user=Depends(verify_session)
):
    """Get user's chat sessions"""
    try:
        from services.memory_service import MemoryService

        memory_service = MemoryService()
        chats = await memory_service.get_user_chats(user.id, limit, offset)
        
        # Get total count for pagination
        all_chats = await memory_service.get_user_chats(user.id, limit=1000, offset=0)  # Get a large number to count
        total = len(all_chats)
        
        return {
            "chats": chats,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "hasMore": offset + len(chats) < total
            }
        }

    except Exception as e:
        logger.error(f"Error getting user chats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching chats")


@router.get("/{chat_id}/messages")
@limiter.limit("10/minute")
async def get_chat_messages(
    request: Request,
    chat_id: str, 
    limit: int = 50, 
    offset: int = 0,
    user=Depends(verify_session)
):
    """Get messages for a specific chat"""
    try:
        from services.memory_service import MemoryService

        memory_service = MemoryService()

        # Verify chat belongs to user
        user_chats = await memory_service.get_user_chats(user.id)
        chat_exists = any(chat["id"] == chat_id for chat in user_chats)

        if not chat_exists:
            raise HTTPException(status_code=404, detail="Chat not found")

        result = await memory_service.get_chat_history(chat_id, limit, offset)
        messages = result["messages"]
        total_count = result["count"]
        
        return {
            "messages": messages,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "hasMore": offset + len(messages) < total_count
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching messages")


@router.delete("/{chat_id}")
@limiter.limit("10/minute")
async def delete_chat(request: Request, chat_id: str, user=Depends(verify_session)):
    """Delete a chat session"""
    try:
        async with Prisma() as db:
            # Verify ownership using userId directly (not through Profile relation)
            chat = await db.chat.find_unique(where={"id": chat_id})

            if not chat or chat.userId != user.id:
                raise HTTPException(status_code=404, detail="Chat not found")

            # Delete chat and all associated messages (cascade)
            await db.chat.delete(where={"id": chat_id})

        return {"message": "Chat deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting chat")
