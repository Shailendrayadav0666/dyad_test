# User Stories - Detailed Steps

## Purpose
**Convert requirements into user-centered stories with acceptance criteria**

User Stories focus on:
- Translating business requirements into user-centered narratives
- Defining clear acceptance criteria for each story
- Creating user personas that represent different stakeholder types
- Establishing shared understanding across teams
- Providing testable specifications for implementation

## Prerequisites
- Workspace Detection must be complete
- Requirements Analysis recommended (can reference requirements if available)

> 🔴 **Three parts in this stage**: **Part 1 — Planning** (ask team size FIRST, then plan), **Part 2 — Generation** (stories + personas + populate the Story Tracker), **Part 3 — Push to Jira** (always asked). The team size drives story granularity; each story's `Requires` dependencies are assigned in the **Dependency Graph** stage that runs immediately after this one.

---

# PART 1: PLANNING

## Step 1: Begin Story Planning — Ask Team Size FIRST

User Stories always execute for every software development request.

**Before creating the plan, ask the team size** — this is asked FIRST because story **granularity depends on it**:

```
❓ How many developers will be working on implementation? (team size)
   Stories are sized so that at least [team_size] independent stories are
   workable in parallel at any time, so no developer sits idle waiting on
   another's in-progress work (unless the architecture makes parallelism impossible).
```

- Record the answer as `team_size` in `aipdlc-docs/aipdlc-state.md`. **The Dependency Graph stage reuses this value — it is not asked again there.**
- Tune story granularity to `team_size`: break work into enough small, independent stories that ≥ `team_size` stories can run in parallel.
- Log the question and answer in `aipdlc-docs/audit.md`.

Then proceed to story plan creation.

## Step 2: Create Story Plan
- Assume the role of a product owner
- Generate a comprehensive plan with step-by-step execution checklist for story development
- Each step and sub-step should have a checkbox []
- Focus on methodology and approach for converting requirements into user stories

## Step 3: Generate Context-Appropriate Questions
**DIRECTIVE**: Thoroughly analyze the requirements and context to identify ALL areas where clarification would improve story quality and team understanding. Be proactive in asking questions to ensure comprehensive user story development.

**CRITICAL**: Default to asking questions when there is ANY ambiguity or missing detail that could affect story quality. It's better to ask too many questions than to create incomplete or unclear stories.

**See `common/question-format-guide.md` for question formatting rules**

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve story creation decisions
- **When in doubt, ask the question** - overconfidence leads to poor stories

### 🔴 MANDATORY QUESTION — Number of Stories to Create (smart suggestion, always included)

**Every generated question set MUST include this question — it is NOT optional and NOT context-dependent.** While the other questions in this step are context-appropriate (asked only when relevant), the number-of-stories question is ALWAYS asked, with a concrete AI-computed recommendation and the reasons behind it.

Before writing it into the plan, **do the analysis** so the suggestion is grounded, not arbitrary:
- Read the Parent Epic brief (`aipdlc-docs/inception/requirements/epic-brief.md`) and `aipdlc-docs/inception/requirements/requirements.md` (if present).
- Count the distinct capabilities / functional requirements (REQ-IDs), user journeys, and personas involved, and gauge their complexity.
- Compute a **recommended story count** that (a) keeps each story small, independent, and INVEST-compliant, and (b) yields **≥ `team_size` independently workable stories** (from Step 1) so no developer is left idle.

Embed EXACTLY this question in the plan (fill in the computed values — never leave it open-ended without a recommendation):

```
❓ How many user stories should I create for this work?

   💡 Recommended: [X] stories  (suggested range: [X-lo]–[X-hi])

   Why [X]:
   - [reason 1 — e.g. "covers 8 functional requirements grouped into cohesive slices"]
   - [reason 2 — e.g. "keeps ≥ [team_size] stories runnable in parallel so no developer is idle"]
   - [reason 3 — e.g. "each story stays small/testable (INVEST) rather than a multi-week epic"]

   Reply with a number to override, or "ok"/"use recommended" to accept [X].
[Answer]:
```

- **ALWAYS compute and show a concrete recommended number `[X]` and the reasons** — never present this as an open-ended question with no suggestion.
- When the user accepts, use `[X]`. If the user gives a different number, use theirs — but if it would break the parallelism rule (fewer than `team_size` independent stories) or force oversized/undersized stories, flag the trade-off during Step 9/10 analysis and confirm before generation.
- Record the agreed value as `target_story_count` in `aipdlc-docs/aipdlc-state.md`. The Generation phase (Part 2) MUST create this many stories (adjusting only if Step 9/10 analysis or the Step 18.5 coverage check proves a different count is required — log any deviation and its reason in audit.md).

**Question categories to evaluate** (consider ALL categories):
- **User Personas** - Ask about user types, roles, characteristics, and motivations
- **Story Granularity** - Ask about appropriate level of detail, story size, and breakdown approach
- **Story Format** - Ask about format preferences, template usage, and documentation standards
- **Breakdown Approach** - Ask about organization method, prioritization, and grouping strategies
- **Acceptance Criteria** - Ask about detail level, format, testing approach, and validation methods
- **User Journeys** - Ask about user workflows, interaction patterns, and experience flows
- **Business Context** - Ask about business goals, success metrics, and stakeholder needs
- **Technical Constraints** - Ask about technical limitations, integration requirements, and system boundaries

## Step 4: Include Mandatory Story Artifacts in Plan
- **ALWAYS** include these mandatory artifacts in the story plan:
  - [ ] Generate stories.md with user stories following INVEST criteria
  - [ ] stories.md MUST begin with the Parent Epic header line (see Step 16 — Epic header rule)
  - [ ] Generate personas.md with user archetypes and characteristics
  - [ ] Ensure stories are Independent, Negotiable, Valuable, Estimable, Small, Testable
  - [ ] Include acceptance criteria for each story
  - [ ] **EVERY story carries a `**Covers**: [REQ-IDs]` line** naming the requirements from `requirements.md` its acceptance criteria implement (MANDATORY — see `common/requirements-traceability.md` Rule 2; "reference requirements if available" is superseded, coverage is never optional)
  - [ ] **Requirements Coverage Matrix + full-coverage check** — every REQ-ID fully expressed by the union of its covering stories' ACs (see Step 18 / `common/requirements-traceability.md` Rule 3)
  - [ ] Map personas to relevant user stories

## Step 5: Present Story Options
- Include different approaches for story breakdown in the plan document:
  - **User Journey-Based**: Stories follow user workflows and interactions
  - **Feature-Based**: Stories organized around system features and capabilities
  - **Persona-Based**: Stories grouped by different user types and their needs
  - **Domain-Based**: Stories organized around business domains or contexts
  - **Epic-Based**: Stories structured as hierarchical epics with sub-stories
- Explain trade-offs and benefits of each approach
- Allow for hybrid approaches with clear decision criteria

## Step 6: Store Story Plan
- Save the complete story plan with embedded questions in `aipdlc-docs/inception/plans/` directory
- Filename: `story-generation-plan.md`
- Include all [Answer]: tags for user input
- Ensure plan is comprehensive and covers all story development aspects

## Step 7: Request User Input
- Ask user to fill in all [Answer]: tags directly in the story plan document
- Emphasize importance of audit trail and decision documentation
- Provide clear instructions on how to fill in the [Answer]: tags
- Explain that all questions must be answered before proceeding

## Step 8: Collect Answers
- Wait for user to provide answers to all questions using [Answer]: tags in the document
- Do not proceed until ALL [Answer]: tags are completed
- Review the document to ensure no [Answer]: tags are left blank

## Step 9: ANALYZE ANSWERS (MANDATORY)
Before proceeding, you MUST carefully review all user answers for:
- **Vague or ambiguous responses**: "mix of", "somewhere between", "not sure", "depends", "maybe", "probably"
- **Undefined criteria or terms**: References to concepts without clear definitions
- **Contradictory answers**: Responses that conflict with each other
- **Missing generation details**: Answers that lack specific guidance for implementation
- **Answers that combine options**: Responses that merge different approaches without clear decision rules
- **Incomplete explanations**: Answers that reference external factors without defining them
- **Assumption-based responses**: Answers that assume knowledge not explicitly stated

## Step 10: MANDATORY Follow-up Questions
If the analysis in step 9 reveals ANY ambiguous answers, you MUST:
- Create a separate clarification questions file using [Answer]: tags
- DO NOT proceed to approval until ALL ambiguities are completely resolved
- **CRITICAL**: Be thorough - ask follow-up questions for every unclear response
- Examples of required follow-ups:
  - "You mentioned 'mix of A and B' - what specific criteria should determine when to use A vs B?"
  - "You said 'somewhere between A and B' - can you define the exact middle ground approach?"
  - "You indicated 'not sure' - what additional information would help you decide?"
  - "You mentioned 'depends on complexity' - how do you define complexity levels and thresholds?"
  - "You chose 'hybrid approach' - what are the specific rules for when to use each method?"
  - "You said 'probably X' - what factors would make it definitely X vs definitely not X?"
  - "You referenced 'standard practice' - can you define what that standard practice is?"

## Step 11: Avoid Implementation Details
- Focus on story creation methodology, not prioritization or development tasks
- Do not discuss technical generation at this stage
- Avoid creating development timelines or sprint planning
- Keep focus on story structure and format decisions

## Step 12: Log Approval Prompt
- Before asking for approval, log the prompt with timestamp in `aipdlc-docs/audit.md`
- Include the complete approval prompt text
- Use ISO 8601 timestamp format

## Step 13: Wait for Explicit Approval of Plan
- Do not proceed until the user explicitly approves the story approach
- Approval must be clear and unambiguous
- If user requests changes, update the plan and repeat the approval process

## Step 14: Record Approval Response
- Log the user's approval response with timestamp in `aipdlc-docs/audit.md`
- Include the exact user response text
- Mark the approval status clearly

---

# PART 2: GENERATION

## Step 14.5: Ask Story Creation Mode (MANDATORY — before generating any story)
- [ ] Log the prompt in `aipdlc-docs/audit.md` with timestamp, then ask:
  ```
  ❓ How would you like the user stories to be created?
     A) One by one — I create a story, you review & approve it, then I create the next
     B) All at once — I generate every story together for a single review
  [Answer]:
  ```
- [ ] **Present EXACTLY the two options above — A and B, nothing else.** Do NOT add a third option, an "Other/custom" choice, a "skip" choice, or any extra alternative to this prompt. It is a strict A/B question.
- [ ] Wait for the answer. Record it as `story_creation_mode: one-by-one | all-at-once` in `aipdlc-docs/aipdlc-state.md`.
- [ ] Log the user's complete raw response in `aipdlc-docs/audit.md` with timestamp.
- [ ] **In BOTH modes**, after ALL stories are created, the final full approval (Steps 19–22) is still MANDATORY — per-story approvals in one-by-one mode do NOT replace it.

## Step 15: Load Story Generation Plan
- [ ] Read the complete story plan from `aipdlc-docs/inception/plans/story-generation-plan.md`
- [ ] Identify the next uncompleted step (first [ ] checkbox)
- [ ] Load the context and requirements for that step

## Step 16: Execute Current Step
- [ ] Perform exactly what the current step describes
- [ ] Generate story artifacts as specified in the plan
- [ ] Follow the approved methodology and format from Planning
- [ ] Use the story breakdown approach specified in the plan
- [ ] **Apply the `story_creation_mode` from Step 14.5 when generating stories**:

**🔗 Epic header rule (BOTH creation modes — applies when stories.md is first created)**:
- [ ] The VERY FIRST line of `aipdlc-docs/inception/user-stories/stories.md` MUST be the Parent Epic header:
  ```markdown
  EPIC JIRA TICKET: [full Epic URL, e.g. https://<site>.atlassian.net/browse/PROJ-50]
  ```
  Read the Epic URL from `## Jira` in `aipdlc-docs/aipdlc-state.md` (Epic URL line). If no Parent Epic is recorded at creation time, write `EPIC JIRA TICKET: none (no Parent Epic recorded)` — and when an Epic is later resolved during the Jira push (Step 25), UPDATE this header line with the full Epic URL in the same interaction. All stories are appended BELOW this header.

**🧾 Requirements traceability rule (BOTH creation modes — applies to every story generated)**:
- [ ] EVERY story written to `stories.md` carries a `**Covers**: REQ-F-xx, REQ-NF-yy` line naming the requirement IDs from `aipdlc-docs/inception/requirements/requirements.md` its acceptance criteria implement (`common/requirements-traceability.md` Rule 2). A story with an empty `Covers` is invalid — fix it before presenting the story. For multi-requirement stories, an AC-level breakdown (`AC-n → REQ-ID`) is encouraged. When a requirement is split across stories for parallelism, the integration behavior between the slices MUST be owned by an explicit AC on one of them.

**IF `story_creation_mode` = one-by-one**:
- [ ] Generate exactly ONE story at a time and present it to the user:
  ```
  📖 Story [N.M]: [Title]
  [full story: narrative, acceptance criteria, persona]

  ❓ Approve this story? (approve / request changes)
  ```
- [ ] Log the per-story approval prompt in `aipdlc-docs/audit.md` with timestamp BEFORE asking
- [ ] Wait for the user's response — do NOT generate the next story until this one is approved
- [ ] If changes are requested: apply them, re-present the story, and repeat until approved
- [ ] Log the user's complete raw response (approval or change request) in `aipdlc-docs/audit.md` with timestamp
- [ ] Append the approved story to `stories.md`, then repeat for the next story until all stories are created
- [ ] After the LAST story is approved, continue to Step 17 — the final full approval (Steps 19–22) still applies

**IF `story_creation_mode` = all-at-once**:
- [ ] Generate ALL stories together in one pass (single review happens at Steps 19–22)

## Step 17: Update Progress
- [ ] Mark the completed step as [x] in the story generation plan
- [ ] Update `aipdlc-docs/aipdlc-state.md` current status
- [ ] **Populate the Story Tracker**: add one row per generated story to the `## Story Tracker` table in `aipdlc-docs/aipdlc-state.md`. Columns: Story ID, Title, **Requires = `TBD`** (assigned next stage), `Jira` = `—`, `Status` = `🟢 Ready for Development` (the initial status for every new story), Start/End blank, `Recorded` = current timestamp. Use the table format defined in `inception/dependency-graph-generation.md` (Story Tracker Table Format section).
- [ ] Save all generated artifacts

## Step 18: Continue or Complete Generation
- [ ] If more steps remain, return to Step 15
- [ ] If all steps complete, verify stories are ready for next stage
- [ ] Ensure all mandatory artifacts are generated

## Step 18.5: Requirements Full-Coverage Check (MANDATORY — automatic, BEFORE presenting GATE 1)
Execute `common/requirements-traceability.md` Rule 3 — silent and blocking, NO user prompt:
- [ ] Build the coverage matrix: every REQ-ID in `requirements.md` → the story ID(s) whose `Covers` names it
- [ ] **Gap A — uncovered requirement** (a REQ-ID with zero covering stories): add/extend stories automatically, then re-check
- [ ] **Gap B — partial coverage** (the union of the covering stories' ACs does not express the requirement's full end-to-end behavior, including cross-story seams): strengthen the ACs automatically, then re-check
- [ ] Append the matrix to `stories.md` as `## Requirements Coverage Matrix` (REQ-ID | covering stories | status)
- [ ] Log the check outcome (pass, or gaps found + fixes applied) in `aipdlc-docs/audit.md`
- [ ] Include a coverage summary line in the Step 20 completion message (e.g., `🧾 Requirements coverage: 12/12 REQ-IDs fully covered by story ACs`)
- [ ] Do NOT present the Step 19–20 approval until the matrix shows every REQ-ID fully covered

## Step 19: Log Approval Prompt
- **This final full approval is MANDATORY in BOTH creation modes** — in one-by-one mode, per-story approvals do NOT replace this end-of-stage approval of the complete story set
- **🚧 This is GATE 1** — the final approval of the complete story set (both creation modes)
- Before asking for approval, log the prompt with timestamp in `aipdlc-docs/audit.md`
- **No gate marker on this prompt entry — the word "GATE" must NOT appear anywhere in this entry's `##` heading.** Use a plain heading like `## User Stories — Full Story Set Approval Prompt` (NEVER `## User Stories — GATE 1 Approval Prompt`). "GATE 1" appears ONLY in the heading of the response entry (Step 22), where the user's approve/reject decision is recorded
- Include the complete approval prompt text
- Use ISO 8601 timestamp format

## Step 20: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 📚 User Stories Complete
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of generated stories
        - Format: "User stories generation has created [description]:"
        - List key personas generated (bullet points)
        - List user stories created with counts and organization
        - Mention story structure and compliance (INVEST criteria, acceptance criteria)
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the user stories and personas at: `aipdlc-docs/inception/user-stories/stories.md` and `aipdlc-docs/inception/user-stories/personas.md`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** -  Ask for modifications to the stories or personas based on your review  
> ✅ **Approve & Continue** - Approve user stories, then (after the optional Jira push) proceed to the **Dependency Graph** stage

---
```

## Step 21: Wait for Explicit Approval of Generated Stories
- Applies in BOTH creation modes (one-by-one AND all-at-once) — this is the approval of the FULL story set
- Do not proceed until the user explicitly approves the generated stories
- Approval must be clear and unambiguous
- If user requests changes, update stories and repeat the approval process

## Step 22: Record Approval Response
- Log the user's response with timestamp in `aipdlc-docs/audit.md` — **whether it is an approval OR a rejection/change request**
- **The gate is marked in the entry's `##` HEADING — there is NO separate `**GATE Number**:` field.** Use:
  - Approved: `## User Stories — GATE 1 Full Story Set Approved`
  - Rejected: `## User Stories — GATE 1 Full Story Set Rejected — Changes Requested`
- The GATE 1 heading applies to EVERY response at this gate — approved AND rejected outcomes alike; if changes are requested and the gate is re-asked, each re-ask's RESPONSE entry uses a GATE 1 heading again (prompt entries never carry the gate marker). Entry body format is unchanged
- Include the exact user response text
- Mark the outcome clearly (✅ approved / ❌ rejected — changes requested)

## Step 23: Update Progress
- Mark User Stories stage complete in `aipdlc-state.md`
- Update the "Current Status" section
- Prepare for transition to **Part 3 (Push to Jira)**, then the **Dependency Graph** stage

---

# PART 3: PUSH TO JIRA (ALWAYS ASK)

After stories are generated and approved, **ALWAYS** offer to push them to a Jira board. This step always runs (the ask is mandatory); the actual push happens only if the user agrees. Stories remain fully implementable from the local Story Tracker if the user declines.

> **Note**: This pushes **stories** and links each one to the **Parent Epic** — the existing Jira Epic the user provided at workflow start (stored in `aipdlc-docs/aipdlc-state.md` under `## Jira`).

## Step 24: Ask Whether to Push
- [ ] Log the prompt in `aipdlc-docs/audit.md` with timestamp
- [ ] Present:
  ```
  📚 [N] user stories generated.
  ❓ Push these stories to a Jira board now? (yes / no)
     [Include this line ONLY if aipdlc-state.md `## Jira` records a Parent Epic:
      "Each story will be linked to your Parent Epic [EPIC-KEY]."]
     (You can also push later, or implement directly from the local Story Tracker.)
  ```
- [ ] If **no**: leave the `Jira` column as `—`, note the decision in audit.md, and proceed to the Dependency Graph stage. Stories remain implementable locally.

## Step 25: Resolve the Parent Epic & Jira Target (only if yes)
- [ ] **Read the Parent Epic** from `aipdlc-docs/aipdlc-state.md` `## Jira` (Epic key + URL + Project Key). This works even in a brand-new chat — the Epic was stored at workflow start.
- [ ] If **no Parent Epic is recorded** (it was not provided at workflow start), ask now:
  ```
  ❓ Which existing Jira Epic should these stories be linked to?
     Paste the Epic link or key (e.g., PROJ-50), or type "none" to push unlinked.
  ```
  Store the answer in `aipdlc-state.md` under `## Jira` (Parent Epic, Epic URL, Project Key) before pushing.
- [ ] **If the user chose "none"** (or `## Jira` records `Parent Epic: none`): record `Parent Epic: none` in `## Jira`, **ask the user directly for the Jira PROJECT_KEY** (there is no Epic key to derive it from) and store it in `## Jira`, skip Epic verification below, and skip Step 26b entirely.
- [ ] Otherwise (an Epic is recorded):
  - **Verify the Epic exists** via the Atlassian MCP (`getJiraIssue [EPIC-KEY]`). If it cannot be fetched, STOP and report — do not push stories against an unverified Epic.
  - **Derive the PROJECT_KEY from the Epic key** (e.g., `PROJ-50` → `PROJ`) and confirm it with the user — do NOT assume or hard-code it.
- [ ] Confirm the issue type to create (default: `Story`).

## Step 26: Create Issues via Atlassian MCP
- [ ] For each story, create a Jira issue using the Atlassian (Rovo) MCP:
  ```
  @atlassian createJiraIssue in project [PROJECT_KEY]:
    issueType: Story
    summary: [story title]
    description: [story narrative + acceptance criteria + persona] {Note: Markdown with REAL line breaks — never literal \n escapes (Rovo converts Markdown → ADF).}
                {End the description with a footer line on its own: "---" then "Built with AI-PDLC v[N]", where [N] is read at runtime from the "AI-PDLC Framework Version" line in CLAUDE.md (do not hardcode a number) — records which framework version this work unit was developed with.}
    labels: [ai-pdlc, aipdlc-v[N]]   {aipdlc-v[N] = the FULL framework version (including the minor, e.g. 2.3 → aipdlc-v2.3 — never the major only, never aipdlc-v2), read at runtime from the "AI-PDLC Framework Version" line in CLAUDE.md; do not hardcode; this is a board-filterable version tag that mirrors the description footer.}
    Component: default
    Organization: All Orgs
    Severity: Low
  ```
- [ ] **Mandatory story fields** — the project requires these on every story; ALWAYS set them to these fixed values (do not ask the user, do not vary per story):
  - **Component** = `default`
  - **Organization** = `All Orgs`
  - **Severity** = `Low`
- [ ] These may be custom fields in the project. If `createJiraIssue` rejects them by name, call `getJiraIssueTypeMetaWithFields` (project = [PROJECT_KEY], issueType = Story) to resolve their field IDs (e.g., `components`, `customfield_XXXXX`) and the exact allowed option values, then retry the creation with those IDs. Never skip these fields — creation without them will fail or leave the story invalid.
- [ ] **VERIFY** each creation succeeded; capture the returned issue key (e.g., `PROJ-123`).
- [ ] If a creation fails, STOP, report the error, and do not silently continue.

## Step 26a: Transition Each Story to "Ready for Development" (MANDATORY)
- [ ] Jira creates issues in the default initial status (e.g., Backlog / To Do) — stories MUST NOT be left there. Immediately after each story is created:
  1. Call `getTransitionsForJiraIssue [STORY-KEY]` to list available transitions
  2. Find the transition to **"Ready for Development"** (accept close variants like "Ready for Dev" / "Ready to Develop"); call `transitionJiraIssue [STORY-KEY]` with that transition ID
  3. **VERIFY** by fetching the issue back and confirming its status is Ready for Development
- [ ] If no such transition is available from the initial status, check for an intermediate transition path (e.g., Backlog → To Do → Ready for Development) and walk it. If the status genuinely doesn't exist in the project's workflow, STOP and report to the user — do not leave stories silently in Backlog/To Do.
- [ ] Log each transition (issue key, from → to status) in `aipdlc-docs/audit.md` with timestamp.

## Step 26b: Link Each Story to the Parent Epic (skip only if user chose "none")
- [ ] For each created story, set its parent to the Parent Epic — confirm-first:
  ```
  @atlassian editJiraIssue [STORY-KEY]: set Epic Link / parent = [EPIC-KEY]
  # or, if the project uses issue links instead of parent:
  @atlassian createIssueLink: [EPIC-KEY] "is parent of" / "relates to" [STORY-KEY]
  ```
  (If the project supports it, setting `parent` directly in `createJiraIssue` at Step 26 is equally valid — then this step is verification only.)
- [ ] **VERIFY each link landed**: fetch each story back and confirm its parent/Epic Link is [EPIC-KEY]. If a link fails, STOP and report — never leave stories silently unlinked.
- [ ] Report the Epic → linked story keys mapping to the user.

## Step 27: Write Keys Back
- [ ] In `aipdlc-docs/inception/user-stories/stories.md`, annotate each story with its Jira key and link (`**Jira**: PROJ-123` + URL).
- [ ] Verify the `EPIC JIRA TICKET:` header at the TOP of stories.md carries the resolved Parent Epic's full URL — update it now if it still reads `none` (or leave `none` only if the user explicitly chose "none" at push time).
- [ ] In the `## Story Tracker` of `aipdlc-docs/aipdlc-state.md`, set each story's `Jira` column to its key and update `Recorded` to the current timestamp.
- [ ] Confirm to the user: list each Story ID → Jira key.

## Step 28: Log the Push
- [ ] Append to `aipdlc-docs/audit.md`: the user's push decision, the PROJECT_KEY, the Parent Epic key, the created issue keys, and the story→Epic links, with timestamps.
- [ ] **NEVER create or link Jira issues without explicit user confirmation in this turn.**

---

# CRITICAL RULES

## Planning Phase Rules
- **CONTEXT-APPROPRIATE QUESTIONS**: Only ask questions relevant to this specific context
- **MANDATORY ANSWER ANALYSIS**: Always analyze answers for ambiguities before proceeding
- **NO PROCEEDING WITH AMBIGUITY**: Must resolve all vague answers before generation
- **EXPLICIT APPROVAL REQUIRED**: User must approve plan before generation starts

## Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the story generation plan
- **FOLLOW PLAN EXACTLY**: Do not deviate from the step sequence
- **UPDATE CHECKBOXES**: Mark [x] immediately after completing each step
- **USE APPROVED METHODOLOGY**: Follow the story approach from Planning
- **VERIFY COMPLETION**: Ensure all story artifacts are complete before proceeding

## Completion Criteria
- All planning questions answered and ambiguities resolved
- Story plan explicitly approved by user
- Every story carries a non-empty `**Covers**:` line; the Requirements Coverage Matrix in stories.md shows EVERY REQ-ID from requirements.md fully covered (Step 18.5 passed)
- Story creation mode asked and recorded (Step 14.5); in one-by-one mode, every story individually approved and logged in audit.md
- Final full approval of the complete story set obtained in BOTH modes (Steps 19–22) and logged in audit.md
- All steps in story generation plan marked [x]
- All story artifacts generated according to plan (stories.md, personas.md)
- Generated stories explicitly approved by user
- Stories verified and ready for next stage
