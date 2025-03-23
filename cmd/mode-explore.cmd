@echo off
set "NAIAD_COMM_DIR=C:\ProgramData\NAIAD\comm"
if not exist "%NAIAD_COMM_DIR%" mkdir "%NAIAD_COMM_DIR%"
echo %DATE% %TIME% > "%NAIAD_COMM_DIR%\mode_explore"
exit /b 0