"""
Version modulaire de Pipi Player
Utilise les modules extraits pour améliorer la lisibilité
"""

# Imports depuis les modules
from modules.imports_and_constants import *
from modules import initialization
from modules import keyboard_events
from modules import ui_creation
from modules import config_manager
from modules import audio_player
from modules import ui_controls

class MusicPlayer:
    def __init__(self, root):
        """Initialise le lecteur de musique avec une approche modulaire"""
        
        # Initialisation de la fenêtre
        initialization.init_window(self, root)
        
        # Initialisation de pygame
        initialization.init_pygame(self)
        
        # Initialisation des variables
        initialization.init_variables(self)
        
        # Initialisation des composants
        initialization.init_components(self)
        
        # Chargement des données
        initialization.init_data(self)
    
    # ===== MÉTHODES D'ÉVÉNEMENTS CLAVIER =====
    def setup_keyboard_bindings(self):
        return keyboard_events.setup_keyboard_bindings(self)
    
    def on_space_pressed(self, event):
        return keyboard_events.on_space_pressed(self, event)
    
    def on_root_click(self, event):
        return keyboard_events.on_root_click(self, event)
    
    def setup_focus_bindings(self):
        return keyboard_events.setup_focus_bindings(self)
    
    # ===== MÉTHODES D'INTERFACE =====
    def create_ui(self):
        return ui_creation.create_ui(self)
    
    def on_tab_changed(self, event):
        return ui_creation.on_tab_changed(self, event)
    
    def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
        return ui_creation.colorize_ttk_frames(self, widget, colors)
    
    # ===== MÉTHODES ORIGINALES (à extraire dans d'autres modules) =====
    
    def _count_downloaded_files(self):
        """Compte les fichiers téléchargés sans les afficher"""
        downloads_dir = "downloads"
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
            self.num_downloaded_files = 0
            return
        
        # Extensions audio supportées
        audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
        
        # Compter les fichiers
        count = 0
        for filename in os.listdir(downloads_dir):
            if filename.lower().endswith(audio_extensions):
                count += 1
        
        self.num_downloaded_files = count

    def _update_downloads_button(self):
        """Met à jour le texte du bouton téléchargées avec le nombre actuel"""
        if hasattr(self, 'downloads_btn'):
            self.downloads_btn.configure(text="Téléchargées " + f"({self.num_downloaded_files})")
    
    # NOTE: Toutes les autres méthodes du fichier original main.py 
    # doivent être copiées ici ou extraites dans d'autres modules
    
    # ===== MÉTHODES DE CONFIGURATION =====
    def load_icons(self):
        return config_manager.load_icons(self)
    
    def _update_volume_sliders(self):
        return audio_player._update_volume_sliders(self)
    
    def load_playlists(self):
        return config_manager.load_playlists(self)
    
    def save_playlists(self):
        return config_manager.save_playlists(self)
    
    def load_config(self):
        return config_manager.load_config(self)
    
    def save_config(self):
        return config_manager.save_config(self)
    
    # ===== MÉTHODES AUDIO =====
    def play_pause(self):
        return audio_player.play_pause(self)
    
    def play_track(self):
        return audio_player.play_track(self)
    
    def next_track(self):
        return audio_player.next_track(self)
    
    def prev_track(self):
        return audio_player.prev_track(self)
    
    def set_volume(self, volume):
        return audio_player.set_volume(self, volume)
    
    def set_volume_offset(self, offset):
        return audio_player.set_volume_offset(self, offset)
    
    def _apply_volume(self):
        return audio_player._apply_volume(self)
    
    def update_time(self):
        return audio_player.update_time(self)
    
    def toggle_random_mode(self):
        return audio_player.toggle_random_mode(self)
    
    def toggle_loop_mode(self):
        return audio_player.toggle_loop_mode(self)
    
    def set_position(self, position):
        return audio_player.set_position(self, position)
    
    # ===== MÉTHODES D'INTERFACE AVANCÉES =====
    def setup_search_tab(self):
        return ui_controls.setup_search_tab(self)
    
    def setup_library_tab(self):
        return ui_controls.setup_library_tab(self)
    
    def setup_controls(self):
        return ui_controls.setup_controls(self)
    
    def switch_library_tab(self, tab_name):
        return ui_controls.switch_library_tab(self, tab_name)
    
    def on_progress_press(self, event):
        return ui_controls.on_progress_press(self, event)
    
    def on_progress_drag(self, event):
        return ui_controls.on_progress_drag(self, event)
    
    def on_progress_release(self, event):
        return ui_controls.on_progress_release(self, event)
    
    def _reset_volume_offset(self, event):
        return ui_controls._reset_volume_offset(self, event)
    
    # ===== MÉTHODES UTILITAIRES =====
    def on_closing(self):
        """Gère la fermeture de l'application"""
        # Sauvegarder la configuration avant de fermer
        self.save_config()
        self.save_playlists()
        
        # Arrêter la musique
        import pygame
        pygame.mixer.music.stop()
        
        # Fermer la fenêtre
        self.root.destroy()
        
        print("👋 Pipi Player fermé")

# Point d'entrée
if __name__ == "__main__":
    print("🎵 Pipi Player - Version Modulaire")
    print("=" * 50)
    print("Cette version utilise des modules pour améliorer la lisibilité")
    print("Fichier original: 4582 lignes → Version modulaire")
    print("=" * 50)
    
    root = tk.Tk()
    player = MusicPlayer(root)
    
    # Configuration de fermeture
    root.protocol("WM_DELETE_WINDOW", player.on_closing)
    
    print("✅ Application lancée avec succès!")
    print("📁 Modules chargés:")
    print("   - imports_and_constants")
    print("   - initialization") 
    print("   - keyboard_events")
    print("   - ui_creation")
    print("   - config_manager")
    print("   - audio_player")
    print("   - ui_controls")
    print("=" * 50)
    
    root.mainloop()