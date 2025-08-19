#!/usr/bin/env python3
"""
Test pour vérifier que le nettoyage de la sélection fonctionne correctement
"""

import tkinter as tk
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clear_current_selection import (
    clear_all_current_song_selections,
    clear_current_song_selection,
    clear_current_song_selection_in_downloads,
    clear_current_song_selection_in_playlists
)

class MockWidget:
    """Mock d'un widget tkinter"""
    
    def __init__(self, selected=False, bg_color='#4a4a4a'):
        self.selected = selected
        self.bg_color = bg_color
        self.config_called = False
        self.config_color = None
        
    def config(self, bg=None):
        if bg:
            self.config_called = True
            self.config_color = bg
            self.bg_color = bg
    
    def winfo_children(self):
        return []

class MockContainer:
    """Mock d'un container tkinter"""
    
    def __init__(self, children=None):
        self.children = children or []
        
    def winfo_children(self):
        return self.children

class MockMusicPlayer:
    """Mock du MusicPlayer pour tester le nettoyage de sélection"""
    
    def __init__(self):
        # Créer des widgets mock avec sélection
        self.selected_widget1 = MockWidget(selected=True, bg_color='#5a9fd8')
        self.selected_widget2 = MockWidget(selected=True, bg_color='#5a9fd8')
        self.normal_widget = MockWidget(selected=False, bg_color='#4a4a4a')
        
        # Créer les containers
        self.playlist_container = MockContainer([
            self.selected_widget1,
            self.normal_widget
        ])
        
        self.downloads_container = MockContainer([
            self.selected_widget2
        ])
        
        self.playlist_content_container = MockContainer([])
        
        # Mock de _set_item_colors
        self.set_item_colors_calls = []
        
    def _set_item_colors(self, widget, color):
        """Mock de la fonction _set_item_colors"""
        self.set_item_colors_calls.append((widget, color))
        widget.config(bg=color)

def test_clear_current_song_selection():
    """Test du nettoyage de sélection dans la playlist principale"""
    print("🧪 Test: Nettoyage sélection playlist principale")
    
    music_player = MockMusicPlayer()
    
    # État initial
    assert music_player.selected_widget1.selected == True
    assert music_player.selected_widget1.bg_color == '#5a9fd8'
    assert music_player.normal_widget.selected == False
    
    # Appeler la fonction de nettoyage
    clear_current_song_selection(music_player)
    
    # Vérifier les résultats
    assert music_player.selected_widget1.selected == False
    assert music_player.normal_widget.selected == False
    
    # Vérifier que _set_item_colors a été appelée
    assert len(music_player.set_item_colors_calls) == 2
    assert music_player.set_item_colors_calls[0] == (music_player.selected_widget1, '#4a4a4a')
    assert music_player.set_item_colors_calls[1] == (music_player.normal_widget, '#4a4a4a')
    
    print("✅ Test réussi: Sélection nettoyée dans la playlist principale")

def test_clear_current_song_selection_in_downloads():
    """Test du nettoyage de sélection dans les téléchargements"""
    print("🧪 Test: Nettoyage sélection téléchargements")
    
    music_player = MockMusicPlayer()
    
    # État initial
    assert music_player.selected_widget2.selected == True
    assert music_player.selected_widget2.bg_color == '#5a9fd8'
    
    # Appeler la fonction de nettoyage
    clear_current_song_selection_in_downloads(music_player)
    
    # Vérifier les résultats
    assert music_player.selected_widget2.selected == False
    
    # Vérifier que _set_item_colors a été appelée
    assert len(music_player.set_item_colors_calls) == 1
    assert music_player.set_item_colors_calls[0] == (music_player.selected_widget2, '#4a4a4a')
    
    print("✅ Test réussi: Sélection nettoyée dans les téléchargements")

def test_clear_all_current_song_selections():
    """Test du nettoyage de sélection dans tous les containers"""
    print("🧪 Test: Nettoyage sélection dans tous les containers")
    
    music_player = MockMusicPlayer()
    
    # État initial
    assert music_player.selected_widget1.selected == True
    assert music_player.selected_widget2.selected == True
    
    # Appeler la fonction de nettoyage global
    clear_all_current_song_selections(music_player)
    
    # Vérifier les résultats
    assert music_player.selected_widget1.selected == False
    assert music_player.selected_widget2.selected == False
    
    # Vérifier que _set_item_colors a été appelée pour tous les widgets
    assert len(music_player.set_item_colors_calls) >= 2
    
    print("✅ Test réussi: Sélection nettoyée dans tous les containers")

def test_fallback_without_set_item_colors():
    """Test du fallback quand _set_item_colors n'existe pas"""
    print("🧪 Test: Fallback sans _set_item_colors")
    
    music_player = MockMusicPlayer()
    # Supprimer la méthode _set_item_colors pour tester le fallback
    delattr(music_player, '_set_item_colors')
    
    # État initial
    assert music_player.selected_widget1.selected == True
    
    # Appeler la fonction de nettoyage
    clear_current_song_selection(music_player)
    
    # Vérifier les résultats
    assert music_player.selected_widget1.selected == False
    assert music_player.selected_widget1.config_called == True
    assert music_player.selected_widget1.config_color == '#4a4a4a'
    
    print("✅ Test réussi: Fallback fonctionne sans _set_item_colors")

if __name__ == "__main__":
    print("🔧 Test du système de nettoyage de sélection\n")
    
    try:
        test_clear_current_song_selection()
        test_clear_current_song_selection_in_downloads()
        test_clear_all_current_song_selections()
        test_fallback_without_set_item_colors()
        
        print(f"\n🎉 Tous les tests sont passés ! Le système de nettoyage de sélection fonctionne correctement.")
        
    except AssertionError as e:
        print(f"\n❌ Test échoué: {e}")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")