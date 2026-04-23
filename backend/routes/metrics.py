"""
routes/metrics.py — GET /api/metrics
Returns model accuracy, CV scores, Pearson correlations, beta values, label distribution.
"""

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from ml.model_store import ModelStore

router = APIRouter()


@router.get("/metrics")
def get_metrics():
    if not ModelStore.is_ready():
        raise HTTPException(status_code=503, detail="Models are still loading.")

    store = ModelStore.get()

    model_metrics = {}
    for name, res in store["models"].items():
        model_metrics[name] = {
            "test_accuracy": round(res["acc"], 4),
            "cv_accuracy":   round(res["cv"], 4),
            "confusion_matrix": res["cm"],
            "classification_report": res["report"],
        }

    return jsonable_encoder(
        {
            "models": model_metrics,
            "pearson": store["pearson"],
            "assumed_betas": store["assumed_betas"],
            "learned_betas": store["learned_betas"],
            "lin_r2": round(store["lin_r2"], 4),
            "lin_intercept": round(store["lin_intercept"], 4),
            "label_dist": store["label_dist"],
            "best_model": store["best_model"],
            "dataset_shape": store["dataset_shape"],
            "features": store["features"],
        }
    )
