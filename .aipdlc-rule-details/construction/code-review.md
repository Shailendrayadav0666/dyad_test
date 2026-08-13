# Code Review - Detailed Steps

> 🔴 **REVIEW-ONLY WORKFLOW.** The REVIEWER role MUST NOT edit source code, tests, or configs. It may write ONLY to `aipdlc-docs/construction/reviews/` and update the Story Tracker in `aipdlc-docs/aipdlc-state.md`. Findings are produced as a report; fixes are performed during **Remediate** (`construction/remediate.md`). If issues are found, this workflow MUST recommend Remediate as the next step.

**Purpose**: **Strictly verify that each story's acceptance criteria and mapped requirements are completed by the code — nothing more.** Produce a versioned review report. Reviews can target a **specific story** or **all stories together** (the full Story Tracker reviewed against the code in one pass).

> ⚖️ **SCOPE DISCIPLINE (HARD RULE)** — Report a finding ONLY if it is one of:
> 1. An **acceptance criterion NOT met** (or only partially met) by the code
> 2. A **requirement mapped to the story NOT implemented** as specified
> 3. A **genuine defect** (bug, crash, security hole, broken flow) that prevents an AC/requirement from actually working
>
> Do **NOT** report: style/naming/formatting nits, refactoring or SOLID suggestions, "could be improved" / "consider adding" / nice-to-have items, missing docs/comments, or hypothetical future concerns. **A clean review (zero findings) is a valid and expected outcome — NEVER invent findings to justify the review.** This review runs automatically after every `dev-implement`; padding it with advisory items creates endless remediate loops.

**Recommended execution**: Run as a **read-only workflow** (no code-editing tools) so the reviewer physically cannot modify source. The orchestrator reads the returned report path and verdict.

## Agent Role
**REVIEWER** — analyzes and reports only.

---

## Tell Me What to Review

**DO NOT guess what to review. Present this prompt and wait:**

```text
What would you like me to review?

Options:
  a) A specific story                    (e.g., "story 1.2" — remediate can then fix that story alone)
  b) All stories together against the code   (type "all stories")
```

**Then, based on the answer, resolve the review target:**
- **Story**: identify the story number (e.g., N.M) and confirm it exists in the Story Tracker.
- **All stories**: every story in the `## Story Tracker` whose implementation has begun — Status `🔵 In Development` or `🧪 Ready for Testing` — is in scope. **EXCLUDED**: `🟢 Ready for Development` stories (no code yet). Note that a `🔵 In Development` story may still be mid-build (actively claimed by a developer, or awaiting its PR) — call this out so the user knows the review reflects its current, possibly-incomplete state. List the in-scope story IDs AND the excluded IDs (with reason) back to the user before starting.

---

## Phase 0: Review History Check (Prevents Endless Loops)

Before reviewing, ALWAYS check for a previous report matching the review target, then determine the review mode. Apply the rules below for the chosen target.

### If reviewing a story (story N.M)
1. **Previous review** — Does `aipdlc-docs/construction/reviews/story-[N.M]-code-review-v*.md` exist? If yes, read the latest version; note its status (APPROVED / CHANGES REQUESTED) and prior issues. **Also check** for a newer `all-stories-code-review-v*.md` that covers this story — if one exists and is newer, surface its findings for this story so they are not double-reported or missed.
2. **Determine review mode**:
   - No previous review → **INITIAL_REVIEW** (🔴 + 🟠 — the only severities in this review)
   - Previous APPROVED + code unchanged → **SKIP**: "✅ Story [N.M] already approved. Code unchanged since last review."
   - Previous APPROVED + code changed → **NEW_CHANGES** (🔴 + 🟠 in changed files only)
   - Previous CHANGES REQUESTED → **FIX_VERIFICATION** (verify prior issues fixed + new 🔴/🟠 only)

### If reviewing all stories
1. **Previous review** — Does `aipdlc-docs/construction/reviews/all-stories-code-review-v*.md` exist? If yes, read the latest version; note its status (APPROVED / CHANGES REQUESTED) and prior issues per story. **Also check** individual `story-*-code-review-v*.md` reports newer than the last all-stories report — carry their open issues into this review so nothing is lost between the two report types.
2. **Determine review mode**:
   - No previous review → **INITIAL_REVIEW** (🔴 + 🟠 — the only severities in this review)
   - Previous APPROVED + code unchanged → **SKIP**: "✅ All stories already approved. Code unchanged since last review."
   - Previous APPROVED + code changed → **NEW_CHANGES** (🔴 + 🟠 in changed files only)
   - Previous CHANGES REQUESTED → **FIX_VERIFICATION** (verify prior issues fixed + new 🔴/🟠 only; apply per-story)

---

## Phase 1: Preparation
1. **Load review scope** — varies by review target:

   **If reviewing a story:**
   - [ ] Read the story from `aipdlc-docs/inception/user-stories/stories.md`
   - [ ] Extract its acceptance criteria
   - [ ] Identify the files implementing this story (from `aipdlc-docs/construction/code/` summaries and the actual workspace code)
   - [ ] Note what is IN and OUT of scope

   **If reviewing all stories:**
   - [ ] Read the `## Story Tracker` in `aipdlc-docs/aipdlc-state.md` — enumerate every in-scope story (Status `🔵 In Development` or `🧪 Ready for Testing`; exclude `🟢 Ready for Development`)
   - [ ] For every in-scope story, read its acceptance criteria from `aipdlc-docs/inception/user-stories/stories.md`
   - [ ] Read `aipdlc-docs/inception/application-design/application-design.md` (if Application Design ran) and `aipdlc-docs/inception/requirements/epic-brief.md` (if captured) for structural context — used only to locate code
   - [ ] Identify all implementation files (from `aipdlc-docs/construction/code/` summaries and workspace code)
   - [ ] Group findings by story in the report

2. **Read context** — error handling, logging, naming, and testing patterns from the design artifacts and any enabled extensions
3. **Read the code** — open all files to review, trace the main flows

## Phase 2: AC & Requirements Verification (the ONLY review checklist)
- [ ] **Acceptance Criteria — verify each one**: for EVERY acceptance criterion of every in-scope story, trace the code and record a verdict:
  - ✅ **Met** — cite the evidence (`file:line` of the implementing code)
  - ⚠️ **Partially Met** — state exactly what part of the AC is missing or deviates from the spec
  - ❌ **Not Met** — state what is absent
- [ ] **Requirements coverage**: verify each requirement mapped to the story (from `requirements.md` / the story narrative) is implemented as written — same Met / Partially Met / Not Met verdicts with evidence
- [ ] **Genuine defects only**: report a bug, crash, security hole, or broken flow ONLY when it prevents an AC/requirement from actually working (e.g., the AC's flow throws, auth required by the story is absent, data required by an AC is never persisted)
- [ ] **Tests as AC evidence — STATIC check only, never re-run**: verify unit tests covering the ACs exist by READING them (they were generated + executed to ≥90% coverage during Code Generation's Unit Test & Coverage step). **Do NOT re-execute the unit test suite or re-measure coverage in this review** — when invoked via `dev-implement`, the gate just ran in the same session; reuse the passed-in/audit-recorded results (tests X/X passing, coverage %) as the report's evidence. Report a finding ONLY if an AC has no verification at all — do not nitpick test style or demand extra tests beyond the ACs
- [ ] **Extension compliance** — if any extensions are enabled in `aipdlc-state.md`, verify applicable rules (mark N/A where not relevant); violations of enabled extension rules are genuine findings

**Explicitly OUT of scope** (do NOT check, do NOT report): code style, naming, formatting, file organization, magic numbers, comment/documentation quality, SOLID/DRY/refactoring opportunities, performance ideas not required by an AC/NFR, and any "good to have" suggestion. If everything traces to Met with no defects → verdict is ✅ APPROVED with zero issues.

## Phase 3: Document Findings
- [ ] Assign each issue a severity — only TWO are reportable: **🔴 Blocker** (AC/requirement Not Met, or a defect that breaks it) / **🟠 High** (AC/requirement Partially Met or deviates from spec) — plus a category, file:line, and a suggested fix. There are NO 🟡 Medium / 🟢 Low advisory findings in this review
- [ ] Create the report at the appropriate path (increment version `v[X]` on re-review). **The two targets use deliberately different filenames so Remediate can identify and intake either:**
  - **Story review**: `aipdlc-docs/construction/reviews/story-[N.M]-code-review-v[X].md`
  - **All-stories review**: `aipdlc-docs/construction/reviews/all-stories-code-review-v[X].md`
- [ ] For all-stories reviews, group issues by story section in the report (issue IDs prefixed per story, e.g. `S1.2-ISS-001`, so Remediate can map every issue back to its story)
- [ ] Determine overall status strictly from the verdicts: any 🔴 (AC/req Not Met or broken) → ❌ CHANGES REQUESTED; only 🟠 (Partially Met) → ⚠️ APPROVED WITH COMMENTS; all ACs/requirements Met, zero issues → ✅ APPROVED

## Phase 4: Record the Verdict (NO Status Change)
- [ ] **Code Review is read-only and does NOT change the Story Tracker status.** A story under review stays `🔵 In Development` — the ONLY valid statuses are `🟢 Ready for Development`, `🔵 In Development`, and `🧪 Ready for Testing`, and the move to `🧪 Ready for Testing` happens only when the PR is raised via `dev-implement`. Do NOT set or demote any status here.
- [ ] Update only the review report and the audit trail — never the tracker Status column. (You MAY refresh the story row's `Recorded` timestamp to note that a review ran, but leave `Status` unchanged.)
- [ ] Because no status changes, there is normally **no Jira transition** in this phase. If your team's process nonetheless requires a board move on review completion, apply the **Jira Sync Rule** (confirm-first, verify) — but do NOT change the local tracker Status.
- [ ] Log the review verdict (✅ APPROVED / ⚠️ APPROVED WITH COMMENTS / ❌ CHANGES REQUESTED) and the full findings list by severity in `aipdlc-docs/audit.md` with timestamps

---

## Issue Severity

| Level | Icon | Meaning | Action |
|-------|------|---------|--------|
| Blocker | 🔴 | AC/requirement NOT met, or a defect that breaks it | MUST fix before approval |
| High | 🟠 | AC/requirement PARTIALLY met / deviates from spec | SHOULD fix |

🟡 Medium / 🟢 Low do not exist in this review — anything that would have been advisory (style, refactoring, nice-to-have) is out of scope and is not reported at all.

---

## Output

**Location** (choose based on review target):
- Story: `aipdlc-docs/construction/reviews/story-[N.M]-code-review-v[X].md`
- All stories: `aipdlc-docs/construction/reviews/all-stories-code-review-v[X].md`

### Code Review Report Template

```markdown
# Code Review - [Story N.M: <Story Name> | All Stories]

**Date**: [YYYY-MM-DD]
**Reviewed By**: REVIEWER (ai-pdlc)
**Review Number**: [1, 2, ...]
**Review Mode**: [INITIAL_REVIEW / FIX_VERIFICATION / NEW_CHANGES]
**Review Target**: [Story N.M | All Stories]
**Status**: ✅ APPROVED / ⚠️ APPROVED WITH COMMENTS / ❌ CHANGES REQUESTED
**Jira**: [PROJ-NNN, or list of keys for all-stories, or —]

## Review Summary
**Components Reviewed**: [files]
**Stories in Scope**: [story numbers covered; for all-stories, also list stories excluded for having no code]
**Tests Reviewed**: [Yes/No — statically; suite NOT re-run]  **Coverage**: [X]% (from Code Generation's Unit Test & Coverage gate — not re-measured)
**Overall Assessment**: [2-3 sentences — strictly on AC/requirement completion]

## AC & Requirements Verification
[One table per in-scope story. EVERY acceptance criterion and mapped requirement gets a row — this is the core of the report.]

### Story N.M: [Title]
| # | AC / Requirement | Verdict | Evidence / Gap |
|---|------------------|---------|----------------|
| AC-1 | [criterion text] | ✅ Met | `path/file.ext:45` |
| AC-2 | [criterion text] | ⚠️ Partially Met | [what's missing] → ISS-001 |
| AC-3 | [criterion text] | ❌ Not Met | [what's absent] → ISS-002 |

## Issues Found
[For all-stories reviews: group issues under one `## Story N.M` section per story, and prefix IDs per story — e.g. `S1.2-ISS-001` — so Remediate can map every issue to its story.]

### ISS-001: [Title] 🔴 Blocker
**AC/Requirement**: [the specific AC or requirement this fails]  **File**: `path/file.ext:45-52`
**Issue**: [how the AC/requirement is not met, or the defect that breaks it]
**Suggested Fix**: [code or description]

[If there are NO issues, write "No issues — all acceptance criteria and requirements verified as Met." Do not pad this section.]

## Issue Summary
| # | ID | Severity | AC/Requirement | File | Status |
|---|-----|----------|----------------|------|--------|
| 1 | ISS-001 | 🔴 Blocker | AC-2 (Story 1.2) | auth.ext:45 | Must Fix |

**Counts**: Blockers: [a] | High: [b]

## Approval Status
**Decision**: [APPROVED / APPROVED WITH COMMENTS / CHANGES REQUESTED]
**Reason**: [...]
```

---

## Anti-Loop Protection
1. ✅ ALWAYS check for previous reviews first
2. ✅ SKIP if already approved and code unchanged
3. ✅ Only 🔴 + 🟠 exist in this review — every finding must map to a specific AC/requirement
4. ❌ DON'T invent findings — a clean review (zero issues) is valid and expected when all ACs are Met
5. ❌ DON'T surface style/refactor/nice-to-have items — they are out of scope, on first review AND re-reviews
6. ❌ **DON'T edit code, tests, or any non-review file** — review + report only
7. ❌ **DON'T re-run the unit test suite or re-measure coverage** — the Unit Test & Coverage gate in Code Generation already ran it to ≥90%; reuse that recorded evidence (this review reads tests, it does not execute them)

---

## After Review — Mandatory Next-Step Output

After writing the report, present ONLY this block (do not improvise code edits):

```
📋 Code review complete — aipdlc-docs/construction/reviews/<report-filename>.md
   Target: [Story N.M | All Stories]
   ACs verified: [met]/[total] Met | [p] Partially Met | [n] Not Met
   Status: [✅ APPROVED | ⚠️ APPROVED WITH COMMENTS | ❌ CHANGES REQUESTED]
   Issues: [a] 🔴 | [b] 🟠

▶️ Next step:
1️⃣  Remediate         ← required if ❌ CHANGES REQUESTED
                                              recommended if ⚠️ APPROVED WITH COMMENTS
                                              N/A if ✅ APPROVED
2️⃣  Implement / review the next story        ← if ✅ APPROVED

Type your choice (1 / 2).
```
