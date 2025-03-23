@echo off
REM naiad-notify.cmd
REM Script per notificare NAIAD di processare la clipboard

REM Definizione percorso
set "NAIAD_COMM_DIR=C:\ProgramData\NAIAD\comm"

REM Crea la directory se non esiste
if not exist "%NAIAD_COMM_DIR%" mkdir "%NAIAD_COMM_DIR%"

REM Crea il file trigger
echo %DATE% %TIME% > "%NAIAD_COMM_DIR%\process_clipboard"

exit /b 0