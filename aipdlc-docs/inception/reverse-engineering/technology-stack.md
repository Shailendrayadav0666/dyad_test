# Technology Stack

All versions below were read directly from manifest/lock files and the local `venv` — never guessed. Two columns are given for backend libraries where relevant: the constraint declared in `requirements.txt`, and the version actually resolved in the local `venv/Lib/site-packages` (`ls venv/Lib/site-packages | grep -iE "^(anthropic|qdrant|fastapi|uvicorn|pdfplumber|sentence.transformers|torch|numpy)"`).

## Programming Languages
- **Python** — 3.11.0 (local interpreter, `python --version`); README/requirements.txt note that 3.13 has limited support for `pdfplumber` and related dependencies and recommend 3.11. Used for the entire `backend/` package.
- **JavaScript (JSX, ES modules)** — no `.babelrc`/TypeScript config found; plain modern JS via Vite/`@vitejs/plugin-react` (`"type": "module"` in `frontend-react/package.json`). Used for the entire `frontend-react/` package.

## Frameworks
- **FastAPI** — declared `>=0.115.0`, resolved `0.139.0`. Backend web framework (`backend/main.py`, `backend/api/routes.py`).
- **React** — `^18.3.1` declared and resolved (`frontend-react/package-lock.json`). Frontend UI library.
- **Uvicorn** — declared `[standard]>=0.30.0`, resolved `0.51.0`. ASGI server running the FastAPI app.

## Infrastructure
- **Qdrant (embedded, in-memory)** — `qdrant-client` declared `>=1.18.0`, resolved `1.18.0`. Runs as `QdrantClient(":memory:")` inside the backend process — not a deployed/networked service. No persistent storage.
- **Anthropic Claude API** — `anthropic` declared `>=0.34.0`, resolved `0.116.0`. External LLM API called for answer generation (model id `claude-sonnet-4-6`, hardcoded in `AnswerGenerator.MODEL`).
- No cloud infrastructure (AWS/GCP/Azure), containers, or IaC were found in the repo.

## Build Tools
- **Vite** — `^5.4.0` declared, `5.4.x` family resolved per lockfile; frontend dev server + bundler.
- **@vitejs/plugin-react** — `^4.3.1`; enables JSX/Fast Refresh in Vite.
- **pip** — backend dependency installation via `requirements.txt` (no lockfile/hashes; version ranges only, not pinned exact versions).

## Testing Tools
- **None configured.** No test framework (pytest, unittest config, Jest, Vitest, React Testing Library) appears in `requirements.txt`, `frontend-react/package.json`, or as config files anywhere in the repo. No CI workflow files exist (`find . -path "*/.github/*"` → 0 results). See `code-quality-assessment.md`.

## Other Notable Backend Dependencies (from `requirements.txt`, with resolved venv versions)
- `python-multipart` `>=0.0.12` — required by FastAPI for `multipart/form-data` file uploads.
- `python-dotenv` `>=1.0.1` — loads `.env` in `backend/main.py:9`.
- `pdfplumber` `>=0.10.3`, resolved `0.11.10` — primary PDF text extraction.
- `sentence-transformers` `>=3.0.1`, resolved `5.6.0` — local embedding model runtime.
- `numpy` `>=1.26.0`, resolved `2.4.6`.
- `torch` `>=2.3.0`, resolved `2.13.0` — backing tensor runtime for `sentence-transformers`.

**Caveat**: `backend/components/pdf_processor.py` also imports `PyPDF2` as an optional fallback (`try: from PyPDF2 import PdfReader except ImportError: PdfReader = None`), but `PyPDF2` is **not listed** in `requirements.txt`. As shipped, only `pdfplumber` is guaranteed to be installed, so the fallback path is effectively dead code unless a developer manually installs `PyPDF2`.
