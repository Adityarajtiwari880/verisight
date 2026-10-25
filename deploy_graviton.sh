#!/usr/bin/env bash
# ==============================================================================
# VeriSight MCP — AWS Graviton Arm64 (Ubuntu 24.04) One-Click Deployment Script
# Configures Cloud-Optimized OpenCV Library (COOL) and launches FastAPI Daemon
# ==============================================================================

set -e

echo "=== [1/5] Verifying AWS Graviton Arm64 Hardware Architecture ==="
ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
    echo "WARNING: Detected architecture '$ARCH'. AWS Graviton instances run on 'aarch64'."
else
    echo "Confirmed: Running on AWS Graviton ($ARCH)."
fi

echo "=== [2/5] Configuring COOL (Cloud-Optimized OpenCV) Environment Paths ==="
export LD_LIBRARY_PATH="/opt/cool/cpp_sdk/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="/opt/cool/python_3.12/site-packages/:$PYTHONPATH"

# Persist to environment for all future SSH sessions
sudo tee -a /etc/environment > /dev/null << 'EOF'
LD_LIBRARY_PATH="/opt/cool/cpp_sdk/lib:$LD_LIBRARY_PATH"
PYTHONPATH="/opt/cool/python_3.12/site-packages/:$PYTHONPATH"
EOF

echo "=== [3/5] Verifying OpenCV 5 & COOL KleidiCV Acceleration ==="
python3 -c "
import cv2, platform
print(f'Active Python: {platform.python_version()} on {platform.machine()}')
print(f'Active OpenCV: {cv2.__version__} from {cv2.__file__}')
is_cool = '/opt/cool' in cv2.__file__
print(f'COOL Arm64 Active: {is_cool}')
"

echo "=== [4/5] Installing Backend Service Dependencies ==="
cd "$(dirname "$0")/backend"
pip3 install -r requirements.txt --break-system-packages

echo "=== [5/5] Launching VeriSight MCP FastAPI Daemon on Port 8000 ==="
# Check if port 8000 is occupied, if so kill old process
sudo fuser -k 8000/tcp || true

nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/verisight.log 2>&1 &

sleep 3
if curl -s http://127.0.0.1:8000/api/aws-status > /dev/null; then
    echo "SUCCESS: VeriSight MCP is LIVE on Port 8000!"
    echo "Test endpoint: curl http://127.0.0.1:8000/api/aws-status"
else
    echo "ERROR: Service failed to start. Showing logs from /tmp/verisight.log:"
    cat /tmp/verisight.log
    exit 1
fi
