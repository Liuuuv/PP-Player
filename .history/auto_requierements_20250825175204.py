# auto_requirements.py
import ast
import os
import subprocess
import sys
import importlib
import re

def should_ignore_path(path):
    """
    Détermine si un chemin doit être ignoré lors du scan
    """
    ignore_patterns = [
        # Dossiers à ignorer
        r'__pycache__', r'\.venv', r'venv', r'env', r'\.git', 
        r'\.vscode', r'\.idea', r'\.history', r'node_modules',
        r'build', r'dist', r'\.pytest_cache', r'\.mypy_cache',
        r'\.hypothesis', r'\.tox', r'\.eggs', r'\.ruff_cache',
        
        # Fichiers à ignorer
        r'\.pyc$', r'\.pyo$', r'\.pyd$', r'\.so$', r'\.dll$',
        r'\.exe$', r'\.bin$', r'\.db$', r'\.sqlite$', r'\.log$',
        r'\.cache$', r'\.swp$', r'\.swo$', r'~$',
        
        # Fichiers de configuration et autres
        r'requirements\.txt$', r'pyproject\.toml$', r'setup\.cfg$',
        r'\.gitignore$', r'\.dockerignore$', r'\.env', r'\.ini$',
        r'\.toml$', r'\.json$', r'\.yaml$', r'\.yml$', r'\.xml$',
        r'\.html$', r'\.css$', r'\.js$', r'\.md$', r'\.txt$',
        r'\.csv$', r'\.tsv$', r'\.xlsx$', r'\.pdf$', r'\.jpg$',
        r'\.png$', r'\.gif$', r'\.ico$', r'\.svg$', r'\.mp3$',
        r'\.wav$', r'\.mp4$', r'\.avi$', r'\.zip$', r'\.tar$',
        r'\.gz$', r'\.rar$', r'\.7z$',
    ]
    
    path = os.path.normpath(path)
    
    # Vérifier tous les patterns d'ignorance
    for pattern in ignore_patterns:
        if re.search(pattern, path):
            return True
    
    # Ignorer les fichiers cachés (commençant par .)
    if any(part.startswith('.') for part in path.split(os.sep)):
        return True
    
    return False

def extract_imports(file_path):
    """Extrait tous les imports d'un fichier Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
        except:
            print(f"⚠️  Impossible de lire {file_path}")
            return set()
    except Exception as e:
        print(f"⚠️  Erreur lecture {file_path}: {e}")
        return set()
    
    imports = set()
    
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:  # Ignorer les imports relatifs
                    imports.add(node.module.split('.')[0])
    except SyntaxError as e:
        print(f"⚠️  SyntaxError dans {file_path}: {e}")
    except Exception as e:
        print(f"⚠️  Erreur AST dans {file_path}: {e}")
    
    return imports

def scan_project_imports():
    """Scan tous les fichiers Python du projet pour trouver les imports"""
    project_imports = set()
    scanned_files = 0
    
    print("🔍 Scan des fichiers Python...")
    
    for root, dirs, files in os.walk('.'):
        # Modifier dirs in-place pour ignorer les dossiers indésirables
        dirs[:] = [d for d in dirs if not should_ignore_path(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            if should_ignore_path(file_path):
                continue
                
            if file.endswith('.py'):
                try:
                    imports = extract_imports(file_path)
                    project_imports.update(imports)
                    scanned_files += 1
                except Exception as e:
                    print(f"⚠️  Erreur traitement {file_path}: {e}")
    
    print(f"📊 {scanned_files} fichiers Python analysés")
    return project_imports

def filter_std_libs(imports):
    """Filtre les bibliothèques standards de Python"""
    std_libs = set(sys.stdlib_module_names)
    
    # Ajouter d'autres modules standards courants
    extra_std_libs = {
        'tkinter', 'xml', 'json', 'sqlite3', 'ssl', 'hashlib',
        'datetime', 'math', 're', 'os', 'sys', 'threading',
        'subprocess', 'pathlib', 'collections', 'itertools',
        'functools', 'logging', 'urllib', 'http', 'email'
    }
    std_libs.update(extra_std_libs)
    
    return {imp for imp in imports if imp not in std_libs and not imp.startswith('_')}

def get_installed_packages():
    """Retourne la liste des packages installés"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format', 'freeze'], 
                              capture_output=True, text=True, check=True)
        installed_packages = set()
        for line in result.stdout.splitlines():
            if '==' in line:
                installed_packages.add(line.split('==')[0].lower())
        return installed_packages
    except:
        return set()

def auto_install_requirements():
    """Installe automatiquement les dépendances manquantes"""
    print("🔍 Analyse automatique des dépendances...")
    print("⏳ Cette opération peut prendre quelques secondes...")
    
    # Scanner tous les imports
    all_imports = scan_project_imports()
    external_imports = filter_std_libs(all_imports)
    
    if not external_imports:
        print("✅ Aucune dépendance externe détectée")
        return True
    
    print(f"📦 Dépendances détectées: {', '.join(sorted(external_imports))}")
    
    # Obtenir les packages déjà installés
    installed_packages = get_installed_packages()
    
    # Trouver les dépendances manquantes
    missing_deps = [dep for dep in external_imports if dep.lower() not in installed_packages]
    
    if not missing_deps:
        print("✅ Toutes les dépendances sont déjà installées")
        return True
    
    print(f"⚠️  Dépendances manquantes: {', '.join(missing_deps)}")
    
    # Demander confirmation à l'utilisateur
    if hasattr(sys, 'frozen'):  # Si exécuté en .exe, pas de input()
        response = 'y'
    else:
        response = input("🚀 Voulez-vous installer les dépendances manquantes? (O/n): ").strip().lower()
    
    if response in ('', 'o', 'oui', 'y', 'yes'):
        print(f"📦 Installation de {len(missing_deps)} dépendances...")
        try:
            # Installer toutes les dépendances en une fois
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_deps)
            print("✅ Toutes les dépendances ont été installées avec succès!")
            
            # Redémarrer pour charger les nouvelles dépendances
            if not hasattr(sys, 'frozen'):
                print("🔄 Redémarrage de l'application...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation: {e}")
            print("💡 Essayez d'installer manuellement: pip install " + " ".join(missing_deps))
            return False
    else:
        print("❌ Installation annulée par l'utilisateur")
        return False

def generate_requirements_file():
    """Génère un fichier requirements.txt automatiquement"""
    print("📝 Génération du fichier requirements.txt...")
    
    all_imports = scan_project_imports()
    external_imports = filter_std_libs(all_imports)
    
    if external_imports:
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            for dep in sorted(external_imports):
                f.write(f"{dep}\n")
        print(f"✅ Fichier requirements.txt généré avec {len(external_imports)} dépendances")
    else:
        print("ℹ️  Aucune dépendance externe détectée pour requirements.txt")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'generate':
        generate_requirements_file()
    else:
        auto_install_requirements()