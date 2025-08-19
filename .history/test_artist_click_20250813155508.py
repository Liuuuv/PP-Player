#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script pour simuler un clic sur un artiste
"""

import main
import tkinter as tk

def test_artist_click():
    """Test simulé d'un clic sur un artiste"""
    
    root = tk.Tk()
    root.withdraw()  # Masquer la fenêtre
    
    try:
        player = main.MusicPlayer(root)
        
        # Simuler des données vidéo comme celles reçues lors d'un clic sur artiste
        fake_video_data = {
            'channel_url': 'https://www.youtube.com/@TestArtist',
            'uploader': 'Test Artist',
            'title': 'Test Song'
        }
        
        # Tester l'appel à _show_artist_content
        print("🧪 Test de _show_artist_content...")
        player._show_artist_content("Test Artist", fake_video_data)
        print("✅ _show_artist_content exécuté sans erreur!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    success = test_artist_click()
    if success:
        print("\n🎉 Test réussi! L'erreur 'NoneType' object has no attribute 'update_idletasks' devrait être corrigée.")
    else:
        print("\n💥 Test échoué! Il y a encore des problèmes.")