#!/usr/bin/env python3
"""
Script de test pour vérifier que le système de surveillance du dossier downloads fonctionne
"""

import os
import time
import shutil

def test_downloads_watcher():
    """Test le système de surveillance du dossier downloads"""
    
    downloads_dir = "downloads"
    test_file = "test_song.mp3"
    test_path = os.path.join(downloads_dir, test_file)
    
    # Créer le dossier downloads s'il n'existe pas
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
    
    print("=== Test du système de surveillance downloads ===")
    print(f"Dossier downloads: {os.path.abspath(downloads_dir)}")
    
    # Compter les fichiers actuels
    audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
    initial_count = 0
    for filename in os.listdir(downloads_dir):
        if filename.lower().endswith(audio_extensions):
            initial_count += 1
    
    print(f"Nombre initial de fichiers: {initial_count}")
    
    # Créer un fichier de test
    print(f"Création du fichier de test: {test_file}")
    with open(test_path, 'w') as f:
        f.write("# Fichier de test MP3 factice")
    
    print("Fichier créé. Le système de surveillance devrait détecter ce changement dans les 2 secondes...")
    print("Vérifiez dans l'application que:")
    print("1. Le bouton 'Téléchargées' affiche le nouveau nombre")
    print("2. Si vous êtes dans l'onglet téléchargées, la liste se recharge automatiquement")
    
    # Attendre un peu
    time.sleep(5)
    
    # Supprimer le fichier de test
    print(f"Suppression du fichier de test: {test_file}")
    if os.path.exists(test_path):
        os.remove(test_path)
    
    print("Fichier supprimé. Le système devrait détecter ce changement aussi...")
    print("Test terminé!")

if __name__ == "__main__":
    test_downloads_watcher()