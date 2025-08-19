#!/usr/bin/env python3
"""
Script de test pour vérifier la fonctionnalité de changement de dossier de téléchargements
"""

import os
import sys

def test_downloads_path_loading():
    """Test le chargement du chemin personnalisé"""
    
    # Simuler la méthode _load_downloads_path
    def _load_downloads_path():
        try:
            config_file = os.path.join(os.getcwd(), "downloads_path.txt")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_path = f.read().strip()
                if custom_path and os.path.exists(custom_path):
                    return custom_path
        except Exception as e:
            print(f"Erreur lors du chargement du chemin personnalisé: {e}")
        
        # Retourner le chemin par défaut si aucun chemin personnalisé n'est trouvé
        default_path = os.path.join(os.getcwd(), "downloads")
        os.makedirs(default_path, exist_ok=True)
        return default_path
    
    # Test 1: Vérifier le chemin par défaut
    print("=== Test 1: Chemin par défaut ===")
    downloads_folder = _load_downloads_path()
    print(f"Dossier de téléchargements: {downloads_folder}")
    print(f"Existe: {os.path.exists(downloads_folder)}")
    
    # Test 2: Créer un fichier de configuration personnalisé
    print("\n=== Test 2: Chemin personnalisé ===")
    test_path = os.path.join(os.getcwd(), "test_downloads")
    os.makedirs(test_path, exist_ok=True)
    
    config_file = os.path.join(os.getcwd(), "downloads_path.txt")
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(test_path)
    
    downloads_folder = _load_downloads_path()
    print(f"Dossier de téléchargements personnalisé: {downloads_folder}")
    print(f"Correspond au test: {downloads_folder == test_path}")
    
    # Nettoyer
    if os.path.exists(config_file):
        os.remove(config_file)
    if os.path.exists(test_path):
        os.rmdir(test_path)
    
    print("\n=== Test terminé ===")

def test_icon_exists():
    """Vérifier que l'icône existe"""
    icon_path = os.path.join(os.getcwd(), "assets", "select_downloads_folder.png")
    print(f"=== Test icône ===")
    print(f"Chemin de l'icône: {icon_path}")
    print(f"Icône existe: {os.path.exists(icon_path)}")
    
    if not os.path.exists(icon_path):
        print("ATTENTION: L'icône select_downloads_folder.png n'existe pas!")
        print("Vérifiez que le fichier est présent dans le dossier assets/")

if __name__ == "__main__":
    print("Test de la fonctionnalité de changement de dossier de téléchargements")
    print("=" * 70)
    
    test_downloads_path_loading()
    test_icon_exists()