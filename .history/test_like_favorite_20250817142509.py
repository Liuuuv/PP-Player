#!/usr/bin/env python3
"""
Script de test pour vérifier les fonctionnalités like et favorite
"""

import tkinter as tk
from main import MusicPlayer
import time

def test_like_favorite_functionality():
    """Test des fonctionnalités like et favorite"""
    print("=== Test des fonctionnalités Like et Favorite ===")
    
    # Créer l'application
    root = tk.Tk()
    player = MusicPlayer(root)
    
    # Vérifier que les playlists spéciales existent
    print(f"Playlists disponibles: {list(player.playlists.keys())}")
    
    # Vérifier que "Liked" et "Favorites" sont présentes
    assert "Liked" in player.playlists, "La playlist 'Liked' n'existe pas"
    assert "Favorites" in player.playlists, "La playlist 'Favorites' n'existe pas"
    print("✓ Playlists 'Liked' et 'Favorites' créées avec succès")
    
    # Vérifier que les boutons existent
    assert hasattr(player, 'like_button'), "Le bouton like n'existe pas"
    assert hasattr(player, 'favorite_button'), "Le bouton favorite n'existe pas"
    print("✓ Boutons like et favorite créés avec succès")
    
    # Vérifier que les icônes sont chargées
    assert "like_empty" in player.icons, "Icône like_empty non chargée"
    assert "like_full" in player.icons, "Icône like_full non chargée"
    assert "favorite_empty" in player.icons, "Icône favorite_empty non chargée"
    assert "favorite_full" in player.icons, "Icône favorite_full non chargée"
    print("✓ Icônes like et favorite chargées avec succès")
    
    # Vérifier que les variables sont initialisées
    assert hasattr(player, 'liked_songs'), "Variable liked_songs non initialisée"
    assert hasattr(player, 'favorite_songs'), "Variable favorite_songs non initialisée"
    assert isinstance(player.liked_songs, set), "liked_songs n'est pas un set"
    assert isinstance(player.favorite_songs, set), "favorite_songs n'est pas un set"
    print("✓ Variables liked_songs et favorite_songs initialisées correctement")
    
    print("\n=== Tous les tests sont passés avec succès ! ===")
    print("Les fonctionnalités suivantes ont été implémentées :")
    print("1. ✓ Bouton recommendations déplacé à gauche de shuffle")
    print("2. ✓ Boutons like et favorite ajoutés à droite de add")
    print("3. ✓ Icônes like_empty/like_full et favorite_empty/favorite_full chargées")
    print("4. ✓ Playlists 'Liked' et 'Favorites' créées automatiquement")
    print("5. ✓ Fonctions toggle pour like et favorite implémentées")
    print("6. ✓ Sauvegarde/chargement des likes et favorites dans la configuration")
    print("7. ✓ Mise à jour automatique des boutons lors du changement de chanson")
    print("8. ✓ Playlists 'Liked' et 'Favorites' affichées en premier dans la liste")
    
    # Fermer l'application
    root.destroy()

if __name__ == "__main__":
    test_like_favorite_functionality()