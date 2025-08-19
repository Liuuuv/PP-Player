# Configuration Centralisée - Onglet Recherche

## 📁 Nouveau fichier de configuration

Tous les paramètres de l'onglet de recherche et de l'onglet artiste sont maintenant centralisés dans :
**`search_tab/config.py`**

## 🔧 Paramètres configurables

### 🔍 **Recherche YouTube**
```python
YOUTUBE_SEARCH_OPTIONS = {
    'quiet': True,
    'socket_timeout': 10,
    'retries': 2,
    # ... autres options yt-dlp
}

SEARCH_LIMITS = {
    'max_results_per_search': 50,    # Nombre max de résultats
    'initial_results': 30,           # Résultats initiaux
    'load_more_batch': 20,           # Lot "Charger plus"
    'max_total_results': 200         # Limite absolue
}
```

### 📊 **Affichage par lots**
```python
DISPLAY_BATCHING = {
    'batch_size': 10,                # Résultats par lot
    'batch_delay': 8,                # Délai entre lots (ms)
    'cache_batch_size': 15,          # Lots plus gros pour cache
    'cache_batch_delay': 2,          # Délai cache (ms)
    'wait_time_between_results': 20  # Délai entre résultats
}
```

### 🎨 **Interface utilisateur**
```python
INTERFACE_CONFIG = {
    'show_thumbnails': True,
    'thumbnail_size': (120, 90),
    'show_duration': True,
    'show_view_count': True,
    'max_duration_show_search': 600  # 10 minutes
}

UI_COLORS = {
    'cache_indicator_color': '#00ff00',    # Vert cache
    'normal_text_color': 'white',
    'error_color': '#ff4444',
    'cache_indicator_duration': 3000       # 3 secondes
}
```

### 💾 **Cache intelligent**
```python
SEARCH_CACHE_CONFIG = {
    'max_searches': 50,              # Recherches en cache
    'search_expire_time': 3600,      # 1 heure
    'max_interface_states': 20,      # États d'interface
    'cache_file': 'downloads/search_cache.json'
}

THUMBNAIL_CACHE_CONFIG = {
    'max_thumbnails': 200,           # Miniatures en cache
    'thumbnail_expire_time': 1800,   # 30 minutes
    'thumbnail_timeout': 5,          # Timeout téléchargement
    'preload_thumbnails': True
}
```

### 🧠 **Préchargement intelligent**
```python
PRELOAD_CONFIG = {
    'enable_intelligent_preload': True,
    'min_usage_count': 2,            # Min utilisations
    'preload_recency_hours': 24,     # Recherches récentes
    'max_preload_searches': 3,       # Max préchargements
    'preload_delay_seconds': 30,     # Délai entre préchargements
    'preload_check_interval_hours': 2 # Vérification toutes les 2h
}
```

### 🎭 **Onglet Artiste**
```python
ARTIST_TAB_CONFIG = {
    'max_width_artist_name': 90,     # Largeur max nom (px)
    'thumbnail_pool_size': 4,        # Pool miniatures
    'playlist_pool_size': 2,         # Pool playlists
    'max_artists_cache': 15,         # Cache artistes
    'max_playlists_cache': 30,       # Cache playlists
    'search_limits': {
        'videos': 50,                # Max vidéos par artiste
        'releases': 30,              # Max sorties
        'playlists': 25              # Max playlists
    }
}
```

### ⚡ **Performance**
```python
PERFORMANCE_CONFIG = {
    'use_thread_pools': True,
    'thumbnail_pool_size': 4,
    'search_pool_size': 2,
    'debounce_search_ms': 500,
    'cleanup_interval_minutes': 10,
    'max_concurrent_downloads': 3
}

NETWORK_CONFIG = {
    'search_timeout': 15,            # Timeout recherche
    'thumbnail_timeout': 5,          # Timeout miniatures
    'max_retries': 2,                # Tentatives max
    'connection_timeout': 10
}
```

## 🛠️ **Fonctions utilitaires**

```python
# Récupérer des paramètres
from search_tab.config import (
    get_search_limit,
    get_display_config,
    get_cache_config,
    get_preload_config,
    get_artist_config,
    get_ui_message,
    get_ui_color
)

# Exemples d'utilisation
batch_size = get_display_config('batch_size')
cache_color = get_ui_color('cache_indicator_color')
max_searches = get_cache_config('max_searches', 'search')
artist_width = get_artist_config('max_width_artist_name')
```

## 📈 **Afficher la configuration**

```python
from search_tab.config import print_config_summary
print_config_summary()
```

Affiche :
```
=== CONFIGURATION ONGLET RECHERCHE ===
Résultats par recherche: 50
Taille des lots: 10
Délai entre lots: 8ms
Cache recherches: 50
Cache miniatures: 200
Préchargement: Activé
Pools de threads: Activés

=== CONFIGURATION ONGLET ARTISTE ===
Largeur max nom artiste: 90px
Pool miniatures artiste: 4
Pool playlists artiste: 2
Cache artistes: 15
Cache playlists: 30
Limites recherche artiste: {'videos': 50, 'releases': 30, 'playlists': 25}
=====================================
```

## 🔄 **Migration depuis config.py**

### Paramètres déplacés :
- ❌ `SEARCH_WAIT_TIME_BETWEEN_RESULTS` → ✅ `DISPLAY_BATCHING['wait_time_between_results']`
- ❌ `THUMBNAIL_SIZE` → ✅ `INTERFACE_CONFIG['default_thumbnail_size']`
- ❌ `MAX_DURATION_SHOW_SEARCH` → ✅ `INTERFACE_CONFIG['max_duration_show_search']`
- ❌ `ARTIST_TAB_MAX_WIDTH_ARTIST_NAME` → ✅ `ARTIST_TAB_CONFIG['max_width_artist_name']`

### Fichiers mis à jour :
- ✅ `search_tab/results.py` - Utilise la nouvelle config
- ✅ `artist_tab/core.py` - Utilise la nouvelle config
- ✅ `artist_tab/cache_manager.py` - Utilise la nouvelle config
- ✅ `artist_tab_manager.py` - Utilise la nouvelle config

## 🎯 **Avantages**

### ✅ **Centralisation**
- Tous les paramètres au même endroit
- Plus facile à maintenir et modifier
- Configuration cohérente

### ✅ **Flexibilité**
- Paramètres facilement ajustables
- Validation automatique des valeurs
- Valeurs par défaut sécurisées

### ✅ **Performance**
- Optimisations configurables
- Adaptation selon les besoins
- Monitoring des performances

### ✅ **Maintenance**
- Code plus propre et organisé
- Moins de valeurs hardcodées
- Documentation intégrée

## 🚀 **Utilisation**

Pour modifier un paramètre, il suffit d'éditer `search_tab/config.py` :

```python
# Exemple : Augmenter la taille des lots pour plus de vitesse
DISPLAY_BATCHING = {
    'batch_size': 15,        # Au lieu de 10
    'batch_delay': 5,        # Au lieu de 8
    # ...
}
```

**Tous les changements sont appliqués immédiatement au redémarrage !** 🎉

## 📝 **Notes importantes**

- ⚠️ **Validation automatique** : Les valeurs incorrectes sont détectées au démarrage
- 🔒 **Valeurs par défaut** : Si la config n'est pas accessible, des valeurs sûres sont utilisées
- 🔄 **Rétrocompatibilité** : L'ancien système continue de fonctionner en cas d'erreur

**La configuration est maintenant centralisée, flexible et facile à utiliser !** 🚀