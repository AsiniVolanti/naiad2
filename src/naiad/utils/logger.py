from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from ..core.environment import env

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup logger con gestione percorsi per ambiente frozen"""
    logger = logging.getLogger(name)
    
    if logger.handlers:  # Evita handler duplicati
        return logger
        
    logger.setLevel(getattr(logging, level.upper()))
    
    # Formattazione
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler con rotazione
    log_file = env.logs_dir / f"{name.replace('.', '_')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger