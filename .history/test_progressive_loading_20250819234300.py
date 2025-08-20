#!/usr/bin/env python3
"""
Script de test pour le chargement progressif des téléchargements
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Simuler une classe parent minimale
class MockParent:
    def __init__(self):
        self.root = None

# Importer la classe
from library_tab.downloads import DownloadsProgressiveLoader

def test_progressive_loader():
    """Test de base du chargement progressif"""
    print("=== Test du chargement progressif ===")
    
    # Créer un parent fictif
    parent = MockParent()
    
    # Créer le loader
    loader = DownloadsProgressiveLoader(parent)
    
    # Créer une liste de fichiers fictifs
    test_files = [f"fichier_{i:03d}.mp3" for i in range(100)]
    
    # Initialiser avec 50 fichiers et load_count=10
    loader.load_count = 10
    loader.initialize(test_files)
    
    print(f"Fichiers totaux: {len(test_files)}")
    print(f"Load count: {loader.load_count}")
    
    # Vérifier l'initialisation
    stats = loader.get_stats()
    print(f"Après initialisation: {stats}")
    
    # Tester le chargement progressif
    iteration = 1
    while loader.can_load_more():
        print(f"\n--- Itération {iteration} ---")
        new_files = loader.load_more()
        print(f"Nouveaux fichiers chargés: {len(new_files)}")
        
        stats = loader.get_stats()
        print(f"Statistiques: {stats}")
        
        iteration += 1
        
        # Éviter une boucle infinie
        if iteration > 15:
            break
    
    print("\n=== Test terminé ===")
    print(f"Tous les fichiers ont été chargés: {not loader.can_load_more()}")

if __name__ == "__main__":
    test_progressive_loader()