#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier la suppression des métadonnées YouTube
"""

import os
import sys
import json

# Ajouter le répertoire parent au path pour importer les modules
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_remove_metadata():
    """Test de la suppression des métadonnées YouTube"""
    
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
        
        def remove_youtube_url_metadata(self, filepath):
            """Supprime l'URL YouTube des métadonnées quand un fichier est supprimé"""
            try:
                import json
                metadata_file = os.path.join("downloads", "youtube_urls.json")
                
                if not os.path.exists(metadata_file):
                    return
                    
                # Charger les métadonnées existantes
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                filename = os.path.basename(filepath)
                
                # Supprimer l'entrée si elle existe
                if filename in metadata:
                    del metadata[filename]
                    
                    # Sauvegarder les métadonnées mises à jour
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                    print(f"✓ URL YouTube supprimée des métadonnées: {filename}")
                else:
                    print(f"✗ Aucune URL trouvée pour: {filename}")
                
            except Exception as e:
                print(f"✗ Erreur suppression métadonnées YouTube: {e}")
        
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
                return metadata.get(filename)
                
            except Exception as e:
                print(f"✗ Erreur lecture métadonnées YouTube: {e}")
                return None
    
    # Créer le dossier downloads s'il n'existe pas
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    # Tester les fonctions
    player = MockPlayer()
    
    # Test 1: Ajouter quelques URLs de test
    test_files = [
        ("downloads/test1.mp3", "https://www.youtube.com/watch?v=test1"),
        ("downloads/test2.mp3", "https://www.youtube.com/watch?v=test2"),
        ("downloads/test3.mp3", "https://www.youtube.com/watch?v=test3")
    ]
    
    print("=== Ajout des URLs de test ===")
    for filepath, url in test_files:
        player.save_youtube_url_metadata(filepath, url)
    
    # Vérifier le contenu du fichier
    print("\n=== Contenu du fichier de métadonnées ===")
    try:
        with open("downloads/youtube_urls.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"Nombre d'entrées: {len(metadata)}")
        for filename, url in metadata.items():
            print(f"  {filename} -> {url}")
    except Exception as e:
        print(f"Erreur lecture fichier: {e}")
    
    # Test 2: Supprimer une URL
    print("\n=== Test de suppression ===")
    player.remove_youtube_url_metadata("downloads/test2.mp3")
    
    # Vérifier que l'URL a été supprimée
    print("\n=== Vérification après suppression ===")
    try:
        with open("downloads/youtube_urls.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"Nombre d'entrées: {len(metadata)}")
        for filename, url in metadata.items():
            print(f"  {filename} -> {url}")
        
        if "test2.mp3" not in metadata:
            print("✓ Test réussi ! L'URL a été correctement supprimée.")
        else:
            print("✗ Test échoué ! L'URL n'a pas été supprimée.")
            
    except Exception as e:
        print(f"Erreur lecture fichier: {e}")
    
    # Test 3: Essayer de supprimer une URL inexistante
    print("\n=== Test suppression URL inexistante ===")
    player.remove_youtube_url_metadata("downloads/inexistant.mp3")

if __name__ == "__main__":
    print("Test de suppression des métadonnées YouTube...")
    test_remove_metadata()
    print("\nTest terminé.")