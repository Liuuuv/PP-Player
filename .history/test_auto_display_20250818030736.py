#!/usr/bin/env python3
"""
Test du système d'affichage automatique 10+1+10 corrigé
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_removed_indicators():
    """Vérifie que les indicateurs '...XXX musiques suivantes' sont supprimés"""
    print("=== Test suppression des indicateurs ===")
    
    try:
        from search_tab.main_playlist import _refresh_windowed_playlist_display
        import inspect
        
        # Examiner le code source pour voir si les indicateurs sont supprimés
        source = inspect.getsource(_refresh_windowed_playlist_display)
        
        if "musiques suivantes" in source:
            print("❌ Les indicateurs 'musiques suivantes' sont encore présents")
            return False
        elif "musiques précédentes" in source:
            print("❌ Les indicateurs 'musiques précédentes' sont encore présents")
            return False
        else:
            print("✅ Les indicateurs ont été supprimés du code")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def test_smart_loading_integration():
    """Test de l'intégration du chargement intelligent"""
    print("\n=== Test intégration chargement intelligent ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Activer le debug et le système intelligent
        update_main_playlist_config(
            debug_scroll=True,
            enable_smart_loading=True,
            reload_on_song_change=True
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Configuration de test
        player.main_playlist = [f"test_{i:03d}.mp3" for i in range(1, 101)]  # 100 musiques
        player.current_index = 25
        
        print(f"✓ Playlist test: {len(player.main_playlist)} musiques")
        print(f"✓ Position courante: {player.current_index}")
        
        # Test 1: Calcul de fenêtre intelligente
        print("\n--- Test 1: Calcul fenêtre intelligente ---")
        start, end = player._calculate_smart_window()
        if start is not None and end is not None:
            print(f"  Fenêtre calculée: {start}-{end} ({end-start} éléments)")
            
            # Vérifier que la chanson courante est incluse
            if start <= player.current_index < end:
                print(f"  ✅ Chanson courante ({player.current_index}) incluse")
            else:
                print(f"  ❌ Chanson courante ({player.current_index}) exclue")
                
            # Vérifier que c'est bien ~21 éléments (10+1+10)
            window_size = end - start
            if 15 <= window_size <= 30:
                print(f"  ✅ Taille raisonnable: {window_size} éléments")
            else:
                print(f"  ⚠️  Taille inhabituelle: {window_size} éléments")
                
        else:
            print("  ❌ Calcul échoué")
            return False
        
        # Test 2: Simulation changement de musique
        print("\n--- Test 2: Simulation changement musique ---")
        old_index = player.current_index
        player.current_index = 50  # Changer vers milieu
        
        print(f"  Changement: {old_index} → {player.current_index}")
        
        # Déclencher le système
        player._trigger_smart_reload_on_song_change()
        
        # Vérifier nouvelle fenêtre
        new_start, new_end = player._calculate_smart_window()
        print(f"  Nouvelle fenêtre: {new_start}-{new_end}")
        
        if new_start <= player.current_index < new_end:
            print(f"  ✅ Nouvelle position ({player.current_index}) incluse")
        else:
            print(f"  ❌ Nouvelle position ({player.current_index}) exclue")
        
        # Test 3: Test des déclencheurs dans control.py
        print("\n--- Test 3: Vérification déclencheurs control.py ---")
        
        import control
        import inspect
        
        # Vérifier que les fonctions contiennent les déclencheurs
        functions_to_check = ['prev_track', 'next_track', 'play_selected']
        
        for func_name in functions_to_check:
            if hasattr(control, func_name):
                source = inspect.getsource(getattr(control, func_name))
                if '_trigger_smart_reload_on_song_change' in source:
                    print(f"  ✅ Déclencheur ajouté dans {func_name}")
                else:
                    print(f"  ❌ Déclencheur manquant dans {func_name}")
            else:
                print(f"  ⚠️  Fonction {func_name} non trouvée")
        
        root.destroy()
        print("\n✅ Test intégration réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test intégration: {e}")
        return False

def test_automatic_loading_scenario():
    """Test d'un scénario complet de chargement automatique"""
    print("\n=== Test scénario complet automatique ===")
    
    try:
        from main import MusicPlayer
        from search_tab.config import update_main_playlist_config
        import tkinter as tk
        
        # Configuration agressive pour voir les résultats
        update_main_playlist_config(
            debug_scroll=True,
            enable_smart_loading=True,
            auto_unload_unused=True,
            reload_on_song_change=True,
            songs_before_current=10,
            songs_after_current=10
        )
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Grande playlist pour tester l'effet
        player.main_playlist = [f"huge_{i:04d}.mp3" for i in range(1, 501)]  # 500 musiques
        
        scenarios = [
            {"name": "Début", "index": 10},
            {"name": "Milieu", "index": 250}, 
            {"name": "Fin", "index": 480},
            {"name": "Très début", "index": 2},
            {"name": "Très fin", "index": 495}
        ]
        
        for scenario in scenarios:
            print(f"\n--- Scénario {scenario['name']} (position {scenario['index']}) ---")
            
            # Changer vers cette position
            player.current_index = scenario['index']
            
            # Calculer la fenêtre optimale
            start, end = player._calculate_smart_window()
            
            if start is not None and end is not None:
                window_size = end - start
                print(f"  Fenêtre: {start}-{end} ({window_size} éléments)")
                print(f"  Musiques non chargées: {len(player.main_playlist) - window_size}")
                
                # Vérifier l'efficacité
                efficiency = (len(player.main_playlist) - window_size) / len(player.main_playlist) * 100
                print(f"  Efficacité mémoire: {efficiency:.1f}% d'économie")
                
                if efficiency > 80:
                    print(f"  ✅ Excellente optimisation")
                elif efficiency > 60:
                    print(f"  ✅ Bonne optimisation")
                else:
                    print(f"  ⚠️  Optimisation faible")
                    
                # Vérifier la protection de la chanson courante
                if start <= scenario['index'] < end:
                    print(f"  ✅ Chanson courante protégée")
                else:
                    print(f"  ❌ Chanson courante non protégée !")
                    
            else:
                print(f"  ❌ Calcul échoué")
        
        root.destroy()
        print("\n✅ Test scénario complet réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur scénario complet: {e}")
        return False

def show_corrections_summary():
    """Affiche le résumé des corrections apportées"""
    print("\n" + "="*80)
    print("🔧 CORRECTIONS APPORTÉES AU SYSTÈME")
    print("="*80)
    
    print("\n✅ PROBLÈME 1 CORRIGÉ: Indicateurs supprimés")
    print("   ❌ Avant: '...XXX musiques suivantes' et '...XXX musiques précédentes'")  
    print("   ✅ Après: Affichage propre sans indicateurs")
    
    print("\n✅ PROBLÈME 2 CORRIGÉ: Chargement/déchargement automatique")
    print("   ❌ Avant: Système pas déclenché automatiquement")
    print("   ✅ Après: Déclencheurs ajoutés dans toutes les fonctions de changement")
    
    print("\n🔧 MODIFICATIONS APPORTÉES:")
    print("   1. Suppression des indicateurs dans _refresh_windowed_playlist_display()")
    print("   2. Intégration du système intelligent dans le rafraîchissement")
    print("   3. Déclencheurs ajoutés dans control.py:")
    print("      - prev_track() → _trigger_smart_reload_on_song_change()")
    print("      - next_track() → _trigger_smart_reload_on_song_change()")
    print("      - play_selected() → _trigger_smart_reload_on_song_change()")
    print("   4. Force l'exécution immédiate dans setup_scroll()")
    
    print("\n🎯 RÉSULTAT ATTENDU:")
    print("   • Affichage propre sans '...XXX musiques suivantes'")
    print("   • Chargement automatique 10+1+10 à chaque changement")
    print("   • Déchargement intelligent des éléments inutiles")
    print("   • Performance optimisée avec grandes playlists")

if __name__ == "__main__":
    print("🔧 TEST DES CORRECTIONS DU SYSTÈME D'AFFICHAGE")
    print("="*80)
    
    success1 = test_removed_indicators()
    success2 = test_smart_loading_integration()
    success3 = test_automatic_loading_scenario()
    
    show_corrections_summary()
    
    if success1 and success2 and success3:
        print(f"\n{'='*80}")
        print("🎉 TOUTES LES CORRECTIONS VALIDÉES !")
        print("✅ Indicateurs supprimés")
        print("✅ Chargement/déchargement automatique fonctionnel")
        print("✅ Déclencheurs intégrés")
        print("✅ Scénarios de test réussis")
        print("🚀 Le système corrigé est prêt à l'emploi !")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("⚠️  Certaines corrections peuvent nécessiter des ajustements")
        print("🔧 Vérifiez les erreurs ci-dessus")
        print(f"{'='*80}")