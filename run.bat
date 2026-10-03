@echo off
REM ============================================================
REM  Maharashtrian Recipe Generator — Launch Script (Windows)
REM ============================================================
REM  Starts both the FastAPI backend and the Streamlit frontend.
REM ============================================================

echo.
echo  ========================================
echo   Maharashtrian Recipe Generator
echo  ========================================
echo.

REM -- Check if Ollama is reachable --
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Ollama CLI not found on PATH.
    echo           Install it from https://ollama.com and run:
    echo             ollama serve
    echo             ollama pull gemma2:2b
    echo.
)

REM -- Install dependencies --
echo [1/3] Installing Python dependencies...
pip install -r requirements.txt --quiet
echo.

REM -- Start FastAPI backend --
echo [2/3] Starting FastAPI backend on http://localhost:8000 ...
start "FastAPI Backend" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM -- Give the backend a moment to start --
timeout /t 3 /nobreak >nul

REM -- Start Streamlit frontend --
echo [3/3] Starting Streamlit frontend on http://localhost:8501 ...
start "Streamlit Frontend" cmd /k "streamlit run app.py --server.port 8501 --server.headless true"

echo.
echo  Both servers are starting!
echo    Backend  : http://localhost:8000/docs
echo    Frontend : http://localhost:8501
echo.
echo  Press any key to exit this launcher (servers will keep running).
pause >nul
