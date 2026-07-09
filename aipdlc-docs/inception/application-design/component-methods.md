# Component Methods & Interfaces

**Level of Detail**: High-level method signatures; detailed business logic deferred to Functional Design  
**Implementation Style**: Monolithic design for PoC; minimal interfaces, direct instantiation

---

## Backend Components

### 1. PDF Processor

```python
class PDFProcessor:
    def __init__(self):
        pass
    
    def validate(self, pdf_file: BinaryIO) -> bool:
        """Validate PDF format and integrity."""
        
    def extract_text(self, pdf_file: BinaryIO) -> str:
        """Extract readable text from PDF."""
        
    def get_metadata(self, pdf_file: BinaryIO) -> dict:
        """Extract PDF metadata (filename, pages, etc.)."""
```

**Methods**:
- `validate(pdf_file)` → bool
  - Validates PDF is readable and not corrupted
  - Returns True if valid, raises exception otherwise

- `extract_text(pdf_file)` → str
  - Extracts all readable text from PDF
  - Returns concatenated text string
  - Handles multi-page PDFs

- `get_metadata(pdf_file)` → dict
  - Extracts filename, page count, creation date
  - Returns metadata dict for session tracking

**Exceptions**: `InvalidPDFError`, `FileReadError`, `UnsupportedFormatError`

---

### 2. Embedding Engine

```python
class EmbeddingEngine:
    def __init__(self):
        pass
    
    def chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Split text into overlapping chunks."""
        
    def generate_embeddings(self, chunks: list[str]) -> list[tuple[str, list[float]]]:
        """Generate vector embeddings for each chunk."""
        
    def process(self, text: str) -> list[tuple[str, list[float]]]:
        """End-to-end: chunk text and generate embeddings."""
```

**Methods**:
- `chunk_text(text, chunk_size, overlap)` → list[str]
  - Splits text into chunks of `chunk_size` with `overlap` characters between chunks
  - Returns list of chunk strings

- `generate_embeddings(chunks)` → list[tuple[str, list[float]]]
  - Calls embedding API for each chunk
  - Returns list of (chunk_text, embedding_vector) pairs

- `process(text)` → list[tuple[str, list[float]]]
  - Orchestrates chunking and embedding generation
  - Returns complete list of chunks with embeddings

**Exceptions**: `EmbeddingError`, `TextProcessingError`

---

### 3. Vector Store Client

```python
class VectorStoreClient:
    def __init__(self):
        self.client = None  # Qdrant in-memory client
        
    def initialize(self, collection_name: str, vector_size: int) -> None:
        """Initialize Qdrant in-memory instance."""
        
    def add_vectors(self, vectors: list[tuple[str, list[float], dict]]) -> None:
        """Store embeddings with metadata."""
        
    def search(self, query_vector: list[float], k: int = 5) -> list[tuple[str, float, dict]]:
        """Search for top-K similar vectors."""
        
    def close(self) -> None:
        """Clean up and close vector store."""
```

**Methods**:
- `initialize(collection_name, vector_size)` → None
  - Creates in-memory Qdrant instance
  - Sets up collection for storing embeddings
  - Called once per session

- `add_vectors(vectors)` → None
  - `vectors`: list of (chunk_text, embedding_vector, metadata_dict)
  - Stores vectors in Qdrant collection
  - Metadata includes chunk index, source page, etc.

- `search(query_vector, k)` → list[tuple[str, float, dict]]
  - Returns top-K most similar vectors to query
  - Includes chunk text, similarity score, metadata

- `close()` → None
  - Cleanup and destroy in-memory collection
  - Called at session end

**Exceptions**: `VectorStoreError`, `CollectionError`

---

### 4. RAG Retriever

```python
class RAGRetriever:
    def __init__(self, vector_store: VectorStoreClient, embedding_engine: EmbeddingEngine):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine
        
    def retrieve(self, question: str, k: int = 5) -> list[dict]:
        """Retrieve top-K relevant context chunks for a question."""
        
    def format_context(self, chunks: list[dict]) -> str:
        """Format retrieved chunks into context string for LLM."""
```

**Methods**:
- `retrieve(question, k)` → list[dict]
  - Embeds the question
  - Searches vector store for top-K similar chunks
  - Returns list of dicts: `{text, score, metadata}`

- `format_context(chunks)` → str
  - Joins chunks into single context string
  - Includes chunk separators and metadata (page, position)
  - Formatted for input to LLM

**Dependencies**: Vector Store Client, Embedding Engine

**Exceptions**: `RetrievalError`, `NoResultsError`

---

### 5. Answer Generator

```python
class AnswerGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key  # Claude API key
        
    def generate(self, question: str, context: str) -> tuple[str, list[str]]:
        """Generate answer with citations."""
        
    def extract_citations(self, response: str, context: str) -> list[str]:
        """Extract citation references from LLM response."""
        
    def format_response(self, answer: str, citations: list[str]) -> dict:
        """Format answer and citations for API response."""
```

**Methods**:
- `generate(question, context)` → tuple[str, list[str]]
  - Calls Claude API with system prompt + context + question
  - System prompt: "Generate answer grounded in context; include page/section citations"
  - Returns (answer_text, list_of_citations)

- `extract_citations(response, context)` → list[str]
  - Parses response for citation patterns (e.g., "Page X", "Section Y")
  - Validates citations map to source chunks
  - Returns formatted citations

- `format_response(answer, citations)` → dict
  - Structures answer and citations for API response
  - Returns: `{answer: str, citations: list[str], confidence: float}`

**Dependencies**: Claude API client

**Exceptions**: `APIError`, `RateLimitError`, `CitationExtractionError`

---

## API & Frontend Components

### 6. REST API Layer

```python
class ChatbotAPI:
    def __init__(self):
        self.session_manager = SessionManager()
        
    def upload_pdf(self, pdf_file: BinaryIO) -> dict:
        """POST /upload - Upload PDF and initialize session."""
        
    def query(self, session_id: str, question: str) -> dict:
        """POST /query - Submit question and get answer."""
        
    def get_status(self, session_id: str) -> dict:
        """GET /status - Get session status."""
```

**Methods**:
- `upload_pdf(pdf_file)` → dict
  - Validates PDF
  - Extracts text and generates embeddings
  - Creates session, stores in SessionManager
  - Returns: `{session_id, status: "ready", message}`

- `query(session_id, question)` → dict
  - Retrieves session from SessionManager
  - Calls RAG Retriever to get context
  - Calls Answer Generator to generate answer
  - Returns: `{answer, citations, source_chunks}`

- `get_status(session_id)` → dict
  - Returns session state (PDF ready, ready for queries, etc.)
  - Returns: `{session_id, status, created_at, last_query}`

**Dependencies**: SessionManager, RAG Retriever, Answer Generator

**HTTP Status Codes**:
- 200: Success
- 400: Invalid request (bad PDF, missing field)
- 404: Session not found
- 500: Server error (API failure, processing error)

**Exceptions**: Caught and formatted as HTTP error responses

---

### 7. Web Interface (Frontend)

```javascript
class ChatbotUI {
    constructor() {
        this.sessionId = null;
        this.apiUrl = '/api';
    }
    
    async uploadPDF(file) {
        // Send PDF to /upload endpoint
        // Display upload progress
        // Store sessionId
    }
    
    async submitQuestion(question) {
        // Send question to /query endpoint
        // Display answer and citations
        // Add to chat history
    }
    
    displayAnswer(answer, citations) {
        // Render answer with highlighted citations
        // Show source references
    }
    
    renderCitations(citations) {
        // Format citations for display (page/section references)
    }
}
```

**Key Methods**:
- `uploadPDF(file)` → Promise
  - POST file to `/upload` endpoint
  - Display progress indicator
  - Store returned sessionId

- `submitQuestion(question)` → Promise
  - POST question + sessionId to `/query`
  - Display answer with citations
  - Add Q&A pair to chat history

- `displayAnswer(answer, citations)` → void
  - Render answer text
  - Highlight citations and link to source

- `renderCitations(citations)` → HTML
  - Format as clickable references (Page X, Section Y)
  - Show full citation on hover/click

---

## System Services

### 8. Session Manager

```python
class SessionManager:
    def __init__(self):
        self.sessions = {}  # In-memory storage
        
    def create_session(self, pdf_metadata: dict) -> str:
        """Create new session, return session_id."""
        
    def store_session_data(self, session_id: str, data: dict) -> None:
        """Store PDF text, embeddings, vector store in session."""
        
    def get_session(self, session_id: str) -> dict:
        """Retrieve session data."""
        
    def destroy_session(self, session_id: str) -> None:
        """Cleanup and delete session."""
```

**Methods**:
- `create_session(pdf_metadata)` → str
  - Generates unique session ID (UUID)
  - Initializes session dict
  - Returns session_id

- `store_session_data(session_id, data)` → None
  - Stores: `{pdf_text, embeddings, vector_store, query_history}`
  - Keys session by session_id

- `get_session(session_id)` → dict
  - Retrieves session data
  - Updates last_activity timestamp
  - Raises SessionNotFoundError if expired

- `destroy_session(session_id)` → None
  - Closes vector store
  - Removes session from memory
  - Called on timeout or user logout

**Exceptions**: `SessionNotFoundError`, `SessionExpiredError`

---

### 9. Error Handler

```python
class ErrorHandler:
    @staticmethod
    def handle_exception(e: Exception, context: dict) -> dict:
        """Convert exception to API response."""
        
    @staticmethod
    def log_error(e: Exception, context: dict) -> None:
        """Log error with full context."""
```

**Methods**:
- `handle_exception(exception, context)` → dict
  - Maps exception type to HTTP status code
  - Returns: `{error: str, message: str, status_code: int}`
  - Examples:
    - `InvalidPDFError` → 400
    - `SessionNotFoundError` → 404
    - `APIError` → 502

- `log_error(exception, context)` → None
  - Logs exception type, message, traceback
  - Includes context (component, operation, inputs)
  - Format: timestamp, level, component, message, traceback

**Exceptions**: Utility class; does not raise

---

## Integration Points

**Session Lifecycle**:
```
API.upload_pdf()
  → PDFProcessor.extract_text()
  → EmbeddingEngine.process()
  → VectorStoreClient.initialize()
  → VectorStoreClient.add_vectors()
  → SessionManager.create_session()
  → Return session_id

API.query()
  → SessionManager.get_session()
  → RAGRetriever.retrieve()
  → AnswerGenerator.generate()
  → Return answer + citations

Session cleanup:
  → SessionManager.destroy_session()
  → VectorStoreClient.close()
```

---

## Next Steps

**Functional Design** will specify:
- Exact algorithm for text chunking (fixed-size, sliding window, sentence-based)
- Embedding generation strategy (model selection, batch processing)
- LLM prompt engineering for citations
- Citation extraction logic (regex, parsing strategy)
- Error handling specifics (retry logic, fallbacks)
- Performance optimization (caching, batch operations)
