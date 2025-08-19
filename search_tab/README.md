# Module search_tab/results.py

## Vue d'ensemble

Ce module contient toutes les fonctions liées à la recherche et à l'affichage des résultats YouTube dans l'onglet "Recherche". Il a été réorganisé pour être le plus indépendant possible du fichier main.py.

## Architecture

### Fonctions principales

Le module contient toutes les fonctions nécessaires pour :

1. **Recherche YouTube** : `search_youtube()`, `_perform_initial_search()`, `_fetch_more_results()`
2. **Gestion des résultats** : `_add_search_result()`, `_display_batch_results()`, `_clear_results()`
3. **Interface utilisateur** : `_show_search_results()`, `_update_search_results_ui()`, `_update_results_counter()`
4. **Gestion des événements** : `_on_search_entry_change()`, `_on_result_click()`, `_on_filter_change()`
5. **Gestion du scroll** : `_should_load_more_results()`, `_load_more_search_results()`, `_check_scroll_position()`
6. **Gestion des miniatures** : `_show_current_song_thumbnail()`, `_load_large_thumbnail()`, `_recreate_thumbnail_frame()`

### Classe SearchManager

Une classe `SearchManager` a été ajoutée pour encapsuler toute la logique de recherche de manière plus modulaire :

```python
# Création d'un gestionnaire de recherche
search_manager = search_tab.results.create_search_manager(self)

# Utilisation
search_manager.search_youtube()
search_manager.clear_results()
search_manager.load_more_results()
```

## Utilisation

### Depuis main.py

Toutes les fonctions dans main.py délèguent maintenant vers ce module :

```python
def search_youtube(self):
    return search_tab.results.search_youtube(self)

def _clear_results(self):
    return search_tab.results._clear_results(self)
```

### Utilisation directe du module

```python
import search_tab.results as search_results

# Appel direct des fonctions
search_results.search_youtube(app_instance)
search_results._clear_results(app_instance)

# Ou utilisation du gestionnaire
search_manager = search_results.create_search_manager(app_instance)
search_manager.search_youtube()
```

## Dépendances

Le module est conçu pour être indépendant mais utilise encore quelques dépendances externes :

### Modules importés
- `search_tab` (via `from search_tab import *`) : Contient tous les imports nécessaires
- `tooltip` : Pour les info-bulles

### Fonctions externes appelées
- `self._show_artist_content()` : Délègue vers `artist_tab_manager`
- `self.download_selected_youtube()` : Délègue vers `services.downloading`
- `self._show_youtube_playlist_menu()` : Délègue vers `ui_menus`
- `self._show_pending_playlist_menu()` : Délègue vers `tools`
- `self._reset_frame_appearance()` : Délègue vers `tools`

## Fonctions déplacées

Les fonctions suivantes ont été déplacées depuis d'autres modules vers `search_tab/results.py` :

### Depuis main.py
- `_add_search_result()`
- `_recreate_thumbnail_frame()`
- `_on_scrollbar_release()`
- `_check_scroll_position()`

### Depuis tools.py
- `_should_load_more_results()`
- `_update_results_counter()`
- `_update_stats_bar()`

## Configuration requise

Le module nécessite que l'instance de l'application ait les attributs suivants :

### Attributs de recherche
- `current_search_query` : Requête de recherche actuelle
- `search_cancelled` : Flag d'annulation de recherche
- `is_searching` : Flag indiquant si une recherche est en cours
- `is_loading_more` : Flag indiquant si plus de résultats sont en cours de chargement
- `search_results_count` : Nombre de résultats affichés
- `all_search_results` : Liste de tous les résultats
- `max_search_results` : Limite maximale de résultats
- `current_search_batch` : Lot de recherche actuel
- `max_search_batchs` : Nombre maximum de lots

### Widgets UI
- `youtube_canvas` : Canvas pour l'affichage des résultats
- `results_container` : Container des résultats
- `youtube_results_frame` : Frame principale des résultats
- `thumbnail_frame` : Frame pour les miniatures
- `status_bar` : Barre de statut
- `stats_bar` : Barre de statistiques
- `results_counter_label` : Label du compteur de résultats

## Tests

Un script de test `test_search_reorganization.py` est disponible pour vérifier que toutes les fonctions sont correctement organisées :

```bash
python test_search_reorganization.py
```

## Avantages de cette réorganisation

1. **Modularité** : Toute la logique de recherche est centralisée
2. **Indépendance** : Le module est moins dépendant du main.py
3. **Maintenabilité** : Plus facile de maintenir et déboguer
4. **Réutilisabilité** : Le SearchManager peut être utilisé dans d'autres contextes
5. **Testabilité** : Plus facile de tester les fonctions de recherche isolément