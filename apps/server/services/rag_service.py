import google.generativeai as genai
from typing import List, Dict, Any, Optional
import time
import asyncio
import re
from config.settings import settings
from utils.logger import logger
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.memory_service import MemoryService
import json


class RAGService:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        # Initialize services
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.memory_service = MemoryService()

        # Setup prompts and thresholds
        self.setup_prompts()

    def setup_prompts(self):
        """Setup multilingual prompt templates"""
        self.rag_system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from Bengali and English documents. 

Key Instructions:
1. Answer in the SAME LANGUAGE as the question
2. If the question is in Bengali (বাংলা), answer in Bengali
3. If the question is in English, answer in English
4. Base your answer ONLY on the provided context
5. If you cannot find the answer in the context, say "আমি প্রদত্ত প্রসঙ্গে এই প্রশ্নের উত্তর খুঁজে পাচ্ছি না।" (Bengali) or "I cannot find the answer to this question in the provided context." (English)
6. Be concise and direct in your answers
7. Cite relevant parts of the context when possible

Context from documents:
{context}

Previous conversation context:
{conversation_context}

Question: {question}

Answer:"""

        # Fallback prompt for when no relevant context is found
        self.fallback_prompt = """You are a helpful AI assistant. Answer the following question to the best of your ability.

Important Instructions:
1. Answer in the SAME LANGUAGE as the question
2. If the question is in Bengali (বাংলা), answer in Bengali
3. If the question is in English, answer in English
4. Be helpful and informative
5. If you don't know something, admit it honestly

Question: {question}

Answer:"""

        # Minimum similarity threshold for using RAG context
        self.similarity_threshold = 0.3
        self.high_confidence_threshold = 0.7

    async def generate_answer(
        self,
        question: str,
        chat_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Complete RAG pipeline with improved chunk correlation and fallback"""
        start_time = time.time()

        try:
            query_language = self._detect_query_language(question)
            logger.info(f"Processing {query_language} query: {question[:50]}...")

            query_embedding = await self.embedding_service.encode_text_async(question)

            relevant_chunks = await self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=settings.TOP_K_CHUNKS,
                language_filter=query_language if query_language != "mixed" else None,
                document_ids=document_ids,
            )

            # 4. Get conversation context if chat_id provided
            conversation_context = ""
            if chat_id:
                context_data = await self.memory_service.get_relevant_context(
                    chat_id, question
                )
                conversation_context = self._format_conversation_context(context_data)

            # 5. Evaluate chunk relevance and decide approach
            use_rag = self._should_use_rag_context(relevant_chunks, question)

            if use_rag:
                # Use RAG with context
                context = self._format_context(relevant_chunks)

                prompt = self.rag_system_prompt.format(
                    context=context,
                    conversation_context=conversation_context,
                    question=question,
                )

                answer = await self._generate_with_gemini(prompt)
                confidence = self._calculate_confidence(relevant_chunks, answer)

                rag_metadata = {
                    "approach": "rag",
                    "chunks_used": len(relevant_chunks),
                    "max_similarity": (
                        max([chunk["similarity"] for chunk in relevant_chunks])
                        if relevant_chunks
                        else 0
                    ),
                    "language": query_language,
                }

            else:
                # Use fallback approach with general knowledge
                logger.info("Low chunk relevance detected, using fallback approach")

                prompt = self.fallback_prompt.format(question=question)
                answer = await self._generate_with_gemini(prompt)
                confidence = 0.5  # Medium confidence for fallback responses

                rag_metadata = {
                    "approach": "fallback",
                    "chunks_used": 0,
                    "max_similarity": (
                        max([chunk["similarity"] for chunk in relevant_chunks])
                        if relevant_chunks
                        else 0
                    ),
                    "reason": "low_chunk_relevance",
                    "language": query_language,
                }

            # 6. Calculate metrics
            response_time = time.time() - start_time

            # 7. Store interaction in database
            if chat_id:
                await self._store_interaction(
                    chat_id=chat_id,
                    question=question,
                    answer=answer,
                    retrieved_chunks=relevant_chunks,
                    confidence=confidence,
                    document_ids=document_ids,
                    rag_metadata=rag_metadata,
                    response_time=response_time,
                )

            return {
                "answer": answer,
                "sources": relevant_chunks,
                "confidence": confidence,
                "response_time": response_time,
                "language": query_language,
                "chunks_retrieved": len(relevant_chunks),
                "approach_used": rag_metadata["approach"],
            }

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            # Return a basic fallback response in case of errors
            return {
                "answer": self._get_error_response(question),
                "sources": [],
                "confidence": 0.1,
                "response_time": time.time() - start_time,
                "language": self._detect_query_language(question),
                "chunks_retrieved": 0,
                "approach_used": "error_fallback",
            }

    def _should_use_rag_context(
        self, chunks: List[Dict[str, Any]], question: str
    ) -> bool:
        """Determine if chunks are relevant enough to use RAG approach"""
        if not chunks:
            return False

        # Check if any chunk meets similarity threshold
        max_similarity = max([chunk["similarity"] for chunk in chunks])

        if max_similarity < self.similarity_threshold:
            logger.info(
                f"Max similarity {max_similarity:.3f} below threshold {self.similarity_threshold}"
            )
            return False

        # Additional checks can be added here (e.g., semantic coherence)
        return True

    def _get_error_response(self, question: str) -> str:
        """Generate error response in appropriate language"""
        language = self._detect_query_language(question)

        if language == "bn":
            return "দুঃখিত, আপনার প্রশ্নের উত্তর দিতে আমার কিছু সমস্যা হচ্ছে। অনুগ্রহ করে আবার চেষ্টা করুন।"
        else:
            return "Sorry, I'm having trouble answering your question right now. Please try again."

    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate response using Gemini"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.model.generate_content(prompt)
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating with Gemini: {str(e)}")
            raise

    def _detect_query_language(self, text: str) -> str:
        """Detect if query is Bengali, English, or mixed"""
        bengali_chars = len(re.findall(r"[\u0980-\u09FF]", text))
        english_chars = len(re.findall(r"[a-zA-Z]", text))
        total_chars = bengali_chars + english_chars

        if total_chars == 0:
            return "en"

        bengali_ratio = bengali_chars / total_chars

        if bengali_ratio > 0.7:
            return "bn"
        elif bengali_ratio < 0.3:
            return "en"
        else:
            return "mixed"

    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into context string"""
        if not chunks:
            return "No relevant context found."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            similarity_score = chunk.get("similarity", 0)
            document_title = chunk.get("document_title", "Unknown Document")
            content = chunk.get("content", "")

            context_parts.append(
                f"Source {i} (Similarity: {similarity_score:.2f}, Document: {document_title}):\n{content}\n"
            )

        return "\n".join(context_parts)

    def _format_conversation_context(self, context_data: Dict[str, Any]) -> str:
        """Format conversation context from memory"""
        if not context_data or not context_data.get("recent_messages"):
            return ""

        recent_messages = context_data["recent_messages"]
        formatted_messages = []

        for msg in recent_messages[-3:]:  # Last 3 messages for context
            role = msg.get("role", "").upper()
            content = msg.get("content", "")
            formatted_messages.append(f"{role}: {content}")

        return "\n".join(formatted_messages)

    def _calculate_confidence(self, chunks: List[Dict[str, Any]], answer: str) -> float:
        """Calculate confidence score based on chunk similarity and answer quality"""
        if not chunks:
            return 0.3

        # Base confidence on highest similarity
        max_similarity = max([chunk["similarity"] for chunk in chunks])

        # Adjust based on number of chunks used
        chunk_bonus = min(len(chunks) * 0.1, 0.3)

        # Basic answer quality check (length and structure)
        answer_quality = min(len(answer.split()) / 20, 1.0) * 0.1

        confidence = max_similarity + chunk_bonus + answer_quality
        return min(confidence, 1.0)

    async def _store_interaction(
        self,
        chat_id: str,
        question: str,
        answer: str,
        retrieved_chunks: List[Dict],
        confidence: float,
        document_ids: Optional[List[str]] = None,
        rag_metadata: Optional[Dict[str, Any]] = None,
        response_time: Optional[float] = None,
    ):
        """Store user question and AI response in database"""
        try:
            # Store user message
            await self.memory_service.store_message(
                chat_id=chat_id,
                content=question,
                role="user",
                document_ids=document_ids,
            )

            # Store AI response
            await self.memory_service.store_message(
                chat_id=chat_id,
                content=answer,
                role="ai",
                retrieved_chunks=json.dumps(retrieved_chunks),
                grounding_score=confidence,
                rag_metadata=rag_metadata,
                response_time=response_time,
            )

        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")

    async def create_chat_session(
        self, user_id: str, first_query: str
    ) -> Dict[str, Any]:
        """Create a new chat session"""
        return await self.memory_service.create_chat_session(user_id, first_query)

    async def get_chat_history(
        self, chat_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get chat history"""
        return await self.memory_service.get_chat_history(chat_id, limit)

    async def get_user_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's chat sessions"""
        return await self.memory_service.get_user_chats(user_id)
