"""API key authentication."""
import os
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)
EXPECTED_API_KEY = os.environ.get("API_KEY", "dev-key-do-not-use-in-production")


def verify_api_key(api_key: str = Depends(API_KEY_HEADER)) -> str:
    if not secrets.compare_digest(api_key, EXPECTED_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key
