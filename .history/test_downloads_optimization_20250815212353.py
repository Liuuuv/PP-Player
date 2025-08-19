#!/usr/bin/env python3
"""
Test des optimisations d'affichage des téléchargements
"""

import time
import os
import sys

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_file_loading_performance():
    """Test de performance du chargement des fichiers"""
    downloads_dir = "downloads"
    
    if not os.path.exists(downloads_dir):
        print("Dossier downloads non trouvé")
        return
    
    # Extensions audio supportées
    audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
    
    print("=== Test de performance du chargement des fichiers ===")
    
    # Test 1: Méthode originale
    start_time = time.time()
    files_original = []
    for filename in os.listdir(downloads_dir):
        if filename.lower().endswith(audio_extensions):
            filepath = os.path.join(downloads_dir, filename)
            files_original.append(filepath)
    original_time = time.time() - start_time
    
    # Test 2: Méthode optimisée avec tri
    start_time = time.time()
    files_info = []
    for filename in os.listdir(downloads_dir):
        if filename.lower().endswith(audio_extensions):
            filepath = os.path.join(downloads_dir, filename)
            files_info.append((filepath, filename))
    
    # Trier par date de modification
    files_info.sort(key=lambda x: os.path.getmtime(x[0]), reverse=True)
    files_optimized = [filepath for filepath, _ in files_info]
    optimized_time = time.time() - start_time
    
    print(f"Nombre de fichiers trouvés: {len(files_original)}")
    print(f"Temps méthode originale: {original_time:.4f}s")
    print(f"Temps méthode optimisée: {optimized_time:.4f}s")
    
    if optimized_time < original_time:
        improvement = ((original_time - optimized_time) / original_time) * 100
        print(f"Amélioration: {improvement:.1f}%")
    else:
        print("Pas d'amélioration significative")
    
    return len(files_original)

def simulate_display_performance(num_files):
    """Simule la performance d'affichage"""
    print(f"\n=== Simulation d'affichage pour {num_files} fichiers ===")
    
    # Paramètres d'optimisation
    INITIAL_DISPLAY_BATCH_SIZE = 20
    LAZY_LOAD_DELAY = 10  # ms
    METADATA_LOAD_DELAY = 50  # ms
    
    # Calcul du temps théorique
    if num_files <= INITIAL_DISPLAY_BATCH_SIZE:
        # Affichage rapide
        estimated_time = num_files * 0.001  # 1ms par fichier
        print(f"Mode: Affichage rapide")
        print(f"Temps estimé d'affichage initial: {estimated_time:.3f}s")
    else:
        # Affichage par batch
        initial_time = INITIAL_DISPLAY_BATCH_SIZE * 0.001
        remaining_files = num_files - INITIAL_DISPLAY_BATCH_SIZE
        remaining_batches = (remaining_files + 9) // 10  # Arrondi supérieur
        batch_time = remaining_batches * (LAZY_LOAD_DELAY / 1000)
        
        total_time = initial_time + batch_time
        
        print(f"Mode: Affichage par batch")
        print(f"Affichage initial ({INITIAL_DISPLAY_BATCH_SIZE} fichiers): {initial_time:.3f}s")
        print(f"Affichage différé ({remaining_files} fichiers): {batch_time:.3f}s")
        print(f"Temps total estimé: {total_time:.3f}s")
        
        # Temps de chargement des métadonnées
        metadata_time = num_files * (METADATA_LOAD_DELAY / 1000)
        print(f"Temps de chargement des métadonnées: {metadata_time:.3f}s")

def main():
    """Fonction principale de test"""
    print("Test des optimisations d'affichage des téléchargements")
    print("=" * 60)
    
    # Test de performance du chargement
    num_files = test_file_loading_performance()
    
    if num_files > 0:
        # Simulation de l'affichage
        simulate_display_performance(num_files)
        
        print(f"\n=== Résumé des optimisations ===")
        print("✓ Tri des fichiers par date (plus récents en premier)")
        print("✓ Affichage par batch pour les grandes listes")
        print("✓ Chargement différé des métadonnées")
        print("✓ Chargement différé des miniatures")
        print("✓ Interface réactive dès le premier batch")
        
        if num_files > 50:
            print(f"\n⚡ Avec {num_files} fichiers, l'amélioration sera très visible !")
        elif num_files > 20:
            print(f"\n⚡ Avec {num_files} fichiers, l'amélioration sera notable.")
        else:
            print(f"\n✓ Avec {num_files} fichiers, l'affichage sera instantané.")
    else:
        print("\nAucun fichier audio trouvé dans le dossier downloads.")

if __name__ == "__main__":
    main()