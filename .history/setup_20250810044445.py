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
from tooltip import create_tooltip



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
    self.setup_focus_bindings()
    
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



def setup_controls(self):
        # Control Frame (should be at the bottom, no expand)
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Waveform Frame (above song info)
        waveform_frame = ttk.Frame(control_frame)
        waveform_frame.pack(fill=tk.X)
        
        # Song Info
        self.song_label = ttk.Label(
            control_frame, text="No track selected", 
            font=('Helvetica', 12, 'bold')
        )
        self.song_label.pack(pady=10)
        
        # Progress Bar
        self.progress = ttk.Scale(
            control_frame, from_=0, to=100, orient=tk.HORIZONTAL,
            command=self.set_position
        )
        self.progress.pack(fill=tk.X, pady=5)
        
        self.progress.bind("<Button-1>", self.on_progress_press)   # début drag
        self.progress.bind("<ButtonRelease-1>", self.on_progress_release)  # fin drag
        self.progress.bind("<B1-Motion>", self.on_progress_drag) # pendant drag
        
        # Time Labels
        time_frame = ttk.Frame(control_frame)
        time_frame.pack(fill=tk.X)
        
        self.current_time_label = ttk.Label(time_frame, text="00:00")
        self.current_time_label.pack(side=tk.LEFT)
        
        self.song_length_label = ttk.Label(time_frame, text="00:00")
        self.song_length_label.pack(side=tk.RIGHT)
        
        # Conteneur horizontal pour volume offset + boutons + volume
        buttons_volume_frame = ttk.Frame(control_frame)
        buttons_volume_frame.pack(fill=tk.X, pady=20)

        # Frame volume offset à gauche (largeur fixe)
        volume_offset_frame = ttk.Frame(buttons_volume_frame, width=180)
        volume_offset_frame.grid(row=0, column=0, sticky="w")
        volume_offset_frame.grid_propagate(False)  # Empêcher le redimensionnement

        ttk.Label(volume_offset_frame, text="Volume Offset").pack()
        self.volume_offset_slider = ttk.Scale(
            volume_offset_frame, from_=-50, to=50, 
            command=self.set_volume_offset, value=0,
            orient='horizontal',
            length=150
        )
        self.volume_offset_slider.pack(padx=15)
        
        # Ajouter le clic droit pour remettre à 0
        self.volume_offset_slider.bind("<Button-3>", self._reset_volume_offset)

        # Frame boutons (centré)
        button_frame = ttk.Frame(buttons_volume_frame)
        button_frame.grid(row=0, column=1, padx=20)

        # Boutons avec grid (centré dans button_frame)
        # Ordre: random, loop, prev, play, next, hey, add
        
        # Boutons plus petits (random, loop, hey, add)
        small_button_style = {'width': 30, 'height': 30}
        
        # Bouton Random (plus petit)
        self.random_button = tk.Button(
            button_frame, 
            image=self.icons["shuffle"],
            bg="#3d3d3d" if not self.random_mode else "#4a8fe7",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            width=40,
            height=40,
            command=self.toggle_random_mode
        )
        self.random_button.grid(row=0, column=0, padx=3)
        
        # Bouton Loop (plus petit)
        self.loop_button = tk.Button(
            button_frame, 
            image=self.icons["loop"],
            bg="#3d3d3d" if self.loop_mode == 0 else "#4a8fe7",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            width=40,
            height=40,
            command=self.toggle_loop_mode
        )
        self.loop_button.grid(row=0, column=1, padx=3)
        
        # Boutons principaux (taille normale)
        ttk.Button(button_frame, image=self.icons["prev"], command=self.prev_track).grid(row=0, column=2, padx=5)
        self.play_button = ttk.Button(button_frame, image=self.icons["play"], command=self.play_pause)
        self.play_button.grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, image=self.icons["next"], command=self.next_track).grid(row=0, column=4, padx=5)
        
        # Bouton Hey (plus petit)
        self.hey_button = tk.Button(
            button_frame, 
            image=self.icons["hey"],
            bg="#3d3d3d",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            width=40,
            height=40,
        )
        self.hey_button.grid(row=0, column=5, padx=3)
        
        # Bouton Add (plus petit, en dernier)
        self.add_button = tk.Button(
            button_frame, 
            image=self.icons["add"],
            bg="#3d3d3d",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            width=40,
            height=40,
            command=self.add_to_playlist
        )
        self.add_button.grid(row=0, column=6, padx=3)

        # Frame volume à droite (largeur fixe identique)
        volume_frame = ttk.Frame(buttons_volume_frame, width=180)
        volume_frame.grid(row=0, column=2, sticky="e")
        volume_frame.grid_propagate(False)  # Empêcher le redimensionnement

        ttk.Label(volume_frame, text="Volume").pack()
        self.volume_slider = ttk.Scale(
            volume_frame, from_=0, to=100, 
            command=self.set_volume, value=self.volume*100,
            orient='horizontal',
            length=150
        )
        self.volume_slider.pack(padx=15)

        # Configuration des colonnes pour centrage parfait
        buttons_volume_frame.grid_columnconfigure(0, weight=1)  # volume offset - prend l'espace
        buttons_volume_frame.grid_columnconfigure(1, weight=0)  # boutons centrés - taille fixe
        buttons_volume_frame.grid_columnconfigure(2, weight=1)  # volume - prend l'espace

        
        # Status Bar
        self.status_bar = ttk.Label(
            control_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(10,0))
        
        ## Bouton Show Waveform
        self.show_waveform_btn = tk.Button(
            control_frame,
            text="Show Waveform",
            command=self.show_waveform_on_clicked,
            bg="#3d3d3d",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            padx=10,
            pady=5
        )
        self.show_waveform_btn.pack(pady=(0, 10))
        
        # Waveform Canvas
        self.waveform_canvas = tk.Canvas(waveform_frame, height=0, bg='#2d2d2d', highlightthickness=0)
        self.waveform_canvas.pack(fill=tk.X, pady=0)
        # Canvas starts with height=0, will expand when waveform button is clicked
        
        # Bind resize event to update waveform when window is resized
        self.waveform_canvas.bind('<Configure>', self.on_waveform_canvas_resize)

def setup_keyboard_bindings(self):
        """Configure les raccourcis clavier"""
        # Binding pour la barre d'espace (pause/play)
        self.root.bind('<KeyPress-space>', self.on_space_pressed)
        
        # Binding pour retirer le focus des champs de saisie quand on clique ailleurs
        self.root.bind('<Button-1>', self.on_root_click)
        
        # S'assurer que la fenêtre peut recevoir le focus pour les événements clavier
        self.root.focus_set()