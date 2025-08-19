#!/usr/bin/env python3
"""
Test du scénario spécifique : recherche → ouvre artist_tab → ferme artist_tab
"""

import sys
import os
import time

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_scenario():
    """Test du scénario complet"""
    print("=== Test du scénario : recherche → artist_tab → fermeture ===")
    
    try:
        # Import des modules
        import search_tab.core
        print("✓ Import de search_tab.core réussi")
        
        # Simuler le scénario avec un mock player
        class MockPlayer:
            def __init__(self):
                self.artist_mode = False
                self.artist_notebook = None
                self.current_search_query = "daoko"
                self.search_results_count = 10
                self.thumbnail_calls = []
                
            def _show_current_song_thumbnail(self):
                self.thumbnail_calls.append("thumbnail_shown")
                print("Mock: _show_current_song_thumbnail appelée")
        
        player = MockPlayer()
        
        print("\n1. État initial : recherche effectuée avec résultats")
        print(f"   - Requête: '{player.current_search_query}'")
        print(f"   - Résultats: {player.search_results_count}")
        print(f"   - Artist mode: {player.artist_mode}")
        
        # Vérifier que la miniature ne s'affiche pas (résultats présents)
        should_show = search_tab.core.should_show_large_thumbnail(player)
        print(f"   - Miniature devrait s'afficher: {should_show} (attendu: False)")
        assert should_show == False, "Ne devrait pas afficher la miniature avec des résultats"
        
        print("\n2. Ouverture de l'artist_tab")
        player.artist_mode = True
        print(f"   - Artist mode: {player.artist_mode}")
        
        # Vérifier que l'artist_tab est détecté comme ouvert
        is_open = search_tab.core.is_artist_tab_open(player)
        print(f"   - Artist tab ouvert: {is_open} (attendu: True)")
        assert is_open == True, "Artist tab devrait être détecté comme ouvert"
        
        # Vérifier que la miniature ne s'affiche toujours pas (artist_tab ouvert)
        should_show = search_tab.core.should_show_large_thumbnail(player)
        print(f"   - Miniature devrait s'afficher: {should_show} (attendu: False)")
        assert should_show == False, "Ne devrait pas afficher la miniature avec artist_tab ouvert"
        
        print("\n3. Fermeture de l'artist_tab")
        player.artist_mode = False
        print(f"   - Artist mode: {player.artist_mode}")
        
        # Simuler la fermeture avec handle_artist_tab_close
        print("   - Appel de handle_artist_tab_close...")
        initial_calls = len(player.thumbnail_calls)
        search_tab.core.handle_artist_tab_close(player)
        
        # Vérifier que la miniature ne s'affiche PAS (résultats encore présents)
        final_calls = len(player.thumbnail_calls)
        print(f"   - Appels thumbnail avant: {initial_calls}, après: {final_calls}")
        print(f"   - Miniature affichée: {final_calls > initial_calls} (attendu: False)")
        assert final_calls == initial_calls, "Ne devrait pas afficher la miniature car résultats présents"
        
        print("\n4. Clear de la recherche (simulation)")
        player.current_search_query = ""
        player.search_results_count = 0
        print(f"   - Requête: '{player.current_search_query}'")
        print(f"   - Résultats: {player.search_results_count}")
        
        # Maintenant la miniature devrait s'afficher
        should_show = search_tab.core.should_show_large_thumbnail(player)
        print(f"   - Miniature devrait s'afficher: {should_show} (attendu: True)")
        assert should_show == True, "Devrait afficher la miniature sans résultats ni artist_tab"
        
        # Simuler le clear avec handle_search_clear
        print("   - Appel de handle_search_clear...")
        initial_calls = len(player.thumbnail_calls)
        search_tab.core.handle_search_clear(player)
        
        final_calls = len(player.thumbnail_calls)
        print(f"   - Appels thumbnail avant: {initial_calls}, après: {final_calls}")
        print(f"   - Miniature affichée: {final_calls > initial_calls} (attendu: True)")
        assert final_calls > initial_calls, "Devrait afficher la miniature après clear"
        
        print("\n✅ Scénario testé avec succès !")
        print("\nComportement vérifié :")
        print("✓ Avec résultats de recherche → pas de miniature")
        print("✓ Avec artist_tab ouvert → pas de miniature") 
        print("✓ Fermeture artist_tab + résultats présents → pas de miniature")
        print("✓ Clear recherche + pas d'artist_tab → miniature affichée")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test du scénario: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = test_scenario()
    
    if success:
        print("\n" + "="*60)
        print("🎉 SCÉNARIO VALIDÉ ! 🎉")
        print("="*60)
        print("\nLe comportement est correct :")
        print("• Recherche → résultats affichés → pas de miniature")
        print("• Ouverture artist_tab → pas de miniature")
        print("• Fermeture artist_tab → vérification des résultats")
        print("  - Si résultats présents → pas de miniature")
        print("  - Si pas de résultats → miniature affichée")
        print("• Clear recherche → vérification artist_tab")
        print("  - Si artist_tab ouvert → pas de miniature")
        print("  - Si artist_tab fermé → miniature affichée")
    else:
        print("\n❌ Le scénario a échoué")
        sys.exit(1)

if __name__ == "__main__":
    main()