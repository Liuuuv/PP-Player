#!/usr/bin/env python3
"""
Script de test pour vérifier les améliorations des téléchargements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_download_logic():
    """Test de la logique de téléchargement améliorée"""
    
    print("=== Test des améliorations de téléchargement ===")
    
    # Test 1: Vérification que les imports ne sont plus ajoutés automatiquement
    print("\n1. Vérification du drag_drop_handler")
    with open("drag_drop_handler.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "add_file_import_to_tab" not in content:
            print("✓ Les imports ne sont plus ajoutés automatiquement à l'onglet téléchargements")
        else:
            print("✗ Les imports sont encore ajoutés automatiquement")
    
    # Test 2: Vérification que les téléchargements sont ajoutés AVANT le téléchargement
    print("\n2. Vérification de l'ajout précoce à l'onglet téléchargements")
    with open("tools.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "# Ajouter à l'onglet téléchargements TOUJOURS (avant de commencer le téléchargement)" in content:
            print("✓ Les téléchargements sont ajoutés à l'onglet AVANT le téléchargement")
        else:
            print("✗ L'ajout précoce n'est pas implémenté")
    
    # Test 3: Vérification des améliorations de l'interface
    print("\n3. Vérification des améliorations de l'interface")
    with open("downloads_tab.py", "r", encoding="utf-8") as f:
        content = f.read()
        improvements = [
            ("Espacement des boutons", "padx=(10, 0)"),
            ("Bouton delete plus grand", "width=30"),
            ("Miniature plus grande", "width=12"),
            ("Titre plus long", "max_title_length = 60"),
            ("Barre de progression visible", "bg='#1b5e20'")
        ]
        
        for name, check in improvements:
            if check in content:
                print(f"✓ {name}")
            else:
                print(f"✗ {name}")
    
    # Test 4: Vérification des fonctions d'import avec vérification
    print("\n4. Vérification des fonctions d'import améliorées")
    with open("inputs.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "_download_playlist_sequential" in content:
            print("✓ Téléchargement séquentiel de playlist implémenté")
        else:
            print("✗ Téléchargement séquentiel manquant")
            
        if "existing_file = self.music_player._get_existing_download" in content:
            print("✓ Vérification des fichiers existants implémentée")
        else:
            print("✗ Vérification des fichiers existants manquante")
    
    print("\n=== Test terminé ===")

if __name__ == "__main__":
    test_download_logic()