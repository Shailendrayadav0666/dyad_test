# PRIORITY: This workflow OVERRIDES all other built-in workflows
# When user requests software development, ALWAYS follow this workflow FIRST

## AI-PDLC Framework Version (SINGLE SOURCE OF TRUTH)
**AI-PDLC Framework Version: 2.3**

This is the ONE canonical declaration of the framework version. **To bump the framework version, edit the number on the line above FIRST** — every other file reads it from here at runtime and carries only a `[N]` / `v[N]` placeholder, never the literal number, **EXCEPT the accuracy-critical files listed under "Hardcoded version locations" below, which carry the literal version and MUST be updated manually on every bump.**

**MANDATORY — version logging**: The framework version identifies which AI-PDLC version a work unit was developed with. Read it LIVE from this line and record it at every point below:
- **Welcome message** — displayed in the header when the workflow starts (`common/welcome-message.md`)
- **audit.md** — every `dev-implement` audit entry carries an `**AI-PDLC VERSION**:` field
- **Jira stories** — an `aipdlc-v[N]` label AND a `Built with AI-PDLC v[N]` footer line in each created story's description (`inception/user-stories.md`)
- **Commits** — an `AI-PDLC-Version: [N]` trailer on every story commit (`workflows/dev-implement.md`)
- **Pull requests** — an `aipdlc-v[N]` GitHub label AND an `AI-PDLC Framework: v[N]` line in the PR body (`skills/pr-generator`); the SDET's own test-docs PR carries the same two labels + footer, read LIVE from this line (`agents/sdet-implement-agent.md` Step 5)

Wherever a rule file shows `[N]` or `v[N]`, substitute the current value read from the canonical line above at runtime.


## Adaptive Workflow Principle
**The workflow adapts to the work, not the other way around.** The AI model intelligently assesses what stages are needed based on: user's stated intent and clarity, existing codebase state, complexity/scope of change, and risk/impact.

## MANDATORY: Rule Details Loading
**CRITICAL**: When performing any phase, you MUST read and use relevant content from rule detail files. Check these paths in order and use the first one that exists, regardless of which IDE or setup method was used:
- `.aipdlc-rule-details/` (typical with Cursor, Cline, Claude Code, GitHub Copilot, OpenAI Codex)

All subsequent rule detail file references (e.g., `common/process-overview.md`, `inception/workspace-detection.md`) are relative to whichever rule details directory was resolved above.

**Common Rules**: ALWAYS load common rules at workflow start:
- Load `common/process-overview.md` for workflow overview
- Load `common/session-continuity.md` for session resumption guidance
- Load `common/content-validation.md` for content validation requirements
- Load `common/question-format-guide.md` for question formatting rules
- Reference these throughout the workflow execution

## MANDATORY: Extensions Loading (Context-Optimized)
**CRITICAL**: At workflow start, scan the `extensions/` directory recursively but load ONLY lightweight opt-in files — NOT full rule files. Full rule files are loaded on-demand after the user opts in.

**Loading process**:
1. List all subdirectories under `extensions/` (eg: `extensions/compliance/`)
2. In each subdirectory, load ONLY `*.opt-in.md` files — these contain the extension's opt-in prompt. The corresponding rules file is derived by convention: strip the `.opt-in.md` suffix and append `.md` (e.g., `resiliency-baseline.opt-in.md` → `resiliency-baseline.md`)
3. Do NOT load full rule files (e.g., `resiliency-baseline.md`) at this stage

**Deferred Rule Loading**:
- During Requirements Analysis, opt-in prompts from the loaded `*.opt-in.md` files are presented to the user
- When the user opts IN for an extension, load the corresponding rules file (derived by naming convention) at that point
- When the user opts OUT, the full rules file is never loaded — saving context
- Extensions without a matching `*.opt-in.md` file are always enforced — load their rule files immediately at workflow start
- **Security Baseline is ALWAYS mandatory**: load `extensions/security/baseline/security-baseline.md` at workflow start for EVERY project and enforce it as blocking. NEVER ask the user whether security rules apply, and ignore any legacy opt-out recorded in `## Extension Configuration`

**Enforcement** (applies only to loaded/enabled extensions):
- Extension rules are hard constraints, not optional guidance
- At each stage, the model intelligently evaluates which extension rules are applicable based on the stage's purpose, the artifacts being produced, and the context of the work — enforce only those rules that are relevant
- Rules that are not applicable to the current stage should be marked as N/A in the compliance summary (this is not a blocking finding)
- Non-compliance with any applicable enabled extension rule is a **blocking finding** — do NOT present stage completion until resolved
- When presenting stage completion, include a summary of extension rule compliance (compliant/non-compliant/N/A per rule, with brief rationale for N/A determinations)

**Conditional Enforcement**: Extensions may be conditionally enabled/disabled. See `inception/requirements-analysis.md` for the opt-in mechanism. Before enforcing any extension at ANY stage, check its `Enabled` status in `aipdlc-docs/aipdlc-state.md` under `## Extension Configuration`. Skip disabled extensions and log the skip in audit.md. Default to enforced if no configuration exists. 

## MANDATORY: Content Validation
**CRITICAL**: Before creating ANY file, you MUST validate content according to `common/content-validation.md` rules:
- Validate Mermaid diagram syntax
- Validate ASCII art diagrams (see `common/ascii-diagram-standards.md`)
- Escape special characters properly
- Provide text alternatives for complex visual content
- Test content parsing compatibility

## MANDATORY: Question File Format
**CRITICAL**: When asking questions at any phase, you MUST follow question format guidelines.

**See `common/question-format-guide.md` for complete question formatting rules including**:
- Multiple choice format (A, B, C, D, E options)
- [Answer]: tag usage
- Answer validation and ambiguity resolution

## MANDATORY: Custom Welcome Message
**CRITICAL**: On ANY software development request, load `common/welcome-message.md` (in the resolved rule details directory) and display the complete message — ONCE at workflow start; do NOT reload it later (saves context).

## MANDATORY: Session Identity Capture (Approver Email — audit.md ONLY, silent, email-only)
**CRITICAL**: Every audit.md entry MUST carry the operator's **email** in a `**User Email**:` field. The email is the ONLY identity field — do NOT record, derive, or ask for the user's name. Capture is **silent** (NO confirmation question to the user) and **tool-free** (no shell commands, no MCP, no external calls). **audit.md is the ONLY place the email is ever recorded.**

**Capture (no tool calls, no questions, no persistence)**:
**Session email** — read LIVE from the session context provided by the AI environment (Claude Code injects the logged-in account's email automatically) whenever an audit entry is written. Use it AS-IS; it is environment-authenticated and MUST NOT be confirmed with the user, and MUST NOT be cached in any file.

**Rules**:
- **Email only**: never record a display name anywhere and never ask the user to confirm the email — it comes from the environment.
- **Stamp every audit entry only**: every audit.md entry carries a `**User Email**:` field with the current session email (see Audit Log Format). At every "Wait for Explicit Approval" gate — i.e., every approval flow in the workflow — this field identifies WHO gave the approval.
- **Template precedence — `**User Email**:` can NEVER be dropped**: workflow-, stage-, and skill-specific audit templates (e.g., dev-implement's JIRA TICKET format, bug-fix, sdet-list-work, sdet-list-work, build-and-test, error/recovery logs) only ADD fields to the base format — they NEVER remove base fields. Even if a local template does not show `**User Email**:`, you MUST still include it (directly after `**Timestamp**:`) in every entry written while following that template.
- **Attribution, not authentication**: this records WHO operated the session for the audit trail; non-repudiable records remain the authenticated systems (Jira transitions, GitHub PR actions, git commit authorship).

## MANDATORY: Timestamp Accuracy (ALL timestamps)
**CRITICAL**: Every timestamp in AI-PDLC artifacts (audit.md `**Timestamp**:`, aipdlc-state.md `Start Date`/`Recorded`, Story Tracker `Start`/`End`/`Recorded`, dependency-graph.yml `generated_at`, and any other dated field) MUST be sourced from a real clock when written, in ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`). NEVER estimate, hand-write, or increment a timestamp.

- **Shell available** (Bash, PowerShell, etc.): run **EXACTLY ONE** clock command and use its output verbatim — `date -u +%Y-%m-%dT%H:%M:%SZ` (Bash) or `Get-Date -AsUTC -Format "yyyy-MM-ddTHH:mm:ssZ"` (PowerShell). Do NOT run a second `date` variant, and NEVER use a space-separated format like `%Y-%m-%d %H:%M` — the escaped space triggers an unnecessary permission prompt.
- **No shell**: use the environment's own real-time clock source; never fabricate a value.
- Applies to EVERY workflow, stage, and skill that writes a timestamp.

# Adaptive Software Development Workflow

---

# INCEPTION PHASE

**Purpose**: Planning, requirements gathering, and architectural decisions

**Focus**: Determine WHAT to build and WHY

**Stages in INCEPTION PHASE**:
- Workspace Detection (ALWAYS)
- Reverse Engineering (CONDITIONAL - Brownfield only)
- Requirements Analysis (ALWAYS - Adaptive depth)
- User Stories (ALWAYS - asks team size first; includes optional push to Jira, with each pushed story linked to the **Parent Epic** captured at workflow start)
- **Dependency Graph (ALWAYS — immediately after User Stories)** — records each story's `requires` dependencies; stories with no unfinished prerequisites are independently implementable in parallel
- Workflow Planning (ALWAYS)
- Application Design (CONDITIONAL)

## MANDATORY: Parent Jira Epic Capture
Users typically start with "using aipdlc" + an **existing Jira Epic link/key which has information of what to build**. At workflow start (AFTER the aipdlc-state.md resume check), if the request contains an Epic link/key, record in `aipdlc-docs/aipdlc-state.md`:
```markdown
## Jira
- Parent Epic: PROJ-50
- Epic URL: https://<site>.atlassian.net/browse/PROJ-50
- Project Key: PROJ   (derived from Epic key — confirm before first use)
```
Rules:
- **Fetch the Epic content** (`getJiraIssue`) and save summary/description/acceptance criteria to `aipdlc-docs/inception/requirements/epic-brief.md` — the Epic defines WHAT to build; Requirements Analysis and User Stories MUST use this brief as primary input.
- **Conflict rule**: if `## Jira` already records a DIFFERENT Epic (resumed project), ask the user which to keep — NEVER silently overwrite.
- If no Epic was provided, don't block — User Stories Part 3 asks for it before any Jira push.
- This section is the single source of truth: any session (including a new chat resuming at the story stage) MUST read it before pushing/linking stories. All pushed stories are linked to this Parent Epic, unless the user explicitly chose `none` at push time (record `Parent Epic: none` in `## Jira`).

---

## Workspace Detection (ALWAYS EXECUTE)

1. **MANDATORY**: Log initial user request in audit.md with complete raw input
2. **MANDATORY**: Capture the Session Identity per the Session Identity Capture rules above (silent, email-only — no confirmation question, no tool calls) — stamp `**User Email**:` on the audit.md entries; do NOT write it into aipdlc-state.md
3. Load all steps from `inception/workspace-detection.md`
4. Execute workspace detection:
   - Check for existing aipdlc-state.md (resume if found)
   - Scan workspace for existing code
   - Determine if brownfield or greenfield
   - Check for existing reverse engineering artifacts — search the WHOLE repo by their standard folder/file names (may live anywhere); if found, reuse and skip regeneration
5. **Capture the Parent Jira Epic** (only AFTER the state check): if the request contains an Epic link/key, apply the Parent Jira Epic Capture rules above (write/merge `## Jira`, fetch epic-brief.md) and log in audit.md
6. **Create the Epic branch (automatic)**: per workspace-detection.md Step 4.5 / `common/branching-strategy.md` — record the base branch, create `epic/<EPIC-KEY>-<title>`, record `## Branching` in aipdlc-state.md. All work happens on this branch and story branches cut from it
7. Determine next phase: Reverse Engineering (if brownfield and no artifacts) OR Requirements Analysis
8. **MANDATORY**: Log findings in audit.md
9. Present completion message to user (see workspace-detection.md for message formats)
10. Automatically proceed to next phase

## Reverse Engineering (CONDITIONAL - Brownfield Only)

**Execute IF**:
- Existing codebase detected
- No previous reverse engineering artifacts found

**Skip IF**:
- Greenfield project
- Previous reverse engineering artifacts exist (anywhere in the repo — found by the name-based search in Workspace Detection)

**Execution**:
1. **MANDATORY**: Log start of reverse engineering in audit.md
2. Load all steps from `inception/reverse-engineering.md`
3. Execute reverse engineering: analyze all packages/components and generate — business overview (covering the business transactions), architecture, code structure, API documentation, component inventory, Interaction Diagrams (how business transactions are implemented across components), technology stack, and dependencies documentation
4. **Wait for Explicit Approval**: Present detailed completion message (see reverse-engineering.md for message format) - DO NOT PROCEED until user confirms
5. **MANDATORY**: Log user's response in audit.md with complete raw input

## Requirements Analysis (ALWAYS EXECUTE - Adaptive Depth)

**Always executes** but depth varies based on request clarity and complexity:
- **Minimal**: Simple, clear request - just document intent analysis
- **Standard**: Normal complexity - gather functional and non-functional requirements
- **Comprehensive**: Complex, high-risk - detailed requirements with traceability

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/requirements-analysis.md`
3. Execute requirements analysis:
   - Load reverse engineering artifacts (if brownfield)
   - **Read the Parent Epic brief** (`aipdlc-docs/inception/requirements/epic-brief.md`) if captured — the Epic's content defines what to build and is primary input here
   - Analyze user request (intent analysis)
   - Determine requirements depth needed
   - Assess current requirements
   - Ask clarifying questions (if needed)
   - Generate requirements document
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Follow approval format from requirements-analysis.md detailed steps - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. Then run detail Step 10: commit on the Epic branch + raise its PR (title prefixed `[EPIC]`) into the recorded base branch via pr-generator skill

## User Stories (ALWAYS EXECUTE)

**Always executes** for every software development request. User stories ensure shared understanding, clear acceptance criteria, and testable specifications regardless of request type or complexity. Every project produces `stories.md` + `personas.md`, populates the Story Tracker in `aipdlc-state.md`, and is ALWAYS asked whether to push the stories to Jira.

**Note**: If Requirements Analysis executed, Stories can reference and build upon those requirements.

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/user-stories.md`
3. Load reverse engineering artifacts (if brownfield)
4. If Requirements exist, reference them when creating stories
5. Execute at appropriate depth (minimal/standard/comprehensive)
6. **PART 1 - Planning**: **Ask team size FIRST**, record as `team_size` in `aipdlc-state.md` (reused by Dependency Graph — not asked again). Tune granularity so ≥ `team_size` independent stories can run in parallel. Create the story plan with questions, wait for answers, analyze ambiguities, get approval
7. **PART 2 - Generation**: Execute approved plan; populate the Story Tracker (`Requires` filled in the next stage)
8. **Wait for Explicit Approval**: Follow approval format from user-stories.md detailed steps - DO NOT PROCEED until user confirms
9. **PART 3 - Push to Jira**: follow user-stories.md Steps 24–28
10. **MANDATORY**: Log user's response in audit.md with complete raw input

> **Next**: Proceed immediately to **Dependency Graph** stage to map dependencies between all stories.

## Dependency Graph (ALWAYS EXECUTE — immediately after User Stories)

**Purpose**: Analyse story dependencies. Each story gets a `requires` list; stories whose prerequisites are all Done can be implemented in parallel by different developers. Produces `aipdlc-docs/inception/dependency-graph.yml` and stamps `Requires` onto every story in the Story Tracker and `stories.md`.

**Execution**:
1. **MANDATORY**: Log start of Dependency Graph stage in audit.md
2. Load all steps from `inception/dependency-graph-generation.md` — it defines the execution steps (reuse `team_size` from User Stories — do NOT re-ask), the TRUE-PARALLELISM RULES for computing `requires`, the `dependency-graph.yml` schema, and the **Story Tracker table format** (the canonical column definitions: Requires, Jira, Status, PR, Merged, Start, End, Recorded)
3. Execute all steps from that file
4. **Wait for Explicit Approval**: Show the graph and ready-stories summary per that file's approval format - DO NOT PROCEED until user confirms
5. **MANDATORY**: Log user's response in audit.md with complete raw input

---

## 🔄 MANDATORY: Jira Sync Rule (applies everywhere a story status changes)

**Rule**: Whenever a story's status is updated in the Story Tracker (`aipdlc-state.md`), check the **Jira** column for that story:

- If **Jira = `—`** (local story): update only the local tracker. No Jira action.
- If **Jira = `PROJ-XXX`** (Jira-linked story): **also transition the Jira issue** via the Atlassian MCP, confirm-first:
  ```
  🔄 Story 1.2 has Jira ID PROJ-102.
  Transition Jira issue to "[target status]"? (yes / skip)
  ```
  On yes: call Atlassian MCP to transition the issue. Verify the transition succeeded. Log in audit.md.
  On skip: update only the local tracker; note the skip in audit.md.

**This rule applies at every point where story status changes**:
- Ready for Development (initial status when the story is created)
- In Development — **EXCEPTION: automatic** (picking a story via `dev-implement` is the claim — update Jira + tracker without asking, verify, announce; stays In Development through code gen, Code Review, Remediate, the PR raise, AND the auto PR review)
- Any other custom status transition

**🔷 Epic Status Sync (Parent Epic follows the stories)**:
- **First story starts** — when the FIRST story moves to `🔵 In Development` via `dev-implement`, ALSO transition the Parent Epic (from `## Jira`) to "In Development" — **automatic** (like the story transition itself), verified, announced, logged in audit.md.
- **All stories done** — when the LAST story reaches `🧪 Ready for Testing` (i.e. ALL story PRs are merged), offer (**confirm-first**) to transition the Parent Epic to "Ready for Testing"; verify and log. If the last story's PR is raised while other PRs are still open, do NOT move the Epic — report the open PRs and keep the stories (and Epic) `🔵 In Development` until every PR merges.
- Skip both silently if `## Jira` records `Parent Epic: none`.

**The same confirm-first, verify rule applies to story↔Parent-Epic links** (created during User Stories Part 3).

**NEVER** silently update only one side. Local tracker and Jira must stay in sync.

---

## Workflow Planning (ALWAYS EXECUTE)

1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/workflow-planning.md`
3. **MANDATORY**: Load content validation rules from `common/content-validation.md`
4. Load all prior context:
   - Reverse engineering artifacts (if brownfield)
   - Intent analysis
   - Requirements (if executed)
   - User stories
5. Execute workflow planning:
   - Determine which phases to execute
   - Determine depth level for each phase
   - Create multi-package change sequence (if brownfield)
   - Generate workflow visualization (VALIDATE Mermaid syntax before writing)
6. **MANDATORY**: Validate all content before file creation per content-validation.md rules
7. **Wait for Explicit Approval**: Present recommendations using language from workflow-planning.md Step 9, emphasizing user control to override recommendations - DO NOT PROCEED until user confirms
8. **MANDATORY**: Log user's response in audit.md with complete raw input

## Application Design (CONDITIONAL)

**Execute IF**:
- New components or services needed
- Component methods and business rules need definition
- Service layer design required
- Component dependencies need clarification

**Skip IF**:
- Changes within existing component boundaries
- No new components or methods
- Pure implementation changes

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `inception/application-design.md`
3. Load reverse engineering artifacts (if brownfield)
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Present detailed completion message (see application-design.md for message format) - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

## Transition to CONSTRUCTION PHASE

After Application Design is approved (or after Workflow Planning approval when
Application Design is skipped), proceed directly to the **CONSTRUCTION PHASE**.
The Construction design stages run **once at system level**, scoped to the
**intake brief** at `aipdlc-docs/inception/requirements/epic-brief.md`
(written from the provided Jira Epic, or from the user's requirements
document / natural-language description). Log the transition in audit.md.

---

# 🟢 CONSTRUCTION PHASE

**Purpose**: Detailed design, NFR implementation, and code generation

**Focus**: Determine HOW to build it

**Stages in CONSTRUCTION PHASE**:
- System-Level DESIGN Stages (single pass, scoped to the intake brief; **no code is generated here**):
  - Functional Design (CONDITIONAL, system-level)
  - NFR Requirements (CONDITIONAL, system-level)
  - NFR Design (CONDITIONAL, system-level)
  - Infrastructure Design (CONDITIONAL, system-level)
- 🛑 **MANDATORY STOP — after Infrastructure Design (or after the design stages are skipped), before Code Generation** — the workflow HALTS and waits for the user. Code Generation does NOT start automatically.
- 🚀 Development Handoff (announce stories are ready; tell the user to use the **`dev-implement`** keyword to pick and build each story)
- Code Generation (per-**story**, via the **`dev-implement`** keyword only) — defined in `workflows/dev-implement.md`; reads the Dependency Graph (from Inception) to show the currently ready stories; begins with **Story Selection** (local Story Tracker or Jira), creates the story branch from the Epic branch (`common/branching-strategy.md`), generates code, then unit tests run to ≥90% coverage; on PR raise it stores the PR URL and keeps the story `🔵 In Development` (a story becomes `🧪 Ready for Testing` only when its PR MERGES); updates the Story Tracker on every status change
- Code Review & Remediate (OPTIONAL — story-wise or all-stories) — defined in `workflows/code-review.md` and `workflows/remediate.md`; invoked standalone by the keywords **`code-review`** and **`remediate`**

**🧪 Build and Test is NOT part of this phase** — not at epic level, not at story level. It is SDET's, run per story via the `/sdet-implement` skill. No stage here runs it.

**Note on the STOP CHECKPOINT**: After Infrastructure Design (or after design stages are skipped), the workflow MUST stop and present the Development Handoff. It MUST NOT proceed into Code Generation on its own — the user explicitly drives code generation with the `dev-implement` keyword.

---

## System-Level DESIGN Stages (Single Pass)

**The following DESIGN stages execute in sequence, ONCE for the whole system, scoped to the intake brief captured at workflow start. Code Generation is NOT part of these stages — it happens later, per-story, via `dev-implement`, after the mandatory STOP CHECKPOINT.**

**Primary inputs for EVERY design stage below** (load before the stage's Step 1):
1. `aipdlc-docs/inception/requirements/epic-brief.md` — the intake brief defines WHAT to build
2. `aipdlc-docs/inception/requirements/requirements.md`
3. `aipdlc-docs/inception/user-stories/stories.md` + the `## Story Tracker` in `aipdlc-state.md`
4. `aipdlc-docs/inception/application-design/` artifacts (if Application Design ran)

### Functional Design (CONDITIONAL, system-level)

**Execute IF**:
- New data models or schemas
- Complex business logic
- Business rules need detailed design

**Skip IF**:
- Simple logic changes
- No new business logic

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/functional-design.md`
3. Execute functional design for the whole system
4. **MANDATORY**: Present standardized 2-option completion message as defined in functional-design.md - DO NOT use emergent 3-option behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### NFR Requirements (CONDITIONAL, system-level)

**Execute IF**:
- Performance requirements exist
- Security considerations needed
- Scalability concerns present
- Tech stack selection required

**Skip IF**:
- No NFR requirements
- Tech stack already determined

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/nfr-requirements.md`
3. Execute NFR assessment for the whole system
4. **MANDATORY**: Present standardized 2-option completion message as defined in nfr-requirements.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### NFR Design (CONDITIONAL, system-level)

**Execute IF**:
- NFR Requirements was executed
- NFR patterns need to be incorporated

**Skip IF**:
- No NFR requirements
- NFR Requirements was skipped

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/nfr-design.md`
3. Execute NFR design for the whole system
4. **MANDATORY**: Present standardized 2-option completion message as defined in nfr-design.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

### Infrastructure Design (CONDITIONAL, system-level)

**Execute IF**:
- Infrastructure services need mapping
- Deployment architecture required
- Cloud resources need specification

**Skip IF**:
- No infrastructure changes
- Infrastructure already defined

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from `construction/infrastructure-design.md`
3. Execute infrastructure design for the whole system
4. **MANDATORY**: Present standardized 2-option completion message as defined in infrastructure-design.md - DO NOT use emergent behavior
5. **Wait for Explicit Approval**: User must choose between "Request Changes" or "Continue to Next Stage" - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

> **End of the System-Level DESIGN stages.** Once the design stages have completed (or been skipped), DO NOT generate code. Proceed to the mandatory STOP CHECKPOINT below.

---

## 🛑 MANDATORY STOP — After Infrastructure Design, Before Code Generation

**This is a hard halt.** After the design stages complete (Infrastructure Design is done or skipped), the workflow MUST stop and wait for the user. **Code Generation MUST NOT start automatically.** Present the Development Handoff below, then block until the user invokes `dev-implement`.

1. **MANDATORY**: Log reaching the stop CHECKPOINT in audit.md.
2. Mark in `aipdlc-state.md`: `Design complete — awaiting dev-implement`.
3. **Commit + push the design artifacts on the Epic branch (automatic — this is what unblocks SDET)**: stage everything produced by the design stages (`aipdlc-docs/construction/design/**`, the updated `aipdlc-state.md`, `audit.md`), commit on the Epic branch with an `AI-PDLC-Version: [N]` trailer, and push to origin so the branch on the remote carries the acceptance criteria + requirements + design artifacts that `/sdet-implement` reads. Announce the commit hash and the pushed branch; log both in audit.md. If the push fails, say so explicitly and tell the user to push manually — **SDET cannot start until this branch is on origin**.
4. Present the **Development Handoff** message (below).
5. **HALT.** Do not proceed to Code Generation or any later stage until the user types `dev-implement` (to build a story)

## 🚀 Development Handoff — Use `dev-implement` to Build Each Story

**Present this AFTER the system-level design stages are complete (or skipped) and at the STOP CHECKPOINT above, BEFORE any Code Generation. This is the moment the workflow hands off to development.**

```markdown
# ✅ Design Done — Ready to Build

📚 **[N] user stories created** during Inception.
[IF stories were pushed to Jira:]
🔗 **On Jira project [PROJECT_KEY]** — stories [PROJ-101 … PROJ-1NN][, all linked to Parent Epic [EPIC-KEY] — include this clause ONLY if `## Jira` records an Epic (not `none`)].
[IF stories were NOT pushed to Jira:]
📍 Tracked locally only (not pushed to Jira).

🌊 Dependency Graph: [M] stories are ready to start now (no unfinished prerequisites).
🧩 Design stages: [list which ran vs were skipped].
🌿 Epic branch: `[epic-branch]` — design artifacts **committed and pushed** ([commit hash]).

> **🚀 <u>**DEV — use the keyword `dev-implement`**</u>**
> 1️⃣  Stay on / switch to the epic branch `[epic-branch]` and pull the latest.
> 2️⃣  Type **`dev-implement`** and pick a story (by Story ID / number, or Jira key).
>     Run it **once per story** — it cuts `story/N.M-…` from the epic branch.

> **🧪 <u>**SDET — use the skill `/sdet-implement`**</u>** (in parallel, starting now)
> SDET does **not** wait for development — no dev code, branch, PR or merge is needed.
> 1️⃣  `git fetch origin && git checkout [epic-branch] && git pull --ff-only`
> 2️⃣  Type **`/sdet-implement <story-ID or Jira key>`** — once per story.
>     It cuts `sdet/<JIRA-ID>-<title>` from this branch, writes the MANUAL test steps to
>     `aipdlc-docs/tests/<JIRA-ID>-<title>/` from the story's acceptance criteria, and raises
>     its own PR back into `[epic-branch]`.

🔴 Type `dev-implement` / `/sdet-implement` EXACTLY as shown — do not describe what you want in your
   own words. Any other phrasing is not a framework trigger and the workflow will not advance.
```

- **[N]** = total stories. Show the Jira line only if stories were pushed (Jira column populated); Epic key from `## Jira`. Otherwise show the local-only line.
- Substitute `[epic-branch]` and the commit hash with real values from `## Branching` / the Step 3 commit — never ship a placeholder.
- Log this handoff in audit.md.

---

## Code Generation (Only execute when the user types `dev-implement`, per-story)

**On invocation of the `dev-implement` keyword, read `workflows/dev-implement.md` and follow it exactly.**

---

## Code Review & Remediate

**Status**: OPTIONAL. It can be invoked standalone at any time for **a specific story** or for **all stories together**.

**On invocation, read the matching workflow file and follow it exactly:**
- **`code-review`** → read `workflows/code-review.md` 
- **`remediate`** → read `workflows/remediate.md` 

**Suggestion after a story's PR is raised** (present, do NOT auto-run):
```markdown
> **🚀 OPTIONAL NEXT STEPS**
>
> 1️⃣  **code-review** — review a story's code, or all stories together (REVIEWER, read-only report) — 
> 2️⃣  **remediate** — fix issues from a review report, story-wise or all-stories (DEV) — 

```

**Execution**:
1. **MANDATORY**: Log any user input during these stages in audit.md
2. Load `workflows/code-review.md` and/or `workflows/remediate.md` only when the user invokes them (each is self-contained — no separate detail file to load)
3. **NEVER** auto-run these; they are user-initiated
4. **MANDATORY**: Log user responses and any Jira updates in audit.md with complete raw input

---

# 🎫 TICKET WORKFLOW (keyword: `ticket-implement <JIRA-ID>` — Bug OR Enhancement)

**On `ticket-implement <JIRA-ID>`** (an existing Jira ticket): read `workflows/ticket-implement.md` and follow it exactly.

---

## Key Principles

- **Adaptive Execution**: Only execute stages that add value
- **Transparent Planning**: Always show execution plan before starting
- **User Control**: User can request stage inclusion/exclusion
- **Progress Tracking**: Update aipdlc-state.md with executed and skipped stages
- **Complete Audit Trail**: Log ALL user inputs and AI responses in audit.md with timestamps — COMPLETE RAW INPUT, never summarized/paraphrased, every interaction (not just approvals)
- **Quality Focus**: Complex changes get full treatment, simple changes stay efficient
- **Content Validation**: Always validate content before file creation per content-validation.md rules
- **NO EMERGENT BEHAVIOR**: Construction phases MUST use standardized 2-option completion messages as defined in their respective rule files. DO NOT create 3-option menus or other emergent navigation patterns.

## MANDATORY: Plan-Level Checkbox Enforcement

### MANDATORY RULES FOR PLAN EXECUTION
1. **NEVER complete any work without updating plan checkboxes**
2. **IMMEDIATELY after completing ANY step described in a plan file, mark that step [x]**
3. **This must happen in the SAME interaction where the work is completed**
4. **NO EXCEPTIONS**: Every plan step completion MUST be tracked with checkbox updates

### Two-Level Checkbox Tracking System
- **Plan-Level**: Track detailed execution progress within each stage
- **Stage-Level**: Track overall workflow progress in aipdlc-state.md
- **Update immediately**: All progress updates in SAME interaction where work is completed

## Prompts Logging Requirements
- **MANDATORY**: Log EVERY user input (prompts, questions, responses) with timestamp in audit.md
- **MANDATORY**: Capture user's COMPLETE RAW INPUT exactly as provided (never summarize)
- **MANDATORY**: Log every approval prompt with timestamp before asking the user
- **MANDATORY**: Record every user response with timestamp after receiving it
- **MANDATORY**: Stamp every entry with the current operator's email (`**User Email**:`) — read LIVE from the session context, never confirmed with the user, NEVER a name (email only), and recorded ONLY in audit.md (never in aipdlc-state.md). At every approval flow ("Wait for Explicit Approval" gates, Jira transition confirmations, PR confirmations, etc.), this field records WHO approved. This applies to EVERY audit entry in EVERY workflow, stage, and skill — including those with their own local audit templates (dev-implement, bug flows, skills): local templates add fields, they never remove `**User Email**:`
- **CRITICAL**: ALWAYS append/Edit audit.md — NEVER use tools or commands that overwrite its entire contents (this causes duplication)
- Use ISO 8601 format for timestamps (YYYY-MM-DDTHH:MM:SSZ)
- Include stage context for each entry
- **Ordering**: ALWAYS append new entries to the **END** of the file in strict chronological order (oldest → newest). NEVER prepend or reorder existing entries.
- **File creation**: If `audit.md` does not exist, create it with an `# Audit Log` header before writing the first entry.

### Audit Log Format:
```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO timestamp]
**User Email**: [current session email — read live from the session context; email ONLY, never a name; on approval-flow entries this identifies the approver]
**User Input**: "[Complete raw user input - never summarized]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

### Correct Tool Usage for audit.md

✅ Read audit.md, then append/Edit the new entry.
❌ Never rewrite the whole file with read contents plus additions (duplication).

## Directory Structure

```text
<WORKSPACE-ROOT>/                   # ⚠️ APPLICATION CODE HERE
├── [project-specific structure]    # Varies by project (see code-generation.md)
│
├── aipdlc-docs/                     # 📄 DOCUMENTATION ONLY
│   ├── inception/                  # 🔵 INCEPTION PHASE
│   │   ├── plans/
│   │   ├── reverse-engineering/    # Brownfield only
│   │   ├── requirements/
│   │   ├── user-stories/           # stories.md, personas.md
│   │   ├── application-design/     # incl. code organization strategy
│   │   └── dependency-graph.yml    # requires/enables for every story
│   ├── construction/               # 🟢 CONSTRUCTION PHASE
│   │   ├── plans/
│   │   ├── design/                 # System-level design (single pass)
│   │   │   ├── functional-design/
│   │   │   ├── nfr-requirements/
│   │   │   ├── nfr-design/
│   │   │   └── infrastructure-design/
│   │   ├── code/                   # Markdown summaries 
│   │   ├── reviews/                # Code review reports (story-[N.M]-code-review-v[X].md, all-stories-code-review-v[X].md)
│   ├── tests/                      # 🧪 SDET — Build and Test, ONE folder per story
│   │   └── <JIRA-ID>-<jira-title>/ # manual test steps
│   ├── operations/                 # 🟡 OPERATIONS PHASE
│   ├── aipdlc-state.md             
│   └── audit.md
```

**CRITICAL RULE**:
- Application code: Workspace root (NEVER in aipdlc-docs/)
- Documentation: aipdlc-docs/ only
- Project structure: See code-generation.md for patterns by project type