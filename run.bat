@echo off
echo Installing required libraries...
pip install fastapi uvicorn

echo.
echo Starting the fast server...
uvicorn main:app --reload

pause

