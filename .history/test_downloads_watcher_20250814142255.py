#!/usr/bin/env python3
"""
Script de test pour vérifier que le système de surveillance du dossier downloads fonctionne
pour les ajouts ET les suppressions de fichiers
"""

import os
import time
import shutil

def test_downloads_watcher():
    """Test le système de surveillance du dossier downloads"""
    
    downloads_dir = "downloads"
    test_files = ["test_song_1.mp3", "test_song_2.wav", "test_song_3.flac"]
    
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
    
    # Test 1: Ajouter des fichiers un par un
    print("\n--- Test 1: Ajout de fichiers ---")
    for i, test_file in enumerate(test_files):
        test_path = os.path.join(downloads_dir, test_file)
        print(f"Création du fichier {i+1}/3: {test_file}")
        with open(test_path, 'w') as f:
            f.write(f"# Fichier de test {test_file} factice")
        
        print("Fichier créé. Le système devrait détecter ce changement dans les 2 secondes...")
        print("Vérifiez dans l'application que:")
        print("1. Le bouton 'Téléchargées' affiche le nouveau nombre")
        print("2. Si vous êtes dans l'onglet téléchargées, la liste se recharge automatiquement")
        
        # Attendre pour voir la détection
        time.sleep(3)
    
    print(f"\nTous les fichiers créés. Total attendu: {initial_count + len(test_files)}")
    
    # Test 2: Supprimer des fichiers un par un
    print("\n--- Test 2: Suppression de fichiers ---")
    for i, test_file in enumerate(test_files):
        test_path = os.path.join(downloads_dir, test_file)
        if os.path.exists(test_path):
            print(f"Suppression du fichier {i+1}/3: {test_file}")
            os.remove(test_path)
            
            print("Fichier supprimé. Le système devrait détecter ce changement...")
            print("Vérifiez que l'onglet téléchargées se recharge automatiquement")
            
            # Attendre pour voir la détection
            time.sleep(3)
    
    print(f"\nTous les fichiers supprimés. Total attendu: {initial_count}")
    print("\n=== Test terminé! ===")
    print("Le système de surveillance devrait avoir détecté tous les changements.")

if __name__ == "__main__":
    test_downloads_watcher()