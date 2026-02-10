# Installation Guide

## Prerequisites

- Python 3.13+
- pip

## Quick Start

```bash
# 1. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install all dependencies (exact pinned versions)
pip install -r requirements.txt

# 3. Set environment variables
export PORTKEY_API_KEY="your-portkey-api-key"
export MCP_SERVER_URL="https://mcp.portkey.ai/your-mcp-server/mcp"
export MCP_API_KEY="your-mcp-api-key"

# 4. Run the agent
python main.py
```

## Notes

- `requirements.txt` contains all 79 dependencies (direct + transitive) pinned to exact versions from `uv.lock`. This guarantees a reproducible install.
- If you have [uv](https://github.com/astral-sh/uv) installed, you can use `uv sync` instead of steps 1–2 above, which uses the `uv.lock` lockfile directly.
