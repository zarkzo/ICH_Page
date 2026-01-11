"""
FastAPI Main Application - Multi-Model Support
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import uuid
from app.preprocessing import process_dicom
from app.inference import load_all_models, predict_all_models, load_model
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ICH Detection API - Multi-Model",
    description="AI-powered multilabel ICH detection with three-model comparison",
    version="2.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Global models dictionary
models = {}

# Model configuration
MODEL_PATHS = {
    "model_a": "models/eff2.keras",
    "model_b": "models/conx.keras",
    "model_c": "models/cascade.keras",
}


@app.on_event("startup")
async def startup_event():
    """Load all models at application startup"""
    global models

    # Check if all model files exist
    missing_models = []
    for key, path in MODEL_PATHS.items():
        if not os.path.exists(path):
            missing_models.append(path)

    if missing_models:
        logger.warning(f"Missing model files: {missing_models}")
        logger.warning("Using fallback: loading single model for all three")

        # Fallback: use single model for demonstration
        fallback_path = "models/ich_model.h5"
        if os.path.exists(fallback_path):
            from app.inference import load_model

            single_model = load_model(fallback_path, "Fallback Model")
            models = {
                "model_a": single_model,
                "model_b": single_model,
                "model_c": single_model,
            }
            logger.info("✓ Using single model for all three slots (demo mode)")
        else:
            logger.error("No models available - predictions will fail")
            return
    else:
        # Load all three models
        try:
            models = load_all_models(MODEL_PATHS)
            logger.info("✓ All three models loaded successfully - API ready")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "ICH Detection API - Multi-Model",
        "version": "2.0.0",
        "models": {
            "model_a": "Model A loaded" if "model_a" in models else "Not loaded",
            "model_b": "Model B loaded" if "model_b" in models else "Not loaded",
            "model_c": "Model C loaded" if "model_c" in models else "Not loaded",
        },
        "endpoints": {"health": "/health", "predict": "/predict", "docs": "/docs"},
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": {
            "model_a": "model_a" in models and models["model_a"] is not None,
            "model_b": "model_b" in models and models["model_b"] is not None,
            "model_c": "model_c" in models and models["model_c"] is not None,
        },
        "total_models": len([m for m in models.values() if m is not None]),
    }


@app.post("/predict", tags=["Prediction"])
async def predict_ich(file: UploadFile = File(...)):
    """
    Predict ICH from uploaded DICOM file using all three models

    Returns predictions from Model A, Model B, Model C, and Ensemble
    """
    # Validate models are loaded
    if not models or all(m is None for m in models.values()):
        raise HTTPException(
            status_code=503, detail="Models not loaded - service unavailable"
        )

    # Validate file extension
    if not file.filename.endswith(".dcm"):
        raise HTTPException(
            status_code=400, detail="Only DICOM files (.dcm) are accepted"
        )

    file_id = str(uuid.uuid4())
    dicom_path = f"uploads/{file_id}.dcm"

    logger.info(f"Processing request: file={file.filename}, id={file_id}")

    try:
        # Save uploaded file
        with open(dicom_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File saved: {dicom_path} ({len(content)} bytes)")

        # Process DICOM (unchanged preprocessing pipeline)
        original_img, processed_img, rgb_array = process_dicom(
            dicom_path=dicom_path, output_dir="outputs", file_id=file_id
        )

        # Run inference on all models
        predictions = predict_all_models(models, rgb_array)

        # Clean up uploaded file
        os.remove(dicom_path)
        logger.info(f"Cleaned up: {dicom_path}")

        # Prepare response
        response = {
            "file_id": file_id,
            "original_image": f"/outputs/{file_id}_original.png",
            "processed_image": f"/outputs/{file_id}_processed.png",
            "predictions": predictions,
            "model_info": {
                "model_a": "Model A - Primary",
                "model_b": "Model B - Secondary",
                "model_c": "Model C - Validation",
                "ensemble": "Mean ensemble of all models",
            },
        }

        logger.info(f"Request complete: Multi-model predictions generated")

        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)

        if os.path.exists(dicom_path):
            os.remove(dicom_path)

        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
