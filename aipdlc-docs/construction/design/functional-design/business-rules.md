# Business Rules & Validation Logic

**Scope**: Validation rules, constraints, business policies, and edge case handling

---

## Input Validation Rules

### PDF Upload Validation

| Rule | Constraint | Action |
|------|-----------|--------|
| **File Format** | Must be .pdf or application/pdf | Reject if not PDF |
| **File Size** | Max 50 MB (configurable) | Reject if exceeds |
| **File Integrity** | File not corrupted, readable | Attempt to open; reject if fails |
| **Text Extractable** | PDF must contain readable text | Warn if no text extracted |
| **File Name** | No special constraints | Store for reference |

### Question Input Validation

| Rule | Constraint | Action |
|------|-----------|--------|
| **Question Length** | Min 2 characters, max 1000 | Reject if outside range |
| **Not Empty** | Question cannot be blank | Reject blank input |
| **Character Set** | UTF-8 valid text | Reject invalid encoding |
| **Session Valid** | Session must exist and not expired | Return 404 if not found |

**Edge Case: Short Queries (< 10 characters)**
- Handle single-word or very short questions
- Example: "mitochondria", "photosynthesis"
- Processing: Same RAG pipeline applies; Claude handles context mapping
- Risk: May retrieve many loosely-related chunks; mitigated by top-5 limit

---

## Chunking Constraints

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| **Chunk Size** | 512 characters | Balance context vs specificity |
| **Overlap** | 50 characters (10% of chunk) | Preserve context continuity |
| **Min Chunk Size** | 10 characters (minimum) | Avoid empty chunks |
| **Max Chunk Size** | 512 characters | Fixed size for consistency |

**Edge Case Handling**:
- **Very short text** (< 512 chars): Single chunk, no overlap
- **Special characters**: Preserve as-is; embedding model handles
- **Tables/Lists**: Chunked like regular text (no special handling for PoC)

---

## Embedding & Search Constraints

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| **Vector Model** | sentence-transformers | Lightweight, open-source |
| **Vector Dimension** | 384 | Balance quality vs performance |
| **Similarity Metric** | Cosine similarity | Standard for embeddings |
| **Top-K Results** | 5 chunks | Enough context, manageable size |
| **Similarity Threshold** | None (no threshold filtering) | Simple PoC approach |
| **Reranking** | None | Keep simple for PoC |

**Validation**:
- Embedding vector must have exactly 384 dimensions
- Similarity scores must be in range [-1, 1]
- Top-K results must be sorted by similarity (descending)

---

## LLM Response Constraints

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| **Model** | Claude (any version available) | High-quality answers |
| **Max Tokens** | 1000 | Reasonable answer length |
| **Temperature** | 0.7 | Balanced consistency/variety |
| **Response Format** | Natural language + citations | Claude's default format |

**Response Validation**:
- Answer must not be empty
- Answer should contain citations (ideal, not enforced)
- Answer length < max_tokens (enforced by API)

---

## Citation Extraction Rules

| Rule | Handling |
|------|----------|
| **Citation Pattern** | Extract "Page X" or "Page X, Section Y" | 
| **Case Sensitivity** | Case-insensitive matching | 
| **Validation** | No validation (trust Claude) | 
| **Empty Citations** | Return empty list if no patterns found | 
| **Duplicate Citations** | Allow duplicates (not deduplicated) | 
| **Format Output** | Return as list of strings | 

**Pattern Examples**:
- "Page 5" → `Page 5`
- "Page 12, Section 3.1" → `Page 12, Section 3.1`
- "From page 7" → `Page 7`
- "see page 15" → `Page 15`

---

## Session Management Rules

| Rule | Constraint | Handling |
|------|-----------|----------|
| **Session Creation** | UUID unique, created on upload | Generate new UUID |
| **Session Lifetime** | In-memory, no persistence | Lost on app restart |
| **Session Timeout** | No timeout for PoC | Sessions live indefinitely (until app exit) |
| **Query Limit** | No limit per session | Unlimited queries per session |
| **Concurrent Sessions** | Multiple sessions possible | Each stored separately in SessionManager |
| **Session Deletion** | Manual or on app exit | No automatic cleanup |

**Session State Validation**:
- session_id must be valid UUID format
- pdf_text must be non-empty string
- embeddings list must have at least 1 embedding
- vector_store handle must be valid Qdrant instance
- query_history must be list (can be empty)

---

## Error Handling Rules

### PDF Processing Errors
```
InvalidPDFError → 400 Bad Request
  Message: "Invalid PDF file. Please check the file and try again."

FileReadError → 500 Internal Server Error
  Message: "Error reading PDF file. Please try again."

TextExtractionError → 500 Internal Server Error
  Message: "Error extracting text from PDF. Please try again."
```

### Embedding/Search Errors
```
EmbeddingError → 500 Internal Server Error
  Message: "Error processing embeddings. Please try again."

VectorStoreError → 500 Internal Server Error
  Message: "Error searching documents. Please try again."
```

### LLM/API Errors
```
APIError / RateLimitError → 502 Bad Gateway
  Message: "LLM service temporarily unavailable. Please try again."

APITimeout → 504 Gateway Timeout
  Message: "LLM service is taking too long. Please try again."
```

### Session Errors
```
SessionNotFoundError → 404 Not Found
  Message: "Session expired or not found. Please upload a new PDF."

InvalidSessionError → 400 Bad Request
  Message: "Invalid session ID. Please upload a new PDF."
```

**Fail-Fast Principle**: Return error immediately; no retries in PoC.

---

## Business Policy Rules

### Accuracy Priority
- Answer accuracy > response speed
- All answers grounded in context
- Citations required where possible
- Trust LLM output (no post-validation in PoC)

### Simplicity for PoC
- No authentication/authorization
- No rate limiting
- No audit logging (except error logging)
- No data persistence
- No optimization for scale

### Student Privacy
- No logging of questions or answers (for future: add privacy policy)
- No tracking of student behavior
- Sessions destroyed at end (no history storage)

---

## Constraint Summary

**Must-Have** (enforcement required):
- PDF must be valid format
- Text must be extractable
- Embeddings must be correct dimension
- Sessions must be unique

**Should-Have** (guidance, not enforced):
- Answer should include citations
- Response should be under 1000 tokens
- Query should be 2-1000 characters

**Nice-to-Have** (future enhancements):
- Cache embeddings across sessions
- Rerank results for better quality
- Validate citations against sources
- Support follow-up questions

---

## Edge Cases (Focused on Short Queries for PoC)

### Edge Case 1: Single-Word Queries
**Example**: "mitochondria"  
**Processing**: Embed word → search → retrieve related chunks  
**Risk**: May match many loosely-related chunks  
**Handling**: Top-5 results may include some noise; Claude disambiguates in answer  
**Solution**: Works acceptably for PoC; if needed, add query expansion in future

### Edge Case 2: Numeric Queries
**Example**: "1.5", "pH", "2024"  
**Processing**: Embed as text → search  
**Risk**: Embedding model may not handle pure numbers well  
**Handling**: Claude still works with retrieved context  
**Solution**: Accept for PoC; monitor quality

### Edge Case 3: Non-English Queries (Future)
**Not in PoC**: Assume English only for now  
**Future**: Would need multilingual embedding model

### Future Edge Cases (Deferred)
- Long multi-part questions (e.g., "Compare X and Y; explain why; what's the impact?")
- Out-of-scope questions (e.g., "What's the weather?")
- Ambiguous questions (e.g., "What is this?")
- Questions contradicting PDF content

---

## Data Integrity Rules

| Data | Integrity Rule |
|------|---|
| **PDF Text** | Extracted text must match original PDF content |
| **Chunks** | Chunks must be non-overlapping in original text (but overlap in storage) |
| **Embeddings** | One embedding per chunk; same model for questions and documents |
| **Answers** | Answer must be generated by Claude API, not cached/synthesized |
| **Citations** | Citations must be extracted from Claude's response, not fabricated |

---

**Summary**: Business rules prioritize accuracy and simplicity for PoC, with clear validation and error handling.
