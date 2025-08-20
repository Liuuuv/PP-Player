#!/usr/bin/env python3
"""
Test du système de bibliothèque indépendant
"""

import sys
import os
import tempfile
import shutil

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_independent_library():
    """Test du système de bibliothèque indépendant"""
    print("=== Test du système de bibliothèque indépendant ===")
    
    # Créer un dossier temporaire pour les tests
    temp_dir = tempfile.mkdtemp(prefix="musicplayer_test_")
    print(f"Dossier de test: {temp_dir}")
    
    try:
        # Créer quelques fichiers de test
        test_files = [
            "test_song_001.mp3",
            "test_song_002.flac", 
            "test_song_003.wav",
            "not_audio.txt"  # Ce fichier ne devrait pas être détecté
        ]
        
        for filename in test_files:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("fake audio content")
        
        print(f"Fichiers de test créés: {len(test_files)}")
        
        # Tester le gestionnaire de téléchargements
        from library_tab.downloads_manager import DownloadsManager
        
        manager = DownloadsManager(temp_dir)
        
        # Tester la récupération des fichiers
        audio_files = manager.get_all_files()
        print(f"Fichiers audio détectés: {len(audio_files)}")
        
        for filepath in audio_files:
            print(f"  - {os.path.basename(filepath)}")
        
        # Tester la recherche
        search_results = manager.search_files("001")
        print(f"Résultats de recherche pour '001': {len(search_results)}")
        
        # Tester les statistiques
        stats = manager.get_stats()
        print(f"Statistiques: {stats}")
        
        # Tester le chargement progressif
        from library_tab.downloads import DownloadsProgressiveLoader
        
        class MockParent:
            def __init__(self):
                self.root = None
        
        parent = MockParent()
        loader = DownloadsProgressiveLoader(parent)
        loader.initialize(audio_files)
        
        print(f"Chargement progressif initialisé avec {len(audio_files)} fichiers")
        
        # Tester le chargement par batch
        initial_window = loader.get_current_window()
        print(f"Fenêtre initiale: {len(initial_window)} fichiers")
        
        if loader.can_load_more():
            new_files = loader.load_more()
            print(f"Nouveaux fichiers chargés: {len(new_files)}")
        
        loader_stats = loader.get_stats()
        print(f"Statistiques du loader: {loader_stats}")
        
        print("\n✅ Test du système indépendant réussi!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Nettoyer le dossier temporaire
        try:
            shutil.rmtree(temp_dir)
            print(f"Dossier de test nettoyé: {temp_dir}")
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")

def test_config_independence():
    """Test de l'indépendance de la configuration"""
    print("\n=== Test de l'indépendance de la configuration ===")
    
    try:
        from library_tab.config_local import get_library_config, set_library_config
        
        # Tester la configuration par défaut
        load_count = get_library_config('load_more_count')
        print(f"load_more_count par défaut: {load_count}")
        
        # Modifier la configuration
        set_library_config('load_more_count', 15)
        new_load_count = get_library_config('load_more_count')
        print(f"load_more_count après modification: {new_load_count}")
        
        # Tester une valeur inexistante
        unknown_value = get_library_config('unknown_key', 'default_value')
        print(f"Valeur inconnue avec défaut: {unknown_value}")
        
        print("✅ Test de configuration indépendante réussi!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test de config: {e}")

if __name__ == "__main__":
    test_independent_library()
    test_config_independence()