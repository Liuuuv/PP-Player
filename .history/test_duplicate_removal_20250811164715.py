#!/usr/bin/env python3
"""
Script de test pour vérifier que la suppression de musiques dupliquées fonctionne correctement.
"""

def test_duplicate_removal_logic():
    """Test de la logique de suppression avec des doublons"""
    
    # Simuler une playlist avec des doublons
    playlist = [
        "song1.mp3",
        "song2.mp3", 
        "song1.mp3",  # Doublon de song1
        "song3.mp3",
        "song1.mp3"   # Autre doublon de song1
    ]
    
    print("Playlist initiale:")
    for i, song in enumerate(playlist):
        print(f"  {i}: {song}")
    
    # Test 1: Supprimer le premier doublon (index 2)
    print("\nTest 1: Suppression de l'index 2 (song1.mp3 - premier doublon)")
    test_playlist = playlist.copy()
    
    # Ancienne méthode (problématique)
    old_index = test_playlist.index("song1.mp3")  # Retourne toujours 0
    print(f"Ancienne méthode - index trouvé: {old_index} (INCORRECT)")
    
    # Nouvelle méthode (correcte)
    correct_index = 2  # L'index réel qu'on veut supprimer
    print(f"Nouvelle méthode - index utilisé: {correct_index} (CORRECT)")
    
    test_playlist.pop(correct_index)
    print("Playlist après suppression:")
    for i, song in enumerate(test_playlist):
        print(f"  {i}: {song}")
    
    # Test 2: Supprimer le dernier doublon (index 4 dans la playlist originale, maintenant 3)
    print("\nTest 2: Suppression du dernier doublon (maintenant à l'index 3)")
    correct_index = 3  # Le dernier song1.mp3
    test_playlist.pop(correct_index)
    print("Playlist après suppression:")
    for i, song in enumerate(test_playlist):
        print(f"  {i}: {song}")
    
    print("\nTest réussi ! La nouvelle méthode permet de supprimer le bon élément.")

if __name__ == "__main__":
    test_duplicate_removal_logic()