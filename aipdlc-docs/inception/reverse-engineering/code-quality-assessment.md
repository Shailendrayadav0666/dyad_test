# Code Quality Assessment

## Test Coverage

- **Overall**: **None.** No test suite exists for either package — verified by `find . -iname "*test*" -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/.git/*"`, which returns only unrelated AI-PDLC framework documentation about testing (e.g. `.aipdlc-rule-details/construction/build-and-test.md`), not actual test code. No `pytest`, `unittest`, `Jest`, or `Vitest` dependency is declared in `requirements.txt` or `frontend-react/package.json`.
- **Unit Tests**: Not present. "Test coverage %" is intentionally **not reported as a number** here — there is no coverage tool configured and running one was not possible without first authoring a test suite, which is out of scope for this analysis. Reporting a percentage would be fabricated.
- **Integration Tests**: Not present.
- **Test suite execution**: Not run — there is nothing to run.

## Code Quality Indicators

- **Linting**: **Not configured.** No `.eslintrc*`, `.flake8`, `ruff.toml`, or `pyproject.toml` linting section found anywhere in the repo (`find . -maxdepth 3 -iname ".eslintrc*" -o -iname "pyproject.toml" -o -iname ".flake8" -o -iname "ruff.toml"` → 0 results, excluding `node_modules`). No `eslint`/`ruff`/`flake8`/`black` dependency is declared either.
- **Code Style**: Reasonably **consistent** within each package by hand: backend modules uniformly use docstrings, type hints on public methods, and a custom-exception-per-component pattern (see `code-structure.md` Design Patterns); frontend components uniformly use function components + hooks, no class components. No automated formatter enforces this, so consistency currently depends on manual discipline.
- **Documentation**: **Good at the docstring/comment level** — every backend class and public method has a docstring describing args/returns/raises; several files carry root-cause comments explaining non-obvious choices (e.g. the `qdrant-client` `query_points` vs `search()` version shim in `vector_store.py:174-176`). Project-level docs (`README.md`, `PROJECT_SUMMARY.md`) exist but were **not** used as evidence for any claim in this analysis per the accuracy rules — they may describe an earlier/aspirational state of the code.

## Technical Debt

- **No automated tests of any kind** (`backend/`, `frontend-react/`) — the highest-priority gap for a project moving past proof-of-concept.
- **No CI/CD pipeline** — no `.github/workflows` or any other CI config exists.
- **Dev-server port mismatch**: `frontend-react/vite.config.js:9-10` proxies `/api` to `http://localhost:5000`, while `backend/main.py:35` defaults to port `8000` when the `PORT` env var is unset. The repo's own `.env.example` sets `PORT=5000`, which resolves the mismatch in practice *only if* a developer copies `.env.example` to `.env` — a fresh clone without that step will have the frontend proxy pointing at the wrong port.
- **Stale `.env.example` content**: `.env.example` documents `FLASK_ENV` / `FLASK_DEBUG`, which are Flask conventions — the current backend is FastAPI/uvicorn and does not read those variables anywhere in `backend/` (verified: no `os.environ` or `os.getenv` reference to `FLASK_ENV`/`FLASK_DEBUG` in the codebase). This is leftover from an earlier framework choice and is misleading to new contributors.
- **Undeclared runtime dependency**: `backend/components/pdf_processor.py` imports `PyPDF2` as an optional fallback, but it is not listed in `requirements.txt` (see `technology-stack.md`/`dependencies.md`) — the fallback path is currently unreachable on a clean install.
- **Fully in-memory, non-persistent state**: `SessionManager` (plain `dict`) and `VectorStore` (`QdrantClient(":memory:")`) mean all sessions/embeddings are lost on every backend restart, and the app cannot run behind more than one worker/process without sessions becoming invisible to whichever worker didn't create them (`uvicorn.run(..., reload=True)` in `backend/main.py:36` runs a single worker with auto-reload, which is dev-appropriate but not production-ready).
- **No concurrency guards on shared in-memory state**: `SessionManager.sessions` and `VectorStore.collections` are plain dicts mutated without locks; concurrent requests against the same session (e.g. rapid double-submit of `/api/answer`) could race, though FastAPI's async single-event-loop model makes this a lower risk than in a multi-threaded server.
- **Two documentation-doc duplicates at the repo root** (`README.md` and `README copy.md`, plus `PROJECT_SUMMARY.md` and `AIPDLC-workflow.md`) — a maintenance/drift risk since it's unclear which is authoritative; not verified against code as part of this analysis.

## Patterns and Anti-patterns

- **Good Patterns**:
  - Consistent custom-exception-per-component design lets the API layer map failures to precise HTTP error codes (`backend/api/routes.py`'s per-`except` blocks).
  - Graceful optional-dependency handling (`try/except ImportError` for `pdfplumber`/`PyPDF2`, `qdrant-client` API-version shim) avoids hard import-time crashes.
  - Clear separation of concerns across components (PDF parsing, embedding, vector storage, retrieval, generation, session state each in their own module).
  - Frontend correctly guards `ANTHROPIC_API_KEY`-less operation by disabling `/api/answer` cleanly (`500 api_key_missing`) rather than crashing the whole backend at startup.
- **Anti-patterns**:
  - **Broad `except Exception` catch-alls** at both the outer route level (`backend/api/routes.py:112-113, 175-176, 238-239`) and around `session_manager.get_session` calls (e.g. `backend/api/routes.py:143-145`) — these swallow the original exception type/traceback and can mask real bugs behind a generic `session_not_found` or `server_error`.
  - **Permissive CORS combined with credentials**: `backend/main.py:15-24` sets `allow_methods=["*"]`, `allow_headers=["*"]`, and `allow_credentials=True` together — while `allow_origins` is restricted to two localhost origins (mitigating real-world risk today), this combination is a known CORS anti-pattern that would need tightening before any non-local deployment.
  - **No server-side input validation on `/api/answer`'s query length** (unlike `/api/query`, which caps at 500 characters) — an inconsistency between the two similar endpoints.
  - **Hardcoded model id** (`AnswerGenerator.MODEL = "claude-sonnet-4-6"`) with no environment-variable override, making model upgrades require a code change.
