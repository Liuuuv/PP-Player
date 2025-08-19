"""
Gestion des playlists
"""
import json
import os
from config.constants import PLAYLISTS_FILE, DOWNLOADS_DIR


class PlaylistManager:
    """Gestionnaire des playlists"""
    
    def __init__(self):
        self.playlists = {}
        self.current_playlist_name = "Main Playlist"
        self.playlists[self.current_playlist_name] = []
        self.current_viewing_playlist = None
        self.main_playlist_from_playlist = False
        
        # Variables pour la sélection multiple
        self.selected_items = set()
        self.selection_frames = {}
        self.shift_selection_active = False
        
    @property
    def main_playlist(self):
        """Retourne la playlist principale"""
        return self.playlists[self.current_playlist_name]
    
    @main_playlist.setter
    def main_playlist(self, value):
        """Définit la playlist principale"""
        self.playlists[self.current_playlist_name] = value
    
    def create_playlist(self, name):
        """Crée une nouvelle playlist"""
        if name not in self.playlists:
            self.playlists[name] = []
            return True
        return False
    
    def delete_playlist(self, name):
        """Supprime une playlist"""
        if name in self.playlists and name != "Main Playlist":
            del self.playlists[name]
            return True
        return False
    
    def add_to_playlist(self, playlist_name, filepath):
        """Ajoute un fichier à une playlist"""
        if playlist_name in self.playlists:
            if filepath not in self.playlists[playlist_name]:
                self.playlists[playlist_name].append(filepath)
                return True
        return False
    
    def remove_from_playlist(self, playlist_name, filepath):
        """Supprime un fichier d'une playlist"""
        if playlist_name in self.playlists:
            if filepath in self.playlists[playlist_name]:
                self.playlists[playlist_name].remove(filepath)
                return True
        return False
    
    def get_playlist(self, name):
        """Récupère une playlist par son nom"""
        return self.playlists.get(name, [])
    
    def get_playlist_names(self):
        """Retourne la liste des noms de playlists"""
        return list(self.playlists.keys())
    
    def save_playlists(self):
        """Sauvegarde les playlists dans un fichier JSON"""
        try:
            # Créer le dossier downloads s'il n'existe pas
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            
            # Sauvegarder toutes les playlists sauf la main playlist
            playlists_to_save = {
                name: songs for name, songs in self.playlists.items() 
                if name != "Main Playlist"
            }
            
            with open(PLAYLISTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(playlists_to_save, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erreur sauvegarde playlists: {e}")
    
    def load_playlists(self):
        """Charge les playlists depuis le fichier JSON"""
        try:
            if os.path.exists(PLAYLISTS_FILE):
                with open(PLAYLISTS_FILE, 'r', encoding='utf-8') as f:
                    loaded_playlists = json.load(f)
                
                # Ajouter les playlists chargées (en gardant la main playlist)
                for name, songs in loaded_playlists.items():
                    # Vérifier que les fichiers existent encore
                    existing_songs = [song for song in songs if os.path.exists(song)]
                    if existing_songs:  # Ne garder que les playlists non vides
                        self.playlists[name] = existing_songs
                        
        except Exception as e:
            print(f"Erreur chargement playlists: {e}")
    
    def clear_selection(self):
        """Vide la sélection actuelle"""
        self.selected_items.clear()
        self.selection_frames.clear()
        self.shift_selection_active = False
    
    def add_to_selection(self, filepath, frame=None):
        """Ajoute un élément à la sélection"""
        self.selected_items.add(filepath)
        if frame:
            self.selection_frames[filepath] = frame
    
    def remove_from_selection(self, filepath):
        """Supprime un élément de la sélection"""
        self.selected_items.discard(filepath)
        self.selection_frames.pop(filepath, None)
    
    def is_selected(self, filepath):
        """Vérifie si un élément est sélectionné"""
        return filepath in self.selected_items
    
    def get_selected_count(self):
        """Retourne le nombre d'éléments sélectionnés"""
        return len(self.selected_items)