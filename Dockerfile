FROM python:3.11-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install git, curl, and certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR="/usr/local/bin" sh

# Copy package metadata and source
COPY pyproject.toml README.md LICENSE ./
COPY backend ./backend
COPY verisight ./verisight

# Install dependencies and package in system python
RUN uv pip install --system -e .

# Default MCP command
CMD ["python", "-m", "backend.cli", "mcp"]
