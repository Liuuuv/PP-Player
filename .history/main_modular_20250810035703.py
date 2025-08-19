"""
Version modulaire de Pipi Player
Utilise les modules extraits pour améliorer la lisibilité
"""

# Imports depuis les modules
from modules.imports_and_constants import *
from modules import initialization
from modules import keyboard_events
from modules import ui_creation

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
    
    # Placeholder pour les méthodes manquantes - à implémenter
    def load_icons(self):
        """Charge les icônes (à implémenter)"""
        pass
    
    def _update_volume_sliders(self):
        """Met à jour les sliders de volume (à implémenter)"""
        pass
    
    def update_time(self):
        """Thread de mise à jour du temps (à implémenter)"""
        pass
    
    def load_playlists(self):
        """Charge les playlists (à implémenter)"""
        pass
    
    def load_config(self):
        """Charge la configuration (à implémenter)"""
        pass
    
    def setup_search_tab(self):
        """Configure l'onglet de recherche (à implémenter)"""
        # Placeholder - implémentation basique pour éviter les erreurs
        import tkinter as tk
        from tkinter import ttk
        
        # Frame de recherche simple
        search_frame = ttk.Frame(self.search_tab)
        search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label temporaire
        temp_label = ttk.Label(search_frame, text="Onglet Recherche - À implémenter")
        temp_label.pack(pady=20)
    
    def setup_library_tab(self):
        """Configure l'onglet de bibliothèque (à implémenter)"""
        # Placeholder - implémentation basique pour éviter les erreurs
        import tkinter as tk
        from tkinter import ttk
        
        # Frame de bibliothèque simple
        library_frame = ttk.Frame(self.library_tab)
        library_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label temporaire
        temp_label = ttk.Label(library_frame, text="Onglet Bibliothèque - À implémenter")
        temp_label.pack(pady=20)
    
    def setup_controls(self):
        """Configure les contrôles de lecture (à implémenter)"""
        # Placeholder - implémentation basique pour éviter les erreurs
        import tkinter as tk
        from tkinter import ttk
        
        # Frame de contrôles simple
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Boutons de base
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=10)
        
        # Bouton play/pause
        self.play_button = ttk.Button(button_frame, text="▶️ Play", command=self.play_pause)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Label de statut
        self.status_label = ttk.Label(control_frame, text="Lecteur prêt")
        self.status_label.pack(pady=5)
    
    def play_pause(self):
        """Lecture/pause (à implémenter)"""
        pass

# Point d'entrée
if __name__ == "__main__":
    print("🎵 Pipi Player - Version Modulaire")
    print("=" * 50)
    print("Cette version utilise des modules pour améliorer la lisibilité")
    print("Fichier original: 4582 lignes → Version modulaire")
    print("=" * 50)
    
    root = tk.Tk()
    player = MusicPlayer(root)
    
    # Configuration de fermeture (à implémenter)
    # root.protocol("WM_DELETE_WINDOW", player.on_closing)
    
    root.mainloop()