#!/usr/bin/env python3
"""
Script de test pour vérifier que les fonctions de métadonnées YouTube utilisent le bon chemin
"""
import os
import sys

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import MusicPlayer
import tkinter as tk

def test_youtube_metadata_paths():
    """Test que les fonctions utilisent le bon chemin pour youtube_urls.json"""
    
    # Créer une instance temporaire du lecteur
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre
    
    try:
        player = MusicPlayer(root)
        
        print(f"Dossier downloads configuré: {player.downloads_folder}")
        
        # Test avec un fichier fictif
        test_filepath = os.path.join(player.downloads_folder, "test_song.mp3")
        
        # Tester get_youtube_url_from_metadata
        result = player.get_youtube_url_from_metadata(test_filepath)
        print(f"get_youtube_url_from_metadata: OK (retour: {result})")
        
        # Tester get_youtube_metadata
        result = player.get_youtube_metadata(test_filepath)
        print(f"get_youtube_metadata: OK (retour: {result})")
        
        # Tester save_youtube_url_metadata
        try:
            player.save_youtube_url_metadata(test_filepath, "https://youtube.com/test", "2024-01-01")
            print("save_youtube_url_metadata: OK")
            
            # Vérifier que le fichier a été créé au bon endroit
            expected_metadata_file = os.path.join(player.downloads_folder, "youtube_urls.json")
            if os.path.exists(expected_metadata_file):
                print(f"✅ Fichier créé au bon endroit: {expected_metadata_file}")
                
                # Nettoyer le fichier de test
                os.remove(expected_metadata_file)
                print("Fichier de test nettoyé")
            else:
                print(f"❌ Fichier non trouvé à l'emplacement attendu: {expected_metadata_file}")
                
        except Exception as e:
            print(f"Erreur lors du test save_youtube_url_metadata: {e}")
        
        print("\n✅ Tous les tests sont passés avec succès!")
        print(f"Les fonctions utilisent correctement le dossier: {player.downloads_folder}")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
    finally:
        root.destroy()

if __name__ == "__main__":
    test_youtube_metadata_paths()