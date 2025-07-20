from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import joblib
import pandas as pd
from propval.shared.config import Settings
from contextlib import asynccontextmanager

# Load configuration
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context: load the trained pipeline on startup."""
    model_path = Path(settings.model_dir) / settings.model_filename
    if not model_path.exists():
        raise RuntimeError(f"Model file not found at {model_path}")
    # Load the pipeline into app state
    app.state.pipeline = joblib.load(model_path)
    yield
    # Shutdown/cleanup logic here if needed

# Instantiate the FastAPI app with the lifespan handler
app = FastAPI(
    title="Property Valuation API",
    description="Expose a trained property valuation pipeline via REST endpoints.",
    lifespan=lifespan,
)

# Pydantic models for request/response validation
class PredictRequest(BaseModel):
    data: list[dict]  # list of feature dictionaries

class PredictResponse(BaseModel):
    predictions: list[float]

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """
    Accept a batch of feature records and return model predictions.
    """
    try:
        df = pd.DataFrame(req.data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid request payload: {e}")

    pipeline = app.state.pipeline
    try:
        preds = pipeline.predict(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {e}")

    return PredictResponse(predictions=preds.tolist())

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}