# trigger_processor.py
import threading
import time
import logging
from pathlib import Path
from naiad.ai.base import SessionStyle

class TriggerProcessor(threading.Thread):
    """Thread dedicato alla gestione dei trigger file"""
    
    def __init__(self, app):
        super().__init__(daemon=True, name="TriggerProcessor")
        self.app = app
        self.running = True
        self.logger = app.logger

    def run(self):
        """Loop principale per la gestione dei trigger"""
        while self.running:
            try:
                # Gestione dei file trigger
                trigger_files = self.app.trigger_files

                if trigger_files["clean_history"].exists():
                    try:
                        self.app.context["history"] = []
                    finally:
                        trigger_files["clean_history"].unlink(missing_ok=True)
                elif trigger_files["process"].exists():
                    try:
                        self.app.process_clipboard()
                    finally:
                        trigger_files["process"].unlink(missing_ok=True)
                # Gestione modalità
                elif trigger_files["mode_chat"].exists():
                    try:
                        self.app.handle_mode(SessionStyle.CHAT)
                    finally:
                        trigger_files["mode_chat"].unlink(missing_ok=True)
                elif trigger_files["mode_explore"].exists():
                    try:
                        self.app.handle_mode(SessionStyle.EXPLORATION)
                    finally:
                        trigger_files["mode_explore"].unlink(missing_ok=True)
                elif trigger_files["mode_translate"].exists():
                    try:
                        self.app.handle_mode(SessionStyle.TRANSLATION)
                    finally:
                        trigger_files["mode_translate"].unlink(missing_ok=True)
                elif trigger_files["mode_write"].exists():
                    try:
                        self.app.handle_mode(SessionStyle.ARTICLE_WRITING)
                    finally:
                        trigger_files["mode_write"].unlink(missing_ok=True)
                elif trigger_files["mode_create"].exists():
                    try:
                        self.app.handle_mode(SessionStyle.CREATIVE_WRITING)
                    finally:
                        trigger_files["mode_create"].unlink(missing_ok=True)
                # Controlli TTS
                elif trigger_files['tts_pause'].exists():
                    try:
                        self.app.tts.pause()
                    finally:    
                        trigger_files['tts_pause'].unlink(missing_ok=True)
                elif trigger_files['tts_resume'].exists():
                    try:
                        self.app.tts.resume()
                    finally:
                        trigger_files['tts_resume'].unlink(missing_ok=True)
                elif trigger_files['tts_stop'].exists():
                    try:
                        self.app.tts.stop()
                    finally:
                        trigger_files['tts_stop'].unlink(missing_ok=True)
                elif trigger_files['tts_restart'].exists():
                    try:
                        self.app.tts.restart()
                    finally:
                        trigger_files['tts_restart'].unlink(missing_ok=True)
                # Controllo translate
                elif trigger_files['retry'].exists():
                    try:
                        self.app.retryTranslation()
                    finally:
                        trigger_files['retry'].unlink(missing_ok=True)
                # Gestione artefatti e chat
                elif trigger_files['print_artifact'].exists():
                    try:
                        self.app.print_session_content()
                    finally:
                        trigger_files['print_artifact'].unlink(missing_ok=True)
                elif trigger_files['list_artifact'].exists():
                    try:
                        self.app.list_artifact()
                    finally:
                        trigger_files['list_artifact'].unlink(missing_ok=True)
                elif trigger_files['read_artifact'].exists():
                    try:
                        self.app.read_artifact()
                    finally:
                        trigger_files['read_artifact'].unlink(missing_ok=True)
                elif trigger_files['resume_creative_artifact'].exists():
                    try:
                        self.app.resume_creative_artifact()
                    finally:
                        trigger_files['resume_creative_artifact'].unlink(missing_ok=True)
                elif trigger_files['resume_article_artifact'].exists():
                    try:
                        self.app.resume_article_artifact()
                    finally:
                        trigger_files['resume_article_artifact'].unlink(missing_ok=True)
                elif trigger_files['delete_artifact'].exists():
                    try:
                        self.app.delete_artifact()
                    finally:
                        trigger_files['delete_artifact'].unlink(missing_ok=True)
                elif trigger_files['save_chat'].exists():
                    try:
                        self.app.save_current_chat()
                    finally:
                        trigger_files['save_chat'].unlink(missing_ok=True)
                elif trigger_files['list_chats'].exists():
                    try:
                        self.app.list_saved_chats()
                    finally:
                        trigger_files['list_chats'].unlink(missing_ok=True)
                elif trigger_files['read_chat'].exists():
                    try:
                        self.app.read_saved_chat()
                    finally:
                        trigger_files['read_chat'].unlink(missing_ok=True)
                elif trigger_files['resume_chat'].exists():
                    try:
                        self.app.resume_saved_chat()
                    finally:
                        trigger_files['resume_chat'].unlink(missing_ok=True)
                elif trigger_files['delete_chat'].exists():
                    try:
                        self.app.delete_chat()
                    finally:
                        trigger_files['delete_chat'].unlink(missing_ok=True)
                elif trigger_files['prepare_whatsapp'].exists():
                    try:
                        self.app.prepare_whatsapp_message()
                    finally:
                        trigger_files['prepare_whatsapp'].unlink(missing_ok=True)

                # Breve pausa per ridurre l'uso della CPU
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Errore nel processamento trigger: {e}")

    def stop(self):
        """Ferma il thread di processamento"""
        self.running = False
        self.logger.info("TriggerProcessor fermato")