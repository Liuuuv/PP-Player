#!/usr/bin/env python3
import re
import os

def remove_debug_prints(file_path):
    """Supprime tous les print qui contiennent DEBUG: d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern pour matcher les lignes print avec DEBUG:
        # Supporte print("DEBUG:...") et print(f"DEBUG:...")
        pattern = r'^\s*print\(f?"DEBUG:.*?\)\s*$'
        
        # Supprimer les lignes qui matchent le pattern
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            if not re.match(pattern, line):
                filtered_lines.append(line)
        
        # Réécrire le fichier
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(filtered_lines))
        
        print(f"Messages DEBUG supprimés de {file_path}")
        return True
        
    except Exception as e:
        print(f"Erreur lors du traitement de {file_path}: {e}")
        return False

# Traiter le fichier search_tab/results.py
file_path = r"c:\Users\olivi\kDrive\projets\loisir\music_player\search_tab\results.py"
remove_debug_prints(file_path)