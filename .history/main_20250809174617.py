import pygame
import os
import tkinter as tk
from tkinter import filedialog, ttk
from mutagen.mp3 import MP3
import time
import threading
from pydub import AudioSegment
import numpy as np
from PIL import Image, ImageTk
from yt_dlp import YoutubeDL
# from pytube import Search

from waveforms import*


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("PipiProut")
        self.root.geometry("800x700")
        self.root.configure(bg='#2d2d2d')
        
        # Initialisation pygame
        pygame.mixer.init()
        
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        # Récupérer les données audio pour visualisation
        samples = pygame.sndarray.array(pygame.mixer.music)
        self.waveform_data = None
        self.waveform_data_raw = None
        
        # Variables
        self.playlist = []
        self.current_index = 0
        self.paused = False
        self.volume = 0.3
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
            'external_downloader_args': ['-ss', '0', '-to', '10'],  # Télécharge d'abord les 10 premières secondes
            # Optimisations pour la recherche
            # 'extract_flat': True,
            # 'simulate': True,
            # 'skip_download': True,
        }
        self.is_searching = False
        

        self.song_length = 0
        self.current_time = 0
        
        self.user_dragging = False
        self.base_position = 0
        
        self.show_waveform_current = False
        
        # Chargement des icônes
        self.icons = {}
        self.load_icons()
        
        # UI Modern
        self.create_ui()
        
        # Thread de mise à jour
        self.update_thread = threading.Thread(target=self.update_time, daemon=True)
        self.update_thread.start()
        
        self.current_downloads = set()  # Pour suivre les URLs en cours de téléchargement
        self.resize_timer = None  # Pour éviter de redessiner trop souvent pendant le redimensionnement

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
        
         # Création du Notebook (onglets)
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
        
        # Contrôles de lecture (en bas, communs aux deux onglets)
        self.setup_controls()
        
        # Lier le changement d'onglet à une fonction
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        
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

        search_btn = ttk.Button(youtube_frame, text="Rechercher", command=self.search_youtube)
        search_btn.pack(side=tk.LEFT)
    
        # Middle Frame (Playlist and results)
        middle_frame = ttk.Frame(self.search_tab)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Playlist Frame (left side - takes all vertical space)
        playlist_frame = ttk.Frame(middle_frame)
        playlist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas et Scrollbar pour la playlist
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
        
        # Youtube Results Frame (right side - fixed width)
        youtube_results_frame = ttk.Frame(middle_frame, width=350)
        youtube_results_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Canvas avec Scrollbar pour les résultats YouTube
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
        self.youtube_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.youtube_canvas.pack(side="left", fill="both", expand=True)

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
        downloads_btn = tk.Button(
            vertical_tabs_frame,
            text="Téléchargées",
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
        downloads_btn.pack(fill=tk.X, pady=2)
        self.library_tab_buttons["téléchargées"] = downloads_btn
        
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
        # Titre
        title_label = ttk.Label(
            self.library_content_frame, 
            text="Musiques téléchargées", 
            font=('Helvetica', 14, 'bold')
        )
        title_label.pack(pady=(10, 20))
        
        # Canvas avec scrollbar pour les téléchargements
        downloads_canvas = tk.Canvas(
            self.library_content_frame,
            bg='#3d3d3d',
            highlightthickness=0
        )
        downloads_scrollbar = ttk.Scrollbar(
            self.library_content_frame,
            orient="vertical",
            command=downloads_canvas.yview
        )
        downloads_canvas.configure(yscrollcommand=downloads_scrollbar.set)
        
        downloads_scrollbar.pack(side="right", fill="y")
        downloads_canvas.pack(side="left", fill="both", expand=True)
        
        self.downloads_container = ttk.Frame(downloads_canvas)
        downloads_canvas.create_window((0, 0), window=self.downloads_container, anchor="nw")
        
        self.downloads_container.bind(
            "<Configure>",
            lambda e: downloads_canvas.configure(
                scrollregion=downloads_canvas.bbox("all")
            )
        )
        
        self._bind_mousewheel(downloads_canvas, downloads_canvas)
        self._bind_mousewheel(self.downloads_container, downloads_canvas)
        
        # Charger et afficher les fichiers téléchargés
        self.load_downloaded_files()
    
    def show_playlists_content(self):
        """Affiche le contenu de l'onglet playlists"""
        title_label = ttk.Label(
            self.library_content_frame, 
            text="Playlists (à développer)", 
            font=('Helvetica', 14, 'bold')
        )
        title_label.pack(pady=50)
    
    def load_downloaded_files(self):
        """Charge et affiche tous les fichiers du dossier downloads"""
        downloads_dir = "downloads"
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
            return
        
        # Extensions audio supportées
        audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
        
        # Parcourir le dossier downloads
        for filename in os.listdir(downloads_dir):
            if filename.lower().endswith(audio_extensions):
                filepath = os.path.join(downloads_dir, filename)
                self._add_download_item(filepath)
    
    def _add_download_item(self, filepath):
        """Ajoute un élément téléchargé avec le même visuel que les résultats de recherche"""
        try:
            filename = os.path.basename(filepath)
            
            # Frame principal pour l'item
            item_frame = ttk.Frame(
                self.downloads_container,
                style='TFrame',
                padding=(5, 5)
            )
            item_frame.pack(fill='x', pady=2)
            
            # Configuration de la grille en 4 colonnes : miniature, texte, durée, bouton
            item_frame.columnconfigure(0, minsize=120, weight=0)  # Miniature plus large
            item_frame.columnconfigure(1, weight=1)               # Texte
            item_frame.columnconfigure(2, minsize=60, weight=0)   # Durée
            item_frame.columnconfigure(3, minsize=80, weight=0)   # Bouton
            
            # 1. Miniature (colonne 0)
            thumbnail_label = tk.Label(
                item_frame,
                bg='#3d3d3d',
                width=15,  # Plus large
                height=5   # Plus haute
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsw', padx=(0, 5))
            
            # Charger la miniature (chercher un fichier image associé)
            self._load_download_thumbnail(filepath, thumbnail_label)
            
            # 2. Texte (colonne 1)
            text_frame = ttk.Frame(item_frame)
            text_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 5))
            
            title_label = tk.Label(
                text_frame,
                text=filename,
                bg='#3d3d3d',
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left'
            )
            title_label.pack(side='left', fill='x', expand=True)
            
            # 3. Durée (colonne 2)
            duration_label = tk.Label(
                item_frame,
                text=self._get_audio_duration(filepath),
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 8),
                anchor='center'
            )
            duration_label.grid(row=0, column=2, sticky='ns', padx=(0, 5))
            
            # 4. Bouton "Ajouter à la playlist" (colonne 3)
            add_btn = tk.Button(
                item_frame,
                text="+ Playlist",
                command=lambda f=filepath: self._add_download_to_playlist(f),
                bg="#4a8fe7",
                fg="white",
                activebackground="#5a9fd8",
                relief="flat",
                bd=0,
                padx=8,
                pady=4,
                font=('TkDefaultFont', 8)
            )
            add_btn.grid(row=0, column=3, sticky='ns')
            
            # Double-clic pour jouer directement
            def on_item_double_click():
                self._add_download_to_playlist(filepath)
                # Jouer immédiatement
                if filepath in self.playlist:
                    self.current_index = self.playlist.index(filepath)
                    self.play_track()
            
            item_frame.bind("<Double-1>", lambda e: on_item_double_click())
            thumbnail_label.bind("<Double-1>", lambda e: on_item_double_click())
            title_label.bind("<Double-1>", lambda e: on_item_double_click())
            
        except Exception as e:
            print(f"Erreur affichage download item: {e}")
    
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
    
    def _add_download_to_playlist(self, filepath):
        """Ajoute un fichier téléchargé à la playlist"""
        if filepath not in self.playlist:
            self.playlist.append(filepath)
            self._add_playlist_item(filepath)
            self.status_bar.config(text=f"Ajouté à la playlist: {os.path.basename(filepath)}")
        else:
            self.status_bar.config(text=f"Déjà dans la playlist: {os.path.basename(filepath)}")
    
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
        
        # Conteneur horizontal pour boutons + volume
        buttons_volume_frame = ttk.Frame(control_frame)
        buttons_volume_frame.pack(fill=tk.X, pady=20)

        # Frame boutons (centré)
        button_frame = ttk.Frame(buttons_volume_frame)
        button_frame.grid(row=0, column=1, padx=20)

        # Boutons avec grid (centré dans button_frame)
        ttk.Button(button_frame, image=self.icons["add"], command=self.add_to_playlist).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, image=self.icons["prev"], command=self.prev_track).grid(row=0, column=1, padx=5)
        self.play_button = ttk.Button(button_frame, image=self.icons["play"], command=self.play_pause)
        self.play_button.grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, image=self.icons["next"], command=self.next_track).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, image=self.icons["hey"]).grid(row=0, column=4, padx=5)

        # Frame volume à droite
        volume_frame = ttk.Frame(buttons_volume_frame)
        volume_frame.grid(row=0, column=2, sticky="e")

        ttk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT)
        self.volume_slider = ttk.Scale(
            volume_frame, from_=0, to=100, 
            command=self.set_volume, value=self.volume*100,
            orient='horizontal',
            length=200
        )
        self.volume_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)

        # Ajouter une colonne vide à gauche pour centrer (optionnel)
        buttons_volume_frame.grid_columnconfigure(0, weight=1)
        buttons_volume_frame.grid_columnconfigure(1, weight=0)  # bouton centré
        buttons_volume_frame.grid_columnconfigure(2, weight=0)  # volume
        buttons_volume_frame.grid_columnconfigure(3, weight=1)

        
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
            if isinstance(child, ttk.Frame):
                style_name = f"Debug.TFrame{color_index}"
                # Copier le layout standard "TFrame"
                style.layout(style_name, style.layout("TFrame"))
                style.configure(style_name, background=colors[color_index % len(colors)])
                child.configure(style=style_name)
                color_index += 1

            # Appel récursif sur les enfants
            self.colorize_ttk_frames(child, colors)
            

        
        
    
    # def add_to_playlist(self):
    #     files = filedialog.askopenfilenames(
    #         filetypes=[("Fichiers Audio", "*.mp3 *.wav *.ogg *.flac"), ("Tous fichiers", "*.*")]
    #     )
    #     for file in files:
    #         self.playlist.append(file)
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
            self.playlist.append(file)
            self._add_playlist_item(file)
        self.status_bar.config(text=f"{len(files)} track added")

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



    def _add_playlist_item(self, filepath, thumbnail_path=None):
        """Ajoute un élément à la playlist avec un style rectangle uniforme"""
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
            
            # Configuration de la grille en 4 colonnes : miniature, titre, durée, bouton
            item_frame.columnconfigure(0, minsize=80, weight=0)  # Miniature
            item_frame.columnconfigure(1, weight=1)              # Titre
            item_frame.columnconfigure(2, minsize=60, weight=0)  # Durée
            item_frame.columnconfigure(3, minsize=40, weight=0)  # Bouton

            # 2. Miniature (colonne 0)
            thumbnail_label = tk.Label(
                item_frame,
                bg='#4a4a4a',
                width=10,
                height=3
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsw', padx=(10, 10), pady=8)
            
            # Charger la miniature
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._load_image_thumbnail(thumbnail_path, thumbnail_label)
            else:
                self._load_mp3_thumbnail(filepath, thumbnail_label)

            # 3. Titre (colonne 1)
            title_label = tk.Label(
                item_frame,
                text=filename,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left'
            )
            title_label.grid(row=0, column=1, sticky='nsew', padx=(0, 10), pady=8)
            
            # 4. Durée (colonne 2)
            duration_text = self._get_audio_duration(filepath)
            duration_label = tk.Label(
                item_frame,
                text=duration_text,
                bg='#4a4a4a',
                fg='#cccccc',
                font=('TkDefaultFont', 8),
                anchor='center'
            )
            duration_label.grid(row=0, column=2, sticky='ns', padx=(0, 10), pady=8)

            # 5. Bouton de suppression (colonne 3)
            delete_btn = tk.Button(
                item_frame,
                text="✕",
                command=lambda f=filepath, frame=item_frame: self._remove_playlist_item(f, frame),
                bg='#ff4444',
                fg='white',
                activebackground='#ff6666',
                relief='flat',
                bd=0,
                width=3,
                height=1,
                font=('TkDefaultFont', 8)
            )
            delete_btn.grid(row=0, column=3, sticky='ns', padx=(0, 10), pady=8)

            item_frame.filepath = filepath
            
            def on_item_click():
                self.current_index = self.playlist.index(filepath)
                self.play_track()
                
            item_frame.bind("<Double-1>", lambda e: on_item_click())
            thumbnail_label.bind("<Double-1>", lambda e: on_item_click())
            title_label.bind("<Double-1>", lambda e: on_item_click())

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

    
    def _remove_playlist_item(self, filepath, frame):
        """Supprime un élément de la playlist"""
        try:
            # Trouver l'index de l'élément à supprimer
            index = self.playlist.index(filepath)
            
            # Supprimer de la liste
            self.playlist.pop(index)
            
            # Supprimer de l'affichage
            frame.destroy()
            
            
            # Mettre à jour l'index courant si nécessaire
            if index < self.current_index:
                self.current_index -= 1
            elif index == self.current_index:
                pygame.mixer.music.stop()
                self.current_index = min(index, len(self.playlist) - 1)
                if len(self.playlist) > 0:
                    self.play_track()
            
            self.status_bar.config(text=f"Piste supprimée")
        except ValueError:
            pass
        except Exception as e:
            self.status_bar.config(text=f"Erreur suppression: {e}")
    
    def _load_image_thumbnail(self, image_path, label):
        """Charge une image normale comme thumbnail"""
        try:
            img = Image.open(image_path)
            img.thumbnail((120, 68), Image.Resampling.LANCZOS)  # Plus grande (ratio 16:9)
            photo = ImageTk.PhotoImage(img)
            label.configure(image=photo)
            label.image = photo
        except Exception as e:
            print(f"Erreur chargement image thumbnail: {e}")
            # Fallback à une icône par défaut
            default_icon = Image.new('RGB', (120, 68), color='#3d3d3d')
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
            default_icon = Image.new('RGB', (120, 68), color='#3d3d3d')
            photo = ImageTk.PhotoImage(default_icon)
            label.configure(image=photo)
            label.image = photo
            
        except Exception as e:
            print(f"Erreur chargement thumbnail MP3: {e}")
            # Fallback à une icône par défaut
            default_icon = Image.new('RGB', (120, 68), color='#3d3d3d')
            photo = ImageTk.PhotoImage(default_icon)
            label.configure(image=photo)
            label.image = photo

    def _play_playlist_item(self, filepath):
        """Joue un élément de la playlist"""
        try:
            self.current_index = self.playlist.index(filepath)
            self.play_track()
        except ValueError:
            pass

    def play_track(self):
        try:
            song = self.playlist[self.current_index]
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(start=0)
            self.base_position = 0
            pygame.mixer.music.set_volume(self.volume)
            
            self.paused = False
            self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")
            
            # Mettre en surbrillance la piste courante
            self.select_playlist_item(index=self.current_index)
            
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
        
        # Effacer les résultats précédents
        # self.youtube_results.delete(0, tk.END)
        self._clear_results()  # Utilisez la méthode qui vide le container
        self.search_list = []
        self.status_bar.config(text="Recherche en cours...")
        self.root.update()  # Forcer la mise à jour de l'interface
        
        query = self.youtube_entry.get()
        if not query:
            return
            
        self.is_searching = True
        # self.youtube_results.delete(0, tk.END)
        self._clear_results()  # Utilisez la méthode qui vide le container
        self.status_bar.config(text="Recherche en cours...")
        
        # Lancer la recherche dans un thread séparé
        threading.Thread(target=self._perform_search, args=(query,), daemon=True).start()


    def _perform_search(self, query):
        try:
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'max_downloads': 10,
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                results = ydl.extract_info(f"ytsearch10:{query}", download=False)
                
                if not results or 'entries' not in results:
                    self.root.after(0, lambda: self.status_bar.config(text="Aucun résultat trouvé"))
                    return
                    
                # Nettoyer le container avant d'ajouter de nouveaux résultats
                self.root.after(0, self._clear_results)
                
                # Filtrer pour ne garder que les vidéos (pas les playlists/chaines)
                video_results = [
                    entry for entry in results['entries']
                    if "https://www.youtube.com/watch?v=" in entry.get('url')  # Seulement les vidéos
                    and entry.get('duration',0) <= 600.0  # Durée max de 10 minutes
                ]
                
                # Afficher les résultats
                for i, video in enumerate(video_results):
                    self.root.after(0, lambda v=video, idx=i: self._add_search_result(v, idx))
                    
                self.root.after(0, lambda: self.status_bar.config(
                    text=f"{len(video_results)} vidéos trouvées"
                ))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_bar.config(text=f"Erreur recherche: {e}"))
        finally:
            self.is_searching = False

    def _clear_results(self):
        """Vide le container de résultats"""
        for widget in self.results_container.winfo_children():
            widget.destroy()
        self.youtube_canvas.yview_moveto(0)  # Remet le scroll en haut

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
            
            # Configuration de la grille en 3 colonnes : miniature, titre, durée
            result_frame.columnconfigure(0, minsize=120, weight=0)  # Miniature plus large
            result_frame.columnconfigure(1, weight=1)               # Titre
            result_frame.columnconfigure(2, minsize=60, weight=0)   # Durée
            
            # 1. Miniature (colonne 0)
            thumbnail_label = tk.Label(
                result_frame,
                bg='#4a4a4a',
                width=15,  # Plus large
                height=5   # Plus haute
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsw', padx=(10, 10), pady=8)
            
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
            
            # Événements de clic
            duration_label.bind("<Double-1>", lambda e, f=result_frame: self._on_result_click(f))
            title_label.bind("<Double-1>", lambda e, f=result_frame: self._on_result_click(f))
            thumbnail_label.bind("<Double-1>", lambda e, f=result_frame: self._on_result_click(f))
            result_frame.bind("<Double-1>", lambda e, f=result_frame: self._on_result_click(f))
            
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
        """Ajoute le fichier téléchargé à la playlist (à appeler dans le thread principal)"""
        # Vérifier si le fichier est déjà dans la playlist
        if filepath not in self.playlist:
            self.playlist.append(filepath)
            self._add_playlist_item(filepath, thumbnail_path)
            self.status_bar.config(text=f"{title} ajouté à la playlist")
        else:
            self.status_bar.config(text=f"{title} est déjà dans la playlist")

    def _load_thumbnail(self, label, url):
        """Charge et affiche la miniature"""
        try:
            import requests
            from io import BytesIO
            
            response = requests.get(url, timeout=5)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img.thumbnail((120, 68), Image.Resampling.LANCZOS)  # Plus grande (ratio 16:9)
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
    
    def get_adaptive_waveform_data(self, canvas_width):
        """Génère des données waveform adaptées à la largeur du canvas"""
        if self.waveform_data_raw is None:
            return None
            
        # Calculer la résolution optimale : 2-3 échantillons par pixel pour une bonne qualité
        target_resolution = max(canvas_width * 2, 6000)  # Minimum 1000 échantillons
        
        # Sous-échantillonner les données brutes
        if len(self.waveform_data_raw) > target_resolution:
            step = len(self.waveform_data_raw) // target_resolution
            return self.waveform_data_raw[::step]
        else:
            return self.waveform_data_raw
    
    def play_pause(self):
        if not self.playlist:
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
    #         song = self.playlist[self.current_index]
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
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_track()

    def next_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
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

        # Obtenir la largeur du canvas et adapter la résolution
        canvas_width = self.waveform_canvas.winfo_width()
        if canvas_width <= 1:
            self.waveform_canvas.update_idletasks()
            canvas_width = self.waveform_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 600

        # Générer les données adaptées à la largeur du canvas
        adaptive_data = self.get_adaptive_waveform_data(canvas_width)
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

    
    def load_icons(self):

        icon_names = {
            "add": "add.png",
            "prev": "prev.png",
            "play": "play.png",
            "next": "next.png",
            "hey": "hey.png",
            "pause": "pause.png",
            "delete": "delete.png"
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
        
    
    def set_volume(self, val):
        self.volume = float(val) / 100
        pygame.mixer.music.set_volume(self.volume)
    
    def on_progress_press(self, event):
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
        if self.user_dragging:
            pos = self.progress.get()  # En secondes
            self.current_time_label.config(
                text=time.strftime('%M:%S', time.gmtime(pos))
            )
            self.draw_waveform_around(pos)

    def on_progress_release(self, event):
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
        """Appelé quand le canvas waveform change de taille"""
        # Ne redessiner que si la waveform est visible et qu'on a des données
        if (self.show_waveform_current and 
            self.waveform_data_raw is not None and 
            event.width > 1):  # S'assurer qu'on a une largeur valide
            
            # Annuler le timer précédent s'il existe
            if self.resize_timer:
                self.root.after_cancel(self.resize_timer)
            
            # Programmer le redessin avec un délai de 100ms pour éviter trop de redraws
            self.resize_timer = self.root.after(100, lambda: self.draw_waveform_around(self.current_time))
        
        
    
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
            time.sleep(0.05)
            # print(self.current_time)
    
    def on_closing(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.on_closing)
    root.mainloop()