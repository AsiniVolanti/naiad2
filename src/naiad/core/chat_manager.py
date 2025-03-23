# chat_manager.py
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from typing import Optional, List, Tuple, Dict
from pathlib import Path
import logging
from naiad.ai.base import SessionStyle
from naiad.core.environment import env

@dataclass
class SuspendedChat:
    style: SessionStyle
    history: list
    suspended_at: datetime
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> 'SuspendedChat':
        """Crea un'istanza da un dizionario"""
        return cls(
            style=SessionStyle(data['style']),
            history=data['history'],
            suspended_at=datetime.fromisoformat(data['suspended_at']),
            description=data['description']
        )

    def to_dict(self) -> dict:
        """Converte l'istanza in un dizionario serializzabile"""
        return {
            'style': self.style.value,
            'history': self.history,
            'suspended_at': self.suspended_at.isoformat(),
            'description': self.description
        }
@dataclass
class SavedChat:
    """Rappresenta una chat salvata con titolo"""
    style: SessionStyle
    history: list
    saved_at: datetime
    title: str
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> 'SavedChat':
        """Crea un'istanza da un dizionario"""
        return cls(
            style=SessionStyle(data['style']),
            history=data['history'],
            saved_at=datetime.fromisoformat(data['saved_at']),
            title=data['title'],
            description=data['description']
        )

    def to_dict(self) -> dict:
        """Converte l'istanza in un dizionario serializzabile"""
        return {
            'style': self.style.value,
            'history': self.history,
            'saved_at': self.saved_at.isoformat(),
            'title': self.title,
            'description': self.description
        }

class ChatManager:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("chat_manager")
        # Dizionario che mappa SessionStyle -> SuspendedChat
        self.current_style: Optional[SessionStyle] = None
        self._ensure_db_dir()
        self.chats_dir = env.db_dir 
        

    def _ensure_db_dir(self):
        """Crea la directory per i file di salvataggio se non esiste"""
        if not env.db_dir.exists():
            env.db_dir.mkdir(parents=True)
            self.logger.info(f"Creata directory per i file di salvataggio: {env.db_dir}")

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
            filename = "Chat senza titolo"
        
        return filename

    def _extract_title_from_content(self, content: List[dict], max_words: int = 5) -> str:
        """
        Estrae un titolo dalla chat.
        
        Args:
            content: Contenuto della chat
            max_words: Numero massimo di parole da utilizzare per il titolo
            
        Returns:
            str: Titolo estratto dal contenuto
        """
        # Cerca l'ultimo messaggio dell'utente
        for msg in reversed(content):
            if msg["role"] == "user":
                # Rimuove caratteri non validi e divide in parole
                words = msg["content"].replace('\n', ' ').strip().split()
                
                # Prende le prime max_words parole
                title_words = words[:max_words]
                
                # Se il titolo è troppo lungo (> 50 caratteri), lo tronca
                title = ' '.join(title_words)
                if len(title) > 50:
                    title = title[:47] + '...'
                    
                return title
                
        return "Chat senza titolo"
    
    def save_chat(self, style: SessionStyle, history: list, title: Optional[str] = None) -> Path:
        """
        Salva una chat su file.
        
        Args:
            style: Stile della sessione
            history: Cronologia dei messaggi
            title: Titolo opzionale per la chat
            
        Returns:
            Path: Percorso del file salvato
            
        Raises:
            IOError: Se si verifica un errore durante il salvataggio
        """
        try:
            if not history:  # Non salvare chat vuote
                raise ValueError("La chat è vuota")

            # Se non è specificato un titolo, estrailo dal contenuto
            if not title:
                title = self._extract_title_from_content(history)
            
            # Sanitizza il nome del file
            safe_filename = self._sanitize_filename(title)
            
            # Aggiungi estensione .json se non presente
            if not safe_filename.endswith('.json'):
                safe_filename += '.json'
                
            # Costruisce il path completo
            file_path = self.chats_dir / safe_filename
            
            # Se il file esiste, aggiunge un numero progressivo
            # counter = 1
            # while file_path.exists():
            #    base_name = safe_filename.rsplit('.', 1)[0]
            #    file_path = self.chats_dir / f"{base_name}_{counter}.json"
            #    counter += 1
            
            # Prepara i dati da salvare
            chat_data = {
                'style': style.value,
                'title': title,
                'history': history,
                'saved_at': datetime.now().isoformat()
            }
            
            # Salva il contenuto
            file_path.write_text(json.dumps(chat_data, indent=2, ensure_ascii=False), encoding='utf-8')
            
            self.logger.info(f"Chat salvata in: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Errore durante il salvataggio della chat: {e}")
            raise IOError(f"Impossibile salvare la chat: {str(e)}")

    def get_chats_list(self) -> list[tuple[str, SessionStyle, datetime]]:
        """
        Ottiene la lista delle chat salvate ordinate per data.
        
        Returns:
            list[tuple[str, SessionStyle, datetime]]: Lista di tuple (nome_file, stile, data_modifica)
        """
        try:
            result = []
            for file in self.chats_dir.glob('*.json'):
                try:
                    data = json.loads(file.read_text(encoding='utf-8'))
                    style = SessionStyle(data['style'])
                    saved_at = datetime.fromisoformat(data['saved_at'])
                    result.append((file.name, style, saved_at))
                except Exception as e:
                    self.logger.error(f"Errore lettura chat {file}: {e}")
                    continue
                    
            # Ordina per data più recente
            return sorted(result, key=lambda x: x[2], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Errore recupero lista chat: {e}")
            return []

    def get_chat_content(self, filename: str) -> tuple[SessionStyle, list]:
        """
        Legge il contenuto di una chat.
        
        Args:
            filename: Nome del file da leggere
            
        Returns:
            tuple[SessionStyle, list]: Stile della sessione e cronologia messaggi
            
        Raises:
            FileNotFoundError: Se il file non esiste
        """
        file_path = self.chats_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Chat non trovata: {filename}")
            
        data = json.loads(file_path.read_text(encoding='utf-8'))
        return SessionStyle(data['style']), data['history']

    def format_chats_list(self, filter_style: Optional[SessionStyle] = None) -> str:
        """
        Formatta la lista delle chat per la lettura vocale.
        
        Args:
            filter_style: Se specificato, filtra le chat per stile
            
        Returns:
            str: Testo formattato per la lettura
        """
        chats = self.get_chats_list()
        if filter_style:
            chats = [(name, style, date) for name, style, date in chats if style == filter_style]
        
        if not chats:
            return "Non ci sono chat salvate."
            
        style_names = {
            SessionStyle.TRANSLATION: "traduzione",
            SessionStyle.CHAT: "chat",
            SessionStyle.EXPLORATION: "esplorazione",
            SessionStyle.CREATIVE_WRITING: "scrittura creativa",
            SessionStyle.ARTICLE_WRITING: "scrittura articoli"
        }
        
        # Crea una lista numerata per facile riferimento
        lines = ["Ecco le chat salvate, dalla più recente:"]
        for i, (name, style, date) in enumerate(chats, 1):
            style_name = style_names.get(style, str(style))
            date_str = date.strftime("%d/%m/%Y alle %H:%M")
            name_without_ext = name.rsplit('.', 1)[0]
            lines.append(f"Numero {i}: {name_without_ext}, {style_name}, salvata il {date_str}")
            
        return " ... ".join(lines)

    
    def get_chat_by_number(self, number: int, include_title: bool = False) -> tuple:
        """
        Recupera una chat dal suo numero in lista.
        
        Args:
            number: Numero della chat (1-based)
            include_title: Se True, include il titolo nella tupla restituita
            
        Returns:
            tuple: (filename, style, history) o (filename, style, history, title)
            
        Raises:
            IndexError: Se il numero non è valido
        """
        chats = self.get_chats_list()
        
        if not 1 <= number <= len(chats):
            raise IndexError(f"Numero non valido. Ci sono {len(chats)} chat.")
            
        filename = chats[number-1][0]
        data = json.loads((self.chats_dir / filename).read_text(encoding='utf-8'))
        style = SessionStyle(data['style'])
        history = data['history']
        
        if include_title:
            title = data.get('title', filename.rsplit('.', 1)[0])
            return filename, style, history, title
            
        return filename, style, history

    def delete_chat(self, filename: str) -> bool:
        """
        Elimina una chat salvata.
        
        Args:
            filename: Nome del file da eliminare
            
        Returns:
            bool: True se la chat è stata eliminata con successo
        """
        try:
            file_path = self.chats_dir / filename
            if not file_path.exists():
                return False
                
            file_path.unlink()
            self.logger.info(f"Chat eliminata: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Errore durante l'eliminazione della chat {filename}: {e}")
            return False

    def delete_chat_by_number(self, number: int) -> tuple[bool, str]:
        """
        Elimina una chat dato il suo numero in lista.
        
        Args:
            number: Numero della chat (1-based)
            
        Returns:
            tuple[bool, str]: (successo, nome_file)
            
        Raises:
            IndexError: Se il numero non è valido
        """
        chats = self.get_chats_list()
        
        if not 1 <= number <= len(chats):
            raise IndexError(f"Numero non valido. Ci sono {len(chats)} chat.")
            
        filename = chats[number-1][0]
        success = self.delete_chat(filename)
        return success, filename