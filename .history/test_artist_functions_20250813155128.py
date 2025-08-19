#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script pour vérifier que toutes les fonctions d'artiste sont disponibles
"""

import main

def test_artist_functions():
    """Test que toutes les fonctions d'artiste nécessaires existent"""
    
    # Créer une instance fictive pour tester
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Masquer la fenêtre
    
    try:
        player = main.MusicPlayer(root)
        
        # Tester que les fonctions existent
        functions_to_test = [
            '_hide_search_elements',
            '_show_artist_content', 
            '_save_current_search_state',
            '_create_artist_tabs',
            '_search_artist_content_async',
            '_find_artist_channel_id',
            '_search_artist_videos_with_id',
            '_search_artist_releases_with_id',
            '_search_artist_playlists_with_id',
            '_display_artist_videos',
            '_display_artist_releases', 
            '_display_artist_playlists',
            '_add_artist_result',
            '_load_artist_thumbnail',
            '_show_error_in_tabs',
            '_cancel_artist_search',
            '_update_loading_messages',
            '_return_to_search'
        ]
        
        missing_functions = []
        for func_name in functions_to_test:
            if not hasattr(player, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"❌ Fonctions manquantes: {missing_functions}")
            return False
        else:
            print("✅ Toutes les fonctions d'artiste sont disponibles!")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    success = test_artist_functions()
    if success:
        print("\n🎉 Test réussi! L'erreur '_hide_search_elements' devrait être corrigée.")
    else:
        print("\n💥 Test échoué! Il y a encore des fonctions manquantes.")