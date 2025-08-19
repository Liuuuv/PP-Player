#!/usr/bin/env python3
"""
Test simple pour vérifier la configuration du scroll avec debug
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_scroll_configuration():
    """Test de la configuration du scroll"""
    print("=== Test de la configuration du scroll ===")
    
    try:
        from search_tab.config import get_main_playlist_config, update_main_playlist_config
        
        # Activer le debug
        update_main_playlist_config(debug_scroll=True, debug_windowing=True)
        
        print("✅ DEBUG: Configuration mise à jour")
        print(f"   - Debug scroll: {get_main_playlist_config('debug_scroll')}")
        print(f"   - Debug windowing: {get_main_playlist_config('debug_windowing')}")
        print(f"   - Scroll infini: {get_main_playlist_config('enable_infinite_scroll')}")
        
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Erreur configuration: {e}")
        return False

def test_function_imports():
    """Test des imports de fonctions"""
    print("\n=== Test des imports de fonctions ===")
    
    try:
        from main import MusicPlayer
        import tkinter as tk
        
        # Créer une instance minimale
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        
        player = MusicPlayer(root)
        
        # Tester les fonctions une par une
        functions_to_test = [
            ('_setup_infinite_scroll', 'Configuration scroll infini'),
            ('_update_display_based_on_scroll_position', 'Synchronisation scroll'),
            ('_update_windowed_display', 'Mise à jour fenêtre'),
            ('_on_scroll_with_update', 'Gestion scroll avec mise à jour'),
        ]
        
        for func_name, description in functions_to_test:
            if hasattr(player, func_name):
                print(f"✅ DEBUG: {description} ({func_name}) - disponible")
                
                # Test d'appel simple
                try:
                    func = getattr(player, func_name)
                    if func_name == '_setup_infinite_scroll':
                        func()
                        print(f"   → Exécution réussie")
                    elif func_name == '_update_display_based_on_scroll_position':
                        # Simuler une playlist
                        player.main_playlist = ['test1.mp3', 'test2.mp3', 'test3.mp3']
                        func()
                        print(f"   → Exécution réussie")
                    else:
                        print(f"   → Fonction disponible (test d'exécution non fait)")
                except Exception as e:
                    print(f"   ⚠️ Erreur exécution: {type(e).__name__}")
            else:
                print(f"❌ DEBUG: {description} ({func_name}) - manquante")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Erreur imports: {e}")
        return False

def test_binding_detection():
    """Test de détection des bindings"""
    print("\n=== Test de détection des bindings ===")
    
    try:
        from main import MusicPlayer
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Vérifier les attributs nécessaires
        attributes_to_check = [
            ('playlist_canvas', 'Canvas de playlist'),
            ('playlist_scrollbar', 'Scrollbar de playlist'),
            ('playlist_container', 'Container de playlist'),
        ]
        
        for attr_name, description in attributes_to_check:
            if hasattr(player, attr_name):
                attr_value = getattr(player, attr_name)
                if attr_value:
                    print(f"✅ DEBUG: {description} ({attr_name}) - trouvé: {type(attr_value)}")
                else:
                    print(f"⚠️ DEBUG: {description} ({attr_name}) - None")
            else:
                print(f"❌ DEBUG: {description} ({attr_name}) - manquant")
        
        # Test de la fonction _bind_mousewheel
        if hasattr(player, '_bind_mousewheel'):
            print("✅ DEBUG: Fonction _bind_mousewheel disponible")
        else:
            print("❌ DEBUG: Fonction _bind_mousewheel manquante")
        
        # Test de la fonction _on_mousewheel
        if hasattr(player, '_on_mousewheel'):
            print("✅ DEBUG: Fonction _on_mousewheel disponible")
        else:
            print("❌ DEBUG: Fonction _on_mousewheel manquante")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Erreur détection bindings: {e}")
        return False

def show_debug_summary():
    """Affiche un résumé des points à vérifier"""
    print("\n" + "="*60)
    print("🔍 RÉSUMÉ DU DEBUG - POINTS À VÉRIFIER")
    print("="*60)
    
    print("\n🎯 PROBLÈME ACTUEL:")
    print("   • La barre de scroll scroll mais les musiques ne défilent pas")
    print("   • Les messages de debug nous aideront à identifier où ça bloque")
    
    print("\n🔧 POINTS À VÉRIFIER DANS L'APPLICATION:")
    print("   1. Les messages '🖱️ DEBUG: Scroll détecté sur playlist_canvas' s'affichent-ils ?")
    print("   2. Les messages '🔄 DEBUG: _update_display_based_on_scroll_position()' s'affichent-ils ?")
    print("   3. Les messages '🔄 DEBUG: _update_windowed_display()' s'affichent-ils ?")
    print("   4. Y a-t-il des erreurs dans les messages de debug ?")
    
    print("\n🚨 SI AUCUN MESSAGE DE DEBUG NE S'AFFICHE:")
    print("   → Le problème est dans les bindings (scroll pas détecté)")
    print("   → Vérifier _bind_mousewheel et _on_mousewheel")
    
    print("\n🚨 SI LES MESSAGES S'AFFICHENT MAIS PAS DE CHANGEMENT VISUEL:")
    print("   → Le problème est dans _update_windowed_display")
    print("   → Vérifier la destruction/création des éléments")
    
    print("\n🚨 SI LES MESSAGES D'ERREUR S'AFFICHENT:")
    print("   → Lire les tracebacks pour identifier le problème exact")
    
    print("\n🎮 PROCHAINES ÉTAPES:")
    print("   1. Lancez l'application normale")
    print("   2. Allez dans l'onglet Recherche")
    print("   3. Scrollez avec la molette dans la playlist")
    print("   4. Observez les messages de debug dans la console")
    print("   5. Rapportez ce que vous voyez")

if __name__ == "__main__":
    print("🔍 TEST SIMPLE DE DEBUG DU SCROLL")
    print("="*60)
    
    success1 = test_scroll_configuration()
    success2 = test_function_imports()
    success3 = test_binding_detection()
    
    show_debug_summary()
    
    if success1 and success2 and success3:
        print(f"\n{'='*60}")
        print("✅ CONFIGURATION DE DEBUG PRÊTE !")
        print("🔍 Lancez maintenant l'application et testez le scroll")
        print("📋 Observez les messages de debug pour diagnostiquer")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("⚠️ Il y a des problèmes avec la configuration de debug")
        print(f"{'='*60}")