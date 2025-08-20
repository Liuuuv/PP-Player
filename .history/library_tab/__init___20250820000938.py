# Imports communs pour le module library_tab - Version indépendante
import sys
import os

# Imports de base nécessaires
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
import time
import threading
from PIL import Image, ImageTk

# Imports locaux indépendants
from .config_local import get_config, get_library_config, load_main_config
from .utils import (
    safe_file_operation, get_file_duration, format_duration,
    normalize_filename, is_audio_file, get_audio_files_in_directory,
    create_directory_if_not_exists, ThreadSafeCache, create_tooltip,
    debounce, log_performance
)

# Essayer de charger la configuration principale si disponible
try:
    load_main_config()
except Exception as e:
    print(f"Impossible de charger la config principale: {e}")

# Imports optionnels du projet principal (avec fallback)
def safe_import(module_name, fallback=None):
    """Importe un module de manière sécurisée avec fallback"""
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        return __import__(module_name)
    except ImportError as e:
        print(f"Module {module_name} non disponible: {e}")
        return fallback

# Imports optionnels
config_module = safe_import('config')
setup_module = safe_import('setup')
file_services_module = safe_import('file_services')
tools_module = safe_import('tools')

# Fonction de compatibilité pour get_config
def get_config_compat(key, default=None):
    """Fonction de compatibilité pour get_config"""
    # Essayer d'abord la config locale
    local_value = get_config(key, None)
    if local_value is not None:
        return local_value
    
    # Essayer la config principale
    if config_module and hasattr(config_module, key):
        return getattr(config_module, key)
    
    return default

# Remplacer get_config par la version compatible
get_config = get_config_compat