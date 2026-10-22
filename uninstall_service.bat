@echo off
setlocal
set "SVC=Filedrop"

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

"%NSSM%" stop %SVC%
"%NSSM%" remove %SVC% confirm
netsh advfirewall firewall delete rule name="Filedrop" >nul

echo.
echo The %SVC% service has been removed. Your files were not touched.
pause
exit /b 0

:failed
echo.
pause
exit /b 1
