"""
Script d'analyse du fichier main.py pour faciliter le partitionnement
"""

import re
import os

def analyze_main_file():
    """Analyse le fichier main.py et génère un rapport"""
    
    if not os.path.exists('main.py'):
        print("❌ Fichier main.py introuvable")
        return
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    print("🔍 ANALYSE DU FICHIER MAIN.PY")
    print("=" * 50)
    
    # Statistiques générales
    total_lines = len(lines)
    non_empty_lines = len([line for line in lines if line.strip()])
    comment_lines = len([line for line in lines if line.strip().startswith('#')])
    
    print(f"📊 STATISTIQUES GÉNÉRALES")
    print(f"   Lignes totales: {total_lines}")
    print(f"   Lignes non vides: {non_empty_lines}")
    print(f"   Lignes de commentaires: {comment_lines}")
    print(f"   Lignes de code: {non_empty_lines - comment_lines}")
    print()
    
    # Analyse des imports
    imports = []
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')):
            imports.append((i+1, line.strip()))
    
    print(f"📦 IMPORTS ({len(imports)} trouvés)")
    for line_num, import_line in imports:
        print(f"   L{line_num:3d}: {import_line}")
    print()
    
    # Analyse des méthodes
    methods = []
    current_class = None
    
    for i, line in enumerate(lines):
        # Détecter les classes
        class_match = re.match(r'^class\s+(\w+)', line)
        if class_match:
            current_class = class_match.group(1)
            continue
        
        # Détecter les méthodes
        method_match = re.match(r'^(\s*)def\s+(\w+)\s*\(', line)
        if method_match:
            indent = len(method_match.group(1))
            method_name = method_match.group(2)
            
            # Calculer la longueur de la méthode
            method_start = i
            method_end = method_start + 1
            
            # Trouver la fin de la méthode
            for j in range(method_start + 1, len(lines)):
                next_line = lines[j]
                if next_line.strip() == '':
                    continue
                
                # Si on trouve une nouvelle méthode ou classe au même niveau ou moins indenté
                if (re.match(r'^(\s*)def\s+', next_line) or 
                    re.match(r'^(\s*)class\s+', next_line) or
                    (next_line.strip() and len(next_line) - len(next_line.lstrip()) <= indent and 
                     not next_line.lstrip().startswith(('#', '"""', "'''")))):
                    method_end = j
                    break
            else:
                method_end = len(lines)
            
            method_length = method_end - method_start
            methods.append((i+1, method_name, method_length, current_class))
    
    print(f"🔧 MÉTHODES ({len(methods)} trouvées)")
    methods.sort(key=lambda x: x[2], reverse=True)  # Trier par longueur décroissante
    
    for line_num, method_name, length, class_name in methods:
        class_info = f" ({class_name})" if class_name else ""
        print(f"   L{line_num:3d}: {method_name}{class_info} - {length} lignes")
    print()
    
    # Suggestions de partitionnement
    print("💡 SUGGESTIONS DE PARTITIONNEMENT")
    print("-" * 30)
    
    # Grouper les méthodes par catégorie
    categories = {
        'Initialisation': ['__init__', 'init_', 'setup_', 'load_', '_count_', '_update_'],
        'Interface': ['create_', 'setup_', 'show_', 'switch_', 'on_tab_', 'colorize_'],
        'Événements': ['on_', 'bind_', 'keyboard_', 'focus_', '_on_'],
        'Audio': ['play_', 'pause_', 'next_', 'previous_', 'volume_', 'audio_'],
        'YouTube': ['youtube_', 'search_', 'download_', '_youtube_'],
        'Playlists': ['playlist_', 'add_to_', 'remove_from_', 'create_playlist'],
        'Fichiers': ['file_', 'add_files', 'delete_', 'move_', 'save_', 'load_'],
        'Configuration': ['config_', 'settings_', '_update_volume_']
    }
    
    for category, patterns in categories.items():
        matching_methods = []
        for line_num, method_name, length, class_name in methods:
            if any(pattern in method_name.lower() for pattern in patterns):
                matching_methods.append((method_name, length))
        
        if matching_methods:
            total_lines = sum(length for _, length in matching_methods)
            print(f"📁 {category}:")
            print(f"   Méthodes: {len(matching_methods)}")
            print(f"   Lignes totales: {total_lines}")
            print(f"   Méthodes: {', '.join(name for name, _ in matching_methods[:5])}")
            if len(matching_methods) > 5:
                print(f"   ... et {len(matching_methods) - 5} autres")
            print()
    
    # Constantes et variables globales
    constants = []
    for i, line in enumerate(lines):
        if re.match(r'^[A-Z_]+ = ', line):
            constants.append((i+1, line.strip()))
    
    if constants:
        print(f"🔧 CONSTANTES ({len(constants)} trouvées)")
        for line_num, constant in constants:
            print(f"   L{line_num:3d}: {constant}")
        print()
    
    print("✅ ANALYSE TERMINÉE")
    print(f"💡 Recommandation: Partitionner en {len([c for c in categories.values() if c])} modules")

if __name__ == "__main__":
    analyze_main_file()