"""
DICOM Preprocessing Module
Handles complete medical image processing pipeline
"""

import pydicom
import numpy as np
import cv2
from PIL import Image
import os
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def read_dicom(dicom_path: str) -> Tuple[np.ndarray, dict]:
    """
    Read DICOM file and extract pixel array with metadata

    Args:
        dicom_path: Path to DICOM file

    Returns:
        pixel_array: Raw pixel data as float32
        metadata: Dictionary containing DICOM metadata
    """
    try:
        ds = pydicom.dcmread(dicom_path)
        pixel_array = ds.pixel_array.astype(np.float32)

        # Extract critical metadata
        metadata = {
            "intercept": (
                float(ds.RescaleIntercept) if "RescaleIntercept" in ds else 0.0
            ),
            "slope": float(ds.RescaleSlope) if "RescaleSlope" in ds else 1.0,
            "invert": ds.PhotometricInterpretation == "MONOCHROME1",
        }

        logger.info(
            f"DICOM loaded: shape={pixel_array.shape}, "
            f"intercept={metadata['intercept']}, "
            f"slope={metadata['slope']}, "
            f"invert={metadata['invert']}"
        )

        return pixel_array, metadata

    except Exception as e:
        logger.error(f"Failed to read DICOM: {e}")
        raise


def to_hounsfield_units(
    pixel_array: np.ndarray, intercept: float, slope: float
) -> np.ndarray:
    """
    Convert pixel values to Hounsfield Units (HU)

    Formula: HU = pixel_value * slope + intercept

    Args:
        pixel_array: Raw pixel data
        intercept: DICOM RescaleIntercept
        slope: DICOM RescaleSlope

    Returns:
        Array in Hounsfield Units
    """
    return pixel_array * slope + intercept


def window_wlww_to_01(
    img: np.ndarray, wl: float, ww: float, intercept: float, slope: float, invert: bool
) -> np.ndarray:
    """
    Apply HU windowing and normalize to [0, 1] range

    This is the core function for medical image windowing.
    It converts raw pixels to HU, applies window settings,
    and normalizes for visualization.

    Args:
        img: Original pixel array
        wl: Window Level (center of window)
        ww: Window Width (range of window)
        intercept: DICOM RescaleIntercept
        slope: DICOM RescaleSlope
        invert: Whether to invert (for MONOCHROME1 images)

    Returns:
        Windowed and normalized array in [0, 1]
    """
    # Step 1: Convert to Hounsfield Units
    hu = to_hounsfield_units(img, intercept, slope)

    # Step 2: Calculate window bounds
    lower = wl - (ww / 2.0)
    upper = wl + (ww / 2.0)

    # Step 3: Apply windowing (clip to window range)
    windowed = np.clip(hu, lower, upper)

    # Step 4: Normalize to [0, 1]
    normalized = (windowed - lower) / (upper - lower)

    # Step 5: Invert if MONOCHROME1
    if invert:
        normalized = 1.0 - normalized

    return normalized


def create_rgb_stack(pixel_array: np.ndarray, metadata: dict) -> np.ndarray:
    """
    Create pseudo-RGB image using multi-window HU processing

    This creates a 3-channel image where each channel represents
    a different diagnostic window:
    - Red channel: Blood window (WL=75, WW=215)
    - Green channel: Brain window (WL=40, WW=80)
    - Blue channel: Bone window (WL=600, WW=2800)

    Args:
        pixel_array: Original DICOM pixel data
        metadata: Dictionary with intercept, slope, invert

    Returns:
        RGB array (H, W, 3) in range [0, 1]
    """
    intercept = metadata["intercept"]
    slope = metadata["slope"]
    invert = metadata["invert"]

    # Apply three different HU windows
    blood = window_wlww_to_01(pixel_array, 75, 215, intercept, slope, invert)
    brain = window_wlww_to_01(pixel_array, 40, 80, intercept, slope, invert)
    bone = window_wlww_to_01(pixel_array, 600, 2800, intercept, slope, invert)

    # Stack as RGB (axis=-1 means channels last)
    # Red = Blood, Green = Brain, Blue = Bone
    rgb = np.stack([blood, brain, bone], axis=-1)

    logger.info(
        f"RGB stack created: shape={rgb.shape}, "
        f"min={rgb.min():.3f}, max={rgb.max():.3f}"
    )

    return rgb


def save_original_image(pixel_array: np.ndarray, output_path: str) -> None:
    """
    Save original DICOM image as PNG for visualization

    Args:
        pixel_array: Raw pixel data
        output_path: Where to save the image
    """
    # Normalize to [0, 255] for visualization
    normalized = (pixel_array - pixel_array.min()) / (
        pixel_array.max() - pixel_array.min()
    )
    img_uint8 = (normalized * 255).astype(np.uint8)

    # Save as PNG
    Image.fromarray(img_uint8).save(output_path)
    logger.info(f"Original image saved: {output_path}")


def save_processed_image(rgb_array: np.ndarray, output_path: str) -> None:
    """
    Save processed RGB image as PNG

    Args:
        rgb_array: Processed RGB array in [0, 1]
        output_path: Where to save the image
    """
    # Convert to uint8 for saving
    rgb_uint8 = (rgb_array * 255).astype(np.uint8)

    # Save as PNG
    Image.fromarray(rgb_uint8).save(output_path)
    logger.info(f"Processed image saved: {output_path}")


def process_dicom(
    dicom_path: str, output_dir: str, file_id: str
) -> Tuple[str, str, np.ndarray]:
    """
    Complete DICOM processing pipeline

    This is the main processing function that orchestrates:
    1. Reading DICOM
    2. Saving original image
    3. Creating RGB stack with multi-window processing
    4. Resizing to 256x256
    5. Saving processed image
    6. Returning model-ready array

    Args:
        dicom_path: Path to input DICOM file
        output_dir: Directory for saving processed images
        file_id: Unique identifier for this file

    Returns:
        original_path: Path to saved original image
        processed_path: Path to saved processed RGB image
        rgb_array: Model-ready array (256, 256, 3) float32
    """
    logger.info(f"Processing DICOM: {dicom_path}")

    # Step 1: Read DICOM file
    pixel_array, metadata = read_dicom(dicom_path)

    # Step 2: Save original image
    original_path = os.path.join(output_dir, f"{file_id}_original.png")
    save_original_image(pixel_array, original_path)

    # Step 3: Create RGB stack with multi-window processing
    rgb = create_rgb_stack(pixel_array, metadata)

    # Step 4: Resize to 256x256 (model input size)
    rgb_resized = cv2.resize(rgb, (256, 256), interpolation=cv2.INTER_LINEAR)

    # Step 5: Convert to float32 for model inference
    rgb_float = rgb_resized.astype(np.float32)

    # Step 6: Save processed RGB image
    processed_path = os.path.join(output_dir, f"{file_id}_processed.png")
    save_processed_image(rgb_resized, processed_path)

    logger.info(
        f"Processing complete: original={original_path}, " f"processed={processed_path}"
    )

    return original_path, processed_path, rgb_float
