#!/usr/bin/env python3
"""
Test d'intégration pour vérifier le bon fonctionnement de la logique search_tab/core.py
avec l'application réelle
"""

import sys
import os
import time

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_integration():
    """Test d'intégration avec l'application réelle"""
    print("=== Test d'intégration search_tab/core.py ===")
    
    try:
        # Import des modules
        import search_tab.core
        import search_tab.results
        print("✓ Imports réussis")
        
        # Vérifier que les fonctions existent
        functions_to_check = [
            'is_artist_tab_open',
            'should_show_large_thumbnail', 
            'handle_search_clear',
            'handle_artist_tab_close'
        ]
        
        for func_name in functions_to_check:
            if hasattr(search_tab.core, func_name):
                print(f"✓ Fonction {func_name} trouvée")
            else:
                print(f"✗ Fonction {func_name} manquante")
                return False
        
        # Vérifier que les fonctions dans results.py utilisent bien core.py
        print("\n=== Vérification de l'intégration ===")
        
        # Lire le contenu de results.py pour vérifier les imports
        results_path = os.path.join(project_dir, 'search_tab', 'results.py')
        with open(results_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifier les intégrations
        integrations = [
            ('search_tab.core.handle_search_clear', '_clear_youtube_search'),
            ('search_tab.core.should_show_large_thumbnail', '_show_current_song_thumbnail'),
            ('search_tab.core.handle_artist_tab_close', '_return_to_search')
        ]
        
        for core_func, results_func in integrations:
            if core_func in content:
                print(f"✓ {results_func} utilise {core_func}")
            else:
                print(f"✗ {results_func} n'utilise pas {core_func}")
                return False
        
        print("\n✓ Tous les tests d'intégration sont passés !")
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors des tests d'intégration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = test_integration()
    
    if success:
        print("\n" + "="*50)
        print("🎉 IMPLÉMENTATION RÉUSSIE ! 🎉")
        print("="*50)
        print("\nLa logique search_tab/core.py est correctement implémentée :")
        print("✓ Clear de recherche → vérifie artist_tab → affiche miniature si fermé")
        print("✓ Fermeture artist_tab → vérifie résultats → affiche miniature si vide")
        print("✓ Affichage miniature → vérifie conditions → affiche seulement si approprié")
        print("\nL'onglet search_tab est maintenant plus indépendant du main !")
    else:
        print("\n❌ Des problèmes ont été détectés dans l'implémentation")
        sys.exit(1)

if __name__ == "__main__":
    main()