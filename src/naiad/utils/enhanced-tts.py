from gtts import gTTS
import pygame
import threading
import tempfile
import os
from typing import Optional
from enum import Enum

class TTSState(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"

class EnhancedTTSProvider:
    def __init__(self):
        pygame.mixer.init()
        self._current_file: Optional[str] = None
        self._state = TTSState.IDLE
        self._lock = threading.Lock()
        # self._temp_dir = tempfile.mkdtemp()
        
    def speak(self, text: str) -> None:
        """Avvia la riproduzione di un nuovo testo"""
        with self._lock:
            self.stop()  # Ferma qualsiasi riproduzione in corso
            
            # Crea un nuovo file temporaneo
            temp_file = "gtts.mp3" # os.path.join(self._temp_dir, 'speech.mp3')
            tts = gTTS(text=text, lang='it', slow=False)
            tts.save(temp_file)
            
            # Memorizza il file corrente e avvia la riproduzione
            self._current_file = temp_file
            pygame.mixer.music.load(self._current_file)
            pygame.mixer.music.play()
            self._state = TTSState.PLAYING
            
    def pause(self) -> None:
        """Mette in pausa la riproduzione"""
        with self._lock:
            if self._state == TTSState.PLAYING:
                pygame.mixer.music.pause()
                self._state = TTSState.PAUSED
                
    def resume(self) -> None:
        """Riprende la riproduzione"""
        with self._lock:
            if self._state == TTSState.PAUSED:
                pygame.mixer.music.unpause()
                self._state = TTSState.PLAYING
                
    def stop(self) -> None:
        """Ferma la riproduzione"""
        with self._lock:
            if self._state in [TTSState.PLAYING, TTSState.PAUSED]:
                pygame.mixer.music.stop()
                self._state = TTSState.STOPPED
                
    def restart(self) -> None:
        """Riavvia la riproduzione dall'inizio"""
        with self._lock:
            if self._current_file and self._state != TTSState.IDLE:
                pygame.mixer.music.play()
                self._state = TTSState.PLAYING
                
    @property
    def state(self) -> TTSState:
        """Restituisce lo stato corrente del TTS"""
        return self._state
        
    def cleanup(self) -> None:
        """Pulisce le risorse"""
        self.stop()
        pygame.mixer.quit()
        # Rimuove i file temporanei
        if os.path.exists(self._temp_dir):
            for file in os.listdir(self._temp_dir):
                try:
                    os.remove(os.path.join(self._temp_dir, file))
                except Exception:
                    pass
            os.rmdir(self._temp_dir)