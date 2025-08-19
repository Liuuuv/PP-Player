#!/usr/bin/env python3
"""
Script de test pour vérifier que les likes et favorites sont mutuellement exclusifs
"""

import tkinter as tk
from main import MusicPlayer
import os

def test_mutual_exclusion():
    """Test de l'exclusion mutuelle entre likes et favorites"""
    print("=== Test de l'exclusion mutuelle Like/Favorite ===")
    
    # Créer l'application
    root = tk.Tk()
    player = MusicPlayer(root)
    
    # Simuler une chanson dans la playlist
    test_song = "test_song.mp3"
    player.main_playlist = [test_song]
    player.current_index = 0
    
    print(f"Chanson de test: {test_song}")
    
    # Test 1: Ajouter aux likes
    print("\n1. Ajout aux likes...")
    player.toggle_like_current_song()
    
    # Vérifications
    assert test_song in player.liked_songs, "La chanson n'est pas dans liked_songs"
    assert test_song not in player.favorite_songs, "La chanson ne devrait pas être dans favorite_songs"
    assert test_song in player.playlists["Liked"], "La chanson n'est pas dans la playlist Liked"
    assert test_song not in player.playlists["Favorites"], "La chanson ne devrait pas être dans la playlist Favorites"
    print("✓ Chanson ajoutée aux likes uniquement")
    
    # Test 2: Ajouter aux favoris (devrait retirer des likes)
    print("\n2. Ajout aux favoris (devrait retirer des likes)...")
    player.toggle_favorite_current_song()
    
    # Vérifications
    assert test_song not in player.liked_songs, "La chanson ne devrait plus être dans liked_songs"
    assert test_song in player.favorite_songs, "La chanson n'est pas dans favorite_songs"
    assert test_song not in player.playlists["Liked"], "La chanson ne devrait plus être dans la playlist Liked"
    assert test_song in player.playlists["Favorites"], "La chanson n'est pas dans la playlist Favorites"
    print("✓ Chanson retirée des likes et ajoutée aux favoris")
    
    # Test 3: Ajouter aux likes (devrait retirer des favoris)
    print("\n3. Ajout aux likes (devrait retirer des favoris)...")
    player.toggle_like_current_song()
    
    # Vérifications
    assert test_song in player.liked_songs, "La chanson n'est pas dans liked_songs"
    assert test_song not in player.favorite_songs, "La chanson ne devrait plus être dans favorite_songs"
    assert test_song in player.playlists["Liked"], "La chanson n'est pas dans la playlist Liked"
    assert test_song not in player.playlists["Favorites"], "La chanson ne devrait plus être dans la playlist Favorites"
    print("✓ Chanson retirée des favoris et ajoutée aux likes")
    
    # Test 4: Retirer des likes
    print("\n4. Retrait des likes...")
    player.toggle_like_current_song()
    
    # Vérifications
    assert test_song not in player.liked_songs, "La chanson ne devrait plus être dans liked_songs"
    assert test_song not in player.favorite_songs, "La chanson ne devrait pas être dans favorite_songs"
    assert test_song not in player.playlists["Liked"], "La chanson ne devrait plus être dans la playlist Liked"
    assert test_song not in player.playlists["Favorites"], "La chanson ne devrait pas être dans la playlist Favorites"
    print("✓ Chanson retirée des likes, aucune dans les favoris")
    
    # Test 5: Ajouter aux favoris puis retirer
    print("\n5. Ajout aux favoris puis retrait...")
    player.toggle_favorite_current_song()  # Ajouter
    assert test_song in player.favorite_songs, "La chanson n'est pas dans favorite_songs"
    print("✓ Chanson ajoutée aux favoris")
    
    player.toggle_favorite_current_song()  # Retirer
    assert test_song not in player.favorite_songs, "La chanson ne devrait plus être dans favorite_songs"
    assert test_song not in player.liked_songs, "La chanson ne devrait pas être dans liked_songs"
    print("✓ Chanson retirée des favoris, aucune dans les likes")
    
    print("\n=== Tous les tests d'exclusion mutuelle sont passés avec succès ! ===")
    print("Fonctionnalités vérifiées :")
    print("1. ✓ Ajouter aux likes retire automatiquement des favoris")
    print("2. ✓ Ajouter aux favoris retire automatiquement des likes")
    print("3. ✓ Une chanson ne peut être que dans une seule catégorie à la fois")
    print("4. ✓ Les playlists 'Liked' et 'Favorites' sont synchronisées correctement")
    print("5. ✓ Retirer d'une catégorie ne l'ajoute pas automatiquement à l'autre")
    
    # Fermer l'application
    root.destroy()

if __name__ == "__main__":
    test_mutual_exclusion()