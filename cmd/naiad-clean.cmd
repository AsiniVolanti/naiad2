@echo off
REM naiad_new:chat.cmd
REM Script per notificare NAIAD di processare la clipboard attivando una nuova chat

REM Definizione percorso
set "NAIAD_COMM_DIR=C:\ProgramData\NAIAD\comm"

REM Crea la directory se non esiste
if not exist "%NAIAD_COMM_DIR%" mkdir "%NAIAD_COMM_DIR%"

REM Crea il file trigger
echo %DATE% %TIME% > "%NAIAD_COMM_DIR%\clean_history"

exit /b 0