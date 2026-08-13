# Story Selection - Detailed Steps

**Purpose**: Before generating code, determine WHICH **Jira** story is being implemented — the user types the Jira story they want to develop — run the Doability Gate, and move it from `🟢 Ready for Development` to `🔵 In Development` **automatically** (picking the story is the claim — no confirmation is asked for this transition, in Jira or the local tracker).

**Story statuses** (the only valid Story Tracker statuses — see the Story Status Lifecycle in `CLAUDE.md`):
`🟢 Ready for Development` → (this stage, on `dev-implement`) → `🔵 In Development` (stays here through code gen, review, PR raise, PR review) → (after the PR is **MERGED**) → `🧪 Ready for Testing`.

**Runs**: At the start of Code Generation (Step 0), once per story, when the user invokes `dev-implement`. Mandatory.

## Prerequisites
- User Stories stage complete (`aipdlc-docs/inception/user-stories/stories.md` exists)
- Dependency Graph stage complete (`aipdlc-docs/inception/dependency-graph.yml` exists with `requires`/`enables`)
- `aipdlc-docs/aipdlc-state.md` contains a `## Story Tracker` table

---

## Step 0: No Bulk PR-Merge Reconciliation Here (by design)

Story Selection does **NOT** scan every `🔵 In Development` story and promote it to `🧪 Ready for Testing`
Instead, dependency readiness is checked **live, per prerequisite, only for the story being selected** — see the **Doability Gate (Step 4)** below. Nothing in this step mutates the Story Tracker or Jira.

## Step 1: Verify Jira Availability
- [ ] Story selection is **Jira-only** — the user develops a Jira story. Confirm the Atlassian MCP is connected.
- [ ] If the MCP is NOT available, STOP and tell the user Jira integration is required to select a story (connect the Atlassian MCP first) — there is no local-only selection path.

## Step 2: Present Story Selection Prompt

Present the following:

```text
Which Jira story would you like to develop?

Type the Jira story key (e.g. PROJ-123):
```

**DO NOT guess which story to implement. Wait for the user to type the Jira story key.**

## Step 3: Resolve the Selected Story (Jira)
- [ ] Take the Jira story key the user typed — do NOT assume it.
- [ ] Fetch the issue (`getJiraIssue`) and show its summary, status, priority, and acceptance criteria.
- [ ] **ASK FOR CONFIRMATION**: "Implement this story? (yes / no)"
- [ ] Map the Jira issue to a local story in `stories.md` via the `Jira` column. If no matching local story exists, create one from the issue body so code generation has a reference. Note its `Requires`.

## Step 4: 🚦 Doability Gate (MANDATORY — live PR-merge check)
- [ ] Look up the chosen story in `dependency-graph.yml` → read its `requires`. No `requires` (or empty) → doable, skip to Step 5.
- [ ] For EACH story in `requires`, resolve doability directly:
  - If its Story Tracker `Status` already reads `🧪 Ready for Testing` → doable, no further check needed for this prerequisite.
  - Otherwise, read its recorded `PR` column. If a PR URL is present, check its real state LIVE: `gh pr view <PR-URL-or-branch> --json state,mergedAt,baseRefName`.
    - `mergedAt` set (state MERGED) → doable.
    - OPEN, CLOSED (not merged), or no PR recorded yet → NOT doable.
- [ ] **Doable IFF every prerequisite resolves doable above** — i.e. each has its PR **MERGED into the epic branch** (its code is present there). If ANY prerequisite is NOT doable, 🛑 **STOP THE RUN** (do not loop back to Step 2, do not let the user bypass this gate):
  ```
  🛑 Cannot start Story [N.M] yet.
     It requires Story [X.Y] ([JIRA-KEY]), whose PR is not merged yet:
       • Story [X.Y] — [JIRA-KEY] — <PR URL, or "no PR raised yet"> — status: <OPEN / CLOSED (not merged) / none>
       [list every unmet prerequisite]

  ➡️ Merge Story [X.Y]'s PR into the epic branch first, then run `dev-implement`
     again to develop Story [N.M].
  ```
  Log the block (which prerequisite(s), their live-checked PR state) in audit.md, then END this `dev-implement` run. No story/Jira status has changed at this point — Step 5 (the move to `🔵 In Development`) has not run yet. The user re-invokes `dev-implement` after merging the blocking PR(s).
- [ ] If every prerequisite resolves doable, proceed to Step 5. This live check is authoritative and agrees with the branch-cut dependency-merge check in `common/branching-strategy.md` Section 3 (which remains as a defense-in-depth safety net at branch-creation time, e.g. if a merge were undone between this gate and the branch cut).

## Step 5: Move Story to In Development (AUTOMATIC — no confirmation)

**Picking a story IS the claim.** Once the user selects the story and the Doability Gate passes, move it to `🔵 In Development` automatically — do NOT ask the user to confirm the Jira transition or the tracker update.

- [ ] If the selected story has a Jira key, transition via the Atlassian MCP immediately:
  ```
  @atlassian transitionJiraIssue [JIRA-KEY] -> "In Development"
  add comment: "Development started via ai-pdlc (story moved to In Development)."
  ```
- [ ] **VERIFY**: fetch the issue back and confirm the transition landed. If rejected, list available transitions and retry with the exact name. Still failing → STOP and report.
- [ ] **👤 ASSIGN THE STORY TO THE OPERATOR (AUTOMATIC — same claim)**: the developer who typed `dev-implement` claims the story, so set them as the Jira assignee — no confirmation asked:
  1. Read the operator's **email** LIVE from the session context (the same email stamped as `**User Email**:` in audit.md — never ask, never cache).
  2. Resolve their Jira account: `@atlassian lookupJiraAccountId` with that email.
  3. Set the assignee: `@atlassian editJiraIssue [JIRA-KEY]` with `assignee = <resolved accountId>`.
  4. **VERIFY**: fetch the issue back and confirm the assignee matches. If the email resolves to NO Jira account (or multiple ambiguous matches), do NOT guess — leave the assignee unchanged, warn the user (`⚠️ Could not resolve <email> to a Jira account — story left unassigned; assign manually.`), and log the failure in audit.md. Assignment failure is NON-blocking: development proceeds either way.
- [ ] Announce the change to the user (informational, not a question): "🔵 Story [N.M] claimed — Jira [JIRA-KEY] moved to In Development, assigned to [session email]."
- [ ] **🔷 EPIC → In Development (AUTOMATIC — first story only)**: If this is the FIRST story to move to `🔵 In Development` (no other story in the Story Tracker is `🔵 In Development` or `🧪 Ready for Testing`), also transition the **Parent Epic** (from `## Jira` in `aipdlc-state.md`) to "In Development":
  ```
  @atlassian transitionJiraIssue [EPIC-KEY] -> "In Development"
  add comment: "First story ([N.M] / [JIRA-KEY]) started via ai-pdlc — epic moved to In Development."
  ```
  Verify the transition landed (retry with the board's exact transition name if rejected), announce it ("🔷 Epic [EPIC-KEY] moved to In Development — development has started."), and log it in audit.md. Skip silently if `## Jira` records `Parent Epic: none` or the Epic is already In Development (or beyond).
- [ ] These are the ONLY automatic Jira transitions in the workflow (story → In Development on pick, plus the Epic → In Development on the first pick) — every OTHER status change (e.g., `🧪 Ready for Testing`) still follows the confirm-first Jira Sync Rule.

## Step 6: Update Story Tracker (AUTOMATIC — no confirmation)
- [ ] In `aipdlc-docs/aipdlc-state.md` `## Story Tracker`, for the selected story set (without asking):
  - **Status** → `🔵 In Development` (moved from `🟢 Ready for Development`)
  - **Start** → today's date (`YYYY-MM-DD`) if not already set
  - **Recorded** → current timestamp (`YYYY-MM-DD HH:MM`)
- [ ] Append to `aipdlc-docs/audit.md`: the selected story, the automatic status change `🟢 Ready for Development → 🔵 In Development` (Jira + tracker, with verification result), and the Jira assignee set (email + resolved accountId, or the resolution failure) with timestamps. The entry MUST include the `**JIRA TICKET**:` field — the story's Jira key as a clickable link `[PROJ-XXX](<site-base-url>/browse/PROJ-XXX)`, or the local Story ID when `Jira = —` (see the Audit Entry Format in `workflows/dev-implement.md`).
- [ ] The story now **stays `🔵 In Development`** through Code Generation, the automated Code Review, any Remediate loop, the PR raise, and the auto PR Review — it moves to `🧪 Ready for Testing` ONLY when its PR is **MERGED** into the epic branch, promoted exclusively by the `sdet-list-work` skill, after SDET has tested it. (dev-implement/story-selection only ever live-check a prerequisite's PR at the Doability Gate — they never promote this story's own tracker/Jira status.)

## Step 7: Hand Off to Code Generation
- [ ] Return the resolved story (ID, title, acceptance criteria, Jira key/link if any) to Code Generation Part 1.
- [ ] Code Generation proceeds to plan and generate code for this story (implementation, then unit tests to ≥90% coverage) into the application code structure, on the story branch cut from the epic branch (see code-generation.md Critical Rules and `common/branching-strategy.md`).

---

## Critical Rules
- 🔴 Story selection is **Jira-only** — there is NO local-story selection path. The user types the Jira story key they want to develop; if the Atlassian MCP is unavailable, STOP.
- 🔴 NEVER guess which story to implement — always ask the user to type the Jira story key and wait.
- 🔴 NEVER bypass the Doability Gate — all of a story's `requires` must be confirmed MERGED: either already `🧪 Ready for Testing` in the tracker, or live-verified via `gh pr view` at gate time. Any unmet prerequisite → 🛑 STOP the run with a clear message naming it (never loop back silently, never let the user bypass it).
- 🔴 The ONLY valid Story Tracker statuses are `🟢 Ready for Development`, `🔵 In Development`, and `🧪 Ready for Testing`. This stage moves the story to `🔵 In Development` only.
- 🔴 ALWAYS take the Jira story key the user types at development time — do not assume it.
- 🔴 The `🟢 Ready for Development → 🔵 In Development` transition is AUTOMATIC on story pick — apply it to Jira AND the Story Tracker without asking, ALWAYS verify the Jira transition landed, and announce it. All OTHER Jira transitions remain confirm-first per the Jira Sync Rule.
- 🔴 On every story pick, ALWAYS set the Jira assignee to the operator who invoked `dev-implement` (session email → `lookupJiraAccountId` → `editJiraIssue`, automatic, verified, logged). If the email can't be resolved to a Jira account, leave unassigned, warn, and continue — assignment failure never blocks development.
- 🔴 When the FIRST story of the epic moves to `🔵 In Development`, ALWAYS also transition the Parent Epic (from `## Jira`) to "In Development" automatically — verify, announce, and log it.
- 🔴 ALWAYS record the selected story (and its Start/Recorded timestamps) in the Story Tracker before code generation begins.
- 🔴 When a PROJECT_KEY is needed (e.g., a "pick from jira" search), FIRST reuse the `Project Key` recorded in `aipdlc-state.md` `## Jira`; ask the user only if none is recorded — never hard-code it.
