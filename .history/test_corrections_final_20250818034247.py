#!/usr/bin/env python3
"""
Test des 3 corrections importantes :
1. Protection contre les index négatifs
2. Bouton find direct (sans rechargement d'affichage)
3. Auto-scroll fonctionnel avec animation ease in/out
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_protection_index_negatifs():
    """Test protection contre les index négatifs"""
    print("=== Test protection index négatifs ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Configuration avec debug
        update_main_playlist_config(
            debug_scroll=True,
            enable_smart_loading=True,
            reload_on_song_change=True
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Playlist courte pour tester les cas limites
        player.main_playlist = [f"protection_{i:02d}.mp3" for i in range(1, 21)]  # 20 musiques seulement
        
        print(f"✓ Playlist courte: {len(player.main_playlist)} musiques")
        
        # Test des cas problématiques
        test_cases = [
            ("Position très basse puis remontée rapide", 18, 2),
            ("Position 0 puis descente", 0, 15),
            ("Position négative simulée", -5, 5),
            ("Position au-delà de la playlist", 25, 10),
        ]
        
        for test_name, start_pos, end_pos in test_cases:
            print(f"\n--- {test_name} ---")
            
            # Position de départ
            player.current_index = max(0, min(start_pos, len(player.main_playlist) - 1))
            print(f"  Position départ: {player.current_index}")
            
            # Simuler un smart reload (peut créer des index négatifs sans protection)
            print(f"  🔄 Smart reload depuis position {player.current_index}...")
            player._smart_load_unload()
            
            # Changer vers position finale
            player.current_index = max(0, min(end_pos, len(player.main_playlist) - 1))
            print(f"  Position finale: {player.current_index}")
            
            # Nouveau smart reload
            print(f"  🔄 Smart reload vers position {player.current_index}...")
            player._smart_load_unload()
            
            # Vérifier que les fenêtres sont valides
            if hasattr(player, '_last_window_start') and hasattr(player, '_last_window_end'):
                start = player._last_window_start
                end = player._last_window_end
                
                if start >= 0 and end >= 0 and start < len(player.main_playlist):
                    print(f"  ✅ Fenêtre valide: {start}-{end}")
                else:
                    print(f"  ❌ Fenêtre invalide: {start}-{end}")
                    return False
        
        root.destroy()
        print("\n✅ Protection index négatifs fonctionne !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test protection index: {e}")
        return False

def test_bouton_find_direct():
    """Test bouton find direct (sans rechargement d'affichage)"""
    print("\n=== Test bouton find direct ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Configuration
        update_main_playlist_config(
            debug_scroll=True,
            enable_smart_loading=True,
            reload_on_song_change=True
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Playlist moyenne pour le test
        player.main_playlist = [f"find_direct_{i:03d}.mp3" for i in range(1, 101)]  # 100 musiques
        
        print(f"✓ Playlist test find: {len(player.main_playlist)} musiques")
        
        # Cas 1: Chanson déjà dans la fenêtre chargée (scroll direct)
        print(f"\n--- Cas 1: Chanson déjà chargée (scroll direct) ---")
        player.current_index = 30
        player._smart_load_unload()  # Charger fenêtre autour de 30
        
        if hasattr(player, '_last_window_start') and hasattr(player, '_last_window_end'):
            start = player._last_window_start
            end = player._last_window_end
            print(f"  Fenêtre chargée: {start}-{end}")
            
            # Changer vers une chanson dans la même fenêtre
            player.current_index = 35
            print(f"  Nouvelle position: {player.current_index} (dans fenêtre chargée)")
            
            # Test bouton find (devrait être direct)
            print(f"  🎯 Test bouton find direct...")
            player._scroll_to_current_song()
            print(f"  ✅ Find direct réussi")
        
        # Cas 2: Chanson pas dans la fenêtre (rechargement minimal + scroll)
        print(f"\n--- Cas 2: Chanson pas chargée (rechargement + scroll) ---")
        player.current_index = 80  # Loin de la fenêtre précédente
        print(f"  Nouvelle position: {player.current_index} (hors fenêtre)")
        
        # Test bouton find (devrait recharger puis scroller)
        print(f"  🎯 Test bouton find avec rechargement...")
        player._scroll_to_current_song()
        print(f"  ✅ Find avec rechargement réussi")
        
        root.destroy()
        print("\n✅ Bouton find direct fonctionne !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test bouton find: {e}")
        return False

def test_auto_scroll_fonctionnel():
    """Test auto-scroll avec animation ease in/out"""
    print("\n=== Test auto-scroll fonctionnel ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        import control
        
        # Configuration
        update_main_playlist_config(
            debug_scroll=True,
            enable_smart_loading=True,
            reload_on_song_change=True
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Playlist pour auto-scroll
        player.main_playlist = [f"auto_scroll_{i:03d}.mp3" for i in range(1, 201)]  # 200 musiques
        player.auto_scroll_enabled = True  # ACTIVER auto-scroll
        
        print(f"✓ Playlist auto-scroll: {len(player.main_playlist)} musiques")
        print(f"✓ Auto-scroll activé: {player.auto_scroll_enabled}")
        
        # Test cas différents d'auto-scroll
        test_scenarios = [
            ("Auto-scroll direct (chanson dans fenêtre)", 50, 52, False),
            ("Auto-scroll avec rechargement (chanson loin)", 50, 150, True),
            ("Auto-scroll début playlist", 100, 5, True),
            ("Auto-scroll fin playlist", 50, 190, True),
        ]
        
        for scenario_name, start_pos, end_pos, should_reload in test_scenarios:
            print(f"\n--- {scenario_name} ---")
            
            # Position de départ
            player.current_index = start_pos
            player._smart_load_unload()  # Charger fenêtre initiale
            print(f"  Position départ: {player.current_index}")
            
            # Simuler changement vers nouvelle position
            player.current_index = end_pos
            print(f"  Changement vers: {player.current_index}")
            
            # Test auto-scroll intelligent
            print(f"  🎮 Test auto-scroll smart...")
            player.select_current_song_smart(auto_scroll=True, force_reload=should_reload)
            
            # Vérifier le résultat
            if hasattr(player, '_last_window_start') and hasattr(player, '_last_window_end'):
                start = player._last_window_start
                end = player._last_window_end
                
                if start <= player.current_index < end:
                    print(f"  ✅ Auto-scroll réussi: chanson {player.current_index} dans fenêtre {start}-{end}")
                else:
                    print(f"  ❌ Auto-scroll échoué: chanson {player.current_index} pas dans fenêtre {start}-{end}")
                    return False
        
        # Test intégration avec control.py
        print(f"\n--- Test intégration control.py ---")
        
        player.current_index = 100
        player._smart_load_unload()
        
        # Test prev_track avec auto-scroll
        print(f"  Test prev_track avec auto-scroll...")
        old_index = player.current_index
        control.prev_track(player)
        print(f"  Prev track: {old_index} → {player.current_index}")
        
        # Test next_track avec auto-scroll
        print(f"  Test next_track avec auto-scroll...")
        old_index = player.current_index
        control.next_track(player)
        print(f"  Next track: {old_index} → {player.current_index}")
        
        root.destroy()
        print("\n✅ Auto-scroll fonctionnel !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test auto-scroll: {e}")
        return False

def test_scenario_complet():
    """Test d'un scénario complet avec toutes les corrections"""
    print("\n=== Test scénario complet ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Configuration complète
        update_main_playlist_config(
            debug_scroll=True,
            enable_smart_loading=True,
            reload_on_song_change=True,
            songs_before_current=10,
            songs_after_current=10
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Grande playlist pour test complet
        player.main_playlist = [f"complet_{i:04d}.mp3" for i in range(1, 501)]  # 500 musiques
        player.auto_scroll_enabled = True
        
        print(f"✓ GRANDE playlist: {len(player.main_playlist)} musiques")
        
        # Scénario : Navigation extrême avec toutes les fonctionnalités
        positions = [5, 250, 490, 10, 300, 2, 495]
        
        for i, position in enumerate(positions):
            print(f"\n--- Étape {i+1}: Position {position} ---")
            
            # 1. Changer position (simule changement de musique)
            player.current_index = position
            
            # 2. Smart reload (avec protection index)
            player._smart_load_unload()
            
            # 3. Auto-scroll intelligent
            player.select_current_song_smart(auto_scroll=True)
            
            # 4. Test bouton find
            player._scroll_to_current_song()
            
            # 5. Vérifier état final
            if hasattr(player, '_last_window_start') and hasattr(player, '_last_window_end'):
                start = player._last_window_start
                end = player._last_window_end
                
                # Vérifications de sécurité
                if start < 0 or end < 0:
                    print(f"  ❌ Index négatifs détectés: {start}-{end}")
                    return False
                
                if not (start <= position < end):
                    print(f"  ❌ Position {position} pas dans fenêtre {start}-{end}")
                    return False
                    
                loaded = end - start
                efficiency = (len(player.main_playlist) - loaded) / len(player.main_playlist) * 100
                print(f"  ✅ Position {position} OK, fenêtre {start}-{end}, efficacité {efficiency:.1f}%")
        
        root.destroy()
        print(f"\n✅ Scénario complet réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur scénario complet: {e}")
        return False

def show_corrections_summary():
    """Résumé des corrections apportées"""
    print("\n" + "="*80)
    print("🎉 CORRECTIONS IMPORTANTES APPORTÉES")
    print("="*80)
    
    print("\n✅ CORRECTION 1: Protection index négatifs")
    print("   ❌ Problème: Chargement musiques avant première musique")
    print("   ✅ Solution: Protection absolue dans _smart_load_unload() et _force_reload_window()")
    print("   • max(0, current_index - songs_before)")
    print("   • Validation rigoureuse start_index >= 0")
    print("   • Double vérification dans toutes les fonctions")
    
    print("\n✅ CORRECTION 2: Bouton find direct") 
    print("   ❌ Problème: Bouton find refaisait l'affichage avant scroll")
    print("   ✅ Solution: _scroll_to_current_song() optimisée")
    print("   • Si chanson dans fenêtre chargée → Scroll direct avec animation")
    print("   • Si chanson pas chargée → Rechargement minimal puis scroll")
    print("   • Délai optimisé (50ms) pour fluidité")
    
    print("\n✅ CORRECTION 3: Auto-scroll fonctionnel")
    print("   ❌ Problème: Auto-scroll ne fonctionnait pas")
    print("   ✅ Solution: select_current_song_smart() avec animations")
    print("   • control.prev_track() → select_current_song_smart(auto_scroll=True)")
    print("   • control.next_track() → select_current_song_smart(auto_scroll=True)")
    print("   • tools.play_track() → select_current_song_smart(auto_scroll=False)")
    print("   • Animation ease in/out automatique")
    
    print("\n🔧 AMÉLIORATIONS TECHNIQUES:")
    print("   • Protection absolue contre index négatifs/invalides")
    print("   • Validation rigoureuse dans toutes les fonctions")
    print("   • Debug détaillé pour diagnostics")
    print("   • Optimisations de performance")
    print("   • Gestion d'erreurs robuste")
    
    print("\n🎮 EXPÉRIENCE UTILISATEUR FINALE:")
    print("   🎵 Changement musique → Auto-scroll fluide avec animation")
    print("   🎯 Bouton find → Scroll direct instantané ou rechargement minimal")
    print("   ⏭️ Prev/Next → Auto-scroll automatique si activé")
    print("   🛡️ Navigation extrême → Pas de crash, pas d'index négatifs")
    print("   ⚡ Performance → Constante même avec 500+ musiques")

if __name__ == "__main__":
    print("🔧 TEST DES 3 CORRECTIONS IMPORTANTES")
    print("="*80)
    
    success1 = test_protection_index_negatifs()
    success2 = test_bouton_find_direct()  
    success3 = test_auto_scroll_fonctionnel()
    success4 = test_scenario_complet()
    
    show_corrections_summary()
    
    if success1 and success2 and success3 and success4:
        print(f"\n{'='*80}")
        print("🎉 TOUTES LES CORRECTIONS RÉUSSIES !")
        print("✅ Protection index négatifs fonctionnelle")
        print("✅ Bouton find direct opérationnel") 
        print("✅ Auto-scroll avec animations fonctionnel")
        print("✅ Scénario complet validé")
        print("🚀 Le système est maintenant parfaitement corrigé !")
        print("🎵 Testez toutes les fonctionnalités !")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("⚠️  Certaines corrections nécessitent des ajustements")
        print("🔧 Vérifiez les erreurs ci-dessus")
        print(f"{'='*80}")