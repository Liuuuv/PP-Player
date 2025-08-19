#!/usr/bin/env python3
import os
import sys
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError

def test_metadata(filepath):
    """Test les métadonnées d'un fichier MP3"""
    print(f"\n=== Test métadonnées pour: {os.path.basename(filepath)} ===")
    
    if not os.path.exists(filepath):
        print("Fichier non trouvé!")
        return
    
    try:
        # Méthode 1: MP3 avec ID3
        audio = MP3(filepath)
        print(f"Durée: {audio.info.length:.2f}s")
        
        if audio.tags:
            print("Tags ID3 trouvés:")
            for key, value in audio.tags.items():
                print(f"  {key}: {value}")
            
            # Tags spécifiques
            if 'TPE1' in audio.tags:
                print(f"Artiste (TPE1): {audio.tags['TPE1']}")
            if 'TALB' in audio.tags:
                print(f"Album (TALB): {audio.tags['TALB']}")
            if 'TIT2' in audio.tags:
                print(f"Titre (TIT2): {audio.tags['TIT2']}")
        else:
            print("Aucun tag ID3 trouvé")
            
    except ID3NoHeaderError:
        print("Pas d'en-tête ID3")
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Méthode 2: Mutagen générique
    try:
        from mutagen import File
        audio = File(filepath)
        if audio:
            print("\nTags génériques:")
            for key, value in audio.items():
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Erreur mutagen générique: {e}")

if __name__ == "__main__":
    downloads_dir = "downloads"
    
    # Tester quelques fichiers
    if os.path.exists(downloads_dir):
        files = [f for f in os.listdir(downloads_dir) if f.lower().endswith('.mp3')]
        
        if files:
            # Tester les 3 premiers fichiers
            for i, filename in enumerate(files[:3]):
                filepath = os.path.join(downloads_dir, filename)
                test_metadata(filepath)
        else:
            print("Aucun fichier MP3 trouvé dans le dossier downloads")
    else:
        print("Dossier downloads non trouvé")