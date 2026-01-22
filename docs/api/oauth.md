# OAuth and Authentication

## Introduction

Notion uses **OAuth 2.0** for authentication in public integrations. This allows third-party services to request access to user workspaces securely.

## OAuth Flow Overview

The OAuth 2.0 authorization code flow consists of these steps:

1. **User authorization** - User approves your integration via Notion's authorization page
2. **Authorization code** - Notion redirects back with an authorization code
3. **Token exchange** - Exchange the code for an access token
4. **Access API** - Use the access token to make authenticated requests
5. **Refresh token** (optional) - Use refresh token to get new access tokens

```
┌─────────┐                    ┌─────────┐                    ┌──────────┐
│  User   │                    │  Your   │                    │  Notion  │
│ Browser │                    │  App    │                    │   API    │
└────┬────┘                    └────┬────┘                    └────┬─────┘
     │                              │                              │
     │  1. Click "Connect"          │                              │
     ├─────────────────────────────>│                              │
     │                              │                              │
     │  2. Redirect to Notion       │                              │
     │                              ├─────────────────────────────>│
     │                              │                              │
     │  3. User approves            │                              │
     │                              │<─────────────────────────────┤
     │  4. Redirect with code       │                              │
     │<─────────────────────────────┤                              │
     │                              │                              │
     │  5. Send code to app         │                              │
     ├─────────────────────────────>│                              │
     │                              │                              │
     │                              │  6. Exchange code for token  │
     │                              ├─────────────────────────────>│
     │                              │                              │
     │                              │  7. Return access token      │
     │                              │<─────────────────────────────┤
     │                              │                              │
     │  8. Store token, ready!      │                              │
     │<─────────────────────────────┤                              │
     │                              │                              │
```

## Prerequisites

Before implementing OAuth:

1. **Create an integration** at https://www.notion.so/my-integrations
2. **Configure OAuth settings**:
   - OAuth Domain & URIs (redirect URLs)
   - Capabilities (what data your integration needs)
3. **Get your credentials**:
   - **Client ID** - Public identifier for your integration
   - **Client Secret** - Secret used for token exchange

## Authorization URL

To start the OAuth flow, redirect the user to Notion's authorization page:

```
https://api.notion.com/v1/authorize
  ?owner=user
  &client_id={CLIENT_ID}
  &redirect_uri={REDIRECT_URI}
  &response_type=code
  &state={RANDOM_STATE}
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `owner` | Yes | Must be `"user"` |
| `client_id` | Yes | Your integration's OAuth Client ID |
| `redirect_uri` | Yes | Where Notion redirects after approval |
| `response_type` | Yes | Must be `"code"` |
| `state` | Recommended | Random string to prevent CSRF attacks |

### State Parameter

Always use a unique, random `state` parameter to prevent CSRF attacks:

```python
import secrets
import hashlib

def generate_state(user_session_id: str) -> str:
    """Generate a secure state parameter."""
    raw = f"{user_session_id}:{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()

# In your authorization handler
state = generate_state(session.id)
auth_url = f"https://api.notion.com/v1/authorize?...&state={state}"
# Store state in session for verification
session['oauth_state'] = state
```

## Create a Token

Exchange an authorization code for an access token.

```
POST https://api.notion.com/v1/oauth/token
```

### Request Headers

| Header | Value | Description |
|--------|-------|-------------|
| `Authorization` | `Basic {BASE64_ENCODED_CREDENTIALS}` | HTTP Basic Auth with client_id:client_secret |
| `Content-Type` | `application/json` | Request body format |
| `Notion-Version` | `2022-06-28` (or latest) | API version |

### Basic Auth Encoding

Encode your client ID and secret:

```python
import base64

def encode_credentials(client_id: str, client_secret: str) -> str:
    """Encode client credentials for Basic Auth."""
    credentials = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"

# Example
auth_header = encode_credentials(
    client_id="your-client-id",
    client_secret="your-client-secret"
)
# Result: "Basic bWFuYWdlLWV4YW1wbGUtY2xpZW50..."
```

### Request Body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `grant_type` | Yes | string | Must be `"authorization_code"` |
| `code` | Yes | string | Authorization code from redirect |
| `redirect_uri` | Conditional | string | Required if multiple redirect URIs or redirect_uri param was in auth URL |

**Redirect URI Requirements:**
- **Required** if:
  - Multiple redirect URIs configured in integration settings, OR
  - `redirect_uri` query parameter was in authorization URL
- **Not allowed** if:
  - Single redirect URI configured AND no `redirect_uri` in auth URL

In most cases, this field is **required**.

### Request Example

```bash
curl --location --request POST 'https://api.notion.com/v1/oauth/token' \
  --header 'Authorization: Basic '"$BASE64_ENCODED_ID_AND_SECRET"'' \
  --header 'Content-Type: application/json' \
  --header 'Notion-Version: 2022-06-28' \
  --data '{
    "grant_type": "authorization_code",
    "code": "e202e8c9-0990-40af-855f-ff8f872b1ec6",
    "redirect_uri": "https://www.my-integration-endpoint.dev/callback",
    "external_account": {
      "key": "A83823453409384",
      "name": "Notion - team@makenotion.com"
    }
  }'
```

### Response

```json
{
  "access_token": "secret_e202e8c9-0990-40af-855f-ff8f872b1ec6c",
  "bot_id": "b3414d65-1224-5ty7-6ffr-cc9d8773drt601288f",
  "duplicated_template_id": null,
  "owner": {
    "workspace": true
  },
  "workspace_icon": "https://website.domain/images/image.png",
  "workspace_id": "j565j4d7x3-2882-61bs-564a-jj9d9ui-c36hxfr7x",
  "workspace_name": "Ada's Notion Workspace"
}
```

**Note:** If your access token starts with `secret_`, it's an internal integration token. Public integration tokens typically start with a different prefix or have no prefix.

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | Bearer token for API requests |
| `bot_id` | string (UUID) | Bot user ID for this integration |
| `duplicated_template_id` | string \| null | Template ID if workspace duplicated |
| `owner` | object | Owner information |
| `owner.workspace` | boolean | `true` if owned by workspace |
| `owner.user` | object | User info if owned by user |
| `workspace_icon` | string | Workspace icon URL |
| `workspace_id` | string (UUID) | Workspace ID |
| `workspace_name` | string | Workspace display name |

## Refresh a Token

Use a refresh token to obtain a new access token without requiring user interaction.

```
POST https://api.notion.com/v1/oauth/token
```

### Request Body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `grant_type` | Yes | string | Must be `"refresh_token"` |
| `refresh_token` | Yes | string | Refresh token from original token response |

### Request Example

```bash
curl --location --request POST 'https://api.notion.com/v1/oauth/token' \
  --header 'Authorization: Basic '"$BASE64_ENCODED_ID_AND_SECRET"'' \
  --header 'Content-Type: application/json' \
  --header 'Notion-Version: 2022-06-28' \
  --data '{
    "grant_type": "refresh_token",
    "refresh_token": "nrt_4991090011501Ejc6Xn4sHguI7jZIN449mKe9PRhpMfNK"
  }'
```

### Response

```json
{
  "access_token": "ntn_e4502e8c9-1990-60af-845f-ff8f872b1ec6c",
  "refresh_token": "ntn_1202e8c9-0920-412f-055f-8f872ba1df26c",
  "bot_id": "b3414d659-1224-5ty7-6ffr-cc9d8773drt601288f",
  "duplicated_template_id": null,
  "owner": {
    "workspace": true
  },
  "workspace_icon": "https://website.domain/images/image.png",
  "workspace_id": "j565j4d7-2882-61bs-564a-jj9d9ui-c36hxfr7x",
  "workspace_name": "Ada's Notion Workspace"
}
```

**Important:** When refreshing a token:
- A new `access_token` is issued
- A new `refresh_token` is issued
- **Old tokens are invalidated** - Update your storage immediately

## Introspect Token

Check if an access token is active and get its metadata.

```
POST https://api.notion.com/v1/oauth/introspect
```

### Request Body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `token` | Yes | string | Access token to introspect |

### Request Example

```bash
curl --location --request POST 'https://api.notion.com/v1/oauth/introspect' \
  --header 'Authorization: Basic '"$BASE64_ENCODED_ID_AND_SECRET"'' \
  --header 'Content-Type: application/json' \
  --data '{
    "token": "secret_e202e8c9-0990-40af-855f-ff8f872b1ec6c"
  }'
```

### Response

```json
{
  "active": true,
  "scope": "read_content insert_content update_content",
  "iat": 1727554061083
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `active` | boolean | `true` if token is valid, `false` if revoked/expired |
| `scope` | string | Space-separated list of granted scopes |
| `iat` | integer | Token issuance timestamp (Unix milliseconds) |

**Note:** Notion currently doesn't enforce scopes in public integrations, but this field may be used in the future.

## Revoke Token

Invalidate an access token immediately.

```
POST https://api.notion.com/v1/oauth/revoke
```

### Request Body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `token` | Yes | string | Access token to revoke |

### Request Example

```bash
curl --location --request POST 'https://api.notion.com/v1/oauth/revoke' \
  --header 'Authorization: Basic '"$BASE64_ENCODED_ID_AND_SECRET"'' \
  --header 'Content-Type: application/json' \
  --data '{
    "token": "secret_e202e8c9-0990-40af-855f-ff8f872b1ec6"
  }'
```

### Response

Successful revocation returns an empty response with `200 OK` status.

## SDK Architecture

### OAuth Client

```python
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import base64
import secrets
import hashlib

@dataclass
class TokenOwner:
    """Token owner information."""
    workspace: bool = False
    user: Optional[dict] = None

@dataclass
class TokenResponse:
    """OAuth token response."""
    access_token: str
    bot_id: UUID
    owner: TokenOwner
    workspace_id: UUID
    workspace_name: str
    workspace_icon: Optional[str] = None
    duplicated_template_id: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None  # Seconds until expiration

    @property
    def is_workspace_owned(self) -> bool:
        """Check if token is owned by workspace."""
        return self.owner.workspace

@dataclass
class TokenIntrospection:
    """Token introspection response."""
    active: bool
    scope: str
    issued_at: int  # Unix timestamp in milliseconds

    @property
    def scopes(self) -> List[str]:
        """Get scopes as a list."""
        return self.scope.split() if self.scope else []

@dataclass
class StoredToken:
    """Stored token with metadata."""
    access_token: str
    refresh_token: Optional[str]
    bot_id: UUID
    workspace_id: UUID
    workspace_name: str
    user_id: str  # Your app's user ID
    created_at: datetime
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at

class OAuthClient:
    """OAuth 2.0 client for Notion integration."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        api_version: str = "2022-06-28"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.api_version = api_version

    def get_authorization_url(
        self,
        state: str,
        owner: str = "user"
    ) -> str:
        """
        Generate OAuth authorization URL.

        Args:
            state: Random state string for CSRF protection
            owner: Owner type (default: "user")

        Returns:
            Authorization URL
        """
        from urllib.parse import urlencode

        params = {
            "owner": owner,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state
        }

        base_url = "https://api.notion.com/v1/authorize"
        return f"{base_url}?{urlencode(params)}"

    def generate_state(self, user_session_id: str) -> str:
        """
        Generate a secure state parameter.

        Args:
            user_session_id: User's session ID

        Returns:
            State string
        """
        raw = f"{user_session_id}:{secrets.token_hex(16)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _encode_credentials(self) -> str:
        """Encode client credentials for Basic Auth."""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def exchange_code(
        self,
        code: str,
        redirect_uri: Optional[str] = None
    ) -> TokenResponse:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Redirect URI (optional, uses default if not provided)

        Returns:
            TokenResponse with access token

        Raises:
            OAuthError: If token exchange fails
        """
        import httpx

        uri = redirect_uri or self.redirect_uri

        payload = {
            "grant_type": "authorization_code",
            "code": code
        }

        # Only include redirect_uri if needed
        if self._should_include_redirect_uri():
            payload["redirect_uri"] = uri

        headers = {
            "Authorization": self._encode_credentials(),
            "Content-Type": "application/json",
            "Notion-Version": self.api_version
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.notion.com/v1/oauth/token",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            return TokenResponse(
                access_token=data["access_token"],
                bot_id=UUID(data["bot_id"]),
                owner=TokenOwner(
                    workspace=data["owner"].get("workspace", False),
                    user=data["owner"].get("user")
                ),
                workspace_id=UUID(data["workspace_id"]),
                workspace_name=data["workspace_name"],
                workspace_icon=data.get("workspace_icon"),
                duplicated_template_id=data.get("duplicated_template_id"),
                refresh_token=data.get("refresh_token")
            )

    async def refresh_token(
        self,
        refresh_token: str
    ) -> TokenResponse:
        """
        Refresh an access token.

        Args:
            refresh_token: Refresh token from previous token response

        Returns:
            New TokenResponse with new tokens

        Raises:
            OAuthError: If refresh fails
        """
        import httpx

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        headers = {
            "Authorization": self._encode_credentials(),
            "Content-Type": "application/json",
            "Notion-Version": self.api_version
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.notion.com/v1/oauth/token",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            return TokenResponse(
                access_token=data["access_token"],
                bot_id=UUID(data["bot_id"]),
                owner=TokenOwner(
                    workspace=data["owner"].get("workspace", False),
                    user=data["owner"].get("user")
                ),
                workspace_id=UUID(data["workspace_id"]),
                workspace_name=data["workspace_name"],
                workspace_icon=data.get("workspace_icon"),
                duplicated_template_id=data.get("duplicated_template_id"),
                refresh_token=data["refresh_token"]  # NEW refresh token
            )

    async def introspect(
        self,
        token: str
    ) -> TokenIntrospection:
        """
        Introspect an access token.

        Args:
            token: Access token to introspect

        Returns:
            TokenIntrospection with token status

        Raises:
            OAuthError: If introspection fails
        """
        import httpx

        payload = {"token": token}

        headers = {
            "Authorization": self._encode_credentials(),
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.notion.com/v1/oauth/introspect",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            return TokenIntrospection(
                active=data["active"],
                scope=data.get("scope", ""),
                issued_at=data.get("iat", 0)
            )

    async def revoke(self, token: str) -> bool:
        """
        Revoke an access token.

        Args:
            token: Access token to revoke

        Returns:
            True if successful

        Raises:
            OAuthError: If revocation fails
        """
        import httpx

        payload = {"token": token}

        headers = {
            "Authorization": self._encode_credentials(),
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.notion.com/v1/oauth/revoke",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return True

    def _should_include_redirect_uri(self) -> bool:
        """
        Determine if redirect_uri should be included in token request.

        Returns:
            True if redirect_uri should be included
        """
        # Check if redirect_uri query param was in auth URL
        # This would typically be stored during authorization flow
        # For now, default to True (most common case)
        return True
```

### Token Storage

```python
from abc import ABC, abstractmethod

class TokenStore(ABC):
    """Abstract token storage interface."""

    @abstractmethod
    async def save_token(self, user_id: str, token: TokenResponse) -> StoredToken:
        """Save a token for a user."""
        pass

    @abstractmethod
    async def get_token(self, user_id: str) -> Optional[StoredToken]:
        """Get a token for a user."""
        pass

    @abstractmethod
    async def delete_token(self, user_id: str) -> bool:
        """Delete a token for a user."""
        pass

class InMemoryTokenStore(TokenStore):
    """Simple in-memory token store (for development)."""

    def __init__(self):
        self._tokens: dict[str, StoredToken] = {}

    async def save_token(self, user_id: str, token: TokenResponse) -> StoredToken:
        """Save a token for a user."""
        stored = StoredToken(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            bot_id=token.bot_id,
            workspace_id=token.workspace_id,
            workspace_name=token.workspace_name,
            user_id=user_id,
            created_at=datetime.now()
        )
        self._tokens[user_id] = stored
        return stored

    async def get_token(self, user_id: str) -> Optional[StoredToken]:
        """Get a token for a user."""
        return self._tokens.get(user_id)

    async def delete_token(self, user_id: str) -> bool:
        """Delete a token for a user."""
        if user_id in self._tokens:
            del self._tokens[user_id]
            return True
        return False

# Database token store example (PostgreSQL)
class DatabaseTokenStore(TokenStore):
    """PostgreSQL token store implementation."""

    def __init__(self, db_pool):
        self._pool = db_pool

    async def save_token(self, user_id: str, token: TokenResponse) -> StoredToken:
        """Save a token to database."""
        query = """
            INSERT INTO notion_tokens
                (user_id, access_token, refresh_token, bot_id, workspace_id, workspace_name, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (user_id) DO UPDATE
            SET
                access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                bot_id = EXCLUDED.bot_id,
                workspace_id = EXCLUDED.workspace_id,
                workspace_name = EXCLUDED.workspace_name,
                created_at = EXCLUDED.created_at
            RETURNING *
        """

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                user_id,
                token.access_token,
                token.refresh_token,
                str(token.bot_id),
                str(token.workspace_id),
                token.workspace_name,
                datetime.now()
            )

            return StoredToken(
                access_token=row["access_token"],
                refresh_token=row["refresh_token"],
                bot_id=UUID(row["bot_id"]),
                workspace_id=UUID(row["workspace_id"]),
                workspace_name=row["workspace_name"],
                user_id=row["user_id"],
                created_at=row["created_at"]
            )

    async def get_token(self, user_id: str) -> Optional[StoredToken]:
        """Get a token from database."""
        query = "SELECT * FROM notion_tokens WHERE user_id = $1"

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
            if not row:
                return None

            return StoredToken(
                access_token=row["access_token"],
                refresh_token=row["refresh_token"],
                bot_id=UUID(row["bot_id"]),
                workspace_id=UUID(row["workspace_id"]),
                workspace_name=row["workspace_name"],
                user_id=row["user_id"],
                created_at=row["created_at"]
            )

    async def delete_token(self, user_id: str) -> bool:
        """Delete a token from database."""
        query = "DELETE FROM notion_tokens WHERE user_id = $1"

        async with self._pool.acquire() as conn:
            result = await conn.execute(query, user_id)
            return result == "DELETE 1"
```

### Usage Example: Web Application

```python
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
import better_notion

app = FastAPI()

# OAuth client
oauth = OAuthClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    redirect_uri="https://your-app.com/oauth/callback"
)

# Token store (use database in production)
token_store = InMemoryTokenStore()

@app.get("/connect")
async def connect_notion(request: Request):
    """Start OAuth flow."""
    # Generate state parameter
    state = oauth.generate_state(user_session_id="user-session-id")
    request.session["oauth_state"] = state
    request.session["user_id"] = "user-123"  # Your user's ID

    # Redirect to Notion
    auth_url = oauth.get_authorization_url(state=state)
    return RedirectResponse(auth_url)

@app.get("/oauth/callback")
async def oauth_callback(
    request: Request,
    code: str,
    state: str,
    error: str = None
):
    """Handle OAuth callback."""
    if error:
        return {"error": error}

    # Verify state parameter
    saved_state = request.session.get("oauth_state")
    if state != saved_state:
        return {"error": "Invalid state parameter"}

    # Exchange code for token
    token = await oauth.exchange_code(code)

    # Save token for user
    user_id = request.session.get("user_id")
    stored = await token_store.save_token(user_id, token)

    return {"success": True, "workspace": token.workspace_name}

@app.post("/disconnect")
async def disconnect_notion(request: Request):
    """Revoke token and disconnect."""
    user_id = request.session.get("user_id")
    token = await token_store.get_token(user_id)

    if token:
        # Revoke token
        await oauth.revoke(token.access_token)
        # Delete from store
        await token_store.delete_token(user_id)

    return {"success": True}
```

### Usage Example: Token Refresh

```python
async def get_valid_token(user_id: str) -> str:
    """
    Get a valid access token, refreshing if necessary.

    Args:
        user_id: Your app's user ID

    Returns:
        Valid access token
    """
    stored = await token_store.get_token(user_id)

    if not stored:
        raise ValueError("No token found for user")

    # Check if token needs refresh
    introspection = await oauth.introspect(stored.access_token)

    if not introspection.active:
        if not stored.refresh_token:
            raise ValueError("Token expired and no refresh token available")

        # Refresh the token
        new_token = await oauth.refresh_token(stored.refresh_token)

        # Save new token
        await token_store.save_token(user_id, new_token)

        return new_token.access_token

    return stored.access_token

# Use in API client
async def get_user_pages(user_id: str):
    """Get pages for a user."""
    access_token = await get_valid_token(user_id)

    client = better_notion.Client(auth=access_token)
    return await client.search(filter={"property": "object", "value": "page"})
```

## Error Handling

```python
class OAuthError(Exception):
    """OAuth error with details."""

    def __init__(self, message: str, code: str = None, details: dict = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}

    @classmethod
    def from_response(cls, response: dict) -> "OAuthError":
        """Create error from API response."""
        return cls(
            message=response.get("message", "OAuth error"),
            code=response.get("code"),
            details=response
        )

# Common error codes
class InvalidGrantError(OAuthError):
    """Authorization code invalid or expired."""
    pass

class InvalidClientError(OAuthError):
    """Client authentication failed."""
    pass

class InvalidRequestError(OAuthError):
    """Request missing required parameter."""
    pass

# Usage with error handling
try:
    token = await oauth.exchange_code(code)
except httpx.HTTPStatusError as e:
    response = e.response.json()
    if response.get("error") == "invalid_grant":
        raise InvalidGrantError("Code expired, please try again")
    raise OAuthError.from_response(response)
```

## Best Practices

### 1. State Parameter

Always use a unique state parameter and verify it:

```python
# Good - generate secure state
state = oauth.generate_state(session.id)
session["oauth_state"] = state

# Good - verify on callback
if state != session.pop("oauth_state"):
    raise ValueError("Invalid state")

# Bad - no state verification
# Allows CSRF attacks
```

### 2. Token Storage Security

```python
# Good - encrypt tokens in database
encrypted_token = encrypt(token.access_token, encryption_key)

# Good - use HTTPS only
secure_cookie = True
httponly = True
samesite = "lax"

# Bad - store tokens in plain text
# Bad - store tokens in localStorage (XSS vulnerable)
```

### 3. Token Refresh

```python
# Good - proactive refresh before expiration
if stored.expires_at and stored.expires_at < datetime.now() + timedelta(minutes=5):
    token = await oauth.refresh_token(stored.refresh_token)

# Good - handle refresh failures
try:
    token = await oauth.refresh_token(stored.refresh_token)
except OAuthError:
    # User needs to re-authenticate
    await token_store.delete_token(user_id)
    redirect_to_login()
```

### 4. PKCE (Recommended for Public Clients)

For mobile apps or single-page apps (no client secret):

```python
import base64
import hashlib
import secrets

def generate_pkce() -> tuple[str, str, str]:
    """Generate PKCE code verifier and challenge."""
    # Code verifier (random 43-128 chars)
    verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode().rstrip("=")

    # Code challenge (SHA256 hash)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip("=")

    return verifier, challenge

# Use in auth URL
verifier, challenge = generate_pkce()
auth_url = f"...&code_challenge={challenge}&code_challenge_method=S256"

# Send verifier in token exchange
token = await oauth.exchange_code(code, code_verifier=verifier)
```

### 5. Redirect URI Validation

Always validate redirect URIs:

```python
ALLOWED_REDIRECT_URIS = [
    "https://your-app.com/oauth/callback",
    "https://staging.your-app.com/oauth/callback"
]

def validate_redirect_uri(uri: str) -> bool:
    """Validate redirect URI against whitelist."""
    return uri in ALLOWED_REDIRECT_URIS

# Before redirecting to Notion
if not validate_redirect_uri(redirect_uri):
    raise ValueError("Invalid redirect URI")
```

## Related Documentation

- [Authorization Guide](https://developers.notion.com/docs/authorization) - Complete OAuth guide
- [Link Preview Integrations](https://developers.notion.com/docs/link-preview-introduction) - OAuth for Link Previews
- [API Structure](./api-structure.md) - Authentication in API requests
- [Users](./users.md) - User objects and bot information

---

**Next:** See [Search](./search.md) for information about searching across content.
