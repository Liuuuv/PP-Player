#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier les chemins de téléchargements
"""

import os

def check_downloads_paths():
    """Vérifie tous les chemins liés aux téléchargements"""
    
    print("=== DIAGNOSTIC DES CHEMINS DE TÉLÉCHARGEMENTS ===")
    
    # 1. Vérifier le fichier de configuration
    config_file = "downloads_path.txt"
    print(f"\n1. Fichier de configuration: {config_file}")
    print(f"   Existe: {os.path.exists(config_file)}")
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                custom_path = f.read().strip()
            print(f"   Contenu: '{custom_path}'")
            print(f"   Dossier existe: {os.path.exists(custom_path)}")
            
            # Vérifier le contenu du dossier personnalisé
            if os.path.exists(custom_path):
                files = [f for f in os.listdir(custom_path) if f.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a'))]
                print(f"   Fichiers audio: {len(files)}")
                if files:
                    print(f"   Exemples: {files[:3]}")
                
                # Vérifier le cache
                cache_dir = os.path.join(custom_path, ".cache")
                print(f"   Cache existe: {os.path.exists(cache_dir)}")
                if os.path.exists(cache_dir):
                    thumbnails_dir = os.path.join(cache_dir, "thumbnails")
                    print(f"   Thumbnails cache existe: {os.path.exists(thumbnails_dir)}")
        except Exception as e:
            print(f"   Erreur lecture: {e}")
    
    # 2. Vérifier le dossier par défaut
    default_path = os.path.join(os.getcwd(), "downloads")
    print(f"\n2. Dossier par défaut: {default_path}")
    print(f"   Existe: {os.path.exists(default_path)}")
    
    if os.path.exists(default_path):
        files = [f for f in os.listdir(default_path) if f.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a'))]
        print(f"   Fichiers audio: {len(files)}")
        if files:
            print(f"   Exemples: {files[:3]}")
        
        # Vérifier le cache
        cache_dir = os.path.join(default_path, ".cache")
        print(f"   Cache existe: {os.path.exists(cache_dir)}")
        if os.path.exists(cache_dir):
            thumbnails_dir = os.path.join(cache_dir, "thumbnails")
            print(f"   Thumbnails cache existe: {os.path.exists(thumbnails_dir)}")
    
    # 3. Simuler le chargement du chemin comme dans l'application
    print(f"\n3. Simulation du chargement:")
    
    def _load_downloads_path():
        try:
            config_file = "downloads_path.txt"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_path = f.read().strip()
                if custom_path and os.path.exists(custom_path):
                    return custom_path
        except Exception as e:
            print(f"   Erreur lors du chargement du chemin personnalisé: {e}")
        
        # Retourner le chemin par défaut si aucun chemin personnalisé n'est trouvé
        default_path = os.path.join(os.getcwd(), "downloads")
        os.makedirs(default_path, exist_ok=True)
        return default_path
    
    loaded_path = _load_downloads_path()
    print(f"   Chemin chargé: {loaded_path}")
    print(f"   Chemin existe: {os.path.exists(loaded_path)}")

if __name__ == "__main__":
    check_downloads_paths()