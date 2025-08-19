"""
Méthodes d'initialisation pour Pipi Player
Extrait de main.py pour améliorer la lisibilité
"""

def init_window(self, root):
    """Initialise la fenêtre principale"""
    self.root = root
    self.root.title("Pipi Player")
    self.root.geometry("800x700")
    self.root.resizable(False, False)  # Empêcher le redimensionnement
    self.root.configure(bg='#2d2d2d')
    root.option_add("*Button.takeFocus", 0)
    
    # Changer l'icône de la fenêtre
    try:
        import os
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Impossible de charger l'icône: {e}")

def init_pygame(self):
    """Initialise pygame pour l'audio"""
    import pygame
    pygame.mixer.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    
    # Récupérer les données audio pour visualisation
    samples = pygame.sndarray.array(pygame.mixer.music)
    self.waveform_data = None
    self.waveform_data_raw = None

def init_variables(self):
    """Initialise toutes les variables de l'application"""
    import os
    import threading
    
    # Variables de base
    self.main_playlist = []
    self.current_index = 0
    self.paused = False
    self.volume = 0.1
    self.volume_offset = 0  # Offset de volume en pourcentage (-50 à +50)
    
    # Configuration YouTube-DL
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
        'external_downloader': 'ffmpeg',
    }
    
    # Variables de recherche
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
    
    # Variables de lecture
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
    
    # Variables d'interface
    self.icons = {}
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

def init_components(self):
    """Initialise les composants de l'application"""
    import threading
    
    # Chargement des icônes
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

def init_data(self):
    """Charge les données initiales"""
    # Charger les playlists sauvegardées
    self.load_playlists()
    
    # Charger la configuration (volume global et offsets)
    self.load_config()
    
    # Compter les fichiers téléchargés au démarrage
    self._count_downloaded_files()
    
    # Bindings de clavier
    self.setup_keyboard_bindings()