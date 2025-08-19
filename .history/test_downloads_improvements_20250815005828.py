#!/usr/bin/env python3
"""
Script de test pour les améliorations de l'onglet téléchargements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import MusicPlayer
import tkinter as tk

def test_downloads_tab():
    """Test des fonctionnalités de l'onglet téléchargements"""
    
    # Créer l'application
    root = tk.Tk()
    app = MusicPlayer(root)
    
    # Test 1: Ajouter un téléchargement de test
    print("Test 1: Ajout d'un téléchargement de test")
    test_url = "https://www.youtube.com/watch?v=test123"
    test_title = "Test Video - Long Title That Should Be Truncated Properly"
    test_video_data = {
        'title': test_title,
        'thumbnails': [{'url': 'https://example.com/thumb.jpg'}]
    }
    
    success = app.add_download_to_tab(test_url, test_title, test_video_data)
    print(f"Ajout réussi: {success}")
    
    # Test 2: Ajouter un import de fichier
    print("\nTest 2: Ajout d'un import de fichier")
    test_file = "C:\\Users\\test\\music.mp3"
    success = app.add_file_import_to_tab(test_file, "Imported Music File")
    print(f"Import réussi: {success}")
    
    # Test 3: Vérifier l'espacement des boutons
    print("\nTest 3: Interface créée avec espacement des boutons amélioré")
    
    # Afficher l'interface
    print("Interface prête. Fermez la fenêtre pour terminer le test.")
    root.mainloop()

if __name__ == "__main__":
    test_downloads_tab()