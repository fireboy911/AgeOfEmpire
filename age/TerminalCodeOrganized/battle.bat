@echo off
REM Battle CLI wrapper script
REM Allows using "battle run ..." instead of "python MainTerminal.py run ..."

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Run the MainTerminal.py with all arguments passed to this script
python "%SCRIPT_DIR%MainTerminal.py" %*

endlocal
