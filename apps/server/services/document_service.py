from typing import List, Dict, Any
from utils.database import DatabaseManager
from services.document_processor import DocumentProcessor
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from utils.logger import logger
from utils.supabase import supabase
import uuid


class DocumentService:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    async def initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize the knowledge base from the predefined document"""
        try:
            logger.info("Initializing knowledge base...")

            # Check if knowledge base already exists
            async def check_operation(db):
                existing_kb = await db.document.find_first(
                    where={"title": "HSC26 Bangla 1st Paper"}
                )

                if existing_kb:
                    logger.info("Knowledge base already exists")
                    chunk_count = len(
                        await self.vector_store.get_chunks_by_document(existing_kb.id)
                    )
                    return {
                        "status": "already_exists",
                        "document_id": existing_kb.id,
                        "chunk_count": chunk_count,
                    }
                return None

            existing_result = await DatabaseManager.execute(check_operation)
            if existing_result:
                return existing_result

            # Process the knowledge base document
            chunks = await self.document_processor.process_knowledge_base()

            # Create document record
            async def create_operation(db):
                document = await db.document.create(
                    data={
                        "title": "HSC26 Bangla 1st Paper",
                        "content": " ".join([chunk.page_content for chunk in chunks]),
                        "language": "bn",
                        "wordCount": sum(
                            chunk.metadata.get("word_count", 0) for chunk in chunks
                        ),
                        "pageCount": (
                            chunks[0].metadata.get("page_count", 0) if chunks else 0
                        ),
                    }
                )

                # Generate embeddings and store chunks
                chunk_data = []
                for chunk in chunks:
                    embedding = await self.embedding_service.encode_text_async(
                        chunk.page_content
                    )

                    chunk_data.append(
                        {
                            "content": chunk.page_content,
                            "embedding": embedding,
                            "metadata": chunk.metadata,
                            "token_count": len(chunk.page_content.split()),
                        }
                    )

                # Store chunks in vector store
                chunk_ids = await self.vector_store.store_document_chunks(
                    document_id=document.id, chunks_data=chunk_data
                )

                logger.info(
                    f"Knowledge base initialized: {len(chunk_ids)} chunks created"
                )

                return {
                    "status": "initialized",
                    "document_id": document.id,
                    "chunk_count": len(chunk_ids),
                    "total_words": document.wordCount,
                    "total_pages": document.pageCount,
                }

            return await DatabaseManager.execute(create_operation)

        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            raise

    async def upload_document(
        self, file_content: bytes, filename: str, file_type: str, user_id: str
    ) -> Dict[str, Any]:
        """Upload and process a new document"""
        try:
            logger.info(f"Processing uploaded document: {filename}")

            # Upload file to Supabase Storage
            file_id = str(uuid.uuid4())
            file_path = f"documents/{user_id}/{file_id}_{filename}"

            # Upload to Supabase
            storage_response = supabase.storage.from_("documents").upload(
                file_path, file_content
            )

            if storage_response.get("error"):
                raise Exception(f"Storage upload error: {storage_response['error']}")

            # Get public URL
            file_url = supabase.storage.from_("documents").get_public_url(file_path)

            # Process document
            chunks = await self.document_processor.process_uploaded_document(
                file_content, filename, file_type
            )

            if not chunks:
                raise Exception("No content could be extracted from the document")

            # Detect language
            full_content = " ".join([chunk.page_content for chunk in chunks])
            language = self.document_processor.detect_language(full_content)

            # Create database records
            async def upload_operation(db):
                # Create document
                document = await db.document.create(
                    data={
                        "title": filename.rsplit(".", 1)[0],  # Remove extension
                        "content": full_content,
                        "language": language,
                        "wordCount": len(full_content.split()),
                        "pageCount": (
                            chunks[0].metadata.get("page_count", 1) if chunks else 1
                        ),
                    }
                )

                # Create file record
                file_record = await db.file.create(
                    data={
                        "url": file_url["publicURL"],
                        "type": file_type,
                        "fileName": filename,
                        "fileSize": len(file_content),
                        "documentId": document.id,
                    }
                )

                # Generate embeddings and store chunks
                chunk_data = []
                for chunk in chunks:
                    embedding = await self.embedding_service.encode_text_async(
                        chunk.page_content
                    )

                    chunk_data.append(
                        {
                            "content": chunk.page_content,
                            "embedding": embedding,
                            "metadata": chunk.metadata,
                            "token_count": len(chunk.page_content.split()),
                        }
                    )

                # Store chunks in vector store
                chunk_ids = await self.vector_store.store_document_chunks(
                    document_id=document.id,
                    chunks_data=chunk_data,
                    file_id=file_record.id,
                )

                logger.info(
                    f"Document uploaded successfully: {len(chunk_ids)} chunks created"
                )

                return {
                    "document_id": document.id,
                    "file_id": file_record.id,
                    "filename": filename,
                    "language": language,
                    "chunk_count": len(chunk_ids),
                    "word_count": document.wordCount,
                    "page_count": document.pageCount,
                    "file_url": file_url["publicURL"],
                }

            return await DatabaseManager.execute(upload_operation)

        except Exception as e:
            logger.error(f"Error uploading document {filename}: {str(e)}")
            raise

    async def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a user"""
        try:

            async def operation(db):
                # Get documents associated with user's messages
                documents = await db.document.find_many(
                    where={"message": {"chat": {"userId": user_id}}},
                    include={"file": True, "_count": {"select": {"chunks": True}}},
                    order={"createdAt": "desc"},
                )

                return [
                    {
                        "id": doc.id,
                        "title": doc.title,
                        "language": doc.language,
                        "word_count": doc.wordCount,
                        "page_count": doc.pageCount,
                        "chunk_count": doc._count.chunks,
                        "created_at": doc.createdAt.isoformat(),
                        "file": (
                            {
                                "id": doc.file.id,
                                "filename": doc.file.fileName,
                                "type": doc.file.type,
                                "size": doc.file.fileSize,
                                "url": doc.file.url,
                            }
                            if doc.file
                            else None
                        ),
                    }
                    for doc in documents
                ]

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            raise

    async def get_document_details(self, document_id: str) -> Dict[str, Any]:
        """Get detailed information about a document"""
        try:

            async def operation(db):
                document = await db.document.find_unique(
                    where={"id": document_id},
                    include={
                        "file": True,
                        "chunks": {
                            "order": {"chunkIndex": "asc"},
                            "take": 10,  # Limit chunks for performance
                        },
                    },
                )

                if not document:
                    raise Exception(f"Document {document_id} not found")

                return {
                    "id": document.id,
                    "title": document.title,
                    "content_preview": (
                        document.content[:500] + "..."
                        if len(document.content) > 500
                        else document.content
                    ),
                    "language": document.language,
                    "metadata": document.metadata,
                    "word_count": document.wordCount,
                    "page_count": document.pageCount,
                    "created_at": document.createdAt.isoformat(),
                    "file": (
                        {
                            "id": document.file.id,
                            "filename": document.file.fileName,
                            "type": document.file.type,
                            "size": document.file.fileSize,
                            "url": document.file.url,
                        }
                        if document.file
                        else None
                    ),
                    "chunks_preview": [
                        {
                            "id": chunk.id,
                            "content_preview": (
                                chunk.content[:200] + "..."
                                if len(chunk.content) > 200
                                else chunk.content
                            ),
                            "chunk_index": chunk.chunkIndex,
                            "token_count": chunk.tokenCount,
                        }
                        for chunk in document.chunks
                    ],
                }

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error getting document details for {document_id}: {str(e)}")
            raise

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document and its associated data"""
        try:

            async def operation(db):
                # Verify ownership
                document = await db.document.find_unique(
                    where={"id": document_id},
                    include={"message": {"include": {"chat": True}}, "file": True},
                )

                if not document:
                    raise Exception(f"Document {document_id} not found")

                # Check ownership
                if document.message and document.message.chat.userId != user_id:
                    raise Exception("Unauthorized to delete this document")

                # Delete from Supabase Storage if file exists
                if document.file:
                    file_path = document.file.url.split("/")[-1]  # Extract file path
                    try:
                        supabase.storage.from_("documents").remove([file_path])
                    except Exception as e:
                        logger.warning(f"Could not delete file from storage: {str(e)}")

                # Delete chunks
                await self.vector_store.delete_document_chunks(document_id)

                # Delete file record
                if document.file:
                    await db.file.delete(where={"id": document.file.id})

                # Delete document
                await db.document.delete(where={"id": document_id})

                logger.info(f"Document {document_id} deleted successfully")
                return True

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            raise

    async def get_document_stats(self) -> Dict[str, Any]:
        """Get overall document statistics"""
        try:
            stats = await self.vector_store.get_vector_store_stats()
            return stats

        except Exception as e:
            logger.error(f"Error getting document stats: {str(e)}")
            raise

    async def delete_knowledge_base(self) -> Dict[str, Any]:
        """Delete the knowledge base document and all its data"""
        try:
            logger.info("Deleting knowledge base...")

            async def operation(db):
                # Find the knowledge base document
                kb_document = await db.document.find_first(
                    where={"title": "HSC26 Bangla 1st Paper"}, include={"file": True}
                )

                if not kb_document:
                    logger.info("Knowledge base not found")
                    return {
                        "status": "not_found",
                        "message": "Knowledge base does not exist",
                    }

                # Delete chunks from vector store
                chunks_deleted = await self.vector_store.delete_document_chunks(
                    kb_document.id
                )

                # Delete file from storage if exists
                if kb_document.file:
                    try:
                        # Extract file path from URL
                        file_path = kb_document.file.url.split("/")[-1]
                        supabase.storage.from_("documents").remove([file_path])
                    except Exception as e:
                        logger.warning(f"Could not delete file from storage: {str(e)}")

                    # Delete file record
                    await db.file.delete(where={"id": kb_document.file.id})

                # Delete document record
                await db.document.delete(where={"id": kb_document.id})

                logger.info(f"Knowledge base deleted: {chunks_deleted} chunks removed")

                return {
                    "status": "deleted",
                    "document_id": kb_document.id,
                    "chunks_deleted": chunks_deleted,
                    "message": "Knowledge base deleted successfully",
                }

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error deleting knowledge base: {str(e)}")
            raise
