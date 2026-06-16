"""FastAPI application for Gravit Core Phase 1."""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging

from .auth import verify_api_key
from .schemas import VerificationRequestAPI, VerificationResponseAPI
from .converters import api_request_to_internal, internal_result_to_api
from gravit_phase1 import EpistemicVerifierPhase1, StructuralGate

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize verifier (singleton)
_structural_gate = StructuralGate()
_verifier = EpistemicVerifierPhase1(structural_gate=_structural_gate)

# Create FastAPI app
app = FastAPI(
    title="Gravit Core API",
    description="Epistemic Verification Layer for AI Agents. No self-attestation. LLM cannot override.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/v1/verify", response_model=VerificationResponseAPI, tags=["Verification"])
async def verify(
    request: VerificationRequestAPI,
    api_key: str = Depends(verify_api_key)
):
    """Verify an agent's intended action.

    IMPORTANT: The request schema has NO field for agent self-reported confidence.
    Trust is computed from the reasoning chain structure, not claimed.
    """
    logger.info(f"Verification request received for action: {request.proposed_action}")

    # Convert API request to internal dataclasses
    try:
        internal_request = api_request_to_internal(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )

    # Run verification
    result = _verifier.verify(internal_request)

    # Convert to API response
    response = internal_result_to_api(result)

    logger.info(f"Verification complete: decision={response.decision}, trust_score={response.trust_score}")

    return response
