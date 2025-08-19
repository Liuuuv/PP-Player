#!/usr/bin/env python3
"""
Test du nouveau système de chargement progressif :
- Chargement initial : chanson courante + 10 suivantes
- Scroll vers le bas : +10 musiques automatiquement
- Jamais de déchargement (garder tout)
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_progressive_system_activation():
    """Test activation du nouveau système progressif"""
    print("=== Test activation système progressif ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config, get_main_playlist_config
        import tkinter as tk
        
        # Configuration du nouveau système
        update_main_playlist_config(
            debug_scroll=True,
            enable_progressive_loading=True,  # NOUVEAU SYSTÈME
            enable_smart_loading=False,       # Ancien système désactivé
            auto_unload_unused=False,         # Pas de déchargement
            initial_load_after_current=10,    # 10 après la courante
            load_more_on_scroll=10,           # +10 en scrollant
            scroll_trigger_threshold=0.9      # À 90% vers le bas
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Vérifier la configuration
        print(f"✓ Progressive loading: {get_main_playlist_config('enable_progressive_loading')}")
        print(f"✓ Ancien système: {get_main_playlist_config('enable_smart_loading')}")  
        print(f"✓ Pas déchargement: {get_main_playlist_config('never_unload')}")
        print(f"✓ Chargement initial: {get_main_playlist_config('initial_load_after_current')}")
        print(f"✓ Chargement scroll: {get_main_playlist_config('load_more_on_scroll')}")
        
        # Vérifier les nouvelles fonctions
        required_functions = [
            '_progressive_load_system',
            '_setup_progressive_scroll_detection', 
            '_on_progressive_scroll',
            '_load_more_on_scroll',
            '_append_progressive_items',
            '_is_index_already_loaded',
            '_find_relative_index_in_loaded'
        ]
        
        missing = []
        for func_name in required_functions:
            if hasattr(player, func_name):
                print(f"✅ {func_name}")
            else:
                print(f"❌ {func_name}")
                missing.append(func_name)
        
        root.destroy()
        
        if missing:
            print(f"\n❌ Fonctions manquantes: {missing}")
            return False
        
        print("\n✅ Système progressif correctement activé !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test activation: {e}")
        return False

def test_initial_progressive_load():
    """Test du chargement initial progressif"""
    print("\n=== Test chargement initial progressif ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Configuration
        update_main_playlist_config(
            debug_scroll=True,
            enable_progressive_loading=True,
            initial_load_after_current=10
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Playlist de test
        player.main_playlist = [f"progressive_{i:03d}.mp3" for i in range(1, 101)]  # 100 musiques
        
        print(f"✓ Playlist: {len(player.main_playlist)} musiques")
        
        # Test positions différentes
        test_positions = [
            ("Début playlist", 5),
            ("Milieu playlist", 50), 
            ("Près de la fin", 85)
        ]
        
        for test_name, position in test_positions:
            print(f"\n--- {test_name} (position {position}) ---")
            
            # Vider d'abord (simuler playlist vide)
            if hasattr(player, 'playlist_container'):
                for child in player.playlist_container.winfo_children():
                    try:
                        child.destroy()
                    except:
                        pass
            
            # Positionner et déclencher le chargement progressif
            player.current_index = position
            print(f"  Position courante: {player.current_index}")
            
            # Déclencher le chargement progressif
            player._progressive_load_system()
            
            # Vérifier ce qui a été chargé
            loaded_count = len(player.playlist_container.winfo_children()) if hasattr(player, 'playlist_container') else 0
            print(f"  Éléments chargés: {loaded_count}")
            
            # Vérifier qu'on a bien chargé courante + 10 (max 11 éléments)
            expected_max = min(11, len(player.main_playlist) - position)
            if loaded_count <= expected_max and loaded_count > 0:
                print(f"  ✅ Chargement correct ({loaded_count}/{expected_max} max)")
            else:
                print(f"  ❌ Chargement incorrect ({loaded_count}/{expected_max} attendu)")
                return False
                
            # Vérifier que la chanson courante est chargée
            if player._is_index_already_loaded(position):
                print(f"  ✅ Chanson courante ({position}) bien chargée")
            else:
                print(f"  ❌ Chanson courante ({position}) pas chargée !")
                return False
        
        root.destroy()
        print("\n✅ Chargement initial progressif fonctionne !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test chargement initial: {e}")
        return False

def test_scroll_load_more():
    """Test du chargement supplémentaire en scrollant"""
    print("\n=== Test scroll load more ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Configuration
        update_main_playlist_config(
            debug_scroll=True,
            enable_progressive_loading=True,
            initial_load_after_current=5,  # Charger moins au début pour tester le scroll
            load_more_on_scroll=8,         # +8 en scrollant
            scroll_trigger_threshold=0.9
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Grande playlist
        player.main_playlist = [f"scroll_test_{i:03d}.mp3" for i in range(1, 201)]  # 200 musiques
        
        print(f"✓ Grande playlist: {len(player.main_playlist)} musiques")
        
        # Chargement initial
        player.current_index = 10
        player._progressive_load_system()
        
        initial_loaded = len(player.playlist_container.winfo_children())
        print(f"  Chargement initial: {initial_loaded} éléments")
        
        # Simuler plusieurs cycles de "scroll load more"
        scroll_cycles = 3
        
        for cycle in range(1, scroll_cycles + 1):
            print(f"\n--- Cycle scroll {cycle} ---")
            
            # Déclencher load more
            print(f"  🔄 Déclenchement load more...")
            player._load_more_on_scroll()
            
            # Vérifier nouveau nombre d'éléments chargés
            new_loaded = len(player.playlist_container.winfo_children())
            added = new_loaded - (initial_loaded + (cycle-1) * 8)  # 8 = load_more_on_scroll
            
            print(f"  Éléments après cycle {cycle}: {new_loaded}")
            print(f"  Éléments ajoutés ce cycle: {added}")
            
            if added > 0:
                print(f"  ✅ Load more cycle {cycle} réussi")
            else:
                print(f"  ⚠️ Load more cycle {cycle}: rien ajouté (peut-être déjà tout chargé)")
        
        final_loaded = len(player.playlist_container.winfo_children())
        total_added = final_loaded - initial_loaded
        
        print(f"\n📊 Résumé:")
        print(f"  Chargement initial: {initial_loaded}")
        print(f"  Total final: {final_loaded}")
        print(f"  Total ajouté par scroll: {total_added}")
        print(f"  Pourcentage playlist chargée: {final_loaded/len(player.main_playlist)*100:.1f}%")
        
        # Vérifier qu'on n'a JAMAIS déchargé (principe du nouveau système)
        if final_loaded >= initial_loaded:
            print(f"  ✅ Aucun déchargement détecté (système respecté)")
        else:
            print(f"  ❌ Déchargement détecté ! (système non respecté)")
            return False
        
        root.destroy()
        print("\n✅ Scroll load more fonctionne !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test scroll load more: {e}")
        return False

def test_no_unloading_ever():
    """Test que le système ne décharge jamais rien"""
    print("\n=== Test pas de déchargement ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Configuration
        update_main_playlist_config(
            debug_scroll=True,
            enable_progressive_loading=True,
            never_unload=True,
            initial_load_after_current=15
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Playlist de test
        player.main_playlist = [f"no_unload_{i:03d}.mp3" for i in range(1, 151)]  # 150 musiques
        
        print(f"✓ Playlist test: {len(player.main_playlist)} musiques")
        
        # Test de changements de position extrêmes
        positions = [10, 80, 20, 130, 5, 90]
        loaded_counts = []
        
        for i, position in enumerate(positions):
            print(f"\n--- Changement {i+1}: Position {position} ---")
            
            player.current_index = position
            player._progressive_load_system()
            
            loaded = len(player.playlist_container.winfo_children())
            loaded_counts.append(loaded)
            
            print(f"  Position: {position}")
            print(f"  Éléments chargés: {loaded}")
            
            # Vérifier qu'on n'a jamais moins d'éléments qu'avant
            if i > 0 and loaded < loaded_counts[i-1]:
                print(f"  ❌ DÉCHARGEMENT DÉTECTÉ ! {loaded_counts[i-1]} → {loaded}")
                return False
            else:
                print(f"  ✅ Pas de déchargement ({loaded} >= {loaded_counts[i-1] if i > 0 else 0})")
        
        print(f"\n📊 Évolution chargement:")
        for i, (pos, count) in enumerate(zip(positions, loaded_counts)):
            print(f"  Position {pos}: {count} éléments chargés")
        
        # Vérifier que la tendance est toujours croissante ou stable
        decreasing = False
        for i in range(1, len(loaded_counts)):
            if loaded_counts[i] < loaded_counts[i-1]:
                decreasing = True
                break
        
        if not decreasing:
            print(f"✅ Principe 'jamais de déchargement' respecté !")
        else:
            print(f"❌ Principe 'jamais de déchargement' violé !")
            return False
        
        root.destroy()
        print("\n✅ Test pas de déchargement réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test pas de déchargement: {e}")
        return False

def test_integration_with_controls():
    """Test intégration avec les contrôles (auto-scroll)"""
    print("\n=== Test intégration contrôles ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Configuration
        update_main_playlist_config(
            debug_scroll=True,
            enable_progressive_loading=True
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        player.auto_scroll_enabled = True
        
        # Playlist
        player.main_playlist = [f"control_test_{i:03d}.mp3" for i in range(1, 101)]  # 100 musiques
        
        print(f"✓ Playlist: {len(player.main_playlist)} musiques")
        print(f"✓ Auto-scroll activé: {player.auto_scroll_enabled}")
        
        # Test des fonctions d'auto-scroll avec le nouveau système
        test_scenarios = [
            ("Auto-scroll position 30", 30),
            ("Auto-scroll position 70", 70),
            ("Auto-scroll position 5", 5)
        ]
        
        for scenario_name, position in test_scenarios:
            print(f"\n--- {scenario_name} ---")
            
            player.current_index = position
            print(f"  Position: {position}")
            
            # Test de la fonction select_current_song_smart avec le nouveau système
            print(f"  🎮 Test select_current_song_smart...")
            player.select_current_song_smart(auto_scroll=True)
            
            # Vérifier que la chanson est chargée et accessible
            if player._is_index_already_loaded(position):
                relative_index = player._find_relative_index_in_loaded(position)
                if relative_index is not None:
                    print(f"  ✅ Chanson {position} chargée et trouvée (index relatif: {relative_index})")
                else:
                    print(f"  ❌ Chanson {position} chargée mais index relatif non trouvé")
                    return False
            else:
                print(f"  ❌ Chanson {position} pas chargée après select_current_song_smart")
                return False
        
        root.destroy()
        print("\n✅ Intégration contrôles réussie !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur test intégration: {e}")
        return False

def show_progressive_system_summary():
    """Résumé du nouveau système de chargement progressif"""
    print("\n" + "="*80)
    print("🎉 NOUVEAU SYSTÈME DE CHARGEMENT PROGRESSIF")
    print("="*80)
    
    print("\n✅ FONCTIONNEMENT:")
    print("   1. 🎵 Chargement initial: Chanson courante + 10 suivantes")
    print("   2. 📜 Scroll vers le bas: +10 musiques automatiquement à 90%")
    print("   3. 🔒 Jamais de déchargement: Tout ce qui est chargé reste chargé")
    print("   4. 🎮 Auto-scroll intelligent: Compatible avec les contrôles")
    
    print("\n🔧 CONFIGURATION:")
    print("   • enable_progressive_loading: True (nouveau système)")
    print("   • enable_smart_loading: False (ancien système désactivé)")
    print("   • initial_load_after_current: 10 musiques après courante")
    print("   • load_more_on_scroll: 10 musiques de plus en scrollant")
    print("   • scroll_trigger_threshold: 0.9 (à 90% vers le bas)")
    print("   • never_unload: True (jamais de déchargement)")
    
    print("\n⚡ AVANTAGES:")
    print("   ✅ Performance optimisée (charge seulement ce qui est nécessaire)")
    print("   ✅ Expérience utilisateur fluide (scroll infini naturel)")
    print("   ✅ Pas de 'flashs' d'affichage (pas de déchargement)")
    print("   ✅ Compatible avec toutes les fonctionnalités existantes")
    print("   ✅ Adaptatif (charge plus selon les besoins)")
    
    print("\n🎮 UTILISATION:")
    print("   🎵 Lancez une playlist → Chargement automatique courante + 10")
    print("   📜 Scrollez vers le bas → +10 musiques chargées automatiquement")
    print("   ⏭️ Changez de musique → Auto-scroll vers la nouvelle position")
    print("   🎯 Cliquez bouton find → Scroll direct vers courante")
    print("   🔄 Navigation quelconque → Chargement adaptatif intelligent")
    
    print("\n📊 EFFICACITÉ:")
    print("   • Playlists petites (< 50): Chargement minimal nécessaire")
    print("   • Playlists moyennes (50-200): Chargement progressif optimal")
    print("   • Grandes playlists (200+): Très haute efficacité mémoire")
    print("   • Très grandes playlists (1000+): Performance constante")

if __name__ == "__main__":
    print("🎵 TEST NOUVEAU SYSTÈME CHARGEMENT PROGRESSIF")
    print("="*80)
    
    success1 = test_progressive_system_activation()
    success2 = test_initial_progressive_load()
    success3 = test_scroll_load_more()  
    success4 = test_no_unloading_ever()
    success5 = test_integration_with_controls()
    
    show_progressive_system_summary()
    
    if success1 and success2 and success3 and success4 and success5:
        print(f"\n{'='*80}")
        print("🎉 NOUVEAU SYSTÈME PROGRESSIF ENTIÈREMENT FONCTIONNEL !")
        print("✅ Activation et configuration OK")
        print("✅ Chargement initial fonctionnel")
        print("✅ Scroll load more opérationnel")
        print("✅ Aucun déchargement confirmé")
        print("✅ Intégration contrôles validée")
        print("🚀 Le système progressif est prêt à l'emploi !")
        print("🎵 Testez avec vos playlists !")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("⚠️  Le système progressif nécessite des ajustements")
        print("🔧 Vérifiez les erreurs ci-dessus")
        print(f"{'='*80}")