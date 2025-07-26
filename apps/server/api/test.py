from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import verify_session
from prisma import Prisma
from utils.logger import logger
from typing import Dict, Any
import json
import numpy as np

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/auth")
async def test_auth(user=Depends(verify_session)):
    """Test endpoint to verify authentication."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"message": "Authenticated successfully", "user_id": user.id, "user": user}


async def ensure_user_profile(
    user_id: str, email: str, username: str = None
) -> Dict[str, Any]:
    """Ensure user profile exists in database"""
    async with Prisma() as db:
        profile = await db.profile.find_unique(where={"userId": user_id})

        if not profile:
            # Create profile if it doesn't exist
            profile = await db.profile.create(
                data={
                    "userId": user_id,
                    "email": email,
                    "userName": username or email.split("@")[0],
                }
            )
            logger.info(f"Created profile for user {user_id}")

        return {
            "id": profile.id,
            "userId": profile.userId,
            "userName": profile.userName,
            "email": profile.email,
            "created": profile.createdAt.isoformat() if profile.createdAt else None,
        }


@router.post("/models")
async def test_comprehensive_models(user=Depends(verify_session)):
    """Comprehensive test for all models - Create, Read, and Delete operations"""

    test_results = {
        "success": True,
        "operations": [],
        "created_resources": {
            "profile_id": None,
            "chat_id": None,
            "message_ids": [],
            "document_id": None,
            "file_id": None,
            "chunk_ids": [],
        },
        "errors": [],
    }

    try:
        async with Prisma() as db:
            # Step 1: Ensure Profile exists
            logger.info("=== STEP 1: Creating/Verifying Profile ===")
            try:
                profile_result = await ensure_user_profile(user.id, user.email)
                test_results["created_resources"]["profile_id"] = profile_result["id"]
                test_results["operations"].append(
                    {
                        "step": "profile_creation",
                        "status": "success",
                        "details": profile_result,
                    }
                )
                logger.info(f"Profile verified/created: {profile_result}")
            except Exception as e:
                error_msg = f"Profile creation failed: {str(e)}"
                logger.error(error_msg)
                test_results["errors"].append(error_msg)
                test_results["success"] = False
                return test_results

            # Step 2: Create Chat
            logger.info("=== STEP 2: Creating Chat ===")
            try:
                chat = await db.chat.create(
                    data={
                        "name": "Test Chat Session",
                        "userId": user.id,
                        "shortTermMemory": json.dumps(
                            [
                                {"type": "context", "content": "This is a test chat"},
                                {
                                    "type": "preference",
                                    "content": "User prefers detailed explanations",
                                },
                            ]
                        ),
                    }
                )
                test_results["created_resources"]["chat_id"] = chat.id
                test_results["operations"].append(
                    {
                        "step": "chat_creation",
                        "status": "success",
                        "details": {
                            "id": chat.id,
                            "name": chat.name,
                            "userId": chat.userId,
                            "shortTermMemory": chat.shortTermMemory,
                            "created": (
                                chat.createdAt.isoformat() if chat.createdAt else None
                            ),
                        },
                    }
                )
                logger.info(f"Chat created successfully: {chat.id}")
            except Exception as e:
                error_msg = f"Chat creation failed: {str(e)}"
                logger.error(error_msg)
                test_results["errors"].append(error_msg)
                test_results["success"] = False

            # Step 3: Create Document first (required for Messages)
            logger.info("=== STEP 3: Creating Document ===")
            try:
                document = await db.document.create(
                    data={
                        "title": "Test Document for RAG",
                        "content": "This is a comprehensive test document containing Bengali and English text. বাংলা ভাষায় এটি একটি পরীক্ষার নথি। The document contains important information about testing our RAG system.",
                        "language": "mixed",
                        "metadata": json.dumps(
                            {
                                "test_type": "comprehensive",
                                "source": "automated_test",
                                "languages": ["en", "bn"],
                            }
                        ),
                        "wordCount": 50,
                        "pageCount": 1,
                    }
                )
                test_results["created_resources"]["document_id"] = document.id
                test_results["operations"].append(
                    {
                        "step": "document_creation",
                        "status": "success",
                        "details": {
                            "id": document.id,
                            "title": document.title,
                            "language": document.language,
                            "wordCount": document.wordCount,
                            "created": (
                                document.createdAt.isoformat()
                                if document.createdAt
                                else None
                            ),
                        },
                    }
                )
                logger.info(f"Document created successfully: {document.id}")
            except Exception as e:
                error_msg = f"Document creation failed: {str(e)}"
                logger.error(error_msg)
                test_results["errors"].append(error_msg)
                test_results["success"] = False

            # Step 4: Create File
            logger.info("=== STEP 4: Creating File ===")
            try:
                file = await db.file.create(
                    data={
                        "url": "https://example.com/test-file.pdf",
                        "type": "pdf",
                        "fileName": "test-document.pdf",
                        "fileSize": 1024,
                        "documentId": document.id,
                    }
                )
                test_results["created_resources"]["file_id"] = file.id
                test_results["operations"].append(
                    {
                        "step": "file_creation",
                        "status": "success",
                        "details": {
                            "id": file.id,
                            "fileName": file.fileName,
                            "type": file.type,
                            "fileSize": file.fileSize,
                            "documentId": file.documentId,
                            "created": (
                                file.createdAt.isoformat() if file.createdAt else None
                            ),
                        },
                    }
                )
                logger.info(f"File created successfully: {file.id}")
            except Exception as e:
                error_msg = f"File creation failed: {str(e)}"
                logger.error(error_msg)
                test_results["errors"].append(error_msg)
                test_results["success"] = False

            # Step 5: Create Document Chunks
            logger.info("=== STEP 5: Creating Document Chunks ===")
            try:
                # Create sample embeddings (1536 dimensions for OpenAI)
                chunk_data = [
                    {
                        "content": "This is the first chunk of the test document.",
                        "chunkIndex": 0,
                        "tokenCount": 10,
                    },
                    {
                        "content": "এটি দ্বিতীয় অংশ যা বাংলায় লেখা।",
                        "chunkIndex": 1,
                        "tokenCount": 8,
                    },
                    {
                        "content": "This is the third chunk containing mixed content. বাংলা এবং ইংরেজি মিশ্রিত।",
                        "chunkIndex": 2,
                        "tokenCount": 15,
                    },
                ]

                chunk_ids = []
                for chunk_info in chunk_data:
                    # Generate a dummy embedding vector
                    embedding_vector = np.random.rand(1536).tolist()

                    chunk = await db.documentchunk.create(
                        data={
                            "content": chunk_info["content"],
                            "documentId": document.id,
                            "fileId": file.id,
                            "chunkIndex": chunk_info["chunkIndex"],
                            "tokenCount": chunk_info["tokenCount"],
                            "metadata": json.dumps(
                                {
                                    "test_chunk": True,
                                    "language_detected": (
                                        "mixed"
                                        if "বাংলা" in chunk_info["content"]
                                        else "en"
                                    ),
                                }
                            ),
                            "embedding": f"[{','.join(map(str, embedding_vector))}]",
                        }
                    )
                    chunk_ids.append(chunk.id)
                    logger.info(f"Document chunk created: {chunk.id}")

                test_results["created_resources"]["chunk_ids"] = chunk_ids
                test_results["operations"].append(
                    {
                        "step": "chunks_creation",
                        "status": "success",
                        "details": {
                            "count": len(chunk_ids),
                            "chunk_ids": chunk_ids,
                            "chunks": [
                                {
                                    "id": chunk_ids[i],
                                    "content": chunk_data[i]["content"][:50] + "...",
                                    "chunkIndex": chunk_data[i]["chunkIndex"],
                                    "tokenCount": chunk_data[i]["tokenCount"],
                                }
                                for i in range(len(chunk_ids))
                            ],
                        },
                    }
                )
            except Exception as e:
                error_msg = f"Document chunks creation failed: {str(e)}"
                logger.error(error_msg)
                test_results["errors"].append(error_msg)
                test_results["success"] = False

            # Step 6: Create Messages
            logger.info("=== STEP 6: Creating Messages ===")
            if test_results["created_resources"]["chat_id"]:
                try:
                    messages_data = [
                        {
                            "content": "Hello, this is a test message in English.",
                            "role": "user",
                            "ragMetadata": json.dumps(
                                {"approach": "direct", "language_detected": "en"}
                            ),
                        },
                        {
                            "content": "This is the AI response to the test message.",
                            "role": "ai",
                            "groundingScore": 0.85,
                            "responseTime": 1.2,
                            "retrievedChunks": json.dumps(
                                [
                                    {
                                        "chunk_id": (
                                            chunk_ids[0] if chunk_ids else "test_chunk"
                                        ),
                                        "similarity": 0.89,
                                        "content": "Sample retrieved chunk content",
                                    }
                                ]
                            ),
                            "ragMetadata": json.dumps(
                                {
                                    "approach": "rag",
                                    "chunks_retrieved": 3,
                                    "confidence": 0.85,
                                    "language": "en",
                                    "fallback_used": False,
                                }
                            ),
                        },
                        {
                            "content": "আমি বাংলায় একটি প্রশ্ন করতে চাই।",
                            "role": "user",
                            "ragMetadata": json.dumps(
                                {"approach": "direct", "language_detected": "bn"}
                            ),
                        },
                        {
                            "content": "আপনার বাংলা প্রশ্নের উত্তর এখানে। This is a mixed language response.",
                            "role": "ai",
                            "groundingScore": 0.92,
                            "responseTime": 1.8,
                            "retrievedChunks": json.dumps(
                                [
                                    {
                                        "chunk_id": (
                                            chunk_ids[1]
                                            if len(chunk_ids) > 1
                                            else "test_chunk_bn"
                                        ),
                                        "similarity": 0.93,
                                        "content": "বাংলা চাঙ্ক কন্টেন্ট",
                                    }
                                ]
                            ),
                            "ragMetadata": json.dumps(
                                {
                                    "approach": "rag",
                                    "chunks_retrieved": 2,
                                    "confidence": 0.92,
                                    "language": "bn",
                                    "fallback_used": False,
                                }
                            ),
                        },
                    ]

                    message_ids = []
                    for msg_data in messages_data:
                        message = await db.message.create(
                            data={
                                "content": msg_data["content"],
                                "role": msg_data["role"],
                                "chatId": chat.id,
                                "groundingScore": msg_data.get("groundingScore"),
                                "responseTime": msg_data.get("responseTime"),
                                "retrievedChunks": msg_data.get("retrievedChunks"),
                                "ragMetadata": msg_data.get("ragMetadata"),
                            }
                        )
                        message_ids.append(message.id)
                        logger.info(
                            f"Message created: {message.id} - {msg_data['role']}"
                        )

                    test_results["created_resources"]["message_ids"] = message_ids
                    test_results["operations"].append(
                        {
                            "step": "messages_creation",
                            "status": "success",
                            "details": {
                                "count": len(message_ids),
                                "message_ids": message_ids,
                                "messages": [
                                    {
                                        "id": message_ids[i],
                                        "role": messages_data[i]["role"],
                                        "content": messages_data[i]["content"][:50]
                                        + "...",
                                        "groundingScore": messages_data[i].get(
                                            "groundingScore"
                                        ),
                                        "responseTime": messages_data[i].get(
                                            "responseTime"
                                        ),
                                    }
                                    for i in range(len(message_ids))
                                ],
                            },
                        }
                    )
                except Exception as e:
                    error_msg = f"Messages creation failed: {str(e)}"
                    logger.error(error_msg)
                    test_results["errors"].append(error_msg)
                    test_results["success"] = False

            # Step 7: Test Read Operations
            logger.info("=== STEP 7: Testing Read Operations ===")
            try:
                # Test reading chat with messages
                chat_with_messages = await db.chat.find_unique(
                    where={"id": chat.id},
                    include={"messages": {"orderBy": {"createdAt": "asc"}}},
                )

                # Test reading document with chunks
                document_with_chunks = await db.document.find_unique(
                    where={"id": document.id},
                    include={
                        "chunks": {"orderBy": {"chunkIndex": "asc"}},
                        "file": True,
                    },
                )

                test_results["operations"].append(
                    {
                        "step": "read_operations",
                        "status": "success",
                        "details": {
                            "chat_messages_count": (
                                len(chat_with_messages.messages)
                                if chat_with_messages
                                else 0
                            ),
                            "document_chunks_count": (
                                len(document_with_chunks.chunks)
                                if document_with_chunks
                                else 0
                            ),
                            "file_linked": (
                                document_with_chunks.file is not None
                                if document_with_chunks
                                else False
                            ),
                        },
                    }
                )
                logger.info("Read operations completed successfully")
            except Exception as e:
                error_msg = f"Read operations failed: {str(e)}"
                logger.error(error_msg)
                test_results["errors"].append(error_msg)

            # Step 8: Test Bulk Operations
            logger.info("=== STEP 8: Testing Bulk Operations ===")
            try:
                # Test bulk message retrieval
                all_messages = await db.message.find_many(
                    where={"chatId": chat.id}, include={"chat": True}
                )

                # Test bulk chunk retrieval
                all_chunks = await db.documentchunk.find_many(
                    where={"documentId": document.id}
                )

                test_results["operations"].append(
                    {
                        "step": "bulk_operations",
                        "status": "success",
                        "details": {
                            "bulk_messages_retrieved": len(all_messages),
                            "bulk_chunks_retrieved": len(all_chunks),
                            "message_chat_relations": all(
                                [msg.chat is not None for msg in all_messages]
                            ),
                        },
                    }
                )
                logger.info("Bulk operations completed successfully")
            except Exception as e:
                error_msg = f"Bulk operations failed: {str(e)}"
                logger.error(error_msg)
                test_results["errors"].append(error_msg)

    except Exception as e:
        error_msg = f"Database connection or transaction failed: {str(e)}"
        logger.error(error_msg)
        test_results["errors"].append(error_msg)
        test_results["success"] = False

    # Log final results
    logger.info("=== TEST SUMMARY ===")
    logger.info(f"Overall Success: {test_results['success']}")
    logger.info(f"Operations Completed: {len(test_results['operations'])}")
    logger.info(f"Errors Encountered: {len(test_results['errors'])}")

    if test_results["errors"]:
        logger.error("Errors encountered:")
        for error in test_results["errors"]:
            logger.error(f"  - {error}")

    return test_results


@router.delete("/models")
async def cleanup_test_models(user=Depends(verify_session)):
    """Clean up all test models created by the comprehensive test"""

    cleanup_results = {
        "success": True,
        "deleted": {"chats": 0, "messages": 0, "documents": 0, "files": 0, "chunks": 0},
        "errors": [],
    }

    try:
        async with Prisma() as db:
            logger.info("=== STARTING CLEANUP ===")

            # Find and delete test chats (cascading will handle messages)
            test_chats = await db.chat.find_many(
                where={"userId": user.id, "name": {"contains": "Test"}}
            )

            for chat in test_chats:
                # Count messages before deletion
                message_count = await db.message.count(where={"chatId": chat.id})

                await db.chat.delete(where={"id": chat.id})
                cleanup_results["deleted"]["chats"] += 1
                cleanup_results["deleted"]["messages"] += message_count
                logger.info(f"Deleted chat {chat.id} with {message_count} messages")

            # Find and delete test documents
            test_documents = await db.document.find_many(
                where={"title": {"contains": "Test Document"}}
            )

            for document in test_documents:
                # Count related entities before deletion
                chunk_count = await db.documentchunk.count(
                    where={"documentId": document.id}
                )
                file_count = await db.file.count(where={"documentId": document.id})

                # Delete chunks first
                await db.documentchunk.delete_many(where={"documentId": document.id})
                cleanup_results["deleted"]["chunks"] += chunk_count

                # Delete files
                await db.file.delete_many(where={"documentId": document.id})
                cleanup_results["deleted"]["files"] += file_count

                # Delete document
                await db.document.delete(where={"id": document.id})
                cleanup_results["deleted"]["documents"] += 1

                logger.info(
                    f"Deleted document {document.id} with {chunk_count} chunks and {file_count} files"
                )

    except Exception as e:
        error_msg = f"Cleanup failed: {str(e)}"
        logger.error(error_msg)
        cleanup_results["errors"].append(error_msg)
        cleanup_results["success"] = False

    logger.info("=== CLEANUP SUMMARY ===")
    logger.info(f"Chats deleted: {cleanup_results['deleted']['chats']}")
    logger.info(f"Messages deleted: {cleanup_results['deleted']['messages']}")
    logger.info(f"Documents deleted: {cleanup_results['deleted']['documents']}")
    logger.info(f"Files deleted: {cleanup_results['deleted']['files']}")
    logger.info(f"Chunks deleted: {cleanup_results['deleted']['chunks']}")

    return cleanup_results
