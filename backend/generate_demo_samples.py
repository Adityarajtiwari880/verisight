import cv2
import numpy as np

# 1. Create a realistic base "Delivery Box" photo with natural camera sensor noise
base = np.full((480, 640, 3), (140, 175, 205), dtype=np.uint8) # Cardboard color
sensor_noise = np.random.normal(0, 4, base.shape).astype(np.int16)
genuine = np.clip(base.astype(np.int16) + sensor_noise, 0, 255).astype(np.uint8)
cv2.rectangle(genuine, (120, 80), (520, 400), (110, 145, 175), 3)
cv2.putText(genuine, "ORDER #4092 - FRESH PRODUCE", (150, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (70, 90, 110), 2)
cv2.imwrite("1_genuine_claim.jpg", genuine, [int(cv2.IMWRITE_JPEG_QUALITY), 88])

# 2. Create an "AI-Tampered Fraud" photo by splicing a high-frequency synthetic patch
tampered = cv2.imread("1_genuine_claim.jpg")
roi_x, roi_y, roi_w, roi_h = 240, 190, 170, 140
patch = tampered[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w].copy()

# Simulate diffusion/inpainting periodic grid artifact + chrominance shift + fake "damage/mold"
cv2.circle(patch, (85, 70), 48, (35, 55, 45), -1)
grid = np.indices((roi_h, roi_w)).sum(axis=0) % 2 * 28
patch[:, :, 2] = np.clip(patch[:, :, 2].astype(np.int16) + grid, 0, 255).astype(np.uint8)
tampered[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w] = patch

# Save at mismatched quality so ELA + 2D DFT + Sobel immediately catch it
cv2.imwrite("2_ai_inpainted_fraud.jpg", tampered, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
print("Created 1_genuine_claim.jpg and 2_ai_inpainted_fraud.jpg!")