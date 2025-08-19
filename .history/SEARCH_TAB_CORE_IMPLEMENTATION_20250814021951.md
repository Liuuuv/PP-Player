# Implémentation de search_tab/core.py

## Objectif
Rendre l'onglet search_tab et le fichier search_tab le plus indépendant possible du main, en centralisant la logique d'affichage de la miniature selon l'état de l'artist_tab.

## Fonctionnalités implémentées

### 1. `search_tab/core.py` - Nouvelles fonctions

#### `is_artist_tab_open(player)`
- **Rôle** : Vérifie si l'onglet artiste est actuellement ouvert
- **Logique** : 
  - Vérifie `player.artist_mode`
  - Vérifie l'existence et la visibilité de `player.artist_notebook`
- **Retour** : `True` si l'artist_tab est ouvert, `False` sinon

#### `should_show_large_thumbnail(player)`
- **Rôle** : Détermine si on doit afficher la miniature en gros
- **Logique** :
  - Ne pas afficher si l'artist_tab est ouvert
  - Ne pas afficher s'il y a des résultats de recherche affichés
  - Afficher dans tous les autres cas
- **Retour** : `True` si on doit afficher la miniature, `False` sinon

#### `handle_search_clear(player)`
- **Rôle** : Gère le clear de la recherche en vérifiant l'état de l'artist_tab
- **Logique** :
  - Si l'artist_tab est ouvert → ne pas afficher la miniature
  - Si l'artist_tab est fermé → afficher la miniature en gros
- **Utilisation** : Appelée depuis `_clear_youtube_search()`

#### `handle_artist_tab_close(player)`
- **Rôle** : Gère la fermeture de l'artist_tab en vérifiant s'il faut afficher la miniature
- **Logique** :
  - Si pas de résultats de recherche → afficher la miniature en gros
  - Si des résultats de recherche sont présents → ne pas afficher la miniature
- **Utilisation** : Appelée depuis `_return_to_search()`

### 2. Modifications dans `search_tab/results.py`

#### `_clear_youtube_search()`
- **Avant** : Appelait directement `self._show_current_song_thumbnail()`
- **Après** : Utilise `search_tab.core.handle_search_clear(self)`

#### `_show_current_song_thumbnail()`
- **Avant** : Vérifiait seulement `self.artist_mode`
- **Après** : Utilise `search_tab.core.should_show_large_thumbnail(self)`

#### `_return_to_search()`
- **Avant** : Appelait directement `self._show_current_song_thumbnail()`
- **Après** : Utilise `search_tab.core.handle_artist_tab_close(self)`

## Points d'entrée

### 1. Clear de la recherche
- **Déclencheurs** :
  - Bouton croix dans l'interface (setup.py ligne 745)
  - Touche Échap (inputs.py ligne 65)
  - Appel direct à `_clear_youtube_search()`
- **Comportement** :
  - Si artist_tab ouvert → pas d'affichage de miniature
  - Si artist_tab fermé → affichage de la miniature en gros

### 2. Fermeture de l'artist_tab
- **Déclencheurs** :
  - Bouton retour dans l'artist_tab
  - Touche Échap en mode artiste
  - Appel direct à `_return_to_search()`
- **Comportement** :
  - Si pas de résultats de recherche → affichage de la miniature en gros
  - Si résultats de recherche présents → pas d'affichage de miniature

## Avantages de cette implémentation

### 1. Indépendance
- La logique est centralisée dans `search_tab/core.py`
- Réduction des dépendances avec le fichier main
- Import dynamique pour éviter les dépendances circulaires

### 2. Maintenabilité
- Une seule source de vérité pour la logique d'affichage
- Fonctions réutilisables et testables
- Debug centralisé avec messages explicites

### 3. Flexibilité
- Facile d'ajouter de nouvelles conditions
- Logique modulaire et extensible
- Tests unitaires possibles

## Tests
- Script de test créé : `test_search_tab_core.py`
- Tous les tests passent avec succès
- Couverture complète des cas d'usage

## Utilisation
Les fonctions sont automatiquement utilisées par les points d'entrée existants :
- Clear de recherche → `handle_search_clear()`
- Fermeture artist_tab → `handle_artist_tab_close()`
- Affichage miniature → `should_show_large_thumbnail()`

Aucune modification manuelle nécessaire dans le code existant.