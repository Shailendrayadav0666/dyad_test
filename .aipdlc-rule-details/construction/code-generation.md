# Code Generation - Detailed Steps

## Overview
Code Generation is **per-story** and is triggered ONLY by the **`dev-implement`** keyword (orchestrated by `workflows/dev-implement.md`). It runs after the system-level design stages and the 🛑 STOP CHECKPOINT. It has two parts, preceded by Story Selection:
- **Step 0 - Story Selection (MANDATORY)**: identify WHICH story to implement (local Story Tracker or Jira), run the Doability Gate, move it from `🟢 Ready for Development` to `🔵 In Development`
- **Part 1 - Planning**: Create detailed code generation plan — implementation steps per layer, ending with the mandatory **Unit Test & Coverage (≥90%)** step
- **Part 2 - Generation**: Execute approved plan to generate code and artifacts, then generate + RUN unit tests until coverage is ≥90% (Step 11a — same run), then run the FULL repo regression suite and diff it against the pre-change baseline (Step 11b — same run)

**Extensions**: test-mandating extensions (e.g., Property-Based Testing) apply — their required tests are included in the Unit Test & Coverage step per the extension's scope.

**Note**: For brownfield projects, "generate" means modify existing files when appropriate, not create duplicates.

**Audit entries**: EVERY audit.md entry written during this stage (plan approval prompts/responses, per-step generation logs, coverage evidence, completion) MUST include the `**JIRA TICKET**:` field — the story's Jira key as a clickable link, or the local Story ID when `Jira = —` — AND the `**Epic Link**:` field — the full Parent Epic URL as a clickable link, read from `## Jira` in `aipdlc-docs/aipdlc-state.md`, or `none` when no Epic is recorded. See the Audit Entry Format in `workflows/dev-implement.md`.

**Note on design context**: The system-level design artifacts (functional/NFR/infrastructure under `aipdlc-docs/construction/design/`) apply to every story. Code for each story is written into the application structure documented in Application Design (or, if Application Design was skipped, per the structure patterns in Critical Rules below).

## Prerequisites
- System-level design stages complete (functional/NFR/infrastructure as applicable)
- Dependency Graph exists (`aipdlc-docs/inception/dependency-graph.yml`) and the `## Story Tracker` exists in `aipdlc-state.md`
- The story selected via `dev-implement` has passed the Doability Gate (all `requires` are `🧪 Ready for Testing`)
- The story branch is active, cut from the epic branch AFTER the dependency-merge check passed (`common/branching-strategy.md` Section 3). If any prerequisite story's branch is NOT yet merged into the epic branch, code generation MUST NOT start — the workflow has already warned and stopped (Case B): the user must merge the prerequisite's PR into the epic branch first and re-run `dev-implement`

---

# PART 1: PLANNING

## Step 0: Story Selection (MANDATORY)
- [ ] Load and execute all steps from `construction/story-selection.md` — it asks which story, runs the Doability Gate, and moves the story from `🟢 Ready for Development` to `🔵 In Development` automatically (Jira + tracker updated without asking, transition verified). Do NOT restate that logic here.
- [ ] Carry the resolved story (ID, title, acceptance criteria, Jira key/link) into the planning steps below.

## Step 1: Analyze Story & Design Context
- [ ] Read the selected story and its acceptance criteria from `aipdlc-docs/inception/user-stories/stories.md`
- [ ] **Read `aipdlc-docs/inception/requirements/requirements.md` and resolve the story's `Covers` REQ-IDs** — the requirement text itself (not just the story's AC restatement) is MANDATORY planning input; an AC set that understates its requirement never caps the plan (`common/requirements-traceability.md` Rule 5)
- [ ] **Fallback coverage verification**: if `aipdlc-state.md` carries NO `Requirements coverage verified post-design` record, run `common/requirements-traceability.md` Rule 4 now (silent, blocking) before planning proceeds — the thread must never reach code generation unverified
- [ ] Read the system-level design artifacts (functional-design, nfr-design, infrastructure-design under `aipdlc-docs/construction/design/`)
- [ ] Identify the story's dependencies and interfaces (from the Dependency Graph `requires`/`enables`)
- [ ] Validate the story is ready for code generation (Doability Gate passed in Step 0)

### Step 1.5: 📐 RE-CONSULT the Design References (MANDATORY — automatic, ask the user nothing)

**Load `common/design-reference-grounding.md`** and read `## Design References` in `aipdlc-docs/aipdlc-state.md`.

**This step adds NO question, NO gate, and NO checkpoint to code generation.** It runs silently as part of analysing story context. The only existing gate in this phase remains GATE 2 (plan approval) exactly as it was — this step neither extends it nor adds a second one.

- [ ] **FIRST, read the `### Reconciliations` table** in `## Design References` (rule **DR-8**). Every point listed there is a **settled decision taken deliberately against the reference** by an earlier design stage — an excluded capability, a narrowed scope, a locally-scoped stylesheet, an NFR or accessibility constraint. **Those points are closed: follow the framework artifact, NOT the raw reference, and do not re-report them as contradictions.** The design docs the framework generated are the reconciled source of truth wherever they have actually considered a point.
- [ ] **Re-open** every reference whose `Governs` covers a component THIS story builds or modifies, and ground **only the points the reconciliations table does NOT settle**. A fresh read for THIS story's scope is required — *"it was read at Requirements Analysis / Application Design"* does not count, because those stages read only what was in their own scope.
- [ ] For a UI prototype, open the real `*.component.html` / `*.ts` / `*.css` (or equivalent) for this story's components and extract: actual control types (plain `<select>` vs searchable grouped combobox; single- vs multi-select), grouping/ordering, labels and icons, interaction behaviour (search/filter, click-outside-to-close, keyboard, empty states), and custom CSS classes — checking whether those classes exist in the live app's global styles.
- [ ] **On any remaining difference, apply DR-8 precedence — do NOT blanket-prefer the reference:**
   - **Reconciled** (the artifact recorded a decision on this point) → **follow the artifact**; note in one line that the reference differs here by prior decision. **Never reintroduce something a design stage deliberately excluded.**
   - **Unreconciled** (no artifact ever addressed this point — the AC is simply generic or silent) → **follow the reference**, state plainly in the plan what the AC said versus what the design shows, amend the AC / `requirements.md` / Jira per `common/requirements-traceability.md`, and record the reconciliation.
   - Either way: **do NOT stop, do NOT ask an A/B question** — the user reviews it at the existing GATE 2 like everything else in the plan.
- [ ] A capability the prototype shows that is **outside** this story's ACs → check the reconciliations table first: if it is already recorded as excluded, honour that silently. If it is new, note in the plan that you saw it and excluded it as out of scope, and record the reconciliation so no later story re-adds it. Never silently build it, never silently drop it, never ask about it.
- [ ] Any reference still `Read? ⏳` — read it now (DR-2/DR-3/DR-4) and carry on.
- [ ] Log in `audit.md` which references were re-opened, for which components, what was extracted, and any deviation reported.

**The plan (Step 2) states, for EVERY component it creates or changes, exactly one of:**

```
Design reference: <path>/<file> — grounded (<what the reference actually specifies>)
Design reference: none covers this component — built from ACs only
```

This is your own self-check while writing the plan — satisfy it yourself before presenting the plan at the existing GATE 2.

## Step 2: Create Detailed Story Code Generation Plan
- [ ] Read workspace root and project type from `aipdlc-docs/aipdlc-state.md`
- [ ] Determine code location (see Critical Rules for structure patterns)
- [ ] **Brownfield only**: Review reverse engineering code-structure.md for existing files to modify
- [ ] Document exact paths (never aipdlc-docs/)
- [ ] Create explicit steps for implementing this story:
  - Project Structure Setup (greenfield only)
  - Business Logic Generation
  - Business Logic Summary
  - API Layer Generation
  - API Layer Summary
  - Repository Layer Generation
  - Repository Layer Summary
  - Frontend Components Generation (if applicable)
  - Frontend Components Summary (if applicable)
  - Database Migration Scripts (if data models exist)
  - **Unit Test & Coverage (≥90%)** — generate unit tests for ALL new/changed code, run them, measure coverage, and iterate until ≥90% (Step 11a — MANDATORY, always the step after implementation)
  - **Full Regression vs Baseline** — re-run the ENTIRE repo suite and diff against the baseline captured at the Story Branch checkpoint; any NEW failure is fixed in the same run (Step 11b — MANDATORY, always the step after Step 11a)
  - Documentation Generation (API docs, README updates)
  - Deployment Artifacts Generation
- [ ] Number each step sequentially
- [ ] Include story mapping references
- [ ] **Tag EVERY implementation step with the REQ-ID(s) and acceptance criteria it implements** — e.g., `Step 3: Order validation service (REQ-F-03, AC-1, AC-2)` (`common/requirements-traceability.md` Rule 5)
- [ ] Add checkboxes [ ] for each step

## Step 3: Include Story Implementation Context
- [ ] For this story, include:
  - The story's acceptance criteria and the intake brief context (`epic-brief.md`, if present)
  - Dependencies on other stories (`requires`/`enables` from the Dependency Graph)
  - Expected interfaces and contracts (from Application Design, if it ran)
  - Database entities this story owns or touches
  - Service/component boundaries and responsibilities (from Application Design)

## Step 4: Create Story Plan Document
- [ ] Save complete plan as `aipdlc-docs/construction/plans/story-{N.M}-code-generation-plan.md`
- [ ] Include step numbering (Step 1, Step 2, etc.)
- [ ] Include story context and dependencies
- [ ] Include story traceability
- [ ] **Trace completeness self-check (MANDATORY — automatic, blocking, BEFORE presenting the plan at GATE 2)**: verify every REQ-ID in the story's `Covers` AND every acceptance criterion appears in ≥1 tagged plan step. A REQ/AC with no plan step is a blocking gap — extend the plan and re-check (no user prompt). Include the trace summary (REQ/AC → plan steps) in the plan document (`common/requirements-traceability.md` Rule 5)
- [ ] Ensure plan is executable step-by-step
- [ ] Emphasize that this plan is the single source of truth for Code Generation

## Step 5: Summarize Story Plan
- [ ] Provide summary of the story code generation plan to the user
- [ ] Highlight the implementation approach
- [ ] Explain step sequence and story coverage
- [ ] Note total number of steps and estimated scope

## Step 6: Log Approval Prompt
- [ ] **🚧 This is GATE 2** — user approval of the story's code-generation plan (Code Gen Part 1, via `dev-implement`)
- [ ] Before asking for approval, log the prompt with timestamp in `aipdlc-docs/audit.md`
- [ ] **No gate marker on this prompt entry — the word "GATE" must NOT appear anywhere in this entry's `##` heading.** Use a plain heading like `## Code Generation Part 1 — Plan Approval Prompt (Story N.M)` (NEVER `## ... GATE 2 Approval Prompt`). "GATE 2" appears ONLY in the heading of the response entry (Step 8), where the user's approve/reject decision is recorded
- [ ] Include reference to the complete story code generation plan
- [ ] Include the `**JIRA TICKET**:` field (story's Jira link, or local Story ID) and the `**Epic Link**:` field (full Parent Epic URL from `## Jira` in aipdlc-state.md, or `none`)
- [ ] Use ISO 8601 timestamp format

## Step 7: Wait for Explicit Approval
- [ ] Do not proceed until the user explicitly approves the story code generation plan
- [ ] Approval must cover the entire plan and generation sequence
- [ ] If user requests changes, update the plan and repeat approval process

## Step 8: Record Approval Response
- [ ] Log the user's response with timestamp in `aipdlc-docs/audit.md` — **whether it is an approval OR a rejection/change request**
- [ ] **The gate is marked in the entry's `##` HEADING — there is NO separate `**GATE Number**:` field.** Use:
  - Approved: `## Code Generation Part 1 — GATE 2 Plan Approved (Story N.M)`
  - Rejected: `## Code Generation Part 1 — GATE 2 Plan Rejected — Changes Requested (Story N.M)`
- [ ] The GATE 2 heading applies to EVERY response at this gate — approved AND rejected outcomes alike (each re-ask after plan changes uses a GATE 2 heading on its RESPONSE entry only — prompt entries never carry the gate marker)
- [ ] Include the exact user response text
- [ ] Mark the outcome clearly (✅ approved / ❌ rejected — changes requested)

## Step 9: Update Progress
- [ ] Mark Code Generation Part 1 (Planning) complete in `aipdlc-state.md`

---

# PART 2: GENERATION

## Step 10: Load Story Code Generation Plan
- [ ] Read the complete plan from `aipdlc-docs/construction/plans/story-{N.M}-code-generation-plan.md`
- [ ] Identify the next uncompleted step (first [ ] checkbox)
- [ ] Load the context for that step (story, dependencies, design artifacts)

## Step 11: Execute Current Step
- [ ] Verify target directory from plan (never aipdlc-docs/)
- [ ] **Brownfield only**: Check if target file exists
- [ ] If this step is the **Unit Test & Coverage (≥90%)** step, execute Step 11a in full (mandatory — tests are generated, RUN, and iterated to ≥90% coverage in this same run, never deferred to SDET or a later session).
- [ ] Generate exactly what the current step describes:
  - **If file exists**: Modify it in-place (never create `ClassName_modified.java`, `ClassName_new.java`, etc.)
  - **If file doesn't exist**: Create new file
- [ ] Write to correct locations:
  - **Application Code**: Workspace root per project structure
  - **Documentation**: `aipdlc-docs/construction/code/` (markdown only)
  - **Build/Config Files**: Workspace root
- [ ] Follow the story's acceptance criteria
- [ ] Respect dependencies and interfaces

## Step 11a: Unit Test & Coverage Step (MANDATORY — after implementation, ≥90% coverage, same run)
Runs ONCE per story, immediately after all implementation steps are complete (business logic, API, repository, frontend):
- [ ] **Generate unit tests** covering ALL of the story's new/changed code — happy paths, edge cases, error scenarios, per acceptance criterion
- [ ] **RUN the tests** with the project's test runner; fix any failures (whether in the tests or defects they expose in the implementation) until 100% of tests pass
- [ ] **Measure coverage** on the story's new/changed code using the stack's standard coverage tool (e.g., jest `--coverage`, pytest-cov, JaCoCo)
- [ ] **Iterate until ≥90%**: if coverage is below **90%**, identify the uncovered lines/branches, add or adjust tests, and re-run — repeat WITHIN THIS SAME RUN until coverage is ≥90%. Do not defer the gap to SDET or a later session
- [ ] If ≥90% is genuinely unreachable (e.g., untestable generated boilerplate), surface the gap to the user with the measured %, the uncovered code, and the reason — never silently accept below-target coverage
- [ ] **Capture PROOF artifacts (MANDATORY — durable, verifiable evidence, not just a text claim)**: from the FINAL passing test run, save the actual tool output to `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/`:
  - [ ] **`unit-test-run.log`** — the raw, unedited stdout/stderr of the final test-runner invocation (the run that shows X/X passing). Do NOT hand-transcribe or summarize it — capture the real output (e.g., `npm test -- --coverage > unit-test-run.log 2>&1`, `pytest --cov ... | tee unit-test-run.log`)
  - [ ] **`coverage-report.*`** — the coverage tool's own machine-readable report from the same run. **This file is MANDATORY, not best-effort.** You MUST invoke the runner with the flags that emit a real report file — do NOT rely on the terminal summary alone:
    - **Node/JS (jest, nyc, vitest)**: enable coverage reporters so `coverage/lcov.info` (and/or `coverage-final.json`, HTML) is produced — e.g., `jest --coverage --coverageReporters=lcov --coverageReporters=json-summary`
    - **Python (pytest-cov)**: `pytest --cov=<pkg> --cov-report=xml --cov-report=html` → `coverage.xml` (+ `htmlcov/`)
    - **Java (JaCoCo)**: the `jacoco.xml`/HTML report from the build
    - **Any other stack**: use that stack's standard coverage-report flag to emit a machine-readable file (lcov / xml / json / HTML)
    Copy the emitted report into the evidence folder so it survives independent of the build workspace. **🔴 GATE FAILURE — if the stack HAS coverage-report tooling but no report file is produced and stored, the Unit Test & Coverage gate is NOT satisfied: STOP and surface it to the user (the terminal summary in `unit-test-run.log` alone is NOT sufficient proof).**
    - **⚠️ Narrow exception — only when the stack has NO coverage-report tooling at all**: if the language/test stack genuinely provides no way to emit a machine-readable coverage report (after actually checking for the standard tool), this is a **documented, surfaced exception — NOT a silent skip**. Record in `evidence-manifest.md` which coverage tool(s) were checked and why none is available, keep the mandatory `unit-test-run.log`, and explicitly surface the exception to the user for acknowledgment. This exception NEVER applies when a coverage tool exists for the stack (Python/pytest-cov, JS/jest·nyc·vitest, Java/JaCoCo, Go `-coverprofile`, .NET coverlet, etc.) — there the report file remains strictly mandatory.
  - [ ] **`evidence-manifest.md`** — a short manifest recording: the exact command(s) run, the test runner + coverage tool used, tests passing (X/X), the measured coverage % on the story's new/changed code, and a relative-path link to each artifact above
- [ ] **Cite the proof, not just the numbers**: in the story summary and audit.md, record tests passing (X/X) and the measured coverage %, AND link the evidence folder path `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/`. The numbers reported downstream (completion message, Code Review, PR/Jira comment) MUST match these saved artifacts

## Step 11b: Full Regression checkpoint (MANDATORY — after Step 11a, same run)
The ≥90% gate in Step 11a is scoped to the story's NEW/changed code. It cannot detect assertions this story invalidated in **pre-existing shared test files** — that is what this step is for.
- [ ] **Re-run the ENTIRE repo test suite** (all pre-existing tests + this story's new tests) and save the raw output to `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/full-regression.log`
- [ ] **Diff against `baseline-regression.log`** captured on the story branch before any code was generated (`workflows/dev-implement.md` Step 1.5 Item 4.5)
- [ ] **NEW failures (green at baseline, red now)** — **this story broke them, so this story fixes them.** Fix them within THIS SAME run (no user prompt), then re-run and re-diff, iterating until the diff is clean. Fix each according to what actually broke:
  - **Obsolete expectation** — behaviour legitimately changed, the assertion encodes the old contract → **update the assertion** (keep the test; it still guards real behaviour)
  - **Genuinely dead** — exercises a code path this story removed → **delete it** after confirming the new tests cover the replacement path
  - **Real regression** — the test is correct and the implementation broke it → **fix the implementation, never the test**
- [ ] 🔴 **NEVER delete, skip, or weaken a failing test merely to turn the suite green** — that discards the guard and hides real regressions while the coverage gate still reports ≥90% on new code
- [ ] **Failures already red at baseline** → not this story's doing. They are already logged in `baseline-regression.log`; ignore them and do not block/fix on them.
- [ ] **Record in `evidence-manifest.md`**: baseline vs post-change pass/fail counts, and each NEW failure with what broke and how it was fixed
- [ ] Proceed to Code Review only once the diff is clean (zero NEW failures, ignore the old failures from baseline run)

## Step 12: Update Progress
- [ ] Mark the completed step as [x] in the code generation plan
- [ ] **Story Tracker**: ensure the story being implemented is `🔵 In Development` with a `Start` date; update `Recorded` to the current timestamp in `aipdlc-docs/aipdlc-state.md`
- [ ] Update `aipdlc-docs/aipdlc-state.md` current status
- [ ] **Brownfield only**: Verify no duplicate files created (e.g., no `ClassName_modified.java` alongside `ClassName.java`)
- [ ] Save all generated artifacts

## Step 13: Continue or Complete Generation
- [ ] If more steps remain, return to Step 10
- [ ] If all steps complete, proceed to present completion message

## Step 14: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 💻 Code Generation Complete - Story [N.M]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary
        - **Brownfield**: Distinguish modified vs created files (e.g., "• Modified: `src/services/user-service.ts`", "• Created: `src/services/auth-service.ts`")
        - **Greenfield**: List created files with paths (e.g., "• Created: `src/services/user-service.ts`")
        - List tests, documentation, deployment artifacts with paths
        - Keep factual, no workflow instructions
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the generated code at:
> - **Application Code**: `[actual-workspace-path]`
> - **Documentation**: `aipdlc-docs/construction/code/`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> ✅ Code generation is complete. An **automated Code Review will now run for this story** —
> you do not need to request it. When it finishes you'll choose **Approve & continue** (commit,
> push & raise the PR) or **Remediate** (fix the findings first).

---
```

## Step 15: Hand Off to Automated Code Review (no user gate here)

🔴 **GUARDRAIL — "Code Review" and "Remediate" here are WORKFLOW RULE FILES, NOT Claude skills.** They are executed by `Read`ing and following `workflows/code-review.md` / `workflows/remediate.md` (which pull detailed steps from `construction/code-review.md` / `construction/remediate.md`). There is **NO** Claude skill named `code-review` or `remediate` — **NEVER** invoke one via the Skill tool. The only review that IS a skill is **`pr-review`** (post-PR, AUTO MODE, as-is).

- **When invoked via `dev-implement`** (the normal path): do NOT stop for a "Request Changes / Continue" choice. Immediately hand control back to `workflows/dev-implement.md` **Post-Code-Generation Automation**, which auto-runs Code Review, audits the full log, and then presents the Approve & continue / Remediate decision. The user's opportunity to request changes is handled through the Remediate path after review.
- **When invoked standalone** (code generation only, not under `dev-implement`): present the completion announcement and wait for the user to either request changes or confirm; do not auto-run downstream workflows.

## Step 16: Record Approval & Story Status (Confirm-First)
> **When invoked via `dev-implement`** (the normal path): do NOT change the status here. The story stays `🔵 In Development` through code generation, the automated Code Review, any Remediate loop, the PR raise (Section D — which only STORES the PR URL and sets `Merged=no`), and the auto PR review
- Log approval in audit.md with timestamp
- Record the user's approval response with timestamp
- **Post-implementation status — standalone code-generation only** (NOT under `dev-implement`): the story remains `🔵 In Development`.
  ```
  ✅ Story [N.M] implemented (tests [X/X] passing, coverage [Z]%).
  ❓ Mark story 🧪 Ready for Testing now? (yes — set Ready for Testing + End date / no — keep In Development)
  ```
  - On yes: update the `## Story Tracker` — **Status** → `🧪 Ready for Testing`, **End** timestamp, **Recorded** timestamp.
  - If the story has a Jira key, apply the **Jira Sync Rule** (confirm-first): transition the Jira issue to the board state that mirrors Ready for Testing via the Atlassian MCP, verify it landed, add a comment with evidence (tests X/X passing, coverage %).
  - If the story is local-only (`Jira = —`), update only the tracker.
- **NEVER update Jira without explicit user confirmation in this turn.**
- **The ONLY valid Story Tracker statuses are `🟢 Ready for Development`, `🔵 In Development`, and `🧪 Ready for Testing`.**

---

## Critical Rules

### Code Location Rules
- **Application code**: Workspace root only (NEVER aipdlc-docs/)
- **Documentation**: aipdlc-docs/ only (markdown summaries)
- **Read workspace root** from aipdlc-state.md before generating code

**Structure patterns by project type**:
- **Brownfield**: Use existing structure (e.g., `src/main/java/`, `lib/`, `pkg/`)
- **Greenfield (default)**: `src/`, `tests/`, `config/` in workspace root
- **Greenfield, multiple services (per Application Design)**: `{service-name}/src/`, `{service-name}/tests/`
- **Greenfield, modular monolith (per Application Design)**: `src/{module-name}/`, `tests/{module-name}/`

### Brownfield File Modification Rules
- Check if file exists before generating
- If exists: Modify in-place (never create copies like `ClassName_modified.java`)
- If doesn't exist: Create new file
- Verify no duplicate files after generation (Step 12)

### Planning Phase Rules
- Create explicit, numbered steps for all generation activities
- Include story traceability in the plan
- **REQ-ID THREAD**: load requirements.md + the story's `Covers` REQ-IDs as planning input, tag every step with the REQ/AC it implements, and pass the trace completeness self-check (every covered REQ-ID and every AC in ≥1 step) before GATE 2 — per `common/requirements-traceability.md` Rule 5
- Document story context and dependencies
- Get explicit user approval before generation

### Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the story plan
- **FOLLOW PLAN EXACTLY**: Do not deviate from the step sequence
- **UPDATE CHECKBOXES**: Mark [x] immediately after completing each step
- **STORY TRACEABILITY**: Mark the story's plan steps [x] when functionality is implemented
- **RESPECT DEPENDENCIES**: Only implement when the story's `requires` dependencies are `🧪 Ready for Testing` (Doability Gate)
- 🔴 **SQL RESERVED-WORD GUARDRAIL**: when generating any SQL (queries, migrations, stored procedures), never use a target-dialect reserved keyword (e.g., in T-SQL: `key`, `order`, `date`, `user`, `identity`, `year`, `percent`, `session`, `open`, `close`) as an unquoted column/table alias or identifier. Always bracket/quote any alias that could collide (`AS [Order]` in T-SQL, backticks in MySQL, double quotes in Postgres), or simply pick a non-colliding alias name.
- 🔴 **ANGULAR/JS ASYNC SCOPE GUARDRAIL**: when generating Angular (or any JS/TS) code with async callbacks, always use arrow functions for `.subscribe()`, `.then()`, `.pipe()` operator, and other async callbacks inside a class, so `this` correctly resolves to the enclosing component/service/directive instance — never a plain `function() {...}` callback in that position. Always unsubscribe from long-lived Observables in `ngOnDestroy` (`Subscription.unsubscribe()`, `takeUntil(this.destroy$)`, or the `async` pipe) so a callback never fires against a destroyed component instance. Never shadow an outer-scope variable name inside a nested/chained API-call callback — give inner-scope variables from chained calls distinct names.

### Unit Test & Coverage Rules (MANDATORY — every story)
- 🔴 **TESTS AFTER IMPLEMENTATION, SAME RUN**: Once the story's implementation is complete, ALWAYS execute Step 11a — generate unit tests, RUN them, and iterate to the coverage target before the story is announced complete
- 🔴 **COVERAGE GATE (≥90%)**: measure coverage on the story's new/changed code; below target → add/adjust tests and re-run within the same run until met (or surface the gap to the user with the measured % and a reason).
- 🔴 **PROOF ARTIFACTS (MANDATORY)**: from the FINAL passing run, save the raw runner output (`unit-test-run.log`), the coverage tool's **machine-readable report file** (`coverage-report.*` — lcov/xml/json/HTML), and an `evidence-manifest.md` to `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/`. Evidence is the actual tool output, NOT a hand-written claim. **The coverage-report file is MANDATORY whenever the stack has coverage tooling** — run the tool with the flags that emit it (`--cov-report=xml`, `--coverageReporters=lcov`, JaCoCo report, etc.); a terminal summary alone does NOT satisfy the gate. Only when the stack genuinely has NO coverage-report tooling is the file waived — a documented, user-surfaced exception recorded in `evidence-manifest.md`, never a silent skip. Every X/X-passing and coverage-% figure reported downstream (completion message, Code Review, PR/Jira comment) MUST match these saved artifacts.

  | Metric | Target | Scope |
  |--------|--------|-------|
  | Unit Test Coverage | ≥90% | All new/changed code for the story |

### Automation Friendly Code Rules
When generating UI code (web, mobile, desktop), ensure elements are automation-friendly:
- Add `data-testid` attributes to interactive elements (buttons, inputs, links, forms)
- Use consistent naming: `{component}-{element-role}` (e.g., `login-form-submit-button`, `user-list-search-input`)
- Avoid dynamic or auto-generated IDs that change between renders
- Keep `data-testid` values stable across code changes (only change when element purpose changes)

## Completion Criteria
- Story Selection completed (Step 0) and the implemented story recorded in the Story Tracker
- Complete code generation plan created and approved
- All steps in the code generation plan marked [x]
- The selected story implemented according to plan
- All code generated, with unit tests generated AND executed after implementation (Step 11a)
- Unit test coverage **≥90%** for all new/changed code (measured and iterated to target in the same run)
- **Proof artifacts saved** to `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/` — `unit-test-run.log` (raw runner output), `coverage-report.*` (the coverage tool's **mandatory** machine-readable report: lcov/xml/json/HTML), and `evidence-manifest.md` — with the reported X/X passing + coverage % matching those artifacts. Missing the coverage-report file = gate not satisfied
- Post-implementation Story Tracker update applied (status + timestamps); Jira phase prompt presented and applied if confirmed for Jira-tracked stories
- Deployment artifacts generated
- Story ready for build and verification
