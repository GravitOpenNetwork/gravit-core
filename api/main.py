"""FastAPI application."""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging

from .auth import verify_api_key
from .schemas import VerificationRequestAPI, VerificationResponseAPI
from .converters import api_request_to_internal, internal_result_to_api
from gravit_phase1 import EpistemicVerifierPhase1, StructuralGate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_structural_gate = StructuralGate()
_verifier = EpistemicVerifierPhase1(structural_gate=_structural_gate)

app = FastAPI(
    title="Gravit Core API",
    description="Epistemic Verification Layer for AI Agents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/v1/verify", response_model=VerificationResponseAPI)
async def verify(
    request: VerificationRequestAPI,
    api_key: str = Depends(verify_api_key)
):
    logger.info(f"Verification request for action: {request.proposed_action}")

    try:
        internal_request = api_request_to_internal(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = _verifier.verify(internal_request)
    response = internal_result_to_api(result)

    logger.info(f"Decision: {response.decision}, trust_score: {response.trust_score}")
    return response
