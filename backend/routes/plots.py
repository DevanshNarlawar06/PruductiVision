"""
routes/plots.py — GET /api/plots/list  &  GET /api/plots/{name}
Lists all available plots and serves individual PNGs.
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

PLOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plots")

PLOT_META = {
    "0_budget_sm_split":            "24-Hour Time Budget & SM Split",
    "1_pearson_heatmap":            "Pearson Correlation Heatmap",
    "2_eda":                        "EDA — Feature Relationships with Productivity",
    "2b_inter_feature_correlations":"Inter-Feature Correlations (Time Competition & Late-Night Effects)",
    "3_beta_comparison":            "Assumed vs Learned Beta Coefficients",
    "4_train_test_class_check":     "Train/Test Class Proportion Check",
    "5_confusion":                  "Confusion Matrices (All 3 Models)",
    "6_model_comparison":           "Model Comparison — Test vs CV Accuracy",
    "7_feature_importances":        "Random Forest Feature Importances",
    "8_decision_tree":              "Decision Tree (max_depth=6)",
    "sanity_score_hist":            "Productivity Score Distribution (Sanity Check)",
}


@router.get("/plots/list")
def list_plots():
    return [
        {"key": k, "label": v, "url": f"/api/plots/{k}"}
        for k, v in PLOT_META.items()
    ]


@router.get("/plots/{name}")
def get_plot(name: str):
    if name not in PLOT_META:
        raise HTTPException(status_code=404, detail=f"Plot '{name}' not found.")
    path = os.path.join(PLOTS_DIR, f"{name}.png")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"Plot file not yet generated.")
    return FileResponse(path, media_type="image/png")
