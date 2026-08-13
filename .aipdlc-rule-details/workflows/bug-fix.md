# 🐞 WORKFLOW: `bug-fix <JIRA-ID>` (Bug/Defect — Inception)

**Purpose**: Take an existing Jira defect ticket through a trimmed Inception + design pass, **break once at the SDET handoff** (Step 9 — design artifacts committed + pushed so the SDET can start `/sdet-implement` in parallel), then continue into `bug-fix-implement` on the user's `yes` — no second keyword needed. The ticket may be of Jira issue type **Bug OR Story** — raised by anyone (not necessarily via the `raise-defect` skill).

**How the bug flow differs from the epic flow**:
- ONE branch: `bug/<JIRA-ID>-<kebab-title>` cut from the **base branch**. No epic branch, no story branches.
- ONE story, derived from the ticket itself — no team-size question, no story generation loop, no push-to-Jira (the ticket already exists), **no Dependency Graph stage**.
- NO PR after Requirements approval — the single **`[BUG]`** PR is raised at the END by `bug-fix-implement`, after code review approval.
- A NEW **Impact Analysis + AI-Origin Detection** step replaces multi-story planning.
- The ticket is transitioned to "In Development" when `bug-fix-implement` starts and is **NEVER moved to "Ready for Testing" by these workflows**
- All Parent-Epic sync steps are **skipped** — there is no epic in this flow.

## MANDATORY: Rule Details Loading

This workflow may be invoked standalone in a fresh session. Resolve the rule details directory (`.aipdlc-rule-details/`) and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`, `common/question-format-guide.md`
- `common/branching-strategy.md` — **Bug Branch Model** section
- `inception/workspace-detection.md`, `inception/reverse-engineering.md` (if RE runs), `inception/requirements-analysis.md`, `inception/workflow-planning.md`
- `agents/defect-provenance-analyst.md` — loaded at Step 5b (line-level AI-origin detection)
- Extensions per CLAUDE.md's Extensions Loading rules (Security Baseline is ALWAYS mandatory)

Display the welcome message (`common/welcome-message.md`) once at start. All CLAUDE.md audit-logging rules apply: log EVERY user input verbatim in `aipdlc-docs/audit.md` (append-only, ISO 8601 timestamps).

## MANDATORY: Audit Entry Format — JIRA TICKET on EVERY entry

Every audit.md entry written during this workflow MUST include the `**User Email**:` field (current session email) and the `**JIRA TICKET**:` field with the defect ticket as a clickable Markdown link `[PROJ-XXX](<site-base-url>/browse/PROJ-XXX)`:

```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO timestamp]
**User Email**: [current session email — read live from the session context]
**User Input**: "[Complete raw user input - never summarized]"
**JIRA TICKET**: "[The defect ticket, as a Jira hyperlink]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

## Approval Gates — this workflow owns NONE of the numbered gates

The bug flow's **numbered** approval gates both live in `workflows/bug-fix-implement.md`:

| Gate | Where | The decision |
|------|-------|--------------|
| **🚧 GATE 2** | `bug-fix-implement` Step 4 — Fix Plan | Approve the fix plan, or request changes. **No code before it passes.** |
| **🚧 GATE 3** | `bug-fix-implement` Step 8 — after the AUTO Code Review | Approve & continue, or Remediate. **No commit/push/PR before it passes.** |

Every approval inside THIS file (requirements at Step 4, impact analysis at Step 5, the single story at Step 6, workflow planning at Step 7) is a **stage approval, NOT a numbered gate** — do NOT put "GATE" in any audit heading written by this workflow. There is **NO GATE 1 in the bug flow**: GATE 1 is the epic flow's approval of the COMPLETE story set (`inception/user-stories.md`), and this flow derives exactly ONE story from the ticket instead of generating a story set.

---

## Step 1 — Ticket Capture

1. **Resume check first**: if `aipdlc-docs/aipdlc-state.md` exists, read it. If `## Jira` records a DIFFERENT ticket/epic, ask the user which to keep — NEVER silently overwrite. If it records this same ticket with `Workflow Type: bug`, resume from the recorded stage per `common/session-continuity.md`.
2. Parse the `<JIRA-ID>` from the invocation (key or URL). If missing, ask for it and wait.
3. **Fetch the ticket** via the Atlassian MCP (`getJiraIssue`) — accept issue type **Bug or Story** (or Task). Save summary, description, severity, steps to reproduce, environment, and acceptance criteria (if any) to `aipdlc-docs/inception/requirements/bug-brief.md`. The bug-brief is the intake brief: it defines WHAT to fix and is the primary input to every later stage.
4. Record in `aipdlc-docs/aipdlc-state.md`:
   ```markdown
   ## Jira
   - Workflow Type: bug
   - Parent Ticket: PROJ-123        (the defect being fixed — issue type: [Bug/Story])
   - Ticket URL: https://<site>.atlassian.net/browse/PROJ-123
   - Project Key: PROJ              (derived from the key — confirm before first use)
   - Parent Epic: none              (bug flow — all Parent-Epic sync steps are skipped)
   ```
   `Workflow Type: bug` is the marker every resumed session reads FIRST — it routes execution to this workflow's rules, not the epic flow's.
5. **MANDATORY**: Log the invocation (complete raw input) and the ticket fetch in audit.md.

## Step 2 — Workspace Detection + Bug Branch

1. Execute `inception/workspace-detection.md` Steps 1–4 as written (workspace scan, brownfield/greenfield, RE-artifact search anywhere in the repo, state file creation). A bug fix is expected to be **brownfield**; if the workspace is empty, STOP and tell the user there is no code to fix.
2. **Step 4.5 replacement — create the BUG branch (automatic)** instead of an epic branch. Execute `common/branching-strategy.md` **Bug Branch Model**:
   - Record the **base branch** (`git branch --show-current` — never assume `main`).
   - Create `bug/<JIRA-ID>-<kebab-case-ticket-title>` (whole name ≤ 60 chars; working tree must be clean, else show `git status` and ask).
   - Record in `aipdlc-state.md`:
     ```markdown
     ## Branching
     - Base Branch: main
     - Bug Branch: bug/PROJ-123-login-timeout
     - Bug PR: (pending — raised by bug-fix-implement after code review approval)
     ```
   - **ALL work — docs and code — happens on this ONE branch.** No story branches are ever cut in the bug flow.
3. Log the branch creation (name, base) in audit.md; present the Workspace Detection completion message and proceed automatically.

## Step 3 — Reverse Engineering (CONDITIONAL — as-is)

Exactly per the epic flow: if RE artifacts exist anywhere in the repo (or restorable from `aipdlc-archives/epics/` or `aipdlc-archives/bugs/` — workspace-detection Step 3 covers this), reuse them and skip. Otherwise run `inception/reverse-engineering.md` in full, with its approval gate. Log everything in audit.md.

## Step 4 — Requirements Analysis (as-is, bug-scoped)

1. Execute `inception/requirements-analysis.md` with `bug-brief.md` as the primary input. Depth will usually be **minimal** (the ticket defines the defect); use standard/comprehensive only if the fix is genuinely complex or high-risk. Its Step 1.5 reads the `## Context Project` answer captured by `ticket-implement` (Step 3.5) and, if `Use Artifacts: Yes`, uses **only** the recorded path as background context about the existing system — do NOT re-ask.
2. Extension opt-ins are presented as usual; Security Baseline is always enforced.
3. **Wait for explicit approval** of requirements.md.
4. On approval: commit the inception artifacts on the **bug branch**. 🔴 **Do NOT raise a PR here** — unlike the epic flow's Step 10, the bug flow raises its single `[BUG]` PR at the end, inside `bug-fix-implement`.
5. **MANDATORY**: Log the user's response verbatim in audit.md.

## Step 5 — 🆕 Impact Analysis + AI-Origin Detection

**Purpose**: Find WHERE the fix must be made (better planning), and determine whether the defective code was AI-generated (defect attribution).

### 5a. Impact Analysis
1. Using the RE artifacts, the bug-brief, and code search (grep/glob/read), identify the **affected files/components**: where the defect lives, the likely root cause, and the blast radius (callers, consumers, shared files). The Root-Cause Hypothesis MUST cite explicit **`file:line-range`** evidence per affected file — 5b's line-level provenance tracing consumes these exact ranges.
2. Write `aipdlc-docs/inception/impact-analysis.md`:
   ```markdown
   # Impact Analysis — [JIRA-ID]
   ## Root-Cause Hypothesis
   [What is wrong and why, with file:line evidence]
   ## Affected Files
   | File | Why it must change | Defect-line origin (5b) | Originating ticket (5b) |
   |------|--------------------|-------------------------|-------------------------|
   ## Blast Radius
   [Callers/consumers/tests that could be impacted by the fix]
   ```
3. This document is the primary planning input for `bug-fix-implement`'s fix plan.

### 5b. AI-Origin Detection (line-level, via the Defect Provenance Analyst agent)
1. Load `agents/defect-provenance-analyst.md` and execute its procedure with 5a's root-cause `file:line-range` findings as input. It traces each **defective line** (not the file's last change) to the commit that **introduced** the defective logic (`git blame -w -M -C -L`, walking past cosmetic commits via `git log -L`; omission bugs attribute to the enclosing block's introducing commit), resolves that commit's PR, resolves the **originating Jira ticket** that shipped the line, and returns a **Provenance Verdict table** — verdict AI-generated / human / **undetermined**, each row with concrete evidence (SHA, PR number, which marker) plus the originating ticket and which source it came from.
2. Record each verdict (with introducing commit + evidence) in the impact-analysis table's **Defect-line origin (5b)** column, and include the full Provenance Verdict table in `impact-analysis.md`. 🔴 Label only on positive evidence (per the agent's marker rules) — NEVER guess; "undetermined" gets no label.
3. **If ANY defective line's introducing change is AI-generated**, ask (confirm-first):
   ```
   🤖 The defective line(s) [file:line(s)] were introduced by AI-generated code
      (evidence: [PR #N "ai-generated" label / Claude co-author on <sha> / AI-PDLC-Version trailer]).
   Add the label "ai-generated-defect" to Jira ticket [JIRA-ID]? (yes / skip)
   ```
   On yes: add the label via the Atlassian MCP (`editJiraIssue`), **verify it landed**, and log the complete evidence (file:line, introducing commit SHA, PR number, which marker) in audit.md. On skip: log the skip.
4. If no defective line is AI-generated: log "human-origin (or undetermined) — no label applied" in audit.md with the per-line evidence.

### 5c. Link the Bug to its Originating Ticket(s) — AUTOMATIC (no confirmation)

Establishes the relationship `[Bug] --"is caused by"--> [Originating Story / Bug / Enhancement]` so the causal chain is queryable in Jira without anyone doing it by hand. This runs **automatically** — there is no confirm-first gate — because the analyst reports a ticket only on positive, verified evidence.

1. Take the analyst's **deduplicated list of resolved originating ticket keys** (5b). Drop any key equal to the bug's own `Parent Ticket` (self-link guard). If the list is empty (all rows `—` or `undetermined`), skip silently and log "no originating ticket resolvable — no link created" in audit.md with the per-line evidence.
2. **Resolve the link type at runtime** via `getIssueLinkTypes` — 🔴 never hardcode a type name. Every Jira link type has an *outward* description (how A relates to B) and an *inward* description (how B relates to A); match on the **inward** one.

   **Selection rule** — exactly one type qualifies:
   - A type whose inward description is exactly **"is caused by"**. Use it (step 3a).
   - **Nothing else qualifies.** No near-matches, no "close enough" custom types, no semantic judgement. If no type has the inward description "is caused by", skip step 3a and take the fallback in step 3b.

   🔴 **Never substitute another type.** `Blocks`, `Duplicates`, `caused` and `Clones` mean specific, different things and must never stand in for causation. `Relates` is used **only** on the fallback path in 3b, and **only** alongside the comment that records the actual direction.

3a. **Primary path — an "is caused by" link type EXISTS.** For each remaining key, call `createIssueLink` with the **bug as the inward issue** (`bug is caused by <originating key>`) using the type resolved in step 2, then **verify** the link landed (re-read the bug's issue links). This is the ONLY path taken whenever "is caused by" is available: no `Relates` link is created and no explanatory comment is posted.

3b. **Fallback when no "is caused by" link type exists — generic link on `Relates to` + comment, BOTH, AUTOMATIC (no prompt).** Do NOT stop and do NOT ask the user to link manually. Do both of the following, in this order:

   **1 Link generically** — `createIssueLink` using the instance's general-association type (`Relates to` only). This makes the originating ticket visible and navigable from the bug's **Linked issues** panel, which a comment alone cannot do. ⚠️ `Relates` is **symmetric** — it carries no direction, so on its own it does NOT express "is caused by". It is a navigation aid only; is what records the actual relationship.

   **2 Comment the real relationship** — `addCommentToJiraIssue` on the bug. This comment is the **authoritative record of causation** whenever ① is a generic link. Keep it exactly this plain — formal, no emoji, no decoration:

   ```markdown
   **Is caused by**: [PROJ-102](<site-base-url>/browse/PROJ-102), [PROJ-456](<site-base-url>/browse/PROJ-456)

   The "is caused by" link type is not available on this Jira instance, so this defect has
   been linked to the above work item(s) as "relates to" instead. The direction of causation
   is recorded here: this defect is caused by the work item(s) listed above.

   Traced from the commit that introduced the defective line(s).
   ```

   Verify BOTH the link and the comment landed. In audit.md, log that the fallback path was used, which generic type was chosen, **the full list of link types the instance actually returned** (so an admin can see what's missing), and the same evidence chain as a real causal link.

   🔴 The generic link is **only ever** created on this fallback path, and **never without** the comment — a bare `Relates` link would silently lose the direction of causation. If the comment fails to post, remove the generic link (or, if removal fails, log the inconsistency prominently). If the instance has no general-association type either, post the comment alone.

   In the Step 5 summary, tell the user that adding an **"is caused by"** link type to the instance (Jira admin → Issues → Issue linking) would make the relationship queryable in JQL (`issueLinkType = "is caused by"`) — which the fallback path cannot provide.
4. Log every created link in audit.md with the complete evidence chain: `file:line` → introducing commit SHA → PR → matched source (`pr-title` / `commit-subject` / `branch`) → originating key → link type used. Log failures and skips with the same detail.
5. Announce the created links in the Step 5 completion summary.

### 5d. Approval

Present the Impact Analysis summary (including the Provenance Verdict table and any links created in 5c) and **wait for explicit approval** before proceeding. Log the response verbatim.

## Step 6 — Single Story (replaces User Stories + Dependency Graph)

1. Write **exactly ONE story** to `aipdlc-docs/inception/user-stories/stories.md`, derived from the ticket + requirements + impact analysis: story ID `1.1`, title = the fix, acceptance criteria = defect resolved + regression-safe (from the ticket's expected behavior). Do NOT ask team size, do NOT generate personas beyond what the ticket implies, do NOT ask about pushing to Jira (the ticket exists — no new issue is ever created), do NOT create `dependency-graph.yml`.
2. Populate the Story Tracker in `aipdlc-state.md` with the single row:
   | Story | Title | Requires | Jira | Status | Start | End | Recorded |
   |-------|-------|----------|------|--------|-------|-----|----------|
   | 1.1 | [Fix title] | none | PROJ-123 | 🟢 Ready for Development | | | [timestamp] |
   The Jira column is the **existing defect ticket** — the Jira Sync Rule applies to it at every status change.
3. **Wait for explicit approval** of the story; log the response verbatim.

## Step 7 — Workflow Planning (as-is)

Execute `inception/workflow-planning.md`: determine which Construction design stages EXECUTE/SKIP for this fix (most bugs skip most design stages), generate the execution plan + visualization (validate Mermaid), and **wait for explicit approval**.

## Step 8 — Construction Design Stages (CONDITIONAL, as-is)

Run the system-level design stages the plan selected (Functional Design → NFR Requirements → NFR Design → Infrastructure Design), each per its rule file with its standardized 2-option completion message and approval gate. Scope each to the bug-brief + impact analysis.

## Step 9 — 🛑 SDET HANDOFF BREAK → then continue into `bug-fix-implement`

After the design stages complete (or are all skipped), mark in `aipdlc-state.md`: `Design complete — awaiting bug-fix-implement`. Log in audit.md.

**This is a deliberate BREAK in the flow.** The analysis + design artifacts are everything the SDET needs, and the SDET must not have to wait for the fix. So before the fix is built:

1. **Commit + push the analysis and design artifacts on the bug branch (automatic — this is what unblocks SDET)**: stage `aipdlc-docs/inception/**` (bug-brief, requirements, impact analysis, the single story), `aipdlc-docs/construction/design/**`, the updated `aipdlc-state.md` and `audit.md`; commit on the bug branch with an `AI-PDLC-Version: [N]` trailer (`[N]` read live from `CLAUDE.md`); push to origin. Announce the commit hash + pushed branch and log both in audit.md. 🔴 If the push fails, say so explicitly and tell the user to push manually — **the SDET cannot start until this branch is on origin**. Still no `[BUG]` PR here.
2. Present the break message below and **block on its yes/no**.

```markdown
# ✅ Bug Analysis Done — Design Artifacts Pushed

🐞 **Ticket**: [JIRA-ID] — [title]  ([ai-generated-defect label applied / human-origin / undetermined])
🔗 **Caused by**: [PROJ-102, PROJ-456 — linked in Jira / none resolvable]
📍 **Impact**: [N] files identified in aipdlc-docs/inception/impact-analysis.md
🧩 Design stages: [list which ran vs were skipped]
🌿 Branch: bug/[JIRA-ID]-[title] (cut from [base branch]) — analysis + design **committed and pushed** ([commit hash])

> **🧪 <u>**SDET — start NOW, in parallel. The fix does not have to exist.**</u>**
> 1️⃣  `git fetch origin && git checkout bug/[JIRA-ID]-[title] && git pull --ff-only`
> 2️⃣  Type **`/sdet-implement [JIRA-ID]`**
>     It cuts `sdet/[JIRA-ID]-[title]` from this branch, writes the MANUAL test steps to
>     `aipdlc-docs/tests/[JIRA-ID]-[title]/` from the ticket's acceptance criteria, and raises its
>     own PR back into `bug/[JIRA-ID]-[title]` — so the test docs ride the `[BUG]` PR into [base branch].

> **🔧 <u>**DEV — continue to the fix implementation**</u>**
> ❓ **Continue to bug fix implementation now? (yes / no)**
> **yes** → baseline regression → fix plan (🚧 GATE 2 — your approval) → fix + unit tests (≥90%
>           coverage) → FULL regression → auto code review (🚧 GATE 3) → `[BUG]` PR to [base branch]
>           → auto PR review → then STOP (the cycle archive is MANUAL — you run `archive-epic`
>           after the SDET test-plan PR merges into the bug branch).
> **no**  → I halt here; the state is saved. Resume any time with `ticket-implement [JIRA-ID]`
>           (or `bug-fix-implement`) and it picks up at the fix.

🔴 Use `/sdet-implement` and the keywords EXACTLY as shown — do not describe what you want in your
   own words. Any other phrasing is not a framework trigger and the workflow will not advance.
```

3. **Block until the user answers.** Log the raw answer in audit.md.
   - On **no** — halt here. The break is the end of the run; say nothing further.
   - On **yes** — read `workflows/bug-fix-implement.md` and follow it exactly from its Step 1, in the same session, as if the user had typed `bug-fix-implement`. **🚧 GATE 2** (fix-plan approval, its Step 4) remains the user's control point before any code is written, and **🚧 GATE 3** (post-code-review Approve / Remediate, Step 8) before anything is committed, pushed, or PR'd.

Substitute every placeholder (`[JIRA-ID]`, `[base branch]`, `[commit hash]`) with real values — never ship a placeholder to the user.

---

## Critical Rules
- 🔴 EVERY audit entry carries the `**JIRA TICKET**:` field.
- 🔴 Step 9 is a **BREAK, not a stop-and-wait-for-a-keyword**: ALWAYS commit + push the analysis/design artifacts on the bug branch FIRST (the SDET's `/sdet-implement` needs them on origin), present the SDET handoff, then ask the yes/no. On **yes** continuation into `bug-fix-implement` happens in the same session — no second keyword. On **no**, halt with state saved. The yes/no is **flow control, deliberately unnumbered** — never write "GATE" into its audit heading. **GATE 2** (fix-plan approval) inside `bug-fix-implement` is the user's gate before code is written; **GATE 3** (post-review Approve / Remediate) is the gate before commit/push/PR.
- 🔴 The Step 9 break NEVER blocks the SDET on the dev: the SDET's `/sdet-implement [JIRA-ID]` run is independent of the yes/no answer and of the fix existing at all.
- 🔴 This workflow owns **NO numbered gate** — its own approvals (requirements, impact analysis, story, workflow planning) are stage approvals; NEVER write "GATE" into an audit heading from this file. The numbered gates (GATE 2, GATE 3) belong to `bug-fix-implement`, and there is no GATE 1 in the bug flow.
- 🔴 ONE branch (`bug/...`), ONE story, NO dependency graph, NO new Jira issues, NO epic branch, NO Parent-Epic sync.
- 🔴 NO PR at requirements approval — the single `[BUG]` PR is raised by `bug-fix-implement` after review approval.
- 🔴 AI-origin labeling is evidence-based, **line-level** (introducing commit of the defective line(s), per `agents/defect-provenance-analyst.md`), and confirm-first: "ai-generated" PR label OR Claude co-author trailer OR `AI-PDLC-Version:` trailer; "undetermined" is never labeled.
- 🔴 The **"is caused by" link** to the originating ticket (Step 5c) is created **automatically — no confirmation** — for every originating key the analyst resolves on positive evidence, whether the defective line was AI-generated or human-written. The originating ticket may be a **story, a bug, or an enhancement** (all three producers stamp their Jira key on the commit subject, PR title, and branch). Never link on a guessed key, never self-link, and never guess the Jira link type — resolve it via `getIssueLinkTypes` at runtime. If the instance has no causal ("is caused by") type, fall back automatically to a generic `Relates` link **plus** a comment recording the direction — both, never the bare link alone.
- 🔴 The defect ticket is NEVER transitioned to "Ready for Testing" by this flow 
- 🔴 Security Baseline extension always applies; other extensions per their recorded opt-ins.
