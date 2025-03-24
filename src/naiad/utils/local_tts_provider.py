import pyttsx3
import pygame
import os
import logging
import time
import threading
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta

class LocalTTSProvider:
    """Provider per la sintesi vocale utilizzando pyttsx3 e pygame con gestione fallback."""
    
    def __init__(self, logger: Optional[logging.Logger] = None, rate: int = 140):
        self.logger = logger or logging.getLogger("tts_provider")
        self.current_file: Optional[Path] = None
        self.is_playing = False
        self.is_paused = False
        self.is_muted = False
        self.active_files: Dict[Path, datetime] = {}
        self.last_text: Optional[str] = None
        self.engine = None
        self.initialized = False
        self.init_lock = threading.Lock()
        
        # Crea directory temporanea dedicata
        self.temp_dir = Path("C:/ProgramData/NAIAD/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(str(self.temp_dir), 0o755)
        
        # Inizializza pygame per l'audio
        try:
            pygame.mixer.init()
            self.logger.info("Pygame mixer inizializzato con successo")
        except Exception as e:
            self.logger.error(f"Errore inizializzazione pygame mixer: {e}")
        
        # Inizializza TTS in un thread separato per evitare blocchi
        self.tts_thread = threading.Thread(target=self._initialize_tts, args=(rate,))
        self.tts_thread.daemon = True
        self.tts_thread.start()
        
        # Pulisci file obsoleti all'avvio
        self._cleanup_old_files()
    
    def _initialize_tts(self, rate: int):
        """Inizializza il motore TTS in un thread separato"""
        with self.init_lock:
            try:
                self.logger.info("Inizializzazione motore TTS...")
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', rate)
                self.engine.setProperty('volume', 1.0)
                
                # Lista voci disponibili
                voices = self.engine.getProperty('voices')
                self.logger.info(f"Voci disponibili: {len(voices)}")
                
                # Log delle voci disponibili
                for idx, voice in enumerate(voices):
                    self.logger.info(f"Voce {idx}: ID={voice.id}, Nome={voice.name}, Lingua={voice.languages}")
                
                # Priorità: voce italiana, poi qualsiasi voce
                giorgio_voice = next((v for v in voices if 'giorgio' in v.name.lower()), None)
                italian_voice = next((v for v in voices if 'ital' in v.name.lower()), None)
                if giorgio_voice:
                    self.logger.info(f"Selezionata voce di Giorgio: {giorgio_voice.name}")
                    self.engine.setProperty('voice', giorgio_voice.id)
                elif italian_voice:
                    self.logger.info(f"Selezionata voce italiana: {italian_voice.name}")
                    self.engine.setProperty('voice', italian_voice.id)
                elif voices:
                    self.logger.warning(f"Nessuna voce italiana trovata, uso voce predefinita: {voices[0].name}")
                    self.engine.setProperty('voice', voices[0].id)
                else:
                    self.logger.error("Nessuna voce disponibile nel sistema")
                    raise RuntimeError("Nessuna voce disponibile")
                
                # Test semplice per verificare che tutto funzioni
                self.engine.say("L'asino sta volando")
                self.engine.runAndWait()
                
                self.initialized = True
                self.logger.info("Motore TTS inizializzato con successo")
            except Exception as e:
                self.logger.error(f"Errore inizializzazione motore TTS: {e}")
                self.initialized = False
    
    def _wait_for_init(self, timeout=10) -> bool:
        """Attende l'inizializzazione del TTS con timeout"""
        start_time = time.time()
        while not self.initialized and time.time() - start_time < timeout:
            time.sleep(0.1)
        return self.initialized
    
    def _generate_speech_file(self, text: str) -> Optional[Path]:
        """Genera un file audio con pyttsx3 con gestione errori migliorata"""
        if not self._wait_for_init():
            self.logger.error("Timeout attesa inizializzazione TTS")
            return None
            
        with self.init_lock:  # Protegge l'accesso al motore TTS
            temp_file = self.temp_dir / f"speech_{id(text)}_{int(time.time())}.wav"
            
            try:
                # Configura pyttsx3 per salvare su file
                self.engine.save_to_file(text, str(temp_file))
                self.engine.runAndWait()
                
                # Verifica che il file sia stato creato e abbia dimensioni > 0
                if temp_file.exists() and temp_file.stat().st_size > 0:
                    #self.logger.info(f"File audio generato: {temp_file}")
                    return temp_file
                else:
                    self.logger.error(f"File audio non creato o vuoto: {temp_file}")
                    return None
            except Exception as e:
                self.logger.error(f"Errore generazione file audio: {e}")
                return None

    def speak(self, text: str):
        """Sintetizza e riproduce il testo con fallback"""
        try:
            self.last_text = text
            
            if self.is_muted:
                self.logger.debug("TTS è in mute, il testo non verrà riprodotto")
                return
            
            # Ferma riproduzione corrente
            self._stop_playback()
            
            # Genera nuovo file
            temp_file = self._generate_speech_file(text)
            
            if not temp_file:
                self.logger.error("Impossibile generare file audio, fallback su voce diretta")
                try:
                    # Fallback: riproduzione diretta senza file
                    if self.initialized and self.engine:
                        self.engine.say(text)
                        self.engine.runAndWait()
                        return
                except Exception as e:
                    self.logger.error(f"Anche il fallback è fallito: {e}")
                    return
            
            # Piccola pausa per assicurare che il file sia scritto completamente
            time.sleep(0.2)
            
            # Carica e riproduce con retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    pygame.mixer.music.load(str(temp_file))
                    pygame.mixer.music.play()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Tentativo {attempt+1} fallito: {e}, riprovo...")
                        time.sleep(0.5)
                    else:
                        self.logger.error(f"Tutti i tentativi falliti: {e}")
                        return
            
            # Aggiorna stato
            if self.current_file:
                self.active_files[self.current_file] = datetime.now()
            
            self.current_file = temp_file
            self.active_files[temp_file] = datetime.now()
            self.is_playing = True
            self.is_paused = False
            
            # Pulizia in background
            self._cleanup_old_files()
            
        except Exception as e:
            self.logger.error(f"Errore durante la sintesi vocale: {e}")
            self._safe_cleanup()
            
    # [resto dei metodi esistenti come stop, pause, resume, ecc.]
    def stop(self):
        """Ferma la riproduzione."""
        self._stop_playback()
        self._cleanup_old_files()
        
    def pause(self):
        """Mette in pausa la riproduzione."""
        if self.is_playing and not self.is_paused and not self.is_muted:
            try:
                pygame.mixer.music.pause()
                self.is_paused = True
            except Exception as e:
                self.logger.error(f"Errore durante la pausa: {e}")
                
    def resume(self):
        """Riprende la riproduzione."""
        if self.is_muted:
            self.logger.debug("Impossibile riprendere mentre il TTS è in mute")
            return
            
        if self.is_playing and self.is_paused:
            try:
                pygame.mixer.music.unpause()
                self.is_paused = False
            except Exception as e:
                self.logger.error(f"Errore durante la ripresa: {e}")
                
    def restart(self):
        """Riavvia la riproduzione."""
        if self.is_muted:
            self.logger.debug("Impossibile riavviare mentre il TTS è in mute")
            return
            
        if self.current_file and self.current_file.exists():
            try:
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
            except Exception as e:
                self.logger.error(f"Errore durante il riavvio: {e}")
                
    def mute(self):
        """Attiva il mute."""
        if not self.is_muted:
            self._stop_playback()
            self.is_muted = True
            self.logger.debug("TTS mutato")
            
    def unmute(self):
        """Disattiva il mute."""
        if self.is_muted:
            self.is_muted = False
            self.logger.debug("TTS unmutato")
            # Se c'era del testo in riproduzione, lo riproduciamo
            if self.last_text:
                self.speak(self.last_text)
                
    def _stop_playback(self):
        """Ferma la riproduzione e aggiorna lo stato."""
        if self.is_playing:
            try:
                pygame.mixer.music.stop()
                time.sleep(0.1)  # Piccola pausa per assicurare che pygame rilasci il file
                self.is_playing = False
                self.is_paused = False
                
                # Marca il file corrente per la pulizia
                if self.current_file:
                    self.active_files[self.current_file] = datetime.now()
                    
            except Exception as e:
                self.logger.error(f"Errore durante lo stop della riproduzione: {e}")

    def shutdown(self):
        """Metodo esplicito per il cleanup delle risorse prima della distruzione."""
        try:
            # Prima ferma eventuali riproduzioni in corso
            try:
                if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
            except Exception as e:
                self.logger.error(f"Errore fermando la riproduzione: {e}")
                
            # Pulizia file
            try:
                self._cleanup_old_files()
            except Exception as e:
                self.logger.error(f"Errore pulizia file: {e}")
                
            # Chiudi il motore pyttsx3
            try:
                if self.initialized and self.engine:
                    self.engine.stop()
            except Exception as e:
                self.logger.error(f"Errore fermando motore TTS: {e}")
                
            # Chiudi pygame mixer
            try:
                if pygame and pygame.mixer and pygame.mixer.get_init():
                    pygame.mixer.quit()
            except Exception as e:
                self.logger.error(f"Errore chiudendo pygame mixer: {e}")
                
            # Resetta le variabili di stato
            self.current_file = None
            self.is_playing = False
            self.is_paused = False
            
        except Exception as e:
            try:
                self.logger.error(f"Errore durante la chiusura del TTS provider: {e}")
            except:
                pass

    def _safe_cleanup(self):
        """Esegue una pulizia sicura dei file."""
        try:
            self._stop_playback()
            time.sleep(0.1)  # Attesa aggiuntiva per il rilascio dei file
            self._cleanup_old_files()
        except Exception as e:
            self.logger.error(f"Errore durante la pulizia sicura: {e}")
            
    def _cleanup_old_files(self):
        """Pulisce i file temporanei non più in uso."""
        try:
            current_time = datetime.now()
            files_to_remove = []
            
            # Identifica file da rimuovere (più vecchi di 5 secondi)
            for file_path, timestamp in list(self.active_files.items()):
                if current_time - timestamp > timedelta(seconds=5):
                    files_to_remove.append(file_path)
                    
            # Rimuovi file non correnti
            for file_path in files_to_remove:
                if file_path != self.current_file:
                    try:
                        if file_path.exists():
                            file_path.unlink()
                        del self.active_files[file_path]
                    except Exception as e:
                        self.logger.debug(f"File temporaneo {file_path} non ancora disponibile per la rimozione: {e}")
                        
            # Pulisci file orfani
            for file_path in self.temp_dir.glob("speech_*.wav"):
                if file_path not in self.active_files and file_path != self.current_file:
                    try:
                        file_path.unlink()
                    except Exception as e:
                        self.logger.debug(f"File orfano {file_path} non disponibile per la rimozione: {e}")
                        
        except Exception as e:
            self.logger.error(f"Errore durante la pulizia dei file: {e}")