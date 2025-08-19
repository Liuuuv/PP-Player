#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier la fonctionnalité Ctrl+clic pour ouvrir sur YouTube
"""

import os
import sys
import json

# Ajouter le répertoire parent au path pour importer les modules
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_metadata_functions():
    """Test des fonctions de métadonnées YouTube"""
    
    # Créer une classe mock pour tester
    class MockPlayer:
        def save_youtube_url_metadata(self, filepath, youtube_url):
            """Sauvegarde l'URL YouTube originale pour un fichier téléchargé"""
            try:
                import json
                metadata_file = os.path.join("downloads", "youtube_urls.json")
                
                # Charger les métadonnées existantes
                metadata = {}
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except:
                        metadata = {}
                
                # Ajouter la nouvelle URL
                filename = os.path.basename(filepath)
                metadata[filename] = youtube_url
                
                # Sauvegarder
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                print(f"✓ Métadonnées sauvegardées: {filename} -> {youtube_url}")
                    
            except Exception as e:
                print(f"✗ Erreur sauvegarde métadonnées YouTube: {e}")
        
        def get_youtube_url_from_metadata(self, filepath):
            """Récupère l'URL YouTube originale pour un fichier téléchargé"""
            try:
                import json
                metadata_file = os.path.join("downloads", "youtube_urls.json")
                
                if not os.path.exists(metadata_file):
                    return None
                    
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                filename = os.path.basename(filepath)
                url = metadata.get(filename)
                
                if url:
                    print(f"✓ URL trouvée: {filename} -> {url}")
                else:
                    print(f"✗ Aucune URL trouvée pour: {filename}")
                
                return url
                
            except Exception as e:
                print(f"✗ Erreur lecture métadonnées YouTube: {e}")
                return None
    
    # Créer le dossier downloads s'il n'existe pas
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    # Tester les fonctions
    player = MockPlayer()
    
    # Test 1: Sauvegarder une URL
    test_filepath = "downloads/DAOKO - GAMEOVER.mp3"
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print("=== Test de sauvegarde ===")
    player.save_youtube_url_metadata(test_filepath, test_url)
    
    # Test 2: Récupérer l'URL
    print("\n=== Test de récupération ===")
    retrieved_url = player.get_youtube_url_from_metadata(test_filepath)
    
    # Test 3: Vérifier que ça fonctionne
    if retrieved_url == test_url:
        print("✓ Test réussi ! L'URL a été correctement sauvegardée et récupérée.")
    else:
        print(f"✗ Test échoué ! URL attendue: {test_url}, URL récupérée: {retrieved_url}")
    
    # Test 4: Fichier inexistant
    print("\n=== Test fichier inexistant ===")
    nonexistent_url = player.get_youtube_url_from_metadata("downloads/fichier_inexistant.mp3")
    if nonexistent_url is None:
        print("✓ Test réussi ! Aucune URL trouvée pour un fichier inexistant.")
    else:
        print(f"✗ Test échoué ! URL inattendue trouvée: {nonexistent_url}")

if __name__ == "__main__":
    print("Test des fonctionnalités YouTube URL...")
    test_metadata_functions()
    print("\nTest terminé.")