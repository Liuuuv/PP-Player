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
# from pytube import Search



from config import*
import setup


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pipi Player")
        self.root.geometry(GEOMETRY)
        self.root.resizable(False, False)  # Empêcher le redimensionnement
        self.root.configure(bg='#2d2d2d')
        root.option_add("*Button.takeFocus", 0)
        
        setup.setup_window_icon(self)
        
        
        # Initialisation pygame
        pygame.mixer.init()
        
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        # Récupérer les données audio pour visualisation
        samples = pygame.sndarray.array(pygame.mixer.music)
        self.waveform_data = None
        self.waveform_data_raw = None
        
        # Variables
        self.main_playlist = []
        self.current_index = 0
        self.paused = False
        self.volume = 0.1
        self.volume_offset = 0  # Offset de volume en pourcentage (-50 à +50)
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
            # Ajout pour le streaming progressif
            'external_downloader': 'ffmpeg',
            # Optimisations pour la recherche
            # 'extract_flat': True,
            # 'simulate': True,
            # 'skip_download': True,
        }
        self.is_searching = False
        self.current_search_query = ""
        self.search_results_count = 0
        self.max_search_results = 50
        self.results_per_page = 10
        self.is_loading_more = False
        self.current_search_batch = 1
        self.max_search_batchs = self.max_search_results // self.results_per_page + 1
        self.all_search_results = []
        
        self.num_downloaded_files = 0

        self.song_length = 0
        self.current_time = 0
        
        self.user_dragging = False
        self.base_position = 0
        
        self.show_waveform_current = False
        
        # Variables pour les modes de lecture
        self.random_mode = False
        self.loop_mode = 0  # 0: désactivé, 1: loop playlist, 2: loop chanson actuelle
        
        # Variables pour la gestion du volume
        self.volume_offsets = {}  # Dictionnaire {filepath: offset_volume}
        self.config_file = os.path.join("downloads", "player_config.json")
        self.initializing = True  # Flag pour éviter de sauvegarder pendant l'initialisation
        
        # Chargement des icônes
        self.icons = {}
        self.load_icons()
        
        # UI Modern
        self.create_ui()
        
        # Mettre à jour les sliders avec les valeurs chargées
        self._update_volume_sliders()
        
        # Marquer la fin de l'initialisation
        self.initializing = False
        
        # Thread de mise à jour
        self.update_thread = threading.Thread(target=self.update_time, daemon=True)
        self.update_thread.start()
        
        self.current_downloads = set()  # Pour suivre les URLs en cours de téléchargement
        self.resize_timer = None  # Pour éviter de redessiner trop souvent pendant le redimensionnement
        
        # Variables pour l'optimisation de la recherche
        self.search_timer = None  # Timer pour le debounce de la recherche
        self.search_delay = 300  # Délai en millisecondes avant de lancer la recherche
        self.normalized_filenames = {}  # Cache des noms de fichiers normalisés
        
        # Variables pour les playlists
        self.playlists = {}  # Dictionnaire {nom_playlist: [liste_fichiers]}
        self.current_playlist_name = "Main Playlist"  # Main playlist par défaut
        self.playlists[self.current_playlist_name] = []  # Initialiser la main playlist
        # Faire pointer self.main_playlist vers la main playlist pour compatibilité
        self.main_playlist = self.playlists[self.current_playlist_name]
        self.current_viewing_playlist = None  # Playlist actuellement visualisée
        self.main_playlist_from_playlist = False  # True si la main playlist provient d'une playlist
        
        # Variables pour la sélection multiple
        self.selected_items = set()  # Set des chemins de fichiers sélectionnés
        self.selection_frames = {}  # Dictionnaire {filepath: frame} pour retrouver les frames
        self.shift_selection_active = False  # True quand on est en mode sélection Shift
        
        # Charger les playlists sauvegardées
        self.load_playlists()
        
        # Charger la configuration (volume global et offsets)
        self.load_config()
        
        # Compter les fichiers téléchargés au démarrage
        self._count_downloaded_files()
        
        # Bindings de clavier
        self.setup_keyboard_bindings()

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

    def setup_keyboard_bindings(self):
        """Configure les raccourcis clavier"""
        # Binding pour la barre d'espace (pause/play)
        self.root.bind('<KeyPress-space>', self.on_space_pressed)
        
        # Binding pour retirer le focus des champs de saisie quand on clique ailleurs
        self.root.bind('<Button-1>', self.on_root_click)
        
        # S'assurer que la fenêtre peut recevoir le focus pour les événements clavier
        self.root.focus_set()
    
    def on_space_pressed(self, event):
        """Gère l'appui sur la barre d'espace"""
        # Vérifier si le focus n'est pas sur un champ de saisie
        focused_widget = self.root.focus_get()
        if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
            # Si le focus est sur un champ de saisie, ne pas intercepter la barre d'espace
            return
        
        # Appeler la fonction play_pause
        self.play_pause()
        
        # Empêcher la propagation de l'événement
        return "break"
    
    def on_root_click(self, event):
        """Gère les clics sur la fenêtre principale pour retirer le focus des champs de saisie"""
        # Obtenir le widget qui a été cliqué
        clicked_widget = event.widget
        
        # Si on clique sur un champ de saisie, ne rien faire (laisser le focus)
        if isinstance(clicked_widget, (tk.Entry, tk.Text)):
            return
        
        # Vérifier si on clique sur un parent d'un champ de saisie
        parent = clicked_widget
        while parent:
            if isinstance(parent, (tk.Entry, tk.Text)):
                return
            try:
                parent = parent.master
            except:
                break
        
        # Si on arrive ici, on n'a pas cliqué sur un champ de saisie
        # Retirer le focus de tous les champs de saisie
        focused_widget = self.root.focus_get()
        if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
            self.root.focus_set()  # Donner le focus à la fenêtre principale
    
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
    
    def on_tab_changed(self, event):
        """Gère le changement d'onglet"""
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Recherche":
            # Vous pourriez ajouter ici des actions spécifiques au changement d'onglet
            pass
        elif selected_tab == "Bibliothèque":
            # Vous pourriez ajouter ici des actions spécifiques au changement d'onglet
            pass
    
    def setup_search_tab(self):
        # Top Frame (Youtube search)
        top_frame = ttk.Frame(self.search_tab)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ## Youtube Search Frame
        youtube_frame = ttk.Frame(top_frame)
        youtube_frame.pack(fill=tk.X)

        self.youtube_entry = tk.Entry(youtube_frame)
        self.youtube_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.youtube_entry.bind('<Return>', lambda event: self.search_youtube())
        self.youtube_entry.bind('<KeyRelease>', self._on_search_entry_change)

        # Bouton pour effacer la recherche YouTube
        clear_youtube_btn = tk.Button(
            youtube_frame,
            image=self.icons["delete"],
            bg="#3d3d3d",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            font=('TkDefaultFont', 10)
        )
        clear_youtube_btn.bind("<Double-1>", lambda event: self._clear_youtube_search())
        clear_youtube_btn.pack(side=tk.LEFT, padx=(5, 0))

        search_btn = ttk.Button(youtube_frame, text="Rechercher", command=self.search_youtube)
        search_btn.pack(side=tk.LEFT)
    
        # Middle Frame (Main playlist and results)
        middle_frame = ttk.Frame(self.search_tab)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main Playlist Frame (left side - fixed width)
        playlist_frame = ttk.Frame(middle_frame, width=400)
        playlist_frame.pack(side=tk.LEFT, fill=tk.Y)
        playlist_frame.pack_propagate(False)  # Empêcher le redimensionnement automatique

        # Canvas et Scrollbar pour la main playlist
        self.playlist_canvas = tk.Canvas(
            playlist_frame,
            bg='#3d3d3d',
            highlightthickness=0
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
            highlightthickness=0
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
            anchor="w"
        )
        self.downloads_btn.pack(fill=tk.X, pady=2)
        self.library_tab_buttons["téléchargées"] = self.downloads_btn
        
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
            anchor="w"
        )
        playlists_btn.pack(fill=tk.X, pady=2)
        self.library_tab_buttons["playlists"] = playlists_btn
        
        # Initialiser avec l'onglet "téléchargées"
        self.switch_library_tab("téléchargées")
    
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

    
    def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
        style = ttk.Style()
        color_index = 0

        for child in widget.winfo_children():
            # Si c'est un ttk.Frame → appliquer un style
            if isinstance(child, ttk.Frame):
                style_name = f"Debug.TFrame{color_index}"
                style.layout(style_name, style.layout("TFrame"))
                style.configure(style_name, background=colors[color_index % len(colors)])
                child.configure(style=style_name)
                color_index += 1

            # Si c'est un tk.Frame → appliquer une couleur directement
            elif isinstance(child, tk.Frame):
                child.configure(bg=colors[color_index % len(colors)])
                color_index += 1

            # Récursif sur les enfants
            self.colorize_ttk_frames(child, colors)


        
        
    
    def _on_youtube_canvas_configure(self, event):
        """Vérifie si on doit charger plus de résultats quand le canvas change"""
        if self._should_load_more_results():
            self._load_more_search_results()
    
    def _on_youtube_scroll(self, event):
        """Gère le scroll de la molette dans les résultats YouTube"""
        # Scroll normal
        self.youtube_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Vérifier si on doit charger plus de résultats
        if self._should_load_more_results():
            self._load_more_search_results()
    
    def _should_load_more_results(self):
        """Vérifie si on doit charger plus de résultats"""
        if (self.is_loading_more or 
            self.is_searching or
            not self.current_search_query or 
            self.search_results_count >= self.max_search_results or
            self.current_search_batch >= self.max_search_batchs):  # Maximum 3 lots (30 résultats)
            return False
        
        # Vérifier si on est proche du bas
        try:
            # Obtenir la position actuelle du scroll (0.0 à 1.0)
            scroll_top, scroll_bottom = self.youtube_canvas.yview()
            
            # Si on est à plus de 80% vers le bas, charger plus
            if scroll_bottom > 0.8:
                print(f"Scroll détecté: {scroll_bottom:.2f}, chargement du lot {self.current_search_batch + 1}...")
                return True
            
            return False
        except Exception as e:
            print(f"Erreur détection scroll: {e}")
            return False
    
    def _on_scrollbar_release(self, event):
        """Appelée quand on relâche la scrollbar"""
        self._check_scroll_position()
    
    def _check_scroll_position(self):
        """Vérifie la position du scroll et charge plus si nécessaire"""
        if self._should_load_more_results():
            self._load_more_search_results()
    
    
    
    def switch_library_tab(self, tab_name):
        """Change l'onglet actif dans la bibliothèque"""
        self.current_library_tab = tab_name
        
        # Mettre à jour l'apparence des boutons
        for name, button in self.library_tab_buttons.items():
            if name == tab_name:
                button.config(bg="#4a8fe7")  # Actif
            else:
                button.config(bg="#3d3d3d")  # Inactif
        
        # Vider le contenu actuel
        for widget in self.library_content_frame.winfo_children():
            widget.destroy()
        
        # Afficher le contenu selon l'onglet
        if tab_name == "téléchargées":
            self.show_downloads_content()
        elif tab_name == "playlists":
            self.show_playlists_content()
    
    def show_downloads_content(self):
        """Affiche le contenu de l'onglet téléchargées"""
        
        # Frame pour la barre de recherche
        search_frame = ttk.Frame(self.library_content_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        # Barre de recherche
        self.library_search_entry = tk.Entry(
            search_frame,
            bg='#3d3d3d',
            fg='white',
            insertbackground='white',
            relief='flat',
            bd=5
        )
        self.library_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Lier l'événement de saisie pour la recherche en temps réel
        self.library_search_entry.bind('<KeyRelease>', self._on_library_search_change)
        
        # Bouton pour effacer la recherche
        clear_btn = tk.Button(
            search_frame,
            image=self.icons["delete"],
            bg="#3d3d3d",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            padx=8,
            pady=2
        )
        clear_btn.bind("<Double-1>", lambda event: self._clear_library_search())
        clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Canvas avec scrollbar pour les téléchargements
        self.downloads_canvas = tk.Canvas(
            self.library_content_frame,
            bg='#3d3d3d',
            highlightthickness=0
        )
        self.downloads_scrollbar = ttk.Scrollbar(
            self.library_content_frame,
            orient="vertical",
            command=self.downloads_canvas.yview
        )
        self.downloads_canvas.configure(yscrollcommand=self.downloads_scrollbar.set)
        
        self.downloads_scrollbar.pack(side="right", fill="y")
        self.downloads_canvas.pack(side="left", fill="both", expand=True)
        
        self.downloads_container = ttk.Frame(self.downloads_canvas)
        self.downloads_canvas.create_window((0, 0), window=self.downloads_container, anchor="nw")
        
        self.downloads_container.bind(
            "<Configure>",
            lambda e: self.downloads_canvas.configure(
                scrollregion=self.downloads_canvas.bbox("all")
            )
        )
        
        self._bind_mousewheel(self.downloads_canvas, self.downloads_canvas)
        self._bind_mousewheel(self.downloads_container, self.downloads_canvas)
        
        # Initialiser la liste de tous les fichiers téléchargés
        self.all_downloaded_files = []
        
        # Charger et afficher les fichiers téléchargés
        self.load_downloaded_files()
    
    def show_playlists_content(self):
        """Affiche le contenu de l'onglet playlists"""
        
        # Frame pour les boutons de gestion
        management_frame = ttk.Frame(self.library_content_frame)
        management_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        # Bouton créer nouvelle playlist
        create_btn = tk.Button(
            management_frame,
            # text="➕",
            image=self.icons["add"],
            command=lambda: self._create_new_playlist_dialog(),
            bg='#4d4d4d',
            fg="white",
            activebackground="#5a9fd8",
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            font=('TkDefaultFont', 14)
        )
        create_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Canvas avec scrollbar pour les playlists
        self.playlists_canvas = tk.Canvas(
            self.library_content_frame,
            bg='#3d3d3d',
            highlightthickness=0
        )
        self.playlists_scrollbar = ttk.Scrollbar(
            self.library_content_frame,
            orient="vertical",
            command=self.playlists_canvas.yview
        )
        self.playlists_canvas.configure(yscrollcommand=self.playlists_scrollbar.set)
        
        self.playlists_scrollbar.pack(side="right", fill="y")
        self.playlists_canvas.pack(side="left", fill="both", expand=True)
        
        self.playlists_container = ttk.Frame(self.playlists_canvas)
        self.playlists_canvas.create_window((0, 0), window=self.playlists_container, anchor="nw")
        
        self.playlists_container.bind(
            "<Configure>",
            lambda e: self.playlists_canvas.configure(
                scrollregion=self.playlists_canvas.bbox("all")
            )
        )
        
        self._bind_mousewheel(self.playlists_canvas, self.playlists_canvas)
        self._bind_mousewheel(self.playlists_container, self.playlists_canvas)
        
        # Charger et afficher les playlists
        self._display_playlists()
    
    def _display_playlists(self):
        """Affiche toutes les playlists en grille 3x3"""
        # Vider le container actuel
        for widget in self.playlists_container.winfo_children():
            widget.destroy()
        
        # Organiser les playlists en lignes de 3 (exclure la main playlist)
        playlist_items = [(name, songs) for name, songs in self.playlists.items() if name != "Main Playlist"]
        
        for row in range(0, len(playlist_items), 2):
            # Créer un frame pour cette ligne
            row_frame = tk.Frame(self.playlists_container, bg='#3d3d3d')
            row_frame.pack(fill=tk.X, pady=10, padx=10)
            
            # Configurer les colonnes pour qu'elles soient égales
            for col in range(2):
                row_frame.columnconfigure(col, weight=1, uniform="playlist_col")
            
            # Ajouter jusqu'à 2 playlists dans cette ligne
            for col in range(2):
                playlist_index = row + col
                if playlist_index < len(playlist_items):
                    playlist_name, songs = playlist_items[playlist_index]
                    self._add_playlist_card(row_frame, playlist_name, songs, col)
    
    def _add_playlist_card(self, parent_frame, playlist_name, songs, column):
        """Ajoute une carte de playlist avec miniatures"""
        try:
            # Frame principal pour la carte de playlist
            card_frame = tk.Frame(
                parent_frame,
                bg='#4a4a4a',
                relief='flat',
                bd=1,
                highlightbackground='#5a5a5a',
                highlightthickness=1
            )
            card_frame.grid(row=0, column=column, sticky='nsew', padx=10, pady=5)
            
            # Configuration de la grille de la carte
            card_frame.columnconfigure(0, weight=1)
            card_frame.rowconfigure(0, weight=1)  # Zone des miniatures
            card_frame.rowconfigure(1, weight=0)  # Titre
            card_frame.rowconfigure(2, weight=0)  # Nombre de chansons
            card_frame.rowconfigure(3, weight=0)  # Boutons
            
            # 1. Zone des miniatures (2x2 grid) - taille fixe pour uniformité
            thumbnails_frame = tk.Frame(card_frame, bg='#4a4a4a', width=220, height=220)
            thumbnails_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
            thumbnails_frame.grid_propagate(False)  # Maintenir la taille fixe
            
            # Configurer la grille 2x2 pour les miniatures
            for i in range(2):
                thumbnails_frame.columnconfigure(i, weight=1)
                thumbnails_frame.rowconfigure(i, weight=1)
            
            # Ajouter les 4 premières miniatures (ou moins si pas assez de chansons)
            for i in range(4):
                row = i // 2
                col = i % 2
                
                thumbnail_label = tk.Label(
                    thumbnails_frame,
                    bg='#3d3d3d',
                    relief='flat'
                )
                thumbnail_label.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
                
                # Charger la miniature si la chanson existe
                if i < len(songs):
                    self._load_playlist_thumbnail_large(songs[i], thumbnail_label)
                else:
                    # Miniature vide
                    thumbnail_label.config(text="♪", fg='#666666', font=('TkDefaultFont', 20))
            
            # 2. Titre de la playlist
            title_label = tk.Label(
                card_frame,
                text=playlist_name,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 11, 'bold'),
                anchor='center'
            )
            title_label.grid(row=1, column=0, sticky='ew', padx=10, pady=(5, 2))
            
            # 3. Nombre de chansons
            count_label = tk.Label(
                card_frame,
                text=f"{len(songs)} titres",
                bg='#4a4a4a',
                fg='#cccccc',
                font=('TkDefaultFont', 9),
                anchor='center'
            )
            count_label.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 5))
            
            # 4. Boutons
            buttons_frame = tk.Frame(card_frame, bg='#4a4a4a')
            buttons_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=(0, 5))
            
            # Bouton renommer - plus gros
            rename_btn = tk.Button(
                buttons_frame,
                image=self.icons["rename"],
                command=lambda name=playlist_name: self._rename_playlist_dialog(name),
                bg="#ffa500",
                fg="white",
                activebackground="#ffb733",
                relief="flat",
                bd=0,
                width=4,
                height=2,
            )
            rename_btn.pack(side=tk.LEFT, padx=2)
            
            # Bouton supprimer - plus gros et icône complète
            delete_btn = tk.Button(
                buttons_frame,
                image=self.icons["delete"],
                bg="#ff4444",
                fg="white",
                activebackground="#ff6666",
                relief="flat",
                bd=0,
                width=4,
                height=2,
            )
            delete_btn.pack(side=tk.RIGHT, padx=2)
            
            # Double-clic pour supprimer
            delete_btn.bind("<Double-1>", lambda e, name=playlist_name: self._delete_playlist_dialog(name))
            
            # Double-clic pour voir le contenu de la playlist
            def on_playlist_double_click():
                self._show_playlist_content_in_tab(playlist_name)
            
            card_frame.bind("<Double-1>", lambda e: on_playlist_double_click())
            thumbnails_frame.bind("<Double-1>", lambda e: on_playlist_double_click())
            title_label.bind("<Double-1>", lambda e: on_playlist_double_click())
            count_label.bind("<Double-1>", lambda e: on_playlist_double_click())
            
        except Exception as e:
            print(f"Erreur affichage playlist card: {e}")
    
    def _load_playlist_thumbnail_large(self, filepath, label):
        """Charge une miniature carrée plus grande pour une chanson dans une playlist"""
        try:
            # Chercher une image associée (même nom mais extension image)
            base_name = os.path.splitext(filepath)[0]
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            
            thumbnail_found = False
            for ext in image_extensions:
                thumbnail_path = base_name + ext
                if os.path.exists(thumbnail_path):
                    # Charger l'image
                    image = Image.open(thumbnail_path)
                    
                    # Créer une image carrée en cropant au centre
                    width, height = image.size
                    size = min(width, height)
                    left = (width - size) // 2
                    top = (height - size) // 2
                    right = left + size
                    bottom = top + size
                    
                    # Crop au centre pour faire un carré
                    img_cropped = image.crop((left, top, right, bottom))
                    
                    # Redimensionner à une taille plus grande (100x100)
                    img_resized = img_cropped.resize((100, 100), Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(img_resized)
                    label.configure(image=photo, text="")
                    label.image = photo
                    thumbnail_found = True
                    break
            
            if not thumbnail_found:
                # Utiliser une icône par défaut plus grande
                label.config(text="♪", fg='#666666', font=('TkDefaultFont', 20))
                
        except Exception as e:
            print(f"Erreur chargement thumbnail playlist: {e}")
            label.config(text="♪", fg='#666666', font=('TkDefaultFont', 20))

    def _load_playlist_thumbnail(self, filepath, label):
        """Charge une miniature pour une chanson dans une playlist"""
        try:
            # Chercher une image associée (même nom mais extension image)
            base_name = os.path.splitext(filepath)[0]
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            
            thumbnail_found = False
            for ext in image_extensions:
                thumbnail_path = base_name + ext
                if os.path.exists(thumbnail_path):
                    # Charger et redimensionner l'image
                    image = Image.open(thumbnail_path)
                    image = image.resize((75, 56), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    label.configure(image=photo, text="")
                    label.image = photo
                    thumbnail_found = True
                    break
            
            if not thumbnail_found:
                # Utiliser une icône par défaut
                label.config(text="♪", fg='#666666', font=('TkDefaultFont', 12))
                
        except Exception as e:
            print(f"Erreur chargement thumbnail playlist: {e}")
            label.config(text="♪", fg='#666666', font=('TkDefaultFont', 12))
    
    def save_playlists(self):
        """Sauvegarde les playlists dans un fichier JSON"""
        try:
            import json
            playlists_file = os.path.join("downloads", "playlists.json")
            
            # Créer le dossier downloads s'il n'existe pas
            os.makedirs("downloads", exist_ok=True)
            
            # Sauvegarder toutes les playlists sauf la main playlist
            playlists_to_save = {name: songs for name, songs in self.playlists.items() if name != "Main Playlist"}
            
            with open(playlists_file, 'w', encoding='utf-8') as f:
                json.dump(playlists_to_save, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erreur sauvegarde playlists: {e}")
    
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
    
    def save_config(self):
        """Sauvegarde la configuration (volume global et offsets de volume)"""
        try:
            import json
            
            # Créer le dossier downloads s'il n'existe pas
            os.makedirs("downloads", exist_ok=True)
            
            config = {
                "global_volume": self.volume,
                "volume_offsets": self.volume_offsets
            }
            

            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")
    
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
    
    def _rename_playlist_dialog(self, old_name):
        """Dialogue pour renommer une playlist"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Renommer Playlist")
        dialog.geometry("300x150")
        dialog.configure(bg='#2d2d2d')
        dialog.resizable(False, False)
        
        # Centrer la fenêtre
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Label
        label = tk.Label(dialog, text=f"Nouveau nom pour '{old_name}':", 
                        bg='#2d2d2d', fg='white', font=('TkDefaultFont', 10))
        label.pack(pady=20)
        
        # Entry avec le nom actuel
        entry = tk.Entry(dialog, bg='#3d3d3d', fg='white', insertbackground='white',
                        relief='flat', bd=5, font=('TkDefaultFont', 10))
        entry.pack(pady=10, padx=20, fill=tk.X)
        entry.insert(0, old_name)
        entry.select_range(0, tk.END)
        entry.focus()
        
        # Frame pour les boutons
        button_frame = tk.Frame(dialog, bg='#2d2d2d')
        button_frame.pack(pady=20)
        
        def rename_playlist():
            new_name = entry.get().strip()
            if new_name and new_name != old_name and new_name not in self.playlists:
                # Renommer la playlist
                self.playlists[new_name] = self.playlists.pop(old_name)
                self.status_bar.config(text=f"Playlist renommée: '{old_name}' → '{new_name}'")
                self._display_playlists()  # Rafraîchir l'affichage
                self.save_playlists()  # Sauvegarder
                dialog.destroy()
            elif new_name in self.playlists:
                self.status_bar.config(text=f"Playlist '{new_name}' existe déjà")
            elif new_name == old_name:
                dialog.destroy()  # Pas de changement
            else:
                self.status_bar.config(text="Nom de playlist invalide")
        
        def cancel():
            dialog.destroy()
        
        # Boutons
        rename_btn = tk.Button(button_frame, text="Renommer", command=rename_playlist,
                              bg="#ffa500", fg="white", activebackground="#ffb733",
                              relief="flat", bd=0, padx=20, pady=5)
        rename_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Annuler", command=cancel,
                              bg="#666666", fg="white", activebackground="#777777",
                              relief="flat", bd=0, padx=20, pady=5)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        entry.bind('<Return>', lambda e: rename_playlist())
        dialog.bind('<Escape>', lambda e: cancel())
    
    def _delete_playlist_dialog(self, playlist_name):
        """Dialogue pour confirmer la suppression d'une playlist"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Supprimer Playlist")
        dialog.geometry("350x150")
        dialog.configure(bg='#2d2d2d')
        dialog.resizable(False, False)
        
        # Centrer la fenêtre
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Label de confirmation
        label = tk.Label(dialog, text=f"Êtes-vous sûr de vouloir supprimer\nla playlist '{playlist_name}' ?", 
                        bg='#2d2d2d', fg='white', font=('TkDefaultFont', 10),
                        justify=tk.CENTER)
        label.pack(pady=30)
        
        # Frame pour les boutons
        button_frame = tk.Frame(dialog, bg='#2d2d2d')
        button_frame.pack(pady=20)
        
        def delete_playlist():
            del self.playlists[playlist_name]
            self.status_bar.config(text=f"Playlist '{playlist_name}' supprimée")
            self._display_playlists()  # Rafraîchir l'affichage
            self.save_playlists()  # Sauvegarder
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # Boutons
        delete_btn = tk.Button(button_frame, text="Supprimer",
                              bg="#3d3d3d", fg="white", activebackground="#ff6666",
                              relief="flat", bd=0, padx=20, pady=5)
        delete_btn.bind("<Double-1>", lambda event: delete_playlist())
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Annuler", command=cancel,
                              bg="#666666", fg="white", activebackground="#777777",
                              relief="flat", bd=0, padx=20, pady=5)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Escape key
        dialog.bind('<Escape>', lambda e: cancel())
    
    def _show_playlist_content_window(self, playlist_name):
        """Affiche le contenu d'une playlist dans une fenêtre avec le même style que les téléchargements"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Playlist: {playlist_name}")
        dialog.geometry("800x600")
        dialog.configure(bg='#2d2d2d')
        
        # Centrer la fenêtre
        dialog.transient(self.root)
        
        # Titre
        title_label = tk.Label(dialog, text=f"Playlist: {playlist_name}", 
                              bg='#2d2d2d', fg='white', font=('Helvetica', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Canvas avec scrollbar pour les musiques
        canvas = tk.Canvas(
            dialog,
            bg='#3d3d3d',
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            dialog,
            orient="vertical",
            command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        container = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=container, anchor="nw")
        
        container.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        container.bind("<MouseWheel>", _on_mousewheel)
        
        # Afficher les musiques de la playlist
        songs = self.playlists.get(playlist_name, [])
        for filepath in songs:
            self._add_playlist_song_item(container, filepath, playlist_name)
        
        # Bouton fermer
        close_btn = tk.Button(dialog, text="Fermer", command=dialog.destroy,
                             bg="#666666", fg="white", activebackground="#777777",
                             relief="flat", bd=0, padx=20, pady=5)
        close_btn.pack(pady=10)
    
    def _add_playlist_song_item(self, container, filepath, playlist_name):
        """Ajoute un élément de musique dans la fenêtre de playlist (même style que téléchargements)"""
        try:
            filename = os.path.basename(filepath)
            
            # Vérifier si c'est la chanson en cours de lecture
            is_current_song = (len(self.main_playlist) > 0 and 
                             self.current_index < len(self.main_playlist) and 
                             self.main_playlist[self.current_index] == filepath)
            
            # Frame principal
            bg_color = COLOR_SELECTED if is_current_song else '#4a4a4a'
            item_frame = tk.Frame(
                container,
                bg=bg_color,
                relief='flat',
                bd=1,
                highlightbackground='#5a5a5a',
                highlightthickness=1
            )
            item_frame.pack(fill="x", padx=5, pady=2)
            
            # Configuration de la grille
            item_frame.columnconfigure(0, minsize=80, weight=0)  # Miniature
            item_frame.columnconfigure(1, weight=1)              # Texte
            item_frame.columnconfigure(2, minsize=60, weight=0)  # Durée
            item_frame.columnconfigure(3, minsize=120, weight=0) # Boutons
            item_frame.rowconfigure(0, minsize=50, weight=0)
            
            # 1. Miniature
            thumbnail_label = tk.Label(
                item_frame,
                bg=bg_color,
                width=10,
                height=3,
                anchor='center'
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(10, 10), pady=8)
            thumbnail_label.grid_propagate(False)
            
            # Charger la miniature
            self._load_download_thumbnail(filepath, thumbnail_label)
            
            # 2. Texte
            truncated_title = self._truncate_text_for_display(filename)
            title_label = tk.Label(
                item_frame,
                text=truncated_title,
                bg=bg_color,
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left',
                wraplength=170
            )
            title_label.grid(row=0, column=1, sticky='nsew', padx=(0, 10), pady=8)
            
            # 3. Durée
            duration_label = tk.Label(
                item_frame,
                text=self._get_audio_duration(filepath),
                bg=bg_color,
                fg='#cccccc',
                font=('TkDefaultFont', 8),
                anchor='center'
            )
            duration_label.grid(row=0, column=2, sticky='ns', padx=(0, 10), pady=8)
            
            # 4. Boutons
            buttons_frame = tk.Frame(item_frame, bg=bg_color)
            buttons_frame.grid(row=0, column=3, sticky='ns', padx=(0, 10), pady=8)
            
            # Bouton jouer
            play_btn = tk.Button(
                buttons_frame,
                image=self.icons["play"],
                command=lambda f=filepath: self._play_from_playlist(f, playlist_name),
                bg="#4a8fe7",
                fg="white",
                activebackground="#5a9fd8",
                relief="flat",
                bd=0,
                padx=8,
                pady=4,
                font=('TkDefaultFont', 8)
            )
            play_btn.pack(side=tk.LEFT, padx=2)
            
            # Bouton supprimer de la playlist
            remove_btn = tk.Button(
                buttons_frame,
                image=self.icons["delete"],
                bg="#3d3d3d",
                fg="white",
                activebackground="#ff6666",
                relief="flat",
                bd=0,
                padx=8,
                pady=4
            )
            remove_btn.bind("<Double-1>", lambda event, f=filepath: self._remove_from_playlist(f, playlist_name, item_frame, event))
            remove_btn.pack(side=tk.RIGHT, padx=2)
            
        except Exception as e:
            print(f"Erreur affichage playlist song item: {e}")
    
    def _play_from_playlist(self, filepath, playlist_name):
        """Joue une musique depuis une playlist spécifique"""
        # Ajouter à la main playlist si pas déjà présent
        if filepath not in self.main_playlist:
            self.main_playlist.append(filepath)
            self._add_main_playlist_item(filepath)
        
        # Jouer la musique
        self.current_index = self.main_playlist.index(filepath)
        self.play_track()
    
    def _remove_from_playlist(self, filepath, playlist_name, item_frame, event=None):
        """Supprime une musique d'une playlist spécifique"""
        # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
        if event and (event.state & 0x4):  # Ctrl est enfoncé
            self._delete_from_downloads(filepath, item_frame)
        else:
            # Suppression normale de la playlist
            if playlist_name in self.playlists and filepath in self.playlists[playlist_name]:
                self.playlists[playlist_name].remove(filepath)
                item_frame.destroy()
                self.status_bar.config(text=f"Supprimé de '{playlist_name}': {os.path.basename(filepath)}")
                
                # Rafraîchir l'affichage des playlists si on est dans l'onglet playlists
                if hasattr(self, 'current_library_tab') and self.current_library_tab == "playlists":
                    self._display_playlists()
                
                # Sauvegarder les playlists
                self.save_playlists()
    
    def _show_playlist_content_dialog(self, playlist_name):
        """Ancienne méthode - gardée pour compatibilité"""
        self._show_playlist_content_window(playlist_name)
    
    def _show_playlist_content_in_tab(self, playlist_name):
        """Affiche le contenu d'une playlist dans l'onglet bibliothèque (même style que téléchargements)"""
        # Vider le contenu actuel
        for widget in self.library_content_frame.winfo_children():
            widget.destroy()
        
        # Stocker le nom de la playlist en cours de visualisation
        self.current_viewing_playlist = playlist_name
        
        # Frame pour le bouton retour et titre
        header_frame = ttk.Frame(self.library_content_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        # Bouton retour avec icône
        back_btn = tk.Button(
            header_frame,
            image=self.icons["back"],
            command=self._back_to_playlists,
            bg="#4a8fe7",
            fg="white",
            activebackground="#5a9fd8",
            relief="flat",
            bd=0,
            padx=8,
            pady=8
        )
        back_btn.pack(side=tk.LEFT)
        
        # Titre de la playlist avec nombre de chansons
        songs_count = len(self.playlists.get(playlist_name, []))
        title_label = tk.Label(
            header_frame,
            text=f"Playlist: {playlist_name} ({songs_count} titres)",
            bg='#2d2d2d',
            fg='white',
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Canvas avec scrollbar pour les musiques (même style que téléchargements)
        self.playlist_content_canvas = tk.Canvas(
            self.library_content_frame,
            bg='#3d3d3d',
            highlightthickness=0
        )
        self.playlist_content_scrollbar = ttk.Scrollbar(
            self.library_content_frame,
            orient="vertical",
            command=self.playlist_content_canvas.yview
        )
        self.playlist_content_canvas.configure(yscrollcommand=self.playlist_content_scrollbar.set)
        
        self.playlist_content_scrollbar.pack(side="right", fill="y")
        self.playlist_content_canvas.pack(side="left", fill="both", expand=True)
        
        self.playlist_content_container = ttk.Frame(self.playlist_content_canvas)
        self.playlist_content_canvas.create_window((0, 0), window=self.playlist_content_container, anchor="nw")
        
        self.playlist_content_container.bind(
            "<Configure>",
            lambda e: self.playlist_content_canvas.configure(
                scrollregion=self.playlist_content_canvas.bbox("all")
            )
        )
        
        self._bind_mousewheel(self.playlist_content_canvas, self.playlist_content_canvas)
        self._bind_mousewheel(self.playlist_content_container, self.playlist_content_canvas)
        
        # Afficher les musiques de la playlist
        self._display_playlist_songs(playlist_name)
    
    def _back_to_playlists(self):
        """Retourne à l'affichage des playlists"""
        self.current_viewing_playlist = None
        
        # Nettoyer complètement le contenu actuel
        for widget in self.library_content_frame.winfo_children():
            widget.destroy()
        
        # Réafficher le contenu des playlists
        self.show_playlists_content()
    
    def _display_playlist_songs(self, playlist_name):
        """Affiche les musiques d'une playlist avec le même style que les téléchargements"""
        if playlist_name not in self.playlists:
            return
        
        # Vider le container actuel
        for widget in self.playlist_content_container.winfo_children():
            widget.destroy()
        
        songs = self.playlists[playlist_name]
        
        for i, filepath in enumerate(songs):
            self._add_playlist_song_item(filepath, playlist_name, i)
    
    def _add_playlist_song_item(self, filepath, playlist_name, song_index):
        """Ajoute un élément de musique de playlist avec le même visuel que les téléchargements"""
        try:
            filename = os.path.basename(filepath)
            
            # Vérifier si c'est la chanson en cours de lecture
            is_current_song = (len(self.main_playlist) > 0 and 
                             self.current_index < len(self.main_playlist) and 
                             self.main_playlist[self.current_index] == filepath)
            
            # Frame principal - même style que les téléchargements
            bg_color = '#5a9fd8' if is_current_song else '#4a4a4a'
            item_frame = tk.Frame(
                self.playlist_content_container,
                bg=bg_color,
                relief='flat',
                bd=1,
                highlightbackground='#5a5a5a',
                highlightthickness=1
            )
            item_frame.pack(fill="x", padx=5, pady=2)
            
            # Stocker les informations pour pouvoir les retrouver plus tard
            item_frame.filepath = filepath
            item_frame.playlist_name = playlist_name
            item_frame.song_index = song_index
            item_frame.selected = is_current_song
            
            # Configuration de la grille en 5 colonnes : numéro, miniature, texte, durée, bouton
            item_frame.columnconfigure(0, minsize=40, weight=0)  # Numéro
            item_frame.columnconfigure(1, minsize=80, weight=0)  # Miniature
            item_frame.columnconfigure(2, weight=1)              # Texte
            item_frame.columnconfigure(3, minsize=60, weight=0)  # Durée
            item_frame.columnconfigure(4, minsize=80, weight=0)  # Bouton
            item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
            
            # 1. Numéro de la chanson (colonne 0)
            number_label = tk.Label(
                item_frame,
                text=str(song_index + 1),  # +1 pour commencer à 1 au lieu de 0
                bg=bg_color,
                fg='white',
                font=('TkDefaultFont', 10, 'bold'),
                anchor='center'
            )
            number_label.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=8)
            
            # 2. Miniature (colonne 1)
            thumbnail_label = tk.Label(
                item_frame,
                bg=bg_color,
                width=10,
                height=3,
                anchor='center'
            )
            thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=8)
            thumbnail_label.grid_propagate(False)
            
            # Charger la miniature
            self._load_download_thumbnail(filepath, thumbnail_label)
            
            # 3. Texte (colonne 2)
            truncated_title = self._truncate_text_for_display(filename)
            title_label = tk.Label(
                item_frame,
                text=truncated_title,
                bg=bg_color,
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left',
                wraplength=170
            )
            title_label.grid(row=0, column=2, sticky='nsew', padx=(0, 10), pady=8)
            
            # 4. Durée (colonne 3)
            duration_label = tk.Label(
                item_frame,
                text=self._get_audio_duration(filepath),
                bg=bg_color,
                fg='#cccccc',
                font=('TkDefaultFont', 8),
                anchor='center'
            )
            duration_label.grid(row=0, column=3, sticky='ns', padx=(0, 10), pady=8)
            
            # 5. Bouton "Supprimer de la playlist" (colonne 4) avec icône delete
            remove_btn = tk.Button(
                item_frame,
                image=self.icons["delete"],  # Utiliser l'icône delete non rognée
                bg="#3d3d3d",
                activebackground='#ff6666',
                relief='flat',
                bd=0,
                padx=5,
                pady=5
            )
            remove_btn.bind("<Double-1>", lambda event: self._remove_from_playlist_view(filepath, playlist_name, event))
            remove_btn.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
            
            # Double-clic pour lancer la playlist depuis cette musique
            def on_song_double_click():
                self._play_playlist_from_song(playlist_name, song_index)
            
            # Bind double-clic sur tous les éléments
            item_frame.bind("<Double-1>", lambda e: on_song_double_click())
            number_label.bind("<Double-1>", lambda e: on_song_double_click())
            thumbnail_label.bind("<Double-1>", lambda e: on_song_double_click())
            title_label.bind("<Double-1>", lambda e: on_song_double_click())
            duration_label.bind("<Double-1>", lambda e: on_song_double_click())
            
        except Exception as e:
            print(f"Erreur affichage musique playlist: {e}")
    
    def _remove_from_playlist_view(self, filepath, playlist_name, event=None):
        """Supprime une musique de la playlist et rafraîchit l'affichage"""
        # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
        if event and (event.state & 0x4):  # Ctrl est enfoncé
            # Pour la suppression définitive, on utilise une approche différente
            # car on n'a pas de frame à passer
            try:
                if os.path.exists(filepath):
                    # Supprimer le fichier audio
                    os.remove(filepath)
                    
                    # Supprimer la miniature associée si elle existe
                    thumbnail_path = os.path.splitext(filepath)[0] + ".jpg"
                    if os.path.exists(thumbnail_path):
                        os.remove(thumbnail_path)
                    
                    # Supprimer de la playlist
                    if filepath in self.main_playlist:
                        self.main_playlist.remove(filepath)
                    
                    # Supprimer de toutes les playlists
                    for pname, playlist_songs in self.playlists.items():
                        if filepath in playlist_songs:
                            playlist_songs.remove(filepath)
                    
                    # Sauvegarder les playlists
                    self.save_playlists()
                    
                    # Mettre à jour le compteur
                    self._count_downloaded_files()
                    self._update_downloads_button()
                    
                    self.status_bar.config(text=f"Fichier supprimé définitivement: {os.path.basename(filepath)}")
                    
                    # Rafraîchir l'affichage
                    self._display_playlist_songs(playlist_name)
                    self._update_playlist_title(playlist_name)
                    
                    # Rafraîchir la bibliothèque si nécessaire
                    self._refresh_downloads_library()
                    
            except Exception as e:
                self.status_bar.config(text=f"Erreur suppression fichier: {str(e)}")
                print(f"Erreur suppression fichier: {e}")
        else:
            # Suppression normale de la playlist
            if playlist_name in self.playlists and filepath in self.playlists[playlist_name]:
                self.playlists[playlist_name].remove(filepath)
                self.save_playlists()
                # Rafraîchir l'affichage
                self._display_playlist_songs(playlist_name)
                # Mettre à jour le titre avec le nouveau nombre de chansons
                self._update_playlist_title(playlist_name)
    
    def _update_playlist_title(self, playlist_name):
        """Met à jour le titre de la playlist avec le nombre de chansons"""
        if (hasattr(self, 'current_viewing_playlist') and 
            self.current_viewing_playlist == playlist_name):
            # Chercher le label du titre dans l'interface
            for widget in self.library_content_frame.winfo_children():
                if isinstance(widget, ttk.Frame):  # header_frame
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label) and "Playlist:" in child.cget("text"):
                            songs_count = len(self.playlists.get(playlist_name, []))
                            child.config(text=f"Playlist: {playlist_name} ({songs_count} titres)")
                            break
    
    def _play_playlist_from_song(self, playlist_name, song_index):
        """Lance la playlist depuis une musique spécifique"""
        if playlist_name not in self.playlists:
            return
        
        # Copier la playlist dans la main playlist
        self.main_playlist.clear()
        self.main_playlist.extend(self.playlists[playlist_name])
        
        # Marquer que la main playlist provient d'une playlist
        self.main_playlist_from_playlist = True
        
        # Définir l'index de départ
        self.current_index = song_index
        
        # Lancer la lecture
        self.play_track()
        
        # Rafraîchir l'affichage de la playlist principale
        self._refresh_playlist_display()
    
    def load_downloaded_files(self):
        """Charge et affiche tous les fichiers du dossier downloads"""
        downloads_dir = "downloads"
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
            return
        
        # Extensions audio supportées
        audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
        
        # Vider la liste actuelle et le cache
        self.all_downloaded_files = []
        self.normalized_filenames = {}
        
        # Parcourir le dossier downloads et stocker tous les fichiers
        for filename in os.listdir(downloads_dir):
            if filename.lower().endswith(audio_extensions):
                filepath = os.path.join(downloads_dir, filename)
                self.all_downloaded_files.append(filepath)
                
                # Créer le cache du nom normalisé pour accélérer les recherches
                normalized_name = os.path.basename(filepath).lower()
                self.normalized_filenames[filepath] = normalized_name
        
        # Mettre à jour le nombre de fichiers téléchargés
        self.num_downloaded_files = len(self.all_downloaded_files)
        
        # Afficher tous les fichiers (sans filtre)
        self._display_filtered_downloads(self.all_downloaded_files)
        
        # Mettre à jour le texte du bouton
        self._update_downloads_button()
    
    def _display_filtered_downloads(self, files_to_display):
        """Affiche une liste filtrée de fichiers téléchargés (optimisé)"""
        # Vider le container actuel
        for widget in self.downloads_container.winfo_children():
            widget.destroy()
        
        # Afficher les fichiers filtrés par batch pour améliorer les performances
        if len(files_to_display) > 50:  # Si beaucoup de fichiers, les afficher par batch
            self._display_files_batch(files_to_display, 0)
        else:
            # Afficher directement si peu de fichiers
            for filepath in files_to_display:
                self._add_download_item(filepath)
    
    def _display_files_batch(self, files_to_display, start_index, batch_size=20):
        """Affiche les fichiers par batch pour éviter de bloquer l'interface"""
        end_index = min(start_index + batch_size, len(files_to_display))
        
        # Afficher le batch actuel
        for i in range(start_index, end_index):
            self._add_download_item(files_to_display[i])
        
        # Programmer le batch suivant si nécessaire
        if end_index < len(files_to_display):
            self.root.after(10, lambda: self._display_files_batch(files_to_display, end_index, batch_size))
    
    def _on_library_search_change(self, event):
        """Appelée à chaque changement dans la barre de recherche (avec debounce)"""
        # Annuler le timer précédent s'il existe
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        
        # Programmer une nouvelle recherche après le délai
        self.search_timer = self.root.after(self.search_delay, self._perform_library_search)
    
    def _perform_library_search(self):
        """Effectue la recherche réelle (appelée après le délai)"""
        search_term = self.library_search_entry.get().lower().strip()
        
        if not search_term:
            # Si la recherche est vide, afficher tous les fichiers
            self._display_filtered_downloads(self.all_downloaded_files)
        else:
            # Diviser le terme de recherche en mots individuels
            search_words = search_term.split()
            
            # Filtrer les fichiers selon le terme de recherche (optimisé avec cache)
            filtered_files = []
            for filepath in self.all_downloaded_files:
                # Utiliser le cache au lieu de recalculer à chaque fois
                filename = self.normalized_filenames.get(filepath, os.path.basename(filepath).lower())
                
                # Vérifier si tous les mots de recherche sont présents dans le nom de fichier
                all_words_found = all(word in filename for word in search_words)
                
                if all_words_found:
                    filtered_files.append(filepath)
            
            self._display_filtered_downloads(filtered_files)
    
    def _clear_library_search(self):
        """Efface la recherche et affiche tous les fichiers"""
        # Annuler le timer de recherche s'il existe
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
            self.search_timer = None
        
        self.library_search_entry.delete(0, tk.END)
        self._display_filtered_downloads(self.all_downloaded_files)
    
    def _on_search_entry_change(self, event):
        """Appelée quand le contenu du champ de recherche change"""
        query = self.youtube_entry.get().strip()
        
        # Si le champ devient vide, afficher la miniature
        if not query:
            # Vider les résultats de recherche
            self._clear_results()
            
            # Réinitialiser les variables de recherche
            self.current_search_query = ""
            self.search_results_count = 0
            self.current_search_batch = 1
            self.all_search_results = []
            self.is_searching = False
            self.is_loading_more = False
            
            # Afficher la miniature de la chanson en cours
            self._show_current_song_thumbnail()
    
    def _clear_youtube_search(self):
        """Efface la recherche YouTube et vide les résultats"""
        self.youtube_entry.delete(0, tk.END)
        
        # Vider les résultats de recherche
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        # Réinitialiser les variables de recherche
        self.current_search_query = ""
        self.search_results_count = 0
        self.current_search_batch = 1
        self.all_search_results = []
        self.is_searching = False
        self.is_loading_more = False
        
        # Afficher la miniature de la chanson en cours quand il n'y a pas de résultats
        self._show_current_song_thumbnail()
    
    def _show_current_song_thumbnail(self):
        """Affiche la miniature de la chanson en cours dans la frame dédiée"""
        # Vérifier que thumbnail_frame existe
        if not hasattr(self, 'thumbnail_frame'):
            return
        
        # Nettoyer la frame précédente
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()
            
        if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
            current_song = self.main_playlist[self.current_index]
            
            # Label pour la miniature - collé au côté gauche
            thumbnail_label = tk.Label(
                self.thumbnail_frame,
                bg='#3d3d3d',
                text="♪",
                fg='#666666',
                font=('TkDefaultFont', 60)
                
            )
            # Pack à gauche sans padding pour coller au bord
            thumbnail_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
            
            # Charger la vraie miniature si elle existe (version grande et carrée)
            self._load_large_thumbnail(current_song, thumbnail_label)
            
        else:
            # Aucune chanson en cours - juste une grande icône musicale
            no_song_label = tk.Label(
                self.thumbnail_frame,
                text="♪",
                bg='#3d3d3d',
                fg='#666666',
                font=('TkDefaultFont', 60)
            )
            # Pack à gauche sans padding pour coller au bord
            no_song_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    def _add_download_item(self, filepath):
        """Ajoute un élément téléchargé avec le même visuel que les résultats de recherche"""
        try:
            filename = os.path.basename(filepath)
            
            # Vérifier si c'est la chanson en cours de lecture
            is_current_song = (len(self.main_playlist) > 0 and 
                             self.current_index < len(self.main_playlist) and 
                             self.main_playlist[self.current_index] == filepath)
            
            # Frame principal - même style que les résultats YouTube
            bg_color = '#5a9fd8' if is_current_song else '#4a4a4a'
            item_frame = tk.Frame(
                self.downloads_container,
                bg=bg_color,  # Fond bleu si c'est la chanson en cours
                relief='flat',
                bd=1,
                highlightbackground='#5a5a5a',
                highlightthickness=1
            )
            item_frame.pack(fill="x", padx=5, pady=2)
            
            # Stocker le chemin du fichier pour pouvoir le retrouver plus tard
            item_frame.filepath = filepath
            item_frame.selected = is_current_song
            
            # Configuration de la grille en 5 colonnes : miniature, texte, durée, bouton ajouter, bouton supprimer
            item_frame.columnconfigure(0, minsize=80, weight=0)  # Miniature
            item_frame.columnconfigure(1, weight=1)              # Texte
            item_frame.columnconfigure(2, minsize=60, weight=0)  # Durée
            item_frame.columnconfigure(3, minsize=80, weight=0)  # Bouton ajouter
            item_frame.columnconfigure(4, minsize=40, weight=0)  # Bouton supprimer
            item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
            
            # 1. Miniature (colonne 0)
            thumbnail_label = tk.Label(
                item_frame,
                bg=bg_color,  # Même fond que le frame parent
                width=10,
                height=3,
                anchor='center'
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(10, 10), pady=8)
            # Forcer la taille fixe
            thumbnail_label.grid_propagate(False)
            
            # Charger la miniature (chercher un fichier image associé)
            self._load_download_thumbnail(filepath, thumbnail_label)
            
            # 2. Texte (colonne 1)
            truncated_title = self._truncate_text_for_display(filename)
            title_label = tk.Label(
                item_frame,
                text=truncated_title,
                bg=bg_color,  # Même fond que le frame parent
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left',
                wraplength=170  # Même largeur que dans la liste de lecture
            )
            title_label.grid(row=0, column=1, sticky='nsew', padx=(0, 10), pady=8)
            
            # 3. Durée (colonne 2)
            duration_label = tk.Label(
                item_frame,
                text=self._get_audio_duration(filepath),
                bg=bg_color,  # Même fond que le frame parent
                fg='#cccccc',
                font=('TkDefaultFont', 8),
                anchor='center'
            )
            duration_label.grid(row=0, column=2, sticky='ns', padx=(0, 10), pady=8)
            
            # 4. Bouton "Ajouter à la liste de lecture" (colonne 3)
            add_btn = tk.Button(
                item_frame,
                text="▼",
                bg="#4a8fe7",
                fg="white",
                activebackground="#5a9fd8",
                relief="flat",
                bd=0,
                padx=8,
                pady=4,
                font=('TkDefaultFont', 8)
            )
            add_btn.grid(row=0, column=3, sticky='ns', padx=(0, 10), pady=8)
            
            # Configurer la commande après création pour avoir la référence du bouton
            add_btn.config(command=lambda f=filepath, btn=add_btn: self._show_playlist_menu(f, btn))
            
            # Stocker la référence du bouton pour le menu
            add_btn.filepath = filepath
            
            # 5. Bouton de suppression (colonne 4)
            delete_btn = tk.Button(
                item_frame,
                image=self.icons['delete'],
                bg=bg_color,
                fg='white',
                activebackground='#ff6666',
                relief='flat',
                bd=0,
                width=self.icons['delete'].width(),
                height=self.icons['delete'].height(),
                font=('TkDefaultFont', 8)
            )
            delete_btn.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
            
            # Fonction pour gérer la suppression avec double-clic
            def on_delete_double_click(event):
                # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
                if event.state & 0x4:  # Ctrl est enfoncé
                    self._delete_from_downloads(filepath, item_frame)
                else:
                    # Suppression normale : retirer de la playlist seulement
                    if filepath in self.main_playlist:
                        index = self.main_playlist.index(filepath)
                        self.main_playlist.remove(filepath)
                        
                        # Mettre à jour l'index courant si nécessaire
                        if index < self.current_index:
                            self.current_index -= 1
                        elif index == self.current_index:
                            pygame.mixer.music.stop()
                            self.current_index = min(index, len(self.main_playlist) - 1)
                            if len(self.main_playlist) > 0:
                                self.play_track()
                            else:
                                pygame.mixer.music.unload()
                                self._show_current_song_thumbnail()
                        
                        # Rafraîchir l'affichage de la playlist principale
                        self._refresh_playlist_display()
                        
                        self.status_bar.config(text=f"Retiré de la playlist: {os.path.basename(filepath)}")
            
            delete_btn.bind("<Double-1>", on_delete_double_click)
            
            # Gestion des clics (simple et double)
            def on_item_click(event):
                # Vérifier si Shift est enfoncé pour la sélection multiple
                if event.state & 0x1:  # Shift est enfoncé
                    self.shift_selection_active = True
                    self.toggle_item_selection(filepath, item_frame)
                elif self.shift_selection_active and len(self.selected_items) > 0:
                    # Si on était en mode sélection et qu'on clique sans Shift, afficher le menu
                    self.show_selection_menu(event)
                else:
                    # Clic normal sans Shift - effacer la sélection si elle existe
                    if self.selected_items:
                        self.clear_selection()
            
            def on_item_double_click(event):
                # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
                if event.state & 0x4:  # Ctrl est enfoncé
                    self._delete_from_downloads(filepath, item_frame)
                elif event.state & 0x1:  # Shift est enfoncé - ne rien faire sur double-clic
                    pass
                else:
                    # Comportement normal : ajouter et jouer
                    self._add_download_to_playlist(filepath)
                    # Jouer immédiatement
                    if filepath in self.main_playlist:
                        self.current_index = self.main_playlist.index(filepath)
                        self.play_track()
            
            # Bindings pour les clics simples et doubles
            item_frame.bind("<Button-2>", on_item_click)
            item_frame.bind("<Double-1>", on_item_double_click)
            thumbnail_label.bind("<Button-2>", on_item_click)
            thumbnail_label.bind("<Double-1>", on_item_double_click)
            title_label.bind("<Button-2>", on_item_click)
            title_label.bind("<Double-1>", on_item_double_click)
            duration_label.bind("<Button-2>", on_item_click)
            duration_label.bind("<Double-1>", on_item_double_click)
            
            # Clic droit pour placer après la chanson en cours
            def on_item_right_click():
                self._play_after_current(filepath)
            
            item_frame.bind("<Button-3>", lambda e: on_item_right_click())
            thumbnail_label.bind("<Button-3>", lambda e: on_item_right_click())
            title_label.bind("<Button-3>", lambda e: on_item_right_click())
            duration_label.bind("<Button-3>", lambda e: on_item_right_click())
            
        except Exception as e:
            print(f"Erreur affichage download item: {e}")
    
    def _play_after_current(self, filepath):
        """Place une musique juste après celle qui joue actuellement et la lance"""
        try:
            # Ajouter à la main playlist si pas déjà présent
            if filepath not in self.main_playlist:
                self.main_playlist.append(filepath)
            
            # Si une musique joue actuellement
            if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
                # Trouver l'index de la musique à déplacer
                song_index = self.main_playlist.index(filepath)
                
                # Si la musique n'est pas déjà juste après la chanson en cours
                target_position = self.current_index + 1
                
                if song_index != target_position:
                    # Retirer la musique de sa position actuelle
                    self.main_playlist.pop(song_index)
                    
                    # Ajuster l'index cible si nécessaire
                    if song_index < self.current_index:
                        target_position = self.current_index  # L'index actuel a diminué de 1
                    
                    # Insérer à la nouvelle position
                    self.main_playlist.insert(target_position, filepath)
                
                # Passer à cette musique
                self.current_index = target_position
                self.play_track()
                
                # Mettre à jour l'affichage de la playlist
                self._refresh_playlist_display()
                
                self.status_bar.config(text=f"Lecture de: {os.path.basename(filepath)}")
            else:
                # Aucune musique en cours, juste jouer cette musique
                self.current_index = self.main_playlist.index(filepath)
                self.play_track()
                self._refresh_playlist_display()
                self.status_bar.config(text=f"Lecture de: {os.path.basename(filepath)}")
                
        except Exception as e:
            print(f"Erreur _play_after_current: {e}")
            self.status_bar.config(text=f"Erreur lors de la lecture")

    def _load_large_thumbnail(self, filepath, label):
        """Charge une grande miniature carrée pour l'affichage principal"""
        # Chercher une image associée (même nom mais extension image)
        base_name = os.path.splitext(filepath)[0]
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        thumbnail_found = False
        for ext in image_extensions:
            thumbnail_path = base_name + ext
            if os.path.exists(thumbnail_path):
                try:
                    img = Image.open(thumbnail_path)
                    
                    # Créer une image carrée en cropant au centre
                    width, height = img.size
                    size = min(width, height)
                    left = (width - size) // 2
                    top = (height - size) // 2
                    right = left + size
                    bottom = top + size
                    
                    # Crop au centre pour faire un carré
                    img_cropped = img.crop((left, top, right, bottom))
                    
                    # Redimensionner à une grande taille (300x300)
                    img_resized = img_cropped.resize((300, 300), Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(img_resized)
                    label.configure(image=photo,
                                    text="",
                                    width=size,
                                    height=size
                    )
                    label.image = photo
                    thumbnail_found = True
                    break
                except Exception as e:
                    print(f"Erreur chargement grande miniature: {e}")
                    continue
        
        if not thumbnail_found:
            # Garder l'icône par défaut
            pass

    def _load_download_thumbnail(self, filepath, label):
        """Charge la miniature pour un fichier téléchargé"""
        # Chercher une image associée (même nom mais extension image)
        base_name = os.path.splitext(filepath)[0]
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        thumbnail_found = False
        for ext in image_extensions:
            thumbnail_path = base_name + ext
            if os.path.exists(thumbnail_path):
                self._load_image_thumbnail(thumbnail_path, label)
                thumbnail_found = True
                break
        
        if not thumbnail_found:
            # Utiliser la miniature MP3 ou une image par défaut
            self._load_mp3_thumbnail(filepath, label)
    
    def _truncate_text_for_display(self, text, max_chars_per_line=25, max_lines=2):
        """Tronque le texte pour l'affichage avec des '...' si nécessaire"""
        # Nettoyer le nom de fichier (enlever l'extension .mp3)
        if text.lower().endswith('.mp3'):
            text = text[:-4]
        
        # Si le texte est court, le retourner tel quel
        if len(text) <= max_chars_per_line:
            return text
        
        # Diviser le texte en mots
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Vérifier si ajouter ce mot dépasserait la limite de caractères
            test_line = current_line + (" " if current_line else "") + word
            
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                # Si on a déjà atteint le nombre max de lignes
                if len(lines) >= max_lines - 1:
                    # Tronquer la ligne actuelle et ajouter "..."
                    if len(current_line) + 3 <= max_chars_per_line:
                        current_line += "..."
                    else:
                        # Enlever des caractères pour faire de la place aux "..."
                        current_line = current_line[:max_chars_per_line-3] + "..."
                    lines.append(current_line)
                    break
                else:
                    # Ajouter la ligne actuelle et commencer une nouvelle
                    if current_line:
                        lines.append(current_line)
                    current_line = word
        
        # Ajouter la dernière ligne si elle n'a pas été ajoutée et si on n'a pas dépassé le max
        if current_line and len(lines) < max_lines:
            lines.append(current_line)
        elif current_line and len(lines) == max_lines:
            # Si on a exactement max_lines et qu'il reste du texte, tronquer la dernière ligne
            if len(lines) > 0:
                last_line = lines[-1]
                if len(last_line) + 3 <= max_chars_per_line:
                    lines[-1] = last_line + "..."
                else:
                    lines[-1] = last_line[:max_chars_per_line-3] + "..."
        
        # S'assurer qu'on ne dépasse jamais max_lines
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            # Ajouter "..." à la dernière ligne si pas déjà présent
            if not lines[-1].endswith("..."):
                if len(lines[-1]) + 3 <= max_chars_per_line:
                    lines[-1] += "..."
                else:
                    lines[-1] = lines[-1][:max_chars_per_line-3] + "..."
        
        return "\n".join(lines)
    
    def _get_audio_duration(self, filepath):
        """Récupère la durée d'un fichier audio"""
        try:
            if filepath.lower().endswith('.mp3'):
                audio = MP3(filepath)
                duration = audio.info.length
            else:
                # Pour les autres formats, utiliser pydub
                audio = AudioSegment.from_file(filepath)
                duration = len(audio) / 1000.0  # pydub donne en millisecondes
            
            return time.strftime('%M:%S', time.gmtime(duration))
        except:
            return "??:??"
    
    def _show_playlist_menu(self, filepath, button):
        """Affiche un menu déroulant pour choisir la playlist"""
        import tkinter.ttk as ttk
        
        # Créer un menu contextuel
        menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
                      activebackground='#4a8fe7', activeforeground='white')
        
        # Ajouter les playlists existantes
        for playlist_name in self.playlists.keys():
            menu.add_command(
                label=f"Ajouter à '{playlist_name}'",
                command=lambda name=playlist_name: self._add_to_specific_playlist(filepath, name)
            )
        
        menu.add_separator()
        
        # Option pour créer une nouvelle playlist
        menu.add_command(
            label="Créer nouvelle playlist...",
            command=lambda: self._create_new_playlist_dialog(filepath)
        )
        
        # Afficher le menu à la position du bouton
        try:
            # Obtenir la position du bouton
            x = button.winfo_rootx() if button else self.root.winfo_pointerx()
            y = button.winfo_rooty() + button.winfo_height() if button else self.root.winfo_pointery()
            menu.post(x, y)
        except:
            # Fallback si on ne peut pas obtenir la position
            menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def _add_to_specific_playlist(self, filepath, playlist_name):
        """Ajoute un fichier à une playlist spécifique"""
        if playlist_name == "Main Playlist":
            # Pour la main playlist, utiliser l'ancienne méthode
            if filepath not in self.main_playlist:
                self.main_playlist.append(filepath)
                self._add_main_playlist_item(filepath)
                self.status_bar.config(text=f"Ajouté à la liste de lecture principale: {os.path.basename(filepath)}")
            else:
                self.status_bar.config(text=f"Déjà dans la liste de lecture principale: {os.path.basename(filepath)}")
        else:
            # Pour les autres playlists
            if filepath not in self.playlists[playlist_name]:
                self.playlists[playlist_name].append(filepath)
                self.status_bar.config(text=f"Ajouté à '{playlist_name}': {os.path.basename(filepath)}")
                self.save_playlists()  # Sauvegarder
            else:
                self.status_bar.config(text=f"Déjà dans '{playlist_name}': {os.path.basename(filepath)}")
    
    def _create_new_playlist_dialog(self, filepath=None):
        """Dialogue pour créer une nouvelle playlist"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouvelle Playlist")
        dialog.geometry("300x150")
        dialog.configure(bg='#2d2d2d')
        dialog.resizable(False, False)
        
        # Centrer la fenêtre
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Label
        label = tk.Label(dialog, text="Nom de la nouvelle playlist:", 
                        bg='#2d2d2d', fg='white', font=('TkDefaultFont', 10))
        label.pack(pady=20)
        
        # Entry
        entry = tk.Entry(dialog, bg='#3d3d3d', fg='white', insertbackground='white',
                        relief='flat', bd=5, font=('TkDefaultFont', 10))
        entry.pack(pady=10, padx=20, fill=tk.X)
        entry.focus()
        
        # Frame pour les boutons
        button_frame = tk.Frame(dialog, bg='#2d2d2d')
        button_frame.pack(pady=20)
        
        def create_playlist():
            name = entry.get().strip()
            if name and name not in self.playlists:
                self.playlists[name] = []
                if filepath:
                    self.playlists[name].append(filepath)
                    self.status_bar.config(text=f"Playlist '{name}' créée et fichier ajouté")
                else:
                    self.status_bar.config(text=f"Playlist '{name}' créée")
                
                # Rafraîchir l'affichage des playlists si on est dans l'onglet playlists
                if hasattr(self, 'current_library_tab') and self.current_library_tab == "playlists":
                    self._display_playlists()
                
                # Sauvegarder les playlists
                self.save_playlists()
                
                dialog.destroy()
            elif name in self.playlists:
                self.status_bar.config(text=f"Playlist '{name}' existe déjà")
            else:
                self.status_bar.config(text="Nom de playlist invalide")
        
        def cancel():
            dialog.destroy()
        
        # Boutons
        create_btn = tk.Button(button_frame, text="Créer", command=create_playlist,
                              bg="#4a8fe7", fg="white", activebackground="#5a9fd8",
                              relief="flat", bd=0, padx=20, pady=5)
        create_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Annuler", command=cancel,
                              bg="#666666", fg="white", activebackground="#777777",
                              relief="flat", bd=0, padx=20, pady=5)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        entry.bind('<Return>', lambda e: create_playlist())
        dialog.bind('<Escape>', lambda e: cancel())
    
    def _add_download_to_playlist(self, filepath):
        """Ajoute un fichier téléchargé à la main playlist (pour compatibilité)"""
        self._add_to_specific_playlist(filepath, "Main Playlist")
    
    
    
    # def add_to_playlist(self):
    #     files = filedialog.askopenfilenames(
    #         filetypes=[("Fichiers Audio", "*.mp3 *.wav *.ogg *.flac"), ("Tous fichiers", "*.*")]
    #     )
    #     for file in files:
    #         self.main_playlist.append(file)
    #         self.playlist_box.insert(tk.END, os.path.basename(file))
    #     self.status_bar.config(text=f"{len(files)} track added")
    
    def _bind_mousewheel(self, widget, canvas):
        """Lie la molette de souris seulement quand le curseur est sur le widget"""
        widget.bind("<Enter>", lambda e: self._bind_scroll(canvas))
        widget.bind("<Leave>", lambda e: self._unbind_scroll(canvas))

    def _bind_scroll(self, canvas):
        """Active le défilement pour un canvas spécifique"""
        canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind_all("<Button-4>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind_all("<Button-5>", lambda e: self._on_mousewheel(e, canvas))

    def _unbind_scroll(self, canvas):
        """Désactive le défilement pour un canvas spécifique"""
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
    
    def add_to_playlist(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Fichiers Audio", "*.mp3 *.wav *.ogg *.flac"), ("Tous fichiers", "*.*")]
        )
        for file in files:
            self.main_playlist.append(file)
            self._add_main_playlist_item(file)
        
        # Marquer que la main playlist ne provient pas d'une playlist (ajout individuel)
        self.main_playlist_from_playlist = False
        
        self.status_bar.config(text=f"{len(files)} track added to main playlist")

    def _truncate_text_to_width(self, text, font, max_width):
        """Tronque le texte pour qu'il tienne dans la largeur spécifiée"""
        import tkinter.font as tkFont
        
        # Créer un objet font pour mesurer le texte
        if isinstance(font, str):
            font_obj = tkFont.Font(family=font)
        elif isinstance(font, tuple):
            font_obj = tkFont.Font(family=font[0], size=font[1] if len(font) > 1 else 10)
        else:
            font_obj = tkFont.Font()
        
        # Si le texte tient déjà, le retourner tel quel
        if font_obj.measure(text) <= max_width:
            return text
        
        # Sinon, tronquer progressivement
        ellipsis = "..."
        ellipsis_width = font_obj.measure(ellipsis)
        available_width = max_width - ellipsis_width
        
        if available_width <= 0:
            return ellipsis
        
        # Recherche dichotomique pour trouver la longueur optimale
        left, right = 0, len(text)
        result = text
        
        while left <= right:
            mid = (left + right) // 2
            test_text = text[:mid]
            
            if font_obj.measure(test_text) <= available_width:
                result = test_text + ellipsis
                left = mid + 1
            else:
                right = mid - 1
        
        return result



    def _add_main_playlist_item(self, filepath, thumbnail_path=None, song_index=None):
        """Ajoute un élément à la main playlist avec un style rectangle uniforme"""
        try:
            filename = os.path.basename(filepath)
            
            # 1. Frame principal - grand rectangle uniforme
            item_frame = tk.Frame(
                self.playlist_container,
                bg='#4a4a4a',  # Fond gris uniforme
                relief='flat',
                bd=1,
                highlightbackground='#5a5a5a',
                highlightthickness=1
            )
            item_frame.pack(fill='x', pady=2, padx=5)
            
            # Déterminer si on affiche les numéros (seulement si provient d'une playlist)
            show_numbers = self.main_playlist_from_playlist
            # Utiliser l'index fourni ou calculer l'index actuel
            if song_index is not None:
                current_song_index = song_index
            else:
                current_song_index = len(self.main_playlist) - 1  # Index de la chanson actuelle (dernière ajoutée)
            
            if show_numbers:
                # Configuration de la grille en 5 colonnes : numéro, miniature, titre, durée, bouton
                item_frame.columnconfigure(0, minsize=10, weight=0)  # Numéro
                item_frame.columnconfigure(1, minsize=80, weight=0)  # Miniature
                item_frame.columnconfigure(2, weight=1)              # Titre
                item_frame.columnconfigure(3, minsize=60, weight=0)  # Durée
                item_frame.columnconfigure(4, minsize=40, weight=0)  # Bouton
                item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
                
                # Numéro de la chanson (colonne 0)
                number_label = tk.Label(
                    item_frame,
                    text=str(current_song_index + 1),  # +1 pour commencer à 1 au lieu de 0
                    bg='#4a4a4a',
                    fg='white',
                    font=('TkDefaultFont', 10, 'bold'),
                    anchor='center'
                )
                number_label.grid(row=0, column=0, sticky='nsew', padx=(2, 2), pady=2)
                
                # Miniature (colonne 1)
                thumbnail_label = tk.Label(
                    item_frame,
                    bg='#4a4a4a',
                    width=10,
                    height=3,
                    anchor='center'
                )
                thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=8)
                thumbnail_label.grid_propagate(False)
                
                col_offset = 1  # Décalage pour les colonnes suivantes
            else:
                # Configuration de la grille en 4 colonnes : miniature, titre, durée, bouton
                item_frame.columnconfigure(0, minsize=80, weight=0)  # Miniature
                item_frame.columnconfigure(1, weight=1)              # Titre
                item_frame.columnconfigure(2, minsize=60, weight=0)  # Durée
                item_frame.columnconfigure(3, minsize=40, weight=0)  # Bouton
                item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
                
                # Miniature (colonne 0)
                thumbnail_label = tk.Label(
                    item_frame,
                    bg='#4a4a4a',
                    width=10,
                    height=3,
                    anchor='center'
                )
                thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(10, 10), pady=8)
                thumbnail_label.grid_propagate(False)
                
                col_offset = 0  # Pas de décalage
            
            # Charger la miniature
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._load_image_thumbnail(thumbnail_path, thumbnail_label)
            else:
                self._load_mp3_thumbnail(filepath, thumbnail_label)

            # Titre (colonne 1 + col_offset)
            truncated_title = self._truncate_text_for_display(filename)
            title_label = tk.Label(
                item_frame,
                text=truncated_title,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left',
                wraplength=170  # Définir la largeur maximale du texte
            )
            title_label.grid(row=0, column=1+col_offset, sticky='nsew', padx=(0, 10), pady=8)
            
            # Durée (colonne 2 + col_offset)
            duration_text = self._get_audio_duration(filepath)
            duration_label = tk.Label(
                item_frame,
                text=duration_text,
                bg='#4a4a4a',
                fg='#cccccc',
                font=('TkDefaultFont', 8),
                anchor='center'
            )
            duration_label.grid(row=0, column=2+col_offset, sticky='ns', padx=(0, 10), pady=8)

            # Bouton de suppression (colonne 3 + col_offset)
            delete_btn = tk.Button(
                item_frame,
                image=self.icons['delete'],
                bg='#3d3d3d',
                fg='white',
                activebackground='#4a4a4a',
                relief='flat',
                bd=0,
                width=self.icons['delete'].width(),  # Utiliser la largeur de l'image
                height=self.icons['delete'].height(),  # Utiliser la hauteur de l'image
                font=('TkDefaultFont', 8)
            )
            delete_btn.grid(row=0, column=3+col_offset, sticky='ns', padx=(0, 10), pady=8)
            delete_btn.bind("<Double-1>", lambda event, f=filepath, frame=item_frame: self._remove_playlist_item(f, frame, event))
            
            item_frame.filepath = filepath
            
            def on_playlist_item_click(event):
                # Vérifier si Shift est enfoncé pour la sélection multiple
                if event.state & 0x1:  # Shift est enfoncé
                    self.shift_selection_active = True
                    self.toggle_item_selection(filepath, item_frame)
                elif self.shift_selection_active and len(self.selected_items) > 0:
                    # Si on était en mode sélection et qu'on clique sans Shift, afficher le menu
                    self.show_selection_menu(event)
                else:
                    # Clic normal sans Shift - effacer la sélection si elle existe
                    if self.selected_items:
                        self.clear_selection()
            
            def on_playlist_item_double_click(event):
                # Vérifier si Shift est enfoncé - ne rien faire sur double-clic avec Shift
                if event.state & 0x1:  # Shift est enfoncé
                    pass
                else:
                    # Comportement normal : jouer la musique
                    self.current_index = self.main_playlist.index(filepath)
                    self.play_track()
                
            # Bindings pour clics simples et doubles
            item_frame.bind("<Button-1>", on_playlist_item_click)
            item_frame.bind("<Double-1>", on_playlist_item_double_click)
            thumbnail_label.bind("<Button-1>", on_playlist_item_click)
            thumbnail_label.bind("<Double-1>", on_playlist_item_double_click)
            title_label.bind("<Button-1>", on_playlist_item_click)
            title_label.bind("<Double-1>", on_playlist_item_double_click)
            duration_label.bind("<Button-1>", on_playlist_item_click)
            duration_label.bind("<Double-1>", on_playlist_item_double_click)
            
            # Ajouter le binding pour le numéro si il existe
            if show_numbers:
                number_label.bind("<Button-1>", on_playlist_item_click)
                number_label.bind("<Double-1>", on_playlist_item_double_click)

        except Exception as e:
            print(f"Erreur affichage playlist item: {e}")
    
    def select_playlist_item(self, item_frame=None, index=None):
        """Met en surbrillance l'élément sélectionné dans la playlist"""
        # Désélectionner tous les autres éléments
        for child in self.playlist_container.winfo_children():
            if hasattr(child, 'selected'):
                child.selected = False
                self._set_item_colors(child, '#4a4a4a')  # Couleur normale
        
        # Si on a fourni un index plutôt qu'un frame
        if index is not None:
            children = self.playlist_container.winfo_children()
            if 0 <= index < len(children):
                item_frame = children[index]
        
        # Sélectionner l'élément courant si fourni
        if item_frame:
            item_frame.selected = True
            self._set_item_colors(item_frame, '#5a9fd8')  # Couleur de surbrillance (bleu)
            
            # Faire défiler pour que l'élément soit visible
            self.playlist_canvas.yview_moveto(item_frame.winfo_y() / self.playlist_container.winfo_height())
    
    def _set_item_colors(self, item_frame, bg_color):
        """Change uniquement la couleur de fond des éléments d'un item de playlist"""
        def set_colors_recursive(widget, color):
            # Changer seulement la couleur de fond, pas le texte ni les boutons
            if hasattr(widget, 'config'):
                try:
                    # Ne changer que le fond, pas les autres propriétés
                    if not isinstance(widget, tk.Button):  # Exclure les boutons
                        widget.config(bg=color)
                except:
                    pass  # Certains widgets ne supportent pas bg
            
            # Appliquer récursivement aux enfants
            try:
                for child in widget.winfo_children():
                    set_colors_recursive(child, color)
            except:
                pass
        
        set_colors_recursive(item_frame, bg_color)
    
    def toggle_item_selection(self, filepath, frame):
        """Ajoute ou retire un élément de la sélection multiple"""
        if filepath in self.selected_items:
            # Désélectionner
            self.selected_items.remove(filepath)
            if filepath in self.selection_frames:
                del self.selection_frames[filepath]
            
            if filepath == self.main_playlist[self.current_index]:
                self._set_item_colors(frame, COLOR_SELECTED)
            else:
                self._set_item_colors(frame, '#4a4a4a')  # Couleur normale
        else:
            # Sélectionner
            self.selected_items.add(filepath)
            self.selection_frames[filepath] = frame
            self._set_item_colors(frame, '#ff8c00')  # Couleur orange pour la sélection multiple
    
    def clear_selection(self):
        """Efface toute la sélection multiple"""
        for filepath in list(self.selected_items):
            if filepath in self.selection_frames:
                frame = self.selection_frames[filepath]
                if filepath == self.main_playlist[self.current_index]:
                    self._set_item_colors(frame, COLOR_SELECTED)
                else:
                    self._set_item_colors(frame, '#4a4a4a')  # Couleur normale
                # self._set_item_colors(frame, '#4a4a4a')  # Couleur normale
        
        self.selected_items.clear()
        self.selection_frames.clear()
        self.shift_selection_active = False
    
    def show_selection_menu(self, event):
        """Affiche un menu contextuel pour les éléments sélectionnés"""
        if not self.selected_items:
            return
        
        # Créer le menu contextuel
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # Vérifier si on a des vidéos YouTube non téléchargées dans la sélection
        has_youtube_videos = any(item.startswith("https://www.youtube.com/watch?v=") for item in self.selected_items)
        
        if has_youtube_videos:
            # Option pour télécharger et ajouter à la main playlist
            context_menu.add_command(
                label="Télécharger et ajouter à la liste de lecture",
                command=self.download_and_add_selection_to_main_playlist
            )
            context_menu.add_separator()
        
        # Ajouter les options pour chaque playlist
        for playlist_name in self.playlists.keys():
            if playlist_name != "Main Playlist":  # Exclure la main playlist
                if has_youtube_videos:
                    context_menu.add_command(
                        label=f"Télécharger et ajouter à '{playlist_name}'",
                        command=lambda name=playlist_name: self.download_and_add_selection_to_playlist(name)
                    )
                else:
                    context_menu.add_command(
                        label=f"Ajouter à '{playlist_name}'",
                        command=lambda name=playlist_name: self.add_selection_to_playlist(name)
                    )
        
        # Séparateur
        if len(self.playlists) > 1:
            context_menu.add_separator()
        
        # Option pour créer une nouvelle playlist
        if has_youtube_videos:
            context_menu.add_command(
                label="Télécharger et créer nouvelle playlist...",
                command=self.download_and_create_playlist_from_selection
            )
        else:
            context_menu.add_command(
                label="Créer nouvelle playlist...",
                command=self.create_playlist_from_selection
            )
        
        # Séparateur
        context_menu.add_separator()
        
        # Option pour annuler la sélection
        context_menu.add_command(
            label="Annuler la sélection",
            command=self.clear_selection
        )
        
        # Afficher le menu à la position de la souris
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def add_selection_to_playlist(self, playlist_name):
        """Ajoute tous les éléments sélectionnés à une playlist"""
        if playlist_name not in self.playlists:
            return
        
        added_count = 0
        for filepath in self.selected_items:
            if filepath not in self.playlists[playlist_name]:
                self.playlists[playlist_name].append(filepath)
                added_count += 1
        
        # Sauvegarder les playlists
        self.save_playlists()
        
        # Afficher un message de confirmation
        self.status_bar.config(text=f"{added_count} musique(s) ajoutée(s) à '{playlist_name}'")
        
        # Effacer la sélection
        self.clear_selection()
    
    def create_playlist_from_selection(self):
        """Crée une nouvelle playlist avec les éléments sélectionnés"""
        if not self.selected_items:
            return
        
        # Demander le nom de la nouvelle playlist
        playlist_name = tk.simpledialog.askstring(
            "Nouvelle playlist",
            "Nom de la nouvelle playlist:",
            parent=self.root
        )
        
        if playlist_name and playlist_name.strip():
            playlist_name = playlist_name.strip()
            
            # Vérifier que le nom n'existe pas déjà
            if playlist_name in self.playlists:
                tk.messagebox.showerror("Erreur", f"Une playlist nommée '{playlist_name}' existe déjà.")
                return
            
            # Créer la nouvelle playlist avec les éléments sélectionnés
            self.playlists[playlist_name] = list(self.selected_items)
            
            # Sauvegarder les playlists
            self.save_playlists()
            
            # Afficher un message de confirmation
            self.status_bar.config(text=f"Playlist '{playlist_name}' créée avec {len(self.selected_items)} musique(s)")
            
            # Effacer la sélection
            self.clear_selection()
            
            # Rafraîchir l'affichage des playlists si on est dans l'onglet playlists
            if hasattr(self, 'current_library_tab') and self.current_library_tab == "playlists":
                self._display_playlists()
    
    def download_and_add_selection_to_main_playlist(self):
        """Télécharge les vidéos YouTube sélectionnées et les ajoute à la main playlist"""
        youtube_urls = [item for item in self.selected_items if item.startswith("https://www.youtube.com/watch?v=")]
        local_files = [item for item in self.selected_items if not item.startswith("https://www.youtube.com/watch?v=")]
        
        if not youtube_urls and not local_files:
            return
        
        # Ajouter immédiatement les fichiers locaux
        for filepath in local_files:
            if filepath not in self.main_playlist:
                self.main_playlist.append(filepath)
        
        if local_files:
            self._refresh_playlist_display()
        
        # Télécharger les vidéos YouTube
        if youtube_urls:
            self.status_bar.config(text=f"Téléchargement de {len(youtube_urls)} vidéo(s)...")
            threading.Thread(target=self._download_youtube_selection, args=(youtube_urls, "Main Playlist"), daemon=True).start()
        
        # Effacer la sélection
        self.clear_selection()
    
    def download_and_add_selection_to_playlist(self, playlist_name):
        """Télécharge les vidéos YouTube sélectionnées et les ajoute à une playlist"""
        youtube_urls = [item for item in self.selected_items if item.startswith("https://www.youtube.com/watch?v=")]
        local_files = [item for item in self.selected_items if not item.startswith("https://www.youtube.com/watch?v=")]
        
        if playlist_name not in self.playlists:
            return
        
        # Ajouter immédiatement les fichiers locaux
        added_count = 0
        for filepath in local_files:
            if filepath not in self.playlists[playlist_name]:
                self.playlists[playlist_name].append(filepath)
                added_count += 1
        
        if added_count > 0:
            self.save_playlists()
            self.status_bar.config(text=f"{added_count} fichier(s) ajouté(s) à '{playlist_name}'")
        
        # Télécharger les vidéos YouTube
        if youtube_urls:
            self.status_bar.config(text=f"Téléchargement de {len(youtube_urls)} vidéo(s) pour '{playlist_name}'...")
            threading.Thread(target=self._download_youtube_selection, args=(youtube_urls, playlist_name), daemon=True).start()
        
        # Effacer la sélection
        self.clear_selection()
    
    def download_and_create_playlist_from_selection(self):
        """Télécharge les vidéos YouTube sélectionnées et crée une nouvelle playlist"""
        if not self.selected_items:
            return
        
        # Demander le nom de la nouvelle playlist
        playlist_name = tk.simpledialog.askstring(
            "Nouvelle playlist",
            "Nom de la nouvelle playlist:",
            parent=self.root
        )
        
        if playlist_name and playlist_name.strip():
            playlist_name = playlist_name.strip()
            
            # Vérifier que le nom n'existe pas déjà
            if playlist_name in self.playlists:
                tk.messagebox.showerror("Erreur", f"Une playlist nommée '{playlist_name}' existe déjà.")
                return
            
            youtube_urls = [item for item in self.selected_items if item.startswith("https://www.youtube.com/watch?v=")]
            local_files = [item for item in self.selected_items if not item.startswith("https://www.youtube.com/watch?v=")]
            
            # Créer la nouvelle playlist avec les fichiers locaux
            self.playlists[playlist_name] = list(local_files)
            self.save_playlists()
            
            # Télécharger les vidéos YouTube
            if youtube_urls:
                self.status_bar.config(text=f"Téléchargement de {len(youtube_urls)} vidéo(s) pour la nouvelle playlist '{playlist_name}'...")
                threading.Thread(target=self._download_youtube_selection, args=(youtube_urls, playlist_name), daemon=True).start()
            else:
                self.status_bar.config(text=f"Playlist '{playlist_name}' créée avec {len(local_files)} musique(s)")
            
            # Effacer la sélection
            self.clear_selection()
            
            # Rafraîchir l'affichage des playlists si on est dans l'onglet playlists
            if hasattr(self, 'current_library_tab') and self.current_library_tab == "playlists":
                self._display_playlists()
    
    def _download_youtube_selection(self, youtube_urls, target_playlist):
        """Télécharge une liste d'URLs YouTube et les ajoute à la playlist cible"""
        downloaded_count = 0
        total_count = len(youtube_urls)
        
        for i, url in enumerate(youtube_urls):
            try:
                # Trouver la frame correspondante pour obtenir les infos de la vidéo
                video_data = None
                for filepath, frame in self.selection_frames.items():
                    if filepath == url and hasattr(frame, 'video_data'):
                        video_data = frame.video_data
                        break
                
                if not video_data:
                    continue
                
                # Mettre à jour le statut
                self.root.after(0, lambda i=i, total=total_count: self.status_bar.config(
                    text=f"Téléchargement {i+1}/{total}: {video_data.get('title', 'Sans titre')[:30]}..."
                ))
                
                # Télécharger la vidéo
                title = video_data.get('title', 'Sans titre')
                safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
                
                downloads_dir = os.path.abspath("downloads")
                if not os.path.exists(downloads_dir):
                    os.makedirs(downloads_dir)
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(downloads_dir, f'{safe_title}.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    downloaded_file = ydl.prepare_filename(info)
                    
                    final_path = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3').replace('.mp4', '.mp3')
                    if not final_path.endswith('.mp3'):
                        final_path += '.mp3'
                    
                    # Ajouter à la playlist cible
                    if target_playlist == "Main Playlist":
                        if final_path not in self.main_playlist:
                            self.main_playlist.append(final_path)
                            self.root.after(0, self._refresh_playlist_display)
                    else:
                        if target_playlist in self.playlists and final_path not in self.playlists[target_playlist]:
                            self.playlists[target_playlist].append(final_path)
                            self.root.after(0, self.save_playlists)
                    
                    downloaded_count += 1
                    
            except Exception as e:
                print(f"Erreur téléchargement {url}: {e}")
        
        # Mettre à jour le statut final
        if target_playlist == "Main Playlist":
            self.root.after(0, lambda: self.status_bar.config(
                text=f"{downloaded_count}/{total_count} vidéo(s) téléchargée(s) et ajoutée(s) à la liste de lecture"
            ))
        else:
            self.root.after(0, lambda: self.status_bar.config(
                text=f"{downloaded_count}/{total_count} vidéo(s) téléchargée(s) et ajoutée(s) à '{target_playlist}'"
            ))
        
        # Mettre à jour le nombre de fichiers téléchargés
        self.root.after(0, self._count_downloaded_files)
        self.root.after(0, self._update_downloads_button)
        
        # Rafraîchir la bibliothèque si on est dans l'onglet téléchargées
        if hasattr(self, 'current_library_tab') and self.current_library_tab == "téléchargées":
            self.root.after(0, self.load_downloaded_files)
    
    def select_library_item(self, current_filepath):
        """Met en surbrillance l'élément sélectionné dans la bibliothèque"""
        # Vérifier si on est dans l'onglet bibliothèque et si le container existe
        if (hasattr(self, 'downloads_container') and 
            self.downloads_container.winfo_exists()):
            
            # Désélectionner tous les autres éléments et sélectionner le bon
            for child in self.downloads_container.winfo_children():
                if hasattr(child, 'filepath'):
                    if child.filepath == current_filepath:
                        # Sélectionner cet élément
                        child.selected = True
                        self._set_item_colors(child, '#5a9fd8')  # Couleur de surbrillance (bleu)
                    else:
                        # Désélectionner les autres
                        child.selected = False
                        self._set_item_colors(child, '#4a4a4a')  # Couleur normale
    
    def select_playlist_content_item(self, current_filepath):
        """Met en surbrillance l'élément sélectionné dans l'affichage du contenu d'une playlist"""
        # Vérifier si on est en train de visualiser une playlist et si le container existe
        if (hasattr(self, 'playlist_content_container') and 
            self.playlist_content_container.winfo_exists() and
            hasattr(self, 'current_viewing_playlist')):
            
            # Désélectionner tous les autres éléments et sélectionner le bon
            for child in self.playlist_content_container.winfo_children():
                if hasattr(child, 'filepath'):
                    if child.filepath == current_filepath:
                        # Sélectionner cet élément
                        child.selected = True
                        self._set_item_colors(child, '#5a9fd8')  # Couleur de surbrillance (bleu)
                    else:
                        # Désélectionner les autres
                        child.selected = False
                        self._set_item_colors(child, '#4a4a4a')  # Couleur normale

    
    def _remove_playlist_item(self, filepath, frame, event=None):
        """Supprime un élément de la main playlist"""
        try:
            # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
            if event and (event.state & 0x4):  # Ctrl est enfoncé
                self._delete_from_downloads(filepath, frame)
            else:
                # Suppression normale de la playlist
                # Trouver l'index de l'élément à supprimer
                index = self.main_playlist.index(filepath)
                
                # Supprimer de la liste
                self.main_playlist.pop(index)
                
                # Supprimer de l'affichage
                frame.destroy()
                
                
                # Mettre à jour l'index courant si nécessaire
                if index < self.current_index:
                    self.current_index -= 1
                elif index == self.current_index:
                    pygame.mixer.music.stop()
                    self.current_index = min(index, len(self.main_playlist) - 1)
                    if len(self.main_playlist) > 0:
                        self.play_track()
                    else:
                        pygame.mixer.music.unload()
                        
                        # Afficher la miniature de la chanson en cours
                        self._show_current_song_thumbnail()
                
                # Si la playlist devient vide, réinitialiser le flag
                if len(self.main_playlist) == 0:
                    self.main_playlist_from_playlist = False
                
                self.status_bar.config(text=f"Piste supprimée de la main playlist")
        except ValueError:
            pass
        except Exception as e:
            self.status_bar.config(text=f"Erreur suppression: {e}")

    def _delete_from_downloads(self, filepath, frame):
        """Supprime définitivement un fichier du dossier downloads"""
        try:
            if os.path.exists(filepath):
                # Supprimer le fichier audio
                os.remove(filepath)
                
                # Supprimer la miniature associée si elle existe
                thumbnail_path = os.path.splitext(filepath)[0] + ".jpg"
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                # Supprimer de la playlist
                if filepath in self.main_playlist:
                    index = self.main_playlist.index(filepath)
                    self.main_playlist.remove(filepath)
                    
                    # Mettre à jour l'index courant si nécessaire
                    if index < self.current_index:
                        self.current_index -= 1
                    elif index == self.current_index:
                        pygame.mixer.music.stop()
                        self.current_index = min(index, len(self.main_playlist) - 1)
                        if len(self.main_playlist) > 0:
                            self.play_track()
                        else:
                            pygame.mixer.music.unload()
                            self._show_current_song_thumbnail()
                
                # Supprimer de toutes les playlists
                for playlist_name, playlist_songs in self.playlists.items():
                    if filepath in playlist_songs:
                        playlist_songs.remove(filepath)
                
                # Sauvegarder les playlists
                self.save_playlists()
                
                # Détruire l'élément de l'interface
                frame.destroy()
                
                # Mettre à jour le compteur
                self._count_downloaded_files()
                self._update_downloads_button()
                
                self.status_bar.config(text=f"Fichier supprimé définitivement: {os.path.basename(filepath)}")
                
                # Rafraîchir la bibliothèque si nécessaire
                self._refresh_downloads_library()
                
        except Exception as e:
            self.status_bar.config(text=f"Erreur suppression fichier: {str(e)}")
            print(f"Erreur suppression fichier: {e}")
    
    def _load_image_thumbnail(self, image_path, label):
        """Charge une image normale comme thumbnail"""
        try:
            img = Image.open(image_path)
            img.thumbnail((80, 45), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label.configure(image=photo)
            label.image = photo
        except Exception as e:
            print(f"Erreur chargement image thumbnail: {e}")
            # Fallback à une icône par défaut
            default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
            photo = ImageTk.PhotoImage(default_icon)
            label.configure(image=photo)
            label.image = photo

    def _load_mp3_thumbnail(self, filepath, label):
        """Charge la cover art depuis un MP3 ou une thumbnail externe"""
        try:
            # D'abord vérifier s'il existe une thumbnail externe (pour les vidéos YouTube)
            base_path = os.path.splitext(filepath)[0]
            for ext in ['.jpg', '.png', '.webp']:
                thumbnail_path = base_path + ext
                if os.path.exists(thumbnail_path):
                    self._load_image_thumbnail(thumbnail_path, label)
                    return
            
            # # Sinon, essayer de charger depuis les tags ID3
            # if filepath.lower().endswith('.mp3'):
            #     from mutagen.mp3 import MP3
            #     from mutagen.id3 import ID3
            #     audio = MP3(filepath, ID3=ID3)
            #     if 'APIC:' in audio.tags:
            #         apic = audio.tags['APIC:'].data
            #         img = Image.open(io.BytesIO(apic))
            #         img.thumbnail((80, 45), Image.Resampling.LANCZOS)
            #         photo = ImageTk.PhotoImage(img)
            #         label.configure(image=photo)
            #         label.image = photo
            #         return
            
            # Fallback à une icône par défaut
            default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
            photo = ImageTk.PhotoImage(default_icon)
            label.configure(image=photo)
            label.image = photo
            
        except Exception as e:
            print(f"Erreur chargement thumbnail MP3: {e}")
            # Fallback à une icône par défaut
            default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
            photo = ImageTk.PhotoImage(default_icon)
            label.configure(image=photo)
            label.image = photo

    def _play_playlist_item(self, filepath):
        """Joue un élément de la playlist"""
        try:
            self.current_index = self.main_playlist.index(filepath)
            self.play_track()
        except ValueError:
            pass

    def play_track(self):
        try:
            song = self.main_playlist[self.current_index]
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(start=0)
            self.base_position = 0
            
            # Charger l'offset de volume spécifique à cette musique
            self.volume_offset = self.volume_offsets.get(song, 0)
            # Mettre à jour le slider d'offset
            if hasattr(self, 'volume_offset_slider'):
                self.volume_offset_slider.set(self.volume_offset)
            
            # Appliquer le volume avec l'offset
            self._apply_volume()
            
            self.paused = False
            self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")
            
            # Mettre en surbrillance la piste courante dans la playlist
            self.select_playlist_item(index=self.current_index)
            
            # Mettre en surbrillance la piste courante dans la bibliothèque aussi
            self.select_library_item(song)
            
            # Mettre en surbrillance la piste courante dans l'affichage du contenu de playlist si on y est
            self.select_playlist_content_item(song)
            
            # Mettre à jour la miniature dans la zone de recherche si elle est vide
            if not self.current_search_query and len(self.results_container.winfo_children()) <= 1:
                # Vider d'abord la zone
                for widget in self.results_container.winfo_children():
                    widget.destroy()
                # Afficher la nouvelle miniature
                self._show_current_song_thumbnail()
            
            # Update info
            audio = MP3(song)
            self.song_length = audio.info.length
            self.progress.config(to=self.song_length)
            self.song_length_label.config(text=time.strftime(
                '%M:%S', time.gmtime(self.song_length))
            )
            
            self.song_label.config(text=os.path.basename(song))
            self.status_bar.config(text="Playing")
            
            self.generate_waveform_preview(song)

        except Exception as e:
            self.status_bar.config(text=f"Erreur: {str(e)}")

    def _on_mousewheel(self, event, canvas):
        """Gère le défilement avec la molette de souris"""
        if event.delta:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            # Pour Linux qui utilise event.num au lieu de event.delta
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
    
    # def search_youtube(self):
    #     query = self.youtube_entry.get()
    #     self.youtube_results.delete(0, tk.END)
    #     with YoutubeDL(self.ydl_opts) as ydl:
    #         try:
    #             results = ydl.extract_info(f"ytsearch2:{query}", download=False)['entries']
    #             self.search_list = results
    #             for video in results:
    #                 self.youtube_results.insert(tk.END, video.get('title'))
    #             self.status_bar.config(text=f"{len(results)} résultats trouvés")
    #         except Exception as e:
    #             self.status_bar.config(text=f"Erreur recherche: {e}")
    
    def search_youtube(self):
        if self.is_searching:
            return
        
        query = self.youtube_entry.get().strip()
        if not query:
            # Si la recherche est vide, afficher la miniature
            self._clear_results()
            self._show_current_song_thumbnail()
            return
        
        # Nouvelle recherche - réinitialiser les compteurs
        self.current_search_query = query
        self.search_results_count = 0
        self.is_loading_more = False
        self.current_search_batch = 1
        self.all_search_results = []  # Stocker tous les résultats
        
        # Effacer les résultats précédents
        self._clear_results()
        self.search_list = []
        self.status_bar.config(text="Recherche en cours...")
        self.root.update()
        
        self.is_searching = True
        
        # Lancer une recherche complète au début
        threading.Thread(target=self._perform_complete_search, args=(query,), daemon=True).start()

    def _perform_complete_search(self, query):
        """Effectue une recherche complète et stocke tous les résultats"""
        try:
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'max_downloads': 50,  # Chercher 50 résultats
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                # Recherche de 50 résultats
                results = ydl.extract_info(f"ytsearch50:{query}", download=False)
                
                if not results or 'entries' not in results:
                    self.root.after(0, lambda: self.status_bar.config(text="Aucun résultat trouvé"))
                    self.root.after(0, self._show_current_song_thumbnail)
                    return
                
                # Nettoyer le container
                self.root.after(0, self._clear_results)
                
                # Filtrer pour ne garder que les vidéos (pas les playlists/chaines)
                video_results = [
                    entry for entry in results['entries']
                    if (entry and 
                        "https://www.youtube.com/watch?v=" in entry.get('url', '') and
                        entry.get('duration', 0) <= 600.0)  # Durée max de 10 minutes
                ]
                
                # Stocker tous les résultats (maximum 30)
                self.all_search_results = video_results[:self.max_search_results]
                
                # Si aucun résultat après filtrage, afficher la miniature
                if not self.all_search_results:
                    self.root.after(0, lambda: self.status_bar.config(text="Aucun résultat trouvé"))
                    self.root.after(0, self._show_current_song_thumbnail)
                    return
                
                # Afficher les 10 premiers résultats
                self._display_batch_results(1)
                
        except Exception as e:
            self.root.after(0, lambda: self.status_bar.config(text=f"Erreur recherche: {e}"))
        finally:
            self.is_searching = False
            self.is_loading_more = False

    def _display_batch_results(self, batch_number):
        """Affiche un lot de 10 résultats"""
        start_index = (batch_number - 1) * 10
        end_index = min(start_index + 10, len(self.all_search_results))
        
        # Si c'est le premier lot, afficher le canvas de résultats
        if batch_number == 1 and end_index > start_index:
            self.root.after(0, self._show_search_results)
        
        # Afficher les résultats de ce lot
        for i in range(start_index, end_index):
            if i < len(self.all_search_results):
                video = self.all_search_results[i]
                self.root.after(0, lambda v=video, idx=i: self._add_search_result(v, idx))
                self.search_results_count += 1
        
        # Mettre à jour le statut
        self.root.after(0, lambda: self.status_bar.config(
            text=f"{self.search_results_count}/{len(self.all_search_results)} résultats affichés (lot {batch_number})"
        ))




    
    def _load_more_search_results(self):
        """Charge plus de résultats pour la recherche actuelle"""
        print(f"_load_more_search_results appelée - Lot actuel: {self.current_search_batch}, Résultats: {self.search_results_count}/{len(self.all_search_results)}")
        
        if (self.is_loading_more or 
            self.is_searching or
            not self.current_search_query or 
            self.search_results_count >= len(self.all_search_results) or
            self.current_search_batch >= self.max_search_batchs):
            print("Conditions non remplies pour charger plus")
            return
        
        self.is_loading_more = True
        self.current_search_batch += 1
        
        self.status_bar.config(text=f"Chargement du lot {self.current_search_batch}...")
        
        # Afficher le prochain lot depuis les résultats déjà stockés
        self._display_batch_results(self.current_search_batch)
        
        self.is_loading_more = False

    def _clear_results(self):
        """Vide le container de résultats et gère l'affichage des frames"""
        for widget in self.results_container.winfo_children():
            widget.destroy()
        self.youtube_canvas.yview_moveto(0)  # Remet le scroll en haut
        
        # Masquer le canvas et scrollbar, afficher la frame thumbnail
        self.youtube_canvas.pack_forget()
        self.scrollbar.pack_forget()
        self.thumbnail_frame.pack(fill=tk.BOTH, expand=True)
    
    def _show_search_results(self):
        """Affiche le canvas de résultats et masque la frame thumbnail"""
        self.thumbnail_frame.pack_forget()
        self.scrollbar.pack(side="right", fill="y")
        self.youtube_canvas.pack(side="left", fill="both", expand=True)

    # def _add_search_result(self, video, index):
    #     """Ajoute un résultat à la liste et scroll si nécessaire"""
    #     title = video.get('title', 'Sans titre')
    #     self.youtube_results.insert(tk.END, title)
        
    #     # Faire défiler vers le bas si c'est un des derniers résultats
    #     if index >= 5:
    #         self.youtube_results.see(tk.END)
    
    def _add_search_result(self, video, index):
        """Ajoute un résultat avec un style rectangle uniforme"""
        try:
            title = video.get('title', 'Sans titre')
            duration = video.get('duration', 0)
            
            # Frame principal - grand rectangle uniforme
            result_frame = tk.Frame(
                self.results_container,
                bg='#4a4a4a',  # Fond gris uniforme
                relief='flat',
                bd=1,
                highlightbackground='#5a5a5a',
                highlightthickness=1
            )
            video['search_frame'] = result_frame
            result_frame.pack(fill="x", padx=5, pady=2)
            
            # Stocker l'URL dans le frame pour détecter les doublons
            result_frame.video_url = video.get('url', '')
            
            # Configuration de la grille en 3 colonnes : miniature, titre, durée
            result_frame.columnconfigure(0, minsize=80, weight=0)  # Miniature
            result_frame.columnconfigure(1, weight=1)              # Titre
            result_frame.columnconfigure(2, minsize=60, weight=0)  # Durée
            result_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
            
            # 1. Miniature (colonne 0)
            thumbnail_label = tk.Label(
                result_frame,
                bg='#4a4a4a',
                width=10,
                height=3,
                anchor='center'
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(10, 10), pady=8)
            # Forcer la taille fixe
            thumbnail_label.grid_propagate(False)
            
            # 2. Titre (colonne 1)
            title_label = tk.Label(
                result_frame,
                text=title,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left'
            )
            title_label.grid(row=0, column=1, sticky='nsew', padx=(0, 10), pady=8)
            
            # 3. Durée (colonne 2)
            duration_label = tk.Label(
                result_frame,
                text=time.strftime('%M:%S', time.gmtime(duration)),
                bg='#4a4a4a',
                fg='#cccccc',
                font=('TkDefaultFont', 8),
                anchor='center'
            )
            duration_label.grid(row=0, column=2, sticky='ns', padx=(0, 10), pady=8)
            
            # Stocker la référence à la vidéo
            result_frame.video_data = video
            result_frame.title_label = title_label
            result_frame.duration_label = duration_label
            result_frame.thumbnail_label = thumbnail_label
            
            # Événements de clic pour la sélection multiple
            def on_result_click(event, frame=result_frame):
                # Vérifier si Shift est enfoncé pour la sélection multiple
                if event.state & 0x1:  # Shift est enfoncé
                    self.shift_selection_active = True
                    # Utiliser l'URL comme identifiant unique pour les résultats YouTube
                    video_url = frame.video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={frame.video_data.get('id')}"
                    self.toggle_item_selection(video_url, frame)
                elif self.shift_selection_active and len(self.selected_items) > 0:
                    # Si on était en mode sélection et qu'on clique sans Shift, afficher le menu
                    self.show_selection_menu(event)
                else:
                    # Clic normal sans Shift - effacer la sélection si elle existe
                    if self.selected_items:
                        self.clear_selection()
            
            def on_result_double_click(event, frame=result_frame):
                # Vérifier si Shift est enfoncé - ne rien faire sur double-clic avec Shift
                if event.state & 0x1:  # Shift est enfoncé
                    pass
                else:
                    # Comportement normal : télécharger
                    self._on_result_click(frame)
            
            # Bindings pour les clics simples et doubles
            duration_label.bind("<Button-1>", on_result_click)
            duration_label.bind("<Double-1>", on_result_double_click)
            title_label.bind("<Button-1>", on_result_click)
            title_label.bind("<Double-1>", on_result_double_click)
            thumbnail_label.bind("<Button-1>", on_result_click)
            thumbnail_label.bind("<Double-1>", on_result_double_click)
            result_frame.bind("<Button-1>", on_result_click)
            result_frame.bind("<Double-1>", on_result_double_click)
            
            # Événements de clic droit pour ajouter après la chanson en cours
            duration_label.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            title_label.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            thumbnail_label.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            result_frame.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            
            # Charger la miniature en arrière-plan
            if video.get('thumbnails'):
                threading.Thread(
                    target=self._load_thumbnail,
                    args=(thumbnail_label, video['thumbnails'][1]['url']) if len(video['thumbnails']) > 1 else (thumbnail_label, video['thumbnails'][0]['url']),
                    daemon=True
                ).start()
                
        except Exception as e:
            print(f"Erreur affichage résultat: {e}")
    
    def _on_result_click(self, frame):
        """Gère le clic sur un résultat"""
        if hasattr(frame, 'video_data'):
            video = frame.video_data
            
            # Vérifier si déjà en cours de téléchargement
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            if url in self.current_downloads:
                self.status_bar.config(text="Téléchargement déjà en cours...")
                return
            
            # Changer l'apparence pour indiquer le téléchargement
            frame.config(bg='#ff6666')  # Rouge pour téléchargement
            frame.title_label.config(bg='#ff6666', fg='#cccccc')
            frame.duration_label.config(bg='#ff6666', fg='#aaaaaa')
            frame.thumbnail_label.config(bg='#ff6666')
            
            self.search_list = [frame.video_data]  # Pour la compatibilité avec download_selected_youtube
            frame.video_data['search_frame'] = frame
            try:
                self.download_selected_youtube(None)
            except Exception as e:
                # En cas d'erreur, remettre l'apparence normale
                frame.config(bg='#ffcc00')  # Jaune pour erreur
                frame.title_label.config(bg='#ffcc00', fg='#333333')
                frame.duration_label.config(bg='#ffcc00', fg='#666666')
                frame.thumbnail_label.config(bg='#ffcc00')
    
    def _on_result_right_click(self, frame):
        """Gère le clic droit sur un résultat pour l'ajouter après la chanson en cours"""
        if hasattr(frame, 'video_data'):
            video = frame.video_data
            
            # Vérifier si déjà en cours de téléchargement
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            if url in self.current_downloads:
                self.status_bar.config(text="Téléchargement déjà en cours...")
                return
            
            # Changer l'apparence pour indiquer le téléchargement
            frame.config(bg='#ff6666')  # Rouge pour téléchargement
            frame.title_label.config(bg='#ff6666', fg='#cccccc')
            frame.duration_label.config(bg='#ff6666', fg='#aaaaaa')
            frame.thumbnail_label.config(bg='#ff6666')
            
            # Télécharger et ajouter après la chanson en cours
            self._download_and_add_after_current(video, frame)
    
    def _download_and_add_after_current(self, video, frame):
        """Télécharge une vidéo et l'ajoute après la chanson en cours"""
        def download_thread():
            try:
                url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
                self.current_downloads.add(url)
                
                # Télécharger la vidéo
                with YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    # Trouver le fichier téléchargé
                    filename = ydl.prepare_filename(info)
                    # Remplacer l'extension par .mp3
                    audio_filename = os.path.splitext(filename)[0] + '.mp3'
                    
                    if os.path.exists(audio_filename):
                        # Ajouter à la main playlist après la chanson en cours
                        insert_position = self.current_index + 1
                        self.main_playlist.insert(insert_position, audio_filename)
                        
                        # Mettre à jour l'affichage de la main playlist
                        self.root.after(0, lambda: self._refresh_playlist_display())
                        
                        # Télécharger la thumbnail
                        self._download_youtube_thumbnail(info, audio_filename)
                        
                        # Changer l'apparence pour indiquer le succès
                        self.root.after(0, lambda: self._set_download_success_appearance(frame))
                        
                        self.root.after(0, lambda: self.status_bar.config(
                            text=f"Ajouté après la chanson en cours: {os.path.basename(audio_filename)}"
                        ))
                    else:
                        raise Exception("Fichier audio non trouvé après téléchargement")
                        
            except Exception as e:
                print(f"Erreur téléchargement: {e}")
                # En cas d'erreur, changer l'apparence
                self.root.after(0, lambda: self._set_download_error_appearance(frame))
                self.root.after(0, lambda: self.status_bar.config(text=f"Erreur téléchargement: {str(e)}"))
            finally:
                self.current_downloads.discard(url)
        
        # Lancer le téléchargement dans un thread séparé
        threading.Thread(target=download_thread, daemon=True).start()
    
    def _refresh_playlist_display(self):
        """Rafraîchit l'affichage de la main playlist"""
        # Vider le container actuel
        for widget in self.playlist_container.winfo_children():
            widget.destroy()
        
        # Recréer tous les éléments avec les bons index
        for i, filepath in enumerate(self.main_playlist):
            self._add_main_playlist_item(filepath, song_index=i)
        
        # Remettre en surbrillance la chanson en cours si elle existe
        if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
            self.select_playlist_item(index=self.current_index)
    
    def _set_download_success_appearance(self, frame):
        """Change l'apparence du frame pour indiquer un téléchargement réussi"""
        frame.config(bg='#4a8fe7')  # Bleu pour succès
        frame.title_label.config(bg='#4a8fe7', fg='white')
        frame.duration_label.config(bg='#4a8fe7', fg='#cccccc')
        frame.thumbnail_label.config(bg='#4a8fe7')
    
    def _set_download_error_appearance(self, frame):
        """Change l'apparence du frame pour indiquer une erreur de téléchargement"""
        frame.config(bg='#ffcc00')  # Jaune pour erreur
        frame.title_label.config(bg='#ffcc00', fg='#333333')
        frame.duration_label.config(bg='#ffcc00', fg='#666666')
        frame.thumbnail_label.config(bg='#ffcc00')
    
    def _download_youtube_thumbnail(self, video_info, filepath):
        """Télécharge la thumbnail YouTube et l'associe au fichier audio"""
        try:
            if not video_info.get('thumbnails'):
                return
                
            # Prendre la meilleure qualité disponible
            thumbnail_url = video_info['thumbnails'][-1]['url']
            
            import requests
            from io import BytesIO
            
            response = requests.get(thumbnail_url, timeout=5)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            
            # Sauvegarder la thumbnail dans le même dossier que l'audio
            thumbnail_path = os.path.splitext(filepath)[0] + ".jpg"
            img.save(thumbnail_path)
            
            return thumbnail_path
            
        except Exception as e:
            print(f"Erreur téléchargement thumbnail: {e}")
            return None


    def download_selected_youtube(self, event=None):
        if not self.search_list:
            return
        
        video = self.search_list[0]
        url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
        
        # Vérifier si cette URL est déjà en cours de téléchargement
        if url in self.current_downloads:
            self.status_bar.config(text="Ce téléchargement est déjà en cours")
            return
        
        # Créer un thread pour le téléchargement
        download_thread = threading.Thread(
            target=self._download_youtube_thread,
            args=(url,),  # Passer l'URL en argument
            daemon=True
        )
        download_thread.start()

    def _download_youtube_thread(self, url):
        try:
            video = self.search_list[0]
            title = video['title']
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            
            # Ajouter l'URL aux téléchargements en cours
            self.current_downloads.add(url)
            # print(self.current_downloads, "current _download_youtube_thread")
            self._update_search_results_ui()
            

            # Vérifier si le fichier existe déjà
            existing_file = self._get_existing_download(title)
            if existing_file:
                # Trouver la thumbnail correspondante
                base_path = os.path.splitext(existing_file)[0]
                thumbnail_path = None
                for ext in ['.jpg', '.png', '.webp']:
                    possible_thumb = base_path + ext
                    if os.path.exists(possible_thumb):
                        thumbnail_path = possible_thumb
                        break
                
                self.root.after(0, lambda: self._add_downloaded_file(existing_file, thumbnail_path, title))
                self.root.after(0, lambda: self.status_bar.config(text=f"Fichier existant trouvé: {title}"))
                # Mettre à jour la bibliothèque même pour les fichiers existants
                self.root.after(0, lambda: self._refresh_downloads_library())
                # Remettre l'apparence normale
                video['search_frame'].config(bg='#4a4a4a')
                video['search_frame'].title_label.config(bg='#4a4a4a', fg='white')
                video['search_frame'].duration_label.config(bg='#4a4a4a', fg='#cccccc')
                video['search_frame'].thumbnail_label.config(bg='#4a4a4a')
                self.current_downloads.remove(url)  # Retirer de la liste quand terminé
                self._update_search_results_ui()
                return
                
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
            
            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, lambda: self.status_bar.config(text=f"Téléchargement de {safe_title}..."))
            
            downloads_dir = os.path.abspath("downloads")
            if not os.path.exists(downloads_dir):
                try:
                    os.makedirs(downloads_dir)
                except Exception as e:
                    self.root.after(0, lambda: self.status_bar.config(text=f"Erreur création dossier: {str(e)}"))
                    return

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(downloads_dir, f'{safe_title}.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'writethumbnail': True,
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._download_progress_hook],
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                print("downloaded_file", downloaded_file)
                final_path = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3').replace('.mp4', '.mp3')
                if not final_path.endswith('.mp3'):
                    final_path += '.mp3'
                
                thumbnail_path = os.path.splitext(final_path)[0] + ".jpg"
                if os.path.exists(downloaded_file + ".jpg"):
                    os.rename(downloaded_file + ".jpg", thumbnail_path)
                
                # Mettre à jour l'interface dans le thread principal
                self.root.after(0, lambda: self._add_downloaded_file(final_path, thumbnail_path, safe_title))
                # Remettre l'apparence normale
                video['search_frame'].config(bg='#4a4a4a')
                video['search_frame'].title_label.config(bg='#4a4a4a', fg='white')
                video['search_frame'].duration_label.config(bg='#4a4a4a', fg='#cccccc')
                video['search_frame'].thumbnail_label.config(bg='#4a4a4a')
        
        except Exception as e:
            self.root.after(0, lambda e=e: self.status_bar.config(text=f"Erreur: {str(e)}"))
            if 'search_frame' in video:
                # Apparence d'erreur (jaune)
                video['search_frame'].config(bg='#ffcc00')
                video['search_frame'].title_label.config(bg='#ffcc00', fg='#333333')
                video['search_frame'].duration_label.config(bg='#ffcc00', fg='#666666')
                video['search_frame'].thumbnail_label.config(bg='#ffcc00')
        finally:
            # S'assurer que l'URL est retirée même en cas d'erreur
            if url in self.current_downloads:
                self.current_downloads.remove(url)
                self._update_search_results_ui()
                

    def _download_progress_hook(self, d):
        """Hook pour afficher la progression du téléchargement"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '?')
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Téléchargement... {percent} à {speed}"
            ))

    def _add_downloaded_file(self, filepath, thumbnail_path, title):
        """Ajoute le fichier téléchargé à la main playlist (à appeler dans le thread principal)"""
        # Vérifier si le fichier est déjà dans la main playlist
        if filepath not in self.main_playlist:
            self.main_playlist.append(filepath)
            self._add_main_playlist_item(filepath, thumbnail_path)
            self.status_bar.config(text=f"{title} ajouté à la main playlist")
            
            # Marquer que la main playlist ne provient pas d'une playlist (ajout individuel)
            self.main_playlist_from_playlist = False
        else:
            self.status_bar.config(text=f"{title} est déjà dans la main playlist")
        
        # Mettre à jour le compteur de fichiers téléchargés
        self._count_downloaded_files()
        self._update_downloads_button()
        
        # Mettre à jour la liste des téléchargements dans l'onglet bibliothèque
        self._refresh_downloads_library()
    
    def _refresh_downloads_library(self):
        """Met à jour la liste des téléchargements dans l'onglet bibliothèque si il est actif"""
        try:
            # Vérifier si on est dans l'onglet bibliothèque et sous-onglet téléchargées
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if current_tab == "Bibliothèque" and hasattr(self, 'current_library_tab') and self.current_library_tab == "téléchargées":
                # Vérifier si les widgets de téléchargement existent
                if hasattr(self, 'downloads_container') and hasattr(self, 'all_downloaded_files'):
                    # Recharger la liste des fichiers téléchargés
                    downloads_dir = "downloads"
                    if os.path.exists(downloads_dir):
                        # Extensions audio supportées
                        audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
                        
                        # Sauvegarder l'ancien état pour comparaison
                        old_files = set(self.all_downloaded_files)
                        
                        # Recharger la liste
                        self.all_downloaded_files = []
                        self.normalized_filenames = {}
                        
                        for filename in os.listdir(downloads_dir):
                            if filename.lower().endswith(audio_extensions):
                                filepath = os.path.join(downloads_dir, filename)
                                self.all_downloaded_files.append(filepath)
                                # Mettre à jour le cache
                                normalized_name = os.path.basename(filepath).lower()
                                self.normalized_filenames[filepath] = normalized_name
                        
                        # Mettre à jour le compteur de fichiers téléchargés
                        self.num_downloaded_files = len(self.all_downloaded_files)
                        
                        # Mettre à jour le texte du bouton
                        self._update_downloads_button()
                        
                        # Vérifier s'il y a de nouveaux fichiers
                        new_files = set(self.all_downloaded_files)
                        if new_files != old_files:
                            # Appliquer le filtre de recherche actuel si il y en a un
                            if hasattr(self, 'library_search_entry') and self.library_search_entry.get().strip():
                                # Relancer la recherche avec le terme actuel
                                self._perform_library_search()
                            else:
                                # Afficher tous les fichiers
                                self._display_filtered_downloads(self.all_downloaded_files)
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la bibliothèque: {e}")

    def _load_thumbnail(self, label, url):
        """Charge et affiche la miniature"""
        try:
            import requests
            from io import BytesIO
            
            response = requests.get(url, timeout=5)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img.thumbnail((80, 45), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.root.after(0, lambda: self._display_thumbnail(label, photo))
        except Exception as e:
            print(f"Erreur chargement thumbnail: {e}")

    def _display_thumbnail(self, label, photo):
        """Affiche la miniature dans le label"""
        label.configure(image=photo)
        label.image = photo  # Garder une référence
    
    
    def _get_existing_download(self, title):
        """Vérifie si un fichier existe déjà dans downloads avec un titre similaire"""
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
        downloads_dir = os.path.abspath("downloads")
        
        if not os.path.exists(downloads_dir):
            return None
        
        # Chercher les fichiers correspondants
        for filename in os.listdir(downloads_dir):
            # Comparer les noms normalisés (sans extension et caractères spéciaux)
            base_name = os.path.splitext(filename)[0]
            normalized_base = "".join(c for c in base_name if c.isalnum() or c in " -_")
            
            if normalized_base.startswith(safe_title[:20]) or safe_title.startswith(normalized_base[:20]):
                filepath = os.path.join(downloads_dir, filename)
                # Vérifier que c'est bien un fichier audio
                if filepath.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                    return filepath
        return None

    def _update_search_results_ui(self):
        """Met à jour l'apparence des résultats en fonction de l'état de téléchargement"""
        for child in self.results_container.winfo_children():
            if hasattr(child, 'video_data'):
                video = child.video_data
                url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
                
                if url in self.current_downloads:
                    # Apparence de téléchargement (rouge)
                    child.config(bg='#ff6666')
                    child.title_label.config(bg='#ff6666', fg='#cccccc')
                    child.duration_label.config(bg='#ff6666', fg='#aaaaaa')
                    child.thumbnail_label.config(bg='#ff6666')
                else:
                    # Apparence normale
                    child.config(bg='#4a4a4a')
                    child.title_label.config(bg='#4a4a4a', fg='white')
                    child.duration_label.config(bg='#4a4a4a', fg='#cccccc')
                    child.thumbnail_label.config(bg='#4a4a4a')

    def generate_waveform_preview(self, filepath):
        """Génère les données audio brutes pour la waveform (sans sous-échantillonnage)"""
        try:
            audio = AudioSegment.from_file(filepath)
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)

            # Stocker les données brutes normalisées (sans sous-échantillonnage)
            self.waveform_data_raw = samples / max(abs(samples).max(), 1)
            self.waveform_data = None  # Sera calculé dynamiquement
        except Exception as e:
            self.status_bar.config(text=f"Erreur waveform preview: {e}")
            self.waveform_data_raw = None
            self.waveform_data = None
    
    def get_adaptive_waveform_data(self, canvas_width=None):
        """Génère des données waveform adaptées à la durée de la musique"""
        if self.waveform_data_raw is None:
            return None
            
        # Calculer la résolution basée sur la durée de la musique
        # Plus la musique est longue, plus on a besoin de résolution pour voir les détails
        if self.song_length > 0:
            # 100 échantillons par seconde de musique (résolution fixe)
            target_resolution = int(self.song_length * 100)
            # Limiter entre 1000 et 20000 échantillons pour des performances raisonnables
            target_resolution = max(20000, min(1000, target_resolution))
        else:
            target_resolution = 1000  # Valeur par défaut
        
        # Sous-échantillonner les données brutes
        if len(self.waveform_data_raw) > target_resolution:
            step = len(self.waveform_data_raw) // target_resolution
            return self.waveform_data_raw[::step]
        else:
            return self.waveform_data_raw
    
    def play_pause(self):
        if not self.main_playlist:
            return
            
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_button.config(image=self.icons["play"])
            self.play_button.config(text="Play")
        elif self.paused:
            # pygame.mixer.music.unpause()
            pygame.mixer.music.play(start=self.current_time)
            self.base_position = self.current_time
            self.paused = False
            self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")

        else:
            self.paused = False
            self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")
            self.play_track()
    
    # def play_track(self):
    #     try:
    #         song = self.main_playlist[self.current_index]
    #         pygame.mixer.music.load(song)
    #         pygame.mixer.music.play(start=0)
    #         self.base_position = 0
    #         pygame.mixer.music.set_volume(self.volume)
            
    #         # Update info
    #         audio = MP3(song)
    #         self.song_length = audio.info.length
    #         self.progress.config(to=self.song_length)
    #         self.song_length_label.config(text=time.strftime(
    #             '%M:%S', time.gmtime(self.song_length)
    #         )
    #         )
            
    #         self.song_label.config(text=os.path.basename(song))
    #         self.play_button.config(text="Pause")
    #         self.paused = False
    #         self.status_bar.config(text="Playing")
            
    #         # Highlight current track
    #         self.playlist_box.selection_clear(0, tk.END)
    #         self.playlist_box.selection_set(self.current_index)
    #         self.playlist_box.activate(self.current_index)
            
    #         self.generate_waveform_preview(song)

    #     except Exception as e:
    #         self.status_bar.config(text=f"Erreur: {str(e)}")


    def play_selected(self, event):
        if self.playlist_box.curselection():
            self.current_index = self.playlist_box.curselection()[0]
            self.play_track()
    
    def prev_track(self):
        if not self.main_playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.main_playlist)
        self.play_track()

    def next_track(self):
        if not self.main_playlist:
            return
        
        # Mode loop chanson : rejouer la même chanson
        if self.loop_mode == 2:
            self.play_track()
            return
        
        # Si on est à la dernière chanson et que le mode loop playlist n'est pas activé
        if self.current_index >= len(self.main_playlist) - 1 and self.loop_mode != 1:
            # Arrêter la lecture
            pygame.mixer.music.stop()
            self.status_bar.config(text="Fin de la playlist")
            return
        
        # Passer à la chanson suivante (avec boucle playlist si mode loop playlist activé)
        self.current_index = (self.current_index + 1) % len(self.main_playlist)
        self.play_track()
    
    
    def show_waveform_on_clicked(self):
        self.show_waveform_current = not self.show_waveform_current

        if self.show_waveform_current:
            self.waveform_canvas.config(height=80)
            self.waveform_canvas.pack(fill=tk.X, pady=(0, 10))
            self.draw_waveform_around(self.current_time)
            self.show_waveform_btn.config(bg="#4a8fe7", activebackground="#4a8fe7")
        else:
            self.waveform_canvas.delete("all")
            self.waveform_canvas.config(height=0)
            self.waveform_canvas.pack(fill=tk.X, pady=0)
            self.show_waveform_btn.config(bg="#3d3d3d", activebackground="#4a4a4a")

    def draw_waveform_around(self, time_sec, window_sec=5):
        if self.waveform_data_raw is None:
            return

        total_length = self.song_length
        if total_length == 0:
            return

        # Générer les données adaptées à la durée de la musique (résolution fixe)
        adaptive_data = self.get_adaptive_waveform_data()
        if adaptive_data is None:
            return

        center_index = int((time_sec / total_length) * len(adaptive_data))
        half_window = int((window_sec / total_length) * len(adaptive_data)) // 2

        start = max(0, center_index - half_window)
        end = min(len(adaptive_data), center_index + half_window)

        display_data = adaptive_data[start:end]
        self.waveform_canvas.delete("all")
        width = self.waveform_canvas.winfo_width()
        height = self.waveform_canvas.winfo_height()
        
        # Si le canvas n'a pas encore de largeur valide, on attend
        if width <= 1:
            self.waveform_canvas.update_idletasks()
            width = self.waveform_canvas.winfo_width()
        
        # Si toujours pas de largeur valide, on utilise une valeur par défaut
        if width <= 1:
            width = 600  # largeur par défaut
            
        mid = height // 2
        scale = height // 2

        step = width / len(display_data) if len(display_data) > 0 else 1
        
        ## version segments verticaux
        for i, val in enumerate(display_data):
            x = i * step
            y = val * scale
            self.waveform_canvas.create_line(x, mid - y, x, mid + y, fill="#66ccff")
        
        ## version interpolation linéaire
        # points = []
        # for i, val in enumerate(display_data):
        #     x = i * step
        #     y = mid - val * scale
        #     points.append((x, y))

        # for i in range(1, len(points)):
        #     x1, y1 = points[i - 1]
        #     x2, y2 = points[i]
        #     self.waveform_canvas.create_line(x1, y1, x2, y2, fill="#66ccff", width=1)


        # Calculer la position exacte du trait rouge dans la fenêtre
        # time_sec est la position actuelle, on calcule sa position relative dans la fenêtre affichée
        if total_length > 0:
            # Position relative de time_sec dans la fenêtre affichée
            window_start_time = (start / len(adaptive_data)) * total_length
            window_end_time = (end / len(adaptive_data)) * total_length
            window_duration = window_end_time - window_start_time
            
            if window_duration > 0:
                relative_pos = (time_sec - window_start_time) / window_duration
                red_line_x = relative_pos * width
                # S'assurer que la ligne reste dans les limites du canvas
                red_line_x = max(0, min(width, red_line_x))
            else:
                red_line_x = width // 2
        else:
            red_line_x = width // 2
        
        
        
        self.waveform_canvas.create_line(
            red_line_x, 0, red_line_x, height, fill="#ff4444", width=2
        )

    
    
        
    
    def set_volume(self, val):
        # print(f"Setting volume to {val}")
        self.volume = float(val) / 100
        self._apply_volume()
        # Sauvegarder le volume global seulement si on n'est pas en cours d'initialisation
        if not self.initializing:
            self.save_config()
    
    def set_volume_offset(self, val):
        self.volume_offset = float(val)
        self._apply_volume()
        
        # Sauvegarder l'offset pour la musique en cours seulement si on n'est pas en cours d'initialisation
        if not self.initializing and self.main_playlist and self.current_index < len(self.main_playlist):
            current_file = self.main_playlist[self.current_index]
            self.volume_offsets[current_file] = self.volume_offset
            self.save_config()
    
    def _apply_volume(self):
        """Applique le volume avec l'offset"""
        # Calculer le volume final avec l'offset
        final_volume = self.volume + (self.volume_offset / 100)
        # S'assurer que le volume reste entre 0 et 1
        final_volume = max(0, min(1, final_volume))
        pygame.mixer.music.set_volume(final_volume)
    
    def _reset_volume_offset(self, event):
        """Remet l'offset de volume à 0 (clic droit)"""
        self.volume_offset_slider.set(0)
        # set_volume_offset sera appelé automatiquement par le slider
    
    def on_progress_press(self, event):
        if not self.main_playlist:
            return
        self.user_dragging = True
        self.drag_start_time = self.current_time
        # Remember if waveform was already visible before clicking/dragging
        self.waveform_was_visible = self.show_waveform_current
        # Show waveform for any interaction with progress bar (click or drag)
        if not self.show_waveform_current:
            self.show_waveform_current = True
            self.waveform_canvas.config(height=80)
            self.waveform_canvas.pack(fill=tk.X, pady=(0, 10))
            # Force canvas update before drawing
            self.waveform_canvas.update_idletasks()
            # Draw waveform at current position for immediate feedback
            pos = self.progress.get()
            self.draw_waveform_around(pos)
    
    def on_progress_drag(self, event):
        if not self.main_playlist:
            return
        if self.user_dragging:
            pos = self.progress.get()  # En secondes
            self.current_time_label.config(
                text=time.strftime('%M:%S', time.gmtime(pos))
            )
            self.draw_waveform_around(pos)

    def on_progress_release(self, event):
        if not self.main_playlist:
            return
        # Récupère la valeur actuelle de la progress bar
        pos = self.progress.get()
        # Change la position de la musique (en secondes)
        try:
            if not self.paused:
                pygame.mixer.music.play(start=pos)
            pygame.mixer.music.set_volume(self.volume)
            self.current_time = pos
            self.base_position = pos  # Important : mettre à jour la position de base
            
            # Hide waveform if it wasn't visible before dragging
            if not self.waveform_was_visible:
                self.show_waveform_current = False
                # Don't delete the waveform content, just hide the canvas
                self.waveform_canvas.config(height=0)
                self.waveform_canvas.pack(fill=tk.X, pady=0)
            else:
                # Keep waveform visible and update it
                self.draw_waveform_around(self.current_time)
                
            self.user_dragging = False
            # self.base_position = pos
        except Exception as e:
            self.status_bar.config(text=f"Erreur position: {e}")
    
    def on_waveform_canvas_resize(self, event):
        """Appelé quand le canvas waveform change de taille (désactivé car fenêtre non redimensionnable)"""
        # Fonction désactivée car la fenêtre n'est plus redimensionnable
        # et la résolution de la waveform ne dépend plus de la taille du canvas
        pass
        
        
    
    # def set_position(self, val):
    #     return
    #     if pygame.mixer.music.get_busy() and not self.paused:
    #         pygame.mixer.music.set_pos(float(val))
    #         self.current_time = float(val)
    
    def set_position(self, val):
        pos = float(val)
        self.base_position = pos
        if self.user_dragging:
            return
        try:
            pygame.mixer.music.play(start=pos)
            self.play_button.config(image=self.icons["pause"], text="Pause")
        except Exception as e:
            self.status_bar.config(text=f"Erreur set_pos: {e}")
        
            
    
    def update_time(self):
        while True:
            if pygame.mixer.music.get_busy() and not self.paused and not self.user_dragging:
                self.current_time = self.base_position + pygame.mixer.music.get_pos() / 1000
                
                if self.current_time > self.song_length:
                    self.current_time = self.song_length
                    self.next_track()
                # pygame retourne -1 si la musique est finie, donc on filtre
                if self.current_time < 0:
                    self.current_time = 0
                self.progress.config(value=self.current_time)
                self.current_time_label.config(
                    text=time.strftime('%M:%S', time.gmtime(self.current_time))
                )
                
                if self.show_waveform_current:
                    self.draw_waveform_around(self.current_time)
                else:
                    self.waveform_canvas.delete("all")
            self.root.update()
            time.sleep(0.01)
            # print(self.current_time)
    
    def on_closing(self):
        # Sauvegarder la configuration avant de fermer
        self.save_config()
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.root.destroy()

    def toggle_random_mode(self):
        """Active/désactive le mode aléatoire"""
        self.random_mode = not self.random_mode
        
        # Mettre à jour l'apparence du bouton
        if self.random_mode:
            self.random_button.config(bg="#4a8fe7")
            self.status_bar.config(text="Mode aléatoire activé")
            # Mélanger la suite de la playlist à partir de la chanson suivante
            self._shuffle_remaining_playlist()
        else:
            self.random_button.config(bg="#3d3d3d")
            self.status_bar.config(text="Mode aléatoire désactivé")

    def toggle_loop_mode(self):
        """Cycle entre les 3 modes de boucle : désactivé -> loop playlist -> loop chanson -> désactivé"""
        self.loop_mode = (self.loop_mode + 1) % 3
        
        # Mettre à jour l'apparence du bouton selon le mode
        if self.loop_mode == 0:
            # Désactivé
            self.loop_button.config(bg="#3d3d3d", image=self.icons["loop"])
            self.status_bar.config(text="Mode boucle désactivé")
        elif self.loop_mode == 1:
            # Loop playlist
            self.loop_button.config(bg="#4a8fe7", image=self.icons["loop"])
            self.status_bar.config(text="Mode boucle playlist activé")
        elif self.loop_mode == 2:
            # Loop chanson actuelle
            self.loop_button.config(bg="#4a8fe7", image=self.icons["loop1"])
            self.status_bar.config(text="Mode boucle chanson activé")

    def _shuffle_remaining_playlist(self):
        """Mélange aléatoirement la suite de la playlist à partir de la chanson suivante"""
        if len(self.main_playlist) <= self.current_index + 1:
            return  # Pas de chansons suivantes à mélanger
        
        import random
        
        # Sauvegarder la partie avant la chanson courante (incluse)
        before_current = self.main_playlist[:self.current_index + 1]
        
        # Récupérer la partie après la chanson courante
        after_current = self.main_playlist[self.current_index + 1:]
        
        # Mélanger la partie après la chanson courante
        random.shuffle(after_current)
        
        # Reconstituer la playlist
        self.main_playlist = before_current + after_current
        
        # Rafraîchir l'affichage de la playlist
        self._refresh_playlist_display()
        
        self.status_bar.config(text=f"Suite de la playlist mélangée ({len(after_current)} titres)")

if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.on_closing)
    root.mainloop()
