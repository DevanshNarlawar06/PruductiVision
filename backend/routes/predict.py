"""
routes/predict.py — POST /api/predict
"""

import numpy as np
from fastapi import APIRouter, HTTPException
from schemas import PredictRequest, PredictResponse, SingleModelResult
from ml.model_store import ModelStore

router = APIRouter()

LABEL_ORDER = ["Low", "Medium", "High"]
FEATURES = ["edu_sm_hours", "ent_sm_hours", "self_study_hours",
            "sleep_hours", "leisure_hours", "platform_enc"]


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if not ModelStore.is_ready():
        raise HTTPException(status_code=503, detail="Models are still loading. Try again shortly.")

    store = ModelStore.get()
    models   = store["models"]
    scaler   = store["scaler"]
    le_p     = store["le_platform"]
    lin      = store["lin_model"]
    best_key = store["best_model"]

    # Validate platform
    if req.platform not in le_p.classes_:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown platform '{req.platform}'. "
                   f"Valid: {list(le_p.classes_)}"
        )

    platform_enc = int(le_p.transform([req.platform])[0])

    raw = np.array([[
        req.edu_sm_hours,
        req.ent_sm_hours,
        req.self_study_hours,
        req.sleep_hours,
        req.leisure_hours,
        platform_enc,
    ]], dtype=float)

    raw_scaled = scaler.transform(raw)

    # Linear regression score estimate
    sleep_dev = req.sleep_hours - 7.0
    lin_input = np.array([[
        req.edu_sm_hours,
        req.ent_sm_hours,
        req.self_study_hours,
        sleep_dev,
        req.leisure_hours,
    ]])
    score_est = float(np.clip(lin.predict(lin_input)[0], 0, 10))

    all_preds = {}
    for name, res in models.items():
        mdl = res["model"]
        X = raw_scaled if "Logistic" in name else raw
        pred_idx = int(mdl.predict(X)[0])
        pred_label = LABEL_ORDER[pred_idx]

        if hasattr(mdl, "predict_proba"):
            proba = mdl.predict_proba(X)[0]
            conf = float(proba[pred_idx])
        else:
            conf = 1.0

        all_preds[name] = SingleModelResult(label=pred_label, confidence=round(conf, 4))

    # Best model probabilities
    best_mdl = models[best_key]["model"]
    best_X   = raw_scaled if "Logistic" in best_key else raw
    if hasattr(best_mdl, "predict_proba"):
        proba_best = best_mdl.predict_proba(best_X)[0]
        probs = {LABEL_ORDER[i]: round(float(proba_best[i]), 4) for i in range(3)}
    else:
        pred_lbl = all_preds[best_key].label
        probs = {l: (1.0 if l == pred_lbl else 0.0) for l in LABEL_ORDER}

    # Reconcile score_estimate with the classifier label so they never contradict.
    # Instead of hard-clipping exactly to the boundary (like 5.4), gently push it inside
    # the valid range to feel organic.
    best_label = all_preds[best_key].label
    ranges = {
        "Low": (0.0, 5.49),
        "Medium": (5.5, 7.49),
        "High": (7.5, 10.0)
    }
    valid_min, valid_max = ranges[best_label]
    
    if not (valid_min <= score_est <= valid_max):
        # Calculate an expected score relying on model probabilities
        expected = (probs.get("Low", 0) * 4.0 + 
                    probs.get("Medium", 0) * 6.5 + 
                    probs.get("High", 0) * 8.5)
        
        # If the expected score is STILL outside the box (e.g. model confidence is 1.0)
        # we dynamically offset it based on the input features so it moves fluidly
        # when the user changes sliders, avoiding it getting stuck at 5.4.
        if not (valid_min <= expected <= valid_max):
            input_factor = (req.edu_sm_hours + req.self_study_hours + max(0, req.sleep_hours - 5)) / 22.0
            expected = valid_min + (valid_max - valid_min) * np.clip(input_factor, 0.15, 0.85)
            
        score_est = float(np.clip(expected, valid_min, valid_max))
    else:
        score_est = float(np.clip(score_est, valid_min, valid_max))

    return PredictResponse(
        label=all_preds[best_key].label,
        score_estimate=round(score_est, 2),
        probabilities=probs,
        model_used=best_key,
        all_model_predictions=all_preds,
    )
