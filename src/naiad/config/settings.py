# naiad/config/settings.py
from pathlib import Path
import yaml
import logging
from naiad.core.environment import env
from naiad.utils.logger import setup_logger

class Settings:
    # Configurazione predefinita direttamente nel codice invece che in un file esterno
    DEFAULT_CONFIG = {
        "api": {
            "anthropic": {
                "api_key": "",  # Sarà impostata tramite environment o file di configurazione
                "models":  {
                    "exploration": {
                       "model": "claude-3-5-sonnet-20241022",
                        "parameters": {
                            "temperature": 0.7,
                            "max_tokens": 1000
                        }          
                    },
                    "creative_writing": {
                       "model": "claude-3-5-sonnet-20241022",
                        "parameters": {
                            "temperature": 0.9,
                            "max_tokens": 2000
                        }          
                    },
                    "article_writing": {
                       "model": "claude-3-5-sonnet-20241022",
                        "parameters": {
                            "temperature": 0.6,
                            "max_tokens": 3000
                        }          
                    },
                    "translation": {
                       "model": "claude-3-5-haiku-20241022",
                        "parameters": {
                            "temperature": 0.3,
                            "max_tokens": 500
                        }          
                    },
                    "chat": {
                       "model": "claude-3-5-haiku-20241022",
                        "parameters": {
                            "temperature": 0.8,
                            "max_tokens": 800
                        }          
                    }
                }
            },
            "openai": {
                "api_key": ""
            },
            "perplexity": {
                "api_key": ""
            }
        },
        "tts": {
            "provider": "gtts",
            "language": "it",
            "rate": 140
        },
        "logging": {
            "level": "INFO",
            "file": "naiad.log"
        }
    }

    def __init__(self):
        self.logger = setup_logger('naiad.config')
        self._config = {}
        self._load_config()

    def _load_config(self):
        try:
            # Percorso del file di configurazione
            config_file = env.config_dir / 'config.yaml'
            
            if config_file.exists():
                # Se esiste un file di configurazione, caricalo
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    # Unisce la configurazione utente con quella predefinita
                    self._config = self._merge_configs(self.DEFAULT_CONFIG, user_config or {})
                self.logger.info(f"Configurazione caricata da {config_file}")
            else:
                # Se non esiste, usa la configurazione predefinita e salvala
                self._config = self.DEFAULT_CONFIG.copy()
                config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
                self.logger.info(f"Creato nuovo file di configurazione in {config_file}")

            # Carica API key da variabile d'ambiente se disponibile
            import os
            env_api_key = os.environ.get('ANTHROPIC_API_KEY')
            if env_api_key:
                self._config['api']['anthropic']['api_key'] = env_api_key
                self.logger.info("API key Anthropic caricata da variabile d'ambiente")
            
        except Exception as e:
            self.logger.error(f"Errore caricamento configurazione: {e}")
            # In caso di errore, usa la configurazione predefinita
            self._config = self.DEFAULT_CONFIG.copy()
            self.logger.info("Usando configurazione predefinita dopo errore")

    def _merge_configs(self, default: dict, user: dict) -> dict:
        """Unisce ricorsivamente la configurazione utente con quella predefinita"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default=None):
        """Ottiene un valore di configurazione usando la notazione dot"""
        try:
            value = self._config
            for part in key.split('.'):
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def model_configs(self) -> dict:
        """Ottiene le configurazioni dei modelli dalla configurazione corrente"""
        return self.get('api.anthropic.models', {})
    
    @property
    def anthropic_api_key(self) -> str:
        """Ottiene la API key di Anthropic"""
        return self.get('api.anthropic.api_key', '')

    @property
    def anthropic_default_model(self) -> str:
        """Ottiene il modello Anthropic predefinito"""
        return self.get('api.anthropic.default_model', 'claude-3-5-haiku-20241022')

    @property
    def openai_api_key(self) -> str:
        """Ottiene la API key di OpenAI"""
        return self.get('api.openai.api_key', '')

    @property
    def perplexity_api_key(self) -> str:
        """Ottiene la API key di Perplexity"""
        return self.get('api.perplexity.api_key', '')
