# Import centralisé depuis __init__.py
from __init__ import *

class FileTracker:
    """Gestionnaire pour suivre les fichiers dans les playlists et les supprimer automatiquement"""
    
    def __init__(self, music_player):
        self.music_player = music_player
        self.file_to_playlists = {}  # {filepath: [playlist_names]}
        self.playlist_to_files = {}  # {playlist_name: [filepaths]}
        self.file_index_cache = {}   # {filepath: {playlist_name: index}}
        
    def rebuild_index(self):
        """Reconstruit l'index des fichiers dans les playlists"""
        self.file_to_playlists.clear()
        self.playlist_to_files.clear()
        self.file_index_cache.clear()
        
        # Parcourir toutes les playlists
        for playlist_name, files in self.music_player.playlists.items():
            self.playlist_to_files[playlist_name] = files.copy()
            
            for index, filepath in enumerate(files):
                # Normaliser le chemin
                normalized_path = os.path.normpath(filepath)
                
                # Ajouter à l'index file -> playlists
                if normalized_path not in self.file_to_playlists:
                    self.file_to_playlists[normalized_path] = []
                self.file_to_playlists[normalized_path].append(playlist_name)
                
                # Ajouter à l'index des positions
                if normalized_path not in self.file_index_cache:
                    self.file_index_cache[normalized_path] = {}
                self.file_index_cache[normalized_path][playlist_name] = index
    
    def add_file_to_playlist(self, filepath, playlist_name):
        """Ajoute un fichier à l'index quand il est ajouté à une playlist"""
        normalized_path = os.path.normpath(filepath)
        
        # Ajouter à l'index file -> playlists
        if normalized_path not in self.file_to_playlists:
            self.file_to_playlists[normalized_path] = []
        if playlist_name not in self.file_to_playlists[normalized_path]:
            self.file_to_playlists[normalized_path].append(playlist_name)
        
        # Ajouter à l'index playlist -> files
        if playlist_name not in self.playlist_to_files:
            self.playlist_to_files[playlist_name] = []
        if normalized_path not in self.playlist_to_files[playlist_name]:
            self.playlist_to_files[playlist_name].append(normalized_path)
        
        # Mettre à jour l'index des positions
        if normalized_path not in self.file_index_cache:
            self.file_index_cache[normalized_path] = {}
        
        playlist_files = self.music_player.playlists.get(playlist_name, [])
        if normalized_path in playlist_files:
            self.file_index_cache[normalized_path][playlist_name] = playlist_files.index(normalized_path)
    
    def remove_file_from_playlist(self, filepath, playlist_name):
        """Supprime un fichier de l'index quand il est retiré d'une playlist"""
        normalized_path = os.path.normpath(filepath)
        
        # Retirer de l'index file -> playlists
        if normalized_path in self.file_to_playlists:
            if playlist_name in self.file_to_playlists[normalized_path]:
                self.file_to_playlists[normalized_path].remove(playlist_name)
            if not self.file_to_playlists[normalized_path]:
                del self.file_to_playlists[normalized_path]
        
        # Retirer de l'index playlist -> files
        if playlist_name in self.playlist_to_files:
            if normalized_path in self.playlist_to_files[playlist_name]:
                self.playlist_to_files[playlist_name].remove(normalized_path)
        
        # Retirer de l'index des positions
        if normalized_path in self.file_index_cache:
            if playlist_name in self.file_index_cache[normalized_path]:
                del self.file_index_cache[normalized_path][playlist_name]
            if not self.file_index_cache[normalized_path]:
                del self.file_index_cache[normalized_path]
    
    def get_playlists_containing_file(self, filepath):
        """Retourne la liste des playlists contenant ce fichier"""
        normalized_path = os.path.normpath(filepath)
        return self.file_to_playlists.get(normalized_path, [])
    
    def file_exists_on_disk(self, filepath):
        """Vérifie si le fichier existe sur le disque"""
        return os.path.exists(filepath)
    
    def remove_deleted_file_from_all_playlists(self, filepath):
        """Supprime un fichier de toutes les playlists et met à jour l'affichage"""
        normalized_path = os.path.normpath(filepath)
        
        # Obtenir les playlists contenant ce fichier
        affected_playlists = self.get_playlists_containing_file(filepath)
        
        if not affected_playlists:
            return []
        
        print(f"Suppression de {filepath} des playlists: {affected_playlists}")
        
        # Supprimer de chaque playlist
        for playlist_name in affected_playlists:
            if playlist_name in self.music_player.playlists:
                playlist = self.music_player.playlists[playlist_name]
                
                # Supprimer toutes les occurrences du fichier
                while filepath in playlist:
                    playlist.remove(filepath)
                
                # Si c'est la playlist principale, mettre à jour current_index si nécessaire
                if playlist_name == self.music_player.current_playlist_name:
                    if hasattr(self.music_player, 'current_index'):
                        # Vérifier si l'index actuel est affecté
                        if (self.music_player.current_index < len(playlist) and 
                            self.music_player.current_index >= 0):
                            # L'index est toujours valide
                            pass
                        elif self.music_player.current_index >= len(playlist):
                            # L'index dépasse, le ramener à la fin
                            self.music_player.current_index = max(0, len(playlist) - 1)
        
        # Mettre à jour l'index
        self.remove_file_from_all_indexes(filepath)
        
        # Sauvegarder les playlists
        self.music_player.save_playlists()
        
        return affected_playlists
    
    def remove_file_from_all_indexes(self, filepath):
        """Supprime un fichier de tous les index"""
        normalized_path = os.path.normpath(filepath)
        
        # Supprimer de l'index file -> playlists
        if normalized_path in self.file_to_playlists:
            del self.file_to_playlists[normalized_path]
        
        # Supprimer de l'index des positions
        if normalized_path in self.file_index_cache:
            del self.file_index_cache[normalized_path]
        
        # Supprimer de l'index playlist -> files
        for playlist_name in self.playlist_to_files:
            if normalized_path in self.playlist_to_files[playlist_name]:
                self.playlist_to_files[playlist_name].remove(normalized_path)
    
    def check_and_clean_missing_files(self):
        """Vérifie tous les fichiers et supprime ceux qui n'existent plus"""
        missing_files = []
        
        # Vérifier tous les fichiers dans l'index
        for filepath in list(self.file_to_playlists.keys()):
            if not self.file_exists_on_disk(filepath):
                missing_files.append(filepath)
                self.remove_deleted_file_from_all_playlists(filepath)
        
        return missing_files
    
    def get_stats(self):
        """Retourne des statistiques sur l'index"""
        return {
            'total_files': len(self.file_to_playlists),
            'total_playlists': len(self.playlist_to_files),
            'files_per_playlist': {name: len(files) for name, files in self.playlist_to_files.items()}
        }
    
    def init_file_tracker(self):
        """Initialise le gestionnaire de fichiers"""
        self.rebuild_index()



def rebuild_file_index(self):
    """Reconstruit l'index des fichiers"""
    if hasattr(self, 'file_tracker'):
        self.file_tracker.rebuild_index()

def remove_deleted_file_from_playlists(self, filepath):
    """Supprime un fichier supprimé de toutes les playlists"""
    if hasattr(self, 'file_tracker'):
        affected_playlists = self.file_tracker.remove_deleted_file_from_all_playlists(filepath)
        
        # Mettre à jour l'affichage si nécessaire
        if affected_playlists:
            # Recharger l'affichage de la bibliothèque
            if hasattr(self, 'load_downloaded_files'):
                self.safe_after(100, self.load_downloaded_files)
            
            # Recharger l'affichage des playlists
            if hasattr(self, 'load_playlists_display'):
                self.safe_after(100, self.load_playlists_display)
            
            # Mettre à jour la status bar
            self.status_bar.config(text=f"Fichier supprimé de {len(affected_playlists)} playlist(s)")
        
        return affected_playlists
    return []

def check_missing_files(self):
    """Vérifie et nettoie les fichiers manquants"""
    if hasattr(self, 'file_tracker'):
        missing_files = self.file_tracker.check_and_clean_missing_files()
        if missing_files:
            self.status_bar.config(text=f"{len(missing_files)} fichier(s) manquant(s) supprimé(s) des playlists")
        return missing_files
    return []

def add_file_to_tracker(self, filepath, playlist_name):
    """Ajoute un fichier au tracker"""
    if hasattr(self, 'file_tracker'):
        self.file_tracker.add_file_to_playlist(filepath, playlist_name)

def remove_file_from_tracker(self, filepath, playlist_name):
    """Supprime un fichier du tracker"""
    if hasattr(self, 'file_tracker'):
        self.file_tracker.remove_file_from_playlist(filepath, playlist_name)