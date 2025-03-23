import webview
from pathlib import Path
import logging
from typing import Optional


class UIManager:
    """
    Gestisce la creazione e il ciclo di vita delle finestre UI di NAIAD.
    Si basa su pywebview per mostrare le interfacce HTML.
    """
    
    def __init__(self, assets_dir: Path, logger: logging.Logger):
        """
        Inizializza il gestore delle UI.
        
        Args:
            assets_dir: Directory contenente i file delle interfacce HTML
            logger: Logger per la registrazione degli eventi
        """
        self.assets_dir = assets_dir
        self.logger = logger
        self.active_window: Optional[webview.Window] 
        self.window_mode: Optional[str] = None

    def _create_window(self, mode: str, api_instance) -> Optional[webview.Window]:
        try:
            # Chiudi la finestra precedente se esiste
            if self.active_window:
                self.close_window()

            # Crea la nuova finestra passando direttamente l'istanza api
            html_file = f"{mode}-ui.html"
            html_path = str(self.assets_dir / html_file)
            
            window = webview.create_window(
                f'NAIAD {mode.capitalize()}',
                html_path,
                width=800,
                height=800,
                resizable=True,
                js_api=api_instance  # Espone l'intera istanza API
            )

            self.active_window = window
            self.window_mode = mode
            
            self.logger.info(f"Creata nuova finestra {mode}")
            return window

        except Exception as e:
            self.logger.error(f"Errore apertura finestra {mode}: {e}")
            return None
        
    def _old_create_window(self, mode: str, api_instance) -> Optional[webview.Window]:
        """
        Crea una nuova finestra webview con le API esposte appropriate.
        
        Args:
            mode: Modalità della finestra ('artifacts' o 'chats')
            api_instance: Istanza dell'API da esporre alla finestra
            
        Returns:
            Window: L'oggetto finestra creato o None in caso di errore
        """
        html_file = f"{mode}-ui.html"
        html_path = str(self.assets_dir / html_file)
        
        try:
            window = webview.create_window(
                f'NAIAD {mode.capitalize()}',
                html_path,
                width=800,
                height=800,
                resizable=True,
                text_select=False
            )
            # Controllo che window sia la prima finestra in webview.windows
            if webview.windows and window != webview.windows[0]:
                # Se non lo è, la metto sposto in prima posizione
                webview.windows.remove(window)
                webview.windows.insert(0, window)


            # Espone le API necessarie in base alla modalità
            if mode == 'artifacts':
                window.expose(api_instance.list_artifacts)
                window.expose(api_instance.read_artifact)
                window.expose(api_instance.resume_creative_artifact)
                window.expose(api_instance.resume_article_artifact)
                window.expose(api_instance.delete_artifact)
                window.expose(api_instance.read_artifacts_page)
            elif mode == 'chats':
                window.expose(api_instance.list_chats)
                window.expose(api_instance.read_chat)
                window.expose(api_instance.delete_chat)
                window.expose(api_instance.resume_chat)
                window.expose(api_instance.read_chats_page)

            # API comuni per tutte le modalità
            window.expose(api_instance.tts_speak)
            window.expose(api_instance.tts_stop)
            window.expose(api_instance.tts_restart)
            window.expose(api_instance.tts_resume)
            window.expose(api_instance.tts_pause)
            window.expose(api_instance.close_window)

            # Salva il riferimento alla finestra attiva e la modalità
            self.active_window = window
            self.window_mode = mode

            return window
            
        except Exception as e:
            self.logger.error(f"Errore creazione finestra {mode}: {e}")
            return None

    def close_window(self) -> dict:
        """
        Chiude la finestra corrente e pulisce le risorse associate.
        Può essere chiamato sia dall'interfaccia utente che internamente.
        
        Returns:
            dict: Risultato dell'operazione per l'interfaccia JavaScript
        """
        try:
            if self.active_window:
                self.active_window.destroy()
                self.active_window = None
                self.window_mode = None
                self.logger.info("Finestra chiusa correttamente")
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Errore durante la chiusura della finestra: {e}")
            return {'success': False, 'error': str(e)}

    def show_window(self, mode: str, api_instance) -> bool:
        """
        Mostra una finestra UI, chiudendo quella precedente se esistente.
        
        Args:
            mode: Tipo di finestra da mostrare ('artifacts' o 'chats')
            api_instance: Istanza dell'API da esporre alla finestra
            
        Returns:
            bool: True se la finestra è stata creata con successo
        """
        try:
            # Chiudi la finestra precedente se esiste
            if self.active_window:
                self.close_window()

            # Crea la nuova finestra
            if self._create_window(mode, api_instance):
                self.logger.info(f"Creata nuova finestra {mode}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Errore apertura finestra {mode}: {e}")
            return False

    def has_active_window(self) -> bool:
        """
        Verifica se c'è una finestra attiva.
        
        Returns:
            bool: True se esiste una finestra attiva
        """
        return self.active_window is not None

    def cleanup(self):
        """
        Pulisce tutte le risorse e chiude eventuali finestre attive.
        Da chiamare durante lo shutdown dell'applicazione.
        """
        if self.active_window:
            self.close_window()
            self.logger.info("Pulizia UIManager completata")