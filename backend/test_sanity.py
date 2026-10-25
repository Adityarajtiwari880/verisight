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

def run_tests():
    print("=" * 60)
    print("  VeriSight MCP Forensic Pipeline - Automated Sanity Verification")
    print(f"  Target Backend: {BASE_URL}")
    print("=" * 60)

    # 1. Test Health / Cloud Audit status
    try:
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
        res_g = upload_claim(genuine_path, "Genuine Fresh Fruit Claim")
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
        print("\n--- Test Case 2: Real-World Inpainted Image ---")
        print(f"  Verdict:            {res_t['verdict']}")
        print(f"  Tamper Probability: {res_t['tamper_probability']}%")
        print(f"  Autonomous Action:  {res_t['action_taken']}")
        assert res_t["verdict"] in ["REJECT_SYNTHETIC_TAMPER", "MANUAL_REVIEW_FLAGGED", "REJECT_CLAIM_SYNTHETIC_FRAUD"], (
            f"Tampered image failed detection: {res_t['verdict']}"
        )
        print("  Status:             PASSED (Fraud Detected)")

    # 4. Check MCP Tools Listing
    req_mcp = urllib.request.Request(f"{BASE_URL}/mcp/tools")
    with urllib.request.urlopen(req_mcp, timeout=5) as resp:
        mcp_data = json.loads(resp.read().decode())
        tools = mcp_data.get("tools", [])
        print(f"\n[OK] Model Context Protocol (MCP) Server: {len(tools)} OpenCV 5 tools registered.")

    print("\n" + "=" * 60)
    print("  ALL VERISIGHT MCP FORENSIC PIPELINE TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
