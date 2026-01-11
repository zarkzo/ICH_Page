"""
Multi-Model Inference Module
Handles loading and inference for three models with ensemble support
"""

import tensorflow as tf
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# ICH classification labels
LABELS = [
    "Any ICH",
    "Intraparenchymal",
    "Intraventricular",
    "Subarachnoid",
    "Subdural",
    "Epidural",
]

THRESHOLD = 0.5


def weighted_bce(y_true, y_pred):
    pos_weight = 3.0
    loss = tf.nn.weighted_cross_entropy_with_logits(
        labels=y_true, logits=tf.math.log(y_pred / (1 - y_pred)), pos_weight=pos_weight
    )
    return tf.reduce_mean(loss)


def load_model(model_path: str, model_name: str = "Model"):
    """
    Load Keras model from .h5 or .keras file

    Args:
        model_path: Path to model file
        model_name: Friendly name for logging

    Returns:
        Loaded Keras model
    """
    try:
        logger.info(f"Loading {model_name} from: {model_path}")
        model = tf.keras.models.load_model(model_path, compile=False)
        logger.info(f"{model_name} loaded successfully")
        logger.info(f"Input shape: {model.input_shape}")
        logger.info(f"Output shape: {model.output_shape}")
        return model
    except Exception as e:
        logger.error(f"Failed to load {model_name}: {e}")
        raise


def load_all_models(model_paths: Dict[str, str]) -> Dict[str, object]:
    """
    Load all three models at startup

    Args:
        model_paths: Dictionary with keys 'model_a', 'model_b', 'model_c'

    Returns:
        Dictionary of loaded models
    """
    models = {}

    for key, path in model_paths.items():
        model_name = key.replace("_", " ").title()
        models[key] = load_model(path, model_name)

    logger.info(f"All {len(models)} models loaded successfully")
    return models


def predict_single_model(model, rgb_array: np.ndarray, model_name: str) -> Dict:
    """
    Run inference on a single model

    Args:
        model: Loaded Keras model
        rgb_array: Preprocessed image (256, 256, 3) float32
        model_name: Model identifier for logging

    Returns:
        Dictionary with predictions and detected labels
    """
    # Add batch dimension
    input_batch = np.expand_dims(rgb_array, axis=0)

    # Run inference
    predictions = model.predict(input_batch, verbose=0)[0]

    # Format results
    results = {"model_name": model_name, "confidences": {}, "detected": []}

    for label, score in zip(LABELS, predictions):
        confidence = float(score) * 100
        results["confidences"][label] = round(confidence, 2)

        if score >= THRESHOLD:
            results["detected"].append(label)

    logger.info(f"{model_name}: {len(results['detected'])} hemorrhages detected")

    return results


def predict_all_models(models: Dict[str, object], rgb_array: np.ndarray) -> Dict:
    """
    Run inference on all three models and compute ensemble

    Args:
        models: Dictionary of loaded models (model_a, model_b, model_c)
        rgb_array: Preprocessed image (256, 256, 3) float32

    Returns:
        Dictionary with all model results and ensemble
    """
    results = {"model_a": None, "model_b": None, "model_c": None, "ensemble": None}

    # Collect raw predictions
    all_predictions = []

    # Run each model
    for key, model in models.items():
        model_name = key.replace("_", " ").title()
        results[key] = predict_single_model(model, rgb_array, model_name)

        # Extract raw prediction values for ensemble
        pred_values = [results[key]["confidences"][label] / 100.0 for label in LABELS]
        all_predictions.append(pred_values)

    # Compute ensemble (mean)
    ensemble_predictions = np.mean(all_predictions, axis=0)

    # Format ensemble results
    results["ensemble"] = {
        "model_name": "Ensemble (Mean)",
        "confidences": {},
        "detected": [],
    }

    for label, score in zip(LABELS, ensemble_predictions):
        confidence = float(score) * 100
        results["ensemble"]["confidences"][label] = round(confidence, 2)

        if score >= THRESHOLD:
            results["ensemble"]["detected"].append(label)

    logger.info(
        f"Ensemble: {len(results['ensemble']['detected'])} hemorrhages detected"
    )

    return results


def compute_voting_ensemble(model_results: List[Dict]) -> Dict:
    """
    Compute ensemble using majority voting (alternative method)

    Args:
        model_results: List of prediction results from each model

    Returns:
        Ensemble result based on voting
    """
    vote_counts = {label: 0 for label in LABELS}
    confidence_sums = {label: 0.0 for label in LABELS}

    # Count votes
    for result in model_results:
        for label in result["detected"]:
            vote_counts[label] += 1
        for label, conf in result["confidences"].items():
            confidence_sums[label] += conf

    # Average confidences
    num_models = len(model_results)
    avg_confidences = {
        label: round(confidence_sums[label] / num_models, 2) for label in LABELS
    }

    # Majority voting (>50% of models)
    detected = [label for label, count in vote_counts.items() if count > num_models / 2]

    return {
        "model_name": "Ensemble (Voting)",
        "confidences": avg_confidences,
        "detected": detected,
    }
