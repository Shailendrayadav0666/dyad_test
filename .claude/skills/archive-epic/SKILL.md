---
name: archive-epic
description: >
  Closes an epic's, bug's, OR enhancement's release cycle. Generates the cycle's DELTA
  reverse engineering artifacts (what the development changed) in a cycle-namespaced folder
  (delta/<CYCLE-ID>-<name>/) so N parallel cycles never conflict, then archives the
  complete aipdlc-docs — including audit.md, aipdlc-state.md, and the reverse
  engineering documents with the delta — into aipdlc-archives/epics/<EPIC-ID>-<name>/
  (epic cycles), aipdlc-archives/bugs/<BUG-ID>-<name>/ (bug cycles), or
  aipdlc-archives/enhancements/<ENH-ID>-<name>/ (enhancement cycles), per the
  Workflow Type recorded in aipdlc-state.md, at the workspace root. Does NOT stitch the delta into the root docs — that happens
  post-merge on the base branch via the stitch-delta skill (the completion message
  instructs the user). Confirm-first at every destructive step; offers an optional
  workspace reset for the next epic cycle.
when_to_use: >
  Trigger when the user says: "archive-epic", "archive the epic", "close the release
  cycle", "archive aipdlc docs", "end of release archive", "stitch the delta",
  "stitch reverse engineering delta", "wrap up this epic", "release archive".
allowed-tools: Read Grep Glob Bash Write Edit
---

# 📦 Archive Epic — Delta Stitch + Release Archive

Load and execute the agent instructions from:

```
.aipdlc-rule-details/agents/archive-epic-agent.md
```

Read that file completely and follow every step defined in it.

**Key rules**:
- Delta generation MUST follow the "Delta Reverse Engineering & Stitching" section of `.aipdlc-rule-details/inception/reverse-engineering.md`; deltas are written to the epic-namespaced folder `delta/<EPIC-ID>-<epic-name-slug>/`
- NEVER stitch root reverse engineering docs in this skill — stitching happens post-merge on the base branch via the `stitch-delta` skill
- Delta generation is **ADD-ONLY**: new files inside `delta/<EPIC-ID>-<slug>/` only. The original root reverse engineering documents must remain byte-identical — never modified, renamed, moved, or deleted by this skill (verified via `git status` after generation)
- NEVER delete or reset anything before the archive copy is created AND verified
- **Archive layout is FIXED — always nest, never flatten**: every archive folder (`aipdlc-archives/epics|bugs|enhancements/<ID>-<name>/`) MUST contain exactly two top-level entries — an `aipdlc-docs/` subfolder holding the ENTIRE copied `aipdlc-docs/` tree (folder name preserved), and a sibling `archive-manifest.md`. NEVER copy `aipdlc-docs/`'s contents directly into the archive folder root (that produces `construction/`, `inception/`, `aipdlc-state.md`, `audit.md` sitting loose next to `archive-manifest.md` — an inconsistent layout that breaks workspace-detection's archive-restore path, which always reads `<archive>/aipdlc-docs/inception/reverse-engineering/`). See archive-epic-agent.md Step 5 for the exact copy command and the mandatory structural verification.
- **Archive EVERYTHING under `aipdlc-docs/` — for EVERY cycle type**: the archived `aipdlc-docs/` subfolder is a **complete, recursive, unfiltered, byte-for-byte** copy of the live `aipdlc-docs/` — every folder and every file at every depth (`inception/`, `construction/`, `tests/`, `operations/`, `reverse-engineering/` incl. `delta/` + `stitch-epic.md`, plans, reviews, code summaries, unit-test evidence, `aipdlc-state.md`, `audit.md`, plus anything else present). The cycle type (`epics/` | `bugs/` | `enhancements/`) changes **only the destination subfolder — never what gets copied**: a bug or enhancement cycle archives the same full tree an epic cycle does. NEVER archive a subset/whitelist, never skip a folder for looking empty/stale/irrelevant-to-this-cycle-type/owned-by-another-role, never filter by extension, name, dotfile-ness, or `.gitignore` (untracked and ignored files are archived too), and never move/delete/rewrite/summarize anything while copying.
- **The ONE permitted exclusion — already-stitched deltas (archive-epic-agent.md Step 3a)**: after the full copy, delta folders recorded in the `stitch-epic.md` ledger are pruned **from the archive copy only**, because their content already lives inside the root reverse engineering documents this archive carries (this keeps archive growth linear rather than quadratic in the number of cycles). 🔴 **Always kept**: this cycle's own delta (not yet stitched) and any delta *absent* from the ledger (pending un-stitched — the archive may be its only surviving copy after an option-B full reset). 🔴 The **live** `delta/` folder is NEVER touched — it is what the PR carries to base for `stitch-delta`. No other exclusion may be inferred from this one. Enforced by the BLOCKING completeness check in archive-epic-agent.md Step 5.5 — the live-vs-archived relative-path diff must contain exactly the pruned delta paths and nothing else before Step 6 is allowed to delete any live docs.
- **Bug mode**: when `aipdlc-state.md` `## Jira` records `Workflow Type: bug`, the agent runs in bug mode — cycle ID = the defect ticket, archive goes to `aipdlc-archives/bugs/<BUG-ID>-<name>/`, and the readiness check verifies the `[BUG]` PR was raised (the bug's story intentionally stays In Development). Epic archives go to `aipdlc-archives/epics/<EPIC-ID>-<name>/`.
- **Enhancement mode**: when `## Jira` records `Workflow Type: enhancement`, the agent runs in enhancement mode — identical to bug mode except: cycle ID = the enhancement ticket (`Parent Ticket`), archive goes to `aipdlc-archives/enhancements/<ENH-ID>-<name>/`, and the readiness check verifies the `[ENH]` PR was raised (`Enhancement PR` in `## Branching`).
- If `aipdlc-archives/` (or its `epics/`/`bugs/`/`enhancements/` subfolders) already exists, reuse it — never recreate it or touch other cycle folders inside it; only a same-name cycle folder may be replaced, and only after the user explicitly confirms
- Every destructive step is confirm-first; log everything in audit.md. **Sole exception — Step 3a's already-stitched delta prune runs AUTOMATICALLY (no prompt)**: it deletes only from the archive copy, only content already folded into that archive's root RE docs, while the live tree is still fully intact — it is logged in audit.md and `archive-manifest.md` rather than confirmed. No other deletion may claim this exception.
- **Auto-triggered ONLY for epic cycles** — by pr-generator on an **Epic → Base PR**: there the Step 6 workspace-reset question is NOT asked — option A (Reset, keep root reverse engineering docs) is auto-selected, announced, and logged in audit.md. Option B is never auto-selected.
- 🔴 **Bug and enhancement cycles archive MANUALLY** — the operator invokes this skill themselves. `bug-fix-implement` (Step 12) and `enhancement-implement` (Step 19) deliberately do NOT invoke it, and pr-generator's Phase 7 auto-trigger excludes `[BUG]`/`[ENH]` → Base PRs. Those runs are standalone, so the Step 6 reset question IS asked. **Why**: SDET work lands on the cycle branch unsynchronised with the ticket's PR — `/sdet-implement` writes `aipdlc-docs/tests/<JIRA-ID>-<title>/` on its own `sdet/...` branch + PR (often raised after the fix is done) and `sdet-list-work` Option C amends test plans later still. Since this skill takes a one-shot destructive snapshot and then resets the live docs, an automatic archive at PR time would silently omit `tests/` or miss later test-plan edits, with nothing left to re-capture them.
- **Step 2.5 SDET readiness check (all modes)**: the branch must be up to date with origin, expected `aipdlc-docs/tests/<JIRA-ID>-…/` folders must exist, and no `sdet/...` PR into the cycle branch may still be open. Gaps are surfaced with a confirm-first "archive anyway?" prompt and, if the user proceeds, recorded as `**Known Gaps**:` in `archive-manifest.md`.
- **Timing invariant (manual runs)**: `archive-epic` must still run **BEFORE the `[BUG]`/`[ENH]` PR merges** — its cycle-close commit rides the open PR, which is the only way the RE delta reaches the base branch for `stitch-delta`.
- **The cycle-close changes MUST be committed and pushed on the epic/bug/enhancement branch** (Step 6.5, push confirm-first) — the delta only reaches the base branch by riding the open PR; an unpushed delta means stitch-delta finds nothing. The open PR tracks the branch and picks up the commit automatically.
