import os
import sys
from pathlib import Path
import time
from datetime import datetime, timedelta
import shutil
import logging

from naiad.core.environment import env
from naiad.utils.logger import setup_logger
from naiad.core.artifact_manager import ArtifactManager
from naiad.core.chat_manager import ChatManager
from naiad.ai.base import SessionStyle
from naiad.core.main import NAIADUI

def create_sample_artifacts(artifact_manager):
    """Crea alcuni artefatti di esempio"""
    sample_texts = [
        ("Lettera al sindaco sulla mobilità urbana", 
         "Egregio Signor Sindaco, scrivo per portare alla sua attenzione..."),
        ("Poesia: Il volo dell'aquilone", 
         "Nel cielo azzurro di primavera, un aquilone danza..."),
        ("Riflessioni sull'intelligenza artificiale",
         "L'avvento dell'AI sta trasformando profondamente..."),
        ("Testo canzone: Primavera in città",
         "Verso 1: Le strade si riempiono di colori..."),
        ("Il futuro della comunicazione",
         "La comunicazione sta attraversando una fase di profondo cambiamento...")
    ]
    
    for title, content in sample_texts:
        artifact_manager.save_artifact(content, title)
        # Breve pausa per avere timestamp diversi
        time.sleep(0.1)

def create_sample_chats(chat_manager):
    """Crea alcune chat di esempio"""
    sample_chats = [
        {
            "style": SessionStyle.CHAT,
            "title": "Discussione sul clima e ambiente",
            "history": [
                {"role": "user", "content": "PARLARE CLIMA CAMBIAMENTI"},
                {"role": "assistant", "content": "Il cambiamento climatico è una sfida cruciale..."}
            ]
        },
        {
            "style": SessionStyle.CREATIVE_WRITING,
            "title": "Poesia sulla primavera",
            "history": [
                {"role": "user", "content": "SCRIVERE POESIA PRIMAVERA"},
                {"role": "assistant", "content": "Ecco una poesia sulla primavera..."}
            ]
        },
        {
            "style": SessionStyle.ARTICLE_WRITING,
            "title": "Articolo sulla mobilità sostenibile",
            "history": [
                {"role": "user", "content": "SCRIVERE ARTICOLO MOBILITA SOSTENIBILE"},
                {"role": "assistant", "content": "La mobilità sostenibile è un tema centrale..."}
            ]
        },
        {
            "style": SessionStyle.EXPLORATION,
            "title": "Esplorazione spazio e pianeti",
            "history": [
                {"role": "user", "content": "PARLARE PIANETI SISTEMA SOLARE"},
                {"role": "assistant", "content": "Il sistema solare è composto da..."}
            ]
        }
    ]
    
    for chat in sample_chats:
        chat_manager.save_chat(
            style=chat["style"],
            history=chat["history"],
            title=chat["title"]
        )
        time.sleep(0.1)

def setup_test_environment():
    """Prepara l'ambiente di test"""
    # Crea directory temporanea per i test
    test_dir = Path("test_naiad_ui")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # Setup logger
    logger = setup_logger("test_naiad_ui")
    
    # Inizializza managers
    artifact_manager = ArtifactManager(test_dir, logger)
    chat_manager = ChatManager(logger)
    
    return test_dir, artifact_manager, chat_manager

def cleanup_test_environment(test_dir):
    """Pulisce l'ambiente di test"""
    if test_dir.exists():
        shutil.rmtree(test_dir)

def main():
    """Test principale"""
    try:
        # Setup
        test_dir, artifact_manager, chat_manager = setup_test_environment()
        
        # Crea dati di esempio
        print("Creazione artefatti di esempio...")
        create_sample_artifacts(artifact_manager)
        
        print("Creazione chat di esempio...")
        create_sample_chats(chat_manager)
        
        # Test UI artefatti
        print("\nAvvio test UI artefatti...")
        ui = NAIADUI()
        ui.run('artifacts')
        
        # Breve pausa
        time.sleep(2)
        
        # Test UI chat
        print("\nAvvio test UI chat...")
        ui = NAIADUI()
        ui.run('chats')
        
    except Exception as e:
        print(f"Errore durante il test: {e}")
        raise
    finally:
        cleanup_test_environment(test_dir)

if __name__ == "__main__":
    main()