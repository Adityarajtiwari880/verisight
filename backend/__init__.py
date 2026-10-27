"""
VeriSight MCP — Autonomous Multi-Spectral Image Forensics Engine
Powered by OpenCV 5 + Model Context Protocol (MCP)
Author: Aditya Raj Tiwari <adityasantosh2026@gmail.com>
License: Apache-2.0
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Union
import numpy as np
import cv2

# Ensure backend root is in sys.path
_current_dir = str(Path(__file__).resolve().parent)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from agent import ForensicAgent, forensic_agent
from forensics import (
    tool_global_ela_scan,
    tool_roi_fourier_probe,
    tool_gradient_chrominance_check,
    tool_sweep_jpeg_ghosts,
    tool_sensor_noise_probe,
    tool_recapture_pad_analysis,
    tool_vehicle_damage_verification,
    tool_semantic_scene_triage,
    tool_perceptual_hash
)

__version__ = "2.2.0"
__author__ = "Aditya Raj Tiwari"
__license__ = "Apache-2.0"

def scan_image(
    image_input: Union[str, np.ndarray, bytes],
    claim_type: str = "Quick-Commerce / Auto Insurance Claim",
    sensitivity: str = "balanced"
) -> Dict[str, Any]:
    """
    Primary 1-line Python SDK entry point for VeriSight multi-spectral forensics.
    
    Args:
        image_input: File path (str), NumPy BGR image array, or raw bytes.
        claim_type: Domain category for semantic subject triage.
        sensitivity: 'conservative', 'balanced', or 'aggressive'.
        
    Returns:
        Dict containing verdict, tamper_probability, ROI coordinates, and multi-spectral metrics.
    """
    raw_bytes = None
    if isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise FileNotFoundError(f"Image not found at path: {image_input}")
        with open(image_input, "rb") as f:
            raw_bytes = f.read()
        img = cv2.imread(image_input, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"OpenCV failed to decode image: {image_input}")
    elif isinstance(image_input, bytes):
        raw_bytes = image_input
        np_arr = np.frombuffer(image_input, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("OpenCV failed to decode byte stream into valid image array.")
    elif isinstance(image_input, np.ndarray):
        img = image_input
    else:
        raise TypeError(f"Unsupported image_input type: {type(image_input)}")

    return forensic_agent.run_investigation(
        img,
        raw_bytes=raw_bytes,
        claim_type=claim_type,
        sensitivity=sensitivity
    )

verify_claim = scan_image

__all__ = [
    "scan_image",
    "verify_claim",
    "forensic_agent",
    "ForensicAgent",
    "__version__"
]
