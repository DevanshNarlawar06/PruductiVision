"""
main.py — FastAPI application entry point
Social Media vs Student Productivity — ML Pipeline v5.0
PICT | SY_09 | DSM CIE-I
"""

import os
import sys
import time

# Ensure backend/ is on the path so relative imports work
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from ml.generate_dataset import generate
from ml.train import train_pipeline
from ml.model_store import ModelStore
from ml.model_artifacts import load_training_result, save_training_result
from routes.predict import router as predict_router
from routes.metrics import router as metrics_router
from routes.plots import router as plots_router

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Generate dataset, train all models, store in singleton — runs once at startup."""
    print("=" * 65)
    print("  Social Media vs Productivity - FastAPI Backend  v5.0")
    print("=" * 65)
    t0 = time.time()

    result = load_training_result(MODELS_DIR, PLOTS_DIR)
    if result is not None:
        print(f"\n[STARTUP] Loaded trained models from {MODELS_DIR}")
    else:
        print("\n[STARTUP] Generating synthetic dataset (N=600, seed=42)...")
        df = generate(n=600, seed=42)
        print(f"[STARTUP] Dataset ready: {df.shape}")

        print("[STARTUP] Training models & generating plots...")
        result = train_pipeline(df, plots_dir=PLOTS_DIR)
        save_training_result(result, MODELS_DIR)
        print(f"[STARTUP] Saved model bundle -> {os.path.join(MODELS_DIR, 'trained_bundle.joblib')}")

    ModelStore.set(result)
    elapsed = time.time() - t0
    print(f"\n[STARTUP] OK  Models ready in {elapsed:.1f}s")
    print(f"[STARTUP]    Best model : {result['best_model']}")
    for name, res in result["models"].items():
        print(f"[STARTUP]    {name:<25} Test={res['acc']*100:.1f}%  CV={res['cv']*100:.1f}%")
    print(f"[STARTUP]    Plots dir -> {PLOTS_DIR}")
    print()

    yield  # app runs here

    print("[SHUTDOWN] Goodbye.")


app = FastAPI(
    title="Social Media vs Student Productivity API",
    description="ML pipeline — Logistic Regression, Decision Tree & Random Forest | PICT SY_09 DSM",
    version="5.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(predict_router, prefix="/api", tags=["Predict"])
app.include_router(metrics_router, prefix="/api", tags=["Metrics"])
app.include_router(plots_router,   prefix="/api", tags=["Plots"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "ready":  ModelStore.is_ready(),
        "version": "5.0.0",
        "project": "Social Media vs Student Productivity | PICT SY_09 DSM CIE-I",
    }


@app.get("/api/health", tags=["Health"])
def health():
    return {"ready": ModelStore.is_ready()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

# Trigger reload again
