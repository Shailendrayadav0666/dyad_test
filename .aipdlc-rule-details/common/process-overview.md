# ai-pdlc Adaptive Workflow Overview

**Purpose**: Technical reference for AI model and developers to understand complete workflow structure.

**Note**: Similar content exists in welcome-message.md (user welcome message) and README.md (documentation). This duplication is INTENTIONAL - each file serves a different purpose:
- **This file**: Detailed technical reference with Mermaid diagram for AI model context loading
- **welcome-message.md**: User-facing welcome message with ASCII diagram
- **README.md**: Human-readable documentation for repository

## The Three-Phase Lifecycle:
• **INCEPTION PHASE**: Planning and architecture (Workspace Detection → Requirements → User Stories → Dependency Graph → Workflow Planning → Application Design)
• **CONSTRUCTION PHASE**: System-level design → 🛑 STOP → per-story Code Generation via `dev-implement` (on a story branch cut from the Epic branch; code, then unit tests to ≥90% coverage) → optional Code Review & Remediate
• **OPERATIONS PHASE**: Placeholder for future deployment and monitoring workflows

**🧪 SDET TRACK (parallel, NOT part of any phase)**: **Build and Test belongs to SDET, not to Construction** — neither at epic level nor at story level. SDET runs **`/sdet-implement`** per story, at the same time as development, to generate that story's manual test steps from its acceptance criteria (no code is read) into `aipdlc-docs/tests/<JIRA-ID>-<jira-title>/`, and **`sdet-list-work`** on the epic branch to move merged, tested stories to 🧪 Ready for Testing.

## The Adaptive Workflow:
• **Workspace Detection** (always; captures the Parent Jira Epic link if provided) → **Reverse Engineering** (brownfield only) → **Requirements Analysis** (always, adaptive depth) → **User Stories** (always; asks team size, + optional push to Jira with stories linked to the Parent Epic) → **Dependency Graph** (always; assigns `requires`) → **Workflow Planning** (always) → **Application Design** (conditional) → **System-Level Design** (conditional; single pass) → 🛑 **STOP** → **Code Generation** (per-story, via `dev-implement`, on story branches cut from the Epic branch, with unit tests to ≥90% coverage) → **Code Review & Remediate** (optional; story-wise or all stories). Running alongside from the moment stories exist: the **SDET track** — **`/sdet-implement`** (Build and Test per story) and **`sdet-list-work`**.

## How It Works:
• **AI analyzes** your request, workspace, and complexity to determine which stages are needed
• **These stages always execute**: Workspace Detection (incl. automatic Epic branch creation), Requirements Analysis (adaptive depth), User Stories (team size + optional Jira push), Dependency Graph (`requires`), Workflow Planning, Code Generation (per-story via `dev-implement`, with unit tests to ≥90% coverage)
• **All other stages are conditional**: Reverse Engineering, Application Design, system-level design stages (Functional Design, NFR Requirements, NFR Design, Infrastructure Design)
• **Optional, user-initiated**: Code Review and Remediate — independently invokable at any time for a specific story or all stories together (`code-review`, `remediate`)
• **SDET-initiated, parallel to everything above**: `/sdet-implement` (Build and Test, per story) and `sdet-list-work` (merged, tested stories → Ready for Testing). Never auto-run — SDET types them.
• **Mandatory STOP**: after the design stages and before any code generation, the workflow halts — code is generated per-story only when the user types `dev-implement`
• **No fixed sequences**: Stages execute in the order that makes sense for your specific task

## Your Team's Role:
• **Answer questions** in dedicated question files using [Answer]: tags with letter choices (A, B, C, D, E)
• **Option E available**: Choose "Other" and describe your custom response if provided options don't match
• **Work as a team** to review and approve each phase before proceeding
• **Collectively decide** on architectural approach when needed
• **Important**: This is a team effort - involve relevant stakeholders for each phase

## ai-pdlc Three-Phase Workflow:

```mermaid
flowchart TD
    Start(["User Request"])
    
    subgraph INCEPTION["🔵 INCEPTION PHASE"]
        WD["Workspace Detection<br/><b>ALWAYS</b>"]
        RE["Reverse Engineering<br/><b>CONDITIONAL</b>"]
        RA["Requirements Analysis<br/><b>ALWAYS</b>"]
        Stories["User Stories<br/>(team size + Jira)<br/><b>ALWAYS</b>"]
        DG["Dependency Graph<br/>(requires)<br/><b>ALWAYS</b>"]
        WP["Workflow Planning<br/><b>ALWAYS</b>"]
        AppDesign["Application Design<br/><b>CONDITIONAL</b>"]
    end
    
    subgraph CONSTRUCTION["🟢 CONSTRUCTION PHASE"]
        FD["Functional Design<br/><b>CONDITIONAL</b>"]
        NFRA["NFR Requirements<br/><b>CONDITIONAL</b>"]
        NFRD["NFR Design<br/><b>CONDITIONAL</b>"]
        ID["Infrastructure Design<br/><b>CONDITIONAL</b>"]
        STOP["🛑 STOP — use dev-implement<br/><b>MANDATORY HALT</b>"]
        CG["Code Generation<br/>per-story + unit tests ≥90%<br/><b>dev-implement</b>"]
        CR["Code Review / Remediate<br/><b>OPTIONAL</b>"]
    end
    
    subgraph SDETTRACK["🧪 SDET TRACK — parallel, not a phase"]
        BT["Build and Test<br/>per story, manual steps from AC<br/><b>/sdet-implement</b>"]
        QS["SDET Sign-off<br/>merged + tested → Ready for Testing<br/><b>sdet-list-work</b>"]
    end
    
    subgraph OPERATIONS["🟡 OPERATIONS PHASE"]
        OPS["Operations<br/><b>PLACEHOLDER</b>"]
    end
    
    Start --> WD
    WD -.-> RE
    WD --> RA
    RE --> RA
    
    RA --> Stories
    Stories --> DG
    DG --> WP
    
    WP -.-> AppDesign
    AppDesign -.-> FD
    WP -.-> FD
    FD -.-> NFRA
    NFRA -.-> NFRD
    NFRD -.-> ID
    ID --> STOP
    WP --> STOP
    STOP -->|user types dev-implement| CG
    CG -.->|repeat per story| CG
    CG -.-> CR
    Stories -.->|SDET starts in parallel| BT
    BT -.->|repeat per story| BT
    BT --> QS
    CG --> QS
    QS -.-> OPS
    QS --> End(["Complete"])
    
    style WD fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style RA fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style Stories fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style DG fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style WP fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style STOP fill:#E53935,stroke:#B71C1C,stroke-width:3px,color:#fff
    style CG fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style BT fill:#26A69A,stroke:#00695C,stroke-width:3px,color:#fff
    style QS fill:#26A69A,stroke:#00695C,stroke-width:3px,color:#fff
    style CR fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style OPS fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style RE fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style AppDesign fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style FD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style NFRA fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style NFRD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style ID fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style INCEPTION fill:#BBDEFB,stroke:#1565C0,stroke-width:3px, color:#000
    style CONSTRUCTION fill:#C8E6C9,stroke:#2E7D32,stroke-width:3px, color:#000
    style SDETTRACK fill:#B2DFDB,stroke:#00695C,stroke-width:3px, color:#000
    style OPERATIONS fill:#FFF59D,stroke:#F57F17,stroke-width:3px, color:#000
    style Start fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000
    style End fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000
    
    linkStyle default stroke:#333,stroke-width:2px
```

**Stage Descriptions:**

**🔵 INCEPTION PHASE** - Planning and Architecture
- Workspace Detection: Analyze workspace state and project type (ALWAYS)
- Reverse Engineering: Analyze existing codebase (CONDITIONAL - Brownfield only)
- Requirements Analysis: Gather and validate requirements (ALWAYS - Adaptive depth)
- User Stories: Create user stories and personas; ask team size; populate the Story Tracker; optional push to Jira with each story linked to the Parent Epic from `aipdlc-state.md` `## Jira` (ALWAYS)
- Dependency Graph: Record each story's `requires` dependencies so independent stories can be developed in parallel; write dependency-graph.yml (ALWAYS — right after User Stories)
- Workflow Planning: Create execution plan (ALWAYS)
- Application Design: High-level component identification and service layer design (CONDITIONAL)

**🟢 CONSTRUCTION PHASE** - Design and Implementation
- Functional Design: Detailed business logic design at the system level (CONDITIONAL, system-level)
- NFR Requirements: Determine NFRs and select tech stack (CONDITIONAL, system-level)
- NFR Design: Incorporate NFR patterns and logical components (CONDITIONAL, system-level)
- Infrastructure Design: Map to actual infrastructure services (CONDITIONAL, system-level)
- 🛑 STOP: mandatory halt after the design stages, before any Code Generation
- Code Generation: Per-**story**, triggered by `dev-implement` only — Story Selection (tracker or Jira) → story branch cut from the Epic branch → Part 1 Planning → Part 2 Generation → unit tests generated + run to ≥90% coverage (ALWAYS, per-story)
- Code Review: Review a story's code, or all stories together, read-only, produce a versioned report (OPTIONAL, `code-review`)
- Remediate: Fix issues from a review report (fix → unit test → green, running only the in-scope story's unit tests), annotate the report in place (OPTIONAL, `remediate`)

**🧪 SDET TRACK** - Parallel to Construction, owned by SDET (NOT a Construction stage at epic or story level)
- Build and Test: Per **story**, triggered by **`/sdet-implement`** only — resolves one story, reads its acceptance criteria (Jira / `stories.md`), requirements and design artifacts, and writes **manual test steps** for every applicable test plan (build verification, integration, E2E, API, contract, security, performance, accessibility) into `aipdlc-docs/tests/<JIRA-ID>-<jira-title>/`. **Never reads application source code** — it runs while the developer is still writing it. Manual test steps only: no test automation, no test execution, no branches or PRs (SDET-initiated, per story)
- SDET Sign-off: Triggered by **`sdet-list-work`** on the epic branch — pulls latest, reports which stories dev has merged (test these) vs still in development, then asks SDET which merged-and-tested stories to move to 🧪 Ready for Testing and moves exactly those in the Story Tracker and Jira (SDET-initiated)

**🟡 OPERATIONS PHASE** - Placeholder
- Operations: Placeholder for future deployment and monitoring workflows (PLACEHOLDER)

**Key Principles:**
- Phases execute only when they add value
- Each phase independently evaluated
- INCEPTION focuses on "what" and "why"
- CONSTRUCTION focuses on "how" — build and test is SDET's parallel track, not a Construction stage
- OPERATIONS is placeholder for future expansion
- Simple changes may skip conditional INCEPTION stages
- Complex changes get full INCEPTION and CONSTRUCTION treatment
---

## 🐞 Bug/Defect Flow (variant)

When `aipdlc-state.md` `## Jira` records `Workflow Type: bug` (started via `ticket-implement <JIRA-ID>` routed to bug, or the direct keyword `bug-fix <JIRA-ID>`, on an existing Bug/Story ticket), the lifecycle is the TRIMMED variant defined in `workflows/bug-fix.md` + `workflows/bug-fix-implement.md` — ONE flow with a single break at design-done — the **SDET Handoff Break** (`bug-fix.md` Step 9: analysis + design artifacts committed and pushed on the bug branch, the SDET told to pull it and run `/sdet-implement <JIRA-ID>`, then a yes/no that continues into the fix in the same session, no second keyword) — NOT the epic flow above:
• ONE branch `bug/<JIRA-ID>-<title>` from the base branch (no epic/story branches) • Impact Analysis + line-level AI-Origin Detection via `agents/defect-provenance-analyst.md` (traces each defective line to its introducing commit; may label the ticket `ai-generated-defect`; resolves the originating story/bug/enhancement ticket and links the bug to it as `is caused by` — automatic, no confirmation; if the instance has no causal link type, falls back to a `Relates` link + a comment recording the direction) • ONE story from the ticket, NO Dependency Graph, no Jira story push • no PR at requirements approval — a single `[BUG]` PR to the base branch at the end • baseline + full regression runs around the fix • ticket stays In Development after the PR — SDET transitions it via `sdet-list-work` Option B run **on the bug branch, before the archive** (never on the base branch; the base branch's only cycle action is `stitch-delta`) • 🔴 **MANUAL archive** — the operator runs `archive-epic` (→ `aipdlc-archives/bugs/<BUG-ID>-<name>/`) once the SDET test-plan PR has merged into the bug branch, and before the `[BUG]` PR merges; the workflow NEVER auto-invokes it.
A resumed session MUST check `Workflow Type` FIRST and follow the bug workflow files when it is `bug`.
