# Repository Guidelines

## Project Structure & Module Organization
- `backend/` hosts the FastAPI stack; start services via `main.py` and trigger agents with `run_agent.py`.
- Multi-channel connectors live in `backend/servers/`, Mongo helpers in `backend/mongodb/`, and prompts in `backend/prompts.yml`.
- `frontend/` contains the React app: views under `src/components/`, shared hooks in `src/hooks/`, utilities in `src/utils/`, and Tailwind assets in `src/styles/`.
- Config and marketing copy sit at the repo root (`config.yml`, `Prompts Show Off.txt`).

## Build, Test, and Development Commands
- `uv sync` installs backend dependencies; `uv run uvicorn main:app --reload` launches the API for local development.
- `uv run python run_agent.py --agent <name>` executes a one-off agent for smoke checks.
- `npm install` (or `pnpm install`) prepares the frontend; `npm run dev` serves the React app locally, `npm run build` creates the production bundle, and `npm run preview` validates it.

## Coding Style & Naming Conventions
- Target Python 3.10+, four-space indentation, and type-hinted function signatures; group routers by provider under `backend/servers/<provider>/`.
- Environment variables use `UPPER_SNAKE_CASE` and flow through `pydantic-settings`.
- Frontend uses TypeScript strict mode, React function components in PascalCase, hooks prefixed with `use`, and utilities in lower-kebab filenames.
- Run `npm run lint` plus any formatter hooks before opening a PR.

## Testing Guidelines
- Backend relies on pytest; name files `test_*.py` alongside code or in `backend/tests/`.
- Run `uv run pytest backend/test_rephrase_endpoint.py` for targeted coverage or `uv run pytest` for the full suite.
- Use `httpx.AsyncClient` fixtures to isolate FastAPI routes and mock MCP adapters to keep tests deterministic.

## Commit & Pull Request Guidelines
- Write concise, imperative commit subjects (e.g., "Add Twitter MCP adapter") and expand context in the body when needed.
- Pull requests should describe schema or API changes, link relevant issues, summarize test coverage, and include UI screenshots when frontend surfaces change.
- Flag config or prompt updates explicitly so reviewers can validate agent behavior.

## Security & Configuration Tips
- Never commit `.env` files; document required keys instead and load them via `pydantic-settings`.
- Update `config.yml` or `backend/prompts.yml` only through reviewed PRs, and dry-run new connectors with placeholder keys before merging.
