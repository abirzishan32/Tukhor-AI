# তুখোড় RAG System

## 🎯 Overview

তুখোড় is a comprehensive Bengali-English RAG (Retrieval-Augmented Generation) system built with:

-   **Backend**: FastAPI with Python
-   **Frontend**: Next.js with TypeScript
-   **Database**: PostgreSQL with Prisma ORM
-   **Vector Store**: pgvector for similarity search
-   **LLM**: Google Gemini Pro
-   **Embeddings**: Multilingual sentence transformers
-   **Storage**: Supabase for file storage

## 🏗️ Architecture

### Core Components

1. **Document Processing Pipeline**

    - PDF text extraction with PyMuPDF
    - Bengali text cleaning and normalization
    - Intelligent chunking with overlap
    - Multilingual embedding generation

2. **Vector Store**

    - PostgreSQL with pgvector extension
    - Cosine similarity search
    - Metadata filtering and language detection

3. **Memory Management**

    - **Short-term**: Session-based recent message cache
    - **Long-term**: PostgreSQL persistent storage
    - Context-aware conversation handling

4. **RAG Pipeline**

    - Query language detection
    - Semantic similarity search
    - Context-aware prompt generation
    - Gemini Pro response generation

5. **Evaluation System**
    - Groundedness scoring
    - Relevance metrics
    - User feedback collection
    - Performance analytics

## 🚀 Setup Instructions

### Prerequisites

1. **Install Dependencies**

    ```bash
    # Initialize python virtual environment
    python -m venv .venv

    # Activate virtual environment
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

    # Install Server dependencies
    cd apps/server
    pip install -r requirements.txt

    # Install Client dependencies
    cd ../client
    npm install
    ```

2. **Supabase Setup**

    - Create a Supabase project
    - Enable pgvector extension
    - Configure storage bucket for document uploads
    - Use the environment variables from Supabase dashboard

3. **Database Setup**

    ```bash
    # Install pgvector extension ফfrom supabase dashboard
    # or via SQL command
    CREATE EXTENSION IF NOT EXISTS vector;

    ```

4. **Initialize Prisma Client**

    ```bash
    npm run gen
    ```

5. **Environment Configuration**

    ```bash
    # Copy Base environment template
    cp .env.example .env

    # Configure required variables:
    # - DATABASE_URL (PostgreSQL connection string)
    # - DIRECT_URL (Direct database access URL, if applicable)


    # Copy Server environment template
    cp apps/server/.env.example apps/server/.env

    # Configure required variables:
    # - DATABASE_URL
    # - DIRECT_URL
    # - GOOGLE_API_KEY
    # - SUPABASE credentials
    # - KNOWLEDGE_BASE_URL (direct download link for HSC26 Bangla 1st paper PDF)
    

    # Copy Client environment template
    cp apps/client/.env.example apps/client/.env

    # Configure client environment variables:
    # - NEXT_PUBLIC_API_URL (URL of the FastAPI server)
    # - DATABASE_URL
    # - DIRECT_URL (if using direct database access)
    # - NEXT_PUBLIC_SUPABASE_URL
    # - NEXT_PUBLIC_SUPABASE_ANON_KEY

    ```

### Initialization

1. **Start the Server**

    ```bash
    cd apps/server
    uvicorn main:app --reload
    ```

2. **Initialize Knowledge Base**

    ```bash
    # Option 1: API endpoint
    POST /api/v1/system/initialize
    ```

    Or, use the web page

3. **Start the Client**

    ```bash
    cd apps/client
    npm run dev
    ```

## 🧪 Testing

### Bengali Test Cases (From Requirements)

1. **Character Identification**

    - Q: "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?"
    - Expected: "শুম্ভনাথ"

2. **Destiny Reference**

    - Q: "কাকে অনুপমের ভাগ্য দেবতা বলে উল্লেখ করা হয়েছ?"
    - Expected: "মামাকে"

3. **Age Information**
    - Q: "বিয়ের সময় কল্যাণীর প্রকৃত বয়স কত ছিল?"
    - Expected: "১৫ বছর"

### Testing Options

1. **CLI Testing Tool**

    ```bash
    # Run all tests
    python advanced_cli_test.py --mode all --save-results

    # Interactive mode
    python advanced_cli_test.py --mode interactive

    # Test only
    python advanced_cli_test.py --mode test
    ```

2. **API Testing**

    ```bash
    # Test endpoint
    POST /api/v1/rag/ask
    {
      "question": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?",
      "chat_id": null
    }
    ```

3. **System Health Check**

    ```bash
    GET /api/v1/system/health
    GET /api/v1/system/status
    ```

## 🔧 API Endpoints

### RAG Endpoints

- `POST /api/v1/rag/ask` - Main RAG query endpoint
- `GET /api/v1/rag/chats` - Get user's chat sessions
- `GET /api/v1/rag/chats/{chat_id}/history` - Get chat history
- `POST /api/v1/rag/feedback` - Submit user feedback
- `DELETE /api/v1/rag/chats/{chat_id}` - Delete chat session

### Document Management

- `POST /api/v1/documents/upload` - Upload new document
- `GET /api/v1/documents/` - List user documents
- `GET /api/v1/documents/{doc_id}` - Get document details
- `DELETE /api/v1/documents/{doc_id}` - Delete document
- `POST /api/v1/documents/initialize-kb` - Initialize knowledge base

### Chat Management

- `POST /api/v1/chat/` - Create new chat
- `POST /api/v1/chat/{chat_id}/message` - Send message to chat
- `GET /api/v1/chat/{chat_id}` - Get chat details

### System Management

- `POST /api/v1/system/initialize` - Initialize entire system
- `GET /api/v1/system/status` - Get system status
- `GET /api/v1/system/health` - Comprehensive health check
- `DELETE /api/v1/system/knowledge-base` - Delete knowledge base

## 📊 Features Implemented

### ✅ Core Requirements

- [x] Bengali-English bilingual support
- [x] PDF document processing (HSC26 Bangla 1st paper)
- [x] Vector-based document retrieval
- [x] Context-aware response generation
- [x] Long-term and short-term memory
- [x] Multi-session chat support
- [x] Automatic chat title generation

### ✅ Bonus Features

- [x] Comprehensive REST API
- [x] RAG evaluation metrics
- [x] User feedback collection
- [x] Document upload and management
- [x] System health monitoring

### 🎯 Advanced Features

- [x] Language-aware chunking
- [x] Multilingual embeddings
- [x] Conversation context management
- [x] Source attribution
- [x] Confidence scoring
- [x] Performance metrics
- [x] Error handling and logging

## 🔍 RAG Pipeline Details

### 1. Query Processing

```python
# Language detection
query_language = detect_language(question)

# Embedding generation
query_embedding = embedding_service.encode_text(question)
```

### 2. Document Retrieval

```python
# Similarity search with filters
relevant_chunks = vector_store.similarity_search(
    query_embedding=query_embedding,
    top_k=5,
    language_filter=query_language
)
```

### 3. Context Assembly

```python
# Combine document context and conversation history
context = format_context(relevant_chunks)
conversation_context = get_conversation_context(chat_id)
```

### 4. Response Generation

```python
prompt = rag_system_prompt.format(
    context=context,
    conversation_context=conversation_context,
    question=question
)
response = gemini_model.generate_content(prompt)
```

### 5. Evaluation and Storage

```python
# Calculate metrics
confidence = calculate_confidence(chunks, response)
groundedness = calculate_groundedness(response, sources)

# Store interaction
store_message(chat_id, question, response, metadata)
```

## 📈 Performance Considerations

### Optimization Strategies

1. **Embedding Caching**: Cache embeddings for frequently asked questions
2. **Batch Processing**: Process multiple documents simultaneously
3. **Connection Pooling**: Efficient database connections
4. **Async Operations**: Non-blocking I/O for better performance
5. **Vector Indexing**: Proper indexing for similarity search

### Scalability Features

1. **Stateless Design**: Easy horizontal scaling
2. **Background Processing**: Document processing in background
3. **Rate Limiting**: Protection against abuse
4. **Error Recovery**: Robust error handling
5. **Monitoring**: Comprehensive logging and metrics

## 🔧 Configuration

### Key Settings

```python
# RAG Configuration
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_CHUNKS = 5

# LLM Configuration
GEMINI_MODEL = "gemini-2.5-flash"
MAX_RESPONSE_TOKENS = 1000

# Vector Store Configuration
VECTOR_DIMENSION = 384
SIMILARITY_THRESHOLD = 0.5
```

## 🐛 Troubleshooting

### Common Issues

1. **Embedding Model Loading**

    - Ensure sufficient memory (>2GB)
    - Check internet connectivity for model download

2. **Database Connection**

    - Verify PostgreSQL is running
    - Check pgvector extension installation

3. **Gemini API**

    - Validate API key
    - Check quota limits

4. **Bengali Text Processing**
    - Ensure UTF-8 encoding
    - Validate Unicode normalization

### Debug Commands

```bash
# Check system status
curl -X GET "http://localhost:8000/api/v1/system/health"

# Test database connection
curl -X GET "http://localhost:8000/db-status"

# Initialize Knowledge Base system
curl -X POST "http://localhost:8000/api/v1/system/initialize"
```
