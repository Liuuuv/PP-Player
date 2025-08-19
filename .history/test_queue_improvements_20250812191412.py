#!/usr/bin/env python3
"""
Test pour vérifier les améliorations de la queue :
1. Ajout à la queue avec playlist vide
2. Drag gauche pour ajouter en premier dans la queue avec playlist vide
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

def test_scenarios():
    """Test des différents scénarios d'ajout à la queue"""
    
    print("=== Test 1: Ajout à la queue avec playlist vide ===")
    music_player = MockMusicPlayer()
    drag_handler = DragDropHandler(music_player)
    
    print(f"État initial - Playlist: {music_player.main_playlist}, Queue: {music_player.queue_items}")
    
    # Ajouter un fichier à la queue
    drag_handler._add_to_queue("song1.mp3")
    
    print(f"Après ajout - Playlist: {music_player.main_playlist}, Queue: {music_player.queue_items}")
    print(f"✅ Résultat attendu: Playlist=[song1.mp3], Queue=set() (vide)")
    print()
    
    print("=== Test 2: Ajout en premier dans la queue avec playlist vide ===")
    music_player2 = MockMusicPlayer()
    drag_handler2 = DragDropHandler(music_player2)
    
    print(f"État initial - Playlist: {music_player2.main_playlist}, Queue: {music_player2.queue_items}")
    
    # Ajouter un fichier en premier dans la queue
    drag_handler2._add_to_queue_first("song2.mp3")
    
    print(f"Après ajout - Playlist: {music_player2.main_playlist}, Queue: {music_player2.queue_items}")
    print(f"✅ Résultat attendu: Playlist=[song2.mp3], Queue=set() (vide)")
    print()
    
    print("=== Test 3: Ajout à la queue avec chanson existante ===")
    music_player3 = MockMusicPlayer()
    music_player3.main_playlist = ["existing_song.mp3"]
    music_player3.current_index = 0
    drag_handler3 = DragDropHandler(music_player3)
    
    print(f"État initial - Playlist: {music_player3.main_playlist}, Queue: {music_player3.queue_items}")
    
    # Ajouter un fichier à la queue
    drag_handler3._add_to_queue("song3.mp3")
    
    print(f"Après ajout - Playlist: {music_player3.main_playlist}, Queue: {music_player3.queue_items}")
    print(f"✅ Résultat attendu: Playlist=[existing_song.mp3, song3.mp3], Queue contient l'index de song3.mp3")
    print()
    
    print("=== Test 4: Ajout en premier dans la queue avec chanson existante ===")
    music_player4 = MockMusicPlayer()
    music_player4.main_playlist = ["existing_song.mp3"]
    music_player4.current_index = 0
    drag_handler4 = DragDropHandler(music_player4)
    
    print(f"État initial - Playlist: {music_player4.main_playlist}, Queue: {music_player4.queue_items}")
    
    # Ajouter un fichier en premier dans la queue
    drag_handler4._add_to_queue_first("song4.mp3")
    
    print(f"Après ajout - Playlist: {music_player4.main_playlist}, Queue: {music_player4.queue_items}")
    print(f"✅ Résultat attendu: Playlist=[existing_song.mp3, song4.mp3], Queue contient l'index de song4.mp3")
    print()

if __name__ == "__main__":
    test_scenarios()
    print("🎉 Tests terminés ! Vérifiez que les résultats correspondent aux attentes.")