# তুখোড় RAG API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints require authentication via session cookies. The system uses Supabase authentication middleware with automatic user profile creation.

## RAG Endpoints

### 1. Ask Question

**POST** `/rag/ask`

Ask a question in Bengali or English and get an AI-generated response using the RAG pipeline.

**Request Body:**

```json
{
    "question": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?",
    "chat_id": "optional_chat_id",
    "document_ids": ["doc1", "doc2"],
    "include_history": true
}
```

**Response:**

```json
{
    "answer": "শুম্ভনাথ",
    "sources": [
        {
            "id": "chunk_123",
            "content": "অনুপমের ভাষায় সুপুরুষ হল শুম্ভনাথ...",
            "similarity": 0.95,
            "document_title": "HSC26 Bangla 1st Paper",
            "chunk_index": 42,
            "metadata": {
                "page": 15,
                "language": "bn"
            }
        }
    ],
    "confidence": 0.89,
    "response_time": 2.34,
    "language": "bn",
    "chunks_retrieved": 5,
    "chat_id": "chat_abc123",
    "created_new_chat": true,
    "approach_used": "rag"
}
```

**Approach Types:**

-   `rag`: Used RAG pipeline with document context
-   `fallback`: Used general knowledge (low document similarity)
-   `error_fallback`: Fallback due to system error

### 2. Submit Feedback

**POST** `/rag/feedback`

Submit user feedback for a response to improve system performance.

**Request Body:**

```json
{
    "message_id": "msg_123",
    "feedback": "helpful"
}
```

**Feedback Values:** `helpful`, `not_helpful`, `partial`

**Response:**

```json
{
    "message": "Feedback submitted successfully"
}
```

### 3. Get Evaluation Statistics

**GET** `/rag/evaluation/stats`

Get evaluation statistics for system performance monitoring.

**Response:**

```json
{
    "total_responses": 1250,
    "average_confidence": 0.82,
    "average_response_time": 2.45,
    "language_distribution": {
        "bn": 890,
        "en": 360
    },
    "approach_distribution": {
        "rag": 1120,
        "fallback": 130
    },
    "feedback_summary": {
        "helpful": 890,
        "not_helpful": 45,
        "partial": 125
    }
}
```

## Chat Management Endpoints

### 1. Send Message

**POST** `/chat/message`

Enhanced chat endpoint with RAG integration and file upload support.

**Request (multipart/form-data):**

```
content: "অনুপমের চরিত্র সম্পর্কে বলুন"
chat_id: "optional_chat_id"
files: [file1.pdf, file2.txt]
```

**Response:**

```json
{
    "message": {
        "content": "অনুপম একটি জটিল চরিত্র...",
        "role": "ai",
        "created_at": "2024-01-15T10:30:00Z"
    },
    "rag_metadata": {
        "approach": "rag",
        "chunks_used": 5,
        "max_similarity": 0.89,
        "language": "bn"
    },
    "chat_id": "chat_123",
    "created_new_chat": false
}
```

### 2. Get User Chats

**GET** `/chat/`

Get all chat sessions for the current user.

**Response:**

```json
[
    {
        "id": "chat_123",
        "name": "অনুপমের চরিত্র বিশ্লেষণ",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T11:30:00Z",
        "message_count": 15
    }
]
```

### 3. Get Chat Messages

**GET** `/chat/{chat_id}/messages?limit=50`

Get messages for a specific chat session.

**Response:**

```json
{
    "messages": [
        {
            "id": "msg_123",
            "content": "অনুপমের চরিত্র সম্পর্কে বলুন",
            "role": "user",
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": "msg_124",
            "content": "অনুপম একটি জটিল চরিত্র...",
            "role": "ai",
            "created_at": "2024-01-15T10:30:15Z",
            "rag_metadata": {
                "chunks_used": 5,
                "confidence": 0.89
            }
        }
    ],
    "chat_id": "chat_123"
}
```

### 4. Delete Chat

**DELETE** `/chat/{chat_id}`

Delete a chat session and all associated messages.

**Response:**

```json
{
    "message": "Chat deleted successfully"
}
```

## Document Management Endpoints

### 1. Upload Document

**POST** `/documents/upload`

Upload and process a document for RAG with automatic language detection and chunking.

**Request (multipart/form-data):**

```
file: document.pdf
```

**Response:**

```json
{
    "document_id": "doc_123",
    "filename": "bangla_literature.pdf",
    "language": "bn",
    "chunk_count": 45,
    "word_count": 12500,
    "page_count": 25,
    "file_url": "https://storage.supabase.co/object/public/documents/..."
}
```

### 2. List User Documents

**GET** `/documents/`

Get all documents uploaded by the current user.

**Response:**

```json
{
    "documents": [
        {
            "id": "doc_123",
            "title": "bangla_literature",
            "language": "bn",
            "word_count": 12500,
            "page_count": 25,
            "chunk_count": 45,
            "created_at": "2024-01-15T10:00:00Z",
            "file": {
                "id": "file_456",
                "filename": "bangla_literature.pdf",
                "type": "pdf",
                "size": 2048576,
                "url": "https://storage.supabase.co/..."
            }
        }
    ],
    "total_count": 1
}
```

### 3. Get Document Details

**GET** `/documents/{document_id}`

Get detailed information about a specific document including chunk preview.

**Response:**

```json
{
    "id": "doc_123",
    "title": "bangla_literature",
    "content_preview": "এই ডকুমেন্টে বাংলা সাহিত্যের...",
    "language": "bn",
    "metadata": {
        "page_count": 25,
        "author": "Unknown",
        "title": "Bangla Literature",
        "creator": "PyMuPDF"
    },
    "word_count": 12500,
    "created_at": "2024-01-15T10:00:00Z",
    "file": {
        "filename": "bangla_literature.pdf",
        "size": 2048576,
        "url": "https://storage.supabase.co/..."
    },
    "chunks_preview": [
        {
            "id": "chunk_789",
            "content_preview": "বাংলা সাহিত্যে অনুপম একটি...",
            "chunk_index": 0,
            "token_count": 150
        }
    ]
}
```

### 4. Delete Document

**DELETE** `/documents/{document_id}`

Delete a document and all associated chunks from vector store.

**Response:**

```json
{
    "message": "Document and 45 chunks deleted successfully"
}
```

### 5. Initialize Knowledge Base

**POST** `/documents/initialize-kb`

Initialize the knowledge base with the predefined HSC Bengali literature document.

**Response:**

```json
{
    "message": "Knowledge base initialization completed",
    "result": {
        "status": "initialized",
        "document_id": "kb_doc_123",
        "chunk_count": 234,
        "total_words": 45000,
        "total_pages": 120,
        "language": "bn"
    }
}
```

### 6. Get Document Statistics

**GET** `/documents/stats/overview`

Get overview statistics for all user documents.

**Response:**

```json
{
    "total_documents": 5,
    "total_chunks": 278,
    "total_words": 67500,
    "language_distribution": {
        "bn": 3,
        "en": 1,
        "mixed": 1
    },
    "storage_used": "15.2 MB"
}
```

### 7. Batch Upload Documents

**POST** `/documents/batch-upload`

Upload multiple documents simultaneously.

**Request (multipart/form-data):**

```
files: [file1.pdf, file2.txt, file3.pdf]
```

**Response:**

```json
{
    "results": [
        {
            "filename": "file1.pdf",
            "status": "success",
            "document_id": "doc_124"
        },
        {
            "filename": "file2.txt",
            "status": "error",
            "error": "Unsupported file type"
        }
    ],
    "successful": 1,
    "failed": 1
}
```

## System Management Endpoints

### 1. Initialize System

**POST** `/system/initialize`

Initialize the entire RAG system including knowledge base and vector store.

**Response:**

```json
{
    "message": "System initialization completed successfully",
    "knowledge_base_status": {
        "status": "initialized",
        "document_id": "kb_doc_123",
        "chunk_count": 234,
        "language": "bn"
    },
    "vector_store_stats": {
        "total_chunks": 234,
        "total_documents": 1,
        "language_distribution": {
            "bn": 1
        }
    },
    "system_ready": true
}
```

### 2. Get System Status

**GET** `/system/status`

Get current system status and configuration parameters.

**Response:**

```json
{
    "system_ready": true,
    "vector_store_stats": {
        "total_chunks": 234,
        "total_documents": 1,
        "language_distribution": {
            "bn": 1
        }
    },
    "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "chunk_settings": {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "top_k_chunks": 5
    },
    "similarity_threshold": 0.3,
    "high_confidence_threshold": 0.7
}
```

### 3. Health Check

**GET** `/system/health`

Comprehensive health check for all system components.

**Response:**

```json
{
    "overall": "healthy",
    "components": {
        "database": "healthy",
        "vector_store": "healthy",
        "embedding_service": "healthy",
        "knowledge_base": "healthy",
        "gemini_api": "healthy"
    },
    "performance": {
        "avg_response_time": 2.45,
        "embedding_dimension": 384,
        "total_memory_usage": "1.2 GB"
    }
}
```

### 4. Delete Knowledge Base

**DELETE** `/system/knowledge-base`

Delete the knowledge base and all associated vector data.

**Response:**

```json
{
    "message": "Knowledge base deleted successfully",
    "status": "deleted",
    "document_id": "kb_doc_123",
    "chunks_deleted": 234
}
```

## Profile Management Endpoints

### 1. Get Profile

**GET** `/profile/`

Get current user's profile information.

**Response:**

```json
{
    "id": "profile_123",
    "userId": "user_456",
    "userName": "রহিম উদ্দিন",
    "email": "rahim@example.com",
    "image": "https://avatar.url/image.jpg",
    "createdAt": "2024-01-15T10:00:00Z",
    "updatedAt": "2024-01-15T11:30:00Z"
}
```

### 2. Update Profile

**PUT** `/profile/`

Update user profile information.

**Request Body:**

```json
{
    "userName": "নতুন নাম",
    "image": "https://new-avatar.url/image.jpg"
}
```

**Response:**

```json
{
    "id": "profile_123",
    "userId": "user_456",
    "userName": "নতুন নাম",
    "email": "rahim@example.com",
    "image": "https://new-avatar.url/image.jpg",
    "updatedAt": "2024-01-15T12:00:00Z"
}
```

### 3. Get Profile Statistics

**GET** `/profile/stats`

Get user activity statistics.

**Response:**

```json
{
    "total_chats": 15,
    "total_messages": 245,
    "documents_uploaded": 5,
    "favorite_language": "bn",
    "avg_session_length": "25 minutes",
    "most_active_topic": "বাংলা সাহিত্য"
}
```

### 4. Delete Profile

**DELETE** `/profile/`

Delete user profile and all associated data.

**Response:**

```json
{
    "message": "Profile and all associated data deleted successfully"
}
```

## Error Responses

### Standard HTTP Status Codes

#### 400 Bad Request

```json
{
    "detail": "Invalid file type. Supported formats: PDF, TXT"
}
```

#### 401 Unauthorized

```json
{
    "detail": "Not authenticated"
}
```

#### 403 Forbidden

```json
{
    "detail": "Access denied. Chat belongs to different user."
}
```

#### 404 Not Found

```json
{
    "detail": "Chat not found"
}
```

#### 413 Payload Too Large

```json
{
    "detail": "File size exceeds maximum limit of 10MB"
}
```

#### 422 Unprocessable Entity

```json
{
    "detail": "Invalid feedback type. Must be: helpful, not_helpful, or partial"
}
```

#### 429 Too Many Requests

```json
{
    "detail": "Rate limit exceeded. Please try again later."
}
```

#### 500 Internal Server Error

```json
{
    "detail": "Error processing document: PDF extraction failed"
}
```

## Usage Examples

### Bengali Question with RAG

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ask" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_cookie" \
  -d '{
    "question": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?",
    "include_history": true
  }'
```

### English Question with Document Filter

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ask" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_cookie" \
  -d '{
    "question": "Who is the main character in the story?",
    "chat_id": "chat_123",
    "document_ids": ["doc_456"]
  }'
```

### Upload Document with Progress

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Cookie: session=your_session_cookie" \
  -F "file=@bengali_literature.pdf" \
  --progress-bar
```

### Chat with File Upload

```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Cookie: session=your_session_cookie" \
  -F "content=এই ডকুমেন্ট সম্পর্কে আমাকে বলুন" \
  -F "files=@new_document.pdf"
```

### Initialize System

```bash
curl -X POST "http://localhost:8000/api/v1/system/initialize" \
  -H "Content-Type: application/json"
```

### System Health Check

```bash
curl -X GET "http://localhost:8000/api/v1/system/health"
```

## Rate Limits

Rate limits are applied per user and are configurable:

-   **RAG queries**: 10 requests per minute
-   **Document uploads**: 5 uploads per minute
-   **Chat messages**: 20 messages per minute
-   **General API calls**: 100 requests per minute

## Performance Metrics

### Response Times (Typical)

-   **Simple RAG queries**: 1-3 seconds
-   **Complex RAG queries**: 3-8 seconds
-   **Document upload + processing**: 10-60 seconds
-   **Knowledge base initialization**: 2-5 minutes
-   **System health check**: < 1 second

### Accuracy Metrics

-   **Bengali query accuracy**: ~92%
-   **English query accuracy**: ~89%
-   **Document retrieval precision**: ~87%
-   **Language detection accuracy**: ~96%

## Configuration

### Supported File Types

-   **PDF**: Text extraction with PyMuPDF
-   **TXT**: Direct text processing
-   **Maximum size**: 10MB per file
-   **Batch upload**: Up to 5 files simultaneously

### Language Support

-   **Bengali (বাংলা)**: Full support with specialized text processing
-   **English**: Full support
-   **Mixed**: Automatic detection and appropriate processing

### Vector Store Configuration

-   **Embedding model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
-   **Embedding dimension**: 384
-   **Similarity metric**: Cosine similarity
-   **Chunk size**: 500 characters
-   **Chunk overlap**: 50 characters
-   **Top-K retrieval**: 5 chunks

### LLM Configuration

-   **Primary model**: Google Gemini 2.5 Flash
-   **Fallback models**: Gemini 1.5 Pro, Gemini 1.5 Flash
-   **Context window**: Up to 1M tokens
-   **Response languages**: Bengali, English (auto-detected)


## API Versioning

-   **Current version**: v1
-   **Base path**: `/api/v1`
