"""
FastAPI application entry point.

Provides the webhook receiver endpoint and health check.
"""

from fastapi import FastAPI

from workflow_orchestration_queue.notifier.webhook import router as webhook_router

app = FastAPI(
    title="workflow-orchestration-queue",
    description="Autonomous agentic orchestration system — transforms GitHub Issues into execution orders fulfilled by AI agents",
    version="0.1.0",
)

app.include_router(webhook_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring and docker-compose healthcheck."""
    return {"status": "online", "system": "OS-APOW Notifier"}
