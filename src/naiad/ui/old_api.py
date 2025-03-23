import pyperclip
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

class Api:
    """
    Classe che espone le funzionalità del backend alle interfacce UI.
    Ora opera direttamente con NAIADApplication invece che con NAIADUI.
    """
    def __init__(self, app):
        """
        Inizializza l'API con riferimento all'applicazione principale
        
        Args:
            app: Istanza di NAIADApplication
        """
        self.app = app  # Riferimento all'applicazione principale
        self.logger = app.logger  # Logger condiviso
        self.comm_dir = app.comm_dir  # Directory per la comunicazione

    # Metodi TTS (Text-to-Speech)
    def tts_speak(self, text: str):
        """Sintetizza il testo in voce"""
        try:
            self.app.tts.speak(text)
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error speaking text: {e}")
            return {'success': False, 'error': str(e)}

    def tts_stop(self):
        """Ferma la sintesi vocale"""
        try:
            self.app.tts.stop()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error stopping TTS: {e}")
            return {'success': False, 'error': str(e)}

    def tts_pause(self):
        """Mette in pausa la sintesi vocale"""
        try:
            self.app.tts.pause()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error pausing TTS: {e}")
            return {'success': False, 'error': str(e)}

    def tts_resume(self):
        """Riprende la sintesi vocale"""
        try:
            self.app.tts.resume()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error resuming TTS: {e}")
            return {'success': False, 'error': str(e)}

    def tts_restart(self):
        """Riavvia la sintesi vocale"""
        try:
            self.app.tts.restart()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error restarting TTS: {e}")
            return {'success': False, 'error': str(e)}

    # Metodi per la gestione degli artefatti
    def list_artifacts(self):
        """Recupera la lista degli artefatti salvati"""
        try:
            artifacts = self.app.artifact_manager.get_artifacts_list()
            self.logger.info(f"Found {len(artifacts)} artifacts")
            
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
        
    def read_artifacts_page(self, items, total_count):
        """
        Legge vocalmente il contenuto di una pagina di artefatti.
        Interrompe qualsiasi lettura precedente prima di iniziare.
        """
        try:
            # Prima ferma qualsiasi lettura in corso
            self.app.tts.stop()
            
            # Prepara il messaggio introduttivo
            intro = f"Trovati {total_count} artefatti totali. "
            if not items:
                self.app.tts.speak(intro + "Nessun artefatto in questa pagina.")
                return {'success': True}

            # Prepara la lista degli artefatti nella pagina
            artifacts_text = []
            # Enumerate parte da 1
            for idx, item in enumerate(items, 1):
                name = item['name'].rsplit('.', 1)[0]  # Rimuove l'estensione
                date = datetime.fromisoformat(item['date']).strftime("%d/%m/%Y alle %H:%M")
                artifacts_text.append(f"Numero {idx}: {name}, salvato il {date}")

            # Legge il messaggio completo
            message = intro + "In questa pagina: " + ". ".join(artifacts_text)
            self.app.tts.speak(message)
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Error reading artifacts page: {e}")
            return {'success': False, 'error': str(e)}


    def read_artifact(self, number):
        """Legge un artefatto specifico"""
        try:
            filename, content = self.app.artifact_manager.get_artifact_by_number(number)
            self.app.tts.speak(content)
            return {'success': True, 'content': content}
        except Exception as e:
            self.logger.error(f"Error reading artifact: {e}")
            return {'success': False, 'error': str(e)}

    def resume_creative_artifact(self, number):
        """Riprende un artefatto in modalità creativa"""
        try:
            # Usa il metodo esistente di NAIADApplication
            pyperclip.copy(str(number))
            resume_file = self.comm_dir / 'resume_creative_artifact'
            resume_file.touch()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error resuming creative artifact: {e}")
            return {'success': False, 'error': str(e)}

    def resume_article_artifact(self, number):
        """Riprende un artefatto in modalità articolo"""
        try:
            pyperclip.copy(str(number))
            resume_file = self.comm_dir / 'resume_article_artifact'
            resume_file.touch()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error resuming article artifact: {e}")
            return {'success': False, 'error': str(e)}

    def delete_artifact(self, number):
        """Elimina un artefatto"""
        try:
            filename, _ = self.app.artifact_manager.get_artifact_by_number(number)
            success = self.app.artifact_manager.delete_artifact(filename)
            if success:
                self.app.tts.speak(f"Artefatto {filename} cancellato con successo")
            return {'success': success}
        except Exception as e:
            self.logger.error(f"Error deleting artifact: {e}")
            return {'success': False, 'error': str(e)}

    # Metodi per la gestione delle chat
    def list_chats(self):
        """Recupera la lista delle chat salvate"""
        try:
            chats = self.app.chat_manager.get_chats_list()
            #self.logger.info(f"Found {len(chats)} chats")
            
            result = [
                {
                    'name': name,
                    'date': date.isoformat(),
                    'number': idx + 1,
                    'type': style.value
                }
                for idx, (name, style, date) in enumerate(chats)
            ]
            return result
        except Exception as e:
            self.logger.error(f"Error listing chats: {e}")
            return []

    def read_chats_page(self, items, total_count):
        """
        Legge vocalmente il contenuto di una pagina di chat.
        Interrompe qualsiasi lettura precedente prima di iniziare.
        """
        try:
            # Prima ferma qualsiasi lettura in corso
            self.app.tts.stop()
            
            # Mappa dei nomi degli stili
            style_names = {
                'translation': 'traduzione',
                'chat': 'chat',
                'exploration': 'esplorazione',
                'creative_writing': 'scrittura creativa',
                'article_writing': 'scrittura articoli'
            }

            # Prepara il messaggio introduttivo
            intro = f"Trovate {total_count} chat totali. "
            if not items:
                self.app.tts.speak(intro + "Nessuna chat in questa pagina.")
                return {'success': True}

            # Prepara la lista delle chat nella pagina
            chats_text = []
            for idx, item in enumerate(items, 1):
                name = item['name'].rsplit('.', 1)[0]  # Rimuove l'estensione
                date = datetime.fromisoformat(item['date']).strftime("%d/%m/%Y alle %H:%M")
                style = style_names.get(item['type'], item['type'])
                chats_text.append(f"Numero {idx}: {name}, {style}, salvata il {date}")

            # Legge il messaggio completo
            message = intro + "In questa pagina: " + ". ".join(chats_text)
            self.app.tts.speak(message)
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Error reading chats page: {e}")
            return {'success': False, 'error': str(e)}

    def read_chat(self, number):
        """Legge l'ultima risposta di una chat"""
        try:
            filename, style, history = self.app.chat_manager.get_chat_by_number(number)
            
            last_response = None
            for message in reversed(history):
                if message['role'] == 'assistant':
                    last_response = message['content']
                    break
            
            if last_response:
                self.app.tts.speak(last_response)
                return {'success': True, 'content': last_response}
            else:
                error_msg = "No assistant response found in chat"
                self.logger.warning(error_msg)
                return {'success': False, 'error': error_msg}
        except Exception as e:
            self.logger.error(f"Error reading chat: {e}")
            return {'success': False, 'error': str(e)}

    def resume_chat(self, number):
        """Riprende una chat salvata"""
        try:
            pyperclip.copy(str(number))
            resume_file = self.comm_dir / 'resume_chat'
            resume_file.touch()
            return {'success': True}
        except Exception as e:
            self.logger.error(f"Error resuming chat: {e}")
            return {'success': False, 'error': str(e)}

    def delete_chat(self, number):
        """Elimina una chat salvata"""
        try:
            success, filename = self.app.chat_manager.delete_chat_by_number(number)
            if success:
                self.app.tts.speak(f"Chat {filename} eliminata con successo")
            return {'success': success}
        except Exception as e:
            self.logger.error(f"Error deleting chat: {e}")
            return {'success': False, 'error': str(e)}

    def close_window(self):
        """
        Chiude la finestra UI corrente usando il metodo del UIManager
        """
        return self.app.ui_manager.close_window()