#!/usr/bin/env python3
"""
Test pour vérifier que l'ajout à la queue fonctionne correctement quand la playlist est vide
"""

import sys
import os

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from drag_drop_handler import DragDropHandler

class MockMusicPlayer:
    def __init__(self):
        self.main_playlist = []
        self.current_index = 0
        self.queue_items = set()
        self.current_downloads = set()
        self.pending_queue_additions = {}
        self.pending_play_after_current = {}
        self.pending_queue_first_additions = {}
        self.main_playlist_from_playlist = False
        
        class MockStatusBar:
            def config(self, text):
                print(f"Status: {text}")
        
        self.status_bar = MockStatusBar()
        
        class MockRoot:
            def update_idletasks(self):
                pass
            def after(self, delay, func):
                func()
        
        self.root = MockRoot()
    
    def _update_downloads_queue_visual(self):
        print("Mise à jour visuelle de la queue")

def test_add_to_queue_empty_playlist():
    """Test d'ajout à la queue quand la playlist est vide"""
    print("=== Test: Ajout à la queue avec playlist vide ===")
    
    # Créer un mock music player avec playlist vide
    music_player = MockMusicPlayer()
    drag_handler = DragDropHandler(music_player)
    
    # Vérifier l'état initial
    print(f"Playlist initiale: {music_player.main_playlist}")
    print(f"Queue initiale: {music_player.queue_items}")
    
    # Ajouter un fichier à la queue
    test_file = "test_song.mp3"
    drag_handler._add_to_queue(test_file)
    
    # Vérifier le résultat
    print(f"Playlist après ajout: {music_player.main_playlist}")
    print(f"Queue après ajout: {music_player.queue_items}")
    
    # Vérifications
    assert len(music_player.main_playlist) == 1, f"La playlist devrait contenir 1 élément, mais contient {len(music_player.main_playlist)}"
    assert music_player.main_playlist[0] == test_file, f"Le fichier devrait être {test_file}, mais est {music_player.main_playlist[0]}"
    assert len(music_player.queue_items) == 0, f"La queue devrait être vide, mais contient {music_player.queue_items}"
    
    print("✅ Test réussi: Le fichier a été ajouté à la playlist sans être marqué comme queue")

def test_add_to_queue_first_empty_playlist():
    """Test d'ajout en premier dans la queue quand la playlist est vide"""
    print("\n=== Test: Ajout en premier dans la queue avec playlist vide ===")
    
    # Créer un mock music player avec playlist vide
    music_player = MockMusicPlayer()
    drag_handler = DragDropHandler(music_player)
    
    # Vérifier l'état initial
    print(f"Playlist initiale: {music_player.main_playlist}")
    print(f"Queue initiale: {music_player.queue_items}")
    
    # Ajouter un fichier en premier dans la queue
    test_file = "test_song_first.mp3"
    drag_handler._add_to_queue_first(test_file)
    
    # Vérifier le résultat
    print(f"Playlist après ajout: {music_player.main_playlist}")
    print(f"Queue après ajout: {music_player.queue_items}")
    
    # Vérifications
    assert len(music_player.main_playlist) == 1, f"La playlist devrait contenir 1 élément, mais contient {len(music_player.main_playlist)}"
    assert music_player.main_playlist[0] == test_file, f"Le fichier devrait être {test_file}, mais est {music_player.main_playlist[0]}"
    assert len(music_player.queue_items) == 0, f"La queue devrait être vide, mais contient {music_player.queue_items}"
    
    print("✅ Test réussi: Le fichier a été ajouté à la playlist sans être marqué comme queue")

def test_add_to_queue_with_existing_song():
    """Test d'ajout à la queue quand il y a déjà une chanson"""
    print("\n=== Test: Ajout à la queue avec chanson existante ===")
    
    # Créer un mock music player avec une chanson
    music_player = MockMusicPlayer()
    music_player.main_playlist = ["existing_song.mp3"]
    music_player.current_index = 0
    drag_handler = DragDropHandler(music_player)
    
    # Vérifier l'état initial
    print(f"Playlist initiale: {music_player.main_playlist}")
    print(f"Queue initiale: {music_player.queue_items}")
    
    # Ajouter un fichier à la queue
    test_file = "test_song_queue.mp3"
    drag_handler._add_to_queue(test_file)
    
    # Vérifier le résultat
    print(f"Playlist après ajout: {music_player.main_playlist}")
    print(f"Queue après ajout: {music_player.queue_items}")
    
    # Vérifications
    assert len(music_player.main_playlist) == 2, f"La playlist devrait contenir 2 éléments, mais contient {len(music_player.main_playlist)}"
    assert test_file in music_player.main_playlist, f"Le fichier {test_file} devrait être dans la playlist"
    assert len(music_player.queue_items) == 1, f"La queue devrait contenir 1 élément, mais contient {len(music_player.queue_items)}"
    
    print("✅ Test réussi: Le fichier a été ajouté à la playlist et marqué comme queue")

if __name__ == "__main__":
    test_add_to_queue_empty_playlist()
    test_add_to_queue_first_empty_playlist()
    test_add_to_queue_with_existing_song()
    print("\n🎉 Tous les tests sont passés avec succès!")