# E2E Test Steps — AT-794 Global Light/Dark Theme Toggle

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/AT-793-light-dark-theme-toggle` |
| This story's merged PR | ⚠️ TO CONFIRM: fill in the `[STORY]` PR URL once AT-794's code merges into the epic branch |
| Confirm the story is in the build | `git log --oneline | grep AT-794` |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING / Makefile). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` (Vite dev server, `frontend-react/`, per `vite.config.js`) |
| Local services that must be up | None required for TC-E2E-01/02/03/04/05/06/08. The backend (`uvicorn`, default port 8000) is only needed to reach the Chat page for the full page/component sweep in TC-E2E-07 (requires a PDF upload) |
| Test data / accounts to seed | A small valid PDF (any 1–2 page PDF, ≤50 MB) to upload for TC-E2E-07 |

> If the build or local run fails, that is a **blocker on the dev team** — report it and do not log
> functional failures against a system that never started.

---

### TC-E2E-01 — Theme toggle is visible in the header on load

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-01, REQ-F-02 |
| **Type** | E2E |
| **Priority** | P1 (critical path) |
| **Preconditions** | Local instance running per System Under Test; fresh browser session (no prior localStorage for this origin) |
| **Test data** | None |

**Steps**
1. Open the app at the local base URL in a fresh/incognito browser window.
2. Look at the app header/navbar.

**Expected result**
- A single icon-button toggle (sun or moon icon) is visible in the header, present regardless of which section (Upload/Chat) is showing.

**Pass/Fail criteria**: PASS if exactly one theme toggle icon-button is visible in the header; FAIL if it is missing, duplicated, or rendered outside the header.
**Cleanup**: None (no state changed).

---

### TC-E2E-02 — App defaults to light mode on a fresh load

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-F-04 |
| **Type** | E2E |
| **Priority** | P1 (critical path) |
| **Preconditions** | Fresh/incognito browser window, no prior interaction with the app in this session |
| **Test data** | None |

**Steps**
1. Open the app at the local base URL in a fresh/incognito browser window.
2. Observe the background/text colors and the toggle icon's state.

**Expected result**
- The app renders in light mode (light background, dark text) with no manual interaction.
- The toggle icon shows the "switch to dark" affordance (e.g. moon icon, per whichever convention is implemented).

**Pass/Fail criteria**: PASS if the app is in light mode by default; FAIL if it loads in dark mode or an indeterminate/mixed state.
**Cleanup**: None.

---

### TC-E2E-03 — Clicking the toggle switches the entire UI to dark mode instantly

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-03, REQ-NF-01 |
| **Type** | E2E |
| **Priority** | P1 (critical path) |
| **Preconditions** | App loaded in light mode (default) |
| **Test data** | None |

**Steps**
1. Load the app (light mode, default).
2. Click the theme toggle in the header.
3. Immediately observe the entire visible UI (header, currently rendered section, buttons, text).
4. Check the browser tab/URL — confirm no page reload occurred (e.g. watch the Network tab for a fresh `document` request, or note that in-memory state such as an in-progress upload/typed text is preserved).

**Expected result**
- All currently rendered elements switch to the dark theme at once (same click, same frame) — no partial/split-theme state.
- No full-page reload occurs.
- No visible flash of unstyled/wrong-themed content during the switch.

**Pass/Fail criteria**: PASS if the switch is instant, complete, and reload-free with no visible flash; FAIL if any element lags, stays in the old theme, or a reload/flash is observed.
**Cleanup**: Click the toggle again to return to light mode, or reload the page (resets to light per AC-4).

---

### TC-E2E-04 — Toggling twice returns the UI to the original theme (round-trip)

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-03 |
| **Type** | E2E |
| **Priority** | P2 |
| **Preconditions** | App loaded in light mode (default) |
| **Test data** | None |

**Steps**
1. Load the app (light mode).
2. Click the toggle once (→ dark mode).
3. Click the toggle again (→ should return to light mode).

**Expected result**
- After the second click, the UI is visually identical to the initial light-mode load, and the toggle icon shows the original "switch to dark" affordance.

**Pass/Fail criteria**: PASS if the second click fully restores the original light theme; FAIL if any element is left in dark styling or the icon state is wrong.
**Cleanup**: None (state already restored to light).

---

### TC-E2E-05 — Reloading the page after toggling resets the theme to light (no persistence)

| Field | Value |
|-------|-------|
| **Traces to** | AC-4 / REQ-F-05 |
| **Type** | E2E |
| **Priority** | P1 (critical path) |
| **Preconditions** | App loaded, toggled to dark mode |
| **Test data** | None |

**Steps**
1. Load the app (light mode, default).
2. Click the toggle to switch to dark mode; confirm dark mode is active.
3. Reload the page (`F5` / browser refresh).
4. Observe the theme after reload.

**Expected result**
- After reload, the app renders in light mode again, regardless of the theme that was active before the reload.

**Pass/Fail criteria**: PASS if the reloaded app is in light mode; FAIL if it remembers/restores dark mode.
**Cleanup**: None (already back to default).

---

### TC-E2E-06 — A new browser session does not inherit a previously toggled theme (no cross-session persistence)

| Field | Value |
|-------|-------|
| **Traces to** | AC-4 / REQ-F-05 |
| **Type** | E2E |
| **Priority** | P2 (negative/edge case) |
| **Preconditions** | An existing browser window has the app open and toggled to dark mode |
| **Test data** | None |

**Steps**
1. In browser window A, load the app and toggle to dark mode.
2. Open a **new** incognito/private window (window B) and navigate to the same local base URL.
3. Observe the theme in window B.
4. Optionally inspect Application/Storage tab in devtools for `localStorage`/cookies related to theme — confirm none exist.

**Expected result**
- Window B loads in light mode, independent of window A's toggled state.
- No theme-related key is found in `localStorage` or cookies.

**Pass/Fail criteria**: PASS if window B is light mode and no theme value is persisted anywhere observable; FAIL if window B inherits dark mode or a theme value is found in storage.
**Cleanup**: Close window B.

---

### TC-E2E-07 — Both themes render correctly across all key pages/components (Upload and Chat sections)

| Field | Value |
|-------|-------|
| **Traces to** | AC-5 / REQ-NF-02 |
| **Type** | E2E |
| **Priority** | P1 (critical path) |
| **Preconditions** | Local instance running with backend up (per System Under Test) |
| **Test data** | One small valid PDF (≤50 MB, e.g. a 2-page sample document) |

**Steps**
1. Load the app (light mode) — the Upload section is shown. Visually scan for unstyled elements or unreadable text.
2. Toggle to dark mode. Visually scan the Upload section again.
3. Toggle back to light mode. Upload the test PDF and wait for it to finish processing, arriving at the Chat section.
4. Type a question and submit it (Ctrl+Enter) to render at least one chat bubble with an expanded citations list (click a citation to expand it).
5. Toggle to dark mode while the Chat section (with the message and expanded citation) is visible. Visually scan the whole Chat section, including the message bubble and citation panel.
6. Toggle back to light mode and repeat the visual scan on the Chat section.

**Expected result**
- In both themes, all text is readable against its background (no low-contrast or invisible text) on both the Upload section and the Chat section (including message bubbles and the citations panel).
- No element appears unstyled (e.g. default browser styling, no background/foreground colors applied).

**Pass/Fail criteria**: PASS if no visual defect (unreadable text, broken contrast, unstyled element) is found on either section in either theme; FAIL if any single element is illegible or unstyled.
**Cleanup**: Reload the page (resets session state and theme to defaults).

---

### TC-E2E-08 — Theme toggle reuses the existing styling approach (no new/parallel theming system)

| Field | Value |
|-------|-------|
| **Traces to** | AC-6 / REQ-NF-03 |
| **Type** | E2E |
| **Priority** | P2 |
| **Preconditions** | Local instance running; browser devtools available |
| **Test data** | None |

**Steps**
1. Load the app and open browser devtools → Network tab. Reload and toggle the theme a few times.
2. Confirm no new external CSS framework/library request appears in the Network tab (e.g. no new CDN stylesheet, no new npm-served CSS bundle beyond the app's existing single bundle) as a result of theme toggling.
3. Open devtools → Elements tab. Inspect a few themed elements (header, a button, the chat bubble) in both light and dark mode.
4. Compare the class-naming/styling mechanism observed (e.g. plain CSS classes vs. a newly introduced CSS-in-JS/utility framework) against what is used elsewhere in the app's rendered markup — it should look like the **same** mechanism, not a second, parallel one applied only to themed elements.

**Expected result**
- No new external styling framework/library is loaded purely to support the toggle.
- Themed elements use the same styling mechanism (e.g. CSS classes toggled via a root/body class or CSS variables) observed throughout the rest of the rendered app, not a visibly distinct/parallel system.

**Pass/Fail criteria**: PASS if inspection shows one consistent styling mechanism across the app, in both themes, with no new external stylesheet loaded; FAIL if a second/parallel styling system or a newly loaded external framework is observed.
**Cleanup**: Close devtools.
