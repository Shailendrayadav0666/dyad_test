# ✨ WORKFLOW: `enhancement-implement <JIRA-ID>` (Enhancement — Analysis + Implementation in ONE flow)

## MANDATORY: Rule Details Loading

May be invoked standalone in a fresh session. Resolve `.aipdlc-rule-details/` and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`, `common/question-format-guide.md`
- `common/branching-strategy.md` — **Bug Branch Model** section (the enhancement branch follows the same single-branch model, with the `enhancement/` prefix)
- `inception/workspace-detection.md`, `inception/reverse-engineering.md` (if RE runs), `inception/requirements-analysis.md`, `inception/workflow-planning.md`
- `construction/code-generation.md` (planning/generation/coverage mechanics — story selection and story-branch steps do NOT apply here). 🔴 **Follow the Guardrail defined there (Generation Phase Rules)** for any generated code.
- `workflows/code-review.md` (auto-run after the implementation) and `workflows/remediate.md` (on the Remediate path)

🔴 **GUARDRAIL — `code-review` and `remediate` are WORKFLOW RULE FILES, NOT Claude skills.** Whenever this workflow "runs Code Review" or "runs Remediate", you MUST `Read` and follow `workflows/code-review.md` / `workflows/remediate.md` (which pull their detailed steps from `construction/code-review.md` / `construction/remediate.md`) as instructions. There is **NO** Claude skill named `code-review` or `remediate` — **NEVER** invoke one via the Skill tool. The only review that IS a skill is **`pr-review`** (post-PR, AUTO MODE, invoked as-is).
- Extensions per CLAUDE.md's Extensions Loading rules (Security Baseline is ALWAYS mandatory)

Skills used **as-is — NEVER edit them**: **`pr-generator`** (pass target branch = the **Base Branch**; PR type `[ENH]`), **`pr-review`** (AUTO MODE after the PR), and **`archive-epic`** in **cycle mode** (🔴 **NEVER auto-invoked by this workflow — the operator runs it manually** after all SDET work has landed on the enhancement branch; archives under `aipdlc-archives/enhancements/`; see Step 19).

Display the welcome message (`common/welcome-message.md`) once at start. All CLAUDE.md audit-logging rules apply: log EVERY user input verbatim in `aipdlc-docs/audit.md` (append-only, ISO 8601 timestamps).

## MANDATORY: Audit Entry Format — JIRA TICKET on EVERY entry

Every audit.md entry in this workflow carries the `**User Email**:` field (current session email, read live), the `**JIRA TICKET**:` field (the enhancement ticket as a clickable Jira hyperlink `[PROJ-XXX](<site-base-url>/browse/PROJ-XXX)`), and — from Phase B onward — the `**AI-PDLC VERSION**:` field (read at runtime from the "AI-PDLC Framework Version" line in `CLAUDE.md` — never hardcoded), exactly as `dev-implement` does.

## MANDATORY: Approval Gates in this Workflow — GATE 2 and GATE 3

This workflow carries **exactly two numbered approval gates**, defined identically to `dev-implement`:

| Gate | Where | The decision |
|------|-------|--------------|
| **🚧 GATE 2** | **Step 11 — Implementation Plan** | Approve the implementation plan, or request changes. **No code is written before GATE 2 passes.** |
| **🚧 GATE 3** | **Step 15 — after the AUTO Code Review** | Approve & continue, or Remediate first. **Nothing is committed, pushed, or PR'd before GATE 3 passes.** |

There is **NO GATE 1 in the enhancement flow** — GATE 1 is the epic flow's approval of the COMPLETE story set (`inception/user-stories.md`), and this flow derives exactly ONE story from the ticket instead of generating a story set. The Phase A stage approvals (requirements, impact analysis, single story, workflow planning) and the **Implementation Gate** ("Ready to implement now? yes/no", between Phase A and Phase B) are **deliberately unnumbered** — they are stage/flow-control approvals, not numbered gates.

**🔴 GATE MARKING PROTOCOL (identical to `dev-implement` / `construction/code-generation.md` — never deviate)**:
1. **The gate is marked in the audit entry's `##` HEADING — there is NO separate `**GATE Number**:` field.** Never invent one.
2. **The PROMPT entry NEVER carries the gate marker** — the word "GATE" must NOT appear anywhere in the prompt entry's `##` heading. Use a plain heading (e.g. `## Implementation Plan Approval Prompt (Enhancement PROJ-456)`).
3. **The RESPONSE entry carries the gate in its `##` heading**, on **BOTH** outcomes — approved AND rejected alike.
4. Every re-ask at the same gate (after changes, or after a remediate loop) uses a `GATE N` heading again — on its RESPONSE entry only.
5. Entry body format is unchanged — every gate entry still carries `**User Email**:`, `**JIRA TICKET**:` and (Phase B) `**AI-PDLC VERSION**:`.

---

# PHASE A — Analysis (trimmed Inception + design)

## Step 1 — Ticket Capture

1. **Resume check first**: if `aipdlc-docs/aipdlc-state.md` exists, read it. If `## Jira` records a DIFFERENT ticket/epic, ask the user which to keep — NEVER silently overwrite. If it records this same ticket with `Workflow Type: enhancement`, resume from the recorded stage per `common/session-continuity.md`.
2. Parse the `<JIRA-ID>` from the invocation (key or URL). If missing, ask for it and wait.
3. **Fetch the ticket** via the Atlassian MCP (`getJiraIssue`) — issue type **Story or Task** (a Bug should go through `bug-fix` instead — warn if it's a Bug and confirm before continuing). Save summary, description, and acceptance criteria to `aipdlc-docs/inception/requirements/enhancement-brief.md` — the intake brief: it defines WHAT to enhance and is the primary input to every later stage.
4. Record in `aipdlc-docs/aipdlc-state.md`:
   ```markdown
   ## Jira
   - Workflow Type: enhancement
   - Parent Ticket: PROJ-456        (the enhancement being built — issue type: [Story/Task])
   - Ticket URL: https://<site>.atlassian.net/browse/PROJ-456
   - Project Key: PROJ              (derived from the key — confirm before first use)
   - Parent Epic: none              (enhancement flow — all Parent-Epic sync steps are skipped)
   ```
   `Workflow Type: enhancement` is the marker every resumed session reads FIRST — it routes execution to this workflow's rules.
5. **MANDATORY**: Log the invocation (complete raw input) and the ticket fetch in audit.md.

## Step 2 — Workspace Detection + Enhancement Branch (branch FIRST, before requirements)

1. Execute `inception/workspace-detection.md` Steps 1–4 as written (workspace scan, brownfield/greenfield, RE-artifact search anywhere in the repo, state file creation). An enhancement is expected to be **brownfield**; if the workspace is empty, STOP and suggest the full epic flow instead.
2. **Create the ENHANCEMENT branch (automatic)** — same single-branch model as the bug flow (`common/branching-strategy.md` Bug Branch Model), with the `enhancement/` prefix:
   - Record the **base branch** (`git branch --show-current` — never assume `main`).
   - Create `enhancement/<JIRA-ID>-<kebab-case-ticket-title>` (whole name ≤ 60 chars; working tree must be clean, else show `git status` and ask).
   - Record in `aipdlc-state.md`:
     ```markdown
     ## Branching
     - Base Branch: main
     - Enhancement Branch: enhancement/PROJ-456-export-to-csv
     - Enhancement PR: (pending — raised at the end after code review approval)
     ```
   - **ALL work — docs and code — happens on this ONE branch.** No story branches are ever cut.
3. Log the branch creation (name, base) in audit.md; present the Workspace Detection completion message and proceed automatically.

## Step 3 — Reverse Engineering (CONDITIONAL — as-is)

Exactly per the epic flow: if RE artifacts exist anywhere in the repo (or restorable from `aipdlc-archives/`), reuse them and skip. Otherwise run `inception/reverse-engineering.md` in full, with its approval gate. Log everything in audit.md.

## Step 4 — Requirements Analysis (as-is, enhancement-scoped)

1. Execute `inception/requirements-analysis.md` with `enhancement-brief.md` as the primary input. Depth will usually be **minimal/standard** (the ticket defines the enhancement); use comprehensive only if it is genuinely complex or high-risk. Its Step 1.5 reads the `## Context Project` answer captured by `ticket-implement` (Step 3.5) and, if `Use Artifacts: Yes`, uses **only** the recorded path as background context about the existing system — do NOT re-ask.
2. Extension opt-ins are presented as usual; Security Baseline is always enforced.
3. **Wait for explicit approval** of requirements.md.
4. On approval: commit the inception artifacts on the **enhancement branch**. 🔴 **Do NOT raise a PR here** — the single `[ENH]` PR is raised at the end, after code review approval.
5. **MANDATORY**: Log the user's response verbatim in audit.md.

## Step 5 — Impact Analysis (NO AI-Origin Detection)

**Purpose**: Find WHERE the enhancement lands — the files/components to change and the blast radius — for an accurate implementation plan.

1. Using the RE artifacts, the enhancement-brief, and code search (grep/glob/read), identify the **affected files/components**: where the new behavior plugs in, what must change, and the blast radius (callers, consumers, shared files, tests). Cite explicit **`file:line-range`** evidence per touch point.
2. Write `aipdlc-docs/inception/impact-analysis.md`:
   ```markdown
   # Impact Analysis — [JIRA-ID]
   ## Change Approach
   [Where the enhancement plugs in and why, with file:line evidence]
   ## Affected Files
   | File | Why it must change |
   |------|--------------------|
   ## Blast Radius
   [Callers/consumers/tests that could be impacted by the change]
   ```
3. Present the Impact Analysis summary and **wait for explicit approval** before proceeding. Log the response verbatim. This document is the primary planning input for the implementation phase.

## Step 6 — Single Story (replaces User Stories + Dependency Graph)

1. Write **exactly ONE story** to `aipdlc-docs/inception/user-stories/stories.md`, derived from the ticket + requirements + impact analysis: story ID `1.1`, title = the enhancement, acceptance criteria from the ticket (plus regression-safe), and a `**Covers**: REQ-F-xx, …` line naming the REQ-IDs assigned in the enhancement-scoped `requirements.md` (`common/requirements-traceability.md` Rules 2 & 7) — coverage must be complete: every REQ-ID from that requirements.md maps to this one story. Do NOT ask team size, do NOT generate extra personas, do NOT ask about pushing to Jira (the ticket exists — no new issue is ever created), do NOT create `dependency-graph.yml`.
2. Populate the Story Tracker in `aipdlc-state.md` with the single row (Jira column = the existing enhancement ticket — the Jira Sync Rule applies to it at every status change):
   | Story | Title | Requires | Jira | Status | Start | End | Recorded |
   |-------|-------|----------|------|--------|-------|-----|----------|
   | 1.1 | [Enhancement title] | none | PROJ-456 | 🟢 Ready for Development | | | [timestamp] |
3. **Wait for explicit approval** of the story; log the response verbatim.

## Step 7 — Workflow Planning (as-is)

Execute `inception/workflow-planning.md`: determine which Construction design stages EXECUTE/SKIP for this enhancement (small enhancements skip most design stages), generate the execution plan + visualization (validate Mermaid), and **wait for explicit approval**.

## Step 8 — Construction Design Stages (CONDITIONAL, as-is)

Run the system-level design stages the plan selected (Functional Design → NFR Requirements → NFR Design → Infrastructure Design), each per its rule file with its standardized 2-option completion message and approval gate. Scope each to the enhancement-brief + impact analysis.

---

# 🛑 SDET HANDOFF BREAK → 🚦 Implementation Checkpoint (ask, don't stop)

After the design stages complete (or are all skipped), mark in `aipdlc-state.md`: `Analysis complete — awaiting implementation approval`, log in audit.md.

**This is a deliberate BREAK in the flow.** The analysis + design artifacts are everything the SDET needs, and the SDET must not have to wait for the code. So before Phase B:

1. **Commit + push the analysis and design artifacts on the enhancement branch (automatic — this is what unblocks SDET)**: stage `aipdlc-docs/inception/**` (enhancement-brief, requirements, impact analysis, the single story), `aipdlc-docs/construction/design/**`, the updated `aipdlc-state.md` and `audit.md`; commit on the enhancement branch with an `AI-PDLC-Version: [N]` trailer (`[N]` read live from `CLAUDE.md`); push to origin. Announce the commit hash + pushed branch and log both in audit.md. 🔴 If the push fails, say so explicitly and tell the user to push manually — **the SDET cannot start until this branch is on origin**. Still no `[ENH]` PR here.
2. Present the break message below and **block on its yes/no**.

```markdown
# ✅ Enhancement Analysis Done — Design Artifacts Pushed

✨ **Ticket**: [JIRA-ID] — [title]
📍 **Impact**: [N] files identified in aipdlc-docs/inception/impact-analysis.md
🧩 Design stages: [list which ran vs were skipped]
🌿 Branch: enhancement/[JIRA-ID]-[title] (cut from [base branch]) — analysis + design **committed and pushed** ([commit hash])

> **🧪 <u>**SDET — start NOW, in parallel. The code does not have to exist.**</u>**
> 1️⃣  `git fetch origin && git checkout enhancement/[JIRA-ID]-[title] && git pull --ff-only`
> 2️⃣  Type **`/sdet-implement [JIRA-ID]`**
>     It cuts `sdet/[JIRA-ID]-[title]` from this branch, writes the MANUAL test steps to
>     `aipdlc-docs/tests/[JIRA-ID]-[title]/` from the ticket's acceptance criteria, and raises its
>     own PR back into `enhancement/[JIRA-ID]-[title]` — so the test docs ride the `[ENH]` PR into [base branch].

> **⚙️ <u>**DEV — continue with the implementation plan and code generation**</u>**
> ❓ **Ready to implement now? (yes / no)**
> **yes** → baseline regression → implementation plan (🚧 GATE 2 — your approval) → code + unit
>           tests (≥90% coverage) → FULL regression → auto code review (🚧 GATE 3) → `[ENH]` PR to
>           [base branch] → auto PR review → then STOP (the cycle archive is MANUAL — you run
>           `archive-epic` after the SDET test-plan PR merges into the enhancement branch).
> **no**  → I halt here; the state is saved. Resume any time with `ticket-implement [JIRA-ID]`
>           (or `enhancement-implement [JIRA-ID]`) and it picks up at this gate.

🔴 Use `/sdet-implement` and the keywords EXACTLY as shown — do not describe what you want in your
   own words. Any other phrasing is not a framework trigger and the workflow will not advance.
```

**Block until the user answers.** On **no**, halt here (state is saved — re-invoking `enhancement-implement <JIRA-ID>` or `ticket-implement <JIRA-ID>` resumes at this gate). On **yes**, log the response verbatim and continue to Phase B. Substitute every placeholder (`[JIRA-ID]`, `[base branch]`, `[commit hash]`) with real values — never ship a placeholder to the user.

---

# PHASE B — Implementation (same flow, after "yes")

## Step 9 — Ticket → 🔵 In Development (automatic)

The user's "yes" IS the claim. Without asking:
1. Story Tracker (single row): Status → `🔵 In Development`, Start + Recorded timestamps set.
2. Transition the Jira ticket to the board's "In Development" state via the Atlassian MCP — resolve the actual transition with `getTransitionsForJiraIssue` (never hardcode the state name). **Verify it landed**, announce it, log in audit.md.
3. **👤 Assign the ticket to the operator (automatic — same claim)**: read the session **email** LIVE from the session context, resolve it with `lookupJiraAccountId`, set the assignee via `editJiraIssue`, **verify** by fetching the issue back. Unresolvable/ambiguous email → leave unassigned, warn, continue (non-blocking). Announce and log in audit.md.
4. **Add the AI-PDLC version label** `aipdlc-v[N]` to the ticket ( `[N]` read at runtime from the "AI-PDLC Framework Version" line in `CLAUDE.md` — never hardcoded). Skip if already present. Verify, announce, log.
5. 🔴 Skip all Parent-Epic sync steps — `## Jira` records `Parent Epic: none`.

## Step 10 — 🧪 BASELINE Regression Run (BEFORE any change)

Same as the bug flow: discover and run the **entire repo's unit test suite** with no code changes yet; record the baseline (commands, results, pre-existing failures) in `aipdlc-docs/construction/code/enhancement-<JIRA-ID>-summary.md`; pre-existing failures are logged, not fixed. Log in audit.md. If the repo has no test suite, record that explicitly.

## Step 11 — Implementation Plan (🚧 GATE 2)

1. Build the plan from `impact-analysis.md` + the design artifacts, using `code-generation.md`'s Part 1 planning format (checkboxed steps), ending with the mandatory Unit Test & Coverage (≥90%) step and the Full Regression Gate (Step 14). **📐 GROUND THE PLAN in the previously generated docs** — every step MUST trace back to the ticket's acceptance criteria, `enhancement-brief.md`, `requirements.md`, the impact analysis, and any design artifacts; never invent scope, files, or behavior not backed by them. **🧾 REQ-ID THREAD**: tag every plan step with the REQ-ID(s)/AC(s) it implements and self-check that every REQ-ID from `requirements.md` and every AC of the single story appears in ≥1 step before presenting the plan (`common/requirements-traceability.md` Rules 5 & 7).
2. **Re-validate the impact analysis against current code.** If the plan must touch files NOT in the impact analysis, add them to `impact-analysis.md` first .
3. **🚧 GATE 2 — Implementation Plan Approval (MANDATORY — no code before this passes)**:
   1. **Log the prompt** in `aipdlc-docs/audit.md` (ISO 8601 timestamp) BEFORE asking, with a plain heading like `## Implementation Plan Approval Prompt (Enhancement [JIRA-ID])`; **the word "GATE" must NOT appear in the prompt entry's heading** ("GATE 2" belongs only on the response entry, below). Include a reference to the complete implementation plan.
   2. Present the plan, then ask (verbatim):
      ```
      📋 Implementation plan ready for Enhancement [JIRA-ID] — [N] steps.
      Plan: aipdlc-docs/construction/plans/enhancement-[JIRA-ID]-implementation-plan.md

      ❓ What next?
        A) ✅ Approve plan     — proceed to generate the enhancement (Step 12)
        B) 🔧 Request changes  — revise the plan and re-present
      [Answer]:
      ```
   3. **Wait for explicit approval — do NOT proceed to Step 12 until the user approves.** On **B**, revise the plan and re-present (each re-ask logs a fresh GATE 2 response entry).
   4. **MANDATORY**: Log the user's raw response in audit.md. **🚧 This decision is GATE 2** — the gate is marked in the response entry's `##` HEADING (there is NO separate `**GATE Number**:` field), on BOTH outcomes:
      - A: `## Implementation Plan — GATE 2 Plan Approved (Enhancement [JIRA-ID])`
      - B: `## Implementation Plan — GATE 2 Plan Rejected — Changes Requested (Enhancement [JIRA-ID])`
      Mark the outcome clearly (✅ approved / ❌ rejected — changes requested). Entry body format is unchanged.

## Step 12 — Generate the Enhancement

Execute the approved plan step by step on the enhancement branch, marking each checkbox `[x]` in the same interaction it completes. **🛡️ PLAN FIDELITY**: implement EXACTLY the GATE 2-approved plan — no unplanned files, features, refactors, or scope drift; a needed deviation goes back through **GATE 2** (Step 11) for re-approval, never applied silently. Write code to the workspace root per the existing project structure. Log progress in audit.md.

## Step 13 — Unit Tests + Coverage Gate (≥90%)

1. Write unit tests covering all new/changed code, exercising the enhancement's acceptance criteria.
2. RUN them; fix failures; measure coverage on the new/changed code; iterate in the SAME run until **≥90%**.
3. Capture evidence (tests X/X passing + measured %) in `enhancement-<JIRA-ID>-summary.md` and audit.md, with the machine-readable coverage report per dev-implement's evidence rules (`aipdlc-docs/construction/code/unit-test-evidence/story-1.1/`).

## Step 14 — 🧪 FULL Regression Gate (after the change)

Re-run the **entire repo's unit test suite** and compare against the Step 10 baseline — exactly as the bug flow: **new failures** (passing at baseline, failing now) are 🔴 BLOCKING (fix and re-run until zero); pre-existing failures are listed, not blocking. Append the complete outcome to `enhancement-<JIRA-ID>-summary.md` and log the comparison in audit.md.

## Step 15 — AUTO Code Review → 🚧 GATE 3 Approve / Remediate

Mirrors dev-implement Sections A–C, enhancement-scoped. The Code Review runs **automatically** — the user is NOT asked whether to review.

### 15a. AUTO Code Review (MANDATORY, automatic)
1. **Log** in audit.md that automated Code Review is starting for Enhancement [JIRA-ID] (ISO 8601 timestamp).
2. Auto-run `workflows/code-review.md` scoped to this change (read-only — it MUST NOT edit source) → versioned report `aipdlc-docs/construction/reviews/enhancement-<JIRA-ID>-code-review-v[X].md`. Pass in the Step 13/14 evidence — the review MUST NOT re-run the tests or re-measure coverage; it cites the stored evidence.
3. **MANDATORY — audit the complete review log**: the `**JIRA TICKET**:` field, report path, verdict, and the complete list of findings by severity (🔴 Blocker / 🟠 High). Do not summarize away findings.
4. Proceed to **15b**.

### 15b. 🚧 GATE 3 — Review Decision Gate (MANDATORY)
1. **Log the prompt** in audit.md with a plain heading like `## Review Decision Prompt (Enhancement [JIRA-ID])`; **the word "GATE" must NOT appear in the prompt entry's heading** ("GATE 3" belongs only on the response entry, step 4) — then present (verbatim):
   ```
   🔍 Automated Code Review complete for Enhancement [JIRA-ID].
   Report: aipdlc-docs/construction/reviews/enhancement-[JIRA-ID]-code-review-v[X].md
   Verdict: [clean — all ACs Met / findings: 🔴 X  🟠 Y]

   ❓ What next?
     A) ✅ Approve & continue — commit, push `<enhancement-branch>`, and raise the [ENH] PR
     B) 🔧 Remediate        — fix the review findings first
   [Answer]:
   ```
2. **On A (Approve & continue)** → go to **Step 16 (Commit, Push & Raise the `[ENH]` PR)**.
3. **On B (Remediate)** → go to **15c**.
4. **MANDATORY**: Log the user's raw response in audit.md. **🚧 This decision is GATE 3** — the gate is marked in the response entry's `##` HEADING (there is NO separate `**GATE Number**:` field), on BOTH outcomes:
   - A: `## Review Decision — GATE 3 Approved & Continue (Enhancement [JIRA-ID])`
   - B: `## Review Decision — GATE 3 Not Approved — Remediate (Enhancement [JIRA-ID])`
   Entry body format is unchanged; the prompt entry never carries the gate marker.

### 15c. Remediate Loop (on Remediate)
1. **Log** in audit.md that Remediate is starting for Enhancement [JIRA-ID], naming the review report being remediated.
2. Run `workflows/remediate.md` scoped to that report (fix → unit test → green). **Re-run the FULL repo suite if the remediation touched non-test code**, comparing against the Step 10 baseline again — only NEW failures block.
3. **MANDATORY — audit the complete remediate log**: which findings were fixed (by severity), files changed, unit-test evidence, regression comparison. Record the complete log, not a summary.
4. **🚧 Post-Remediate Decision Gate** — log the prompt with a plain heading like `## Post-Remediate Decision Prompt (Enhancement [JIRA-ID])` (**the word "GATE" must NOT appear in the prompt entry's heading**), then present (verbatim):
   ```
   🔧 Remediation complete for Enhancement [JIRA-ID].
   ❓ What next?
     A) ✅ Approve & continue — commit, push `<enhancement-branch>`, and raise the [ENH] PR
     B) 🔁 Re-review        — run automated Code Review again
   [Answer]:
   ```
   - **On A** → go to **Step 16**.
   - **On B (Re-review)** → return to **15a** (produces the next report version `v[X+1]`), then **15b** again. This loop repeats until the user chooses Approve & continue.
5. **MANDATORY**: Log the user's raw response in audit.md. **🚧 This decision is GATE 3** — marked in the response entry's `##` HEADING (no separate field), on BOTH outcomes:
   - A: `## Post-Remediate Decision — GATE 3 Approved & Continue (Enhancement [JIRA-ID])`
   - B: `## Post-Remediate Decision — GATE 3 Not Approved — Re-review (Enhancement [JIRA-ID])`

### 15d. Status
The ticket stays `🔵 In Development` throughout review and remediation.

## Step 16 — Commit, Push & Raise the `[ENH]` PR

1. Confirm the active branch is the Enhancement Branch. Stage and commit (code + tests + updated docs) with the framework signature trailer, `[N]` read live from CLAUDE.md:
   ```
   git add <files>
   git commit -m "[ENH][PROJ-456] <concise enhancement summary>" -m "AI-PDLC-Version: [N]"
   ```
   Record the hash in audit.md.
2. Invoke **`pr-generator`** (as-is), passing **target branch = the Base Branch** from `## Branching`. The PR title carries the **`[ENH]`** prefix; the skill applies the `ai-generated` and `aipdlc-v[N]` labels (plus the `AI-PDLC Framework: v[N]` line in the PR body) and its own Phase 5 confirmation gate — honor it.
3. Record the PR URL in `## Branching` (`Enhancement PR: <url>`) and the full outcome in audit.md.

## Step 17 — Tracker Update (NO Ready-for-Testing transition)

1. Story Tracker: keep Status = `🔵 In Development`; set **End** = today and **Recorded** = now; note the PR URL.
2. 🔴 **Do NOT transition the Jira ticket to "Ready for Testing"** — the ticket stays In Development after the PR. Promotion is SDET's, via `sdet-list-work` Option B, run **on `<enhancement-branch>` while the `[ENH]` PR is still OPEN** — never post-merge on the base branch (see Step 19). Add a Jira **comment** on the ticket (confirm-first) linking the PR with evidence (tests passing, coverage %, regression clean vs baseline).
3. Log in audit.md (with the JIRA TICKET field).

## Step 18 — AUTO PR Review

Invoke the **`pr-review`** skill (as-is) in **AUTO MODE** against the just-raised PR: it posts a plain COMMENT review (summary + inline comments) automatically — no prompt, never a formal APPROVE/REQUEST_CHANGES. Record the outcome in audit.md.

## Step 19 — Archive Handoff (MANUAL)

🔴 **RE-READ FIRST.** Before writing any part of this step's output, `Read` this Step 19 section from the file again. Do NOT reconstruct it from memory or from earlier in this session's context — "I already read this file earlier" does not satisfy this.

### The ordering invariant

| # | Action | Relative to the archive |
|---|--------|-------------------------|
| 1 | `sdet/...` PR(s) merge into `<enhancement-branch>` | BEFORE |
| 2 | `sdet-list-work` Option C amendments pushed to `<enhancement-branch>` | BEFORE |
| 3 | `sdet-list-work` Option B sign-off → ticket `🧪 Ready for Testing` | BEFORE |
| 4 | **`archive-epic`** (enhancement mode) | ⬅ **THE ARCHIVE** |
| 5 | **`[ENH]` PR merges into `<base-branch>`** | AFTER |
| 6 | `stitch-delta` on `<base-branch>` | AFTER |

🔴 **`archive-epic` runs at row 4 — BEFORE the `[ENH]` PR merges (row 5).** Its cycle-close commit must ride the still-OPEN `[ENH]` PR; that is the ONLY path by which the RE delta reaches `<base-branch>` for `stitch-delta`.

**TWO DIFFERENT PRs appear here — never write "the PR" unqualified:**
- the **`sdet/...` PR** → merges into `<enhancement-branch>`. The archive **waits for this one**.
- the **`[ENH]` PR** → merges into `<base-branch>`. The archive **must precede this one**.

"Wait until all SDET work has landed" means rows 1–3 **only** — never row 5.

**🔴 BANNED OUTPUT — each inverts the invariant. Never emit them, in any wording:**
- "archive runs post-merge" / "it runs post-merge only"
- "when the `[ENH]` PR merges, run `archive-epic`"
- "DO NOT invoke `archive-epic` manually now"
- any instruction for the developer to transition the Jira ticket in this step

Do NOT invoke `archive-epic`, do NOT ask whether to invoke it, and do NOT add an options menu or any competing next-steps block. The block below is the entire output of this step.

### Emit this message VERBATIM (placeholders substituted)

The ONLY permitted modification is substituting `<url>`, `<enhancement-branch>`, `<base-branch>`, `[JIRA-ID]`, `<slug>` with real values from `## Branching` / the Step 16 PR. **Never ship an unsubstituted placeholder**; never add, remove, reorder, reword, or summarise a line:

```
✅ Enhancement complete — [ENH] PR: <url> (ticket [JIRA-ID] remains 🔵 In Development).
   📦 The cycle archive was deliberately NOT run — it is yours to run, at step 4️⃣ below.

➡️ NEXT ACTIONS (in this order):
   1️⃣  Wait until the SDET `sdet/...` PR(s) for [JIRA-ID] have MERGED into `<enhancement-branch>`
       (the SDET PR into the enhancement branch — NOT the [ENH] PR into `<base-branch>`)
   2️⃣  On `<enhancement-branch>`: `git checkout <enhancement-branch> && git pull --ff-only`
       (pulls the merged `aipdlc-docs/tests/<JIRA-ID>-.../` docs in so the archive captures them)
   3️⃣  SDET: use the skill sdet-list-work — on `<enhancement-branch>`, NOT on `<base-branch>`
       • Option C to amend a test plan (commit + push to `<enhancement-branch>` so the archive captures it)
       • Option B to sign off — promotes ticket [JIRA-ID] 🔵 In Development → 🧪 Ready for Testing
       (Sign-off happens HERE, before the archive — so the tracker still exists and the sign-off
        plus test-plan edits are captured in the archive.)
   4️⃣  Use the skill archive-epic  (enhancement mode → `aipdlc-archives/enhancements/<JIRA-ID>-<slug>/`)
       🔴 MUST happen while the [ENH] PR is still OPEN — its cycle-close commit rides that
          open PR, which is how the RE delta reaches `<base-branch>`.
   5️⃣  ONLY NOW merge the [ENH] PR into `<base-branch>`: <url>
   6️⃣  Switch to `<base-branch>` and pull the latest
   7️⃣  Use the skill stitch-delta (applies this enhancement's RE delta to the root docs — final action;
       the ONLY base-branch step)

🔴 ORDER IS LOAD-BEARING: archive-epic (4️⃣) runs BEFORE the [ENH] PR merges (5️⃣).
   Merging first breaks stitch-delta and forces a manual recovery PR.
🔴 Use the skill names EXACTLY as shown — do not describe what you want in your own words.
   Any other phrasing is not a framework trigger and the workflow will not advance.
```

---

## Critical Rules
- EVERY audit entry carries `**User Email**:` and `**JIRA TICKET**:`; Phase B entries also carry `**AI-PDLC VERSION**:` (read live from CLAUDE.md — never hardcoded).
- ONE branch (`enhancement/...`) created FIRST — before requirements; ONE story, NO dependency graph, NO new Jira issues, NO epic branch, NO Parent-Epic sync.
- NO PR at requirements approval — the single `[ENH]` PR is raised at Step 16 after review approval, target = Base Branch, via `pr-generator` only, `ai-generated` + `aipdlc-v[N]` labels.
- The **SDET Handoff Break** runs BEFORE the Implementation Gate question: ALWAYS commit + push the analysis/design artifacts on the enhancement branch first (the SDET's `/sdet-implement` needs them on origin) and present the SDET instructions. The SDET's run is independent of the yes/no answer and of the code existing at all.
- The Implementation Gate is a **yes/no question in the same flow** — never auto-continue into Phase B without the user's explicit "yes"; on "no", halt with state saved. It is **deliberately unnumbered** (flow control, not a numbered gate) — only GATE 2 and GATE 3 are numbered in this workflow.
- 🔴 **GATE 2 (Step 11) is the gate before any code exists** — NEVER write a single line of the enhancement until the user explicitly approves the implementation plan. Any mid-coding deviation from the approved plan goes back through GATE 2 for re-approval, never applied silently.
- 🔴 **GATE 3 (Step 15) is the gate before anything leaves the machine** — NEVER commit, push, or raise the `[ENH]` PR until the user explicitly chooses "Approve & continue" at the Review Decision Gate or the Post-Remediate Decision Gate.
- **GATE MARKING PROTOCOL** — the gate is marked ONLY in the audit entry's `##` HEADING; there is NO `**GATE Number**:` field. The PROMPT entry never carries the word "GATE"; the RESPONSE entry carries `GATE 2` / `GATE 3` on BOTH outcomes (approved AND rejected alike), and every re-ask logs a fresh gated response entry. See the Approval Gates section above.
- This workflow has **NO GATE 1** — GATE 1 is the epic flow's COMPLETE-story-set approval; the enhancement flow derives ONE story from the ticket.
- At Step 9, ALWAYS assign the Jira ticket to the operator (session email → `lookupJiraAccountId` → `editJiraIssue`; automatic, verified, logged; failure non-blocking).
- ALWAYS run the BASELINE regression BEFORE any change and the FULL regression AFTER; only NEW failures (vs baseline) block; log both runs in `enhancement-<JIRA-ID>-summary.md`.
- Plan grounded in the previously generated docs; coding follows the approved plan exactly — deviations re-approved, never silent. Coverage on new/changed code ≥90%.
- The ticket stays `🔵 In Development` after the PR — promotion to Ready for Testing is SDET's, via `sdet-list-work` Option B run **on the enhancement branch, before `archive-epic` and before the `[ENH]` PR merges** (not post-merge on the base branch — after the archive's workspace reset there is no Story Tracker left to promote).
- **NEVER run Build & Test in this workflow.** Build and Test is not a Construction step at any level — it belongs to SDET and is run separately, per ticket, via the **`/sdet-implement`** skill (black-box, from the ticket's acceptance criteria, into `aipdlc-docs/tests/<JIRA-ID>-<jira-title>/`). Do not load `construction/build-and-test.md` here and do not write anything under `aipdlc-docs/construction/build-and-test/`.
- 🔴 After the PR: AUTO `pr-review` (comment-only), then **STOP — the archive is MANUAL**. NEVER invoke `archive-epic` from this workflow. **Re-read Step 19 before emitting its handoff, and emit that block VERBATIM with placeholders substituted** — do not paraphrase it. The operator runs `archive-epic` once the SDET `sdet/...` PR(s) (and any `sdet-list-work` Option C amendments) have merged **into the enhancement branch**, and **BEFORE the `[ENH]` PR merges into the base branch**, so the delta rides the open PR for post-merge `stitch-delta`. Never tell the user the archive runs post-merge — that inverts the invariant.
- Security Baseline extension always applies; other extensions per their recorded opt-ins.
