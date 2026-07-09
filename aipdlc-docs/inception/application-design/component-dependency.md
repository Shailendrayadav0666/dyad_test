# Component Dependencies & Communication

**Architecture Style**: Layered with direct instantiation  
**Coupling**: Minimal; components have well-defined boundaries  
**Communication**: Direct method calls (synchronous, in-process)

---

## Dependency Matrix

| Component | Depends On | Used By | Type |
|-----------|-----------|---------|------|
| PDF Processor | None | Embedding Engine | Direct call |
| Embedding Engine | Embedding API | Vector Store Client, RAG Retriever | Direct call |
| Vector Store Client | Qdrant library | Session Manager, RAG Retriever | Direct call |
| RAG Retriever | Embedding Engine, Vector Store Client | Answer Generator, API Layer | Direct call |
| Answer Generator | Claude API | API Layer | Direct call |
| REST API Layer | All services | Web Interface | HTTP/REST |
| Web Interface | REST API Layer | User | HTTP |
| Session Manager | Vector Store Client | API Layer | Direct call |
| Error Handler | None | All components | Static utility |

---

## Communication Patterns

### Pattern 1: Direct Service Call
**Used By**: Backend components  
**Mechanism**: Python method calls  
**Synchronous**: Yes  
**Example**:
```python
engine = EmbeddingEngine()
chunks = engine.chunk_text(text)
embeddings = engine.generate_embeddings(chunks)
```

---

### Pattern 2: Dependency Injection (Constructor)
**Used By**: RAG Retriever, Session Manager  
**Mechanism**: Pass dependencies in __init__  
**Example**:
```python
class RAGRetriever:
    def __init__(self, vector_store: VectorStoreClient, embedding_engine: EmbeddingEngine):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine
```

**Rationale**: Simple PoC; no need for complex DI containers

---

### Pattern 3: HTTP/REST
**Used By**: Web Interface ↔ REST API Layer  
**Mechanism**: HTTP requests/responses  
**Asynchronous**: Can be async on frontend  
**Example**:
```javascript
POST /upload
Content-Type: application/json
{
  "file": <binary>
}

Response 200 OK
{
  "session_id": "abc123",
  "status": "ready"
}
```

---

## Data Flow

### Data Flow 1: PDF Upload → Processing

```
User PDF
    ↓
[PDF Processor] — Extract text
    ↓
    Text
    ↓
[Embedding Engine] — Chunk + embed
    ↓
    (Chunk, Vector, Metadata) tuples
    ↓
[Vector Store Client] — Store
    ↓
    Qdrant collection (in-memory)
    ↓
[Session Manager] — Persist
    ↓
    Session object in memory
```

**Data at Each Step**:
- Input: Binary PDF
- After extraction: Raw text (string)
- After chunking: List of text chunks
- After embedding: List of (chunk, vector, metadata)
- After storage: Vectors in Qdrant, session state

---

### Data Flow 2: Query → Answer

```
User Question
    ↓
[Embedding Engine] — Embed question
    ↓
    Question vector
    ↓
[Vector Store Client] — Search
    ↓
    Top-K (chunk, score, metadata) tuples
    ↓
[Format context]
    ↓
    Formatted context string
    ↓
[Answer Generator] — Call Claude
    ↓
    Answer + citations
    ↓
[Format response]
    ↓
    JSON response
```

**Data at Each Step**:
- Input: Question string
- After embedding: Vector
- After search: Ranked chunks with scores
- After formatting: Single context string
- After LLM: Answer text
- Final response: `{answer, citations, sources}`

---

## Coupling & Cohesion Analysis

### Low Coupling
✅ PDF Processor: No dependencies; can be replaced  
✅ Vector Store Client: Isolated; interface to Qdrant  
✅ Answer Generator: Isolated; depends only on Claude API  
✅ Web Interface: Only talks to REST API

### Moderate Coupling
⚠️ Embedding Engine: Depends on embedding model (but encapsulated)  
⚠️ RAG Retriever: Depends on Vector Store Client + Embedding Engine (by design)  
⚠️ API Layer: Depends on all services (orchestrator pattern)

### High Cohesion
✅ Each component has single responsibility  
✅ Clear interfaces between components  
✅ No circular dependencies  
✅ Session Manager aggregates but doesn't duplicate logic

---

## Integration Points

### 1. Session Creation (Story 1.1 → 1.3)
```
API /upload request
  → PDFProcessor.extract_text(file)
  → EmbeddingEngine.process(text)
  → VectorStoreClient.initialize() + add_vectors()
  → SessionManager.create_session()
  → Return session_id
```

**Integration**: PDF Processor → Embedding Engine → Vector Store → Session Manager

---

### 2. Query Processing (Story 1.4 → 1.5)
```
API /query request
  → SessionManager.get_session(session_id)
  → RAGRetriever.retrieve(question)
    → EmbeddingEngine (question embedding)
    → VectorStoreClient (search)
  → AnswerGenerator.generate(question, context)
  → Return answer + citations
```

**Integration**: RAG Retriever → Answer Generator

---

### 3. Error Propagation
```
Any component raises exception
  → Propagates up to API Layer
  → Error Handler catches
  → Formats as HTTP error
  → Returns to client
```

**Error Flow**: All components → API Layer → Error Handler → HTTP response

---

## Initialization Order

### Session Initialization (Order Matters)
1. **PDF Processor** — Extract text (no dependencies)
2. **Embedding Engine** — Generate embeddings (needs text from #1)
3. **Vector Store Client** — Create collection (needs to exist before storing)
4. **Vector Store Client.add_vectors()** — Store embeddings (needs #3)
5. **Session Manager** — Create session with all data (needs #1-#4)

**Incorrect Order** → Runtime errors (e.g., vector store not initialized)

---

### Query Initialization (Order Matters)
1. **Session Manager.get_session()** — Retrieve existing session
2. **RAG Retriever** — Access session's Vector Store Client
3. **Answer Generator** — Uses context from RAG Retriever

**Rationale**: Session must exist before querying; components depend on session state

---

## Synchronization & Concurrency

**Current (PoC)**:
- No concurrency handling
- Single-threaded synchronous calls
- No locking or thread-safety

**Future Considerations**:
- Thread-safe session storage (if multi-threaded)
- Concurrent embedding generation (batch processing)
- Async API calls (don't block on LLM)

---

## Component Lifetime

### Long-Lived
- **Session Manager**: Created at app startup; persists through session lifecycle
- **REST API Layer**: Created at app startup; handles all requests
- **Error Handler**: Singleton; created at app startup

### Per-Session
- **Vector Store Client**: Created once per session; destroyed at session end
- **Session object**: Created on upload; destroyed on timeout/logout

### Per-Request
- **RAG Retriever**: Created per query; stateless
- **Answer Generator**: Called per query; stateless
- **PDF Processor**: Called once at upload; short-lived

---

## Replacement & Extension Points

### Pluggable Components
1. **Embedding Model**: Replace EmbeddingEngine with different model (OpenAI, local, etc.)
2. **LLM**: Replace Answer Generator's Claude calls with different LLM
3. **Vector Store**: Replace Qdrant with different DB (Pinecone, Weaviate, etc.)
4. **Frontend**: Replace Vue/React with different framework
5. **API Framework**: Replace Flask/FastAPI with different HTTP framework

### Extension Points
1. **Logging**: Add comprehensive logging throughout services
2. **Metrics**: Add performance tracking (query latency, embedding time)
3. **Caching**: Add embedding cache to reduce API calls
4. **Reranking**: Add reranking layer to RAG Retriever (multi-pass search)
5. **Persistent Storage**: Replace in-memory session with database

---

## Next Steps

- **Functional Design** will detail:
  - Exact initialization sequences
  - Error handling per component
  - Performance optimization
  - Concurrency considerations (if applicable)
- **Code Generation** will implement with proper dependency wiring per story
