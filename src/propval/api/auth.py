from fastapi import Header, HTTPException, Depends
from propval.shared.config import Settings



def verify_api_key(x_api_key: str = Header(...)):
    """Dependency to check if the API key matches."""
    settings = Settings()
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
