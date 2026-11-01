"""
VeriSight MCP — Command Line Interface (CLI)
Provides instant terminal forensics, MCP server daemon, and hardware benchmarks.
"""

import sys
import os
import argparse
import json
from pathlib import Path

# Add backend directory to path
_current_dir = str(Path(__file__).resolve().parent)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

import cv2
from backend import scan_image, __version__

def cmd_scan(args):
    """Executes multi-spectral forensic scan on a single image file."""
    if not os.path.exists(args.image_path):
        print(f"Error: File not found: {args.image_path}", file=sys.stderr)
        sys.exit(1)

    try:
        report = scan_image(
            args.image_path,
            claim_type=args.claim_type,
            sensitivity=args.sensitivity
        )
    except Exception as e:
        print(f"Forensic Analysis Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        # Exclude huge base64 visuals in standard terminal JSON output unless requested
        output_data = {k: v for k, v in report.items() if k != "visuals"}
        print(json.dumps(output_data, indent=2))
        return

    metrics = report.get("metrics", {})
    verdict = report.get("verdict", "UNKNOWN")
    risk = report.get("tamper_probability", 0.0)
    action = report.get("action_taken", "")
    roi = report.get("roi", [])

    # Colorized terminal status
    status_icon = "PASS" if "APPROVE" in verdict else ("ALERT" if "REVIEW" in verdict else "FRAUD")

    print("\n" + "=" * 68)
    print(f"  VERISIGHT FORENSIC REPORT — v{__version__}")
    print(f"  Target File : {args.image_path}")
    print("=" * 68)
    print(f"  VERDICT             : [{status_icon}] {verdict}")
    print(f"  TAMPER PROBABILITY  : {risk}%")
    print(f"  SUSPECT ROI (x,y,w,h): {roi}")
    print(f"  ELA P95 ENERGY      : {metrics.get('ela_score', 0.0)}")
    print(f"  2D-DFT HIGH FREQ    : {metrics.get('fft_high_freq_energy', 0.0)}")
    print(f"  CHROMINANCE DIFF    : {metrics.get('chrominance_discrepancy_pct', 0.0)}%")
    print(f"  PRNU SENSOR NOISE   : {metrics.get('prnu_noise_divergence_pct', 0.0)}% divergence")
    print(f"  LIVENESS (PAD)      : {metrics.get('liveness_score', 0.0)}% ({metrics.get('pad_status', 'N/A')})")
    print(f"  INFERENCE LATENCY   : {metrics.get('latency_ms', 0.0)} ms")
    print("-" * 68)
    print(f"  AUTONOMOUS ACTION   : {action}")
    print("=" * 68 + "\n")

def cmd_server(args):
    """Starts the VeriSight FastAPI + MCP JSON-RPC Daemon."""
    if args.mcp:
        from backend.mcp_server import run_stdio_server
        run_stdio_server()
        return
    import uvicorn
    print(f"Starting VeriSight MCP Server on {args.host}:{args.port}...")
    uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=args.reload)

def cmd_mcp(args):
    """Runs standard I/O (stdio) MCP server for Claude Desktop, Cursor, and Smithery."""
    from backend.mcp_server import run_stdio_server
    run_stdio_server()

def cmd_benchmark(args):
    """Runs the OpenCV 5 hardware acceleration benchmark."""
    from backend.benchmark_runner import run_benchmark
    print(f"Executing OpenCV 5 Performance Benchmark ({args.iterations} iterations)...")
    res = run_benchmark(iterations=args.iterations)
    print(json.dumps(res, indent=2))

def main():
    parser = argparse.ArgumentParser(
        prog="verisight",
        description=f"VeriSight MCP v{__version__} — OpenCV 5 Physical Vision Forensics Engine"
    )
    parser.add_argument("--version", action="version", version=f"VeriSight v{__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: scan
    scan_parser = subparsers.add_parser("scan", help="Run multi-spectral forensic audit on an image")
    scan_parser.add_argument("image_path", help="Path to image file (JPG, PNG, WEBP)")
    scan_parser.add_argument("--claim-type", default="General Forensic / Document / E-Commerce Claim", help="Contextual claim domain")
    scan_parser.add_argument("--sensitivity", choices=["conservative", "balanced", "aggressive"], default="balanced")
    scan_parser.add_argument("--json", action="store_true", help="Print structured JSON output")
    scan_parser.set_defaults(func=cmd_scan)

    # Command: server
    server_parser = subparsers.add_parser("server", help="Start the FastAPI & MCP JSON-RPC Server")
    server_parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    server_parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    server_parser.add_argument("--reload", action="store_true", help="Enable auto-reloader for dev")
    server_parser.add_argument("--mcp", action="store_true", help="Start as stdio MCP server for Claude Desktop / Cursor")
    server_parser.set_defaults(func=cmd_server)

    # Command: mcp
    mcp_parser = subparsers.add_parser("mcp", help="Run standard I/O (stdio) MCP server for Claude Desktop, Cursor, and Smithery")
    mcp_parser.set_defaults(func=cmd_mcp)

    # Command: benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run hardware SIMD latency benchmark")
    bench_parser.add_argument("--iterations", type=int, default=25, help="Number of profiling iterations")
    bench_parser.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
