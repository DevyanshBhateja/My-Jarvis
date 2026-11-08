#!/bin/bash
# Quick start script for running the Jarvis real-time voice assistant

echo "=============================================================================="
echo "JARVIS REAL-TIME VOICE ASSISTANT - QUICK START"
echo "=============================================================================="
echo ""

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}" || exit 1

if [ ! -f "main.py" ] || [ ! -d "jarvis_rt" ]; then
    echo "[ERROR] Could not find main.py or jarvis_rt in ${PROJECT_ROOT}"
    exit 1
fi

echo "[STEP 1] Checking dependencies..."
echo ""

# Check virtual environment (.venv or oj-env)
VENV_PATH=""
if [ -d ".venv" ]; then
    VENV_PATH=".venv"
elif [ -d "oj-env" ]; then
    VENV_PATH="oj-env"
else
    echo "[ERROR] Virtual environment (.venv or oj-env) not found in ${PROJECT_ROOT}"
    exit 1
fi

echo "[✓] Virtual environment found at ${VENV_PATH}"

# Check for required commands
if ! command -v pw-play &> /dev/null && ! command -v paplay &> /dev/null && ! command -v mpg123 &> /dev/null && ! command -v ffplay &> /dev/null; then
    echo "[WARN] No preferred audio player found. Recommended:"
    echo "  sudo dnf install pipewire-utils mpg123"
fi

echo "[✓] Audio environment checked"
echo ""

echo "[STEP 2] Starting the assistant..."
echo ""
echo "Activating virtual environment (${VENV_PATH}) and starting main.py..."
echo ""
echo "Expected output:"
echo "  [JARVIS] Starting real-time assistant..."
echo "  [MIC] Starting stream..."
echo "  [VAD] Using WebRTC VAD"
echo "  [JARVIS] Listening for speech..."
echo ""
echo "To stop the assistant, press Ctrl+C"
echo ""
echo "=============================================================================="
echo ""

# Activate venv and run main.py
source "${VENV_PATH}/bin/activate"
python main.py
