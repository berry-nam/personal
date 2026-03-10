# CLAUDE.md — kr-acc (Korean Politician Open Graph)

## Project Overview

kr-acc is a civic tech transparency platform that aggregates Korean National Assembly data into a unified graph database. It ingests legislator profiles, bill proposals, plenary voting records, and committee data from 열린국회정보 (Open Assembly) APIs, stores them in PostgreSQL + Apache AGE (graph extension), serves them via FastAPI, and visualizes them with React + D3.js.

**This is an open-source civic tech project (MIT license), not a commercial product.**

## Tech Stack

|Layer    |Technology                      |Version      |
|---------|--------------------------------|-------------|
|Database |PostgreSQL 16 + Apache AGE 1.5  |Latest stable|
|Backend  |FastAPI (Python 3.12+, async)   |0.115+       |
|ORM      |SQLAlchemy 2.x (async) + asyncpg|Latest       |
|ETL      |Prefect 3.x                     |Latest       |
|Frontend |React 19 + Vite + TypeScript    |Latest       |
|Graph Viz|D3.js v7 (force-directed)       |Latest       |
|Charts   |Recharts                        |Latest       |
|UI       |Tailwind CSS 4 + shadcn/ui      |Latest       |
|State    |TanStack Query v5               |Latest       |
|Routing  |React Router v7                 |Latest       |
|Deploy   |Docker Compose                  |Latest       |
|CI/CD    |GitHub Actions                  |N/A          |

## Coding Conventions

### Python (Backend + ETL)

- Python 3.12+, type hints everywhere
- async/await for all I/O (httpx, asyncpg, SQLAlchemy async)
- Pydantic v2 for all schemas (request/response validation)
- `uv` for dependency management
- Ruff for linting + formatting (line-length=100)
- pytest + pytest-asyncio for testing
- Docstrings: Google style

### TypeScript (Frontend)

- Strict mode, no `any`
- Functional components only, hooks for state
- TanStack Query for all server state (no Redux)
- Path aliases: `@/` → `src/`
- ESLint + Prettier
- Component naming: PascalCase files
- API types auto-generated or manually synced with backend schemas

### Git

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- Branch strategy: `main` → `dev` → feature branches
- PR required for main

## Key Design Decisions

1. **Apache AGE over Neo4j**: Zero additional cost — AGE runs as a PostgreSQL extension.
2. **Prefect over Airflow**: Lighter weight for a solo/small team project.
3. **Dual storage pattern**: Relational tables are source of truth. AGE graph layer is derived/synced.
4. **No auth in v1**: All data is legally public. Read-only API.
5. **Korean party colors**: Use official party colors for all visualizations.

## Environment Variables

```env
# Required
ASSEMBLY_API_KEY=your_api_key_from_open_assembly_go_kr
DATABASE_URL=postgresql+asyncpg://kracc:kracc@db:5432/kracc
DATABASE_URL_SYNC=postgresql://kracc:kracc@db:5432/kracc

# Optional
AGE_GRAPH_NAME=kr_acc
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:5173"]
LOG_LEVEL=INFO
ETL_SCHEDULE_CRON="0 3 * * *"
```
