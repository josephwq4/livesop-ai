@echo off
echo ====================================
echo LiveSOP AI - Quick Start Script
echo ====================================
echo.

echo [1/4] Setting up Backend...
cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Setting up environment variables...
if not exist .env (
    copy .env.example .env
    echo Created .env file - Please edit it with your API keys!
) else (
    echo .env file already exists
)

cd ..

echo.
echo [3/4] Setting up Frontend...
cd frontend

echo Installing Node dependencies...
call npm install

echo Setting up frontend environment...
if not exist .env (
    copy .env.example .env
    echo Created frontend .env file
) else (
    echo Frontend .env file already exists
)

cd ..

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Edit backend/.env with your API keys (OpenAI, Slack, Jira, Gmail)
echo 2. Start the backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo 3. Start the frontend: cd frontend ^&^& npm run dev
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo API Docs will be at: http://localhost:8000/docs
echo.
pause
