#!/usr/bin/env python3
"""
Test pour vérifier que l'ajout à la queue via drag & drop met à jour l'affichage de la playlist
"""

import tkinter as tk
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from drag_drop_handler import DragDropHandler

class MockMusicPlayer:
    """Mock du MusicPlayer pour tester le drag & drop"""
    
    def __init__(self):
        self.main_playlist = ["song1.mp3", "song2.mp3", "song3.mp3"]
        self.current_index = 1  # Chanson en cours : song2.mp3
        self.queue_items = set()
        self.status_bar = MockStatusBar()
        self.main_playlist_from_playlist = False
        self.refresh_called = False
        self.update_visual_called = False
        
    def _refresh_playlist_display(self):
        """Mock de la fonction de rafraîchissement"""
        self.refresh_called = True
        print("✅ _refresh_playlist_display() appelée")
        
    def _update_downloads_queue_visual(self):
        """Mock de la fonction de mise à jour visuelle"""
        self.update_visual_called = True
        print("✅ _update_downloads_queue_visual() appelée")

class MockStatusBar:
    """Mock de la barre de statut"""
    
    def __init__(self):
        self.text = ""
        
    def config(self, text=""):
        self.text = text
        print(f"Status: {text}")

def test_drag_queue_refresh():
    """Test que l'ajout à la queue via drag & drop met à jour l'affichage"""
    print("🧪 Test: Ajout à la queue via drag & drop")
    
    # Créer le mock music player
    music_player = MockMusicPlayer()
    
    # Créer le drag drop handler
    drag_handler = DragDropHandler(music_player)
    
    # État initial
    print(f"Playlist initiale: {music_player.main_playlist}")
    print(f"Chanson en cours (index {music_player.current_index}): {music_player.main_playlist[music_player.current_index]}")
    print(f"Queue items: {music_player.queue_items}")
    
    # Ajouter un fichier à la queue
    test_file = "new_song.mp3"
    print(f"\n➕ Ajout de '{test_file}' à la queue...")
    
    # Reset des flags
    music_player.refresh_called = False
    music_player.update_visual_called = False
    
    # Appeler la fonction d'ajout à la queue
    drag_handler._add_to_queue(test_file)
    
    # Vérifier les résultats
    print(f"\nPlaylist après ajout: {music_player.main_playlist}")
    print(f"Queue items: {music_player.queue_items}")
    
    # Vérifier que les fonctions de mise à jour ont été appelées
    if music_player.refresh_called:
        print("✅ _refresh_playlist_display() a été appelée")
    else:
        print("❌ _refresh_playlist_display() N'A PAS été appelée")
        
    if music_player.update_visual_called:
        print("✅ _update_downloads_queue_visual() a été appelée")
    else:
        print("❌ _update_downloads_queue_visual() N'A PAS été appelée")
    
    # Vérifier que le fichier a été ajouté à la bonne position
    expected_position = music_player.current_index + 1  # Juste après la chanson en cours
    if len(music_player.main_playlist) > expected_position and music_player.main_playlist[expected_position] == test_file:
        print(f"✅ Le fichier a été ajouté à la bonne position ({expected_position})")
    else:
        print(f"❌ Le fichier n'est pas à la position attendue ({expected_position})")
    
    # Vérifier que l'index est dans queue_items
    if expected_position in music_player.queue_items:
        print(f"✅ L'index {expected_position} est marqué comme faisant partie de la queue")
    else:
        print(f"❌ L'index {expected_position} n'est PAS marqué comme faisant partie de la queue")
    
    return music_player.refresh_called and music_player.update_visual_called

def test_drag_queue_first_refresh():
    """Test que l'ajout en premier dans la queue via drag & drop met à jour l'affichage"""
    print("\n🧪 Test: Ajout en premier dans la queue via drag & drop")
    
    # Créer le mock music player
    music_player = MockMusicPlayer()
    
    # Créer le drag drop handler
    drag_handler = DragDropHandler(music_player)
    
    # État initial
    print(f"Playlist initiale: {music_player.main_playlist}")
    print(f"Chanson en cours (index {music_player.current_index}): {music_player.main_playlist[music_player.current_index]}")
    
    # Ajouter un fichier en premier dans la queue
    test_file = "priority_song.mp3"
    print(f"\n➕ Ajout de '{test_file}' en premier dans la queue...")
    
    # Reset des flags
    music_player.refresh_called = False
    music_player.update_visual_called = False
    
    # Appeler la fonction d'ajout en premier dans la queue
    drag_handler._add_to_queue_first(test_file)
    
    # Vérifier les résultats
    print(f"\nPlaylist après ajout: {music_player.main_playlist}")
    print(f"Queue items: {music_player.queue_items}")
    
    # Vérifier que les fonctions de mise à jour ont été appelées
    if music_player.refresh_called:
        print("✅ _refresh_playlist_display() a été appelée")
    else:
        print("❌ _refresh_playlist_display() N'A PAS été appelée")
        
    if music_player.update_visual_called:
        print("✅ _update_downloads_queue_visual() a été appelée")
    else:
        print("❌ _update_downloads_queue_visual() N'A PAS été appelée")
    
    return music_player.refresh_called and music_player.update_visual_called

if __name__ == "__main__":
    print("🔧 Test de la correction du drag & drop vers la queue\n")
    
    # Exécuter les tests
    test1_passed = test_drag_queue_refresh()
    test2_passed = test_drag_queue_first_refresh()
    
    # Résumé
    print(f"\n📊 Résultats des tests:")
    print(f"Test ajout à la queue: {'✅ PASSÉ' if test1_passed else '❌ ÉCHOUÉ'}")
    print(f"Test ajout en premier: {'✅ PASSÉ' if test2_passed else '❌ ÉCHOUÉ'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 Tous les tests sont passés ! Le problème d'affichage devrait être corrigé.")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez les corrections.")