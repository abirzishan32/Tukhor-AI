from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
from services.document_service import DocumentService
from middleware.auth import verify_session
from utils.logger import logger
from config.settings import settings

router = APIRouter(prefix="/documents", tags=["Documents"])


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    language: str
    chunk_count: int
    word_count: int
    page_count: int
    file_url: str


class DocumentListResponse(BaseModel):
    documents: List[Dict[str, Any]]
    total_count: int


@router.post("/initialize-kb")
async def initialize_knowledge_base(user=Depends(verify_session)):
    """Initialize the knowledge base from predefined document"""
    try:
        document_service = DocumentService()
        result = await document_service.initialize_knowledge_base()

        return {"message": "Knowledge base initialization completed", "result": result}

    except Exception as e:
        logger.error(f"Error initializing knowledge base: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error initializing knowledge base: {str(e)}"
        )


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), user=Depends(verify_session)):
    """Upload and process a document"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large")

        # Check file extension
        file_extension = f".{file.filename.split('.')[-1].lower()}"
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="File type not supported")

        # Process document
        document_service = DocumentService()
        result = await document_service.upload_document(
            file_content=file_content,
            filename=file.filename,
            file_type=file_extension[1:],
            user_id=user.id,
        )

        return DocumentResponse(
            document_id=result["document_id"],
            filename=result["filename"],
            language=result["language"],
            chunk_count=result["chunk_count"],
            word_count=result["word_count"],
            page_count=result["page_count"],
            file_url=result["file_url"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )


@router.get("/", response_model=DocumentListResponse)
async def get_user_documents(user=Depends(verify_session)):
    """Get all documents for the current user"""
    try:
        document_service = DocumentService()
        documents = await document_service.get_user_documents(user.id)

        return DocumentListResponse(documents=documents, total_count=len(documents))

    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching documents")


@router.get("/{document_id}")
async def get_document_details(document_id: str, user=Depends(verify_session)):
    """Get detailed information about a specific document"""
    try:
        document_service = DocumentService()
        details = await document_service.get_document_details(document_id)

        return details

    except Exception as e:
        logger.error(f"Error getting document details: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Document not found")
        raise HTTPException(status_code=500, detail="Error fetching document details")


@router.delete("/{document_id}")
async def delete_document(document_id: str, user=Depends(verify_session)):
    """Delete a document and its associated data"""
    try:
        document_service = DocumentService()
        success = await document_service.delete_document(document_id, user.id)

        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Document not found")
        if "unauthorized" in str(e).lower():
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this document"
            )
        raise HTTPException(status_code=500, detail="Error deleting document")


@router.get("/stats/overview")
async def get_document_stats(user=Depends(verify_session)):
    """Get overall document statistics"""
    try:
        document_service = DocumentService()
        stats = await document_service.get_document_stats()

        return stats

    except Exception as e:
        logger.error(f"Error getting document stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error fetching document statistics"
        )


@router.post("/batch-upload")
async def batch_upload_documents(
    files: List[UploadFile] = File(...), user=Depends(verify_session)
):
    """Upload multiple documents at once"""
    try:
        if len(files) > 10:  # Limit batch upload
            raise HTTPException(status_code=400, detail="Maximum 10 files per batch")

        document_service = DocumentService()
        results = []
        errors = []

        for file in files:
            try:
                if not file.filename:
                    errors.append(
                        {"filename": "unknown", "error": "No filename provided"}
                    )
                    continue

                file_content = await file.read()

                # Check file size
                if len(file_content) > settings.MAX_UPLOAD_SIZE:
                    errors.append(
                        {"filename": file.filename, "error": "File too large"}
                    )
                    continue

                # Check file extension
                file_extension = f".{file.filename.split('.')[-1].lower()}"
                if file_extension not in settings.ALLOWED_EXTENSIONS:
                    errors.append(
                        {"filename": file.filename, "error": "File type not supported"}
                    )
                    continue

                # Process document
                result = await document_service.upload_document(
                    file_content=file_content,
                    filename=file.filename,
                    file_type=file_extension[1:],
                    user_id=user.id,
                )

                results.append(
                    {
                        "filename": result["filename"],
                        "document_id": result["document_id"],
                        "language": result["language"],
                        "chunk_count": result["chunk_count"],
                        "status": "success",
                    }
                )

            except Exception as e:
                errors.append({"filename": file.filename, "error": str(e)})

        return {
            "successful_uploads": len(results),
            "failed_uploads": len(errors),
            "results": results,
            "errors": errors,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing batch upload")
