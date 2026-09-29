#!/usr/bin/env bash
set -e

# Resolve script directory so it can be executed from any path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Launch interactive physics sandbox using virtualenv, uv, or system manimgl
if [ -f "./.venv/bin/manimgl" ]; then
    exec ./.venv/bin/manimgl src/dynamic_memory.py InteractiveDynamicMemory "$@"
elif command -v uv >/dev/null 2>&1; then
    exec uv run manimgl src/dynamic_memory.py InteractiveDynamicMemory "$@"
elif command -v manimgl >/dev/null 2>&1; then
    exec manimgl src/dynamic_memory.py InteractiveDynamicMemory "$@"
else
    echo "Error: manimgl not found."
    echo "Please install dependencies via 'uv sync' or 'pip install -r requirements.txt'."
    exit 1
fi
