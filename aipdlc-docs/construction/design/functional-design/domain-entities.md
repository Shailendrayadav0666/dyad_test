# Domain Entities & Data Model

**Design Approach**: Simple entity model for PoC; focused on core concepts

---

## Core Entities

### 1. Session
**Purpose**: Encapsulates a PDF document and its embeddings for Q&A

**Attributes**:
- `session_id` (UUID): Unique identifier
- `created_at` (timestamp): When session created
- `last_activity` (timestamp): Last query time
- `pdf_metadata` (object): Original PDF info
  - `filename` (string): Uploaded filename
  - `page_count` (int): Number of pages
  - `upload_size` (int): File size in bytes
- `pdf_text` (string): Full extracted text
- `embeddings` (list[Embedding]): All chunks + vectors
- `vector_store` (handle): Qdrant in-memory instance
- `query_history` (list[Query]): All Q&A pairs in session

**Lifecycle**:
- Created: On PDF upload
- Destroyed: On session timeout or app exit
- In-memory: No persistence

---

### 2. Document (Logical)
**Purpose**: Represents uploaded PDF (metadata only in PoC)

**Attributes**:
- `filename` (string): Original filename
- `pages` (int): Total pages
- `extracted_text` (string): Full text content
- `extraction_timestamp` (timestamp): When extracted

**Note**: Not a separate entity in code; represented within Session

---

### 3. Chunk
**Purpose**: Individual text segment with embedding

**Attributes**:
- `text` (string): Chunk content (max 512 chars)
- `vector` (list[float]): Embedding vector (384 dimensions)
- `page` (int): Source page number
- `chunk_index` (int): Position in document
- `position_in_page` (int): Character offset in page

**Creation**: One chunk per 512-char segment with 50-char overlap

**Relationships**:
- Belongs to: One Document
- Used by: Vector search queries

---

### 4. Query
**Purpose**: User question within session

**Attributes**:
- `question` (string): The user's question
- `embedding` (list[float]): Question's embedding (384 dim)
- `timestamp` (timestamp): When asked
- `retrieved_chunks` (list[Chunk]): Top-5 semantic matches
- `answer` (string): Generated answer from Claude
- `citations` (list[string]): Extracted citations
- `query_id` (string): Unique identifier for this query

**Relationships**:
- Belongs to: One Session
- References: Multiple Chunks (via retrieval)

---

### 5. Answer
**Purpose**: LLM-generated response

**Attributes**:
- `text` (string): Full answer text
- `model` (string): "Claude" + version
- `citations` (list[Citation]): Extracted citations
- `confidence` (optional): No metrics in PoC
- `generation_time_ms` (int): API latency

**Derived from**: Query + Retrieved chunks

---

### 6. Citation
**Purpose**: Reference to source material

**Attributes**:
- `page` (int): Page number
- `section` (optional string): Section identifier
- `text` (string): Formatted citation ("Page 5" or "Page 5, Section 3")

**Creation**: Extracted via regex from Claude's answer

**Relationship**: References: One or more Chunks

---

## Simple Data Model (PoC)

```
Session
├── pdf_metadata (Document info)
├── pdf_text (string)
├── embeddings (List[Chunk])
│   ├── [Chunk]
│   │   ├── text
│   │   ├── vector (384-dim)
│   │   ├── page
│   │   └── chunk_index
│   ├── [Chunk]
│   └── [...]
├── vector_store (Qdrant handle)
└── query_history (List[Query])
    ├── [Query]
    │   ├── question
    │   ├── embedding
    │   ├── timestamp
    │   ├── retrieved_chunks (List[Chunk])
    │   ├── answer (string)
    │   └── citations (List[Citation])
    │       ├── [Citation: "Page 5"]
    │       └── [Citation: "Page 12, Section 3"]
    └── [Query]
```

---

## Entity Relationships

| Entity | Relates To | Type | Cardinality |
|--------|-----------|------|---|
| Session | Chunk | Contains | 1:N |
| Session | Query | Contains | 1:N |
| Query | Chunk | References (via retrieval) | N:M |
| Query | Citation | Contains | 1:N |
| Citation | Chunk | References | N:1 |

---

## Entity Constraints

### Session
- session_id must be unique UUID
- pdf_text must be non-empty
- embeddings list must have at least 1 chunk
- vector_store must be valid Qdrant handle

### Chunk
- text must be 1-512 characters
- vector must have exactly 384 dimensions
- page must be >= 1
- chunk_index must be >= 0

### Query
- question must be 2-1000 characters
- answer must be non-empty string
- citations list can be empty (no citations found)

### Citation
- page must be >= 1
- text must be non-empty

---

## Entity Lifecycle

### Session Lifecycle
```
Create (on PDF upload)
  ├─ Initialize session_id (UUID)
  ├─ Extract PDF text
  ├─ Generate chunks + embeddings
  ├─ Store in Qdrant
  └─ Create empty query_history
    ↓
Active (processing queries)
  ├─ Accept questions
  ├─ Add Query to history
  └─ Retrieve + generate answers
    ↓
Destroy (on timeout or app exit)
  ├─ Close Qdrant instance
  ├─ Clear embeddings
  └─ Remove session from memory
```

### Query Lifecycle
```
Create (user asks question)
  ├─ Receive question text
  ├─ Validate (length, characters)
  ├─ Generate embedding
  └─ Search Qdrant (top-5)
    ↓
Enrich
  ├─ Format context
  ├─ Call Claude API
  ├─ Receive answer
  ├─ Extract citations (regex)
  └─ Format response
    ↓
Store
  ├─ Add to query_history
  └─ Return to user
```

---

## Data Storage (In-Memory Only)

**Python Dict Structure**:
```python
sessions = {
    "session_uuid_1": {
        "created_at": "2026-07-09T10:00:00Z",
        "pdf_metadata": {...},
        "pdf_text": "...",
        "embeddings": [
            {"text": "chunk1", "vector": [...384 floats...], "page": 1, "index": 0},
            {"text": "chunk2", "vector": [...], "page": 1, "index": 1},
        ],
        "vector_store": <qdrant_handle>,
        "query_history": [
            {
                "question": "What is X?",
                "embedding": [...384 floats...],
                "answer": "X is...",
                "citations": ["Page 5", "Page 12"],
                "timestamp": "2026-07-09T10:05:00Z"
            }
        ]
    }
}
```

---

## Entity Design Rationale

**Simple Model for PoC**:
- No separate Document entity (info stored in Session)
- No separate Answer entity (stored within Query)
- No separate Embedding entity (stored as part of Chunk)
- Minimal relationships; all data tied to Session

**Benefits**:
- Easy to understand and implement
- No complex joins or lookups
- Fast in-memory access
- Natural fit for per-session ephemeral data

**Future Enhancement Opportunities**:
- Persistent Document storage (database)
- Separate Answer entity for reuse/caching
- Citation validation against source chunks
- Conversation history across sessions
- User profiles and query analytics

---

**Summary**: Simple, flat entity model optimized for PoC clarity and speed.
