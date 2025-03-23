import sys
import os
import webview
import json
from pathlib import Path
from typing import Optional, List, Dict
import logging
from datetime import datetime

from naiad.utils.logger import setup_logger
from naiad.core.environment import env
from naiad.core.artifact_manager import ArtifactManager
from naiad.core.chat_manager import ChatManager
from naiad.utils.tts_provider import GTTSProvider
from naiad.ai.base import SessionStyle

class NAIADUI:
    def __init__(self):
        self.logger = setup_logger('naiad.ui')
        self.window = None
        self.artifact_manager = ArtifactManager(env.data_root, self.logger)
        self.chat_manager = ChatManager(self.logger)
        self.tts = GTTSProvider(self.logger)

    def expose_api(self):
        """Espone le API JavaScript per l'interfaccia web"""
        return {
            # API Artefatti
            'listArtifacts': self.list_artifacts,
            'readArtifact': self.read_artifact,
            'resumeCreativeArtifact': self.resume_creative_artifact,
            'resumeArticleArtifact': self.resume_article_artifact,
            'deleteArtifact': self.delete_artifact,
            
            # API Chat
            'listChats': self.list_chats,
            'readChat': self.read_chat,
            'resumeChat': self.resume_chat,
            'deleteChat': self.delete_chat,
            
            # API TTS
            'ttsPlay': self.tts.speak,
            'ttsPause': self.tts.pause,
            'ttsResume': self.tts.resume,
            'ttsStop': self.tts.stop,
            'ttsRestart': self.tts.restart
        }

    def list_artifacts(self) -> List[Dict]:
        """Lista gli artefatti per l'interfaccia web"""
        try:
            artifacts = self.artifact_manager.get_artifacts_list()
            self.logger.info(f"Trovati {len(artifacts)} artefatti")
            return [
                {
                    'name': name,
                    'date': date.isoformat(),
                    'number': idx + 1
                }
                for idx, (name, date) in enumerate(artifacts)
            ]
        except Exception as e:
            self.logger.error(f"Errore lista artefatti: {e}")
            return []

    def read_artifact(self, number: int) -> Dict:
        """Legge un artefatto dato il suo numero"""
        try:
            filename, content = self.artifact_manager.get_artifact_by_number(number)
            self.tts.speak(content)
            return {'success': True, 'content': content}
        except Exception as e:
            self.logger.error(f"Errore lettura artefatto: {e}")
            return {'success': False, 'error': str(e)}

    def resume_creative_artifact(self, number: int) -> Dict:
        """Riprende un artefatto in modalità creativa"""
        try:
            filename, content = self.artifact_manager.get_artifact_by_number(number)
            # Crea file trigger per NAIAD
            (env.comm_dir / 'mode_create').touch()
            (env.comm_dir / 'process_clipboard').touch()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Errore ripresa artefatto creativo: {e}")
            return {'success': False, 'error': str(e)}

    def resume_article_artifact(self, number: int) -> Dict:
        """Riprende un artefatto in modalità articolo"""
        try:
            filename, content = self.artifact_manager.get_artifact_by_number(number)
            # Crea file trigger per NAIAD
            (env.comm_dir / 'mode_write').touch()
            (env.comm_dir / 'process_clipboard').touch()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Errore ripresa artefatto articolo: {e}")
            return {'success': False, 'error': str(e)}

    def delete_artifact(self, number: int) -> Dict:
        """Cancella un artefatto"""
        try:
            filename, _ = self.artifact_manager.get_artifact_by_number(number)
            success = self.artifact_manager.delete_artifact(filename)
            return {'success': success}
        except Exception as e:
            self.logger.error(f"Errore cancellazione artefatto: {e}")
            return {'success': False, 'error': str(e)}

    def list_chats(self) -> List[Dict]:
        """Lista le chat per l'interfaccia web"""
        try:
            chats = self.chat_manager.get_chats_list()
            return [
                {
                    'name': name,
                    'type': style.value,
                    'date': date.isoformat(),
                    'number': idx + 1
                }
                for idx, (name, style, date) in enumerate(chats)
            ]
        except Exception as e:
            self.logger.error(f"Errore lista chat: {e}")
            return []

    def read_chat(self, number: int) -> Dict:
        """Legge una chat dato il suo numero"""
        try:
            filename, style, history = self.chat_manager.get_chat_by_number(number)
            # Trova l'ultima risposta
            last_response = None
            for msg in reversed(history):
                if msg['role'] == 'assistant':
                    last_response = msg['content']
                    break
            if last_response:
                self.tts.speak(last_response)
            return {'success': True, 'content': last_response}
        except Exception as e:
            self.logger.error(f"Errore lettura chat: {e}")
            return {'success': False, 'error': str(e)}

    def resume_chat(self, number: int) -> Dict:
        """Riprende una chat"""
        try:
            filename, style, history = self.chat_manager.get_chat_by_number(number)
            # Crea file trigger per NAIAD
            (env.comm_dir / f'mode_{style.value}').touch()
            (env.comm_dir / 'resume_chat').touch()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Errore ripresa chat: {e}")
            return {'success': False, 'error': str(e)}

    def delete_chat(self, number: int) -> Dict:
        """Cancella una chat"""
        try:
            success, filename = self.chat_manager.delete_chat_by_number(number)
            return {'success': success}
        except Exception as e:
            self.logger.error(f"Errore cancellazione chat: {e}")
            return {'success': False, 'error': str(e)}

    def run(self, mode: str = 'artifacts'):
        """Avvia l'interfaccia utente"""
        try:
            # Carica l'HTML appropriato
            html_file = 'artifacts-ui.html' if mode == 'artifacts' else 'chats-ui.html'
            html_path = str(env.assets_dir / html_file)
         
             # Verifica che il file HTML esista
            if not os.path.exists(html_path):
                raise FileNotFoundError(f"File HTML non trovato: {html_path}")
            
            self.logger.info(f"Caricamento interfaccia da: {html_path}")
            # Crea la finestra
            self.window = webview.create_window(
                'NAIAD UI',
                html_path,
                js_api=self.expose_api(),
                width=800,
                height=600,
                resizable=True,
                text_select=False
            )
            
            # Avvia il loop principale
            webview.start(debug=True)
            
        except Exception as e:
            self.logger.error(f"Errore avvio UI: {e}")
            sys.exit(1)
        finally:
            self.cleanup()

    def cleanup(self):
        """Pulizia risorse"""
        try:
            if self.tts:
                self.tts.cleanup()
        except Exception as e:
            self.logger.error(f"Errore pulizia: {e}")

def main():
    """Entry point"""
    # Parsing argomenti
    mode = 'artifacts'  # default
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode not in ['artifacts', 'chats']:
            print(f"Modalità non valida: {mode}")
            sys.exit(1)
    
    # Avvia UI
    ui = NAIADUI()
    ui.run(mode)

if __name__ == '__main__':
    main()