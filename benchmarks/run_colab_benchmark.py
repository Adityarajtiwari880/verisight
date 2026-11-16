"""
VeriSight MCP — Authoritative Empirical Forensic Benchmark Suite
Evaluates VeriSight v2.2.6 across real-world camera photographs and authentic forensic claims:
- COCO val2017 & OpenCV organic high-dynamic camera captures (Authentic Ground-Truth)
- Real-world AI inpainting, fabricated collision impact, tax invoice alteration,
  and generative diffusion tampering (Fraud Ground-Truth).

Runs in Google Colab / AWS Cloud / Local with 0 local storage footprint (streaming in-memory).
Outputs: Confusion Matrix, Specificity, Recall, Precision, F1-Score, ROC-AUC, and Latency.
"""

import os
import sys
import time
import argparse
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import json
import cv2
import numpy as np

# Add repo to sys.path if running inside workspace
repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_dir not in sys.path:
    sys.path.insert(0, repo_dir)

try:
    from backend.agent import forensic_agent
    from backend.aws_adapter import aws_adapter
except ImportError:
    from verisight.backend.agent import forensic_agent
    from verisight.backend.aws_adapter import aws_adapter

def get_curated_benchmark_dataset(limit: int = 30):
    """
    Constructs an empirical benchmark dataset:
    1. Authentic real-world camera photos (COCO val2017 Flickr captures & OpenCV organic captures).
    2. Real-world fraudulent claims (inpainted produce mold, fabricated vehicle dents,
       altered tax invoice totals, altered voucher codes, carton punctures, broken screens, and diffusion inpainting).
    """
    authentic_records = []
    tampered_records = []

    # 1. Authentic COCO real-world Flickr captures
    coco_ids = [
        139, 285, 632, 724, 776, 785, 802, 872, 885, 1000,
        1268, 1296, 1353, 1490, 1503
    ]
    for cid in coco_ids:
        authentic_records.append({
            "id": f"coco_{cid}",
            "url": f"http://images.cocodataset.org/val2017/{cid:012d}.jpg",
            "ground_truth": "AUTHENTIC",
            "category": "Natural Camera Scene (COCO Flickr)",
            "claim_type": "Commercial Delivery Package Claim"
        })

    # 2. Authentic OpenCV real camera captures
    opencv_authentic = [
        ("opencv_fruits", "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/fruits.jpg", "Organic Fresh Produce"),
        ("opencv_messi", "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/messi5.jpg", "Sports Motion Action"),
        ("opencv_butterfly", "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/butterfly.jpg", "Wildlife Macro"),
        ("opencv_baboon", "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/baboon.jpg", "Animal Fur Texture"),
        ("opencv_building", "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/building.jpg", "Architectural Facade")
    ]
    for name, url, cat in opencv_authentic:
        authentic_records.append({
            "id": name,
            "url": url,
            "ground_truth": "AUTHENTIC",
            "category": cat,
            "claim_type": "Commercial Delivery Package Claim"
        })

    # 3. Ground-truth real-world fraudulent claims hosted on GitHub raw
    repo_raw = "https://raw.githubusercontent.com/Adityarajtiwari880/verisight/main/backend"
    repo_fraud_samples = [
        ("gt_strawberries_inpainted", f"{repo_raw}/sample_real_strawberries_inpainted.jpg", "AI Inpainted Mold Fraud", "Commercial Delivery Package Claim"),
        ("gt_car_bumper_dent", f"{repo_raw}/sample_real_car_bumper_dent.jpg", "AI Car Bumper Dent Fraud", "Automotive Collision Claim"),
        ("gt_invoice_tampered", f"{repo_raw}/sample_real_invoice_tampered.jpg", "Tampered Tax Invoice Price", "Commercial Invoice Claim"),
        ("gt_voucher_tampered", f"{repo_raw}/sample_real_voucher_tampered.jpg", "Altered Voucher Promo Code", "Commercial Voucher Claim"),
        ("gt_ai_diffusion_fraud", f"{repo_raw}/2_ai_inpainted_fraud.jpg", "Generative AI Diffusion Inpaint", "Commercial Delivery Package Claim"),
        ("gt_delivery_box_puncture", f"{repo_raw}/sample_real_delivery_box_puncture.jpg", "Inpainted Parcel Crush Damage", "Commercial Delivery Package Claim"),
        ("gt_cracked_windshield", f"{repo_raw}/sample_real_cracked_windshield.jpg", "Inpainted Auto Glass Bullseye", "Automotive Collision Claim"),
        ("gt_spoiled_milk_mold", f"{repo_raw}/sample_real_spoiled_milk_mold.jpg", "Inpainted Dairy Food Spoilage", "Commercial Delivery Package Claim"),
        ("gt_altered_prescription", f"{repo_raw}/sample_real_altered_prescription.jpg", "Altered Medical Rx Dosage", "Commercial Invoice Claim"),
        ("gt_broken_screen_phone", f"{repo_raw}/sample_real_broken_screen_phone.jpg", "Inpainted Electronics Screen Crack", "Commercial Delivery Package Claim")
    ]
    for name, url, cat, ctype in repo_fraud_samples:
        tampered_records.append({
            "id": name,
            "url": url,
            "ground_truth": "TAMPERED",
            "category": cat,
            "claim_type": ctype
        })

    # Interleave 2:1 (Authentic:Tampered) for an empirical distribution
    interleaved = []
    a_idx, t_idx = 0, 0
    while a_idx < len(authentic_records) or t_idx < len(tampered_records):
        if a_idx < len(authentic_records):
            interleaved.append(authentic_records[a_idx])
            a_idx += 1
        if a_idx < len(authentic_records):
            interleaved.append(authentic_records[a_idx])
            a_idx += 1
        if t_idx < len(tampered_records):
            interleaved.append(tampered_records[t_idx])
            t_idx += 1

    return interleaved[:limit]

def run_benchmark(max_samples: int = 30, output_dir: str = "benchmark_output"):
    os.makedirs(output_dir, exist_ok=True)
    dataset = get_curated_benchmark_dataset(limit=max_samples)

    print("=" * 80)
    print("  VERISIGHT MCP — EMPIRICAL FORENSIC BENCHMARK SUITE")
    print(f"  Target Sample Size : {len(dataset)} Ground-Truth Pairs")
    print(f"  Execution Mode     : Streaming In-Memory (Zero Disk Footprint)")
    print("=" * 80)

    y_true = []
    y_pred_risk = []
    y_pred_binary = []
    latencies = []
    results_log = []

    tp, tn, fp, fn = 0, 0, 0, 0

    print(f"\n{'Sample ID':<32} | {'Ground Truth':<12} | {'Verdict':<26} | {'Risk':<6} | {'Status'}")
    print("-" * 95)

    for rec in dataset:
        aws_adapter.clear_test_ledger()
        sample_id = rec["id"]
        gt = rec["ground_truth"]

        # Fetch image bytes in memory
        try:
            url = rec["url"]
            # Fallback to local file if available in workspace
            local_name = url.split("/")[-1]
            local_path = os.path.join(repo_dir, "backend", local_name)
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    raw_b = f.read()
            else:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    raw_b = resp.read()
            img = cv2.imdecode(np.frombuffer(raw_b, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                continue

            t0 = time.perf_counter()
            res = forensic_agent.run_investigation(
                img,
                raw_bytes=raw_b,
                claim_type=rec["claim_type"],
                claim_id=f"BM-{sample_id}"
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed)

            verdict = res["verdict"]
            risk = res["tamper_probability"]

            is_predicted_tamper = (verdict in ["REJECT_SYNTHETIC_TAMPER", "HUMAN_IN_THE_LOOP_REVIEW", "REJECT_DUPLICATE_CLAIM_FRAUD"]) or (risk >= 45.0)

            gt_bin = 1 if gt == "TAMPERED" else 0
            pred_bin = 1 if is_predicted_tamper else 0

            y_true.append(gt_bin)
            y_pred_risk.append(risk / 100.0)
            y_pred_binary.append(pred_bin)

            if gt == "TAMPERED":
                if pred_bin == 1:
                    tp += 1
                    status = "CORRECT (Caught Fraud)"
                else:
                    fn += 1
                    status = "FALSE NEGATIVE"
            else:
                if pred_bin == 0:
                    tn += 1
                    status = "CORRECT (Auto-Approved)"
                else:
                    fp += 1
                    status = "FALSE POSITIVE"

            print(f"{sample_id:<32} | {gt:<12} | {verdict:<26} | {risk:>5.1f}% | {status}")

            results_log.append({
                "sample_id": sample_id,
                "ground_truth": gt,
                "verdict": verdict,
                "risk_score": risk,
                "latency_ms": round(elapsed, 2),
                "metrics": res.get("metrics", {})
            })

            del img
        except Exception as e:
            print(f"Error processing {sample_id}: {e}")
            continue

    total = len(y_true)
    if total == 0:
        print("[!] No samples evaluated.")
        return

    acc = (tp + tn) / total * 100.0
    spec = tn / max(1, (tn + fp)) * 100.0
    rec = tp / max(1, (tp + fn)) * 100.0
    prec = tp / max(1, (tp + fp)) * 100.0
    f1 = 2 * (prec * rec) / max(1e-5, (prec + rec))
    mean_lat = np.mean(latencies) if latencies else 0.0

    print("\n" + "=" * 60)
    print("  VERISIGHT MCP — BENCHMARK EVALUATION SUMMARY")
    print("=" * 60)
    print(f"  Total Samples Evaluated  : {total}")
    print(f"  Overall Accuracy         : {acc:.1f}%")
    print(f"  Specificity (Authentic)  : {spec:.1f}%  ({tn} True Negative, {fp} False Positive)")
    print(f"  Recall (Fraud Caught)    : {rec:.1f}%  ({tp} True Positive, {fn} False Negative)")
    print(f"  Precision                : {prec:.1f}%")
    print(f"  F1-Score                 : {f1:.1f}%")
    print(f"  Mean Inference Latency   : {mean_lat:.2f} ms")
    print("=" * 60)

    # Save summary report
    summary = {
        "verisight_version": "2.2.6",
        "total_samples": total,
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "accuracy_pct": round(acc, 2),
        "specificity_pct": round(spec, 2),
        "recall_pct": round(rec, 2),
        "precision_pct": round(prec, 2),
        "f1_score_pct": round(f1, 2),
        "mean_latency_ms": round(mean_lat, 2),
        "detailed_results": results_log
    }

    report_path = os.path.join(output_dir, "benchmark_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[OK] Benchmark report saved to: {report_path}")

    # Plot Confusion Matrix and ROC curve
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
        from sklearn.metrics import confusion_matrix, roc_curve, auc

        cm = confusion_matrix(y_true, y_pred_binary)
        fpr, tpr, _ = roc_curve(y_true, y_pred_risk)
        roc_auc = auc(fpr, tpr)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax1,
                    xticklabels=["Pred Authentic", "Pred Fraud"],
                    yticklabels=["Actual Authentic", "Actual Fraud"])
        ax1.set_title("VeriSight Forensic Confusion Matrix", fontsize=14, fontweight="bold")

        ax2.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC (AUC = {roc_auc:.3f})")
        ax2.plot([0, 1], [0, 1], color="navy", lw=1.5, linestyle="--")
        ax2.set_xlim([0.0, 1.0])
        ax2.set_ylim([0.0, 1.05])
        ax2.set_xlabel("False Positive Rate", fontsize=11)
        ax2.set_ylabel("True Positive Rate", fontsize=11)
        ax2.set_title("Receiver Operating Characteristic (ROC)", fontsize=14, fontweight="bold")
        ax2.legend(loc="lower right")
        ax2.grid(True, alpha=0.3)

        fig_path = os.path.join(output_dir, "benchmark_confusion_matrix.png")
        plt.tight_layout()
        plt.savefig(fig_path, dpi=200)
        plt.close()
        print(f"[OK] Confusion Matrix & ROC plots saved to: {fig_path}")
    except Exception as e:
        print(f"[!] Warning: Plot generation skipped: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run VeriSight Empirical Forensic Benchmark")
    parser.add_argument("--samples", type=int, default=30, help="Maximum number of samples to evaluate")
    parser.add_argument("--output", type=str, default="benchmark_output", help="Output directory for reports")
    args = parser.parse_args()

    run_benchmark(max_samples=args.samples, output_dir=args.output)
