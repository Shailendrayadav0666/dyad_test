# Application Components

**Architecture Style**: Layered (backend, frontend, API)  
**Component Organization**: Functional decomposition by service responsibility  
**Scope**: High-level component identification; detailed business logic deferred to Functional Design

---

## Backend Components

### 1. PDF Processor

**Purpose**: Handle PDF document upload, validation, and text extraction  
**Responsibility**:
- Accept PDF file uploads from the API
- Validate PDF format and file integrity
- Extract readable text content from PDF
- Handle errors (corrupted files, unsupported formats)

**Inputs**:
- PDF file (binary)

**Outputs**:
- Extracted text (string)
- Metadata (filename, upload timestamp)

**Lifecycle**: Created per document upload; short-lived (used during extraction phase only)

**Dependencies**: None (external: file system/I/O)

---

### 2. Embedding Engine

**Purpose**: Generate vector embeddings for text chunks  
**Responsibility**:
- Chunk extracted text into manageable segments
- Generate vector embeddings for each chunk
- Track chunk metadata (source position, content)

**Inputs**:
- Extracted text (string)

**Outputs**:
- List of (chunk_text, embedding_vector, metadata)

**Notes**: Monolithic design; text chunking and embedding generation combined in single component for PoC simplicity

**Lifecycle**: Created once per session; persists during Q&A phase

**Dependencies**: Embedding model (Claude embeddings API or similar)

---

### 3. Vector Store Client

**Purpose**: Manage Qdrant in-memory vector database  
**Responsibility**:
- Initialize Qdrant in-memory instance
- Store embeddings with metadata
- Manage collection lifecycle
- Provide retrieval interface

**Inputs**:
- Embeddings (vectors with metadata)

**Outputs**:
- Stored/retrieved embeddings with metadata

**Lifecycle**: Created once per session; destroyed at session end

**Dependencies**: Qdrant client library

---

### 4. RAG Retriever

**Purpose**: Perform semantic search and retrieve relevant context  
**Responsibility**:
- Convert user question to embedding
- Search Qdrant for similar chunks
- Return top-K most relevant chunks
- Include relevance scores and source metadata

**Inputs**:
- User question (string)
- Vector Store Client instance
- K (number of results)

**Outputs**:
- List of (chunk_text, relevance_score, metadata)

**Design**: Simple Query-to-Embedding; straightforward semantic search (no reranking/multi-pass for PoC)

**Lifecycle**: Stateless; created per query

**Dependencies**: Vector Store Client, Embedding Engine (for question embedding)

---

### 5. Answer Generator

**Purpose**: Generate accurate answers with source citations  
**Responsibility**:
- Accept retrieved context chunks and user question
- Call Claude API to generate answer
- Extract and format citations from response
- Return answer + citations

**Inputs**:
- User question (string)
- Retrieved context chunks (list of strings)
- Source metadata (page numbers, sections)

**Outputs**:
- Generated answer (string)
- Formatted citations (list of source references)

**Design**: LLM-Only; Claude generates answer with citations inline; parser extracts citations from response

**Lifecycle**: Stateless; created per query

**Dependencies**: Claude API client

---

## API & Frontend Components

### 6. REST API Layer

**Purpose**: HTTP interface for client communication  
**Responsibility**:
- Route HTTP requests to appropriate backend services
- Manage session lifecycle
- Format responses (JSON)
- Handle HTTP errors and status codes

**Endpoints** (simple CRUD):
- `POST /upload` — Upload PDF, initialize session, return session metadata
- `POST /query` — Submit question, get answer + citations
- `GET /status` — Get session status

**Lifecycle**: Long-lived; handles multiple requests per session

**Dependencies**: All backend components (orchestrator role)

---

### 7. Web Interface (Frontend)

**Purpose**: User-facing interface for PDF upload and Q&A  
**Responsibility**:
- Display file upload UI
- Capture user questions
- Display answers with citations
- Manage session state on client

**Key Features**:
- Drag-and-drop PDF upload
- Real-time Q&A chat interface
- Citation highlighting in answers
- Session indicator (upload status, query results)

**Technology**: TBD (React, Vue, vanilla JS — decide during Story 1.6)

**Lifecycle**: Browser-based; persists during session

**Dependencies**: REST API Layer (communicates via HTTP)

---

## System Services

### 8. Session Manager

**Purpose**: Manage session lifecycle and state  
**Responsibility**:
- Create session on PDF upload
- Store session data in memory (PDF text, embeddings, query history)
- Clean up session on timeout/completion
- Provide session state to other components

**Session Data** (in-memory, per-session):
- `session_id`: Unique identifier
- `pdf_text`: Extracted text
- `embeddings`: List of (chunk, vector, metadata)
- `vector_store`: Qdrant instance
- `query_history`: List of previous Q&A pairs
- `created_at`: Timestamp
- `last_activity`: Timestamp for timeout tracking

**Lifecycle**: Created per document upload; destroyed at session end (explicit or timeout)

**Dependencies**: Vector Store Client

---

### 9. Error Handler

**Purpose**: Centralized error management and logging  
**Responsibility**:
- Catch exceptions from any component
- Log error context (component, operation, input)
- Format error responses for API layer
- Determine appropriate HTTP status codes

**Error Categories**:
- **Validation errors**: Invalid PDF, malformed input
- **Processing errors**: Embedding generation failure, Qdrant failure
- **API errors**: Claude API timeout/failure
- **System errors**: Out of memory, file I/O errors

**Lifecycle**: Utility service; instantiated once at startup

**Dependencies**: Logging framework

---

## Component Interaction Summary

```
User Request
    ↓
[REST API Layer] (orchestrator)
    ├─ /upload → [PDF Processor] → [Embedding Engine] → [Vector Store Client] → [Session Manager]
    └─ /query → [RAG Retriever] → [Vector Store Client] → [Answer Generator] → [REST API Layer]
    ↓
[Web Interface]
```

**Data Flow**:
1. PDF Upload: PDF → Processor → Extract text → Embedding Engine → Vectors → Vector Store → Session
2. Query: Question → Embedding Engine → Vector → RAG Retriever → Chunks → Answer Generator → Response
3. Error: Any component → Error Handler → Log + Format → API Layer → HTTP Response

---

## Design Principles Applied

1. **Separation of Concerns**: Each component has single, well-defined responsibility
2. **Stateless Services**: Retriever, Answer Generator are stateless; state managed by Session Manager
3. **Simple Dependencies**: Direct instantiation; minimal abstraction for PoC
4. **Layered Architecture**: Clear frontend/API/backend separation
5. **Memory-Based Sessions**: In-process, ephemeral; no persistent storage needed for PoC

---

## Next Steps

- **Functional Design** will detail:
  - Method signatures and parameters for each component
  - Business logic and algorithms (RAG pipeline, chunking strategy, citation extraction)
  - Error handling specifics and edge cases
- **Code Generation** will implement components per user stories (1.1 through 1.7)
