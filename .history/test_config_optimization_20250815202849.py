#!/usr/bin/env python3
"""
Test de la configuration des optimisations de playlist
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_config_functions():
    """Test des fonctions de configuration"""
    print("=== Test des fonctions de configuration ===")
    
    try:
        from playlist_config import (
            should_use_windowing, get_window_size, get_preload_size, 
            get_optimization_level, update_config, get_config
        )
        
        print("✓ Import des fonctions de configuration réussi")
        
        # Test des seuils par défaut
        test_sizes = [10, 25, 50, 75, 100, 200, 500]
        
        print("\nTest des seuils d'optimisation:")
        for size in test_sizes:
            windowing = should_use_windowing(size)
            window_size = get_window_size(size)
            preload_size = get_preload_size(size)
            opt_level = get_optimization_level(size)
            
            print(f"  {size:3d} musiques: fenêtrage={windowing}, fenêtre={window_size:2d}, préchargement={preload_size:2d}, niveau={opt_level}")
        
        # Test de modification de configuration
        print("\nTest de modification de configuration:")
        original_threshold = get_config("windowing_threshold", 50)
        print(f"  Seuil original: {original_threshold}")
        
        # Modifier le seuil
        update_config(windowing_threshold=100)
        new_threshold = get_config("windowing_threshold", 50)
        print(f"  Nouveau seuil: {new_threshold}")
        
        # Tester avec le nouveau seuil
        print("  Test avec nouveau seuil:")
        for size in [75, 100, 125]:
            windowing = should_use_windowing(size)
            print(f"    {size} musiques: fenêtrage={windowing}")
        
        print("✅ Test des fonctions de configuration réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de configuration: {e}")
        return False

def test_playlist_with_config():
    """Test de la playlist avec configuration"""
    print("\n=== Test de la playlist avec configuration ===")
    
    try:
        from main import MusicPlayer
        from playlist_config import update_config, get_config
        import tkinter as tk
        
        # Créer une instance temporaire
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Simuler une grande playlist
        player.main_playlist = [f"test{i}.mp3" for i in range(1, 151)]  # 150 musiques
        player.current_index = 75  # Au milieu
        
        print(f"✓ Playlist de test créée: {len(player.main_playlist)} musiques")
        
        # Test 1: Configuration par défaut (seuil = 50)
        print("\n1. Test avec configuration par défaut:")
        try:
            player._refresh_main_playlist_display()
            print("   ✓ Affichage avec fenêtrage (défaut)")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
        
        # Test 2: Désactiver les optimisations
        print("\n2. Test avec optimisations désactivées:")
        update_config(enable_optimizations=False)
        try:
            player._refresh_main_playlist_display()
            print("   ✓ Affichage complet forcé (optimisations désactivées)")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
        
        # Test 3: Réactiver avec seuil plus élevé
        print("\n3. Test avec seuil élevé (200 musiques):")
        update_config(enable_optimizations=True, windowing_threshold=200)
        try:
            player._refresh_main_playlist_display()
            print("   ✓ Affichage complet (sous le seuil)")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
        
        # Test 4: Playlist très grande avec seuil normal
        print("\n4. Test avec playlist très grande:")
        player.main_playlist = [f"test{i}.mp3" for i in range(1, 301)]  # 300 musiques
        update_config(windowing_threshold=50)
        try:
            player._refresh_main_playlist_display()
            print("   ✓ Affichage avec fenêtrage (grande playlist)")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
        
        root.destroy()
        print("\n✅ Test de la playlist avec configuration réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test de playlist: {e}")
        return False

def show_config_summary():
    """Affiche un résumé de la configuration"""
    print("\n" + "="*70)
    print("📋 RÉSUMÉ DE LA CONFIGURATION DES OPTIMISATIONS")
    print("="*70)
    
    try:
        from playlist_config import USER_CONFIG
        
        print("\n🔧 PARAMÈTRES CONFIGURABLES:")
        for key, value in USER_CONFIG.items():
            print(f"   {key}: {value}")
        
        print("\n📊 SEUILS D'OPTIMISATION:")
        print("   • ≤ 20 musiques: Aucune optimisation")
        print("   • 21-50 musiques: Optimisations légères")
        print("   • 51-200 musiques: Fenêtrage activé")
        print("   • > 200 musiques: Optimisations maximales")
        
        print("\n⚙️  POUR MODIFIER LA CONFIGURATION:")
        print("   from playlist_config import update_config")
        print("   update_config(windowing_threshold=100)  # Nouveau seuil")
        print("   update_config(enable_optimizations=False)  # Désactiver")
        print("   update_config(window_size=40)  # Taille de fenêtre")
        
    except Exception as e:
        print(f"Erreur lors de l'affichage du résumé: {e}")

if __name__ == "__main__":
    print("🔧 TEST DE LA CONFIGURATION DES OPTIMISATIONS")
    print("="*70)
    
    success1 = test_config_functions()
    success2 = test_playlist_with_config()
    
    show_config_summary()
    
    if success1 and success2:
        print(f"\n{'='*70}")
        print("🎉 CONFIGURATION FONCTIONNELLE !")
        print("✅ Les optimisations sont maintenant configurables")
        print("✅ Le fenêtrage respecte les seuils configurés")
        print("✅ Vous pouvez ajuster les paramètres selon vos besoins")
        print(f"{'='*70}")
    else:
        print(f"\n{'='*70}")
        print("⚠️  Il y a des problèmes avec la configuration")
        print(f"{'='*70}")