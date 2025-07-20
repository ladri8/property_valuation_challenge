from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List, Dict, Any, Optional


class Settings(BaseSettings):
    # relative  to BASE_DIR, not absolute:
    #Data paths
    train_data: str = "data/train.csv"
    test_data: str = "data/test.csv"

    # Feature configs
    
    # id or id_col (since id is a python keyword is not present in the data provided)
    # this can be made extensible in case other data versins have it
    id_col: Optional[str] = None


    categorical_cols: List[str] = ["type", "sector"]
    target: str = "price"

    # Model hyperparameters
    model_params: Dict[str, Any] = {

        "learning_rate": 0.01,
        "n_estimators": 300,
        "max_depth": 5,
        "loss": "absolute_error",
    }

    # new fields for model persistence
    model_dir: Path = Path("models")   # relative to BASE_DIR
    model_filename: str  = "pipeline.joblib"  
    