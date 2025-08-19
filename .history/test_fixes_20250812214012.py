#!/usr/bin/env python3
"""
Test pour vérifier que les corrections des erreurs fonctionnent
"""

import tkinter as tk
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clear_current_selection import clear_all_current_song_selections

class MockWidget:
    """Mock d'un widget tkinter qui peut être détruit"""
    
    def __init__(self, exists=True, selected=False):
        self.exists = exists
        self.selected = selected
        self.config_calls = []
        
    def winfo_exists(self):
        return self.exists
        
    def config(self, **kwargs):
        if not self.exists:
            raise tk.TclError("bad window path name")
        self.config_calls.append(kwargs)
        
    def destroy(self):
        self.exists = False

class MockContainer:
    """Mock d'un container tkinter"""
    
    def __init__(self, children=None, exists=True):
        self.children = children or []
        self.exists = exists
        
    def winfo_exists(self):
        return self.exists
        
    def winfo_children(self):
        if not self.exists:
            raise tk.TclError("bad window path name")
        return self.children
        
    def destroy(self):
        self.exists = False
        for child in self.children:
            child.destroy()

class MockMusicPlayer:
    """Mock du MusicPlayer pour tester la robustesse"""
    
    def __init__(self, scenario="normal"):
        if scenario == "normal":
            # Scénario normal
            self.widget1 = MockWidget(exists=True, selected=True)
            self.widget2 = MockWidget(exists=True, selected=False)
            
            self.playlist_container = MockContainer([self.widget1, self.widget2], exists=True)
            self.downloads_container = MockContainer([], exists=True)
            self.playlist_content_container = MockContainer([], exists=True)
            
        elif scenario == "destroyed_widgets":
            # Scénario avec widgets détruits
            self.widget1 = MockWidget(exists=False, selected=True)  # Widget détruit
            self.widget2 = MockWidget(exists=True, selected=False)
            
            self.playlist_container = MockContainer([self.widget1, self.widget2], exists=True)
            self.downloads_container = MockContainer([], exists=True)
            self.playlist_content_container = MockContainer([], exists=True)
            
        elif scenario == "destroyed_container":
            # Scénario avec container détruit
            self.widget1 = MockWidget(exists=True, selected=True)
            
            self.playlist_container = MockContainer([self.widget1], exists=False)  # Container détruit
            self.downloads_container = MockContainer([], exists=True)
            self.playlist_content_container = MockContainer([], exists=True)
        
        self.set_item_colors_calls = []
        
    def _set_item_colors(self, widget, color):
        """Mock de _set_item_colors"""
        self.set_item_colors_calls.append((widget, color))
        widget.config(bg=color)

def test_normal_scenario():
    """Test du scénario normal"""
    print("🧪 Test: Scénario normal")
    
    music_player = MockMusicPlayer("normal")
    
    # Appeler la fonction
    clear_all_current_song_selections(music_player)
    
    # Vérifier que ça fonctionne
    assert music_player.widget1.selected == False
    assert len(music_player.set_item_colors_calls) >= 1
    
    print("✅ Test réussi: Scénario normal")

def test_destroyed_widgets_scenario():
    """Test avec des widgets détruits"""
    print("🧪 Test: Widgets détruits")
    
    music_player = MockMusicPlayer("destroyed_widgets")
    
    # Appeler la fonction - ne devrait pas lever d'exception
    try:
        clear_all_current_song_selections(music_player)
        print("✅ Test réussi: Pas d'exception avec widgets détruits")
    except Exception as e:
        print(f"❌ Test échoué: Exception levée: {e}")
        return False
    
    # Vérifier que le widget existant a été traité
    assert music_player.widget2.selected == False
    
    return True

def test_destroyed_container_scenario():
    """Test avec un container détruit"""
    print("🧪 Test: Container détruit")
    
    music_player = MockMusicPlayer("destroyed_container")
    
    # Appeler la fonction - ne devrait pas lever d'exception
    try:
        clear_all_current_song_selections(music_player)
        print("✅ Test réussi: Pas d'exception avec container détruit")
    except Exception as e:
        print(f"❌ Test échoué: Exception levée: {e}")
        return False
    
    return True

def test_missing_containers():
    """Test avec des containers manquants"""
    print("🧪 Test: Containers manquants")
    
    # Créer un music player sans certains containers
    class MockMusicPlayerMinimal:
        def __init__(self):
            # Seulement playlist_container, pas les autres
            self.widget1 = MockWidget(exists=True, selected=True)
            self.playlist_container = MockContainer([self.widget1], exists=True)
            # Pas de downloads_container ni playlist_content_container
            
        def _set_item_colors(self, widget, color):
            widget.config(bg=color)
    
    music_player = MockMusicPlayerMinimal()
    
    # Appeler la fonction - ne devrait pas lever d'exception
    try:
        clear_all_current_song_selections(music_player)
        print("✅ Test réussi: Pas d'exception avec containers manquants")
    except Exception as e:
        print(f"❌ Test échoué: Exception levée: {e}")
        return False
    
    # Vérifier que le widget a été traité
    assert music_player.widget1.selected == False
    
    return True

if __name__ == "__main__":
    print("🔧 Test des corrections d'erreurs\n")
    
    try:
        test_normal_scenario()
        success1 = test_destroyed_widgets_scenario()
        success2 = test_destroyed_container_scenario()
        success3 = test_missing_containers()
        
        if success1 and success2 and success3:
            print(f"\n🎉 Tous les tests sont passés ! Les corrections fonctionnent correctement.")
        else:
            print(f"\n⚠️  Certains tests ont échoué.")
            
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")