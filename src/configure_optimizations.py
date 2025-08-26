#!/usr/bin/env python3
"""
Script d'exemple pour configurer les optimisations de playlist
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def configure_for_small_collections():
    """Configuration optimisée pour les petites collections (< 100 musiques)"""
    from playlist_config import update_config
    
    update_config(
        windowing_threshold=100,  # Fenêtrage seulement au-dessus de 100 musiques
        window_size=50,           # Fenêtre plus grande
        enable_preloading=False,  # Pas de préchargement nécessaire
        jump_size=20              # Sauts plus grands
    )
    print("✅ Configuration optimisée pour petites collections")

def configure_for_large_collections():
    """Configuration optimisée pour les grandes collections (> 500 musiques)"""
    from playlist_config import update_config
    
    update_config(
        windowing_threshold=30,   # Fenêtrage dès 30 musiques
        window_size=25,           # Fenêtre plus petite pour plus de fluidité
        enable_preloading=True,   # Préchargement activé
        preload_size=30,          # Préchargement plus important
        jump_size=25              # Sauts plus grands pour naviguer rapidement
    )
    print("✅ Configuration optimisée pour grandes collections")

def configure_for_performance():
    """Configuration pour maximiser les performances"""
    from playlist_config import update_config
    
    update_config(
        windowing_threshold=20,   # Fenêtrage très tôt
        window_size=20,           # Fenêtre minimale
        enable_preloading=True,   # Préchargement activé
        preload_size=15,          # Préchargement modéré
        enable_async_refresh=True # Rafraîchissement asynchrone
    )
    print("✅ Configuration optimisée pour les performances")

def disable_all_optimizations():
    """Désactive toutes les optimisations (affichage complet)"""
    from playlist_config import update_config
    
    update_config(
        enable_optimizations=False,
        enable_preloading=False,
        enable_async_refresh=False
    )
    print("✅ Toutes les optimisations désactivées")

def show_current_config():
    """Affiche la configuration actuelle"""
    from playlist_config import USER_CONFIG, get_optimization_level
    
    print("\n📋 CONFIGURATION ACTUELLE:")
    print("="*50)
    for key, value in USER_CONFIG.items():
        print(f"  {key:20}: {value}")
    
    print("\n📊 EXEMPLES DE COMPORTEMENT:")
    test_sizes = [25, 50, 100, 200, 500]
    for size in test_sizes:
        level = get_optimization_level(size)
        print(f"  {size:3d} musiques: niveau {level}")

def interactive_configuration():
    """Configuration interactive"""
    from playlist_config import update_config, get_config
    
    print("\n🔧 CONFIGURATION INTERACTIVE")
    print("="*50)
    
    try:
        # Seuil de fenêtrage
        current_threshold = get_config("windowing_threshold", 50)
        print(f"\nSeuil de fenêtrage actuel: {current_threshold}")
        new_threshold = input("Nouveau seuil (ou Entrée pour garder): ").strip()
        if new_threshold and new_threshold.isdigit():
            update_config(windowing_threshold=int(new_threshold))
            print(f"✅ Seuil mis à jour: {new_threshold}")
        
        # Taille de fenêtre
        current_window = get_config("window_size", 30)
        print(f"\nTaille de fenêtre actuelle: {current_window}")
        new_window = input("Nouvelle taille (ou Entrée pour garder): ").strip()
        if new_window and new_window.isdigit():
            update_config(window_size=int(new_window))
            print(f"✅ Taille de fenêtre mise à jour: {new_window}")
        
        # Optimisations
        current_opt = get_config("enable_optimizations", True)
        print(f"\nOptimisations activées: {current_opt}")
        toggle_opt = input("Basculer les optimisations? (o/n): ").strip().lower()
        if toggle_opt == 'o':
            update_config(enable_optimizations=not current_opt)
            print(f"✅ Optimisations: {not current_opt}")
        
        print("\n✅ Configuration mise à jour!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Configuration annulée")

if __name__ == "__main__":
    print("🎛️  CONFIGURATEUR D'OPTIMISATIONS DE PLAYLIST")
    print("="*60)
    
    while True:
        print("\nOptions disponibles:")
        print("1. Configuration pour petites collections (< 100 musiques)")
        print("2. Configuration pour grandes collections (> 500 musiques)")
        print("3. Configuration pour performances maximales")
        print("4. Désactiver toutes les optimisations")
        print("5. Configuration interactive")
        print("6. Afficher la configuration actuelle")
        print("0. Quitter")
        
        choice = input("\nVotre choix (0-6): ").strip()
        
        if choice == "1":
            configure_for_small_collections()
        elif choice == "2":
            configure_for_large_collections()
        elif choice == "3":
            configure_for_performance()
        elif choice == "4":
            disable_all_optimizations()
        elif choice == "5":
            interactive_configuration()
        elif choice == "6":
            show_current_config()
        elif choice == "0":
            print("👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide")
        
        input("\nAppuyez sur Entrée pour continuer...")
        print("\n" + "="*60)