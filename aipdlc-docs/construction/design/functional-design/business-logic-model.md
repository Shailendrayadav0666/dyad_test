# Business Logic Model — RAG Exam Preparation Chatbot

**Scope**: Detailed algorithms, workflows, and business processes for the RAG system  
**Design Approach**: PoC simplicity; accurate over optimized

---

## RAG Pipeline Algorithm

The core business logic is the Retrieval-Augmented Generation (RAG) pipeline, executed in two main workflows:

### Workflow 1: PDF Ingestion & Embedding (Stories 1.1 → 1.3)

```
PDF Upload
    ↓
1. PDF Validation
   - Check file format (PDF)
   - Verify file not corrupted
   - Validate file size (reasonable limit, e.g., < 50MB)
    ↓
2. Text Extraction
   - Extract all readable text from PDF
   - Preserve order (page by page)
   - Handle multi-page documents
    ↓
3. Text Chunking (Fixed-Size Strategy)
   - Chunk size: 512 characters (configurable)
   - Overlap: 50 characters between consecutive chunks
   - Algorithm:
     * Start at position 0
     * Read 512 characters
     * Move forward by (512 - 50) = 462 characters
     * Repeat until end of text
   - Rationale: Fixed-size ensures consistent embedding quality; overlap provides context continuity
    ↓
4. Embedding Generation (Open-Source Model)
   - Model: sentence-transformers (e.g., 'all-MiniLM-L6-v2')
   - Dimension: 384
   - For each chunk:
     * Generate embedding vector
     * Store (chunk_text, vector, metadata)
   - Batch process chunks if possible for performance
    ↓
5. Vector Storage (Qdrant In-Memory)
   - Initialize Qdrant client in-memory mode
   - Create collection with vector dimension = 384
   - For each embedding:
     * Insert vector with payload (chunk_text, page_number, chunk_index)
   - Build index for fast similarity search
    ↓
6. Session Creation
   - Generate unique session_id (UUID)
   - Store in SessionManager:
     * pdf_text (original extracted text)
     * embeddings (list of chunk+vector+metadata)
     * vector_store (Qdrant handle)
     * query_history (empty list, grows with queries)
    ↓
Session Ready for Queries
```

**Key Decisions**:
- **Fixed-size chunking**: Simple, deterministic, consistent
- **Overlap**: Ensures context is not lost at chunk boundaries
- **Open-source embeddings**: Lightweight, no API costs, reproducible
- **In-memory Qdrant**: Fast, ephemeral, perfect for PoC

---

### Workflow 2: Query Processing & Answer Generation (Stories 1.4 → 1.5)

```
User Question
    ↓
1. Question Embedding
   - Convert question to embedding using same model as chunking
   - Result: vector of dimension 384
    ↓
2. Semantic Search (Simple Top-K)
   - Query: Search Qdrant for K=5 most similar chunks to question vector
   - Similarity metric: Cosine similarity (default in Qdrant)
   - Return: Top-5 (chunk_text, similarity_score, metadata)
   - Rationale: K=5 provides enough context without noise; simple top-K is fast
    ↓
3. Context Formatting
   - Sort retrieved chunks by original order (page, position)
   - Format as single context string:
     ```
     --- CONTEXT START ---
     [Page {page}] {chunk_text}
     [Page {page}] {chunk_text}
     ...
     --- CONTEXT END ---
     ```
   - Include page numbers for later citation extraction
    ↓
4. LLM Answer Generation (Claude API)
   - System prompt (template-based):
     ```
     You are an exam study assistant. Answer the student's question 
     accurately based ONLY on the provided context from course materials.
     
     IMPORTANT: Include exact source citations in your answer.
     For each fact, cite as "Page X" or "Page X, Section Y" where available.
     
     If the context does not contain enough information to answer,
     say "This information is not covered in the provided materials."
     ```
   - User message:
     ```
     Context:
     {formatted_context}
     
     Question: {user_question}
     ```
   - Call Claude with max_tokens=1000 (reasonable limit for exam answers)
   - Temperature: 0.7 (balanced between consistency and variety)
    ↓
5. Citation Extraction (Pattern Matching)
   - Parse Claude's response for citation patterns:
     * Pattern 1: "Page \d+" → "Page X"
     * Pattern 2: "Page \d+, Section" → "Page X, Section ..."
     * Pattern 3: "Section .*" → "Section ..."
   - Extract all matches using regex
   - Format as list: ["Page 5", "Page 12, Section 3", ...]
   - Rationale: Simple regex for PoC; Claude naturally outputs citations in this format
    ↓
6. Response Formatting
   - Return to API:
     ```json
     {
       "answer": "<Claude's full answer>",
       "citations": ["Page 5", "Page 12, Section 3.1"],
       "source_chunks": [
         {
           "chunk": "text excerpt",
           "page": 5,
           "score": 0.87
         }
       ]
     }
     ```
    ↓
Answer Delivered to User
```

**Key Decisions**:
- **Simple Top-K**: Fast, deterministic, sufficient for PoC
- **Template-based prompt**: Reusable, consistent
- **Pattern matching for citations**: Simple, works with Claude's natural output
- **No citation validation**: Trust Claude; PoC can validate later if needed

---

## Error Handling Logic (Fail-Fast Strategy)

For a PoC with accuracy prioritized, fail-fast is appropriate—errors are reported immediately, no retries.

### Error Scenarios & Handling

| Scenario | Cause | Handling |
|----------|-------|----------|
| **Invalid PDF** | Wrong format, corrupted file | Reject, return 400 Bad Request |
| **Extraction Failure** | Unreadable PDF, encoding issues | Log error, return 500 with message |
| **Embedding Error** | Model failure, OOM | Catch exception, return 500 |
| **Qdrant Error** | Vector store initialization/query failure | Catch exception, return 500 |
| **Claude API Timeout** | API unresponsive, rate limit | Catch exception, return 502 Bad Gateway |
| **Citation Parse Failure** | Response doesn't match pattern | Return answer without citations (graceful) |
| **Session Not Found** | Expired or invalid session_id | Return 404 Not Found |

**Exception Propagation Flow**:
```
Component raises exception
    ↓
Propagates up call stack
    ↓
REST API Layer catches
    ↓
Error Handler formats response
    ↓
Return HTTP error response (400/404/500/502)
```

**Rationale**: Fail-fast keeps PoC simple; retry logic and graceful degradation can be added later.

---

## State Management (Stateless Per-Query)

Each query is independent; no awareness of previous queries within session.

**Benefits for PoC**:
- Simpler logic (no conversation history to manage)
- Faster response (no context accumulation)
- Easier to test (each query is self-contained)

**Session State Structure**:
```python
{
    "session_id": "uuid",
    "pdf_text": "extracted text",
    "embeddings": [
        {"chunk": "text", "vector": [floats], "page": int, "index": int}
    ],
    "vector_store": qdrant_handle,
    "query_history": [
        {"question": "Q1", "answer": "A1", "citations": [...], "timestamp": ...},
        {"question": "Q2", "answer": "A2", "citations": [...], "timestamp": ...}
    ]
}
```

**Query History**: Tracked for user reference (show previous Q&A) but NOT used to influence subsequent query answers.

---

## Multi-Step Processing with Batch Optimization (Optional)

For efficiency, can batch operations where applicable:

### Batch Embedding (Optional for Story 1.2)
```
If processing many chunks:
  - Batch chunks into groups of 32
  - Call embedding model once per batch (faster than per-chunk)
  - Collect all embeddings
```

### Single Query Processing
```
- Single question: one embedding (not batched)
- Single Qdrant search: return top-5
- Single LLM call: one prompt, one response
```

---

## Answer Quality (No Metrics in PoC)

No quality metrics returned to user in PoC. Future enhancements:
- Relevance score: Include similarity_score from Qdrant
- Confidence level: Based on context quality (average similarity)
- Source count: Number of chunks supporting answer

---

## Frontend Workflows

### Upload Workflow
```
User selects PDF file
    ↓
Frontend validates (file size, type)
    ↓
POST /upload with file
    ↓
API processes (extract → embed → store)
    ↓
Return session_id + status: "ready"
    ↓
Frontend stores session_id in local storage
    ↓
Display "PDF ready for questions"
```

### Query Workflow
```
User types question
    ↓
Frontend validates (not empty, reasonable length)
    ↓
POST /query with {session_id, question}
    ↓
API processes (embed → search → generate answer)
    ↓
Return {answer, citations, sources}
    ↓
Frontend displays answer with highlighted citations
    ↓
Add to chat history
```

---

## Data Transformation Pipeline

**Input**: PDF document (binary)

**→ Step 1**: Extract text (string)

**→ Step 2**: Chunk text (list of strings)

**→ Step 3**: Embed chunks (list of vectors)

**→ Step 4**: Store in Qdrant (vectors with metadata)

**→ Step 5**: Question embedding (single vector)

**→ Step 6**: Search & rank (list of similar chunks)

**→ Step 7**: Format context (single text string)

**→ Step 8**: LLM generation (answer + citations)

**→ Step 9**: Parse citations (list of citation strings)

**→ Output**: Answer with citations (JSON response)

---

## Performance Characteristics (PoC Expectations)

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| PDF extraction | < 5 seconds | Depends on PDF size |
| Chunking | < 1 second | Linear in text length |
| Embedding generation | 1-10 seconds | Depends on chunk count |
| Qdrant storage | < 1 second | In-memory fast |
| Question embedding | < 1 second | Single query |
| Semantic search | < 100ms | In-memory Qdrant is fast |
| Claude API call | 2-10 seconds | Depends on API load |
| Citation extraction | < 100ms | Simple regex |
| **Total upload flow** | **5-20 seconds** | Dominated by embedding |
| **Total query flow** | **3-15 seconds** | Dominated by Claude API |

**Rationale**: PoC prioritizes accuracy > speed; these latencies are acceptable for study sessions.

---

## Algorithm Summary

**Chunking**: Fixed 512-char chunks with 50-char overlap  
**Embeddings**: Open-source sentence-transformers (384 dim)  
**Search**: Cosine similarity, top-5 chunks  
**Prompting**: Template-based system prompt  
**Citation**: Regex pattern matching  
**Error Handling**: Fail-fast (no retry)  
**State**: Stateless per-query (history tracked but not used)  
**Quality**: No metrics (accuracy only)

All decisions optimize for PoC simplicity and clarity.

---

**Next Steps**: Business Rules document specifies validation logic, constraints, and edge case handling.
