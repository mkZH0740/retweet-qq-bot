cd .\venv\Scripts
call activate.bat

cd ..
cd ..

start runServer.bat
choice /t 10 /d y /n >nul
start runBot.bat /wait ""