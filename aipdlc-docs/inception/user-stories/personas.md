# User Personas — RAG Exam Preparation Chatbot

---

## Primary Persona: The Student

**Name**: Alex

**Role**: University Student

**Goals**:
- Prepare effectively for upcoming exams
- Quickly find answers to questions about course materials
- Understand complex topics by getting contextual explanations
- Know where in the course materials to find relevant information

**Pain Points**:
- Spends too much time searching through textbooks and lecture notes
- Gets confused when studying multiple materials (handouts, textbooks, lecture slides)
- Needs quick verification of understanding during study sessions
- Struggles to find exact page references for information

**Technical Proficiency**: Moderate (comfortable with web apps, no coding required)

**Device Usage**: Laptop/desktop during study sessions; occasional tablet use

**Behavior**:
- Uploads course PDFs (textbook chapters, lecture notes, research papers)
- Asks questions while studying
- Expects immediate, accurate answers grounded in the materials
- Appreciates exact page/section references to locate material independently
- Studies in short sessions (30-60 minutes at a time)

**Context**:
- Typically prepares 1-2 weeks before exams
- Works alone (solo studying)
- Needs a simple, distraction-free interface
- Values accuracy and precision over speed

**Relevant Stories**:
- All stories (1.1 through 1.7) — The entire system is designed around this persona's needs

---

## Persona Coverage

| Persona | Primary Stories | Secondary Stories |
|---------|-----------------|-------------------|
| Student | 1.1, 1.5, 1.6 | 1.2, 1.3, 1.4, 1.7 |

**Rationale**: 
- **1.1 (PDF Upload)**: Direct interaction — student uploads materials
- **1.5 (Answer Generation)**: Direct interaction — student receives answers with citations
- **1.6 (Web UI)**: Direct interaction — student uses the interface
- **1.2-1.4**: Backend infrastructure supporting the student's needs
- **1.7**: System integration ensuring reliability for student use

---

## Persona-Driven Requirements

**From Alex's Goals and Pain Points:**
1. ✅ **Quick access to answers** → Story 1.4 (RAG Retrieval speeds up search)
2. ✅ **Exact source locations** → Story 1.5 (Answer includes page citations)
3. ✅ **Multi-material support** → Story 1.1 (Upload any PDF)
4. ✅ **Simple interface** → Story 1.6 (Intuitive web UI)
5. ✅ **Accuracy** → Story 1.5 (LLM grounded in retrieved context)

---

**Next Step**: Proceed to Dependency Graph stage to assign wave numbers based on sequential dependencies.
