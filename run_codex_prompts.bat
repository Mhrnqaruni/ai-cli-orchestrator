@echo off
REM ============================================================
REM Codex Sequential Prompt Runner
REM Reads prompts from codex_prompt.txt and sends them to Codex
REM one-by-one, each in the SAME session with full context.
REM
REM Usage:
REM   run_codex_prompts.bat              (uses --full-auto mode)
REM   run_codex_prompts.bat --yolo       (uses --dangerously-bypass-approvals-and-sandbox)
REM   run_codex_prompts.bat --timeout=600
REM   run_codex_prompts.bat --file=my_prompts.txt
REM ============================================================

echo ============================================================
echo CODEX SEQUENTIAL PROMPT RUNNER
echo ============================================================
echo.

REM Check if codex_prompt.txt exists (default)
if "%~1"=="" (
    if not exist codex_prompt.txt (
        echo ERROR: codex_prompt.txt not found!
        echo.
        echo Please create codex_prompt.txt with numbered prompts:
        echo   1. first prompt
        echo   2. second prompt
        echo   3. third prompt
        echo.
        pause
        exit /b 1
    )
)

REM Check if python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Run the Python script with all arguments passed through
python "%~dp0codex_sequential.py" %*

echo.
echo ============================================================
echo Done!
echo ============================================================
pause
