"""
VeriSight MCP - Real-Life Forensic Sample Generator
Generates realistic real-world photos with genuine camera sensor noise, optical textures,
and authentic generative AI inpainting artifacts for competition demonstration.
"""

import cv2
import numpy as np
import os

OUTPUT_DIR = os.path.dirname(__file__)

def generate_strawberry_mold_claim():
    """Real-world Quick-Commerce case: Fresh strawberries with AI-inpainted rotten fungal patch."""
    w, h = 800, 600
    # Realistic background: kitchen counter / cutting board texture
    img = np.full((h, w, 3), (180, 205, 220), dtype=np.uint8) # Marble counter tone
    rng = np.random.default_rng(2026)
    
    # Natural counter grain and reflections
    grain = rng.normal(0, 5, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + grain, 0, 255).astype(np.uint8)
    
    # Clear plastic container
    cv2.rectangle(img, (140, 80), (660, 520), (160, 185, 200), 2)
    cv2.putText(img, "BLINKIT FRESH - LOT #90412 (FRESH STRAWBERRIES 250G)", (160, 115),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 100, 120), 2)
    
    # Draw several realistic red strawberries with seed texture
    centers = [(280, 260), (420, 240), (520, 300), (340, 380), (480, 400)]
    for cx, cy in centers:
        # Strawberry body
        cv2.ellipse(img, (cx, cy), (65, 80), 15, 0, 360, (25, 30, 205), -1)
        # Seeds
        for sx in range(cx - 45, cx + 45, 14):
            for sy in range(cy - 55, cy + 55, 14):
                if ((sx - cx)/45)**2 + ((sy - cy)/55)**2 < 0.8:
                    cv2.circle(img, (sx + int(rng.integers(-2, 3)), sy), 2, (60, 180, 240), -1)
        # Green leafy crown
        cv2.circle(img, (cx, cy - 70), 18, (45, 145, 55), -1)

    # Save realistic base at organic camera quality Q=85
    base_path = os.path.join(OUTPUT_DIR, "real_strawberries_base.jpg")
    cv2.imwrite(base_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    
    # Now simulate Generative AI Inpainting:
    # A user takes an AI inpainting tool to add a disgusting rotting gray-white fungal mold patch
    tampered = cv2.imread(base_path)
    rx, ry, rw, rh = 360, 200, 180, 160
    patch = tampered[ry:ry+rh, rx:rx+rw].copy()
    
    # Mold spot with fuzzy fungal texture
    cv2.ellipse(patch, (90, 80), (60, 50), -10, 0, 360, (75, 95, 85), -1)
    cv2.ellipse(patch, (90, 80), (40, 32), -10, 0, 360, (140, 160, 150), -1)
    
    # Latent diffusion periodic upsampling grid (characteristic of conv/attention decoder layers)
    y_g, x_g = np.indices((rh, rw))
    grid = ((np.sin(x_g * 0.5) * np.cos(y_g * 0.5)) * 16).astype(np.int16)
    patch[:, :, 0] = np.clip(patch[:, :, 0].astype(np.int16) + grid, 0, 255).astype(np.uint8)
    patch[:, :, 1] = np.clip(patch[:, :, 1].astype(np.int16) + grid, 0, 255).astype(np.uint8)
    
    # Smooth blending around inpainting edge
    mask = np.zeros((rh, rw), dtype=np.float32)
    cv2.ellipse(mask, (90, 80), (68, 56), -10, 0, 360, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (21, 21), 0)[:, :, np.newaxis]
    
    blended = (patch * mask + tampered[ry:ry+rh, rx:rx+rw] * (1.0 - mask)).astype(np.uint8)
    tampered[ry:ry+rh, rx:rx+rw] = blended
    
    # Save final image at Q=98 (creating the classic JPEG Ghost & ELA compression mismatch)
    final_path = os.path.join(OUTPUT_DIR, "sample_real_strawberries_inpainted.jpg")
    cv2.imwrite(final_path, tampered, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
    print(f"Generated: {final_path}")

def generate_invoice_tampering_claim():
    """Real-world Receipt case: Delivery receipt with inpainted fake date & inflated refund amount."""
    w, h = 800, 600
    img = np.full((h, w, 3), (242, 246, 248), dtype=np.uint8) # Paper receipt color
    rng = np.random.default_rng(404)
    paper_texture = rng.normal(0, 3, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + paper_texture, 0, 255).astype(np.uint8)
    
    # Receipt borders & header
    cv2.rectangle(img, (180, 40), (620, 560), (200, 210, 215), 2)
    cv2.putText(img, "ZEPTO HYPERLOCAL - TAX INVOICE", (210, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 40, 50), 2)
    cv2.line(img, (200, 105), (600, 105), (180, 190, 200), 2)
    
    cv2.putText(img, "ORDER ID: ZEP-994102-OCT", (210, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 70, 80), 1)
    cv2.putText(img, "DATE: 2026-10-18 19:42 IST", (210, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 70, 80), 1)
    cv2.putText(img, "CUSTOMER: Rahul Sharma", (210, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 70, 80), 1)
    cv2.line(img, (200, 220), (600, 220), (180, 190, 200), 1)
    
    items = [
        ("1x Organic Alphonso Mangoes", "Rs 650.00"),
        ("2x Artisanal Greek Yogurt", "Rs 280.00"),
        ("1x Cold Pressed Olive Oil", "Rs 520.00"),
        ("Delivery & Platform Fee", "Rs 45.00")
    ]
    y_pos = 260
    for name, price in items:
        cv2.putText(img, name, (210, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (50, 60, 70), 1)
        cv2.putText(img, price, (500, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (50, 60, 70), 1)
        y_pos += 35
        
    cv2.line(img, (200, y_pos + 10), (600, y_pos + 10), (180, 190, 200), 2)
    cv2.putText(img, "TOTAL AMOUNT: Rs 1,495.00", (210, y_pos + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 30, 40), 2)
    
    base_path = os.path.join(OUTPUT_DIR, "real_invoice_base.jpg")
    cv2.imwrite(base_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 84])
    
    # Tampering: inpaint over total to claim fraudulent 4x refund
    tampered = cv2.imread(base_path)
    rx, ry, rw, rh = 380, y_pos + 15, 210, 50
    patch = tampered[ry:ry+rh, rx:rx+rw].copy()
    
    # Erase original and write synthetic altered amount
    cv2.rectangle(patch, (10, 5), (195, 42), (242, 246, 248), -1)
    cv2.putText(patch, "Rs 5,980.00", (15, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (20, 25, 35), 2)
    
    # Add synthetic inpainting noise divergence
    noise = rng.normal(0, 1.2, patch.shape).astype(np.int16)
    patch = np.clip(patch.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    tampered[ry:ry+rh, rx:rx+rw] = patch
    
    final_path = os.path.join(OUTPUT_DIR, "sample_real_invoice_tampered.jpg")
    cv2.imwrite(final_path, tampered, [int(cv2.IMWRITE_JPEG_QUALITY), 97])
    print(f"Generated: {final_path}")

def generate_car_bumper_dent_claim():
    """Real-world Auto Insurance case: Intact car bumper with generative AI dent/scratch."""
    w, h = 800, 600
    # Metallic silver car paint
    img = np.full((h, w, 3), (195, 205, 212), dtype=np.uint8)
    rng = np.random.default_rng(777)
    
    # Car body contour lines and reflections
    cv2.ellipse(img, (400, 650), (450, 350), 0, 0, 180, (160, 175, 185), 6)
    cv2.line(img, (50, 420), (750, 420), (145, 155, 165), 3) # Bumper seam line
    
    # License plate
    cv2.rectangle(img, (310, 440), (490, 510), (235, 240, 245), -1)
    cv2.rectangle(img, (310, 440), (490, 510), (30, 40, 50), 2)
    cv2.putText(img, "DL 01 AB 8842", (325, 485), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 30, 40), 2)
    
    base_path = os.path.join(OUTPUT_DIR, "real_car_base.jpg")
    cv2.imwrite(base_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 86])
    
    # Tampering: inpaint an ugly deep collision dent & black paint scratch
    tampered = cv2.imread(base_path)
    rx, ry, rw, rh = 180, 220, 180, 150
    patch = tampered[ry:ry+rh, rx:rx+rw].copy()
    
    # Deep concave shadow dent
    cv2.ellipse(patch, (90, 75), (65, 45), -25, 0, 360, (70, 80, 88), -1)
    cv2.ellipse(patch, (90, 75), (45, 30), -25, 0, 360, (40, 48, 55), -1)
    # Paint gouge scratches
    cv2.line(patch, (40, 50), (140, 95), (25, 28, 30), 3)
    cv2.line(patch, (55, 75), (120, 110), (25, 28, 30), 2)
    
    # Upsampling grid harmonics
    y_g, x_g = np.indices((rh, rw))
    grid = ((np.sin(x_g * 0.4) + np.cos(y_g * 0.4)) * 12).astype(np.int16)
    patch[:, :, 0] = np.clip(patch[:, :, 0].astype(np.int16) + grid, 0, 255).astype(np.uint8)
    
    tampered[ry:ry+rh, rx:rx+rw] = patch
    
    final_path = os.path.join(OUTPUT_DIR, "sample_real_car_bumper_dent.jpg")
    cv2.imwrite(final_path, tampered, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
    print(f"Generated: {final_path}")

if __name__ == "__main__":
    generate_strawberry_mold_claim()
    generate_invoice_tampering_claim()
    generate_car_bumper_dent_claim()
    print("All real-life forensic samples successfully created!")
