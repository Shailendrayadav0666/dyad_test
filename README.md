# RAG Exam Preparation Chatbot

A retrieval-augmented generation (RAG) chatbot that helps university students prepare for exams by answering questions based on PDF course materials.

## Features

- **PDF Upload**: Drag-and-drop or click to upload a PDF study document
- **Smart Retrieval**: Semantic search over document content using vector embeddings
- **Accurate Answers**: Claude-powered answer generation grounded in source materials
- **Source Citations**: Every answer includes relevance-scored citations from the document
- **Session Management**: In-memory per-session state for quick interactive use

## Project Status

✅ **Complete (PoC/MVP)** - Fully functional RAG chatbot  
**Version**: 1.0.0 (2026-07-09)

## Architecture

### Technology Stack

- **Backend**: FastAPI + uvicorn
- **PDF Processing**: pdfplumber (text extraction)
- **Vector Embeddings**: sentence-transformers `all-MiniLM-L6-v2` (384-dimensional)
- **Vector Store**: Qdrant (in-memory)
- **LLM**: Claude `claude-opus-4-8` via Anthropic SDK
- **Frontend**: React 18 + Vite

### Components

1. **PDF Processor** (`backend/components/pdf_processor.py`)
   - Validates PDF files
   - Extracts readable text
   - Retrieves metadata

2. **Embedding Engine** (`backend/components/embedding_engine.py`)
   - Chunks text into fixed-size segments (512 characters, 50-char overlap)
   - Generates vector embeddings (sentence-transformers, 384-dimensional)
   - Handles text processing and embedding generation

3. **Vector Store** (`backend/components/vector_store.py`)
   - In-memory Qdrant database for vector storage
   - Stores embeddings with metadata (chunk text, size, model)
   - Semantic search via cosine similarity
   - Per-session collections for isolation

4. **RAG Retriever** (`backend/components/rag_retriever.py`)
   - Converts user queries to embeddings
   - Searches vector store for similar chunks
   - Formats results with relevance scores
   - Prepares context for LLM answer generation

5. **Answer Generator** (`backend/components/answer_generator.py`)
   - Calls Claude API with RAG context
   - Generates grounded answers based on PDF content
   - Extracts and formats citations from answer
   - Validates answer quality

6. **Session Manager** (`backend/components/session_manager.py`)
   - Creates and manages sessions
   - Stores session data in-memory (PDF text, embeddings, vector store refs)
   - Handles session lifecycle

7. **API Layer** (`backend/api/routes.py`)
   - POST `/upload` - Upload, extract, chunk, embed, and store in Qdrant
   - GET `/status/<session_id>` - Get session status
   - POST `/query` - Submit question and retrieve context
   - POST `/answer` - Generate answer with citations

4. **Frontend** (`frontend-react/`)
   - React 18 + Vite dev server
   - Drag-and-drop upload zone
   - Chat interface with typing indicator and citation panel

## Setup & Installation

### Prerequisites

- Python 3.11 (3.13 has limited pdfplumber support)
- Node.js 18+
- An Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd rag-pdlc
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env — set ANTHROPIC_API_KEY and PORT=5000
   ```

5. **Install frontend dependencies**
   ```bash
   cd frontend-react
   npm install
   ```

### Running the App

Open two terminals from the project root.

#### Terminal 1 — FastAPI backend

```bash
python -m backend.main
```

Server starts on `http://localhost:5000`.

#### Terminal 2 — React dev server

```bash
cd frontend-react
npm run dev
```

UI is available at `http://localhost:5173` (proxied to the backend automatically).

## Usage

### As a Student

1. **Upload Course Material**
   - Navigate to the web interface
   - Drag-and-drop a PDF or click to select
   - Wait for processing (text extraction)

2. **Ask Questions**
   - Type your question in the chat box
   - Click "Send" or press Ctrl+Enter
   - Receive an answer with source citations

### API Usage

#### Upload PDF
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/api/upload
```

Response:
```json
{
  "session_id": "uuid-123",
  "status": "ready",
  "pdf_info": {
    "filename": "document.pdf",
    "pages": 50,
    "extracted_characters": 125000
  }
}
```

#### Get Session Status
```bash
curl http://localhost:5000/api/status/uuid-123
```

#### Query & Retrieve Context
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"session_id": "uuid-123", "query": "What is photosynthesis?"}' \
  http://localhost:5000/api/query
```

Response:
```json
{
  "session_id": "uuid-123",
  "query": "What is photosynthesis?",
  "status": "success",
  "chunks_retrieved": 5,
  "context_chunks": [
    {
      "rank": 1,
      "chunk_text": "Photosynthesis is the process...",
      "similarity_score": 0.9234,
      "chunk_size": 512
    }
  ],
  "context_string": "[#1, score=0.9234]\nPhotosynthesis is the process...\n---\n[#2, score=0.8891]..."
}
```

#### Generate Answer with Citations
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"session_id": "uuid-123", "query": "What is photosynthesis?"}' \
  http://localhost:5000/api/answer
```

Response:
```json
{
  "session_id": "uuid-123",
  "query": "What is photosynthesis?",
  "status": "success",
  "answer": "Photosynthesis is the process by which plants convert light energy into chemical energy...",
  "citations": [
    {
      "source_rank": 1,
      "chunk_text": "Photosynthesis is the process...",
      "similarity_score": 0.9234
    }
  ],
  "chunks_used": 5
}
```

## Running Tests

### Integration Tests

```bash
cd tests
python test_integration.py
```

Expected output: All 7 tests pass (text chunking, embeddings, storage, search, RAG retrieval, session management, error handling)

### Manual API Testing

See `TESTING.md` for comprehensive testing guide including:
- API endpoint examples (curl commands)
- Web UI testing procedures
- Performance benchmarks
- Error scenario testing
- End-to-end workflow validation

## Documentation

- **README.md** — This file (user guide)
- **TESTING.md** — Comprehensive testing guide
- **PROJECT_SUMMARY.md** — Technical architecture and project details
- **Source code** — Inline documentation and docstrings

## Development Progress

### Story 1.1: PDF Upload & Text Extraction ✅
- [x] PDFProcessor component (validate, extract_text, get_metadata)
- [x] SessionManager component (in-memory session storage)
- [x] /upload API endpoint (multipart form-data)
- [x] /status API endpoint (session status retrieval)
- [x] Frontend upload UI (drag-drop + file selection)
- [x] Flask application setup (5000 port, 50MB max)

### Story 1.2: Text Chunking & Vector Embedding Generation ✅
- [x] EmbeddingEngine component (chunk_text, generate_embeddings, process)
- [x] Fixed-size text chunking (512 characters, 50-character overlap)
- [x] Sentence-transformers embeddings (all-MiniLM-L6-v2, 384-dimensional)
- [x] Batch embedding generation (batch size 32)
- [x] Integration with /upload endpoint
- [x] Embedding storage in session

### Story 1.3: Qdrant Integration & Vector Storage ✅
- [x] VectorStore component (create_collection, store_embeddings, search)
- [x] In-memory Qdrant instance initialization
- [x] Per-session collection creation
- [x] Embedding storage with metadata (chunk text, size, model)
- [x] Cosine similarity search (top-K retrieval)
- [x] Integration with /upload endpoint
- [x] Collection info tracking

### Story 1.4: RAG Retrieval & Context Search ✅
- [x] RAGRetriever component (retrieve_context, get_context_string)
- [x] Query embedding via sentence-transformers
- [x] Vector store similarity search (top-5 chunks)
- [x] Context formatting with relevance scores
- [x] POST /query endpoint implementation
- [x] Query history tracking in session
- [x] Result validation

### Story 1.5: LLM-Based Answer Generation with Citations ✅
- [x] AnswerGenerator component (generate_answer, extract_citations)
- [x] Claude API integration (Anthropic SDK)
- [x] RAG prompt template with context injection
- [x] Citation extraction and formatting
- [x] POST /answer endpoint implementation
- [x] Answer validation
- [x] Citation tracking in response

### Story 1.6: Web Interface — PDF Upload & Chat UI ✅
- [x] Frontend chat interface updates (handleSubmitQuestion)
- [x] API integration with /answer endpoint
- [x] Answer display with citations in chat
- [x] Citation formatting with relevance scores
- [x] Message history persistence (localStorage)
- [x] Session restoration on page reload
- [x] CSS styling for citations section
- [x] Loading states and error handling

### Story 1.7: API Integration & End-to-End Testing ✅
- [x] Python integration test suite (7 test cases)
- [x] API endpoint validation tests
- [x] End-to-end workflow testing
- [x] Error handling and edge case testing
- [x] TESTING.md with complete test procedures
- [x] Test curl examples for all endpoints
- [x] Known limitations and constraints documented
- [x] Troubleshooting guide for common issues

### Story 1.4: RAG Retrieval (Planned)
- [ ] Implement semantic search
- [ ] Retrieve top-K relevant chunks
- [ ] Format context for LLM

### Story 1.5: Answer Generation (Planned)
- [ ] Integrate Claude API
- [ ] Implement prompt engineering
- [ ] Extract citations from response
- [ ] Format answer with citations

### Story 1.6: Web Interface (Planned)
- [ ] Complete chat UI
- [ ] Display answers with citations
- [ ] Improve UX/responsiveness

### Story 1.7: Integration & Testing (Planned)
- [ ] Wire all components together
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation

## Configuration

### Environment Variables

```env
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
UPLOAD_FOLDER=/tmp/uploads

# Claude API (Story 1.5+)
ANTHROPIC_API_KEY=sk-...

# Qdrant (Story 1.3+)
QDRANT_URL=http://localhost:6333
```

### Application Settings

- **Max Upload Size**: 50 MB
- **PDF Chunk Size**: 512 characters (Story 1.2)
- **Embedding Dimension**: 384 (sentence-transformers)
- **Top-K Results**: 5 chunks (Story 1.4)
- **Session Storage**: In-memory (ephemeral)

## Testing

### Manual Testing (Story 1.1)

1. **Test PDF Upload**
   ```bash
   # Upload a test PDF
   curl -X POST -F "file=@test.pdf" http://localhost:5000/api/upload
   ```

2. **Test Invalid File**
   ```bash
   # Should return 400 error
   curl -X POST -F "file=@test.txt" http://localhost:5000/api/upload
   ```

3. **Test Session Status**
   ```bash
   curl http://localhost:5000/api/status/{session_id}
   ```

### Automated Tests (Future)
- Unit tests for PDFProcessor
- Integration tests for API endpoints
- E2E tests for upload flow

## Known Limitations

- **PoC Stage**: Simplified for proof-of-concept
- **No Persistence**: Sessions are in-memory (data lost on app restart)
- **Single File**: Only one PDF per session (Story 1.2+: multi-document support)
- **No Authentication**: Open access (Story 1.6+: add auth)
- **No Rate Limiting**: Unlimited requests (future: add rate limiting)

## Future Enhancements

- [ ] Multi-document support
- [ ] Conversation history across sessions
- [ ] Answer quality feedback/rating
- [ ] User authentication
- [ ] Document library/persistence
- [ ] Advanced search (semantic + keyword hybrid)
- [ ] Follow-up question support
- [ ] Performance optimization (caching, batching)

## Architecture & Design

See the design documents in `aipdlc-docs/`:
- **Application Design**: `aipdlc-docs/inception/application-design/`
- **Functional Design**: `aipdlc-docs/construction/design/functional-design/`
- **Requirements**: `aipdlc-docs/inception/requirements/`

## Contributing

This project follows the AI-PDLC (Adaptive Product Development Lifecycle) workflow. For development:

1. Check `aipdlc-docs/aipdlc-state.md` for current story status
2. Select a story from the current ready wave
3. Review the story acceptance criteria
4. Follow the code generation plan
5. Submit for review

## Support

For questions or issues:
- Check the documentation in `aipdlc-docs/`
- Review design artifacts for implementation details
- File a bug or feature request in the project tracker

## License

[To be determined]

---

**Last Updated**: 2026-07-09  
**Current Stage**: Story 1.1 Complete - Proceeding to Story 1.2
