# Requirements — Light / Dark Theme Toggle (AT-793)

## Intent Analysis Summary
- **User Request**: Add a light mode / dark mode toggle to the UI, fast and simple.
- **Request Type**: New Feature
- **Scope Estimate**: Single Component (frontend UI — global theme layer + header control)
- **Complexity Estimate**: Trivial

## Source
- Jira Epic: [AT-793](https://3pillarglobal-demo.atlassian.net/browse/AT-793)
- Epic Brief: `aipdlc-docs/inception/requirements/epic-brief.md`
- Reverse Engineering Artifacts: `aipdlc-docs/inception/reverse-engineering/` (frontend is a React/Vite SPA under `frontend-react/`, no existing theming system found)

## Clarifications Received
- Toggle placement: app header/navbar, visible on every page.
- Default theme on load: light mode.
- Control style: simple icon button (sun/moon), swaps icon and toggles theme on click.

## Functional Requirements

- **REQ-F-01**: The UI SHALL provide a single toggle control, placed in the app header/navbar, that switches the entire application between a light theme and a dark theme.
- **REQ-F-02**: The toggle SHALL render as a simple icon button showing a sun icon in dark mode (tap to go light) and a moon icon in light mode (tap to go dark), or the reverse convention, consistently applied.
- **REQ-F-03**: On toggle activation, the theme change SHALL apply immediately and globally — all pages and components currently rendered SHALL reflect the new theme without a page reload.
- **REQ-F-04**: The application SHALL default to light mode on every fresh load (no persistence — see REQ-F-05).
- **REQ-F-05**: The theme choice SHALL NOT persist across page reloads or sessions — each fresh load resets to light mode (default). *(Out of scope: localStorage/cookie persistence, OS-preference auto-detection, per-device/account sync.)*

## Non-Functional Requirements

- **REQ-NF-01**: Toggling SHALL be visually instantaneous (no perceptible lag or flash of unstyled content).
- **REQ-NF-02**: Both themes SHALL maintain readable text/background contrast on all pages/components — no unreadable text, broken contrast, or unstyled elements in either mode.
- **REQ-NF-03**: The implementation SHALL reuse the existing frontend styling approach in `frontend-react/` (no new design/theming system introduced) — per the epic brief's binding constraint of "no constraint, any reasonable approach."

## Out of Scope
- Auto-detection of OS/system theme preference.
- Persistence of theme choice across reloads/sessions/devices.
- Per-component or per-page custom theming beyond the single global light/dark switch.

## Verification / Success Criteria
- Manual QA checklist (per epic brief): click the toggle, walk through key pages/components in both light and dark mode, confirm correct instant rendering and no visual regressions. Traces to REQ-F-01, REQ-F-03, REQ-NF-01, REQ-NF-02.

## Requirements Traceability
| REQ-ID | Description | Source |
|---|---|---|
| REQ-F-01 | Global light/dark toggle in header | Epic brief + clarification |
| REQ-F-02 | Sun/moon icon button style | Clarification |
| REQ-F-03 | Instant, global theme application | Epic brief |
| REQ-F-04 | Default to light mode | Clarification |
| REQ-F-05 | No persistence | Epic brief (out of scope) |
| REQ-NF-01 | Instantaneous toggle | Epic brief |
| REQ-NF-02 | No visual defects in either mode | Epic brief |
| REQ-NF-03 | Reuse existing styling approach | Epic brief (constraints) |
