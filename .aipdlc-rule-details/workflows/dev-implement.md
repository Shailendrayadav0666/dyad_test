# 🔑 WORKFLOW: `dev-implement` (Construction Phase — Code Generation)

## MANDATORY: Rule Details Loading

This workflow may be invoked standalone (the user just types `dev-implement`, possibly in a fresh session). Before doing anything else, resolve the rule details directory (check  `.aipdlc-rule-details/`) and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`
- The REQ-ID thread rules from `common/requirements-traceability.md` (plan-level trace + fallback coverage verification)
- The branching model from `common/branching-strategy.md` (epic branch → story branches)
- Story selection steps from `construction/story-selection.md`
- The detailed code generation steps from `construction/code-generation.md`. 🔴 **Follow the Guardrail defined there (Generation Phase Rules)** for any generated code.
- The reviewer steps from `workflows/code-review.md` (auto-run after code generation) and the fixer steps from `workflows/remediate.md` (on the Remediate path)

🔴 **GUARDRAIL — `code-review` and `remediate` are WORKFLOW RULE FILES, NOT Claude skills.** Whenever this workflow "runs Code Review" or "runs Remediate", you MUST `Read` and follow `workflows/code-review.md` / `workflows/remediate.md` (which pull their detailed steps from `construction/code-review.md` / `construction/remediate.md`) as instructions. There is **NO** Claude skill named `code-review` or `remediate` — **NEVER** invoke one via the Skill tool. The only review that IS a skill is **`pr-review`** (post-PR, AUTO MODE, invoked as-is).

This workflow also uses the **`pr-generator`** Claude skill (`.claude/skills/pr-generator/`) to push the branch and raise the PR — always pass it the **target branch** explicitly (story PRs target the **Epic Branch** from `aipdlc-state.md` `## Branching`). **NEVER edit that skill — invoke it as-is.**

After the PR is raised (the story STAYS `🔵 In Development` — it is promoted to `🧪 Ready for Testing` only when the PR MERGES), this workflow also auto-invokes the **`pr-review`** Claude skill (`.claude/skills/pr-review/`) against that same PR in its **AUTO MODE** — it posts a plain COMMENT review (summary + inline comments) automatically, with no user prompt and no formal GitHub approve/request-changes. **NEVER edit that skill — invoke it as-is.**

This workflow does **NOT** itself flip any story's tracker/Jira status to `🧪 Ready for Testing` — that promotion is performed ONLY by the **`sdet-list-work`** skill (`.claude/skills/sdet-list-work/`), which SDET runs separately on the epic branch after it has tested the merged stories. Instead, when the user picks a story that `requires` another story, the **Doability Gate** (`construction/story-selection.md` Step 4) checks that specific prerequisite's PR merge state LIVE, right there — if it isn't merged yet, the gate blocks with a clear message and the run stops; if it's merged, the pick proceeds normally. See Step 1.5 below.

All paths below are relative to the resolved rule details directory.

---

## MANDATORY: Audit Entry Format for this Workflow — JIRA TICKET on EVERY entry

**EVERY audit.md entry written during a `dev-implement` run — from Story Selection, through the Story Branch checkpoint, code-generation planning, code generation done, Unit Test & Coverage, automated Code Review, Remediate, and Approve/PR — MUST include the `**User Email**:`, `**JIRA TICKET**:`, `**Epic Link**:` and `**AI-PDLC VERSION**:` fields.** No dev-implement audit entry may omit them.

```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO timestamp]
**User Email**: [current session email — read live from the session context]
**User Input**: "[Complete raw user input - never summarized]"
**JIRA TICKET**: "[Complete JIRA Ticket that was implemented]"
**Epic Link**: "[Full Parent Epic URL as a clickable link, from ## Jira in aipdlc-state.md — or "none"]"
**AI-PDLC VERSION**: "[Framework version [N] read from the "AI-PDLC Framework Version" line in CLAUDE.md — do not hardcode]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

- **AI-PDLC VERSION**: read at runtime from the canonical "AI-PDLC Framework Version" line in `CLAUDE.md` — this records which framework version the work unit was developed with. Never omit it and never hardcode a literal version.
- **Epic Link**: the FULL Parent Epic URL read from `## Jira` in `aipdlc-docs/aipdlc-state.md` (Epic URL line), written as a clickable Markdown link `[EPIC-KEY](<site-base-url>/browse/EPIC-KEY)`. If `## Jira` records `Parent Epic: none` (or no Epic exists), write `none` — the field itself is never dropped.
- For a Jira-linked story, write the ticket as a clickable Markdown link `[PROJ-XXX](<site-base-url>/browse/PROJ-XXX)` — never bare text.
- For local-only stories (`Jira = —`), put the local Story ID (e.g., `Story 1.2 (local — no Jira)`) in the same field — the field itself is never dropped.
- This applies to every step's entries: selection prompt/response, automatic In-Development transition, branch creation (or Case B stop), plan approval, per-step generation logs, coverage evidence, review outcome, remediate outcome, and the commit/push/PR result.

---

## Step 1 — Keyword Behavior (on invocation)

1. **Read `## Branching`** from `aipdlc-docs/aipdlc-state.md` (Base Branch + Epic Branch). If missing, run `common/branching-strategy.md` Section 1 now (create the epic branch) before proceeding.
1.5. **🔗 No bulk status reconciliation here (by design)**: dev-implement does NOT scan/promote all `🔵 In Development` stories at the start of a run — it never rewrites the Story Tracker or Jira for a story it isn't actively selecting. Dependency readiness is instead verified **live, per prerequisite**, inside the **Doability Gate** (Step 2 below → `construction/story-selection.md` Step 4) at the moment a story with `requires` is picked:
   - Each prerequisite's PR is checked directly (`gh pr view <PR-URL-or-branch> --json state,mergedAt,baseRefName`) unless its Story Tracker `Status` already reads `🧪 Ready for Testing`.
   - **Merged (or already `🧪 Ready for Testing`)** → that prerequisite is doable; proceed.
   - **OPEN / CLOSED (not merged) / no PR yet** → 🛑 the Doability Gate BLOCKS with a clear message naming the unmerged prerequisite and its PR, and the run STOPS — no story/Jira status is changed by dev-implement itself.
   The Story Tracker/Jira status itself is moved to `🧪 Ready for Testing` only when SDET runs the **`sdet-list-work`** skill on the epic branch — it lists the stories whose PRs have merged and promotes the ones SDET confirms it has finished testing.
1.75. **⚠️ Sequential-development banner (MANDATORY — show on EVERY invocation, before Story Selection)**: display this note to the user verbatim, then continue:
   ```
   ⚠️ Note: stories are NOT to be developed in parallel in this session — dev-implement builds ONE story at a time, sequentially (each story branch is cut from the epic branch).
   To develop stories in parallel, open a NEW folder/clone of this same repo, check the Dependency Graph, and run dev-implement there on an INDEPENDENT story.
   ```
2. **Story Selection + Doability Gate**: execute `construction/story-selection.md` in full — it asks which story (Story ID / number, title, or Jira key), reads it from the local Story Tracker / `stories.md` (or resolves the Jira key), runs the Doability Gate, and moves the story from `🟢 Ready for Development` to `🔵 In Development` **automatically** (picking the story is the claim — Jira and the Story Tracker are both updated without asking, Jira transition verified, and the Jira issue is **assigned to the operator who invoked `dev-implement`** — session email → `lookupJiraAccountId` → `editJiraIssue`, verified, non-blocking on failure). Do NOT re-implement the prompt or the gate here.
3. **🌿 Story Branch checkpoint (MANDATORY — immediately after story selection)**: In the SAME interaction where the story is chosen, create the story branch per **Step 1.5** below. Do NOT begin Code Generation until the story branch is created and active.
4. Only once the Doability Gate passes **and** the story branch is active **and** the BASELINE regression has been captured (Step 1.5 Item 4.5), proceed with **Code Generation** (Part 1 Planning → Part 2 Generation → unit tests to ≥90% coverage → FULL regression vs baseline).

---

## Step 1.5 — 🌿 Story Branch checkpoint (MANDATORY)

Runs **after** Story Selection resolves the story (Doability Gate passed, story marked `🔵 In Development`) and **before** Code Generation Part 1. Execute **`common/branching-strategy.md` Section 3 — Story Branch Creation** in full. Summary (the strategy file is authoritative):

1. **Log the prompt** in `aipdlc-docs/audit.md` (ISO 8601 timestamp) before asking anything.
2. Derive the branch name automatically — `story/<N.M>-<kebab-case-story-title>` (Jira key prefixed when present) — and show it to the user for confirmation (they may override the name).
3. **Refresh the epic branch** (`git fetch origin && git checkout <epic-branch> && git pull --ff-only`), then run the **dependency-merge check** on the story's `requires`:
   - All prerequisites merged into the epic branch (or none) → cut the story branch **from the epic branch** (NEVER from main/the base branch).
   - Any prerequisite NOT merged → 🛑 **WARN AND STOP** with the Case B message from branching-strategy.md Section 3: tell the user to merge the prerequisite's PR into the epic branch first, do NOT create a story branch (there is no alternative base), revert the story to `🟢 Ready for Development` (tracker + Jira, verified), log in audit.md, and END this `dev-implement` run — the user re-invokes it after merging.
4. **Record in audit.md**: the story branch name, the base it was cut from, and the user's raw responses.
4.5. **🧪 BASELINE Regression Run (MANDATORY, AUTOMATIC — BEFORE any code is generated)**: on the freshly cut story branch, run the **ENTIRE repo test suite** (not just this story's area) and save the raw runner output to `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/baseline-regression.log`. Record the pass/fail counts and the full list of failing tests in audit.md. This is the reference point the post-implementation regression gate is diffed against. **No user prompt — capture it and continue.**
   - Any failures here were already present on the epic branch (introduced by a PREVIOUSLY MERGED story, not this one). **Logging them in `baseline-regression.log` is all that is required — do not try to fix them, and do not block on them.** They exist only to define what "already broken" means, so the post-implementation gate can tell this story's breakage apart from everyone else's.
   - If the repo has no test suite at all, record that explicitly in audit.md — the post-implementation gate then covers only this story's new tests.
5. Carry the story branch forward — it is the target branch for the commit/push/PR step after review. **Do NOT proceed to Code Generation until the branch is created and confirmed active** (`git branch --show-current` matches).

> **Multiple developers**: Each dev independently runs `dev-implement` and selects a different ready story. The Dependency Graph (`requires` on each story) plus the Doability Gate ensure no two devs pick stories with unresolved dependencies.

> **Design context**: The system-level design artifacts (functional/NFR/infrastructure) live under `aipdlc-docs/construction/design/` and apply to every story. Code for the story is written into the application structure defined in Application Design (or code-generation.md's structure rules).

---

# Code Generation (per-story)

**Runs once per story selected via `dev-implement`.**

**Two parts, preceded by Story Selection + Story Branch checkpoint:**
1. **Part 1 - Planning**: Create a detailed code-generation plan (implement layers, then the mandatory Unit Test & Coverage step).
2. **Part 2 - Generation**: Execute the approved plan to generate code and artifacts, then generate + run unit tests until coverage is ≥90% (same run).

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md.
2. Load all steps from `construction/code-generation.md`.
3. **STEP 0 — Story Selection (MANDATORY)**: Execute `construction/story-selection.md` in full — it is dependency-aware and self-contained. It asks which story (ID / number, title, or Jira key), shows the currently ready stories, runs the **Doability Gate** (proceed only if every `requires` is confirmed MERGED — already `🧪 Ready for Testing`, or live-verified via `gh pr view`; else 🛑 STOP the run with a clear message naming the unmerged prerequisite), and — **automatically, no confirmation** — moves the chosen story from `🟢 Ready for Development` to `🔵 In Development` in the Story Tracker + Jira (transition verified, announced), **assigns the Jira issue to the operator who typed `dev-implement`** (session email → account lookup, verified, non-blocking on failure), setting `Start`/`Recorded`. If the story is already `🔵 In Development`, warn that it may be claimed by another dev. Do NOT re-implement the selection prompt or gate logic here.
3.5. **STEP 0.5 — Story Branch checkpoint (MANDATORY)**: Execute **Step 1.5** — create the story branch from the epic branch (dependency-merge check; on any unmerged prerequisite, warn and STOP per Case B — merge first) and record it in audit.md. This branch is the target for the commit/push/PR step after review. Do NOT start Part 1 until the branch is active.
4. **PART 1 - Planning**: Create the code-generation plan with checkboxes — implementation steps per layer, ending with the mandatory **Unit Test & Coverage (≥90%)** step. **📐 GROUND THE PLAN in the previously generated docs**: every plan step MUST trace back to the story's acceptance criteria, `epic-brief.md`, `requirements.md`, and the design artifacts under `aipdlc-docs/construction/design/` + Application Design — never invent scope, files, or behavior not backed by those documents. **🎨 DESIGN REFERENCE GROUNDING (`common/design-reference-grounding.md` Rule DR-5 — automatic, adds NO question and NO gate)**: execute `code-generation.md` **Step 1.5** silently — read the `### Reconciliations` table first (**DR-8**: points already decided against a reference by an earlier design stage are settled — follow the framework's design docs there and never reintroduce an excluded capability), then re-open every registered design reference in `aipdlc-state.md`'s `## Design References` that covers a component this story builds (a fresh read for THIS story's scope; "read in an earlier stage" does NOT count) and ground only the **unreconciled** points, and state per component either `Design reference: <path> — grounded (...)` or `Design reference: none covers this component`. On an unreconciled prototype/AC mismatch, apply **DR-6**: follow the design, say plainly in the plan what differed, amend the AC to stay truthful, record the reconciliation, and continue — the user sees it at the existing GATE 2; do NOT halt or ask. **🧾 REQ-ID THREAD (`common/requirements-traceability.md` Rule 5)**: resolve the story's `Covers` REQ-IDs and read their text in `requirements.md` (the requirement, not just the AC restatement, is planning input), tag every plan step with the REQ-ID(s)/AC(s) it implements, and pass the trace completeness self-check (every covered REQ-ID and every AC in ≥1 step — blocking, fixed silently) BEFORE presenting the plan. Then get user approval (**🚧 GATE 2** — the user's approve/reject RESPONSE entry in audit.md carries the gate in its HEADING, e.g. `## Code Generation Part 1 — GATE 2 Plan Approved (Story N.M)`, or ## Code `Generation Part 1 — GATE 2 Plan Rejected — Changes Requested`, per `code-generation.md` Step 8; no separate field, and the prompt entry never carries the gate marker).
5. **PART 2 - Generation**: Execute the approved plan for this story, writing into the application code structure. **🛡️ PLAN FIDELITY**: implement EXACTLY the approved plan — no unplanned files, features, refactors, or scope drift; keep the generated code consistent with the design docs the plan was grounded in. If mid-coding you discover the plan must change, STOP, present the revised plan back through GATE 2 for re-approval before continuing.
6. **UNIT TEST & COVERAGE GATE (≥90%) — MANDATORY, same run**: After the story's implementation is complete, execute the Unit Test & Coverage step defined in `code-generation.md` (Step 11a): generate unit tests for all new/changed code, RUN them, measure coverage, and if coverage is below **90%** add/adjust tests (and fix any defects the tests expose) within the SAME run until ≥90% is reached. While the story is still `🔵 In Development`, **capture the PROOF artifacts of this run** to `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/` — the raw runner output (`unit-test-run.log`), the coverage tool's **mandatory machine-readable report** (`coverage-report.*` — lcov/xml/json/HTML, produced by running the tool with the report-emitting flags such as `--cov-report=xml` / `--coverageReporters=lcov`; a terminal summary alone does NOT satisfy the gate), and an `evidence-manifest.md` (command run, tests X/X, measured coverage %, artifact links). These stored artifacts — not a hand-written claim — are the evidence carried into Code Review and the PR/Jira comment; every figure reported downstream MUST match them.
6.5. **🧪 FULL REGRESSION GATE (MANDATORY, AUTOMATIC — after the Unit Test & Coverage gate, same run)**: re-run the **ENTIRE repo test suite** (all pre-existing tests + this story's new tests), save the raw output to `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/full-regression.log`, and diff it against `baseline-regression.log` from Step 1.5 Item 4.5. **No user prompt — fix and continue.**
   - **NEW failures (green at baseline, red now)** → **this story broke them, so this story fixes them.** Fix them within THIS SAME run, then re-run and re-diff, iterating until the diff is clean — never hand a new failure back to the user. Fix each according to what actually broke, and a failing test is NEVER "fixed" by deleting or skipping it to make the suite green:
     - **Obsolete expectation** — behaviour legitimately changed, the assertion encodes the old contract → **update the assertion** (keep the test; it still guards real behaviour)
     - **Genuinely dead** — exercises a code path this story removed → **delete it** and confirm this story's new tests cover the replacement path
     - **Real regression** — the test is correct and the implementation broke it → **fix the implementation, never the test**
   - **Failures already red at baseline** → not this story's doing. Already logged in `baseline-regression.log`; ignore them and do not block on them.
   - Proceed to Code Review only once the diff is clean (zero NEW failures).
   - Record in `evidence-manifest.md`: baseline vs post-change pass/fail counts, and each NEW failure with what broke and how it was fixed. **Audit the diff in audit.md.**
7. **POST-IMPLEMENTATION — status stays `🔵 In Development` until the PR is MERGED**: Do NOT change the tracker status here, and do NOT prompt for a board status. The story **remains `🔵 In Development`** through the automated Code Review (Section A), any Remediate loop (Section C), the commit/push/**PR raise** (Section D), and the automated PR Review (Section E). Raising the PR does **NOT** promote it. The story moves to `🧪 Ready for Testing` **only when its PR is MERGED into the epic branch** — and SDET has signed it off with the `sdet-list-work` skill (dev-implement itself only ever live-checks a specific prerequisite's merge state at its own Doability Gate — it never promotes tracker/Jira status). The developed ticket is recorded as a full Jira hyperlink in `aipdlc-docs/audit.md`:
   - **MANDATORY — record the developed ticket as a full Jira hyperlink in `aipdlc-docs/audit.md`**: for a Jira-linked story, resolve the site base URL (from `getAccessibleAtlassianResources`, or reuse the base already recorded in `aipdlc-docs/`) and write the ticket as a clickable Markdown link `[PROJ-XXX](<site-base-url>/browse/PROJ-XXX)` in the audit entry for this implementation — never bare text. When the PR is raised (Section D) record the PR URL and that the story stays `🔵 In Development` (Merged=no); when the PR later merges, record the promotion to `🧪 Ready for Testing` with evidence (tests passing + measured coverage % ≥90%). For local-only stories (`Jira = —`), record the local Story ID instead. Example entry:
      ```markdown
        ## [Stage Name or Interaction Type]
         **Timestamp**: [ISO timestamp]
         **User Email**: [current session email — read live from the session context]
         **User Input**: "[Complete raw user input - never summarized]"
        **JIRA TICKET**: "[Complete JIRA Ticket that was implemented]"
        **Epic Link**: "[Full Parent Epic URL as a clickable link, from ## Jira in aipdlc-state.md — or "none"]"
        **AI-PDLC VERSION**: "[Framework version [N] read from the "AI-PDLC Framework Version" line in CLAUDE.md — do not hardcode]"
       **AI Response**: "[AI's response or action taken]"
       **Context**: [Stage, action, or decision made]
   
---      ```
8. **Update Dependency Graph**: After a story reaches `🧪 Ready for Testing` (i.e. its PR merged and SDET signed it off via `sdet-list-work`), recompute the ready set — stories whose `requires` are now all `🧪 Ready for Testing` become selectable.
9. **MANDATORY**: Present the code-generation completion announcement as defined in `code-generation.md` Step 14 (Code Generation Complete + file summary). This announces completion only — it does NOT ask the user to choose between review and continue anymore.
10. **AUTO-TRIGGER Code Review (MANDATORY — no longer user-selected)**: As soon as code generation for the story is done, automatically proceed into the **Post-Code-Generation Automation** section below. Code Review runs on its own; the user is NOT asked whether to run it.
11. **MANDATORY**: Log every user response in this stage in audit.md with complete raw input.

---

# Post-Code-Generation Automation — Auto Code Review → (Remediate) → Commit / Push / PR

**Runs automatically once Code Generation Part 2 completes for the story. The user is NOT asked whether to review — Code Review is triggered automatically.** The target branch for the commit/push/PR is the branch resolved in Step 1.5 (newly created, or the current branch).

## A. Auto Code Review (MANDATORY, automatic)
1. **Log** in audit.md that automated Code Review is starting for Story [N.M] (ISO 8601 timestamp).
2. **Run Code Review for this story**: load and execute `workflows/code-review.md` scoped to **this specific story** (target = "story [N.M]"), as a **read-only** review (it MUST NOT edit source). It produces the versioned report at `aipdlc-docs/construction/reviews/story-[N.M]-code-review-v[X].md`. Code Review does **NOT** change the tracker status — the story stays `🔵 In Development`.
   - **⚡ NO TEST RE-RUN**: the Unit Test & Coverage gate (Step 6) measured coverage on this story's new/changed code to ≥90%, and the Full Regression Gate (Step 6.5) ran the ENTIRE repo suite and diffed it against the Step 1.5 baseline — both in THIS same run, with proof artifacts saved under `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/` (`unit-test-run.log`, `coverage-report.*`, `baseline-regression.log`, `full-regression.log`, `evidence-manifest.md`). Pass that captured evidence into the review — Code Review MUST NOT re-execute the unit tests or re-measure coverage; it verifies test existence/AC coverage statically and **cites the stored proof artifacts** (link `unit-test-run.log` + `coverage-report.*` and quote the tests X/X passing + measured coverage % from `evidence-manifest.md`) in its report, rather than restating unverified numbers.
3. **MANDATORY — audit the complete review log**: append to `aipdlc-docs/audit.md` the full Code Review outcome — the `**JIRA TICKET**:` and `**Epic Link**:` fields, report path, review verdict, and the complete list of findings by severity (🔴 Blocker / 🟠 High — the only severities; findings map strictly to unmet/partially-met ACs and requirements), plus any Jira/tracker status change. Do not summarize away findings; record the complete log of this automated review.
4. Proceed to **B. Review Decision Gate**.

## B. Review Decision Gate (MANDATORY)
1. **Log the prompt** in audit.md — with a plain heading like `## Review Decision Prompt (Story N.M)`; **the word "GATE" must NOT appear in the prompt entry's heading** ("GATE 3" belongs only on the response entry, Step 4) — then present (verbatim):
   ```
   🔍 Automated Code Review complete for Story [N.M].
   Report: aipdlc-docs/construction/reviews/story-[N.M]-code-review-v[X].md
   Verdict: [clean — all ACs Met / findings: 🔴 X  🟠 Y]

   ❓ What next?
     A) ✅ Approve & continue — commit, push to branch `<target-branch>`, and raise the PR
     B) 🔧 Remediate        — fix the review findings first
   [Answer]:
   ```
2. **On A (Approve & continue)** → go to **D. Commit, Push & Raise PR**.
3. **On B (Remediate)** → go to **C. Remediate Loop**.
4. **MANDATORY**: Log the user's raw response in audit.md. **🚧 This decision is GATE 3** — the gate is marked in the response entry's `##` HEADING (there is NO separate `**GATE Number**:` field), on BOTH outcomes:
   - A: `## Review Decision — GATE 3 Approved & Continue (Story N.M)`
   - B: `## Review Decision — GATE 3 Not Approved — Remediate (Story N.M)`
   Entry body format is unchanged; the prompt entry never carries the gate marker.

## C. Remediate Loop (on Remediate)
1. **Log** in audit.md that Remediate is starting for Story [N.M], naming the review report being remediated.
2. **Run Remediate**: load and execute `workflows/remediate.md` scoped to **this story's** review report (`story-[N.M]-code-review-v[X].md`). It fixes findings (fix → unit test → green, running ONLY this story's unit tests) and annotates the report in place. Remediate does **NOT** change the tracker status — the story stays `🔵 In Development` throughout.
3. **MANDATORY — audit the complete remediate log**: append to `aipdlc-docs/audit.md` the full Remediate outcome — the `**JIRA TICKET**:` and `**Epic Link**:` fields, which findings were fixed (by severity), the files changed, unit-test evidence, and any tracker/Jira status change. Record the complete log, not a summary.
4. **Post-Remediate Decision Gate** — log the prompt with a plain heading like `## Post-Remediate Decision Prompt (Story N.M)` (**the word "GATE" must NOT appear in the prompt entry's heading** — "GATE 3" belongs only on the response entry, Step 5), then present (verbatim):
   ```
   🔧 Remediation complete for Story [N.M].
   ❓ What next?
     A) ✅ Approve & continue — commit, push to branch `<target-branch>`, and raise the PR
     B) 🔁 Re-review        — run automated Code Review again
   [Answer]:
   ```
   - **On A** → go to **D. Commit, Push & Raise PR**.
   - **On B (Re-review)** → return to **A. Auto Code Review** (produces the next report version `v[X+1]`), then **B. Review Decision Gate** again. This loop repeats until the user chooses Approve & continue.
5. **MANDATORY**: Log the user's raw response in audit.md. **🚧 This decision is GATE 3** — the gate is marked in the response entry's `##` HEADING (no separate field), on BOTH outcomes:
   - A: `## Post-Remediate Decision — GATE 3 Approved & Continue (Story N.M)`
   - B: `## Post-Remediate Decision — GATE 3 Not Approved — Re-review (Story N.M)`

## D. Commit, Push & Raise PR (on any Approve & continue)
1. **Log** in audit.md that the user approved and the commit/push/PR step is starting, naming the target branch.
2. **Commit the story's changes to the target branch**:
   - Confirm the active branch is the target branch from Step 1.5 (`git branch --show-current`). If it is not, switch to it (confirm-first).
   - Stage and commit the generated/remediated application code (do NOT commit unrelated changes). The commit message MUST carry an `AI-PDLC-Version:` trailer as the framework signature, where `[N]` is read at runtime from the "AI-PDLC Framework Version" line in `CLAUDE.md` (do not hardcode a number). Use a clear message, e.g.:
     ```
     git add <story files>
     git commit -m "[Story N.M / JIRA-KEY] <concise summary of the implemented story>" -m "AI-PDLC-Version: [N]"
     ```
     The `AI-PDLC-Version: [N]` trailer goes on its own line at the end of the message body (alongside any existing trailers), with `[N]` substituted from the CLAUDE.md canonical line.
   - Record the commit hash in audit.md.
3. **Push & raise the PR via the `pr-generator` skill (used as-is — DO NOT edit it)**:
   - Invoke the **`pr-generator`** Claude skill, passing **target branch = the Epic Branch** from `aipdlc-state.md` `## Branching` — story PRs merge into the epic branch, NEVER into main/the base branch. The skill diffs the story branch against the target, reads `aipdlc-state.md` + `audit.md` for context, drafts the PR title/body (the title MUST carry the **`[STORY]`** prefix — this is a story → epic-branch PR), gets its own explicit confirmation, then pushes the branch, ensures the `ai-generated` and `aipdlc-v[N]` labels, and opens the PR.
   - The pr-generator's confirmation gate (its Phase 5) is honored — do not bypass it.
4. **MANDATORY**: Record in audit.md the PR outcome returned by pr-generator (branch pushed, PR URL, labels applied — `ai-generated` + `aipdlc-v[N]`), including the `**JIRA TICKET**:` and `**Epic Link**:` fields.
5. **STORE THE PR AND KEEP THE STORY `🔵 In Development` (do NOT promote on PR raise)**:
   - In `aipdlc-docs/aipdlc-state.md` `## Story Tracker`, for this story set **PR** → the PR URL returned by pr-generator, **Merged** → `no`, **Recorded** → current timestamp. **Do NOT change Status** — the story **remains `🔵 In Development`**. Raising the PR is NOT the promotion trigger; **merging** it is.
   - **Do NOT transition Jira here** and do NOT set `End`. The story moves to `🧪 Ready for Testing` — in the tracker AND on the Jira board — ONLY when its PR is confirmed MERGED, handled by the `sdet-list-work` skill (dev-implement's own Doability Gate live-checks a prerequisite's merge state when needed, but never promotes this story's tracker/Jira status itself).
   - **MANDATORY** — record in `aipdlc-docs/audit.md` (per Step 7 above) the developed ticket as a full Jira hyperlink, the PR URL, and that the story stays `🔵 In Development` pending merge (Merged=no).
6. **Ready set unchanged**: because the story is still `🔵 In Development` (not `🧪 Ready for Testing`), it does NOT yet unblock dependents. Dependents become selectable only after this story's PR merges and it is promoted to `🧪 Ready for Testing`. (This aligns with the branch-cut dependency-merge check in `common/branching-strategy.md` — a dependent needs its prerequisite's code MERGED into the epic branch.)
7. **🔷 EPIC → Ready for Testing (only when ALL PRs are MERGED)**: The epic moves to Ready for Testing only when EVERY story is `🧪 Ready for Testing` (i.e. every PR merged). Since the just-raised PR is not merged yet, this typically does NOT fire here — it fires from the `sdet-list-work` skill once the last PR merges and SDET has signed every story off. **If this is the last story and one or more PRs are still open**, do NOT move the epic — instead report:
   ```
   ✅ Story [N.M] PR raised (kept 🔵 In Development until merged).
   ✋ As checked, these story PRs are still OPEN — hence keeping their status as 🔵 In Development,
      and the Parent Epic stays In Development until every PR is merged:
        • Story [X.Y] — [JIRA-KEY] — <PR URL>
        • ...
   ➡️ Merge those PRs, then SDET (on the epic branch) uses the skill `sdet-list-work` — it lists the
      merged stories, and promotes the ones SDET has tested to 🧪 Ready for Testing; when ALL are
      signed off, the Epic is offered a move to Ready for Testing. The exact instructions are repeated in the Section F handoff below.
   ```
   Only when `sdet-list-work` later leaves EVERY story `🧪 Ready for Testing` is the Parent Epic (from `## Jira`) offered a confirm-first transition to "Ready for Testing" (verified, logged). Skip the epic transition silently if `## Jira` records `Parent Epic: none`.
8. Proceed to **E. Auto PR Review**.

## E. Auto PR Review (MANDATORY, automatic — runs right after the PR is raised; story is still `🔵 In Development`)
1. **Log** in audit.md that automated PR Review is starting for Story [N.M], naming the PR URL/number from Section D.
2. **Invoke the `pr-review` Claude skill** (`.claude/skills/pr-review/`, used as-is — DO NOT edit it) in its **AUTO MODE**, passing the PR just raised in Section D so it does not need to ask which PR (its Phase 0 is satisfied automatically). It reads the diff, grounds itself in `aipdlc-state.md` + `audit.md`, and drafts inline comments + a summary review.
3. **AUTO MODE — post automatically, comments only, no prompt**: the skill posts the review **without asking the user** (its Phase 5 confirmation is skipped by design in this mode) and **only as a plain COMMENT review** (summary + inline comments) — NEVER a formal GitHub `APPROVE`/`REQUEST_CHANGES`. The same GitHub identity that just raised the PR is posting the review, so a formal self-review is impossible; there is no decision for the user to make here. Do not re-introduce a prompt around the skill.
4. **MANDATORY**: Record in audit.md the outcome — review posted automatically (AUTO MODE, comment-only), the posted review URL, findings summary, and the `**JIRA TICKET**:` and `**Epic Link**:` fields.
5. Proceed to **F. Next-Action Handoff** — this run is NOT complete until that message is shown.

## F. 🎯 Next-Action Handoff (MANDATORY — the LAST thing this run outputs)

**This message closes every `dev-implement` run that raised a PR. It is not optional and it is not a summary — it tells the user the EXACT actions and the EXACT keyword to type next.** The story is `🔵 In Development` with an unmerged PR; nothing advances until the user merges it and runs the next keyword.

1. **Determine the remaining work first** — count the stories in the `## Story Tracker` that are still `🟢 Ready for Development` (call it `[K]`), and whether this story was the **last** one (no story is `🟢 Ready for Development` and no other story is `🔵 In Development` with an unmerged PR).
2. **Present EXACTLY ONE of the two blocks below (verbatim, placeholders substituted).** Show the `[K] stories remain` block when `K > 0`; show the `LAST story` block when this was the final story.

   **Case 1 — more stories remain (`K > 0`)**:
   ```
   🔀 PR RAISED — NOT MERGED. Story [N.M] stays 🔵 In Development until this PR merges.
      PR: <PR URL>  →  target branch: `<epic-branch>`

   ➡️ NEXT ACTIONS — do these in order:
      1️⃣  Merge the PR above into `<epic-branch>` (your decision — the framework never merges for you).
      2️⃣  Switch back to the epic branch
      3️⃣  Type this keyword to continue: dev-implement
          It lets you pick the next story — if that story `requires` Story [N.M], the Doability
          Gate live-checks THIS PR's merge state before proceeding; not merged yet → it stops and
          tells you to merge first. [K] stor[y/ies] still 🟢 Ready for Development.
          (Story [N.M]'s own tracker status stays 🔵 In Development until SDET runs `sdet-list-work`.)

   🔴 Type the keyword `dev-implement` EXACTLY as shown — do not describe what you want in your own
      words. Any other phrasing is not a framework trigger and the workflow will not advance.
   ```

   **Case 2 — this was the LAST story of the epic**:
   ```
   🔀 PR RAISED — NOT MERGED. Story [N.M] (the LAST story of epic [EPIC-KEY]) stays 🔵 In Development
      until this PR merges.  PR: <PR URL>  →  target branch: `<epic-branch>`

   ➡️ NEXT ACTIONS — do these in order:
      1️⃣  Merge the PR above into `<epic-branch>`.
          [IF other story PRs are still open, list them here and state that ALL of them must be
           merged before step 3 can complete:
             • Story [X.Y] — [JIRA-KEY] — <PR URL>  (still OPEN)]
      2️⃣  Switch to the epic branch:
      3️⃣  Hand over to SDET — they type this skill: sdet-list-work  (then pick Option B)
          It lists every story whose PR has merged, SDET tests them, names the ones it has finished
          testing, and those move to 🧪 Ready for Testing (tracker + Jira, verified). When ALL are
          signed off it offers the Parent Epic move and points at `pr-generator` for the Epic PR.
          (SDET's Build and Test steps for each story come from `/sdet-implement <story>`, run in parallel.)

   🔴 Type the keyword `sdet-list-work` EXACTLY as shown — do not describe what you want in your own
      words. Any other phrasing is not a framework trigger and the workflow will not advance.
   ```
3. **Say NOTHING after this block** — no options menu, no extra suggestions, no "let me know if…". The handoff message is the end of the run.
4. **MANDATORY**: log in audit.md which case was presented (more-stories vs last-story) and the keyword the user was told to type.

---

## 🔄 Jira Sync Rule (reminder)

This workflow changes story status (`🟢 Ready for Development` → `🔵 In Development` at story selection, then `🔵 In Development` → `🧪 Ready for Testing` **when the PR is MERGED** — NOT when it is raised). The **Jira Sync Rule** in `CLAUDE.md` applies at every status change:
- If **Jira = `—`** (local story): update only the local tracker.
- If **Jira = `PROJ-XXX`**: also transition the Jira issue via the Atlassian MCP and verify the transition. Never silently update only one side.
- **Exception — story transitions are automatic**: the `🟢 → 🔵 In Development` transition at story pick is applied to Jira AND the tracker WITHOUT asking (picking the story is the claim), and the `🔵 → 🧪 Ready for Testing` transition on confirmed PR merge is likewise applied WITHOUT asking (the merged PR is the trigger) — both verified + announced. Only non-story transitions (e.g., the Parent Epic moves) remain **confirm-first**.
- **Assignee on claim**: when the story moves to `🔵 In Development`, the Jira issue is ALSO **assigned to the operator who typed `dev-implement`** — resolve the session email (the same one stamped as `**User Email**:` in audit.md) via `lookupJiraAccountId`, set the assignee via `editJiraIssue`, verify, announce, log in audit.md. Automatic (part of the same claim, no confirmation). If the email doesn't resolve to a Jira account, leave the issue unassigned, warn the user, and continue — never block development on assignment.
- **Ready for Testing = PR merged**: a story moves `🔵 In Development` → `🧪 Ready for Testing` ONLY when its PR is confirmed MERGED AND SDET has named it in the `sdet-list-work` skill after testing it (verified + announced + logged). dev-implement never promotes it. Raising the PR stores the PR URL and keeps the story `🔵 In Development` (`Merged=no`).
- **Epic status sync**: when the FIRST story moves to `🔵 In Development`, the Parent Epic is transitioned to "In Development" **automatically** (Story Selection Step 5); when the LAST story reaches `🧪 Ready for Testing` (all PRs merged), the Parent Epic is transitioned to "Ready for Testing" **confirm-first** (from `sdet-list-work`). Both are verified and logged in audit.md.

---

## Critical Rules
- 🔴 EVERY audit.md entry in this workflow — selection, branching, planning, generation, coverage, review, remediate, PR — MUST carry the `**User Email**:` (current session email), `**JIRA TICKET**:`, `**Epic Link**:` (full Parent Epic URL from `## Jira` in aipdlc-state.md, or `none`) AND `**AI-PDLC VERSION**:` fields (version read at runtime from the "AI-PDLC Framework Version" line in `CLAUDE.md` — never hardcoded). See the Audit Entry Format section above.
- 🔴 EVERY story commit MUST carry the `AI-PDLC-Version: [N]` trailer (framework signature, read live from `CLAUDE.md`) — see Section D Step 2.
- 🔴 ALWAYS show the sequential-development banner (Step 1.75) on every invocation, BEFORE Story Selection — one story at a time per session; parallel development happens in a separate folder/clone on an independent story.
- 🔴 NEVER guess which story to implement — always ask and wait.
- 🔴 PLAN GUARDRAIL: the code-generation plan MUST be grounded in the previously generated docs (story acceptance criteria, epic-brief, requirements, design artifacts), and coding MUST follow the approved plan exactly — any needed deviation goes back through GATE 2 for re-approval, never applied silently.
- 🔴 REQ-ID THREAD: `requirements.md` + the story's `Covers` REQ-IDs are MANDATORY planning inputs; every plan step is tagged with the REQ/AC it implements and the trace completeness self-check (every covered REQ-ID and every AC in ≥1 step) MUST pass before GATE 2. If `aipdlc-state.md` has no `Requirements coverage verified post-design` record, run the Rule 4 fallback verification (silent, blocking) before planning. See `common/requirements-traceability.md`.
- 🔴 ALWAYS create the story branch (Step 1.5) right after Story Selection — cut from the refreshed EPIC branch per `common/branching-strategy.md`, NEVER from main/the base branch or a dependency branch — and run the dependency-merge check BEFORE any code is generated: if any prerequisite is unmerged into the epic branch, WARN AND STOP and tell the user to merge it first.
- 🔴 NEVER bypass the Doability Gate — a story is doable only when ALL its `requires` are confirmed MERGED: either already `🧪 Ready for Testing` in the tracker, or live-verified via `gh pr view` at gate time (`construction/story-selection.md` Step 4). Any prerequisite that is neither → 🛑 STOP the run with a clear message naming it; do NOT loop back and do NOT let the user bypass it.
- 🔴 The ONLY valid Story Tracker statuses are `🟢 Ready for Development`, `🔵 In Development`, and `🧪 Ready for Testing`. The story stays `🔵 In Development` through code generation, Code Review, Remediate, the PR raise, AND the auto PR Review; it becomes `🧪 Ready for Testing` ONLY when its PR is confirmed **MERGED** into the epic branch, promoted exclusively by the `sdet-list-work` skill, on SDET's explicit say-so. Raising the PR NEVER promotes the story, and NEITHER does a later `dev-implement` run — it only ever live-checks a specific prerequisite's PR at its own Doability Gate.
- 🔴 At Section D, when the PR is raised, STORE the PR URL in the Story Tracker (`PR` column, `Merged=no`) and keep the story `🔵 In Development` — do NOT transition Jira or set `End` here.
- 🔴 dev-implement does NOT bulk-reconcile or promote prior `🔵 In Development` stories at the start of a run (Step 1.5) — that promotion is exclusively the `sdet-list-work` skill's job. dev-implement only ever live-checks the PR-merge state of a SPECIFIC prerequisite, at the Doability Gate, when a story that `requires` it is being selected — and STOPS the run with a clear message if that prerequisite isn't merged yet.
- 🔴 ALWAYS enforce the Unit Test & Coverage gate: after implementation, generate unit tests, RUN them, and iterate within the same run until coverage on the story's new/changed code is **≥90%** — never mark the story done below that threshold without surfacing it to the user with a reason.
- 🔴 ALWAYS run the BASELINE regression (entire repo suite) on the story branch BEFORE any code is generated (Step 1.5 Item 4.5) and the FULL regression AFTER the Unit Test & Coverage gate (Step 6.5), then diff them. Both runs are **automatic — never prompt the user for either**. Failures NEW vs the baseline were broken BY this story, so this story **fixes them in the same run** — iterate until the diff is clean, fixing each according to what broke (update an obsolete expectation / delete a genuinely dead test / fix the implementation for a real regression). **NEVER delete, skip, or weaken a failing test merely to make the suite green, and NEVER hand a new failure back to the user.** Failures already red at baseline are not this story's doing — they are logged in `baseline-regression.log` and ignored. The ≥90% coverage gate is scoped to the story's new code and does NOT substitute for this — coverage on new code says nothing about assertions the change invalidated in pre-existing shared test files.
- 🔴 ALWAYS capture the TEST PROOF artifacts from that same run before leaving `🔵 In Development` — save the raw runner output (`unit-test-run.log`), the coverage tool's **mandatory machine-readable report** (`coverage-report.*` — lcov/xml/json/HTML), and `evidence-manifest.md` to `aipdlc-docs/construction/code/unit-test-evidence/story-[N.M]/`. Run the tool with the flags that emit the report file; a terminal summary alone does NOT satisfy the gate — when the stack HAS coverage tooling, no coverage-report file means the gate is not met, STOP and surface it. The only waiver is a stack with genuinely NO coverage-report tooling, and that must be a documented, user-surfaced exception in `evidence-manifest.md` — never a silent skip. Evidence is the actual tool output, never a hand-written claim; every X/X-passing and coverage-% figure in the completion message, Code Review report, and PR/Jira comment MUST match these stored artifacts.
- 🔴 After Code Generation, ALWAYS auto-run Code Review (`workflows/code-review.md`) — it is no longer user-selected — and audit its complete log in audit.md before presenting the Approve/Remediate decision.
- 🔴 NEVER commit, push, or raise a PR until the user explicitly chooses "Approve & continue". Commit to the story branch from Step 1.5, then push + raise the PR ONLY via the `pr-generator` skill (used as-is), passing **target branch = the Epic Branch**. Story PR titles MUST carry the **`[STORY]`** prefix (pr-generator applies it).
- 🔴 EPIC STATUS SYNC: on the FIRST story pick, the Parent Epic moves to "In Development" automatically; when ALL stories are `🧪 Ready for Testing` (i.e. ALL PRs merged), offer (confirm-first) to move the Parent Epic to "Ready for Testing". Verify every epic transition and log it. If the last story's PR is raised while other PRs are still open, do NOT move the epic — report the open PRs and keep everything `🔵 In Development`.
- 🔴 After the PR is raised (the story STAYS `🔵 In Development` — it is NOT yet Ready for Testing), ALWAYS auto-invoke the `pr-review` skill (used as-is) against that PR in **AUTO MODE** — it posts automatically as a plain COMMENT review (summary + inline comments) with NO user prompt and NEVER a formal GitHub APPROVE/REQUEST_CHANGES (the PR author's own identity cannot formally self-review). The skill's Phase 5 confirmation applies only to standalone runs.
- 🔴 EVERY run that raises a PR MUST end with the **Section F Next-Action Handoff** — the exact merge instruction, the switch to epic branch command, and the ONE keyword to type (`dev-implement` when stories remain, `sdet-list-work` when this was the last story). Never end a run with a bare "PR raised" summary, and never leave the next step to the user's own words. Nothing is output after the handoff block.
- 🔴 On Remediate, ALWAYS audit the complete remediate log and then offer "Approve & continue" or "Re-review"; on Re-review, loop back through automated Code Review.
- 🔴 STORY Jira transitions are **automatic** (no confirmation): `🔵 In Development` at story pick, and `🧪 Ready for Testing` when the PR is confirmed MERGED. Any OTHER Jira transition (e.g., the Parent Epic moves) requires explicit user confirmation. ALWAYS verify every transition landed and log it in audit.md.
- 🔴 At story pick, ALWAYS set the Jira assignee to the operator who invoked `dev-implement` (session email → `lookupJiraAccountId` → `editJiraIssue`; automatic, verified, logged). Unresolvable email → leave unassigned, warn, continue — assignment failure never blocks development.
- 🔴 ALWAYS update the Story Tracker (and `Recorded` timestamp) on every status change.

---
