# src/naiad/core/environment.py
"""
Gestione dell'ambiente di esecuzione NAIAD.
Questo modulo gestisce le differenze tra ambiente di sviluppo e frozen.
"""

import os
import sys
from pathlib import Path
from typing import Union, Optional
import logging

class Environment:
    """Gestisce l'ambiente di esecuzione di NAIAD"""
    
    def __init__(self):
        self._is_frozen = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
        self._app_root = Path(sys._MEIPASS) if self._is_frozen else Path(__file__).parent
        self._data_root = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / 'NAIAD'
        
        # Inizializza le directory necessarie
        self._init_directories()
        
    def _init_directories(self):
        """Inizializza la struttura delle directory"""
        dirs = {
            'config': self.config_dir,
            'logs': self.logs_dir,
            'db': self.db_dir,
            'cache': self.cache_dir
        }
        
        for name, path in dirs.items():
            path.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_frozen(self) -> bool:
        """Indica se l'applicazione è in esecuzione da un ambiente frozen"""
        return self._is_frozen
    
    @property
    def app_root(self) -> Path:
        """Directory root dell'applicazione"""
        return self._app_root
        
    @property
    def data_root(self) -> Path:
        """Directory root per i dati dell'applicazione"""
        return self._data_root
        
    @property
    def config_dir(self) -> Path:
        """Directory per i file di configurazione"""
        return self.data_root / 'config'
        
    @property
    def logs_dir(self) -> Path:
        """Directory per i file di log"""
        return self.data_root / 'logs'
        
    @property
    def db_dir(self) -> Path:
        """Directory per i file del database"""
        return self.data_root / 'db'
        
    @property
    def cache_dir(self) -> Path:
        """Directory per i file di cache"""
        return self.data_root / 'cache'
        
    @property
    def assets_dir(self) -> Path:
        """Directory per le risorse statiche"""
        return self.data_root / 'assets'
    
    def get_resource_path(self, *parts: str) -> Path:
        """
        Ottiene il percorso di una risorsa dell'applicazione
        
        Args:
            *parts: Parti del percorso relativo alla risorsa
            
        Returns:
            Path assoluto alla risorsa
        """
        return self.app_root.joinpath(*parts)
    
    def get_data_path(self, *parts: str) -> Path:
        """
        Ottiene il percorso di un file dati dell'applicazione
        
        Args:
            *parts: Parti del percorso relativo al file
            
        Returns:
            Path assoluto al file dati
        """
        return self.data_root.joinpath(*parts)
    
    def ensure_directory(self, *parts: str) -> Path:
        """
        Assicura che una directory esista
        
        Args:
            *parts: Parti del percorso relativo alla directory
            
        Returns:
            Path alla directory creata
        """
        path = self.data_root.joinpath(*parts)
        path.mkdir(parents=True, exist_ok=True)
        return path

# Istanza singleton dell'environment
env = Environment()

# Esporta funzioni helper per comodità
def is_frozen() -> bool:
    """Indica se l'applicazione è in esecuzione da un ambiente frozen"""
    return env.is_frozen

def get_app_root() -> Path:
    """Ottiene la directory root dell'applicazione"""
    return env.app_root

def get_resource_path(*parts: str) -> Path:
    """Ottiene il percorso di una risorsa dell'applicazione"""
    return env.get_resource_path(*parts)

def get_data_path(*parts: str) -> Path:
    """Ottiene il percorso di un file dati dell'applicazione"""
    return env.get_data_path(*parts)