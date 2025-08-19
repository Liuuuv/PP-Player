from __init__ import *

def _clear_search_cache(self):
    """Vide le cache des recherches"""
    try:
        # Vider les caches de recherche en mémoire
        if hasattr(self, 'extended_search_cache'):
            self.extended_search_cache.clear()
        
        if hasattr(self, 'normalized_filenames'):
            self.normalized_filenames.clear()
        
        if hasattr(self, 'all_search_results'):
            self.all_search_results.clear()
        
        # Vider le cache des résultats YouTube si il existe
        search_cache_file = os.path.join("downloads", ".cache", "search_results.json")
        if os.path.exists(search_cache_file):
            os.remove(search_cache_file)
        
        messagebox.showinfo("Cache vidé", "Le cache des recherches a été vidé avec succès.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du vidage du cache des recherches:\n{str(e)}")

def _clear_artist_cache(self):
    """Vide le cache des artistes"""
    try:
        # Vider les caches d'artistes en mémoire
        if hasattr(self, 'artist_cache'):
            self.artist_cache.clear()
        
        if hasattr(self, 'playlist_content_cache'):
            self.playlist_content_cache.clear()
        
        # Vider les fichiers de cache des artistes
        artist_cache_dir = os.path.join("downloads", ".cache", "artists")
        if os.path.exists(artist_cache_dir):
            import shutil
            shutil.rmtree(artist_cache_dir)
            os.makedirs(artist_cache_dir, exist_ok=True)
        
        messagebox.showinfo("Cache vidé", "Le cache des artistes a été vidé avec succès.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du vidage du cache des artistes:\n{str(e)}")

def _clear_thumbnail_cache(self):
    """Vide le cache des miniatures"""
    try:
        # Vider le cache des miniatures en mémoire
        if hasattr(self, 'thumbnail_cache'):
            self.thumbnail_cache.clear()
        
        # Vider le dossier des miniatures
        thumbnails_cache_dir = os.path.join("downloads", ".cache", "thumbnails")
        if os.path.exists(thumbnails_cache_dir):
            import shutil
            shutil.rmtree(thumbnails_cache_dir)
            os.makedirs(thumbnails_cache_dir, exist_ok=True)
        
        # Vider le fichier de métadonnées des miniatures
        metadata_cache_file = os.path.join("downloads", ".cache", "metadata.json")
        if os.path.exists(metadata_cache_file):
            os.remove(metadata_cache_file)
        
        messagebox.showinfo("Cache vidé", "Le cache des miniatures a été vidé avec succès.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du vidage du cache des miniatures:\n{str(e)}")

def _clear_playlist_content_cache(self):
    """Vide le cache des contenus de playlists"""
    try:
        # Vider le cache des contenus de playlists en mémoire
        if hasattr(self, 'playlist_content_cache'):
            self.playlist_content_cache.clear()
        
        # Vider les fichiers de cache des playlists
        playlist_cache_file = os.path.join("downloads", ".cache", "playlists.json")
        if os.path.exists(playlist_cache_file):
            os.remove(playlist_cache_file)
        
        messagebox.showinfo("Cache vidé", "Le cache des playlists a été vidé avec succès.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du vidage du cache des playlists:\n{str(e)}")

def _clear_all_caches(self):
    """Vide tous les caches"""
    try:
        # Demander confirmation
        result = messagebox.askyesno(
            "Confirmation",
            "Êtes-vous sûr de vouloir vider tous les caches ?\n\n"
            "Cela inclut :\n"
            "• Cache des recherches\n"
            "• Cache des artistes\n"
            "• Cache des miniatures\n"
            "• Cache des playlists\n"
            "• Cache des durées (sera recalculé)\n\n"
            "Cette action peut ralentir temporairement l'application.",
            icon='warning'
        )
        
        if not result:
            return
        
        # Vider tous les caches en mémoire
        caches_to_clear = [
            'extended_search_cache',
            'normalized_filenames', 
            'all_search_results',
            'artist_cache',
            'playlist_content_cache',
            'thumbnail_cache',
            'duration_cache'
        ]
        
        for cache_name in caches_to_clear:
            if hasattr(self, cache_name):
                getattr(self, cache_name).clear()
        
        # Vider tout le dossier de cache
        cache_dir = os.path.join("downloads", ".cache")
        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
            
            # Recréer la structure de base
            os.makedirs(cache_dir, exist_ok=True)
            os.makedirs(os.path.join(cache_dir, "thumbnails"), exist_ok=True)
            os.makedirs(os.path.join(cache_dir, "artists"), exist_ok=True)
        
        messagebox.showinfo("Cache vidé", "Tous les caches ont été vidés avec succès.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du vidage des caches:\n{str(e)}")