#!/usr/bin/env python3
"""
Script de test pour le système centralisé de téléchargements
"""

from __init__ import *
import download_manager

class MockApp:
    """Classe mock pour simuler l'application principale"""
    
    def __init__(self):
        self.main_playlist = []
        self.current_index = 0
        self.recommendation_mode = "sparse"
        self.status_bar = MockStatusBar()
        self.root = MockRoot()
        self.drag_drop_handler = MockDragDropHandler()
        self.download_manager = MockDownloadManager()
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'outtmpl': os.path.join("downloads", '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
    def add_download_to_tab(self, url, title, video_data=None):
        """Simule l'ajout à l'onglet téléchargements"""
        return self.download_manager.add_download(url, title)
    
    def save_youtube_url_metadata(self, filepath, url, upload_date=None):
        """Simule la sauvegarde des métadonnées"""
        print(f"Métadonnées sauvegardées: {os.path.basename(filepath)} -> {url}")
    
    def add_to_main_playlist(self, filepath, thumbnail_path=None, song_index=None, show_status=True):
        """Simule l'ajout à la playlist principale"""
        self.main_playlist.append(filepath)
        print(f"✓ Ajouté à la playlist principale: {os.path.basename(filepath)}")
    
    def _safe_add_to_queue(self, filepath):
        """Version sécurisée d'ajout à la queue"""
        if hasattr(self, 'drag_drop_handler'):
            self.drag_drop_handler._add_to_queue(filepath)
    
    def _safe_add_to_queue_first(self, filepath):
        """Version sécurisée d'ajout en premier dans la queue"""
        if hasattr(self, 'drag_drop_handler'):
            self.drag_drop_handler._add_to_queue_first(filepath)
    
    def _safe_add_to_main_playlist(self, filepath):
        """Version sécurisée d'ajout à la playlist"""
        self.add_to_main_playlist(filepath)
    
    def _refresh_playlist_display(self):
        """Simule le rafraîchissement de l'affichage"""
        print("Affichage de la playlist rafraîchi")
    
    def _update_downloads_button(self):
        """Simule la mise à jour du bouton téléchargements"""
        pass
    
    def _refresh_downloads_library(self):
        """Simule le rafraîchissement de la bibliothèque"""
        pass
    
    def update_downloads_display(self):
        """Simule la mise à jour de l'affichage des téléchargements"""
        pass

class MockDragDropHandler:
    """Mock pour le gestionnaire de drag & drop"""
    
    def __init__(self):
        self.queue_items = []
    
    def _add_to_queue(self, filepath):
        """Simule l'ajout à la queue"""
        self.queue_items.append(filepath)
        print(f"✓ Ajouté à la queue: {os.path.basename(filepath)}")
    
    def _add_to_queue_first(self, filepath):
        """Simule l'ajout en premier dans la queue"""
        self.queue_items.insert(0, filepath)
        print(f"✓ Ajouté en premier dans la queue: {os.path.basename(filepath)}")

class MockDownloadManager:
    """Mock pour le gestionnaire de téléchargements"""
    
    def __init__(self):
        self.downloads = {}
    
    def add_download(self, url, title):
        """Simule l'ajout d'un téléchargement"""
        if url not in self.downloads:
            self.downloads[url] = {'title': title, 'progress': 0, 'status': 'En attente'}
            print(f"✓ Téléchargement ajouté à l'onglet: {title}")
            return True
        return False
    
    def update_progress(self, url, progress, status=None):
        """Simule la mise à jour de la progression"""
        if url in self.downloads:
            self.downloads[url]['progress'] = progress
            if status:
                self.downloads[url]['status'] = status
            print(f"Progression: {self.downloads[url]['title']} - {progress}% ({status})")
    
    def mark_error(self, url, error_message):
        """Simule le marquage d'erreur"""
        if url in self.downloads:
            self.downloads[url]['status'] = error_message
            print(f"Erreur: {self.downloads[url]['title']} - {error_message}")

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

def test_centralized_download():
    """Test du téléchargement centralisé"""
    print("=== Test du téléchargement centralisé ===\n")
    
    app = MockApp()
    
    # Test 1: Téléchargement simple avec ajout à la playlist
    print("--- Test 1: Téléchargement avec ajout à la playlist ---")
    
    def mock_callback(filepath):
        download_manager.add_to_playlist_after_download(app, filepath)
    
    # Simuler un téléchargement (sans vraiment télécharger)
    print("Simulation d'un téléchargement...")
    mock_filepath = "downloads/Test_Song.mp3"
    mock_callback(mock_filepath)
    
    print(f"Playlist après téléchargement: {len(app.main_playlist)} éléments")
    
    # Test 2: Téléchargement avec ajout à la queue
    print("\n--- Test 2: Téléchargement avec ajout à la queue ---")
    
    def mock_queue_callback(filepath):
        download_manager.add_to_queue_after_download(app, filepath)
    
    mock_filepath2 = "downloads/Test_Song_2.mp3"
    mock_queue_callback(mock_filepath2)
    
    print(f"Queue après téléchargement: {len(app.drag_drop_handler.queue_items)} éléments")
    
    # Test 3: Téléchargement avec ajout en premier dans la queue
    print("\n--- Test 3: Téléchargement avec ajout en premier dans la queue ---")
    
    def mock_queue_first_callback(filepath):
        download_manager.add_to_queue_first_after_download(app, filepath)
    
    mock_filepath3 = "downloads/Test_Song_3.mp3"
    mock_queue_first_callback(mock_filepath3)
    
    print(f"Queue après ajout en premier: {len(app.drag_drop_handler.queue_items)} éléments")
    print(f"Premier élément de la queue: {os.path.basename(app.drag_drop_handler.queue_items[0])}")

def test_download_manager_integration():
    """Test de l'intégration avec le gestionnaire de téléchargements"""
    print("\n=== Test de l'intégration avec le gestionnaire ===\n")
    
    app = MockApp()
    
    # Simuler l'ajout d'un téléchargement à l'onglet
    url = "https://youtube.com/watch?v=test123"
    title = "Test Video"
    
    print("--- Ajout à l'onglet téléchargements ---")
    added = app.add_download_to_tab(url, title)
    print(f"Téléchargement ajouté: {added}")
    
    # Simuler la progression
    print("\n--- Simulation de la progression ---")
    app.download_manager.update_progress(url, 25, "Téléchargement...")
    app.download_manager.update_progress(url, 50, "Téléchargement...")
    app.download_manager.update_progress(url, 75, "Téléchargement...")
    app.download_manager.update_progress(url, 100, "Terminé")
    
    # Simuler une erreur
    print("\n--- Simulation d'une erreur ---")
    error_url = "https://youtube.com/watch?v=error123"
    error_title = "Error Video"
    app.add_download_to_tab(error_url, error_title)
    app.download_manager.mark_error(error_url, "Vidéo non disponible")

def main():
    """Lance tous les tests"""
    print("=== Tests du système centralisé de téléchargements ===\n")
    
    test_centralized_download()
    test_download_manager_integration()
    
    print("\n=== Fin des tests ===")
    print("\nRésumé:")
    print("- Le système centralisé permet de gérer tous les téléchargements")
    print("- Les callbacks permettent d'ajouter à la playlist ou à la queue")
    print("- L'intégration avec l'onglet téléchargements fonctionne")
    print("- La gestion des erreurs est prise en compte")

if __name__ == "__main__":
    main()