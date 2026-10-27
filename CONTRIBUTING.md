# Contributing to VeriSight MCP

Thank you for your interest in contributing to **VeriSight MCP**! We welcome contributions from computer vision researchers, systems engineers, and open-source enthusiasts.

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Python 3.10+** (tested up to 3.14)
- **Node.js 18+** & **npm**
- **Git**
- Optional: Linux ARM64 or AWS Graviton instance for COOL NEON testing.

### 2. Clone the Repository
```bash
git clone https://github.com/Adityarajtiwari880/verisight.git
cd verisight
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Run the backend server locally:
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Running Automated Sanity Tests

Before opening a pull request, ensure all 10 end-to-end multi-spectral sanity tests pass:

```bash
python backend/test_sanity.py
```

Expected output:
```
============================================================
  ALL VERISIGHT MCP FORENSIC PIPELINE TESTS PASSED!
============================================================
```

And verify that the Next.js frontend builds without TypeScript or bundling errors:
```bash
npm --prefix frontend run build
```

---

## 📐 Coding & Design Guidelines

1. **Pure Signal Processing Math**: Core forensic tools in `backend/forensics.py` must rely strictly on standard OpenCV primitives (`cv2.absdiff`, `cv2.Sobel`, `cv2.dft`, `cv2.findContours`). Avoid adding heavy multi-gigabyte neural network dependencies unless modularized as an optional plugin.
2. **Deterministic & Explainable**: Every decision must produce human-auditable telemetry (DQT tables, frequency energy, PRNU noise variance, chrominance discrepancy).
3. **Multi-Modal Concordance**: Never fail or condemn an authentic image based on an isolated ELA spike. Always require orthogonal corroboration (PRNU divergence, JPEG ghosts, seam feathering, or diffusion color fringing).
4. **Latency Budget**: Tools must adhere to a sub-5ms latency budget per frame to remain real-time and edge-compatible.

---

## 🚀 Pull Request Process

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Write clean, self-documenting code with informative commit messages following conventional commits (`feat: ...`, `fix: ...`, `docs: ...`, `perf: ...`).
3. Ensure automated tests pass 100%.
4. Open a Pull Request on GitHub against `main`. Provide a concise description of the changes, mathematical justification, and before/after verification metrics.

---

## ⚖️ License & Attribution

By submitting contributions to VeriSight MCP, you agree that your contributions will be licensed under the project's [Apache 2.0 License](LICENSE).
