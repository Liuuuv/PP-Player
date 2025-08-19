#!/usr/bin/env python3
"""
Test pour vérifier que le problème de clear + reload est résolu
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_clear_and_reload_scenario():
    """Test du scénario : jouer toutes les musiques -> clear -> rejouer toutes les musiques"""
    print("=== Test du scénario Clear + Reload ===")
    
    try:
        from main import MusicPlayer
        import tkinter as tk
        
        # Créer une instance temporaire
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Simuler des fichiers téléchargés
        player.all_downloaded_files = [f"test{i}.mp3" for i in range(1, 101)]  # 100 fichiers
        
        # Simuler les attributs nécessaires
        if not hasattr(player, 'status_bar'):
            player.status_bar = tk.Label(root, text="Test")
        if not hasattr(player, 'random_button'):
            player.random_button = tk.Button(root, text="Random")
        
        print("✓ Configuration initiale avec 100 fichiers")
        
        # ÉTAPE 1: Simuler "jouer toutes les musiques"
        print("\n1. Simulation de 'jouer toutes les musiques'...")
        
        # Simuler le chargement de la playlist
        player.main_playlist.clear()
        player.main_playlist.extend(player.all_downloaded_files.copy())
        player.current_index = 0
        player.random_mode = False
        
        # Simuler l'affichage avec fenêtrage (créer les variables)
        player._last_window_start = 0
        player._last_window_end = 30
        
        print(f"   ✓ Playlist chargée: {len(player.main_playlist)} musiques")
        print(f"   ✓ Variables de fenêtrage: start={player._last_window_start}, end={player._last_window_end}")
        
        # ÉTAPE 2: Simuler le clear
        print("\n2. Simulation du clear de la playlist...")
        
        # Appeler la fonction de reset
        player.reset_main_playlist()
        
        print(f"   ✓ Playlist après clear: {len(player.main_playlist)} musiques")
        
        # Vérifier que les variables de fenêtrage sont supprimées
        has_window_start = hasattr(player, '_last_window_start')
        has_window_end = hasattr(player, '_last_window_end')
        
        print(f"   ✓ Variable _last_window_start supprimée: {not has_window_start}")
        print(f"   ✓ Variable _last_window_end supprimée: {not has_window_end}")
        
        if has_window_start or has_window_end:
            print("   ❌ PROBLÈME: Les variables de fenêtrage n'ont pas été supprimées !")
            return False
        
        # ÉTAPE 3: Simuler le rechargement
        print("\n3. Simulation du rechargement de toutes les musiques...")
        
        # Recharger la playlist
        player.main_playlist.clear()
        player.main_playlist.extend(player.all_downloaded_files.copy())
        player.current_index = 0
        
        print(f"   ✓ Playlist rechargée: {len(player.main_playlist)} musiques")
        
        # Tester la fonction de rafraîchissement asynchrone
        try:
            player._refresh_main_playlist_display_async()
            print("   ✓ Rafraîchissement asynchrone réussi")
        except Exception as e:
            print(f"   ❌ Erreur lors du rafraîchissement: {e}")
            return False
        
        # Vérifier que les nouvelles variables de fenêtrage peuvent être créées
        try:
            player._refresh_windowed_playlist_display()
            print("   ✓ Affichage par fenêtrage réussi")
        except Exception as e:
            print(f"   ❌ Erreur lors de l'affichage par fenêtrage: {e}")
            return False
        
        root.destroy()
        print("\n✅ Test du scénario Clear + Reload réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur générale: {e}")
        return False

def test_windowing_variables_reset():
    """Test spécifique de la réinitialisation des variables de fenêtrage"""
    print("\n=== Test de la réinitialisation des variables ===")
    
    try:
        from main import MusicPlayer
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Créer manuellement les variables de fenêtrage
        player._last_window_start = 10
        player._last_window_end = 40
        player._last_select_time = 123456789
        
        print("✓ Variables de fenêtrage créées manuellement")
        print(f"   _last_window_start: {player._last_window_start}")
        print(f"   _last_window_end: {player._last_window_end}")
        print(f"   _last_select_time: {player._last_select_time}")
        
        # Appeler reset_main_playlist
        player.reset_main_playlist()
        
        # Vérifier que les variables sont supprimées/réinitialisées
        has_start = hasattr(player, '_last_window_start')
        has_end = hasattr(player, '_last_window_end')
        select_time = getattr(player, '_last_select_time', None)
        
        print("\nAprès reset_main_playlist:")
        print(f"   _last_window_start existe: {has_start}")
        print(f"   _last_window_end existe: {has_end}")
        print(f"   _last_select_time: {select_time}")
        
        if has_start or has_end:
            print("❌ ÉCHEC: Les variables de fenêtrage n'ont pas été supprimées")
            return False
        
        if select_time != 0:
            print("❌ ÉCHEC: _last_select_time n'a pas été réinitialisé à 0")
            return False
        
        root.destroy()
        print("✅ Réinitialisation des variables réussie !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de réinitialisation: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TEST DE LA CORRECTION DU PROBLÈME CLEAR + RELOAD")
    print("="*60)
    
    success1 = test_clear_and_reload_scenario()
    success2 = test_windowing_variables_reset()
    
    print("\n" + "="*60)
    if success1 and success2:
        print("🎉 CORRECTION RÉUSSIE !")
        print("✅ Le problème Clear + Reload est résolu")
        print("✅ Les variables de fenêtrage sont correctement réinitialisées")
        print("\n🚀 L'application devrait maintenant afficher la playlist")
        print("   même après un clear et un rechargement !")
    else:
        print("⚠️  Il reste des problèmes à corriger")
    print("="*60)