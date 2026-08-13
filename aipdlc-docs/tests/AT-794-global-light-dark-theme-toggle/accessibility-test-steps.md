# Accessibility Test Steps — AT-794 Global Light/Dark Theme Toggle

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/AT-793-light-dark-theme-toggle` |
| This story's merged PR | ⚠️ TO CONFIRM: fill in the `[STORY]` PR URL once AT-794's code merges into the epic branch |
| Confirm the story is in the build | `git log --oneline | grep AT-794` |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING / Makefile). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` (Vite dev server, `frontend-react/`, per `vite.config.js`) |
| Local services that must be up | None — all cases below are checkable on the Upload section alone |
| Test data / accounts to seed | None |

> If the build or local run fails, that is a **blocker on the dev team** — report it and do not log
> functional failures against a system that never started.

---

### TC-A11Y-01 — Theme toggle is reachable and operable by keyboard alone

| Field | Value |
|-------|-------|
| **Traces to** | AC-1, AC-2 / REQ-F-01, REQ-F-03 |
| **Type** | Accessibility (WCAG 2.4.7 Focus Visible, 2.1.1 Keyboard) |
| **Priority** | P1 (critical path) |
| **Preconditions** | Local instance running, app loaded in light mode |
| **Test data** | None |

**Steps**
1. Load the app. Click once anywhere neutral (e.g. the page background) to ensure focus starts outside any control.
2. Press `Tab` repeatedly until the theme toggle receives visible focus.
3. Press `Enter` (and, separately on a repeat pass, `Space`) while the toggle is focused.

**Expected result**
- The toggle is reachable via `Tab` in a logical order (e.g. as part of the header).
- Pressing `Enter` or `Space` while focused activates the toggle exactly as a mouse click would (theme switches).

**Pass/Fail criteria**: PASS if the toggle is keyboard-reachable and both `Enter` and `Space` activate it; FAIL if it is skipped by `Tab` or does not respond to keyboard activation.
**Cleanup**: Toggle back to light mode if left in dark mode.

---

### TC-A11Y-02 — Theme toggle has an accessible name/label

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-01, REQ-F-02 |
| **Type** | Accessibility (WCAG 4.1.2 Name, Role, Value) |
| **Priority** | P1 (critical path) |
| **Preconditions** | Local instance running |
| **Test data** | None |

**Steps**
1. Load the app.
2. Open browser devtools → Accessibility tree (or use a screen reader, e.g. NVDA/VoiceOver) and inspect the toggle element.
3. Read the computed accessible name/role reported for the toggle.

**Expected result**
- The toggle exposes a non-empty, descriptive accessible name (e.g. "Switch to dark mode" / "Toggle theme") and a `button` role — not just a bare icon with no label.
- The accessible name updates (or remains descriptive) after the theme is switched, reflecting the action the next click will perform.

**Pass/Fail criteria**: PASS if a screen reader/accessibility tree reports a descriptive name and button role; FAIL if the name is empty, generic ("button"), or absent.
**Cleanup**: None.

---

### TC-A11Y-03 — Light mode meets WCAG AA text contrast across key pages/components

| Field | Value |
|-------|-------|
| **Traces to** | AC-5 / REQ-NF-02 |
| **Type** | Accessibility (WCAG 1.4.3 Contrast Minimum — AA, 4.5:1 for normal text) |
| **Priority** | P1 (critical path) |
| **Preconditions** | App loaded in light mode (default) |
| **Test data** | A contrast-checking devtool (e.g. Chrome devtools' built-in contrast ratio readout, or an axe/Lighthouse accessibility scan) |

**Steps**
1. Load the app in light mode (Upload section shown).
2. Run an automated accessibility scan (e.g. Lighthouse "Accessibility" audit, or axe DevTools) against the page, or manually sample text/background pairs with the devtools contrast checker (header text, body text, toggle icon, buttons).
3. Record any contrast violation flagged.

**Expected result**
- No text/background pair falls below the WCAG AA contrast ratio (4.5:1 normal text / 3:1 large text) anywhere on the scanned page.

**Pass/Fail criteria**: PASS if the scan reports zero contrast violations; FAIL if any element fails the AA threshold.
**Cleanup**: None.

---

### TC-A11Y-04 — Dark mode meets WCAG AA text contrast across key pages/components

| Field | Value |
|-------|-------|
| **Traces to** | AC-5 / REQ-NF-02 |
| **Type** | Accessibility (WCAG 1.4.3 Contrast Minimum — AA) |
| **Priority** | P1 (critical path) |
| **Preconditions** | App loaded, toggled to dark mode |
| **Test data** | Same contrast-checking devtool as TC-A11Y-03 |

**Steps**
1. Load the app and click the theme toggle to switch to dark mode.
2. Repeat the same automated scan / manual contrast sampling as TC-A11Y-03 against the dark-mode rendering.
3. Record any contrast violation flagged.

**Expected result**
- No text/background pair falls below the WCAG AA contrast ratio anywhere on the scanned page in dark mode.

**Pass/Fail criteria**: PASS if zero contrast violations are reported in dark mode; FAIL if any element fails the AA threshold.
**Cleanup**: Toggle back to light mode or reload.

---

### TC-A11Y-05 — Focus indicator remains visible on the toggle in both themes

| Field | Value |
|-------|-------|
| **Traces to** | AC-5 / REQ-NF-02 |
| **Type** | Accessibility (WCAG 2.4.7 Focus Visible) |
| **Priority** | P2 |
| **Preconditions** | App loaded |
| **Test data** | None |

**Steps**
1. Load the app in light mode. Press `Tab` until the toggle receives focus. Observe the focus outline/ring.
2. Click the toggle to switch to dark mode. Press `Tab` away and back to the toggle. Observe the focus outline/ring again.

**Expected result**
- A clearly visible focus indicator (outline/ring with sufficient contrast against its background) is present on the toggle in **both** light and dark mode — not just one.

**Pass/Fail criteria**: PASS if the focus indicator is visible with adequate contrast in both themes; FAIL if it disappears, blends into the background, or is only visible in one theme.
**Cleanup**: None.

---

### TC-A11Y-06 — No broken/unstyled elements in either theme at 200% browser zoom (edge case)

| Field | Value |
|-------|-------|
| **Traces to** | AC-5 / REQ-NF-02 |
| **Type** | Accessibility (WCAG 1.4.4 Resize Text) |
| **Priority** | P3 (edge case) |
| **Preconditions** | App loaded |
| **Test data** | None |

**Steps**
1. Load the app in light mode. Zoom the browser to 200% (`Ctrl` + `+` repeatedly, or browser zoom setting).
2. Visually scan the header, toggle, and visible section for overlapping, clipped, or unstyled elements.
3. Toggle to dark mode while still zoomed to 200%. Repeat the visual scan.

**Expected result**
- At 200% zoom, all text remains readable, no element is clipped/overlapping, and no element loses its theme styling, in **both** light and dark mode.

**Pass/Fail criteria**: PASS if no layout/visual defect appears at 200% zoom in either theme; FAIL if any element is broken, clipped, or unstyled at that zoom level.
**Cleanup**: Reset browser zoom to 100%.
