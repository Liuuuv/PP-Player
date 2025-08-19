# Import centralisé depuis __init__.py
from __init__ import *


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pipi Player")
        self.root.geometry(GEOMETRY)
        # Fixer la taille mais permettre le déplacement
        self.root.resizable(False, False)
        self.root.minsize(800, 700)
        self.root.maxsize(800, 700)
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
        self.search_cancelled = False  # Flag pour annuler la recherche en cours
        self.current_search_thread = None  # Thread de recherche actuel
        
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
        setup.load_icons(self)
        
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

    def _on_youtube_scroll(self, event):
        """Gère le scroll de la molette dans les résultats YouTube"""
        inputs._on_youtube_scroll(self, event)
    
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
            text=f"{playlist_name} ({songs_count} titres)",
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
        return library_tab.playlists._back_to_playlists(self)

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
            truncated_title = self._truncate_text_for_display(filename, max_width_pixels=170, font_family='TkDefaultFont', font_size=9)
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
            create_tooltip(delete_btn, "Supprimer de la playlist\nDouble-clic pour retirer cette chanson de la playlist")
            
            item_frame.filepath = filepath
            
            def on_playlist_item_click(event):
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
            title_label.bind("<Button-3>", on_playlist_item_right_click)
            duration_label.bind("<Button-3>", on_playlist_item_right_click)
            
            if show_numbers:
                number_label.bind("<Button-3>", on_playlist_item_right_click)

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
            self.selection_frames[filepath] = frame
            self._set_item_colors(frame, '#ff8c00')  # Couleur orange pour la sélection multiple
        
        # Mettre à jour l'affichage du nombre d'éléments sélectionnés
        self.update_selection_display()
    
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
        self.root.after(0, file_services._count_downloaded_files(self))
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

            self.song_label.config(text=os.path.basename(song)[:-4] if os.path.basename(song).lower().endswith('.mp3') else os.path.basename(song))

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
        if self.is_searching and self.current_search_thread:
            self.search_cancelled = True
            # Attendre un court moment pour que le thread précédent se termine
            self.root.after(100, lambda: self._start_new_search())
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
        
        # Nouvelle recherche - réinitialiser les compteurs et flags
        self.search_cancelled = False
        self.current_search_query = query
        self.search_results_count = 0
        self.is_loading_more = False
        self.current_search_batch = 1
        self.all_search_results = []  # Stocker tous les résultats filtrés
        self.all_raw_search_results = []  # Stocker tous les résultats bruts
        
        # Effacer les résultats précédents
        self._clear_results()
        self.search_list = []
        self.status_bar.config(text="Recherche en cours...")
        self.root.update()
        
        self.is_searching = True
        
        # Lancer une recherche complète au début
        self.current_search_thread = threading.Thread(target=self._perform_complete_search, args=(query,), daemon=True)
        self.current_search_thread.start()

    def _perform_complete_search(self, query):
        """Effectue une recherche complète et stocke tous les résultats"""
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.search_cancelled:
                return
                
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'max_downloads': 50,  # Chercher 50 résultats
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                # Vérifier l'annulation avant la recherche
                if self.search_cancelled:
                    return
                    
                # Recherche de 50 résultats
                results = ydl.extract_info(f"ytsearch50:{query}", download=False)
                
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
                
                # Stocker tous les résultats (maximum 50)
                self.all_search_results = filtered_results[:self.max_search_results]
                
                # Si aucun résultat après filtrage, afficher la miniature
                if not self.all_search_results:
                    if not self.search_cancelled:
                        self.root.after(0, lambda: self._safe_status_update("Aucun résultat trouvé"))
                        self.root.after(0, self._show_current_song_thumbnail)
                    return
                
                # Vérifier l'annulation avant l'affichage
                if self.search_cancelled:
                    return
                
                # Afficher les 10 premiers résultats
                self._display_batch_results(1)
                
        except Exception as e:
            if not self.search_cancelled:
                self.root.after(0, lambda: self.status_bar.config(text=f"Erreur recherche: {e}"))
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
        # Si on a des résultats de recherche stockés, les refiltrer et réafficher
        if hasattr(self, 'all_raw_search_results') and self.all_raw_search_results:
            # Refiltrer les résultats bruts avec les nouveaux critères
            filtered_results = self._filter_search_results(self.all_raw_search_results)
            self.all_search_results = filtered_results[:self.max_search_results]
            
            # Effacer les résultats actuels
            self._clear_results()
            
            # Réinitialiser les compteurs
            self.search_results_count = 0
            self.current_search_batch = 1
            
            # Si aucun résultat après filtrage, afficher la miniature
            if not self.all_search_results:
                self.status_bar.config(text="Aucun résultat avec ces filtres")
                self._show_current_song_thumbnail()
                return
            
            # Afficher les résultats filtrés
            self._show_search_results()
            self._display_batch_results(1)

    def _display_batch_results(self, batch_number):
        """Affiche un lot de 10 résultats"""
        # Vérifier si la recherche a été annulée
        if self.search_cancelled:
            return
            
        start_index = (batch_number - 1) * 10
        end_index = min(start_index + 10, len(self.all_search_results))
        
        # Si c'est le premier lot, afficher le canvas de résultats
        if batch_number == 1 and end_index > start_index:
            if not self.search_cancelled:
                self.root.after(0, self._show_search_results)
        
        # Afficher les résultats de ce lot
        for i in range(start_index, end_index):
            # Vérifier l'annulation à chaque itération
            if self.search_cancelled:
                return
                
            if i < len(self.all_search_results):
                video = self.all_search_results[i]
                if not self.search_cancelled:
                    self.root.after(0, lambda v=video, idx=i: self._safe_add_search_result(v, idx))
                    self.search_results_count += 1
        
        # Mettre à jour le statut seulement si pas annulé
        if not self.search_cancelled:
            self.root.after(0, lambda: self._safe_update_status(batch_number))




    
    def _load_more_search_results(self):
        """Charge plus de résultats pour la recherche actuelle"""
        print(f"_load_more_search_results appelée - Lot actuel: {self.current_search_batch}, Résultats: {self.search_results_count}/{len(self.all_search_results)}")
        
        if (self.is_loading_more or 
            self.is_searching or
            self.search_cancelled or  # Vérifier si la recherche a été annulée
            not self.current_search_query or 
            self.search_results_count >= len(self.all_search_results) or
            self.current_search_batch >= self.max_search_batchs):
            return
        
        self.is_loading_more = True
        self.current_search_batch += 1
        
        self.status_bar.config(text=f"Chargement du lot {self.current_search_batch}...")
        
        # Vérifier l'annulation avant d'afficher les résultats
        if not self.search_cancelled:
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
    
    def _create_circular_image(self, image, size=(60, 60)):
        """Crée une image circulaire à partir d'une image rectangulaire"""
        try:
            # Redimensionner l'image
            image = image.resize(size, Image.Resampling.LANCZOS)
            
            # Créer un masque circulaire
            mask = Image.new('L', size, 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            
            # Appliquer le masque
            output = Image.new('RGBA', size, (0, 0, 0, 0))
            output.paste(image, (0, 0))
            output.putalpha(mask)
            
            return output
        except Exception as e:
            print(f"Erreur création image circulaire: {e}")
            return image

    def _safe_add_search_result(self, video, index):
        """Version sécurisée de _add_search_result qui vérifie l'annulation"""
        if not self.search_cancelled:
            self._add_search_result(video, index)
    
    def _safe_update_status(self, batch_number):
        """Version sécurisée de la mise à jour du statut"""
        if not self.search_cancelled and hasattr(self, 'status_bar'):
            try:
                self.status_bar.config(
                    text=f"{self.search_results_count}/{len(self.all_search_results)} résultats affichés (lot {batch_number})"
                )
            except Exception as e:
                print(f"Erreur mise à jour statut: {e}")

    def _add_search_result(self, video, index):
        """Ajoute un résultat avec un style rectangle uniforme"""
        try:
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
                        # Comportement normal : télécharger
                        self._on_result_click(frame)
            
            # Bindings pour les clics simples et doubles
            duration_label.bind("<Button-1>", on_result_click)
            duration_label.bind("<Double-1>", on_result_double_click)
            title_label.bind("<Button-1>", on_result_click)
            title_label.bind("<Double-1>", on_result_double_click)
            thumbnail_label.bind("<Button-1>", on_result_click)
            thumbnail_label.bind("<Double-1>", on_result_double_click)
            
            # Ajouter des tooltips pour expliquer les interactions
            if is_channel:
                tooltip_text = "Chaîne YouTube\nDouble-clic: Ouvrir dans le navigateur\nShift + Clic: Sélection multiple"
            else:
                tooltip_text = "Vidéo YouTube\nDouble-clic: Télécharger et ajouter à la playlist\nShift + Clic: Sélection multiple"
            create_tooltip(title_label, tooltip_text)
            create_tooltip(duration_label, tooltip_text)
            create_tooltip(thumbnail_label, tooltip_text)
            result_frame.bind("<Button-1>", on_result_click)
            result_frame.bind("<Double-1>", on_result_double_click)
            
            # Événements de clic droit pour ajouter après la chanson en cours
            duration_label.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
            title_label.bind("<Button-3>", lambda e, f=result_frame: self._on_result_right_click(f))
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
            self._reset_frame_appearance(frame, '#ff6666')
            
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
                if existing_file not in self.main_playlist:
                    self.main_playlist.append(existing_file)
                    self._add_main_playlist_item(existing_file)
                    self.status_bar.config(text=f"Ajouté à la liste principale: {os.path.basename(existing_file)}")
                else:
                    self.status_bar.config(text=f"Déjà dans la liste principale: {os.path.basename(existing_file)}")
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
            # Pour la main playlist, utiliser l'ancienne méthode
            if filepath not in self.main_playlist:
                self.main_playlist.append(filepath)
                self._add_main_playlist_item(filepath, thumbnail_path)
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
                        if filepath not in self.main_playlist:
                            self.main_playlist.append(filepath)
                            self._add_main_playlist_item(filepath, thumbnail_path)
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
                
                self.root.after(0, lambda: self._add_downloaded_file(existing_file, thumbnail_path, title, url))
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
            
            # Stocker le titre pour l'affichage de progression
            self.current_download_title = safe_title
            
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
                self.root.after(0, lambda: self._add_downloaded_file(final_path, thumbnail_path, safe_title, url))
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
            # Réinitialiser le titre de téléchargement
            self.current_download_title = ""
                

    def _download_progress_hook(self, d):
        """Hook pour afficher la progression du téléchargement"""
        if d['status'] == 'downloading':
            # Extraire le pourcentage au format XX.X%
            percent_raw = d.get('_percent_str', '0.0%')
            try:
                # Extraire seulement les chiffres et le point décimal
                import re
                percent_match = re.search(r'(\d+\.?\d*)%', percent_raw)
                percent = f"{float(percent_match.group(1)):.1f}%" if percent_match else "0.0%"
            except:
                percent = "0.0%"
            
            # Extraire la vitesse au format XXX.XXKiB/s ou XXX.XXMiB/s
            speed_raw = d.get('_speed_str', '0KiB/s')
            try:
                # Extraire la vitesse avec l'unité
                speed_match = re.search(r'(\d+\.?\d*)(KiB/s|MiB/s|GiB/s)', speed_raw)
                if speed_match:
                    speed_value = float(speed_match.group(1))
                    speed_unit = speed_match.group(2)
                    speed = f"{speed_value:.2f}{speed_unit}"
                else:
                    speed = "0.00KiB/s"
            except:
                speed = "0.00KiB/s"
            
            title = self.current_download_title if self.current_download_title else "fichier"
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Téléchargement de {title} ({percent} - {speed})"
            ))

    def _add_downloaded_file(self, filepath, thumbnail_path, title, url=None):
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
        
        # Vérifier s'il y a des playlists en attente pour cette URL
        if url and url in self.pending_playlist_additions:
            pending_playlists = self.pending_playlist_additions[url]
            for playlist_name in pending_playlists:
                if playlist_name == "Main Playlist":
                    # La Main Playlist a déjà été gérée ci-dessus, ne rien faire
                    pass
                elif playlist_name in self.playlists:
                    if filepath not in self.playlists[playlist_name]:
                        self.playlists[playlist_name].append(filepath)
                        self.status_bar.config(text=f"{title} ajouté à '{playlist_name}' (en attente)")
            
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
            
            # Corriger l'URL si elle commence par //
            if url.startswith('//'):
                url = 'https:' + url
            
            response = requests.get(url, timeout=5)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img.thumbnail((80, 45), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.root.after(0, lambda: self._display_thumbnail(label, photo))
        except Exception as e:
            print(f"Erreur chargement thumbnail: {e}")

    def _load_circular_thumbnail(self, label, url):
        """Charge et affiche la miniature circulaire pour les chaînes"""
        tools._load_circular_thumbnail(self, label, url)

    def _display_thumbnail(self, label, photo):
        """Affiche la miniature dans le label"""
        tools._display_thumbnail(self, label, photo)

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
        control.generate_waveform_preview(self, filepath)

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
        tools._shuffle_remaining_playlist(self)

if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.on_closing)
    root.mainloop()
