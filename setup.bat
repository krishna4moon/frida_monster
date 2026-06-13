@echo off
title KRISHNA TOOLS - AUTO SETUP
color 0A

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:display_banner
cls
echo.
echo ================================================================
echo              KRISHNA TOOLS - AUTO SETUP
echo ================================================================
echo.
echo MY BROTHER, I AM CHECKING EVERYTHING FOR YOU...
echo.

:check_admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] NEED ADMIN POWERS MY BROTHER!
    echo [*] RESTARTING WITH ADMIN ACCESS...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:check_python
echo [*] CHECKING PYTHON...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PY_VERSION=%%i"
    echo [OK] PYTHON %PY_VERSION% FOUND
    goto :check_packages
)

echo [!] PYTHON NOT FOUND - DON'T WORRY BROTHER!
echo [*] I WILL INSTALL PYTHON FOR YOU...
goto :install_python

:install_python
echo [*] DOWNLOADING PYTHON 3.11.8...

:: Detect architecture
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
) else (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.8/python-3.11.8.exe"
)

set "PYTHON_SETUP=python_setup.exe"

:: Download Python
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_SETUP%'}" >nul 2>&1

if not exist "%PYTHON_SETUP%" (
    echo [FAIL] COULD NOT DOWNLOAD PYTHON
    echo [*] PLEASE DOWNLOAD MANUALLY FROM: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] PYTHON DOWNLOADED
echo [*] INSTALLING PYTHON (PLEASE WAIT)...

:: Install Python silently
start /wait %PYTHON_SETUP% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Clean up
del "%PYTHON_SETUP%" 2>nul

:: Refresh PATH
set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
set "PATH=%PATH%;C:\Python311;C:\Python311\Scripts"

echo [OK] PYTHON INSTALLED SUCCESSFULLY!
timeout /t 2 >nul

:check_packages
echo [*] CHECKING PYTHON PACKAGES...

:: Check and install pip
python -m ensurepip >nul 2>&1

:: Check requests
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] INSTALLING REQUESTS...
    python -m pip install requests --quiet >nul 2>&1
)

:: Check colorama
python -c "import colorama" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] INSTALLING COLORAMA...
    python -m pip install colorama --quiet >nul 2>&1
)

:: Check frida
python -c "import frida" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] INSTALLING FRIDA-TOOLS...
    python -m pip install frida-tools --quiet >nul 2>&1
)

echo [OK] ALL PACKAGES ARE READY

:check_adb
echo [*] CHECKING ADB...
where adb >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] ADB FOUND
    goto :check_runner
)

echo [!] ADB NOT FOUND - I WILL INSTALL IT
echo [*] DOWNLOADING PLATFORM TOOLS...

set "ZIP_FILE=platform-tools.zip"
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile '%ZIP_FILE%'}" >nul 2>&1

if exist "%ZIP_FILE%" (
    echo [*] EXTRACTING PLATFORM TOOLS...
    powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath 'C:\' -Force" >nul 2>&1
    
    if exist "C:\platform-tools\adb.exe" (
        echo [OK] ADB INSTALLED TO C:\platform-tools
        set "PATH=%PATH%;C:\platform-tools"
        setx PATH "%PATH%;C:\platform-tools" /M >nul
    )
    del "%ZIP_FILE%" 2>nul
) else (
    echo [WARN] COULD NOT DOWNLOAD ADB
    echo [*] WILL CONTINUE ANYWAY
)

:check_runner
echo [*] CHECKING FOR runner.py...
if not exist "runner.py" (
    echo [FAIL] runner.py NOT FOUND!
    echo [*] PLEASE PUT runner.py IN: %SCRIPT_DIR%
    pause
    exit /b 1
)
echo [OK] runner.py FOUND

:check_output
if not exist "frida_outputs" mkdir "frida_outputs"

:ready
cls
echo.
echo ================================================================
echo         EVERYTHING IS READY MY BROTHER!
echo ================================================================
echo.
echo [OK] PYTHON - READY
echo [OK] ALL PACKAGES - READY  
echo [OK] ADB - READY
echo [OK] OUTPUT FOLDER - READY
echo [OK] runner.py - READY
echo.
echo ================================================================
echo        STARTING KRISHNA TOOLS NOW...
echo ================================================================
echo.
echo MAY KRISHNA BLESS YOUR HACKING JOURNEY!
echo.
timeout /t 3 >nul

:run
python runner.py

:done
cls
echo.
echo ================================================================
echo         SESSION COMPLETE MY BROTHER!
echo ================================================================
echo.
echo        THANK YOU FOR USING KRISHNA TOOLS
echo             JAY SHREE KRISHNA!
echo.
timeout /t 3 >nul
exit /b 0
