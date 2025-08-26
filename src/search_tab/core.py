import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier search_tab
from search_tab import *

def is_artist_tab_open(player):
    """
    Vérifie si l'onglet artiste est actuellement ouvert
    
    Args:
        player: Instance du MusicPlayer
        
    Returns:
        bool: True si l'artist_tab est ouvert, False sinon
    """
    try:
        # Vérifier si on est en mode artiste
        if hasattr(player, 'artist_mode') and player.artist_mode:
            return True
            
        # Vérifier si le notebook artiste existe et est visible
        if (hasattr(player, 'artist_notebook') and 
            player.artist_notebook and 
            player.artist_notebook.winfo_exists() and
            player.artist_notebook.winfo_viewable()):
            return True
            
        return False
        
    except Exception as e:
        return False

def should_show_large_thumbnail(player):
    """
    Détermine si on doit afficher la miniature en gros
    
    Args:
        player: Instance du MusicPlayer
        
    Returns:
        bool: True si on doit afficher la miniature en gros, False sinon
    """
    try:
        # Ne pas afficher la miniature en gros si l'artist_tab est ouvert
        if is_artist_tab_open(player):
            return False
            
        # Vérifier s'il y a des résultats de recherche affichés
        if (hasattr(player, 'current_search_query') and 
            player.current_search_query and 
            hasattr(player, 'search_results_count') and 
            player.search_results_count > 0):
            return False
            
        # Si aucune condition ne s'oppose, afficher la miniature
        return True
        
    except Exception as e:
        return True  # Par défaut, afficher la miniature

def handle_search_clear(player):
    """
    Gère le clear de la recherche en vérifiant l'état de l'artist_tab
    
    Args:
        player: Instance du MusicPlayer
    """
    try:
        # Si l'artist_tab est ouvert, ne pas afficher la miniature en gros
        if is_artist_tab_open(player):
            return
            
        # Sinon, afficher la miniature en gros
        if hasattr(player, '_show_current_song_thumbnail'):
            player._show_current_song_thumbnail()
        else:
            # Import dynamique pour éviter les dépendances circulaires
            import search_tab.results
            search_tab.results._show_current_song_thumbnail(player)
            
    except Exception as e:
        pass

def handle_artist_tab_close(player):
    """
    Gère la fermeture de l'artist_tab en vérifiant s'il faut afficher la miniature
    
    Args:
        player: Instance du MusicPlayer
    """
    try:
        # Vérifier s'il n'y a pas de résultats de recherche à droite
        has_search_results = (hasattr(player, 'current_search_query') and 
                            player.current_search_query and 
                            hasattr(player, 'search_results_count') and 
                            player.search_results_count > 0)
        
        if not has_search_results:
            if hasattr(player, '_show_current_song_thumbnail'):
                player._show_current_song_thumbnail()
            else:
                # Import dynamique pour éviter les dépendances circulaires
                import search_tab.results
                search_tab.results._show_current_song_thumbnail(player)
        else:
            pass
            
    except Exception as e:
        pass