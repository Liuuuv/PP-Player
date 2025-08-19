# Configuration spécifique au module artist_tab
# Ce fichier contient toutes les constantes et configurations pour les pages d'artiste

# ==================== CONFIGURATION INTERFACE ====================

# Couleurs pour les pages d'artiste
ARTIST_COLORS = {
    'background': '#3d3d3d',
    'frame_bg': '#4a4a4a',
    'frame_hover': '#5a5a5a',
    'text_primary': 'white',
    'text_secondary': '#aaaaaa',
    'text_error': '#ff6666',
    'border': '#555555',
    'button_bg': '#555555',
    'button_hover': '#666666'
}

# Dimensions et espacements
ARTIST_LAYOUT = {
    'thumbnail_size': 60,
    'frame_padding': 3,
    'frame_margin': 1,
    'text_padding': 5,
    'button_padding': 10
}

# Polices
ARTIST_FONTS = {
    'title': ('TkDefaultFont', 8),
    'subtitle': ('TkDefaultFont', 7),
    'button': ('TkDefaultFont', 8),
    'loading': ('TkDefaultFont', 10)
}

# ==================== CONFIGURATION RECHERCHE ====================

# Options YouTube-DL optimisées pour les recherches d'artiste
ARTIST_SEARCH_OPTIONS = {
    'extract_flat': True,
    'quiet': True,
    'no_warnings': True,
    'ignoreerrors': True,
    'socket_timeout': 3,    # Timeout ultra-court
    'retries': 0,           # Pas de retry pour plus de rapidité
    'fragment_retries': 0,  # Pas de retry pour les fragments
    'skip_unavailable_fragments': True,
    'abort_on_unavailable_fragment': False,
    'concurrent_fragment_downloads': 1
}

# Limites de recherche optimisées
ARTIST_SEARCH_LIMITS = {
    'max_videos': 20,      # Réduit pour plus de rapidité
    'max_releases': 15,    # Réduit pour plus de rapidité
    'max_playlists': 10,   # Réduit pour plus de rapidité
    'batch_size': 6,       # Augmenté pour plus d'efficacité
    'display_delay': 5     # Réduit pour plus de rapidité
}

# Cache
ARTIST_CACHE_CONFIG = {
    'enable_cache': True,
    'cache_duration': 3600,  # 1 heure en secondes
    'max_cache_size': 100  # Nombre maximum d'artistes en cache
}

# ==================== CONFIGURATION MESSAGES ====================

# Messages d'interface
ARTIST_MESSAGES = {
    'loading': {
        'channel_id': "Recherche de l'ID de la chaîne...",
        'videos': "Chargement des vidéos...",
        'releases': "Chargement des sorties...",
        'playlists': "Chargement des playlists...",
        'playlist_content': "Chargement du contenu de la playlist...",
        'thumbnail': "Chargement...",
        'count': "Chargement..."
    },
    'errors': {
        'channel_not_found': "Impossible de trouver l'ID de la chaîne",
        'no_videos': "Aucune vidéo trouvée pour cet artiste",
        'no_releases': "Aucune sortie trouvée pour cet artiste",
        'no_playlists': "Aucune playlist trouvée pour cet artiste",
        'playlist_load_error': "Erreur lors du chargement de la playlist",
        'search_cancelled': "Recherche annulée",
        'network_error': "Erreur de connexion"
    },
    'buttons': {
        'back': "← Retour",
        'load_more': "Charger plus...",
        'retry': "Réessayer"
    }
}

# ==================== CONFIGURATION ONGLETS ====================

# Configuration des onglets d'artiste
ARTIST_TABS = {
    'songs': {
        'title': 'Musiques',
        'icon': '🎵',
        'enabled': True
    },
    'releases': {
        'title': 'Sorties',
        'icon': '💿',
        'enabled': True
    },
    'playlists': {
        'title': 'Playlists',
        'icon': '📁',
        'enabled': True
    }
}

# ==================== CONFIGURATION MINIATURES ====================

# Configuration des miniatures optimisée
ARTIST_THUMBNAILS = {
    'default_size': (60, 45),
    'quality': 'medium',  # low, medium, high
    'cache_thumbnails': True,
    'timeout': 3,  # Timeout réduit pour plus de rapidité
    'retry_count': 0,  # Pas de retry pour plus de rapidité
    'max_cache_size': 100,  # Limite du cache
    'expire_time': 300  # 5 minutes
}

# ==================== CONFIGURATION URLS ====================

# Patterns d'URL YouTube
YOUTUBE_PATTERNS = {
    'channel_by_id': 'https://www.youtube.com/channel/{channel_id}',
    'channel_videos': 'https://www.youtube.com/channel/{channel_id}/videos',
    'channel_releases': 'https://www.youtube.com/channel/{channel_id}/releases',
    'channel_playlists': 'https://www.youtube.com/channel/{channel_id}/playlists',
    'search_channel': 'https://www.youtube.com/@{username}',
    'search_query': 'ytsearch1:{query} channel'
}

# ==================== FONCTIONS UTILITAIRES ====================

def get_artist_color(color_name):
    """Récupère une couleur de la configuration"""
    return ARTIST_COLORS.get(color_name, '#3d3d3d')

def get_artist_font(font_name):
    """Récupère une police de la configuration"""
    return ARTIST_FONTS.get(font_name, ('TkDefaultFont', 8))

def get_artist_message(category, message_key):
    """Récupère un message de la configuration"""
    return ARTIST_MESSAGES.get(category, {}).get(message_key, "")

def get_search_limit(limit_name):
    """Récupère une limite de recherche"""
    return ARTIST_SEARCH_LIMITS.get(limit_name, 10)

def get_youtube_url(pattern_name, **kwargs):
    """Génère une URL YouTube selon un pattern"""
    pattern = YOUTUBE_PATTERNS.get(pattern_name, "")
    try:
        return pattern.format(**kwargs)
    except KeyError:
        return ""

# ==================== VALIDATION ====================

def validate_artist_config():
    """Valide la configuration du module artist_tab"""
    required_colors = ['background', 'frame_bg', 'text_primary']
    required_fonts = ['title', 'subtitle']
    required_limits = ['max_videos', 'batch_size']
    
    errors = []
    
    # Vérifier les couleurs requises
    for color in required_colors:
        if color not in ARTIST_COLORS:
            errors.append(f"Couleur manquante: {color}")
    
    # Vérifier les polices requises
    for font in required_fonts:
        if font not in ARTIST_FONTS:
            errors.append(f"Police manquante: {font}")
    
    # Vérifier les limites requises
    for limit in required_limits:
        if limit not in ARTIST_SEARCH_LIMITS:
            errors.append(f"Limite manquante: {limit}")
    
    if errors:
        print("Erreurs de configuration artist_tab:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

# Valider la configuration au chargement
if __name__ == "__main__":
    if validate_artist_config():
        print("Configuration artist_tab valide ✓")
    else:
        print("Configuration artist_tab invalide ✗")