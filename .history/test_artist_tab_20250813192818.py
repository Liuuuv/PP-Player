#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script pour vérifier que la réorganisation du module artist_tab fonctionne correctement.
Ce script teste l'importation et l'accès aux fonctions sans lancer l'interface graphique.
"""

import sys
import os

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_imports():
    """Test des imports du module artist_tab"""
    print("=== Test des imports ===")
    
    try:
        # Test import du gestionnaire
        from artist_tab_manager import ArtistTabManager, init_artist_tab_manager
        print("✓ Import artist_tab_manager réussi")
        
        # Test import des modules artist_tab
        import artist_tab.core
        import artist_tab.songs
        import artist_tab.releases
        import artist_tab.playlists
        print("✓ Import des modules artist_tab réussi")
        
        # Test import du module principal artist_tab
        from artist_tab.main import ArtistTabModule, get_artist_tab_module
        print("✓ Import artist_tab.main réussi")
        
        return True
        
    except ImportError as e:
        print(f"✗ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"✗ Erreur inattendue: {e}")
        return False

def test_artist_tab_manager():
    """Test de la classe ArtistTabManager"""
    print("\n=== Test ArtistTabManager ===")
    
    try:
        from artist_tab_manager import ArtistTabManager
        
        # Créer une instance mock du lecteur de musique
        class MockMusicPlayer:
            def __init__(self):
                self.artist_mode = False
                self.current_artist_name = ""
                self.artist_tab_active_sorties = False
                self.artist_tab_active_playlists = False
        
        mock_player = MockMusicPlayer()
        manager = ArtistTabManager(mock_player)
        
        # Vérifier que le manager a bien les méthodes attendues
        expected_methods = [
            'show_artist_content',
            'create_artist_tabs', 
            'search_artist_content_async',
            'find_artist_channel_id',
            'cancel_artist_search',
            'search_artist_videos',
            'search_artist_releases',
            'search_artist_playlists',
            'display_artist_videos',
            'display_artist_releases',
            'display_artist_playlists'
        ]
        
        missing_methods = []
        for method in expected_methods:
            if not hasattr(manager, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"✗ Méthodes manquantes: {missing_methods}")
            return False
        else:
            print("✓ Toutes les méthodes attendues sont présentes")
            return True
            
    except Exception as e:
        print(f"✗ Erreur lors du test ArtistTabManager: {e}")
        return False

def test_artist_tab_module():
    """Test du module principal artist_tab"""
    print("\n=== Test ArtistTabModule ===")
    
    try:
        from artist_tab.main import ArtistTabModule, get_artist_tab_module
        
        # Test de l'instance globale
        module = get_artist_tab_module()
        if not isinstance(module, ArtistTabModule):
            print("✗ get_artist_tab_module() ne retourne pas une instance ArtistTabModule")
            return False
        
        # Vérifier que le module a accès aux sous-modules
        if not hasattr(module, 'core') or not hasattr(module, 'songs') or not hasattr(module, 'releases') or not hasattr(module, 'playlists'):
            print("✗ Le module n'a pas accès à tous les sous-modules")
            return False
        
        print("✓ ArtistTabModule fonctionne correctement")
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test ArtistTabModule: {e}")
        return False

def test_function_access():
    """Test de l'accès aux fonctions dans les sous-modules"""
    print("\n=== Test accès aux fonctions ===")
    
    try:
        import artist_tab.core
        import artist_tab.songs
        import artist_tab.releases
        import artist_tab.playlists
        
        # Vérifier quelques fonctions clés
        core_functions = ['_show_artist_content', '_create_artist_tabs', '_search_artist_content_async']
        songs_functions = ['_search_artist_videos_with_id', '_display_artist_videos']
        releases_functions = ['_search_artist_releases_with_id', '_display_artist_releases']
        playlists_functions = ['_search_artist_playlists_with_id', '_display_artist_playlists']
        
        modules_to_test = [
            (artist_tab.core, core_functions, "core"),
            (artist_tab.songs, songs_functions, "songs"),
            (artist_tab.releases, releases_functions, "releases"),
            (artist_tab.playlists, playlists_functions, "playlists")
        ]
        
        all_good = True
        for module, functions, name in modules_to_test:
            missing = [f for f in functions if not hasattr(module, f)]
            if missing:
                print(f"✗ Fonctions manquantes dans {name}: {missing}")
                all_good = False
            else:
                print(f"✓ Toutes les fonctions présentes dans {name}")
        
        return all_good
        
    except Exception as e:
        print(f"✗ Erreur lors du test d'accès aux fonctions: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("Test de la réorganisation du module artist_tab")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_artist_tab_manager,
        test_artist_tab_module,
        test_function_access
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("RÉSULTATS:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ Tous les tests réussis ({passed}/{total})")
        print("La réorganisation du module artist_tab est fonctionnelle !")
        return 0
    else:
        print(f"✗ {total - passed} test(s) échoué(s) sur {total}")
        print("Il y a des problèmes à corriger.")
        return 1

if __name__ == "__main__":
    sys.exit(main())