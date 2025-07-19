from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # relative  to BASE_DIR, not absolute:
    #Data paths
    train_data: str = "data/train.csv"
    test_data: str = "data/test.csv"

    #add model paths here later 
    