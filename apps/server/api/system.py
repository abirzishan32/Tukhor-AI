from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from services.document_service import DocumentService
from services.vector_store import VectorStore
from middleware.auth import verify_session
from utils.logger import logger
from config.settings import settings

router = APIRouter(prefix="/system", tags=["System"])


class InitializationResponse(BaseModel):
    message: str
    knowledge_base_status: Dict[str, Any]
    vector_store_stats: Dict[str, Any]
    system_ready: bool


@router.post("/initialize", response_model=InitializationResponse)
async def initialize_system(user=Depends(verify_session)):
    """Initialize the RAG system with knowledge base and dependencies"""
    try:
        logger.info("Starting system initialization...")

        # Initialize document service
        document_service = DocumentService()
        vector_store = VectorStore()

        # Initialize knowledge base
        kb_result = await document_service.initialize_knowledge_base()

        # Get vector store statistics
        stats = await vector_store.get_vector_store_stats()

        # Check if system is ready
        system_ready = (
            kb_result["status"] in ["initialized", "already_exists"]
            and stats["total_chunks"] > 0
        )

        logger.info(f"System initialization completed. Ready: {system_ready}")

        return InitializationResponse(
            message="System initialization completed successfully",
            knowledge_base_status=kb_result,
            vector_store_stats=stats,
            system_ready=system_ready,
        )

    except Exception as e:
        logger.error(f"Error during system initialization: {e}")
        raise HTTPException(
            status_code=500, detail=f"System initialization failed: {str(e)}"
        )


@router.get("/status")
async def get_system_status():
    """Get current system status"""
    try:
        vector_store = VectorStore()
        stats = await vector_store.get_vector_store_stats()

        # Check if knowledge base exists
        knowledge_base_ready = (
            stats["total_documents"] > 0 and stats["total_chunks"] > 0
        )

        return {
            "system_ready": knowledge_base_ready,
            "vector_store_stats": stats,
            "embedding_model": settings.EMBEDDING_MODEL,
            "chunk_settings": {
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "top_k_chunks": settings.TOP_K_CHUNKS,
            },
        }

    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching system status")


@router.get("/health")
async def health_check():
    """Comprehensive health check for all system components"""
    try:
        health_status = {
            "database": "unknown",
            "vector_store": "unknown",
            "embedding_service": "unknown",
            "knowledge_base": "unknown",
            "overall": "unknown",
        }

        # Check database connection
        try:
            from prisma import Prisma

            async with Prisma() as db:
                await db.query_raw("SELECT 1")
            health_status["database"] = "healthy"
        except Exception as e:
            health_status["database"] = f"unhealthy: {str(e)}"

        # Check vector store
        try:
            vector_store = VectorStore()
            stats = await vector_store.get_vector_store_stats()
            health_status["vector_store"] = "healthy"
            health_status["knowledge_base"] = (
                "healthy" if stats["total_chunks"] > 0 else "no_data"
            )
        except Exception as e:
            health_status["vector_store"] = f"unhealthy: {str(e)}"
            health_status["knowledge_base"] = "unavailable"

        # Check embedding service
        try:
            from services.embedding_service import EmbeddingService

            embedding_service = EmbeddingService()
            test_embedding = embedding_service.encode_text("test")
            health_status["embedding_service"] = (
                "healthy" if len(test_embedding) > 0 else "unhealthy"
            )
        except Exception as e:
            health_status["embedding_service"] = f"unhealthy: {str(e)}"

        # Overall health
        unhealthy_components = [
            k
            for k, v in health_status.items()
            if "unhealthy" in str(v) or v == "unknown"
        ]
        if not unhealthy_components:
            health_status["overall"] = "healthy"
        else:
            health_status["overall"] = f"unhealthy: {', '.join(unhealthy_components)}"

        return health_status

    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return {
            "overall": f"error: {str(e)}",
            "database": "unknown",
            "vector_store": "unknown",
            "embedding_service": "unknown",
            "knowledge_base": "unknown",
        }


class DeleteKnowledgeBaseResponse(BaseModel):
    message: str
    status: str
    document_id: str
    chunks_deleted: int


@router.delete("/knowledge-base", response_model=DeleteKnowledgeBaseResponse)
async def delete_knowledge_base(user=Depends(verify_session)):
    """Delete the knowledge base and all associated data"""
    try:
        logger.info("Starting knowledge base deletion...")

        # Initialize document service
        document_service = DocumentService()

        # Delete knowledge base
        kb_result = await document_service.delete_knowledge_base()

        if kb_result["status"] == "not_found":
            raise HTTPException(
                status_code=404,
                detail="Knowledge base not found",
            )

        logger.info(
            f"Knowledge base deletion completed: {kb_result['chunks_deleted']} chunks removed"
        )

        return DeleteKnowledgeBaseResponse(
            message=kb_result["message"],
            status=kb_result["status"],
            document_id=kb_result["document_id"],
            chunks_deleted=kb_result["chunks_deleted"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during knowledge base deletion: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Knowledge base deletion failed: {str(e)}"
        )
