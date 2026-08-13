---
name: stitch-delta
description: >
  Applies pending epic delta reverse engineering artifacts onto the root reverse
  engineering documents. Runs on the BASE branch (e.g., main) AFTER an epic's PR has
  merged — root docs are never stitched on epic branches, which makes root-doc merge
  conflicts impossible with N parallel epics. Discovers un-stitched deltas by comparing
  delta/<EPIC-ID>-*/ folders against the stitch-epic.md ledger, stitches them in merge
  order with a per-delta verification gate, records each in the ledger (so re-runs and
  push-race retries skip already-stitched deltas), and pushes directly to the base
  branch confirm-first.
when_to_use: >
  Trigger when the user says: "stitch-delta", "stitch the delta", "stitch deltas",
  "apply pending deltas", "stitch reverse engineering delta", "update root reverse
  engineering docs after merge", "post-merge stitch".
allowed-tools: Read Grep Glob Bash Write Edit
---

# 🧵 Stitch Delta — Post-Merge Root Doc Update

Load and execute the agent instructions from:

```
.aipdlc-rule-details/agents/stitch-delta-agent.md
```

Read that file completely and follow every step defined in it.

**Key rules**:
- MUST run on the base branch after the epic PR merged; pull latest before stitching — NEVER stitch on an epic branch
- Idempotent: a delta recorded in `stitch-epic.md` is NEVER stitched again — re-runs and push-race retries skip it
- Ledger format: `| Cycle | Jira Ticket | Delta Folder | Stitched At | Commit Range | Documents Updated |` — `Cycle` is `epic`, `bug`, or `enhancement`, `Jira Ticket` is the cycle's Jira ticket number. If an existing ledger uses the old format (no Cycle/Jira Ticket columns), migrate it in place first per the agent file's Step 2 migration rule
- Stitching MUST follow the "Delta Reverse Engineering & Stitching" section of `.aipdlc-rule-details/inception/reverse-engineering.md`, including the post-stitch verification gate
- Push is confirm-first; on a race-rejected push, pull --rebase, re-check the ledger, retry — NEVER force-push
- **If the direct push is BLOCKED by branch protection** (base rejects direct pushes / requires a PR): fall back to raising a **PR** into the base branch from a `docs/stitch-delta-*` branch. That PR MUST carry the `ai-generated` and `aipdlc-v2.3` labels (version hardcoded to `2.3`). See the agent file's Step 5.4.
- Root reverse engineering documents are UPDATED IN PLACE at their existing paths — never deleted, renamed, or replaced by delta files. After stitching, every root doc that existed before must still exist, showing as modified only
