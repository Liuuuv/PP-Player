#!/usr/bin/env python3
"""
Script de test pour vérifier que l'application démarre sans erreur
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_imports():
    """Test des imports principaux"""
    print("Test des imports...")
    
    try:
        # Test des imports de base
        import tkinter as tk
        print("✓ tkinter importé")
        
        import pygame
        print("✓ pygame importé")
        
        # Test des imports du projet
        from main import MusicPlayer
        print("✓ MusicPlayer importé")
        
        import search_tab.main_playlist
        print("✓ search_tab.main_playlist importé")
        
        import library_tab.downloads
        print("✓ library_tab.downloads importé")
        
        print("\n✅ Tous les imports sont OK !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur d'import: {e}")
        return False

def test_methods():
    """Test de l'existence des méthodes optimisées"""
    print("\nTest des méthodes optimisées...")
    
    try:
        from main import MusicPlayer
        import tkinter as tk
        
        # Créer une instance temporaire pour tester
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        
        player = MusicPlayer(root)
        
        # Vérifier que les nouvelles méthodes existent
        methods_to_check = [
            '_disable_play_buttons',
            '_enable_play_buttons', 
            '_refresh_main_playlist_display_async'
        ]
        
        for method_name in methods_to_check:
            if hasattr(player, method_name):
                print(f"✓ {method_name} existe")
            else:
                print(f"❌ {method_name} manquante")
                return False
        
        root.destroy()
        print("\n✅ Toutes les méthodes optimisées sont présentes !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test des méthodes: {e}")
        return False

if __name__ == "__main__":
    print("=== Test de démarrage de l'application ===")
    
    success = True
    success &= test_imports()
    success &= test_methods()
    
    if success:
        print("\n🎉 L'application est prête à être utilisée avec les optimisations !")
        print("\nPour tester les optimisations:")
        print("1. Lancez l'application normalement")
        print("2. Allez dans l'onglet Bibliothèque")
        print("3. Cliquez sur 'Jouer toutes les musiques' avec 50+ musiques")
        print("4. Observez la fluidité améliorée !")
    else:
        print("\n⚠️  Il y a des problèmes à corriger avant d'utiliser l'application.")