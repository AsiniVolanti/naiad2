# naiad/core/main.py
# naiad/core/main.py
"""Main application module for NAIAD"""
import sys
import time
import logging
import signal
import os
import ctypes
import pyperclip
import win32con
import win32api
from pathlib import Path
import yaml
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime
import json
import keyboard
import webview

# Move imports to avoid circularity
from naiad.utils.logger import setup_logger
from naiad.utils.tts_provider import GTTSProvider
from naiad.utils.local_tts_provider import LocalTTSProvider
from naiad.core.environment import env
from naiad.core.exit_handler import ExitHandler
from naiad.config.settings import Settings
from naiad.ai.base import ChatContext, SessionStyle
from naiad.ai.anthropic_provider import AnthropicProvider
from naiad.core.chat_manager import ChatManager
from naiad.core.artifact_manager import ArtifactManager
from naiad.core.trigger_processor import TriggerProcessor
from naiad.ui.api import Api

class NAIADApplication:
    def __init__(self):
        self.running = False
        self.logger = None
        self.base_dir = Path("C:/ProgramData/NAIAD")
        # Carico la configurazione
        self.settings = Settings()
        
        # Directory di comunicazione
        self.comm_dir = self.base_dir / "comm"
        # File di trigger
        self.trigger_files = {
            'process': self.comm_dir / "process_clipboard",
            'clean_history' : self.comm_dir / "clean_history",
            # Modalità sessione
            'mode_chat': self.comm_dir / "mode_chat",
            'mode_explore': self.comm_dir / "mode_explore",
            'mode_translate': self.comm_dir / "mode_translate",
            'mode_write': self.comm_dir / "mode_write",
            'mode_create': self.comm_dir / "mode_create",
            # Controlli TTS
            'tts_pause': self.comm_dir / "tts_pause",
            'tts_resume': self.comm_dir / "tts_resume",
            'tts_stop': self.comm_dir / "tts_stop",
            'tts_restart': self.comm_dir / "tts_restart",
            # Controllo translate
            'retry': self.comm_dir / "retry",
            #Controllo artefatti
            'print_artifact': self.comm_dir / "print_artifact",
            'list_artifact': self.comm_dir / "list_artifact",
            'resume_creative_artifact': self.comm_dir / "resume_creative_artifact",
            'resume_article_artifact': self.comm_dir / "resume_article_artifact",
            'delete_artifact': self.comm_dir / "delete_artifact",    
            'read_artifact': self.comm_dir / "read_artifact",
            'prepare_whatsapp': self.comm_dir / "prepare_whatsapp"

        }

        # Modifica i file trigger per la gestione delle chat
        self.trigger_files.update(
            {
            'save_chat': self.comm_dir / "save_chat",      # Salva la chat corrente
            'list_chats': self.comm_dir / "list_chats",    # Lista tutte le chat
            'read_chat': self.comm_dir / "read_chat",      # Legge una chat specifica
            'resume_chat': self.comm_dir / "resume_chat",    # Riprende una chat specifica
            'delete_chat': self.comm_dir / "delete_chat"    # Cancella una chat specifica
            }
         )

        self.lock_file = self.base_dir / "naiad.lock"

        # Inizializza TTS e Orchestrator
        self.tts = None  # Inizializzato in setup
        self.ai = None  # Inizializzato in setup
        
        self.current_session = None
        
        self.API_KEY = self.settings.anthropic_api_key
        
        # Stato applicazione
        self.current_mode = SessionStyle.TRANSLATION
        self.chat_context = ChatContext(
            platform="direct",
            participants=["Nicola", "Claude"],
            tone="informal",
            max_length=200
        )

        self.context = {
            "style": self.current_mode,
            "chat_context": self.chat_context,
            
            "translation_examples": [
            {
                "grid_content":"IO OGGI FELICE PROVARE NUOVO PROGRAMMA CERVELLO AIUTARE SCRIVERE ITALIANO BELLO",
                "italian_translation":"Oggi sono felice perchè ho iniziato ad usare un nuovo programma di AI, che mi aiuta a scrivere in un italiano corretto"
            },
            {
                "grid_content":"QUANDO TU LIBERTA' GIORNO DOMANDA",
                "italian_translation":"Quando sei disponibile ?"
            },
            {
                "grid_content":"SABATO TU VENIRE ORE DOMANDA",
                "italian_translation":"A che ora puoi venire sabato ?"
            }
        ],
            "history": [],
            "model_config": {} # Configurazione modello per la sessione corrente
        }

        self.current_chat_title = None  # Nuovo attributo per il titolo della chat corrente
        
        # Registra handler per la chiusura pulita
        self.exit_handler = None # Inizializzato in setup

        # Chat manager per sospensione e ripresa
        self.chat_manager = None
        
         # ArtifactManager per salvataggio artefatti
        self.artifact_manager = None

        self.api = None


    def setup(self):
        """Inizializza l'applicazione"""
        # Crea le directory necessarie
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.comm_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        log_dir = self.base_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Configura il logger
        self.logger = logging.getLogger('NAIAD')
        self.logger.setLevel(logging.INFO)
        
        # File handler con rotazione
        handler = logging.FileHandler(log_dir / "naiad.log", encoding='utf-8')
        handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        )
        self.logger.addHandler(handler)
        
        ## Inizializzo text to speech
        tts_config = self.settings.get('tts', {})
        tts_provider = tts_config.get('provider', 'gtts')
        tts_rate = int(tts_config.get('rate', 140))
        if tts_provider == 'gtts':
            self.tts = GTTSProvider(self.logger)
        else:
            self.tts = LocalTTSProvider(self.logger, rate = tts_rate)
            

        # Carica la configurazione iniziale del modello
        initial_config = self.settings.model_configs.get(self.current_mode.value, {})
        if not initial_config:
            self.logger.warning(f"No configuration found for initial mode {self.current_mode.value}")
            initial_config = {
                "model": self.settings.anthropic_default_model,
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }

        self.context["model_config"] = initial_config

        self.ai  = AnthropicProvider(api_key=self.settings.anthropic_api_key, 
                                    logger=self.logger)
                                    #model = self.settings.anthropic_model)

        self.exit_handler = ExitHandler("NAIAD", self.lock_file, self.logger)
        # Chat manager per sospensione e ripresa
        self.chat_manager = ChatManager(self.logger)
         # Inizializza ArtifactManager
        self.artifact_manager = ArtifactManager(self.base_dir, self.logger)
        self.api = Api(self)

    def print_session_content(self):
        """Gestisce il comando STAMPA salvando l'artefatto della sessione"""
        try:
            if not self.context["history"]:
                response = "Nessun contenuto disponibile nella sessione corrente."
                self.tts.speak(response)
                return
                
            # Salva il contesto corrente
            original_history = self.context["history"].copy()
            
            # Invia il comando STAMPA all'AI mantenendo il contesto originale
            response = self.ai.generate_response("STAMPA", self.context)
            
            # Ripristina il contesto originale
            self.context["history"] = original_history
            
            # Legge il contenuto della clipboard per il titolo
            clipboard_content = self.get_clipboard_content().strip()
            
            # Determina il titolo da usare
            if 2 <= len(clipboard_content.split()) <= 5:
                # Usa il contenuto della clipboard se ha lunghezza appropriata
                title = clipboard_content
            elif self.current_chat_title:
                # Usa il titolo dell'artefatto precedente se disponibile
                title = self.current_chat_title
            else:
                # Estrarrà il titolo dal contenuto
                title = None

            try:
                # Salva l'artefatto
                saved_path = self.artifact_manager.save_artifact(
                    response.content, 
                    filename = title if title else None)
                success_msg = f"Ho salvato l'artefatto come {saved_path.name}"
            except IOError as e:
                self.logger.error(f"Errore salvataggio artefatto: {e}")
                success_msg = "Non sono riuscito a salvare l'artefatto, ma te lo mostro comunque"
            
            # Copia il contenuto nella clipboard
            self.set_clipboard_content(response.content)
            time.sleep(0.1)
            self.notify_grid3()
            
            # Comunica vocalmente
            self.tts.speak(f"{success_msg}... {response.content}")
            
        except Exception as e:
            self.logger.error(f"Errore durante la stampa del contenuto: {e}")
            error_msg = "Si è verificato un errore durante la stampa del contenuto."
            self.set_clipboard_content(error_msg)
            self.notify_grid3()
            self.tts.speak(error_msg)

    def list_artifact(self):
        """Elenca gli artefatti salvati"""
        try:
            # Ottieni la lista formattata
            response = self.artifact_manager.format_artifact_list()
            
            # Leggi la lista
            self.tts.speak(response)
            
            # Copia nella clipboard per riferimento
            self.notify_grid3()
            
        except Exception as e:
            self.logger.error(f"Errore durante la lettura degli artefatti: {e}")
            error_msg = "Si è verificato un errore durante la lettura degli artefatti."
            self.tts.speak(error_msg)
            
    def read_artifact(self):
        """Legge il contenuto di un artefatto specifico"""
        try:
            # Leggi il numero dell'artefatto dalla clipboard
            number_str = self.get_clipboard_content().strip()
            
            try:
                number = int(number_str)
            except ValueError:
                self.tts.speak("Per favore, specifica il numero dell'artefatto da leggere.")
                return
                
            try:
                # Recupera l'artefatto
                filename, content = self.artifact_manager.get_artifact_by_number(number)
                # Copia il contenuto nella clipboard
                self.set_clipboard_content(content)
                self.notify_grid3()
                
                # Leggi nome file e contenuto
                self.tts.speak(content)
                self.tts.speak(f"{filename}... {content}")
                
            except IndexError as e:
                self.tts.speak(str(e))
            except FileNotFoundError:
                self.tts.speak("L'artefatto richiesto non è più disponibile.")
                
        except Exception as e:
            self.logger.error(f"Errore durante la lettura dell'artefatto: {e}")
            error_msg = "Si è verificato un errore durante la lettura dell'artefatto."
            self.tts.speak(error_msg)       

    def resume_creative_artifact(self):
        """Gestisce il comando di ripresa creativa"""
        try:
            number = int(self.get_clipboard_content().strip())
            return self.api.resume_creative_artifact(number)
        except ValueError:
            self.tts.speak("Per favore, specifica il numero dell'artefatto da modificare")
        except Exception as e:
            self.logger.error(f"Errore durante la ripresa creativa: {e}")
            self.tts.speak("Si è verificato un errore durante la ripresa creativa")

    def resume_article_artifact(self):
        """Gestisce il comando di ripresa articolo"""
        try:
            number = int(self.get_clipboard_content().strip())
            return self.api.resume_article_artifact(number)
        except ValueError:
            self.tts.speak("Per favore, specifica il numero dell'artefatto da modificare")
        except Exception as e:
            self.logger.error(f"Errore durante la ripresa articolo: {e}")
            self.tts.speak("Si è verificato un errore durante la ripresa dell'articolo")

    def resume_saved_chat(self):
        """Gestisce il comando di ripresa chat"""
        try:
            number = int(self.get_clipboard_content().strip())
            return self.api.resume_chat(number)
        except ValueError:
            self.tts.speak("Per favore, specifica il numero della chat da riprendere")
        except Exception as e:
            self.logger.error(f"Errore durante la ripresa della chat: {e}")
            self.tts.speak("Si è verificato un errore durante la ripresa della chat")
        
    def delete_artifact(self):
        """
        Cancella un artefatto specificato dal suo numero.
        Il contenuto della clipboard deve contenere il numero dell'artefatto.
        """
        try:
            # Legge il numero dell'artefatto dalla clipboard
            try:
                artifact_number = int(self.get_clipboard_content().strip())
            except ValueError:
                self.tts.speak("Per favore, specifica il numero dell'artefatto da cancellare")
                return
                
            try:
                # Recupera il nome del file dell'artefatto
                filename, _ = self.artifact_manager.get_artifact_by_number(artifact_number)
                
                # Tenta la cancellazione
                if self.artifact_manager.delete_artifact(filename):
                    self.tts.speak(f"Artefatto {filename} cancellato con successo")
                else:
                    self.tts.speak("Non sono riuscito a cancellare l'artefatto")
                    
            except (IndexError, FileNotFoundError) as e:
                self.tts.speak(str(e))
                return
        except Exception as e:
            self.logger.error(f"Errore durante la cancellazione dell'artefatto: {e}")
            error_msg = "Si è verificato un errore durante la cancellazione dell'artefatto."
            self.tts.speak(error_msg)
        
    def save_current_chat(self):
        """Salva la chat corrente con titolo opzionale"""
        try:
            if not self.context["history"]:
                self.tts.speak("Non c'è contenuto da salvare nella sessione corrente")
                return
                
            # Legge il contenuto della clipboard per il titolo
            clipboard_content = self.get_clipboard_content().strip()
            
            # Determina il titolo da usare
            if 2 <= len(clipboard_content.split()) <= 5:
                # Usa il contenuto della clipboard se ha lunghezza appropriata
                title = clipboard_content
            elif self.current_chat_title:
                # Usa il titolo dell'artefatto precedente se disponibile
                title = self.current_chat_title
            else:
                # Estrarrà il titolo dal contenuto
                title = None
         
            saved_path = self.chat_manager.save_chat(
                style=self.current_mode,
                history=self.context["history"],
                title=title if title else None
            )
            
            style_name = self._get_style_name(self.current_mode)
            success_msg = f"Ho salvato la sessione di {style_name} come {saved_path.stem}"
            self.tts.speak(success_msg)
             
        except Exception as e:
            self.logger.error(f"Errore salvataggio chat: {e}")
            self.tts.speak("Si è verificato un errore durante il salvataggio della chat")

    
    def list_saved_chats(self):
        """Elenca le chat salvate, opzionalmente filtrate per lo stile corrente"""
        try:
            # Ottiene la lista formattata delle chat
            response = self.chat_manager.format_chats_list()
                #filter_style=self.current_mode  # Filtra per stile corrente
             #)
            
            # Comunica la lista vocalmente
            self.tts.speak(response)
            
            # Copia nella clipboard per riferimento
            #self.set_clipboard_content(response)
            self.notify_grid3()
            
        except Exception as e:
            self.logger.error(f"Errore lettura lista chat: {e}")
            self.tts.speak("Si è verificato un errore durante la lettura delle chat salvate")

    def read_saved_chat(self):
        """Legge una chat salvata dato il suo numero"""
        try:
            # Legge il numero dalla clipboard
            number_str = self.get_clipboard_content().strip()
            
            try:
                number = int(number_str)
            except ValueError:
                self.tts.speak("Per favore, specifica il numero della chat da leggere")
                return
                
            try:
                # Recupera la chat
                filename, style, history = self.chat_manager.get_chat_by_number(number)
                
                # Trova l'ultima risposta dell'assistente
                last_response = None
                for msg in reversed(history):
                    if msg["role"] == "assistant":
                        last_response = msg["content"]
                        break
                
                if last_response:
                    # Non copia l'ultima risposta nella clipboard
                    #self.set_clipboard_content(last_response)
                    #self.notify_grid3()
                    
                    # Comunica vocalmente
                    style_name = self._get_style_name(style)
                    response = f"Chat {filename.rsplit('.', 1)[0]} di tipo {style_name}. Ultima risposta: {last_response}"
                    self.tts.speak(response)
                else:
                    self.tts.speak("La chat non contiene risposte dell'assistente")
                
            except IndexError as e:
                self.tts.speak(str(e))
            except FileNotFoundError:
                self.tts.speak("La chat richiesta non è più disponibile")
                
        except Exception as e:
            self.logger.error(f"Errore lettura chat: {e}")
            self.tts.speak("Si è verificato un errore durante la lettura della chat")

    def delete_chat(self):
        """Elimina una chat salvata dato il suo numero"""
        try:
            # Legge il numero dalla clipboard
            number_str = self.get_clipboard_content().strip()
            
            try:
                number = int(number_str)
            except ValueError:
                self.tts.speak("Per favore, specifica il numero della chat da eliminare")
                return
                
            try:
                # Prova a eliminare la chat
                success, filename = self.chat_manager.delete_chat_by_number(number)
                
                if success:
                    chat_name = filename.rsplit('.', 1)[0]
                    self.tts.speak(f"Ho eliminato la chat {chat_name}")
                else:
                    self.tts.speak("Non sono riuscito a eliminare la chat")
                
            except IndexError as e:
                self.tts.speak(str(e))
                
        except Exception as e:
            self.logger.error(f"Errore eliminazione chat: {e}")
            self.tts.speak("Si è verificato un errore durante l'eliminazione della chat")

    def prepare_whatsapp_message(self):
        """Prepara un messaggio per WhatsApp basato sulla sessione corrente"""
        try:
            if not self.context["history"]:
                response = "Non c'è contenuto disponibile nella sessione corrente per preparare un messaggio."
                self.tts.speak(response)
                return
                
            # Salva il contesto corrente
            original_history = self.context["history"].copy()
            
            # Invia un comando specifico all'AI
            prompt = (
                "Prepara un messaggio WhatsApp basato sulla nostra conversazione. "
                "Il messaggio deve essere conciso, chiaro e adatto al contesto di una chat. "
                "Puoi includere emoji ma non formattazioni speciali. Non suggerire estensioni o modifiche"
            )
            
            # Genera la risposta mantenendo il contesto
            response = self.ai.generate_response(prompt, self.context)
            
            # Ripristina il contesto originale
            self.context["history"] = original_history
            
            # Legge vocalmente il messaggio preparato
            self.tts.speak("Ecco il messaggio pronto per WhatsApp: " + response.content)
            
            # Copia il risultato nella clipboard per facilitare l'incollaggio su WhatsApp
            self.set_clipboard_content(response.content)
            self.notify_grid3()
            
        except Exception as e:
            self.logger.error(f"Errore durante la preparazione del messaggio WhatsApp: {e}")
            error_msg = "Si è verificato un errore durante la preparazione del messaggio WhatsApp."
            self.tts.speak(error_msg)
            self.set_clipboard_content(error_msg)
            self.notify_grid3()

    def _get_style_name(self, style: SessionStyle) -> str:
        """Ottiene il nome in italiano della modalità"""
        style_names = {
            SessionStyle.TRANSLATION: "traduzione",
            SessionStyle.CHAT: "chat",
            SessionStyle.EXPLORATION: "esplorazione",
            SessionStyle.CREATIVE_WRITING: "scrittura creativa",
            SessionStyle.ARTICLE_WRITING: "scrittura articoli"
        }
        return style_names.get(style, str(style))
   

    def _create_lock_file(self) -> bool:
        """Gestisce il file di lock per single instance"""
        try:
            if self.lock_file.exists():
                # Verifica se il processo è ancora attivo
                pid = int(self.lock_file.read_text().strip())
                try:
                    # Su Windows, prova ad aprire il processo
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    handle = kernel32.OpenProcess(1, False, pid)
                    if handle:
                        kernel32.CloseHandle(handle)
                        self.logger.warning("NAIAD è già in esecuzione")
                        return False
                except (ValueError, OSError):
                    pass  # Il processo non esiste più
                
            # Crea nuovo file di lock
            self.lock_file.write_text(str(os.getpid()))
            return True
            
        except Exception as e:
            self.logger.error(f"Errore creazione lock file: {e}")
            return False

    def _cleanup(self):
        """Pulizia risorse"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
            #if self.trigger_file.exists():
            #    self.trigger_file.unlink()
        except Exception as e:
            self.logger.error(f"Errore pulizia: {e}")

    def get_clipboard_content(self) -> str:
        """Legge il contenuto della clipboard in modo silenzioso"""
        content = ""
        try:
            # Apre la clipboard in modo silenzioso usando CF_CLIPBOARD
            '''
            win32clipboard.OpenClipboard()
            try:
                # Prima prova il formato Unicode
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                # Se non disponibile, prova il testo normale
                elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                    content = win32clipboard.GetClipboardData(win32con.CF_TEXT).decode('cp1252')
            finally:
                win32clipboard.CloseClipboard()
            '''
            content = pyperclip.paste()    
        except Exception as e:
            self.logger.error(f"Errore lettura clipboard: {e}")
        
        return content.strip() if content else ""



    def set_clipboard_content(self, content: str):
        """Scrive sulla clipboard in modo silenzioso"""
        if not content:
            return
            
        try:
            # Apre la clipboard in modo silenzioso
            '''
            if win32clipboard.OpenClipboard():
                time.sleep(0.1)
                try:
                    # win32clipboard.EmptyClipboard()
                    # Usa CF_UNICODETEXT per supportare tutti i caratteri
                    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, content)
                    time.sleep(0.1)
                finally:
                    win32clipboard.CloseClipboard()
            '''
            pyperclip.copy(content)        
        except Exception as e:
            self.logger.error(f"Errore scrittura clipboard: {e}")

    def notify_grid3(self):
        """Notifica GRID3 simulando la pressione di F2 usando SendInput"""
        try:
            # Definizione delle strutture necessarie per SendInput
            KEYEVENTF_KEYUP = 0x0002
            INPUT_KEYBOARD = 1
            
            class KEYBDINPUT(ctypes.Structure):
                _fields_ = [
                    ("wVk", ctypes.c_ushort),
                    ("wScan", ctypes.c_ushort),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                ]

            class INPUT_UNION(ctypes.Union):
                _fields_ = [("ki", KEYBDINPUT)]

            class INPUT(ctypes.Structure):
                _fields_ = [
                    ("type", ctypes.c_ulong),
                    ("ii", INPUT_UNION)
                ]

            # Prepara l'input per F2 (VK_F2 = 0x71)
            x = INPUT(INPUT_KEYBOARD, INPUT_UNION(ki=KEYBDINPUT(0x71, 0, 0, 0, None)))
            x_up = INPUT(INPUT_KEYBOARD, INPUT_UNION(ki=KEYBDINPUT(0x71, 0, KEYEVENTF_KEYUP, 0, None)))
            
            # Invia l'input
            inputs = (INPUT * 2)(x, x_up)
            nInputs = len(inputs)
            cbSize = ctypes.c_int(ctypes.sizeof(INPUT))
            ctypes.windll.user32.SendInput(nInputs, ctypes.pointer(inputs), cbSize)
            
        except Exception as e:
            self.logger.error(f"Errore invio F2: {e}")


    def process_clipboard(self):
        """Elabora il contenuto della clipboard"""
        try:
            # Leggi contenuto
            prompt = self.get_clipboard_content()
            if not prompt:
                self.logger.warning("Clipboard vuota")
                return

            # Controlli di sicurezza usando la history
            if self.context["history"]:
                # Controlla se il prompt è uguale all'ultima risposta
                last_message = self.context["history"][-1]
                if last_message["role"] == "assistant" and prompt == last_message["content"]:
                    self.logger.info("Clipboard contiene l'ultima risposta - ignoro")
                    return

                # Controlla se il prompt è uguale all'ultimo prompt
                if len(self.context["history"]) >= 2:
                    last_prompt = self.context["history"][-2]
                    if last_prompt["role"] == "user" and prompt == last_prompt["content"]:
                        if not prompt.isdigit():
                            self.logger.info("Prompt identico all'ultimo - ignoro")
                            return


            self.logger.info(f"Elaboro contenuto in modalità {self.current_mode.value} History:{len(self.context['history'])}")

            # Qui implementa la logica di elaborazione con AI

            response = self.ai.generate_response(prompt, self.context)

            # Inserisco nello storico
            self.context["history"].extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response.content}
            ])

            # Leggo la risposta
            self.tts.speak(response.content)

            # Scrivi risposta nella clipboard
            self.set_clipboard_content(response.content)
            
            # Notifica GRID3
            time.sleep(0.1)  # Piccolo delay per sicurezza
            self.notify_grid3() # Posso eliminarlo

        except Exception as e:
            self.logger.error(f"Errore elaborazione: {e}")
            # Notifica errore attraverso clipboard
            error_msg = f"Errore: {str(e)}"
            self.set_clipboard_content(error_msg)
            self.notify_grid3()

    def retryTranslation(self):
        try:
            self.logger.info(f"Riprova la risposta {self.current_mode.value}")

            # Qui implementa la logica di elaborazione con AI
            prompt = "RIPROVA"

            response = self.ai.generate_response(prompt, self.context)

            # Leggo la risposta
            self.tts.speak(response.content)

            # Inserisco nello storico
            self.context["history"].extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response.content}
            ])

            # Scrivi risposta nella clipboard
            self.set_clipboard_content(response.content)
            
            # Notifica GRID3
            time.sleep(0.1)  # Piccolo delay per sicurezza
            self.notify_grid3() # Posso eliminarlo
        
        except Exception as e:
            self.logger.error(f"Errore elaborazione: {e}")
            # Notifica errore attraverso clipboard
            error_msg = f"Errore: {str(e)}"
            self.set_clipboard_content(error_msg)
            self.notify_grid3()



    def handle_mode(self, new_mode:SessionStyle):
        if self.current_mode != new_mode:
            self.current_mode = new_mode
            self.context["style"] = new_mode
            self.context["history"]  = []
            self.current_chat_title = None # Resetta il titolo della chat corrente

            # Ottieni la configurazione del modello per il nuovo stile
            model_config = self.settings.model_configs.get(new_mode.value, {})
            if not model_config:
                self.logger.warning(f"No configuration found for mode {new_mode.value}")
                model_config = {
                    "model": self.settings.anthropic_default_model,
                    "parameters": {
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                }
            self.context["model_config"] = model_config
            self.logger.info(f"Nuova chat in modalità: {new_mode.value}")
        else:
            pass

    def cleanup_trigger_files(self):
        """Rimuove tutti i file di trigger"""
        try:
            for trigger_file in self.trigger_files.values():
                if trigger_file.exists():
                    trigger_file.unlink(missing_ok=True)
                    self.logger.info(f"Rimosso file trigger: {trigger_file}")
        except Exception as e:
            self.logger.error(f"Errore nella pulizia dei file trigger: {e}")
            

    def run(self):
        """Loop principale dell'applicazione"""
        try:
            # Inizializzazione
            self.setup()
            
            # Verifica single instance
            if not self._create_lock_file():
                sys.exit(1)

            self.running = True

            # Gestione segnali
            signal.signal(signal.SIGINT, lambda s, f: self.stop())
            signal.signal(signal.SIGTERM, lambda s, f: self.stop())

            # Avvia il thread di processamento trigger
            trigger_processor = TriggerProcessor(self)
            trigger_processor.start()
            self.logger.info("TriggerProcessor avviato")
            
            # Crea la finestra principale
            try:
                # Usa il file HTML unificato dall'assets_dir
                html_path = str(env.assets_dir / "unified-list.html")
                
                # Crea la finestra principale
                window = webview.create_window(
                    'NAIAD Manager',
                    html_path,
                    width=800,
                    height=800,
                    resizable=True,
                    text_select=False
                )

                # Espone tutte le API necessarie
                window.expose(self.api.list_artifacts)
                window.expose(self.api.read_artifact)
                window.expose(self.api.resume_creative_artifact)
                window.expose(self.api.resume_article_artifact)
                window.expose(self.api.delete_artifact)
                window.expose(self.api.read_artifacts_page)
                window.expose(self.api.list_chats)
                window.expose(self.api.read_chat)
                window.expose(self.api.delete_chat)
                window.expose(self.api.resume_chat)
                window.expose(self.api.read_chats_page)
                window.expose(self.api.tts_speak)
                window.expose(self.api.tts_stop)
                window.expose(self.api.tts_restart)
                window.expose(self.api.tts_resume)
                window.expose(self.api.tts_pause)
                window.expose(self.api.close_window)
                window.expose(self.api.get_asset_path)

                self.logger.info("NAIAD avviato con interfaccia unificata")
                
                # Avvia il loop principale di webview
                webview.start(debug=False)
                
            except Exception as e:
                self.logger.error(f"Errore durante la creazione della finestra: {e}")
                raise
                
        except Exception as e:
            self.logger.error(f"Errore fatale: {e}", exc_info=True)
        finally:
            # Ferma il thread di processamento
            self.logger.info("Arresto NAIAD...")
            trigger_processor.stop()
            trigger_processor.join(timeout=5)
            self.stop()

    def stop(self):
        """Ferma l'applicazione"""
        if not self.running:
            return
    
        self.logger.info("Arresto NAIAD...")
        self.running = False
    
        # Chiudi esplicitamente il provider TTS
        if self.tts:
            self.tts.shutdown()
        
        self._cleanup()
        self.logger.info("NAIAD arrestato")


def launch_ui(mode: str):
    """
    Lancia l'interfaccia utente NAIAD
    
    Args:
        mode: 'artifacts' o 'chats'
    """
    try:
        # Importa NAIADUI solo quando necessario
        from naiad.ui.naiad_ui import NAIADUI
        ui = NAIADUI()
        ui.run(mode)
    except Exception as e:
        print(f"Errore avvio interfaccia utente: {e}")
        sys.exit(1)

def print_usage():
    """Stampa le istruzioni per l'uso"""
    print("""
        Uso: NAIAD.exe [mode]
        Modalità disponibili:
        backend    - Avvia NAIAD in modalità backend (default)
        artifacts  - Avvia l'interfaccia utente per la gestione degli artefatti
        chats      - Avvia l'interfaccia utente per la gestione delle chat
        """)

def oldmain():
    """Entry point principale dell'applicazione"""
    # Verifica che sia specificata una modalità
    if len(sys.argv) != 2:
        print("È necessario specificare una modalità di avvio")
        print_usage()
        sys.exit(1)

    # Parsing modalità
    mode = sys.argv[1].lower()
    if mode not in ['backend', 'artifacts', 'chats']:
        print(f"Modalità non valida: {mode}")
        print_usage()
        sys.exit(1)
    
    # Avvia la modalità appropriata
    try:
        if mode == 'backend':
            app = NAIADApplication()
            app.run()
        else:
            # Avvia l'interfaccia utente
            launch_ui(mode)
    except Exception as e:
        print(f"Errore fatale: {e}")
        sys.exit(1)


def main():
    """Entry point modificato"""
    # L'applicazione ora viene sempre avviata in modalità backend
    try:
        app = NAIADApplication()
        app.run()
    except Exception as e:
        print(f"Errore fatale: {e}")
        sys.exit(1)

if __name__ == '__main__':
    """
    app = NAIADApplication()
    try:
        app.run()
    except Exception as e:
        print(f"Errore fatale: {e}")
        sys.exit(1)
    """
    main() 
