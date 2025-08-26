#!/usr/bin/env python3
import os
import shutil
import glob
import subprocess
import sys
import venv

def build_with_venv():
    print("🔧 Construction avec environnement virtuel...")
    
    # Nettoyer les builds précédents
    clean_build_folders()
    
    # Chemin de l'environnement virtuel
    venv_path = "build_venv"
    
    # Vérifier si l'environnement existe déjà
    if not os.path.exists(venv_path):
        # Créer l'environnement virtuel s'il n'existe pas
        create_virtual_environment(venv_path)
        # Installer les dépendances
        install_dependencies(venv_path)
    else:
        print(f"✅ Utilisation de l'environnement virtuel existant: {venv_path}")
        # Vérifier et installer les dépendances manquantes
        check_dependencies(venv_path)
    
    # Construire avec PyInstaller depuis l'environnement virtuel
    build_with_pyinstaller(venv_path)
    
    # Copier les ressources supplémentaires après la construction
    copy_additional_resources()
    
    print("✅ Construction terminée avec environnement virtuel!")
    print("📦 Dossier complet: dist/PPPlayer/")

def copy_additional_resources():
    """Copie les ressources supplémentaires dans le dossier de l'application"""
    print("📁 Copie des ressources supplémentaires...")
    
    dist_dir = "dist/PPPlayer"
    
    # Liste des dossiers et fichiers à copier
    resources_to_copy = [
        ("assets", os.path.isdir),
        # ("player_config.json", os.path.isfile),
        # ("ai_music_data.json", os.path.isfile),
    ]
    
    for resource, check_func in resources_to_copy:
        if check_func(os.path.join("src", resource)):
            destination = os.path.join(dist_dir, resource)
            resource = os.path.join("src", resource)
            if os.path.isdir(resource):
                # Copier un dossier
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                shutil.copytree(resource, destination)
                print(f"✅ Dossier copié: {resource}")
            else:
                # Copier un fichier
                shutil.copy2(resource, dist_dir)
                print(f"✅ Fichier copié: {resource}")
        else:
            print(f"⚠️  Ressource non trouvée: {resource}")
    
    print("✅ Ressources supplémentaires copiées")

def create_virtual_environment(venv_path):
    """Crée un environnement virtuel propre"""
    print(f"🐍 Création de l'environnement virtuel: {venv_path}")
    venv.create(venv_path, with_pip=True)
    print("✅ Environnement virtuel créé")

def install_dependencies(venv_path):
    """Installe les dépendances dans l'environnement virtuel"""
    print("📦 Installation des dépendances...")
    
    # Activer le venv et installer les dépendances
    pip_path = get_pip_path(venv_path)
    
    # Installer PyInstaller et les dépendances
    dependencies = ["pyinstaller"] + get_project_dependencies()
    for dep in dependencies:
        try:
            subprocess.run([pip_path, "install", dep], check=True, capture_output=True)
            print(f"✅ Installé: {dep}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Erreur lors de l'installation de {dep}: {e.stderr.decode() if e.stderr else 'Unknown error'}")
    
    print("✅ Dépendances installées")

def check_dependencies(venv_path):
    """Vérifie et installe les dépendances manquantes"""
    print("🔍 Vérification des dépendances...")
    
    pip_path = get_pip_path(venv_path)
    dependencies = ["pyinstaller"] + get_project_dependencies()
    
    for dep in dependencies:
        try:
            # Vérifier si le package est déjà installé
            result = subprocess.run([pip_path, "show", dep], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                print(f"📦 Installation de {dep}...")
                subprocess.run([pip_path, "install", dep], check=True, capture_output=True)
                print(f"✅ Installé: {dep}")
            else:
                print(f"✅ Déjà installé: {dep}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur avec {dep}: {e.stderr.decode() if e.stderr else 'Unknown error'}")
    
    print("✅ Vérification des dépendances terminée")

def get_pip_path(venv_path):
    """Retourne le chemin vers pip selon l'OS"""
    if os.name == 'nt':  # Windows
        return os.path.join(venv_path, "Scripts", "pip.exe")
    else:  # Linux/Mac
        return os.path.join(venv_path, "bin", "pip")

def get_project_dependencies():
    """Retourne les dépendances du projet"""
    # Seulement les dépendances externes (pas les modules standards)
    return [
        "pygame",
        "customtkinter",
        "requests",
        "yt-dlp",  # Note: yt_dlp s'installe avec yt-dlp
        "pillow",  # PIL est maintenant pillow
        "numpy",
        "mutagen",  # Installer seulement mutagen, pas mutagen.mp3
        "ytmusicapi",
        "bs4"
    ]

def build_with_pyinstaller(venv_path):
    """Lance PyInstaller depuis l'environnement virtuel"""
    print("🚀 Lancement de PyInstaller depuis le venv...")
    
    if os.name == 'nt':  # Windows
        pyinstaller_path = os.path.join(venv_path, "Scripts", "pyinstaller.exe")
        data_sep = ';'
    else:  # Linux/Mac
        pyinstaller_path = os.path.join(venv_path, "bin", "pyinstaller")
        data_sep = ';'
    
    build_command = [
        pyinstaller_path,
        "src/main.py",
        "--name=PPPlayer",
        "--onedir",
        "--windowed", # sans console
        # "--console", # avec console
        "--clean",
        "--noconfirm",
        "--paths=src",
        "--hidden-import=config",
        "--hidden-import=player",
        "--hidden-import=utils",
        # Hidden imports nécessaires
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=mutagen",
        "--hidden-import=mutagen.mp3",
        "--hidden-import=yt_dlp",
        "--hidden-import=customtkinter",
        "--hidden-import=tkinter",  # Important pour customtkinter
        "--hidden-import=ffmpeg",
        # Options pour réduire la taille
        "--exclude-module=matplotlib",
        "--exclude-module=pandas",
        "--exclude-module=scipy",
    ]
    
    # Ajouter le dossier ffmpeg au build si présent (placé à la racine du projet)
    if os.path.isdir("ffmpeg"):
        print("Ajout du dossier ffmpeg au build...")
        build_command += ["--add-data", f"ffmpeg{data_sep}ffmpeg"]
    else:
        print("Aucun dossier ffmpeg trouvé, aucune option de build pour ffmpeg ajoutée")
    
    try:
        subprocess.run(build_command, check=True)
        print("✅ PyInstaller a terminé avec succès")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de PyInstaller: {e}")
        sys.exit(1)

def clean_build_folders():
    """Nettoie les dossiers de build"""
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🧹 Nettoyé: {folder}")
    
    for spec_file in glob.glob("*.spec"):
        os.remove(spec_file)
        print(f"🧹 Nettoyé: {spec_file}")

def clean_virtual_environment(venv_path):
    """Nettoie l'environnement virtuel après construction"""
    choice = input("Voulez-vous supprimer l'environnement virtuel? (o/n): ")
    if choice.lower() in ['o', 'oui', 'y', 'yes']:
        shutil.rmtree(venv_path)
        print("🧹 Environnement virtuel supprimé")
    else:
        print(f"📁 Environnement virtuel conservé: {venv_path}")

if __name__ == "__main__":
    build_with_venv()