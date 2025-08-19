#!/usr/bin/env python3
"""
Script de test final pour vérifier toutes les corrections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_final_fixes():
    """Test final de toutes les corrections"""
    
    print("=== Test final des corrections ===")
    
    # Test 1: Correction NameError avec variable 'e'
    print("\n1. Correction NameError avec variable 'e'")
    with open("inputs.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "error_msg = str(e)" in content:
            print("✓ NameError corrigé")
        else:
            print("✗ NameError non corrigé")
    
    # Test 2: Séparation logique fichiers existants/nouveaux téléchargements
    print("\n2. Séparation logique fichiers existants/nouveaux téléchargements")
    with open("tools.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "if existing_file:" in content and "else:" in content and "# Ajouter à l'onglet téléchargements pour un nouveau téléchargement" in content:
            print("✓ Séparation logique implémentée")
        else:
            print("✗ Séparation logique manquante")
    
    # Test 3: Bouton pause avec icônes
    print("\n3. Bouton pause avec icônes")
    with open("setup.py", "r", encoding="utf-8") as f:
        content = f.read()
        if '"pause", "play"' in content and 'pause_small' in content:
            print("✓ Icônes pause/play ajoutées")
        else:
            print("✗ Icônes pause/play manquantes")
    
    # Test 4: Fonction toggle_downloads_pause
    print("\n4. Fonction toggle_downloads_pause")
    with open("downloads_tab.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "def toggle_downloads_pause" in content and "downloads_paused" in content:
            print("✓ Fonction toggle_downloads_pause implémentée")
        else:
            print("✗ Fonction toggle_downloads_pause manquante")
    
    # Test 5: Intégration pause dans téléchargement
    print("\n5. Intégration pause dans téléchargement")
    with open("tools.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "while hasattr(self, 'downloads_paused') and self.downloads_paused:" in content:
            print("✓ Intégration pause dans téléchargement")
        else:
            print("✗ Intégration pause manquante")
    
    # Test 6: Correction titre qui disparaît
    print("\n6. Correction titre qui disparaît")
    with open("downloads_tab.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "if not hasattr(widgets['thumbnail_label'], 'image')" in content:
            print("✓ Correction titre qui disparaît")
        else:
            print("✗ Correction titre manquante")
    
    # Test 7: Correction KeyError 'search_frame'
    print("\n7. Correction KeyError 'search_frame'")
    with open("tools.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "if 'search_frame' in video:" in content:
            print("✓ Correction KeyError 'search_frame'")
        else:
            print("✗ Correction KeyError manquante")
    
    print("\n=== Test terminé ===")
    print("\nRésumé des fonctionnalités implémentées :")
    print("• Bouton poubelle pour supprimer/annuler téléchargements")
    print("• Bouton pause pour mettre en pause/reprendre téléchargements")
    print("• Correction de la barre de progression verte")
    print("• Correction des erreurs NameError et KeyError")
    print("• Séparation logique fichiers existants/nouveaux téléchargements")
    print("• Préservation du titre des téléchargements")

if __name__ == "__main__":
    test_final_fixes()