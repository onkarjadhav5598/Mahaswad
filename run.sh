#!/usr/bin/env bash
# ============================================================
#  Maharashtrian Recipe Generator — Launch Script (Linux/macOS)
# ============================================================
#  Starts both the FastAPI backend and the Streamlit frontend.
# ============================================================

set -e

echo ""
echo "  ========================================"
echo "   🍛 Maharashtrian Recipe Generator"
echo "  ========================================"
echo ""

# -- Check Ollama --
if ! command -v ollama &> /dev/null; then
    echo "[WARNING] Ollama CLI not found on PATH."
    echo "          Install it from https://ollama.com and run:"
    echo "            ollama serve"
    echo "            ollama pull gemma2:2b"
    echo ""
fi

# -- Install dependencies --
echo "[1/3] Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo ""

# -- Start FastAPI backend in background --
echo "[2/3] Starting FastAPI backend on http://localhost:8000 ..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
sleep 2

# -- Start Streamlit frontend in background --
echo "[3/3] Starting Streamlit frontend on http://localhost:8501 ..."
streamlit run app.py --server.port 8501 --server.headless true &
FRONTEND_PID=$!

echo ""
echo "  Both servers are running!"
echo "    Backend  : http://localhost:8000/docs"
echo "    Frontend : http://localhost:8501"
echo ""
echo "  Press Ctrl+C to stop both servers."
echo ""

# -- Trap Ctrl+C to kill both processes --
trap "echo ''; echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

# Wait for either to exit
wait
