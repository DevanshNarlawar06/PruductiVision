"""
schemas.py — Pydantic request/response models
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict


PLATFORM_OPTIONS = ["YouTube", "Instagram", "Snapchat", "LinkedIn", "Discord"]


class PredictRequest(BaseModel):
    edu_sm_hours: float = Field(..., ge=0.0, le=7.0,
        description="Educational social media hours per day (YouTube, LinkedIn, Discord)")
    ent_sm_hours: float = Field(..., ge=0.0, le=7.0,
        description="Entertainment social media hours per day (Instagram, Snapchat)")
    self_study_hours: float = Field(..., ge=0.2, le=6.0,
        description="Self-study / homework hours per day")
    sleep_hours: float = Field(..., ge=4.5, le=9.5,
        description="Sleep hours per night")
    leisure_hours: float = Field(..., ge=0.1, le=2.5,
        description="Leisure / recreation hours per day")
    platform: str = Field(...,
        description="Primary social media platform: YouTube | Instagram | Snapchat | LinkedIn | Discord")

    @field_validator("platform")
    @classmethod
    def platform_must_be_known(cls, v: str) -> str:
        if v not in PLATFORM_OPTIONS:
            raise ValueError(
                f"platform must be one of {PLATFORM_OPTIONS}, got {v!r}"
            )
        return v


class SingleModelResult(BaseModel):
    label: str
    confidence: float


class PredictResponse(BaseModel):
    label: str
    score_estimate: float
    probabilities: Dict[str, float]
    model_used: str
    all_model_predictions: Dict[str, SingleModelResult]


class MetricsResponse(BaseModel):
    models: dict
    pearson: dict
    assumed_betas: dict
    learned_betas: dict
    lin_r2: float
    lin_intercept: float
    label_dist: dict
    best_model: str
    dataset_shape: list
    features: list
