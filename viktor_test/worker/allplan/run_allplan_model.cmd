@echo off
setlocal

set "ALLPLAN_EXE=%~1"
set "PYP_TARGET=%~2"

if "%ALLPLAN_EXE%"=="" (
    echo Missing Allplan executable argument. 1>&2
    exit /b 1
)

if "%PYP_TARGET%"=="" (
    echo Missing PythonPart path argument. 1>&2
    exit /b 1
)

if not exist "%ALLPLAN_EXE%" (
    echo Allplan executable not found: %ALLPLAN_EXE% 1>&2
    exit /b 1
)

if not exist "%PYP_TARGET%" (
    echo PythonPart not found: %PYP_TARGET% 1>&2
    exit /b 1
)

start "" /wait "%ALLPLAN_EXE%" -o "@%PYP_TARGET%"
exit /b %ERRORLEVEL%
