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
    
    # Construire avec Nuitka depuis l'environnement virtuel
    build_with_nuitka(venv_path)
    
    # Copier les ressources supplémentaires après la construction
    copy_additional_resources()
    
    print("✅ Construction terminée avec environnement virtuel!")
    print("📦 Dossier complet: dist/PPPlayer/")

def copy_additional_resources():
    """Copie les ressources supplémentaires dans le dossier de l'application"""
    print("📁 Copie des ressources supplémentaires...")
    
    dist_dir = "dist/PPPlayer"
    
    # Créer le dossier dist s'il n'existe pas
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # Liste des dossiers et fichiers à copier
    resources_to_copy = [
        ("assets", os.path.isdir),
        ("player_config.json", os.path.isfile),
        ("ai_music_data.json", os.path.isfile),
    ]
    
    for resource, check_func in resources_to_copy:
        if check_func(resource):
            destination = os.path.join(dist_dir, resource)
            
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
    
    # Installer Nuitka et les dépendances
    dependencies = ["nuitka"] + get_project_dependencies()
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
    dependencies = ["nuitka"] + get_project_dependencies()
    
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

def get_python_path(venv_path):
    """Retourne le chemin vers python selon l'OS"""
    if os.name == 'nt':  # Windows
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Linux/Mac
        return os.path.join(venv_path, "bin", "python")

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

def build_with_nuitka(venv_path):
    """Lance Nuitka depuis l'environnement virtuel"""
    print("🚀 Lancement de Nuitka depuis le venv...")
    
    # Utiliser le Python du venv pour exécuter Nuitka en module
    python_path = get_python_path(venv_path)
    
    # Options de base pour Nuitka
    build_command = [
        python_path,
        "-m",
        "nuitka",
        "--standalone",
        "--onefile",
        "--windows-console-mode=disable",  # Nouvelle option pour désactiver la console
        "--output-dir=dist",
        "--output-filename=PPPlayer.exe" if os.name == 'nt' else "--output-filename=PPPlayer",

        # OPTIONS DE CACHE POUR ACCÉLÉRER LES PROCHAINES COMPILATIONS
        "--enable-cache",  # Active le cache des compilations
        "--cache-dir=nuitka_cache",  # Dossier dédié pour le cache
        # "--remove-output",  # REMPLACÉ pour conserver les fichiers temporaires utiles
        
        "--enable-plugin=tk-inter",
        "--include-package=config",
        "--include-package=player",
        "--include-package=utils",
        "--include-package=PIL",
        "--include-package=mutagen",
        "--include-package=yt_dlp",
        "--include-package=customtkinter",
        "--include-package-data=customtkinter",
        "--include-package-data=PIL",
        "--include-module=config",
        "--include-module=player",
        "--include-module=utils",
        "--follow-imports",  # Inclure tous les imports
        # Ajoutez ces options pour plus de verbosité :
        "--show-progress",  # Montre la progression de la compilation
        "--show-memory",    # Affiche l'utilisation mémoire
        "--verbose",        # Sortie détaillée
    ]
    
    # Ajouter les données supplémentaires (comme ffmpeg) seulement si le dossier existe et n'est pas vide
    ffmpeg_dir = "ffmpeg"
    if os.path.isdir(ffmpeg_dir) and os.listdir(ffmpeg_dir):
        print("✅ Ajout du dossier ffmpeg au build...")
        build_command.append("--include-data-dir=ffmpeg=ffmpeg")
    else:
        print("⚠️  Dossier ffmpeg non trouvé ou vide, ignoré")
    
    # Fichier principal à compiler
    build_command.append("main.py")
    
    try:
        print("🔨 Compilation avec Nuitka...")
        print(f"Commande exécutée: {' '.join(build_command)}")
        
        # Exécuter avec affichage en temps réel
        process = subprocess.Popen(
            build_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Fusionner stderr dans stdout
            universal_newlines=True,
            bufsize=1
        )
        
        # Afficher la sortie en temps réel
        print("\n--- Début de la compilation Nuitka ---")
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Attendre la fin du processus et récupérer le code de retour
        return_code = process.wait()
        
        if return_code == 0:
            print("✅ Nuitka a terminé avec succès")
        else:
            raise subprocess.CalledProcessError(return_code, build_command)
        
        # Nuitka crée un exécutable directement dans dist/
        exe_name = "PPPlayer.exe" if os.name == 'nt' else "PPPlayer"
        exe_path = os.path.join("dist", exe_name)
        
        if os.path.exists(exe_path):
            print(f"✅ Exécutable créé: {exe_path}")
            
            # Créer le dossier PPPlayer et déplacer l'exécutable dedans
            ppplayer_dir = "dist/PPPlayer"
            if not os.path.exists(ppplayer_dir):
                os.makedirs(ppplayer_dir)
            
            destination_exe = os.path.join(ppplayer_dir, exe_name)
            shutil.move(exe_path, destination_exe)
            print(f"✅ Exécutable déplacé vers: {destination_exe}")
            
        else:
            print("⚠️  Exécutable non trouvé dans dist/")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de Nuitka: {e}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        print("Assurez-vous que Nuitka est correctement installé dans l'environnement virtuel")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ Fichier non trouvé: {e}")
        print("Vérifiez les chemins de l'environnement virtuel")
        sys.exit(1)

def clean_build_folders():
    """Nettoie les dossiers de build"""
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🧹 Nettoyé: {folder}")
    
    # Nettoyer aussi les fichiers .build générés par Nuitka
    for build_dir in glob.glob("*.build"):
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
            print(f"🧹 Nettoyé: {build_dir}")
    
    # Nettoyer les fichiers .dist (anciennes versions de Nuitka)
    for dist_dir in glob.glob("*.dist"):
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
            print(f"🧹 Nettoyé: {dist_dir}")
    
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
    # Optionnel: nettoyer l'environnement virtuel après construction
    # clean_virtual_environment("build_venv")