"""
Persist trained pipeline to backend/models/ (joblib) so restarts can skip re-training.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import joblib

# Bump if you change train_pipeline outputs or dataset contract
ARTIFACT_SCHEMA = 1
PIPELINE_VERSION = "5.0.0"
EXPECTED_N = 600
EXPECTED_SEED = 42

BUNDLE_NAME = "trained_bundle.joblib"
MANIFEST_NAME = "manifest.json"
# If this plot is missing, we retrain so /api/plots stays consistent
PLOT_SENTINEL = "5_confusion.png"


def _manifest_payload() -> Dict[str, Any]:
    return {
        "pipeline_version": PIPELINE_VERSION,
        "artifact_schema": ARTIFACT_SCHEMA,
        "n_samples": EXPECTED_N,
        "random_seed": EXPECTED_SEED,
    }


def _paths(models_dir: str) -> tuple[str, str]:
    os.makedirs(models_dir, exist_ok=True)
    bundle = os.path.join(models_dir, BUNDLE_NAME)
    manifest = os.path.join(models_dir, MANIFEST_NAME)
    return bundle, manifest


def save_training_result(result: Dict[str, Any], models_dir: str) -> None:
    """Write joblib bundle + manifest after a successful train_pipeline."""
    bundle_path, manifest_path = _paths(models_dir)
    joblib.dump(result, bundle_path, compress=3)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(_manifest_payload(), f, indent=2)


def load_training_result(models_dir: str, plots_dir: str) -> Optional[Dict[str, Any]]:
    """
    Load bundle if manifest matches and plots dir looks populated.
    Returns None if anything is missing, stale, or load fails.
    """
    bundle_path = os.path.join(models_dir, BUNDLE_NAME)
    manifest_path = os.path.join(models_dir, MANIFEST_NAME)
    sentinel = os.path.join(plots_dir, PLOT_SENTINEL)

    if not (os.path.isfile(bundle_path) and os.path.isfile(manifest_path)):
        return None
    if not os.path.isfile(sentinel):
        return None

    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    expected = _manifest_payload()
    for key in expected:
        if manifest.get(key) != expected[key]:
            return None

    try:
        return joblib.load(bundle_path)
    except Exception:
        return None
