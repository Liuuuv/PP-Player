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
    for p in [
        os.path.join(os.getcwd(), "build"),
        os.path.join(os.getcwd(), "dist"),
        os.path.join(os.getcwd(), "music_player", "build"),
        os.path.join(os.getcwd(), "music_player", "dist"),
        os.path.join(os.getcwd(), "music_player", "output"),
    ]:
        if os.path.exists(p):
            shutil.rmtree(p)
    
    # Construction avec PyInstaller
    root = os.getcwd()
    hooks_path = os.path.join(root, "pyi_hooks", "alias_init.py")
    assets_dir = os.path.join(root, "music_player", "assets")
    ai_data = os.path.join(root, "music_player", "ai_music_data.json")
    downloads_path_txt = os.path.join(root, "music_player", "downloads_path.txt")

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",            # Dossier avec un .exe
        "--windowed",          # Application fenêtrée (sans console)
        "--name=PipiPlayer",   # Nom de l'exécutable
        f"--icon={os.path.join(assets_dir, 'icon.ico')}",
        f"--add-data={assets_dir};assets",
        f"--add-data={ai_data};.",
        f"--add-data={downloads_path_txt};.",
        "--collect-all=pygame",
        "--collect-data=customtkinter",
        "--collect-all=mutagen",
        "--hidden-import=yt_dlp",
        f"--runtime-hook={hooks_path}",
        os.path.join(root, "music_player", "main.py")  # Point d'entrée
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