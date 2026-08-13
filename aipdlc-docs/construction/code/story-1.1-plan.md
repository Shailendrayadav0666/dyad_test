# Code Generation Plan — Story 1.1: Global Light/Dark Theme Toggle (AT-794)

## Grounding
- **Story ACs**: `aipdlc-docs/inception/user-stories/stories.md` Story 1.1, AC-1..AC-6
- **Requirements**: `aipdlc-docs/inception/requirements/requirements.md` REQ-F-01..05, REQ-NF-01..03
- **Epic brief**: `aipdlc-docs/inception/requirements/epic-brief.md`
- **Design references**: none registered in `## Design References` (no design stages ran — Workflow Planning skipped all system-level design stages)
- **Existing code findings** (verified by reading `frontend-react/src/index.css` and `App.jsx` directly):
  - The app already defines its full color palette as CSS custom properties on `:root` (`--bg`, `--surface`, `--text`, `--primary`, etc.) and already has a **`@media (prefers-color-scheme: dark)`** block overriding those same tokens for dark mode. This is the "existing styling approach" REQ-NF-03 requires reusing.
  - There is currently **no manual toggle** — dark mode only follows OS preference, and there is no `data-theme` attribute anywhere.
  - `App.jsx` renders `<header className="app-header">` — this is the natural home for the toggle (AC-1: "header/navbar").
  - No test framework exists in `frontend-react/package.json` (no vitest/jest, no `test` script) — one must be added to satisfy the ≥90% coverage gate.

## Plan

- [ ] **Step 1** (→ REQ-NF-03, AC-6): Re-key the dark-theme CSS variable overrides in `frontend-react/src/index.css` from `@media (prefers-color-scheme: dark)` to `:root[data-theme="dark"]` — this makes theme explicit/manual instead of OS-driven, reusing the exact same token structure (no new theming system introduced). Light mode remains the bare `:root` default.
- [ ] **Step 2** (→ REQ-F-04, AC-3): Create `frontend-react/src/hooks/useTheme.js` — a small hook holding theme state (`useState('light')`, no persistence read/write per REQ-F-05), and a `useEffect` that sets `document.documentElement.setAttribute('data-theme', theme)` whenever it changes, so `index.css`'s new selector applies globally and instantly (AC-2).
- [ ] **Step 3** (→ REQ-F-01, REQ-F-02, AC-1): Create `frontend-react/src/components/ThemeToggle.jsx` — a single icon button (🌙 moon shown in light mode / ☀️ sun shown in dark mode, tapping flips the theme), styled via existing `.btn`/`.btn-secondary` classes (no new CSS framework).
- [ ] **Step 4** (→ REQ-F-01, REQ-F-03, REQ-F-05, AC-1, AC-2, AC-3, AC-4): Wire `useTheme` + `<ThemeToggle>` into `frontend-react/src/App.jsx`'s `<header className="app-header">`, alongside the existing brand block. No localStorage read/write for theme (session-only, resets to light on every fresh load — REQ-F-05/AC-4 is satisfied by construction: state is never persisted).
- [ ] **Step 5** (→ REQ-NF-02, AC-5): Add minimal header-layout CSS (flex row: brand left, toggle right) to `index.css` under the existing `.app-header`/`.header-brand` rules, and spot-check that both themes keep contrast on the toggle button itself (uses existing `--surface`/`--border`/`--text` tokens, so no new contrast risk introduced).
- [ ] **Step 6 — Unit Test & Coverage (≥90%, MANDATORY)**:
  - [ ] Add a minimal test toolchain (not present in the repo): `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom` as devDependencies; add a `"test": "vitest run --coverage"` script and a `vitest.config.js` (jsdom environment, coverage provider `v8`, reporters including `lcov`/`json` for a machine-readable report).
  - [ ] Write `frontend-react/src/hooks/useTheme.test.jsx` — asserts default state is `'light'`, toggling flips to `'dark'` and back, and the `data-theme` attribute on `document.documentElement` is kept in sync.
  - [ ] Write `frontend-react/src/components/ThemeToggle.test.jsx` — asserts the correct icon renders per theme and clicking calls the toggle handler.
  - [ ] Run the suite with coverage; iterate until new/changed files (`useTheme.js`, `ThemeToggle.jsx`, and the touched lines in `App.jsx`) are ≥90% covered.
  - [ ] Save `unit-test-run.log`, `coverage-report.*` (lcov/json), and `evidence-manifest.md` to `aipdlc-docs/construction/code/unit-test-evidence/story-1.1/`.

## Requirements Trace Completeness Self-Check
| REQ-ID | AC | Plan Step(s) |
|---|---|---|
| REQ-F-01 | AC-1 | Steps 3, 4 |
| REQ-F-02 | AC-1 | Step 3 |
| REQ-F-03 | AC-2 | Steps 2, 4 |
| REQ-F-04 | AC-3 | Step 2 |
| REQ-F-05 | AC-4 | Steps 2, 4 (no persistence implemented) |
| REQ-NF-01 | AC-2 | Step 2 (instant via CSS variables, no re-render cost) |
| REQ-NF-02 | AC-5 | Step 5 |
| REQ-NF-03 | AC-6 | Step 1 |

Every covered REQ-ID and every AC appears in ≥1 step. ✅ Trace complete.
