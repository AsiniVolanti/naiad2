# naiad/ai/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class SessionStyle(Enum):
    EXPLORATION = "exploration"
    CREATIVE_WRITING = "creative_writing"
    ARTICLE_WRITING = "article_writing"
    TRANSLATION = "translation"
    CHAT = "chat"  # Nuovo stile per chat social

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    OTHER = "other"  # Per messaggi di altri partecipanti alla chat

@dataclass
class ChatContext:
    """Contesto specifico per le chat"""
    platform: str  # es. "facebook", "whatsapp", "telegram"
    participants: List[str]  # Lista dei partecipanti alla conversazione
    tone: str  # es. "informal", "formal", "friendly"
    max_length: int  # Lunghezza massima consigliata per i messaggi

@dataclass
class Response:
    """Classe per rappresentare una risposta da un provider AI"""
    content: str
    metadata: Dict[str, Any]

class ProviderException(Exception):
    """Eccezione base per errori dei provider AI"""
    pass

class AIProviderInterface(ABC):
    """Interfaccia base per i provider AI"""
    @abstractmethod
    def generate_response(self, prompt: str, context: Dict[str, Any]) -> Response:
        pass

    @abstractmethod
    def validate_response(self, response: Response) -> bool:
        pass
    
