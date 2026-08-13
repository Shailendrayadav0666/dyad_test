---
name: raise-defect
description: >
  Helps an SDET raise a defect/bug in Jira with a minimal, fixed question set:
  Title, Description, Severity (Low / Medium / High / Critical — mapped to the Jira
  Severity context field), Environment Found, and Discovery Activity. Components is always
  "Default" and Associated Org is always "All" (never asked). Creates the Jira bug via
  the Atlassian MCP tagged with "bug", "defect", "ai-generated", "ai-pdlc" and "aipdlc-v[N]" labels
  (the framework version read live from CLAUDE.md). Confirm-first: nothing is
  written to Jira until the SDET reviews and approves the drafted ticket.
when_to_use: >
  Trigger when the user (SDET) says: "raise a defect", "raise a bug", "log a defect",
  "file a bug", "report a defect", "create a bug ticket", "found a bug", "new defect",
  "SDET bug", "log this issue in Jira".
allowed-tools: Read Grep Glob Bash Write
---

# 🐞 Raise Defect — SDET Bug Reporting to Jira

You help the tester raise a Jira defect by collecting ONLY the fields below, drafting the
ticket, getting **explicit approval**, and then creating it in Jira via the Atlassian MCP.
**Do NOT ask for anything beyond these fields** — no preconditions, steps to reproduce,
expected/actual, priority, reproducibility, or affected story questions.

---

## Phase 0: Preconditions

1. Confirm the Atlassian MCP is available. If it isn't connected, stop and tell the tester to
   connect the Atlassian (Jira) integration first — do not attempt workarounds.
2. Determine the target **Jira project key**:
   - If the tester gave one, use it.
   - Else check `aipdlc-docs/aipdlc-state.md` (Story Tracker Jira column) / `aipdlc-docs/audit.md`
     for the project key already used on this project and propose it.
   - Else ask: `Which Jira project should this defect go into? (PROJECT_KEY)`

---

## Phase 1: Collect the Defect Fields (ONLY these — ask nothing else)

Present as a short numbered list so the tester can answer inline; fill in anything they already
told you and only ask for what's missing. Do not invent details.

1. **Title** — a concise, descriptive summary of the defect.
2. **Description** — what the defect is, in the tester's words (free text; use it as-is).
3. **Severity** — one of:
   ```
   A) Low
   B) Medium
   C) High
   D) Critical
   ```
   This maps to the Jira **Severity** context field on the Bug issue type:
   - Low → `Sev 4 - Low`
   - Medium → `Sev 3 - Med`
   - High → `Sev 2 - High`
   - Critical → `Sev 1 - Critical`
4. **Environment Found** — where the defect was found. If the project's `Environment Found`
   field has a fixed option list (check via `getJiraIssueTypeMetaWithFields`), present those
   options; otherwise accept free text, and prompt with a bracketed suggestion so the tester
   knows the typical shape of an answer, e.g. `**Environment Found** (e.g. Production, QA, Staging, Dev):`.
5. **Discovery Activity** — the activity during which the defect was discovered. If the
   project's `Discovery Activity` field has a fixed option list (check via
   `getJiraIssueTypeMetaWithFields`), present those options; otherwise accept free text.

**Fixed values — NEVER ask the tester for these**:
- **Components** = `Default`
- **Associated Org** = `All`

---

## Phase 2: Draft the Defect

Build the ticket:
- **issueType**: `Bug` (fall back to the project's nearest defect type if `Bug` doesn't exist —
  check with `getJiraProjectIssueTypesMetadata` and confirm the chosen type with the tester).
- **summary**: the Title from Phase 1.
- **description**: built from the Phase 1 answers in **real Markdown** — the Atlassian MCP
  converts Markdown to Jira's ADF automatically. Never use Jira wiki markup (`h3.`, `*`, `#`) —
  it lands as literal raw text. Use this exact structure, with **Environment Found** and
  **Discovery Activity** as headings:
  ```markdown
  ### Description
  [the tester's Description from Phase 1, as-is]

  ### Environment Found
  [the Environment Found answer]

  ### Discovery Activity
  [the Discovery Activity answer]

  ---
  Raised via the AI-PDLC raise-defect skill by SDET. Drafted with AI ([MODEL NAME]).
  📐 AI-PDLC Framework: v[N]
  ```
- **labels**: `bug`, `defect`, `ai-generated`, `ai-pdlc`, and `aipdlc-v[N]`.
  - `[MODEL NAME]` — the actual session model (e.g., "Claude Sonnet 5") — never left as a placeholder.
  - `[N]` — the framework version, read live at runtime from the "AI-PDLC Framework Version" line
    in the project's `CLAUDE.md` (e.g. `aipdlc-v2.3`). Never hardcode and never leave as a placeholder.
- **Severity** (Jira context/custom field on the Bug type — find its field ID via
  `getJiraIssueTypeMetaWithFields`): set to the mapped option (`Sev 4 - Low` / `Sev 3 - Med` /
  `Sev 2 - High` / `Sev 1 - Critical`).
- **Environment Found** / **Discovery Activity**: always included as headings in the
  description (above). If the project ALSO exposes them as custom fields (check
  `getJiraIssueTypeMetaWithFields`), set those fields too with the same answers.
- **Components**: `Default` (if the project's `Component/s` field has no `Default` option,
  check with `getJiraProjectIssueTypesMetadata` and confirm the closest equivalent with the tester).
- **Associated Org**: `All` (if the project doesn't expose an `Associated Org` field, confirm
  with the tester whether to skip it or use the nearest equivalent).

**Show the full drafted ticket to the tester** (project, type, title, description, severity,
environment found, discovery activity, labels — `bug`, `defect`, `ai-generated`, `ai-pdlc`, `aipdlc-v[N]` —
components `Default`, associated org `All`). Do not create anything yet.

---

## Phase 3: Confirm Before Creating (REQUIRED — do not skip)

Ask explicitly: **"Create this defect in Jira project <KEY> with the details above — yes/no?"**
Do not proceed without an explicit yes. If the tester wants edits, revise and re-confirm.

---

## Phase 4: Create the Defect (only after confirmation)

1. Create the issue via the Atlassian MCP `createJiraIssue` with all fields from Phase 2
   (custom fields — Severity, Environment Found, Discovery Activity, Associated Org — go via
   their field IDs discovered from `getJiraIssueTypeMetaWithFields`). **Verify** it was created
   and capture the new **issue key** (e.g. `PROJ-321`).
2. Build the full issue URL: `<site-base-url>/browse/<ISSUE-KEY>` (get the site base URL from
   `getAccessibleAtlassianResources`, or reuse the base already recorded in `aipdlc-docs/`).
3. **Log in `aipdlc-docs/audit.md`** (append-only at the end — never rewrite the file):
   ```markdown
   ## Defect Raised (SDET)
   **Timestamp**: [ISO timestamp]
   **User Email**: [current session email — read live from the session context]
   **Defect**: [<ISSUE-KEY>](<site-base-url>/browse/<ISSUE-KEY>) — [title]
   **Severity**: [Low/Medium/High/Critical → Sev value]
   **Environment Found / Discovery Activity**: [..] / [..]
   **Raised by**: [SDET user]

   ---
   ```
4. Report back to the tester the created **defect key as a clickable link**
   `[<ISSUE-KEY>](<site-base-url>/browse/<ISSUE-KEY>)`.

---

## Execution Rules

1. **Never create a Jira issue without the Phase 3 confirmation** — non-negotiable gate.
2. **Only ask the five Phase 1 fields** (Title, Description, Severity, Environment Found,
   Discovery Activity) — never interview for anything else.
3. **Always tag `bug`, `defect`, `ai-generated`, `ai-pdlc`, and `aipdlc-v[N]` labels** and set issueType to
   the project's bug/defect type. `[N]` is the framework version read live at runtime from the
   "AI-PDLC Framework Version" line in the project's `CLAUDE.md` — never hardcode, never a
   placeholder. A pre-existing similar label (`AI Generated`, `ai_generated`, `bot`, etc.) is NOT
   a substitute for the exact `ai-generated` label.
4. **Always set Components = `Default` and Associated Org = `All`** — mandatory fixed values;
   never leave them blank and never ask the tester to choose them.
5. **Severity is a Jira context (custom) field**, not the built-in priority — set it via its
   field ID with the mapped `Sev N - ...` option value.
6. **Always verify** creation and capture the real issue key; never report a guessed key.
7. **Always log the raised defect in `aipdlc-docs/audit.md`** with the full Jira hyperlink.
8. **Resolve `[MODEL NAME]`** to the actual session model — never leave the placeholder.
9. **Resolve `[N]`** to the framework version read live from the "AI-PDLC Framework Version"
   line in `CLAUDE.md` — never hardcode and never leave the placeholder unresolved.