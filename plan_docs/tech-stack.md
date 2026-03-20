# workflow-orchestration-queue: Technology Stack

This document summarizes the technology stack for the workflow-orchestration-queue system. For detailed specifications, refer to the linked documents.

## Primary Language

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12+ | Primary language for Orchestrator, API Webhook receiver, and all system logic |

## Web Framework & Server

| Technology | Purpose | Reference |
|------------|---------|-----------|
| **FastAPI** | High-performance async web framework for the Webhook Notifier ("The Ear") | [Impl Spec §Frameworks](OS-APOW%20Implementation%20Specification%20v1.2.md) |
| **Uvicorn** | Lightning-fast ASGI web server for production | [Impl Spec §Frameworks](OS-APOW%20Implementation%20Specification%20v1.2.md) |

## Data Validation & Settings

| Technology | Purpose | Reference |
|------------|---------|-----------|
| **Pydantic** | Strict data validation, settings management, and schema definitions (WorkItem, TaskType, WorkItemStatus) | [Impl Spec §Frameworks](OS-APOW%20Implementation%20Specification%20v1.2.md) |

## HTTP Client

| Technology | Purpose | Reference |
|------------|---------|-----------|
| **HTTPX** | Fully asynchronous HTTP client for GitHub REST API calls without blocking the event loop | [Impl Spec §Frameworks](OS-APOW%20Implementation%20Specification%20v1.2.md) |

## Package Management

| Technology | Version | Purpose | Reference |
|------------|---------|---------|-----------|
| **uv** | 0.10.9+ | Rust-based Python package installer and dependency resolver (orders of magnitude faster than pip/poetry) | [Impl Spec §Frameworks](OS-APOW%20Implementation%20Specification%20v1.2.md) |

## Containerization & Infrastructure

| Technology | Purpose | Reference |
|------------|---------|-----------|
| **Docker CLI** | Core underlying worker execution engine with sandboxing and environment consistency | [Impl Spec §Containerization](OS-APOW%20Implementation%20Specification%20v1.2.md) |
| **DevContainers** | Reproducible worker environment (bit-for-bit identical to human developer environment) | [Arch Guide §2D](OS-APOW%20Architecture%20Guide%20v3.2.md) |
| **Docker Compose** | Multi-container orchestration for complex scenarios (web app + database) | [Impl Spec §Docker Compose](OS-APOW%20Implementation%20Specification%20v1.2.md) |

## Shell Scripts

| Technology | Purpose | Reference |
|------------|---------|-----------|
| **PowerShell Core (pwsh)** | Shell Bridge Scripts, Auth synchronization, cross-platform CLI | [Impl Spec §Language](OS-APOW%20Implementation%20Specification%20v1.2.md) |
| **Bash** | Shell Bridge Scripts, devcontainer-opencode.sh orchestration | [Arch Guide §2C](OS-APOW%20Architecture%20Guide%20v3.2.md) |

## LLM Runtime

| Technology | Purpose | Reference |
|------------|---------|-----------|
| **opencode-server CLI** | AI agent runtime that executes markdown-based instruction modules | [Arch Guide §2D](OS-APOW%20Architecture%20Guide%20v3.2.md) |
| **GLM-5 / Claude 3.5 Sonnet** | LLM Core for agent reasoning | [Arch Guide §2D](OS-APOW%20Architecture%20Guide%20v3.2.md) |

## Security & Authentication

| Feature | Purpose | Reference |
|---------|---------|-----------|
| **HMAC SHA256** | Cryptographic verification of GitHub webhook signatures | [Arch Guide §5](OS-APOW%20Architecture%20Guide%20v3.2.md) |
| **GitHub App Installation Tokens** | Scoped authentication with least-privilege access | [Arch Guide §5](OS-APOW%20Architecture%20Guide%20v3.2.md) |

## Project Configuration

| File | Purpose |
|------|---------|
| `pyproject.toml` | Core definition file for uv dependencies and metadata |
| `uv.lock` | Deterministic lockfile for exact package versions |

## Environment Variables (Required)

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | GitHub App installation token |
| `GITHUB_REPO` | Target repository (org/repo format) |
| `SENTINEL_BOT_LOGIN` | GitHub login of the bot account for distributed locking |

## Resource Constraints

| Resource | Limit | Purpose |
|----------|-------|---------|
| CPU | 2 CPUs | Prevent DoS from rogue agents |
| RAM | 4GB | Ensure orchestrator stability |

---

*See also: [Architecture Overview](architecture.md), [Implementation Specification](OS-APOW%20Implementation%20Specification%20v1.2.md)*
