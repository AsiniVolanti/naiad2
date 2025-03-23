from pathlib import Path
import os
import logging
from datetime import datetime
from typing import Optional

class ArtifactManager:
    def __init__(self, base_dir: Path, logger: logging.Logger):
        """
        Inizializza il gestore degli artefatti.
        
        Args:
            base_dir: Directory base per il salvataggio degli artefatti
            logger: Logger per la registrazione degli eventi
        """
        self.base_dir = base_dir
        self.logger = logger
        self.artifacts_dir = base_dir / "artifacts"
        self._ensure_directory()

    def _extract_title_from_content(self, content: str, max_words: int = 5) -> str:
        """
        Estrae un titolo dal contenuto dell'artefatto.
        
        Args:
            content: Contenuto dell'artefatto
            max_words: Numero massimo di parole da utilizzare per il titolo
            
        Returns:
            str: Titolo estratto dal contenuto
        """
        # Rimuove caratteri non validi e divide in parole
        words = content.replace('\n', ' ').strip().split()
        
        # Prende le prime max_words parole
        title_words = words[:max_words]
        
        # Se il titolo è troppo lungo (> 50 caratteri), lo tronca
        title = ' '.join(title_words)
        if len(title) > 50:
            title = title[:47] + '...'
            
        return title

    def _ensure_directory(self):
        """Assicura che la directory degli artefatti esista"""
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitizza il nome del file rimuovendo caratteri non validi.
        
        Args:
            filename: Nome del file da sanitizzare
            
        Returns:
            str: Nome del file sanitizzato
        """
        # Caratteri non validi in Windows
        invalid_chars = '<>:"/\\|?*'
        
        # Sostituisce caratteri non validi con underscore
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Rimuove spazi iniziali e finali
        filename = filename.strip()
        
        # Se il filename è vuoto, usa un timestamp
        if not filename:
            filename = "Senza titolo"
            
        return filename
        
    def save_artifact(self, content: str, filename: Optional[str] = None) -> Path:
        """
        Salva un artefatto su file.
        
        Args:
            content: Contenuto dell'artefatto
            filename: Nome del file (opzionale)
            
        Returns:
            Path: Percorso del file salvato
            
        Raises:
            IOError: Se si verifica un errore durante il salvataggio
        """
        try:
            # Se non è specificato un filename, usa un timestamp
            if not filename or len(filename.split()) > 5:
                filename = self._extract_title_from_content(content)
            
            # Sanitizza il nome del file
            safe_filename = self._sanitize_filename(filename)
            
            # Aggiunge estensione .txt se non presente
            if not safe_filename.endswith('.txt'):
                safe_filename += '.txt'
                
            # Costruisce il path completo
            file_path = self.artifacts_dir / safe_filename
            
            # Se il file esiste, aggiunge un numero progressivo
            counter = 1
            while file_path.exists():
                base_name = safe_filename.rsplit('.', 1)[0]
                file_path = self.artifacts_dir / f"{base_name}_{counter}.txt"
                counter += 1
            
            # Salva il contenuto
            file_path.write_text(content, encoding='utf-8')
            
            self.logger.info(f"Artefatto salvato in: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Errore durante il salvataggio dell'artefatto: {e}")
            raise IOError(f"Impossibile salvare l'artefatto: {str(e)}")
            
    
    def get_artifacts_list(self) -> list[tuple[str, datetime]]:
        """
        Ottiene la lista degli artefatti salvati ordinati per data.
        
        Returns:
            list[tuple[str, datetime]]: Lista di tuple (nome_file, data_modifica)
        """
        files = list(self.artifacts_dir.glob('*.txt'))
        result = []
        
        for file in files:
            mod_time = datetime.fromtimestamp(file.stat().st_mtime)
            result.append((file.name, mod_time))
            
        # Ordina per data più recente
        return sorted(result, key=lambda x: x[1], reverse=True)
        
    def get_artifact_content(self, filename: str) -> str:
        """
        Legge il contenuto di un artefatto.
        
        Args:
            filename: Nome del file da leggere
            
        Returns:
            str: Contenuto dell'artefatto
            
        Raises:
            FileNotFoundError: Se il file non esiste
        """
        file_path = self.artifacts_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Artefatto non trovato: {filename}")
            
        return file_path.read_text(encoding='utf-8')
        
    def format_artifact_list(self) -> str:
        """
        Formatta la lista degli artefatti per la lettura vocale.
        
        Returns:
            str: Testo formattato per la lettura
        """
        artifacts = self.get_artifacts_list()
        
        if not artifacts:
            return "Non ci sono artefatti salvati."
            
        # Crea una lista numerata per facile riferimento
        lines = ["Ecco gli artefatti salvati, dal più recente:"]
        for i, (name, date) in enumerate(artifacts, 1):
            pure_name = name.rsplit('.', 1)[0]
            date_str = date.strftime("%d/%m/%Y alle %H:%M")
            lines.append(f"Numero {i}: {pure_name}, salvato il {date_str}")
            
        return " ... ".join(lines)

    def get_artifact_by_number(self, number: int) -> tuple[str, str]:
        """
        Recupera un artefatto dal suo numero in lista.
        
        Args:
            number: Numero dell'artefatto (1-based)
            
        Returns:
            tuple[str, str]: (nome_file, contenuto)
            
        Raises:
            IndexError: Se il numero non è valido
        """
        artifacts = self.get_artifacts_list()
        
        if not 1 <= number <= len(artifacts):
            raise IndexError(f"Numero non valido. Ci sono {len(artifacts)} artefatti.")
            
        filename = artifacts[number-1][0]
        content = self.get_artifact_content(filename)
        return filename, content

    def delete_artifact(self, filename: str) -> bool:
        """
        Cancella un artefatto dal filesystem.
        
        Args:
            filename: Nome del file da cancellare
            
        Returns:
            bool: True se la cancellazione è avvenuta con successo
        """
        try:
            file_path = self.artifacts_dir / filename
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Artefatto {filename} cancellato con successo")
                return True
            else:
                self.logger.warning(f"Artefatto {filename} non trovato")
                return False
                
        except Exception as e:
            self.logger.error(f"Errore durante la cancellazione dell'artefatto {filename}: {e}")
            return False 