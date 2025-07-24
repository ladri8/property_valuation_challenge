"""
# main.py
This module defines the main entry point for the property valuation API.
It sets up the FastAPI application, defines endpoints, and handles requests.

"""

import logging
from pathlib import Path
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Depends, Header

from propval.api.auth import verify_api_key
from propval.shared.config import Settings

# Configure logging
logger = logging.getLogger("propval.api")
logger.setLevel(logging.INFO)

# Load configuration
settings = Settings()

print(f"[DEBUG] Loaded API key from settings: {settings.api_key}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model pipeline on startup."""
    model_path = Path(settings.model_dir) / settings.model_filename
    print(f"Looking for model at: {model_path}")
    if not model_path.exists():
        raise RuntimeError(f"Model file not found")
    app.state.pipeline = joblib.load(model_path)
    yield

app = FastAPI(
    title="Property Valuation API",
    lifespan=lifespan
)

@app.get("/", include_in_schema=False)
def index():
    return {"message": "Bienvenido/a a la Property Valuation API"}

@app.post("/predict", dependencies=[Depends(verify_api_key)])
def predict(payload: dict, request: Request, x_api_key: str = Header(...)):
    """Return property price predictions for input records."""
    client = request.client.host if request.client else "unknown"
    data = payload.get("data")

    if not data or not isinstance(data, list):
        raise HTTPException(status_code=422, detail="Payload must contain a list under 'data'.")

    logger.info(f"Received request from {client} with {len(data)} records.")

    try:
        df = pd.DataFrame(data)
        logger.info(f"[{client}] input dataframe columns: {df.columns.tolist()}")
        logger.info(f"[{client}] input dataframe preview:\n{df.head()}")
        
        pipeline = app.state.pipeline
        logger.info(f"[{client}] pipeline loaded: {pipeline}")
        preds = pipeline.predict(df)
        logger.info(f"[{client}] predictions successful.")
    
    except Exception as e:
        logger.error(f"[{client}] prediction failed: {e}")
        raise HTTPException(status_code=400, detail=f"Prediction error: {e}")

    logger.info(f"[{client}] returning {len(preds)} predictions.")
    return {"predicted_property_value": float(preds.tolist()[0])}

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


