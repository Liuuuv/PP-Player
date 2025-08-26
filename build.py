# #!/usr/bin/env python3
# import PyInstaller.__main__
# import os
# import shutil
# import glob
# import sys

# def build_complete():
#     print("🔧 Construction du projet complet...")
    
#     # Nettoyer les builds précédents
#     clean_build_folders()
    
#     # Trouver tous les modules Python du projet
#     python_modules = find_python_modules()
#     print(f"📦 Modules Python trouvés: {python_modules}")
    
#     # Construire l'exécutable avec tous les modules inclus
#     build_command = [
#         "main.py",
#         "--name=PPPlayer",
#         "--onefile",
#         "--windowed",
#         "--clean",
#         "--noconfirm",
#         # Inclure tous les modules Python locaux
#         *[f"--hidden-import={module}" for module in python_modules],
#         # Ajouter le dossier courant au PATH Python pour les imports
#         "--paths=.",
#     ]
    
#     print("🚀 Lancement de PyInstaller...")
#     PyInstaller.__main__.run(build_command)
    
#     # Copier tous les fichiers nécessaires
#     copy_all_files()
    
#     print("✅ Construction terminée avec succès!")
#     print("📦 Exécutable: dist/PPPlayer.exe")

# def find_python_modules():
#     """Trouve tous les modules Python du projet"""
#     modules = []
    
#     # Modules dans le dossier racine
#     for py_file in glob.glob("*.py"):
#         if py_file != "main.py" and should_include(py_file):
#             module_name = os.path.splitext(py_file)[0]
#             modules.append(module_name)
    
#     # Packages (dossiers avec __init__.py)
#     for item in os.listdir():
#         if os.path.isdir(item) and should_include(item):
#             init_file = os.path.join(item, "__init__.py")
#             if os.path.exists(init_file):
#                 modules.append(item)
#                 print(f"📦 Package détecté: {item}")
    
#     return modules

# def copy_all_files():
#     """Copie tous les fichiers nécessaires pour l'exécution"""
#     dist_dir = "dist"
    
#     print("📁 Copie des fichiers...")
    
#     # 1. Copier tous les fichiers Python (nécessaires pour l'importation runtime)
#     for py_file in glob.glob("*.py"):
#         if py_file != "main.py" and should_include(py_file):
#             shutil.copy2(py_file, dist_dir)
#             print(f"🐍 Copié: {py_file}")
    
#     # 2. Copier tous les fichiers de données
#     for pattern in ["*.json", "*.txt", "*.cfg", "*.ini", "*.xml", "*.yml"]:
#         for file in glob.glob(pattern):
#             if should_include(file):
#                 shutil.copy2(file, dist_dir)
#                 print(f"📄 Copié: {file}")
    
#     # 3. Copier tous les dossiers (sauf exclus)
#     for item in os.listdir():
#         if os.path.isdir(item) and should_include(item):
#             # Vérifier si c'est un package Python
#             init_file = os.path.join(item, "__init__.py")
#             if os.path.exists(init_file):
#                 # Pour les packages, copier tout le dossier
#                 dest = os.path.join(dist_dir, item)
#                 if os.path.exists(dest):
#                     shutil.rmtree(dest)
#                 shutil.copytree(item, dest)
#                 print(f"📦 Package copié: {item}/")
#             else:
#                 # Pour les dossiers de données normaux
#                 dest = os.path.join(dist_dir, item)
#                 if os.path.exists(dest):
#                     shutil.rmtree(dest)
#                 shutil.copytree(item, dest)
#                 print(f"📁 Dossier copié: {item}/")

# def clean_build_folders():
#     """Nettoie les dossiers de build précédents"""
#     for folder in ["build", "dist"]:
#         if os.path.exists(folder):
#             shutil.rmtree(folder)
#             print(f"🧹 Nettoyé: {folder}")
    
#     # Nettoyer les fichiers .spec
#     for spec_file in glob.glob("*.spec"):
#         os.remove(spec_file)
#         print(f"🧹 Nettoyé: {spec_file}")

# def should_include(path):
#     """
#     Vérifie si le fichier/dossier doit être inclus
#     """
#     name = os.path.basename(path)
    
#     # Exclusion des fichiers/dossiers système
#     exclude_patterns = {
#         "dist", "build", "__pycache__", 
#         ".git", ".vscode", ".idea",
#         "venv", "env", ".venv", ".env",
#         "node_modules", "temp", "tmp"
#     }
    
#     # Exclure les fichiers/dossiers cachés
#     if name.startswith('.'):
#         return False
    
#     # Exclure les patterns spécifiques
#     if name in exclude_patterns:
#         return False
    
#     # Exclure les extensions spécifiques
#     if name.endswith(('.spec', '.pyc', '.pyo', '.pyd')):
#         return False
    
#     return True

# if __name__ == "__main__":
#     build_complete()


#!/usr/bin/env python3
import PyInstaller.__main__
import os
import shutil
import glob
import sys


def clean_build_folders():
    """Nettoie les dossiers de build précédents"""
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🧹 Nettoyé: {folder}")
    
    # Nettoyer les fichiers .spec
    for spec_file in glob.glob("*.spec"):
        os.remove(spec_file)
        print(f"🧹 Nettoyé: {spec_file}")

#!/usr/bin/env python3
import PyInstaller.__main__
import os
import shutil
import glob

def build_ondir():
    print("🔧 Construction en mode onedir (recommandé)...")
    
    clean_build_folders()
    
    build_command = [
        "main.py",
        "--name=PPPlayer",
        "--onedir",        # ← MODE ONEDIR au lieu de onefile
        "--windowed",
        "--clean",
        "--noconfirm",
        "--paths=.",
        "--hidden-import=config",
        "--hidden-import=player",
        "--hidden-import=utils",
    ]
    
    PyInstaller.__main__.run(build_command)
    print("✅ Construction onedir terminée!")
    print("📦 Dossier complet: dist/PPPlayer/")

if __name__ == "__main__":
    build_ondir()