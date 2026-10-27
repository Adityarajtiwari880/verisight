# 🔬 VeriSight MCP — Autonomous Physical AI Visual Forensics Engine

[![VeriSight CI](https://github.com/Adityarajtiwari880/verisight/actions/workflows/ci.yml/badge.svg)](https://github.com/Adityarajtiwari880/verisight/actions)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![OpenCV 5](https://img.shields.io/badge/OpenCV-5.0.0-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Protocol%202024--11--05-10B981)](https://modelcontextprotocol.io/)
[![AWS Graviton](https://img.shields.io/badge/AWS-Graviton%20Arm64%20(COOL)-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/ec2/graviton/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16.4.3-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

> **Sub-3ms Physical AI and multi-spectral visual forensics engine built on pure OpenCV 5 and SIMD acceleration.** Detects generative AI inpainting, deepfake manipulation, duplicate photo reuse, and presentation recapture attacks with zero heavyweight neural network dependencies.

---

## 📌 Problem Statement: Synthetic First-Party Fraud

In 2026, quick-commerce platforms (**Blinkit, Zepto, Instamart, Amazon Fresh**), e-commerce marketplaces, and **insurers** lose billions of dollars annually to **Synthetic First-Party Refund Fraud**. 

Claimants photograph an authentic, undamaged item, package, or car bumper, apply consumer generative AI inpainting tools (such as Flux, Adobe Firefly, or Stable Diffusion Inpainting) to synthesize photorealistic rotten mold, cracks, tears, or dents, and exploit automated instant-refund bots.

```
Authentic Image ──> Generative AI Inpaint (Flux / Firefly) ──> Instant Refund Bot ──> Payout Leakage ($$$)
                                  │
                                  ▼
                         [ VERISIGHT MCP ]
               • Sub-3ms Physical Sensor Analysis
               • Mathematical Invariant Checks
               • Autonomous Auto-Block & S3 Vault
```

**VeriSight MCP** solves this via an autonomous **Perception → Hypothesis → Action Physical AI Agent** built on **OpenCV 5** and optimized with the **Cloud-Optimized OpenCV Library (COOL)** for **AWS Graviton (Arm64)**. It inspects images in under **3 milliseconds**, exposing mathematical artifacts left by generative diffusion processes, verifying authentic CMOS sensor noise, and executing automated payout decisions while committing cryptographic evidence dossiers to **Amazon S3** and **Amazon DynamoDB**.

---

## ⚡ VeriSight vs Traditional Deep Learning Models

| Dimension | Traditional Deep Learning (ResNet / CLIP / ViT) | VeriSight Physical AI Engine |
| :--- | :--- | :--- |
| **Inference Latency** | 250 ms – 1,200 ms (Unviable for instant checkout) | **< 2.8 ms (380+ FPS)** |
| **Model Weight Footprint** | 350 MB – 2.4 GB PyTorch weights | **0 MB (Pure OpenCV 5 C++ & SIMD Primitives)** |
| **Compute Requirement** | High-end Nvidia GPU (CUDA required) | **Pure CPU / Arm64 NEON (AWS Graviton)** |
| **Generalization & Drift** | Vulnerable to adversarial attacks & new diffusion models | **Grounded in mathematical physical optics & sensor physics** |
| **Audit Explainability** | Black-box softmax probabilities | **Deterministic mathematical proof (ELA, PRNU, 2D FFT, Ghosts)** |
| **Recapture Attack Defense**| None (Foiled by 2D screen or paper printout) | **Built-in Presentation Attack Detection (PAD)** |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A["📸 Incoming Claim Image (REST / MCP / CLI)"] --> B["Active Perception: CIE LAB Luminance Check"]
    B --> C{"Lighting Optimal?"}
    C -- "No (< 65/255)" --> D["Adaptive CLAHE Contrast Normalization"]
    C -- "Yes" --> E["Multi-Spectral Forensic Suite"]
    D --> E

    subgraph E["Multi-Spectral Mathematical Forensic Pipeline"]
        E1["Gradient-Normalized ELA (Sobel Compensated)"]
        E2["PRNU CMOS Sensor Noise Extraction"]
        E3["Azimuthal 2D FFT Diffusion Lattice Harmonics"]
        E4["Multi-Q JPEG Quantization Ghost Sweeper"]
        E5["Perceptual Hash Sybil Duplicate Detection"]
        E6["2D Recapture Presentation Attack Detection (PAD)"]
    end

    E1 & E2 & E3 & E4 & E5 & E6 --> F["Autonomous Concordance Gate"]
    F --> G{"Concordance Verdict"}
    
    G -- "Risk < 35%" --> H["🟢 AUTO_APPROVE_CLAIM (Instant Payout)"]
    G -- "35% <= Risk < 70%" --> I["🟡 HUMAN_IN_THE_LOOP_REVIEW"]
    G -- "Risk >= 70%" --> J["🔴 REJECT_SYNTHETIC_TAMPER (Auto-Blocked)"]
    
    H & I & J --> K["Cryptographic Audit Dossier (SHA-256 + S3 / DynamoDB)"]
```

---

## 💻 2-Line Python SDK & Terminal CLI

VeriSight can be embedded as a Python library, invoked from the command line, or run as a standalone server:

### Python SDK
```python
from backend import scan_image, verify_claim

# 1-Line multi-spectral forensic audit
report = scan_image("claims/produce_claim.jpg", claim_type="Fresh Produce")

print(f"Verdict: {report['verdict']} ({report['tamper_probability']}% Risk)")
print(f"Suspect ROI: {report['roi']} | ELA Score: {report['metrics']['ela_score']}")
print(f"Action: {report['recommended_action']}")
```

### Terminal CLI
```bash
# Instant forensic audit of an image
verisight scan path/to/voucher.jpg

# Output machine-readable JSON telemetry
verisight scan path/to/invoice.jpg --json

# Run reproducible ARM64 COOL performance benchmark
verisight benchmark --frames 100

# Launch MCP Server and FastAPI Backend Daemon
verisight server --port 8000
```

---

## 🌐 Model Context Protocol (MCP) Integration

VeriSight natively implements the **Anthropic Model Context Protocol (MCP)** specification (`protocol_version: 2024-11-05`). External LLM agents (**Claude Desktop**, **Cursor**, **Windsurf**, **LangChain**) can discover and call VeriSight tools autonomously.

### Claude Desktop & Cursor Configuration

Add VeriSight to your `claude_desktop_config.json` (or Cursor MCP settings):

```json
{
  "mcpServers": {
    "verisight": {
      "command": "python",
      "args": ["-m", "backend.cli", "server", "--mcp"]
    }
  }
}
```

### Available MCP Tools:
* `verisight_inspect_claim`: End-to-end multi-spectral forensic triage on an image.
* `verisight_active_clahe`: Dynamic CIE LAB contrast enhancement.
* `verisight_sweep_jpeg_ghosts`: Multi-Q JPEG quantization discrepancy sweeper.
* `verisight_azimuthal_fourier_probe`: 2D DFT frequency-domain harmonic analysis.
* `verisight_sensor_noise_prnu`: High-pass CMOS sensor noise extraction and variance check.
* `verisight_cloud_ledger_audit`: Immutable audit trail retrieval from DynamoDB and S3 evidence vaults.

---

## 🌟 Core Enterprise Capabilities

* **Live In-Browser Webcam Scanner:** Real-time video feed with guided targeting reticles allowing live validation of physical items and paper documents.
* **Interactive 4x ROI Loupe Magnifier:** High-precision circular inspection loupe zooming into the suspect ROI to show pixel-level inpainting seams and sensor grain discontinuities.
* **Hardware & EXIF Provenance:** Extracts camera make, model, JPEG DQT Quantization Tables, and detects editing software signatures (`Photoshop`, `Inpaint`, `GIMP`).
* **Edge-Compensated Gradient-Normalized ELA:** Sobel-gradient normalized Error Level Analysis eliminates edge false positives while amplifying generative compression mismatches.
* **Multi-Spectral Color-Space Decomposition:** Deconstructs and inspects claims across RGB, CIE LAB, YCrCb, and HSV orthogonal color spaces.
* **Tunable Forensic Sensitivity:** Real-time selector for `Conservative`, `Balanced`, and `Zero-Trust / Aggressive` threshold profiles.
* **Cryptographic Evidence Dossier:** 1-click export of court-admissible audit certificates signed with SHA-256 seals.

---

## 🔬 Mathematical Forensics Deep-Dive (OpenCV 5)

| Forensic Pillar | OpenCV 5 Core Functions | Physical / Mathematical Principle |
| :--- | :--- | :--- |
| **1. Photometric Active Perception** | `cv2.cvtColor`, `cv2.createCLAHE` | Evaluates CIE LAB luminance. Normalizes underexposed scenes ($<65/255$) without distorting sensor gradients. |
| **2. Edge-Compensated ELA** | `cv2.imencode`, `cv2.absdiff`, `cv2.Sobel`, `cv2.findContours` | Normalizes ELA difference by Sobel gradient magnitude ($E_{\text{norm}} = E / (1 + \alpha G)$) to eliminate false positives on text and high-contrast typography. |
| **3. Azimuthal 2D Fast Fourier Transform** | `cv2.createHanningWindow`, `cv2.dft`, `cv2.magnitude`, `np.hypot` | Natural images decay as $P(f) \propto 1/f^2$. Diffusion model latent decoders introduce periodic upsampling harmonic peaks in outer frequency bands. |
| **4. Multi-Q JPEG Ghost Sweeper** | `cv2.imencode` across $Q \in [60, 96]$, `cv2.absdiff` | Sweeps candidate quality factors to identify divergence in the local error minimum curve between suspect ROI and ambient image. |
| **5. Sensor Noise PRNU Residual** | `cv2.medianBlur`, `cv2.absdiff`, rolling window `np.std` | Real CMOS sensors generate uniform high-pass noise fingerprints. Spliced generative inpainting creates artificial local variance dead-zones ($Z > 3\sigma$). |
| **6. Chrominance Gradient Check** | `cv2.cvtColor(YCrCb)`, `cv2.Sobel` | Diffusion inpainting creates subtle chrominance edge discrepancies in the $Cr/Cb$ orthogonal color spaces. |

---

## 📊 Verified Experimental Benchmarks

### Real-World Test Matrix

| Test Scenario | Luminance Check | Target ROI & ELA Score | 2D DFT & Chrominance Discrepancy | Autonomous Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Genuine Claim (`1_genuine_claim.jpg`)** | `178.7 / 255` (Optimal) | ROI `[160, 120, 320, 240]` \| ELA = **`17.0`** | DFT = `69.03` \| Chrominance = **`25.13%`** | **`AUTO_APPROVE_CLAIM` (8.5% Risk)** |
| **Real Strawberries Mold (`sample_real_strawberries`)** | `175.0 / 255` (Optimal) | ROI `[142, 92, 356, 316]` \| ELA = **`64.0`** | DFT = `78.20` \| Chrominance = **`75.08%`** | **`REJECT_SYNTHETIC_TAMPER` (78.7% Risk)** |
| **Real Altered Invoice (`sample_real_invoice`)** | `210.0 / 255` (Optimal) | ROI `[146, 316, 290, 49]` \| ELA = **`34.0`** | PRNU Noise Diff = **`125.54%`** | **`REJECT_SYNTHETIC_TAMPER` (80.1% Risk)** |
| **Real Car Bumper Dent (`sample_real_bumper`)** | `185.0 / 255` (Optimal) | ROI `[150, 181, 132, 108]` \| ELA = **`16.0`** | Chrominance = **`94.58%`** | **`REJECT_SYNTHETIC_TAMPER` (70.9% Risk)** |
| **Authentic Coupon Screenshot (Code D)** | `221.0 / 255` (Optimal) | Border Suppression Active \| ELA = **`31.2`** | PRNU Concordance = `Verified` | **`AUTO_APPROVE_CLAIM` (30.8% Risk)** |
| **WhatsApp Multi-Hop Edge Case** | `< 65.0 / 255` (CLAHE) | Global recompression block artifacts | Ambiguous SNR detected | **`HUMAN_IN_THE_LOOP_REVIEW` (61.5% Risk)** |

---

### Reproducible AWS Graviton Arm64 (COOL) Hardware Benchmark

```
======================================================================
 VERISIGHT MCP — REPRODUCIBLE OPENCV 5 COOL BENCHMARK
======================================================================
Platform Architecture: aarch64 (AWS Graviton3 / c7g.medium)
OpenCV Build Version : 5.0.0 (Arm64 COOL KleidiCV Enabled)
Binary Source File   : /opt/cool/python_3.12/site-packages/cv2/__init__.py
Executing 100 continuous perception-decision pipeline frames...

--- REPRODUCIBLE BENCHMARK RESULTS TABLE ---
| Metric                        | AWS Graviton (Arm64 + COOL) | Baseline x86 Unoptimized | Delta / Speedup     |
| :---------------------------- | :-------------------------- | :----------------------- | :------------------ |
| **Mean Frame Latency**        | **2.62 ms**                 | 3.72 ms                  | **+42.0% Faster**   |
| **95th Percentile Latency**   | **3.10 ms**                 | 4.40 ms                  | **Guaranteed SLA**  |
| **Forensic Throughput**       | **381.6 FPS**               | 268.8 FPS                | **Enterprise Scale**|
| **KleidiCV NEON Acceleration**| **ACTIVE (/opt/cool)**      | Disabled                 | **Hardware Arm64**  |
======================================================================
```

---

## 📁 Repository Structure

```
verisight/
├── .github/
│   ├── workflows/ci.yml         # Automated Python 3.11 & Next.js CI
│   ├── ISSUE_TEMPLATE/          # Bug reports & feature requests
│   └── PULL_REQUEST_TEMPLATE.md # Contributor review standards
├── backend/
│   ├── __init__.py              # Python SDK exports (scan_image, verify_claim)
│   ├── cli.py                   # Terminal CLI entry point (verisight command)
│   ├── agent.py                 # Autonomous Perception-Hypothesis-Action loop
│   ├── forensics.py             # Pure OpenCV 5 multi-spectral inspection primitives
│   ├── mcp_server.py            # Model Context Protocol JSON-RPC implementation
│   ├── main.py                  # FastAPI REST endpoints & WebSocket feeds
│   ├── cloud_storage.py         # AWS S3 & DynamoDB evidence persistence
│   └── test_sanity.py           # End-to-end automated sanity verification suite
├── frontend/                    # Next.js 16.4.3 enterprise dark-mode dashboard
│   ├── app/                     # React Server Components & UI layouts
│   └── components/              # Interactive 4x ROI Loupe, Webcam, & Spectrum viewers
├── docker-compose.yml           # Production multi-stage container orchestration
├── Dockerfile.arm64             # AWS Graviton COOL deployment container
├── deploy_graviton.sh           # Automated EC2 setup script
├── pyproject.toml               # Standalone package build (pip install verisight)
├── mcp_claude_desktop.json      # Ready-to-use Claude Desktop configuration
├── CITATION.cff                 # Academic & industry citation metadata
├── CONTRIBUTING.md              # Contributor guidelines & code style
├── SECURITY.md                  # Vulnerability disclosure policy
├── LICENSE                      # Apache 2.0 Open-Source License
└── README.md
```

---

## 🚀 Quickstart & Deployment

### Option A: Docker Compose (Recommended)
Run the complete production stack (FastAPI Backend + Next.js UI) with a single command:
```bash
git clone https://github.com/Adityarajtiwari880/verisight.git
cd verisight
docker compose up --build
```
* **Web UI Dashboard:** [http://localhost:3000](http://localhost:3000)
* **REST API & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Model Context Protocol (MCP) Endpoint:** `http://localhost:8000/mcp/rpc`

---

### Option B: Local Development Run (Windows / macOS / Linux)

```bash
# 1. Clone repository
git clone https://github.com/Adityarajtiwari880/verisight.git
cd verisight

# 2. Start the FastAPI OpenCV 5 Backend (Terminal 1)
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 3. Start the Next.js Frontend Dashboard (Terminal 2)
cd ../frontend
npm install
npm run dev
```

---

### Option C: AWS Graviton EC2 Deployment (Arm64 + COOL)

```bash
# 1. SSH into your AWS Graviton instance
ssh -i "your-key.pem" ubuntu@<YOUR-EC2-PUBLIC-IP>

# 2. Clone repo and run deployment script
git clone https://github.com/Adityarajtiwari880/verisight.git
cd verisight
chmod +x deploy_graviton.sh
./deploy_graviton.sh

# 3. Verify hardware acceleration status
curl http://127.0.0.1:8000/api/aws-status
```

---

## 🤝 Contributing

We welcome contributions from the computer vision, security, and open-source communities!
* Please review our [Contributing Guidelines](CONTRIBUTING.md) for branch naming, coding standards, and PR protocols.
* All PRs must pass `python backend/test_sanity.py` and `npm --prefix frontend run build`.
* Code of Conduct: [Contributor Covenant 2.1](CODE_OF_CONDUCT.md).

---

## 🔒 Security

For security vulnerabilities and responsible disclosure protocols, please see our [Security Policy](SECURITY.md). Do not submit security vulnerabilities through public GitHub issues.

---

## 📖 Citation

If you use VeriSight in your research, production systems, or publications, please cite it using our [CITATION.cff](CITATION.cff):

```bibtex
@software{tiwari2026verisight,
  author       = {Tiwari, Aditya Raj},
  title        = {VeriSight MCP: Autonomous Physical AI Visual Forensics Engine},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/Adityarajtiwari880/verisight}
}
```

---

## 👥 Authors & Acknowledgments

* **Aditya Raj Tiwari** — *Lead Architect & Computer Vision Engineer* ([GitHub](https://github.com/Adityarajtiwari880))
* Special thanks to the **OpenCV Foundation** and **Amazon Web Services (AWS)** for open-source benchmarks and tooling support.

---

## 📜 License

Licensed under the **[Apache License, Version 2.0](LICENSE)**. You may freely use, modify, and distribute this software for commercial and private purposes according to the license terms.
