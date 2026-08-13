EPIC JIRA TICKET: https://3pillarglobal-demo.atlassian.net/browse/AT-793

# User Stories — Light / Dark Theme Toggle

## Story 1.1: Global Light/Dark Theme Toggle

**Jira**: [AT-794](https://3pillarglobal-demo.atlassian.net/browse/AT-794)

**As an** end user of the UI
**I want** a toggle in the header that switches the whole app between light and dark themes
**So that** I can view the app comfortably in different lighting conditions and enjoy a more polished UI.

**Persona**: End User

**Covers**: REQ-F-01, REQ-F-02, REQ-F-03, REQ-F-04, REQ-F-05, REQ-NF-01, REQ-NF-02, REQ-NF-03

### Acceptance Criteria
- **AC-1** (→ REQ-F-01, REQ-F-02): Given the app is loaded, when I look at the header/navbar, then I see a single icon-button toggle (sun/moon) that controls the app's theme.
- **AC-2** (→ REQ-F-03, REQ-NF-01): Given the app is in either theme, when I click the toggle, then the entire UI (all currently rendered pages/components) switches to the other theme instantly, with no page reload and no perceptible lag or flash of unstyled content.
- **AC-3** (→ REQ-F-04): Given I load the app fresh (no prior interaction in this load), when the page renders, then it displays in light mode by default.
- **AC-4** (→ REQ-F-05): Given I have toggled the theme, when I reload the page or start a new session, then the theme resets to the default (light mode) — no persistence across reloads/sessions/devices.
- **AC-5** (→ REQ-NF-02): Given either theme is active, when I navigate through the key pages/components of the app, then all text remains readable and no element is left unstyled or with broken contrast.
- **AC-6** (→ REQ-NF-03): Given the existing frontend styling approach in `frontend-react/`, when the toggle is implemented, then it reuses that existing approach rather than introducing a new/parallel theming system.

**Requires**: none

---

## Requirements Coverage Matrix

| REQ-ID | Description | Covering Stories | Status |
|---|---|---|---|
| REQ-F-01 | Global toggle in header | 1.1 | ✅ Fully Covered |
| REQ-F-02 | Sun/moon icon button style | 1.1 | ✅ Fully Covered |
| REQ-F-03 | Instant, global theme application | 1.1 | ✅ Fully Covered |
| REQ-F-04 | Default to light mode | 1.1 | ✅ Fully Covered |
| REQ-F-05 | No persistence | 1.1 | ✅ Fully Covered |
| REQ-NF-01 | Instantaneous toggle | 1.1 | ✅ Fully Covered |
| REQ-NF-02 | No visual defects in either mode | 1.1 | ✅ Fully Covered |
| REQ-NF-03 | Reuse existing styling approach | 1.1 | ✅ Fully Covered |

**Coverage**: 8/8 REQ-IDs fully covered by story ACs.
