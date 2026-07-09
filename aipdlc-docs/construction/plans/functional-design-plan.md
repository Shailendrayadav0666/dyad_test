# Functional Design Plan — RAG Exam Preparation Chatbot

**Purpose**: Define detailed business logic, algorithms, domain models, and business rules for the RAG system.

**Scope**: System-level design (single pass for entire application before per-story code generation)

---

## Functional Design Checklist

- [ ] **Step 1**: Review intake brief and application design
- [ ] **Step 2**: Answer functional design clarification questions
- [ ] **Step 3**: Resolve any ambiguities
- [ ] **Step 4**: Generate functional design artifacts
- [ ] **Step 5**: Review and approval

---

## System Context

**Intake Brief**: RAG chatbot that accepts PDF documents and provides accurate answers to exam preparation questions, with exact source citations.

**Key Requirements**:
- Answer accuracy prioritized over speed
- All answers must include exact citations (page/section)
- Stateless sessions (no persistence)
- Domain-agnostic (works with any academic subject)
- PoC stage (simplicity over optimization)

**Application Design**: Layered architecture with 9 components (PDF Processor, Embedding Engine, Vector Store, RAG Retriever, Answer Generator, API, Web UI, Session Manager, Error Handler)

---

## Functional Design Clarification Questions

### Question 1: Text Chunking Strategy

How should the system chunk PDF text for embedding?

A) **Fixed-Size Chunks** — Break text into chunks of fixed size (e.g., 512 characters) with fixed overlap (e.g., 50 characters)

B) **Sliding Window** — Variable-size chunks based on sentence boundaries, with sliding window for context

C) **Sentence-Based** — Chunk at sentence boundaries; each chunk is complete sentence(s)

D) **Adaptive Chunking** — Chunk size adapts based on content type (questions vs passages vs lists)

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 2: Embedding Model & Vector Dimension

Which embedding model and vector dimension should be used?

A) **Claude Embeddings** — Use Claude API embeddings; dimension TBD by API

B) **OpenAI Embeddings** — Use OpenAI API (text-embedding-3-small or -large); dimension 1536

C) **Open-Source Model** — Use local embedding model (sentence-transformers); dimension 384-768

D) **TBD During Implementation** — Defer choice to Story 1.2

X) Other (please describe after [Answer]: tag below)

[Answer]: c

---

### Question 3: Retrieval Search Strategy

How should the RAG Retriever perform semantic search?

A) **Simple Top-K** — Embed question, search Qdrant for top-K most similar chunks (e.g., K=5)

B) **Similarity Threshold** — Return chunks above similarity threshold, not just top-K (more flexible)

C) **Reranking** — Initial top-K search, then rerank results using relevance model

D) **Hybrid Search** — Combine semantic search with keyword search for robustness

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 4: LLM Prompt Engineering

How should the Claude prompt be structured for answer generation with citations?

A) **Template-Based** — Fixed system prompt template with placeholders for context and question

B) **Dynamic Prompting** — System prompt adapts based on query type (factual vs analytical vs synthesis)

C) **Chain-of-Thought** — Prompt Claude to "think step-by-step" before generating answer

D) **Structured Output** — Use Claude's structured output feature to get {answer, citations} as JSON

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 5: Citation Extraction Logic

How should citations be extracted and formatted from Claude's response?

A) **Pattern Matching** — Use regex/string patterns to find citations (e.g., "Page X, Section Y")

B) **LLM-Based Extraction** — Ask Claude to output citations in structured format; parse response

C) **Source Mapping** — Answer Generator maintains explicit mapping of answer text to source chunks

D) **Hybrid** — LLM generates answer with citations inline; pattern matching extracts and validates

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 6: Validation & Error Recovery

How should validation errors (e.g., embedding failure, API timeout) be handled?

A) **Fail-Fast** — Return error immediately to user; no retry

B) **Automatic Retry** — Retry failed operations (e.g., API calls) with exponential backoff

C) **Graceful Degradation** — If embeddings unavailable, fall back to keyword search

D) **User Choice** — Return error message; let user retry or proceed differently

X) Other (please describe after [Answer]: tag below)

[Answer]: a
---

### Question 7: Citation Validation

Should the system validate that citations accurately reference source chunks?

A) **No Validation** — Trust Claude's citations; no validation

B) **Basic Validation** — Check citations reference actual chunks (page/section exists)

C) **Content Validation** — Verify cited content actually supports the answer (high bar)

D) **Confidence Score** — Assign confidence score to answers based on citation quality

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 8: Multi-Query Handling

If a user asks multiple questions in the same session, how should the system behave?

A) **Stateless Per-Query** — Each query is independent; no awareness of previous queries

B) **Query History** — Track previous Q&A pairs; context-aware responses within session

C) **Follow-Up Handling** — Support follow-up questions (e.g., "explain that further")

D) **Conversation Mode** — Build conversational history; reference previous answers

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 9: Answer Quality Metrics

How should answer quality be measured or indicated to the user?

A) **No Metrics** — Return answer as-is; no quality indication

B) **Relevance Score** — Include relevance score (similarity) with answer

C) **Confidence Level** — Assign confidence (high/medium/low) based on context quality

D) **Source Count** — Indicate how many source chunks support the answer

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 10: Edge Cases & Constraints

How should the system handle edge cases?

A) **Short Queries** — How to handle single-word or very short questions?

B) **Long Queries** — Should long multi-part questions be split or answered as whole?

C) **Out-of-Scope Questions** — Questions unrelated to PDF content?

D) **Ambiguous Questions** — Questions with multiple interpretations?

E) **All of Above** — Define handling for all edge cases

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 11: Domain Model - Core Entities

Should the functional design explicitly define domain model entities?

A) **Simple** — Just focus on PDFs and answers; no formal entity model

B) **Detailed** — Define explicit entities: Document, Chunk, Query, Answer, Citation with relationships

C) **Lightweight** — Define key entities (Chunk, Answer) but keep it simple for PoC

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

### Question 12: Frontend State Management

For the Web Interface, how should state be managed?

A) **Minimal State** — Store only session ID; most state on server

B) **Client State** — Store uploaded PDF info, query history on client

C) **Shared State** — Mix of client state (UI) and server state (data)

D) **TBD During Story 1.6** — Defer to frontend implementation story

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

## Next Steps

1. Answer all questions above using [Answer]: tags
2. I'll review answers for consistency and clarity
3. If follow-up questions needed, I'll ask them
4. Then I'll generate detailed functional design artifacts:
   - `business-logic-model.md` — RAG pipeline algorithm, workflows
   - `business-rules.md` — Validation, constraints, business policies
   - `domain-entities.md` — Entity definitions and relationships
   - `frontend-components.md` — UI component structure (if applicable)

**Please fill in all [Answer]: tags and reply with your completed answers.**
