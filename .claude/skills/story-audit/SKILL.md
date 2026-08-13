---
name: story-audit
description: >
  Audits an existing Jira Story or Epic against the AI-PDLC quality bar. Fetches the issue,
  assesses what's present vs missing, scores it, and offers to fill gaps through targeted
  questions — then updates the issue in Jira with the improvements. Works for any issue type
  (Story, Epic, Task) but applies the appropriate checklist for each.
  Trigger on "audit this story", "check this story", "is this story ready",
  "audit this epic", "story audit", "review PROJ-123", "is PROJ-123 complete",
  "validate this ticket", "check this ticket", or any request to verify a Jira issue
  has enough detail to be actionable.
compatibility: Requires Jira access via the Atlassian MCP.
---

# Story & Epic Audit

Fetch a Jira issue, measure it against the right quality bar, report what's strong and what's
missing, and — if the user wants — fill the gaps through targeted questions and update the issue
in Jira.

## Philosophy

**Assess first, fix second.** The audit is a read-only diagnosis. Fixing is opt-in. The user
may just want the report, or they may want to walk through the gaps and patch the issue right
now. Support both.

**Type-aware.** Epics and Stories have different quality bars. Detect the issue type from Jira
and apply the matching checklist. If the type is something else (Task, Bug, Initiative), use
the closest checklist and note the adaptation.

---

## Step 1 — Ask for the issue

If the user already provided a key (e.g. "audit PROJ-42"), use it. Otherwise ask:

```
Which Jira issue should I audit?
Provide the issue key (e.g. PROJ-42) or full URL.
```

## Step 2 — Fetch and classify

Use the Atlassian MCP `getJiraIssue` to fetch the issue. Identify:
- **Issue type** (Epic, Story, Task, Bug, etc.)
- **Summary**
- **Description** (full content)
- **Labels**
- **Status**
- **Links** (parent Epic, child issues, related issues)

Select the matching checklist from `references/quality-checklists.md`:
- Epic → **Epic Checklist**
- Story / Task → **Story Checklist**
- Other → **Story Checklist** (adapted, note this to the user)

## Step 3 — Run the audit

Evaluate every item on the checklist. For each item, assign one of:

- **PASS** — present and sufficient
- **WEAK** — present but thin, vague, or incomplete
- **MISSING** — not present at all
- **N/A** — not applicable for this issue

Present the results as a scorecard:

```
Audit: [KEY] — "[summary]" ([issue type])

SCORECARD
=========
[x] Item name                          PASS
[~] Item name                          WEAK — [brief reason]
[ ] Item name                          MISSING
[-] Item name                          N/A

Score: X / Y passing (Z%)

VERDICT: [Ready / Needs Work / Incomplete]
```

**Verdict thresholds:**
- **Ready** — all required items PASS, no MISSING on required fields
- **Needs Work** — no MISSING on required fields, but 1+ WEAK items
- **Incomplete** — 1+ required fields are MISSING

## Step 4 — Offer to fix

If verdict is **Ready**, congratulate and stop.

If verdict is **Needs Work** or **Incomplete**, offer:

```
This issue has gaps. Want me to:

A) Walk through the gaps and help fill them — I'll ask targeted questions, then update the issue in Jira
B) Just take the report — I'll leave the issue as-is

[Answer]:
```

**If A**: For each WEAK or MISSING item, ask focused questions (multiple-choice where possible,
with an open "Other"). Work through them in priority order (required fields first, then
recommended). After gathering answers, draft the updated description and show it to the user
for approval before writing to Jira.

**If B**: Done. The scorecard is the deliverable.

## Step 5 — Update the issue in Jira (only if user chose A)

1. Draft the improved description incorporating all gathered answers.
2. **Show the full updated description** to the user for review.
3. **Confirm before writing**: "Update [KEY] in Jira with these improvements? (yes / no)"
4. On yes, update via the Atlassian MCP. Verify success.
5. Report: "Updated [KEY] in Jira."

---

## HARD GUARDRAILS — do not violate

- **No file or directory creation.** Do not create, write, or modify any file or folder in the workspace.
- **No local artifacts.** The audit lives in chat; fixes go to Jira only.
- **Jira in, Jira out.** Read via `getJiraIssue`, update via the Atlassian MCP. Nothing else.
- **Confirm before every Jira write.** Never update without explicit user approval ("yes").
- **Never fabricate content.** If something is unknown, ask — don't guess. Mark genuine unknowns as open questions.
- **Preserve existing content.** When updating, merge improvements into the existing description — never discard content that was already there.

---

## Bundled resources

- `references/quality-checklists.md` — the Epic and Story checklists used for scoring.
