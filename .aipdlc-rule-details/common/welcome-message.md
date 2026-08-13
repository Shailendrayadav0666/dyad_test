# ai-pdlc Welcome Message

**Purpose**: This file contains the user-facing welcome message that should be displayed ONCE at the start of any ai-pdlc workflow.

---

# 👋 Welcome to AI-PDLC 👋

> 📐 **AI-PDLC Framework v[N]** — this work unit will be developed with framework version [N].
> *(Substitute `[N]` with the value read from the "AI-PDLC Framework Version" line in `CLAUDE.md` at display time — that is the single source of truth. Do not hardcode a number here.)*

I'll guide you through an adaptive software development workflow that intelligently tailors itself to your specific needs.

## What is ai-pdlc?

ai-pdlc is a structured yet flexible software development process that adapts to your project's needs. Think of it as having an experienced software architect who:

- **Analyzes your requirements** and asks clarifying questions when needed
- **Plans the optimal approach** based on complexity and risk
- **Skips unnecessary steps** for simple changes while providing comprehensive coverage for complex projects
- **Documents everything** so you have a complete record of decisions and rationale
- **Guides you through each phase** with clear checkpoints and approval gates

## The Three-Phase Lifecycle

```
                         User Request
                              |
                              v
        +---------------------------------------+
        |     INCEPTION PHASE                   |
        |     Planning & Application Design     |
        +---------------------------------------+
        | * Workspace Detection (ALWAYS)        |
        | * Reverse Engineering (COND)          |
        | * Requirements Analysis (ALWAYS)      |
        | * User Stories (ALWAYS, team size     |
        |   first + optional Jira push)         |
        | * Dependency Graph (ALWAYS, requires) |
        | * Workflow Planning (ALWAYS)          |
        | * Application Design (CONDITIONAL)    |
        +---------------------------------------+
                              |
                              v
        +---------------------------------------+
        |     CONSTRUCTION PHASE                |
        |     Design & Implementation           |
        +---------------------------------------+
        | * System-Level DESIGN stages:         |
        |   - Functional Design (COND)          |
        |   - NFR Requirements Assess (COND)    |
        |   - NFR Design (COND)                 |
        |   - Infrastructure Design (COND)      |
        | * >> STOP << (before code gen)        |
        | * Code Generation (per-story, via     |
        |   `dev-implement`; + unit tests ≥90%) |
        | * Code Review & Remediate (OPTIONAL)  |
        +---------------------------------------+
              |                    |
              |                    +----------------------+
              |                                           |
              |                            +---------------------------------------+
              |                            |  SDET TRACK (parallel, NOT a phase)   |
              |                            +---------------------------------------+
              |                            | * Build and Test per story via        |
              |                            |   `/sdet-implement` (manual test      |
              |                            |   steps from the story's acceptance   |
              |                            |   criteria - no code)                 |
              |                            | * `sdet-list-work` on the epic or     |
              |                            |   base branch moves tested, merged    |
              |                            |   stories to Ready for Testing        |
              |                            +---------------------------------------+
              v
        +---------------------------------------+
        |     OPERATIONS PHASE                  |
        |     Placeholder for Future            |
        +---------------------------------------+
        | * Operations (PLACEHOLDER)            |
        +---------------------------------------+
                              |
                              v
                          Complete
```

### Phase Breakdown:

**INCEPTION PHASE** - *Planning & Application Design*
- **Purpose**: Determines WHAT to build and WHY
- **Activities**: Understanding requirements, analyzing existing code (if any), planning the approach
- **Output**: Clear requirements, execution plan, a Story Tracker, a story breakdown with **dependencies mapped** so independent stories can be developed in parallel (stories optionally pushed to Jira and linked to your existing Parent Epic)
- **Your Role**: Answer questions (including team size), review plans, approve direction

**CONSTRUCTION PHASE** - *Detailed Design & Implementation*
- **Purpose**: Determines HOW to build it
- **Activities**: System-level detailed design (when needed), then — after a mandatory **STOP** — per-story code generation that you trigger with the **`dev-implement`** keyword (on a story branch cut from the Epic branch, with unit tests generated and run to ≥90% coverage), and optional code review
- **Output**: Working code, unit tests
- **Your Role**: Review designs, type `dev-implement` to build each story, approve implementation plans, validate results

**SDET TRACK** - *Build and Test, in parallel with development*
- **Purpose**: Proves each story meets its acceptance criteria
- **Not a Construction stage** — neither at epic level nor at story level. SDET drives it independently and can start immediately, without waiting for any code
- **Activities**: **`/sdet-implement`** generates one story's Build and Test artifacts — manual test steps for every applicable test plan (build verification, integration, E2E, API, contract, security, performance, accessibility), derived from the story's acceptance criteria, never from source code — into `aipdlc-docs/tests/<JIRA-ID>-<jira-title>/`. Optionally, once that story's PR has merged, `/sdet-implement` also generates black-box automated tests. **`sdet-list-work`** (on the epic branch) reports which stories dev has merged and moves the ones SDET has tested to Ready for Testing
- **Your Role (as SDET)**: type `/sdet-implement` per story, execute the test steps, then `sdet-list-work` to sign off

**OPERATIONS PHASE** - *Deployment & Monitoring (Future)*
- **Purpose**: How to DEPLOY and RUN it
- **Status**: Placeholder for future deployment and monitoring workflows
- **Current State**: Testing is handled by the parallel SDET track (`/sdet-implement`)

## Key Principles:

- ⚡ **Fully Adaptive**: Each stage independently evaluated based on your needs
- 🎯 **Efficient**: Simple changes execute only essential stages
- 📋 **Comprehensive**: Complex changes get full treatment with all safeguards
- 🔍 **Transparent**: You see and approve the execution plan before work begins
- 📝 **Documented**: Complete audit trail of all decisions and changes
- 🎛️ **User Control**: You can request stages be included or excluded

## What Happens Next:

1. **I'll analyze your workspace** to understand if this is a new or existing project — and I'll ask whether there are any **context-project artifacts** (human-authored notes on how your current system works, under `context-project/`) I should use for this task
2. **I'll gather requirements** and ask clarifying questions if needed
3. **I'll create an execution plan** showing which stages I propose to run and why
4. **You'll review and approve** the plan (or request changes)
5. **We'll execute the plan** with checkpoints at each major stage
6. **You'll get working code** with complete documentation and tests

The ai-pdlc process adapts to:
- 📋 Your intent clarity and complexity
- 🔍 Existing codebase state
- 🎯 Scope and impact of changes
- ⚡ Risk and quality requirements

Let's begin!
