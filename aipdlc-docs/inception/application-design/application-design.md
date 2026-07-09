# Application Design — RAG Exam Preparation Chatbot

**Document Version**: 1.0  
**Date**: 2026-07-09  
**Architecture Style**: Layered (frontend, API, backend)  
**Design Approach**: Monolithic for PoC; optimized for simplicity

---

## Executive Summary

This document consolidates the high-level application design for a RAG (Retrieval-Augmented Generation) chatbot for exam preparation. The system follows a **layered architecture** with clear separation of concerns:

- **Frontend Layer**: Web UI for PDF upload and chat
- **API Layer**: REST endpoints for client communication
- **Backend Services**: PDF processing, embeddings, vector search, answer generation
- **System Services**: Session management, error handling

**Key Design Decisions**:
1. Layered architecture for clear separation of frontend, API, and backend
2. Monolithic design for PoC simplicity (no microservices)
3. Direct instantiation of components (minimal abstraction)
4. Simple, stateless services where possible
5. Session-based state management for PDF and embeddings

**Target Audience**: Developers implementing Stories 1.1–1.7

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│               WEB INTERFACE (Frontend)                   │
│              [React/Vue/Vanilla JS]                     │
│         (PDF Upload, Chat UI, Citations)               │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────┐
│          REST API LAYER (HTTP Gateway)                  │
│    POST /upload  |  POST /query  |  GET /status        │
└──┬────────────────────────────────────────┬─────────────┘
   │                                        │
   ▼                                        ▼
┌──────────────────┐              ┌─────────────────────┐
│  PDF Ingestion   │              │   RAG Pipeline      │
│    Service       │              │     Service         │
│                  │              │                     │
│ • Validate       │              │ • Embed question    │
│ • Extract text   │              │ • Search vectors    │
│ • Get metadata   │              │ • Retrieve chunks   │
└────────┬─────────┘              │ • Generate answer   │
         │                        │ • Extract citations │
         ▼                        └──────────┬──────────┘
┌──────────────────────────────────────────┘
│
├─→ Embedding Service
│    • Chunk text
│    • Generate embeddings
│
├─→ Vector Store Service (Qdrant)
│    • Initialize in-memory DB
│    • Store embeddings
│    • Search vectors
│
├─→ Session Manager
│    • Create sessions
│    • Store session data
│    • Manage lifecycle
│
└─→ Answer Generator
     • Call Claude API
     • Extract citations
     • Format response

Error Handler (Utility)
 └─→ Catch exceptions
 └─→ Log errors
 └─→ Format error responses
```

---

## Components Overview

### Backend Components (9 total)

#### Data Processing
1. **PDF Processor** — Validates, extracts text from PDFs
2. **Embedding Engine** — Chunks text, generates vectors
3. **Vector Store Client** — Manages Qdrant in-memory DB

#### RAG Pipeline
4. **RAG Retriever** — Semantic search, retrieves context
5. **Answer Generator** — LLM integration, citations

#### API & Frontend
6. **REST API Layer** — HTTP routing, orchestration
7. **Web Interface** — Frontend for upload/chat

#### System Services
8. **Session Manager** — Session lifecycle, in-memory storage
9. **Error Handler** — Centralized error management

---

## Key Design Principles

### 1. Separation of Concerns
Each component has single, well-defined responsibility:
- PDF Processor: PDF handling only
- Embedding Engine: Text chunking and embeddings only
- Vector Store: Vector storage and search only
- Answer Generator: LLM integration only

### 2. Layered Architecture
Clear layer separation:
- **Presentation** (Web UI) — Standalone; communicates via HTTP
- **API** (REST endpoints) — Routes requests to services
- **Business Logic** (Services) — Core RAG functionality
- **Utilities** (Error handler, logging) — Cross-cutting concerns

### 3. Stateless Services
Most services are stateless:
- RAG Retriever: Accepts input, returns output
- Answer Generator: Takes context, returns answer
- Embedding Engine: Takes text, returns vectors

**Stateful**: Only Session Manager maintains session state

### 4. Simple Dependencies
- Direct instantiation where possible
- No complex DI containers
- Clear, explicit dependencies in constructors

### 5. Minimal Abstraction for PoC
- No interfaces unless needed for mocking
- Concrete classes over abstract interfaces
- Pragmatic design over architectural purity

---

## Detailed Component Specifications

See individual design documents for detailed specifications:

### [components.md](components.md)
High-level component responsibilities, inputs/outputs, lifecycle

### [component-methods.md](component-methods.md)
Method signatures, parameters, return types, exceptions

### [services.md](services.md)
Service definitions, interactions, orchestration patterns

### [component-dependency.md](component-dependency.md)
Dependencies, communication patterns, data flow, coupling analysis

---

## Request Flows

### Flow 1: PDF Upload (Story 1.1)

```
User Action: Upload PDF
    ↓
HTTP POST /upload (file)
    ↓
API Layer receives request
    ↓
PDF Processor
  ├─ Validate PDF
  └─ Extract text
    ↓
Return extracted text
    ↓
HTTP 200 Response (ready for next step)
```

**Next Step (Story 1.2)**: Chunk text and generate embeddings

---

### Flow 2: Complete Ingestion (Stories 1.2 → 1.3)

```
Extracted Text (from Flow 1)
    ↓
Embedding Engine
  ├─ Chunk text (configurable chunk size/overlap)
  └─ Generate embeddings for each chunk
    ↓
Return (Chunk, Vector, Metadata) tuples
    ↓
Vector Store Client
  ├─ Initialize Qdrant in-memory collection
  └─ Add vectors with metadata
    ↓
Session Manager
  ├─ Create session object
  ├─ Store embeddings and vector store handle
  └─ Return session_id
    ↓
HTTP 200 Response {session_id, status: "ready"}
    ↓
Client ready to query
```

**Outcome**: Session ready with PDF embeddings stored in Qdrant

---

### Flow 3: Query Processing (Stories 1.4 → 1.5)

```
User Action: Submit question
    ↓
HTTP POST /query {session_id, question}
    ↓
API Layer receives request
    ↓
Session Manager retrieves session data
    ↓
RAG Retriever
  ├─ Embedding Engine: Embed question
  ├─ Vector Store Client: Search for top-K similar chunks
  └─ Return ranked chunks + metadata
    ↓
Answer Generator
  ├─ Format context from chunks
  ├─ Call Claude API with system prompt + context + question
  ├─ Parse response for answer and citations
  └─ Extract citation references
    ↓
HTTP 200 Response {answer, citations, sources}
    ↓
Web Interface displays answer with highlighted citations
```

**Outcome**: User gets accurate answer grounded in PDF content

---

## Technology Stack Decisions

### Core Technologies
- **Language**: Python (backend), JavaScript (frontend)
- **Embedding Model**: TBD during implementation (Claude embeddings or OpenAI)
- **Vector Database**: Qdrant (in-memory)
- **LLM**: Claude API (Anthropic)
- **API Framework**: TBD (Flask or FastAPI)
- **Frontend**: TBD (React, Vue, or vanilla JS)

### Rationale
- **Python**: Well-supported for ML/RAG workloads
- **Qdrant**: Fast in-memory vector search; perfect for PoC
- **Claude API**: High-quality answers; built-in citation support
- **Modular Stack**: Each layer can be replaced later

---

## Data Models

### Session Data (In-Memory)
```python
{
    "session_id": "uuid-string",
    "created_at": "ISO-8601 timestamp",
    "last_activity": "ISO-8601 timestamp",
    "pdf_metadata": {
        "filename": "string",
        "page_count": "integer",
        "upload_size": "integer"
    },
    "pdf_text": "full extracted text",
    "embeddings": [
        {
            "chunk": "text chunk",
            "vector": [float, float, ...],  # embedding vector
            "chunk_index": integer,
            "page": integer,
            "position": integer
        }
    ],
    "vector_store": "qdrant_client_handle",
    "query_history": [
        {
            "question": "user question",
            "answer": "generated answer",
            "citations": ["Page X", "Section Y"],
            "timestamp": "ISO-8601 timestamp"
        }
    ]
}
```

### API Request/Response Models

#### Upload Request
```json
{
    "file": "<binary PDF data>"
}
```

#### Upload Response
```json
{
    "session_id": "abc-123-def",
    "status": "ready",
    "message": "PDF uploaded and processed successfully",
    "pdf_info": {
        "filename": "exam_notes.pdf",
        "pages": 50,
        "chunks": 125
    }
}
```

#### Query Request
```json
{
    "session_id": "abc-123-def",
    "question": "What are the main causes of climate change?"
}
```

#### Query Response
```json
{
    "answer": "According to your document, the main causes are...",
    "citations": [
        "Page 5, Section 2.1: Greenhouse Gas Emissions",
        "Page 12, Section 3: Human Activities"
    ],
    "sources": [
        {
            "chunk": "text excerpt from page 5...",
            "page": 5,
            "section": "2.1",
            "relevance_score": 0.92
        }
    ],
    "query_id": "query-456"
}
```

---

## Error Handling Strategy

### Error Categories

| Category | Examples | HTTP Status | Handling |
|----------|----------|------------|----------|
| **Validation** | Invalid PDF, missing field | 400 Bad Request | Reject request |
| **Session** | Session not found, expired | 404 Not Found | Return error |
| **Processing** | Embedding failure, Qdrant error | 500 Internal | Log + retry |
| **API** | Claude timeout, rate limit | 502 Bad Gateway | Retry + timeout |
| **System** | Out of memory, file I/O | 500 Internal | Log + error |

### Error Response Format
```json
{
    "error": "error_code",
    "message": "Human-readable error message",
    "status_code": 400,
    "timestamp": "ISO-8601 timestamp"
}
```

---

## Performance Considerations

### Current (PoC)
- No performance optimization required
- Accuracy prioritized over speed
- Single-threaded, synchronous processing

### Future Optimizations
- **Batch Embedding**: Generate multiple embeddings in parallel
- **Caching**: Cache question embeddings to avoid re-embedding
- **Async Processing**: Use async/await for LLM calls
- **Reranking**: Multi-pass retrieval for better results
- **Indexing**: Optimize vector search with indexing strategies

---

## Security Considerations (PoC)

### Current Approach
- Security baseline rules disabled for PoC
- No authentication/authorization
- No encryption
- No rate limiting

### Future Enhancement
- API authentication (API keys)
- Input validation (sanitize PDFs, questions)
- Rate limiting (per session)
- Audit logging (track queries, answers)
- Data privacy (anonymize, purge old sessions)

---

## Testing Strategy

### Unit Testing
- Test each component in isolation
- Mock external dependencies (Claude API, Qdrant)
- Test error paths

### Integration Testing
- Test component interactions (e.g., RAG Retriever + Answer Generator)
- Test full flows (upload → query → answer)
- Test with sample PDFs

### E2E Testing (Story 1.7)
- Test complete flow: upload PDF → submit question → get answer + citations
- Validate answer accuracy against ground truth
- Validate citation correctness

---

## Implementation Roadmap

### Story 1.1: PDF Upload & Text Extraction
- Implement PDF Processor component
- Create /upload API endpoint
- Validate PDF handling

### Story 1.2: Text Chunking & Embedding
- Implement Embedding Engine
- Integrate embedding model
- Test embedding quality

### Story 1.3: Qdrant Integration
- Implement Vector Store Client
- Initialize in-memory Qdrant
- Implement Session Manager
- Store embeddings

### Story 1.4: RAG Retrieval
- Implement RAG Retriever
- Test semantic search
- Validate chunk ranking

### Story 1.5: Answer Generation
- Implement Answer Generator
- Integrate Claude API
- Develop prompt engineering
- Extract and format citations

### Story 1.6: Web Interface
- Build frontend (framework TBD)
- Implement upload UI
- Implement chat interface
- Display citations

### Story 1.7: Integration & Testing
- Wire all components together
- Implement /query endpoint
- Add error handling
- Comprehensive E2E testing
- Documentation

---

## Next Phase

This Application Design document completes the Inception phase. The next phase is:

### Functional Design (CONSTRUCTION Phase)
Detailed algorithms and business logic for:
- Text chunking strategy (fixed-size, sliding window, or sentence-based)
- Embedding generation specifics
- LLM prompt engineering
- Citation extraction logic
- Error handling details
- Performance optimization

**Trigger**: Code generation will reference Functional Design specifications

---

## References

- [components.md](components.md) — Detailed component specifications
- [component-methods.md](component-methods.md) — Method signatures and interfaces
- [services.md](services.md) — Service layer and orchestration
- [component-dependency.md](component-dependency.md) — Dependencies and communication
- [requirements.md](../requirements/requirements.md) — Functional requirements
- [stories.md](../user-stories/stories.md) — User stories
- [dependency-graph.yml](../dependency-graph.yml) — Story dependencies and waves

---

**Status**: ✅ Ready for Functional Design  
**Next Step**: Proceed to Functional Design stage
