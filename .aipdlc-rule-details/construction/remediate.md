# Remediate - Detailed Steps

**Purpose**: Fix defects identified in a code-review report — **story-wise** (from a `story-[N.M]` report) or **across all stories** (from an `all-stories` report) — using fix → unit test → green — and annotate the report in place with resolution evidence.

> 🔎 **Report format intake** (matches what `construction/code-review.md` produces): issues are named `ISS-XXX` (story reports) or `S[N.M]-ISS-XXX` (all-stories reports), each tied to a specific **AC/Requirement**, with ONLY two severities — **🔴 Blocker** (AC/requirement Not Met, or a defect that breaks it) and **🟠 High** (AC/requirement Partially Met / deviates from spec). There are no 🟡 Medium / 🟢 Low findings.

**Recommended execution**: Run as a **code-editing workflow**, scoped strictly to the issues in the named report.

## Agent Role
**DEV** — fixes code based on a review report; every fix lands with a unit test.

## Before Starting
- [ ] **Check for reports** (do NOT read yet): `aipdlc-docs/construction/reviews/story-*-code-review-v*.md` and `aipdlc-docs/construction/reviews/all-stories-code-review-v*.md`
- [ ] If none exist, **STOP**: "Run Code Review (construction/code-review.md) first to produce a report to remediate from."

---

## Step 1 — Tell Me Which Report to Remediate (ask FIRST)

**Never guess.** Enumerate the newest version per story (plus the newest all-stories report) and present all available reports:

```
Which report should I remediate from?

📝 CODE REVIEW REPORTS (aipdlc-docs/construction/reviews/):
  STORY REPORTS (fix one story):
  1. story-1.2-code-review-v2.md      — ❌ CHANGES REQUESTED  (2 🔴, 1 🟠)
  2. story-2.1-code-review-v1.md      — ⚠️ APPROVED WITH COMMENTS (0 🔴, 3 🟠)
  ALL-STORIES REPORTS (fix across all stories):
  3. all-stories-code-review-v1.md    — ❌ CHANGES REQUESTED  (1 🔴, 4 🟠)

Type your choice (e.g., "1"):
```

Read the chosen report end-to-end before touching code.

## Step 2 — Load Review Target Context
- [ ] **Determine report type** from the filename:
  - `story-[N.M]-*` → story report: read the story from `aipdlc-docs/inception/user-stories/stories.md` — acceptance criteria, IN/OUT of scope
  - `all-stories-*` → all-stories report: read the `## Story Tracker` in `aipdlc-docs/aipdlc-state.md` and, for every story that has issues in the report (per the `S[N.M]-ISS-*` prefixes / per-story sections), its acceptance criteria from `stories.md`
- [ ] Read the related code summaries from `aipdlc-docs/construction/code/` and the actual files named in the report's File column

## Step 3 — Build Remediation Backlog & Confirm Scope
- [ ] Build a backlog from the report: `{id, severity, ac/requirement, file:line, summary}` (issue IDs are `ISS-XXX`, or `S[N.M]-ISS-XXX` in all-stories reports — keep the ID exactly as the report names it)
- [ ] **Skip already-resolved items** — any issue already carrying a `Status: ✅ Resolved` marker (re-entrant; surface the skipped count)
- [ ] **Severity scope**: reports contain only 🔴 Blocker + 🟠 High — BOTH are MANDATORY to fix (an issue is always an unmet/partially-met AC or requirement); deferring any issue requires explicit user consent
- [ ] **MANDATORY: summarize the plan and HALT** until the user confirms:
  ```
  Remediation plan from <report>:
    Will fix:  🔴 ISS-001 — [AC-2, Story 1.2 — summary]   🟠 ISS-002 — [AC-3, Story 1.2 — summary]
  ❓ Proceed? (yes / adjust scope / cancel)
  ```
  Do NOT touch code before this confirmation.
- [ ] **Do NOT change the Story Tracker status.** Every story being remediated stays `🔵 In Development` — the ONLY valid statuses are `🟢 Ready for Development`, `🔵 In Development`, and `🧪 Ready for Testing`. You MAY refresh `Recorded` → now to note that remediation started, but leave `Status` unchanged.

## Step 4 — Remediate Per Issue

Iterate the backlog in severity order (🔴 → 🟠). For EACH issue:
- [ ] 1. **Apply the fix**: follow the report's "Suggested Fix" when sound; deviate only with a logged justification
- [ ] 2. **Write/Update a unit test** that reproduces the defect scenario against the fixed code; run it — must pass
- [ ] If the issue is non-testable — pure rename/doc — note this explicitly instead of a test
- [ ] **Run ONLY the unit tests of the story (or stories) in scope** — 100% pass; fix any breakage you cause immediately. Do NOT run the full repo suite or integration tests here
- [ ] **Mark the issue resolved in the report** (append a Resolution block — never delete original text)

## Step 5 — Annotate the Source Report (in place)
- [ ] **Stamp the top-of-report status banner** (template below): `✅ Resolved` if all in-scope issues fixed, else `🟡 Partially Remediated (X/Y)`
- [ ] Append a **Remediation Section** at the end of the report (template below)
- [ ] **Never create a separate remediation log file** — all evidence lives inside the source report (one source of truth)

## Step 6 — Record Remediation Outcome (NO Status Change)
- [ ] **Do NOT change the Story Tracker status.** Every story covered by the remediation stays `🔵 In Development` (it moves to `🧪 Ready for Testing` only when its PR is **merged** — promoted by the `sdet-list-work` skill once SDET has tested it). You MAY refresh `Recorded` → now, but leave `Status` unchanged.
- [ ] Because no status changes, there is normally **no Jira transition** here. If your team's process requires a board comment/move on remediation, apply the **Jira Sync Rule** (confirm-first, verify) with an evidence comment (tests X/X; coverage %) — but do NOT change the local tracker Status.
- [ ] Log the remediation outcome — findings fixed by severity, files changed, unit-test evidence — in `aipdlc-docs/audit.md` with timestamps

---

## Output

### Top-of-Report Status Banner (insert directly under the report's H1)
```markdown
> ## 🛠️ Remediation Status: ✅ Resolved
> - **Remediated**: [YYYY-MM-DD] by DEV (ai-pdlc)
> - **Fixed**: [N] issue(s) — 🔴 [a] / 🟠 [b]
> - **Deferred (with user consent)**: [M] — see Remediation Section
> - **Tests**: [P/P] passing | **Coverage**: [Z]%
```
(Use `🟡 Partially Remediated (X/Y)` if anything was deferred.)

### Per-Issue Resolution Block (append under each fixed issue)
```markdown
**Resolution** ([YYYY-MM-DD], DEV):
- Fix: [1-line description]
- Change ref: `path/file.ext:45-58`
- Test evidence: `path/file.test.ext` (all green)
- Status: ✅ Resolved
```

### Remediation Section (append to END of the report)
```markdown
---
# 🛠️ Remediation — [YYYY-MM-DD]
**Severity Scope**: 🔴 Blocker + 🟠 High
**Target**: [Story N.M | All Stories]

## Issues Remediated
| ID | Severity | AC/Requirement | File:Line | Summary | Resolution | Test Added |
|----|----------|----------------|-----------|---------|------------|------------|

## Issues Deferred (with user consent)
| ID | Severity | Reason |
|----|----------|--------|

## Files Changed
| File | Change Type | Description |
|------|-------------|-------------|

## Testing Summary
- Targeted tests added: [X]
- Story unit tests: [Y/Y] passing | Coverage: [Z]%

## Next Steps
- [ ] Re-request Code Review (construction/code-review.md) — required if any 🔴 fixed
```

> **Re-runs**: if a Remediation Section dated today already exists, replace it; older dates are kept (append a new dated section). Always update the top banner to the latest state.

---

## Rules
- 🔴 ALWAYS read the source report end-to-end before touching code
- 🔴 ALWAYS confirm scope BEFORE writing code — HALT until the user says proceed
- 🔴 Fix order is always fix → unit test → green. No fix lands without a test (unless non-testable — note it)
- 🔴 Run ONLY the in-scope story's unit tests after EVERY issue — NEVER the full repo suite or integration tests
- 🔴 Never silently downgrade a 🔴/🟠 — if you cannot fix it, STOP and surface it
- 🔴 Never modify the report's original issue text — only APPEND (banner, per-issue Resolution blocks, end Section). The `Status: ✅ Resolved` line is the idempotency marker; skip such items on re-runs
- 🔴 No Jira writes without explicit user confirmation, and always VERIFY

---

## After Remediation — Mandatory Next-Step Output
```
✅ Remediation complete — <report filename>
   Fixed: [X] (🔴[a] 🟠[b])  |  Deferred: [Y]
   Tests: [P/P] | Coverage: [Z]%

▶️ Next step:
1️⃣  Code Review (construction/code-review.md)  ← required if any 🔴 was fixed
2️⃣  Satisfied with the remediation? Raise a PR of these changes 

Type your choice.
```

**Exception — reached via `dev-implement`**: OMIT option 4️⃣ from the menu. That flow raises the PR itself at its "Commit, Push & Raise PR" stage after the Approve & continue decision — do not offer a second PR here.

Log this prompt and the user's complete raw choice in `aipdlc-docs/audit.md` with timestamps.

## Step 7 — On Choice 4️⃣: Raise the PR via pr-generator

When the user picks 4️⃣ (standalone invocations only):
1. Invoke the **`pr-generator` skill** (`.claude/skills/pr-generator`) via the Skill tool, passing the appropriate **target branch** (a story branch targets the Epic Branch from `aipdlc-state.md` `## Branching`; the epic branch targets the recorded Base Branch). Follow the skill EXACTLY as written — do NOT modify it or bypass its own confirmations (it handles uncommitted changes, pushes the branch, and raises the PR with confirm-first gates).
2. Log the resulting PR URL in `aipdlc-docs/audit.md` with timestamp.
3. If the user picks 1️⃣/2️⃣/3️⃣ instead, the changes stay local — a PR can be raised anytime later by invoking the pr-generator skill.
