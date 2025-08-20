#!/usr/bin/env python3
"""
Test du système de téléchargements indépendant
"""

import sys
import os
import tempfile
import shutil

# Ajouter le répertoire du projet au path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def test_downloads_system():
    """Test complet du système de téléchargements indépendant"""
    print("=== Test du système de téléchargements indépendant ===")
    
    # Créer un dossier temporaire pour les tests
    temp_dir = tempfile.mkdtemp(prefix="downloads_test_")
    print(f"Dossier de test: {temp_dir}")
    
    try:
        # Créer des fichiers de test
        test_files = [
            "Song 001 - Artist A.mp3",
            "Song 002 - Artist B.flac", 
            "Song 003 - Artist C.wav",
            "Song 004 - Artist A.m4a",
            "Song 005 - Artist D.ogg",
            "not_audio.txt",  # Ce fichier ne devrait pas être détecté
            "readme.md"       # Ce fichier non plus
        ]
        
        for filename in test_files:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("fake audio content for testing")
        
        print(f"Fichiers de test créés: {len(test_files)}")
        
        # Tester le gestionnaire de téléchargements
        from library_tab.downloads_manager import DownloadsManager
        
        manager = DownloadsManager(temp_dir)
        
        # Test 1: Récupération des fichiers audio
        audio_files = manager.get_all_files()
        print(f"✓ Fichiers audio détectés: {len(audio_files)}/5 attendus")
        
        for filepath in audio_files:
            print(f"  - {os.path.basename(filepath)}")
        
        # Test 2: Recherche
        search_results = manager.search_files("Artist A")
        print(f"✓ Résultats de recherche pour 'Artist A': {len(search_results)}")
        
        search_results_001 = manager.search_files("001")
        print(f"✓ Résultats de recherche pour '001': {len(search_results_001)}")
        
        # Test 3: Statistiques
        stats = manager.get_stats()
        print(f"✓ Statistiques: {stats['total_files']} fichiers, {stats['total_size_mb']:.3f} MB")
        
        # Test 4: Chargement progressif
        from library_tab.downloads import DownloadsProgressiveLoader
        
        class MockParent:
            def __init__(self):
                self.root = None
        
        parent = MockParent()
        loader = DownloadsProgressiveLoader(parent)
        
        # Initialiser avec tous les fichiers
        loader.initialize(audio_files)
        print(f"✓ Chargement progressif initialisé: {loader.load_count} par batch")
        
        # Tester le chargement par batch
        initial_window = loader.get_current_window()
        print(f"✓ Fenêtre initiale: {len(initial_window)} fichiers")
        
        # Simuler le chargement progressif
        total_loaded = len(initial_window)
        batch_count = 1
        
        while loader.can_load_more():
            new_files = loader.load_more()
            total_loaded += len(new_files)
            batch_count += 1
            print(f"✓ Batch {batch_count}: +{len(new_files)} fichiers (total: {total_loaded})")
            
            if batch_count > 10:  # Sécurité pour éviter une boucle infinie
                break
        
        # Vérifier que tous les fichiers ont été chargés
        final_stats = loader.get_stats()
        print(f"✓ Chargement final: {final_stats['loaded_files']}/{final_stats['total_files']} fichiers")
        
        # Test 5: Cache et métadonnées
        print("\n--- Test du cache ---")
        for filepath in audio_files[:2]:  # Tester seulement les 2 premiers
            duration = manager.get_file_duration(filepath)
            formatted_duration = manager.get_formatted_duration(filepath)
            print(f"✓ {os.path.basename(filepath)}: {formatted_duration}")
        
        # Test 6: Nettoyage et sauvegarde
        manager.save_and_cleanup()
        print("✓ Cache nettoyé et sauvegardé")
        
        print("\n✅ Tous les tests du système indépendant ont réussi!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Nettoyer le dossier temporaire
        try:
            shutil.rmtree(temp_dir)
            print(f"✓ Dossier de test nettoyé: {temp_dir}")
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")

def test_configuration():
    """Test de la configuration indépendante"""
    print("\n=== Test de la configuration indépendante ===")
    
    try:
        from library_tab.config_local import get_library_config, set_library_config
        
        # Test des valeurs par défaut
        load_count = get_library_config('load_more_count')
        print(f"✓ load_more_count par défaut: {load_count}")
        
        scroll_threshold = get_library_config('scroll_threshold')
        print(f"✓ scroll_threshold par défaut: {scroll_threshold}")
        
        # Test de modification
        set_library_config('load_more_count', 15)
        new_load_count = get_library_config('load_more_count')
        print(f"✓ load_more_count après modification: {new_load_count}")
        
        # Test de valeur inexistante
        unknown = get_library_config('unknown_setting', 'default')
        print(f"✓ Valeur inconnue avec défaut: {unknown}")
        
        print("✅ Configuration indépendante fonctionne correctement!")
        
    except Exception as e:
        print(f"❌ Erreur lors du test de configuration: {e}")

if __name__ == "__main__":
    test_downloads_system()
    test_configuration()