"""
FastAPI Production REST API for Plant Seedlings Classification.
"""

import io
import time
from typing import Optional, List
from pathlib import Path
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import (
    CLASS_NAMES,
    PLANT_SPECIES_INFO,
    SUPPORTED_ARCHITECTURES,
    BENCHMARK_RESULTS,
)
from src.predict import SeedlingClassifier

app = FastAPI(
    title="🌱 Plant Seedlings Classification API",
    description="REST API for automated plant seedlings classification across 7 CNN architectures.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory model cache
model_instances = {}


def get_cached_classifier(architecture: str) -> SeedlingClassifier:
    arch_key = architecture.strip().lower()
    if arch_key not in model_instances:
        model_instances[arch_key] = SeedlingClassifier(architecture=architecture)
    return model_instances[arch_key]


# --- Pydantic Schemas ---
class HealthResponse(BaseModel):
    status: str
    supported_models: List[str]
    num_classes: int
    timestamp: float


class PredictionItem(BaseModel):
    class_name: str
    scientific_name: str
    confidence: float
    confidence_percent: str
    type: str
    severity: str
    action: str
    description: str


class PredictionResponse(BaseModel):
    architecture_used: str
    prediction: str
    plant_type: str
    confidence_percent: str
    latency_ms: float
    top_k: List[PredictionItem]
    agricultural_advisory: dict


@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
def health_check():
    """Returns service health status and supported models."""
    return {
        "status": "healthy",
        "supported_models": SUPPORTED_ARCHITECTURES,
        "num_classes": len(CLASS_NAMES),
        "timestamp": time.time(),
    }


@app.get("/models")
def list_models():
    """Returns supported CNN architectures and architectural benchmarks."""
    return {
        "architectures": SUPPORTED_ARCHITECTURES,
        "benchmarks": BENCHMARK_RESULTS,
    }


@app.get("/species")
def list_species():
    """Returns database of all 12 target seedling species and agronomic data."""
    return {
        "total_species": len(CLASS_NAMES),
        "species": PLANT_SPECIES_INFO,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_seedling(
    file: UploadFile = File(...),
    architecture: str = Query("ResNet50", description="CNN architecture to use for prediction"),
    top_k: int = Query(3, ge=1, le=12, description="Number of top predictions to return"),
    use_tta: bool = Query(False, description="Enable Test-Time Augmentation"),
):
    """
    Classifies a seedling image and returns species predictions and agricultural guidance.
    """
    if architecture not in SUPPORTED_ARCHITECTURES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid architecture '{architecture}'. Supported: {SUPPORTED_ARCHITECTURES}",
        )

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    start_time = time.time()
    classifier = get_cached_classifier(architecture)
    result = classifier.predict(image, top_k=top_k, use_tta=use_tta)
    latency_ms = (time.time() - start_time) * 1000

    return {
        "architecture_used": architecture,
        "prediction": result["prediction"],
        "plant_type": result["type"],
        "confidence_percent": result["confidence_percent"],
        "latency_ms": round(latency_ms, 2),
        "top_k": result["top_k"],
        "agricultural_advisory": result["agricultural_advisory"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
