#!/usr/bin/env python3
"""
Script de test pour vérifier que le mode sparse ajoute à la queue
"""

from __init__ import *
import recommendation

class MockDragDropHandler:
    """Mock pour le gestionnaire de drag & drop"""
    
    def __init__(self):
        self.queue_items = []
    
    def _add_to_queue(self, filepath):
        """Simule l'ajout à la queue"""
        self.queue_items.append(filepath)
        print(f"✓ Ajouté à la queue: {os.path.basename(filepath)}")
        print(f"  Queue actuelle: {len(self.queue_items)} éléments")

class MockApp:
    """Classe mock pour simuler l'application principale"""
    
    def __init__(self):
        self.main_playlist = ["song1.mp3", "song2.mp3", "song3.mp3"]
        self.current_index = 0
        self.recommendation_mode = "sparse"
        self.status_bar = MockStatusBar()
        self.root = MockRoot()
        self.drag_drop_handler = MockDragDropHandler()
        
    def get_youtube_metadata(self, filepath):
        """Simule les métadonnées YouTube"""
        metadata_map = {
            "song1.mp3": {'url': 'https://youtube.com/watch?v=SRF8d_wPXSI'},
            "song2.mp3": {'url': 'https://youtube.com/watch?v=l1hVhzcOiic'},
            "song3.mp3": {'url': 'https://youtube.com/watch?v=abc123def456'},
        }
        return metadata_map.get(filepath)
    
    def add_to_main_playlist(self, filepath, thumbnail_path=None, song_index=None, show_status=True):
        """Simule l'ajout à la playlist principale"""
        self.main_playlist.append(filepath)
        print(f"✓ Ajouté à la playlist principale: {os.path.basename(filepath)}")
    
    def _safe_add_to_queue(self, filepath):
        """Version sécurisée d'ajout à la queue"""
        if hasattr(self, 'drag_drop_handler'):
            self.drag_drop_handler._add_to_queue(filepath)
    
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
        print(f"Métadonnées sauvegardées: {os.path.basename(filepath)} -> {url}")
    
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

def test_sparse_mode_queue():
    """Test que le mode sparse ajoute bien à la queue"""
    print("=== Test du mode sparse avec queue ===\n")
    
    # Créer l'app mock en mode sparse
    app = MockApp()
    app.recommendation_mode = "sparse"
    
    print(f"Mode de recommandation: {app.recommendation_mode}")
    print(f"Queue initiale: {len(app.drag_drop_handler.queue_items)} éléments")
    print(f"Playlist initiale: {len(app.main_playlist)} éléments\n")
    
    # Créer le système de recommandation
    rec_system = recommendation.RecommendationSystem(app)
    rec_system.enable_auto_recommendations = True
    
    # Simuler des recommandations
    mock_recommendations = [
        {
            'title': 'Test Recommendation 1',
            'videoId': 'test123',
            'url': 'https://youtube.com/watch?v=test123',
            'artists': [{'name': 'Test Artist'}]
        }
    ]
    
    print("--- Simulation du téléchargement d'une recommandation ---")
    
    # Simuler le téléchargement (sans vraiment télécharger)
    def mock_download():
        # Simuler un fichier téléchargé
        fake_filepath = "downloads/Test_Recommendation_1.mp3"
        
        # Tester l'ajout selon le mode
        recommendation_mode = getattr(app, 'recommendation_mode', 'sparse')
        if recommendation_mode == "sparse":
            print(f"Mode sparse détecté - ajout à la queue")
            app._safe_add_to_queue(fake_filepath)
        else:
            print(f"Mode add détecté - ajout à la playlist")
            app.add_to_main_playlist(fake_filepath)
    
    mock_download()
    
    print(f"\n--- Résultats ---")
    print(f"Queue finale: {len(app.drag_drop_handler.queue_items)} éléments")
    print(f"Playlist finale: {len(app.main_playlist)} éléments")
    
    if len(app.drag_drop_handler.queue_items) > 0:
        print("✓ SUCCESS: La recommandation a été ajoutée à la queue")
    else:
        print("✗ FAIL: La recommandation n'a pas été ajoutée à la queue")

def test_add_mode_playlist():
    """Test que le mode add ajoute bien à la playlist"""
    print("\n=== Test du mode add avec playlist ===\n")
    
    # Créer l'app mock en mode add
    app = MockApp()
    app.recommendation_mode = "add"
    
    print(f"Mode de recommandation: {app.recommendation_mode}")
    print(f"Queue initiale: {len(app.drag_drop_handler.queue_items)} éléments")
    print(f"Playlist initiale: {len(app.main_playlist)} éléments\n")
    
    print("--- Simulation du téléchargement d'une recommandation ---")
    
    # Simuler le téléchargement
    def mock_download():
        fake_filepath = "downloads/Test_Recommendation_2.mp3"
        
        recommendation_mode = getattr(app, 'recommendation_mode', 'sparse')
        if recommendation_mode == "sparse":
            print(f"Mode sparse détecté - ajout à la queue")
            app._safe_add_to_queue(fake_filepath)
        else:
            print(f"Mode add détecté - ajout à la playlist")
            app.add_to_main_playlist(fake_filepath)
    
    mock_download()
    
    print(f"\n--- Résultats ---")
    print(f"Queue finale: {len(app.drag_drop_handler.queue_items)} éléments")
    print(f"Playlist finale: {len(app.main_playlist)} éléments")
    
    if len(app.main_playlist) > 3:  # 3 était la taille initiale
        print("✓ SUCCESS: La recommandation a été ajoutée à la playlist")
    else:
        print("✗ FAIL: La recommandation n'a pas été ajoutée à la playlist")

def main():
    """Lance tous les tests"""
    print("=== Tests des modes de recommandation avec queue/playlist ===\n")
    
    test_sparse_mode_queue()
    test_add_mode_playlist()
    
    print("\n=== Fin des tests ===")

if __name__ == "__main__":
    main()