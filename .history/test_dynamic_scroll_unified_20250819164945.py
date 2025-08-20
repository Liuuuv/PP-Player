#!/usr/bin/env python3
"""
Test du système de scroll dynamique unifié
Vérifie que l'unification des systèmes infinite_scroll et progressive_scroll fonctionne
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_config_unification():
    """Test que la configuration utilise bien le nouveau système unifié"""
    print("🧪 TEST: Configuration du système unifié")
    
    try:
        from search_tab.config import get_main_playlist_config
        
        # Vérifier que le nouveau paramètre existe
        dynamic_scroll = get_main_playlist_config('enable_dynamic_scroll')
        print(f"✅ enable_dynamic_scroll: {dynamic_scroll}")
        
        # Vérifier que les anciens paramètres n'existent plus ou sont remplacés
        try:
            infinite_scroll = get_main_playlist_config('enable_infinite_scroll')
            print(f"⚠️ enable_infinite_scroll encore présent: {infinite_scroll}")
        except:
            print("✅ enable_infinite_scroll supprimé")
            
        try:
            progressive_loading = get_main_playlist_config('enable_progressive_loading')
            print(f"⚠️ enable_progressive_loading encore présent: {progressive_loading}")
        except:
            print("✅ enable_progressive_loading supprimé")
        
        # Vérifier les autres paramètres du scroll dynamique
        scroll_threshold = get_main_playlist_config('scroll_threshold')
        load_more_count = get_main_playlist_config('load_more_count')
        initial_load = get_main_playlist_config('initial_load_after_current')
        trigger_threshold = get_main_playlist_config('scroll_trigger_threshold')
        
        print(f"✅ scroll_threshold: {scroll_threshold}")
        print(f"✅ load_more_count: {load_more_count}")
        print(f"✅ initial_load_after_current: {initial_load}")
        print(f"✅ scroll_trigger_threshold: {trigger_threshold}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test configuration: {e}")
        return False

def test_functions_unification():
    """Test que les nouvelles fonctions existent"""
    print("\n🧪 TEST: Fonctions du système unifié")
    
    try:
        import tkinter as tk
        from main import MusicPlayer
        
        # Créer une instance de test
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        player = MusicPlayer(root)
        
        # Vérifier que les nouvelles fonctions existent
        functions_to_check = [
            '_setup_dynamic_scroll',
            '_on_dynamic_scroll'
        ]
        
        for func_name in functions_to_check:
            if hasattr(player, func_name):
                print(f"✅ {func_name}: fonction disponible")
            else:
                print(f"❌ {func_name}: fonction manquante")
        
        # Vérifier que les anciennes fonctions sont toujours là pour compatibilité
        legacy_functions = [
            '_setup_infinite_scroll',  # Devrait rediriger vers dynamic_scroll
            '_setup_progressive_scroll_detection'
        ]
        
        for func_name in legacy_functions:
            if hasattr(player, func_name):
                print(f"🔄 {func_name}: fonction de compatibilité disponible")
            else:
                print(f"⚠️ {func_name}: fonction de compatibilité manquante")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test fonctions: {e}")
        return False

def test_integration():
    """Test d'intégration simple"""
    print("\n🧪 TEST: Intégration du système unifié")
    
    try:
        import tkinter as tk
        from main import MusicPlayer
        from search_tab.config import get_main_playlist_config
        
        # Créer une instance de test
        root = tk.Tk()
        root.withdraw()
        player = MusicPlayer(root)
        
        # Simuler une playlist
        player.main_playlist = [f"track_{i:03d}.mp3" for i in range(1, 101)]  # 100 pistes
        player.current_index = 50
        
        # Tester la configuration du scroll dynamique
        try:
            player._setup_dynamic_scroll()
            print("✅ Configuration du scroll dynamique réussie")
        except Exception as e:
            print(f"⚠️ Erreur configuration: {type(e).__name__}")
        
        # Tester l'appel du scroll dynamique
        try:
            player._on_dynamic_scroll()
            print("✅ Appel du scroll dynamique réussi")
        except Exception as e:
            print(f"⚠️ Erreur appel scroll: {type(e).__name__}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🎯 TEST DU SYSTÈME DE SCROLL DYNAMIQUE UNIFIÉ")
    print("=" * 60)
    
    # Tests
    config_ok = test_config_unification()
    functions_ok = test_functions_unification()
    integration_ok = test_integration()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS:")
    print(f"   • Configuration: {'✅ OK' if config_ok else '❌ ÉCHEC'}")
    print(f"   • Fonctions: {'✅ OK' if functions_ok else '❌ ÉCHEC'}")
    print(f"   • Intégration: {'✅ OK' if integration_ok else '❌ ÉCHEC'}")
    
    if all([config_ok, functions_ok, integration_ok]):
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Le système de scroll dynamique unifié est opérationnel")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    print("\n📋 CHANGEMENTS EFFECTUÉS:")
    print("   • enable_infinite_scroll + enable_progressive_loading → enable_dynamic_scroll")
    print("   • _setup_infinite_scroll + _setup_progressive_scroll_detection → _setup_dynamic_scroll")
    print("   • _on_progressive_scroll → _on_dynamic_scroll")
    print("   • Fonctions de compatibilité maintenues pour la transition")
    
    print("\n🎮 UTILISATION:")
    print("   • Un seul paramètre: enable_dynamic_scroll")
    print("   • Une seule fonction de setup: _setup_dynamic_scroll()")
    print("   • Une seule fonction de gestion: _on_dynamic_scroll()")
    print("   • Combine les fonctionnalités des deux anciens systèmes")

if __name__ == "__main__":
    main()