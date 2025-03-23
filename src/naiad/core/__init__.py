"""Core components for NAIAD"""
from .environment import env, is_frozen, get_app_root, get_resource_path, get_data_path
from .main import NAIADApplication

__all__ = ['NAIADApplication']