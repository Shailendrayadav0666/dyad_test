# Frontend Components & UI/UX Design

**Scope**: Web interface structure, components, state management, user flows  
**Framework**: TBD (React, Vue, or vanilla JS — decided in Story 1.6)  
**Design Philosophy**: Simple, clean, focused on exam preparation use case

---

## Page Structure

### Single-Page Application (SPA)

The frontend is a single-page app with minimal routing:

```
ChatbotApp
├── Header
│   ├── Title: "Exam Prep Chatbot"
│   └── Status: "Ready" | "Processing" | "PDF Uploaded"
├── Main Content
│   ├── [If no session] UploadSection
│   └── [If session active] ChatSection
└── Footer
    └── Info/Help text
```

---

## Component 1: Upload Section

**Purpose**: Accept PDF upload, display upload progress

**Props** (if using component framework):
- `onUploadStart()`: Callback when upload begins
- `onUploadSuccess(sessionId)`: Callback with session_id
- `onUploadError(error)`: Callback if upload fails

**State**:
- `isUploading` (boolean): Upload in progress
- `uploadProgress` (0-100): File upload progress
- `selectedFile` (File): User-selected PDF
- `error` (string): Error message if any

**Rendering**:
```
┌─────────────────────────────────────┐
│    Upload Your Course Material       │
│                                     │
│  [Drag & drop PDF here]             │
│        or                           │
│  [Browse Files button]              │
│                                     │
│  ☐ I accept the privacy policy      │
│                                     │
│  [Upload PDF button]                │
└─────────────────────────────────────┘
```

**Interactions**:
- Drag-and-drop file into upload zone
- Click "Browse Files" to select
- Click "Upload PDF" to submit
- Show progress bar during upload
- On success: Hide upload section, show chat
- On error: Display error message, allow retry

**Validation**:
- File must be PDF
- File must be < 50MB
- Button disabled until file selected

---

## Component 2: Chat Section

**Purpose**: Display Q&A history, accept questions, show answers with citations

**Props**:
- `sessionId` (string): Active session ID
- `onQuestion(question)`: Submit question to API
- `onClearSession()`: Start new session

**State**:
- `messages` (list): Q&A history
  ```
  [
    {type: "question", text: "What is photosynthesis?", timestamp: "..."},
    {type: "answer", text: "Photosynthesis is...", citations: [...], timestamp: "..."},
    ...
  ]
  ```
- `isWaiting` (boolean): Waiting for answer
- `inputValue` (string): Current question text

**Rendering**:
```
┌─────────────────────────────────────┐
│  PDF Ready | Clear & Upload New     │
├─────────────────────────────────────┤
│                                     │
│  Q: What is photosynthesis?         │
│  [timestamp]                        │
│                                     │
│  A: Photosynthesis is the process   │
│  by which plants convert light...   │
│                                     │
│  Sources:                           │
│  • Page 5                           │
│  • Page 12, Section 3.1             │
│  [timestamp]                        │
│                                     │
│  Q: How does it relate to respiration?
│  [timestamp]                        │
│                                     │
│  A: Respiration is the reverse...   │
│  ...                                │
│                                     │
├─────────────────────────────────────┤
│ [Question input field         ] [?] │
│                                     │
│ [Submit] [Clear History]            │
└─────────────────────────────────────┘
```

**Sub-Components**:
- **MessageBubble**: Renders single Q or A
- **CitationLink**: Renders citation as clickable/hoverable
- **LoadingIndicator**: Shows while waiting for answer

---

## Component 3: Message Bubble (Q&A)

**Purpose**: Display individual question or answer

**Props**:
- `type` ("question" | "answer"): Message type
- `text` (string): Message content
- `citations` (list[string]): For answers only
- `sources` (list): For answers, source chunk info
- `timestamp` (string): ISO timestamp

**Question Bubble Rendering**:
```
┌─────────────────────────────┐
│  👤 You                     │
│  What is osmosis?           │
│  2:15 PM                    │
└─────────────────────────────┘
```

**Answer Bubble Rendering**:
```
┌─────────────────────────────────────┐
│  🤖 Exam Assistant                  │
│  Osmosis is the movement of...      │
│                                     │
│  Sources:                           │
│  • Page 8                           │
│  • Page 23, Section 4.2             │
│                                     │
│  2:16 PM                            │
└─────────────────────────────────────┘
```

**Interactions**:
- Citations clickable → show context
- Hover over answer → show relevance score (future)
- Copy answer button (future)

---

## Component 4: Input Section

**Purpose**: Accept user questions

**Elements**:
- **Text Input**: Multiline input for questions (placeholder: "Ask a question...")
- **Submit Button**: Send question (disabled while waiting)
- **Clear History**: Clears chat (optional)

**State**:
- `inputValue` (string): Current typed text
- `isDisabled` (boolean): Disabled while waiting for answer

**Behaviors**:
- Submit on button click or Enter key
- Validate input (not empty, 2-1000 chars)
- Disable input while waiting for response
- Clear input after submit
- Show error if validation fails

---

## State Management

**Global State** (minimal for PoC):
- `sessionId` (string): Current session ID
- `isSessionActive` (boolean): Has PDF uploaded
- `isLoading` (boolean): Waiting for API response
- `error` (string): Error message if any
- `messages` (list): Q&A history

**Component Local State**:
- **Upload**: File selection, progress
- **Chat**: Input field, message list
- **Input**: Current text value

**State Persistence** (Browser Storage):
- Store `sessionId` in localStorage
- Store `messages` in localStorage (for replay)
- Clear on page refresh? (UX decision: TBD)

---

## API Integration Points

### Upload Component → /upload Endpoint
```
POST /upload
Content-Type: multipart/form-data
Body: {file: <PDF file>}

Response: 200 OK
{
  "session_id": "uuid-123",
  "status": "ready",
  "pdf_info": {
    "filename": "notes.pdf",
    "pages": 50
  }
}
```

### Chat Component → /query Endpoint
```
POST /query
Content-Type: application/json
Body: {
  "session_id": "uuid-123",
  "question": "What is X?"
}

Response: 200 OK
{
  "answer": "X is a...",
  "citations": ["Page 5", "Page 23, Section 4"],
  "sources": [
    {
      "chunk": "text excerpt",
      "page": 5,
      "score": 0.87
    }
  ]
}
```

---

## User Interaction Flows

### Flow 1: Upload & First Question
```
User                          Frontend              Backend
  │                              │                    │
  ├─ Select PDF ──────────────→  │                    │
  │                              ├─ POST /upload ────→ │
  │                              │                    ├─ Process
  │                              │← 200 + session ────┤
  │                              │                    │
  ├─ See "PDF Ready" ←──────────┤                    │
  │                              │                    │
  ├─ Type question ──────────→   │                    │
  ├─ Click Submit ───────────→   │                    │
  │                              ├─ POST /query ─────→ │
  │                              │                    ├─ Retrieve
  │                              │                    ├─ Generate
  │                              │← 200 + answer ────┤
  │                              │                    │
  ├─ See answer + citations ←───┤                    │
```

### Flow 2: Follow-Up Questions (Same Session)
```
User types new question
  ├─ Frontend stores session_id from first upload
  ├─ POST /query (same session_id, new question)
  ├─ Backend reuses Qdrant collection
  ├─ Return answer (fast, no re-upload needed)
  └─ Display in chat history
```

### Flow 3: New PDF (Clear & Start Over)
```
User clicks "Clear & Upload New"
  ├─ Clear chat history
  ├─ Clear session_id
  ├─ Clear localStorage
  └─ Show upload section again
```

---

## Error Handling in Frontend

### Upload Errors
| Error | Display |
|-------|---------|
| Invalid file type | "Please upload a PDF file" |
| File too large | "File must be less than 50 MB" |
| Network error | "Upload failed. Please try again." |
| Server error | "Error processing PDF. Please try again." |

### Query Errors
| Error | Display |
|-------|---------|
| Empty question | "Please enter a question" |
| Session expired | "Session expired. Please upload a new PDF." |
| Network error | "Failed to get answer. Please try again." |
| API timeout | "Response took too long. Please try again." |

---

## Responsive Design

**Desktop** (> 768px):
- Full width chat interface
- Side-by-side upload and chat (future refinement)

**Tablet** (481-768px):
- Full width, single column
- Touch-friendly buttons

**Mobile** (< 480px):
- Full width
- Large tap targets (48px minimum)
- Input at bottom (sticky)

---

## Accessibility Features (Basic)

- **Alt text**: All images have descriptive alt
- **Keyboard nav**: Tab through buttons, inputs
- **Color contrast**: WCAG AA minimum
- **Focus indicators**: Visible focus rings
- **Labels**: All inputs labeled
- **Screen reader**: Semantic HTML, ARIA labels where needed

---

## Performance Considerations

- **Input debouncing**: Limit API calls on rapid typing (future)
- **Message virtualization**: If thousands of messages, virtualize (future)
- **Lazy loading**: Load images/components on demand (future)

---

## UI/UX Principles

**For Exam Preparation**:
- Clean, distraction-free interface
- Clear citation display (key feature)
- Quick question-answer flow
- Easy to try multiple questions
- Clear feedback on processing state

---

## Future Enhancements (Not in PoC)

- Citation highlighting in answers
- Follow-up question suggestions
- Answer quality feedback
- Search within chat history
- Dark mode
- Multi-language support

---

**Summary**: Simple, focused web interface optimized for exam preparation use case with minimal state management.
