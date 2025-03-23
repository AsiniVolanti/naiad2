import win32api
import win32con
import signal
import logging
import sys
from pathlib import Path
import threading
import atexit

class ExitHandler:
    """Gestore avanzato per la chiusura pulita dell'applicazione"""
    
    def __init__(self, app_name: str, lock_file: Path, logger: logging.Logger):
        self.app_name = app_name
        self.logger = logger
        self.lock_file = lock_file
        self._exit_event = threading.Event()
        self._cleanup_done = False
        
        # Registra gli handler per tutti i possibili eventi di chiusura
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura tutti gli handler necessari"""
        
        def handle_windows_event(event_type):
            """Handler unificato per eventi di Windows"""
            event_names = {
                win32con.CTRL_C_EVENT: 'CTRL_C',
                win32con.CTRL_BREAK_EVENT: 'CTRL_BREAK',
                win32con.CTRL_CLOSE_EVENT: 'CTRL_CLOSE',
                win32con.CTRL_LOGOFF_EVENT: 'CTRL_LOGOFF',
                win32con.CTRL_SHUTDOWN_EVENT: 'CTRL_SHUTDOWN'
            }
            event_name = event_names.get(event_type, f'Unknown({event_type})')
            self.logger.info(f"Ricevuto evento Windows: {event_name}")
            self.initiate_shutdown()
            return True  # Necessario per Windows per indicare che l'evento è stato gestito
        
        def handle_signal(signum, frame):
            """Handler unificato per segnali POSIX"""
            signal_names = {
                signal.SIGINT: 'SIGINT',
                signal.SIGTERM: 'SIGTERM',
                signal.SIGABRT: 'SIGABRT',
                signal.SIGBREAK: 'SIGBREAK'
            }
            signal_name = signal_names.get(signum, f'Unknown({signum})')
            self.logger.info(f"Ricevuto segnale: {signal_name}")
            self.initiate_shutdown()
        
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Handler per eccezioni non gestite"""
            self.logger.error("Eccezione non gestita", exc_info=(exc_type, exc_value, exc_traceback))
            self.initiate_shutdown()
        
        def handle_exit():
            """Handler per atexit"""
            self.cleanup()
        
        # Registra handler per eventi Windows
        try:
            win32api.SetConsoleCtrlHandler(handle_windows_event, True)
        except Exception as e:
            self.logger.error(f"Errore registrazione handler Windows: {e}")
        
        # Registra handler per segnali POSIX
        for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]:
            try:
                signal.signal(sig, handle_signal)
            except Exception as e:
                self.logger.error(f"Errore registrazione handler per {sig}: {e}")
        
        # Registra handler per eccezioni non gestite
        sys.excepthook = handle_exception
        
        # Registra handler atexit
        atexit.register(handle_exit)
    
    def initiate_shutdown(self):
        """Avvia la procedura di shutdown"""
        if self._exit_event.is_set():
            return  # Evita shutdown multipli
        
        self.logger.info("Avvio procedura di shutdown...")
        self._exit_event.set()
        self.cleanup()
        
        # Force exit se necessario
        try:
            sys.exit(0)
        except SystemExit:
            pass
    
    def cleanup(self):
        """Esegue la pulizia delle risorse"""
        if self._cleanup_done:
            return
        
        self.logger.info("Esecuzione pulizia...")
        try:
            # Rimuovi file di lock
            if self.lock_file.exists():
                self.lock_file.unlink()
                self.logger.info("File di lock rimosso")
            
            # Qui possono essere aggiunte altre operazioni di pulizia
            
            self._cleanup_done = True
            self.logger.info("Pulizia completata")
            
        except Exception as e:
            self.logger.error(f"Errore durante la pulizia: {e}")
    
    def is_shutting_down(self) -> bool:
        """Verifica se è in corso lo shutdown"""
        return self._exit_event.is_set()