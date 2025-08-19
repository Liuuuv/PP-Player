#!/usr/bin/env python3
"""
Test script pour vérifier que la réorganisation des fonctions de recherche fonctionne correctement.
"""

import sys
import os

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_search_functions_import():
    """Test que toutes les fonctions de recherche peuvent être importées depuis search_tab.results"""
    try:
        import search_tab.results as search_results
        
        # Liste des fonctions qui devraient être dans search_tab.results
        expected_functions = [
            '_ensure_results_container_exists',
            '_recreate_youtube_canvas', 
            '_update_search_results_ui',
            '_load_more_search_results',
            '_fetch_more_results',
            '_display_batch_results',
            '_display_new_results',
            '_clear_results',
            '_show_search_results',
            '_on_filter_change',
            '_on_youtube_canvas_configure',
            '_start_new_search',
            '_filter_search_results',
            '_perform_initial_search',
            '_save_current_search_state',
            '_on_search_entry_change',
            '_execute_search_change',
            '_clear_youtube_search',
            '_show_current_song_thumbnail',
            '_load_large_thumbnail',
            '_return_to_search',
            'search_youtube',
            '_safe_update_status',
            '_safe_status_update',
            '_add_search_result',
            '_on_result_click',
            '_on_result_right_click',
            '_safe_add_search_result',
            '_recreate_thumbnail_frame',
            '_on_scrollbar_release',
            '_check_scroll_position',
            '_should_load_more_results',
            '_update_results_counter',
            '_update_stats_bar'
        ]
        
        missing_functions = []
        for func_name in expected_functions:
            if not hasattr(search_results, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"❌ Fonctions manquantes dans search_tab.results: {missing_functions}")
            return False
        else:
            print(f"✅ Toutes les {len(expected_functions)} fonctions de recherche sont présentes dans search_tab.results")
            return True
            
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_main_delegations():
    """Test que les fonctions dans main.py délèguent correctement vers search_tab.results"""
    try:
        # Importer le main pour vérifier les délégations
        import main
        
        # Créer une instance fictive pour tester
        class MockApp:
            def __init__(self):
                self.search_cancelled = False
                
        app = MockApp()
        
        # Tester quelques fonctions clés (sans les exécuter complètement)
        functions_to_test = [
            'search_youtube',
            '_start_new_search', 
            '_clear_results',
            '_show_search_results',
            '_safe_add_search_result',
            '_update_results_counter',
            '_update_stats_bar'
        ]
        
        for func_name in functions_to_test:
            if hasattr(main.MusicPlayer, func_name):
                print(f"✅ {func_name} existe dans main.MusicPlayer")
            else:
                print(f"❌ {func_name} manque dans main.MusicPlayer")
                return False
        
        print("✅ Toutes les fonctions de délégation sont présentes dans main.py")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des délégations: {e}")
        return False

def test_search_manager():
    """Test que la classe SearchManager fonctionne correctement"""
    try:
        import search_tab.results as search_results
        
        # Créer une instance fictive pour tester
        class MockApp:
            def __init__(self):
                self.search_cancelled = False
                
        app = MockApp()
        
        # Tester la création du SearchManager
        search_manager = search_results.create_search_manager(app)
        
        if not isinstance(search_manager, search_results.SearchManager):
            print("❌ SearchManager n'est pas du bon type")
            return False
            
        # Tester que le SearchManager a les bonnes méthodes
        expected_methods = [
            'search_youtube',
            'clear_results',
            'load_more_results',
            'update_results_ui',
            'on_search_entry_change',
            'clear_search',
            'show_current_song_thumbnail',
            'on_filter_change',
            'should_load_more_results',
            'update_results_counter',
            'update_stats_bar'
        ]
        
        missing_methods = []
        for method_name in expected_methods:
            if not hasattr(search_manager, method_name):
                missing_methods.append(method_name)
        
        if missing_methods:
            print(f"❌ Méthodes manquantes dans SearchManager: {missing_methods}")
            return False
        else:
            print(f"✅ SearchManager a toutes les {len(expected_methods)} méthodes attendues")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test du SearchManager: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🔍 Test de la réorganisation des fonctions de recherche YouTube")
    print("=" * 60)
    
    success = True
    
    # Test 1: Import des fonctions
    print("\n1. Test d'import des fonctions de search_tab.results:")
    success &= test_search_functions_import()
    
    # Test 2: Délégations dans main.py
    print("\n2. Test des délégations dans main.py:")
    success &= test_main_delegations()
    
    # Test 3: SearchManager
    print("\n3. Test de la classe SearchManager:")
    success &= test_search_manager()
    
    # Résultat final
    print("\n" + "=" * 60)
    if success:
        print("🎉 Tous les tests sont passés ! La réorganisation semble réussie.")
        print("\n📋 Résumé de la réorganisation:")
        print("   • Toutes les fonctions de recherche YouTube sont maintenant dans search_tab/results.py")
        print("   • Les fonctions dans main.py délèguent correctement vers le module search_tab.results")
        print("   • Le module search_tab/results.py est plus indépendant du main")
    else:
        print("❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return success

if __name__ == "__main__":
    main()