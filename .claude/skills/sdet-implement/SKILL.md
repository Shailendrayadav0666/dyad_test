---
name: sdet-implement
description: >
  SDET Build and Test for ONE story, run in PARALLEL with development. Build and Test is not a stage
  of the development workflow — it lives here. Resolves a story, reads its acceptance criteria from
  Jira / stories.md plus requirements.md and the construction design artifacts — never application
  source code — and writes that story's Build and Test artifacts as MANUAL test steps
  (build verification, integration, E2E, API, contract, security, performance, accessibility) into
  aipdlc-docs/tests/<JIRA-ID>-<jira-title>/, with every test case traced to an acceptance criterion.
  Needs no DEV code, branch, PR or merge, so SDET can run it the moment a story exists — it never
  depends on or waits for the dev's branch/PR. It DOES cut its own `sdet/<JIRA-ID>-<title>` branch
  from the resolved integration branch (Epic Branch for epic cycles, Bug/Enhancement Branch for
  those cycles), commit the generated docs, and (confirm-first) push and raise its own PR back into
  that branch, labeled `ai-generated` + `aipdlc-v<version>` (the framework version read live from
  CLAUDE.md, same convention as pr-generator). No test automation, no test execution, no application code
  changes — and never changes story or Jira status (that remains `sdet-list-work`'s job).
when_to_use: >
  Trigger when the user says: "/sdet-implement 1.2", "/sdet-implement PROJ-123", "/sdet-implement",
  "build and test for story 1.2", "generate test steps for story 1.2",
  "manual test cases for PROJ-123", "test plan for this story",
  "test cases from acceptance criteria", "SDET this story", "run sdet-implement", "sdet-implement".
allowed-tools: Read Grep Glob Bash Write
---

# 🧪 SDET Implement — Build and Test (per story)

Load and execute the agent instructions from:

```
.aipdlc-rule-details/agents/sdet-implement-agent.md
```

Read that file completely and follow every step defined in it.

