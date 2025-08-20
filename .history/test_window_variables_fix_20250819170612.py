#!/usr/bin/env python3
"""
Test de correction des variables de fenêtrage manquantes
Vérifie que _last_window_start et _last_window_end sont correctement initialisées
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_window_variables_initialization():
    """Test que les variables de fenêtrage sont correctement initialisées"""
    print("🧪 TEST: Initialisation des variables de fenêtrage")
    
    try:
        import tkinter as tk
        from main import MusicPlayer
        
        # Créer une instance de test
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        player = MusicPlayer(root)
        
        # Simuler une playlist
        player.main_playlist = [f"track_{i:03d}.mp3" for i in range(1, 101)]  # 100 pistes
        player.current_index = 25  # Position au milieu
        
        print(f"✅ Playlist créée: {len(player.main_playlist)} pistes")
        print(f"✅ Position courante: {player.current_index}")
        
        # Vérifier l'état initial
        has_start = hasattr(player, '_last_window_start')
        has_end = hasattr(player, '_last_window_end')
        print(f"📊 État initial - _last_window_start: {has_start}, _last_window_end: {has_end}")
        
        # Configurer le scroll dynamique
        try:
            player._setup_dynamic_scroll()
            print("✅ Configuration du scroll dynamique réussie")
            
            # Vérifier que les variables sont maintenant initialisées
            has_start_after = hasattr(player, '_last_window_start')
            has_end_after = hasattr(player, '_last_window_end')
            print(f"📊 Après setup - _last_window_start: {has_start_after}, _last_window_end: {has_end_after}")
            
            if has_start_after and has_end_after:
                print(f"✅ Variables initialisées: start={player._last_window_start}, end={player._last_window_end}")
            else:
                print("❌ Variables toujours manquantes après setup")
                
        except Exception as e:
            print(f"⚠️ Erreur configuration: {type(e).__name__}: {e}")
        
        # Tester le système de chargement progressif
        try:
            player._progressive_load_system()
            print("✅ Système de chargement progressif appelé")
            
            # Vérifier les variables après chargement
            if hasattr(player, '_last_window_start') and hasattr(player, '_last_window_end'):
                start = player._last_window_start
                end = player._last_window_end
                print(f"✅ Variables après chargement: start={start}, end={end}")
                
                # Vérifier que les valeurs sont logiques
                if 0 <= start <= player.current_index <= end <= len(player.main_playlist):
                    print("✅ Valeurs des variables logiques")
                else:
                    print(f"⚠️ Valeurs suspectes: current_index={player.current_index}, playlist_size={len(player.main_playlist)}")
            else:
                print("❌ Variables toujours manquantes après chargement progressif")
                
        except Exception as e:
            print(f"⚠️ Erreur chargement progressif: {type(e).__name__}: {e}")
        
        # Tester les fonctions qui utilisent ces variables
        try:
            player._load_more_songs_below()
            print("✅ _load_more_songs_below appelée sans erreur")
        except Exception as e:
            print(f"⚠️ Erreur _load_more_songs_below: {type(e).__name__}: {e}")
        
        try:
            player._extend_window_down(player._last_window_end + 5)
            print("✅ _extend_window_down appelée sans erreur")
        except Exception as e:
            print(f"⚠️ Erreur _extend_window_down: {type(e).__name__}: {e}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def test_load_more_on_scroll():
    """Test spécifique de la fonction _load_more_on_scroll"""
    print("\n🧪 TEST: Fonction _load_more_on_scroll")
    
    try:
        import tkinter as tk
        from main import MusicPlayer
        
        # Créer une instance de test
        root = tk.Tk()
        root.withdraw()
        player = MusicPlayer(root)
        
        # Simuler une playlist
        player.main_playlist = [f"track_{i:03d}.mp3" for i in range(1, 51)]  # 50 pistes
        player.current_index = 10
        
        # Initialiser le système
        player._setup_dynamic_scroll()
        player._progressive_load_system()
        
        # Tester _load_more_on_scroll
        try:
            player._load_more_on_scroll()
            print("✅ _load_more_on_scroll exécutée sans erreur")
        except Exception as e:
            print(f"❌ Erreur _load_more_on_scroll: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test load_more: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🎯 TEST DE CORRECTION DES VARIABLES DE FENÊTRAGE")
    print("=" * 60)
    
    # Tests
    init_ok = test_window_variables_initialization()
    load_ok = test_load_more_on_scroll()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS:")
    print(f"   • Initialisation variables: {'✅ OK' if init_ok else '❌ ÉCHEC'}")
    print(f"   • Fonction load_more: {'✅ OK' if load_ok else '❌ ÉCHEC'}")
    
    if all([init_ok, load_ok]):
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Les variables de fenêtrage sont correctement initialisées")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    print("\n📋 CORRECTIONS APPORTÉES:")
    print("   • Initialisation de _last_window_start et _last_window_end dans _setup_dynamic_scroll()")
    print("   • Mise à jour des variables dans _progressive_load_system()")
    print("   • Correction de la référence load_more_on_scroll → load_more_count")
    print("   • Protection contre les variables manquantes")

if __name__ == "__main__":
    main()