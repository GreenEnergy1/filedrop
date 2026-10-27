@echo off
setlocal
cd /d "%~dp0"
set "ROOT=%CD%"
set "SVC=Filedrop"
set "PORT=1080"

net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: Run this script as Administrator.
    goto :failed
)

set "NSSM="
for /f "delims=" %%P in ('where nssm.exe 2^>nul') do if not defined NSSM set "NSSM=%%P"
if not defined NSSM if exist "%~dp0nssm.exe" set "NSSM=%~dp0nssm.exe"
if not defined NSSM if exist "%ProgramFiles%\nssm\win64\nssm.exe" set "NSSM=%ProgramFiles%\nssm\win64\nssm.exe"
if not defined NSSM if exist "C:\nssm\win64\nssm.exe" set "NSSM=C:\nssm\win64\nssm.exe"
if not defined NSSM (
    echo ERROR: nssm.exe was not found.
    echo Put nssm.exe in this folder, or add the folder that contains it to PATH.
    echo Open a NEW Administrator terminal after changing PATH.
    goto :failed
)
echo Using NSSM: "%NSSM%"

sc query %SVC% >nul 2>&1
if not errorlevel 1 (
    echo ERROR: The %SVC% service is already installed.
    echo Run uninstall_service.bat first if you want to reinstall it.
    goto :failed
)

if not exist venv (
    python -m venv venv
)
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :failed

venv\Scripts\python.exe setup.py
if errorlevel 1 goto :failed

if not exist logs mkdir logs

"%NSSM%" install %SVC% "%ROOT%\venv\Scripts\python.exe" "%ROOT%\app.py"
"%NSSM%" set %SVC% AppDirectory "%ROOT%"
"%NSSM%" set %SVC% DisplayName "Filedrop"
"%NSSM%" set %SVC% Description "Serves a simple downloads page for a folder of files."
"%NSSM%" set %SVC% Start SERVICE_AUTO_START
"%NSSM%" set %SVC% AppEnvironmentExtra FILEDROP_PORT=%PORT%
"%NSSM%" set %SVC% AppStdout "%ROOT%\logs\filedrop.log"
"%NSSM%" set %SVC% AppStderr "%ROOT%\logs\filedrop.log"
"%NSSM%" set %SVC% AppRotateFiles 1
"%NSSM%" set %SVC% AppRotateBytes 1048576
"%NSSM%" set %SVC% AppExit Default Restart

netsh advfirewall firewall add rule name="Filedrop" dir=in action=allow protocol=TCP localport=%PORT% >nul
netsh advfirewall firewall add rule name="Filedrop Discovery" dir=in action=allow protocol=UDP localport=5353 remoteip=localsubnet >nul

"%NSSM%" start %SVC%
if errorlevel 1 goto :failed

echo.
echo Filedrop is running as a Windows service on port %PORT% and advertising itself on the LAN.
echo Open http://localhost:%PORT% to browse the selected folder.
pause
exit /b 0

:failed
echo.
pause
exit /b 1
