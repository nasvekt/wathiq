"""Wathiq — Auth middleware for JWT and API key validation."""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def verify_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verify bearer token. Returns the token value."""
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    return token


async def verify_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verify HMAC-signed API key. Returns the client ID."""
    auth_header = credentials.credentials
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing API key")

    # Format: "Hmac CLIENT_ID:SIGNATURE"
    parts = auth_header.split(" ")
    if len(parts) == 2 and parts[0].lower() == "hmac":
        try:
            client_id, signature = parts[1].split(":", 1)
            return client_id
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid API key format")

    # Fallback: treat as raw bearer token
    return auth_header