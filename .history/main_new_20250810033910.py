"""
Point d'entrée principal de l'application Pipi Player
"""
import tkinter as tk
from tkinter import ttk
import os
import sys

# Ajouter le répertoire courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from core.playlist import PlaylistManager
from core.player import AudioPlayer
from services.youtube_service import YouTubeService
from services.file_service import FileService
from ui.main_window import MainWindow
from ui.controls import ControlsManager
from ui.search_tab import SearchTab
from ui.library_tab import LibraryTab
from utils.keyboard import KeyboardManager


class PipiPlayer:
    """Application principale du lecteur de musique"""
    
    def __init__(self):
        # Créer la fenêtre principale
        self.main_window = MainWindow("Pipi Player")
        self.root = self.main_window.get_root()
        
        # Initialiser les composants
        self.settings = Settings()
        self.playlist_manager = PlaylistManager()
        self.file_service = FileService()
        self.youtube_service = YouTubeService()
        
        # Créer le lecteur audio
        self.audio_player = AudioPlayer(self.playlist_manager, self.settings)
        
        # Configurer les callbacks du lecteur
        self._setup_audio_callbacks()
        
        # Créer l'interface utilisateur
        self._create_ui()
        
        # Gestionnaire de clavier
        self.keyboard_manager = KeyboardManager(self.root, self.audio_player)
        
        # Charger la configuration
        self._load_initial_data()
        
        # Configurer la fermeture
        self.main_window.set_close_callback(self.on_closing)
    
    def _setup_audio_callbacks(self):
        """Configure les callbacks du lecteur audio"""
        self.audio_player.on_track_changed = self._on_track_changed
        self.audio_player.on_time_updated = self._on_time_updated
        self.audio_player.on_status_changed = self._on_status_changed
    
    def _create_ui(self):
        """Crée l'interface utilisateur"""
        # Créer le notebook (onglets)
        notebook = self.main_window.create_notebook()
        
        # Créer les contrôles de lecture
        self.controls = ControlsManager(
            self.main_window.get_main_frame(),
            self.audio_player,
            self.settings
        )
        
        # Créer l'onglet de recherche
        self.search_tab = SearchTab(
            notebook,
            self.youtube_service,
            self.playlist_manager,
            self.audio_player
        )
        self.main_window.add_tab(self.search_tab.get_frame(), "Recherche")
        
        # Créer l'onglet de bibliothèque
        self.library_tab = LibraryTab(
            notebook,
            self.playlist_manager,
            self.file_service,
            self.audio_player,
            self.settings
        )
        self.main_window.add_tab(self.library_tab.get_frame(), "Bibliothèque")
        
        # Lier le changement d'onglet
        self.main_window.bind_tab_changed(self._on_tab_changed)
    
    def _load_initial_data(self):
        """Charge les données initiales"""
        # Charger la configuration
        self.settings.load_config()
        
        # Charger les playlists
        self.playlist_manager.load_playlists()
        
        # Mettre à jour l'interface
        self.controls.update_volume_display()
    
    def _on_track_changed(self, track_path, index):
        """Appelé quand la piste change"""
        self.controls.update_track_info(track_path)
        
        # Mettre à jour l'affichage des playlists si nécessaire
        if hasattr(self.library_tab, 'refresh_current_view'):
            self.library_tab.refresh_current_view()
    
    def _on_time_updated(self, current_time, total_time):
        """Appelé quand le temps de lecture est mis à jour"""
        self.controls.update_time_display(current_time, total_time)
    
    def _on_status_changed(self, status):
        """Appelé quand le statut du lecteur change"""
        self.controls.update_status(status)
    
    def _on_tab_changed(self, event):
        """Appelé quand l'onglet change"""
        # Mettre à jour l'affichage selon l'onglet sélectionné
        pass
    
    def on_closing(self):
        """Appelé à la fermeture de l'application"""
        # Sauvegarder la configuration
        self.settings.save_config()
        
        # Sauvegarder les playlists
        self.playlist_manager.save_playlists()
        
        # Nettoyer le lecteur audio
        self.audio_player.cleanup()
        
        # Fermer la fenêtre
        self.main_window.destroy()
    
    def run(self):
        """Lance l'application"""
        self.main_window.mainloop()


def main():
    """Point d'entrée principal"""
    app = PipiPlayer()
    app.run()


if __name__ == "__main__":
    main()