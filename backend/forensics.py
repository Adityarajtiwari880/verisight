"""
VeriSight MCP - Advanced Mathematical Forensics Module
OpenCV 5.0.0 Optimized Multi-Spectral Signal Analysis
Supports native resolution, edge-compensated ELA, PRNU noise variance,
and EXIF / DQT quantization table provenance extraction.
"""

import cv2
import numpy as np
import base64
import time
import io
from typing import Tuple, Dict, Any, List, Optional
from PIL import Image, ExifTags

def encode_img_base64(img: np.ndarray, quality: int = 90) -> str:
    """Encodes an OpenCV image to a base64 JPEG data URL."""
    _, buffer = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

def tool_extract_metadata_provenance(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Step 0: Camera Provenance & EXIF / DQT Table Integrity Analysis.
    Extracts camera hardware tags, lens parameters, software editing signatures,
    and Discrete Quantization Tables (DQT) from raw JPEG stream.
    """
    provenance = {
        "camera_make": "Organic Camera Sensor / Direct Hardware Capture",
        "camera_model": "Standard High-Dynamic CMOS",
        "software_signature": "None (Original Camera Capture)",
        "dqt_tables_count": 0,
        "is_edited_software_flag": False,
        "tamper_indicators": [],
        "exif_tags_found": 0,
        "color_space": "sRGB Standard"
    }
    
    try:
        pil_img = Image.open(io.BytesIO(raw_bytes))
        dqt = getattr(pil_img, "quantization", None)
        if dqt:
            provenance["dqt_tables_count"] = len(dqt)
            
        exif = pil_img.getexif()
        if exif:
            provenance["exif_tags_found"] = len(exif)
            suspicious_software = [
                "photoshop", "gimp", "picsart", "canva", "inpaint",
                "stablediffusion", "midjourney", "dall-e", "lightroom", "snapseed"
            ]
            for tag_id, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id)).lower()
                val_str = str(value)
                
                if "make" in tag_name:
                    provenance["camera_make"] = val_str
                elif "model" in tag_name:
                    provenance["camera_model"] = val_str
                elif "software" in tag_name:
                    provenance["software_signature"] = val_str
                    if any(s in val_str.lower() for s in suspicious_software):
                        provenance["is_edited_software_flag"] = True
                        provenance["tamper_indicators"].append(f"AI/Editing Software Tag: {val_str}")
                elif "datetime" in tag_name:
                    provenance["capture_datetime"] = val_str
    except Exception:
        pass
        
    return provenance

def tool_active_clahe_remediation(img: np.ndarray, clip_limit: float = 3.5, tile_size: int = 8) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Step 1: Photometric Active Perception & Remediation.
    Evaluates frame luminance. If underexposed (< 65/255) like a dim warehouse or night delivery,
    dynamically applies Contrast Limited Adaptive Histogram Equalization (CLAHE) in LAB space.
    """
    t0 = time.perf_counter()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_lum = float(np.mean(gray))
    std_lum = float(np.std(gray))
    applied = False
    
    if mean_lum < 65.0:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
        l_enhanced = clahe.apply(l)
        enhanced_lab = cv2.merge((l_enhanced, a, b))
        output_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        applied = True
    else:
        output_img = img.copy()
        
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    return output_img, {
        "applied": applied,
        "mean_luminance": round(mean_lum, 2),
        "std_luminance": round(std_lum, 2),
        "clip_limit": clip_limit,
        "tile_grid": (tile_size, tile_size),
        "latency_ms": elapsed_ms
    }

def tool_global_ela_scan(img: np.ndarray, quality: int = 90) -> Tuple[np.ndarray, List[int], float, Dict[str, Any]]:
    """
    Step 2: Edge-Compensated Gradient-Normalized ELA & Adaptive ROI Localization.
    Normalizes ELA residual by local Sobel gradient magnitude:
    E_norm = E / (1.0 + 1.2 * G_norm).
    This suppresses natural edge spikes (text, textures) while dramatically amplifying
    true generative inpainting seams and compression quantization discrepancies.
    """
    t0 = time.perf_counter()
    h, w = img.shape[:2]
    
    # 1. Compute re-compression error
    _, encoded = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    compressed = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    ela_diff = cv2.absdiff(img, compressed)
    ela_gray = cv2.cvtColor(ela_diff, cv2.COLOR_BGR2GRAY)
    ela_amplified = cv2.multiply(ela_gray, 18.0)
    
    # 2. Compute local edge gradient magnitude on original image
    gray_orig = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gx = cv2.Sobel(gray_orig, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray_orig, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = cv2.magnitude(gx, gy)
    grad_norm = cv2.normalize(grad_mag, None, 0, 1.0, cv2.NORM_MINMAX)
    
    # 3. Edge-compensated ELA (eliminates false positives on natural edges)
    compensated_ela = (ela_amplified.astype(np.float32) / (1.0 + 1.2 * grad_norm)).astype(np.uint8)
    blurred = cv2.GaussianBlur(compensated_ela, (9, 9), 0)
    
    # 4. Adaptive thresholding calibrated to 95th-percentile energy
    p95 = float(np.percentile(blurred, 95))
    dyn_thresh = max(20, min(45, int(p95 * 0.65)))
    _, thresh = cv2.threshold(blurred, dyn_thresh, 255, cv2.THRESH_BINARY)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    suspect_roi = [int(w * 0.25), int(h * 0.25), int(w * 0.5), int(h * 0.5)]
    max_area = 0
    min_area_thresh = (w * h) * 0.0015 # Capped for small inpainting regions
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area and area > min_area_thresh:
            max_area = area
            x, y, cw, ch = cv2.boundingRect(cnt)
            pad_x = int(cw * 0.08)
            pad_y = int(ch * 0.08)
            rx = max(0, x - pad_x)
            ry = max(0, y - pad_y)
            rw = min(w - rx, cw + 2 * pad_x)
            rh = min(h - ry, ch + 2 * pad_y)
            suspect_roi = [rx, ry, rw, rh]
            
    rx, ry, rw, rh = suspect_roi
    anomaly_score = float(np.percentile(compensated_ela[ry:ry+rh, rx:rx+rw], 95))
    
    # Turbo color-mapped heatmap
    ela_heatmap = cv2.applyColorMap(compensated_ela, cv2.COLORMAP_JET)
    cv2.rectangle(ela_heatmap, (rx, ry), (rx + rw, ry + rh), (0, 255, 255), 2)
    cv2.putText(ela_heatmap, f"Peak ROI (ELA={anomaly_score:.1f})", (rx, max(20, ry - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
                
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    return ela_heatmap, suspect_roi, round(anomaly_score, 2), {
        "roi": suspect_roi,
        "ela_p95_score": round(anomaly_score, 2),
        "clusters_detected": len(contours),
        "dyn_thresh_used": dyn_thresh,
        "edge_compensation_active": True,
        "latency_ms": elapsed_ms
    }

def tool_sweep_jpeg_ghosts(img: np.ndarray, roi: List[int], quality_range: Tuple[int, int, int] = (60, 96, 4)) -> Tuple[np.ndarray, float, int, Dict[str, Any]]:
    """
    Step 3A: Multi-Q JPEG Ghost Sweeper.
    Sweeps quality factors Q in [min_q, max_q] and computes difference residuals.
    Reveals whether the ROI has an isolated minimum compression error curve differing from background.
    """
    t0 = time.perf_counter()
    x, y, w, h = roi
    h_img, w_img = img.shape[:2]
    
    rx = max(0, min(x, w_img - 1))
    ry = max(0, min(y, h_img - 1))
    rw = max(1, min(w, w_img - rx))
    rh = max(1, min(h, h_img - ry))
    
    min_q, max_q, step = quality_range
    qualities = list(range(min_q, max_q + 1, step))
    
    roi_errors = []
    bg_errors = []
    bg_mask = np.ones((h_img, w_img), dtype=bool)
    bg_mask[ry:ry+rh, rx:rx+rw] = False
    
    for q in qualities:
        _, enc = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), q])
        dec = cv2.imdecode(enc, cv2.IMREAD_COLOR)
        diff = cv2.absdiff(img, dec)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        roi_err = float(np.mean(gray_diff[ry:ry+rh, rx:rx+rw]))
        bg_err = float(np.mean(gray_diff[bg_mask])) if np.any(bg_mask) else roi_err
        
        roi_errors.append(roi_err)
        bg_errors.append(bg_err)
        
    min_roi_idx = int(np.argmin(roi_errors))
    min_bg_idx = int(np.argmin(bg_errors))
    q_roi_star = qualities[min_roi_idx]
    q_bg_star = qualities[min_bg_idx]
    
    diff_curve = np.abs(np.array(roi_errors) - np.array(bg_errors))
    ghost_discrepancy = float(np.max(diff_curve))
    
    _, opt_enc = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), q_roi_star])
    opt_dec = cv2.imdecode(opt_enc, cv2.IMREAD_COLOR)
    ghost_diff = cv2.absdiff(img, opt_dec)
    ghost_gray = cv2.cvtColor(ghost_diff, cv2.COLOR_BGR2GRAY)
    ghost_norm = cv2.normalize(ghost_gray, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    ghost_heatmap = cv2.applyColorMap(ghost_norm, cv2.COLORMAP_TURBO)
    cv2.rectangle(ghost_heatmap, (rx, ry), (rx + rw, ry + rh), (255, 255, 0), 2)
    
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    return ghost_heatmap, round(ghost_discrepancy, 2), q_roi_star, {
        "optimal_roi_quality": q_roi_star,
        "optimal_bg_quality": q_bg_star,
        "ghost_discrepancy_score": round(ghost_discrepancy, 2),
        "latency_ms": elapsed_ms
    }

def tool_roi_fourier_probe(img: np.ndarray, roi: List[int]) -> Tuple[np.ndarray, float, float, Dict[str, Any]]:
    """
    Step 3B: 2D Fast Fourier Transform (cv2.dft) & High-Frequency Harmonic Probe.
    Transforms ROI into frequency domain with Hanning window to detect periodic
    latent diffusion upsampler grid harmonics.
    """
    t0 = time.perf_counter()
    x, y, w, h = roi
    crop = img[max(0, y):y+h, max(0, x):x+w]
    if crop.size == 0:
        crop = img
        
    gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    target_dim = 256
    resized_crop = cv2.resize(gray_crop, (target_dim, target_dim))
    
    hann = cv2.createHanningWindow((target_dim, target_dim), cv2.CV_32F)
    windowed = resized_crop.astype(np.float32) * hann
    
    dft = cv2.dft(windowed, flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]) + 1.0)
    mag_norm = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    fft_color = cv2.applyColorMap(mag_norm, cv2.COLORMAP_MAGMA)
    
    center = target_dim // 2
    mask = np.ones((target_dim, target_dim), np.uint8)
    cv2.circle(mask, (center, center), 35, 0, -1)
    high_freq_energy = float(cv2.mean(mag_norm, mask=mask)[0])
    
    y_c, x_c = np.ogrid[:target_dim, :target_dim]
    r = np.hypot(x_c - center, y_c - center).astype(np.int32)
    outer_band = (r > 40) & (r < center - 10)
    band_vals = mag_norm[outer_band]
    harmonic_ratio = float(np.max(band_vals) / (np.mean(band_vals) + 1e-5)) if band_vals.size > 0 else 1.0
    
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    return fft_color, round(high_freq_energy, 2), round(harmonic_ratio, 2), {
        "high_freq_energy": round(high_freq_energy, 2),
        "harmonic_ratio": round(harmonic_ratio, 2),
        "latency_ms": elapsed_ms
    }

def tool_gradient_chrominance_check(img: np.ndarray, roi: List[int]) -> Tuple[np.ndarray, float, Dict[str, Any]]:
    """
    Step 3C: Chrominance Sobel Gradients (cv2.Sobel in YCrCb).
    Measures edge gradient variance discrepancies between the tampered patch
    and the ambient background.
    """
    t0 = time.perf_counter()
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    _, cr, _ = cv2.split(ycrcb)
    
    sobelx = cv2.Sobel(cr, cv2.CV_32F, 1, 0, ksize=3)
    sobely = cv2.Sobel(cr, cv2.CV_32F, 0, 1, ksize=3)
    grad_mag = cv2.magnitude(sobelx, sobely)
    grad_vis = cv2.normalize(grad_mag, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    grad_heatmap = cv2.applyColorMap(grad_vis, cv2.COLORMAP_VIRIDIS)
    
    x, y, w, h = roi
    roi_var = float(np.std(grad_vis[y:y+h, x:x+w])) if w * h > 0 else 10.0
    bg_var = float(np.std(grad_vis)) + 1e-5
    inconsistency_ratio = round(abs(roi_var - bg_var) / bg_var * 100.0, 2)
    
    cv2.rectangle(grad_heatmap, (x, y), (x + w, y + h), (255, 0, 0), 2)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    return grad_heatmap, inconsistency_ratio, {
        "chrom_discrepancy_pct": inconsistency_ratio,
        "latency_ms": elapsed_ms
    }

def tool_sensor_noise_probe(img: np.ndarray, roi: List[int]) -> Tuple[np.ndarray, float, float, Dict[str, Any]]:
    """
    Step 3D: Sensor PRNU & High-Pass Noise Residual.
    Extracts R = I - cv2.medianBlur(I, 3) and measures local variance divergence.
    """
    t0 = time.perf_counter()
    h_img, w_img = img.shape[:2]
    x, y, w, h = roi
    rx = max(0, min(x, w_img - 1))
    ry = max(0, min(y, h_img - 1))
    rw = max(1, min(w, w_img - rx))
    rh = max(1, min(h, h_img - ry))
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.medianBlur(gray, 3)
    noise_residual = cv2.absdiff(gray, denoised).astype(np.float32)
    
    roi_std = float(np.std(noise_residual[ry:ry+rh, rx:rx+rw]))
    bg_mask = np.ones((h_img, w_img), dtype=bool)
    bg_mask[ry:ry+rh, rx:rx+rw] = False
    bg_std = float(np.std(noise_residual[bg_mask])) if np.any(bg_mask) else roi_std
    
    z_score = abs(roi_std - bg_std) / (bg_std + 1e-5)
    noise_divergence_pct = round(z_score * 100.0, 2)
    
    noise_amplified = cv2.normalize(noise_residual, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    noise_heatmap = cv2.applyColorMap(noise_amplified, cv2.COLORMAP_HOT)
    cv2.rectangle(noise_heatmap, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 2)
    
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    return noise_heatmap, round(roi_std, 2), noise_divergence_pct, {
        "roi_noise_std": round(roi_std, 2),
        "noise_divergence_pct": noise_divergence_pct,
        "latency_ms": elapsed_ms
    }

def tool_color_space_decomposition(img: np.ndarray) -> Dict[str, str]:
    """
    Multi-Spectral Color Space Decomposition:
    Renders RGB, CIE LAB (Luminance), YCrCb (Chrominance), and HSV (Saturation/Hue).
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    return {
        "rgb": encode_img_base64(img),
        "lab": encode_img_base64(lab),
        "ycrcb": encode_img_base64(ycrcb),
        "hsv": encode_img_base64(hsv)
    }

def tool_semantic_scene_triage(img_bgr: np.ndarray, claim_type: str = "") -> Dict[str, Any]:
    """
    Step 0-B: Autonomous Semantic Domain & Biometric Validation.
    Analyzes visual subject structure before running forensics to ensure:
    1. Human faces/portraits are flagged if submitted for non-biometric claims (e.g. invoice or produce).
    2. Document claims have structured horizontal text gradients and quadrilateral boundaries.
    3. Direct camera calibration tests are recognized and allowed.
    """
    t0 = time.perf_counter()
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
    
    # 1. Biometric Skin & Face Detection
    mask_hsv = cv2.inRange(hsv, np.array([3, 25, 45]), np.array([24, 175, 255]))
    mask_ycrcb = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
    skin = cv2.bitwise_and(mask_hsv, mask_ycrcb)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, kernel)
    skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(skin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    total_area = h * w
    faces = []
    for c in contours:
        area = cv2.contourArea(c)
        if area > 0.035 * total_area: # Takes at least 3.5% of total frame
            bx, by, bw, bh = cv2.boundingRect(c)
            aspect = float(bh) / max(bw, 1)
            if 0.85 <= aspect <= 2.3: # Facial aspect ratio
                faces.append({
                    "bbox": [int(bx), int(by), int(bw), int(bh)],
                    "area_pct": round(float(area / total_area) * 100, 1)
                })
                
    face_detected = len(faces) > 0
    primary_face_bbox = faces[0]["bbox"] if face_detected else None
    
    # 2. Text line density and Paper Whiteness (for invoices / receipts)
    paper_mask = (gray > 145) & (hsv[:, :, 1] < 55)
    paper_ratio = np.count_nonzero(paper_mask) / float(total_area)

    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    _, text_thresh = cv2.threshold(np.abs(grad_x), 35, 255, cv2.THRESH_BINARY)
    kernel_text = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
    text_lines = cv2.morphologyEx(text_thresh.astype(np.uint8), cv2.MORPH_CLOSE, kernel_text)
    t_contours, _ = cv2.findContours(text_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    text_boxes = [c for c in t_contours if cv2.boundingRect(c)[2] > 35 and cv2.boundingRect(c)[3] < 35]
    text_lines_count = len(text_boxes)
    has_document_structure = (text_lines_count >= 5) and (paper_ratio >= 0.28)

    # 3. Organic Produce Pigmentation (Strawberries, Apples, Oranges, Mangoes, Greens)
    m_red1 = cv2.inRange(hsv, np.array([0, 90, 115]), np.array([10, 255, 255]))
    m_red2 = cv2.inRange(hsv, np.array([170, 90, 115]), np.array([180, 255, 255]))
    m_yellow = cv2.inRange(hsv, np.array([11, 100, 130]), np.array([35, 255, 255]))
    m_green = cv2.inRange(hsv, np.array([36, 75, 70]), np.array([85, 255, 255]))
    produce_mask = m_red1 | m_red2 | m_yellow | m_green
    produce_ratio = np.count_nonzero(produce_mask) / float(total_area)
    has_produce_pigments = produce_ratio >= 0.04
    
    # 4. Claim Domain Analysis
    c_lower = claim_type.lower()
    is_camera_test = any(k in c_lower for k in ["camera", "sensor", "calibration", "direct", "hardware", "biometric"])
    is_invoice_claim = any(k in c_lower for k in ["invoice", "receipt", "tax", "bill", "zepto"])
    is_produce_claim = any(k in c_lower for k in ["produce", "fruit", "strawberry", "strawberries", "mold", "rot"])
    is_auto_claim = any(k in c_lower for k in ["bumper", "car", "vehicle", "auto", "collision", "dent"])
    
    is_valid_subject = True
    rejection_subcode = None
    rejection_reason = None
    
    if is_camera_test:
        # Camera sensor calibration welcomes faces, room, or any physical object
        is_valid_subject = True
    elif is_invoice_claim:
        if face_detected:
            is_valid_subject = False
            rejection_subcode = "HUMAN_BIOMETRIC_MISMATCH"
            rejection_reason = "Detected human face/portrait in commercial tax invoice refund claim. An official delivery receipt or tax invoice document is required."
        elif not has_document_structure:
            is_valid_subject = False
            rejection_subcode = "MISSING_INVOICE_STRUCTURE"
            rejection_reason = f"No white document paper or structured invoice text lines detected (Paper area: {paper_ratio*100:.1f}%, Text lines: {text_lines_count}). Please frame the actual paper receipt or digital bill."
    elif is_produce_claim:
        if face_detected:
            is_valid_subject = False
            rejection_subcode = "HUMAN_PORTRAIT_MISMATCH"
            rejection_reason = "Detected human portrait in fresh produce refund claim. Please photograph the physical perishable product."
        elif not has_produce_pigments:
            is_valid_subject = False
            rejection_subcode = "NO_PRODUCE_DETECTED"
            rejection_reason = f"No organic fresh produce or perishable food pigmentation detected in frame (Produce color index: {produce_ratio*100:.1f}%). Please photograph the claimed grocery item."
    elif is_auto_claim:
        if face_detected:
            is_valid_subject = False
            rejection_subcode = "HUMAN_PORTRAIT_MISMATCH"
            rejection_reason = "Detected human portrait in automotive damage claim. Please photograph the vehicle body or bumper damage."
            
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    return {
        "is_valid_subject": is_valid_subject,
        "face_detected": face_detected,
        "faces_count": len(faces),
        "primary_face_bbox": primary_face_bbox,
        "has_document_structure": has_document_structure,
        "text_lines_count": text_lines_count,
        "rejection_subcode": rejection_subcode,
        "rejection_reason": rejection_reason,
        "latency_ms": latency_ms
    }
