@echo off
setlocal enabledelayedexpansion

:: This shim intercepts calls to gsudo and removes the -c flag which causes errors on some systems.

set "ARGS="
:loop
if "%~1"=="" goto end
if "%~1"=="-c" (
    shift
    goto loop
)
:: Append argument, handling quotes
set "arg=%~1"
set "ARGS=!ARGS! "!arg!""
shift
goto loop

:end
:: Call the real gsudo. We assume it's in the PATH. 
:: We use 'gsudo.exe' to avoid calling this batch file recursively if possible, 
:: but a better way is to find the full path.
for /f "delims=" %%i in ('where gsudo.exe') do (
    if /i "%%i" neq "%~f0" (
        "%%i" %ARGS%
        exit /b !errorlevel!
    )
)

:: Fallback if where fails or only finds us
gsudo.exe %ARGS%
