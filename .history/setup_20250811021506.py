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
        "rename": "rename.png",
        "cross": "cross.png",
        "search": "search.png",
        "clear": "clear.png",
        "find": "find.png",
        "output": "output.png"
    }

    # Chemin absolu vers le dossier assets
    base_path = os.path.join(os.path.dirname(__file__), "assets")

    self.icons = {}
    for key, filename in icon_names.items():
        try:
            path = os.path.join(base_path, filename)
            image = Image.open(path).resize((32, 32), Image.Resampling.LANCZOS)
            self.icons[key] = ImageTk.PhotoImage(image)
            
            # Créer une version plus petite pour certaines icônes
            if key in ["cross", "search"]:
                image_small = Image.open(path).resize((16, 16), Image.Resampling.LANCZOS)
                self.icons[key + "_small"] = ImageTk.PhotoImage(image_small)
            
            # Créer une version plus petite pour les icônes clear et find
            if key in ["clear", "find"]:
                image_small = Image.open(path).resize((20, 20), Image.Resampling.LANCZOS)
                self.icons[key + "_small"] = ImageTk.PhotoImage(image_small)
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
    
    # Bouton Output en haut à droite
    self.output_button = tk.Button(
        self.main_frame, 
        image=self.icons["output"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        width=20,
        height=20,
        command=self.show_output_devices,
        takefocus=0
    )
    self.output_button.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)
    create_tooltip(self.output_button, "Périphérique de sortie\nChanger le périphérique audio de sortie")
    
    # Contrôles de lecture (créés en premier pour être toujours visibles en bas)
    self.setup_controls()
    
        # Création du Notebook (onglets) - prend l'espace restant
    self.notebook = ttk.Notebook(self.main_frame, takefocus=0)
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
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # Waveform Frame (above song info)
        waveform_frame = ttk.Frame(control_frame)
        waveform_frame.pack(fill=tk.X)
        
        # Song Info
        self.song_label = ttk.Label(
            control_frame, text="No track selected", 
            font=('Helvetica', 12, 'bold')
        )
        self.song_label.pack(pady=(5, 2))
        

        
        # Progress Bar
        self.progress = ttk.Scale(
            control_frame, from_=0, to=100, orient=tk.HORIZONTAL,
            command=self.set_position, takefocus=0
        )
        self.progress.pack(fill=tk.X, pady=2)
        create_tooltip(self.progress, "Barre de progression\nCliquez ou glissez pour naviguer dans la chanson")
        
        self.progress.bind("<Button-1>", self.on_progress_press)   # début drag
        self.progress.bind("<ButtonRelease-1>", self.on_progress_release)  # fin drag
        self.progress.bind("<B1-Motion>", self.on_progress_drag) # pendant drag
        
        # Conteneur horizontal pour volume offset + boutons + volume
        buttons_volume_frame = ttk.Frame(control_frame)
        buttons_volume_frame.pack(fill=tk.X, pady=5)

        # Frame volume offset à gauche (largeur fixe)
        volume_offset_frame = ttk.Frame(buttons_volume_frame, width=180)
        volume_offset_frame.grid(row=0, column=0, sticky="w")
        volume_offset_frame.grid_propagate(False)  # Empêcher le redimensionnement

        # Time Label à gauche (collé au bord gauche)
        self.current_time_label = ttk.Label(volume_offset_frame, text="00:00")
        self.current_time_label.pack(anchor="w", pady=(0, 5))
        
        ttk.Label(volume_offset_frame, text="Volume Offset").pack()
        self.volume_offset_slider = ttk.Scale(
            volume_offset_frame, from_=-75, to=75, 
            command=self.set_volume_offset, value=0,
            orient='horizontal',
            length=150, takefocus=0
        )
        self.volume_offset_slider.pack(padx=15)
        create_tooltip(self.volume_offset_slider, "Volume Offset\nAjuste le volume spécifiquement pour cette chanson\nClic droit: Remettre à 0")
        
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
            command=self.toggle_random_mode,
            takefocus=0
        )
        self.random_button.grid(row=0, column=0, padx=3)
        create_tooltip(self.random_button, "Mode aléatoire\nLit les chansons dans un ordre aléatoire")
        
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
            command=self.toggle_loop_mode,
            takefocus=0
        )
        self.loop_button.grid(row=0, column=1, padx=3)
        create_tooltip(self.loop_button, "Mode répétition\nClic 1: Répète la playlist\nClic 2: Répète la chanson\nClic 3: Désactivé")
        
        # Boutons principaux (taille normale)
        self.prev_button = ttk.Button(button_frame, image=self.icons["prev"], command=self.prev_track, takefocus=0)
        self.prev_button.grid(row=0, column=2, padx=5)
        create_tooltip(self.prev_button, "Chanson précédente\nRevient à la chanson précédente de la playlist")

        self.play_button = ttk.Button(button_frame, image=self.icons["play"], command=self.play_pause, takefocus=0)
        self.play_button.grid(row=0, column=3, padx=5)
        create_tooltip(self.play_button, "Lecture/Pause\nDémarre ou met en pause la lecture\n(Raccourci: Barre d'espace)")
        
        self.next_button = ttk.Button(button_frame, image=self.icons["next"], command=self.next_track, takefocus=0)
        self.next_button.grid(row=0, column=4, padx=5)
        create_tooltip(self.next_button, "Chanson suivante\nPasse à la chanson suivante de la playlist")
        
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
            takefocus=0
        )
        self.hey_button.grid(row=0, column=5, padx=3)
        create_tooltip(self.hey_button, "Bouton Hey\nFonctionnalité spéciale (à définir)")
        
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
            command=self.add_to_playlist,
            takefocus=0
        )
        self.add_button.grid(row=0, column=6, padx=3)
        create_tooltip(self.add_button, "Ajouter des fichiers\nAjoute des fichiers audio à la playlist")

        # Frame volume à droite (largeur fixe identique)
        volume_frame = ttk.Frame(buttons_volume_frame, width=180)
        volume_frame.grid(row=0, column=2, sticky="e")
        volume_frame.grid_propagate(False)  # Empêcher le redimensionnement

        # Time Label à droite (collé au bord droit)
        self.song_length_label = ttk.Label(volume_frame, text="00:00")
        self.song_length_label.pack(anchor="e", pady=(0, 5))
        
        ttk.Label(volume_frame, text="Volume").pack()
        self.volume_slider = ttk.Scale(
            volume_frame, from_=0, to=200, 
            command=self.set_volume, value=self.volume*100,
            orient='horizontal',
            length=150, takefocus=0
        )
        self.volume_slider.pack(padx=15)
        create_tooltip(self.volume_slider, "Volume principal\nAjuste le volume global de l'application")

        # Configuration des colonnes pour centrage parfait
        buttons_volume_frame.grid_columnconfigure(0, weight=1)  # volume offset - prend l'espace
        buttons_volume_frame.grid_columnconfigure(1, weight=0)  # boutons centrés - taille fixe
        buttons_volume_frame.grid_columnconfigure(2, weight=1)  # volume - prend l'espace

        
        # Status Bar
        self.status_bar = ttk.Label(
            control_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(5,0))
        
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
            pady=5,
            takefocus=0
        )
        self.show_waveform_btn.pack(pady=(0, 5))
        create_tooltip(self.show_waveform_btn, "Afficher la forme d'onde\nAffiche/masque la visualisation de la forme d'onde audio")
        
        # Waveform Canvas
        self.waveform_canvas = tk.Canvas(waveform_frame, height=0, bg='#2d2d2d', highlightthickness=0, takefocus=0)
        self.waveform_canvas.pack(fill=tk.X, pady=0)
        # Canvas starts with height=0, will expand when waveform button is clicked
        
        # Bind resize event to update waveform when window is resized
        self.waveform_canvas.bind('<Configure>', self.on_waveform_canvas_resize)

def setup_keyboard_bindings(self):
        """Configure les raccourcis clavier"""
        # Binding pour la barre d'espace (pause/play)
        self.root.bind('<KeyPress-space>', self.on_space_pressed)
        
        # Binding pour la touche Échap
        self.root.bind('<KeyPress-Escape>', self.on_escape_pressed)
        
        # Binding pour retirer le focus des champs de saisie quand on clique ailleurs
        self.root.bind('<Button-1>', self.on_root_click)
        
        # S'assurer que la fenêtre peut recevoir le focus pour les événements clavier
        self.root.focus_set()

def setup_search_tab(self):
    # Top Frame (Youtube search)
    top_frame = ttk.Frame(self.search_tab)
    top_frame.pack(fill=tk.X, pady=(0, 10))
    
    ## Youtube Search Frame
    youtube_frame = ttk.Frame(top_frame)
    youtube_frame.pack(fill=tk.X)

    # Frame pour les cases à cocher (au-dessus de la barre de recherche)
    checkboxes_frame = ttk.Frame(youtube_frame)
    checkboxes_frame.pack(fill=tk.X, pady=(0, 5))

    # Variables pour les cases à cocher
    self.show_artists = tk.BooleanVar(value=True)
    self.show_tracks = tk.BooleanVar(value=True)

    # Case à cocher Artists
    artists_checkbox = tk.Checkbutton(
        checkboxes_frame,
        text="Artists",
        variable=self.show_artists,
        bg='#2d2d2d',
        fg='white',
        selectcolor='#3d3d3d',
        activebackground='#2d2d2d',
        activeforeground='white',
        font=('Arial', 9),
        command=self._on_filter_change,
        takefocus=False
    )
    artists_checkbox.pack(side=tk.RIGHT, padx=(10, 0))

    # Case à cocher Tracks
    tracks_checkbox = tk.Checkbutton(
        checkboxes_frame,
        text="Tracks",
        variable=self.show_tracks,
        bg='#2d2d2d',
        fg='white',
        selectcolor='#3d3d3d',
        activebackground='#2d2d2d',
        activeforeground='white',
        font=('Arial', 9),
        command=self._on_filter_change,
        takefocus=False
    )
    tracks_checkbox.pack(side=tk.RIGHT, padx=(10, 0))

    # Frame pour la barre de recherche
    search_input_frame = ttk.Frame(youtube_frame)
    search_input_frame.pack(fill=tk.X)

    self.youtube_entry = tk.Entry(search_input_frame)
    self.youtube_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    self.youtube_entry.bind('<Return>', lambda event: self.search_youtube())
    self.youtube_entry.bind('<KeyRelease>', self._on_search_entry_change)

    # Bouton pour effacer la recherche YouTube
    clear_youtube_btn = tk.Button(
        search_input_frame,
        image=self.icons["cross_small"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=4,
        pady=4,
        width=20,
        height=20,
        takefocus=0
    )
    clear_youtube_btn.bind("<Button-1>", lambda event: self._clear_youtube_search())
    clear_youtube_btn.pack(side=tk.LEFT, padx=(5, 0))
    create_tooltip(clear_youtube_btn, "Effacer la recherche\nClic pour vider le champ de recherche")

    search_btn = tk.Button(
        search_input_frame,
        image=self.icons["search_small"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=4,
        pady=4,
        width=20,
        height=20,
        command=self.search_youtube,
        takefocus=0
    )
    search_btn.pack(side=tk.LEFT, padx=(5, 0))
    create_tooltip(search_btn, "Rechercher sur YouTube\nLance une recherche de vidéos sur YouTube\n(Raccourci: Entrée dans le champ de recherche)")

    # Middle Frame (Main playlist and results)
    middle_frame = ttk.Frame(self.search_tab)
    middle_frame.pack(fill=tk.BOTH, expand=True)
    
    # Main Playlist Frame (left side - fixed width)
    playlist_frame = ttk.Frame(middle_frame, width=400)
    playlist_frame.pack(side=tk.LEFT, fill=tk.Y)
    playlist_frame.pack_propagate(False)  # Empêcher le redimensionnement automatique
    
    # Frame pour le titre et le bouton clear de la liste de lecture
    playlist_header_frame = tk.Frame(playlist_frame, bg='#2d2d2d')
    playlist_header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
    
    # Titre de la liste de lecture
    playlist_title_label = tk.Label(
        playlist_header_frame,
        text="Liste de lecture",
        bg='#2d2d2d',
        fg='white',
        font=('TkDefaultFont', 12, 'bold')
    )
    playlist_title_label.pack(side=tk.LEFT)
    
    # Selection Info (affiche le nombre d'éléments sélectionnés)
    self.selection_label = tk.Label(
        playlist_header_frame, text="", 
        bg='#2d2d2d',
        fg='#cccccc',
        font=('Helvetica', 10)
    )
    self.selection_label.pack(side=tk.LEFT, padx=(10, 0))
    
    # Frame pour les boutons à droite
    buttons_right_frame = tk.Frame(playlist_header_frame, bg='#2d2d2d')
    buttons_right_frame.pack(side=tk.RIGHT)
    
    # Bouton find pour aller à la musique en cours
    find_current_btn = tk.Button(
        buttons_right_frame,
        image=self.icons["find_small"],
        bg="#4a8fe7",
        fg="white",
        activebackground="#5a9fd8",
        relief="flat",
        bd=0,
        width=20,
        height=20,
        takefocus=0
    )
    find_current_btn.pack(side=tk.LEFT, padx=(0, 5))
    find_current_btn.bind("<Button-1>", self._scroll_to_current_song)
    create_tooltip(find_current_btn, "Aller à la musique en cours\nFait défiler la liste vers la chanson actuellement jouée")
    
    # Bouton clear pour vider la liste de lecture
    clear_playlist_btn = tk.Button(
        buttons_right_frame,
        image=self.icons["clear_small"],
        bg="#d32f2f",
        fg="white",
        activebackground="#f44336",
        relief="flat",
        bd=0,
        width=20,
        height=20,
        takefocus=0
    )
    clear_playlist_btn.pack(side=tk.LEFT)
    # Binding pour double-clic au lieu de simple clic
    clear_playlist_btn.bind("<Double-1>", self._clear_main_playlist)
    create_tooltip(clear_playlist_btn, "Double-cliquer pour vider la liste de lecture\nSupprime toutes les musiques de la liste")

    # Canvas et Scrollbar pour la main playlist
    self.playlist_canvas = tk.Canvas(
        playlist_frame,
        bg='#3d3d3d',
        highlightthickness=0,
        takefocus=0
    )
    self.playlist_scrollbar = ttk.Scrollbar(
        playlist_frame,
        orient="vertical",
        command=self.playlist_canvas.yview
    )
    self.playlist_canvas.configure(yscrollcommand=self.playlist_scrollbar.set)

    self.playlist_scrollbar.pack(side="right", fill="y")
    self.playlist_canvas.pack(side="left", fill="both", expand=True)

    self.playlist_container = ttk.Frame(self.playlist_canvas)
    self.playlist_canvas.create_window((0, 0), window=self.playlist_container, anchor="nw")

    self.playlist_container.bind(
        "<Configure>",
        lambda e: self.playlist_canvas.configure(
            scrollregion=self.playlist_canvas.bbox("all")
        )
    )
    self._bind_mousewheel(self.playlist_canvas, self.playlist_canvas)
    self._bind_mousewheel(self.playlist_container, self.playlist_canvas)
    
    # Youtube Results Frame (right side - expandable)
    youtube_results_frame = ttk.Frame(middle_frame)
    youtube_results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Frame pour la miniature (sans scrollbar, collée à gauche)
    self.thumbnail_frame = tk.Frame(
        youtube_results_frame,
        bg='#3d3d3d',
        height=300,  # Hauteur fixe raisonnable pour la miniature
    )
    # Afficher la frame thumbnail par défaut
    self.thumbnail_frame.pack(fill='both', pady=5, padx=5, anchor="center")

    # Canvas avec Scrollbar pour les résultats YouTube (masqués par défaut)
    self.youtube_canvas = tk.Canvas(
        youtube_results_frame,
        bg='#3d3d3d',
        highlightthickness=0,
        takefocus=0
    )
    
    self.scrollbar = ttk.Scrollbar(
        youtube_results_frame,
        orient="vertical",
        command=self.youtube_canvas.yview
    )
    
    # Configuration du scroll avec détection
    def on_canvas_scroll(*args):
        self.scrollbar.set(*args)
        self.youtube_canvas.after_idle(self._check_scroll_position)
    
    self.youtube_canvas.configure(yscrollcommand=on_canvas_scroll)

    # Ne pas afficher le canvas et scrollbar par défaut
    # self.scrollbar.pack(side="right", fill="y")
    # self.youtube_canvas.pack(side="left", fill="both", expand=True)

    self.results_container = ttk.Frame(self.youtube_canvas)
    self.youtube_canvas.create_window((0, 0), window=self.results_container, anchor="nw")

    self.results_container.bind(
        "<Configure>",
        lambda e: self.youtube_canvas.configure(
            scrollregion=self.youtube_canvas.bbox("all")
        )
    )
    
    self._bind_mousewheel(self.youtube_canvas, self.youtube_canvas)
    self._bind_mousewheel(self.results_container, self.youtube_canvas)
    
    # Bind scroll event pour charger plus de résultats
    self.youtube_canvas.bind('<Configure>', self._on_youtube_canvas_configure)
    self.youtube_canvas.bind('<MouseWheel>', self._on_youtube_scroll)
    
    # Bind aussi sur la scrollbar pour détecter les changements
    self.scrollbar.bind('<ButtonRelease-1>', self._on_scrollbar_release)
    
    # Afficher la miniature de la chanson en cours au démarrage
    self._show_current_song_thumbnail()
    

def setup_library_tab(self):
    """Configure le contenu de l'onglet Bibliothèque avec onglets verticaux"""
    # Frame principal horizontal
    main_library_frame = ttk.Frame(self.library_tab)
    main_library_frame.pack(fill=tk.BOTH, expand=True)
    
    # Frame pour les onglets verticaux (à gauche)
    vertical_tabs_frame = ttk.Frame(main_library_frame, width=150)
    vertical_tabs_frame.pack(side=tk.LEFT, fill=tk.Y)
    vertical_tabs_frame.pack_propagate(False)  # Maintenir la largeur fixe
    
    # Frame pour le contenu (à droite)
    self.library_content_frame = ttk.Frame(main_library_frame)
    self.library_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Variables pour les onglets
    self.current_library_tab = "téléchargées"
    
    # Créer les boutons d'onglets verticaux
    self.library_tab_buttons = {}
    
    # Onglet "Téléchargées"
    self.downloads_btn = tk.Button(
        vertical_tabs_frame,
        text="Téléchargées " + f"({self.num_downloaded_files})",
        command=lambda: self.switch_library_tab("téléchargées"),
        bg="#4a8fe7",
        fg="white",
        activebackground="#5a9fd8",
        relief="flat",
        bd=0,
        padx=10,
        pady=10,
        anchor="w",
        takefocus=0
    )
    self.downloads_btn.pack(fill=tk.X, pady=2)
    self.library_tab_buttons["téléchargées"] = self.downloads_btn
    create_tooltip(self.downloads_btn, "Fichiers téléchargés\nAffiche tous les fichiers audio téléchargés depuis YouTube")
    
    # Onglet "Playlists"
    playlists_btn = tk.Button(
        vertical_tabs_frame,
        text="Playlists",
        command=lambda: self.switch_library_tab("playlists"),
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=10,
        pady=10,
        anchor="w",
        takefocus=0
    )
    playlists_btn.pack(fill=tk.X, pady=2)
    self.library_tab_buttons["playlists"] = playlists_btn
    create_tooltip(playlists_btn, "Playlists personnalisées\nGère et affiche vos playlists personnalisées")
    
    # Initialiser avec l'onglet "téléchargées"
    self.switch_library_tab("téléchargées")