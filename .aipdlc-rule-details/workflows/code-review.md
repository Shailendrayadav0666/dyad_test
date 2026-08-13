# 🔑 WORKFLOW: `code-review`

**Status**: Runs in two ways:
- **Automatically after Code Generation** — `workflows/dev-implement.md` auto-triggers this review for the just-implemented story (pre-scoped to `story [N.M]`; skip the "what to review" prompt in that case) and audits its complete log. This is no longer user-selected in the `dev-implement` flow.
- **Standalone** — user-initiated at any time for a specific story or all stories together.

**Capability**: **Code Review** (`construction/code-review.md`) — REVIEWER role, **read-only**. Reviews a **specific story** or **all stories together against the code**, and produces a versioned report at:
- Story: `aipdlc-docs/construction/reviews/story-[N.M]-code-review-v[X].md`
- All stories: `aipdlc-docs/construction/reviews/all-stories-code-review-v[X].md`

The two filenames are deliberately distinct so **Remediate** can intake either type.

MUST NOT edit source code.

> ⚖️ **STRICT SCOPE**: This review checks ONE thing — **are the story's acceptance criteria and mapped requirements completed by the code, as written?** Findings are limited to: AC/requirement Not Met (🔴), AC/requirement Partially Met (🟠), or a genuine defect that prevents an AC/requirement from working (🔴). NO "good to have" suggestions, NO style/docs nits, NO 🟡/🟢 advisory items. **Zero findings is a valid, expected outcome — never invent issues** (this review already runs automatically after every `dev-implement`; padded findings cause endless remediate loops).
>
> 🧾 **"Mapped requirements" is defined** (`common/requirements-traceability.md` Rule 6): it means EXACTLY the story's `**Covers**: [REQ-IDs]` list in `stories.md`. Read each covered REQ-ID's text in `aipdlc-docs/inception/requirements/requirements.md` and verify the code against the requirement AS WRITTEN THERE, in addition to the story's ACs — an AC set that is a weaker statement than its requirement does NOT cap the review; the shortfall vs the requirement is a finding (Partially Met).

---

## MANDATORY: Rule Details Loading

This workflow may be invoked standalone. Resolve the rule details directory  (check `.aipdlc-rule-details/`) and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`
- The detailed reviewer steps from `construction/code-review.md`

All paths below are relative to the resolved rule details directory.

---

## Recommended workflow execution

- Run **Code Review** as a **read-only workflow** (no code-editing tools) so it physically cannot modify source — enforcing separation of duties. It returns the report path and verdict.

## Per-story / all-stories flow when invoked
1. **Ask what to review** — DO NOT guess. Present:
   ```
   What would you like me to review?
   Options:
     a) A specific story                       (e.g., "story 1.2")
     b) All stories together against the code  (type "all stories")
   ```
   **Exception — auto-run from `dev-implement`**: when this review is triggered automatically after Code Generation, the target is already the just-implemented `story [N.M]`. SKIP this prompt and review that story directly.
   **⚡ NO TEST RE-RUN (auto-run from `dev-implement`)**: dev-implement's Unit Test & Coverage gate already ran the full unit test suite to ≥90% coverage in the same run. Do NOT re-execute the tests or re-measure coverage here — reuse the evidence dev-implement passes in (tests X/X passing + coverage %; also recorded in audit.md) for the report's "Tests Reviewed / Coverage" fields, and verify tests only statically (they exist and cover the ACs).
2. Load and execute all steps from `construction/code-review.md` (Phase 0 history check → Phase 1 prep → Phase 2 checklist → Phase 3 findings → Phase 4 report/verdict).
3. **Produce the report** at the appropriate path per the review target.
4. **Do NOT change the Story Tracker status.** Code Review is read-only and does not introduce a status of its own — a story under review stays `🔵 In Development`. (The story only moves to `🧪 Ready for Testing` later, when its PR is **merged** — promoted by the `sdet-list-work` skill once SDET has tested it.) Record the verdict and findings, not a status change.
5. **If 🔴 Blocker or 🟠 High issues found**: recommend **Remediate** as the next step.
6. The review report's verdict (clean / findings by severity) is the output the user acts on — it does not by itself advance the story's status.

## Execution
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load `construction/code-review.md` when the user invokes this workflow OR when `dev-implement` auto-triggers it after Code Generation
3. **Auto-run only as part of the `dev-implement` post-code-generation flow** (pre-scoped to the implemented story). Otherwise it is user-initiated — never auto-run it outside that flow.
4. **MANDATORY**: Log the complete review log (report path, verdict, findings by severity) and any Jira updates in audit.md with complete raw input. Every entry MUST carry the `**JIRA TICKET**:` field (the reviewed story's Jira link, or local Story ID) AND the `**Epic Link**:` field (full Parent Epic URL from `## Jira` in `aipdlc-docs/aipdlc-state.md`, or `none`) — per the Audit Entry Format in `workflows/dev-implement.md`

---

## 🔄 Jira Sync Rule (reminder)

Code Review does **NOT** change the story status — the story stays `🔵 In Development` — so there is normally no Jira transition to perform here. If a review ever does drive a status change, the **Jira Sync Rule** in `CLAUDE.md` applies (confirm-first, verify, never update only one side).

---

> **Next (optional)**: If issues were found, run **Remediate**. If approved, implement/review the next story.
