import pygame
import os
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
from mutagen.mp3 import MP3
import time
import threading
from pydub import AudioSegment
import numpy as np
from PIL import Image, ImageTk
from yt_dlp import YoutubeDL



def setup_window_icon(self):
    """Set up the window icon for the main application window."""
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Impossible de charger l'icône: {e}")

def load_icons(self):
    """Load icons for the application from the assets directory."""
    icon_names = {
        "add": "add.png",
        "prev": "prev.png",
        "play": "play.png",
        "next": "next.png",
        "hey": "hey.png",
        "pause": "pause.png",
        "delete": "delete.png",
        "back": "back.png",
        "loop": "loop.png",
        "loop1": "loop1.png",
        "shuffle": "shuffle.png",
        "rename": "rename.png"
    }

    # Chemin absolu vers le dossier assets
    base_path = os.path.join(os.path.dirname(__file__), "assets")

    self.icons = {}
    for key, filename in icon_names.items():
        try:
            path = os.path.join(base_path, filename)
            image = Image.open(path).resize((32, 32), Image.Resampling.LANCZOS)
            self.icons[key] = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Erreur chargement {filename}: {e}")

def create_ui(self):
    # Style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background='#2d2d2d')
    style.configure('TLabel', background='#2d2d2d', foreground='white')
    style.configure('TButton', background='#3d3d3d', foreground='white')
    style.configure('TScale', background='#2d2d2d')
    
    # config +
    style = ttk.Style()
    style.theme_use('clam')

    # Style de base des boutons
    style.configure('TButton',
        background='#3d3d3d',
        foreground='white',
        borderwidth=0,
        focusthickness=0,
        padding=6
    )

    # Réduction de l'effet hover (état 'active')
    style.map('TButton',
        background=[('active', '#4a4a4a'), ('!active', '#3d3d3d')],
        relief=[('pressed', 'flat'), ('!pressed', 'flat')],
        focuscolor=[('focus', '')]
    )
    
    # Ajoutez ceci dans la section des styles au début de create_ui()
    style.configure('Downloading.TFrame', background='#ff4444')  # Style rouge pour téléchargement
    style.map('Downloading.TFrame',
            background=[('active', '#ff6666')])  # Variation au survol
    style.configure('ErrorDownloading.TFrame', background="#ffcc00")  # Style jaune pour erreur
    
    # Configuration des onglets
    style.configure('TNotebook', background='#2d2d2d', borderwidth=0)
    style.configure('TNotebook.Tab', 
                background='#3d3d3d', 
                foreground='white',
                padding=[10, 5],
                borderwidth=0)
    style.map('TNotebook.Tab',
            background=[('selected', '#4a8fe7'), ('!selected', '#3d3d3d')],
            foreground=[('selected', 'white'), ('!selected', 'white')])

    # Main Frame
    self.main_frame = ttk.Frame(self.root)
    self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Contrôles de lecture (créés en premier pour être toujours visibles en bas)
    self.setup_controls()
    
        # Création du Notebook (onglets) - prend l'espace restant
    self.notebook = ttk.Notebook(self.main_frame)
    self.notebook.pack(fill=tk.BOTH, expand=True)
    
    
    """Frame pour l'onglet Recherche"""
    self.search_tab = ttk.Frame(self.notebook)
    self.notebook.add(self.search_tab, text="Recherche")
    
    # Frame pour l'onglet Bibliothèque
    self.library_tab = ttk.Frame(self.notebook)
    self.notebook.add(self.library_tab, text="Bibliothèque")
    
    # Contenu de l'onglet Recherche (identique à votre ancienne UI)
    self.setup_search_tab()
    
    # Contenu de l'onglet Bibliothèque (pour l'instant vide)
    self.setup_library_tab()
    
    # Lier le changement d'onglet à une fonction
    self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    # Ajouter des bindings pour retirer le focus des champs de saisie
    self.setup_focus_bindings(self)
    
    # self.colorize_ttk_frames(root)

def setup_focus_bindings(self):
    """Configure les bindings pour retirer le focus des champs de saisie"""
    def remove_focus(event):
        """Retire le focus des champs de saisie"""
        focused_widget = self.root.focus_get()
        if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
            self.root.focus_set()
    
    # Ajouter le binding sur les éléments principaux
    widgets_to_bind = [
        self.main_frame,
        self.notebook,
        self.search_tab,
        self.library_tab
    ]
    
    for widget in widgets_to_bind:
        if hasattr(self, widget.__class__.__name__.lower()) or widget:
            widget.bind('<Button-1>', remove_focus)
    
    # Ajouter aussi sur les canvas et containers qui seront créés
    def bind_canvas_focus():
        """Bind les canvas après leur création"""
        canvas_widgets = []
        
        # Ajouter les canvas s'ils existent
        if hasattr(self, 'playlist_canvas'):
            canvas_widgets.append(self.playlist_canvas)
        if hasattr(self, 'youtube_canvas'):
            canvas_widgets.append(self.youtube_canvas)
        if hasattr(self, 'downloads_canvas'):
            canvas_widgets.append(self.downloads_canvas)
        if hasattr(self, 'playlists_canvas'):
            canvas_widgets.append(self.playlists_canvas)
        
        for canvas in canvas_widgets:
            canvas.bind('<Button-1>', remove_focus)
    
    # Programmer le binding des canvas après un court délai pour s'assurer qu'ils sont créés
    self.root.after(100, bind_canvas_focus)


def _update_volume_sliders(self):
    """Met à jour les sliders de volume avec les valeurs chargées"""
    try:
        # Mettre à jour le slider de volume global
        if hasattr(self, 'volume_slider'):
            self.volume_slider.set(self.volume * 100)
        
        # Mettre à jour le slider d'offset (sera mis à jour quand une musique sera jouée)
        if hasattr(self, 'volume_offset_slider'):
            self.volume_offset_slider.set(self.volume_offset)
            
    except Exception as e:
        print(f"Erreur mise à jour sliders: {e}")

def load_playlists(self):
    """Charge les playlists depuis le fichier JSON"""
    try:
        import json
        playlists_file = os.path.join("downloads", "playlists.json")
        
        if os.path.exists(playlists_file):
            with open(playlists_file, 'r', encoding='utf-8') as f:
                loaded_playlists = json.load(f)
            
            # Ajouter les playlists chargées (en gardant la main playlist)
            for name, songs in loaded_playlists.items():
                # Vérifier que les fichiers existent encore
                existing_songs = [song for song in songs if os.path.exists(song)]
                if existing_songs:  # Seulement ajouter si il y a des chansons valides
                    self.playlists[name] = existing_songs
                    
    except Exception as e:
        print(f"Erreur chargement playlists: {e}")


def load_config(self):
    """Charge la configuration (volume global et offsets de volume)"""
    try:
        import json
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Charger le volume global
            if "global_volume" in config:
                self.volume = config["global_volume"]
                # Mettre à jour le slider de volume
                if hasattr(self, 'volume_slider'):
                    self.volume_slider.set(self.volume * 100)
            
            # Charger les offsets de volume
            if "volume_offsets" in config:
                self.volume_offsets = config["volume_offsets"]
                
    except Exception as e:
        print(f"Erreur chargement config: {e}")


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


def setup_keyboard_bindings(self):
        """Configure les raccourcis clavier"""
        # Binding pour la barre d'espace (pause/play)
        self.root.bind('<KeyPress-space>', self.on_space_pressed)
        
        # Binding pour retirer le focus des champs de saisie quand on clique ailleurs
        self.root.bind('<Button-1>', self.on_root_click)
        
        # S'assurer que la fenêtre peut recevoir le focus pour les événements clavier
        self.root.focus_set()