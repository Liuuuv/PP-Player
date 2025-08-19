#!/usr/bin/env python3
"""
Test pour vérifier que le drag gauche ajoute maintenant correctement à la liste de lecture
avec affichage visuel et couleur jaune-orange
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
    
    def config(self, **kwargs):
        if 'bg' in kwargs:
            print(f"Frame couleur changée vers: {kwargs['bg']}")

class MockMusicPlayer:
    def __init__(self):
        self.main_playlist = []
        self.current_index = 0
        self.queue_items = set()
        self.current_downloads = set()
        self.pending_queue_additions = {}
        self.pending_play_after_current = {}
        self.pending_queue_first_additions = {}
        self.pending_playlist_additions = {}
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
    
    def add_to_main_playlist(self, filepath, show_status=True):
        """Mock de la fonction add_to_main_playlist"""
        if filepath not in self.main_playlist:
            self.main_playlist.append(filepath)
            print(f"  → Fichier ajouté à la playlist avec affichage visuel: {filepath}")
            return True
        else:
            print(f"  → Fichier déjà présent: {filepath}")
            return False
    
    def _update_downloads_queue_visual(self):
        print("Mise à jour visuelle de la queue")

class MockEvent:
    def __init__(self, x_root):
        self.x_root = x_root

def test_drag_left_adds_to_main_playlist():
    """Test que le drag gauche ajoute à la liste de lecture avec affichage visuel"""
    print("=== Test: Drag gauche ajoute à la liste de lecture ===")
    
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
    print(f"✅ Résultat attendu: Le fichier devrait être ajouté à la playlist avec affichage visuel")
    print()

def test_visual_feedback_colors():
    """Test que les couleurs visuelles sont correctes"""
    print("=== Test: Couleurs du feedback visuel ===")
    
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
    
    expected_colors = ['#4a6a4a', '#6a6a4a', '#5a5a5a']
    print(f"Couleurs attendues: {expected_colors}")
    print(f"Couleurs obtenues: {colors_set}")
    print(f"✅ Drag droite: vert (#4a6a4a), Drag gauche: jaune-orange (#6a6a4a), Neutre: gris (#5a5a5a)")
    print()

def test_direct_function_call():
    """Test direct de la nouvelle fonction _add_file_to_main_playlist"""
    print("=== Test: Fonction _add_file_to_main_playlist ===")
    
    music_player = MockMusicPlayer()
    drag_handler = DragDropHandler(music_player)
    
    print(f"État initial - Playlist: {music_player.main_playlist}")
    
    # Appeler directement la nouvelle fonction
    drag_handler._add_file_to_main_playlist("direct_test.mp3")
    
    print(f"Après appel direct - Playlist: {music_player.main_playlist}")
    print(f"✅ Résultat attendu: Le fichier devrait être ajouté avec affichage visuel")
    print()

if __name__ == "__main__":
    test_drag_left_adds_to_main_playlist()
    test_visual_feedback_colors()
    test_direct_function_call()
    print("🎉 Tests terminés ! Vérifiez que les résultats correspondent aux attentes.")