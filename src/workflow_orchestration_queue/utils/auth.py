"""
GitHub Authentication Helpers.

Utilities for authenticating with the GitHub API, including
token validation and header generation.
"""

import logging
from typing import Optional

import httpx

logger = logging.getLogger("OS-APOW-Auth")

GITHUB_API_BASE = "https://api.github.com"


def build_auth_headers(token: str) -> dict[str, str]:
    """Build standard GitHub API authorization headers.

    Args:
        token: GitHub personal access token or app installation token.

    Returns:
        Dictionary with Authorization and Accept headers.
    """
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


async def validate_token(token: str) -> Optional[str]:
    """Validate a GitHub token by calling the /user endpoint.

    Args:
        token: The GitHub token to validate.

    Returns:
        The authenticated user's login name, or None if invalid.
    """
    headers = build_auth_headers(token)
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        try:
            response = await client.get(f"{GITHUB_API_BASE}/user")
            if response.status_code == 200:
                login = response.json().get("login", "")
                logger.info(f"Token validated for user: {login}")
                return login
            else:
                logger.warning(f"Token validation failed: {response.status_code}")
                return None
        except httpx.HTTPError as exc:
            logger.error(f"Token validation error: {exc}")
            return None
