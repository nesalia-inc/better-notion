"""OAuth token management for Notion API.

This module provides token refresh handling for OAuth-based authentication.
"""

from __future__ import annotations

from typing import Any, Callable


class OAuthTokenHandler:
    """Handle OAuth token refresh for Notion API.

    Manages access tokens and refresh tokens, automatically refreshing
    when the access token expires.

    Example:
        >>> def save_tokens(tokens):
        ...     # Save to database/config
        ...     pass
        >>>
        >>> handler = OAuthTokenHandler(
        ...     access_token="ntn_...",
        ...     refresh_token="...",
        ...     on_refresh=save_tokens
        ... )
        >>>
        >>> api = NotionAPI(auth_handler=handler)
    """

    def __init__(
        self,
        *,
        access_token: str,
        refresh_token: str | None = None,
        on_refresh: Callable[[dict[str, str]], None] | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        token_url: str = "https://api.notion.com/v1/oauth/token"
    ) -> None:
        """Initialize OAuth token handler.

        Args:
            access_token: Current OAuth access token
            refresh_token: Optional refresh token for obtaining new access tokens
            on_refresh: Optional callback called when tokens are refreshed.
                       Receives dict with access_token and refresh_token.
            client_id: OAuth client ID (required for refresh)
            client_secret: OAuth client secret (required for refresh)
            token_url: OAuth token endpoint URL
        """
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._on_refresh = on_refresh
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url

    @property
    def access_token(self) -> str:
        """Get current access token."""
        return self._access_token

    @property
    def has_refresh_token(self) -> bool:
        """Check if refresh token is available."""
        return self._refresh_token is not None

    def update_access_token(self, access_token: str) -> None:
        """Update access token (called after manual token update).

        Args:
            access_token: New access token
        """
        self._access_token = access_token

    async def refresh(self, http_client: Any) -> str:
        """Refresh the access token using refresh token.

        Args:
            http_client: HTTP client for making refresh request

        Returns:
            New access token

        Raises:
            ValueError: If refresh_token or client credentials not available
            RuntimeError: If refresh request fails
        """
        if not self._refresh_token:
            raise ValueError("No refresh token available")

        if not self._client_id or not self._client_secret:
            raise ValueError("OAuth client_id and client_secret required for token refresh")

        import httpx

        # Prepare basic auth headers
        import base64

        credentials = base64.b64encode(
            f"{self._client_id}:{self._client_secret}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
        }

        try:
            response = await http_client.post(
                self._token_url,
                headers=headers,
                json=data,
            )
            response.raise_for_status()

            token_data = response.json()

            # Update tokens
            new_access_token = token_data.get("access_token")
            new_refresh_token = token_data.get("refresh_token", self._refresh_token)

            if not new_access_token:
                raise RuntimeError("Refresh response missing access_token")

            self._access_token = new_access_token
            self._refresh_token = new_refresh_token

            # Call callback if provided
            if self._on_refresh:
                self._on_refresh({
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token,
                })

            return new_access_token

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Token refresh failed: {e.response.status_code}") from e
        except Exception as e:
            raise RuntimeError(f"Token refresh failed: {e}") from e
