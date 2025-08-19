#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour nettoyer les lignes vides en excès dans main.py
"""

import re

def clean_empty_lines(filepath):
    """Nettoie les lignes vides en excès dans un fichier"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer les séquences de 3+ lignes vides par 2 lignes vides maximum
    content = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n\n', content)
    
    # Remplacer les séquences de lignes avec seulement des espaces
    content = re.sub(r'\n[ \t]+\n', '\n\n', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Nettoyage terminé pour {filepath}")

if __name__ == "__main__":
    clean_empty_lines(r'c:\Users\olivi\kDrive\projets\loisir\music_player\main.py')