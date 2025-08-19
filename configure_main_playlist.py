#!/usr/bin/env python3
"""
Script de configuration pour la main playlist
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def show_current_config():
    """Affiche la configuration actuelle"""
    try:
        from search_tab.config import MAIN_PLAYLIST_CONFIG, get_main_playlist_config
        
        print("📋 CONFIGURATION ACTUELLE DE LA MAIN PLAYLIST")
        print("="*60)
        
        print("\n🎯 SEUILS D'OPTIMISATION:")
        print(f"  Seuil fenêtrage: {get_main_playlist_config('windowing_threshold')} musiques")
        print(f"  Petites playlists: ≤ {get_main_playlist_config('small_playlist_threshold')} musiques")
        print(f"  Grandes playlists: ≥ {get_main_playlist_config('large_playlist_threshold')} musiques")
        
        print("\n🪟 PARAMÈTRES DE FENÊTRAGE:")
        print(f"  Taille fenêtre standard: {get_main_playlist_config('window_size')}")
        print(f"  Taille fenêtre petite: {get_main_playlist_config('window_size_small')}")
        print(f"  Taille fenêtre moyenne: {get_main_playlist_config('window_size_medium')}")
        print(f"  Taille fenêtre grande: {get_main_playlist_config('window_size_large')}")
        
        print("\n⚡ PARAMÈTRES DE PERFORMANCE:")
        print(f"  Optimisations activées: {get_main_playlist_config('enable_optimizations')}")
        print(f"  Rafraîchissement asynchrone: {get_main_playlist_config('enable_async_refresh')}")
        print(f"  Préchargement activé: {get_main_playlist_config('enable_preloading')}")
        print(f"  Taille préchargement: {get_main_playlist_config('preload_size')}")
        
        print("\n🎮 PARAMÈTRES DE NAVIGATION:")
        print(f"  Taille de saut: {get_main_playlist_config('jump_size')}")
        print(f"  Indicateurs navigation: {get_main_playlist_config('show_navigation_indicators')}")
        
        print("\n🖱️  PARAMÈTRES DE SCROLL:")
        print(f"  Hauteur estimée par élément: {get_main_playlist_config('item_height_estimate')}px")
        print(f"  Délai mise à jour scroll: {get_main_playlist_config('scroll_update_delay')}ms")
        print(f"  Forcer mise à jour scroll: {get_main_playlist_config('force_scroll_update')}")
        
        print("\n🎨 MODE D'AFFICHAGE:")
        print(f"  Mode actuel: {get_main_playlist_config('default_display_mode')}")
        modes = get_main_playlist_config('display_modes')
        for key, desc in modes.items():
            print(f"    {key}: {desc}")
        
        print("\n🐛 DEBUG:")
        print(f"  Debug fenêtrage: {get_main_playlist_config('debug_windowing')}")
        print(f"  Debug scroll: {get_main_playlist_config('debug_scroll')}")
        print(f"  Debug performance: {get_main_playlist_config('debug_performance')}")
        
    except ImportError:
        print("❌ Configuration non disponible (fichier config.py non trouvé)")

def configure_thresholds():
    """Configure les seuils d'optimisation"""
    try:
        from search_tab.config import update_main_playlist_config, get_main_playlist_config
        
        print("\n🎯 CONFIGURATION DES SEUILS")
        print("="*40)
        
        current = get_main_playlist_config('windowing_threshold')
        print(f"Seuil de fenêtrage actuel: {current}")
        new_threshold = input("Nouveau seuil (ou Entrée pour garder): ").strip()
        if new_threshold and new_threshold.isdigit():
            update_main_playlist_config(windowing_threshold=int(new_threshold))
            print(f"✅ Seuil mis à jour: {new_threshold}")
        
        current = get_main_playlist_config('small_playlist_threshold')
        print(f"Seuil petites playlists actuel: {current}")
        new_small = input("Nouveau seuil petites playlists (ou Entrée pour garder): ").strip()
        if new_small and new_small.isdigit():
            update_main_playlist_config(small_playlist_threshold=int(new_small))
            print(f"✅ Seuil petites playlists mis à jour: {new_small}")
        
        current = get_main_playlist_config('large_playlist_threshold')
        print(f"Seuil grandes playlists actuel: {current}")
        new_large = input("Nouveau seuil grandes playlists (ou Entrée pour garder): ").strip()
        if new_large and new_large.isdigit():
            update_main_playlist_config(large_playlist_threshold=int(new_large))
            print(f"✅ Seuil grandes playlists mis à jour: {new_large}")
            
    except ImportError:
        print("❌ Configuration non disponible")

def configure_window_sizes():
    """Configure les tailles de fenêtre"""
    try:
        from search_tab.config import update_main_playlist_config, get_main_playlist_config
        
        print("\n🪟 CONFIGURATION DES TAILLES DE FENÊTRE")
        print("="*45)
        
        sizes = ['window_size', 'window_size_small', 'window_size_medium', 'window_size_large']
        names = ['Standard', 'Petite', 'Moyenne', 'Grande']
        
        for size_key, name in zip(sizes, names):
            current = get_main_playlist_config(size_key)
            print(f"Taille fenêtre {name.lower()} actuelle: {current}")
            new_size = input(f"Nouvelle taille {name.lower()} (ou Entrée pour garder): ").strip()
            if new_size and new_size.isdigit():
                update_main_playlist_config(**{size_key: int(new_size)})
                print(f"✅ Taille {name.lower()} mise à jour: {new_size}")
                
    except ImportError:
        print("❌ Configuration non disponible")

def configure_display_mode():
    """Configure le mode d'affichage"""
    try:
        from search_tab.config import update_main_playlist_config, get_main_playlist_config
        
        print("\n🎨 CONFIGURATION DU MODE D'AFFICHAGE")
        print("="*40)
        
        modes = get_main_playlist_config('display_modes')
        current = get_main_playlist_config('default_display_mode')
        
        print(f"Mode actuel: {current}")
        print("\nModes disponibles:")
        for i, (key, desc) in enumerate(modes.items(), 1):
            print(f"  {i}. {key}: {desc}")
        
        choice = input("\nChoisir un mode (1-4, ou Entrée pour garder): ").strip()
        if choice and choice.isdigit():
            choice_idx = int(choice) - 1
            mode_keys = list(modes.keys())
            if 0 <= choice_idx < len(mode_keys):
                new_mode = mode_keys[choice_idx]
                update_main_playlist_config(default_display_mode=new_mode)
                print(f"✅ Mode d'affichage mis à jour: {new_mode}")
            else:
                print("❌ Choix invalide")
                
    except ImportError:
        print("❌ Configuration non disponible")

def toggle_optimizations():
    """Active/désactive les optimisations"""
    try:
        from search_tab.config import update_main_playlist_config, get_main_playlist_config
        
        print("\n⚡ CONFIGURATION DES OPTIMISATIONS")
        print("="*40)
        
        optimizations = [
            ('enable_optimizations', 'Optimisations générales'),
            ('enable_async_refresh', 'Rafraîchissement asynchrone'),
            ('enable_preloading', 'Préchargement des métadonnées'),
            ('show_navigation_indicators', 'Indicateurs de navigation'),
            ('force_scroll_update', 'Forcer mise à jour scroll')
        ]
        
        for key, name in optimizations:
            current = get_main_playlist_config(key)
            print(f"{name}: {'✅ Activé' if current else '❌ Désactivé'}")
            toggle = input(f"Basculer {name.lower()}? (o/n): ").strip().lower()
            if toggle == 'o':
                update_main_playlist_config(**{key: not current})
                new_state = "✅ Activé" if not current else "❌ Désactivé"
                print(f"✅ {name}: {new_state}")
                
    except ImportError:
        print("❌ Configuration non disponible")

def enable_debug():
    """Active/désactive le debug"""
    try:
        from search_tab.config import update_main_playlist_config, get_main_playlist_config
        
        print("\n🐛 CONFIGURATION DU DEBUG")
        print("="*30)
        
        debug_options = [
            ('debug_windowing', 'Debug fenêtrage'),
            ('debug_scroll', 'Debug scroll'),
            ('debug_performance', 'Debug performance')
        ]
        
        for key, name in debug_options:
            current = get_main_playlist_config(key)
            print(f"{name}: {'✅ Activé' if current else '❌ Désactivé'}")
            toggle = input(f"Basculer {name.lower()}? (o/n): ").strip().lower()
            if toggle == 'o':
                update_main_playlist_config(**{key: not current})
                new_state = "✅ Activé" if not current else "❌ Désactivé"
                print(f"✅ {name}: {new_state}")
                
    except ImportError:
        print("❌ Configuration non disponible")

def test_configuration():
    """Teste la configuration avec différentes tailles de playlist"""
    try:
        from search_tab.config import should_use_windowing, get_optimal_window_size, get_optimal_preload_size
        
        print("\n🧪 TEST DE LA CONFIGURATION")
        print("="*35)
        
        test_sizes = [10, 25, 50, 75, 100, 150, 200, 500, 1000]
        
        print("Taille | Fenêtrage | Taille fenêtre | Préchargement")
        print("-" * 55)
        
        for size in test_sizes:
            windowing = should_use_windowing(size)
            window_size = get_optimal_window_size(size)
            preload_size = get_optimal_preload_size(size)
            
            windowing_str = "✅ Oui" if windowing else "❌ Non"
            print(f"{size:6d} | {windowing_str:9s} | {window_size:14d} | {preload_size:13d}")
            
    except ImportError:
        print("❌ Configuration non disponible")

if __name__ == "__main__":
    print("🎵 CONFIGURATEUR DE LA MAIN PLAYLIST")
    print("="*50)
    
    while True:
        print("\nOptions disponibles:")
        print("1. Afficher la configuration actuelle")
        print("2. Configurer les seuils d'optimisation")
        print("3. Configurer les tailles de fenêtre")
        print("4. Configurer le mode d'affichage")
        print("5. Activer/désactiver les optimisations")
        print("6. Activer/désactiver le debug")
        print("7. Tester la configuration")
        print("0. Quitter")
        
        choice = input("\nVotre choix (0-7): ").strip()
        
        if choice == "1":
            show_current_config()
        elif choice == "2":
            configure_thresholds()
        elif choice == "3":
            configure_window_sizes()
        elif choice == "4":
            configure_display_mode()
        elif choice == "5":
            toggle_optimizations()
        elif choice == "6":
            enable_debug()
        elif choice == "7":
            test_configuration()
        elif choice == "0":
            print("👋 Configuration terminée!")
            break
        else:
            print("❌ Choix invalide")
        
        input("\nAppuyez sur Entrée pour continuer...")
        print("\n" + "="*50)