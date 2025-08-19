#!/usr/bin/env python3
"""
Fonction pour enlever la sélection de la musique en cours (couleur bleue)
lorsqu'on vide la liste de lecture ou qu'on supprime la musique de la liste de lecture ou du PC
"""

import tkinter as tk

def clear_current_song_selection(self):
    """
    Enlève la sélection visuelle de la musique en cours (couleur bleue) dans la playlist principale.
    
    Cette fonction doit être appelée quand :
    - On vide complètement la liste de lecture
    - On supprime la musique actuellement en cours de lecture
    - On supprime une musique du PC et qu'elle était en cours de lecture
    
    La fonction parcourt tous les éléments de la playlist et remet leur couleur normale.
    """
    try:
        # Parcourir tous les éléments de la playlist principale
        if hasattr(self, 'playlist_container'):
            try:
                # Vérifier que le container existe encore
                if self.playlist_container.winfo_exists():
                    for child in self.playlist_container.winfo_children():
                        try:
                            # Vérifier que le child existe encore
                            if child.winfo_exists() and hasattr(child, 'selected'):
                                child.selected = False
                                # Remettre la couleur normale (gris foncé)
                                if hasattr(self, '_set_item_colors'):
                                    self._set_item_colors(child, '#4a4a4a')  # Couleur normale
                                else:
                                    # Fallback si _set_item_colors n'existe pas
                                    try:
                                        child.config(bg='#4a4a4a')
                                    except:
                                        pass
                        except tk.TclError:
                            # Widget détruit, ignorer
                            continue
            except tk.TclError:
                # Container détruit, ignorer
                pass
        
        # Aussi nettoyer la sélection dans les autres containers si ils existent
        # (par exemple dans l'onglet bibliothèque)
        containers_to_check = [
            'downloads_container',  # Container des téléchargements
            'playlist_content_container',  # Container du contenu des playlists
        ]
        
        for container_name in containers_to_check:
            if hasattr(self, container_name):
                container = getattr(self, container_name)
                try:
                    # Vérifier que le container existe encore
                    if container.winfo_exists():
                        for child in container.winfo_children():
                            try:
                                # Vérifier que le child existe encore
                                if child.winfo_exists() and hasattr(child, 'selected'):
                                    child.selected = False
                                    # Remettre la couleur normale
                                    if hasattr(self, '_set_item_colors'):
                                        self._set_item_colors(child, '#4a4a4a')
                                    else:
                                        try:
                                            child.config(bg='#4a4a4a')
                                        except:
                                            pass
                            except tk.TclError:
                                # Widget détruit, ignorer
                                continue
                except tk.TclError:
                    # Container détruit, ignorer
                    continue
                                
    except Exception as e:
        print(f"Erreur lors du nettoyage de la sélection: {e}")

def clear_current_song_selection_in_downloads(self):
    """
    Enlève spécifiquement la sélection dans l'onglet téléchargements.
    
    À utiliser quand on supprime un fichier du PC et qu'il était affiché
    comme en cours de lecture dans l'onglet téléchargements.
    """
    try:
        if hasattr(self, 'downloads_container'):
            for child in self.downloads_container.winfo_children():
                if hasattr(child, 'selected'):
                    child.selected = False
                    if hasattr(self, '_set_item_colors'):
                        self._set_item_colors(child, '#4a4a4a')
                    else:
                        try:
                            child.config(bg='#4a4a4a')
                        except:
                            pass
    except Exception as e:
        print(f"Erreur lors du nettoyage de la sélection dans les téléchargements: {e}")

def clear_current_song_selection_in_playlists(self):
    """
    Enlève spécifiquement la sélection dans l'affichage des playlists.
    
    À utiliser quand on supprime un fichier d'une playlist et qu'il était affiché
    comme en cours de lecture.
    """
    try:
        if hasattr(self, 'playlist_content_container'):
            for child in self.playlist_content_container.winfo_children():
                if hasattr(child, 'selected'):
                    child.selected = False
                    if hasattr(self, '_set_item_colors'):
                        self._set_item_colors(child, '#4a4a4a')
                    else:
                        try:
                            child.config(bg='#4a4a4a')
                        except:
                            pass
    except Exception as e:
        print(f"Erreur lors du nettoyage de la sélection dans les playlists: {e}")

# Fonction principale recommandée à utiliser
def clear_all_current_song_selections(self):
    """
    Fonction principale qui nettoie la sélection dans tous les containers.
    
    Cette fonction combine toutes les fonctions de nettoyage et doit être
    appelée dans les cas suivants :
    
    1. Dans _clear_main_playlist() après avoir vidé la playlist
    2. Dans _remove_main_playlist_item() quand on supprime la chanson en cours
    3. Dans _delete_from_downloads() quand on supprime du PC la chanson en cours
    4. Dans toute autre fonction qui pourrait affecter la chanson en cours
    
    Usage recommandé :
    ```python
    # Après avoir vidé la playlist ou supprimé la chanson en cours
    self.clear_all_current_song_selections()
    ```
    """
    clear_current_song_selection(self)
    clear_current_song_selection_in_downloads(self)
    clear_current_song_selection_in_playlists(self)

# Instructions d'intégration :
"""
Pour intégrer ces fonctions dans le code existant, ajoutez les appels suivants :

1. Dans search_tab/main_playlist.py, fonction _clear_main_playlist() :
   Ajouter après la ligne qui vide les widgets :
   ```python
   # Vider l'affichage de la playlist
   for widget in self.playlist_container.winfo_children():
       widget.destroy()
   
   # AJOUTER ICI :
   self.clear_all_current_song_selections()
   ```

2. Dans search_tab/main_playlist.py, fonction _remove_main_playlist_item() :
   Ajouter après avoir supprimé l'élément si c'était la chanson en cours :
   ```python
   elif index == self.current_index:
       pygame.mixer.music.stop()
       self.current_index = min(index, len(self.main_playlist) - 1)
       if len(self.main_playlist) > 0:
           self.play_track()
       else:
           pygame.mixer.music.unload()
           # AJOUTER ICI :
           self.clear_all_current_song_selections()
           
           # Afficher la miniature de la chanson en cours
           self._show_current_song_thumbnail()
   ```

3. Dans toute fonction _delete_from_downloads() qui supprime un fichier du PC :
   Ajouter après la suppression si c'était la chanson en cours :
   ```python
   # Si c'était la chanson en cours, nettoyer la sélection
   if filepath == self.main_playlist[self.current_index]:
       self.clear_all_current_song_selections()
   ```

4. Pour ajouter ces fonctions au MusicPlayer, ajoutez dans main.py :
   ```python
   from clear_current_selection import (
       clear_all_current_song_selections,
       clear_current_song_selection,
       clear_current_song_selection_in_downloads,
       clear_current_song_selection_in_playlists
   )
   
   # Dans la classe MusicPlayer, ajouter les méthodes :
   def clear_all_current_song_selections(self):
       return clear_all_current_song_selections(self)
   
   def clear_current_song_selection(self):
       return clear_current_song_selection(self)
   
   def clear_current_song_selection_in_downloads(self):
       return clear_current_song_selection_in_downloads(self)
   
   def clear_current_song_selection_in_playlists(self):
       return clear_current_song_selection_in_playlists(self)
   ```
"""