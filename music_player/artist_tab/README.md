# Module Artist Tab - Documentation

## Vue d'ensemble

Le module `artist_tab` est maintenant complètement indépendant et centralisé. Toutes les fonctionnalités liées aux pages d'artiste sont organisées dans ce dossier.

## Structure du module

```
artist_tab/
├── __init__.py          # Imports communs et utilitaires
├── main.py              # Module principal avec classe ArtistTabModule
├── core.py              # Fonctions principales et gestion des onglets
├── songs.py             # Gestion des vidéos/musiques d'artiste
├── releases.py          # Gestion des albums et singles
├── playlists.py         # Gestion des playlists d'artiste
└── README.md            # Cette documentation
```

## Organisation des fonctionnalités

### 1. Fonctions principales (core.py)
- `_show_artist_content()` - Affichage principal du contenu d'artiste
- `_create_artist_tabs()` - Création des onglets Musiques/Sorties/Playlists
- `_search_artist_content_async()` - Recherche asynchrone du contenu
- `_find_artist_channel_id()` - Recherche de l'ID de chaîne YouTube
- `_cancel_artist_search()` - Annulation des recherches en cours

### 2. Gestion des vidéos (songs.py)
- `_search_artist_videos_with_id()` - Recherche des vidéos d'un artiste
- `_display_artist_videos()` - Affichage des vidéos dans l'onglet Musiques

### 3. Gestion des sorties (releases.py)
- `_search_artist_releases_with_id()` - Recherche des albums/singles
- `_display_artist_releases()` - Affichage dans l'onglet Sorties
- `_return_to_releases()` - Retour à la vue des sorties

### 4. Gestion des playlists (playlists.py)
- `_search_artist_playlists_with_id()` - Recherche des playlists
- `_display_artist_playlists()` - Affichage dans l'onglet Playlists
- `_show_playlist_content()` - Affichage du contenu d'une playlist
- `_return_to_playlists()` - Retour à la vue des playlists

## Intégration avec le lecteur principal

### Gestionnaire centralisé (artist_tab_manager.py)

Un gestionnaire centralisé `ArtistTabManager` fait le lien entre le lecteur principal et le module artist_tab :

```python
# Initialisation dans main.py
from artist_tab_manager import init_artist_tab_manager
init_artist_tab_manager(self)

# Utilisation
self.artist_tab_manager.show_artist_content(artist_name, video_data)
```

### Redirection des fonctions

Toutes les fonctions `_artist_*` dans `main.py` sont maintenant de simples redirections vers le gestionnaire :

```python
def _show_artist_content(self, artist_name, video_data):
    return self.artist_tab_manager.show_artist_content(artist_name, video_data)
```

## Variables d'état

Les variables liées aux artistes restent dans la classe principale `MusicPlayer` :

```python
# Variables pour l'affichage artiste
self.artist_mode = False
self.current_artist_name = ""
self.current_artist_channel_url = ""
self.current_artist_channel_id = None
self.artist_notebook = None
self.artist_tab_active_sorties = False
self.artist_tab_active_playlists = False
# ... etc
```

## Avantages de cette organisation

### 1. Indépendance
- Le module artist_tab peut être modifié sans affecter le code principal
- Tous les imports nécessaires sont centralisés dans `__init__.py`
- Structure modulaire claire et logique

### 2. Maintenabilité
- Code organisé par fonctionnalité (vidéos, sorties, playlists)
- Fonctions bien séparées et documentées
- Facilité de débogage et de test

### 3. Extensibilité
- Facile d'ajouter de nouvelles fonctionnalités d'artiste
- Structure prête pour de nouveaux types de contenu
- Interface claire entre le module et le lecteur principal

## Utilisation pour les développeurs

### Modifier les pages d'artiste

Pour modifier quelque chose sur les pages d'artiste, il suffit généralement de travailler dans le dossier `artist_tab/` :

1. **Interface et onglets** → `core.py`
2. **Affichage des vidéos** → `songs.py`
3. **Affichage des sorties** → `releases.py`
4. **Affichage des playlists** → `playlists.py`

### Ajouter une nouvelle fonctionnalité

1. Ajouter la fonction dans le fichier approprié (`core.py`, `songs.py`, etc.)
2. Ajouter la méthode correspondante dans `ArtistTabManager` (`artist_tab_manager.py`)
3. Ajouter la redirection dans `main.py` si nécessaire

### Exemple d'ajout de fonctionnalité

```python
# Dans artist_tab/songs.py
def _search_artist_collaborations(self):
    """Nouvelle fonction pour chercher les collaborations"""
    # ... implémentation

# Dans artist_tab_manager.py
def search_artist_collaborations(self):
    """Recherche les collaborations de l'artiste"""
    return artist_tab.songs._search_artist_collaborations(self.player)

# Dans main.py
def _search_artist_collaborations(self):
    """Recherche les collaborations de l'artiste"""
    return self.artist_tab_manager.search_artist_collaborations()
```

## Migration et compatibilité

Cette réorganisation maintient la compatibilité complète avec l'existant :
- Toutes les fonctions publiques restent accessibles
- Les variables d'état sont préservées
- L'interface utilisateur reste identique
- Aucun changement dans l'utilisation externe

La seule différence est que le code est maintenant mieux organisé et plus maintenable.