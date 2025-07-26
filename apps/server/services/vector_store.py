from typing import List, Dict, Any, Optional
from utils.database import DatabaseManager
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config.settings import settings
from utils.logger import logger
import json
import uuid
from utils.supabase import supabase

class VectorStore:
    def __init__(self):
        pass  # No need to initialize Prisma here anymore

    async def store_document_chunks(
        self,
        document_id: str,
        chunks_data: List[Dict[str, Any]],
        file_id: Optional[str] = None,
    ) -> List[str]:
        """Store document chunks with embeddings in the database"""
        try:

            async def operation(db):
                chunk_ids = []

                for i, chunk_data in enumerate(chunks_data):
                    id = uuid.uuid4().hex
                    await db.execute_raw(
                        """
                        INSERT INTO "DocumentChunk" (
                            "id", "content", "embedding", "metadata", 
                            "documentId", "fileId", "chunkIndex", "tokenCount"
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        RETURNING id
                        """,
                        id,
                        chunk_data["content"],
                        chunk_data["embedding"],
                        chunk_data.get("metadata", "{}"),
                        document_id,
                        file_id,
                        i,
                        chunk_data.get("token_count"),
                    )
                    chunk_ids.append(id)

                logger.info(
                    f"Stored {len(chunk_ids)} chunks for document {document_id}"
                )
                return chunk_ids

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error storing document chunks: {e}")
            raise

    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = None,
        language_filter: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Find most similar chunks using vector similarity"""
        try:
            top_k = top_k or settings.TOP_K_CHUNKS

            query = supabase.table("DocumentChunk")
            query = query.select("""
                *,
                document:Document(*),
                file:File(*)
            """)
            
            if language_filter:
                query = query.eq("document.language", language_filter)
            if document_ids:
                query = query.in_("documentId", document_ids)
                
            response = query.execute()

            chunks = response.data

            if not chunks:
                return []
            
            logger.info(f"Found {len(chunks)} chunks for similarity search")
            #logger.info(chunks[0])
            #log the type and the fields of the first chunk
            logger.info(f"Type: {type(chunks[0])}")
            # Calculate similarities
            similarities = []
            query_vec = np.array(query_embedding)
            for chunk in chunks:
                try:
                    # logger.info(f"Calculating similarity for chunk {chunk.embedding}")
                    # Parse embedding from database
                    chunk_embedding = (
                        json.loads(chunk["embedding"])
                        if isinstance(chunk["embedding"], str)
                        else chunk["embedding"]
                    )
                    chunk_vec = np.array(chunk_embedding)
                    # Calculate cosine similarity
                    similarity = cosine_similarity([query_vec], [chunk_vec])[0][0]
                    similarities.append(
                        {"chunk": chunk, "similarity": float(similarity)}
                    )
                except Exception as e:
                    logger.warning(
                        f"Error calculating similarity for chunk {chunk["id"]}: {str(e)}"
                    )
                    continue
            # Sort by similarity and get top-k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            top_chunks = similarities[:top_k]
            # Format results
            results = []
            for item in top_chunks:
                chunk = item["chunk"]
                results.append(
                    {
                        "id": chunk["id"],
                        "content": chunk["content"],
                        "similarity": item["similarity"],
                        "metadata": chunk["metadata"],
                        "chunk_index": chunk["chunkIndex"],
                        "document_id": chunk["documentId"],
                        "document_title": (
                            chunk["document"]["title"] if chunk["document"] else None
                        ),
                        "document_language": (
                            chunk["document"]["language"] if chunk["document"] else None
                        ),
                        "file_name": chunk["file"]["fileName"] if chunk["file"] else None,
                    }
                )
            logger.info(f"Found {len(results)} similar chunks")
            return results

        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise

    async def get_chunks_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:

            async def operation(db):
                chunks = await db.documentchunk.find_many(
                    where={"documentId": document_id},
                    order={"chunkIndex": "asc"},
                    include={"document": True, "file": True},
                )

                return [
                    {
                        "id": chunk.id,
                        "content": chunk.content,
                        "metadata": chunk.metadata,
                        "chunk_index": chunk.chunkIndex,
                        "token_count": chunk.tokenCount,
                        "document_title": (
                            chunk.document.title if chunk.document else None
                        ),
                    }
                    for chunk in chunks
                ]

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error getting chunks by document {document_id}: {str(e)}")
            raise

    async def delete_document_chunks(self, document_id: str) -> int:
        """Delete all chunks for a document"""
        try:

            async def operation(db):
                result = await db.documentchunk.delete_many(
                    where={"documentId": document_id}
                )

                logger.info(f"Deleted {result} chunks for document {document_id}")

                return result

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error deleting chunks for document {document_id}: {str(e)}")
            raise

    async def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:

            async def operation(db):
                total_chunks = await db.documentchunk.count()
                total_documents = await db.document.count()

                # Language distribution
                language_stats = await db.document.group_by(
                    by=["language"], count={"_all": True}
                )

                return {
                    "total_chunks": total_chunks,
                    "total_documents": total_documents,
                    "language_distribution": {
                        stat["language"]: stat["_count"]["_all"]
                        for stat in language_stats
                    },
                }

            return await DatabaseManager.execute(operation)

        except Exception as e:
            logger.error(f"Error getting vector store stats: {str(e)}")
            raise
