"""
Tests for the webhook receiver.
"""

import hashlib
import hmac
import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from workflow_orchestration_queue.main import app


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check(self) -> None:
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"


class TestWebhookEndpoint:
    """Tests for the /webhooks/github endpoint."""

    def _sign_payload(self, payload: bytes, secret: str = "test-secret") -> str:
        """Generate a valid HMAC signature for a payload."""
        return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    def test_rejects_missing_signature(self) -> None:
        client = TestClient(app)
        response = client.post("/webhooks/github", json={"test": "data"})
        assert response.status_code == 401

    @patch("workflow_orchestration_queue.notifier.webhook._WEBHOOK_SECRET", "test-secret")
    @patch("workflow_orchestration_queue.notifier.webhook._GITHUB_TOKEN", "test-token")
    def test_rejects_invalid_signature(self) -> None:
        client = TestClient(app)
        response = client.post(
            "/webhooks/github",
            json={"test": "data"},
            headers={"X-Hub-Signature-256": "sha256=invalid"},
        )
        assert response.status_code == 401

    @patch("workflow_orchestration_queue.notifier.webhook._WEBHOOK_SECRET", "test-secret")
    @patch("workflow_orchestration_queue.notifier.webhook._GITHUB_TOKEN", "test-token")
    def test_ignores_non_actionable_events(self) -> None:
        client = TestClient(app)
        payload = json.dumps({"action": "closed", "issue": {}})
        signature = self._sign_payload(payload.encode())

        response = client.post(
            "/webhooks/github",
            content=payload.encode(),
            headers={
                "X-Hub-Signature-256": signature,
                "X-GitHub-Event": "issues",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"


class TestEventTriage:
    """Tests for the event triage logic."""

    def test_triage_plan_issue(self) -> None:
        from workflow_orchestration_queue.notifier.triage import triage_event

        payload = {
            "action": "opened",
            "issue": {
                "id": 12345,
                "number": 1,
                "title": "[Application Plan] New Feature",
                "html_url": "https://github.com/test/repo/issues/1",
                "body": "Plan description",
                "node_id": "test_node",
                "labels": [{"name": "agent:plan"}],
            },
            "repository": {
                "full_name": "test/repo",
            },
        }

        result = triage_event("issues", payload)
        assert result is not None
        assert result.task_type.value == "PLAN"

    def test_triage_ignores_non_issues(self) -> None:
        from workflow_orchestration_queue.notifier.triage import triage_event

        result = triage_event("push", {"ref": "refs/heads/main"})
        assert result is None

    def test_triage_ignores_closed_issues(self) -> None:
        from workflow_orchestration_queue.notifier.triage import triage_event

        payload = {
            "action": "closed",
            "issue": {
                "id": 12345,
                "number": 1,
                "title": "Some issue",
                "html_url": "https://github.com/test/repo/issues/1",
                "body": "body",
                "node_id": "test_node",
                "labels": [],
            },
            "repository": {
                "full_name": "test/repo",
            },
        }

        result = triage_event("issues", payload)
        assert result is None
