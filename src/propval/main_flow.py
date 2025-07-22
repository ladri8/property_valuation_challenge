"""
This python module is the main prefect flow with tasks for: 

1.data loading and validation
2.data preprocessing 
3.model training
4.model evaluation

The main pipeline can be run from command line with:

python -m main_flow

"""

from pathlib import Path
import pandas as pd
import numpy as np
import joblib

import prefect
from prefect import flow, task
from prefect.logging import get_run_logger

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_percentage_error,
    mean_absolute_error)

from .constants import BASE_DIR
from .shared.config import Settings
from .data.data_loader import load_data_csv
from .data.schema_validation import schema, validate_and_log
from .pipelines.build_pipeline import build_pipeline

from typing import Union, Dict


NumericArray = Union[np.ndarray, "pd.Series"]


@task
def load_data(file_path: Path) -> pd.DataFrame:
    return load_data_csv(file_path)

@task
def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    return validate_and_log(df, schema)

@task
def train_model(train_cols: pd.DataFrame, target: pd.Series, settings: Settings):
    pipeline = build_pipeline(settings)
    pipeline.fit(train_cols, target)
    return pipeline

@task
def get_prediction(X_test, model):
    return model.predict(X_test)

@task
def evaluate_model(y_test: NumericArray, predictions: NumericArray) -> Dict[str, float]:
    logger = get_run_logger()
    rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
    mape =  float(mean_absolute_percentage_error(y_test, predictions))
    mae = float(mean_absolute_error(y_test, predictions))

    logger.info(f"Test RMSE : {rmse}")
    logger.info(f"Test MAPE: {mape}")
    logger.info(f"Test MAE : {mae}")

    return {"rmse": rmse, "mape": mape, "mae": mae}

@task
def save_model(pipeline, model_dir: Path, model_filename: str) -> Path:
    model_dir.mkdir(parents=True, exist_ok=True)
    path = model_dir / model_filename
    joblib.dump(pipeline, path)
    #logger.info(f"Model saved to {path}")
    return path

# Main Prefect flow for the entire model pipeline
# Orchestrates the tasks defined above in a logical sequence

@flow(name="property-valuation-train-test-flow")
def main_flow():

    logger = get_run_logger()
    settings = Settings()

    # resolve to full paths once
    TRAIN_PATH = BASE_DIR / settings.train_data
    TEST_PATH  = BASE_DIR / settings.test_data
    
    logger.info("Starting property valuation main flow")

    # Load data
    logger.info("Loading train data.")
    train = load_data(TRAIN_PATH)
    
    logger.info("Loading test data.")
    test = load_data(TEST_PATH)

    logger.info("Data loaded successfully.")
    
    # Validate and log train data
    logger.info("Validating train data. Logging new columns if any.")
    train_valid = validate_data(train)
    
    # Validate and log test data
    logger.info("Validating test data. Logging new columns if any.")
    test_valid = validate_data(test)
    
    logger.info("Data validation complete.")

    # Train data
    logger.info("Fitting model with train data.")

    # Split train
    y_train = train_valid[settings.target]
    X_train = train_valid.drop(columns=settings.target, errors="ignore")
    
    pipeline = train_model(X_train, y_train, settings)

    logger.info("Pipeline fitted successfully.")

    # Make predictions on test data
    logger.info("Making predictions on test data.")
    
    # Split test 
    y_test = test_valid[settings.target]
    X_test = test_valid.drop(columns=settings.target, errors="ignore")

    # Make predictions
    predictions = get_prediction(X_test, pipeline)

    logger.info("Predictions made and saved.")

    # Log metrics
    logger.info("Evaluating model on test data...")
    metrics = evaluate_model(y_test,predictions)
    logger.info(f"Final metrics: {metrics}")
    
    # Save Model Artifact
    logger.info("Saving model to disk.")
    full_model_dir  = BASE_DIR / settings.model_dir
    
    saved_model_path = save_model(
        pipeline,
        full_model_dir,
        settings.model_filename,
    )
    logger.info(f"Model persisted at {saved_model_path}")

if __name__ == "__main__":
    main_flow()