# Repository Guidelines

## Project Structure & Module Organization
The `backend/` directory hosts the FastAPI stack and agent runners, with primary entrypoints in `main.py` and `run_agent.py`. Multi-channel connectors live under `backend/servers/`, and MongoDB helpers are grouped in `backend/mongodb/`. Service-specific prompts are stored in `backend/prompts.yml`, while high-level marketing copy examples sit in `Prompts Show Off.txt`. The frontend lives under `frontend/`, with React views in `src/components/`, hooks and utilities in `src/hooks/` and `src/utils/`, and Tailwind styling assets in `src/styles/`. Top-level configs such as `config.yml` coordinate agent behavior.

## Build, Test, and Development Commands
Install backend dependencies with `uv sync` and start the API via `uv run uvicorn main:app --reload` from `backend/`. Run a one-off agent using `uv run python run_agent.py --agent name`. Frontend development uses `npm install` (or `pnpm install`) followed by `npm run dev`. Build the production bundle with `npm run build`, and preview using `npm run preview`.

## Coding Style & Naming Conventions
Target Python 3.10+, four-space indentation, and type-hinted function signatures. Group FastAPI routers by domain under `backend/servers/<provider>/`. Environment variables belong in `UPPER_SNAKE_CASE`. For the frontend, rely on TypeScript strict mode, React function components in PascalCase, hooks prefixed with `use`, and utility modules in lower-kebab filenames. Run `npm run lint` to enforce ESLint and Tailwind conventions before pushing.

## LLM Provider Configuration
`MCP_LLM_PROVIDER` selects the chat backend: `blackbox` (default), `openai`, or `openrouter`. Each provider expects its own key: `BLACKBOX_API_KEY`, `OPENAI_API_KEY`, or `OPENROUTER_API_KEY`. Optional overrides include `*_BASE_URL` and `*_DEFAULT_MODEL`. OpenRouter supports extra headers via `OPENROUTER_HTTP_REFERER` and `OPENROUTER_X_TITLE`; pass custom headers or temporary keys to `MCPAgentExecutor(api_key=...)` when scripting.

## Testing Guidelines
Backend tests use pytest; place files as `test_*.py` beside the code or in `backend/tests/` if the suite expands. Execute `uv run pytest backend/test_rephrase_endpoint.py` for targeted checks or `uv run pytest` for the full suite. Add async HTTP client fixtures via `httpx.AsyncClient` when covering FastAPI routes. Snapshot external API calls and mock MCP adapters to keep tests deterministic.

## Commit & Pull Request Guidelines
Git history is sparse but favors short, imperative summaries (e.g., “Add Twitter MCP adapter”). Reference relevant issues in the body, outline schema or API changes, and attach screenshots for UI updates. Each PR should describe test coverage, note configuration changes, and request review from maintainers responsible for affected modules.

## Security & Configuration Tips
Never commit `.env` files; document required keys in README tables instead. Update `config.yml` and `prompts.yml` through reviewed PRs so agents remain predictable. When adding new connectors, ensure keys are read via `pydantic-settings` and validate secrets with dry-run requests before merging.
