"""
Utilitaires indépendants pour le module library_tab
"""

import os
import time
import threading
from pathlib import Path

def safe_file_operation(func, *args, **kwargs):
    """Exécute une opération sur fichier de manière sécurisée"""
    try:
        return func(*args, **kwargs)
    except (OSError, IOError, PermissionError) as e:
        print(f"Erreur d'opération fichier: {e}")
        return None

def get_file_duration(filepath):
    """Obtient la durée d'un fichier audio de manière indépendante"""
    try:
        from mutagen.mp3 import MP3
        from mutagen.flac import FLAC
        from mutagen.mp4 import MP4
        from mutagen.oggvorbis import OggVorbis
        
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.mp3':
            audio = MP3(filepath)
        elif ext == '.flac':
            audio = FLAC(filepath)
        elif ext in ['.m4a', '.mp4']:
            audio = MP4(filepath)
        elif ext == '.ogg':
            audio = OggVorbis(filepath)
        else:
            return None
            
        return audio.info.length if audio.info else None
        
    except Exception as e:
        print(f"Erreur lors de la lecture de la durée de {filepath}: {e}")
        return None

def format_duration(seconds):
    """Formate une durée en secondes vers mm:ss"""
    if seconds is None:
        return "00:00"
    
    try:
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    except (ValueError, TypeError):
        return "00:00"

def normalize_filename(filename):
    """Normalise un nom de fichier pour la recherche"""
    return os.path.basename(filename).lower()

def is_audio_file(filepath):
    """Vérifie si un fichier est un fichier audio supporté"""
    audio_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.mp4'}
    ext = os.path.splitext(filepath)[1].lower()
    return ext in audio_extensions

def get_audio_files_in_directory(directory):
    """Récupère tous les fichiers audio dans un répertoire"""
    if not os.path.exists(directory):
        return []
    
    audio_files = []
    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and is_audio_file(filepath):
                audio_files.append(filepath)
    except (OSError, PermissionError) as e:
        print(f"Erreur lors de la lecture du répertoire {directory}: {e}")
    
    return sorted(audio_files)

def create_directory_if_not_exists(directory):
    """Crée un répertoire s'il n'existe pas"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        print(f"Erreur lors de la création du répertoire {directory}: {e}")
        return False

class ThreadSafeCache:
    """Cache thread-safe pour les métadonnées"""
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
    
    def get(self, key, default=None):
        with self._lock:
            return self._cache.get(key, default)
    
    def set(self, key, value):
        with self._lock:
            self._cache[key] = value
    
    def clear(self):
        with self._lock:
            self._cache.clear()
    
    def keys(self):
        with self._lock:
            return list(self._cache.keys())

class SimpleTooltip:
    """Tooltip simple et indépendant"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        
        try:
            import tkinter as tk
            
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25
            
            self.tooltip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(tw, text=self.text, justify='left',
                           background='#ffffe0', relief='solid', borderwidth=1,
                           font=('Arial', 8))
            label.pack(ipadx=1)
        except Exception as e:
            print(f"Erreur tooltip: {e}")
    
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def create_tooltip(widget, text):
    """Crée un tooltip pour un widget"""
    return SimpleTooltip(widget, text)

def debounce(wait_time):
    """Décorateur pour limiter la fréquence d'appel d'une fonction"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            def call_func():
                func(*args, **kwargs)
            
            # Annuler l'appel précédent s'il existe
            if hasattr(wrapper, '_timer'):
                wrapper._timer.cancel()
            
            # Programmer le nouvel appel
            wrapper._timer = threading.Timer(wait_time, call_func)
            wrapper._timer.start()
        
        return wrapper
    return decorator

def log_performance(func_name, start_time):
    """Log simple des performances"""
    duration = time.time() - start_time
    if duration > 0.1:  # Log seulement si > 100ms
        print(f"⏱️ {func_name}: {duration:.3f}s")