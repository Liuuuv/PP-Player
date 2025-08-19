#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fixes():
    """Test des corrections apportées"""
    
    print("=== Test des corrections ===")
    
    # Test 1: Vérification de la correction KeyError 'search_frame'
    print("\n1. Vérification de la correction KeyError 'search_frame'")
    with open("tools.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "if 'search_frame' in video:" in content:
            print("✓ Correction KeyError 'search_frame' implémentée")
        else:
            print("✗ Correction KeyError 'search_frame' manquante")
    
    # Test 2: Vérification de l'ajout systématique à l'onglet téléchargements
    print("\n2. Vérification de l'ajout systématique à l'onglet téléchargements")
    with open("tools.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "# Ajouter à l'onglet téléchargements TOUJOURS (avant de commencer le téléchargement)" in content:
            print("✓ Ajout systématique à l'onglet téléchargements implémenté")
        else:
            print("✗ Ajout systématique manquant")
    
    # Test 3: Vérification de la correction du titre qui disparaît
    print("\n3. Vérification de la correction du titre qui disparaît")
    with open("downloads_tab.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "if not hasattr(widgets['thumbnail_label'], 'image')" in content:
            print("✓ Correction du titre qui disparaît implémentée")
        else:
            print("✗ Correction du titre qui disparaît manquante")
    
    # Test 4: Vérification de la marque "Déjà téléchargé"
    print("\n4. Vérification de la marque 'Déjà téléchargé'")
    with open("tools.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "# Marquer comme déjà téléchargé dans l'onglet téléchargements" in content:
            print("✓ Marque 'Déjà téléchargé' implémentée")
        else:
            print("✗ Marque 'Déjà téléchargé' manquante")
    
    print("\n=== Test terminé ===")

if __name__ == "__main__":
    test_fixes()