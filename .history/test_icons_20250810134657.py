#!/usr/bin/env python3
"""
Script de test pour vérifier que toutes les icônes sont correctement chargées
"""

import os
from PIL import Image

def test_icons():
    """Teste si toutes les icônes requises existent"""
    assets_path = os.path.join(os.path.dirname(__file__), "assets")
    
    required_icons = [
        "search.png",
        "cross.png",
        "rename.png", 
        "delete.png"
    ]
    
    print("Test des icônes requises:")
    print("-" * 40)
    
    for icon in required_icons:
        icon_path = os.path.join(assets_path, icon)
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                print(f"✓ {icon} - {img.size[0]}x{img.size[1]} pixels")
            except Exception as e:
                print(f"✗ {icon} - Erreur de lecture: {e}")
        else:
            print(f"✗ {icon} - Fichier manquant")
    
    print("-" * 40)
    print("Test terminé")

if __name__ == "__main__":
    test_icons()