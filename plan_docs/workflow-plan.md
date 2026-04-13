# Workflow Execution Plan: project-setup

**Workflow**: `project-setup`
**Dynamic Workflow File**: `ai_instruction_modules/ai-workflow-assignments/dynamic-workflows/project-setup.md`
**Repository**: `intel-agency/workflow-orchestration-queue-golf43`
**Date**: 2026-04-13

---

## 1. Overview

### Workflow Name

`project-setup` — Initiate a new repository from a cloned template, transitioning it from a bare scaffold into a fully configured, planned, and structured project ready for autonomous development.

### Project Description

**workflow-orchestration-queue (OS-APOW)** is a headless agentic orchestration platform that transforms GitHub Issues into autonomous Execution Orders. The system is a Python 3.12+ background service (the "Sentinel") that polls for work, spawns AI agents in isolated devcontainers via a shell bridge, and reports results back through GitHub labels and comments. It follows a 4-pillar architecture: **Ear** (FastAPI webhook receiver), **State** (GitHub Issues as database via "Markdown as Database"), **Brain** (async Sentinel orchestrator), and **Hands** (opencode worker agents in devcontainers).

The project has a 4-phase roadmap: **Phase 0** (Seeding/Bootstrapping — this workflow), **Phase 1** (Sentinel MVP — polling engine + shell-bridge dispatch), **Phase 2** (The Ear — FastAPI webhook automation), **Phase 3** (Deep Orchestration — hierarchical planning + self-correction).

### Total Assignments

**6 main assignments** in the `initiate-new-repository` script, plus **1 pre-script event** (`create-workflow-plan`), **2 post-assignment events** fired after each main assignment (`validate-assignment-completion`, `report-progress`), and **1 post-script event** (apply `orchestration:plan-approved` label).

### High-Level Summary

1. **Pre-script**: Create this workflow execution plan document.
2. **Init existing repository**: Branch, configure GitHub Project, import labels/rulesets, rename files, open setup PR.
3. **Create app plan**: Analyze plan docs, create application plan issue, create milestones, link to project.
4. **Create project structure**: Scaffold Python project (`pyproject.toml`, `src/`, Dockerfiles, CI/CD, docs).
5. **Create AGENTS.md**: Build agent-focused instructions file for the repository root.
6. **Debrief and document**: Capture lessons learned, execution trace, commit debrief report.
7. **PR approval and merge**: Resolve PR comments, pass CI, merge setup PR, cleanup.
8. **Post-script**: Apply `orchestration:plan-approved` label to the plan issue.

---

## 2. Project Context Summary

### Key Facts from Plan Docs

| Area | Detail |
|------|--------|
| **Language** | Python 3.12+ (NOT .NET — the existing template has .NET tooling but the application is Python-based) |
| **Framework** | FastAPI (for the Notifier webhook service) |
| **Key Libraries** | httpx (async HTTP client), Pydantic (data validation), uvicorn (ASGI server) |
| **Package Manager** | uv (Rust-based, replaces pip/poetry) |
| **Containerization** | Docker + devcontainers via `devcontainer-opencode.sh` shell bridge |
| **Agent Runtime** | opencode CLI (`opencode --model zai-coding-plan/glm-5 --agent Orchestrator`) |
| **Architecture** | 4 pillars: Ear (FastAPI), State (GitHub Issues/Labels), Brain (Sentinel), Hands (opencode worker) |
| **State Machine** | Labels: `agent:queued` → `agent:in-progress` → `agent:success` / `agent:error` |
| **Concurrency** | Assign-then-verify pattern using GitHub Assignees as distributed lock |
| **Credential Security** | `scrub_secrets()` in `src/models/work_item.py` strips `ghp_*`, `ghs_*`, `gho_*`, `github_pat_*`, `Bearer`, `sk-*`, ZhipuAI keys |
| **Heartbeat** | Background async coroutine posts status comments every 5 min during long tasks |
| **Polling** | 60s interval, jittered exponential backoff on 403/429, max backoff 960s |
| **Branch Strategy** | `main` (stable) + `develop` (integration). MVP targets single-repo polling |
| **Self-Bootstrapping** | Phase 1 is manually seeded; the system builds its own Phase 2 and Phase 3 |

### Plan Docs Available

| File | Content |
|------|---------|
| `plan_docs/OS-APOW Development Plan v4.2.md` | 4-phase roadmap, user stories, acceptance criteria, risk assessment |
| `plan_docs/OS-APOW Architecture Guide v3.2.md` | System-level diagrams, ADRs (Shell-Bridge, Polling-First, Provider-Agnostic), data flow |
| `plan_docs/OS-APOW Implementation Specification v1.2.md` | Features, test cases, logging, containerization, project structure, deliverables |
| `plan_docs/OS-APOW Simplification Report v1.md` | 11 simplification items (S-1 through S-11) — several IMPLEMENTED |
| `plan_docs/OS-APOW Plan Review.md` | Strengths, issues/gotchas (I-1 through I-10), improvement recommendations (R-1 through R-9) |
| `plan_docs/orchestrator_sentinel.py` | Reference implementation of the Sentinel (292 lines) |
| `plan_docs/notifier_service.py` | Reference implementation of the Notifier (110 lines) |
| `plan_docs/src/` | Shared models (`models/work_item.py`) and queue (`queue/github_queue.py`) |

### Simplification Decisions (Already Applied)

- **S-3**: Reduced to 3 env vars (`GITHUB_TOKEN`, `GITHUB_ORG`, `SENTINEL_BOT_LOGIN`), rest hardcoded with defaults
- **S-4**: Environment reset hardcoded to `"stop"` mode only
- **S-5**: Single-repo polling only; cross-repo Search API deferred to future phase
- **S-6**: Queue consolidated to single `src/queue/github_queue.py`
- **S-7**: IPv4 scrubbing pattern removed from `scrub_secrets()`
- **S-8**: "Encrypted" log prose removed — plain local log files
- **S-9**: Phase 3 features moved to "Future Work" appendix
- **S-10**: File logging removed — stdout only, rely on `docker logs`
- **S-11**: `raw_payload` field removed from `WorkItem`

### Directives

- **All GitHub Actions MUST be pinned to specific commit SHA** of their latest release (no `@v3` or `@main` tags)

---

## 3. Assignment Execution Plan

### Assignment 0: `create-workflow-plan` (Pre-script Event)

| Field | Detail |
|-------|--------|
| **Short ID** | `create-workflow-plan` |
| **Title** | Create Workflow Execution Plan |
| **Goal** | Produce this document (`plan_docs/workflow-plan.md`) that serves as the execution guide for the entire `project-setup` dynamic workflow. |
| **Type** | Pre-script event — fires once before the main script begins |

**Key Acceptance Criteria:**

- `plan_docs/workflow-plan.md` exists and covers all 6 assignments in execution order
- Each assignment section documents: goal, acceptance criteria, prerequisites, dependencies, risks, and events
- Project-specific notes reflect the Python/FastAPI tech stack (not .NET)
- Sequencing diagram included
- Open questions documented
- File committed to a new branch `dynamic-workflow-project-setup`

**Prerequisites:**

- Repository cloned and accessible
- Plan docs in `plan_docs/` available for analysis
- Dynamic workflow definition (`project-setup.md`) resolved from remote canonical repository

**Dependencies:**

- None — this is the first action in the workflow

**Risks/Challenges:**

- Minimal risk — document creation only, no code or infrastructure changes

**Events:** None around this assignment (it is itself an event)

---

### Assignment 1: `init-existing-repository`

| Field | Detail |
|-------|--------|
| **Short ID** | `init-existing-repository` |
| **Title** | Initialize Existing Repository |
| **Goal** | Create the setup branch, import repository configuration (branch protection, labels, GitHub Project), rename template files to match project name, and open a setup PR. |
| **Execution Order** | 1 of 6 |

**Key Acceptance Criteria:**

- [ ] New branch `dynamic-workflow-project-setup` created from `main` (must be first step)
- [ ] Branch protection ruleset imported from `.github/protected-branches_ruleset.json` (idempotent — skip if exists)
- [ ] GitHub Project created with repository link and columns: Not Started, In Progress, In Review, Done
- [ ] Labels imported from `.github/.labels.json` via `scripts/import-labels.ps1`
- [ ] `ai-new-app-template.code-workspace` renamed to `workflow-orchestration-queue.code-workspace`
- [ ] `.devcontainer/devcontainer.json` `name` property updated to `workflow-orchestration-queue-devcontainer`
- [ ] PR created from `dynamic-workflow-project-setup` to `main` (PR number captured for Assignment 6)
- [ ] All GitHub Actions in any workflow files pinned to commit SHA (directive)

**Project-Specific Notes:**

- The repository was created from the `intel-agency/workflow-orchestration-queue-golf43` template
- Template placeholders (`workflow-orchestration-queue-golf43`, `intel-agency`) in file contents and paths may need updating if the script from `nam20485/workflow-launch2` hasn't already replaced them
- The branch protection ruleset requires `GH_ORCHESTRATION_AGENT_TOKEN` with `administration: write` scope — NOT `GITHUB_TOKEN`
- The `scripts/test-github-permissions.ps1` script should be run first to verify auth scopes

**Prerequisites:**

- GitHub CLI (`gh`) installed and authenticated
- Required auth scopes: `repo`, `project`, `read:project`, `read:user`, `user:email`, `administration: write`
- `.github/protected-branches_ruleset.json` exists in the repository
- `.github/.labels.json` exists in the repository

**Dependencies:**

- None — this is the first main assignment

**Risks/Challenges:**

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing `administration: write` scope | Cannot create branch protection ruleset | Run `scripts/test-github-permissions.ps1` first; report exact error and stop if permission denied |
| Branch already exists | Step fails | Check for existing branch first; report error immediately |
| Label import partial failure | Some labels missing | Use `scripts/import-labels.ps1` which handles individual failures gracefully |
| PR creation fails ("No commits") | PR not created | Ensure at least one commit (rename/config changes) is pushed before attempting `gh pr create` |

**Post-Assignment Events:**

- `validate-assignment-completion` — verify all acceptance criteria are met
- `report-progress` — post progress update to orchestrator

---

### Assignment 2: `create-app-plan`

| Field | Detail |
|-------|--------|
| **Short ID** | `create-app-plan` |
| **Title** | Create Application Plan |
| **Goal** | Analyze the plan documents, create a comprehensive application plan issue, establish project milestones, and link everything to the GitHub Project for tracking. |
| **Execution Order** | 2 of 6 |

**Key Acceptance Criteria:**

- [ ] All plan docs in `plan_docs/` analyzed and understood
- [ ] Technology stack documented in `plan_docs/tech-stack.md` (Python 3.12+, FastAPI, httpx, Pydantic, uv, Docker)
- [ ] High-level architecture documented in `plan_docs/architecture.md` (4-pillar: Ear/State/Brain/Hands)
- [ ] Application plan issue created using the issue template from `.github/ISSUE_TEMPLATE/application-plan.md`
- [ ] Plan issue covers all 4 phases with detailed breakdowns
- [ ] All acceptance criteria from the Implementation Specification addressed
- [ ] Risks and mitigations documented (API rate limits, LLM looping, concurrency, container drift, security injection)
- [ ] Milestones created matching the 4-phase roadmap:
  - Phase 0: Seeding & Bootstrapping
  - Phase 1: Sentinel MVP
  - Phase 2: The Ear (Webhook Automation)
  - Phase 3: Deep Orchestration
- [ ] Plan issue linked to the GitHub Project
- [ ] Plan issue assigned to "Phase 1: Sentinel MVP" milestone
- [ ] Labels applied: `planning`, `documentation`
- [ ] **NO implementation code written** — planning only

**Project-Specific Notes:**

- The plan docs are rich and detailed — the agent has 5 documents plus 2 reference implementation files to draw from
- The application is Python-based; the plan issue MUST NOT reference .NET tooling, `dotnet build`, `.sln`, `.csproj`, etc.
- Key simplification decisions (S-3 through S-11) should be reflected in the plan — the app plan should describe the simplified architecture
- The Plan Review (I-1 through I-10) identifies specific issues in the reference implementations that the plan should address as work items
- The `orchestration:plan-approved` label must NOT be applied by this assignment — it is applied by the post-script event

**Prerequisites:**

- Assignment 1 complete (branch exists, GitHub Project created, labels imported)
- Plan docs available in `plan_docs/` directory
- Issue template available at `.github/ISSUE_TEMPLATE/application-plan.md`

**Dependencies:**

- Output from Assignment 1: GitHub Project (for linking), imported labels (for tagging), working branch

**Risks/Challenges:**

| Risk | Impact | Mitigation |
|------|--------|------------|
| Plan doc info overload | Agent produces unfocused plan | Structure analysis: extract requirements, tech stack, risks separately |
| Plan too vague | Subsequent assignments lack guidance | Ensure plan includes specific file paths, module names, function signatures |
| Milestone creation API issues | Milestones not created | Use `gh api` or `gh milestone create` with error handling |
| Plan references .NET | Wrong tech stack guidance | Emphasize Python/FastAPI in all plan content; explicitly call out "NOT .NET" |

**Pre-Assignment Event:**

- `gather-context` — collect additional context before planning begins

**Post-Assignment Events:**

- `validate-assignment-completion` — verify plan issue, milestones, and project linkage
- `report-progress` — post progress update

**On-Failure Event:**

- `recover-from-error` — systematic error recovery if the assignment fails

---

### Assignment 3: `create-project-structure`

| Field | Detail |
|-------|--------|
| **Short ID** | `create-project-structure` |
| **Title** | Create Project Structure |
| **Goal** | Scaffold the actual Python project structure, Docker configuration, CI/CD workflows, and documentation based on the application plan. |
| **Execution Order** | 3 of 6 |

**Key Acceptance Criteria:**

- [ ] Python project structure created following `pyproject.toml` / `uv` conventions:
  ```
  /
  ├── pyproject.toml
  ├── uv.lock
  ├── src/
  │   ├── notifier_service.py
  │   ├── orchestrator_sentinel.py
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── work_item.py
  │   │   └── github_events.py
  │   └── queue/
  │       ├── __init__.py
  │       └── github_queue.py
  ├── tests/
  │   ├── __init__.py
  │   ├── test_sentinel.py
  │   ├── test_notifier.py
  │   └── test_work_item.py
  ├── scripts/
  │   ├── devcontainer-opencode.sh
  │   ├── gh-auth.ps1
  │   └── common-auth.ps1
  ├── local_ai_instruction_modules/
  │   ├── create-app-plan.md
  │   ├── perform-task.md
  │   └── analyze-bug.md
  ├── Dockerfile
  ├── docker-compose.yml
  └── docs/
  ```
- [ ] `pyproject.toml` configured with dependencies: `fastapi`, `uvicorn`, `httpx`, `pydantic`
- [ ] `.python-version` file pinning Python 3.12+
- [ ] Dockerfile created (Python base, `uv` installer, editable install via `COPY src/` before `uv pip install -e .`)
- [ ] `docker-compose.yml` created (healthcheck uses Python stdlib, NOT `curl`)
- [ ] Basic CI/CD workflow(s) in `.github/workflows/` with all actions pinned to commit SHA
- [ ] README.md created with project overview
- [ ] `.ai-repository-summary.md` created per `create-repository-summary` assignment spec
- [ ] Initial test project structure established
- [ ] All commits pushed to the `dynamic-workflow-project-setup` branch

**Project-Specific Notes:**

- **CRITICAL**: This is a Python project, NOT .NET. Do NOT create `.sln`, `.csproj`, `global.json`, or any .NET-specific files
- The `uv` package manager is used — NOT `pip`, `poetry`, or `pipenv`
- When creating the Dockerfile, ensure `COPY src/ ./src/` appears **before** `uv pip install -e .` (editable installs require source tree present)
- For `docker-compose.yml` healthchecks, use `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"` — NOT `curl`
- Reference implementations exist in `plan_docs/` (`orchestrator_sentinel.py`, `notifier_service.py`, `src/models/`, `src/queue/`) — these should inform but not be blindly copied; they have known issues (I-1 through I-10 from the Plan Review)
- The shared data model (`src/models/work_item.py`) MUST include: `WorkItem`, `TaskType`, `WorkItemStatus`, `scrub_secrets()` — unified for both Sentinel and Notifier
- The queue implementation (`src/queue/github_queue.py`) MUST consolidate both the Sentinel's `GitHubQueue` and the Notifier's stub into a single class with connection pooling (`httpx.AsyncClient` created once in `__init__`)
- All GitHub Actions workflows MUST pin actions to specific commit SHA (e.g., `uses: actions/checkout@<full-sha>`)

**Prerequisites:**

- Assignment 2 complete (application plan issue created, tech stack documented)
- Working branch `dynamic-workflow-project-setup` exists and has initial commits from Assignment 1

**Dependencies:**

- Output from Assignment 2: `plan_docs/tech-stack.md`, `plan_docs/architecture.md`, plan issue
- Output from Assignment 1: working branch, imported labels

**Risks/Challenges:**

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent creates .NET structure | Wrong scaffolding | Reinforce Python tech stack in prompt; verify generated files |
| Editable install fails in Dockerfile | Build breaks | Ensure `COPY src/` before `uv pip install -e .` |
| Healthcheck uses `curl` | Container health check fails (no curl in base image) | Use Python stdlib `urllib.request` instead |
| Actions not pinned to SHA | Fails SHA-pinning directive | Validate all workflow files after creation |
| Reference code has bugs | Bugs propagate | Flag known issues (I-1 through I-10) and note fixes needed |
| Missing `__init__.py` files | Import errors in Python packages | Ensure all `src/` subdirectories have `__init__.py` |

**Post-Assignment Events:**

- `validate-assignment-completion` — verify project structure, Docker build, CI/CD
- `report-progress` — post progress update

---

### Assignment 4: `create-agents-md-file`

| Field | Detail |
|-------|--------|
| **Short ID** | `create-agents-md-file` |
| **Title** | Create AGENTS.md File |
| **Goal** | Create a comprehensive `AGENTS.md` file at the repository root providing AI coding agents with project context, build commands, conventions, and testing instructions. |
| **Execution Order** | 4 of 6 |

**Key Acceptance Criteria:**

- [ ] `AGENTS.md` exists at the repository root
- [ ] Contains project overview describing the 4-pillar architecture and Sentinel purpose
- [ ] Contains verified setup/build/test commands (actually run and confirmed working):
  - Install: `uv sync`
  - Run sentinel: `uv run python src/orchestrator_sentinel.py`
  - Run notifier: `uv run uvicorn src.notifier_service:app --reload`
  - Run tests: `uv run pytest tests/`
  - Lint: `uv run ruff check src/ tests/`
- [ ] Contains code style section (Python conventions, docstring format, type hints)
- [ ] Contains project structure / directory layout
- [ ] Contains testing instructions
- [ ] Contains PR/commit guidelines
- [ ] Written in standard Markdown with clear, agent-focused language
- [ ] Commands validated by running them
- [ ] Committed and pushed to working branch
- [ ] Stakeholder approval obtained

**Project-Specific Notes:**

- `AGENTS.md` follows the open [agents.md](https://agents.md/) specification
- This file complements `README.md` (human-facing) and `.ai-repository-summary.md` — avoid duplication
- Must emphasize: Python project, NOT .NET; uses `uv` for package management
- Should document the key env vars: `GITHUB_TOKEN`, `GITHUB_ORG`, `SENTINEL_BOT_LOGIN`
- Should document the label state machine: `agent:queued` → `agent:in-progress` → `agent:success`/`agent:error`
- Should reference the shared data model location (`src/models/work_item.py`)
- Should note the shell-bridge architecture (`devcontainer-opencode.sh`) and that the Sentinel doesn't use Docker SDK directly

**Prerequisites:**

- Assignment 3 complete (project structure exists, commands can actually be run)
- `pyproject.toml` configured with all dependencies
- Test structure in place

**Dependencies:**

- Output from Assignment 3: full project scaffolding, `pyproject.toml`, `src/` structure, `tests/` structure
- Output from Assignment 1: `README.md` (for cross-referencing)
- Output from Assignment 3: `.ai-repository-summary.md` (for cross-referencing)

**Risks/Challenges:**

| Risk | Impact | Mitigation |
|------|--------|------------|
| Commands not yet working | AGENTS.md documents non-functional commands | Actually run each command before documenting; if `uv sync` fails, fix first |
| Duplicates README.md | Confusing, maintenance burden | Reference README.md for human-focused content; keep AGENTS.md agent-focused |
| Missing env var documentation | Agents can't run the project | Document required env vars and how to set them |

**Post-Assignment Events:**

- `validate-assignment-completion` — verify AGENTS.md exists and commands work
- `report-progress` — post progress update

---

### Assignment 5: `debrief-and-document`

| Field | Detail |
|-------|--------|
| **Short ID** | `debrief-and-document` |
| **Title** | Debrief and Document Learnings |
| **Goal** | Produce a comprehensive debriefing report capturing key learnings, deviations, errors, and improvement suggestions from the entire `project-setup` workflow execution. |
| **Execution Order** | 5 of 6 |

**Key Acceptance Criteria:**

- [ ] Detailed debrief report created following the structured 12-section template:
  1. Executive Summary
  2. Workflow Overview (assignment table with status/duration/complexity)
  3. Key Deliverables
  4. Lessons Learned
  5. What Worked Well
  6. What Could Be Improved
  7. Errors Encountered and Resolutions
  8. Complex Steps and Challenges
  9. Suggested Changes (workflow assignments, agents, prompts, scripts)
  10. Metrics and Statistics
  11. Future Recommendations (short/medium/long term)
  12. Conclusion
- [ ] All deviations from assignments documented
- [ ] Execution trace saved as `debrief-and-document/trace.md`
- [ ] Report reviewed and approved by stakeholder
- [ ] Committed and pushed to working branch

**Project-Specific Notes:**

- The debrief should flag any plan-impacting findings as **ACTION ITEMS** with recommendations: (a) file new issue, or (b) update later phase descriptions
- Known issues from the Plan Review (I-1 through I-10) that weren't fully addressed during scaffolding should be flagged as future work items
- If any simplification items (S-3 through S-11) couldn't be applied during structure creation, flag them
- The execution trace should include: all `gh` commands run, files created/modified, CI results, and any interactive decisions

**Prerequisites:**

- Assignments 1–4 complete (all project work done)

**Dependencies:**

- Outputs from all prior assignments: full history of actions, files, issues, errors

**Risks/Challenges:**

| Risk | Impact | Mitigation |
|------|--------|------------|
| Incomplete execution trace | Debrief lacks evidence | Maintain running log from Assignment 1 onward |
| Debrief too superficial | Not actionable for future | Ensure specific examples, file paths, command outputs |

**Post-Assignment Events:**

- `validate-assignment-completion` — verify report completeness
- `report-progress` — post progress update

---

### Assignment 6: `pr-approval-and-merge`

| Field | Detail |
|-------|--------|
| **Short ID** | `pr-approval-and-merge` |
| **Title** | PR Approval and Merge |
| **Goal** | Complete the full PR lifecycle for the setup PR: resolve all review comments, pass CI, obtain approval, merge, and clean up the setup branch and issues. |
| **Execution Order** | 6 of 6 |

**Key Acceptance Criteria:**

- [ ] CI/CD status checks all pass (CI remediation loop: up to 3 fix attempts)
- [ ] Code review delegated to `code-reviewer` subagent (NOT self-review)
- [ ] Auto-reviewer comments (Copilot, CodeQL, Gemini) waited for and resolved
- [ ] `ai-pr-comment-protocol.md` workflow executed and logged
- [ ] All review threads resolved via `resolveReviewThread` GraphQL mutation
- [ ] `pr-unresolved-threads.json` verified empty
- [ ] Summary comment posted enumerating all thread resolutions
- [ ] Stakeholder/orchestrator approval obtained
- [ ] PR merged using repository's preferred strategy
- [ ] Source branch `dynamic-workflow-project-setup` deleted (if policy allows)
- [ ] Related setup issues closed or updated
- [ ] Run report updated with final status, evidence locations, and next steps
- [ ] `$pr_num` input consumed from Assignment 1 output

**Project-Specific Notes:**

- This is an **automated setup PR** — self-approval by the orchestrator is acceptable per the dynamic workflow spec
- The CI remediation loop (Phase 0.5) MUST still be executed even though self-approval is OK
- If CI fails, up to 3 fix cycles before escalating
- The PR includes changes from ALL prior assignments: branch protection, labels, renamed files, app plan issue, project structure, AGENTS.md, debrief report
- The `scripts/query.ps1` utility can be used for managing PR review threads (supports `--DryRun`, `--AutoResolve`)
- After merge, the `orchestration:plan-approved` label will be applied to the plan issue by the post-script event

**Prerequisites:**

- Assignments 1–5 complete (all work committed to PR branch)
- CI/CD workflows functional and triggered on PR
- PR number available from Assignment 1

**Dependencies:**

- Output from Assignment 1: `$pr_num` (the PR number)
- Output from Assignment 3: CI/CD workflows (must be functional)
- Output from Assignment 5: debrief report (last commit before review)

**Risks/Challenges:**

| Risk | Impact | Mitigation |
|------|--------|------------|
| CI checks fail | Merge blocked | Remediation loop: fix, push, re-check (max 3 attempts) |
| Merge conflicts with `main` | PR cannot merge | Rebase from `main` before merge |
| Branch protection requires human review | Self-approval insufficient | Orchestrator has `administration: write` scope; adjust if needed |
| Branch deletion fails | Orphaned branch | Check policy; document if deletion not possible |

**Post-Assignment Events:**

- `validate-assignment-completion` — verify merge succeeded, branch cleaned up
- `report-progress` — post final progress update

---

## 4. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    project-setup Dynamic Workflow                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ PRE-SCRIPT EVENT ──────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │  [create-workflow-plan] ──► plan_docs/workflow-plan.md           │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│  ┌─ MAIN SCRIPT: initiate-new-repository ──────────────────────────┐   │
│  │                                                                   │   │
│  │  ┌──────────────────────┐                                        │   │
│  │  │ 1. init-existing-    │──► Branch + Ruleset + Project          │   │
│  │  │    repository        │    + Labels + Renames + PR #N          │   │
│  │  └──────────┬───────────┘                                        │   │
│  │             │ [validate] [report]                                  │   │
│  │             ▼                                                      │   │
│  │  ┌──────────────────────┐                                        │   │
│  │  │ 2. create-app-plan   │──► Plan Issue + Milestones             │   │
│  │  │                      │    + tech-stack.md + architecture.md    │   │
│  │  └──────────┬───────────┘                                        │   │
│  │             │ [validate] [report]                                  │   │
│  │             ▼                                                      │   │
│  │  ┌──────────────────────┐                                        │   │
│  │  │ 3. create-project-   │──► Python Scaffolding + Docker         │   │
│  │  │    structure         │    + CI/CD + Docs + Tests               │   │
│  │  └──────────┬───────────┘                                        │   │
│  │             │ [validate] [report]                                  │   │
│  │             ▼                                                      │   │
│  │  ┌──────────────────────┐                                        │   │
│  │  │ 4. create-agents-    │──► AGENTS.md (validated commands)      │   │
│  │  │    md-file           │                                        │   │
│  │  └──────────┬───────────┘                                        │   │
│  │             │ [validate] [report]                                  │   │
│  │             ▼                                                      │   │
│  │  ┌──────────────────────┐                                        │   │
│  │  │ 5. debrief-and-      │──► Debrief Report + trace.md           │   │
│  │  │    document          │                                        │   │
│  │  └──────────┬───────────┘                                        │   │
│  │             │ [validate] [report]                                  │   │
│  │             ▼                                                      │   │
│  │  ┌──────────────────────┐                                        │   │
│  │  │ 6. pr-approval-and-  │──► Resolve Comments → Merge            │   │
│  │  │    merge             │    → Delete Branch → Close Issues      │   │
│  │  │    (input: PR #N)    │                                        │   │
│  │  └──────────┬───────────┘                                        │   │
│  │             │ [validate] [report]                                  │   │
│  │             ▼                                                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│  ┌─ POST-SCRIPT EVENT ─────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │  Apply label `orchestration:plan-approved` to plan issue          │   │
│  │  (triggers next orchestration pipeline phase)                     │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Event Flow per Assignment:**

```
Assignment N
    │
    ├── (execute assignment)
    │
    ├── post-assignment-complete:
    │   ├── validate-assignment-completion
    │   └── report-progress
    │
    ▼
Assignment N+1
```

---

## 5. Open Questions

### Q1: Reference Implementation Handling

The `plan_docs/` directory contains reference implementations (`orchestrator_sentinel.py`, `notifier_service.py`, `src/`). Should these be:
- (a) Copied to `src/` as-is and then fixed during Phase 1 implementation?
- (b) Used as reference only, with fresh implementations written from the plan?
- (c) Removed from `plan_docs/` after the project structure is created (to avoid confusion)?

**Recommendation**: Option (a) with a `TODO` comment block at the top listing known issues (I-1 through I-10).

### Q2: .NET Template Remnants

The template repository has .NET SDK, Avalonia templates, `global.json` references, and `.sln`/`.csproj` files. Should `create-project-structure`:
- (a) Leave existing template files untouched and only add Python structure?
- (b) Remove .NET-specific files that don't serve the Python project?

**Recommendation**: Option (b) — remove or rename .NET-specific files to avoid confusion for AI agents. Document what was removed in the debrief.

### Q3: CI/CD Workflow Scope for Initial Scaffolding

What level of CI/CD should `create-project-structure` establish?
- (a) Minimal: lint + format only (ruff)
- (b) Standard: lint + format + pytest + Docker build
- (c) Full: lint + format + pytest + Docker build + security scan + devcontainer build

**Recommendation**: Option (b) — sufficient to validate the setup PR without over-engineering.

### Q4: Environment Variable Configuration

The Simplification Report (S-3) reduced env vars to 3 required: `GITHUB_TOKEN`, `GITHUB_ORG`, `SENTINEL_BOT_LOGIN`. Should `create-project-structure` create a `.env.example` file documenting these, or is that premature?

**Recommendation**: Create `.env.example` with the 3 required vars documented (no actual values). This helps agents understand the configuration.

### Q5: Test Framework Selection

Should the test scaffolding use `pytest` directly or also include `pytest-asyncio` for testing the async components (Sentinel, Notifier)?

**Recommendation**: Include `pytest-asyncio` in dev dependencies — both the Sentinel and Notifier are async and will need async test fixtures.

### Q6: Label State Machine Scope

Should all the labels described in the architecture (`agent:queued`, `agent:in-progress`, `agent:success`, `agent:error`, `agent:infra-failure`, `agent:impl-error`, `agent:stalled-budget`, `agent:reconciling`) be imported during `init-existing-repository`, or just a subset for Phase 1?

**Recommendation**: Import all labels defined in `.github/.labels.json` — the labels file should already contain the full set. If it doesn't, flag this as an ACTION ITEM in the debrief.

---

## Appendix: Event Summary Table

| Event | Trigger | Assignments | Output Key |
|-------|---------|-------------|------------|
| `pre-script-begin` | Before main script | `create-workflow-plan` | `#events.pre-script-begin.create-workflow-plan` |
| `post-assignment-complete` | After each main assignment | `validate-assignment-completion`, `report-progress` | `#events.post-assignment-complete.<name>` |
| `post-script-complete` | After all assignments done | Apply `orchestration:plan-approved` label | `#events.post-script-complete.plan-approved` |

## Appendix: Assignment Dependency Graph

```
create-workflow-plan (pre-script)
        │
        ▼
init-existing-repository ──────────────────────────────────┐
        │                                                   │
        │  [Branch, PR #N, Project, Labels]                 │
        ▼                                                   │
create-app-plan ────────────────────────────────────────────┤
        │                                                   │
        │  [Plan Issue, Milestones, tech-stack.md]          │
        ▼                                                   │
create-project-structure ───────────────────────────────────┤
        │                                                   │
        │  [Python scaffolding, Docker, CI/CD]              │
        ▼                                                   │
create-agents-md-file ──────────────────────────────────────┤
        │                                                   │
        │  [AGENTS.md with validated commands]              │
        ▼                                                   │
debrief-and-document ───────────────────────────────────────┤
        │                                                   │
        │  [Debrief report, trace.md]                       │
        ▼                                                   │
pr-approval-and-merge (input: PR #N) ───────────────────────┤
        │                                                   │
        │  [Merged PR, deleted branch, closed issues]       │
        ▼                                                   │
post-script: apply orchestration:plan-approved ─────────────┘
