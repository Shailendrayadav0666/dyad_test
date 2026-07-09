# Application Design Plan — RAG Exam Preparation Chatbot

**Purpose**: Define high-level components, their responsibilities, service layer design, and communication patterns before detailed functional design and code generation.

---

## Application Design Checklist

- [ ] **Step 1**: Identify core components and boundaries
- [ ] **Step 2**: Define component responsibilities
- [ ] **Step 3**: Design service layer and orchestration
- [ ] **Step 4**: Answer design clarification questions
- [ ] **Step 5**: Generate design artifacts
- [ ] **Step 6**: Review and approval gate

---

## Initial Component Analysis

Based on requirements and user stories, the system naturally decomposes into these functional areas:

**Backend Components**:
1. **PDF Processor** — Upload, validation, text extraction
2. **Embedding Engine** — Text chunking, embedding generation
3. **Vector Store Client** — Qdrant integration and management
4. **RAG Retriever** — Semantic search and context retrieval
5. **Answer Generator** — LLM integration, citation formatting

**Frontend & API Components**:
6. **REST API Layer** — Endpoint design and routing
7. **Web Interface** — PDF upload UI, chat interface

**System Services**:
8. **Session Manager** — Stateless session lifecycle
9. **Error Handler** — Error management and logging

---

## Design Clarification Questions

Please answer the following questions to guide component design:

### Question 1: Component Organization

How should components be organized in the codebase?

A) **Layered Architecture** — Separate `backend/`, `frontend/`, and `api/` directories; components grouped by technical layer

B) **Feature-Based Organization** — Components grouped by feature (`pdf_processing/`, `embedding/`, `rag_pipeline/`, `web_interface/`)

C) **Modular Architecture** — Each major component is a separate module/package; clear module boundaries and explicit dependencies

D) **Domain-Driven Design** — Components organized around business domains (`document_management/`, `search_engine/`, `qa_service/`)

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 2: Embedding Engine Architecture

For the Embedding Engine component, how should embedding generation be designed?

A) **Monolithic** — Single Embedding Engine class handles text chunking AND embedding generation

B) **Separate Services** — Split into TextChunker and EmbeddingGenerator services with clear interfaces

C) **Strategy Pattern** — Pluggable chunking and embedding strategies to support future model changes

D) **Hybrid** — TextChunker service; EmbeddingGenerator encapsulates model details

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 3: RAG Retriever Design

How should the RAG Retriever search functionality be designed?

A) **Simple Query-to-Embedding** — User question → embed → search → return top-K chunks

B) **Multi-Pass Retrieval** — Initial search → rerank results → return top-K (supports future reranking)

C) **Hybrid Search** — Combine semantic search with keyword search (more robust but PoC may not need)

D) **Adaptive Retrieval** — Search parameters (K, threshold) adapt based on query characteristics

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 4: Answer Generation & Citations

How should the Answer Generator handle answer generation and citation extraction?

A) **LLM-Only** — Prompt Claude to generate answer with citations; parse response for citations

B) **Post-Processing** — Generate answer with Claude; separately extract and validate citations from source chunks

C) **Structured Output** — Use Claude's structured output to get answer + citations in defined format

D) **Citation Mapping** — Answer Generator maintains mapping of answer text to source chunks; explicit citation tracking

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 5: API Design Pattern

How should the REST API be designed?

A) **Simple CRUD** — Minimal endpoints (`POST /upload`, `POST /query`, `GET /status`)

B) **Resource-Based** — RESTful resources (`POST /sessions`, `POST /documents`, `POST /queries`)

C) **RPC-Style** — Action-based endpoints (`POST /api/upload_pdf`, `POST /api/ask_question`)

D) **GraphQL** — Query API instead of REST endpoints (more flexible, overkill for PoC?)

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 6: Session Management

How should stateless sessions be managed?

A) **Memory-Based** — Session data (PDF, embeddings) stored in Python dict/object during request lifecycle

B) **Session ID** — Client receives session ID; server stores session state keyed by ID (per-request)

C) **Ephemeral Storage** — Use temporary files or in-memory caches; auto-cleanup after inactivity

D) **Stateless Design** — Client passes PDF content/hash with each request; no server-side storage

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 7: Error Handling & Logging

How should errors and logging be handled across components?

A) **Exception Propagation** — Exceptions bubble up; API layer catches and formats responses

B) **Result Objects** — Components return Result<T> with success/error; caller decides handling

C) **Logging-Centric** — Comprehensive logging at component boundaries; errors logged with context

D) **Hybrid** — Exceptions for exceptional cases; logging for traceability; Result objects for expected failures

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 8: Component Dependency Management

How should components handle dependencies and communication?

A) **Direct Instantiation** — Components instantiate dependencies directly in __init__

B) **Dependency Injection** — Constructor injection of dependencies (Container pattern for wiring)

C) **Service Locator** — Central registry of components; components request dependencies by name

D) **Factory Pattern** — Factory methods create components and wire dependencies

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 9: Testing & Mockability

How should components be designed for testability?

A) **Interface-Based** — Components depend on abstract interfaces; easy to mock in tests

B) **Minimal Dependencies** — Each component has few dependencies; easier to test in isolation

C) **Test Doubles** — Components designed with clear seams for test doubles (mocks, stubs)

D) **Integration Testing Focus** — Prioritize integration tests over unit tests; components test together

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 10: Technology Stack Choices

Are there specific technology choices you want to commit to now?

A) **Framework** — Use Flask/FastAPI for REST API? [specify]

B) **Database/Storage** — Qdrant only, or add other storage? [specify]

C) **Frontend Framework** — React/Vue/Vanilla JS for web UI? [specify]

D) **Embedding Model** — Use Claude embeddings, OpenAI, or local model? [specify]

E) **All TBD** — Decide during development (common for PoC)

X) Other (please describe after [Answer]: tag below)

[Answer]: B qdrant vector db in memory state

---

## Next Steps

1. Answer all questions above using [Answer]: tags
2. I'll review answers for consistency and clarity
3. If follow-up questions needed, I'll ask them
4. Then I'll generate detailed design artifacts:
   - `components.md` — Component definitions and responsibilities
   - `component-methods.md` — Method signatures and interfaces
   - `services.md` — Service layer and orchestration
   - `component-dependency.md` — Dependencies and communication patterns
   - `application-design.md` — Consolidated design document

**Please fill in all [Answer]: tags and reply with your completed answers.**
