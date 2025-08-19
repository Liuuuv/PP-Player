#!/usr/bin/env python3
"""
Script de test pour les modes de recommandation
"""

from __init__ import *
import recommendation

class MockApp:
    """Classe mock pour simuler l'application principale"""
    
    def __init__(self):
        self.main_playlist = ["song1.mp3", "song2.mp3", "song3.mp3"]
        self.current_index = 0
        self.recommendation_mode = "sparse"
        self.status_bar = MockStatusBar()
        self.root = MockRoot()
        
    def get_youtube_metadata(self, filepath):
        """Simule les métadonnées YouTube"""
        metadata_map = {
            "song1.mp3": {'url': 'https://youtube.com/watch?v=SRF8d_wPXSI'},
            "song2.mp3": {'url': 'https://youtube.com/watch?v=l1hVhzcOiic'},
            "song3.mp3": {'url': 'https://youtube.com/watch?v=abc123def456'},
        }
        return metadata_map.get(filepath)
    
    def add_to_main_playlist(self, filepath, show_status=True):
        """Simule l'ajout à la playlist"""
        self.main_playlist.append(filepath)
        print(f"Ajouté à la playlist: {filepath}")
    
    def _refresh_playlist_display(self):
        """Simule le rafraîchissement de l'affichage"""
        print("Affichage de la playlist rafraîchi")
    
    def _update_downloads_button(self):
        """Simule la mise à jour du bouton téléchargements"""
        pass
    
    def _refresh_downloads_library(self):
        """Simule le rafraîchissement de la bibliothèque"""
        pass
    
    def save_youtube_url_metadata(self, filepath, url, upload_date):
        """Simule la sauvegarde des métadonnées"""
        print(f"Métadonnées sauvegardées: {filepath} -> {url}")
    
    def save_playlists(self):
        """Simule la sauvegarde des playlists"""
        pass

class MockStatusBar:
    """Mock pour la barre de statut"""
    def config(self, text):
        print(f"Status: {text}")

class MockRoot:
    """Mock pour la fenêtre principale"""
    def after(self, delay, callback):
        # Exécuter immédiatement pour les tests
        if callable(callback):
            callback()

def test_sparse_mode():
    """Test du mode sparse"""
    print("=== Test du mode sparse ===")
    
    app = MockApp()
    app.recommendation_mode = "sparse"
    
    # Créer le système de recommandation
    rec_system = recommendation.RecommendationSystem(app)
    rec_system.enable_auto_recommendations = True
    
    print(f"Seuil initial: {rec_system.next_recommendation_threshold}")
    
    # Simuler plusieurs changements de chanson
    for i in range(5):
        app.current_index = i % len(app.main_playlist)
        current_song = app.main_playlist[app.current_index]
        
        print(f"\n--- Chanson {i+1}: {current_song} ---")
        rec_system._process_sparse_mode(current_song)
        
        # Attendre un peu pour voir les résultats
        time.sleep(0.5)
    
    print(f"\nChansons jouées depuis dernière recommandation: {rec_system.songs_played_since_last_recommendation}")
    print(f"Prochain seuil: {rec_system.next_recommendation_threshold}")

def test_add_mode():
    """Test du mode add"""
    print("\n=== Test du mode add ===")
    
    app = MockApp()
    app.recommendation_mode = "add"
    
    # Créer le système de recommandation
    rec_system = recommendation.RecommendationSystem(app)
    rec_system.enable_auto_recommendations = True
    
    # Simuler plusieurs appels pour la même chanson
    current_song = app.main_playlist[0]
    
    for i in range(4):  # Dépasser la limite pour tester
        print(f"\n--- Appel {i+1} pour {current_song} ---")
        rec_system._process_add_mode(current_song)
        time.sleep(0.5)
    
    # Changer de chanson
    print(f"\n--- Changement de chanson ---")
    current_song = app.main_playlist[1]
    rec_system._process_add_mode(current_song)
    
    print(f"\nRecommandations ajoutées pour la chanson actuelle: {rec_system.current_song_recommendations_added}")

def test_configuration():
    """Test de la configuration"""
    print("\n=== Test de la configuration ===")
    
    print(f"RECOMMENDATION_SPARSE_MIN_SONGS: {RECOMMENDATION_SPARSE_MIN_SONGS}")
    print(f"RECOMMENDATION_SPARSE_MAX_SONGS: {RECOMMENDATION_SPARSE_MAX_SONGS}")
    print(f"RECOMMENDATION_ADD_BATCH_SIZE: {RECOMMENDATION_ADD_BATCH_SIZE}")
    print(f"RECOMMENDATION_ADD_MAX_LIMIT: {RECOMMENDATION_ADD_MAX_LIMIT}")

def main():
    """Lance tous les tests"""
    print("=== Tests des modes de recommandation ===\n")
    
    test_configuration()
    test_sparse_mode()
    test_add_mode()
    
    print("\n=== Fin des tests ===")

if __name__ == "__main__":
    main()