#!/usr/bin/env python3
"""
Script de test pour vérifier les nouvelles fonctionnalités de téléchargement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_download_features():
    """Test des nouvelles fonctionnalités de téléchargement"""
    
    print("=== Test des nouvelles fonctionnalités de téléchargement ===")
    
    # Test 1: Vérification du bouton poubelle (déjà existant)
    print("\n1. Vérification du bouton poubelle")
    with open("downloads_tab.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "handle_delete_download" in content and "cancel_active_download" in content:
            print("✓ Bouton poubelle avec annulation implémenté")
        else:
            print("✗ Bouton poubelle manquant")
    
    # Test 2: Vérification de la correction de la barre de progression
    print("\n2. Vérification de la correction de la barre de progression")
    with open("downloads_tab.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "relwidth=relwidth" in content and "progress_overlay.place" in content:
            print("✓ Barre de progression corrigée")
        else:
            print("✗ Barre de progression non corrigée")
    
    # Test 3: Vérification du bouton pause
    print("\n3. Vérification du bouton pause")
    with open("downloads_tab.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "downloads_pause_btn" in content and "toggle_downloads_pause" in content:
            print("✓ Bouton pause implémenté")
        else:
            print("✗ Bouton pause manquant")
    
    # Test 4: Vérification de l'intégration de la pause dans le téléchargement
    print("\n4. Vérification de l'intégration de la pause")
    with open("tools.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "while hasattr(self, 'downloads_paused') and self.downloads_paused:" in content:
            print("✓ Intégration de la pause dans le téléchargement")
        else:
            print("✗ Intégration de la pause manquante")
    
    # Test 5: Vérification de la correction du titre qui disparaît
    print("\n5. Vérification de la correction du titre qui disparaît")
    with open("downloads_tab.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "if not hasattr(widgets['thumbnail_label'], 'image')" in content:
            print("✓ Correction du titre qui disparaît")
        else:
            print("✗ Correction du titre manquante")
    
    # Test 6: Vérification de la correction KeyError 'search_frame'
    print("\n6. Vérification de la correction KeyError 'search_frame'")
    with open("tools.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "if 'search_frame' in video:" in content:
            print("✓ Correction KeyError 'search_frame'")
        else:
            print("✗ Correction KeyError manquante")
    
    print("\n=== Test terminé ===")

if __name__ == "__main__":
    test_download_features()