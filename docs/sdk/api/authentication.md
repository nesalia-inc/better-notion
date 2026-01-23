# Authentication

The Notion API requires authentication for all requests. The SDK supports both **Bearer Token** authentication (for integrations) and **OAuth 2.0** (for public integrations).

## Overview

### Authentication Methods

| Method | Use Case | Description |
|---------|----------|-------------|
| **Bearer Token** | Internal integrations | Integration secret token |
| **OAuth 2.0** | Public integrations | User authorization with access tokens |

### API Version

All requests must include the `Notion-Version` header:

```
Notion-Version: 2025-09-03
```

Supported versions:
- `2022-06-28`
- `2022-10-16`
- `2023-05-13`
- `2024-04-16`
- `2025-09-03` (latest)

## Bearer Token Authentication

### What is Bearer Token?

Bearer token authentication uses an integration secret token:

```python
# Token format
secret_<64-character-string>

# Example
secret_BBBFCvKK4cwJ8gTIIlGgyx8VH6MxkmqKQJNYCtvE7xF1
```

### When to Use

Use bearer token when:
- Building internal tools
- Creating integrations for your own workspace
- Using the integration capabilities in Notion
- Don't need user-specific permissions

### Basic Usage

```python
from better_notion.api import NotionAPI

# Initialize with bearer token
api = NotionAPI(auth="secret_...")

# Token is automatically added to all requests
page = await api.pages.retrieve(page_id)
```

### BearerAuth Class

```python
class BearerAuth:
    """
    Bearer token authentication for Notion integrations.

    Uses integration secret token.
    """

    def __init__(self, token: str):
        """
        Initialize with integration token.

        Args:
            token: Integration secret token

        Raises:
            ValueError: If token format is invalid
        """
        token = token.strip()

        if not token.startswith("secret_"):
            raise ValueError(
                f"Invalid token format. "
                f"Token must start with 'secret_', got: {token[:10]}..."
            )

        self.token = token

    @property
    def headers(self) -> dict[str, str]:
        """
        Get authorization headers.

        Returns:
            Headers dict with Authorization header
        """
        return {
            "Authorization": f"Bearer {self.token}"
        }

    def __repr__(self) -> str:
        """Secure string representation (hides token)."""
        token_preview = f"{self.token[:10]}...{self.token[-4:]}"
        return f"BearerAuth({token_preview})"
```

### Usage in HTTP Client

```python
async def make_request(
    client: HTTPClient,
    auth: BearerAuth,
    method: str,
    path: str
) -> dict:
    """
    Make authenticated request.

    Bearer token is added to request headers.
    """
    headers = auth.headers

    response = await client.request(
        method=method,
        path=path,
        headers=headers
    )

    return response
```

## OAuth 2.0 Authentication

### What is OAuth?

OAuth 2.0 allows public integrations to request user authorization and access their Notion workspace.

### OAuth Flow

```
1. User clicks "Connect to Notion"
2. Redirect to Notion authorization URL
3. User approves integration
4. Notion redirects back with authorization code
5. Exchange code for access token
6. Use access token to make API requests
7. (Optional) Refresh access token when expired
```

### When to Use

Use OAuth when:
- Building a public integration
- Publishing on Notion's integration directory
- Need user-specific permissions
- Want users to authorize your integration

### OAuth 2.0 Implementation

#### OAuthToken Class

```python
class OAuthToken:
    """
    OAuth 2.0 token for Notion API.

    Handles access tokens and optional refresh tokens.
    """

    def __init__(
        self,
        access_token: str,
        *,
        refresh_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        expires_in: int | None = None,
        obtained_at: datetime | None = None,
        auto_refresh: bool = False
    ):
        """
        Initialize OAuth token.

        Args:
            access_token: OAuth access token
            refresh_token: Optional refresh token
            client_id: OAuth client ID
            client_secret: OAuth client secret
            expires_in: Token lifetime in seconds
            obtained_at: When token was obtained
            auto_refresh: Auto-refresh token when expired
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret

        # Calculate expiration time
        if obtained_at and expires_in:
            self.expires_at = obtained_at + timedelta(seconds=expires_in)
        else:
            self.expires_at = None

        self.auto_refresh = auto_refresh

    @property
    def headers(self) -> dict[str, str]:
        """
        Get authorization headers.

        Returns:
            Headers dict with Authorization header
        """
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    def is_expired(self) -> bool:
        """
        Check if token is expired.

        Returns:
            True if token is expired, False otherwise
        """
        if not self.expires_at:
            return False

        return datetime.now() >= self.expires_at

    async def refresh_if_expired(self) -> None:
        """
        Refresh token if expired.

        Requires refresh_token, client_id, and client_secret.
        """
        if self.auto_refresh and self.is_expired():
            if not self.refresh_token:
                raise RuntimeError("Cannot refresh: no refresh token")

            await self._refresh()

    async def _refresh(self) -> None:
        """
        Refresh the access token.

        Calls Notion's OAuth token endpoint.
        """
        import httpx

        response = await httpx.AsyncClient().post(
            "https://api.notion.com/v1/oauth/token",
            json={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        )

        if response.status_code != 200:
            raise OAuthError(f"Token refresh failed: {response.text}")

        data = response.json()

        # Update tokens
        self.access_token = data["access_token"]
        if "refresh_token" in data:
            self.refresh_token = data["refresh_token"]

        # Update expiration
        if "expires_in" in data:
            self.expires_at = datetime.now() + timedelta(
                seconds=data["expires_in"]
            )

    def __repr__(self) -> str:
        """Secure string representation."""
        token_preview = f"{self.access_token[:10]}...{self.access_token[-4:]}"
        return f"OAuthToken({token_preview})"
```

#### OAuth Helper Class

```python
class OAuthHelper:
    """
    Helper for OAuth 2.0 flow.

    Not part of V1 core, but useful reference for implementation.
    """

    OAUTH_AUTHORIZE_URL = "https://api.notion.com/v1/oauth/authorize"
    OAUTH_TOKEN_URL = "https://api.notion.com/v1/oauth/token"

    @staticmethod
    def get_authorization_url(
        client_id: str,
        redirect_uri: str,
        *,
        state: str | None = None,
        response_type: str = "code"
    ) -> str:
        """
        Build OAuth authorization URL.

        Args:
            client_id: OAuth client ID
            redirect_uri: Redirect URI after authorization
            state: Optional state parameter for security
            response_type: Response type (default: "code")

        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": client_id,
            "response_type": response_type,
            "owner": "user",
            "redirect_uri": redirect_uri
        }

        if state:
            params["state"] = state

        query_string = "&".join(
            f"{k}={v}" for k, v in params.items()
        )

        return f"{OAUTH_AUTHORIZE_URL}?{query_string}"

    @staticmethod
    async def exchange_code_for_token(
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> OAuthToken:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from redirect
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: Must match authorization redirect_uri

        Returns:
            OAuthToken with access token

        Raises:
            OAuthError: If token exchange fails
        """
        import httpx

        response = await httpx.AsyncClient().post(
            OAuthHelper.OAUTH_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret
            }
        )

        if response.status_code != 200:
            raise OAuthError(
                f"Token exchange failed: {response.text}"
            )

        data = response.json()

        return OAuthToken(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            obtained_at=datetime.now(),
            expires_in=data.get("expires_in"),
            client_id=client_id,
            client_secret=client_secret
        )
```

### Using OAuth

#### Manual Token Exchange

```python
from better_notion.api import NotionAPI, OAuthToken

# After receiving callback from Notion with authorization code
token = await OAuthHelper.exchange_code_for_token(
    code=auth_code,
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="https://yourapp.com/callback"
)

# Initialize API with OAuth token
api = NotionAPI(auth=token)
```

#### With Auto-Refresh

```python
# Create token with auto-refresh
token = OAuthToken(
    access_token=access_token,
    refresh_token=refresh_token,
    client_id=client_id,
    client_secret=client_secret,
    auto_refresh=True  # Automatically refresh when expired
)

# Initialize API
api = NotionAPI(auth=token)

# Token will auto-refresh before first request if expired
page = await api.pages.retrieve(page_id)
```

## Authentication in NotionAPI

### Initialization

```python
class NotionAPI:
    """
    Low-level Notion API client.

    Accepts both BearerAuth and OAuthToken.
    """

    def __init__(
        self,
        auth: str | BearerAuth | OAuthToken,
        *,
        api_version: str = "2025-09-03",
        **kwargs
    ):
        """
        Initialize API client.

        Args:
            auth: Authentication (token string, BearerAuth, or OAuthToken)
            api_version: Notion API version
            **kwargs: Additional configuration
        """
        # Convert string to BearerAuth
        if isinstance(auth, str):
            auth = BearerAuth(auth)

        self.auth = auth
        self.api_version = api_version

        # Initialize HTTP client
        self._http = HTTPClient(**kwargs)

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> dict:
        """
        Make authenticated API request.

        Handles:
        - OAuth token refresh (if applicable)
        - Adding auth headers
        - Adding Notion-Version header
        """
        # Auto-refresh OAuth token if needed
        if isinstance(self.auth, OAuthToken):
            await self.auth.refresh_if_expired()

        # Build headers
        headers = self.auth.headers.copy()
        headers["Notion-Version"] = self.api_version

        # Merge with custom headers
        if "headers" in kwargs:
            headers.update(kwargs["headers"])

        kwargs["headers"] = headers

        # Make request
        return await self._http.request(method, path, **kwargs)
```

### Usage Examples

```python
# Bearer token (string)
api1 = NotionAPI(auth="secret_...")

# Bearer token (object)
api2 = NotionAPI(auth=BearerAuth("secret_..."))

# OAuth token
api3 = NotionAPI(auth=oauth_token)
```

## Authentication Errors

### Invalid Token

```python
try:
    api = NotionAPI(auth="invalid_token")
    await api.pages.retrieve(page_id)
except UnauthorizedError as e:
    print(f"Authentication failed: {e}")
    # Status: 401
    # Check token format and integration capabilities
```

### Expired OAuth Token

```python
# Without auto-refresh
token = OAuthToken(
    access_token=expired_token,
    auto_refresh=False
)

api = NotionAPI(auth=token)

try:
    await api.pages.retrieve(page_id)
except UnauthorizedError:
    print("Token expired, refresh required")
    # Need to manually refresh token

# With auto-refresh
token = OAuthToken(
    access_token=expired_token,
    refresh_token=refresh_token,
    client_id=client_id,
    client_secret=client_secret,
    auto_refresh=True  # Handles this automatically
)

api = NotionAPI(auth=token)
page = await api.pages.retrieve(page_id)  # Works!
```

### Missing Capabilities

```python
# Integration lacks required capability
api = NotionAPI(auth="secret_...")

try:
    await api.users.list()  # Requires user info capability
except ForbiddenError as e:
    print(f"Missing capability: {e}")
    # Status: 403
    # Enable capability in integration settings
```

## Security Best Practices

### 1. Never Commit Tokens

```python
# BAD - Don't do this
TOKEN = "secret_abc123..."  # Committed to git

# GOOD - Use environment variables
import os
TOKEN = os.getenv("NOTION_TOKEN")
```

### 2. Use Environment Variables

```python
import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Use environment variable
api = NotionAPI(auth=os.getenv("NOTION_TOKEN"))
```

### 3. Token Validation

```python
# Validate token format before use
try:
    auth = BearerAuth(token)
except ValueError as e:
    print(f"Invalid token: {e}")
    # Don't proceed with API calls
```

### 4. Secure Token Storage

```python
# For OAuth tokens
import keyring

# Store in system keyring
keyring.set_password(
    "notion_integration",
    "access_token",
    access_token
)

# Retrieve
token = keyring.get_password(
    "notion_integration",
    "access_token"
)
```

### 5. Token Rotation

```python
# For production, consider token rotation
# Not currently supported by Notion API
# But good to plan for if/when available
```

## Migration Guide

### From Bot Token to OAuth

```python
# Before: Bot token
api = NotionAPI(auth="secret_...")

# After: OAuth token
token = await OAuthHelper.exchange_code_for_token(...)
api = NotionAPI(auth=token)

# No other code changes needed!
```

## Testing Authentication

### Mock Authentication

```python
from unittest.mock import patch

def test_api_call():
    # Mock authentication
    with patch.object(NotionAPI, '_request') as mock:
        mock.return_value = {"id": "page_id"}
        api = NotionAPI(auth="test_token")

        result = await api.pages.retrieve("page_id")

        assert result["id"] == "page_id"

        # Verify auth headers were added
        call_args = mock.call_args
        headers = call_args.kwargs.get("headers", {})

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
```

## Related Documentation

- [Overview](./overview.md) - Low-level API overview
- [HTTP Client](./http-client.md) - HTTP layer
- [Error Handling](./error-handling.md) - Authentication errors
- [Testing](./testing.md) - Testing authenticated requests

## Next Steps

1. Choose authentication method based on use case
2. Set up environment variables for tokens
3. Implement token validation
4. Configure token refresh for OAuth (if applicable)
