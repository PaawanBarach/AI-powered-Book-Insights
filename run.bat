@echo off
cd backend

echo Checking migrations...
if not exist db.sqlite3 (
    echo Creating database and migrations...
    venv\Scripts\python manage.py migrate
)

echo Starting Backend on port 8000...
start "Backend" cmd /c "cd /d %~dp0backend && venv\Scripts\python manage.py runserver"

cd ..\frontend

echo Starting Frontend on port 5173...
start "Frontend" cmd /c "cd /d %~dp0frontend && npm run dev"

echo Done! Open http://localhost:5173
pause