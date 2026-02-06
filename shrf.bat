@echo off
cls
echo.

REM Check for at least 1 argument
if "%~1"=="" (
    echo Usage:
    echo   shrf send file.ext CODE PASSWORD
    echo   shrf get IP CODE PASSWORD
    pause
    goto :eof
)

REM Send mode
if /i "%~1"=="send" (
    if "%~4"=="" (
        echo Usage: shrf send file.ext CODE PASSWORD
        pause
        goto :eof
    )
    python "%~dp0app.py" send "%~2" "%~3" "%~4"
    goto :eof
)

REM Get mode
if /i "%~1"=="get" (
    if "%~4"=="" (
        echo Usage: shrf get IP CODE PASSWORD
        pause
        goto :eof
    )
    python "%~dp0app.py" get "%~2" "%~3" "%~4"
    goto :eof
)

REM Unknown command
echo Invalid command.
echo Usage:
echo   shrf send file.ext CODE PASSWORD
echo   shrf get IP CODE PASSWORD
pause
