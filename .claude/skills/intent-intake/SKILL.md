---
name: intent-intake
description: >
  Use this skill when someone wants to turn a raw idea, feature request, or piece of product context
  into an Intent that can enter Jira — the light front-door gate. Trigger it on "I have an idea",
  "capture this as an intent", "start an intent", "get this into Jira", "turn this research/PRD/deck
  into an intent", or any moment a fuzzy idea needs to become real. It asks upfront whether the user
  has a document to reference or wants to explain in plain English. It gathers a consistent baseline
  — just enough thought to justify a Jira entry — produces a baseline intent artifact, and pushes
  the Epic directly to Jira via the Atlassian MCP. It does NOT do deep elaboration or refinement; that happens later, with engineers, in intent-refinement.
compatibility: Atlassian MCP required — pushes the Epic directly to Jira at the end of intake.
---

# Intent Intake

The membrane between fuzzy thinking and Jira. Everything upstream — research, prototyping, KPI
exploration — lives wherever the team likes (Confluence, git, a napkin). Nothing is "real" until it
clears this gate and becomes an Epic. This skill keeps the gate **fast and consistent**: a baseline
of thought, no more.

## Keep it light on purpose

The overwhelm people feel comes from refinement-depth thinking leaking into the intake moment.
Don't let it. Intake gathers six things and stops. Testable criteria, the domain model, NFRs, risk
registers — **none of that belongs here**; it happens later, with engineers, in intent-refinement. If you
find yourself asking for measurable thresholds or bounded contexts, you've gone too deep — pull back.

## Step 0 — Ask how the person wants to start

**Before doing anything else**, ask the person this question:

```
How would you like to share your idea?

A) I have a document (PRD, research notes, prototype write-up, Confluence page, deck, etc.)
   → paste or share the link/content and I'll read it first
B) I'll explain it in plain English
   → just tell me the idea in your own words

[Answer]: 
```

- **If A**: Read the doc/link they provide, pre-fill every baseline field it already answers, then only ask about the gaps. Capture the `context_link` as the source URL or file reference.
- **If B**: Start from their words. Ask follow-up questions for any of the six baseline fields not covered. Set `context_link` to "plain English — no external doc".

## Step 1 — Capture the idea

Get the outcome in their words, business terms. One outcome per intent — if you hear two, flag and
split.

## Step 2 — Fill the baseline (the six)

Gather exactly these, no more. Ask in one or two short, tappable batches (multiple-choice + an open
"Other") — see `references/intake-questions.md`:

1. **Outcome** — one business sentence.
2. **KPI / business outcome** — the metric this moves.
3. **Rough success signal** — directional only ("faster entry", "fewer failed checkouts"). NOT testable yet.
4. **At least one explicit out-of-scope.**
5. **Known hard constraints** — or an honest "none known."
6. **Confidence + open unknowns**, and the **context link**.

A declared unknown is fine — better than a guess. Record unknowns; don't fill them with plausible fiction.

## Step 3 — Draft the baseline intent

Using `assets/intent-template.md` as a reference shape, draft the filled baseline intent **in chat only** — do not create any local file. Fill the BASELINE sections, leave the FULL sections blank (those are for intent-refinement). Show the draft to the person for review.

## Step 4 — Intake gate

Run the **Intake gate** checklist mentally. It only checks the six are present and non-garbage
— KPI named, out-of-scope not blank, unknowns declared, context linked. It does **not** check for
testable criteria; that bar is intentionally not here. Confirm with the person before proceeding.

## Hand off — Push Epic to Jira via MCP

Once the intake gate passes, **push the Epic directly to Jira using the Atlassian MCP** — Follow this sequence:

1. **Confirm before pushing** — show the user a brief summary of what will be created:
   ```
   Ready to create a Jira Epic with the following details:
   - Title: [intent title]
   - Description: [full intent content from the filled template]
   - Labels: intent-intake

   Push to Jira? (yes / no)
   ```
2. **On yes** — call the Atlassian MCP `createJiraIssue` (or equivalent) with:
   - `issueType`: Epic
   - `summary`: the intent title
   - `description`: the **complete filled intent artifact** (all BASELINE sections as-is, verbatim — do not summarise or shorten)
   - `labels`: `["intent-intake"]`
   - `project`: confirm the PROJECT_KEY with the user if not already known
3. **Verify, don't assume**: re-fetch the created issue (`getJiraIssue` on the returned key) and confirm
   BOTH (a) the returned Jira key is real and resolvable, AND (b) `intent-intake` is present, exact
   string, in its `labels` array. Some MCP implementations silently drop a `labels` field passed at
   create time — do not treat a successful `createJiraIssue` response alone as proof the label landed.
   If the label is missing, retry by updating the issue's labels once (append `intent-intake` to
   whatever is there). If it still fails after the retry, stop and tell the user explicitly — do NOT
   report the intake as complete with the label unconfirmed.

After the Epic is live in Jira **and the label is confirmed**, tell the person the next step is **intent-refinement**.

## HARD GUARDRAILS — do not violate

- **No file or directory creation.** Do not create, write, or modify any file or folder in the workspace. The intent lives in Jira only.
- **No local artifacts.** Do not save or instantiate `intent-template.md` locally. It is a reference shape — draft the content in chat, then push it directly to Jira.
- **No audit.md writes.** Do not write to `audit.md` or any other log file.
- **Jira push only.** The only write action is `createJiraIssue` via the Atlassian MCP (plus, if needed, one retry label-update per Step 3 of the hand-off sequence).
- **Confirm before every Jira write.** Never create a Jira issue without explicit user approval ("yes").
- **🔴 EVERY Epic this skill creates MUST carry the exact label `intent-intake` — no exceptions, not optional.** This applies unconditionally to every successful run, not a per-Epic judgment call. A pre-existing *similar-looking* label elsewhere in the project (`intake`, `intent_intake`, `Intent-Intake`, etc.) is NOT a substitute — the exact string `intent-intake` must be present. Its presence is **verified by re-fetching the created issue** (never assumed from the create call's response alone) before the intake is reported complete. A run that creates the Epic but cannot confirm the label is NOT a successful run; stop and surface the failure to the user. See Step 3 of the hand-off sequence for the exact procedure.

## Bundled resources

- `assets/intent-template.md` — reference shape only; never instantiate it as a local file.
- `references/intake-questions.md` — the light question batches for the six baseline fields.
