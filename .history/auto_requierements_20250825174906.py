# auto_requirements.py
import ast
import os
import subprocess
import sys
import importlib

def extract_imports(file_path):
    """Extrait tous les imports d'un fichier Python"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    imports = set()
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    
    return imports

def scan_project_imports():
    """Scan tous les fichiers Python du projet pour trouver les imports"""
    project_imports = set()
    
    for root, dirs, files in os.walk('.'):
        # Ignorer les dossiers inutiles
        if any(ignore in root for ignore in ['venv', '.venv', '__pycache__', '.git', 'build', 'dist']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    imports = extract_imports(file_path)
                    project_imports.update(imports)
                except Exception as e:
                    print(f"⚠️  Erreur lecture {file_path}: {e}")
    
    return project_imports

def filter_std_libs(imports):
    """Filtre les bibliothèques standards de Python"""
    std_libs = set(sys.stdlib_module_names)
    return {imp for imp in imports if imp not in std_libs and not imp.startswith('_')}

def auto_install_requirements():
    """Installe automatiquement les dépendances manquantes"""
    print("🔍 Scan des imports du projet...")
    
    # Scanner tous les imports
    all_imports = scan_project_imports()
    external_imports = filter_std_libs(all_imports)
    
    print(f"📦 Importations détectées: {', '.join(sorted(external_imports))}")
    
    # Vérifier quelles dépendances sont déjà installées
    missing_deps = []
    for dep in external_imports:
        try:
            importlib.import_module(dep)
            print(f"✓ {dep} déjà installé")
        except ImportError:
            missing_deps.append(dep)
            print(f"✗ {dep} manquant")
    
    # Installer les dépendances manquantes
    if missing_deps:
        print(f"🚀 Installation des dépendances manquantes: {', '.join(missing_deps)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_deps)
            print("✅ Toutes les dépendances ont été installées avec succès!")
            
            # Redémarrer pour charger les nouvelles dépendances
            print("🔄 Redémarrage de l'application...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation: {e}")
            return False
    
    return True

if __name__ == "__main__":
    auto_install_requirements()