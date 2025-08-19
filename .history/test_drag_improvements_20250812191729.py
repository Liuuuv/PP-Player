#!/usr/bin/env python3
"""
Test pour vérifier les améliorations du drag :
1. Drag gauche ajoute maintenant à la playlist (comme drag droite)
2. Clear playlist affiche la miniature correctement
"""

import sys
import os

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from drag_drop_handler import DragDropHandler

class MockFrame:
    def __init__(self, item_type, file_path=None, video_data=None):
        self.drag_item_type = item_type
        self.drag_file_path = file_path
        self.drag_video_data = video_data
        self.is_dragging = True
        self.drag_start_x = 0
        self.original_bg = '#4a4a4a'

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

class MockEvent:
    def __init__(self, x_root):
        self.x_root = x_root

def test_drag_left_adds_to_playlist():
    """Test que le drag gauche ajoute maintenant à la playlist"""
    print("=== Test: Drag gauche ajoute à la playlist ===")
    
    music_player = MockMusicPlayer()
    drag_handler = DragDropHandler(music_player)
    
    # Créer un mock frame pour un fichier
    frame = MockFrame("file", "test_song.mp3")
    
    # Simuler un drag vers la gauche (dx < -100)
    event = MockEvent(-150)  # x_root = -150, donc dx = -150 - 0 = -150
    
    print(f"État initial - Playlist: {music_player.main_playlist}")
    
    # Simuler le drag release vers la gauche
    drag_handler._on_drag_release(event, frame)
    
    print(f"Après drag gauche - Playlist: {music_player.main_playlist}")
    print(f"✅ Résultat attendu: Le fichier devrait être ajouté à la playlist")
    print()

def test_drag_right_still_works():
    """Test que le drag droite fonctionne toujours"""
    print("=== Test: Drag droite fonctionne toujours ===")
    
    music_player = MockMusicPlayer()
    drag_handler = DragDropHandler(music_player)
    
    # Créer un mock frame pour un fichier
    frame = MockFrame("file", "test_song2.mp3")
    
    # Simuler un drag vers la droite (dx > 100)
    event = MockEvent(150)  # x_root = 150, donc dx = 150 - 0 = 150
    
    print(f"État initial - Playlist: {music_player.main_playlist}")
    
    # Simuler le drag release vers la droite
    drag_handler._on_drag_release(event, frame)
    
    print(f"Après drag droite - Playlist: {music_player.main_playlist}")
    print(f"✅ Résultat attendu: Le fichier devrait être ajouté à la playlist")
    print()

def test_visual_feedback():
    """Test que les couleurs visuelles sont correctes"""
    print("=== Test: Feedback visuel ===")
    
    music_player = MockMusicPlayer()
    drag_handler = DragDropHandler(music_player)
    
    # Mock de _set_frame_colors pour capturer les appels
    colors_set = []
    original_set_colors = drag_handler._set_frame_colors
    def mock_set_colors(frame, color):
        colors_set.append(color)
        print(f"Couleur appliquée: {color}")
    
    drag_handler._set_frame_colors = mock_set_colors
    
    frame = MockFrame("file", "test_song3.mp3")
    
    print("Test drag droite (dx = 150):")
    drag_handler._update_drag_visual(frame, 150, 0)
    
    print("Test drag gauche (dx = -150):")
    drag_handler._update_drag_visual(frame, -150, 0)
    
    print("Test drag neutre (dx = 50):")
    drag_handler._update_drag_visual(frame, 50, 0)
    
    print(f"✅ Résultat attendu: Les deux premiers devraient être verts (#4a6a4a), le dernier gris (#5a5a5a)")
    print()

if __name__ == "__main__":
    test_drag_left_adds_to_playlist()
    test_drag_right_still_works()
    test_visual_feedback()
    print("🎉 Tests terminés ! Vérifiez que les résultats correspondent aux attentes.")