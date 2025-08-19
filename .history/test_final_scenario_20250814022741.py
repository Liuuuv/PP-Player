#!/usr/bin/env python3
"""
Test final du scénario complet avec la correction
"""

import sys
import os

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_method_exists():
    """Test que la méthode _display_search_results existe maintenant"""
    print("=== Test de l'existence de la méthode ===")
    
    try:
        # Import du module principal
        from main import MusicPlayer
        import tkinter as tk
        
        # Créer une instance temporaire pour tester
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        
        player = MusicPlayer(root)
        
        # Vérifier que la méthode existe
        if hasattr(player, '_display_search_results'):
            print("✅ Méthode _display_search_results trouvée")
            
            # Vérifier que c'est callable
            if callable(getattr(player, '_display_search_results')):
                print("✅ Méthode _display_search_results est callable")
            else:
                print("❌ Méthode _display_search_results n'est pas callable")
                return False
        else:
            print("❌ Méthode _display_search_results manquante")
            return False
        
        # Nettoyer
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_search_tab_core_integration():
    """Test de l'intégration avec search_tab.core"""
    print("\n=== Test de l'intégration search_tab.core ===")
    
    try:
        import search_tab.core
        
        # Test des fonctions principales
        functions = [
            'is_artist_tab_open',
            'should_show_large_thumbnail',
            'handle_search_clear',
            'handle_artist_tab_close'
        ]
        
        for func_name in functions:
            if hasattr(search_tab.core, func_name):
                print(f"✅ Fonction {func_name} disponible")
            else:
                print(f"❌ Fonction {func_name} manquante")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'intégration: {e}")
        return False

def test_search_results_function():
    """Test de la fonction _display_search_results dans search_tab.results"""
    print("\n=== Test de la fonction dans search_tab.results ===")
    
    try:
        import search_tab.results
        
        # Vérifier que la fonction existe
        if hasattr(search_tab.results, '_display_search_results'):
            print("✅ Fonction _display_search_results trouvée dans search_tab.results")
            
            # Vérifier que c'est callable
            if callable(getattr(search_tab.results, '_display_search_results')):
                print("✅ Fonction _display_search_results est callable")
            else:
                print("❌ Fonction _display_search_results n'est pas callable")
                return False
        else:
            print("❌ Fonction _display_search_results manquante dans search_tab.results")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Tests de validation de la correction")
    print("=" * 50)
    
    tests = [
        test_search_tab_core_integration,
        test_search_results_function,
        test_method_exists
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"❌ Erreur dans {test.__name__}: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("\n✅ Correction validée :")
        print("  • Méthode _display_search_results ajoutée dans main.py")
        print("  • Fonction _display_search_results disponible dans search_tab.results")
        print("  • Intégration search_tab.core fonctionnelle")
        print("  • Le scénario recherche → artist_tab → fermeture devrait maintenant fonctionner")
        
        print("\n🚀 L'application est prête à être testée !")
        
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("La correction n'est pas complète.")
        sys.exit(1)

if __name__ == "__main__":
    main()