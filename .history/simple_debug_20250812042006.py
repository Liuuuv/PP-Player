#!/usr/bin/env python3
"""
Script simple pour tester le drag dans l'application réelle
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer et lancer l'application normalement
if __name__ == "__main__":
    print("🚀 Lancement de l'application...")
    
    # Importer depuis __init__.py comme dans main.py
    from __init__ import *
    
    class DebugMusicPlayer(MusicPlayer):
        def __init__(self, root):
            super().__init__(root)
            print("✅ Application lancée avec debug")
            print("📝 Instructions:")
            print("   1. Allez dans l'onglet Bibliothèque > Téléchargées")
            print("   2. Essayez de dragger depuis différents endroits sur une musique")
            print("   3. Vérifiez si le drag fonctionne depuis le titre, les métadonnées, etc.")
    
    root = tk.Tk()
    app = DebugMusicPlayer(root)
    root.mainloop()