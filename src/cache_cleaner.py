from __init__ import *

def _get_cache_size_str(size_bytes):
    """Convertit une taille en bytes en string lisible"""
    if size_bytes == 0:
        return "0 B"
    elif size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def _get_search_cache_size(self):
    """Calcule la taille du cache des recherches"""
    try:
        total_size = 0
        
        # Taille du cache en mémoire
        if hasattr(self, 'extended_search_cache'):
            import sys
            total_size += sys.getsizeof(self.extended_search_cache)
            for key, value in self.extended_search_cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
        
        if hasattr(self, 'normalized_filenames'):
            import sys
            total_size += sys.getsizeof(self.normalized_filenames)
            for key, value in self.normalized_filenames.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
        
        if hasattr(self, 'all_search_results'):
            import sys
            total_size += sys.getsizeof(self.all_search_results)
        
        # Taille du fichier de cache sur disque
        search_cache_file = os.path.join(self.downloads_folder, ".cache", "search_results.json")
        if os.path.exists(search_cache_file):
            total_size += os.path.getsize(search_cache_file)
        
        return total_size
    except:
        return 0

def _get_artist_cache_size(self):
    """Calcule la taille du cache des artistes"""
    try:
        total_size = 0
        
        # Taille du cache en mémoire
        if hasattr(self, 'artist_cache'):
            import sys
            total_size += sys.getsizeof(self.artist_cache)
            for key, value in self.artist_cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
        
        if hasattr(self, 'playlist_content_cache'):
            import sys
            total_size += sys.getsizeof(self.playlist_content_cache)
            for key, value in self.playlist_content_cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
        
        # Taille du dossier de cache des artistes
        artist_cache_dir = os.path.join(self.downloads_folder, ".cache", "artists")
        if os.path.exists(artist_cache_dir):
            for root, dirs, files in os.walk(artist_cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        
        return total_size
    except:
        return 0

def _get_thumbnail_cache_size(self):
    """Calcule la taille du cache des miniatures"""
    try:
        total_size = 0
        
        # Taille du cache en mémoire
        if hasattr(self, 'thumbnail_cache'):
            import sys
            total_size += sys.getsizeof(self.thumbnail_cache)
            for key, value in self.thumbnail_cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
        
        # Taille du dossier des miniatures
        thumbnails_cache_dir = os.path.join(self.downloads_folder, ".cache", "thumbnails")
        if os.path.exists(thumbnails_cache_dir):
            for root, dirs, files in os.walk(thumbnails_cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        
        # Taille du fichier de métadonnées
        metadata_cache_file = os.path.join(self.downloads_folder, ".cache", "metadata.json")
        if os.path.exists(metadata_cache_file):
            total_size += os.path.getsize(metadata_cache_file)
        
        return total_size
    except:
        return 0

def _get_playlist_content_cache_size(self):
    """Calcule la taille du cache des contenus de playlists"""
    try:
        total_size = 0
        
        # Taille du cache en mémoire
        if hasattr(self, 'playlist_content_cache'):
            import sys
            total_size += sys.getsizeof(self.playlist_content_cache)
            for key, value in self.playlist_content_cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
        
        # Taille du fichier de cache des playlists
        playlist_cache_file = os.path.join(self.downloads_folder, ".cache", "playlists.json")
        if os.path.exists(playlist_cache_file):
            total_size += os.path.getsize(playlist_cache_file)
        
        return total_size
    except:
        return 0

def _get_duration_cache_size(self):
    """Calcule la taille du cache des durées"""
    try:
        total_size = 0
        
        # Taille du cache en mémoire
        if hasattr(self, 'duration_cache'):
            import sys
            total_size += sys.getsizeof(self.duration_cache)
            for key, value in self.duration_cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(value)
        
        # Taille du fichier de cache des durées
        durations_cache_file = os.path.join(self.downloads_folder, ".cache", "durations.json")
        if os.path.exists(durations_cache_file):
            total_size += os.path.getsize(durations_cache_file)
        
        return total_size
    except:
        return 0

def _get_total_cache_size(self):
    """Calcule la taille totale de tous les caches"""
    try:
        total_size = 0
        total_size += _get_search_cache_size(self)
        total_size += _get_artist_cache_size(self)
        total_size += _get_thumbnail_cache_size(self)
        total_size += _get_playlist_content_cache_size(self)
        total_size += _get_duration_cache_size(self)
        return total_size
    except:
        return 0

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
        search_cache_file = os.path.join(self.downloads_folder, ".cache", "search_results.json")
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
        artist_cache_dir = os.path.join(self.downloads_folder, ".cache", "artists")
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
        thumbnails_cache_dir = os.path.join(self.downloads_folder, ".cache", "thumbnails")
        if os.path.exists(thumbnails_cache_dir):
            import shutil
            shutil.rmtree(thumbnails_cache_dir)
            os.makedirs(thumbnails_cache_dir, exist_ok=True)
        
        # Vider le fichier de métadonnées des miniatures
        metadata_cache_file = os.path.join(self.downloads_folder, ".cache", "metadata.json")
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
        playlist_cache_file = os.path.join(self.downloads_folder, ".cache", "playlists.json")
        if os.path.exists(playlist_cache_file):
            os.remove(playlist_cache_file)
        
        messagebox.showinfo("Cache vidé", "Le cache des playlists a été vidé avec succès.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du vidage du cache des playlists:\n{str(e)}")

def _clear_duration_cache(self):
    """Vide le cache des durées"""
    try:
        # Vider le cache des durées en mémoire
        if hasattr(self, 'duration_cache'):
            self.duration_cache.clear()
        
        # Vider le fichier de cache des durées
        durations_cache_file = os.path.join(self.downloads_folder, ".cache", "durations.json")
        if os.path.exists(durations_cache_file):
            os.remove(durations_cache_file)
        
        messagebox.showinfo("Cache vidé", "Le cache des durées a été vidé avec succès.\nLes durées seront recalculées au prochain affichage.")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du vidage du cache des durées:\n{str(e)}")

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
            "• Cache des durées\n\n"
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
        cache_dir = os.path.join(self.downloads_folder, ".cache")
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