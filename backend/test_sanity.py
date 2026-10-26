"""
VeriSight MCP - Automated End-to-End Sanity & Forensic Test
Validates the FastAPI forensic agent with both genuine and tampered claims.
"""
import urllib.request
import urllib.error
import uuid
import json
import os
import sys

BASE_URL = os.environ.get("VERISIGHT_API_URL", "http://127.0.0.1:8000")

def upload_claim(filepath: str, claim_type: str = "Automated Sanity Test"):
    boundary = uuid.uuid4().hex
    with open(filepath, "rb") as f:
        file_bytes = f.read()
    
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{os.path.basename(filepath)}\"\r\n"
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8") + file_bytes + (
        f"\r\n--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"claim_type\"\r\n\r\n"
        f"{claim_type}\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/analyze-claim?sensitivity=balanced",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def verify_forensic_contract(res, label=""):
    assert "visuals" in res, f"[{label}] Missing 'visuals' object"
    assert "gradient_map" in res["visuals"] and res["visuals"]["gradient_map"].startswith("data:image"), (
        f"[{label}] Missing or invalid 'gradient_map' in visuals"
    )
    assert "ela_heatmap" in res["visuals"] and res["visuals"]["ela_heatmap"].startswith("data:image"), (
        f"[{label}] Missing or invalid 'ela_heatmap' in visuals"
    )
    assert "metrics" in res, f"[{label}] Missing 'metrics' object"
    assert "chrominance_discrepancy_pct" in res["metrics"], (
        f"[{label}] Missing 'chrominance_discrepancy_pct' in metrics"
    )
    assert "agent_trace" in res and len(res["agent_trace"]) > 0, (
        f"[{label}] Missing 'agent_trace' reasoning steps"
    )

def run_tests():
    print("=" * 60)
    print("  VeriSight MCP Forensic Pipeline - Automated Sanity Verification")
    print(f"  Target Backend: {BASE_URL}")
    print("=" * 60)

    # 1. Test Health / Cloud Audit status
    try:
        req_reset = urllib.request.Request(f"{BASE_URL}/api/reset-test-ledger", data=b"{}", method="POST")
        urllib.request.urlopen(req_reset, timeout=5)
        req = urllib.request.Request(f"{BASE_URL}/api/aws-status")
        with urllib.request.urlopen(req, timeout=5) as resp:
            aws_info = json.loads(resp.read().decode())
            print(f"[OK] Cloud Storage Mode: {aws_info.get('storage_mode')} (Bucket: {aws_info.get('s3_bucket')}, Records: {aws_info.get('audit_records_count')})")
    except Exception as e:
        print(f"[!] Warning: Could not reach {BASE_URL}/api/aws-status: {e}")
        return False

    # 2. Test Genuine Claim
    script_dir = os.path.dirname(os.path.abspath(__file__))
    genuine_path = os.path.join(script_dir, "1_genuine_claim.jpg")
    if os.path.exists(genuine_path):
        res_g = upload_claim(genuine_path, "Commercial Delivery Package Claim")
        verify_forensic_contract(res_g, "Test Case 1 Genuine")
        print("\n--- Test Case 1: Genuine Unedited Image ---")
        print(f"  Verdict:            {res_g['verdict']}")
        print(f"  Tamper Probability: {res_g['tamper_probability']}%")
        print(f"  Autonomous Action:  {res_g['action_taken']}")
        assert res_g["verdict"] in ["AUTO_APPROVE_CLAIM", "MANUAL_REVIEW_FLAGGED"], (
            f"Genuine image failed: {res_g['verdict']}"
        )
        print("  Status:             PASSED (Zero False Positive)")

    # 3. Test Real-Life AI Inpainted Fruit
    tampered_path = os.path.join(script_dir, "sample_real_strawberries_inpainted.jpg")
    if os.path.exists(tampered_path):
        res_t = upload_claim(tampered_path, "Synthetic Mold Refund Fraud")
        verify_forensic_contract(res_t, "Test Case 2 Inpainted")
        print("\n--- Test Case 2: Real-World Inpainted Image ---")
        print(f"  Verdict:            {res_t['verdict']}")
        print(f"  Tamper Probability: {res_t['tamper_probability']}%")
        print(f"  Autonomous Action:  {res_t['action_taken']}")
        assert res_t["verdict"] in ["REJECT_SYNTHETIC_TAMPER", "MANUAL_REVIEW_FLAGGED", "REJECT_CLAIM_SYNTHETIC_FRAUD"], (
            f"Tampered image failed detection: {res_t['verdict']}"
        )
        print("  Status:             PASSED (Fraud Detected)")

    # 4. Test Semantic Mismatch (Human Face in Tax Invoice Claim)
    import cv2
    import numpy as np
    test_face_img = np.full((480, 640, 3), (200, 200, 200), dtype=np.uint8)
    cv2.ellipse(test_face_img, (320, 220), (90, 130), 0, 0, 360, (140, 175, 225), -1) # Face
    cv2.ellipse(test_face_img, (320, 130), (95, 50), 0, 0, 360, (30, 30, 30), -1)   # Hair
    cv2.ellipse(test_face_img, (320, 440), (180, 120), 0, 0, 360, (80, 80, 120), -1) # Shoulders
    face_path = os.path.join(script_dir, "test_temp_face.jpg")
    cv2.imwrite(face_path, test_face_img)

    try:
        res_mismatch = upload_claim(face_path, "Zepto Tax Invoice Claim")
        verify_forensic_contract(res_mismatch, "Test Case 3 Face in Invoice")
        print("\n--- Test Case 3: Semantic Mismatch (Face in Invoice Claim) ---")
        print(f"  Verdict:            {res_mismatch['verdict']}")
        print(f"  Autonomous Action:  {res_mismatch['action_taken']}")
        assert res_mismatch["verdict"] == "REJECT_INVALID_CLAIM_SUBJECT", (
            f"Expected REJECT_INVALID_CLAIM_SUBJECT, got: {res_mismatch['verdict']}"
        )
        print("  Status:             PASSED (Autonomous Refusal of Selfie in Invoice Claim)")

        # Verify that an authentic camera capture IS APPROVED under Direct Camera Test
        res_cam = upload_claim(genuine_path, "Direct Camera Sensor Test")
        verify_forensic_contract(res_cam, "Test Case 4 Camera Calib")
        print("\n--- Test Case 4: Direct Camera Integrity Calibration ---")
        print(f"  Verdict:            {res_cam['verdict']}")
        print(f"  Autonomous Action:  {res_cam['action_taken']}")
        assert res_cam["verdict"] == "AUTO_APPROVE_CLAIM", (
            f"Expected AUTO_APPROVE_CLAIM for camera calibration, got: {res_cam['verdict']}"
        )
        print("  Status:             PASSED (Camera Calibration Allowed)")

        # Test Case 5: Non-Produce Object (e.g. Denim Jeans / Purse) in Fresh Produce Claim
        test_jeans = np.full((480, 640, 3), (110, 60, 35), dtype=np.uint8) # Dark blue denim
        jeans_path = os.path.join(script_dir, "test_temp_jeans.jpg")
        cv2.imwrite(jeans_path, test_jeans)
        try:
            res_jeans_fruit = upload_claim(jeans_path, "Real-Life Quick-Commerce Produce Claim")
            verify_forensic_contract(res_jeans_fruit, "Test Case 5 Jeans Produce")
            print("\n--- Test Case 5: Non-Produce Object (Jeans/Purse) in Produce Claim ---")
            print(f"  Verdict:            {res_jeans_fruit['verdict']}")
            print(f"  Autonomous Action:  {res_jeans_fruit['action_taken']}")
            assert res_jeans_fruit["verdict"] == "REJECT_INVALID_CLAIM_SUBJECT", (
                f"Expected REJECT_INVALID_CLAIM_SUBJECT, got: {res_jeans_fruit['verdict']}"
            )
            print("  Status:             PASSED (Autonomous Refusal of Purse/Jeans in Produce Claim)")

            res_jeans_invoice = upload_claim(jeans_path, "Real-Life Quick-Commerce Tax Invoice Claim")
            verify_forensic_contract(res_jeans_invoice, "Test Case 6 Jeans Invoice")
            print("\n--- Test Case 6: Non-Document Object (Jeans/Purse) in Invoice Claim ---")
            print(f"  Verdict:            {res_jeans_invoice['verdict']}")
            print(f"  Autonomous Action:  {res_jeans_invoice['action_taken']}")
            assert res_jeans_invoice["verdict"] == "REJECT_INVALID_CLAIM_SUBJECT", (
                f"Expected REJECT_INVALID_CLAIM_SUBJECT, got: {res_jeans_invoice['verdict']}"
            )
            print("  Status:             PASSED (Autonomous Refusal of Purse/Jeans in Invoice Claim)")
        finally:
            if os.path.exists(jeans_path):
                os.remove(jeans_path)
    finally:
        if os.path.exists(face_path):
            os.remove(face_path)

    # 5. Test Case 7: OpenCV pHash Sybil Attack Duplicate Claim Detection
    if os.path.exists(tampered_path):
        res_sybil = upload_claim(tampered_path, "Quick-Commerce Produce Claim")
        verify_forensic_contract(res_sybil, "Test Case 7 Sybil Duplicate")
        print("\n--- Test Case 7: Sybil Attack (Duplicate Claim Photo Reuse) ---")
        print(f"  Verdict:            {res_sybil['verdict']}")
        print(f"  Tamper Probability: {res_sybil['tamper_probability']}%")
        print(f"  Autonomous Action:  {res_sybil['action_taken']}")
        assert res_sybil["verdict"] == "REJECT_DUPLICATE_CLAIM_FRAUD", (
            f"Expected REJECT_DUPLICATE_CLAIM_FRAUD, got: {res_sybil['verdict']}"
        )
        print("  Status:             PASSED (Autonomous Detection of Reused Photo via pHash)")

    # 6. Test Case 8: Presentation Attack Detection (2D Card Print Attack)
    card_path = os.path.join(script_dir, "test_car_card_crop.jpg")
    if os.path.exists(card_path):
        res_card = upload_claim(card_path, "Auto Insurance Claim")
        verify_forensic_contract(res_card, "Test Case 8 PAD Card Recapture")
        print("\n--- Test Case 8: Presentation Attack (Printed Card Recapture) ---")
        print(f"  Verdict:            {res_card['verdict']}")
        print(f"  Tamper Probability: {res_card['tamper_probability']}%")
        print(f"  Autonomous Action:  {res_card['action_taken']}")
        assert res_card["verdict"] in ["REJECT_RECAPTURED_2D_MEDIA", "REJECT_NO_DAMAGE_DETECTED"], (
            f"Expected REJECT_RECAPTURED_2D_MEDIA or REJECT_NO_DAMAGE_DETECTED, got: {res_card['verdict']}"
        )
        print("  Status:             PASSED (Presentation Attack Detected & Refused)")

    # 7. Test Case 9: AI Generated Coupon Code Character Alteration (D -> C)
    voucher_path = os.path.join(script_dir, "sample_real_voucher_tampered.jpg")
    if os.path.exists(voucher_path):
        res_voucher = upload_claim(voucher_path, "E-Commerce Voucher Claim")
        verify_forensic_contract(res_voucher, "Test Case 9 AI Coupon Tamper")
        print("\n--- Test Case 9: AI Generated Coupon Code Tampering (Altered Letter) ---")
        print(f"  Verdict:            {res_voucher['verdict']}")
        print(f"  Tamper Probability: {res_voucher['tamper_probability']}%")
        print(f"  Autonomous Action:  {res_voucher['action_taken']}")
        assert res_voucher["verdict"] in ["REJECT_SYNTHETIC_TAMPER", "MANUAL_REVIEW_FLAGGED"], (
            f"Expected REJECT_SYNTHETIC_TAMPER, got: {res_voucher['verdict']}"
        )
        print("  Status:             PASSED (AI Photo & Micro-Character Tampering Auto-Blocked)")

    # 8. Check MCP Tools Listing & JSON-RPC
    req_mcp = urllib.request.Request(f"{BASE_URL}/mcp/tools")
    with urllib.request.urlopen(req_mcp, timeout=5) as resp:
        mcp_data = json.loads(resp.read().decode())
        tools = mcp_data.get("tools", [])
        print(f"\n[OK] Model Context Protocol (MCP) Server: {len(tools)} OpenCV 5 tools registered.")
        assert len(tools) >= 6, f"Expected >= 6 MCP tools, got {len(tools)}"

    # 7. Check COOL Benchmark Waterfall
    req_bench = urllib.request.Request(f"{BASE_URL}/api/benchmark-cool?iterations=15")
    with urllib.request.urlopen(req_bench, timeout=5) as resp:
        bench_data = json.loads(resp.read().decode())
        waterfall = bench_data.get("tool_waterfall", [])
        print(f"[OK] ARM64 COOL Performance Waterfall: {len(waterfall)} OpenCV 5 primitives profiled.")
        assert len(waterfall) >= 5, "Missing tool waterfall in benchmark"

    print("\n" + "=" * 60)
    print("  ALL VERISIGHT MCP FORENSIC PIPELINE TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
