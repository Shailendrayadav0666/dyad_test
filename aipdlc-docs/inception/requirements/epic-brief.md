# Epic Brief — AT-793: Light / Dark Theme Toggle

**Source**: Jira Epic [AT-793](https://3pillarglobal-demo.atlassian.net/browse/AT-793)
**Labels**: intent-intake, intake-refined

## Outcome
Add a light mode / dark mode toggle to the UI so users can switch the app's theme, delivered as a fast, simple feature.

## KPI / Business Outcome
None specific — UX polish/nice-to-have.

## Success Criteria (measurable)
- Toggle switches the theme instantly on click, across all pages/components.
- No visual defects in either mode (unreadable text, broken contrast, unstyled elements).
- **Verification method**: Manual QA checklist — click toggle, walk through key pages/components in both light and dark mode, confirm correct rendering and no regressions.

## Scope
- **In scope**: A single toggle control that switches the whole UI between light and dark themes.
- **Out of scope**:
  - No auto-detection of OS/system theme preference (manual toggle only).
  - No persistence of theme choice across page reloads/sessions (resets to default each load).
  - No per-component/per-page custom theming — global switch only.
  - No account-level sync of theme preference across devices.

## Binding Constraints
- Stack/platform: no constraint — any reasonable approach fitting the existing codebase is acceptable.
- Integration: none.
- Data handling: none (no persisted user data).
- Performance floor: none beyond "fast" (instant toggle, no perceptible lag).
- Regulatory: none.

## Domain & System Context
- Single concept in play: theme state (light/dark), applied globally to the UI.
- Invariant: exactly one theme is active at any time; toggling always flips it deterministically.

## Users & Personas
- All end users of the UI — no role distinction; everyone sees and can use the same toggle.

## Risks
None significant identified — feature is small and isolated.

## NFR Floor
None beyond the success criteria above (no persistence, no auth, no regulatory scope).

## Open Questions
None — high confidence, no open unknowns.

## Context Link
Plain English — no external doc.
