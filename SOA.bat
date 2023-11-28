@echo off
echo Activating virtual environment...
call .venv\Scripts\activate.bat

::echo Installing dependencies, this process may take a while...
::pip install -r requirements.txt
::echo Dependencies dump finished.

cls

echo Running application...
set APP_PATH=C:\Users\user\Desktop\SOA\app
python %APP_PATH%\main.py

echo Deactivating virtual environment...
deactivate
