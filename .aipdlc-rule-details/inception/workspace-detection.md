# Workspace Detection

**Purpose**: Determine workspace state and check for existing ai-pdlc projects

## Step 1: Check for Existing ai-pdlc Project

Check if `aipdlc-docs/aipdlc-state.md` exists:
- **If exists**: Resume from last phase (load context from previous phases)
- **If not exists**: Continue with new project assessment

## Step 1.5: Capture Session Identity (silent, email-only, audit.md ONLY)

Apply the **MANDATORY: Session Identity Capture** rules from the root workflow file (CLAUDE.md / equivalent). No shell commands, MCP, or external calls — and NO confirmation question to the user:

1. Read the **session email** from the session context provided by the AI environment (Claude Code injects the logged-in account's email automatically). Use it AS-IS — do NOT ask the user to confirm it, and do NOT derive or record a display name (email is the only identity field)
2. Only if the environment provides NO session email (non-Claude environments), ask the user for their email once
3. **Do NOT persist it anywhere**: the email goes ONLY into audit.md entries as the `**User Email**:` field — NEVER into aipdlc-state.md (no `## Session Identity` section) or any other artifact
4. From this point stamp every audit.md entry with `**User Email**:` (read live from the session context) — at every approval flow this field records who approved. A different developer resuming the project automatically logs under their own session email

## Step 1.6: Sync the Local Base Branch with Remote (MANDATORY, before any freshness assessment)

**Why**: A previous cycle's `stitch-delta` commits the refreshed root reverse engineering docs + the `stitch-epic.md` ledger to the **remote** base branch (or, under branch protection, to an unmerged `docs/stitch-delta-*` PR). A new session's local base branch is often **behind** that. If Step 3 judges RE-doc freshness against a **stale local checkout**, it wrongly concludes the stitch never happened and that the RE docs are out of date. Sync FIRST, then judge.

**Run BEFORE scanning for code and BEFORE the Step 3 freshness assessment:**

1. Record the base branch: `git branch --show-current` (the branch the workflow started on — do NOT assume `main`). This runs before any epic branch exists, so the current branch IS the base branch.
2. `git fetch origin` — update remote-tracking refs.
3. **Fast-forward the local base branch to the remote**:
   - If the working tree is clean and the local base can fast-forward: `git pull --ff-only`.
   - **If the tree is dirty or the branches have diverged**: do NOT clobber. Show `git status` / the divergence and ask the user how to proceed (stash, commit, or continue against the current local state). Log the choice in audit.md.
4. **Detect a pending (unmerged) stitch**: check for an open stitch PR into the base branch — `gh pr list --base <base> --state open --search "stitch-delta in:title"` (or head branch `docs/stitch-delta-*`). If one exists, do NOT treat the RE docs as needing regeneration in Step 3 — instead inform the user a stitch is **pending merge** and that the RE docs will be current once that PR merges.
5. Log the sync result (fetched, fast-forwarded to `<sha>`, or the user's chosen action) in audit.md.

This step ONLY synchronizes the local base branch; it does not create the epic branch (that is Step 4.5).

## Step 2: Scan Workspace for Existing Code

**Determine if workspace has existing code:**
- Scan workspace for source code files (.java, .py, .js, .ts, .jsx, .tsx, .kt, .kts, .scala, .groovy, .go, .rs, .rb, .php, .c, .h, .cpp, .hpp, .cc, .cs, .fs, etc.)
- Check for build files (pom.xml, package.json, build.gradle, etc.)
- Look for project structure indicators
- Identify workspace root directory (NOT aipdlc-docs/)

**Record findings:**
```markdown
## Workspace State
- **Existing Code**: [Yes/No]
- **Programming Languages**: [List if found]
- **Build System**: [Maven/Gradle/npm/etc. if found]
- **Project Structure**: [Monolith/Microservices/Library/Empty]
- **Workspace Root**: [Absolute path]
```

## Step 3: Determine Next Phase

**IF workspace is empty (no existing code)**:
- Set flag: `brownfield = false`
- Next phase: Requirements Analysis

**IF workspace has existing code**:
- Set flag: `brownfield = true`
- **Search the ENTIRE repo for existing reverse engineering artifacts — they can live ANYWHERE, not only at the default path.** Folder and file names are always the same, so search by name:
  1. First check the default location: `aipdlc-docs/inception/reverse-engineering/`
  2. If not there, glob the whole workspace for a directory named `reverse-engineering/` (e.g., `**/reverse-engineering/`) at any depth
  3. Also glob for the standard artifact filenames anywhere in the repo: `business-overview.md`, `architecture.md`, `code-structure.md`, `api-documentation.md`, `component-inventory.md`, `technology-stack.md`, `dependencies.md`, `code-quality-assessment.md`, `reverse-engineering-timestamp.md` — a directory containing several of these IS the artifact set even if the folder is named differently
  4. If found outside the default path, record the discovered location in `aipdlc-state.md` (`## Workspace State` → `Reverse Engineering Artifacts: <path>`) and use THAT path everywhere the artifacts are loaded later (Requirements Analysis, User Stories, design stages)
- **IF reverse engineering artifacts exist (at ANY location found above)** — do NOT regenerate them:
    - **Judge freshness against the stitch ledger, NOT file timestamps** (the local base was already synced in Step 1.6, so the ledger and delta folders now reflect the remote). Timestamps are unreliable across clones/checkouts and are the reason a stitched-but-stale local checkout was previously misread as "out of date":
      1. Read the ledger `aipdlc-docs/inception/reverse-engineering/stitch-epic.md` and scan `aipdlc-docs/inception/reverse-engineering/delta/*/` folders.
      2. A delta folder present on disk but NOT recorded in the ledger = a **pending un-stitched delta** → artifacts are stale.
      3. Every delta folder is recorded in the ledger (or there are none) = artifacts are **current** — the previous cycle's stitch is already reflected.
    - **Honor the pending-stitch signal from Step 1.6**: if Step 1.6 found an open `docs/stitch-delta-*` PR into the base, do NOT rerun Reverse Engineering — tell the user the stitch is **pending merge** and proceed with the existing artifacts (the docs become current when that PR merges).
    - **IF artifacts are current**: Load them, skip to Requirements Analysis
    - **IF artifacts are stale (un-stitched delta on disk, no pending stitch PR)**: Next phase is Reverse Engineering (rerun to refresh artifacts) — or offer to run `stitch-delta` to fold the pending delta in
    - **IF user explicitly requests rerun**: Next phase is Reverse Engineering regardless of freshness
- **IF no reverse engineering artifacts**: Check `aipdlc-archives/epics/`, `aipdlc-archives/bugs/` AND `aipdlc-archives/enhancements/` for archive folders (created by the `archive-epic` skill at the end of a previous epic, bug, or enhancement release cycle)
    - **IF archives exist**: The most recently archived cycle folder — across BOTH subfolders, by archive date in `archive-manifest.md` — contains the latest stitched root reverse engineering documents (`<archive>/aipdlc-docs/inception/reverse-engineering/`). Ask the user:
      ```
      ❓ No live reverse engineering artifacts found, but archived artifacts exist
         from the last release cycle ([EPIC-KEY or BUG-KEY] — [name], archived [date]).

      A) Restore the archived reverse engineering documents 
      B) Run fresh reverse engineering against the current codebase (recommended if the code changed since the archive)

      [Answer]:
      ```
      On A: copy the archived `reverse-engineering/` folder into `aipdlc-docs/inception/reverse-engineering/`, log the restore in audit.md, then proceed to Requirements Analysis. On B: next phase is Reverse Engineering.
    - **IF no archives**: Next phase is Reverse Engineering

**Monorepo note**: Reverse engineering artifacts are always checked/generated at the workspace ROOT only — one artifact set covering all modules. Never look for or create per-module artifact sets (see `inception/reverse-engineering.md` "Monorepo Handling").

## Step 4: Create Initial State File

Create `aipdlc-docs/aipdlc-state.md`:

```markdown
# ai-pdlc State Tracking

## Project Information
- **Project Type**: [Greenfield/Brownfield]
- **Start Date**: [ISO timestamp]
- **Current Stage**: INCEPTION - Workspace Detection

## Workspace State
- **Existing Code**: [Yes/No]
- **Reverse Engineering Needed**: [Yes/No]
- **Workspace Root**: [Absolute path]

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aipdlc-docs/)
- **Documentation**: aipdlc-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Stage Progress
[Will be populated as workflow progresses]
```

## Step 4.5: Create the Epic Branch (automatic)

Load `common/branching-strategy.md` and execute **Section 1 — Epic Branch Creation**:
- Record the **base branch** (the branch the workflow started on — do not assume `main`)
- Create `epic/<EPIC-KEY>-<kebab-case-epic-title>` automatically (confirm a name with the user only when no Epic was provided)
- Record `## Branching` (Base Branch, Epic Branch) in `aipdlc-docs/aipdlc-state.md`
- **Skip** if `## Branching` already exists (resumed project) — verify the epic branch exists and switch to it

Log the branch creation (name + base branch) in audit.md.

## Step 4.6: Ensure the Context Project Folder (BROWNFIELD ONLY — check first, create only if missing)

> **🟢 Greenfield → SKIP Steps 4.6 and 4.7 entirely.** An empty workspace has no existing system to describe, so context-project does not apply. Only run these steps when `brownfield = true`.

Ensure a **`context-project/` folder exists at the workspace ROOT** (a sibling of `aipdlc-docs/`, NEVER inside it). This is a human-authored home for **knowledge about the CURRENT project** — how the existing system works, where things live, what each module does (e.g. an `interview.md` per module). It is context about what already exists, NOT requirements for the new work; the framework never auto-populates it.

- **Check first**: test whether `context-project/` already exists at the workspace root. **If it exists** (left by an earlier run or already curated by the team) — reuse it AS-IS: do NOT recreate, empty, overwrite, or delete it or its contents.
- **Only if absent**: create an empty `context-project/` folder. Do NOT create a README inside it.
- This is a safety net so the folder is present even on brownfield flows that skip reverse engineering (where `reverse-engineering.md` would otherwise scaffold it).

## Step 4.7: Context Project Opt-In (BROWNFIELD ONLY — ask ONCE, record in state, reuse on resume)

**Greenfield → skip (see Step 4.6 note).** **Skip this step entirely if `aipdlc-state.md` already contains a `## Context Project` section** (a resumed project already answered) — reuse the recorded values, do NOT re-ask.

Otherwise ask the user ONCE (per `common/question-format-guide.md`):

```
❓ Are there any context-project artifacts I should use for this task?
   (Human-authored knowledge about the CURRENT project — how the existing system works,
    where things live, what each module does — placed under context-project/,
    with one subfolder per module named exactly after it.)

A) Yes — paste the exact path of the file/folder to use (e.g. context-project/ALIX.BMS/interview.md)
B) No  — continue without it

[Answer]:
```

Record the answer in `aipdlc-docs/aipdlc-state.md`:

```markdown
## Context Project
- **Use Artifacts**: [Yes/No]
- **Artifact Path**: [exact file/folder path the user pasted — or `—` if No]
```

Rules:
- On **A**: record the exact path AS-IS. Only that path is ever read (no auto-scanning of the rest of `context-project/`). If the pasted path does not exist, tell the user and re-ask.
- On **B**: record `Use Artifacts: No` and `Artifact Path: —`.
- Log the prompt and the user's complete raw answer in `audit.md`.
- Downstream, **Requirements Analysis** and **Workflow Planning** read `## Context Project` and consult the recorded path (only when `Use Artifacts: Yes`) as a primary input.

## Step 4.8: Load the Design Reference Guardrail (NO question — enforcement only)

**Load `common/design-reference-grounding.md` and apply it for the remainder of the workflow.**

**Do NOT ask the user anything here.** This step adds no prompt. The guardrail is purely reactive: whenever the user names a file path, folder path, spec document, screenshot, or design URL in ANY input at ANY stage — the initial request, a clarifying answer, a request-changes message, a remediation comment — that artifact MUST be registered in `## Design References` in `aipdlc-state.md` and its **actual content read** in the stage where it was named (rules DR-1 / DR-2 / DR-4), then re-consulted before design and code artifacts (DR-5).

If the user's initial request already names such an artifact, register it now and log it in `audit.md`.

## Step 5: Present Completion Message

**For Brownfield Projects:**
```markdown
# 🔍 Workspace Detection Complete

Workspace analysis findings:
• **Project Type**: Brownfield project
• [AI-generated summary of workspace findings in bullet points]
• **Next Step**: Proceeding to **Reverse Engineering** to analyze existing codebase...
```

**For Greenfield Projects:**
```markdown
# 🔍 Workspace Detection Complete

Workspace analysis findings:
• **Project Type**: Greenfield project
• **Next Step**: Proceeding to **Requirements Analysis**...
```

## Step 6: Automatically Proceed

- **No user approval required** - this is informational only
- Automatically proceed to next phase:
  - **Brownfield**: Reverse Engineering (if no existing artifacts) or Requirements Analysis (if artifacts exist)
  - **Greenfield**: Requirements Analysis
