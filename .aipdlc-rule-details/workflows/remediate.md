# 🔑 WORKFLOW: `remediate`

**Status**: OPTIONAL. This is NOT a mandatory phase. It is offered as a recommended next step after Code Review (when issues exist), and can also be invoked standalone at any time.

> **When reached via `dev-implement`**: the user selected "Remediate" at the post-review decision gate. The report to remediate is already known — this story's `story-[N.M]-code-review-v[X].md` — so SKIP the "which report" prompt (Step 2 below) and remediate that report directly. After fixes + audit, control returns to `workflows/dev-implement.md`, which presents the **Approve & continue / Re-review** decision (do not re-implement that decision here).

**Capability**: **Remediate** — DEV role. Fixes issues from a review report (fix → unit test → green; runs ONLY the unit tests of the story/stories in scope — never the full repo suite) and annotates the report in place.

> 🔎 **Intake format** (as produced by `workflows/code-review.md` / `construction/code-review.md`): issues `ISS-XXX` (story) or `S[N.M]-ISS-XXX` (all-stories), each tied to a specific AC/requirement; only two severities exist — 🔴 Blocker (AC/req Not Met or broken) and 🟠 High (Partially Met) — and BOTH are mandatory to fix (defer only with explicit user consent).

---

## MANDATORY: Rule Details Loading

This workflow may be invoked standalone. Resolve the rule details directory the same way `CLAUDE.md` does (check `.aipdlc-rule-details/`) and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`, `common/question-format-guide.md`
- The detailed fixer steps from `construction/remediate.md`

All paths below are relative to the resolved rule details directory.

---

## Recommended workflow execution

- Run **Remediate** as a **code-editing workflow**, scoped strictly to the issues in the named review report.
- The main workflow stays the orchestrator: it confirms the report and scope, spawns remediation, updates the Story Tracker, and handles all confirm-first Jira transitions (workflow never touch the board without confirmation).

## Per-story / all-stories flow when invoked
1. **Check for reports** — `aipdlc-docs/construction/reviews/story-*-code-review-v*.md` (story-wise) and `all-stories-code-review-v*.md` (all stories together; distinct filename so it is unmistakably intakeable here). If none exist, **STOP**: "Run Code Review first to produce a report to remediate from."
2. **Ask which report to remediate** — DO NOT guess. Enumerate the newest version per story plus the newest all-stories report (grouped: story reports, all-stories reports and let the user choose — story-wise remediation from a story report, or a full sweep from an all-stories report.)
3. Load and execute all steps from `construction/remediate.md` (load review target context → build backlog → **confirm scope and HALT** → fix → unit test → green (run only the in-scope story's unit tests), 🔴/🟠 mandatory → annotate report in place).
4. **Do NOT change the Story Tracker status.** Remediate edits code but does not introduce a status of its own — every story it touches stays `🔵 In Development` (it moves to `🧪 Ready for Testing` only when its PR is **merged**, promoted by the `sdet-list-work` skill once SDET has tested it). Record the fixes and evidence in the report and audit.md, not a status change.
5. **Recommend re-review** (`workflows/code-review.md`) — required if any 🔴 was fixed.
6. **Offer a PR of the changes** (standalone invocations only): the "After Remediation" next-step menu in `construction/remediate.md` includes option 4️⃣ — "Satisfied with the remediation? Raise a PR of these changes". If chosen, invoke the **`pr-generator` skill** (`.claude/skills/pr-generator`) as-is (it confirms before push/PR) per Step 7. OMIT this option when remediation was reached via `dev-implement` — that flow raises the PR itself.

## Execution
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load `construction/remediate.md` only when the user invokes this workflow
3. **NEVER** auto-run this; it is user-initiated
3.5. **🎨 DESIGN REFERENCE SUPPLIED DURING REMEDIATION (`common/design-reference-grounding.md` DR-1 + DR-7 — MANDATORY)**: if the user supplies a path, spec file, screenshot, or design URL while adjusting scope or describing an issue, it is a design reference — register it in `## Design References` in `aipdlc-state.md` immediately and read its **actual content** (DR-2), not just the part covering the issue in hand. Then, before fixing anything:
   - **Assess its true blast radius**: determine everything the reference `Governs` — it is usually broader than the current story (a prototype for one control is often a prototype for the whole feature).
   - **State which ALREADY-COMPLETED stories/components it invalidates**, and which not-yet-built stories must now be grounded against it — a plain report in your output, **not a question**. Do NOT silently limit the reference to the story currently being remediated.
   - On a mismatch between the reference and an approved AC, apply **DR-8** then **DR-6**: a point already in the `### Reconciliations` table was decided deliberately — follow the artifact and do not reintroduce it. Otherwise follow the reference, say plainly what differed, amend the AC / `requirements.md` / Jira per `common/requirements-traceability.md` to stay truthful, record the new reconciliation, and continue — no A/B question, no halt (the remediation flow's own existing scope confirmation is the only checkpoint).
   - Log the registration, what was extracted, and the invalidation list in audit.md.
4. **MANDATORY**: Log user responses and any Jira updates in audit.md with complete raw input. Every entry MUST carry the `**JIRA TICKET**:` field (the remediated story's Jira link, or local Story ID) AND the `**Epic Link**:` field (full Parent Epic URL from `## Jira` in `aipdlc-docs/aipdlc-state.md`, or `none`) — per the Audit Entry Format in `workflows/dev-implement.md`

---

## 🔄 Jira Sync Rule (reminder)

Remediate does **NOT** change the story status — every story it touches stays `🔵 In Development` — so there is normally no Jira transition to perform here. If a remediation ever does drive a status change, the **Jira Sync Rule** in `CLAUDE.md` applies (confirm-first, verify, never update only one side).

---

> **Next (optional)**: Re-run **Code Review** (`workflows/code-review.md`) — required if any 🔴 was fixed; otherwise proceed to the next story / Operations.
