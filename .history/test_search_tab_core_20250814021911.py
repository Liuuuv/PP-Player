#!/usr/bin/env python3
"""
Test script pour vérifier le bon fonctionnement de search_tab/core.py
"""

import sys
import os

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Importer le module search_tab.core
try:
    import search_tab.core
    print("✓ Import de search_tab.core réussi")
except ImportError as e:
    print(f"✗ Erreur d'import de search_tab.core: {e}")
    sys.exit(1)

class MockPlayer:
    """Mock du MusicPlayer pour les tests"""
    def __init__(self):
        self.artist_mode = False
        self.artist_notebook = None
        self.current_search_query = ""
        self.search_results_count = 0
        
    def _show_current_song_thumbnail(self):
        print("Mock: _show_current_song_thumbnail appelée")

def test_is_artist_tab_open():
    """Test de la fonction is_artist_tab_open"""
    print("\n=== Test is_artist_tab_open ===")
    
    player = MockPlayer()
    
    # Test 1: artist_mode = False
    result = search_tab.core.is_artist_tab_open(player)
    print(f"artist_mode=False: {result} (attendu: False)")
    assert result == False, "Devrait retourner False quand artist_mode=False"
    
    # Test 2: artist_mode = True
    player.artist_mode = True
    result = search_tab.core.is_artist_tab_open(player)
    print(f"artist_mode=True: {result} (attendu: True)")
    assert result == True, "Devrait retourner True quand artist_mode=True"
    
    print("✓ Tous les tests is_artist_tab_open passés")

def test_should_show_large_thumbnail():
    """Test de la fonction should_show_large_thumbnail"""
    print("\n=== Test should_show_large_thumbnail ===")
    
    player = MockPlayer()
    
    # Test 1: Conditions normales (pas d'artist_tab, pas de résultats)
    result = search_tab.core.should_show_large_thumbnail(player)
    print(f"Conditions normales: {result} (attendu: True)")
    assert result == True, "Devrait retourner True dans des conditions normales"
    
    # Test 2: artist_tab ouvert
    player.artist_mode = True
    result = search_tab.core.should_show_large_thumbnail(player)
    print(f"artist_tab ouvert: {result} (attendu: False)")
    assert result == False, "Devrait retourner False quand artist_tab est ouvert"
    
    # Test 3: artist_tab fermé mais résultats de recherche présents
    player.artist_mode = False
    player.current_search_query = "test"
    player.search_results_count = 5
    result = search_tab.core.should_show_large_thumbnail(player)
    print(f"Résultats de recherche présents: {result} (attendu: False)")
    assert result == False, "Devrait retourner False quand il y a des résultats de recherche"
    
    print("✓ Tous les tests should_show_large_thumbnail passés")

def test_handle_search_clear():
    """Test de la fonction handle_search_clear"""
    print("\n=== Test handle_search_clear ===")
    
    player = MockPlayer()
    
    # Test 1: artist_tab fermé - devrait appeler _show_current_song_thumbnail
    print("Test avec artist_tab fermé:")
    search_tab.core.handle_search_clear(player)
    
    # Test 2: artist_tab ouvert - ne devrait pas appeler _show_current_song_thumbnail
    print("Test avec artist_tab ouvert:")
    player.artist_mode = True
    search_tab.core.handle_search_clear(player)
    
    print("✓ Test handle_search_clear terminé")

def test_handle_artist_tab_close():
    """Test de la fonction handle_artist_tab_close"""
    print("\n=== Test handle_artist_tab_close ===")
    
    player = MockPlayer()
    
    # Test 1: Pas de résultats de recherche - devrait appeler _show_current_song_thumbnail
    print("Test sans résultats de recherche:")
    search_tab.core.handle_artist_tab_close(player)
    
    # Test 2: Avec résultats de recherche - ne devrait pas appeler _show_current_song_thumbnail
    print("Test avec résultats de recherche:")
    player.current_search_query = "test"
    player.search_results_count = 3
    search_tab.core.handle_artist_tab_close(player)
    
    print("✓ Test handle_artist_tab_close terminé")

def main():
    """Fonction principale de test"""
    print("=== Tests de search_tab/core.py ===")
    
    try:
        test_is_artist_tab_open()
        test_should_show_large_thumbnail()
        test_handle_search_clear()
        test_handle_artist_tab_close()
        
        print("\n✓ Tous les tests sont passés avec succès !")
        print("\nLes fonctions de search_tab/core.py sont prêtes à être utilisées.")
        
    except Exception as e:
        print(f"\n✗ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()