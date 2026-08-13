# Dependency Graph Generation (Inception — immediately after User Stories)

**Purpose**: Analyse story dependencies. Each story gets a `requires` list; stories whose prerequisites are all Done have no dependencies on each other and can be implemented in parallel by different developers. `Requires` is stamped onto every story in the Story Tracker and in `stories.md`.

**Always executes** right after User Stories. Produces `aipdlc-docs/inception/dependency-graph.yml` and records each story's `Requires` in the Story Tracker.

## Execution Steps

1. **MANDATORY**: Log start of Dependency Graph stage in audit.md
2. **Reuse `team_size`** collected during User Stories Part 1 (it already drove story granularity — do NOT re-ask). Only if it is missing, ask now:
   ```
   ❓ How many developers will be working on implementation?
      Used to aim for at least [team_size] independent stories being
      available at any time where the architecture allows, so no developer
      is idle waiting on another's in-progress work.
   ```
   Record/confirm as `team_size`.
3. **Determine story dependencies** — for each story, infer from its prerequisites, or ask:
   ```
   Which stories must be fully Done before Story N.M can start?
   (Enter story IDs separated by commas, or "none")
   ```
   Apply **TRUE-PARALLELISM RULES** below before finalising.
4. **Update every story** in `aipdlc-docs/inception/user-stories/stories.md` and the Story Tracker in `aipdlc-state.md` with its `Requires` list
5. **Write `aipdlc-docs/inception/dependency-graph.yml`** (see schema below)
6. **Add `## Dependency Graph` section to `aipdlc-docs/aipdlc-state.md`** containing:
   - Mermaid `graph TD` of the dependency chain
   - Ready-stories summary: which stories have no prerequisites and can start immediately, and which are blocked by what

7. **Wait for Explicit Approval**: Show the graph and summary, ask:
   ```
   📊 Dependency Graph complete.
   - Total stories: K  |  Immediately startable (no prerequisites): M
   - team_size: N  (target: ≥ N independent stories available at a time)

   Proceed? (yes / revise graph)
   ```
   Block until user confirms.
8. **MANDATORY**: Log user's response in audit.md with complete raw input

## TRUE-PARALLELISM RULES (apply when computing `requires`)

- **R1 Seed story**: If a file doesn't exist yet and is needed by 2+ stories, one seed story must create it first; all others `requires` that seed — prevents unmergeable git conflicts
- **R2 Contract rule**: A story only `requires` another when it needs that story's **code to exist at compile/run time**, not merely its API shape
- **R3 Mock rule**: A frontend/consumer story MAY drop a `requires` edge when its tests use mocks/stubs AND a separate integration story verifies real wiring
- **R4 No artificial chains**: Don't add `requires` for narrative ordering — only for genuine runtime/compile-time dependencies
- **R5 Parallelism target**: Aim for at least `team_size` independent stories being available at any time where the architecture allows

## `aipdlc-docs/inception/dependency-graph.yml` Schema

```yaml
version: 1
generated_at: YYYY-MM-DD
team_size: 2

shared_files:
  - package.json          # files touched by 2+ stories — may cause merge conflicts
  - src/routes.ts

stories:
  - id: "1.1"
    title: Story title
    jira: LOCAL           # updated to PROJ-101 after Jira export
    requires: []          # story IDs that must be Done before this starts
    enables: ["1.2"]      # reverse edges (informational only)
```

## Story Tracker Table Format

Create/update in `aipdlc-state.md` under `## Story Tracker` after this stage:

| Story | Title   | Requires | Jira     | Status         | PR         | Merged | Start      | End        | Recorded           |
|-------|---------|----------|----------|----------------|------------|--------|------------|------------|--------------------|
| 1.1   | [Title] | none     | —        | 🟢 Ready for Development | —          | —      |            |            | [YYYY-MM-DD HH:MM] |

- **Requires**: Assigned by this Dependency Graph stage.
- **Jira**: Populated from Part 3 of User Stories (Jira push; each pushed story is linked to the Parent Epic in `## Jira`). Use `—` if story is local-only.
- **PR**: The story's Pull Request URL, recorded by `dev-implement` when the PR is raised (Section D). `—` until a PR exists.
- **Merged**: `no` once the PR is raised, `yes` once the PR is confirmed merged into the epic branch, `—` before a PR exists. A story moves to 🧪 Ready for Testing ONLY when this becomes `yes` (checked via `gh pr view` by the `sdet-list-work` skill, which promotes it once SDET has tested it).
- **Start**: Timestamp when story moves to 🔵 In Development.
- **End**: Timestamp when story moves to 🧪 Ready for Testing (i.e. when its PR is merged).
- **Recorded**: Timestamp of the last tracker update for this row.
