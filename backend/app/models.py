from pydantic import BaseModel
from typing import Dict, List


class PredictionResponse(BaseModel):
    file_id: str
    original_image: str
    processed_image: str
    predictions: Dict


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
