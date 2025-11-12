@echo off
echo.
echo ========================================
echo   Universal OAuth Vault API v3
echo ========================================
echo.
echo Features:
echo   - Rate Limiting (per IP)
echo   - Request Validation (Pydantic)
echo   - Structured Logging (JSON)
echo   - Token Encryption (AES-256-GCM)
echo   - PostgreSQL Storage
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Activate virtual environment
call venv\Scripts\activate

REM Create default tenant if needed
echo Creating default tenant...
python create_default_tenant.py
echo.

echo Starting Vault API v3...
echo.
echo 🚀 Server: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🔍 Health: http://localhost:8000/health
echo 📊 Rate Limiting: ACTIVE
echo 📝 Structured Logs: logs/security.log
echo.

REM Start server
python test_server_v3.py
