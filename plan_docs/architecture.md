# workflow-orchestration-queue: Architecture Overview

This document provides a high-level summary of the system architecture. For detailed specifications, refer to the linked documents.

## Executive Summary

workflow-orchestration-queue transforms **Interactive AI Coding** into **Headless Agentic Orchestration**. It replaces manual human-in-the-loop processes with a persistent, event-driven infrastructure that autonomously fulfills tasks from GitHub Issues.

**Key Innovation:** Standard project management artifacts (GitHub Issues) become "Execution Orders" fulfilled by specialized AI agents without human intervention.

**Reference:** [Architecture Guide §1](OS-APOW%20Architecture%20Guide%20v3.2.md)

---

## The Four Pillars

The system is built on four conceptual pillars, each handling a distinct domain:

### 1. The Ear (Work Event Notifier)

| Aspect | Details |
|--------|---------|
| **Technology** | Python 3.12, FastAPI, Pydantic |
| **Role** | Primary gateway for external stimuli |
| **Responsibilities** | Secure webhook ingestion, HMAC signature verification, event triage, WorkItem manifest generation |
| **Endpoint** | `/webhooks/github` |

**Key Feature:** Cryptographic verification prevents "Prompt Injection via Webhook" by ensuring only verified GitHub events trigger agent actions.

**Reference:** [Architecture Guide §2A](OS-APOW%20Architecture%20Guide%20v3.2.md)

---

### 2. The State (Work Queue)

| Aspect | Details |
|--------|---------|
| **Philosophy** | "Markdown as a Database" |
| **Implementation** | GitHub Issues, Labels, Milestones |
| **Benefits** | World-class audit logs, transparent versioning, out-of-box UI, real-time human intervention |

**State Machine (Labels):**

| Label | Meaning |
|-------|---------|
| `agent:queued` | Task validated, awaiting Sentinel |
| `agent:in-progress` | Sentinel claimed, task assigned |
| `agent:reconciling` | Stale task recovery state |
| `agent:success` | Terminal success (PR created, tests passed) |
| `agent:error` | Technical failure (logs posted to issue) |
| `agent:infra-failure` | Infrastructure failure (devcontainer issues) |

**Concurrency Control:** Uses GitHub "Assignees" as a distributed lock with **assign-then-verify** pattern.

**Reference:** [Architecture Guide §2B](OS-APOW%20Architecture%20Guide%20v3.2.md)

---

### 3. The Brain (Sentinel Orchestrator)

| Aspect | Details |
|--------|---------|
| **Technology** | Python (Async), PowerShell Core, Docker CLI |
| **Role** | Persistent supervisor managing Worker lifecycle |
| **Discovery** | Polling every 60 seconds (polling-first resiliency) |

**Key Operations:**

1. **Polling Discovery** - Scan for `agent:queued` issues with jittered exponential backoff
2. **Auth Synchronization** - Run `scripts/gh-auth.ps1` before execution
3. **Shell-Bridge Protocol** - Manage Worker via `devcontainer-opencode.sh`
4. **Telemetry** - Heartbeat comments every 5 minutes, stdout logging
5. **Environment Reset** - Stop container between tasks to prevent state bleed
6. **Graceful Shutdown** - Handle SIGTERM/SIGINT, finish current task, exit cleanly

**Reference:** [Architecture Guide §2C](OS-APOW%20Architecture%20Guide%20v3.2.md)

---

### 4. The Hands (Opencode Worker)

| Aspect | Details |
|--------|---------|
| **Technology** | opencode-server CLI, LLM (GLM-5/Claude) |
| **Environment** | High-fidelity DevContainer from template |

**Worker Capabilities:**

- **Contextual Awareness** - Access project structure, maintain vector-indexed codebase view
- **Instructional Logic** - Execute `.md` workflow modules from `/local_ai_instruction_modules/`
- **Verification** - Run local test suites before PR submission

**Key Principle:** "Logic-as-Markdown" - workflows can be updated via PR without changing Python code.

**Reference:** [Architecture Guide §2D](OS-APOW%20Architecture%20Guide%20v3.2.md)

---

## Key Architectural Decisions (ADRs)

### ADR 07: Standardized Shell-Bridge Execution

The Orchestrator interacts with the agentic environment **exclusively** via `./scripts/devcontainer-opencode.sh`. This ensures environment parity with local developers and prevents "Configuration Drift."

**Reference:** [Architecture Guide §3](OS-APOW%20Architecture%20Guide%20v3.2.md)

### ADR 08: Polling-First Resiliency Model

Webhooks are an **optimization**, not a requirement. Polling ensures the system self-heals on restart by reconciling GitHub labels.

**Reference:** [Architecture Guide §3](OS-APOW%20Architecture%20Guide%20v3.2.md)

### ADR 09: Provider-Agnostic Interface Layer

All queue interactions are abstracted behind `ITaskQueue` interface using the Strategy Pattern. This enables future support for Linear, Notion, or internal SQL queues.

**Reference:** [Architecture Guide §3](OS-APOW%20Architecture%20Guide%20v3.2.md)

---

## Security Architecture

| Layer | Protection |
|-------|------------|
| **Network Isolation** | Worker containers in dedicated Docker network, isolated from host |
| **Credential Scoping** | Ephemeral tokens via environment variables, destroyed on session end |
| **Credential Scrubbing** | Regex-based scrubber strips PATs, Bearer tokens, API keys from logs |
| **Resource Constraints** | 2 CPU / 4GB RAM limits prevent DoS from rogue agents |
| **HMAC Verification** | All webhooks validated against `WEBHOOK_SECRET` |

**Reference:** [Architecture Guide §5](OS-APOW%20Architecture%20Guide%20v3.2.md)

---

## Data Flow (Happy Path)

```
1. User opens GitHub Issue (application-plan template)
2. Webhook hits Notifier (FastAPI)
3. Notifier verifies signature, confirms title pattern, adds agent:queued label
4. Sentinel detects new label, assigns issue, updates to agent:in-progress
5. Sentinel runs git clone/pull to sync workspace
6. Sentinel executes devcontainer-opencode.sh up
7. Sentinel dispatches prompt command
8. Worker reads issue, executes workflow, creates sub-tasks
9. Worker posts completion comment
10. Sentinel detects exit, removes in-progress, adds agent:success
```

**Reference:** [Architecture Guide §4](OS-APOW%20Architecture%20Guide%20v3.2.md)

---

## Self-Bootstrapping Lifecycle

1. **Bootstrap** - Developer manually clones template
2. **Seed** - Add plan docs to repo
3. **Init** - Run `devcontainer-opencode.sh up`
4. **Orchestrate** - Run project-setup assignment
5. **Autonomous Phase** - Start Sentinel service, AI manages further development

**Reference:** [Architecture Guide §6](OS-APOW%20Architecture%20Guide%20v3.2.md)

---

## Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml               # uv dependencies and metadata
├── uv.lock                      # Deterministic lockfile
├── src/
│   ├── notifier_service.py      # FastAPI webhook ingestion
│   ├── orchestrator_sentinel.py # Background polling and dispatch
│   ├── models/
│   │   ├── work_item.py         # Unified WorkItem, TaskType, scrub_secrets()
│   │   └── github_events.py     # GitHub webhook payload schemas
│   └── queue/
│       └── github_queue.py      # ITaskQueue ABC + GitHubQueue
├── scripts/
│   ├── devcontainer-opencode.sh # Core shell bridge
│   ├── gh-auth.ps1              # GitHub auth utility
│   └── update-remote-indices.ps1# Vector index sync
└── local_ai_instruction_modules/ # Markdown workflow prompts
```

**Reference:** [Impl Spec §Project Structure](OS-APOW%20Implementation%20Specification%20v1.2.md)

---

## Related Documents

- [Technology Stack](tech-stack.md)
- [Architecture Guide v3.2](OS-APOW%20Architecture%20Guide%20v3.2.md)
- [Development Plan v4.2](OS-APOW%20Development%20Plan%20v4.2.md)
- [Implementation Specification v1.2](OS-APOW%20Implementation%20Specification%20v1.2.md)
- [Plan Review](OS-APOW%20Plan%20Review.md)
- [Simplification Report v1](OS-APOW%20Simplification%20Report%20v1.md)
