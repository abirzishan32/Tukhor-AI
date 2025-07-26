from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.rag_service import RAGService
from services.evaluation_service import EvaluationService
from middleware.auth import verify_session
from utils.logger import logger

router = APIRouter(prefix="/rag", tags=["RAG"])


# Pydantic models
class QueryRequest(BaseModel):
    question: str
    chat_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    include_history: bool = True


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    response_time: float
    language: str
    chunks_retrieved: int
    chat_id: Optional[str] = None
    created_new_chat: bool = False


class FeedbackRequest(BaseModel):
    message_id: str
    feedback: str  # 'helpful', 'not_helpful', 'partial'


class ChatHistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]
    chat_id: str
    chat_name: str


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest, user=Depends(verify_session)):
    """Main RAG endpoint for asking questions"""
    try:
        rag_service = RAGService()

        # If no chat_id provided, create a new chat
        chat_id = request.chat_id
        created_new_chat = False

        if not chat_id:
            chat_session = await rag_service.create_chat_session(
                user.id, request.question
            )
            chat_id = chat_session["id"]
            created_new_chat = True
            logger.info(f"Created new chat session: {chat_id}")

        # Generate answer using RAG
        result = await rag_service.generate_answer(
            question=request.question,
            chat_id=chat_id,
            document_ids=request.document_ids,
            user_id=user.id,
        )

        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            response_time=result["response_time"],
            language=result["language"],
            chunks_retrieved=result["chunks_retrieved"],
            chat_id=chat_id,
            created_new_chat=created_new_chat,
        )

    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing question: {str(e)}"
        )


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, user=Depends(verify_session)):
    """Submit user feedback for a response"""
    try:
        if request.feedback not in ["helpful", "not_helpful", "partial"]:
            raise HTTPException(status_code=400, detail="Invalid feedback value")

        evaluation_service = EvaluationService()
        await evaluation_service.store_user_feedback(
            request.message_id, request.feedback
        )

        return {"message": "Feedback submitted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error submitting feedback")


@router.get("/evaluation/stats")
async def get_evaluation_stats(user=Depends(verify_session)):
    """Get evaluation statistics (admin endpoint)"""
    try:
        evaluation_service = EvaluationService()
        stats = await evaluation_service.get_evaluation_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting evaluation stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching evaluation stats")
