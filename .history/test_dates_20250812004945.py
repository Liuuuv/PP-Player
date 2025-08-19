#!/usr/bin/env python3
"""
Test script pour vérifier l'affichage des dates de publication YouTube
"""
import sys
import os
import json
import datetime

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(__file__))

from main import MusicPlayer
import tkinter as tk

def test_youtube_dates():
    """Test l'affichage des dates de publication YouTube"""
    
    # Créer une instance mock pour tester
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre
    
    try:
        player = MusicPlayer(root)
        
        # Fichier de test
        test_filepath = os.path.join("downloads", "test_video.mp3")
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        test_upload_date = "20091025"  # 25 octobre 2009
        
        # Créer un fichier de test fictif
        os.makedirs("downloads", exist_ok=True)
        if not os.path.exists(test_filepath):
            with open(test_filepath, 'w') as f:
                f.write("")  # Fichier vide pour le test
        
        print("=== Test des dates YouTube ===")
        
        # 1. Sauvegarder avec date de publication
        print("1. Sauvegarde des métadonnées avec date de publication...")
        player.save_youtube_url_metadata(test_filepath, test_url, test_upload_date)
        
        # 2. Récupérer les métadonnées
        print("2. Récupération des métadonnées étendues...")
        metadata = player.get_youtube_metadata(test_filepath)
        print(f"   Métadonnées récupérées: {metadata}")
        
        # 3. Tester le formatage de la date
        print("3. Test du formatage des informations (artiste • album • date)...")
        
        # Test avec date YouTube
        formatted_info = player._format_artist_album_info("Test Artist", "Test Album", test_filepath)
        print(f"   Avec date YouTube: {formatted_info}")
        
        # Test avec un fichier sans métadonnées YouTube (utilise date de modification)
        test_filepath_no_youtube = os.path.join("downloads", "test_no_youtube.mp3")
        with open(test_filepath_no_youtube, 'w') as f:
            f.write("")
        formatted_info_no_youtube = player._format_artist_album_info("Local Artist", "Local Album", test_filepath_no_youtube)
        print(f"   Sans date YouTube (date fichier): {formatted_info_no_youtube}")
        
        # 4. Test de compatibilité avec l'ancien format
        print("4. Test de compatibilité avec l'ancien format...")
        # Simuler l'ancien format (juste une chaîne URL)
        metadata_file = os.path.join("downloads", "youtube_urls.json")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            current_metadata = json.load(f)
        
        # Ajouter une entrée à l'ancien format
        current_metadata["test_old_format.mp3"] = "https://www.youtube.com/watch?v=oldformat"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(current_metadata, f, ensure_ascii=False, indent=2)
        
        # Tester la lecture de l'ancien format
        old_url = player.get_youtube_url_from_metadata("test_old_format.mp3")
        old_metadata = player.get_youtube_metadata("test_old_format.mp3")
        print(f"   URL ancien format: {old_url}")
        print(f"   Métadonnées converties: {old_metadata}")
        
        print("\n=== Vérification du fichier de métadonnées ===")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            all_metadata = json.load(f)
        
        for filename, data in all_metadata.items():
            print(f"   {filename}: {data}")
        
        print("\n✅ Test terminé avec succès!")
        
        # Nettoyer les fichiers de test
        for test_file in [test_filepath, test_filepath_no_youtube]:
            if os.path.exists(test_file):
                os.remove(test_file)
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()

if __name__ == "__main__":
    test_youtube_dates()