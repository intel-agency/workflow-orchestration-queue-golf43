# AGENTS.md

## Project Overview

**workflow-orchestration-queue** (OS-APOW) is an autonomous agentic orchestration system that transforms GitHub Issues into "Execution Orders" fulfilled by AI agents. It replaces manual human-in-the-loop coding processes with persistent, event-driven infrastructure.

The system is built on four pillars:
- **Notifier (The Ear)** — FastAPI webhook receiver with HMAC signature verification
- **Queue (The State)** — GitHub Issues and Labels as a state machine ("Markdown as a Database")
- **Sentinel (The Brain)** — Async polling engine that discovers queued tasks and manages worker lifecycle
- **Worker (The Hands)** — opencode-server CLI executing markdown-based workflow instructions

**Tech Stack**: Python 3.12, FastAPI, Pydantic, httpx, uvicorn, uv, Docker

## Setup Commands

- Install dependencies: `uv venv && uv pip install -e ".[dev]"`
- Run tests: `python -m pytest tests/ -v`
- Run tests with coverage: `python -m pytest tests/ --cov=src --cov-report=term-missing`
- Run linter: `python -m ruff check src/ tests/`
- Auto-fix lint issues: `python -m ruff check --fix src/ tests/`
- Type check: `python -m mypy src/`
- Start notifier service: `uvicorn workflow_orchestration_queue.main:app --reload --port 8000`
- Start sentinel poller: `python -m workflow_orchestration_queue.sentinel.poller`
- Docker build: `docker build -t workflow-orchestration-queue .`
- Docker compose up: `docker compose up --build`
- Verify imports: `python -c "from workflow_orchestration_queue.main import app; print('FastAPI app OK')"`

> **Note:** Use the project's virtual environment (`.venv/bin/python`) if `python` is not on PATH.

## Project Structure

```
workflow-orchestration-queue/
├── src/
│   └── workflow_orchestration_queue/
│       ├── __init__.py              # Package root, version
│       ├── main.py                  # FastAPI app entry point (/health, webhook router)
│       ├── config.py                # Settings via pydantic-settings
│       ├── models/
│       │   ├── __init__.py          # Re-exports TaskType, WorkItem, WorkItemStatus, scrub_secrets
│       │   └── work_item.py         # WorkItem model, TaskType/WorkItemStatus enums, scrub_secrets()
│       ├── interfaces/
│       │   ├── __init__.py
│       │   └── task_queue.py        # ITaskQueue ABC (add_to_queue, fetch_queued_tasks, update_status)
│       ├── queue/
│       │   ├── __init__.py
│       │   └── github_queue.py      # GitHubQueue(ITaskQueue) — GitHub Issues as work queue
│       ├── sentinel/
│       │   ├── __init__.py
│       │   ├── poller.py            # Sentinel class — polling loop, task claiming, worker management
│       │   ├── dispatcher.py        # Dispatcher — shell bridge command execution
│       │   └── status.py            # Status transitions (report_success, report_error, etc.)
│       ├── notifier/
│       │   ├── __init__.py
│       │   ├── webhook.py           # FastAPI router — POST /webhooks/github, GET /health
│       │   └── triage.py            # Event triage — maps GitHub events to WorkItems
│       └── utils/
│           ├── __init__.py
│           ├── secrets.py           # scrub_secrets() — regex-based secret redaction
│           └── auth.py              # GitHub auth helpers — build_auth_headers, validate_token
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Shared pytest fixtures
│   ├── test_work_item.py            # Tests for WorkItem model, enums, scrub_secrets
│   ├── test_github_queue.py         # Tests for GitHubQueue
│   ├── test_poller.py               # Tests for Sentinel polling engine
│   └── test_webhook.py              # Tests for webhook receiver and triage
├── pyproject.toml                   # Dependencies, pytest/ruff/mypy config
├── Dockerfile                       # Python 3.12-slim, uv, uvicorn
├── docker-compose.yml               # notifier + sentinel services
├── .env.example                     # Environment variable template
├── .python-version                  # Python version pin (3.12)
├── plan_docs/                       # Reference documents (seeded at repo creation)
│   ├── tech-stack.md
│   ├── architecture.md
│   ├── workflow-plan.md
│   ├── OS-APOW Architecture Guide v3.2.md
│   ├── OS-APOW Development Plan v4.2.md
│   ├── OS-APOW Implementation Specification v1.2.md
│   ├── OS-APOW Plan Review.md
│   └── OS-APOW Simplification Report v1.md
└── docs/                            # Additional documentation
```

## Code Style

- **Python 3.12+** with type hints everywhere
- Follow PEP 8, enforced by **ruff** (line-length: 120, target: py312)
- Use **Pydantic v2** models for all data structures
- Use **async/await** patterns throughout
- Use `from __future__ import annotations` for forward references
- All public functions must have docstrings
- Strict mypy configuration (`mypy src/` with `strict = true`)

## Testing Instructions

- Tests use **pytest** with **pytest-asyncio** (`asyncio_mode = "auto"`)
- Test files in `tests/` mirror `src/` structure
- Run all tests: `python -m pytest tests/ -v`
- Run a single test: `python -m pytest tests/test_work_item.py -v`
- Run with coverage: `python -m pytest tests/ --cov=src --cov-report=term-missing`
- Current coverage: **50%** (target: 80%+)
- Always add/update tests when modifying code
- Test fixtures and shared setup in `tests/conftest.py`

## Architecture Notes

- **Four-pillar architecture**: Notifier → Queue → Sentinel → Worker
- **Provider-agnostic queue interface**: `ITaskQueue` ABC in `interfaces/task_queue.py`
  - Current implementation: `GitHubQueue` using GitHub Issues + Labels
  - Future: Linear, Notion, or SQL backends
- **Shell-bridge pattern**: Sentinel interacts with Workers exclusively via shell scripts (`scripts/devcontainer-opencode.sh`)
- **Polling-first with webhook optimization**: Webhooks are an optimization, not a requirement. Polling self-heals on restart.
- **State managed via GitHub Issues/Labels** ("Markdown as a Database"):
  - `agent:queued` → `agent:in-progress` → `agent:success` / `agent:error` / `agent:infra-failure`
- **Concurrency control**: GitHub "Assignees" as distributed lock with assign-then-verify pattern
- **Security**: HMAC SHA256 webhook verification, regex secret scrubbing, ephemeral tokens

## Configuration

All configuration via environment variables (see `.env.example`):

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub App installation token |
| `GITHUB_REPO` | Yes | Target repository (org/repo) |
| `GITHUB_OWNER` | Yes | GitHub organization |
| `WEBHOOK_SECRET` | Yes | HMAC secret for webhook verification |
| `SENTINEL_BOT_LOGIN` | No | Bot login for distributed locking |
| `POLL_INTERVAL` | No | Seconds between polling cycles (default: 60) |
| `MAX_BACKOFF` | No | Maximum backoff on rate limits in seconds (default: 960) |
| `HEARTBEAT_INTERVAL` | No | Seconds between heartbeat comments (default: 300) |
| `PORT` | No | Server port (default: 8000) |

## CI/CD

- **CI Pipeline**: `.github/workflows/ci.yml`
  - Lint with ruff
  - Type check with mypy (continue-on-error)
  - Run pytest
  - Verify imports
  - Docker build test
- Triggered on push to `main` and `dynamic-workflow-*` branches, and on PRs to `main`

## PR and Commit Guidelines

- Commit message format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`
- All PRs must pass CI checks before merge
- Pin all GitHub Actions to commit SHAs (not version tags)
- Keep changes minimal and targeted

## Common Pitfalls

- **This is a PYTHON project, NOT .NET.** The template has .NET SDK installed in the devcontainer but it is not used by this project.
- The `global.json` and .NET SDK are template artifacts, not part of this project.
- Use `uv` for package management, NOT pip directly.
- Use `httpx.AsyncClient` for all HTTP calls (connection pooling).
- FastAPI runs on port **8000** (not the .NET template ports).
- Healthchecks in `docker-compose.yml` use Python stdlib (`urllib.request`), NOT curl.
- The `plan_docs/` directory contains external-generated documents seeded at clone time. Exclude it from strict linting.
- `mypy` is configured with `strict = true`; type errors must be fixed.
- Current test coverage is 50% — new code should include tests to improve toward 80%.

## Related Documentation

- [README.md](README.md) — Project overview and quick start
- [.ai-repository-summary.md](.ai-repository-summary.md) — Detailed technical documentation
- [plan_docs/architecture.md](plan_docs/architecture.md) — Architecture overview
- [plan_docs/tech-stack.md](plan_docs/tech-stack.md) — Technology stack details
