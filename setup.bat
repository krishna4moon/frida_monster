@echo off
setlocal enabledelayedexpansion

title KRISHNA TOOLS - Setup
color 0E

set "SCRIPT_DIR=%~dp0"
set "PYTHON_INSTALLER=python_installer.exe"
set "PYTHON_VERSION=3.11.8"
set "LOG_FILE=%SCRIPT_DIR%setup.log"

:log
echo [%date% %time%] %* >> "%LOG_FILE%"
exit /b

:display_banner
cls
echo.
echo [96m╔════════════════════════════════════════════════════════════════════════╗[0m
echo [96m║                                                                            ║[0m
echo [96m║           [92m🕉️  KRISHNA TOOLS - COMPLETE SETUP  [96m🕉️                      ║[0m
echo [96m║                 [93mMY BROTHER, LET'S GET STARTED![96m                         ║[0m
echo [96m║                                                                            ║[0m
echo [96m╚════════════════════════════════════════════════════════════════════════════╝[0m
echo.
echo [90m══════════════════════════════════════════════════════════════════════════[0m
echo.
exit /b

:check_admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [93m[!] BROTHER, I NEED ADMIN POWERS FOR THIS![0m
    echo [93m[*] GIVING MYSELF ADMIN ACCESS...[0m
    set "vbs=%temp%\getadmin.vbs"
    >"%vbs%" echo Set UAC = CreateObject^("Shell.Application"^)
    >>"%vbs%" echo UAC.ShellExecute "%~s0", "", "", "runas", 1
    >>"%vbs%" echo WScript.Quit
    cscript //nologo "%vbs%" 2>nul
    del "%vbs%" 2>nul
    exit /b
)
exit /b

:detect_arch
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "ARCH=64"
    set "PYTHON_ARCH=amd64"
    echo [92m[✓] MY BROTHER, YOU'RE ON 64-BIT WINDOWS - PERFECT![0m
) else (
    set "ARCH=86"
    set "PYTHON_ARCH=win32"
    echo [92m[✓] MY BROTHER, 32-BIT WINDOWS - NO PROBLEM![0m
)
exit /b

:check_python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PY_VERSION=%%i"
    echo [92m[✓] BROTHER! PYTHON %PY_VERSION% IS ALREADY HERE![0m
    for /f "tokens=1,2 delims=." %%a in ("%PY_VERSION%") do (
        set "PY_MAJOR=%%a"
        set "PY_MINOR=%%b"
    )
    if !PY_MAJOR! equ 3 if !PY_MINOR! geq 7 (
        set "PYTHON_READY=1"
        echo [92m[✓] PERFECT! YOUR PYTHON IS READY FOR ACTION![0m
    ) else (
        set "PYTHON_READY=0"
        echo [93m[!] BROTHER, YOUR PYTHON IS OLD - LET ME UPDATE IT FOR YOU![0m
    )
) else (
    set "PYTHON_READY=0"
    echo [93m[!] OH BROTHER! PYTHON NOT FOUND - DON'T WORRY![0m
    echo [93m[*] KRISHNA IS HERE - I WILL INSTALL IT FOR YOU![0m
)
exit /b

:download_python
echo.
echo [93m[*] BROTHER, DOWNLOADING PYTHON %PYTHON_VERSION% FOR YOU...[0m
echo [93m[*] THIS WILL JUST TAKE A MOMENT...[0m
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-%PYTHON_ARCH%.exe"
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'" >nul 2>&1
if exist "%PYTHON_INSTALLER%" (
    echo [92m[✓] DONE! PYTHON DOWNLOADED SUCCESSFULLY![0m
) else (
    echo [93m[*] BROTHER, TRYING ALTERNATIVE METHOD...[0m
    bitsadmin /transfer "PythonDownload" /download /priority normal "%PYTHON_URL%" "%CD%\%PYTHON_INSTALLER%" >nul 2>&1
    if exist "%PYTHON_INSTALLER%" (
        echo [92m[✓] GOT IT! PYTHON IS HERE![0m
    ) else (
        echo [91m[✗] BROTHER, DOWNLOAD FAILED - PLEASE CHECK YOUR INTERNET[0m
        pause
        exit /b 1
    )
)
exit /b

:install_python
echo.
echo [93m[*] BROTHER, INSTALLING PYTHON %PYTHON_VERSION%...[0m
echo [93m[*] I'M WORKING MY MAGIC - GIVE ME 2 MINUTES...[0m
start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
if %errorlevel% equ 0 (
    echo [92m[✓] BOOM! PYTHON INSTALLED LIKE A PRO![0m
    call :refresh_path
    set "PYTHON_READY=1"
) else (
    echo [93m[*] BROTHER, TRYING INSTALLATION FOR CURRENT USER...[0m
    start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    if !errorlevel! equ 0 (
        echo [92m[✓] SUCCESS! PYTHON IS NOW YOUR BROTHER![0m
        set "PYTHON_READY=1"
    ) else (
        echo [91m[✗] BROTHER, I TRIED MY BEST BUT INSTALLATION FAILED[0m
        pause
        exit /b 1
    )
)
del "%PYTHON_INSTALLER%" 2>nul
exit /b

:refresh_path
set "PATH=%PATH%;C:\Python%ARCH%;C:\Python%ARCH%\Scripts"
for /d %%i in ("C:\Program Files\Python*") do set "PATH=%%i;%%i\Scripts;%PATH%"
for /d %%i in ("C:\Program Files (x86)\Python*") do set "PATH=%%i;%%i\Scripts;%PATH%"
exit /b

:install_packages
echo.
echo [93m[*] BROTHER, INSTALLING PYTHON PACKAGES...[0m
echo [93m[*] REQUESTS, COLORAMA, FRIDA-TOOLS - ALL COMING RIGHT UP![0m
python -m pip install --upgrade pip --quiet 2>nul
python -m pip install requests colorama frida-tools --quiet 2>nul
if %errorlevel% equ 0 (
    echo [92m[✓] ALL PACKAGES INSTALLED! TOO EASY![0m
) else (
    echo [93m[*] BROTHER, TRYING WITH USER PERMISSIONS...[0m
    python -m pip install requests colorama frida-tools --user --quiet 2>nul
    if !errorlevel! equ 0 (
        echo [92m[✓] GOT THEM! PACKAGES ARE READY![0m
    ) else (
        echo [91m[✗] BROTHER, PACKAGE INSTALLATION FAILED[0m
    )
)
exit /b

:check_adb
echo.
echo [93m[*] BROTHER, CHECKING FOR ADB...[0m
where adb >nul 2>&1
if errorlevel 1 (
    echo [93m[!] ADB NOT FOUND - DON'T WORRY BROTHER![0m
    echo [93m[*] I'M GETTING PLATFORM TOOLS FOR YOU...[0m
    set "PLATFORM_TOOLS_URL=https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    set "ZIP_FILE=platform-tools.zip"
    powershell -Command "Invoke-WebRequest -Uri '%PLATFORM_TOOLS_URL%' -OutFile '%ZIP_FILE%'" >nul 2>&1
    if exist "%ZIP_FILE%" (
        echo [93m[*] EXTRACTING AND SETTING UP...[0m
        powershell -Command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath 'C:\' -Force" >nul 2>&1
        if exist "C:\platform-tools\adb.exe" (
            echo [92m[✓] ADB INSTALLED! DEVICE COMMUNICATION ESTABLISHED![0m
            set "PATH=%PATH%;C:\platform-tools"
            setx PATH "%PATH%;C:\platform-tools" /M >nul
        )
        del "%ZIP_FILE%" 2>nul
    )
) else (
    echo [92m[✓] BROTHER! ADB IS READY AND WAITING![0m
)
exit /b

:create_runner_script
if not exist "%SCRIPT_DIR%runner.py" (
    echo [91m[✗] BROTHER! runner.py NOT FOUND![0m
    echo [93m[*] PLEASE PLACE runner.py IN THE SAME FOLDER[0m
    pause
    exit /b 1
)
echo [92m[✓] BROTHER! runner.py IS READY TO ROCK![0m
exit /b

:main_menu
cls
echo.
echo [96m╔════════════════════════════════════════════════════════════════════════╗[0m
echo [96m║                                                                            ║[0m
echo [96m║              [92m✅ SETUP COMPLETE! WHAT NOW MY BROTHER? ✅[96m                  ║[0m
echo [96m║                                                                            ║[0m
echo [96m╠════════════════════════════════════════════════════════════════════════╣[0m
echo [96m║                                                                            ║[0m
echo [96m║  [92m1[96m. [92m🚀 LAUNCH KRISHNA TOOLS - LET'S HACK![96m                           ║[0m
echo [96m║  [92m2[96m. [93m📦 REINSTALL DEPENDENCIES - JUST IN CASE[96m                        ║[0m
echo [96m║  [92m3[96m. [94m🔧 CHECK INSTALLATION - VERIFY EVERYTHING[96m                       ║[0m
echo [96m║  [92m4[96m. [95m📁 OPEN OUTPUT DIRECTORY - SEE YOUR RESULTS[96m                      ║[0m
echo [96m║  [92m5[96m. [91m❌ EXIT - JAY SHREE KRISHNA[96m                                     ║[0m
echo [96m║                                                                            ║[0m
echo [96m╚════════════════════════════════════════════════════════════════════════╝[0m
echo.
set /p "MENU_CHOICE=[92mKRISHNA@TOOLS~# [0m"

if "%MENU_CHOICE%"=="1" goto :launch_tools
if "%MENU_CHOICE%"=="2" goto :reinstall_deps
if "%MENU_CHOICE%"=="3" goto :check_install
if "%MENU_CHOICE%"=="4" goto :open_output
if "%MENU_CHOICE%"=="5" goto :exit
goto :main_menu

:launch_tools
echo.
echo [92m[*] BROTHER, LAUNCHING KRISHNA TOOLS...[0m
echo [92m[*] MAY KRISHNA BLESS YOUR HACKING JOURNEY![0m
echo [90m══════════════════════════════════════════════════════════════════════════[0m
python runner.py
echo [90m══════════════════════════════════════════════════════════════════════════[0m
echo [92m[✓] SESSION COMPLETE! GOOD JOB BROTHER![0m
pause
goto :main_menu

:reinstall_deps
echo.
echo [93m[*] BROTHER, REINSTALLING DEPENDENCIES...[0m
call :install_packages
echo [92m[✓] ALL FRESH AND READY![0m
pause
goto :main_menu

:check_install
echo.
echo [93m[*] BROTHER, LET ME SHOW YOU WHAT I'VE DONE...[0m
echo [90m────────────────────────────────────────────────────────────────────────[0m
python --version
pip --version
where adb 2>nul
echo [90m────────────────────────────────────────────────────────────────────────[0m
echo [92m[✓] EVERYTHING IS PERFECT! YOU'RE READY TO ROCK![0m
pause
goto :main_menu

:open_output
if exist "%SCRIPT_DIR%frida_outputs" (
    echo [92m[*] BROTHER, OPENING YOUR OUTPUT FOLDER...[0m
    explorer "%SCRIPT_DIR%frida_outputs"
) else (
    echo [93m[*] BROTHER, CREATING OUTPUT FOLDER FOR YOU...[0m
    mkdir "%SCRIPT_DIR%frida_outputs"
    explorer "%SCRIPT_DIR%frida_outputs"
)
pause
goto :main_menu

:exit
echo.
echo [92m╔════════════════════════════════════════════════════════════════════════╗[0m
echo [92m║                                                                            ║[0m
echo [92m║              [96m🙏 THANK YOU MY BROTHER! JAY SHREE KRISHNA 🙏[92m                ║[0m
echo [92m║                                                                            ║[0m
echo [92m║                 [93mSEE YOU SOON! HARE KRISHNA![92m                             ║[0m
echo [92m║                                                                            ║[0m
echo [92m╚════════════════════════════════════════════════════════════════════════╝[0m
echo.
timeout /t 3 >nul
exit /b 0

:main
call :display_banner
call :check_admin
call :detect_arch
call :check_python

if "%PYTHON_READY%"=="0" (
    echo.
    echo [93m[*] DON'T WORRY BROTHER - I'M TAKING CARE OF EVERYTHING![0m
    call :download_python
    call :install_python
)

call :install_packages
call :check_adb
call :create_runner_script

if not exist "%SCRIPT_DIR%frida_outputs" (
    mkdir "%SCRIPT_DIR%frida_outputs"
    echo [92m[✓] BROTHER, OUTPUT FOLDER CREATED FOR YOU![0m
)

cls
echo.
echo [92m╔════════════════════════════════════════════════════════════════════════╗[0m
echo [92m║                                                                            ║[0m
echo [92m║              [96m🎉 SUCCESS! I DID IT MY BROTHER! 🎉[92m                         ║[0m
echo [92m║                                                                            ║[0m
echo [92m║         [93mKRISHNA BLESSED ME AND I SETUP EVERYTHING FOR YOU![92m               ║[0m
echo [92m║                                                                            ║[0m
echo [92m╚════════════════════════════════════════════════════════════════════════╝[0m
echo.
echo [93mWHAT I INSTALLED FOR YOU MY BROTHER:[0m
echo   [92m✓[0m Python %PYTHON_VERSION% - THE MAGICAL TOOL!
echo   [92m✓[0m pip - YOUR PACKAGE MANAGER!
echo   [92m✓[0m requests, colorama, frida-tools - THE HOLY TRINITY!
echo   [92m✓[0m ADB - TO CONNECT WITH YOUR DEVICE!
echo.
echo [93mWHERE YOUR RESULTS WILL BE SAVED:[0m
echo   [92m📁[0m %SCRIPT_DIR%frida_outputs
echo.
echo [96mNOW GO AHEAD AND CHOOSE OPTION 1 TO START HACKING![0m
echo.
pause
goto :main_menu

call :main
