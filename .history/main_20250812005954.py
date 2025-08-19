# Import centralisé depuis __init__.py
from __init__ import *


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pipi Player")
        self.root.geometry(GEOMETRY)
        # Fixer la taille mais permettre le déplacement
        self.root.resizable(False, False)
        self.root.configure(bg='#2d2d2d')
        root.option_add("*Button.takeFocus", 0)
        root.option_add("*TNotebook.Tab.takeFocus", 0)
        
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
        self.volume = 0.2
        self.volume_offset = 0  # Offset de volume en pourcentage (-100 à +100)
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
        self.search_cancelled = False  # Flag pour annuler la recherche en cours
        self.current_search_thread = None  # Thread de recherche actuel
        
        # Variables pour le lazy loading YouTube
        self.initial_search_count = 10  # Nombre de résultats pour la recherche initiale
        self.lazy_load_increment = 10   # Nombre de résultats à charger à chaque fois
        self.has_more_results = False   # True s'il y a potentiellement plus de résultats
        self.total_available_results = 0  # Nombre total de résultats disponibles
        
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
        
        # Variable pour le périphérique audio actuel
        self.current_audio_device = None  # Nom du périphérique audio actuel
        
        # Chargement des icônes
        self.icons = {}
        setup.load_icons(self)
        
        # Initialiser le gestionnaire de drag-and-drop
        self.drag_drop_handler = DragDropHandler(self)
        
        # UI Modern
        setup.create_ui(self)

        # Mettre à jour les sliders avec les valeurs chargées
        setup._update_volume_sliders(self)
        # self._update_volume_sliders()
        
        # Marquer la fin de l'initialisation
        self.initializing = False
        
        # Thread de mise à jour
        self.update_thread = threading.Thread(target=self.update_time, daemon=True)
        self.update_thread.start()
        
        self.current_downloads = set()  # Pour suivre les URLs en cours de téléchargement
        self.current_download_title = ""  # Pour stocker le titre en cours de téléchargement
        self.pending_playlist_additions = {}  # Dictionnaire {url: [liste_playlists]} pour les ajouts en attente
        self.pending_queue_additions = {}  # Dictionnaire {url: True} pour les ajouts à la queue en attente
        self.pending_play_after_current = {}  # Dictionnaire {url: True} pour les "play after current" en attente
        self.pending_queue_first_additions = {}  # Dictionnaire {url: True} pour les ajouts en premier dans la queue en attente
        self.queue_items = set()  # Set des indices (positions) qui font partie de la queue
        self.resize_timer = None  # Pour éviter de redessiner trop souvent pendant le redimensionnement
        
        # Variables pour l'optimisation de la recherche
        self.search_timer = None  # Timer pour le debounce de la recherche
        self.search_delay = 300  # Délai de base en millisecondes avant de lancer la recherche
        self.normalized_filenames = {}  # Cache des noms de fichiers normalisés
        
        # Variables pour mesurer le temps de recherche
        self.search_start_time = None  # Temps de début de recherche
        self.library_search_start_time = None  # Temps de début de recherche bibliothèque
        
        # Variables pour les statistiques
        self.last_search_time = 0.0  # Dernier temps de recherche
        
        # Variables pour les statistiques détaillées
        self.stats = {
            'songs_played': 0,  # Nombre de musiques lues (70% ou plus)
            'total_listening_time': 0.0,  # Temps total d'écoute en secondes
            'searches_count': 0,  # Nombre de recherches effectuées
            'current_song_start_time': None,  # Temps de début de la chanson actuelle
            'current_song_listened_time': 0.0,  # Temps écouté de la chanson actuelle
            'current_song_duration': 0.0,  # Durée de la chanson actuelle
            'played_songs': set()  # Set des chansons déjà comptées comme lues
        }
        
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
        self.selected_items_order = []  # Liste ordonnée des chemins de fichiers sélectionnés (pour maintenir l'ordre de clic)
        self.selection_frames = {}  # Dictionnaire {filepath: frame} pour retrouver les frames
        self.shift_selection_active = False  # True quand on est en mode sélection Shift
        
        # Variables pour l'animation de scroll
        self.scroll_animation_active = False  # True si une animation est en cours
        self.scroll_animation_id = None  # ID du timer d'animation
        
        # Variables pour l'animation du titre
        self.title_animation_active = False  # True si l'animation du titre est en cours
        self.title_animation_id = None  # ID du timer d'animation du titre
        self.title_full_text = ""  # Texte complet du titre
        self.title_scroll_position = 0  # Position actuelle du défilement
        self.title_pause_counter = 0  # Compteur pour la pause entre les cycles
        
        # Charger les playlists sauvegardées
        self.load_playlists()

        # Charger la configuration (volume global et offsets)
        self.load_config()
        
        # Initialiser le périphérique audio actuel si pas encore défini
        if self.current_audio_device is None:
            self._detect_current_audio_device()

        # Compter les fichiers téléchargés au démarrage
        self._count_downloaded_files()

        # Bindings de clavier
        self.setup_keyboard_bindings()
        
        # self.colorize_ttk_frames(root)

    def load_playlists(self):
        setup.load_playlists(self)

    def load_config(self):
        setup.load_config(self)
    
    def _count_downloaded_files(self):
        file_services._count_downloaded_files(self)

    def setup_keyboard_bindings(self):
        setup.setup_keyboard_bindings(self)

    def _update_downloads_button(self):
        """Met à jour le texte du bouton téléchargées avec le nombre actuel"""
        return library_tab.downloads._update_downloads_button(self)

    def setup_focus_bindings(self):
        setup.setup_focus_bindings(self)
    
    def on_space_pressed(self, event):
        inputs.on_space_pressed(self, event)
    
    def on_escape_pressed(self, event):
        """Gère l'appui sur la touche Échap"""
        inputs.on_escape_pressed(self, event)
    
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
    
    def _update_stats_bar(self):
        """Met à jour la barre de statistiques avec le temps de recherche"""
        if not hasattr(self, 'stats_bar'):
            return
            
        if self.last_search_time > 0:
            self.stats_bar.config(text=f"recherche en {self.last_search_time:.2f}s")
        else:
            self.stats_bar.config(text="")
    
    
    def on_tab_changed(self, event):
        """Gère le changement d'onglet"""
        # Annuler la sélection multiple lors du changement d'onglet
        if hasattr(self, 'selected_items') and self.selected_items:
            self.clear_selection()
        
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Recherche":
            # Vous pourriez ajouter ici des actions spécifiques au changement d'onglet
            pass
        elif selected_tab == "Bibliothèque":
            # Vous pourriez ajouter ici des actions spécifiques au changement d'onglet
            pass
    
    def setup_search_tab(self):
        setup.setup_search_tab(self)
    
    def setup_library_tab(self):
        setup.setup_library_tab(self)

    def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
        tools.colorize_ttk_frames(self, widget, colors)
    
    def _on_youtube_canvas_configure(self, event):
        """Vérifie si on doit charger plus de résultats quand le canvas change"""
        return search_tab.results._on_youtube_canvas_configure(self, event)

    # def _on_youtube_scroll(self, event):
    #     """Gère le scroll de la molette dans les résultats YouTube"""
    #     inputs._on_youtube_scroll(self, event)
    
    def _should_load_more_results(self):
        """Vérifie si on doit charger plus de résultats"""
        if (self.is_loading_more or 
            self.is_searching or
            not self.current_search_query or 
            self.search_results_count >= self.max_search_results or
            self.current_search_batch >= self.max_search_batchs):
            return False
        
        # Vérifier si on est proche du bas
        try:
            # Obtenir la position actuelle du scroll (0.0 à 1.0)
            scroll_top, scroll_bottom = self.youtube_canvas.yview()
            
            # Si on est à plus de 80% vers le bas, charger plus
            if scroll_bottom > 0.8:
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
        return library_tab.downloads.show_downloads_content(self)
    
    def show_playlists_content(self):
        """Affiche le contenu de l'onglet Playlists"""
        library_tab.playlists.show_playlists_content(self)
    
    def _display_playlists(self):
        """Affiche toutes les playlists en grille 3x3"""
        library_tab.playlists._display_playlists(self)
    
    def _add_playlist_card(self, parent_frame, playlist_name, songs, column):
        """Ajoute une carte de playlist avec miniatures"""
        library_tab.playlists._add_playlist_card(self, parent_frame, playlist_name, songs, column)
    
    def _load_playlist_thumbnail_large(self, filepath, label):
        """Charge une miniature carrée plus grande pour une chanson dans une playlist"""
        library_tab.playlists._load_playlist_thumbnail_large(self, filepath, label)

    def _load_playlist_thumbnail(self, filepath, label):
        """Charge une miniature pour une chanson dans une playlist"""
        return library_tab.playlists._load_playlist_thumbnail(self, filepath, label)

    
    def save_playlists(self):
        """Sauvegarde les playlists dans un fichier JSON"""
        return library_tab.playlists.save_playlists(self)
    
    def save_config(self):
        """Sauvegarde la configuration (volume global et offsets de volume)"""
        return tools.save_config(self)
  
    def _rename_playlist_dialog(self, old_name):
        """Dialogue pour renommer une playlist"""
        return library_tab.playlists._rename_playlist_dialog(self, old_name)

    
    def _delete_playlist_dialog(self, playlist_name):
        """Dialogue pour confirmer la suppression d'une playlist"""
        return library_tab.playlists._delete_playlist_dialog(self, playlist_name)
    
    def _show_playlist_content_window(self, playlist_name):
        """Affiche le contenu d'une playlist dans une fenêtre avec le même style que les téléchargements"""
        return library_tab.playlists._show_playlist_content_window(self, playlist_name)

    
    def _play_from_playlist(self, filepath, playlist_name):
        """Joue une musique depuis une playlist spécifique"""
        # Ajouter à la main playlist si pas déjà présent
        self.add_to_main_playlist(filepath, show_status=False)
        
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
            pady=8,
            takefocus=0
        )
        back_btn.pack(side=tk.LEFT)
        
        # Titre de la playlist avec nombre de chansons
        songs_count = len(self.playlists.get(playlist_name, []))
        title_label = tk.Label(
            header_frame,
            text=f"{playlist_name} ({songs_count} titres)",
            bg='#2d2d2d',
            fg='white',
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Binding pour la touche Échap pour retourner aux playlists
        self.root.bind('<Escape>', self._on_playlist_escape)
        self.root.focus_set()  # S'assurer que la fenêtre a le focus pour recevoir les événements clavier
        
        # Canvas avec scrollbar pour les musiques (même style que téléchargements)
        self.playlist_content_canvas = tk.Canvas(
            self.library_content_frame,
            bg='#3d3d3d',
            highlightthickness=0,
            takefocus=0
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
        return library_tab.playlists._back_to_playlists(self)
    
    def _on_playlist_escape(self, event):
        """Gère l'appui sur Échap dans une playlist pour retourner aux playlists"""
        if hasattr(self, 'current_viewing_playlist') and self.current_viewing_playlist:
            self._back_to_playlists()
    
    def _clear_main_playlist(self, event=None):
        """Vide complètement la liste de lecture principale (nécessite un double-clic)"""
        if not self.main_playlist:
            self.status_bar.config(text="La liste de lecture est déjà vide")
            return
        
        # Arrêter la lecture si une musique est en cours
        if hasattr(self, 'paused') and not self.paused:
            pygame.mixer.music.stop()
        
        # Vider la liste principale et la playlist "Main Playlist"
        self.main_playlist.clear()
        if "Main Playlist" in self.playlists:
            self.playlists["Main Playlist"].clear()
        self.current_index = 0
        
        # Vider la queue
        if hasattr(self, 'queue_items'):
            self.queue_items.clear()
        
        # Vider l'affichage de la playlist
        for widget in self.playlist_container.winfo_children():
            widget.destroy()
        
        # Mettre à jour l'affichage
        self.status_bar.config(text="Liste de lecture vidée")
        
        # Réinitialiser l'affichage de la chanson actuelle
        if hasattr(self, 'song_label'):
            self.song_label.config(text="No track selected")
        if hasattr(self, 'song_metadata_label'):
            self.song_metadata_label.config(text="")
        
        # Mettre à jour les contrôles
        if hasattr(self, 'time_slider'):
            self.time_slider.set(0)
        if hasattr(self, 'time_label'):
            self.time_label.config(text="00:00 / 00:00")
    
    def _scroll_to_current_song(self, event=None):
        """Fait défiler la liste de lecture vers la chanson en cours (même position que "piste suivante")"""
        if not self.main_playlist or self.current_index >= len(self.main_playlist):
            self.status_bar.config(text="Aucune musique en cours de lecture")
            return
        
        try:
            # Utiliser la même fonction que play_track() pour positionner la vue
            self.select_playlist_item(index=self.current_index)
            
            total_songs = len(self.main_playlist)
            self.status_bar.config(text=f"Navigation vers la chanson {self.current_index + 1}/{total_songs}")
            
        except Exception as e:
            print(f"Erreur lors du scroll vers la chanson actuelle: {e}")
            self.status_bar.config(text="Erreur lors de la navigation")

    def _display_playlist_songs(self, playlist_name):
        """Affiche les musiques d'une playlist avec le même style que les téléchargements"""
        return library_tab.playlists._display_playlist_songs(self, playlist_name)

    def _add_playlist_song_item(self, filepath, playlist_name, song_index):
        """Ajoute un élément de musique de playlist avec le même visuel que les téléchargements"""
        return library_tab.playlists._add_playlist_song_item(self, filepath, playlist_name, song_index)
    
    def _remove_from_playlist_view(self, filepath, playlist_name, event=None):
        """Supprime une musique de la playlist et rafraîchit l'affichage"""
        return library_tab.playlists._remove_from_playlist_view(self, filepath, playlist_name, event)

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
        return library_tab.downloads.load_downloaded_files(self)
    
    def play_all_downloads_ordered(self):
        """Joue toutes les musiques téléchargées dans l'ordre"""
        if not self.all_downloaded_files:
            return
        
        # Copier la liste des fichiers téléchargés dans la playlist principale
        self.main_playlist.clear()
        self.main_playlist.extend(self.all_downloaded_files.copy())
        
        # Désactiver le mode aléatoire et réinitialiser l'index
        self.random_mode = False
        self.current_index = 0
        
        # Mettre à jour l'apparence du bouton random
        self.random_button.config(bg="#3d3d3d")
        
        # Démarrer la lecture
        self.play_track()
        
        # Rafraîchir l'affichage de la playlist
        self._refresh_playlist_display()
    
    def play_all_downloads_shuffle(self):
        """Joue toutes les musiques téléchargées en mode aléatoire"""
        if not self.all_downloaded_files:
            return
        
        # Copier la liste des fichiers téléchargés dans la playlist principale
        self.main_playlist.clear()
        self.main_playlist.extend(self.all_downloaded_files.copy())
        
        # Activer le mode aléatoire et mélanger la playlist
        self.random_mode = True
        import random
        random.shuffle(self.main_playlist)
        self.current_index = 0
        
        # Mettre à jour l'apparence du bouton random
        self.random_button.config(bg="#4a8fe7")
        
        # Démarrer la lecture
        self.play_track()
        
        # Rafraîchir l'affichage de la playlist
        self._refresh_playlist_display()
    
    def _display_filtered_downloads(self, files_to_display):
        """Affiche une liste filtrée de fichiers téléchargés (optimisé)"""
        return library_tab.downloads._display_filtered_downloads(self, files_to_display)
    
    def _display_files_batch(self, files_to_display, start_index, batch_size=20):
        """Affiche les fichiers par batch pour éviter de bloquer l'interface"""
        return library_tab.downloads._display_files_batch(self, files_to_display, start_index, batch_size)
    
    def _display_files_batch_optimized(self, files_to_display, start_index, total_files, batch_size=50):
        """Version optimisée de l'affichage par batch"""
        return library_tab.downloads._display_files_batch_optimized(self, files_to_display, start_index, total_files, batch_size)
    
    def _show_loading_progress(self, total_files):
        """Affiche un indicateur de progression pendant le chargement"""
        return library_tab.downloads._show_loading_progress(self, total_files)
    
    def _add_download_item_fast(self, filepath):
        """Version rapide de _add_download_item qui charge les miniatures en différé"""
        return library_tab.downloads._add_download_item_fast(self, filepath)
    
    def _start_thumbnail_loading(self, files_to_display):
        """Lance le chargement différé des miniatures et durées"""
        return library_tab.downloads._start_thumbnail_loading(self, files_to_display)
    
    def _load_next_thumbnail(self):
        """Charge la prochaine miniature dans la queue"""
        return library_tab.downloads._load_next_thumbnail(self)
    
    # ==================== MÉTHODES DE CACHE ====================
    
    def _init_cache_system(self):
        """Initialise le système de cache pour les miniatures et durées"""
        return library_tab.downloads._init_cache_system(self)
    
    def _load_duration_cache(self):
        """Charge le cache des durées depuis le disque"""
        return library_tab.downloads._load_duration_cache(self)
    
    def _save_duration_cache(self):
        """Sauvegarde le cache des durées sur le disque"""
        return library_tab.downloads._save_duration_cache(self)
    
    def _load_thumbnail_cache(self):
        """Charge les métadonnées du cache des miniatures"""
        return library_tab.downloads._load_thumbnail_cache(self)
    
    def _save_thumbnail_cache_metadata(self):
        """Sauvegarde les métadonnées du cache des miniatures"""
        return library_tab.downloads._save_thumbnail_cache_metadata(self)
    
    def _get_cached_duration(self, filepath):
        """Récupère la durée depuis le cache ou la calcule si nécessaire"""
        return library_tab.downloads._get_cached_duration(self, filepath)
    
    def _calculate_audio_duration(self, filepath):
        """Calcule la durée réelle d'un fichier audio"""
        return library_tab.downloads._calculate_audio_duration(self, filepath)
    
    def _get_cached_thumbnail_path(self, filepath):
        """Retourne le chemin de la miniature en cache"""
        return library_tab.downloads._get_cached_thumbnail_path(self, filepath)
    
    def _is_thumbnail_cache_valid(self, filepath, cache_path):
        """Vérifie si la miniature en cache est encore valide"""
        return library_tab.downloads._is_thumbnail_cache_valid(self, filepath, cache_path)
    
    def _create_cached_thumbnail(self, filepath, cache_path):
        """Crée et sauvegarde une miniature en cache"""
        return library_tab.downloads._create_cached_thumbnail(self, filepath, cache_path)
    
    def _load_cached_thumbnail(self, filepath, label):
        """Charge une miniature depuis le cache ou la crée si nécessaire"""
        return library_tab.downloads._load_cached_thumbnail(self, filepath, label)
    
    def _load_download_thumbnail_fallback(self, filepath, label):
        """Méthode de fallback pour charger les miniatures (ancienne méthode)"""
        return library_tab.downloads._load_download_thumbnail_fallback(self, filepath, label)
    


    
    
    def _get_adaptive_search_delay(self, query):
        """Calcule un délai de recherche adaptatif selon la longueur et le contenu de la requête"""
        if not query:
            return 0  # Pas de délai pour une recherche vide (affichage immédiat)
        
        query_length = len(query.strip())
        
        # Debounce différentiel selon la longueur
        if query_length <= 2:
            return 150  # Court pour éviter les recherches sur 1-2 lettres
        elif query_length <= 4:
            return 200  # Moyen pour les mots courts
        elif query_length <= 8:
            return 250  # Normal pour les mots moyens
        else:
            # return 300  # Plus long pour les recherches complexes
            return 1000  # Plus long pour les recherches complexes
    
    def _on_library_search_change(self, event):
        """Appelée à chaque changement dans la barre de recherche (avec debounce différentiel)"""
        # Annuler le timer précédent s'il existe
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        
        # Obtenir la requête actuelle pour calculer le délai adaptatif
        current_query = self.library_search_entry.get().strip()
        
        # Enregistrer le temps de début de recherche bibliothèque
        if current_query:  # Seulement si on a une requête
            self.library_search_start_time = time.time()
        
        adaptive_delay = self._get_adaptive_search_delay(current_query)
        
        # Programmer une nouvelle recherche après le délai adaptatif
        self.search_timer = self.root.after(adaptive_delay, self._perform_library_search)
    
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
            
            # Calculer et afficher le temps de recherche bibliothèque
            if self.library_search_start_time:
                search_duration = time.time() - self.library_search_start_time
                self.last_search_time = search_duration
                self._update_stats_bar()
    
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
            # Annuler toute recherche en cours
            if self.is_searching:
                self.search_cancelled = True
            
            # Vider les résultats de recherche
            self._clear_results()
            
            # Réinitialiser les variables de recherche
            self.current_search_query = ""
            self.search_results_count = 0
            self.current_search_batch = 1
            self.all_search_results = []
            self.is_searching = False
            self.is_loading_more = False
            self.search_cancelled = False
            self.current_search_thread = None
            
            # Afficher la miniature de la chanson en cours
            self._show_current_song_thumbnail()
    
    def _clear_youtube_search(self):
        """Efface la recherche YouTube et vide les résultats"""
        # Annuler toute recherche en cours
        if self.is_searching:
            self.search_cancelled = True
            
        self.youtube_entry.delete(0, tk.END)
        
        # Vider les résultats de recherche en utilisant la fonction appropriée
        self._clear_results()
        
        # Réinitialiser les variables de recherche
        self.current_search_query = ""
        self.search_results_count = 0
        self.current_search_batch = 1
        self.all_search_results = []
        self.is_searching = False
        self.is_loading_more = False
        self.search_cancelled = False
        self.current_search_thread = None
        
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
                font=('TkDefaultFont', 60),
                width=300,
                height=300
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
                font=('TkDefaultFont', 60),
                width=300,
                height=300
            )
            # Pack à gauche sans padding pour coller au bord
            no_song_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    def _add_download_item(self, filepath):
        """Ajoute un élément téléchargé avec le même visuel que les résultats de recherche, visuel"""
        return library_tab.downloads._add_download_item(self, filepath)
    
    def _play_after_current(self, filepath):
        """Place une musique juste après celle qui joue actuellement et la lance"""
        try:
            # Ajouter à la main playlist si pas déjà présent
            self.add_to_main_playlist(filepath, show_status=False)
            
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

                    # Redimensionner à une grande taille (370x370)
                    img_resized = img_cropped.resize((370, 370), Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(img_resized)
                    label.configure(image=photo,
                                    text="",
                                    width=300,
                                    height=300
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
        return tools._load_download_thumbnail(self, filepath, label)

    def _truncate_text_for_display(self, text, max_width_pixels=200, max_lines=1, font_family='TkDefaultFont', font_size=9):
        """Tronque le texte pour l'affichage avec des '...' si nécessaire"""
        return tools._truncate_text_for_display(self, text, max_width_pixels, max_lines, font_family, font_size)
    
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
    
    def _get_audio_metadata(self, filepath):
        """Récupère les métadonnées d'un fichier audio (artiste et album)"""
        try:
            if filepath.lower().endswith('.mp3'):
                from mutagen.id3 import ID3
                audio = MP3(filepath)
                
                # Extraire l'artiste
                artist = None
                if 'TPE1' in audio:  # Artist
                    artist = str(audio['TPE1'])
                elif 'TPE2' in audio:  # Album artist
                    artist = str(audio['TPE2'])
                
                # Extraire l'album
                album = None
                if 'TALB' in audio:  # Album
                    album = str(audio['TALB'])
                
                return artist, album
            else:
                # Pour les autres formats, utiliser mutagen générique
                from mutagen import File
                audio = File(filepath)
                if audio is None:
                    return None, None
                
                # Extraire l'artiste (différents tags possibles)
                artist = None
                for tag in ['ARTIST', 'artist', 'Artist']:
                    if tag in audio:
                        artist = audio[tag][0] if isinstance(audio[tag], list) else str(audio[tag])
                        break
                
                # Extraire l'album
                album = None
                for tag in ['ALBUM', 'album', 'Album']:
                    if tag in audio:
                        album = audio[tag][0] if isinstance(audio[tag], list) else str(audio[tag])
                        break
                
                return artist, album
        except:
            return None, None
    
    def _format_artist_album_info(self, artist, album, filepath=None):
        """Formate les informations d'artiste, d'album et de date pour l'affichage"""
        parts = []
        
        # Ajouter l'artiste s'il existe
        if artist:
            parts.append(artist)
        
        # Ajouter l'album s'il existe
        if album:
            parts.append(album)
        
        # Ajouter la date si le filepath est fourni
        if filepath and os.path.exists(filepath):
            date_str = None
            
            try:
                # Essayer d'abord d'obtenir la date de publication YouTube
                youtube_metadata = self.get_youtube_metadata(filepath)
                if youtube_metadata and youtube_metadata.get('upload_date'):
                    upload_date = youtube_metadata['upload_date']
                    # Convertir la date YouTube (format: YYYYMMDD) en format lisible
                    import datetime
                    date_obj = datetime.datetime.strptime(upload_date, "%Y%m%d")
                    date_str = date_obj.strftime("%d/%m/%y")
            except Exception as e:
                print(f"Erreur conversion date YouTube: {e}")
            
            # Si pas de date YouTube, utiliser la date de modification du fichier
            if not date_str:
                try:
                    import datetime
                    mtime = os.path.getmtime(filepath)
                    date_obj = datetime.datetime.fromtimestamp(mtime)
                    date_str = date_obj.strftime("%d/%m/%y")
                except:
                    pass  # Ignorer les erreurs de date
            
            # Ajouter la date si elle existe
            if date_str:
                parts.append(date_str)
        
        # Joindre les parties avec le séparateur •
        return " • ".join(parts) if parts else ""
    
    def _extract_and_save_metadata(self, info, filepath):
        """Extrait les métadonnées depuis les informations YouTube et les sauvegarde dans le fichier MP3"""
        return tools._extract_and_save_metadata(self, info, filepath)
    
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
    
    def add_to_main_playlist(self, filepath, thumbnail_path=None, song_index=None, show_status=True, allow_duplicates=False):
        """Fonction centralisée pour ajouter une musique à la main playlist
        
        Args:
            filepath: Chemin vers le fichier audio
            thumbnail_path: Chemin vers la miniature (optionnel)
            song_index: Index spécifique pour la chanson (optionnel)
            show_status: Afficher le message de statut (défaut: True)
            allow_duplicates: Permettre les doublons (défaut: False)
        """
        if allow_duplicates or filepath not in self.main_playlist:
            self.main_playlist.append(filepath)
            self._add_main_playlist_item(filepath, thumbnail_path, song_index)
            if show_status:
                self.status_bar.config(text=f"Ajouté à la liste de lecture principale: {os.path.basename(filepath)}")
            return True
        else:
            if show_status:
                self.status_bar.config(text=f"Déjà dans la liste de lecture principale: {os.path.basename(filepath)}")
            return False

    def _add_to_specific_playlist(self, filepath, playlist_name):
        """Ajoute un fichier à une playlist spécifique"""
        if playlist_name == "Main Playlist":
            # Pour la main playlist, utiliser la nouvelle fonction centralisée
            self.add_to_main_playlist(filepath)
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
                              relief="flat", bd=0, padx=20, pady=5, takefocus=0)
        create_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Annuler", command=cancel,
                              bg="#666666", fg="white", activebackground="#777777",
                              relief="flat", bd=0, padx=20, pady=5, takefocus=0)
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
            self.add_to_main_playlist(file, show_status=False)
        
        # Marquer que la main playlist ne provient pas d'une playlist (ajout individuel)
        self.main_playlist_from_playlist = False
        
        self.status_bar.config(text=f"{len(files)} track added to main playlist")

    def show_output_menu(self):
        """Affiche un menu déroulant pour choisir le périphérique de sortie audio"""
        try:
            # Obtenir la liste des périphériques audio
            import pygame._sdl2.audio
            devices = pygame._sdl2.audio.get_audio_device_names()
            
            if not devices:
                messagebox.showinfo("Périphériques audio", "Aucun périphérique audio trouvé")
                return
            
            # Créer le menu déroulant
            output_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                                 activebackground='#4a8fe7', activeforeground='white',
                                 relief='flat', bd=1)
            
            # Ajouter un titre
            output_menu.add_command(label="Périphériques de sortie", state='disabled')
            output_menu.add_separator()
            
            # Variable partagée pour les radiobuttons
            if not hasattr(self, 'audio_device_var'):
                self.audio_device_var = tk.StringVar(value=self.current_audio_device or "")
            else:
                self.audio_device_var.set(self.current_audio_device or "")
            
            # Ajouter chaque périphérique comme radiobutton
            for device in devices:
                device_name = device.decode('utf-8') if isinstance(device, bytes) else device
                
                output_menu.add_radiobutton(
                    label=device_name,
                    variable=self.audio_device_var,
                    value=device_name,
                    command=lambda d=device, name=device_name: self.change_output_device(d, name)
                )
            
            # Afficher le menu à la position du bouton
            try:
                x = self.output_button.winfo_rootx()
                y = self.output_button.winfo_rooty() + self.output_button.winfo_height()
                output_menu.post(x, y)
            except:
                # Si erreur de positionnement, afficher au curseur
                output_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'accéder aux périphériques audio:\n{str(e)}")

    def change_output_device(self, selected_device, device_name):
        """Change le périphérique de sortie audio"""
        try:
            # Arrêter la musique actuelle
            was_playing = pygame.mixer.music.get_busy() and not self.paused
            current_pos = self.current_time if was_playing else 0
            
            # Réinitialiser pygame mixer avec le nouveau périphérique
            pygame.mixer.quit()
            pygame.mixer.init(devicename=selected_device, frequency=44100, size=-16, channels=2, buffer=4096)
            
            # Reprendre la lecture si nécessaire
            if was_playing and self.main_playlist and self.current_index < len(self.main_playlist):
                current_song = self.main_playlist[self.current_index]
                pygame.mixer.music.load(current_song)
                pygame.mixer.music.play(start=current_pos)
                self._apply_volume()
            
            # Sauvegarder le nouveau périphérique
            self.current_audio_device = device_name
            
            # Mettre à jour la variable des radiobuttons si elle existe
            if hasattr(self, 'audio_device_var'):
                self.audio_device_var.set(device_name)
            
            self.save_config()
            
            self.status_bar.config(text=f"Périphérique changé: {device_name}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de changer le périphérique:\n{str(e)}")

    def _detect_current_audio_device(self):
        """Détecte le périphérique audio actuellement utilisé"""
        try:
            import pygame._sdl2.audio
            devices = pygame._sdl2.audio.get_audio_device_names()
            
            if devices:
                # Par défaut, prendre le premier périphérique (souvent le défaut du système)
                default_device = devices[0]
                self.current_audio_device = default_device.decode('utf-8') if isinstance(default_device, bytes) else default_device
                
        except Exception as e:
            print(f"Erreur détection périphérique audio: {e}")
            self.current_audio_device = "Périphérique par défaut"

    def show_stats_menu(self):
        """Affiche un menu avec les statistiques d'écoute"""
        try:
            # Calculer les statistiques actuelles
            self._update_current_song_stats()
            
            # Formater le temps total d'écoute
            total_time = self.stats['total_listening_time']
            hours = int(total_time // 3600)
            minutes = int((total_time % 3600) // 60)
            seconds = int(total_time % 60)
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                time_str = f"{minutes}m {seconds}s"
            else:
                time_str = f"{seconds}s"
            
            # Créer le menu déroulant
            stats_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                               activebackground='#4a8fe7', activeforeground='white',
                               relief='flat', bd=1)
            
            # Ajouter un titre
            stats_menu.add_command(label="📊 Statistiques d'écoute", state='disabled')
            stats_menu.add_separator()
            
            # Ajouter les statistiques
            stats_menu.add_command(label=f"🎵 Musiques lues: {self.stats['songs_played']}", state='disabled')
            stats_menu.add_command(label=f"⏱️ Temps d'écoute: {time_str}", state='disabled')
            stats_menu.add_command(label=f"🔍 Recherches: {self.stats['searches_count']}", state='disabled')
            
            stats_menu.add_separator()
            stats_menu.add_command(label="🗑️ Réinitialiser", command=self._reset_stats)
            
            # Afficher le menu à la position du bouton
            try:
                x = self.stats_button.winfo_rootx()
                y = self.stats_button.winfo_rooty() + self.stats_button.winfo_height()
                stats_menu.post(x, y)
            except:
                # Si erreur de positionnement, afficher au curseur
                stats_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher les statistiques:\n{str(e)}")

    def _reset_stats(self):
        """Remet à zéro toutes les statistiques"""
        if messagebox.askyesno("Réinitialiser les statistiques", 
                              "Êtes-vous sûr de vouloir remettre à zéro toutes les statistiques ?"):
            self.stats = {
                'songs_played': 0,
                'total_listening_time': 0.0,
                'searches_count': 0,
                'current_song_start_time': None,
                'current_song_listened_time': 0.0,
                'current_song_duration': 0.0,
                'played_songs': set()
            }
            self.save_config()
            self.status_bar.config(text="Statistiques réinitialisées")

    def _update_current_song_stats(self):
        """Met à jour les statistiques de la chanson en cours"""
        try:
            if (self.stats['current_song_start_time'] is not None and 
                self.main_playlist and 
                self.current_index < len(self.main_playlist)):
                
                current_song = self.main_playlist[self.current_index]
                
                # Calculer le temps écouté depuis le début de la chanson
                if not self.paused and pygame.mixer.music.get_busy():
                    elapsed_time = time.time() - self.stats['current_song_start_time']
                    self.stats['current_song_listened_time'] += elapsed_time
                    self.stats['total_listening_time'] += elapsed_time
                    self.stats['current_song_start_time'] = time.time()
                
                # Vérifier si la chanson a été écoutée à 70% ou plus
                if (self.stats['current_song_duration'] > 0 and 
                    self.stats['current_song_listened_time'] >= self.stats['current_song_duration'] * 0.7 and
                    current_song not in self.stats['played_songs']):
                    
                    self.stats['songs_played'] += 1
                    self.stats['played_songs'].add(current_song)
                    # Sauvegarder immédiatement quand une chanson est comptée comme lue
                    self.save_config()
                    
        except Exception as e:
            print(f"Erreur mise à jour stats: {e}")

    def _start_song_stats_tracking(self, song_path):
        """Démarre le suivi des statistiques pour une nouvelle chanson"""
        try:
            # Finaliser les stats de la chanson précédente
            self._update_current_song_stats()
            
            # Initialiser les stats pour la nouvelle chanson
            self.stats['current_song_start_time'] = time.time()
            self.stats['current_song_listened_time'] = 0.0
            
            # Obtenir la durée de la chanson
            try:
                import mutagen
                audio_file = mutagen.File(song_path)
                if audio_file is not None:
                    self.stats['current_song_duration'] = audio_file.info.length
                else:
                    self.stats['current_song_duration'] = 0.0
            except:
                # Si on ne peut pas obtenir la durée, utiliser la durée du player
                self.stats['current_song_duration'] = self.song_length
                
        except Exception as e:
            print(f"Erreur démarrage tracking stats: {e}")

    def _pause_song_stats_tracking(self):
        """Met en pause le suivi des statistiques"""
        try:
            if self.stats['current_song_start_time'] is not None:
                elapsed_time = time.time() - self.stats['current_song_start_time']
                self.stats['current_song_listened_time'] += elapsed_time
                self.stats['total_listening_time'] += elapsed_time
                self.stats['current_song_start_time'] = None
        except Exception as e:
            print(f"Erreur pause tracking stats: {e}")

    def _resume_song_stats_tracking(self):
        """Reprend le suivi des statistiques"""
        try:
            if self.stats['current_song_start_time'] is None:
                self.stats['current_song_start_time'] = time.time()
        except Exception as e:
            print(f"Erreur reprise tracking stats: {e}")

    def show_output_devices(self):
        """Affiche une fenêtre pour choisir le périphérique de sortie audio"""
        try:
            # Obtenir la liste des périphériques audio
            import pygame._sdl2.audio
            devices = pygame._sdl2.audio.get_audio_device_names()
            
            if not devices:
                messagebox.showinfo("Périphériques audio", "Aucun périphérique audio trouvé")
                return
            
            # Créer une fenêtre de sélection (style blanc comme la sélection multiple)
            device_window = tk.Toplevel(self.root)
            device_window.title("Périphérique de sortie")
            device_window.geometry("350x250")
            device_window.configure(bg='white')
            device_window.resizable(False, False)
            
            # Centrer la fenêtre
            device_window.transient(self.root)
            device_window.grab_set()
            
            # Label d'instruction
            instruction_label = tk.Label(
                device_window, 
                text="Sélectionnez un périphérique de sortie :",
                bg='white', 
                fg='black',
                font=('Arial', 10, 'bold')
            )
            instruction_label.pack(pady=15)
            
            # Frame pour la liste
            list_frame = tk.Frame(device_window, bg='white')
            list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
            
            # Listbox avec scrollbar
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            device_listbox = tk.Listbox(
                list_frame,
                yscrollcommand=scrollbar.set,
                bg='white',
                fg='black',
                selectbackground='#4a8fe7',
                selectforeground='white',
                font=('Arial', 9),
                relief='solid',
                bd=1
            )
            device_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=device_listbox.yview)
            
            # Ajouter les périphériques à la liste
            for device in devices:
                device_listbox.insert(tk.END, device.decode('utf-8') if isinstance(device, bytes) else device)
            
            # Frame pour les boutons
            button_frame = tk.Frame(device_window, bg='white')
            button_frame.pack(pady=15)
            
            def apply_device():
                selection = device_listbox.curselection()
                if selection:
                    selected_device = devices[selection[0]]
                    device_name = selected_device.decode('utf-8') if isinstance(selected_device, bytes) else selected_device
                    
                    try:
                        # Arrêter la musique actuelle
                        was_playing = pygame.mixer.music.get_busy() and not self.paused
                        current_pos = self.current_time if was_playing else 0
                        
                        # Réinitialiser pygame mixer avec le nouveau périphérique
                        pygame.mixer.quit()
                        pygame.mixer.init(devicename=selected_device, frequency=44100, size=-16, channels=2, buffer=4096)
                        
                        # Reprendre la lecture si nécessaire
                        if was_playing and self.main_playlist and self.current_index < len(self.main_playlist):
                            current_song = self.main_playlist[self.current_index]
                            pygame.mixer.music.load(current_song)
                            pygame.mixer.music.play(start=current_pos)
                            self._apply_volume()
                        
                        self.status_bar.config(text=f"Périphérique changé: {device_name}")
                        device_window.destroy()
                        
                    except Exception as e:
                        messagebox.showerror("Erreur", f"Impossible de changer le périphérique:\n{str(e)}")
                else:
                    messagebox.showwarning("Sélection", "Veuillez sélectionner un périphérique")
            
            def cancel():
                device_window.destroy()
            
            # Boutons (style blanc)
            apply_btn = tk.Button(
                button_frame,
                text="Appliquer",
                command=apply_device,
                bg='#4a8fe7',
                fg='white',
                activebackground='#5a9fd8',
                activeforeground='white',
                font=('Arial', 9),
                padx=20,
                relief='flat',
                bd=1
            )
            apply_btn.pack(side=tk.LEFT, padx=5)
            
            cancel_btn = tk.Button(
                button_frame,
                text="Annuler",
                command=cancel,
                bg='#e0e0e0',
                fg='black',
                activebackground='#d0d0d0',
                activeforeground='black',
                font=('Arial', 9),
                padx=20,
                relief='flat',
                bd=1
            )
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'accéder aux périphériques audio:\n{str(e)}")

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
                highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
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
            
            # Vérifier si cette position spécifique fait partie de la queue
            is_in_queue = (hasattr(self, 'queue_items') and current_song_index in self.queue_items)
            
            if show_numbers:
                # Configuration de la grille en 6 colonnes : trait queue, numéro, miniature, titre, durée, bouton
                item_frame.columnconfigure(0, minsize=4, weight=0)   # Trait queue (si applicable)
                item_frame.columnconfigure(1, minsize=10, weight=0)  # Numéro
                item_frame.columnconfigure(2, minsize=80, weight=0)  # Miniature
                item_frame.columnconfigure(3, weight=1)              # Titre
                item_frame.columnconfigure(4, minsize=60, weight=0)  # Durée
                item_frame.columnconfigure(5, minsize=40, weight=0)  # Bouton
                item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
                
                # Trait vertical queue (colonne 0) - seulement si la musique est dans la queue
                if is_in_queue:
                    queue_indicator = tk.Frame(
                        item_frame,
                        bg='black',  # Trait noir
                        width=3
                    )
                    queue_indicator.grid(row=0, column=0, sticky='ns', padx=(2, 2), pady=2)
                    queue_indicator.grid_propagate(False)
                
                # Numéro de la chanson (colonne 1)
                number_label = tk.Label(
                    item_frame,
                    text=str(current_song_index + 1),  # +1 pour commencer à 1 au lieu de 0
                    bg='#4a4a4a',
                    fg='white',
                    font=('TkDefaultFont', 10, 'bold'),
                    anchor='center'
                )
                number_label.grid(row=0, column=1, sticky='nsew', padx=(2, 2), pady=2)
                
                # Miniature (colonne 2)
                thumbnail_label = tk.Label(
                    item_frame,
                    bg='#4a4a4a',
                    width=10,
                    height=3,
                    anchor='center'
                )
                thumbnail_label.grid(row=0, column=2, sticky='nsew', padx=(5, 10), pady=8)
                thumbnail_label.grid_propagate(False)
                
                col_offset = 2  # Décalage pour les colonnes suivantes (trait + numéro)
            else:
                # Configuration de la grille en 5 colonnes : trait queue, miniature, titre, durée, bouton
                item_frame.columnconfigure(0, minsize=4, weight=0)   # Trait queue (si applicable)
                item_frame.columnconfigure(1, minsize=80, weight=0)  # Miniature
                item_frame.columnconfigure(2, weight=1)              # Titre
                item_frame.columnconfigure(3, minsize=60, weight=0)  # Durée
                item_frame.columnconfigure(4, minsize=40, weight=0)  # Bouton
                item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
                
                # Trait vertical queue (colonne 0) - seulement si la musique est dans la queue
                if is_in_queue:
                    queue_indicator = tk.Frame(
                        item_frame,
                        bg='black',  # Trait noir
                        width=3
                    )
                    queue_indicator.grid(row=0, column=0, sticky='ns', padx=(2, 2), pady=2)
                    queue_indicator.grid_propagate(False)
                
                # Miniature (colonne 1)
                thumbnail_label = tk.Label(
                    item_frame,
                    bg='#4a4a4a',
                    width=10,
                    height=3,
                    anchor='center'
                )
                thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(10, 10), pady=8)
                thumbnail_label.grid_propagate(False)
                
                col_offset = 1  # Décalage pour le trait queue
            
            # Charger la miniature
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._load_image_thumbnail(thumbnail_path, thumbnail_label)
            else:
                self._load_mp3_thumbnail(filepath, thumbnail_label)

            # Frame pour le texte (titre + métadonnées) (colonne 1 + col_offset)
            text_frame = tk.Frame(item_frame, bg='#4a4a4a')
            text_frame.grid(row=0, column=1+col_offset, sticky='nsew', padx=(0, 10), pady=8)
            text_frame.columnconfigure(0, weight=1)
            
            # Titre principal
            truncated_title = self._truncate_text_for_display(filename, max_width_pixels=170, font_family='TkDefaultFont', font_size=9)
            title_label = tk.Label(
                text_frame,
                text=truncated_title,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left'
            )
            title_label.grid(row=0, column=0, sticky='ew', pady=(2, 0))
            
            # Métadonnées (artiste • album • date)
            artist, album = self._get_audio_metadata(filepath)
            metadata_text = self._format_artist_album_info(artist, album, filepath)
            
            if metadata_text:
                metadata_label = tk.Label(
                    text_frame,
                    text=metadata_text,
                    bg='#4a4a4a',
                    fg='#cccccc',
                    font=('TkDefaultFont', 8),
                    anchor='w',
                    justify='left'
                )
                metadata_label.grid(row=1, column=0, sticky='ew', pady=(0, 2))
            
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
                font=('TkDefaultFont', 8),
                takefocus=0
            )
            delete_btn.grid(row=0, column=3+col_offset, sticky='ns', padx=(0, 10), pady=8)
            delete_btn.bind("<Double-1>", lambda event, f=filepath, frame=item_frame, idx=current_song_index: self._remove_main_playlist_item(f, frame, event, idx))
            create_tooltip(delete_btn, "Supprimer de la playlist\nDouble-clic pour retirer cette chanson de la playlist")
            
            item_frame.filepath = filepath
            item_frame.song_index = current_song_index  # Stocker l'index réel
            
            def on_playlist_item_click(event):
                # Vérifier si Ctrl est enfoncé pour ouvrir sur YouTube
                if event.state & 0x4:  # Ctrl est enfoncé
                    self.open_music_on_youtube(filepath)
                    return
                
                # Initialiser le drag
                self.drag_drop_handler.setup_drag_start(event, item_frame)
                
                # Vérifier si Shift est enfoncé pour la sélection multiple
                if event.state & 0x1:  # Shift est enfoncé
                    self.shift_selection_active = True
                    self.toggle_item_selection(filepath, item_frame)
                else:
                    # Clic normal sans Shift - ne pas effacer la sélection si elle existe
                    pass
            
            def on_playlist_item_double_click(event):
                # Vérifier si Shift est enfoncé ou si on est en mode sélection - ne rien faire
                if event.state & 0x1 or self.selected_items:  # Shift est enfoncé ou mode sélection
                    pass
                else:
                    # Comportement normal : jouer la musique
                    self.current_index = current_song_index  # Utiliser l'index réel stocké
                    self.play_track()
                
            # Bindings pour clics simples et doubles
            item_frame.bind("<Button-1>", on_playlist_item_click)
            item_frame.bind("<Double-1>", on_playlist_item_double_click)
            thumbnail_label.bind("<Button-1>", on_playlist_item_click)
            thumbnail_label.bind("<Double-1>", on_playlist_item_double_click)
            text_frame.bind("<Button-1>", on_playlist_item_click)
            text_frame.bind("<Double-1>", on_playlist_item_double_click)
            title_label.bind("<Button-1>", on_playlist_item_click)
            title_label.bind("<Double-1>", on_playlist_item_double_click)
            if metadata_text:  # Ajouter le binding pour metadata_label s'il existe
                metadata_label.bind("<Button-1>", on_playlist_item_click)
                metadata_label.bind("<Double-1>", on_playlist_item_double_click)
            duration_label.bind("<Button-1>", on_playlist_item_click)
            duration_label.bind("<Double-1>", on_playlist_item_double_click)
            
            # Ajouter le binding pour le numéro si il existe
            if show_numbers:
                number_label.bind("<Button-1>", on_playlist_item_click)
                number_label.bind("<Double-1>", on_playlist_item_double_click)
            
            # Clic droit pour ouvrir le menu de sélection ou placer après la chanson en cours
            def on_playlist_item_right_click(event):
                # Si on a des éléments sélectionnés, ouvrir le menu de sélection
                if self.selected_items:
                    self.show_selection_menu(event)
                else:
                    # Comportement normal : placer après la chanson en cours
                    self._play_after_current(filepath)
            
            item_frame.bind("<Button-3>", on_playlist_item_right_click)
            thumbnail_label.bind("<Button-3>", on_playlist_item_right_click)
            text_frame.bind("<Button-3>", on_playlist_item_right_click)
            title_label.bind("<Button-3>", on_playlist_item_right_click)
            if metadata_text:  # Ajouter le binding pour metadata_label s'il existe
                metadata_label.bind("<Button-3>", on_playlist_item_right_click)
            duration_label.bind("<Button-3>", on_playlist_item_right_click)
            
            if show_numbers:
                number_label.bind("<Button-3>", on_playlist_item_right_click)
            
            # Configuration du drag-and-drop
            self.drag_drop_handler.setup_drag_drop(
                item_frame, 
                file_path=filepath, 
                item_type="playlist_item"
            )
            
            # Tooltip pour expliquer les interactions
            tooltip_text = "Musique de la playlist principale\nDouble-clic: Jouer cette musique\nCtrl + Clic: Ouvrir sur YouTube\nShift + Clic: Sélection multiple\nClic droit: Placer après la chanson en cours"
            create_tooltip(text_frame, tooltip_text)
            create_tooltip(title_label, tooltip_text)
            if metadata_text:  # Ajouter le tooltip pour metadata_label s'il existe
                create_tooltip(metadata_label, tooltip_text)
            create_tooltip(thumbnail_label, tooltip_text)

        except Exception as e:
            print(f"Erreur affichage playlist item: {e}")
    
    def select_playlist_item(self, item_frame=None, index=None, auto_scroll=True):
        """Met en surbrillance l'élément sélectionné dans la playlist
        
        Args:
            item_frame: Frame de l'élément à sélectionner
            index: Index de l'élément à sélectionner (alternatif à item_frame)
            auto_scroll: Si True, fait défiler automatiquement vers l'élément (défaut: True)
        """
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
            
            # Faire défiler avec animation pour que l'élément soit visible (seulement si auto_scroll=True)
            if auto_scroll:
                try:
                    container_height = self.playlist_container.winfo_height()
                    if container_height > 0:
                        target_position = item_frame.winfo_y() / container_height
                        self._smooth_scroll_to_position(target_position)
                    else:
                        # Fallback si la hauteur n'est pas disponible
                        self.playlist_canvas.yview_moveto(item_frame.winfo_y() / self.playlist_container.winfo_height())
                except Exception as e:
                    # Fallback en cas d'erreur
                    print(f"Erreur animation scroll: {e}")
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
    
    def _smooth_scroll_to_position(self, target_position, duration=500):
        """Anime le scroll vers une position cible avec une courbe ease-in-out"""
        # Annuler toute animation en cours
        if self.scroll_animation_id:
            self.root.after_cancel(self.scroll_animation_id)
            self.scroll_animation_id = None
        
        # Si une animation est déjà en cours, l'arrêter
        if self.scroll_animation_active:
            self.scroll_animation_active = False
        
        # Obtenir la position actuelle du scroll
        try:
            current_top, current_bottom = self.playlist_canvas.yview()
            start_position = current_top
        except:
            # En cas d'erreur, faire un scroll instantané
            self.playlist_canvas.yview_moveto(target_position)
            return
        
        # Si on est déjà à la bonne position, ne rien faire
        if abs(start_position - target_position) < 0.001:
            return
        
        # Paramètres de l'animation
        start_time = time.time() * 1000  # Temps en millisecondes
        distance = target_position - start_position
        
        self.scroll_animation_active = True
        
        def ease_in_out_cubic(t):
            """Fonction d'easing cubic ease-in-out"""
            if t < 0.5:
                return 4 * t * t * t
            else:
                return 1 - pow(-2 * t + 2, 3) / 2
        
        def animate_step():
            if not self.scroll_animation_active:
                return
            
            current_time = time.time() * 1000
            elapsed = current_time - start_time
            progress = min(elapsed / duration, 1.0)
            
            # Appliquer la courbe d'easing
            eased_progress = ease_in_out_cubic(progress)
            current_position = start_position + (distance * eased_progress)
            
            # Appliquer la position
            try:
                self.playlist_canvas.yview_moveto(current_position)
            except:
                # En cas d'erreur, arrêter l'animation
                self.scroll_animation_active = False
                return
            
            # Continuer l'animation si pas terminée
            if progress < 1.0:
                self.scroll_animation_id = self.root.after(16, animate_step)  # ~60 FPS
            else:
                self.scroll_animation_active = False
                self.scroll_animation_id = None
        
        # Démarrer l'animation
        animate_step()
    
    def _start_title_animation(self, full_title):
        """Démarre l'animation de défilement du titre si nécessaire"""
        # Arrêter toute animation en cours
        self._stop_title_animation()
        
        # Vérifier si le titre est tronqué
        truncated_title = tools._truncate_text_for_display(self, full_title, max_width_pixels=400, font_family='Helvetica', font_size=12)
        
        # Si le titre n'est pas tronqué, pas besoin d'animation
        if not truncated_title.endswith("..."):
            self.song_label.config(text=truncated_title)
            return
        
        # Initialiser les variables d'animation
        self.title_full_text = full_title
        self.title_scroll_position = 0
        self.title_pause_counter = 60  # Pause initiale plus longue (3 secondes à 20fps)
        self.title_animation_active = True
        
        # Afficher le titre tronqué au début
        self.song_label.config(text=truncated_title)
        
        # Démarrer l'animation
        self._animate_title_step()
    
    def _stop_title_animation(self):
        """Arrête l'animation du titre"""
        if self.title_animation_id:
            self.root.after_cancel(self.title_animation_id)
            self.title_animation_id = None
        self.title_animation_active = False
    
    def _animate_title_step(self):
        """Une étape de l'animation du titre"""
        if not self.title_animation_active:
            return
        
        # Paramètres d'animation
        max_width_pixels = 400
        pause_cycles = 80  # Pause plus longue entre les cycles (4 secondes à 20fps)
        
        # Si on est en pause
        if self.title_pause_counter > 0:
            self.title_pause_counter -= 1
            self.title_animation_id = self.root.after(50, self._animate_title_step)  # 20 FPS pendant la pause
            return
        
        # Calculer le texte visible actuel
        visible_text = self._get_scrolled_title_text(self.title_full_text, self.title_scroll_position, max_width_pixels)
        
        # Mettre à jour le label
        self.song_label.config(text=visible_text)
        
        # Avancer la position de défilement
        self.title_scroll_position += 1
        
        # Si on a fait un tour complet, recommencer avec une pause
        if self.title_scroll_position >= len(self.title_full_text) + 8:  # +8 pour les espaces ajoutés
            self.title_scroll_position = 0
            self.title_pause_counter = pause_cycles
            # Afficher le titre tronqué normal pendant la pause
            truncated_title = tools._truncate_text_for_display(self, self.title_full_text, max_width_pixels=400, font_family='Helvetica', font_size=12)
            self.song_label.config(text=truncated_title)
        
        # Programmer la prochaine étape
        self.title_animation_id = self.root.after(100, self._animate_title_step)  # 10 FPS pour le défilement
    
    def _get_scrolled_title_text(self, full_text, scroll_pos, max_width_pixels):
        """Génère le texte visible avec défilement à la position donnée"""
        import tkinter.font as tkFont
        
        # Créer la police pour mesurer
        font = tkFont.Font(family='Helvetica', size=12)
        ellipsis_width = font.measure("...")
        available_width = max_width_pixels - ellipsis_width
        
        # Créer le texte étendu pour le défilement circulaire
        # On ajoute plus d'espaces pour créer une transition fluide avec plus d'espace
        extended_text = full_text + "        " + full_text
        
        # S'assurer que scroll_pos ne dépasse pas la longueur du texte étendu
        if scroll_pos >= len(extended_text):
            scroll_pos = 0
        
        # Commencer à partir de la position de défilement
        scrolled_text = extended_text[scroll_pos:]
        
        # Si on n'a plus assez de texte, recommencer depuis le début
        if len(scrolled_text) < 10:  # Seuil minimum pour éviter les fins de texte
            scrolled_text = extended_text
        
        # Trouver la longueur maximale qui tient dans l'espace disponible
        visible_text = ""
        for i, char in enumerate(scrolled_text):
            test_text = scrolled_text[:i+1]
            if font.measure(test_text) > available_width:
                break
            visible_text = test_text
        
        # Si on n'a pas pu ajouter au moins un caractère, retourner juste "..."
        if not visible_text:
            return "..."
        
        return visible_text + "..."
    
    def toggle_item_selection(self, filepath, frame):
        """Ajoute ou retire un élément de la sélection multiple"""
        if filepath in self.selected_items:
            # Désélectionner
            self.selected_items.remove(filepath)
            if filepath in self.selected_items_order:
                self.selected_items_order.remove(filepath)
            if filepath in self.selection_frames:
                del self.selection_frames[filepath]
            
            # Vérifier que l'index est valide avant d'accéder à la playlist
            if (self.main_playlist and 
                0 <= self.current_index < len(self.main_playlist) and 
                filepath == self.main_playlist[self.current_index]):
                self._set_item_colors(frame, COLOR_SELECTED)
            else:
                self._set_item_colors(frame, '#4a4a4a')  # Couleur normale
        else:
            # Sélectionner
            self.selected_items.add(filepath)
            self.selected_items_order.append(filepath)  # Maintenir l'ordre de sélection
            self.selection_frames[filepath] = frame
            self._set_item_colors(frame, '#ff8c00')  # Couleur orange pour la sélection multiple
        
        # Mettre à jour l'affichage du nombre d'éléments sélectionnés
        self.update_selection_display()
        # print(self.selected_items_order)  # Afficher la liste ordonnée au lieu du set
    
    def clear_selection(self):
        """Efface toute la sélection multiple"""
        for filepath in list(self.selected_items):
            if filepath in self.selection_frames:
                frame = self.selection_frames[filepath]
                # Vérifier que l'index est valide avant d'accéder à la playlist
                if (self.main_playlist and 
                    0 <= self.current_index < len(self.main_playlist) and 
                    filepath == self.main_playlist[self.current_index]):
                    self._set_item_colors(frame, COLOR_SELECTED)
                else:
                    self._set_item_colors(frame, '#4a4a4a')  # Couleur normale
        
        self.selected_items.clear()
        self.selected_items_order.clear()  # Vider aussi la liste ordonnée
        self.selection_frames.clear()
        self.shift_selection_active = False
        
        # Mettre à jour l'affichage du nombre d'éléments sélectionnés
        self.update_selection_display()
    
    def show_selection_menu(self, event):
        """Affiche un menu contextuel pour sélectionner les playlists"""
        if not self.selected_items:
            return
        
        # Vérifier si on a des vidéos YouTube non téléchargées dans la sélection
        has_youtube_videos = any(item.startswith("https://www.youtube.com/watch?v=") for item in self.selected_items)
        
        # Créer le menu contextuel
        context_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                              activebackground='#4a8fe7', activeforeground='white',
                              relief='flat', bd=1)
        
        # Ajouter un titre avec le nombre d'éléments sélectionnés
        title_text = f"Télécharger et ajouter {len(self.selected_items)} élément(s) à:" if has_youtube_videos else f"Ajouter {len(self.selected_items)} élément(s) à:"
        context_menu.add_command(label=title_text, state='disabled')
        context_menu.add_separator()
        
        # Nouvelles options pour la queue et la main playlist
        if not has_youtube_videos:  # Ces options ne fonctionnent que pour les fichiers locaux
            context_menu.add_command(
                label="📄 Ajouter à la liste de lecture",
                command=self.add_selection_to_main_playlist
            )
            context_menu.add_command(
                label="⏭️ Lire ensuite",
                command=self.add_selection_to_queue_first
            )
            context_menu.add_command(
                label="⏰ Lire bientôt", 
                command=self.add_selection_to_queue_last
            )
            context_menu.add_separator()
        
        # Ajouter les playlists existantes (sauf Main Playlist)
        for playlist_name in self.playlists.keys():
            if playlist_name != "Main Playlist":
                if has_youtube_videos:
                    context_menu.add_command(
                        label=playlist_name,
                        command=lambda p=playlist_name: self.download_and_add_to_multiple_playlists([p])
                    )
                else:
                    context_menu.add_command(
                        label=playlist_name,
                        command=lambda p=playlist_name: self.add_to_multiple_playlists([p])
                    )
        
        # Ajouter une option pour créer une nouvelle playlist
        context_menu.add_separator()
        context_menu.add_command(
            label="Créer nouvelle playlist...",
            command=lambda: self.create_new_playlist_from_selection(has_youtube_videos)
        )
        
        # Ajouter une option pour annuler la sélection
        context_menu.add_separator()
        context_menu.add_command(
            label="Annuler la sélection",
            command=self.clear_selection
        )
        
        # Afficher le menu à la position de la souris
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def add_selection_to_main_playlist(self):
        """Ajoute tous les éléments sélectionnés à la fin de la main playlist dans l'ordre"""
        if not self.selected_items:
            return
            
        added_count = 0
        
        for filepath in self.selected_items_order:
            # Vérifier que c'est bien un fichier local (pas une URL YouTube)
            if not filepath.startswith("https://"):
                if self.add_to_main_playlist(filepath, show_status=False):
                    added_count += 1
        
        # Rafraîchir l'affichage
        self._refresh_playlist_display()
        
        # Afficher le statut
        if added_count > 0:
            self.status_bar.config(text=f"Ajouté {added_count} élément(s) à la liste de lecture")
        else:
            self.status_bar.config(text="Aucun élément n'a été ajouté (déjà présents)")
            
        # Effacer la sélection
        self.clear_selection()
        
        # Marquer que la main playlist ne provient pas d'une playlist
        self.main_playlist_from_playlist = False
    
    def add_selection_to_queue_first(self):
        """Ajoute tous les éléments sélectionnés au début de la queue (lire ensuite)"""
        if not self.selected_items:
            return
            
        added_count = 0
        
        # Position d'insertion : juste après la chanson actuelle
        if len(self.main_playlist) == 0:
            # Pas de playlist, ajouter normalement
            for filepath in self.selected_items_order:
                if not filepath.startswith("https://"):
                    if self.add_to_main_playlist(filepath, show_status=False):
                        added_count += 1
        else:
            insert_position = self.current_index + 1
            
            # Initialiser queue_items si nécessaire
            if not hasattr(self, 'queue_items'):
                self.queue_items = set()
            
            # Ajouter chaque fichier dans l'ordre à la position d'insertion
            for i, filepath in enumerate(self.selected_items_order):
                if not filepath.startswith("https://"):
                    # Ajouter à la main playlist s'il n'y est pas déjà
                    if filepath not in self.main_playlist:
                        # Insérer à la position courante
                        current_insert_pos = insert_position + i
                        self.main_playlist.insert(current_insert_pos, filepath)
                        
                        # Mettre à jour les indices de la queue (décaler ceux qui viennent après)
                        updated_queue = set()
                        for queue_index in self.queue_items:
                            if queue_index >= current_insert_pos:
                                updated_queue.add(queue_index + 1)
                            else:
                                updated_queue.add(queue_index)
                        self.queue_items = updated_queue
                        
                        # Ajouter cette position à la queue
                        self.queue_items.add(current_insert_pos)
                        added_count += 1
                        
                        # Ajuster l'index courant si nécessaire
                        if current_insert_pos <= self.current_index:
                            self.current_index += 1
                    else:
                        # Le fichier existe déjà, trouver sa position et l'ajouter à la queue
                        existing_index = self.main_playlist.index(filepath)
                        self.queue_items.add(existing_index)
        
        # Rafraîchir l'affichage
        self._refresh_playlist_display()
        
        # Afficher le statut
        if added_count > 0:
            self.status_bar.config(text=f"Ajouté {added_count} élément(s) en queue (lire ensuite)")
        else:
            self.status_bar.config(text="Éléments ajoutés à la queue")
            
        # Effacer la sélection
        self.clear_selection()
        
        # Marquer que la main playlist ne provient pas d'une playlist
        self.main_playlist_from_playlist = False
    
    def add_selection_to_queue_last(self):
        """Ajoute tous les éléments sélectionnés à la fin de la queue (lire bientôt)"""
        if not self.selected_items:
            return
            
        added_count = 0
        
        # Initialiser queue_items si nécessaire
        if not hasattr(self, 'queue_items'):
            self.queue_items = set()
        
        # Trouver la dernière position de la queue ou utiliser la fin de la playlist
        if self.queue_items:
            # Trouver l'index le plus élevé dans la queue
            last_queue_position = max(self.queue_items) + 1
        else:
            # Pas de queue existante, insérer après la chanson courante
            last_queue_position = self.current_index + 1 if len(self.main_playlist) > 0 else 0
        
        # Assurer que la position est dans les limites
        last_queue_position = min(last_queue_position, len(self.main_playlist))
        
        # Ajouter chaque fichier à la fin de la queue
        for i, filepath in enumerate(self.selected_items_order):
            if not filepath.startswith("https://"):
                # Ajouter à la main playlist s'il n'y est pas déjà
                if filepath not in self.main_playlist:
                    # Insérer à la position de fin de queue
                    current_insert_pos = last_queue_position + i
                    self.main_playlist.insert(current_insert_pos, filepath)
                    
                    # Mettre à jour les indices de la queue (décaler ceux qui viennent après)
                    updated_queue = set()
                    for queue_index in self.queue_items:
                        if queue_index >= current_insert_pos:
                            updated_queue.add(queue_index + 1)
                        else:
                            updated_queue.add(queue_index)
                    self.queue_items = updated_queue
                    
                    # Ajouter cette position à la queue
                    self.queue_items.add(current_insert_pos)
                    added_count += 1
                    
                    # Ajuster l'index courant si nécessaire
                    if current_insert_pos <= self.current_index:
                        self.current_index += 1
                else:
                    # Le fichier existe déjà, trouver sa position et l'ajouter à la queue
                    existing_index = self.main_playlist.index(filepath)
                    self.queue_items.add(existing_index)
        
        # Rafraîchir l'affichage
        self._refresh_playlist_display()
        
        # Afficher le statut
        if added_count > 0:
            self.status_bar.config(text=f"Ajouté {added_count} élément(s) en queue (lire bientôt)")
        else:
            self.status_bar.config(text="Éléments ajoutés à la queue")
            
        # Effacer la sélection
        self.clear_selection()
        
        # Marquer que la main playlist ne provient pas d'une playlist
        self.main_playlist_from_playlist = False
    
    def create_new_playlist_from_selection(self, has_youtube_videos):
        """Demande le nom d'une nouvelle playlist et y ajoute la sélection"""
        from tkinter import simpledialog
        
        playlist_name = simpledialog.askstring(
            "Nouvelle playlist",
            "Nom de la nouvelle playlist:",
            parent=self.root
        )
        
        if playlist_name and playlist_name.strip():
            playlist_name = playlist_name.strip()
            if has_youtube_videos:
                self.download_and_add_to_multiple_playlists([playlist_name])
            else:
                self.add_to_multiple_playlists([playlist_name])
    
    def update_selection_display(self):
        """Met à jour l'affichage du nombre d'éléments sélectionnés"""
        if hasattr(self, 'selection_label'):
            if self.selected_items:
                count = len(self.selected_items)
                text = f"{count} élément{'s' if count > 1 else ''} sélectionné{'s' if count > 1 else ''}"
                self.selection_label.config(text=text)
            else:
                self.selection_label.config(text="")
    
    def add_to_multiple_playlists(self, playlist_names):
        """Ajoute les éléments sélectionnés à plusieurs playlists"""
        if not self.selected_items or not playlist_names:
            return
        
        total_added = 0
        
        for playlist_name in playlist_names:
            # Créer la playlist si elle n'existe pas
            if playlist_name not in self.playlists:
                self.playlists[playlist_name] = []
            
            # Ajouter les éléments à cette playlist
            added_count = 0
            for filepath in self.selected_items:
                if filepath not in self.playlists[playlist_name]:
                    self.playlists[playlist_name].append(filepath)
                    added_count += 1
            
            total_added += added_count
        
        # Sauvegarder les playlists
        self.save_playlists()
        
        # Afficher un message de confirmation
        if len(playlist_names) == 1:
            self.status_bar.config(text=f"{total_added} musique(s) ajoutée(s) à '{playlist_names[0]}'")
        else:
            self.status_bar.config(text=f"{total_added} musique(s) ajoutée(s) à {len(playlist_names)} playlist(s)")
        
        # Ne pas effacer la sélection pour permettre d'ajouter à d'autres playlists
    
    def download_and_add_to_multiple_playlists(self, playlist_names):
        """Télécharge les vidéos YouTube sélectionnées et les ajoute à plusieurs playlists"""
        if not self.selected_items or not playlist_names:
            return
        
        # Créer les playlists si elles n'existent pas
        for playlist_name in playlist_names:
            if playlist_name not in self.playlists:
                self.playlists[playlist_name] = []
        
        # Télécharger chaque vidéo YouTube et l'ajouter aux playlists
        youtube_items = [item for item in self.selected_items if item.startswith("https://www.youtube.com/watch?v=")]
        
        for video_url in youtube_items:
            # Lancer le téléchargement
            threading.Thread(
                target=self._download_and_add_to_playlists,
                args=(video_url, playlist_names),
                daemon=True
            ).start()
        
        # Afficher un message de confirmation
        if len(playlist_names) == 1:
            self.status_bar.config(text=f"Téléchargement de {len(youtube_items)} vidéo(s) pour '{playlist_names[0]}'...")
        else:
            self.status_bar.config(text=f"Téléchargement de {len(youtube_items)} vidéo(s) pour {len(playlist_names)} playlist(s)...")
        
        # Ne pas effacer la sélection pour permettre d'ajouter à d'autres playlists
    
    def _download_and_add_to_playlists(self, video_url, playlist_names):
        """Télécharge une vidéo et l'ajoute à plusieurs playlists"""
        try:
            # Télécharger la vidéo (utiliser la logique existante)
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                # Construire le chemin du fichier téléchargé
                filename = ydl.prepare_filename(info)
                # Remplacer l'extension par .mp3
                audio_path = os.path.splitext(filename)[0] + '.mp3'
                
                if os.path.exists(audio_path):
                    # Ajouter à toutes les playlists spécifiées
                    for playlist_name in playlist_names:
                        if audio_path not in self.playlists[playlist_name]:
                            self.playlists[playlist_name].append(audio_path)
                    
                    # Sauvegarder les playlists
                    self.save_playlists()
                    
                    # Mettre à jour le compteur de fichiers téléchargés
                    self.root.after(0, self._count_downloaded_files)
                    self.root.after(0, self._update_downloads_button)
                    
                    # Rafraîchir l'affichage si nécessaire
                    self.root.after(0, self.load_downloaded_files)
                    
        except Exception as e:
            print(f"Erreur téléchargement pour playlists multiples: {e}")
    
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
            self.add_to_main_playlist(filepath, show_status=False)
        
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
        return services.downloading.download_youtube_selection(self, youtube_urls, target_playlist)

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

    
    def _remove_main_playlist_item(self, filepath, frame, event=None, song_index=None):
        """Supprime un élément de la main playlist"""
        try:
            # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
            if event and (event.state & 0x4):  # Ctrl est enfoncé
                self._delete_from_downloads(filepath, frame)
            else:
                # Suppression normale de la playlist
                # Utiliser l'index fourni ou trouver l'index de l'élément à supprimer
                if song_index is not None:
                    index = song_index
                else:
                    index = self.main_playlist.index(filepath)
                
                # Supprimer de la liste
                self.main_playlist.pop(index)
                
                # Mettre à jour la queue : supprimer l'index supprimé et décrémenter les indices supérieurs
                if hasattr(self, 'queue_items'):
                    # Supprimer l'index supprimé s'il était dans la queue
                    if index in self.queue_items:
                        self.queue_items.discard(index)
                    
                    # Décrémenter tous les indices supérieurs à celui supprimé
                    updated_queue = set()
                    for queue_index in self.queue_items:
                        if queue_index > index:
                            updated_queue.add(queue_index - 1)  # Décrémenter l'index
                        else:
                            updated_queue.add(queue_index)  # Garder tel quel
                    self.queue_items = updated_queue
                
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
                
                # Rafraîchir complètement l'affichage de la playlist pour éviter les incohérences
                self._refresh_playlist_display()
                
                self.status_bar.config(text=f"Piste supprimée de la main playlist")
        except ValueError:
            pass
        except Exception as e:
            self.status_bar.config(text=f"Erreur suppression: {e}")

    def _delete_from_downloads(self, filepath, frame):
        """Supprime définitivement un fichier du dossier downloads"""
        try:
            if os.path.exists(filepath):
                # Vérifier si le fichier est actuellement en cours de lecture
                is_currently_playing = (filepath in self.main_playlist and 
                                      self.current_index < len(self.main_playlist) and 
                                      self.main_playlist[self.current_index] == filepath)
                
                if is_currently_playing:
                    # Arrêter la lecture et libérer le fichier
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                
                # Supprimer le fichier audio
                os.remove(filepath)
                
                # Supprimer les miniatures associées si elles existent
                base_path = os.path.splitext(filepath)[0]
                for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    thumbnail_path = base_path + ext
                    if os.path.exists(thumbnail_path):
                        os.remove(thumbnail_path)
                
                # Supprimer l'URL YouTube des métadonnées
                self.remove_youtube_url_metadata(filepath)
                
                # Supprimer de la playlist
                if filepath in self.main_playlist:
                    index = self.main_playlist.index(filepath)
                    self.main_playlist.remove(filepath)
                    
                    # Mettre à jour l'index courant si nécessaire
                    if index < self.current_index:
                        self.current_index -= 1
                    elif index == self.current_index:
                        # Le fichier en cours a été supprimé, passer au suivant
                        if len(self.main_playlist) > 0:
                            # Ajuster l'index si on est à la fin de la playlist
                            if self.current_index >= len(self.main_playlist):
                                self.current_index = len(self.main_playlist) - 1
                            # Jouer la chanson suivante (ou la précédente si on était à la fin)
                            self.play_track()
                        else:
                            # Plus de chansons dans la playlist
                            self.current_index = 0
                            self._show_current_song_thumbnail()
                            self.status_bar.config(text="Playlist vide")
                
                # Supprimer de toutes les playlists
                for playlist_name, playlist_songs in self.playlists.items():
                    if filepath in playlist_songs:
                        playlist_songs.remove(filepath)
                
                # Sauvegarder les playlists
                self.save_playlists()
                
                # Détruire l'élément de l'interface
                frame.destroy()
                
                # Mettre à jour le compteur
                file_services._count_downloaded_files(self)
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
            
            # Enlever cette musique de la queue si elle y est
            if (hasattr(self, 'queue_items') and 
                self.current_index in self.queue_items):
                self.queue_items.discard(self.current_index)
            
            # Démarrer le suivi des statistiques pour cette chanson
            self._start_song_stats_tracking(song)
            
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
            
            # Mettre en surbrillance la piste courante dans la playlist (sans scrolling automatique)
            self.select_playlist_item(index=self.current_index, auto_scroll=False)
            
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

            # Obtenir le nom du fichier sans extension
            song_name = os.path.basename(song)[:-4] if os.path.basename(song).lower().endswith('.mp3') else os.path.basename(song)
            
            # Obtenir les métadonnées
            artist, album = self._get_audio_metadata(song)
            metadata_text = self._format_artist_album_info(artist, album, song)
            
            # Démarrer l'animation du titre (seulement le titre)
            self._start_title_animation(song_name)
            
            # Mettre à jour les métadonnées séparément
            if hasattr(self, 'song_metadata_label'):
                self.song_metadata_label.config(text=metadata_text)

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
        # Annuler la recherche précédente si elle est en cours
        if self.is_searching:
            self.search_cancelled = True
            # Nettoyer immédiatement les résultats pour éviter les erreurs de widgets
            self._clear_results()
            # Attendre un court moment pour que le thread précédent se termine
            self.root.after(200, lambda: self._start_new_search())
            return
        
        self._start_new_search()
    
    def _start_new_search(self):
        """Démarre une nouvelle recherche après avoir annulé la précédente"""
        query = self.youtube_entry.get().strip()
        if not query:
            # Si la recherche est vide, afficher la miniature
            self._clear_results()
            self._show_current_song_thumbnail()
            return
        
        # Incrémenter le compteur de recherches
        self.stats['searches_count'] += 1
        
        # Enregistrer le temps de début de recherche
        self.search_start_time = time.time()
        
        # Nouvelle recherche - réinitialiser les compteurs et flags
        self.search_cancelled = False
        self.current_search_query = query
        self.search_results_count = 0
        self.is_loading_more = False
        self.current_search_batch = 1
        self.all_search_results = []  # Stocker tous les résultats filtrés
        self.all_raw_search_results = []  # Stocker tous les résultats bruts
        
        # Réinitialiser le compteur de résultats
        if hasattr(self, 'results_counter_label'):
            self.results_counter_label.config(text="")
        
        # Effacer les résultats précédents
        self._clear_results()
        self.search_list = []
        self.status_bar.config(text="Recherche en cours...")
        self.root.update()
        
        self.is_searching = True
        
        # Lancer une recherche initiale de 10 résultats
        self.current_search_thread = threading.Thread(target=self._perform_initial_search, args=(query,), daemon=True)
        self.current_search_thread.start()

    def _perform_initial_search(self, query):
        """Effectue une recherche initiale de 10 résultats seulement"""
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.search_cancelled:
                return
                
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'max_downloads': self.initial_search_count,  # Chercher seulement 10 résultats initialement
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                # Vérifier l'annulation avant la recherche
                if self.search_cancelled:
                    return
                    
                # Recherche initiale de 10 résultats
                results = ydl.extract_info(f"ytsearch{self.initial_search_count}:{query}", download=False)
                
                # Vérifier l'annulation après la recherche
                if self.search_cancelled:
                    return
                
                if not results or 'entries' not in results:
                    if not self.search_cancelled:
                        self.root.after(0, lambda: self._safe_status_update("Aucun résultat trouvé"))
                        self.root.after(0, self._show_current_song_thumbnail)
                    return
                
                # Vérifier l'annulation avant le traitement des résultats
                if self.search_cancelled:
                    return
                
                # Nettoyer le container
                if not self.search_cancelled:
                    self.root.after(0, self._clear_results)
                
                # Stocker les résultats bruts pour le filtrage ultérieur
                self.all_raw_search_results = results['entries']
                
                # Filtrer selon les cases à cocher
                filtered_results = self._filter_search_results(results['entries'])
                
                # Vérifier l'annulation après le filtrage
                if self.search_cancelled:
                    return
                
                # video_results = [
                #     entry for entry in results['entries']
                #     if (entry and entry.get('duration', 0) <= 600.0)  # Durée max de 10 minutes
                # ]
                
                # Stocker les résultats initiaux
                self.all_search_results = filtered_results
                
                # Indiquer qu'il y a potentiellement plus de résultats si on a obtenu le nombre maximum demandé
                self.has_more_results = len(results['entries']) >= self.initial_search_count
                self.total_available_results = len(self.all_search_results)
                
                # Si aucun résultat après filtrage, afficher la miniature
                if not self.all_search_results:
                    if not self.search_cancelled:
                        self.root.after(0, lambda: self._safe_status_update("Aucun résultat trouvé"))
                        self.root.after(0, self._show_current_song_thumbnail)
                    return
                
                # Vérifier l'annulation avant l'affichage
                if self.search_cancelled:
                    return
                
                # Afficher les résultats initiaux
                self._display_batch_results(1)
                
                # Calculer et afficher le temps de recherche
                if self.search_start_time and not self.search_cancelled:
                    search_duration = time.time() - self.search_start_time
                    self.last_search_time = search_duration
                    self.root.after(0, lambda: self._safe_status_update(
                        f"Recherche terminée - {len(self.all_search_results)} résultats trouvés"
                    ))
                    self.root.after(0, self._update_stats_bar)
                
        except Exception as e:
            if not self.search_cancelled:
                error_msg = f"Erreur recherche: {e}"
                self.root.after(0, lambda: self._safe_status_update(error_msg))
        finally:
            # Ne réinitialiser les flags que si la recherche n'a pas été annulée
            if not self.search_cancelled:
                self.is_searching = False
                self.is_loading_more = False
            self.current_search_thread = None

    def _filter_search_results(self, entries):
        """Filtre les résultats selon les cases à cocher Artists et Tracks"""
        if not entries:
            return []
        
        filtered_results = []
        show_artists = getattr(self, 'show_artists', None)
        show_tracks = getattr(self, 'show_tracks', None)
        
        # Si les variables n'existent pas encore (première recherche), tout afficher
        if show_artists is None or show_tracks is None:
            show_artists_val = True
            show_tracks_val = True
        else:
            show_artists_val = show_artists.get()
            show_tracks_val = show_tracks.get()
        
        for entry in entries:
            if not entry:
                continue
            
            # print("ENTRY" ,entry) # debug
                        
            url = entry.get('url', '')
            duration = entry.get('duration', 0)
            
            # Identifier le type de contenu
            is_video = "https://www.youtube.com/watch?v=" in url
            is_channel = "https://www.youtube.com/channel/" in url or "https://www.youtube.com/@" in url
            
            # Filtrer selon les préférences
            if is_video and show_tracks_val and duration <= 600.0:  # Vidéos (tracks) max 10 minutes
                filtered_results.append(entry)
            elif is_channel and show_artists_val:  # Chaînes (artists)
                filtered_results.append(entry)
        return filtered_results

    def _on_filter_change(self):
        """Appelée quand les cases à cocher changent"""
        search_tab.results._on_filter_change(self)

    def _display_batch_results(self, batch_number):
        """Affiche un lot de 10 résultats"""
        return search_tab.results._display_batch_results(self, batch_number)

    
    def _load_more_search_results(self):
        """Charge plus de résultats pour la recherche actuelle (avec lazy loading)"""
        return search_tab.results._load_more_search_results(self)

    def _fetch_more_results(self, query, total_count, start_time=None):
        """Récupère plus de résultats depuis YouTube"""
        return search_tab.results._fetch_more_results(self, query, total_count, start_time)

    def _display_new_results(self, new_results):
        """Affiche les nouveaux résultats obtenus"""
        search_tab.results._display_new_results(self, new_results)

    def _clear_results(self):
        """Vide le container de résultats et gère l'affichage des frames"""
        search_tab.results._clear_results(self)
    
    def _show_search_results(self):
        """Affiche le canvas de résultats et masque la frame thumbnail"""
        search_tab.results._show_search_results(self)

    def _update_results_counter(self):
        """Met à jour le compteur de résultats affiché"""
        tools._update_results_counter(self)

    # def _add_search_result(self, video, index):
    #     """Ajoute un résultat à la liste et scroll si nécessaire"""
    #     title = video.get('title', 'Sans titre')
    #     self.youtube_results.insert(tk.END, title)
        
    #     # Faire défiler vers le bas si c'est un des derniers résultats
    #     if index >= 5:
    #         self.youtube_results.see(tk.END)
    
    def _create_circular_image(self, image, size=DEFAULT_CIRC_THUMBNAIL_SIZE):
        """Crée une image circulaire à partir d'une image rectangulaire"""
        return tools._create_circular_image(self, image, size=size)

    def _safe_add_search_result(self, video, index):
        """Version sécurisée de _add_search_result qui vérifie l'annulation"""
        if not self.search_cancelled:
            self._add_search_result(video, index)
    
    def _safe_update_status(self, batch_number):
        """Version sécurisée de la mise à jour du statut"""
        if not self.search_cancelled and hasattr(self, 'status_bar'):
            try:
                # Afficher le statut avec indication s'il y a plus de résultats
                status_text = f"{self.search_results_count}/{len(self.all_search_results)} résultats affichés"
                if self.has_more_results:
                    status_text += " (plus disponibles)"
                elif len(self.all_search_results) >= self.max_search_results:
                    status_text += " (limite atteinte)"
                
                self.status_bar.config(text=status_text)
            except Exception as e:
                print(f"Erreur mise à jour statut: {e}")
    
    def _safe_status_update(self, message):
        """Version sécurisée de la mise à jour du statut avec message personnalisé"""
        if not self.search_cancelled and hasattr(self, 'status_bar'):
            try:
                self.status_bar.config(text=message)
            except Exception as e:
                print(f"Erreur mise à jour statut: {e}")

    def _add_search_result(self, video, index):
        """Ajoute un résultat avec un style rectangle uniforme"""
        try:
            # Vérifier si la recherche a été annulée ou si les widgets n'existent plus
            if self.search_cancelled or not hasattr(self, 'results_container'):
                return
            
            # Vérifier que le container existe encore
            try:
                self.results_container.winfo_exists()
            except:
                return
                
            title = video.get('title', 'Sans titre')
            duration = video.get('duration', 0)
            url = video.get('url', '')
            
            # Déterminer le type de contenu
            is_channel = "https://www.youtube.com/channel/" in url or "https://www.youtube.com/@" in url
            
            # Frame principal - grand rectangle uniforme
            result_frame = tk.Frame(
                self.results_container,
                bg='#4a4a4a',  # Fond gris uniforme
                relief='flat',
                bd=1,
                highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
                highlightthickness=1
            )
            video['search_frame'] = result_frame
            result_frame.pack(fill="x", padx=5, pady=2)
            
            # Stocker l'URL dans le frame pour détecter les doublons
            result_frame.video_url = video.get('url', '')
            
            # Configuration de la grille en 3 colonnes : miniature, titre, durée
            # Ajuster la taille selon le type de contenu
            if is_channel:
                result_frame.columnconfigure(0, minsize=90, weight=0)  # Plus d'espace pour miniature circulaire
                result_frame.rowconfigure(0, minsize=70, weight=0)     # Plus de hauteur pour les chaînes
            else:
                result_frame.columnconfigure(0, minsize=80, weight=0)  # Miniature normale
                result_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur normale
            result_frame.columnconfigure(1, weight=1)              # Titre
            result_frame.columnconfigure(2, minsize=60, weight=0)  # Durée
            
            # 1. Miniature (colonne 0)
            if is_channel:
                # Pour les chaînes, plus d'espace et moins de padding
                thumbnail_label = tk.Label(
                    result_frame,
                    bg='#4a4a4a',
                    width=8,
                    height=4,
                    anchor='center'
                ) 
                thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=5)
            else:
                # Pour les vidéos, taille normale
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
            
            # 2. Titre et métadonnées (colonne 1)
            text_frame = tk.Frame(result_frame, bg='#4a4a4a')
            text_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 10), pady=8)
            text_frame.columnconfigure(0, weight=1)
            
            # Titre principal
            title_label = tk.Label(
                text_frame,
                text=title,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left'
            )
            title_label.grid(row=0, column=0, sticky='ew', pady=(2, 0))
            
            # Métadonnées (artiste • album) - seulement pour les vidéos, pas les chaînes
            if not is_channel:
                
                # Extraire les métadonnées depuis les informations YouTube
                artist = video.get('uploader', '')
                album = video.get('album', '')
                
                # print(video) # debug
                
                # Créer le texte des métadonnées
                metadata_text = self._format_artist_album_info(artist, album)
                
                if metadata_text:
                    metadata_label = tk.Label(
                        text_frame,
                        text=metadata_text,
                        bg='#4a4a4a',
                        fg='#cccccc',
                        font=('TkDefaultFont', 8),
                        anchor='w',
                        justify='left'
                    )
                    metadata_label.grid(row=1, column=0, sticky='ew', pady=(0, 2))
            
            # 3. Durée ou type (colonne 2)
            if is_channel:
                duration_text = "Chaîne"
                duration_color = '#ffaa00'  # Orange pour les chaînes
            else:
                duration_text = time.strftime('%M:%S', time.gmtime(duration))
                duration_color = '#cccccc'
            
            duration_label = tk.Label(
                result_frame,
                text=duration_text,
                bg='#4a4a4a',
                fg=duration_color,
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
                # Initialiser le drag
                if not is_channel:  # Seulement pour les vidéos
                    self.drag_drop_handler.setup_drag_start(event, frame)
                
                # Vérifier si Shift est enfoncé pour la sélection multiple
                if event.state & 0x1:  # Shift est enfoncé
                    self.shift_selection_active = True
                    # Utiliser l'URL comme identifiant unique pour les résultats YouTube
                    video_url = frame.video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={frame.video_data.get('id')}"
                    self.toggle_item_selection(video_url, frame)
                else:
                    # Clic normal sans Shift - ne pas effacer la sélection si elle existe
                    pass
            
            def on_result_double_click(event, frame=result_frame):
                # Vérifier si Shift est enfoncé - ne rien faire sur double-clic avec Shift
                if event.state & 0x1:  # Shift est enfoncé
                    pass
                else:
                    # Vérifier si c'est une chaîne
                    video_url = frame.video_data.get('url', '')
                    if "https://www.youtube.com/channel/" in video_url or "https://www.youtube.com/@" in video_url:
                        # Pour les chaînes, ouvrir dans le navigateur
                        import webbrowser
                        webbrowser.open(video_url)
                        self.status_bar.config(text="Chaîne ouverte dans le navigateur")
                    else:
                        # Comportement modifié : télécharger SANS ajouter à la playlist
                        self._on_result_click(frame, add_to_playlist=False)
            
            # Bindings pour les clics simples et doubles
            duration_label.bind("<Button-1>", on_result_click)
            duration_label.bind("<Double-1>", on_result_double_click)
            text_frame.bind("<Button-1>", on_result_click)
            text_frame.bind("<Double-1>", on_result_double_click)
            title_label.bind("<Button-1>", on_result_click)
            title_label.bind("<Double-1>", on_result_double_click)
            if not is_channel and metadata_text:  # Ajouter binding pour metadata_label s'il existe
                metadata_label.bind("<Button-1>", on_result_click)
                metadata_label.bind("<Double-1>", on_result_double_click)
            thumbnail_label.bind("<Button-1>", on_result_click)
            thumbnail_label.bind("<Double-1>", on_result_double_click)
            
            # Ajouter des tooltips pour expliquer les interactions
            if is_channel:
                tooltip_text = "Chaîne YouTube\nDouble-clic: Ouvrir dans le navigateur\nShift + Clic: Sélection multiple"
            else:
                tooltip_text = "Vidéo YouTube\nDouble-clic: Télécharger (sans ajouter à la playlist)\nDrag vers la droite: Télécharger et ajouter à la queue\nDrag vers la gauche: Télécharger et placer en premier dans la queue\nShift + Clic: Sélection multiple"
            create_tooltip(text_frame, tooltip_text)
            create_tooltip(title_label, tooltip_text)
            if not is_channel and metadata_text:
                create_tooltip(metadata_label, tooltip_text)
            create_tooltip(duration_label, tooltip_text)
            create_tooltip(thumbnail_label, tooltip_text)
            result_frame.bind("<Button-1>", on_result_click)
            result_frame.bind("<Double-1>", on_result_double_click)
            
            # Configuration du drag-and-drop pour les vidéos
            if not is_channel:
                self.drag_drop_handler.setup_drag_drop(
                    result_frame, 
                    video_data=video, 
                    item_type="youtube"
                )
            
            # Événements de clic droit pour ajouter après la chanson en cours
            duration_label.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            text_frame.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            title_label.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            if not is_channel and metadata_text:  # Ajouter binding pour metadata_label s'il existe
                metadata_label.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            thumbnail_label.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            result_frame.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            

            
            # Charger la miniature en arrière-plan
            if video.get('thumbnails'):
                thumbnail_url = video['thumbnails'][1]['url'] if len(video['thumbnails']) > 1 else video['thumbnails'][0]['url']
                if is_channel:
                    # Pour les chaînes, utiliser une miniature circulaire
                    threading.Thread(
                        target=self._load_circular_thumbnail,
                        args=(thumbnail_label, thumbnail_url),
                        daemon=True
                    ).start()
                else:
                    # Pour les vidéos, miniature normale
                    threading.Thread(
                        target=self._load_thumbnail,
                        args=(thumbnail_label, thumbnail_url),
                        daemon=True
                    ).start()
                
        except Exception as e:
            print(f"Erreur affichage résultat: {e}")
    
    def _on_result_click(self, frame, add_to_playlist=True):
        """Gère le clic sur un résultat"""
        if hasattr(frame, 'video_data'):
            video = frame.video_data
            
            # Vérifier si déjà en cours de téléchargement
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            if url in self.current_downloads:
                self.status_bar.config(text="Téléchargement déjà en cours...")
                return
            
            # Changer l'apparence pour indiquer le téléchargement
            self._reset_frame_appearance(frame, '#ff6666')
            
            self.search_list = [frame.video_data]  # Pour la compatibilité avec download_selected_youtube
            frame.video_data['search_frame'] = frame
            try:
                self.download_selected_youtube(None, add_to_playlist)
            except Exception as e:
                # En cas d'erreur, remettre l'apparence normale
                frame.config(bg='#ffcc00')  # Jaune pour erreur
                frame.title_label.config(bg='#ffcc00', fg='#333333')
                frame.duration_label.config(bg='#ffcc00', fg='#666666')
                frame.thumbnail_label.config(bg='#ffcc00')
    
    def _on_result_right_click(self, frame):
        """Gère le clic droit sur un résultat pour afficher le menu des playlists"""
        if hasattr(frame, 'video_data'):
            video = frame.video_data
            
            # Vérifier si déjà en cours de téléchargement
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            if url in self.current_downloads:
                # Afficher le menu pour ajouter à une playlist après téléchargement
                self._show_pending_playlist_menu(video, frame, url)
                return
            
            # Afficher le menu des playlists
            self._show_youtube_playlist_menu(video, frame)
    
    def _show_pending_playlist_menu(self, video, frame, url):
        """Affiche un menu pour ajouter une musique en cours de téléchargement à une playlist"""
        import tkinter.ttk as ttk
        
        title = video.get('title', 'Titre inconnu')
        
        # Créer un menu contextuel
        menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
                      activebackground='#4a8fe7', activeforeground='white')
        
        menu.add_command(
            label=f"📥 {title[:30]}{'...' if len(title) > 30 else ''}",
            state='disabled'
        )
        menu.add_separator()
        
        # Vérifier quelles playlists sont déjà en attente pour cette URL
        pending_playlists = self.pending_playlist_additions.get(url, [])
        
        # Ajouter les playlists existantes
        for playlist_name in self.playlists.keys():
            if playlist_name in pending_playlists:
                menu.add_command(
                    label=f"✓ '{playlist_name}' (en attente)",
                    state='disabled'
                )
            else:
                menu.add_command(
                    label=f"Ajouter à '{playlist_name}' après téléchargement",
                    command=lambda name=playlist_name: self._add_to_pending_playlist(url, name, title)
                )
        
        menu.add_separator()
        
        # Option pour créer une nouvelle playlist
        menu.add_command(
            label="Créer nouvelle playlist...",
            command=lambda: self._create_new_playlist_for_pending(url, title)
        )
        
        # Afficher le menu à la position de la souris
        try:
            menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        except:
            # Fallback
            menu.post(100, 100)
    
    def _add_to_pending_playlist(self, url, playlist_name, title):
        """Ajoute une playlist à la liste d'attente pour une URL en cours de téléchargement"""
        if url not in self.pending_playlist_additions:
            self.pending_playlist_additions[url] = []
        
        if playlist_name not in self.pending_playlist_additions[url]:
            self.pending_playlist_additions[url].append(playlist_name)
            self.status_bar.config(text=f"'{title[:30]}...' sera ajouté à '{playlist_name}' après téléchargement")
        else:
            self.status_bar.config(text=f"'{title[:30]}...' est déjà en attente pour '{playlist_name}'")
    
    def _create_new_playlist_for_pending(self, url, title):
        """Crée une nouvelle playlist et l'ajoute à la liste d'attente"""
        playlist_name = simpledialog.askstring(
            "Nouvelle playlist",
            "Nom de la nouvelle playlist:",
            parent=self.root
        )
        
        if playlist_name and playlist_name.strip():
            playlist_name = playlist_name.strip()
            if playlist_name not in self.playlists:
                self.playlists[playlist_name] = []
                self.save_playlists()
                self.status_bar.config(text=f"Playlist '{playlist_name}' créée")
                
                # Ajouter à la liste d'attente
                self._add_to_pending_playlist(url, playlist_name, title)
            else:
                self.status_bar.config(text=f"La playlist '{playlist_name}' existe déjà")
                # Ajouter à la liste d'attente même si elle existe déjà
                self._add_to_pending_playlist(url, playlist_name, title)
    
    def _show_youtube_playlist_menu(self, video, frame):
        """Affiche un menu déroulant pour choisir la playlist pour une vidéo YouTube"""
        import tkinter.ttk as ttk
        
        # Créer un menu contextuel
        menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
                      activebackground='#4a8fe7', activeforeground='white')
        
        # Ajouter les playlists existantes
        for playlist_name in self.playlists.keys():
            menu.add_command(
                label=f"Ajouter à '{playlist_name}'",
                command=lambda name=playlist_name: self._add_youtube_to_playlist(video, frame, name)
            )
        
        menu.add_separator()
        
        # Option pour créer une nouvelle playlist
        menu.add_command(
            label="Créer nouvelle playlist...",
            command=lambda: self._create_new_playlist_dialog_youtube(video, frame)
        )
        
        # Afficher le menu à la position de la souris
        try:
            menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        except:
            # Fallback
            menu.post(100, 100)
    
    def _add_youtube_to_playlist(self, video, frame, playlist_name):
        """Ajoute une vidéo YouTube à une playlist (télécharge si nécessaire)"""
        title = video.get('title', 'Titre inconnu')
        
        # Vérifier si le fichier existe déjà
        existing_file = self._get_existing_download(title)
        if existing_file:
            # Le fichier existe déjà, l'ajouter directement à la playlist
            if playlist_name == "Main Playlist":
                self.add_to_main_playlist(existing_file)
            else:
                if existing_file not in self.playlists[playlist_name]:
                    self.playlists[playlist_name].append(existing_file)
                    self.save_playlists()
                    self.status_bar.config(text=f"Ajouté à '{playlist_name}': {os.path.basename(existing_file)}")
                else:
                    self.status_bar.config(text=f"Déjà dans '{playlist_name}': {os.path.basename(existing_file)}")
        else:
            # Le fichier n'existe pas, le télécharger puis l'ajouter
            self.status_bar.config(text=f"Téléchargement de {title} pour '{playlist_name}'...")
            
            # Changer l'apparence pour indiquer le téléchargement
            self._reset_frame_appearance(frame, '#ff6666')
            
            # Lancer le téléchargement dans un thread
            threading.Thread(
                target=self._download_and_add_to_playlist_thread,
                args=(video, frame, playlist_name),
                daemon=True
            ).start()
    
    def _create_new_playlist_dialog_youtube(self, video, frame):
        """Dialogue pour créer une nouvelle playlist et y ajouter une vidéo YouTube"""
        playlist_name = simpledialog.askstring(
            "Nouvelle playlist",
            "Nom de la nouvelle playlist:",
            parent=self.root
        )
        
        if playlist_name and playlist_name.strip():
            playlist_name = playlist_name.strip()
            if playlist_name not in self.playlists:
                self.playlists[playlist_name] = []
                self.save_playlists()
                self.status_bar.config(text=f"Playlist '{playlist_name}' créée")
                
                # Ajouter la vidéo à la nouvelle playlist
                self._add_youtube_to_playlist(video, frame, playlist_name)
            else:
                self.status_bar.config(text=f"La playlist '{playlist_name}' existe déjà")
    
    

    def _download_and_add_to_playlist_thread(self, video, frame, playlist_name):
        """Thread pour télécharger une vidéo et l'ajouter à une playlist"""
        try:
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            self.current_downloads.add(url)
            
            title = video.get('title', 'Titre inconnu')
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
            
            # Stocker le titre pour l'affichage de progression
            self.current_download_title = safe_title
            
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
                
                final_path = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3').replace('.mp4', '.mp3')
                if not final_path.endswith('.mp3'):
                    final_path += '.mp3'
                
                thumbnail_path = os.path.splitext(final_path)[0] + ".jpg"
                if os.path.exists(downloaded_file + ".jpg"):
                    os.rename(downloaded_file + ".jpg", thumbnail_path)
                
                # Sauvegarder l'URL YouTube originale avec la date de publication
                upload_date = info.get('upload_date') if info else None
                self.save_youtube_url_metadata(final_path, url, upload_date)
                
                # Ajouter à la playlist spécifiée dans le thread principal
                self.root.after(0, lambda: self._add_downloaded_to_playlist(final_path, thumbnail_path, safe_title, playlist_name, url))
                
                # Remettre l'apparence normale dans le thread principal
                self.root.after(0, lambda: self._reset_frame_appearance(frame, '#4a4a4a'))
        
        except Exception as e:
            self.root.after(0, lambda e=e: self.status_bar.config(text=f"Erreur: {str(e)}"))
            # Apparence d'erreur (jaune) dans le thread principal
            self.root.after(0, lambda: self._reset_frame_appearance(frame, '#ffcc00', error=True))
        finally:
            # S'assurer que l'URL est retirée même en cas d'erreur
            if url in self.current_downloads:
                self.current_downloads.remove(url)
                self._update_search_results_ui()
            # Réinitialiser le titre de téléchargement
            self.current_download_title = ""
    
    def _add_downloaded_to_playlist(self, filepath, thumbnail_path, title, playlist_name, url=None):
        """Ajoute un fichier téléchargé à une playlist spécifique (à appeler dans le thread principal)"""
        if playlist_name == "Main Playlist":
            # Pour la main playlist, utiliser la nouvelle fonction centralisée
            added = self.add_to_main_playlist(filepath, thumbnail_path, show_status=False)
            if added:
                self.status_bar.config(text=f"{title} ajouté à la liste principale")
                # Marquer que la main playlist ne provient pas d'une playlist (ajout individuel)
                self.main_playlist_from_playlist = False
            else:
                self.status_bar.config(text=f"{title} est déjà dans la liste principale")
        else:
            # Pour les autres playlists
            if filepath not in self.playlists[playlist_name]:
                self.playlists[playlist_name].append(filepath)
                self.save_playlists()
                self.status_bar.config(text=f"{title} ajouté à '{playlist_name}'")
            else:
                self.status_bar.config(text=f"{title} est déjà dans '{playlist_name}'")
        
        # Vérifier s'il y a d'autres playlists en attente pour cette URL
        if url and url in self.pending_playlist_additions:
            pending_playlists = self.pending_playlist_additions[url]
            for pending_playlist_name in pending_playlists:
                if pending_playlist_name != playlist_name:
                    if pending_playlist_name == "Main Playlist":
                        # Gérer spécialement la Main Playlist
                        added = self.add_to_main_playlist(filepath, thumbnail_path, show_status=False)
                        if added:
                            self.status_bar.config(text=f"{title} aussi ajouté à la liste principale (en attente)")
                            self.main_playlist_from_playlist = False
                    elif pending_playlist_name in self.playlists:
                        # Gérer les autres playlists
                        if filepath not in self.playlists[pending_playlist_name]:
                            self.playlists[pending_playlist_name].append(filepath)
                            self.status_bar.config(text=f"{title} aussi ajouté à '{pending_playlist_name}' (en attente)")
            
            # Sauvegarder les playlists si des ajouts ont été faits
            if pending_playlists:
                self.save_playlists()
            
            # Nettoyer la liste d'attente pour cette URL
            del self.pending_playlist_additions[url]
        
        # Mettre à jour le compteur de fichiers téléchargés
        file_services._count_downloaded_files(self)
        self._update_downloads_button()
        
        # Mettre à jour la liste des téléchargements dans l'onglet bibliothèque
        self._refresh_downloads_library()
    
    def _reset_frame_appearance(self, frame, bg_color, error=False):
        """Remet l'apparence d'un frame de manière sécurisée"""
        try:
            if frame.winfo_exists():
                frame.config(bg=bg_color)
                if hasattr(frame, 'title_label') and frame.title_label.winfo_exists():
                    if error:
                        frame.title_label.config(bg=bg_color, fg='#333333')
                    elif bg_color == '#ff6666':  # Rouge pour téléchargement
                        frame.title_label.config(bg=bg_color, fg='#cccccc')
                    else:
                        frame.title_label.config(bg=bg_color, fg='white')
                if hasattr(frame, 'duration_label') and frame.duration_label.winfo_exists():
                    if error:
                        frame.duration_label.config(bg=bg_color, fg='#666666')
                    elif bg_color == '#ff6666':  # Rouge pour téléchargement
                        frame.duration_label.config(bg=bg_color, fg='#aaaaaa')
                    else:
                        frame.duration_label.config(bg=bg_color, fg='#cccccc')
                if hasattr(frame, 'thumbnail_label') and frame.thumbnail_label.winfo_exists():
                    frame.thumbnail_label.config(bg=bg_color)
        except tk.TclError:
            # Le widget a été détruit, ignorer l'erreur
            pass
    
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
    
    def setup_controls(self):
        setup.setup_controls(self)

    def _refresh_playlist_display(self):
        """Rafraîchit l'affichage de la main playlist"""
        # Vider le container actuel
        for widget in self.playlist_container.winfo_children():
            widget.destroy()
        
        # Recréer tous les éléments avec les bons index
        for i, filepath in enumerate(self.main_playlist):
            self._add_main_playlist_item(filepath, song_index=i)
        
        # Remettre en surbrillance la chanson en cours si elle existe (sans scrolling automatique)
        if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
            self.select_playlist_item(index=self.current_index, auto_scroll=False)
    
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


    def download_selected_youtube(self, event=None, add_to_playlist=True):
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
            args=(url, add_to_playlist),  # Passer l'URL et le flag add_to_playlist
            daemon=True
        )
        download_thread.start()

    def _download_youtube_thread(self, url, add_to_playlist=True):
        return tools._download_youtube_thread(self, url, add_to_playlist)

    def _download_progress_hook(self, d):
        """Hook pour afficher la progression du téléchargement"""
        return tools._download_progress_hook(self, d)

    def _add_downloaded_file(self, filepath, thumbnail_path, title, url=None, add_to_playlist=True):
        """Ajoute le fichier téléchargé à la main playlist (à appeler dans le thread principal)"""
        return tools._add_downloaded_file(self, filepath, thumbnail_path, title, url, add_to_playlist)

    def _refresh_downloads_library(self):
        """Met à jour la liste des téléchargements dans l'onglet bibliothèque si il est actif"""
        return library_tab.downloads._refresh_downloads_library(self)

    def _load_thumbnail(self, label, url):
        """Charge et affiche la miniature"""
        return tools._load_thumbnail(self, label, url)

    def _load_circular_thumbnail(self, label, url):
        """Charge et affiche la miniature circulaire pour les chaînes"""
        return tools._load_circular_thumbnail(self, label, url)

    def _display_thumbnail(self, label, photo):
        """Affiche la miniature dans le label"""
        tools._display_thumbnail(self, label, photo)

    def _get_existing_download(self, title):
        """Vérifie si un fichier existe déjà dans downloads avec un titre similaire"""
        return tools._get_existing_download(self, title)

    def _update_search_results_ui(self):
        """Met à jour l'apparence des résultats en fonction de l'état de téléchargement"""
        return search_tab.results._update_search_results_ui(self)

    def generate_waveform_preview(self, filepath):
        """Génère les données audio brutes pour la waveform (sans sous-échantillonnage)"""
        return control.generate_waveform_preview(self, filepath)

    def get_adaptive_waveform_data(self, canvas_width=None):
        """Génère des données waveform adaptées à la durée de la musique"""
        return control.get_adaptive_waveform_data(self, canvas_width)
    
    def play_pause(self):
        return control.play_pause(self)

    def play_selected(self, event):
        return control.play_selected(self, event)
    
    def prev_track(self):
        control.prev_track(self)

    def next_track(self):
        return control.next_track(self)
    
    def show_waveform_on_clicked(self):
        return control.show_waveform_on_clicked(self)

    def draw_waveform_around(self, time_sec, window_sec=5):
        return control.draw_waveform_around(self, time_sec, window_sec)

    def set_volume(self, val):
        return tools.set_volume(self, val)
    
    def set_volume_offset(self, val):
        return tools.set_volume_offset(self, val)
    
    def _apply_volume(self):
        return tools._apply_volume(self)

    def _reset_volume_offset(self, event):
        return tools._reset_volume_offset(self, event)

    def on_progress_press(self, event):
        return control.on_progress_press(self, event)
    
    def on_progress_drag(self, event):
        return control.on_progress_drag(self, event)

    def on_progress_release(self, event):
        return control.on_progress_release(self, event)
    
    def on_waveform_canvas_resize(self, event):
        return control.on_waveform_canvas_resize(self, event)


    
    # def set_position(self, val):
    #     return
    #     if pygame.mixer.music.get_busy() and not self.paused:
    #         pygame.mixer.music.set_pos(float(val))
    #         self.current_time = float(val)
    
    def set_position(self, val):
        return control.set_position(self, val)
        
            
    
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
        # Mettre à jour les statistiques une dernière fois
        self._update_current_song_stats()
        
        # Arrêter l'animation du titre
        self._stop_title_animation()
        
        # Sauvegarder la configuration avant de fermer
        self.save_config()
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.root.destroy()

    def save_youtube_url_metadata(self, filepath, youtube_url, upload_date=None):
        """Sauvegarde les métadonnées YouTube étendues pour un fichier téléchargé"""
        try:
            import json
            metadata_file = os.path.join("downloads", "youtube_urls.json")
            
            # Charger les métadonnées existantes
            metadata = {}
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except:
                    metadata = {}
            
            # Ajouter les nouvelles métadonnées (maintien compatibilité avec ancien format)
            filename = os.path.basename(filepath)
            
            # Si c'est déjà au nouveau format (dictionnaire), mettre à jour
            if isinstance(metadata.get(filename), dict):
                metadata[filename]['url'] = youtube_url
                if upload_date:
                    metadata[filename]['upload_date'] = upload_date
            else:
                # Créer une nouvelle entrée au format étendu
                metadata[filename] = {
                    'url': youtube_url,
                    'upload_date': upload_date
                }
            
            # Sauvegarder
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erreur sauvegarde métadonnées YouTube: {e}")
    
    def get_youtube_url_from_metadata(self, filepath):
        """Récupère l'URL YouTube originale pour un fichier téléchargé"""
        return tools.get_youtube_metadata(self, filepath)
    def get_youtube_metadata(self, filepath):
        """Récupère toutes les métadonnées YouTube pour un fichier téléchargé"""
        return tools.get_youtube_metadata(self, filepath)
    def remove_youtube_url_metadata(self, filepath):
        """Supprime l'URL YouTube des métadonnées quand un fichier est supprimé"""
        return tools.remove_youtube_url_metadata(self, filepath)

    def open_music_on_youtube(self, filepath):
        """Ouvre une musique sur YouTube - directement si l'URL est connue, sinon par recherche"""
        return tools.open_music_on_youtube(self, filepath)

    def toggle_random_mode(self):
        """Active/désactive le mode aléatoire"""
        return control.toggle_random_mode(self)

    def toggle_loop_mode(self):
        """Cycle entre les 3 modes de boucle : désactivé -> loop playlist -> loop chanson -> désactivé"""
        return control.toggle_loop_mode(self)

    def _shuffle_remaining_playlist(self):
        """Mélange aléatoirement la suite de la playlist à partir de la chanson suivante"""
        return tools._shuffle_remaining_playlist(self)

if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.on_closing)
    root.mainloop()
