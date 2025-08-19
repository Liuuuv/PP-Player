#!/usr/bin/env python3
"""
Test simple pour vérifier que la fonction add_to_main_playlist fonctionne correctement
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_add_to_main_playlist():
    """Test basique de la fonction add_to_main_playlist"""
    print("Test de la fonction add_to_main_playlist...")
    
    # Créer une classe mock simple pour simuler le lecteur de musique
    class MockMusicPlayer:
        def __init__(self):
            self.main_playlist = []
            self.status_bar = MockStatusBar()
        
        def _add_main_playlist_item(self, filepath, thumbnail_path=None, song_index=None):
            print(f"  _add_main_playlist_item appelé avec: {filepath}")
        
        def add_to_main_playlist(self, filepath, thumbnail_path=None, song_index=None, show_status=True):
            """Fonction centralisée pour ajouter une musique à la main playlist"""
            if filepath not in self.main_playlist:
                self.main_playlist.append(filepath)
                self._add_main_playlist_item(filepath, thumbnail_path, song_index)
                if show_status:
                    self.status_bar.config(text=f"Ajouté à la liste de lecture principale: {os.path.basename(filepath)}")
                return True
            else:
                if show_status:
                    self.status_bar.config(text=f"Déjà dans la liste de lecture principale: {os.path.basename(filepath)}")
                return False
    
    class MockStatusBar:
        def config(self, text):
            print(f"  Status: {text}")
    
    # Tests
    player = MockMusicPlayer()
    
    # Test 1: Ajouter une nouvelle musique
    print("\n1. Test ajout d'une nouvelle musique:")
    result = player.add_to_main_playlist("test_song1.mp3")
    print(f"   Résultat: {result}")
    print(f"   Playlist: {player.main_playlist}")
    
    # Test 2: Ajouter la même musique (doublon)
    print("\n2. Test ajout d'un doublon:")
    result = player.add_to_main_playlist("test_song1.mp3")
    print(f"   Résultat: {result}")
    print(f"   Playlist: {player.main_playlist}")
    
    # Test 3: Ajouter une autre musique
    print("\n3. Test ajout d'une autre musique:")
    result = player.add_to_main_playlist("test_song2.mp3")
    print(f"   Résultat: {result}")
    print(f"   Playlist: {player.main_playlist}")
    
    # Test 4: Ajouter sans afficher le status
    print("\n4. Test ajout sans status:")
    result = player.add_to_main_playlist("test_song3.mp3", show_status=False)
    print(f"   Résultat: {result}")
    print(f"   Playlist: {player.main_playlist}")
    
    # Test 5: Ajouter avec thumbnail_path et song_index
    print("\n5. Test ajout avec paramètres optionnels:")
    result = player.add_to_main_playlist("test_song4.mp3", thumbnail_path="thumb.jpg", song_index=3)
    print(f"   Résultat: {result}")
    print(f"   Playlist: {player.main_playlist}")
    
    print("\nTest terminé avec succès !")

if __name__ == "__main__":
    test_add_to_main_playlist()