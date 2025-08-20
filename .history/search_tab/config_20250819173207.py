# Configuration centralisée pour l'onglet de recherche YouTube
# Tous les paramètres configurables pour optimiser les performances et l'expérience utilisateur

# ==================== CONFIGURATION RECHERCHE YOUTUBE ====================

# Paramètres de recherche YouTube-DL
YOUTUBE_SEARCH_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
    'default_search': 'ytsearch',
    'ignoreerrors': True,
    'socket_timeout': 10,
    'retries': 2,
    'fragment_retries': 2,
    'skip_unavailable_fragments': True,
    'abort_on_unavailable_fragment': False
}

# Limites de recherche
SEARCH_LIMITS = {
    'max_results_per_search': 50,      # Nombre maximum de résultats par recherche
    'initial_results': 30,             # Nombre de résultats à charger initialement
    'load_more_batch': 20,             # Nombre de résultats à charger avec "Charger plus"
    'max_total_results': 200           # Limite absolue de résultats
}

# ==================== CONFIGURATION AFFICHAGE ====================

# Paramètres d'affichage par lots
DISPLAY_BATCHING = {
    'batch_size': 10,                  # Nombre de résultats à afficher par lot
    'batch_delay': 8,                  # Délai entre les lots (millisecondes)
    'cache_batch_size': 15,            # Lots plus gros pour l'affichage depuis le cache
    'cache_batch_delay': 2,            # Délai plus court pour le cache
    'force_update_every': 2,           # Forcer update_idletasks tous les N lots
    'wait_time_between_results': 20    # Délai d'attente entre résultats (déplacé depuis config.py)
}

# Paramètres d'interface
INTERFACE_CONFIG = {
    'show_thumbnails': True,           # Afficher les miniatures
    'thumbnail_size': (120, 90),       # Taille des miniatures (largeur, hauteur)
    'default_thumbnail_size': (80, 45), # Taille par défaut (déplacé depuis config.py)
    'circular_thumbnail_size': (45, 45), # Taille miniatures circulaires (déplacé depuis config.py)
    'show_duration': True,             # Afficher la durée des vidéos
    'show_view_count': True,           # Afficher le nombre de vues
    'show_upload_date': True,          # Afficher la date d'upload
    'auto_scroll_to_new': False,       # Auto-scroll vers les nouveaux résultats
    'max_duration_show_search': 600    # Durée max pour afficher résultats (10 min, déplacé depuis config.py)
}

# ==================== CONFIGURATION CACHE ====================

# Cache des recherches
SEARCH_CACHE_CONFIG = {
    'max_searches': 50,                # Nombre maximum de recherches en cache
    'search_expire_time': 3600,        # Expiration des recherches (secondes) - 1 heure
    'max_interface_states': 20,        # États d'interface sauvegardés
    'save_scroll_position': True,      # Sauvegarder la position de scroll
    'cache_file': 'downloads/search_cache.json'  # Fichier de sauvegarde
}

# Cache des miniatures
THUMBNAIL_CACHE_CONFIG = {
    'max_thumbnails': 200,             # Nombre maximum de miniatures en cache
    'thumbnail_expire_time': 1800,     # Expiration des miniatures (secondes) - 30 minutes
    'thumbnail_timeout': 5,            # Timeout pour télécharger une miniature
    'thumbnail_retries': 1,            # Nombre de tentatives pour les miniatures
    'preload_thumbnails': True         # Précharger les miniatures visibles
}

# ==================== CONFIGURATION PRÉCHARGEMENT ====================

# Préchargement intelligent
PRELOAD_CONFIG = {
    'enable_intelligent_preload': True,    # Activer le préchargement intelligent
    'min_usage_count': 2,                  # Nombre minimum d'utilisations pour précharger
    'preload_recency_hours': 24,           # Recherches récentes à considérer (heures)
    'max_preload_searches': 3,             # Nombre maximum de recherches à précharger
    'preload_delay_seconds': 30,           # Délai entre chaque préchargement
    'preload_check_interval_hours': 2,     # Vérification des nouveaux préchargements
    'preload_start_delay_minutes': 5       # Délai avant le premier préchargement
}

# ==================== CONFIGURATION ONGLET ARTISTE ====================

# Paramètres spécifiques à l'onglet artiste
ARTIST_TAB_CONFIG = {
    'max_width_artist_name': 90,       # Largeur max nom artiste (déplacé depuis config.py)
    'thumbnail_pool_size': 4,          # Taille du pool pour miniatures artiste
    'playlist_pool_size': 2,           # Taille du pool pour playlists artiste
    'max_artists_cache': 15,           # Nombre max d'artistes en cache
    'max_playlists_cache': 30,         # Nombre max de playlists en cache
    'search_limits': {
        'videos': 25,                  # Limite vidéos par artiste
        'releases': 25,                # Limite sorties par artiste
        'playlists': 25                # Limite playlists par artiste
    }
}

# ==================== CONFIGURATION PERFORMANCE ====================

# Optimisations de performance
PERFORMANCE_CONFIG = {
    'use_thread_pools': True,          # Utiliser des pools de threads
    'thumbnail_pool_size': 4,          # Taille du pool pour les miniatures
    'search_pool_size': 2,             # Taille du pool pour les recherches
    'debounce_search_ms': 500,         # Délai de debounce pour la recherche automatique
    'cleanup_interval_minutes': 10,    # Intervalle de nettoyage du cache
    'max_concurrent_downloads': 3      # Téléchargements simultanés maximum
}

# Timeouts et retry
NETWORK_CONFIG = {
    'search_timeout': 15,              # Timeout pour les recherches (secondes)
    'thumbnail_timeout': 5,            # Timeout pour les miniatures (secondes)
    'max_retries': 2,                  # Nombre maximum de tentatives
    'retry_delay': 1,                  # Délai entre les tentatives (secondes)
    'connection_timeout': 10           # Timeout de connexion (secondes)
}

# ==================== CONFIGURATION INTERFACE UTILISATEUR ====================

# Messages et textes
UI_MESSAGES = {
    'searching': "Recherche en cours...",
    'loading_more': "Chargement de plus de résultats...",
    'cache_restored': "⚡ {count} résultats restaurés instantanément (cache)",
    'search_completed': "Recherche terminée - {count} résultats trouvés",
    'no_results': "Aucun résultat trouvé",
    'error_occurred': "Erreur lors de la recherche",
    'preload_message': "Préchargement: '{query}' (basé sur votre historique)"
}

# Couleurs et styles
UI_COLORS = {
    'cache_indicator_color': '#00ff00',    # Vert pour les résultats depuis le cache
    'normal_text_color': 'white',          # Couleur normale du texte
    'error_color': '#ff4444',              # Rouge pour les erreurs
    'success_color': '#44ff44',            # Vert pour les succès
    'cache_indicator_duration': 3000       # Durée d'affichage de l'indicateur cache (ms)
}

# ==================== FONCTIONS UTILITAIRES ====================

def get_search_limit(key):
    """Récupère une limite de recherche"""
    return SEARCH_LIMITS.get(key, 30)

def get_display_config(key):
    """Récupère un paramètre d'affichage"""
    return DISPLAY_BATCHING.get(key, 10)

def get_cache_config(key, cache_type='search'):
    """Récupère un paramètre de cache"""
    if cache_type == 'search':
        return SEARCH_CACHE_CONFIG.get(key)
    elif cache_type == 'thumbnail':
        return THUMBNAIL_CACHE_CONFIG.get(key)
    return None

def get_preload_config(key):
    """Récupère un paramètre de préchargement"""
    return PRELOAD_CONFIG.get(key)

def get_performance_config(key):
    """Récupère un paramètre de performance"""
    return PERFORMANCE_CONFIG.get(key)

def get_network_config(key):
    """Récupère un paramètre réseau"""
    return NETWORK_CONFIG.get(key)

def get_ui_message(key, **kwargs):
    """Récupère un message d'interface avec formatage"""
    message = UI_MESSAGES.get(key, "")
    if kwargs:
        return message.format(**kwargs)
    return message

def get_ui_color(key):
    """Récupère une couleur d'interface"""
    return UI_COLORS.get(key, 'white')

def get_artist_config(key):
    """Récupère un paramètre de l'onglet artiste"""
    return ARTIST_TAB_CONFIG.get(key)

# ==================== VALIDATION ====================

def validate_search_config():
    """Valide la configuration de recherche"""
    errors = []
    
    # Vérifier les limites
    if SEARCH_LIMITS['max_results_per_search'] < 1:
        errors.append("max_results_per_search doit être >= 1")
    
    if DISPLAY_BATCHING['batch_size'] < 1:
        errors.append("batch_size doit être >= 1")
    
    if SEARCH_CACHE_CONFIG['max_searches'] < 1:
        errors.append("max_searches doit être >= 1")
    
    # Vérifier les timeouts
    if NETWORK_CONFIG['search_timeout'] < 1:
        errors.append("search_timeout doit être >= 1")
    
    return errors

def print_config_summary():
    """Affiche un résumé de la configuration"""
    print("=== CONFIGURATION ONGLET RECHERCHE ===")
    print(f"Résultats par recherche: {SEARCH_LIMITS['max_results_per_search']}")
    print(f"Taille des lots: {DISPLAY_BATCHING['batch_size']}")
    print(f"Délai entre lots: {DISPLAY_BATCHING['batch_delay']}ms")
    print(f"Cache recherches: {SEARCH_CACHE_CONFIG['max_searches']}")
    print(f"Cache miniatures: {THUMBNAIL_CACHE_CONFIG['max_thumbnails']}")
    print(f"Préchargement: {'Activé' if PRELOAD_CONFIG['enable_intelligent_preload'] else 'Désactivé'}")
    print(f"Pools de threads: {'Activés' if PERFORMANCE_CONFIG['use_thread_pools'] else 'Désactivés'}")
    print()
    print("=== CONFIGURATION ONGLET ARTISTE ===")
    print(f"Largeur max nom artiste: {ARTIST_TAB_CONFIG['max_width_artist_name']}px")
    print(f"Pool miniatures artiste: {ARTIST_TAB_CONFIG['thumbnail_pool_size']}")
    print(f"Pool playlists artiste: {ARTIST_TAB_CONFIG['playlist_pool_size']}")
    print(f"Cache artistes: {ARTIST_TAB_CONFIG['max_artists_cache']}")
    print(f"Cache playlists: {ARTIST_TAB_CONFIG['max_playlists_cache']}")
    print(f"Limites recherche artiste: {ARTIST_TAB_CONFIG['search_limits']}")
    print("=====================================")

# ==================== CONFIGURATION MAIN PLAYLIST ====================

# Configuration de l'affichage de la main playlist
MAIN_PLAYLIST_CONFIG = {
    # Seuils d'optimisation
    'windowing_threshold': 50,         # Nombre de musiques à partir duquel activer le fenêtrage
    'small_playlist_threshold': 20,    # Seuil pour petites playlists (pas d'optimisation)
    'large_playlist_threshold': 200,   # Seuil pour grandes playlists (optimisations maximales)
    
    # Paramètres de fenêtrage
    'window_size': 21,                 # Nombre d'éléments à afficher dans la fenêtre (10 avant + 1 courante + 10 après)
    'window_size_small': 21,           # Taille de fenêtre pour playlists moyennes (50-100)
    'window_size_medium': 21,          # Taille de fenêtre pour playlists grandes (100-200)
    'window_size_large': 21,           # Taille de fenêtre pour très grandes playlists (200+)
    'songs_before_current': 10,        # Nombre de musiques à afficher avant la courante
    'songs_after_current': 10,         # Nombre de musiques à afficher après la courante
    
    # Paramètres de préchargement
    'preload_size': 20,                # Nombre d'éléments à précharger en arrière-plan
    'preload_size_large': 30,          # Préchargement pour grandes playlists
    'enable_preloading': True,         # Activer le préchargement des métadonnées
    
    # Paramètres de navigation
    'jump_size': 15,                   # Nombre de chansons à sauter lors de la navigation rapide
    'jump_size_large': 25,             # Saut plus grand pour grandes playlists
    'show_navigation_indicators': True, # Afficher les indicateurs "... X musiques précédentes"
    
    # Paramètres de performance
    'enable_optimizations': True,      # Activer toutes les optimisations
    'enable_async_refresh': True,      # Rafraîchissement asynchrone
    'refresh_delay': 50,               # Délai en ms pour le rafraîchissement asynchrone
    'button_disable_delay': 150,       # Délai en ms pour réactiver les boutons
    'scroll_update_delay': 10,         # Délai en ms pour mettre à jour la région de scroll
    
    # === SYSTÈME DE SCROLL DYNAMIQUE UNIFIÉ ===
    'enable_dynamic_scroll': True,       # Activer le système de scroll dynamique unifié
    'scroll_threshold': 0.05,            # Seuil pour charger plus (5% du haut/bas)
    'load_more_count': 10,               # Nombre de musiques à charger en plus
    'initial_load_after_current': 10,    # Charger 10 musiques après la courante au départ
    'scroll_trigger_threshold': 0.9,     # Déclencher à 90% du scroll vers le bas
    'never_unload': False,               # Désactivé pour permettre le déchargement intelligent
    
    # Paramètres de recentrage automatique
    'auto_center_on_song_change': True,  # Recentrer automatiquement quand la chanson change
    'user_scroll_timeout': 3000,         # Temps (ms) avant de considérer que l'utilisateur a fini de scroller
    'detect_manual_scroll': True,        # Détecter si l'utilisateur scroll manuellement
    'keep_user_position': True,          # Garder la position si l'utilisateur a scrollé ailleurs
    
    # === NOUVEAU SYSTÈME : DÉCHARGEMENT INTELLIGENT ===
    'enable_smart_unloading': True,      # Activer le déchargement intelligent
    'max_loaded_items': 30,              # Nombre maximum d'éléments chargés avant déchargement
    'preserve_current_view': True,       # Préserver les éléments visibles actuellement
    'preserve_items_after_current': 10,  # Nombre d'éléments à préserver après la position courante
    'preserve_items_before_current': 5, # Nombre d'éléments à préserver avant la position courante
    
    # Ancien système (désactivé au profit du progressif)
    'enable_smart_loading': False,       # Ancien système fenêtré 10+1+10 (désactivé)
    'auto_unload_unused': False,         # Pas de déchargement avec le nouveau système
    'keep_buffer_around_current': 10,    # Buffer à garder autour de la chanson courante
    'keep_buffer_around_view': 5,        # Buffer à garder autour de la position de vue
    'unload_threshold': 50,              # Distance à partir de laquelle décharger (en éléments)
    'reload_on_song_change': False,      # Pas de rechargement complet avec le nouveau système
    
    # Paramètres d'affichage
    'item_height_estimate': 60,        # Hauteur estimée par élément (pour calcul scroll)
    'force_scroll_update': True,       # Forcer la mise à jour du scroll après rafraîchissement
    'smooth_scroll_duration': 500,     # Durée de l'animation de scroll (ms)

    # Modes d'affichage
    'display_modes': {
        'auto': 'Automatique (selon la taille)',
        'full': 'Affichage complet (toujours)',
        'windowed': 'Fenêtrage (toujours)',
        'performance': 'Performance maximale'
    },
    'default_display_mode': 'auto',    # Mode d'affichage par défaut
    
    # Paramètres de debug
    'debug_windowing': True,          # Afficher les infos de debug du fenêtrage
    'debug_scroll': True,             # Afficher les infos de debug du scroll
    'debug_performance': False         # Afficher les infos de performance
}



def get_main_playlist_config(key):
    """Récupère un paramètre de configuration de la main playlist"""
    return MAIN_PLAYLIST_CONFIG.get(key)

def update_main_playlist_config(**kwargs):
    """Met à jour la configuration de la main playlist"""
    MAIN_PLAYLIST_CONFIG.update(kwargs)

def get_optimal_window_size(playlist_size):
    """Retourne la taille de fenêtre optimale selon la taille de la playlist"""
    if playlist_size <= MAIN_PLAYLIST_CONFIG['small_playlist_threshold']:
        return playlist_size  # Afficher tout
    elif playlist_size <= 100:
        return MAIN_PLAYLIST_CONFIG['window_size_small']
    elif playlist_size <= MAIN_PLAYLIST_CONFIG['large_playlist_threshold']:
        return MAIN_PLAYLIST_CONFIG['window_size_medium']
    else:
        return MAIN_PLAYLIST_CONFIG['window_size_large']

def get_optimal_preload_size(playlist_size):
    """Retourne la taille de préchargement optimale selon la taille de la playlist"""
    if playlist_size <= MAIN_PLAYLIST_CONFIG['small_playlist_threshold']:
        return 0  # Pas de préchargement nécessaire
    elif playlist_size <= MAIN_PLAYLIST_CONFIG['large_playlist_threshold']:
        return MAIN_PLAYLIST_CONFIG['preload_size']
    else:
        return MAIN_PLAYLIST_CONFIG['preload_size_large']

def should_use_windowing(playlist_size):
    """Détermine si le fenêtrage doit être utilisé selon la configuration"""
    if not MAIN_PLAYLIST_CONFIG['enable_optimizations']:
        return False
    
    mode = MAIN_PLAYLIST_CONFIG['default_display_mode']
    if mode == 'full':
        return False
    elif mode == 'windowed':
        return True
    elif mode == 'performance':
        return playlist_size > MAIN_PLAYLIST_CONFIG['small_playlist_threshold']
    else:  # mode == 'auto'
        return playlist_size > MAIN_PLAYLIST_CONFIG['windowing_threshold']

# Validation automatique au chargement
_validation_errors = validate_search_config()
if _validation_errors:
    print("ERREURS DE CONFIGURATION:")
    for error in _validation_errors:
        print(f"  - {error}")