#!/usr/bin/env python3
"""
Configuration des paramètres d'optimisation de la playlist
"""

# Seuils d'optimisation
WINDOWING_THRESHOLD = 50  # Nombre de musiques à partir duquel activer le fenêtrage
WINDOW_SIZE = 30  # Nombre d'éléments à afficher dans la fenêtre
PRELOAD_SIZE = 20  # Nombre d'éléments à précharger en arrière-plan
JUMP_SIZE = 15  # Nombre de chansons à sauter lors de la navigation rapide

# Paramètres de performance
BATCH_SIZE = 50  # Taille des lots pour l'affichage par batch
REFRESH_DELAY = 50  # Délai en ms pour le rafraîchissement asynchrone
BUTTON_DISABLE_DELAY = 150  # Délai en ms pour réactiver les boutons

# Paramètres visuels
QUEUE_LINE_WIDTH = 3  # Largeur du trait de queue
QUEUE_LINE_PADX = (2, 0)  # Padding horizontal du trait de queue
QUEUE_LINE_PADY = 5  # Padding vertical du trait de queue

def get_optimization_level(playlist_size):
    """Retourne le niveau d'optimisation selon la taille de la playlist"""
    if playlist_size <= 20:
        return "none"  # Pas d'optimisation
    elif playlist_size <= WINDOWING_THRESHOLD:
        return "light"  # Optimisations légères
    elif playlist_size <= 200:
        return "medium"  # Fenêtrage activé
    else:
        return "heavy"  # Optimisations maximales

def should_use_windowing(playlist_size):
    """Détermine si le fenêtrage doit être utilisé"""
    return playlist_size > WINDOWING_THRESHOLD

def get_window_size(playlist_size):
    """Retourne la taille de fenêtre optimale selon la taille de la playlist"""
    if playlist_size <= WINDOWING_THRESHOLD:
        return playlist_size  # Afficher tout
    elif playlist_size <= 100:
        return WINDOW_SIZE
    elif playlist_size <= 500:
        return min(40, playlist_size)  # Fenêtre plus grande pour les playlists moyennes
    else:
        return min(50, playlist_size)  # Fenêtre encore plus grande pour les très grandes playlists

def get_preload_size(playlist_size):
    """Retourne le nombre d'éléments à précharger"""
    if playlist_size <= WINDOWING_THRESHOLD:
        return 0  # Pas de préchargement nécessaire
    elif playlist_size <= 200:
        return PRELOAD_SIZE
    else:
        return min(30, playlist_size // 10)  # Préchargement adaptatif

# Configuration utilisateur (peut être modifiée)
USER_CONFIG = {
    "windowing_threshold": WINDOWING_THRESHOLD,
    "window_size": WINDOW_SIZE,
    "preload_size": PRELOAD_SIZE,
    "jump_size": JUMP_SIZE,
    "enable_optimizations": True,
    "enable_preloading": True,
    "enable_async_refresh": True
}

def update_config(**kwargs):
    """Met à jour la configuration utilisateur"""
    USER_CONFIG.update(kwargs)

def get_config(key, default=None):
    """Récupère une valeur de configuration"""
    return USER_CONFIG.get(key, default)