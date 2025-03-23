from gtts import gTTS
import pygame
import os
import logging
import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta

class GTTSProvider:
    """Provider per la sintesi vocale utilizzando gTTS e pygame."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("tts_provider")
        self.current_file: Optional[Path] = None
        self.is_playing = False
        self.is_paused = False
        self.is_muted = False
        self.active_files: Dict[Path, datetime] = {}
        self.last_text: Optional[str] = None  # Memorizza l'ultimo testo per riavvio post-mute
        
        # Inizializza pygame per l'audio
        pygame.mixer.init()
        
        # Crea directory temporanea dedicata
        self.temp_dir = Path("C:/ProgramData/NAIAD/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(str(self.temp_dir), 0o755)
        
        # Pulisci file obsoleti all'avvio
        self._cleanup_old_files()
        
    def speak(self, text: str):
        """Sintetizza e riproduce il testo."""
        try:
            self.last_text = text  # Salva il testo per possibile riutilizzo
            
            if self.is_muted:
                self.logger.debug("TTS è in mute, il testo non verrà riprodotto")
                return
                
            # Ferma riproduzione corrente
            self._stop_playback()
            
            # Genera nuovo file
            temp_file = self.temp_dir / f"speech_{id(text)}.mp3"
            
            # Genera l'audio
            tts = gTTS(text=text, lang='it', slow=True)
            tts.save(str(temp_file))
            
            # Piccola pausa per assicurare che il file sia scritto
            time.sleep(0.1)
            
            # Carica e riproduce
            pygame.mixer.music.load(str(temp_file))
            pygame.mixer.music.play()
            
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
            raise
            
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
            except:
                pass
                
            # Pulizia file
            try:
                self._cleanup_old_files()
            except:
                pass
                
            # Chiudi pygame mixer
            try:
                if pygame and pygame.mixer and pygame.mixer.get_init():
                    pygame.mixer.quit()
            except:
                pass
            
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
            for file_path in self.temp_dir.glob("speech_*.mp3"):
                if file_path not in self.active_files and file_path != self.current_file:
                    try:
                        file_path.unlink()
                    except Exception as e:
                        self.logger.debug(f"File orfano {file_path} non disponibile per la rimozione: {e}")
                        
        except Exception as e:
            self.logger.error(f"Errore durante la pulizia dei file: {e}")
            
    def __del__(self):
        """Cleanup alla distruzione dell'oggetto."""
        try:
            pass
            #self._safe_cleanup()
            #pygame.mixer.quit()
        except Exception as e:
            self.logger.error(f"Errore durante la chiusura del TTS provider: {e}")
