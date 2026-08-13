# ai-pdlc Terminology Glossary

## Core Terminology

### Phase vs Stage

**Phase**: One of the three high-level lifecycle phases in ai-pdlc
- 🔵 **INCEPTION PHASE** - Planning & Architecture (WHAT and WHY)
- 🟢 **CONSTRUCTION PHASE** - Design, Implementation & Test (HOW)
- 🟡 **OPERATIONS PHASE** - Deployment & Monitoring (future expansion)

**Stage**: An individual workflow activity within a phase
- Examples: Context Assessment stage, Requirements Assessment stage, Code Generation stage
- Each stage has specific prerequisites, steps, and outputs
- Stages can be ALWAYS-EXECUTE or CONDITIONAL

**Usage Examples**:
- ✅ "The CONSTRUCTION phase contains 7 stages"
- ✅ "The Code Generation stage is always executed"
- ✅ "We're in the INCEPTION phase, executing the Requirements Assessment stage"
- ❌ "The Requirements Assessment phase" (should be "stage")
- ❌ "The CONSTRUCTION stage" (should be "phase")

## Three-Phase Lifecycle

### INCEPTION PHASE
**Purpose**: Planning and architectural decisions  
**Focus**: Determine WHAT to build and WHY  
**Location**: `inception/` directory

**Stages**:
- Workspace Detection (ALWAYS)
- Reverse Engineering (CONDITIONAL - Brownfield only)
- Requirements Analysis (ALWAYS - Adaptive depth)
- User Stories (ALWAYS - asks team size; includes optional push to Jira)
- Dependency Graph (ALWAYS - assigns `requires`; right after User Stories)
- Workflow Planning (ALWAYS)
- Application Design (CONDITIONAL)

**Outputs**: Requirements, user stories, Story Tracker, dependency-graph.yml (requires), architectural decisions

### CONSTRUCTION PHASE
**Purpose**: Detailed design and implementation  
**Focus**: Determine HOW to build it  
**Location**: `construction/` directory

**Stages**:
- Functional Design (CONDITIONAL, system-level)
- NFR Requirements (CONDITIONAL, system-level)
- NFR Design (CONDITIONAL, system-level)
- Infrastructure Design (CONDITIONAL, system-level)
- 🛑 STOP CHECKPOINT (MANDATORY — after design, before Code Generation)
- Code Generation (ALWAYS, per-**story**) — triggered by `dev-implement`; Story Selection (tracker or Jira) → story branch cut from the Epic branch → Part 1: Planning → Part 2: Generation → unit tests to ≥90% coverage
- Code Review (OPTIONAL — `code-review`; read-only versioned report)
- Remediate (OPTIONAL — `remediate`; fixes review-report issues, fix → unit test → green, story-scoped unit tests only)

**Outputs**: Design artifacts, NFR implementations, code, unit tests

**Not in this phase**: **Build and Test** — it belongs to the SDET track below, not to Construction (neither at epic nor at story level).

### SDET TRACK (parallel — not a phase)
**Purpose**: Prove each story meets its acceptance criteria
**Focus**: Determine WHETHER it works
**Location**: `aipdlc-docs/tests/<JIRA-ID>-<jira-title>/` (one folder per story)

**Stages** (both SDET-initiated, never auto-run):
- Build and Test (per **story**, via **`/sdet-implement`**) — manual test steps for every applicable test plan, derived from the story's acceptance criteria; runs in parallel with development and never reads application source code
- SDET Sign-off (via **`sdet-list-work`**, on the epic branch) — reports merged vs in-development stories and moves SDET-tested merged stories to 🧪 Ready for Testing

**Outputs**: Per-story manual test plans and AC→test-case coverage matrices

### OPERATIONS PHASE
**Purpose**: Deployment and operational readiness  
**Focus**: How to DEPLOY and RUN it  
**Location**: `operations/` directory

**Stages**:
- Operations (PLACEHOLDER)

**Outputs**: Build instructions, deployment guides, monitoring setup, verification procedures

---

## Workflow Stages

### Always-Execute Stages
- **Workspace Detection**: Initial analysis of workspace state and project type
- **Requirements Analysis**: Gathering requirements (depth varies based on complexity)
- **User Stories**: Creating user stories and personas; asks team size first; populates the Story Tracker; optional push to Jira
- **Dependency Graph**: Mapping each story's `requires` dependencies so independent stories can run in parallel; writes `dependency-graph.yml`
- **Workflow Planning**: Creating execution plan for which phases to run
- **Code Generation**: Per-story, triggered by `dev-implement` — Story Selection → story branch → Part 1 (Planning) → Part 2 (Generation) → unit tests to ≥90% coverage

### SDET-Initiated Stages (parallel track — never auto-run)
- **Build and Test**: Per story, via `/sdet-implement` — manual test steps generated from the story's acceptance criteria into `aipdlc-docs/tests/<JIRA-ID>-<jira-title>/`; runs alongside development, reads no application code
- **SDET Sign-off**: Via `sdet-list-work` on the epic branch — merged, SDET-tested stories → 🧪 Ready for Testing

### Conditional Stages
- **Reverse Engineering**: Analyzing existing codebase (brownfield projects only)
- **Application Design**: Designing application components, methods, business rules, and services
- **Functional Design**: Technology-agnostic business logic design (system-level)
- **NFR Requirements**: Determining NFRs and selecting tech stack (system-level)
- **NFR Design**: Incorporating NFR patterns and logical components (system-level)
- **Infrastructure Design**: Mapping to actual infrastructure services (system-level)

### Optional, User-Initiated Stages
- **Code Review** (`code-review`): Read-only review of a story's code, or all stories together; produces a versioned report
- **Remediate** (`remediate`): Fixes issues from a review report (fix → unit test → green, running only the in-scope story's unit tests); annotates the report in place

## Application Design Terms

- **Component**: A functional system with specific responsibilities
- **Method**: A function or operation within a component with defined business rules
- **Business Rule**: Logic that governs method behavior and validation
- **Service**: Orchestration layer that coordinates business logic across components
- **Component Dependency**: Relationship and communication pattern between components

## Architecture Terms (Infrastructure)

### Service
An independently deployable component in a microservices architecture. Each service is separately deployable.

**Usage**: "The Payment Service handles all payment processing"

### Module
A logical grouping of functionality within a single service or monolith. Modules are not independently deployable.

**Usage**: "The authentication module within the User Service"

### Component
A reusable building block within a service or module. Components are classes, functions, or packages that provide specific functionality.

**Usage**: "The EmailValidator component validates email addresses"

## Development & Tracking Terms

### Story Tracker
A table in `aipdlc-docs/aipdlc-state.md` (section `## Story Tracker`) with one row per user story: Story ID, Title, Requires, Jira key, Status, PR, Merged, Start, End, Recorded. It is the single source of truth for story status. The ONLY valid statuses are `🟢 Ready for Development` (initial), `🔵 In Development` (picked via `dev-implement`, held through code generation, Code Review, Remediate, the PR raise, and the auto PR review), and `🧪 Ready for Testing` (only after the story's PR is **merged** into the epic branch). The `PR` column stores the PR URL (set when the PR is raised) and `Merged` is `no`/`yes`. Rows are created in User Stories, `Requires` filled by Dependency Graph; the `🟢→🔵` transition is driven by `dev-implement`, and the `🔵→🧪` transition happens after the PR merges, when SDET signs the story off via `sdet-list-work`. Code Review and Remediate do not change status.

### Ready Story
A story whose `requires` prerequisites are ALL `🧪 Ready for Testing` (or that has none). Ready stories have no dependencies on each other's in-progress work and can be implemented **in parallel** by different developers. Determined from the Dependency Graph at selection time (the Doability Gate).

### Dependency Graph
The Inception stage (run right after User Stories) that computes each story's `requires` dependencies. Outputs `aipdlc-docs/inception/dependency-graph.yml` and a `## Dependency Graph` section (Mermaid + ready-stories summary) in `aipdlc-state.md`.

### Parent Epic (Jira)
The **existing** Jira Epic the user provides at workflow start (e.g., "using aipdlc" + an Epic link **whose description defines what to build**). At capture time its summary/description/acceptance criteria are fetched into `aipdlc-docs/inception/requirements/epic-brief.md` (primary input to Requirements Analysis and User Stories), and its key/URL/Project Key are recorded in `aipdlc-docs/aipdlc-state.md` under `## Jira` so any session — including a new chat resuming at the story stage — can find it. Every story pushed to Jira during User Stories Part 3 is linked to this Parent Epic (unless the user chose `none` at push time). ai-pdlc never creates Epics itself;

### `dev-implement` (keyword)
The keyword a developer types to build a single story. It triggers per-story Code Generation: Story Selection (moves the story `🟢 Ready for Development` → `🔵 In Development`) → Doability Gate (all `requires` `🧪 Ready for Testing`) → story branch cut from the Epic branch (`common/branching-strategy.md`) → code generation → unit tests generated + run to ≥90% coverage → automated Code Review → on approval, PR raised into the Epic branch and the story moves to `🧪 Ready for Testing`. See `workflows/dev-implement.md`.

### `team_size`
The number of developers who will implement, asked FIRST in User Stories. Drives story granularity so ≥ `team_size` independent stories are workable in parallel at any time. Stored in `aipdlc-state.md` and reused by the Dependency Graph stage.

## Terminology Guidelines

### When to Use Each Term

**Service**:
- When referring to independently deployable components
- In microservices architecture contexts
- In deployment and infrastructure discussions
- Example: "The Order Service will be deployed to ECS"

**Module**:
- When referring to logical groupings within a service
- In monolith architecture contexts
- When discussing internal organization
- Example: "The reporting module generates all reports"

**Component**:
- When referring to specific classes, functions, or packages
- In design and implementation discussions
- When discussing reusable building blocks
- Example: "The DatabaseConnection component manages connections"

## Stage Terminology

### Planning vs Generation
- **Planning**: Creating a plan with questions and checkboxes for execution
- **Generation**: Executing the plan to create artifacts

Examples (these are internal sub-steps within a single stage, not separate stages):
- Story Planning → Story Generation (within User Stories stage)
- NFR Planning → NFR Generation (within NFR Requirements stage)
- Code Generation Part 1 (Planning) → Code Generation Part 2 (Generation)

### Depth Levels
- **Minimal**: Quick, focused execution for simple changes
- **Standard**: Normal depth with standard artifacts for typical projects
- **Comprehensive**: Full depth with all artifacts for complex/high-risk projects

## Artifact Types

### Plans
Documents with checkboxes and questions that guide execution.
- Located in `aipdlc-docs/plans/`
- Examples: `story-generation-plan.md`, `functional-design-plan.md`

### Artifacts
Generated outputs from executing plans.
- Located in various `aipdlc-docs/` subdirectories
- Examples: `requirements.md`, `stories.md`, `design.md`

### State Files
Files tracking workflow progress and status.
- `aipdlc-state.md`: Overall workflow state
- `audit.md`: Complete audit trail of all interactions

## Common Abbreviations

- **NFR**: Non-Functional Requirements
- **API**: Application Programming Interface
- **CDK**: Cloud Development Kit (AWS)
