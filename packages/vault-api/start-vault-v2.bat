@echo off
echo ========================================
echo Starting Vault API v2 (PostgreSQL + Encryption)
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Create default tenant
echo Creating default tenant...
python create_default_tenant.py
echo.

REM Start server
echo Starting Vault API v2...
python test_server_v2.py
