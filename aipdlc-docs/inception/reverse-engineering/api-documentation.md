# API Documentation

All application routes are defined in `backend/api/routes.py` and mounted under the `/api` prefix in `backend/main.py:26` (`app.include_router(router, prefix="/api")`). One additional route, `/health`, is defined directly on the app (not under `/api`).

## REST APIs

### Health Check
- **Method**: GET
- **Path**: `/health`
- **Purpose**: Liveness check for the FastAPI process.
- **Request**: No body/params.
- **Response**: `200 OK` — `{"status": "ok"}` (`backend/main.py:29-31`).

### Upload PDF
- **Method**: POST
- **Path**: `/api/upload`
- **Purpose**: Validate a PDF, extract its text, chunk + embed it, create a per-session Qdrant collection, store the vectors, and return session/document metadata. This is the entry point that creates a new session.
- **Request**: `multipart/form-data` with a single field `file` (the PDF). Enforced constraints: filename must be non-empty and end in `.pdf`; size ≤ 50 MB (`PDFProcessor.MAX_FILE_SIZE`); must start with the `%PDF` magic bytes and be parseable.
- **Response** (`200`):
  ```json
  {
    "session_id": "<uuid>",
    "status": "ready",
    "message": "PDF uploaded and processed successfully",
    "pdf_info": {
      "filename": "string",
      "pages": 0,
      "file_size": 0,
      "extracted_characters": 0
    }
  }
  ```
  **Error responses** (all `JSONResponse` with `{"error": "<code>", "message": "<text>"}`):
  - `400 empty_filename` — no file selected.
  - `400 invalid_file_type` — extension is not `.pdf`.
  - `400 invalid_pdf` — failed `PDFProcessor.validate` (bad magic bytes / corrupt / unparseable / empty / oversized).
  - `500 extraction_failed` — text extraction raised `FileReadError`.
  - `500 embedding_failed` — chunking/embedding raised `EmbeddingError`.
  - `500 vector_store_failed` — Qdrant collection/upsert raised `VectorStoreError`.
  - `500 server_error` — any other unhandled exception (generic catch-all, `backend/api/routes.py:112-113`).

### Get Session Status
- **Method**: GET
- **Path**: `/api/status/{session_id}`
- **Purpose**: Look up an existing session (used by the frontend on load to validate a `sessionId` saved in `localStorage`).
- **Request**: Path parameter `session_id` (string).
- **Response** (`200`):
  ```json
  {
    "session_id": "string",
    "status": "ready",
    "created_at": "ISO-8601 string",
    "last_activity": "ISO-8601 string",
    "pdf_info": { "...": "pdf_metadata dict from upload" }
  }
  ```
  **Error response**: `404 session_not_found` — `session_id` not found (any exception from `SessionManager.get_session` is caught generically, `backend/api/routes.py:127-131`).

### Query for Raw Context (retrieval only, no LLM call)
- **Method**: POST
- **Path**: `/api/query`
- **Purpose**: Embed a question and run similarity search against the session's Qdrant collection, returning the ranked context chunks without generating a natural-language answer. (Not used by the current React frontend — `src/api/client.js` only calls `uploadPdf`, `getStatus`, and `getAnswer` — but it is a live, reachable endpoint.)
- **Request** (JSON body, Pydantic `QueryBody`):
  ```json
  { "session_id": "string", "query": "string" }
  ```
  Constraints: `query` must be non-empty after `.strip()` and ≤ 500 characters.
- **Response** (`200`):
  ```json
  {
    "session_id": "string",
    "query": "string",
    "status": "success",
    "context_chunks": [
      { "rank": 1, "chunk_text": "string", "similarity_score": 0.0, "chunk_size": 0, "point_id": "string" }
    ],
    "context_string": "string",
    "chunks_retrieved": 0
  }
  ```
  **Error responses**: `400 empty_query`, `400 query_too_long`, `404 session_not_found`, `400 no_embeddings` (session has no vector collection yet), `500 retrieval_failed`, `500 server_error`.

### Get a Cited Answer
- **Method**: POST
- **Path**: `/api/answer`
- **Purpose**: The primary chat transaction — retrieve context, call Claude to generate an answer grounded in that context, validate it, and return the answer with extracted citations. Used by `ChatSection.jsx` via `getAnswer()`.
- **Request** (JSON body, Pydantic `QueryBody`):
  ```json
  { "session_id": "string", "query": "string" }
  ```
  Constraints: `query` non-empty after `.strip()` (no explicit 500-char cap is enforced on this endpoint, unlike `/api/query`).
- **Response** (`200`):
  ```json
  {
    "session_id": "string",
    "query": "string",
    "status": "success",
    "answer": "string",
    "answer_with_sources": "string (answer + '## Sources' footer)",
    "citations": [
      { "source_rank": 1, "chunk_text": "string", "similarity_score": 0.0, "chunk_size": 0, "implicit": false }
    ],
    "context_chunks": [ "... same shape as /api/query context_chunks ..." ],
    "chunks_used": 0
  }
  ```
  **Error responses**: `500 api_key_missing` (no `ANTHROPIC_API_KEY` configured — `answer_generator` singleton is `None`), `400 empty_query`, `404 session_not_found`, `400 no_embeddings`, `500 retrieval_failed`, `400 no_context` (retrieval returned zero chunks), `500 invalid_answer` (failed `AnswerGenerator.validate_answer`), `500 answer_generation_failed`, `500 server_error`.

## Internal APIs

### `PDFProcessor` (`backend/components/pdf_processor.py`)
- **Methods**:
  - `validate(pdf_file) -> bool` — raises `InvalidPDFError` / `FileReadError`.
  - `extract_text(pdf_file) -> str` — raises `FileReadError`.
  - `get_metadata(pdf_file) -> Dict[str, Any]` — never raises; returns an `error` key on failure.
- **Parameters**: `pdf_file` — any file-like object exposing `filename`, `.read()`, `.seek()`, `.tell()` (see `UploadFileWrapper`).
- **Return Types**: `bool`, `str`, `Dict[str, Any]` respectively.

### `SessionManager` (`backend/components/session_manager.py`)
- **Methods**:
  - `create_session(pdf_metadata: Dict) -> str` — returns a new UUID4 session id.
  - `store_session_data(session_id: str, data: Dict) -> None` — raises `SessionNotFoundError`.
  - `get_session(session_id: str) -> Dict[str, Any]` — raises `SessionNotFoundError`; updates `last_activity` as a side effect.
- **Parameters**: as named above.
- **Return Types**: `str`, `None`, `Dict[str, Any]`.

### `EmbeddingEngine` (`backend/components/embedding_engine.py`)
- **Methods**:
  - `chunk_text(text, chunk_size=None, overlap=None) -> List[str]`.
  - `generate_embeddings(chunks, show_progress=False) -> List[Tuple[str, List[float]]]`.
  - `process(text, chunk_size=None, overlap=None) -> List[Tuple[str, List[float]]]` — composes the two above.
  - `get_embedding_dimension() -> int`.
- **Parameters**: `chunk_size`/`overlap` default to 512/50 characters.
- **Return Types**: as annotated above; raises `TextProcessingError` / `EmbeddingError`.

### `VectorStore` (`backend/components/vector_store.py`)
- **Methods**:
  - `create_collection(collection_name: str, vector_size: int = 384) -> str`.
  - `store_embeddings(collection_name: str, embeddings_data: List[Tuple[str, List[float]]]) -> int` (points stored).
  - `search(collection_name: str, query_vector: List[float], top_k: int = 5, score_threshold: Optional[float] = None) -> List[Dict[str, Any]]`.
  - `get_collection_info(collection_name: str) -> Dict[str, Any]`.
- **Parameters**: as named; all raise `VectorStoreError` on failure.
- **Return Types**: as annotated above.

### `RAGRetriever` (`backend/components/rag_retriever.py`)
- **Methods**:
  - `retrieve_context(query, vector_store, collection_name, top_k=None, score_threshold=None) -> List[Dict[str, Any]]`.
  - `get_context_string(context_chunks, separator="\n---\n") -> str`.
- **Parameters**: `top_k` defaults to `DEFAULT_TOP_K = 5`.
- **Return Types**: `List[Dict]`, `str`; raises `RAGRetrieverError`.

### `AnswerGenerator` (`backend/components/answer_generator.py`)
- **Methods**:
  - `generate_answer(question, context_chunks, max_tokens=None) -> Tuple[str, List[Dict[str, Any]]]`.
  - `format_answer_with_citations(answer_text, citations) -> str`.
  - `validate_answer(answer_text) -> Tuple[bool, str]`.
- **Parameters**: `max_tokens` defaults to `MAX_TOKENS = 1024`.
- **Return Types**: as annotated above; raises `AnswerGeneratorError`.

## Data Models

There is no ORM/database schema in this codebase — "data models" here are the in-memory Python `dict` shapes and the one Pydantic model used for request validation.

### `QueryBody` (Pydantic, `backend/api/routes.py:43-45`)
- **Fields**: `session_id: str`, `query: str`.
- **Relationships**: Used as the request body for both `/api/query` and `/api/answer`.
- **Validation**: Type enforcement only from Pydantic; length/emptiness checks (`query` non-empty, ≤500 chars on `/api/query`) are done manually in the route handlers, not via Pydantic validators/constraints.

### Session record (in-memory dict, `SessionManager.create_session`, `backend/components/session_manager.py:32-41`)
- **Fields**: `session_id: str`, `created_at: str (ISO-8601)`, `last_activity: str (ISO-8601)`, `pdf_metadata: dict`, `pdf_text: str`, `embeddings: list`, `vector_store: str | None` (Qdrant collection name), `query_history: list[dict]`.
- **Relationships**: One session ↔ one Qdrant collection (`session_{session_id}`) ↔ one uploaded PDF's chunks.
- **Validation**: None enforced beyond key presence checks in `store_session_data` (`if key in self.sessions[session_id]`, silently drops unknown keys).

### PDF metadata dict (`PDFProcessor.get_metadata`, `backend/components/pdf_processor.py:127-165`)
- **Fields**: `filename: str`, `page_count: int`, `file_size: int`, `upload_timestamp: str | None` (set by the API layer, not by `PDFProcessor` itself), plus `chunks_generated`/`embedding_dimension`/`vectors_stored` added later in `upload_pdf` (`backend/api/routes.py:85-86, 96`).
- **Relationships**: Embedded into the session record and into the `/api/upload` and `/api/status` responses' `pdf_info` field.
- **Validation**: None — on extraction failure, `get_metadata` returns a best-effort dict with an `error` key rather than raising.

### Context chunk / citation dict (`RAGRetriever._format_results`, `AnswerGenerator._extract_citations`)
- **Fields**: `rank`/`source_rank: int`, `chunk_text: str`, `similarity_score: float (rounded to 4 dp)`, `chunk_size: int`, `point_id: str` (context chunks only), `implicit: bool` (citations only, present only when no explicit `[Source #N]` was found in the answer).
- **Relationships**: Citations are a filtered/annotated subset of that turn's context chunks.
- **Validation**: None — plain dict construction.
