# Component Inventory

Counts below were computed by direct filesystem inspection at analysis time (commands shown per section) — see `reverse-engineering-timestamp.md` for the full reproducibility note.

## Application Packages
- `backend` (Python/FastAPI) — the RAG API server: PDF ingestion, embedding, vector search, LLM answer generation. 13 `.py` files (`find backend -name "*.py" | wc -l`).
- `frontend-react` (React/Vite) — the student-facing chat UI. 6 JS/JSX source files under `src/` (`find frontend-react/src -name "*.js" -o -name "*.jsx" | wc -l`).

## Infrastructure Packages
- None found. No CDK, Terraform, CloudFormation, or Dockerfile/docker-compose files exist anywhere in the repo (`find . -iname "Dockerfile*" -o -iname "docker-compose*" -o -iname "*.tf" -not -path "*/node_modules/*"` → 0 results).

## Shared Packages
- None found — this is a two-package repo with no shared/common library package between `backend` and `frontend-react`. `backend/components/*` and `backend/utils/file_wrapper.py` are internal modules of the `backend` application package, not separately-versioned/published shared packages.

## Test Packages
- None found. No test files, test framework config, or test directories exist for either package (`find . -iname "*test*" -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/.git/*"` matches only unrelated AI-PDLC rule-detail docs about testing, not actual test code — see `code-quality-assessment.md`).

## Total Count
- **Total Packages**: 2 (`backend`, `frontend-react`)
- **Application**: 2
- **Infrastructure**: 0
- **Shared**: 0
- **Test**: 0
- **Total git-tracked files in repo**: 98 (`git ls-files | wc -l`, at commit `b9421a80a4abd15dd749302a6f698491a665abe8`)
- **Backend Python source files**: 13 (`find backend -name "*.py" | wc -l`)
- **Frontend JS/JSX source files**: 6 (`find frontend-react/src -name "*.js" -o -name "*.jsx" | wc -l`)
