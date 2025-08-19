#!/usr/bin/env python3
"""
Test du scroll avec messages de debug pour diagnostiquer le problème
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_scroll_debug_messages():
    """Test pour vérifier que les messages de debug s'affichent"""
    print("=== Test des messages de debug du scroll ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Activer le debug
        update_main_playlist_config(debug_scroll=True, debug_windowing=True)
        
        # Créer une instance avec interface minimale
        root = tk.Tk()
        root.title("Test Debug Scroll")
        root.geometry("800x600")
        
        print("✅ DEBUG: Fenêtre Tkinter créée")
        
        player = MusicPlayer(root)
        
        # Simuler une playlist
        player.main_playlist = [f"test_{i:03d}.mp3" for i in range(50)]
        player.current_index = 25
        
        print(f"✅ DEBUG: Playlist créée avec {len(player.main_playlist)} musiques")
        
        # Rafraîchir l'affichage
        try:
            player._refresh_main_playlist_display(force_full_refresh=True)
            print("✅ DEBUG: Affichage rafraîchi")
        except Exception as e:
            print(f"⚠️ DEBUG: Erreur rafraîchissement: {e}")
        
        # Vérifier que les fonctions de debug existent
        functions_to_check = [
            '_setup_infinite_scroll',
            '_update_display_based_on_scroll_position',
            '_update_windowed_display',
            '_on_scroll_with_update'
        ]
        
        for func_name in functions_to_check:
            if hasattr(player, func_name):
                print(f"✅ DEBUG: Fonction {func_name} disponible")
            else:
                print(f"❌ DEBUG: Fonction {func_name} manquante")
        
        # Vérifier les attributs du canvas
        if hasattr(player, 'playlist_canvas'):
            print(f"✅ DEBUG: playlist_canvas trouvé: {type(player.playlist_canvas)}")
            
            # Vérifier les bindings
            try:
                bindings = player.playlist_canvas.bind()
                print(f"📋 DEBUG: Bindings sur playlist_canvas: {bindings}")
            except Exception as e:
                print(f"⚠️ DEBUG: Erreur lecture bindings: {e}")
        else:
            print("❌ DEBUG: playlist_canvas non trouvé")
        
        if hasattr(player, 'playlist_scrollbar'):
            print(f"✅ DEBUG: playlist_scrollbar trouvé: {type(player.playlist_scrollbar)}")
        else:
            print("❌ DEBUG: playlist_scrollbar non trouvé")
        
        # Test manuel de la fonction de synchronisation
        print("\n--- Test manuel de la synchronisation ---")
        try:
            player._update_display_based_on_scroll_position()
            print("✅ DEBUG: Test manuel de synchronisation réussi")
        except Exception as e:
            print(f"❌ DEBUG: Erreur test manuel: {e}")
        
        # Afficher des instructions pour le test manuel
        print("\n" + "="*60)
        print("🖱️ INSTRUCTIONS POUR LE TEST MANUEL:")
        print("="*60)
        print("1. Une fenêtre de test devrait s'ouvrir")
        print("2. Allez dans l'onglet 'Recherche'")
        print("3. Scrollez avec la molette dans la playlist")
        print("4. Observez les messages de debug dans cette console")
        print("5. Fermez la fenêtre pour terminer le test")
        print("="*60)
        
        # Lancer la boucle principale pour permettre l'interaction
        root.mainloop()
        
        print("\n✅ DEBUG: Test terminé")
        return True
        
    except Exception as e:
        print(f"\n❌ DEBUG: Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 TEST DE DEBUG DU SCROLL")
    print("="*60)
    
    success = test_scroll_debug_messages()
    
    if success:
        print("\n✅ Test de debug terminé")
        print("Vérifiez les messages de debug ci-dessus pour diagnostiquer le problème")
    else:
        print("\n❌ Erreur lors du test de debug")