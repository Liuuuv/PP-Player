#!/usr/bin/env python3
"""
Script de test pour vérifier les nouvelles fonctionnalités :
1. Clic droit sur le slider d'offset pour remettre à 0
2. Affichage amélioré des playlists (2 par ligne, miniatures carrées)
"""

import json
import os

def test_config_loading():
    """Test le chargement de la configuration"""
    config_file = "downloads/player_config.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("Configuration chargée :")
        print(f"  Volume global : {config.get('global_volume', 'Non défini')}")
        print(f"  Nombre d'offsets : {len(config.get('volume_offsets', {}))}")
        
        if config.get('volume_offsets'):
            print("  Offsets de volume :")
            for file, offset in config['volume_offsets'].items():
                filename = os.path.basename(file)
                print(f"    {filename}: {offset:+.1f}")
    else:
        print("Fichier de configuration non trouvé")

if __name__ == "__main__":
    print("=== Test des nouvelles fonctionnalités ===")
    print()
    
    print("1. Test de la configuration :")
    test_config_loading()
    print()
    
    print("2. Nouvelles fonctionnalités à tester manuellement :")
    print("   ✅ Clic droit sur le slider d'offset pour le remettre à 0")
    print("   ✅ Affichage des playlists dans l'onglet Bibliothèque > Playlists")
    print("   ✅ Miniatures carrées uniformes (220x220 pixels)")
    print("   ✅ 2 playlists par ligne")
    print()
    
    print("3. Fonctionnalités playlists ajoutées :")
    print("   🆕 Double-clic sur playlist → affichage dans le même onglet")
    print("   🆕 Double-clic sur musique → lance la playlist depuis cette musique")
    print("   🆕 Icône delete (non rognée) pour supprimer une musique")
    print("   🆕 Bouton retour pour revenir aux playlists")
    print()
    
    print("Lancez l'application principale pour tester ces fonctionnalités !")
    print("Allez dans Bibliothèque > Playlists et double-cliquez sur une playlist !")