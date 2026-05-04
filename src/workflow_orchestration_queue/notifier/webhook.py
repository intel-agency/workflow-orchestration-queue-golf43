"""
FastAPI Webhook Receiver.

Handles incoming GitHub webhook events, verifies HMAC signatures,
and routes actionable events to the work queue.

This is the primary gateway ("The Ear") for external stimuli.
"""

import hashlib
import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from workflow_orchestration_queue.interfaces.task_queue import ITaskQueue
from workflow_orchestration_queue.notifier.triage import triage_event
from workflow_orchestration_queue.queue.github_queue import GitHubQueue

router = APIRouter(tags=["webhooks"])

# --- Configuration ---

_WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
_GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _get_queue() -> ITaskQueue:
    """Dependency injection for the queue implementation.

    Phase 1: GitHub. Can be swapped for Linear, Jira, etc.
    """
    return GitHubQueue(token=_GITHUB_TOKEN)


async def verify_signature(request: Request, x_hub_signature_256: str = Header(None)) -> None:
    """Verify the HMAC SHA256 signature of the incoming webhook."""
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="X-Hub-Signature-256 missing")

    body = await request.body()
    if not _WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="WEBHOOK_SECRET not configured")

    signature = "sha256=" + hmac.new(_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")


# --- Endpoints ---


@router.post("/webhooks/github", dependencies=[Depends(verify_signature)])
async def handle_github_webhook(request: Request, queue: ITaskQueue = Depends(_get_queue)) -> dict[str, str]:
    """Handle incoming GitHub webhook events.

    Verifies signature, triages the event, and queues actionable items.
    """
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "")

    # Use the triage module to determine if this event is actionable
    work_item = triage_event(event_type, payload)

    if work_item is None:
        return {"status": "ignored", "reason": "No actionable event mapping found"}

    success = await queue.add_to_queue(work_item)
    if success:
        return {"status": "accepted", "item_id": work_item.id}

    return {"status": "error", "reason": "Failed to queue work item"}
