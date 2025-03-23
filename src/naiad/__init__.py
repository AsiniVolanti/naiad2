"""
NAIAD - Nick's AI Assistant for Dialogue
"""

__version__ = "1.0.0"
__author__ = "G.Fogliazza"
# Import only what's needed at package level
from naiad.core.environment import env, is_frozen, get_app_root, get_resource_path, get_data_path
from naiad.core.main import NAIADApplication
from naiad.config.settings import Settings
from naiad.utils.logger import setup_logger


__all__ = [
    'NAIADApplication',
    'Settings',
    'setup_logger',
    'env',
    'is_frozen',
    'get_app_root',
    'get_resource_path',
    'get_data_path'
]
