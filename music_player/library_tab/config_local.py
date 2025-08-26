"""
Configuration locale pour le module library_tab
Indépendante du système de configuration principal
"""

# Configuration par défaut pour library_tab
LIBRARY_CONFIG = {
    # Chargement progressif
    'load_more_count': 20,
    'scroll_threshold': 0.8,  # Seuil pour déclencher le chargement (80% du bas)
    
    # Performance
    'enable_progressive_loading': True,
    'enable_thumbnail_caching': True,
    'enable_duration_caching': True,
    'batch_size': 50,
    
    # Debug
    'debug_scroll': False,
    'debug_loading': False,
    
    # Interface
    'item_height': 60,
    'thumbnail_size': (50, 50),
    'default_thumbnail_path': 'assets/none.png',
    
    # Couleurs du thème
    'bg_color': '#3d3d3d',
    'fg_color': 'white',
    'active_bg_color': '#4a4a4a',
    'selected_bg_color': '#555555',
    'text_color': '#cccccc',
    'secondary_text_color': '#888888',
}

def get_library_config(key, default=None):
    """Récupère une valeur de configuration locale"""
    return LIBRARY_CONFIG.get(key, default)

def set_library_config(key, value):
    """Définit une valeur de configuration locale"""
    LIBRARY_CONFIG[key] = value

def update_library_config(config_dict):
    """Met à jour plusieurs valeurs de configuration"""
    LIBRARY_CONFIG.update(config_dict)

# Fonction de compatibilité avec l'ancien système
def get_config(key, default=None):
    """Fonction de compatibilité - essaie d'abord la config locale, puis la config principale"""
    # Essayer d'abord la config locale
    if key in LIBRARY_CONFIG:
        return LIBRARY_CONFIG[key]
    
    # Essayer la config principale si disponible
    try:
        import config
        return getattr(config, key, default)
    except (ImportError, AttributeError):
        return default

# Fonction pour charger la config depuis le fichier principal si disponible
def load_main_config():
    """Charge la configuration depuis le fichier principal si disponible"""
    try:
        import config
        
        # Mapper les configurations principales vers les locales
        config_mapping = {
            'load_more_count': 'load_more_count',
            'debug_scroll': 'debug_scroll',
            'enable_progressive_loading': 'enable_progressive_loading',
        }
        
        for main_key, local_key in config_mapping.items():
            if hasattr(config, main_key):
                LIBRARY_CONFIG[local_key] = getattr(config, main_key)
                
        print("Configuration principale chargée dans library_tab")
        
    except ImportError:
        print("Configuration principale non disponible, utilisation de la config locale")