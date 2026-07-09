# User Stories — RAG Exam Preparation Chatbot

**Project**: RAG-Based Chatbot for Exam Preparation  
**Team Size**: 1 Developer  
**Development Approach**: Code-First (Non-TDD)  
**Story Format**: Feature-Based, Large Scope, Strictly Sequential

---

## Story 1.1: PDF Upload & Text Extraction

**Wave**: 1

**Persona**: Student

**Description**:
As a student, I need to upload a PDF document to the chatbot so that it can process the content and make it available for Q&A. The system should accept PDF files, validate them, and extract readable text content for downstream processing.

**Acceptance Criteria**:
1. System accepts PDF file uploads via a web interface and validates file format (must be valid PDF)
2. Extracted text is stored in memory for the session and made available to downstream components

**Technical Notes**:
- Implement PDF parsing library (PyPDF2, pdfplumber, or similar)
- Validate file size and format
- Extract and store text content in a session-scoped data structure
- Include error handling for corrupted or unsupported PDFs
- Test with sample academic PDFs (textbook excerpts, lecture notes)

**Jira**: —

---

## Story 1.2: Text Chunking & Vector Embedding Generation

**Wave**: 2

**Requires**: Story 1.1

**Persona**: Student

**Description**:
As the chatbot system, I need to break down the extracted PDF text into manageable chunks and generate vector embeddings for each chunk, so that I can store them in Qdrant for semantic search. This enables the RAG pipeline to find relevant context quickly.

**Acceptance Criteria**:
1. Extracted text is chunked into logical segments (with configurable chunk size and overlap)
2. Vector embeddings are generated for each chunk using the embedding model

**Technical Notes**:
- Implement text chunking logic (fixed-size, sliding window, or sentence-based)
- Integrate with embedding model (OpenAI, Hugging Face, or Claude embeddings API)
- Handle edge cases (very short documents, special characters, tables)
- Optimize chunk overlap to prevent context loss
- Test embedding quality with sample academic content

**Jira**: —

---

## Story 1.3: Qdrant Integration & Vector Storage

**Wave**: 3

**Requires**: Story 1.2

**Persona**: Student

**Description**:
As the chatbot system, I need to store all generated vector embeddings in a Qdrant in-memory database, so that the RAG pipeline can perform semantic search and retrieve relevant context for student questions.

**Acceptance Criteria**:
1. Qdrant client is initialized with in-memory configuration for the session
2. All embeddings from Story 1.2 are successfully stored and retrievable

**Technical Notes**:
- Set up Qdrant client library (Python SDK)
- Configure in-memory storage (ephemeral, per-session)
- Implement collection creation and management
- Add metadata to embeddings (source page, chunk index) for citation tracking
- Test storage and retrieval performance
- Ensure cleanup/reset for each new session

**Jira**: —

---

## Story 1.4: RAG Retrieval & Context Search

**Wave**: 4

**Requires**: Story 1.3

**Persona**: Student

**Description**:
As a student asking a question, I need the system to search the stored embeddings and retrieve the most relevant context chunks from my uploaded PDF, so that the answer generator has accurate source material to work with.

**Acceptance Criteria**:
1. Student questions are converted to embeddings and used to search Qdrant
2. Top-K most relevant chunks are retrieved with relevance scores

**Technical Notes**:
- Implement query embedding generation (same model as chunking)
- Build semantic search logic with configurable K (e.g., top 3-5 chunks)
- Return chunks with relevance scores and metadata (page, position)
- Handle queries with no relevant matches gracefully
- Test with various question types (factual, analytical, comparative)

**Jira**: —

---

## Story 1.5: LLM-Based Answer Generation with Citations

**Wave**: 5

**Requires**: Story 1.4

**Persona**: Student

**Description**:
As a student, I need the chatbot to generate a clear, accurate answer to my question based on the retrieved context chunks, with exact citations showing where in the PDF the information came from. This ensures answer accuracy and helps me locate relevant material in my notes.

**Acceptance Criteria**:
1. Claude API generates an answer using retrieved context as the prompt input
2. Answer includes exact source citations (page number and/or section name from the PDF)

**Technical Notes**:
- Design system prompt to emphasize accuracy and citation inclusion
- Format context chunks clearly in the LLM prompt
- Parse LLM output to extract answer and validate citation format
- Handle cases where context doesn't fully answer the question (indicate uncertainty)
- Test answer quality with diverse question types
- Ensure citations map correctly to source chunks

**Jira**: —

---

## Story 1.6: Web Interface — PDF Upload & Chat UI

**Wave**: 6

**Requires**: Story 1.5

**Persona**: Student

**Description**:
As a student, I need a user-friendly web interface where I can upload my PDF, ask questions, and see answers with citations displayed clearly. The interface should be intuitive and responsive for studying on various devices.

**Acceptance Criteria**:
1. Web UI allows students to upload PDF files and see confirmation of upload success
2. Chat interface displays student questions, chatbot answers, and citations in a readable format

**Technical Notes**:
- Build frontend with web framework (React, Vue, or vanilla HTML/JS)
- Implement file upload component with drag-and-drop support
- Design chat display for questions/answers with citation highlighting
- Implement session management (session-scoped PDF storage, reset on new session)
- Responsive design for desktop and tablet viewing
- Test cross-browser compatibility

**Jira**: —

---

## Story 1.7: API Integration & End-to-End Testing

**Wave**: 7

**Requires**: Story 1.6

**Persona**: Student

**Description**:
As the development team, I need to ensure all components work together seamlessly in a complete RAG pipeline, with proper API design, error handling, session management, and comprehensive testing to validate the system works end-to-end for exam preparation.

**Acceptance Criteria**:
1. Backend API properly routes requests (upload, query) through the RAG pipeline without errors
2. Full end-to-end flow is tested: PDF upload → question → answer with citation

**Technical Notes**:
- Design and implement REST API endpoints (POST /upload, POST /query, GET /session)
- Implement session management (ephemeral storage, cleanup)
- Add comprehensive error handling and logging
- Create end-to-end test cases covering happy path and error scenarios
- Test accuracy of answers against ground truth (sample PDFs with known answers)
- Performance testing (response latency, embedding generation time)
- Test with diverse academic materials (textbooks, lecture notes, research papers)
- Documentation for API and deployment instructions

**Jira**: —

---

## Story Metadata

| Attribute | Value |
|-----------|-------|
| **Total Stories** | 7 |
| **Story Format** | Feature-Based, Large Scope |
| **Dependencies** | Strictly Sequential (1.2 → 1.1, 1.3 → 1.2, etc.) |
| **Development Approach** | Code-First (tests integrated into acceptance criteria) |
| **Estimated Duration** | 3-5 days per story (21-35 days total for solo developer) |
| **Acceptance Criteria Style** | Minimal (1-2 per story) |

---

**Next Step**: Review and approve these stories, then proceed to Dependency Graph stage where wave numbers will be assigned based on sequential dependencies.
