# workflow-orchestration-queue

> Autonomous agentic orchestration system — transforms GitHub Issues into execution orders fulfilled by AI agents.

## Overview

**workflow-orchestration-queue** (OS-APOW) is a Python-based system that turns GitHub Issues into "Execution Orders" dispatched to AI agents. It replaces manual human-in-the-loop coding processes with persistent, event-driven infrastructure that autonomously fulfills development tasks.

### Key Innovation

Standard project management artifacts (GitHub Issues) become "Execution Orders" fulfilled by specialized AI agents without human intervention.

## Architecture

The system is built on four conceptual pillars:

### The Ear (Work Event Notifier)
- **Technology:** Python 3.12, FastAPI, Pydantic
- **Role:** Webhook receiver with HMAC signature verification
- **Endpoint:** `/webhooks/github`

### The State (Work Queue)
- **Philosophy:** "Markdown as a Database"
- **Implementation:** GitHub Issues and Labels as state machine
- **Labels:** `agent:queued` → `agent:in-progress` → `agent:success` / `agent:error`

### The Brain (Sentinel Orchestrator)
- **Technology:** Python (Async), Docker CLI
- **Role:** Polling engine that discovers queued tasks and manages worker lifecycle
- **Discovery:** Polling every 60 seconds with jittered exponential backoff

### The Hands (Opencode Worker)
- **Technology:** opencode-server CLI, LLM
- **Role:** Executes markdown-based workflow instructions

## Project Structure

```
workflow-orchestration-queue/
├── src/
│   └── workflow_orchestration_queue/
│       ├── __init__.py
│       ├── main.py                    # FastAPI app entry point
│       ├── config.py                  # Settings with pydantic-settings
│       ├── models/
│       │   ├── __init__.py
│       │   └── work_item.py           # WorkItem Pydantic model, enums
│       ├── interfaces/
│       │   ├── __init__.py
│       │   └── task_queue.py          # ITaskQueue ABC
│       ├── queue/
│       │   ├── __init__.py
│       │   └── github_queue.py        # GitHubQueue implementation
│       ├── sentinel/
│       │   ├── __init__.py
│       │   ├── poller.py              # Polling engine
│       │   ├── dispatcher.py          # Shell-bridge dispatcher
│       │   └── status.py              # Status feedback (labels, comments)
│       ├── notifier/
│       │   ├── __init__.py
│       │   ├── webhook.py             # FastAPI webhook receiver
│       │   └── triage.py              # Event triage logic
│       └── utils/
│           ├── __init__.py
│           ├── secrets.py             # scrub_secrets() utility
│           └── auth.py                # GitHub auth helpers
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_work_item.py
│   ├── test_github_queue.py
│   ├── test_poller.py
│   └── test_webhook.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .python-version
```

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for containerized deployment)

### Local Development

```bash
# Install dependencies
uv venv && uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Start the notifier service locally
uvicorn workflow_orchestration_queue.main:app --reload --port 8000

# Start the sentinel poller
python -m workflow_orchestration_queue.sentinel.poller
```

### Docker Deployment

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your GitHub credentials

# Start all services
docker compose up --build
```

### Environment Variables

See [.env.example](.env.example) for all configuration options. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub App installation token |
| `GITHUB_REPO` | Yes | Target repository (org/repo) |
| `GITHUB_OWNER` | Yes | GitHub organization |
| `WEBHOOK_SECRET` | Yes | GitHub webhook secret for HMAC verification |
| `SENTINEL_BOT_LOGIN` | No | Bot login for assign-then-verify locking |

## Development

### Running Tests

```bash
pytest tests/ -v --tb=short
```

### Linting

```bash
ruff check src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Documentation

- [Repository Summary](.ai-repository-summary.md) — Detailed technical documentation
- [Architecture Guide](plan_docs/OS-APOW%20Architecture%20Guide%20v3.2.md) — Full architecture specification
- [Development Plan](plan_docs/OS-APOW%20Development%20Plan%20v4.2.md) — Implementation roadmap
- [Implementation Spec](plan_docs/OS-APOW%20Implementation%20Specification%20v1.2.md) — Detailed implementation guide

## License

See [LICENSE](LICENSE) for details.
