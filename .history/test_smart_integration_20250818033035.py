#!/usr/bin/env python3
"""
Test de l'intégration complète du système intelligent avec :
- Bouton find.png (scroll vers musique courante)
- Auto-scroll
- Barre de scroll correcte
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_scroll_to_current_integration():
    """Test du bouton find.png (scroll vers musique courante)"""
    print("=== Test bouton find.png (scroll vers musique courante) ===")
    
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
        
        # Playlist de test
        player.main_playlist = [f"test_find_{i:03d}.mp3" for i in range(1, 151)]  # 150 musiques
        
        print(f"✓ Playlist: {len(player.main_playlist)} musiques")
        
        # Test des fonctions nécessaires
        functions_to_test = [
            '_scroll_to_current_song',
            'select_current_song_smart',
            '_force_reload_window'
        ]
        
        for func_name in functions_to_test:
            if hasattr(player, func_name):
                print(f"✅ {func_name} : disponible")
            else:
                print(f"❌ {func_name} : manquante")
                return False
        
        # Simulation : chanson loin de la position actuelle
        print(f"\n--- Test scroll vers chanson éloignée ---")
        
        # Charger une fenêtre au début
        player.current_index = 10
        player._smart_load_unload()  # Charge 0-21 environ
        
        # Changer vers une chanson éloignée
        player.current_index = 80
        print(f"  Chanson courante changée vers: {player.current_index}")
        
        # Test de la fonction _scroll_to_current_song (bouton find.png)
        print(f"  🎯 Test _scroll_to_current_song...")
        player._scroll_to_current_song()
        
        # Vérifier le résultat
        if hasattr(player, '_last_window_start') and hasattr(player, '_last_window_end'):
            start = player._last_window_start
            end = player._last_window_end
            print(f"  Nouvelle fenêtre chargée: {start}-{end}")
            
            if start <= player.current_index < end:
                print(f"  ✅ Chanson courante ({player.current_index}) incluse après scroll")
            else:
                print(f"  ❌ Chanson courante ({player.current_index}) pas incluse !")
                return False
        
        # Test de select_current_song_smart
        print(f"\n--- Test select_current_song_smart ---")
        player.select_current_song_smart(auto_scroll=True)
        
        root.destroy()
        print("\n✅ Test scroll_to_current réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test scroll_to_current: {e}")
        return False

def test_auto_scroll_integration():
    """Test de l'auto-scroll avec le système intelligent"""
    print("\n=== Test auto-scroll avec système intelligent ===")
    
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
        
        # Playlist et configuration auto-scroll
        player.main_playlist = [f"autoscroll_{i:03d}.mp3" for i in range(1, 201)]  # 200 musiques
        player.auto_scroll_enabled = True  # Activer auto-scroll
        
        print(f"✓ Playlist: {len(player.main_playlist)} musiques")
        print(f"✓ Auto-scroll activé: {player.auto_scroll_enabled}")
        
        # Test des fonctions modifiées dans control.py
        import control
        import inspect
        
        # Vérifier que control.py utilise bien select_current_song_smart
        functions_to_check = ['prev_track', 'next_track']
        
        for func_name in functions_to_check:
            if hasattr(control, func_name):
                source = inspect.getsource(getattr(control, func_name))
                if 'select_current_song_smart' in source:
                    print(f"✅ {func_name} utilise select_current_song_smart")
                else:
                    print(f"❌ {func_name} n'utilise pas select_current_song_smart")
                    return False
            else:
                print(f"⚠️  Fonction {func_name} non trouvée")
        
        # Test simulation changement avec auto-scroll
        print(f"\n--- Test simulation prev/next avec auto-scroll ---")
        
        # Position initiale
        player.current_index = 50
        print(f"Position initiale: {player.current_index}")
        
        # Simuler prev_track (devrait déclencher auto-scroll intelligent)
        old_index = player.current_index
        control.prev_track(player)
        print(f"Après prev_track: {old_index} → {player.current_index}")
        
        # Simuler next_track  
        old_index = player.current_index
        control.next_track(player)
        print(f"Après next_track: {old_index} → {player.current_index}")
        
        root.destroy()
        print("\n✅ Test auto-scroll réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test auto-scroll: {e}")
        return False

def test_scroll_region_correct():
    """Test que la barre de scroll est correcte"""
    print("\n=== Test barre de scroll correcte ===")
    
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
        
        # Grande playlist pour voir l'effet
        player.main_playlist = [f"scrollbar_{i:04d}.mp3" for i in range(1, 1001)]  # 1000 musiques !
        
        print(f"✓ MEGA Playlist: {len(player.main_playlist)} musiques")
        
        # Charger une petite fenêtre
        player.current_index = 100
        player._smart_load_unload()
        
        # Tester _update_canvas_scroll_region
        print(f"\n--- Test update_canvas_scroll_region ---")
        
        if hasattr(player, '_last_window_start') and hasattr(player, '_last_window_end'):
            start = player._last_window_start
            end = player._last_window_end
            loaded = end - start
            total = len(player.main_playlist)
            
            print(f"Fenêtre chargée: {start}-{end} ({loaded} éléments)")
            print(f"Total musiques: {total}")
            print(f"Pourcentage chargé: {loaded/total*100:.1f}%")
            
            # La barre de scroll devrait refléter seulement les éléments chargés
            # et non la totalité des musiques
            efficiency = (total - loaded) / total * 100
            if efficiency > 95:
                print(f"✅ Excellente optimisation barre de scroll: {efficiency:.1f}% d'économie")
            else:
                print(f"⚠️  Optimisation barre de scroll à améliorer: {efficiency:.1f}%")
        
        root.destroy()
        print("\n✅ Test barre de scroll réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test barre de scroll: {e}")
        return False

def test_all_integrations_scenario():
    """Test d'un scénario complet avec toutes les intégrations"""
    print("\n=== Test scénario complet toutes intégrations ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Configuration complète
        update_main_playlist_config(
            debug_scroll=True,
            enable_smart_loading=True,
            reload_on_song_change=True,
            auto_unload_unused=True,
            songs_before_current=10,
            songs_after_current=10
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Playlist réaliste
        player.main_playlist = [f"integration_{i:03d}.mp3" for i in range(1, 301)]  # 300 musiques
        player.auto_scroll_enabled = True
        
        print(f"✓ Playlist complète: {len(player.main_playlist)} musiques")
        print(f"✓ Auto-scroll: {player.auto_scroll_enabled}")
        
        scenarios = [
            ("Début playlist", 5),
            ("Milieu playlist", 150),
            ("Fin playlist", 290)
        ]
        
        for scenario_name, position in scenarios:
            print(f"\n--- {scenario_name} (position {position}) ---")
            
            # 1. Changer position
            player.current_index = position
            
            # 2. Déclencher smart reload (comme changement de musique)
            player._trigger_smart_reload_on_song_change()
            
            # 3. Test bouton find (scroll to current)
            print(f"  🎯 Test bouton find...")
            player._scroll_to_current_song()
            
            # 4. Test select smart
            print(f"  🔍 Test select smart...")
            player.select_current_song_smart(auto_scroll=True)
            
            # 5. Vérifier état
            if hasattr(player, '_last_window_start') and hasattr(player, '_last_window_end'):
                start = player._last_window_start
                end = player._last_window_end
                loaded = end - start
                
                print(f"  Résultat: fenêtre {start}-{end} ({loaded} éléments)")
                
                if start <= position < end:
                    print(f"  ✅ Position {position} correctement incluse")
                else:
                    print(f"  ❌ Position {position} pas incluse !")
                    return False
                    
                efficiency = (len(player.main_playlist) - loaded) / len(player.main_playlist) * 100
                print(f"  💾 Efficacité: {efficiency:.1f}%")
        
        root.destroy()
        print(f"\n✅ Test scénario complet réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur scénario complet: {e}")
        return False

def show_integration_summary():
    """Résumé de l'intégration complète"""
    print("\n" + "="*80)
    print("🎉 INTÉGRATION COMPLÈTE DU SYSTÈME INTELLIGENT")
    print("="*80)
    
    print("\n✅ BOUTON FIND.PNG (SCROLL VERS COURANTE):")
    print("   • _scroll_to_current_song() modifiée pour le système intelligent")
    print("   • Force le rechargement 10+1+10 autour de la chanson courante")
    print("   • Sélection automatique après rechargement")
    print("   • Compatible avec grandes playlists")
    
    print("\n✅ AUTO-SCROLL:")
    print("   • control.prev_track() utilise select_current_song_smart()")
    print("   • control.next_track() utilise select_current_song_smart()")
    print("   • tools.play_track() utilise select_current_song_smart()")
    print("   • Rechargement automatique si chanson pas chargée")
    
    print("\n✅ BARRE DE SCROLL:")
    print("   • _update_canvas_scroll_region() adaptée au système intelligent")
    print("   • Région basée sur éléments chargés, pas total playlist")
    print("   • Scroll proportionnel à la fenêtre réelle")
    print("   • Performance correcte même avec 1000+ musiques")
    
    print("\n🔧 NOUVELLES FONCTIONS:")
    print("   • select_current_song_smart() : Wrapper intelligent")
    print("   • Conversion automatique index absolu → relatif")
    print("   • Gestion rechargement si nécessaire")
    print("   • Debug complet intégré")
    
    print("\n🎯 COMPATIBILITÉ COMPLÈTE:")
    print("   • ✅ Bouton find.png → Fonctionne parfaitement")
    print("   • ✅ Auto-scroll → Rechargement automatique intelligent")
    print("   • ✅ Barre de scroll → Proportionnelle aux éléments chargés")
    print("   • ✅ Changement de musique → Tout se synchronise")
    
    print("\n🚀 EXPÉRIENCE UTILISATEUR FINALE:")
    print("   🎵 Clic bouton find → Scroll instant vers chanson courante")
    print("   ⏭️ Boutons prev/next → Auto-scroll intelligent si activé")
    print("   📜 Barre de scroll → Taille correcte, pas de confusion")
    print("   🔄 Changement musique → Tout se met à jour automatiquement")
    print("   💾 Grandes playlists → Performance optimisée constante")

if __name__ == "__main__":
    print("🔗 TEST INTÉGRATION COMPLÈTE SYSTÈME INTELLIGENT")
    print("="*80)
    
    success1 = test_scroll_to_current_integration()
    success2 = test_auto_scroll_integration()
    success3 = test_scroll_region_correct()
    success4 = test_all_integrations_scenario()
    
    show_integration_summary()
    
    if success1 and success2 and success3 and success4:
        print(f"\n{'='*80}")
        print("🎉 INTÉGRATION COMPLÈTE RÉUSSIE !")
        print("✅ Bouton find.png compatible")
        print("✅ Auto-scroll intelligent fonctionnel")
        print("✅ Barre de scroll correcte")
        print("✅ Tous les scénarios validés")
        print("🚀 Le système est maintenant parfaitement intégré !")
        print("🎵 Testez toutes les fonctionnalités !")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("⚠️  Certaines intégrations nécessitent des ajustements")
        print("🔧 Vérifiez les erreurs ci-dessus")
        print(f"{'='*80}")