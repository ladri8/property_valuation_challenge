"""
# build_pipeline.py
# This module constructs a machine learning pipeline using sklearn.
# It includes preprocessing steps and a model, ready for training and prediction.   
"""

from category_encoders import TargetEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor


from propval.shared.config import Settings

def build_pipeline(settings: Settings) -> Pipeline:
    """
    Construct and return a sklearn Pipeline:

    - "preprocessor": applies TargetEncoder to settings.categorical_cols
    - "model":       a GradientBoostingRegressor(**settings.model_params)

    Parameters

    settings : Settings
        Pydantic Settings object carrying `categorical_cols` and `model_params`.

    Returns
    -------
    sklearn.pipeline.Pipeline
        Ready for .fit(X, y) and .predict(X).
    """
    # Preprocessing
    cat_encoder = TargetEncoder()
    preprocessor = ColumnTransformer(
        [("categorical", cat_encoder, settings.categorical_cols)]
    )

    # Estimator
    model = GradientBoostingRegressor(**settings.model_params) #this could be made more scalable later

    # Build and return the pipeline
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model",       model),
    ])