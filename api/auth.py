"""API key authentication (constant-time comparison)."""
import os
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)

# Get API key from environment
EXPECTED_API_KEY = os.environ.get("API_KEY", "dev-key-do-not-use-in-production")


def verify_api_key(api_key: str = Depends(API_KEY_HEADER)) -> str:
    """Verify API key using constant-time comparison."""
    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(api_key, EXPECTED_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )
    return api_key
