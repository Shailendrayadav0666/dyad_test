# 🔧 WORKFLOW: `bug-fix-implement` (Bug/Defect — Code Fix)

**Purpose**: Implement the fix for the defect prepared by `bug-fix`. Normally entered from `bug-fix` Step 9's **SDET Handoff Break** — the user answers `yes` there and this workflow runs in the same session (the keyword is only typed to resume a session that answered `no` or ended after analysis). Sibling of `dev-implement`, but: it works **directly on the existing bug branch** (no story selection, no doability gate, no story branch), it runs a **baseline regression pass before touching code**, a **full-repo regression gate after the fix**, and its PR targets the **base branch** with the **`[BUG]`** prefix — after which the archive runs automatically.

## MANDATORY: Rule Details Loading

May be invoked standalone in a fresh session. Resolve `.aipdlc-rule-details/` and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`
- `common/branching-strategy.md` — **Bug Branch Model** section
- `construction/code-generation.md` (planning/generation/coverage mechanics — story selection and story-branch steps do NOT apply here). 🔴 **Follow the Guardrail defined there (Generation Phase Rules)** for any generated code.
- `workflows/code-review.md` (auto-run after the fix) and `workflows/remediate.md` (on the Remediate path)

🔴 **GUARDRAIL — `code-review` and `remediate` are WORKFLOW RULE FILES, NOT Claude skills.** Whenever this workflow "runs Code Review" or "runs Remediate", you MUST `Read` and follow `workflows/code-review.md` / `workflows/remediate.md` (which pull their detailed steps from `construction/code-review.md` / `construction/remediate.md`) as instructions. There is **NO** Claude skill named `code-review` or `remediate` — **NEVER** invoke one via the Skill tool. The only review that IS a skill is **`pr-review`** (post-PR, AUTO MODE, invoked as-is).

Skills used **as-is — NEVER edit them**: **`pr-generator`** (pass target branch = the **Base Branch**; PR type `[BUG]`), **`pr-review`** (AUTO MODE after the PR), and **`archive-epic`** in **bug mode** (🔴 **NEVER auto-invoked by this workflow — the operator runs it manually** after all SDET work has landed on the bug branch; see Step 12).

## MANDATORY: Audit Entry Format

Every audit.md entry in this workflow carries the `**JIRA TICKET**:` field (the defect ticket as a Jira hyperlink) — same format as `bug-fix.md` — AND the `**AI-PDLC VERSION**:` field, exactly as `dev-implement` does:

```markdown
**AI-PDLC VERSION**: "[Framework version [N] read from the "AI-PDLC Framework Version" line in CLAUDE.md — do not hardcode]"
```

The version is read **at runtime** from the canonical "AI-PDLC Framework Version" line in `CLAUDE.md` — it records which framework version the bug fix was developed with. Never omit it and never hardcode a literal number. Append-only, ISO 8601 timestamps, complete raw user input.

## MANDATORY: Approval Gates in this Workflow — GATE 2 and GATE 3

This workflow carries **exactly two numbered approval gates**, defined identically to `dev-implement`:

| Gate | Where | The decision |
|------|-------|--------------|
| **🚧 GATE 2** | **Step 4 — Fix Plan** | Approve the fix plan, or request changes. **No code is written before GATE 2 passes.** |
| **🚧 GATE 3** | **Step 8 — after the AUTO Code Review** | Approve & continue, or Remediate first. **Nothing is committed, pushed, or PR'd before GATE 3 passes.** |

There is **NO GATE 1 in the bug flow** — GATE 1 is the epic flow's approval of the COMPLETE story set (`inception/user-stories.md`), and the bug flow derives exactly ONE story from the ticket instead of generating a story set. The stage approvals inside `bug-fix.md` (requirements, impact analysis, single story, workflow planning) are **stage approvals, not numbered gates**.

**🔴 GATE MARKING PROTOCOL (identical to `dev-implement` / `construction/code-generation.md` — never deviate)**:
1. **The gate is marked in the audit entry's `##` HEADING — there is NO separate `**GATE Number**:` field.** Never invent one.
2. **The PROMPT entry NEVER carries the gate marker** — the word "GATE" must NOT appear anywhere in the prompt entry's `##` heading. Use a plain heading (e.g. `## Fix Plan Approval Prompt (Bug PROJ-123)`).
3. **The RESPONSE entry carries the gate in its `##` heading**, on **BOTH** outcomes — approved AND rejected alike.
4. Every re-ask at the same gate (after changes, or after a remediate loop) uses a `GATE N` heading again — on its RESPONSE entry only.
5. Entry body format is unchanged — every gate entry still carries `**User Email**:`, `**JIRA TICKET**:` and `**AI-PDLC VERSION**:`.

---

## Step 1 — Preconditions

1. Read `aipdlc-docs/aipdlc-state.md`. Require `## Jira` with `Workflow Type: bug` + `Parent Ticket`, and `## Branching` with `Bug Branch`. If missing, STOP: tell the user to run `ticket-implement <JIRA-ID>` first — this workflow only implements a prepared fix.
2. Verify the state records `Design complete — awaiting bug-fix-implement` (or later). If Inception is incomplete, STOP and say which stage is pending.
3. **Switch to the bug branch**: `git fetch origin`, checkout the recorded Bug Branch, `git pull --ff-only` if it has an upstream. Confirm with `git branch --show-current`. 🔴 All work happens on this ONE branch — never cut another branch.
4. Read `aipdlc-docs/inception/impact-analysis.md` and `bug-brief.md` — they drive the plan.

## Step 2 — Ticket → 🔵 In Development (automatic)

Running `bug-fix-implement` IS the claim. Without asking:
1. Story Tracker (single row): Status → `🔵 In Development`, Start + Recorded timestamps set.
2. Transition the Jira ticket to the board's "In Development" state via the Atlassian MCP — resolve the actual transition with `getTransitionsForJiraIssue` (Bug and Story issue types can have different workflows; never hardcode the state name). **Verify it landed**, announce it, log in audit.md.
2.2. **👤 Assign the ticket to the operator (automatic — same claim)**: the developer who typed `bug-fix-implement` claims the fix, so set them as the Jira assignee without asking — read the session **email** LIVE from the session context (the same one stamped as `**User Email**:` in audit.md), resolve it with `lookupJiraAccountId`, set the assignee via `editJiraIssue`, then **verify** by fetching the issue back. If the email resolves to no (or ambiguous) Jira account, leave the assignee unchanged, warn the user, and continue — assignment failure is NON-blocking. Announce and log in audit.md.
2.5. **Add the AI-PDLC version label to the Jira ticket** (mirrors dev-implement's version stamping — the defect ticket was raised by SDET, not by the framework, so it doesn't carry the label yet): add the label `aipdlc-v[N]` to the ticket via the Atlassian MCP, where `[N]` is the FULL framework version (including the minor, e.g. `2.3` → `aipdlc-v2.3` — never the major only, never `aipdlc-v2`), read **at runtime** from the "AI-PDLC Framework Version" line in `CLAUDE.md` (never hardcoded). If the label is already present, skip. Verify, announce, log in audit.md.
3. 🔴 Skip all Parent-Epic sync steps — `## Jira` records `Parent Epic: none` in the bug flow.

## Step 3 — 🧪 BASELINE Regression Run (BEFORE any change)

**Purpose**: know what was already broken so post-fix failures are attributed correctly — a fix must never be blamed for (or silently hide) pre-existing failures.

1. Discover and run the **entire repo's unit test suite** (all modules) with no code changes made yet.
2. Record the baseline in `aipdlc-docs/construction/code/bug-<JIRA-ID>-summary.md`:
   ```markdown
   ## Baseline Regression (pre-fix)
   - Command(s): [exact commands]
   - Result: [X passed / Y failed / Z skipped]
   - Pre-existing failures: [list each failing test, or "none"]
   ```
3. Pre-existing failures are **logged, not fixed** — they are out of scope UNLESS a failing test is itself the defect under fix (note it if so). Log the baseline in audit.md.
4. If the repo has no test suite at all, record that explicitly — the post-fix regression gate then covers only the new tests.

## Step 4 — Fix Plan (🚧 GATE 2)

1. Build the fix plan from `impact-analysis.md` + the design artifacts, using `code-generation.md`'s Part 1 planning format (checkboxed steps), ending with the mandatory Unit Test & Coverage (≥90%) step and the Full Regression Gate (Step 7). **🧾 TRACE THREAD (bug variant, `common/requirements-traceability.md` Rule 7)**: tag every plan step with the `bug-brief.md` expected-behavior statement(s) and `impact-analysis.md` entry it addresses, and self-check that every expected-behavior statement and every impact-analysis touch point appears in ≥1 step before presenting the plan.
2. **Re-validate the impact analysis against current code.** If the plan must touch files NOT in the impact analysis: add them to `impact-analysis.md` and **re-run the Defect Provenance Analyst (`agents/defect-provenance-analyst.md`, per bug-fix Step 5b) on the newly implicated defective lines** — same line-level procedure (trace each defective line to its introducing commit); if any is AI-generated and the ticket isn't labeled yet, offer the `ai-generated-defect` label (confirm-first, verified, logged). Also run **bug-fix Step 5c** on any newly resolved originating ticket keys — create the "is caused by" link automatically (no confirmation), skipping keys already linked, verified and logged.
3. **🚧 GATE 2 — Fix Plan Approval (MANDATORY — no code before this passes)**:
   1. **Log the prompt** in `aipdlc-docs/audit.md` (ISO 8601 timestamp) BEFORE asking, with a plain heading like `## Fix Plan Approval Prompt (Bug [JIRA-ID])`; **the word "GATE" must NOT appear in the prompt entry's heading** ("GATE 2" belongs only on the response entry, below). Include a reference to the complete fix plan.
   2. Present the plan, then ask (verbatim):
      ```
      📋 Fix plan ready for Bug [JIRA-ID] — [N] steps.
      Plan: aipdlc-docs/construction/plans/bug-[JIRA-ID]-fix-plan.md

      ❓ What next?
        A) ✅ Approve plan     — proceed to generate the fix (Step 5)
        B) 🔧 Request changes  — revise the plan and re-present
      [Answer]:
      ```
   3. **Wait for explicit approval — do NOT proceed to Step 5 until the user approves.** On **B**, revise the plan and re-present (each re-ask logs a fresh GATE 2 response entry).
   4. **MANDATORY**: Log the user's raw response in audit.md. **🚧 This decision is GATE 2** — the gate is marked in the response entry's `##` HEADING (there is NO separate `**GATE Number**:` field), on BOTH outcomes:
      - A: `## Fix Plan — GATE 2 Plan Approved (Bug [JIRA-ID])`
      - B: `## Fix Plan — GATE 2 Plan Rejected — Changes Requested (Bug [JIRA-ID])`
      Mark the outcome clearly (✅ approved / ❌ rejected — changes requested). Entry body format is unchanged.

## Step 5 — Generate the Fix

Execute the approved plan step by step on the bug branch, marking each checkbox `[x]` in the same interaction it completes. **🛡️ PLAN FIDELITY**: implement EXACTLY the GATE 2-approved plan — no unplanned files, features, refactors, or scope drift; keep the fix consistent with the impact analysis and design docs the plan was grounded in. If mid-coding you discover the plan must change, STOP, revise it, and present it back through **GATE 2** for re-approval before continuing — never apply a deviation silently. Write code to the workspace root per the existing project structure. Log progress in audit.md.

## Step 6 — Unit Tests + Coverage Gate (≥90%)

1. Write unit test(s) that **reproduce the defect** — they must exercise the exact failure scenario from the bug-brief (ideally shown to fail against the pre-fix logic) — plus tests covering all new/changed code.
2. RUN them; fix failures; measure coverage on the new/changed code; iterate in the SAME run until **≥90%**.
3. Capture evidence (tests X/X passing + measured %) in `bug-<JIRA-ID>-summary.md` and audit.md.

## Step 7 — 🧪 FULL Regression Gate (after the fix)

1. Re-run the **entire repo's unit test suite** (all existing tests + the new bug tests).
2. **Compare against the Step 3 baseline**:
   - **New failures** (passing at baseline, failing now) → caused by the fix. 🔴 BLOCKING: fix them and re-run until zero new failures.
   - **Pre-existing failures** (already failing at baseline) → not blocking; list them as pre-existing.
3. Append the complete outcome to `bug-<JIRA-ID>-summary.md`:
   ```markdown
   ## Full Regression (post-fix)
   - Command(s): [exact commands]
   - Result: [X passed / Y failed / Z skipped]
   - New failures caused by the fix: [none — required to proceed]
   - Pre-existing failures (unchanged from baseline): [list or "none"]
   - New bug tests: [N] — all passing | Coverage on changed code: [NN]%
   ```
4. Log the full comparison in audit.md. Do NOT proceed with new failures outstanding.

## Step 8 — AUTO Code Review → 🚧 GATE 3 Approve / Remediate

Mirrors dev-implement Sections A–C, bug-scoped. The Code Review runs **automatically** — the user is NOT asked whether to review.

### 8a. AUTO Code Review (MANDATORY, automatic)
1. **Log** in audit.md that automated Code Review is starting for Bug [JIRA-ID] (ISO 8601 timestamp).
2. Auto-run `workflows/code-review.md` scoped to this fix (read-only — it MUST NOT edit source) → versioned report `aipdlc-docs/construction/reviews/bug-<JIRA-ID>-code-review-v[X].md`. Pass in the Step 6/7 evidence — the review MUST NOT re-run the tests or re-measure coverage; it cites the stored evidence.
3. **MANDATORY — audit the complete review log**: the `**JIRA TICKET**:` field, report path, verdict, and the complete list of findings by severity (🔴 Blocker / 🟠 High). Do not summarize away findings.
4. Proceed to **8b**.

### 8b. 🚧 GATE 3 — Review Decision Gate (MANDATORY)
1. **Log the prompt** in audit.md with a plain heading like `## Review Decision Prompt (Bug [JIRA-ID])`; **the word "GATE" must NOT appear in the prompt entry's heading** ("GATE 3" belongs only on the response entry, step 4) — then present (verbatim):
   ```
   🔍 Automated Code Review complete for Bug [JIRA-ID].
   Report: aipdlc-docs/construction/reviews/bug-[JIRA-ID]-code-review-v[X].md
   Verdict: [clean — all ACs Met / findings: 🔴 X  🟠 Y]

   ❓ What next?
     A) ✅ Approve & continue — commit, push `<bug-branch>`, and raise the [BUG] PR
     B) 🔧 Remediate        — fix the review findings first
   [Answer]:
   ```
2. **On A (Approve & continue)** → go to **Step 9 (Commit, Push & Raise the `[BUG]` PR)**.
3. **On B (Remediate)** → go to **8c**.
4. **MANDATORY**: Log the user's raw response in audit.md. **🚧 This decision is GATE 3** — the gate is marked in the response entry's `##` HEADING (there is NO separate `**GATE Number**:` field), on BOTH outcomes:
   - A: `## Review Decision — GATE 3 Approved & Continue (Bug [JIRA-ID])`
   - B: `## Review Decision — GATE 3 Not Approved — Remediate (Bug [JIRA-ID])`
   Entry body format is unchanged; the prompt entry never carries the gate marker.

### 8c. Remediate Loop (on Remediate)
1. **Log** in audit.md that Remediate is starting for Bug [JIRA-ID], naming the review report being remediated.
2. Run `workflows/remediate.md` scoped to that report (fix → unit test → green). **Re-run the FULL repo suite if the remediation touched non-test code**, comparing against the Step 3 baseline again — only NEW failures block.
3. **MANDATORY — audit the complete remediate log**: which findings were fixed (by severity), files changed, unit-test evidence, regression comparison. Record the complete log, not a summary.
4. **🚧 Post-Remediate Decision Gate** — log the prompt with a plain heading like `## Post-Remediate Decision Prompt (Bug [JIRA-ID])` (**the word "GATE" must NOT appear in the prompt entry's heading**), then present (verbatim):
   ```
   🔧 Remediation complete for Bug [JIRA-ID].
   ❓ What next?
     A) ✅ Approve & continue — commit, push `<bug-branch>`, and raise the [BUG] PR
     B) 🔁 Re-review        — run automated Code Review again
   [Answer]:
   ```
   - **On A** → go to **Step 9**.
   - **On B (Re-review)** → return to **8a** (produces the next report version `v[X+1]`), then **8b** again. This loop repeats until the user chooses Approve & continue.
5. **MANDATORY**: Log the user's raw response in audit.md. **🚧 This decision is GATE 3** — marked in the response entry's `##` HEADING (no separate field), on BOTH outcomes:
   - A: `## Post-Remediate Decision — GATE 3 Approved & Continue (Bug [JIRA-ID])`
   - B: `## Post-Remediate Decision — GATE 3 Not Approved — Re-review (Bug [JIRA-ID])`

### 8d. Status
The ticket stays `🔵 In Development` throughout review and remediation.

## Step 9 — Commit, Push & Raise the `[BUG]` PR

1. Confirm the active branch is the Bug Branch. Stage and commit the fix (code + tests + updated docs). The commit message MUST carry an `AI-PDLC-Version:` trailer as the framework signature — exactly as dev-implement Section D does — where `[N]` is read at runtime from the "AI-PDLC Framework Version" line in `CLAUDE.md` (do not hardcode a number):
   ```
   git add <fix files>
   git commit -m "[BUG][PROJ-123] <concise fix summary>" -m "AI-PDLC-Version: [N]"
   ```
   The `AI-PDLC-Version: [N]` trailer goes on its own line at the end of the message body (alongside any existing trailers). Record the hash in audit.md.
2. Invoke **`pr-generator`** (as-is), passing **target branch = the Base Branch** from `## Branching`. The PR title carries the **`[BUG]`** prefix; the skill applies the `ai-generated` and `aipdlc-v[N]` labels (plus the `AI-PDLC Framework: v[N]` line in the PR body) and its own Phase 5 confirmation gate — honor it.
3. Record the PR URL in `## Branching` (`Bug PR: <url>`) and the full outcome in audit.md — including the labels applied (`ai-generated` + `aipdlc-v[N]`).

## Step 10 — Tracker Update (NO Ready-for-Testing transition)

1. Story Tracker: keep Status = `🔵 In Development`; set **End** = today and **Recorded** = now; note the PR URL.
2. 🔴 **Do NOT transition the Jira ticket to "Ready for Testing"** (or any further state) the ticket stays In Development after the PR; Add a Jira **comment** on the ticket (automatic) linking the PR with evidence (tests passing, coverage %, regression clean vs baseline).
3. Log in audit.md (with the JIRA TICKET field).

## Step 11 — AUTO PR Review

Invoke the **`pr-review`** skill (as-is) in **AUTO MODE** against the just-raised PR: it posts a plain COMMENT review (summary + inline comments) automatically — no prompt, never a formal APPROVE/REQUEST_CHANGES. Record the outcome in audit.md.

## Step 12 — Archive Handoff (MANUAL)

🔴 **RE-READ FIRST.** Before writing any part of this step's output, `Read` this Step 12 section from the file again. Do NOT reconstruct it from memory or from earlier in this session's context — "I already read this file at Step 1" does not satisfy this.

### The ordering invariant

| # | Action | Relative to the archive |
|---|--------|-------------------------|
| 1 | `sdet/...` PR(s) merge into `<bug-branch>` | BEFORE |
| 2 | `sdet-list-work` Option C amendments pushed to `<bug-branch>` | BEFORE |
| 3 | `sdet-list-work` Option B sign-off → ticket `🧪 Ready for Testing` | BEFORE |
| 4 | **`archive-epic`** (bug mode) | ⬅ **THE ARCHIVE** |
| 5 | **`[BUG]` PR merges into `<base-branch>`** | AFTER |
| 6 | `stitch-delta` on `<base-branch>` | AFTER |

🔴 **`archive-epic` runs at row 4 — BEFORE the `[BUG]` PR merges (row 5).** Its cycle-close commit must reside in the still-OPEN `[BUG]` PR; that is the ONLY path by which the RE delta reaches `<base-branch>` for `stitch-delta`.

**TWO DIFFERENT PRs appear here — never write "the PR" unqualified:**
- the **`sdet/...` PR** → merges into `<bug-branch>`. The archive **waits for this one**.
- the **`[BUG]` PR** → merges into `<base-branch>`. The archive **must precede this one**.

"Wait until all SDET work has landed" means rows 1–3 **only** — never row 5.

**🔴 BANNED OUTPUT — each inverts the invariant. Never emit them, in any wording:**
- "archive runs post-merge" / "it runs post-merge only"
- "when the `[BUG]` PR merges, run `archive-epic`"
- "DO NOT invoke `archive-epic` manually now"
- any instruction for the developer to transition the Jira ticket in this step

Do NOT invoke `archive-epic`, do NOT ask whether to invoke it, and do NOT add an options menu or any competing next-steps block. The block below is the entire output of this step.

### Emit this message VERBATIM (placeholders substituted)

The ONLY permitted modification is substituting `<url>`, `<bug-branch>`, `<base-branch>`, `[JIRA-ID]`, `<slug>` with real values from `## Branching` / the Step 9 PR. **Never ship an unsubstituted placeholder**; never add, remove, reorder, reword, or summarise a line:

```
✅ Bug fix complete — [BUG] PR: <url> (ticket [JIRA-ID] remains 🔵 In Development).
   📦 The cycle archive was deliberately NOT run — it is yours to run, at step 4️⃣ below.

➡️ NEXT ACTIONS (in this order):
   1️⃣  Wait until the SDET `sdet/...` PR(s) for [JIRA-ID] have MERGED into `<bug-branch>`
       (the SDET PR into the bug branch — NOT the [BUG] PR into `<base-branch>`)
   2️⃣  On `<bug-branch>`: `git checkout <bug-branch> && git pull --ff-only`
       (pulls the merged `aipdlc-docs/tests/<JIRA-ID>-.../` docs in so the archive captures them)
   3️⃣  SDET: use the skill sdet-list-work — on `<bug-branch>`, NOT on `<base-branch>`
       • Option C to amend a test plan (commit + push to `<bug-branch>` so the archive captures it)
       • Option B to sign off — promotes ticket [JIRA-ID] 🔵 In Development → 🧪 Ready for Testing
       (Sign-off happens HERE, before the archive.)
   4️⃣  Use the skill archive-epic  on bug branch (bug mode → `aipdlc-archives/bugs/<JIRA-ID>-<slug>/`)
       🔴 MUST happen while the [BUG] PR is still OPEN — its cycle-close commit rides that
          open PR, which is how the RE delta reaches `<base-branch>`.
   5️⃣  ONLY NOW merge the [BUG] PR into `<base-branch>`: <url>
   6️⃣  Switch to `<base-branch>` and pull the latest
   7️⃣  Use the skill stitch-delta (applies this bug's RE delta to the root docs — final action;
       the ONLY base-branch step)

🔴 ORDER IS LOAD-BEARING: archive-epic (4️⃣) runs BEFORE the [BUG] PR merges (5️⃣).
   Merging first breaks stitch-delta and forces a manual recovery PR.
🔴 Use the skill names EXACTLY as shown — do not describe what you want in your own words.
   Any other phrasing is not a framework trigger and the workflow will not advance.
```
---

## Critical Rules
- EVERY audit entry carries the `**JIRA TICKET**:` field AND the `**AI-PDLC VERSION**:` field (version read at runtime from the "AI-PDLC Framework Version" line in `CLAUDE.md` — never hardcoded).
- 🔴 **GATE 2 (Step 4) is the gate before any code exists** — NEVER write a single line of the fix until the user explicitly approves the fix plan. Any mid-coding deviation from the approved plan goes back through GATE 2 for re-approval, never applied silently.
- 🔴 **GATE 3 (Step 8) is the gate before anything leaves the machine** — NEVER commit, push, or raise the `[BUG]` PR until the user explicitly chooses "Approve & continue" at the Review Decision Gate or the Post-Remediate Decision Gate.
- **GATE MARKING PROTOCOL** — the gate is marked ONLY in the audit entry's `##` HEADING; there is NO `**GATE Number**:` field. The PROMPT entry never carries the word "GATE"; the RESPONSE entry carries `GATE 2` / `GATE 3` on BOTH outcomes (approved AND rejected alike), and every re-ask logs a fresh gated response entry. See the Approval Gates section above.
- This workflow has **NO GATE 1** — GATE 1 is the epic flow's COMPLETE-story-set approval; the bug flow derives ONE story from the ticket. `bug-fix.md`'s approvals are stage approvals, not numbered gates.
- Version stamping mirrors dev-implement: the `aipdlc-v[N]` label on the Jira ticket (Step 2.5), the `AI-PDLC-Version: [N]` trailer on the fix commit (Step 9), and the `aipdlc-v[N]` label on the `[BUG]` PR (via pr-generator) — all substituted live from CLAUDE.md.
- ONE branch — work on the recorded Bug Branch only; never create story branches; never commit to the base branch.
- ALWAYS run the BASELINE regression BEFORE any change, and the FULL regression AFTER the fix; only NEW failures (vs baseline) block; log both runs' complete output in `bug-<JIRA-ID>-summary.md`.
- Unit tests must include at least one test reproducing the defect; coverage on new/changed code ≥90%.
- NEVER commit/push/raise the PR before the user chooses "Approve & continue". PR via `pr-generator` only, target = Base Branch, `[BUG]` prefix, `ai-generated` label.
- The ticket stays `🔵 In Development` after the PR — NEVER transition it to Ready for Testing yourself; that is SDET's, via `sdet-list-work` Option B run **on the bug branch, before `archive-epic` and before the `[BUG]` PR merges** (not post-merge on the base branch — after the archive's workspace reset there is no Story Tracker left to promote). No Parent-Epic sync exists in this flow.
- **NEVER run Build & Test in this workflow.** Build and Test is not a Construction step at any level — it belongs to SDET and is run separately, per ticket, via the **`/sdet-implement`** skill (black-box, from the ticket's acceptance criteria, into `aipdlc-docs/tests/<JIRA-ID>-<jira-title>/`). Do not load `construction/build-and-test.md` here and do not write anything under `aipdlc-docs/construction/build-and-test/`.
- At Step 2, ALWAYS assign the Jira ticket to the operator who invoked `bug-fix-implement` (session email → `lookupJiraAccountId` → `editJiraIssue`; automatic, verified, logged). Unresolvable email → leave unassigned, warn, continue — assignment failure never blocks the fix.
- 🔴 After the PR: AUTO `pr-review` (comment-only), then **STOP — the archive is MANUAL**. NEVER invoke `archive-epic` from this workflow. **Re-read Step 12 before emitting its handoff, and emit that block VERBATIM with placeholders substituted** — do not paraphrase it. The operator runs `archive-epic` once the SDET `sdet/...` PR(s) (and any `sdet-list-work` Option C amendments) have merged **into the bug branch**, and **BEFORE the `[BUG]` PR merges into the base branch**, so the delta rides the open PR for post-merge `stitch-delta`. Never tell the user the archive runs post-merge — that inverts the invariant.
