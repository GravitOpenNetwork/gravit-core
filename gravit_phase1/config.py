"""Configuration for Phase 1."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    trust_threshold: float = float(os.environ.get("TRUST_THRESHOLD", "0.7"))
    max_reasoning_steps: int = int(os.environ.get("MAX_REASONING_STEPS", "20"))
    enable_adversarial_detection: bool = os.environ.get("ENABLE_ADVERSARIAL", "true").lower() == "true"
