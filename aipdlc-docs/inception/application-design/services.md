# Service Layer & Orchestration

**Architecture Pattern**: Layered with service-oriented API design  
**Orchestration Style**: API Layer orchestrates component interactions

---

## Service Definitions

### Core Services

#### 1. PDF Ingestion Service
**Responsibility**: Accept and process PDF documents  
**Operations**:
- Upload PDF file
- Validate format and integrity
- Extract text content
- Return processing status

**Inputs**: Binary PDF file  
**Outputs**: Extracted text, processing metadata

**Lifecycle**: Called once per session during upload

---

#### 2. Embedding Service
**Responsibility**: Generate and manage vector embeddings  
**Operations**:
- Chunk input text
- Generate embeddings for chunks
- Store embeddings with metadata

**Inputs**: Text (from PDF Processor)  
**Outputs**: Embeddings (vectors) with chunk metadata

**Lifecycle**: Called during PDF processing; embeddings persisted in Vector Store

---

#### 3. Vector Storage Service
**Responsibility**: Store and retrieve vector embeddings  
**Operations**:
- Initialize in-memory Qdrant instance
- Store embeddings
- Search for similar vectors
- Manage collection lifecycle

**Inputs**: Embeddings, search queries (as vectors)  
**Outputs**: Stored/retrieved embeddings with similarity scores

**Lifecycle**: Created once per session; destroyed at session end

---

#### 4. RAG Pipeline Service
**Responsibility**: Orchestrate retrieval-augmented generation  
**Operations**:
- Convert user question to embedding
- Retrieve relevant context chunks
- Generate answer grounded in context
- Extract and format citations

**Inputs**: User question, document context (in Vector Store)  
**Outputs**: Answer + citations

**Lifecycle**: Called per user query; stateless

---

#### 5. Answer Generation Service
**Responsibility**: Generate answers using LLM with citations  
**Operations**:
- Call Claude API with context + question
- Parse response for answer and citations
- Format response for display

**Inputs**: Question, context chunks  
**Outputs**: Answer text, citation list

**Lifecycle**: Called per query; stateless

---

### Supporting Services

#### 6. Session Management Service
**Responsibility**: Manage session lifecycle and state  
**Operations**:
- Create new session
- Store session data (PDF text, embeddings, query history)
- Retrieve session for queries
- Clean up expired sessions

**Inputs**: PDF metadata, session ID  
**Outputs**: Session handle, session data

**Lifecycle**: Long-lived; persists across multiple requests per session

---

#### 7. Error Handling Service
**Responsibility**: Centralized error management  
**Operations**:
- Catch exceptions from any service
- Log errors with context
- Map exceptions to HTTP responses
- Format error messages

**Inputs**: Exception, context information  
**Outputs**: Formatted error response

**Lifecycle**: Utility service; stateless

---

#### 8. API Gateway Service
**Responsibility**: HTTP routing and request/response handling  
**Operations**:
- Route incoming HTTP requests
- Validate requests
- Orchestrate service calls
- Format JSON responses
- Handle HTTP status codes

**Inputs**: HTTP requests  
**Outputs**: HTTP responses (JSON)

**Lifecycle**: Long-lived; handles all incoming requests

---

## Service Interactions

### Request Flow 1: PDF Upload

```
Client
  ↓
[API Gateway] — POST /upload
  ↓
[Session Manager] — Create session
  ↓
[PDF Ingestion Service] — Extract text
  ↓
[Embedding Service] — Chunk + generate embeddings
  ↓
[Vector Storage Service] — Store embeddings
  ↓
[Session Manager] — Store session data
  ↓
[API Gateway] — Return session_id + status
  ↓
Client
```

**Status**: Session ready for queries

---

### Request Flow 2: Query (Q&A)

```
Client
  ↓
[API Gateway] — POST /query (session_id, question)
  ↓
[Session Manager] — Retrieve session
  ↓
[RAG Pipeline Service]
  ├─ [Embedding Service] — Embed question
  ├─ [Vector Storage Service] — Search for similar chunks
  ├─ [Answer Generation Service] — Generate answer with Claude API
  └─ Format result
  ↓
[API Gateway] — Return answer + citations
  ↓
Client
```

**Processing**: Converts question → embeddings → relevant context → answer

---

### Request Flow 3: Error Handling

```
Any Service
  ↓ (Exception raised)
[Error Handling Service]
  ├─ Log error with context
  ├─ Map exception to HTTP status
  └─ Format error response
  ↓
[API Gateway] — Return error response
  ↓
Client
```

**Scope**: Applies to all services

---

## Service Dependencies Graph

```
API Gateway (orchestrator)
  ├─ Session Manager
  │   ├─ Vector Storage Service
  │   └─ (stores session data)
  │
  ├─ PDF Ingestion Service
  │
  ├─ Embedding Service
  │   └─ (calls embedding model)
  │
  ├─ Vector Storage Service
  │
  ├─ RAG Pipeline Service
  │   ├─ Embedding Service
  │   ├─ Vector Storage Service
  │   └─ Answer Generation Service
  │       └─ (calls Claude API)
  │
  ├─ Answer Generation Service
  │
  └─ Error Handling Service
      └─ (catches all exceptions)
```

---

## Service Orchestration Patterns

### 1. Session-Based Workflow
- **Initiation**: Upload PDF → create session, store embeddings
- **Persistence**: Session data lives in SessionManager throughout session
- **Cleanup**: Session destroyed on logout or timeout
- **State Management**: Stateful at session level; stateless at request level

### 2. Request-Response Pattern
- **Input**: HTTP request with session_id + data
- **Processing**: API Gateway routes to appropriate services
- **Output**: JSON response
- **Error Handling**: Exceptions caught and formatted

### 3. Layered Service Composition
- **Layer 1 (API Gateway)**: HTTP routing, request validation
- **Layer 2 (Services)**: Business logic
- **Layer 3 (Components)**: Low-level operations
- **Utilities**: Error handling, logging, session management

---

## Service Boundaries

### Clear Boundaries
- **PDF Ingestion**: Standalone; takes PDF → returns text
- **Embedding**: Takes text → returns vectors
- **Vector Storage**: Isolated data store; no business logic
- **RAG Pipeline**: Orchestrates retrieval + generation
- **Answer Generation**: Isolated LLM integration

### Coupling Points
- **Session Manager** ↔ **Vector Storage**: Session stores vectors
- **RAG Pipeline** ↔ **Vector Storage**: Retrieves embeddings
- **RAG Pipeline** ↔ **Answer Generation**: Passes context
- **API Gateway** ↔ **All Services**: Central orchestrator

---

## Service Scalability Notes (Future)

**Current (PoC)**:
- All services in-process
- Single Python application
- In-memory session storage
- In-memory vector store (Qdrant)

**Future Expansion**:
- **Microservices**: Split into separate deployments
- **Message Queue**: Async task processing
- **Persistent Storage**: Replace in-memory session storage
- **Distributed Cache**: Cache embeddings across instances
- **Load Balancing**: Scale API Gateway across multiple instances

---

## Implementation Approach

**For Stories 1.1–1.7**:
1. **Story 1.1**: Implement PDF Ingestion Service + API endpoint
2. **Story 1.2**: Implement Embedding Service
3. **Story 1.3**: Implement Vector Storage Service + Session Manager
4. **Story 1.4**: Implement RAG Pipeline Service
5. **Story 1.5**: Implement Answer Generation Service
6. **Story 1.6**: Build Web Interface
7. **Story 1.7**: Wire all services together, E2E testing, API integration

---

## Next Steps

- **Functional Design** will detail:
  - Exact algorithms for each service
  - LLM prompts and response parsing
  - Error handling and retry logic
  - Performance optimization strategies
- **Code Generation** will implement services per story execution
