import sys
import os
import webview
import json
from pathlib import Path
from typing import Optional, List, Dict
import logging
from datetime import datetime
import pyperclip
import webview.platforms

from naiad.utils.logger import setup_logger
from naiad.core.environment import env
from naiad.core.artifact_manager import ArtifactManager
from naiad.core.chat_manager import ChatManager
from naiad.utils.tts_provider import GTTSProvider
from naiad.ai.base import SessionStyle

class UIApi:
    def __init__(self, ui):
        self.ui = ui
        self.logger = ui.logger
        self.comm_dir = env.data_root / 'comm'
    
    def tts_speak(self, text: str):
        try:
            self.ui.tts.speak(text)
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error speaking text: {e}")
            return {'success': False, 'error': str(e)}

    def tts_stop(self):
        try:
            self.ui.tts.stop()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error stopping TTS: {e}")
            return {'success': False, 'error': str(e)}

    def tts_pause(self):
        try:
            self.ui.tts.pause()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error pausing TTS: {e}")
            return {'success': False, 'error': str(e)}

    def tts_resume(self):
        try:
            self.ui.tts.resume()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error resuming TTS: {e}")
            return {'success': False, 'error': str(e)}

    def tts_restart(self):
        try:
            self.ui.tts.restart()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error restarting TTS: {e}")
            return {'success': False, 'error': str(e)}
   
    def list_artifacts(self):
        try:
            artifacts = self.ui.artifact_manager.get_artifacts_list()
            #self.logger.info(f"Found {len(artifacts)} artifacts")
            
            result = [
                {
                    'name': name,
                    'date': date.isoformat(),
                    'number': idx + 1
                }
                for idx, (name, date) in enumerate(artifacts)
            ]
            return result
        except Exception as e:
            self.logger.error(f"Error listing artifacts: {e}")
            return []
            
    def read_artifact(self, number):
        try:
            filename, content = self.ui.artifact_manager.get_artifact_by_number(number)
            self.ui.tts.speak(content)
            return {'success': True, 'content': content}
        except Exception as e:
            self.logger.error(f"Error reading artifact: {e}")
            return {'success': False, 'error': str(e)}
            
   
    def resume_creative_artifact(self, number):
        try:
            # Copia l'indice nella clipboard
            pyperclip.copy(str(number))
            
            # Crea il trigger per resume_creative_artifact
            resume_file = self.comm_dir / 'resume_creative_artifact'
            resume_file.touch()
          
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error resuming creative artifact: {e}")
            return {'success': False, 'error': str(e)}
            
    def resume_article_artifact(self, number):
        try:
            # Copia l'indice nella clipboard
            pyperclip.copy(str(number))
            
            # Crea il trigger per resume_article_artifact
            resume_file = self.comm_dir / 'resume_article_artifact'
            resume_file.touch()
                       
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error resuming article artifact: {e}")
            return {'success': False, 'error': str(e)}
            
    def delete_artifact(self, number):
        try:
            filename, _ = self.ui.artifact_manager.get_artifact_by_number(number)
            success = self.ui.artifact_manager.delete_artifact(filename)
            self.ui.tts.speak("Articolo {filename} cancellato con successo")
            return {'success': success}
        except Exception as e:
            self.logger.error(f"Error deleting artifact: {e}")
            return {'success': False, 'error': str(e)}
            
    def list_chats(self):
        """Lists all saved chats with their metadata"""
        try:
            # Get list of chats with their style and date
            chats = self.ui.chat_manager.get_chats_list()
            #self.logger.info(f"Found {len(chats)} chats")
            
            # Transform into the format expected by the UI
            result = [
                {
                    'name': name,
                    'date': date.isoformat(),
                    'number': idx + 1,
                    'type': style.value  # Add chat style type
                }
                for idx, (name, style, date) in enumerate(chats)
            ]
            return result
        except Exception as e:
            self.logger.error(f"Error listing chats: {e}")
            return []
            
    def read_chat(self, number):
        """Reads the last AI response from the chat history"""
        try:
            # Get chat content
            filename, style, history = self.ui.chat_manager.get_chat_by_number(number)
            
            # Find the last assistant message
            last_response = None
            for message in reversed(history):
                if message['role'] == 'assistant':
                    last_response = message['content']
                    break
            
            if last_response:
                # Speak only the last response
                self.ui.tts.speak(last_response)
                return {'success': True, 'content': last_response}
            else:
                error_msg = "No assistant response found in chat"
                self.logger.warning(error_msg)
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.logger.error(f"Error reading chat: {e}")
            return {'success': False, 'error': str(e)}
        
    def resume_chat(self, number):
        try:
            # Copia l'indice nella clipboard
            pyperclip.copy(str(number))
            
            # Crea il trigger per resume_chat
            resume_file = self.comm_dir / 'resume_chat'
            resume_file.touch()
            
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error resuming chat: {e}")
            return {'success': False, 'error': str(e)}      

    def delete_chat(self, number):
        """Deletes a chat by its number"""
        try:
            success, filename = self.ui.chat_manager.delete_chat_by_number(number)
            if success:
                self.ui.tts.speak(f"Chat {filename} eliminata con successo")
            return {'success': success}
        except Exception as e:
            self.logger.error(f"Error deleting chat: {e}")
            return {'success': False, 'error': str(e)}

    def close_window(self):
        try:
            if self.ui.window:
                self.ui.window.destroy()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
            return {'success': False, 'error': str(e)}

class NAIADUI:
    def __init__(self):
        self.logger = setup_logger('naiad.ui')
        self.window = None
        self.artifact_manager = ArtifactManager(env.data_root, self.logger)
        self.chat_manager = ChatManager(self.logger)
        self.tts = GTTSProvider(self.logger)
        self.api = UIApi(self)

    def set_clipboard_content(self, content: str):
        """Wrapper per gestione clipboard"""
        import pyperclip
        try:
            pyperclip.copy(content)
        except Exception as e:
            self.logger.error(f"Errore impostando la clipboard: {e}")

    def run(self, mode: str = 'artifacts'):
        """Avvia l'interfaccia utente"""
        try:
            # Carica l'HTML appropriato
            html_file = 'artifacts-ui.html' if mode == 'artifacts' else 'chats-ui.html'
            html_path = str(env.assets_dir / html_file)
            icon_path = str(env.assets_dir / 'AsinoVolante.ico')

            # Verifica che il file HTML esista
            if not os.path.exists(html_path):
                raise FileNotFoundError(f"File HTML non trovato: {html_path}")
            
            self.logger.info(f"Caricamento interfaccia da: {html_path}")
            
            # Crea e configura la finestra
            self.window = webview.create_window(
                'NAIAD UI',
                html_path,
                width=800,
                height=800,
                resizable=True,
                text_select=False
            )
            
            if (mode == 'chats'):
                self._expose_chat_api()
            else:
                self._expose_artifact_api()
            # Espone i metodi del tts locale
            self.window.expose(self.api.tts_speak)
            self.window.expose(self.api.tts_stop)
            self.window.expose(self.api.tts_restart)
            self.window.expose(self.api.tts_resume)
            self.window.expose(self.api.tts_pause)
            self.window.expose(self.api.close_window)
            # Avvia il loop principale
            self.logger.info("Starting webview...")
            webview.start(debug=False)
            
        except Exception as e:
            self.logger.error(f"Errore avvio UI: {e}")
            sys.exit(1)
        finally:
            self.cleanup()

    def _expose_artifact_api(self):
        self.window.expose(self.api.list_artifacts)
        self.window.expose(self.api.read_artifact)
        self.window.expose(self.api.resume_creative_artifact)
        self.window.expose(self.api.resume_article_artifact)
        self.window.expose(self.api.delete_artifact)
       
    def _expose_chat_api(self):
        self.window.expose(self.api.list_chats)
        self.window.expose(self.api.read_chat)
        self.window.expose(self.api.delete_chat)
        self.window.expose(self.api.resume_chat)    
            

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