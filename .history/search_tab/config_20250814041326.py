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
    'force_update_every': 2            # Forcer update_idletasks tous les N lots
}

# Paramètres d'interface
INTERFACE_CONFIG = {
    'show_thumbnails': True,           # Afficher les miniatures
    'thumbnail_size': (120, 90),       # Taille des miniatures (largeur, hauteur)
    'show_duration': True,             # Afficher la durée des vidéos
    'show_view_count': True,           # Afficher le nombre de vues
    'show_upload_date': True,          # Afficher la date d'upload
    'auto_scroll_to_new': False        # Auto-scroll vers les nouveaux résultats
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
    print("=====================================")

# Validation automatique au chargement
_validation_errors = validate_search_config()
if _validation_errors:
    print("ERREURS DE CONFIGURATION:")
    for error in _validation_errors:
        print(f"  - {error}")