#!/usr/bin/env python3
"""
Script pour builder l'application en .exe avec PyInstaller
"""
import os
import subprocess
import sys
import shutil

def build_exe():
    """Construit l'application en .exe autonome"""
    print("Construction du lecteur de musique...")
    
    # Installation de PyInstaller si nécessaire
    try:
        import PyInstaller
    except ImportError:
        print("Installation de PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Nettoyer les builds précédents
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Construction avec PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",           # Créer un seul fichier exécutable
        "--windowed",          # Application fenêtrée (sans console)
        "--name=MusicPlayer",  # Nom de l'exécutable
        "--noupx",            # Désactiver UPX pour éviter les alertes antivirus
        "--add-data=version.txt;.",  # Inclure le fichier version
        "--hidden-import=music_player.utils",  # Forcer l'importation des modules
        "--hidden-import=music_player.player",
        "--paths=music_player",  # Ajouter le chemin du package
        "music_player/main.py"   # Point d'entrée
    ]
    
    print("Exécution: " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Construction terminée avec succès!")
        print("L'exécutable se trouve dans le dossier 'dist'")
    else:
        print("Erreur lors de la construction:")
        print(result.stderr)

if __name__ == "__main__":
    build_exe()