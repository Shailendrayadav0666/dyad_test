# AI-PDLC

**AI-PDLC** is an adaptive, AI-driven software development workflow framework. It takes you from a **product idea → a refined Jira Epic → requirements → a finished, reviewed product** — with a human approval at every stage and a complete audit trail.

---

## Table of Contents

1. [How It Works — The Big Picture](#how-it-works--the-big-picture)
2. [Prerequisites](#prerequisites)
3. [Usage](#usage)
4. [Context Project — feeding curated context](#context-project)
5. [Resumable Sessions](#resumable-sessions)
6. [The End-to-End Journey](#the-end-to-end-journey)
7. [The Bug-Fix Journey](#the-bug-fix-journey)
8. [The Enhancement Journey](#the-enhancement-journey)
9. [SDET Operating Guide](#sdet-operating-guide)
10. [Dependency Graph](#dependency-graph)
11. [Keyword Workflows](#keyword-workflows)
12. [Claude Code Skills](#claude-code-skills)
13. [Framework Distribution — auto-install & auto-update AI-PDLC in any repo](#framework-distribution--auto-install--auto-update-ai-pdlc-in-any-repo)
14. [Agents](#agents)

---

## How It Works — The Big Picture

```
                            YOUR RAW PRODUCT IDEA
                                     │
                                     ▼
              ┌─────────────────────────────────────────────┐
              │            SKILL: intent-intake             │
              │                                             │
              │  Captures the idea as a lightweight intent  │
              │  (outcome, KPI, scope, constraints) and     │
              │  pushes it to Jira                          │
              └─────────────────────────────────────────────┘
                                     │
                                     ▼
                 OUTPUT: Jira Epic — baseline (e.g. PROJ-42)
                                     │
                                     ▼
              ┌─────────────────────────────────────────────┐
              │          SKILL: intent-refinement           │
              │                                             │
              │  Elaborates the Epic with engineers:        │
              │  measurable success criteria, scope,        │
              │  constraints, domain model, NFRs, risks     │
              └─────────────────────────────────────────────┘
                                     │
                                     ▼
            OUTPUT: Updates the Jira Epic making it fully detailed & verifiable
                                     │
                                     ▼
              ┌─────────────────────────────────────────────┐
              │   IN CLAUDE CODE (your project), TYPE:      │
              │                                             │
              │      Using AI-PDLC, <jira-epic-url>         │
              └─────────────────────────────────────────────┘
                                     │
                                     ▼
              ┌─────────────────────────────────────────────┐
              │             AI-PDLC LIFECYCLE               │
              │                                             │
              │   🔵 INCEPTION  →  🟢 CONSTRUCTION          │
              │                                             │
              │                                             │
              │                                             │
              │  🧰 SUPPORTING SKILLS                       │
              │     story-audit · sdet-implement ·          │
              │     code-security-review ·                  │
              │     raise-defect · pr-generator · pr-review │
              │     sdet-list-work ·                        │
              │     reverse-engineering-root ·              │
              │     archive-epic · stitch-delta             │
              └─────────────────────────────────────────────┘
                                     │
                                     ▼
                         FINISHED, REVIEWED PRODUCT 
```

Three moving parts:

| Part | Where | What it does |
|------|-------|--------------|
| **`CLAUDE.md`** | project root | The master workflow. Claude Code reads it automatically and it orchestrates every phase, gate, and approval. |
| **`.aipdlc-rule-details/`** | project root | The detailed rulebook: step-by-step instructions for every stage, keyword workflow, agent, and extension. Loaded on demand to save context. |
| **`.claude/skills/`** | project root | Standalone Claude Code skills (intent intake/refinement, story/epic audit, SDET build-and-test, PR generator/review, defect raising, SDET sign-off, security review, reverse engineering, archiving/stitching) that plug into the lifecycle before, during, and after development. |

The workflow is **adaptive**: the AI assesses your request, your workspace (greenfield vs. brownfield), and the complexity/risk of the change, then runs only the stages that add value — at minimal, standard, or comprehensive depth. You stay in control: **every stage requires your explicit approval**, and every interaction is logged verbatim in an audit trail.


---


## Prerequisites

Install and configure the following **before** using the framework into your project:

#### 1. Claude Code

The framework runs entirely inside Claude Code (CLI, desktop app, or IDE extension).

#### 2. GitHub CLI (`gh`)

Used to raise, review, and check the merge state of Pull Requests.

```bash
# macOS
brew install gh

# Windows
winget install --id GitHub.cli

# Linux (Debian/Ubuntu)
sudo apt install gh
```

- Full install doc: <https://github.com/cli/cli#installation>
- **Authenticate after installing**: `gh auth login` (choose GitHub.com → HTTPS → login via browser).
- Verify: `gh auth status` should show you as logged in with `repo` access.

#### 3. Atlassian (Jira) MCP connection

The framework talks to Jira through the **Atlassian MCP server** 

**Claude Code**

Run the following command:

```bash
claude mcp add --transport http atlassian https://mcp.atlassian.com/v1/mcp/authv2
```

Then, inside a Claude Code session, run `/mcp` and complete the OAuth login to your Atlassian site.

**Claude Desktop**

1. Open **Claude Desktop**.
2. Go to **Settings → Extensions**.
3. Select **Browse extensions**, then select **Plugins**.
4. Search for **Atlassian** and install it.

- Atlassian's official server: <https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/>
- Claude Code MCP setup docs: <https://docs.anthropic.com/en/docs/claude-code/mcp>
- Verify: in a Claude Code session, by running `/mcp`

#### 4. Disable Claude Code's built-in `code-review` skill

Turn **off** Claude Code's built-in `code-review` skill.

1. Open your **user-profile** settings file: `~/.claude/settings.json` (Eg: on Windows: `C:\Users\<you>\.claude\settings.json`).
2. Add the following top-level key (merge it into the existing JSON):

```json
"skillOverrides": {
    "code-review": "off"
}
```

3. Save the file and restart Claude Code so the override takes effect.

---

## Usage

Start any software development project by stating your intent in the chat, beginning with the phrase **"Using AI-PDLC, ..."** — ideally including the **Jira Epic link** produced by the intent skills:

```
Using AI-PDLC, https://yoursite.atlassian.net/browse/PROJ-42
```

From there:

1. **The AI-PDLC workflow automatically activates** and guides you from there — it detects your workspace, fetches the Epic (if given), and plans the stages.
2. **Answer the structured questions** AI-PDLC asks you. Questions come in multiple-choice format (A, B, C, D…) with an "Other" option — answer inline with the `[Answer]:` tag.
3. **Carefully review every plan the AI generates.** Provide your oversight and validation — this is a team effort; involve the relevant stakeholders at each phase.
4. **Review the execution plan** to see which stages will run (and at what depth). You can override the recommendation and add/remove stages.
5. **Review the artifacts and approve each stage** to maintain control — no stage proceeds without your explicit approval.
6. **All artifacts are generated in the `aipdlc-docs/` directory** — application code goes in your workspace root, documentation never mixes with it.

Sessions are resumable: state lives in `aipdlc-docs/aipdlc-state.md`, so you can close the chat and pick up exactly where you left off in a fresh session.

---

## Context Project

**What it's for.** A `context-project/` folder at the repo root holding human-authored knowledge about your **current project** — how the system works, where things live, what each module does. Files like `interview.md` explain the existing behavior and layout so the AI understands the codebase. This is *context about what already exists*, **not** requirements for the new work.

**How empty `context-project/` folder is created.** Brownfield only (it describes existing code, so greenfield projects skip it). Made automatically at the repo root the first time reverse engineering runs, and Workspace Detection ensures it exists on brownfield runs. If it already exists, it's reused as-is — never overwritten. You must manually add the relevant documents (eg: interview.md) to this folder and for more information on how to add them, please refer to the section below.

**How to add docs.** One subfolder per module, named **exactly** after the module in your repo; drop that module's explainer docs inside.

```
context-project/
└── ALIX.BMS/            ← named exactly after the module
    └── interview.md     ← how ALIX.BMS works, where things live
```

**How it's used.** At workflow start AI-PDLC asks: *"Are there any context-project artifacts I should use for this task?"*
- **Yes** → paste the exact file/folder path (e.g. `context-project/ALIX.BMS/interview.md`). Only that path is read — used as background context when building `requirements.md` and the plan.
- **No** → the folder is ignored.

The answer is recorded in `aipdlc-docs/aipdlc-state.md`, so a resumed session reuses it without asking again.

---

## Resumable Sessions

**AI-PDLC is fully resumable — no session state is ever locked inside a single chat.**

Two files on disk are the single source of truth:

- **`aipdlc-docs/aipdlc-state.md`**
- **`aipdlc-docs/audit.md`** 

Because both files reside in the repository, the AI-PDLC framework retains its state even after a Claude session is closed and reopened, ensuring no loss of context or progress. This makes the workflow durable across interruptions, machine changes, and team handoffs, while maintaining a comprehensive record of all actions.

---

## The End-to-End Journey

A first-time user's complete path, from idea to merged PR:

### Step 1 — Capture the idea: `intent-intake` (skill)

You have a raw idea. Invoke the skill `intent-intake` via **`/intent-intake`**. The skill asks whether you have a document (PRD, research notes, Confluence page) or will explain in plain English, gathers exactly **six baseline fields** (outcome, KPI, success signal, out-of-scope, constraints, confidence + unknowns), and — after your confirmation — **pushes a Jira Epic** labeled `intent-intake`. Fast and deliberately light: no deep elaboration here.

**Output: a Jira Epic**

### Step 2 — Deepen it: `intent-refinement` (skill)

Invoke the skill `intent-refinement` via **`/intent-refinement`** and give the Epic key. The skill fetches the Epic, assesses gaps, runs focused elaboration question batches (measurable success criteria with thresholds, explicit scope/out-of-scope, constraints, domain model, NFRs, risks), and — confirm-first — **updates the Epic in Jira** to full, verifiable detail with label `intent-refined`.

**Output: the same Epic, now fully detailed.**

### Step 3 — Start development: `Using AI-PDLC, <epic-url>`

Open Claude Code **in your project workspace** and type:

```
Using AI-PDLC, https://yoursite.atlassian.net/browse/PROJ-42
```

The workflow activates: it records the **Parent Epic** in `aipdlc-state.md`, fetches the Epic content into `aipdlc-docs/inception/requirements/epic-brief.md` (the brief that defines WHAT to build), and **automatically creates the Epic branch** (`epic/<EPIC-KEY>-<title>`, recorded with the base branch in `aipdlc-state.md`) — all subsequent work happens on this branch and on story branches cut from it. It then runs the **Inception phase** — requirements analysis (including **extension opt-ins**: the Security Baseline is always enforced; resiliency and property-based-testing rules are offered as opt-ins), user stories (with a team-size question and optional push to Jira, each story linked to the Parent Epic), the **Dependency Graph**, workflow planning, and (if needed) application design. After requirements approval, the inception artifacts are committed on the Epic branch and the **Epic PR into the base branch is raised** (via `pr-generator`).

### Step 4 — System-level design, then STOP

The **Construction phase** runs the conditional system-level design stages (Functional Design, NFR Requirements, NFR Design, Infrastructure Design). After the design stages complete (or are skipped), the workflow **commits and pushes the design artifacts on the epic branch** (that push is what unblocks SDET) and then **hard-stops** at the Development Handoff — code generation never starts automatically. The handoff names both next moves: DEV pulls the epic branch and types `dev-implement` (once per story); SDET pulls the same branch and types `/sdet-implement <story>` (once per story, in parallel, never waiting for dev code).

### Step 5 — Build story by story: `dev-implement`

Type **`dev-implement`** in the Claude Code chat. It shows the **current ready stories**, you pick one (by ID or Jira key), and it runs the full per-story pipeline:

> ⚠️ **Why not parallel in one session?** Stories are built **sequentially** in a session — just type the workflow name and a story number, one story at a time. This is due to **branching**: every story branch is cut from the Epic branch, and prerequisites must be merged into it first. To develop stories **in parallel**, open a **new folder/clone of the same repo**, check the **Dependency Graph**, and run `dev-implement` there on an **independent story** (no shared `requires`).

1. **Doability Checkpoint** — every `requires` prerequisite must be done: its PR confirmed **merged** by a live `gh pr view` check. Blocked stories are rejected with the list of what's outstanding, and the run stops.
2. **Story → In Development** — automatic: Story Tracker updated, Jira transitioned automatically.
3. **Story Branch Checkpoint** — all prerequisite story PRs must already be **merged into the Epic branch**; then the story branch (`story/N.M-<title>`) is cut **from the Epic branch, never base**.
4. **Baseline regression run** — automatic: the *entire* repo test suite runs **on the freshly cut story branch, before any code is generated**. The output of this run is recorded in `baseline-regression.log`.
5. **Plan → your approval → code generation** per your chosen Development Approach.
6. **Unit Test + Coverage** — tests are generated and run, iterating until **≥ 90% coverage** on new code. **Proof artifacts are captured** to `aipdlc-docs/construction/code/unit-test-evidence/story-N.M/` — the raw runner output (`unit-test-run.log`), the coverage tool's **mandatory machine-readable report** (`coverage-report.*` — lcov/xml/json/HTML), and an `evidence-manifest.md`. 
7. **Full regression** — automatic: the entire suite runs again and is diffed against the baseline. **Any NEW failure was broken by this story, so this story fixes it** in the same run.
8. **AUTO code review** (always runs) — verifies each acceptance criterion, reports Blocker / High findings in a versioned report; you approve or run the **remediate loop**.
9. **Commit + story PR** — the story commit carries an **`AI-PDLC-Version` trailer**, then `pr-generator` opens the **story PR into the Epic branch** (labeled `aipdlc-v[N]` alongside `ai-generated`), followed by an **AUTO `pr-review`** pass. The PR URL is stored in the Story Tracker and the story **stays `In Development`**.

Merge the story PR into the Epic branch, then type `dev-implement` again for the next story — it lets you pick the next one (its branch cuts from the Epic branch, so a prerequisite's PR must be merged first, which the Doability Checkpoint verifies live). Repeat until all stories are done.

### Step 6 — Verify and ship

- **Build & Test is SDET's, not a stage here** — it is not a Construction stage at epic or story level. SDET runs `/sdet-implement <story-JIRA-ID>` per story, in parallel with development (the skill automatically creates a `sdet/…` branch from the epic branch + automatic PR raised into the epic branch), then `/sdet-list-work` (local **Option B**) on the epic branch (base branch for bug/enhancement cycles) to approve or reject each merged story — **per story, as each PR merges**.
- **`code-review`** (workflow) produces a read-only review report per story or for all stories — a review already auto-runs inside `dev-implement`, so invoke this standalone for re-reviews or an all-stories pass.
- **`remediate`** (workflow) fixes the findings from a chosen review report.
- Invoke the skill `code-security-review` via **`/code-security-review`** to audit the codebase against security baseline rules.
- Invoke the skill `raise-defect` via **`/raise-defect`** to let SDET file well-formed bugs into Jira.
- Invoke the skill `pr-generator` via **`/pr-generator`** to raise a PR. It runs **standalone** too: trigger it directly (e.g. "raise a PR") and it asks only which branch to target, then raises the PR from your current branch into it — with the `ai-generated` and `aipdlc-N` labels — for **any** branch → branch (N → M), not just epic/enhancement/bug flows. An ordinary standalone PR takes a lightweight fast path (diff-only summary, no Story Tracker/audit lookups); a standalone epic/bug/enh → base PR keeps the full flow, and an **Epic → Base** PR auto-triggers `archive-epic` (for `[BUG]`/`[ENH]` → Base PRs the archive is **manual** — pr-generator only prints a reminder).
- Invoke the skill `pr-review` via **`/pr-review`** to review an open PR with inline, severity-tagged comments.

### Step 7 — Close the EPIC release cycle: `archive-epic` + `stitch-delta`

When the epic is done (all story PRs merged and SDET has approved every story to Ready for testing via `/sdet-list-work`, local **Option B**), invoke **`/pr-generator`** on the epic branch: it raises/updates the Epic → Base PR and **auto-triggers `archive-epic`**, which generates the epic's **delta** reverse engineering artifacts (epic-namespaced, so parallel epics never conflict) and archives the complete `aipdlc-docs` into `aipdlc-archives/epics/<EPIC-ID>-<epic-name>/`. After the epic PR merges, checkout the base branch and invoke **`/stitch-delta`**: it applies all pending deltas onto the root reverse engineering docs in merge order, tracked in the `stitch-epic.md` ledger so nothing is ever stitched twice.

---

## The Bug-Fix Journey

**Every ticket starts the same way** — type **`ticket-implement <JIRA-ID>`**. The router fetches the ticket and asks **one question** with exactly two inline options: *A) Bug fix* or *B) Enhancement* (it shows a recommendation from the issue type/labels, but your answer decides). Answer **A** and it runs the bug flow below. If state already records this ticket, the router skips the question and resumes where you left off.

```
ticket-implement PROJ-123   →   "What is this ticket about?  A) Bug   B) Enhancement"   →   A
```

### Step 1 — Analyze (bug flow)

An Inception runs on **one branch** — `bug/<JIRA-ID>-<title>`, automatically cut from the base branch (no epic branch, no story branches):

1. **Ticket capture** — the ticket is fetched into `bug-brief.md`; state records `Workflow Type: bug`.
2. **Workspace detection + reverse engineering** — existing RE artifacts are reused; if none exist, RE runs exactly as in the brownfield flow.
3. **Requirements analysis** — generates `requirements.md` from the ticket, scoped to the reported bug.
4. **Impact Analysis + AI-Origin Detection (line-level)** — the affected files and defective lines are identified (`impact-analysis.md`, which later drives the fix plan), and the **Defect Provenance Analyst** agent traces each defective line — not just the file's last change — to the commit that *introduced* it (`git blame` / `git log -L`, following moves and skipping cosmetic commits; omission bugs attribute to the enclosing block). If that introducing change was AI-generated (PR carries the **"ai-generated"** label, the commit has a Claude co-author trailer, or an `AI-PDLC-Version:` trailer), the label **`ai-generated-defect`** is added to the Jira ticket (confirm-first, evidence logged in the audit trail). The bug is also linked to the story/stories that caused the issue on JIRA.
5. **One story** is written from the ticket itself — no team-size question, no Jira push (the ticket already exists), **no Dependency Graph**.
6. Workflow planning + conditional design stages (most are skipped for typical bugs), then the Mandatory stop: the analysis + design artifacts are committed and **pushed** on the bug branch (that push is what unblocks SDET), the SDET is told to pull that branch and run **`/sdet-implement <JIRA-ID>`** in parallel, and the dev is asked **"Continue to bug fix implementation? (yes / no)"**. On **yes** the fix (Step 2) runs in the same session — no second keyword; on **no** the flow halts with state saved and SDET carries on regardless.

#### How the bug gets linked to what caused it

As you can see in the fourth point of Step 1, AI-PDLC automatically links the defect to the ticket(s) that introduced it.

The Work link type is **resolved at runtime** from your Jira board and matched on the *inward description*. Exactly one type qualifies — **"is caused by"**.

| Your Jira board has… | What AI-PDLC does |
|----------------------|-------------------|
| **"is caused by"** | Creates `Bug — is caused by → PROJ-102` under **Linked work items**. |
| **No "is caused by"** | Falls back to a **"relates to"** link **plus** one plain fallback comment on the bug recording the real direction. |

The fallback comment:

```
Is caused by: PROJ-102, PROJ-456

The "is caused by" link type is not available on this Jira instance, so this defect has
been linked to the above work item(s) as "relates to" instead. The direction of causation
is recorded here: this defect is caused by the work item(s) listed above.

Traced from the commit that introduced the defective line(s).
``` 

> **Recommended — add an "is caused by" Work link type to your Jira board.**

### Step 2 — Fix: `bug-fix-implement` (same session, after the mandatory stop)

Runs right after the Step 1 mandatory stop on the dev's **yes**, on the same bug branch (type **`bug-fix-implement`** only to resume a session that answered "no" or ended after analysis on step 1):

1. **Ticket → In Development** (automatic).
2. **Baseline regression run** — the *entire* repo test suite runs **before any change**, recording pre-existing failures so the fix is never blamed for (or hides) what was already broken.
3. **Fix plan → your approval → the fix**, with unit tests that **validate the fix** ensuring ≥ 90% coverage on changed code.
4. **Full regression** — the entire suite runs again and is compared against the baseline captureed before: **only new failures block and get fixed**; all output is logged in `bug-<JIRA-ID>-summary.md`.
5. **AUTO code review** → approve or remediate loop.
6. On approval: **`[BUG]` PR straight to the base branch** (via `pr-generator`), followed by an **AUTO `pr-review`** pass. Meanwhile SDET has been running **`/sdet-implement PROJ-123`** on the bug branch since the design stages finished — its `sdet/…` PR merges into the bug branch, so the test docs reside in this same `[BUG]` PR into base branch.
7. **The ticket stays In Development** — it is never moved forward by this workflow. After the `[BUG]` PR merges into the base branch, SDET **invokes `/sdet-list-work`** and picks local **Option B** on the base branch, tests the merged fix by executing manual test steps generated by `/sdet-implement`, and answers one prompt — `<Jira key> approve` or `<Jira key> reject`. Approve → comment `SDET approved the story` + `sdet-approved` label, Jira Ticket → Ready for Testing; reject → comment `SDET rejected the story` + `sdet-rejected` label, ticket stays In Development (SDET manually log the bug in Jira via `/raise-defect`). 
8. **MANUAL archive (bug mode)** — 🔴 **not automatic**. Once the SDET's `/sdet-implement` test-plan PR have **merged into the bug branch** and all SDET work is done and commited to bug branch, pull that branch and invoke **`/archive-epic`** yourself — it generates the bug's delta RE artifacts and archives `aipdlc-docs` into `aipdlc-archives/bugs/<BUG-ID>-<name>/`. It must run **before** the `[BUG]` PR merges (its commit resides in the open PR).
   🔴 **SDET sign-off comes first, on the bug branch**: before the archive, SDET runs **`/sdet-list-work`** on `bug/<JIRA-ID>-…` — Option C to amend a test plan (commit + push it), Option B to approve and promote the ticket to 🧪 Ready for Testing. Exactly like epic cycles, and for the same reason: the sign-off + test-plan edits get captured in the archive. **`/sdet-list-work` never runs on the base branch.**
   After the `[BUG]` PR merges, the base branch has exactly **one** remaining action: **`/stitch-delta`** (applies the delta to the root RE docs — the final action of the cycle).

---

## The Enhancement Journey

For an existing Jira **Story/Task** that enhances the current system (not a defect — that's the bug flow).

**It starts exactly like the bug journey** — type **`ticket-implement <JIRA-ID>`**, and answer **B) Enhancement** to the router's one question. That runs the enhancement flow below.

```
ticket-implement PROJ-456   →   "What is this ticket about?  A) Bug   B) Enhancement"   →   B
```

### Single Enhancement flow 

An Inception runs on **one branch** — `enhancement/<JIRA-ID>-<title>`, automatically cut from the base branch (no epic branch, no story branches):

**Phase A — Analysis:**

1. **Ticket capture** — the ticket (Story/Task) is fetched into `enhancement-brief.md`; state records `Workflow Type: enhancement`. A Bug-type ticket triggers a warning to use `bug` fix flow instead.
2. **Workspace detection + enhancement branch** — the branch is created FIRST, before requirements; existing RE artifacts are reused, otherwise RE runs as in the brownfield flow.
3. **Requirements analysis** — generates `requirements.md` from the ticket, scoped to the requested enhancement.
4. **Impact Analysis (NO AI-Origin Detection)** — the affected files/components and blast radius are identified with `file:line` evidence (`impact-analysis.md`, which later drives the implementation plan).
5. **One story** is written from the ticket itself — no team-size question, no Jira push (the ticket already exists), **no Dependency Graph**.
6. Workflow planning + conditional design stages (small enhancements skip most), then the Mandatory stop: the analysis + design artifacts are committed and **pushed** on the enhancement branch (that push is what unblocks SDET), the SDET is told to pull that branch and run **`/sdet-implement <JIRA-ID>`** in parallel, and the dev is asked **"Ready to implement now? (yes / no)"** — on **no** it halts with state saved (re-invoking resumes at this checkpoint) and SDET carries on regardless; on **yes** it continues with the implementation plan and code generation in the SAME flow.

**Phase B — Implementation (after "yes"):**

1. **Ticket → In Development** (automatic) — the ticket is also assigned to you.
2. **Baseline regression run** — the *entire* repo test suite runs **before any change**, recording pre-existing failures.
3. **Implementation plan → your approval → the code**, with unit tests and ≥ 90% coverage on new/changed code.
4. **Full regression** — the entire suite runs again vs the baseline: **only new failures block and get fixed**; all output is logged in `enhancement-<JIRA-ID>-summary.md`.
5. **AUTO code review** → approve or remediate loop (same gates as `dev-implement`).
6. On approval: **`[ENH]` PR straight to the base branch** (via `pr-generator`), followed by an **AUTO `pr-review`** pass. Meanwhile SDET has been running **`/sdet-implement PROJ-456`** on the enhancement branch since the design stages finished — its `sdet/…` PR merges into the enhancement branch, so the test docs reside in this same `[ENH]` PR into base.
7. **The ticket stays In Development** — after the `[ENH]` PR merges, SDET **invokes `/sdet-list-work`** and picks local **Option B** on the base branch, tests the merged changes by executing manual test steps generated by `/sdet-implement`, and answers one prompt — `<Jira key> approve` or `<Jira key> reject`. Approve → comment `SDET approved the story` + `sdet-approved` label and Ticket → Ready for Testing; reject → comment `SDET rejected the story` + `sdet-rejected` label, ticket stays In Development (SDET manually log the bug in JIRA via `/raise-defect`).
8. **MANUAL archive (enhancement mode)** — 🔴 **not automatic**. Once the SDET's `/sdet-implement` test-plan PR have **merged into the enhancement branch** and  all SDET work is done and commited into the enhancement branch, pull that branch and invoke **`/archive-epic`** yourself — it generates the enhancement's delta RE artifacts and archives `aipdlc-docs` into `aipdlc-archives/enhancements/<ENH-ID>-<name>/`. It must run **before** the `[ENH]` PR merges (its commit resides in the open PR).
   🔴 **SDET sign-off comes first, on the enhancement branch**: before the archive, SDET runs **`/sdet-list-work`** on `enhancement/<JIRA-ID>-…` — Option C to amend a test plan (commit + push it), Option B to approve and promote the ticket to 🧪 Ready for Testing. Exactly like epic cycles, and for the same reason: the Story Tracker still exists there, and the sign-off + test-plan edits get captured in the archive. **`/sdet-list-work` never runs on the base branch.**
   After the `[ENH]` PR merges, the base branch has exactly **one** remaining action: **`/stitch-delta`** (applies the delta to the root RE docs — the final action of the cycle).

---

## SDET Operating Guide

This section is written for the SDET. It states what you are responsible for, where you do the work, and the exact order in which to do it. You use **two skills only**: `/sdet-implement`, `/raise-defect` and `/sdet-list-work`.

### Your responsibility

Build and Test belongs to you. Your work runs **in parallel with development**, not after it. You begin as soon as the design stages of Construction phase finish, which is well before any application code exists. Nothing you do at that point depends on the developer.


### Where you work

Both skills operate on the cycle's **integration branch**. Which branch that is depends on the type of work, and each skill resolves it for you from the project state file and announces it:

| Cycle type | Integration branch | Where the development pull requests merge |
|------------|--------------------|-------------------------------------------|
| Epic (greenfield or brownfield) | The epic branch, for example `epic/PROJ-50-checkout` | Each story's `[STORY]` pull request merges into the epic branch |
| Bug | The base branch, for example `Staging` | The single `[BUG]` pull request merges into the base branch |
| Enhancement | The base branch | The single `[ENH]` pull request merges into the base branch |

All of your generated documentation lives under `aipdlc-docs/tests/<STORY-JIRA-ID>-<title>/`, one folder per story.

### Step 1 — Author the test plan: `/sdet-implement`

**When to start.** The moment the workflow reaches its design handoff. At that point the framework commits and pushes the requirements and design artifacts to the integration branch specifically so that you can start; the message shown at that handoff names the branch and tells you to run this skill. On an epic you run the skill once per story; on a bug or enhancement you run it once for the ticket.

**What to do.**

1. Get on the integration branch and take the latest:

   ```
   git fetch origin
   git checkout <integration-branch>
   git pull --ff-only
   ```

2. Type the skill, naming the story or ticket:

   ```
   /sdet-implement PROJ-102
   ```

   A story number also works on an epic cycle, for example `/sdet-implement 1.2`. Invoking it with no argument makes the skill ask which story you mean.

**What the skill does.** It cuts its own branch, `sdet/<JIRA-ID>-<title>`, from the integration branch. It reads the story's acceptance criteria from Jira, together with the requirements and the construction design artifacts, and decides which test plans apply — integration, end-to-end, API, contract, security, performance, and accessibility. It writes each applicable plan as numbered **manual test steps** into `aipdlc-docs/tests/<STORY-JIRA-ID>-<title>/`, with an index file summarising the plans and the coverage. Every test case names the acceptance criterion it covers, and every acceptance criterion must be covered; that coverage check is a blocking gate.

**What you are asked.** Before any file is written, the skill confirms which test plans it considers applicable. When the plans are complete, it presents a summary and asks you to approve them or request changes. If you request changes, it revises and asks again. Once approved, it asks permission before pushing the branch and opening its pull request.

**What you get.** A pull request titled `[TEST][<JIRA-ID>] Build and Test — <story title>`, raised from `sdet/<JIRA-ID>-<title>` back into the integration branch, labelled `ai-generated` and `aipdlc-v<version>`. On a bug or enhancement cycle this means your test documentation travels into the base branch on the same `[BUG]` or `[ENH]` pull request as the fix. Parallel runs by different SDET and Developer do not conflict, because these files are configured to merge by appending, .gitattributes.

**What this skill deliberately does not do.** It writes no automated test scripts, executes no tests, changes no application code, and never changes a story's status in the tracker or in Jira.

**After the run.** Merge your test-documentation pull request into the integration branch. Do not execute the steps yet — see Step 2.

### Step 2 — Execute the steps, then sign off: `/sdet-list-work`

**When to start.** Only after the developer's pull request for that story has **merged** into the integration branch. Until then there is nothing to test. On an epic you do this per story as each story's pull request merges; you do not wait for the whole epic.

**What to do.**

1. Get on the integration branch and take the latest, as in Step 1. The skill resolves the correct branch itself, tells you which one it expects, and asks before switching.

2. Type the skill:

   ```
   /sdet-list-work
   ```

3. Choose one of three local actions when prompted:

   | Option | Purpose | What it changes |
   |--------|---------|-----------------|
   | A | List the stories whose development pull request has merged and which are still In Development. Status is read live from the Jira board rather than trusted from the local state file. | Nothing |
   | B | Record your sign-off decision after you have tested the merged work. | The Story Tracker, Jira, and the audit log |
   | C | Request a change to a test plan that `/sdet-implement` already generated — add or adjust a manual test case, traced to an acceptance criterion. | The test plan files only |

4. **Build the system and execute the test steps.** Option A gives you the list of stories that are merged and testable, and names each one's test-plan folder. Build and run the system locally from the integration branch, then execute the manual test steps in `aipdlc-docs/tests/<JIRA-ID>-<title>/`.

5. **Record the decision with Option B.** The skill shows the merged, testable items and asks a single question. You answer with one decision per item, for example `1.1 approve, PROJ-103 reject`.

   - **Approve** adds the Jira comment `SDET approved the story`, applies the `sdet-approved` label, and transitions the item from In Development to **Ready for Testing** in both the Story Tracker and Jira.
   - **Reject** adds the Jira comment `SDET rejected the story`, applies the `sdet-rejected` label, and deliberately leaves the item **In Development** for the developer to address. The skill then tells you to log the finding as a tracked Jira defect manually by a raise-defect skill.

   On an epic cycle, once every story has been approved the skill offers, with your confirmation, to move the parent epic to Ready for Testing.

**A note on Option C.** Option C edits the test-plan files in your working tree. It does not commit, push, or open a pull request for you. Commit and push that change yourself so it reaches the branch;

### The order of work for one story

1. The workflow reaches its design handoff and pushes the requirements and design artifacts to the integration branch.
2. You pull that branch and run `/sdet-implement <JIRA-ID>`. You review and approve the generated plans, then allow the push and the pull request.
3. You merge your test-documentation pull request into the integration branch.
4. You repeat steps 2 and 3 for the next story while the developer continues to build. Development and Build and Test proceed independently.
5. The developer's pull request for the story merges into the integration branch.
6. You run `/sdet-list-work` on integration branch and pick Option A to confirm what has merged.
7. You build the system locally from the integration branch and execute the manual test steps generated by `/sdet-implement`.
8. You run `/sdet-list-work` again and pick Option B to approve or reject a story. Approved stories move to Ready for Testing; rejected items stay In Development and you manually log a defect by `/raise-defect` skill.


---

## Dependency Graph

The Dependency Graph stage is what keeps story development **correctly ordered** in AI-PDLC.

**The idea**: every story gets a `requires` list — the stories that must be fully done before it can start. From those dependencies, the graph shows at any moment which stories are **ready** (no unfinished prerequisites) and which are blocked by what.

At each `dev-implement` invocation, the workflow reads the graph and shows the currently ready stories; you pick the next one to build. Two checkpoints enforce the graph: the **Doability Checkpoint** blocks any story whose `requires` prerequisites aren't done — each one must already be `Ready for testing`, or have its PR confirmed merged by a live check — and the **Story Branch Checkpoint** additionally requires all prerequisite story PRs to be merged into the Epic branch before the new story branch is cut. Stories are developed **one at a time per epic** — each story branch cuts from the Epic branch after the previous story's PR has merged.

---

## Keyword Workflows

These are typed directly in chat (any session — they self-load their rules and can resume from state):

### `dev-implement` — build one story

Turns one user story into working code. It shows you which stories are ready to build, you pick one, you approve its implementation plan, and it writes the code — updating the story's status locally and in Jira as it goes.

> ⚠️ Sequential per session (because of branching): one story at a time. For parallel work, use a new folder/clone of the same repo and pick an independent story from the Dependency Graph.

### `code-review` — review the code

Reviews the code of one story (or all stories) against what the story promised and general quality standards. It only reads and reports — it never changes code.

### `remediate` — fix what the review found

Takes a review report and fixes the issues in it, then marks them resolved in the report. If serious issues were fixed, manually run `code-review` again to confirm.

### `ticket-implement <JIRA-ID>` — one front door for bug OR enhancement

This router fetches the ticket, asks **one question** — *"What is this ticket about? A) Bug fix B) Enhancement"* (with a recommendation from the issue type/labels; your answer decides) — then runs the required workflow.

---

## Claude Code Skills

Located in `.claude/skills/` — invoked by natural language or `/skill-name`.

| Skill | What it does |
|-------|--------------|
| **`intent-intake`** | The light front-door: turns a raw idea in natural language (or a PRD/doc/link) into a six-field baseline intent and **pushes it to Jira as an Epic**.  |
| **`intent-refinement`** | Fetches an existing Epic, runs structured elaboration batches until the intent is **verifiable** (measurable criteria + thresholds, scope, constraints, domain model, risks), and updates the Epic in Jira. |
| **`story-audit`** | Audits an existing Jira Story or Epic against the AI-PDLC quality bar: fetches the issue, applies the type-appropriate checklist, scores what's present vs. missing, and (opt-in) fills the gaps through targeted questions, updating the issue in Jira. |
| **`sdet-implement`** | SDET Build and Test (black-box), **per story, in parallel with development** — the dev's code does not need to exist, be built, or be merged, so SDET can start the moment the design stages finish. Run it as `/sdet-implement <JIRA-ID>` on the **epic branch** (epic cycles) or the **bug/enhancement branch** (ticket cycles), **as soon as the design stages of construction phase finish**: it cuts an **`sdet/<JIRA-ID>-<title>`** branch from that latest branch, reads the story's acceptance criteria (Jira), requirements and design artifacts — **never application source code** — decides which test plans apply (integration, E2E, API, contract, security, performance, accessibility) and writes them as **manual test steps** into `aipdlc-docs/tests/<story-JIRA-ID>-<title>/`, one folder per story, every test case traced to an acceptance criterion and every criterion covered. It then **commits and raises a PR back to that same branch** — labeled `ai-generated` + `aipdlc-v[N]` — logged in `audit.md`; `.gitattributes` merges these files by append so parallel SDET runs never conflict. One story per run. |
| **`code-security-review`** | Full-codebase audit against the 16 Security Baseline rules (SECURITY-01…16: encryption, headers, input validation, SSRF, uploads, access control, CSRF, JWT, credentials, sessions, supply chain, XXE, alerting, error handling, crypto standards). Findings by severity, dated report in `aipdlc-docs/code-security-reviews/`. |
| **`raise-defect`** | Interviews the SDET through a fixed field set — Title, Description, Severity, Environment Found, Discovery Activity (Components always `Default`, Associated Org always `All`) — then, after the SDET approves the drafted ticket, creates the Jira Bug labeled `bug`, `defect`, `ai-generated`, `ai-pdlc`, `aipdlc-v[N]`. The developer picks it up via `ticket-implement JIRA-TICKET-ID`. |
| **`pr-generator`** | Raises a GitHub PR from the current branch into a target branch, tagged with `ai-generated` and `aipdlc-N` labels and an `AI-PDLC Framework: vN` line in the body. In automatic workflow mode it grounds the summary in the **Story Tracker** and **audit trail** (never just the raw diff) and titles the PR with an **`[EPIC]`, `[STORY]`, `[BUG]` or `[ENH]`** prefix. **Can also be invoked standalone** (e.g. "/pr-generator") to open a PR from **any branch into any target branch** (N → M): it asks only which branch to target, then raises it with both labels.|
| **`sdet-list-work`** | Once on the integration branch (epic branch for epic cycles, base branch for bug/enhancement cycles), it asks a **local A/B/C menu**: **A) List** — reports what dev has merged (test these, using the `/sdet-implement` steps) vs what is still in development, status read **live from the Jira board**, writes nothing. **B) Approve/Reject** — the sign-off itself: pulls the latest, confirms each recorded PR's real merge state with `gh`, reports the same merged/in-development table, then SDET answers **one prompt with one decision per item** — `<story or Jira key> approve` / `<story or Jira key> reject`. Approved → Jira comment `SDET approved the story` + **`sdet-approved`** label + moved to Ready for Testing in the Story Tracker **and** Jira; rejected → comment `SDET rejected the story` + **`sdet-rejected`** label and it **stays In Development** for dev to fix (SDET log the bug manually via `/raise-defect`). **Runnable per story as each PR merges** — only the optional Parent Epic move waits until every story is approved. **C) Request changes to a test plan** — adds/adjusts a manual test case in a story's `/sdet-implement`-generated test plan, traced to an acceptance criterion, without touching code, branches, or status. Every run closes with a confirm-first Approve/Request-Changes checkpoint.|
| **`pr-review`** | Senior-reviewer pass over a PR: reads diff + description, cross-checks stories and audit context, drafts inline comments tagged 🔴 Blocker / 🟠 Issue / 🟡 Nit / ❓ Question / 🟢 Praise plus a verdict and a "Suggested for human review" section.|
| **`reverse-engineering-root`** | Generates the **root** reverse engineering artifacts once at the workspace root — a single artifact set covering **all monorepo modules**, which every module then reuses for development. Run upfront before an epic cycle and keep it refreshed via `stitch-delta` skill |
| **`archive-epic`** | Closes an **epic, bug, or enhancement** release cycle: captures the cycle's **delta** reverse engineering artifacts in a namespaced folder (`delta/<ID>-<name>/` — so N parallel cycles never conflict), then archives the complete `aipdlc-docs` (audit.md, aipdlc-state.md, RE docs + delta, etc..) into `aipdlc-archives/epics/<EPIC-ID>-<name>/`, `aipdlc-archives/bugs/<BUG-ID>-<name>/`, or `aipdlc-archives/enhancements/<ENH-ID>-<name>/` per the `Workflow Type` in state. Does **not** stitch — the delta resides in the PR; run `stitch-delta` on the base branch after merge. **Auto-triggered only for epic cycles** (pr-generator, Epic → Base PR); **bug and enhancement cycles are archived manually** by the operator once the SDET's work is completed and all the artifacts are merged into the cycle branch. |
| **`stitch-delta`** | Post-merge companion to `archive-epic`: runs on the **base branch** after an epic, bug, or enhancement PR merges, discovers un-stitched deltas by comparing `delta/<ID>-*/` folders against the **`stitch-epic.md` ledger**, stitches them into the root RE docs in merge order (per-delta verification), records each in the ledger (re-runs skip the already-stitched deltas), and pushes confirm-first. Root docs are never stitched on epic/bug/enhancement branches — this makes RE-doc merge conflicts impossible with N parallel cycles. |

---

## Framework Distribution — auto-install & auto-update AI-PDLC in any repo

AI-PDLC ships itself to consuming teams via an automated GitHub workflow
([`.github/workflows/distribute-framework.yml`](.github/workflows/distribute-framework.yml)).
Any repo registered in the subscriber registry
([`.github/aipdlc-subscribers.yml`](.github/aipdlc-subscribers.yml)) automatically receives
the framework **as a Pull Request** — both the first-time installation and every subsequent
framework update.

### How it works

1. **A team onboards once** — they hand over a PAT for their repo and the repo URL.
2. **Merging their registry entry to `main` raises the first-time installation PR** in their repo,
   carrying the complete framework: `CLAUDE.md`, `AIPDLC-workflow.md`, `.aipdlc-rule-details/`,
   the `.claude/skills/`, `.gitattributes` and a `.aipdlc-version` stamp. Onboarding targets **only the newly
   added repo(s)** — existing subscribers are not touched by registry changes.
3. **From then on, every PR merged into `main` of this repo** that touches framework files
   (`CLAUDE.md`, `AIPDLC-workflow.md`, `.aipdlc-rule-details/`, `.claude/skills/`, `.gitattributes`)
   automatically raises an update PR in **every** subscriber repo. Non-framework changes
   (e.g. `README.md`) never distribute. Repos already on the latest version are skipped.
   **PR tracking**: each subscriber has at most **one open AI-PDLC PR** (stable branch
   `aipdlc/framework-update`) — if the previous PR is still unmerged when a new version ships,
   that same PR is updated in place (commits, title, description) instead of opening a second
   one; a brand-new PR is created only after the previous one was merged or closed.

### Onboarding a new team/repo

| Step | Who | Action |
|------|-----|--------|
| 1 | Consuming team | Create a GitHub PAT for their repo — fine-grained with **Contents: Read & write** + **Pull requests: Read & write** (or classic PAT with `repo` scope) — and share it with an AI-PDLC maintainer |
| 2 | AI-PDLC maintainer | Store the PAT as an Actions secret in **this** repo (*Settings → Secrets and variables → Actions*), named e.g. `AIPDLC_PAT_<TEAM>` |
| 3 | AI-PDLC maintainer | Add the entry to [`.github/aipdlc-subscribers.yml`](.github/aipdlc-subscribers.yml) and merge to `main`: |

```yaml
repos:
  - repo: some-org/their-repo              # owner/name or full GitHub URL
    token_secret: AIPDLC_PAT_THEIR_TEAM    # NAME of the Actions secret holding the PAT
    # target_branch: develop               # optional — defaults to the repo's default branch
```

The installation PR appears in the subscriber repo within minutes. A single subscriber failing
(e.g. revoked PAT) never blocks distribution to the others, and each run's summary lists the PR
raised (or the up-to-date skip) per repo.

> **Security**: the registry stores only the **name** of the Actions secret — **never** paste
> a raw PAT into the YAML file. Tokens live encrypted in this repo's Actions secrets.

### Version control

The distributed version is read live from the canonical `AI-PDLC Framework Version` line in
`CLAUDE.md`. Update PRs are titled `[AI-PDLC] Framework update → v[N]`, labeled `aipdlc-v[N]`,
carry an `AI-PDLC-Version: [N]` commit trailer, and write the installed version + source commit
into the subscriber's `.aipdlc-version` file — so you can always tell which framework version any
repo is running.

#### Updating the version — files to update manually

When updating the framework, please ensure the version is also updated in these files:

| File | 
|------|
| **`CLAUDE.md`** | 
| **`.claude/skills/pr-generator/SKILL.md`** | 
| **`.claude/skills/stitch-delta/SKILL.md`** | 
| **`.aipdlc-rule-details/agents/stitch-delta-agent.md`** | 

---

## Agents


| Agent | Invoked by | What it covers |
|-------|-----------|----------------|
| **`code-security-review-agent`** | `/code-security-review` skill | A senior application-security engineer persona. Maps the codebase's attack surface (entry points, data stores, auth boundaries), audits every file against all 16 Security Baseline rules (SECURITY-01…16), classifies findings on a four-level severity scale, and produces a dated report with evidence, remediation, and an OWASP-mapped compliance matrix. |
| **`sdet-implement-agent`** | `/sdet-implement` skill | A senior SDET persona that owns **Build and Test**, per story, in parallel with development. Reads the story's acceptance criteria, requirements, epic brief, design and reverse-engineering artifacts — **never application source code**, because the code may not exist yet. Executes `construction/build-and-test.md`: decides which test plans apply, then writes them as **manual test steps** (`TC-…` cases with preconditions, steps, expected result, pass/fail criteria, cleanup) into `aipdlc-docs/tests/<Story-JIRA-ID>-<jira-title>/`, gated on every acceptance criterion being covered.|
| **`archive-epic-agent`** | `/archive-epic` skill (auto-triggered by `pr-generator` on **Epic→Base PRs only**; **bug and enhancement cycles are invoked manually** by the operator after the SDET test-plan PR merges into the cycle branch) | A release-manager persona that closes an epic, bug, or enhancement cycle: generates the cycle's **add-only, namespaced delta** RE artifacts (root docs stay byte-identical), archives the complete `aipdlc-docs` into `aipdlc-archives/epics\|bugs\|enhancements/` and commits so the delta resides the open PR. |
| **`stitch-delta-agent`** | `/stitch-delta` skill | A documentation-integrator persona that runs **only on the base branch, post-merge**. Discovers un-stitched deltas via the `stitch-epic.md` ledger, merges each into the root RE docs in merge order with a per-delta fact-check against the code at HEAD, and pushes race-safely — the ledger's idempotency guarantee means a delta is never stitched twice. |
| **`defect-provenance-analyst`** | `bug-fix` workflow | A read-only code archaeologist for **line-level AI-origin detection**: traces each defective line past cosmetic commits to the commit that *introduced* the logic (`git blame -w -M -C` / `git log -L`), resolves its PR, and issues an AI-generated / human verdict on **positive evidence only** (AI-Generated PR label, Claude co-author trailer, or `AI-PDLC-Version` trailer). Also resolves the **originating Jira ticket** that shipped the line — story, bug fix or enhancement, read from the PR title or commit subject or branch name — which the bug flow links automatically. |
