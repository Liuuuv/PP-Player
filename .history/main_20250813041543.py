# Import centralisé depuis __init__.py
from __init__ import *
from clear_current_selection import (
    clear_all_current_song_selections,
    clear_current_song_selection,
    clear_current_song_selection_in_downloads,
    clear_current_song_selection_in_playlists
)


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
        
        # Variables pour le chargement des miniatures
        self.thumbnail_loading_timer_id = None  # ID du timer de chargement des miniatures
        
        # Variables pour l'optimisation de la recherche
        self.search_timer = None  # Timer pour le debounce de la recherche
        self.search_delay = 300  # Délai de base en millisecondes avant de lancer la recherche
        self.normalized_filenames = {}  # Cache des noms de fichiers normalisés
        self.extended_search_cache = {}  # Cache étendu incluant artiste et album pour la recherche
        
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
        
        # Variables pour gérer les callbacks différés de manière sécurisée
        self._pending_callbacks = set()  # Set des IDs de callbacks en attente
        self._app_destroyed = False  # Flag pour indiquer si l'app est détruite
        
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
        
        # Variables pour l'auto-scroll
        self.auto_scroll_enabled = False  # True si l'auto-scroll est activé
        self.manual_scroll_detected = False  # True si l'utilisateur a scrollé manuellement
        self.track_change_is_automatic = False  # True si le changement de track est automatique (fin de chanson)
        
        # Variables pour l'animation du titre
        self.title_animation_active = False  # True si l'animation du titre est en cours
        self.title_animation_id = None  # ID du timer d'animation du titre
        self.title_full_text = ""  # Texte complet du titre
        self.title_scroll_position = 0  # Position actuelle du défilement
        self.title_pause_counter = 0  # Compteur pour la pause entre les cycles
        
        # Variable pour indiquer si l'onglet bibliothèque est prêt
        self._library_tab_ready = True  # Initialisé à True par défaut
        
        # Variables pour l'affichage artiste
        self.artist_mode = False  # True si on affiche le contenu d'un artiste
        self.current_artist_name = ""  # Nom de l'artiste actuellement affiché
        self.current_artist_channel_url = ""  # URL de la chaîne de l'artiste
        self.current_artist_channel_id = None  # ID réel de la chaîne YouTube
        self.artist_notebook = None  # Notebook pour les sous-onglets artiste
        self.original_search_content = None  # Contenu original de l'onglet recherche
        self.artist_videos_thread = None  # Thread de recherche des vidéos d'artiste
        self.artist_releases_thread = None  # Thread de recherche des sorties d'artiste
        self.artist_playlists_thread = None  # Thread de recherche des playlists d'artiste
        self.artist_search_cancelled = False  # Flag pour annuler les recherches artiste
        
        # Variables pour le cache des contenus artiste
        self.artist_cache = {}  # Cache {artist_id: {'videos': [], 'releases': [], 'playlists': []}}
        self.playlist_content_cache = {}  # Cache {playlist_url: [videos]}
        
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
        
        # Gérer la fermeture propre de l'application
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # self.colorize_ttk_frames(root)

    def load_playlists(self):
        
        setup.load_playlists(self)

    def load_config(self):
        setup.load_config(self)
    
    def _count_downloaded_files(self):
        file_services._count_downloaded_files(self)

    def setup_keyboard_bindings(self):
        setup.setup_keyboard_bindings(self)
    
    def safe_after(self, delay, callback):
        """Version sécurisée de self.root.after qui évite les erreurs de callbacks orphelins"""
        if hasattr(self, '_app_destroyed') and self._app_destroyed:
            return None
            
        def safe_callback():
            try:
                if not self._app_destroyed and hasattr(self, 'root') and self.root.winfo_exists():
                    callback()
            except tk.TclError:
                pass  # Interface détruite, ignorer
            except Exception as e:
                print(f"Erreur dans callback différé: {e}")
        
        try:
            callback_id = self.root.after(delay, safe_callback)
            if hasattr(self, '_pending_callbacks'):
                self._pending_callbacks.add(callback_id)
            return callback_id
        except tk.TclError:
            return None
    
    def cancel_pending_callbacks(self):
        """Annule tous les callbacks en attente"""
        for callback_id in list(self._pending_callbacks):
            try:
                self.root.after_cancel(callback_id)
            except:
                pass
        self._pending_callbacks.clear()
    
    def on_closing(self):
        """Gère la fermeture propre de l'application"""
        print("DEBUG: Fermeture de l'application...")
        
        # Marquer que l'app est en cours de destruction
        self._app_destroyed = True
        
        # Annuler tous les callbacks en attente
        self.cancel_pending_callbacks()
        
        # Arrêter la musique
        try:
            pygame.mixer.music.stop()
        except:
            pass
        
        # Fermer l'application
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
    def copy_status_to_clipboard(self):
        """Copie le contenu de la status bar dans le presse-papier"""
        try:
            status_text = self.status_bar.cget("text")
            if status_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(status_text)
                # Feedback visuel temporaire
                original_text = status_text
                self.status_bar.config(text="✓ Copié dans le presse-papier")
                self.safe_after(1500, lambda: self.status_bar.config(text=original_text))
        except Exception as e:
            print(f"Erreur lors de la copie: {e}")

    def _update_downloads_button(self):
        """Met à jour le texte du bouton téléchargées avec le nombre actuel"""
        return library_tab.downloads._update_downloads_button(self)

    def setup_focus_bindings(self):
        return setup.setup_focus_bindings(self)
    
    def on_space_pressed(self, event):
        return inputs.on_space_pressed(self, event)
    
    def on_escape_pressed(self, event):
        """Gère l'appui sur la touche Échap"""
        return inputs.on_escape_pressed(self, event)
    
    def on_root_click(self, event):
        return
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
        return tools._update_stats_bar(self)
    
    
    def on_tab_changed(self, event):
        """Gère le changement d'onglet"""
        # Annuler la sélection multiple lors du changement d'onglet (différé pour éviter les conflits)
        if hasattr(self, 'selected_items') and self.selected_items:
            self.safe_after(50, self.clear_selection)
        
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Recherche":
            # Vous pourriez ajouter ici des actions spécifiques au changement d'onglet
            pass
        elif selected_tab == "Bibliothèque":
            # Laisser un délai pour que l'onglet se charge complètement avant les interactions
            self.safe_after(100, lambda: setattr(self, '_library_tab_ready', True))
            pass
    
    def setup_search_tab(self):
        setup.setup_search_tab(self)
    
    def setup_library_tab(self):
        setup.setup_library_tab(self)

    def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
        return tools.colorize_ttk_frames(self, widget, colors)
    
    def _on_youtube_canvas_configure(self, event):
        """Vérifie si on doit charger plus de résultats quand le canvas change"""
        return search_tab.results._on_youtube_canvas_configure(self, event)

    # def _on_youtube_scroll(self, event):
    #     """Gère le scroll de la molette dans les résultats YouTube"""
    #     inputs._on_youtube_scroll(self, event)
    
    def _should_load_more_results(self):
        """Vérifie si on doit charger plus de résultats"""
        return tools._should_load_more_results(self)

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
        try:
            if hasattr(self, 'library_content_frame') and self.library_content_frame.winfo_exists():
                for widget in self.library_content_frame.winfo_children():
                    try:
                        if widget.winfo_exists():
                            widget.destroy()
                    except tk.TclError:
                        # Widget déjà détruit, ignorer
                        continue
        except tk.TclError:
            # Container détruit, ignorer
            pass
        
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
        return library_tab.playlists.show_playlists_content(self)
    
    def _display_playlists(self):
        """Affiche toutes les playlists en grille 3x3"""
        return library_tab.playlists._display_playlists(self)
    
    def _add_playlist_card(self, parent_frame, playlist_name, songs, column):
        """Ajoute une carte de playlist avec miniatures"""
        return library_tab.playlists._add_playlist_card(self, parent_frame, playlist_name, songs, column)

    def _load_playlist_thumbnail_large(self, filepath, label):
        """Charge une miniature carrée plus grande pour une chanson dans une playlist"""
        return library_tab.playlists._load_playlist_thumbnail_large(self, filepath, label)

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
        return player._play_from_playlist(self, filepath, playlist_name)
    
    def _remove_from_playlist(self, filepath, playlist_name, item_frame, event=None):
        """Supprime une musique d'une playlist spécifique"""
        return library_tab.playlists._remove_from_playlist(self, filepath, playlist_name, item_frame, event)
    
    def _show_playlist_content_dialog(self, playlist_name):
        """Ancienne méthode - gardée pour compatibilité"""
        self._show_playlist_content_window(playlist_name)
    
    def _show_playlist_content_in_tab(self, playlist_name):
        """Affiche le contenu d'une playlist dans l'onglet bibliothèque (même style que téléchargements)"""
        return library_tab.playlists._show_playlist_content_in_tab(self, playlist_name)

    def _back_to_playlists(self):
        """Retourne à l'affichage des playlists"""
        return library_tab.playlists._back_to_playlists(self)
    
    def _on_playlist_escape(self, event):
        """Gère l'appui sur Échap dans une playlist pour retourner aux playlists"""
        return library_tab.playlists._on_playlist_escape(self, event)

    def _clear_main_playlist(self, event=None):
        """Vide complètement la liste de lecture principale (nécessite un double-clic)"""
        return search_tab.main_playlist._clear_main_playlist(self, event)
    
    def _scroll_to_current_song(self, event=None):
        """Fait défiler la liste de lecture vers la chanson en cours (même position que "piste suivante")"""
        return search_tab.main_playlist._scroll_to_current_song(self, event)
    
    def _toggle_auto_scroll(self, event=None):
        """Active/désactive l'auto-scroll automatique"""
        self.auto_scroll_enabled = not self.auto_scroll_enabled
        
        # Mettre à jour l'apparence du bouton
        if self.auto_scroll_enabled:
            self.auto_scroll_btn.config(bg="#4a8fe7", activebackground="#5a9fd8")
            self.status_bar.config(text="Auto-scroll activé")
        else:
            self.auto_scroll_btn.config(bg="#4a4a4a", activebackground="#5a5a5a")
            self.status_bar.config(text="Auto-scroll désactivé")
        
        # Réinitialiser le flag de scroll manuel
        self.manual_scroll_detected = False

    def _display_playlist_songs(self, playlist_name):
        """Affiche les musiques d'une playlist avec le même style que les téléchargements"""
        return library_tab.playlists._display_playlist_songs(self, playlist_name)

    def _add_playlist_song_item(self, filepath, playlist_name, song_index):
        """Ajoute un élément de musique de playlist avec le même visuel que les téléchargements"""
        # return library_tab.playlists._add_playlist_song_item(self, filepath, playlist_name, song_index)
        return tools._add_song_item(self, filepath, self.playlist_content_container, playlist_name=playlist_name, song_index=song_index)

    def _remove_from_playlist_view(self, filepath, playlist_name, event=None):
        """Supprime une musique de la playlist et rafraîchit l'affichage"""
        return library_tab.playlists._remove_from_playlist_view(self, filepath, playlist_name, event)

    def _update_playlist_title(self, playlist_name):
        """Met à jour le titre de la playlist avec le nombre de chansons"""
        return library_tab.playlists._update_playlist_title(self, playlist_name)
    
    def _play_playlist_from_song(self, playlist_name, song_index):
        """Lance la playlist depuis une musique spécifique"""
        return library_tab.playlists._play_playlist_from_song(self, playlist_name, song_index)
    
    def load_downloaded_files(self):
        """Charge et affiche tous les fichiers du dossier downloads"""
        return library_tab.downloads.load_downloaded_files(self)
    
    def play_all_downloads_ordered(self):
        """Joue toutes les musiques téléchargées dans l'ordre"""
        return library_tab.downloads.play_all_downloads_ordered(self)

    def play_all_downloads_shuffle(self):
        """Joue toutes les musiques téléchargées en mode aléatoire"""
        return library_tab.downloads.play_all_downloads_shuffle(self)
    
    def _display_filtered_downloads(self, files_to_display):
        """Affiche une liste filtrée de fichiers téléchargés (optimisé)"""
        return library_tab.downloads._display_filtered_downloads(self, files_to_display)
    
    def _restore_search_binding(self):
        """Restaure le binding de recherche après un refresh"""
        return library_tab.downloads._restore_search_binding(self)
    
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
        # return library_tab.downloads._add_download_item_fast(self, filepath)
        return tools._add_song_item(self, filepath, self.downloads_container)
    
    def _start_thumbnail_loading(self, files_to_display, container):
        """Lance le chargement différé des miniatures et durées"""
        # return library_tab.downloads._start_thumbnail_loading(self, files_to_display)
        return tools._start_thumbnail_loading(self, files_to_display, container)
        
    def _load_next_thumbnail(self, container):
        """Charge la prochaine miniature dans la queue"""
        # return library_tab.downloads._load_next_thumbnail(self)
        return tools._load_next_thumbnail(self, container)
    
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
        return library_tab.downloads._get_adaptive_search_delay(self, query)
    
    def _on_library_search_change(self, event):
        """Appelée à chaque changement dans la barre de recherche (avec debounce différentiel)"""
        return library_tab.downloads._on_library_search_change(self, event)
    
    def _build_extended_search_cache(self, filepath):
        """Construit le cache de recherche étendu pour un fichier (nom + artiste + album)"""
        return library_tab.downloads._build_extended_search_cache(self, filepath)

    def _perform_library_search(self):
        """Effectue la recherche réelle (appelée après le délai) - version étendue incluant artiste et album"""
        return library_tab.downloads._perform_library_search(self)

    def _clear_library_search(self):
        """Efface la recherche et affiche tous les fichiers"""
        return library_tab.downloads._clear_library_search(self)
    
    def _on_search_entry_change(self, event):
        """Appelée quand le contenu du champ de recherche change"""
        return search_tab.results._on_search_entry_change(self, event)

    def _clear_youtube_search(self):
        """Efface la recherche YouTube et vide les résultats"""
        return search_tab.results._clear_youtube_search(self)
    
    def _show_current_song_thumbnail(self):
        """Affiche la miniature de la chanson en cours dans la frame dédiée"""
        return search_tab.results._show_current_song_thumbnail(self)
    
    # def _add_download_item(self, filepath):
    #     """Ajoute un élément téléchargé avec le même visuel que les résultats de recherche, visuel"""
    #     return library_tab.downloads._add_download_item(self, filepath)
    
    def _play_after_current(self, filepath):
        """Place une musique juste après celle qui joue actuellement et la lance"""
        return player._play_after_current(self, filepath)

    def _load_large_thumbnail(self, filepath, label):
        """Charge une grande miniature carrée pour l'affichage principal"""
        return search_tab.results._load_large_thumbnail(self, filepath, label)
    
    def _load_download_thumbnail(self, filepath, label):
        """Charge la miniature pour un fichier téléchargé"""
        return tools._load_download_thumbnail(self, filepath, label)

    def _truncate_text_for_display(self, text, max_width_pixels=200, max_lines=1, font_family='TkDefaultFont', font_size=9):
        """Tronque le texte pour l'affichage avec des '...' si nécessaire"""
        return tools._truncate_text_for_display(self, text, max_width_pixels, max_lines, font_family, font_size)
    
    def _get_audio_duration(self, filepath):
        """Récupère la durée d'un fichier audio"""
        return tools._get_audio_duration(self, filepath)
    
    def _get_audio_metadata(self, filepath):
        """Récupère les métadonnées d'un fichier audio (artiste et album)"""
        return tools._get_audio_metadata(self, filepath)
    
    def _format_artist_album_info(self, artist, album, filepath=None):
        """Formate les informations d'artiste, d'album et de date pour l'affichage"""
        return tools._format_artist_album_info(self, artist, album, filepath)
    
    def _extract_and_save_metadata(self, info, filepath):
        """Extrait les métadonnées depuis les informations YouTube et les sauvegarde dans le fichier MP3"""
        return tools._extract_and_save_metadata(self, info, filepath)
    
    def clear_thumbnail_label(self):
        """Efface la grande miniature actuelle"""
        # Nettoyer la frame précédente
        try:
            if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame.winfo_exists():
                for widget in self.thumbnail_frame.winfo_children():
                    try:
                        if widget.winfo_exists():
                            widget.destroy()
                    except tk.TclError:
                        # Widget déjà détruit, ignorer
                        continue
        except tk.TclError:
            # Container détruit, ignorer
            pass

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

    # def _show_playlist_menu(self, filepath, button):
    #     """Affiche un menu déroulant pour choisir la playlist"""
    #     import tkinter.ttk as ttk
        
    #     # Créer un menu contextuel
    #     menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
    #                   activebackground='#4a8fe7', activeforeground='white')
        
    #     # Ajouter les playlists existantes
    #     for playlist_name in self.playlists.keys():
    #         menu.add_command(
    #             label=f"Ajouter à '{playlist_name}'",
    #             command=lambda name=playlist_name: self._add_to_specific_playlist(filepath, name)
    #         )
        
    #     menu.add_separator()
        
    #     # Option pour créer une nouvelle playlist
    #     menu.add_command(
    #         label="Créer nouvelle playlist...",
    #         command=lambda: self._create_new_playlist_dialog(filepath)
    #     )
        
    #     # Afficher le menu à la position du bouton
    #     try:
    #         # Obtenir la position du bouton
    #         x = button.winfo_rootx() if button else self.root.winfo_pointerx()
    #         y = button.winfo_rooty() + button.winfo_height() if button else self.root.winfo_pointery()
    #         menu.post(x, y)
    #     except:
    #         # Fallback si on ne peut pas obtenir la position
    #         menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def add_to_main_playlist(self, filepath, thumbnail_path=None, song_index=None, show_status=True, allow_duplicates=False):
        """Fonction centralisée pour ajouter une musique à la main playlist
        
        Args:
            filepath: Chemin vers le fichier audio
            thumbnail_path: Chemin vers la miniature (optionnel)
            song_index: Index spécifique pour la chanson (optionnel)
            show_status: Afficher le message de statut (défaut: True)
            allow_duplicates: Permettre les doublons (défaut: False)
        """
        return search_tab.main_playlist.add_to_main_playlist(self, filepath, thumbnail_path, song_index, show_status, allow_duplicates)

    def _add_to_specific_playlist(self, filepath, playlist_name):
        """Ajoute un fichier à une playlist spécifique"""
        return tools._add_to_specific_playlist(self, filepath, playlist_name)

    def _create_new_playlist_dialog(self, filepath=None):
        """Dialogue pour créer une nouvelle playlist"""
        return tools._create_new_playlist_dialog(self, filepath)

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
        return tools.add_to_playlist(self)

    def show_output_menu(self):
        """Affiche un menu déroulant pour choisir le périphérique de sortie audio"""
        return ui_menus.show_output_menu(self)

    def change_output_device(self, selected_device, device_name):
        """Change le périphérique de sortie audio"""
        return tools.change_output_device(self, selected_device, device_name)

    def _detect_current_audio_device(self):
        """Détecte le périphérique audio actuellement utilisé"""
        return tools._detect_current_audio_device(self)

    def show_stats_menu(self):
        """Affiche un menu avec les statistiques d'écoute"""
        return ui_menus.show_stats_menu(self)

    def _reset_stats(self):
        """Remet à zéro toutes les statistiques"""
        return stats._reset_stats(self)

    def _update_current_song_stats(self):
        """Met à jour les statistiques de la chanson en cours"""
        return stats._update_current_song_stats(self)

    def _start_song_stats_tracking(self, song_path):
        """Démarre le suivi des statistiques pour une nouvelle chanson"""
        return stats._start_song_stats_tracking(self, song_path)

    def _pause_song_stats_tracking(self):
        """Met en pause le suivi des statistiques"""
        return stats._pause_song_stats_tracking(self)

    def _resume_song_stats_tracking(self):
        """Reprend le suivi des statistiques"""
        return stats._resume_song_stats_tracking(self)

    # def show_output_devices(self):
    #     """Affiche une fenêtre pour choisir le périphérique de sortie audio"""
    #     try:
    #         # Obtenir la liste des périphériques audio
    #         import pygame._sdl2.audio
    #         devices = pygame._sdl2.audio.get_audio_device_names()
            
    #         if not devices:
    #             messagebox.showinfo("Périphériques audio", "Aucun périphérique audio trouvé")
    #             return
            
    #         # Créer une fenêtre de sélection (style blanc comme la sélection multiple)
    #         device_window = tk.Toplevel(self.root)
    #         device_window.title("Périphérique de sortie")
    #         device_window.geometry("350x250")
    #         device_window.configure(bg='white')
    #         device_window.resizable(False, False)
            
    #         # Centrer la fenêtre
    #         device_window.transient(self.root)
    #         device_window.grab_set()
            
    #         # Label d'instruction
    #         instruction_label = tk.Label(
    #             device_window, 
    #             text="Sélectionnez un périphérique de sortie :",
    #             bg='white', 
    #             fg='black',
    #             font=('Arial', 10, 'bold')
    #         )
    #         instruction_label.pack(pady=15)
            
    #         # Frame pour la liste
    #         list_frame = tk.Frame(device_window, bg='white')
    #         list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
            
    #         # Listbox avec scrollbar
    #         scrollbar = tk.Scrollbar(list_frame)
    #         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
    #         device_listbox = tk.Listbox(
    #             list_frame,
    #             yscrollcommand=scrollbar.set,
    #             bg='white',
    #             fg='black',
    #             selectbackground='#4a8fe7',
    #             selectforeground='white',
    #             font=('Arial', 9),
    #             relief='solid',
    #             bd=1
    #         )
    #         device_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    #         scrollbar.config(command=device_listbox.yview)
            
    #         # Ajouter les périphériques à la liste
    #         for device in devices:
    #             device_listbox.insert(tk.END, device.decode('utf-8') if isinstance(device, bytes) else device)
            
    #         # Frame pour les boutons
    #         button_frame = tk.Frame(device_window, bg='white')
    #         button_frame.pack(pady=15)
            
    #         def apply_device():
    #             selection = device_listbox.curselection()
    #             if selection:
    #                 selected_device = devices[selection[0]]
    #                 device_name = selected_device.decode('utf-8') if isinstance(selected_device, bytes) else selected_device
                    
    #                 try:
    #                     # Arrêter la musique actuelle
    #                     was_playing = pygame.mixer.music.get_busy() and not self.paused
    #                     current_pos = self.current_time if was_playing else 0
                        
    #                     # Réinitialiser pygame mixer avec le nouveau périphérique
    #                     pygame.mixer.quit()
    #                     pygame.mixer.init(devicename=selected_device, frequency=44100, size=-16, channels=2, buffer=4096)
                        
    #                     # Reprendre la lecture si nécessaire
    #                     if was_playing and self.main_playlist and self.current_index < len(self.main_playlist):
    #                         current_song = self.main_playlist[self.current_index]
    #                         pygame.mixer.music.load(current_song)
    #                         pygame.mixer.music.play(start=current_pos)
    #                         self._apply_volume()
                        
    #                     self.status_bar.config(text=f"Périphérique changé: {device_name}")
    #                     device_window.destroy()
                        
    #                 except Exception as e:
    #                     messagebox.showerror("Erreur", f"Impossible de changer le périphérique:\n{str(e)}")
    #             else:
    #                 messagebox.showwarning("Sélection", "Veuillez sélectionner un périphérique")
            
    #         def cancel():
    #             device_window.destroy()
            
    #         # Boutons (style blanc)
    #         apply_btn = tk.Button(
    #             button_frame,
    #             text="Appliquer",
    #             command=apply_device,
    #             bg='#4a8fe7',
    #             fg='white',
    #             activebackground='#5a9fd8',
    #             activeforeground='white',
    #             font=('Arial', 9),
    #             padx=20,
    #             relief='flat',
    #             bd=1
    #         )
    #         apply_btn.pack(side=tk.LEFT, padx=5)
            
    #         cancel_btn = tk.Button(
    #             button_frame,
    #             text="Annuler",
    #             command=cancel,
    #             bg='#e0e0e0',
    #             fg='black',
    #             activebackground='#d0d0d0',
    #             activeforeground='black',
    #             font=('Arial', 9),
    #             padx=20,
    #             relief='flat',
    #             bd=1
    #         )
    #         cancel_btn.pack(side=tk.LEFT, padx=5)
            
    #     except Exception as e:
    #         messagebox.showerror("Erreur", f"Impossible d'accéder aux périphériques audio:\n{str(e)}")

    def _truncate_text_to_width(self, text, font, max_width):
        """Tronque le texte pour qu'il tienne dans la largeur spécifiée"""
        return tools._truncate_text_to_width(text, font, max_width)

    def update_is_in_queue(self, song_item):
        return tools.update_is_in_queue(self, song_item)

    def _add_main_playlist_item(self, filepath, thumbnail_path=None, song_index=None):
        """Ajoute un élément à la main playlist avec un style rectangle uniforme"""
        return search_tab.main_playlist._add_main_playlist_item(self, filepath, thumbnail_path, song_index)
        # return tools._add_song_item(self, filepath, thumbnail_path, song_index)

    def select_playlist_item(self, item_frame=None, index=None, auto_scroll=True):
        """Met en surbrillance l'élément sélectionné dans la playlist
        
        Args:
            item_frame: Frame de l'élément à sélectionner
            index: Index de l'élément à sélectionner (alternatif à item_frame)
            auto_scroll: Si True, fait défiler automatiquement vers l'élément (défaut: True)
        """
        return search_tab.main_playlist.select_playlist_item(self, item_frame, index, auto_scroll)

    def _set_item_colors(self, item_frame, bg_color):
        """Change uniquement la couleur de fond des éléments d'un item de playlist"""
        return tools._set_item_colors(self, item_frame, bg_color)
    
    def _smooth_scroll_to_position(self, target_position, duration=500):
        """Anime le scroll vers une position cible avec une courbe ease-in-out"""
        return search_tab.main_playlist._smooth_scroll_to_position(self, target_position, duration)
    
    def _start_title_animation(self, full_title):
        """Démarre l'animation de défilement du titre si nécessaire"""
        return control._start_title_animation(self, full_title)

    def _stop_title_animation(self):
        """Arrête l'animation du titre"""
        return control._stop_title_animation(self)

    def _animate_title_step(self):
        """Une étape de l'animation du titre"""
        return control._animate_title_step(self)
    
    def _get_scrolled_title_text(self, full_text, scroll_pos, max_width_pixels):
        """Génère le texte visible avec défilement à la position donnée"""
        return control._get_scrolled_title_text(self, full_text, scroll_pos, max_width_pixels)
    
    def toggle_item_selection(self, filepath, frame):
        """Ajoute ou retire un élément de la sélection multiple"""
        return tools.toggle_item_selection(self, filepath, frame)
    
    def clear_selection(self):
        """Efface toute la sélection multiple"""
        return tools.clear_selection(self)
    
    def show_selection_menu(self, event):
        """Affiche un menu contextuel pour sélectionner les playlists"""
        return tools.show_selection_menu(self, event)
    
    def _show_single_file_menu(self, event, filepath):
        """Affiche un menu contextuel pour un seul fichier"""
        return tools._show_single_file_menu(self, event, filepath)
    
    def _safe_add_to_main_playlist(self, filepath):
        """Version sécurisée de add_to_main_playlist"""
        return tools._safe_add_to_main_playlist(self, filepath)
    
    def _safe_add_to_queue_first(self, filepath):
        """Version sécurisée de _add_to_queue_first"""
        return tools._safe_add_to_queue_first(self, filepath)
    
    def _safe_add_to_queue(self, filepath):
        """Version sécurisée de _add_to_queue"""
        return tools._safe_add_to_queue(self, filepath)
    
    def _safe_add_to_specific_playlist(self, filepath, playlist_name):
        """Version sécurisée de _add_to_specific_playlist"""
        return tools._safe_add_to_specific_playlist(self, filepath, playlist_name)
    
    def _safe_create_new_playlist_dialog(self, filepath, is_youtube_video):
        """Version sécurisée de _create_new_playlist_dialog"""
        return tools._safe_create_new_playlist_dialog(self, filepath, is_youtube_video)

    def add_selection_to_main_playlist(self):
        """Ajoute tous les éléments sélectionnés à la fin de la main playlist dans l'ordre"""
        return tools.add_selection_to_main_playlist(self)
    
    def add_selection_to_queue_first(self):
        """Ajoute tous les éléments sélectionnés au début de la queue (lire ensuite)"""
        return tools.add_selection_to_queue_first(self)
    
    def add_selection_to_queue_last(self):
        """Ajoute tous les éléments sélectionnés à la fin de la queue (lire bientôt)"""
        return tools.add_selection_to_queue_last(self)

    def create_new_playlist_from_selection(self, has_youtube_videos):
        """Demande le nom d'une nouvelle playlist et y ajoute la sélection"""
        return tools.create_new_playlist_from_selection(self, has_youtube_videos)

    def update_selection_display(self):
        """Met à jour l'affichage du nombre d'éléments sélectionnés"""
        return tools.update_selection_display(self)

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
            # Ajouter l'URL aux téléchargements en cours pour éviter les doublons
            if video_url not in self.current_downloads:
                self.current_downloads.add(video_url)
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
        finally:
            # Retirer l'URL des téléchargements en cours
            if video_url in self.current_downloads:
                self.current_downloads.remove(video_url)
    
    def add_selection_to_playlist(self, playlist_name):
        """Ajoute tous les éléments sélectionnés à une playlist"""
        return tools.add_selection_to_playlist(self, playlist_name)
    
    def create_playlist_from_selection(self):
        """Crée une nouvelle playlist avec les éléments sélectionnés"""
        return library_tab.playlists.create_playlist_from_selection(self)

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
        return tools.download_and_create_playlist_from_selection(self)

    def _download_youtube_selection(self, youtube_urls, target_playlist):
        """Télécharge une liste d'URLs YouTube et les ajoute à la playlist cible"""
        return services.downloading.download_youtube_selection(self, youtube_urls, target_playlist)

    def hide_queue_indicator(self, song_frame):
        """Cache l'indicateur de queue"""
        return tools.hide_queue_indicator(self, song_frame)

    def show_queue_indicator(self, song_frame):
        """Affiche l'indicateur de queue"""
        return tools.show_queue_indicator(self, song_frame)

    def update_visibility_queue_indicator(self, song_frame):
        """Met à jour la visibilité de l'indicateur de queue pour une chanson donnée"""
        return tools.update_visibility_queue_indicator(self, song_frame)

    def select_library_item_from_filepath(self, current_filepath):
        """Met en surbrillance l'élément sélectionné dans la bibliothèque"""
        # return library_tab.downloads.select_library_item(self, current_filepath)
        return tools.select_song_item_from_filepath(self, current_filepath, self.downloads_container)

    def select_playlist_content_item_from_filepath(self, current_filepath):
        """Met en surbrillance l'élément sélectionné dans l'affichage du contenu d'une playlist"""
        if hasattr(self, 'playlist_content_container'):
            # return library_tab.playlists.select_playlist_content_item(self, current_filepath)
            return tools.select_song_item_from_filepath(self, current_filepath, self.playlist_content_container)

    def _remove_main_playlist_item(self, filepath, frame, event=None, song_index=None):
        """Supprime un élément de la main playlist"""
        return search_tab.main_playlist._remove_main_playlist_item(self, filepath, frame, event=event, song_index=song_index)

    def _delete_from_downloads(self, filepath, frame):
        """Supprime définitivement un fichier du dossier downloads"""
        return tools._delete_from_downloads(self, filepath, frame)

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
        return tools.play_track(self)

    def _on_mousewheel(self, event, canvas):
        """Gère le défilement avec la molette de souris"""
        # Détecter le scroll manuel sur la playlist pour désactiver l'auto-scroll
        if hasattr(self, 'playlist_canvas') and canvas == self.playlist_canvas:
            if hasattr(self, 'auto_scroll_enabled') and self.auto_scroll_enabled:
                self.manual_scroll_detected = True
                self.auto_scroll_enabled = False
                self.auto_scroll_btn.config(bg="#4a4a4a", activebackground="#5a5a5a")
                self.status_bar.config(text="Auto-scroll désactivé (scroll manuel détecté)")
        
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
        # Si on est en mode artiste, revenir à la recherche normale
        if hasattr(self, 'artist_mode') and self.artist_mode:
            self._return_to_search()
        
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
        return search_tab.results._start_new_search(self)
    def _perform_initial_search(self, query):
        """Effectue une recherche initiale de 10 résultats seulement"""
        return search_tab.results._perform_initial_search(self, query)

    def _filter_search_results(self, entries):
        """Filtre les résultats selon les cases à cocher Artists et Tracks"""
        return search_tab.results._filter_search_results(self, entries)

    def _on_filter_change(self):
        """Appelée quand les cases à cocher changent"""
        return search_tab.results._on_filter_change(self)

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
        return search_tab.results._display_new_results(self, new_results)

    def _clear_results(self):
        """Vide le container de résultats et gère l'affichage des frames"""
        return search_tab.results._clear_results(self)

    def _show_search_results(self):
        """Affiche le canvas de résultats et masque la frame thumbnail"""
        return search_tab.results._show_search_results(self)

    def _update_results_counter(self):
        """Met à jour le compteur de résultats affiché"""
        return tools._update_results_counter(self)

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
            metadata_label = None  # Initialiser à None par défaut
            
            if not is_channel:
                
                # Extraire les métadonnées depuis les informations YouTube
                artist = video.get('uploader', '')
                album = video.get('album', '')
                
                # print(video) # debug
                
                # Créer un frame pour les métadonnées afin de rendre l'artiste cliquable
                if artist or album:
                    metadata_frame = tk.Frame(text_frame, bg='#4a4a4a')
                    metadata_frame.grid(row=1, column=0, sticky='ew', pady=(0, 2))
                    metadata_frame.columnconfigure(0, weight=1)
                    
                    # Construire le texte des métadonnées avec des labels séparés
                    parts = []
                    if artist:
                        # Label cliquable pour l'artiste
                        artist_label = tk.Label(
                            metadata_frame,
                            text=artist,
                            bg='#4a4a4a',
                            fg='#88aaff',  # Couleur bleue pour indiquer que c'est cliquable
                            font=('TkDefaultFont', 8, 'underline'),
                            anchor='w',
                            justify='left',
                            cursor='hand2'
                        )
                        artist_label.pack(side=tk.LEFT)
                        
                        # Binding pour le clic sur l'artiste
                        def on_artist_click(event, artist_name=artist, video_data=video):
                            self._show_artist_content(artist_name, video_data)
                        
                        artist_label.bind("<Button-1>", on_artist_click)
                        create_tooltip(artist_label, f"Clic pour voir toutes les vidéos de {artist}")
                        
                        # Ajouter le séparateur si on a un album
                        if album:
                            separator_label = tk.Label(
                                metadata_frame,
                                text=" • ",
                                bg='#4a4a4a',
                                fg='#cccccc',
                                font=('TkDefaultFont', 8),
                                anchor='w'
                            )
                            separator_label.pack(side=tk.LEFT)
                    
                    # Ajouter l'album s'il existe
                    if album:
                        album_label = tk.Label(
                            metadata_frame,
                            text=album,
                            bg='#4a4a4a',
                            fg='#cccccc',
                            font=('TkDefaultFont', 8),
                            anchor='w',
                            justify='left'
                        )
                        album_label.pack(side=tk.LEFT)
                    
                    # Conserver la référence pour les bindings ultérieurs
                    metadata_label = metadata_frame  # Pour compatibilité avec le code existant
            
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
            duration_label.bind("<ButtonPress-1>", on_result_click)
            duration_label.bind("<Double-1>", on_result_double_click)
            text_frame.bind("<ButtonPress-1>", on_result_click)
            text_frame.bind("<Double-1>", on_result_double_click)
            title_label.bind("<ButtonPress-1>", on_result_click)
            title_label.bind("<Double-1>", on_result_double_click)
            if metadata_label is not None:  # Ajouter binding pour metadata_frame s'il existe
                metadata_label.bind("<ButtonPress-1>", on_result_click)
                metadata_label.bind("<Double-1>", on_result_double_click)
            thumbnail_label.bind("<ButtonPress-1>", on_result_click)
            thumbnail_label.bind("<Double-1>", on_result_double_click)
            
            # Ajouter des tooltips pour expliquer les interactions
            if is_channel:
                tooltip_text = "Chaîne YouTube\nDouble-clic: Ouvrir dans le navigateur\nShift + Clic: Sélection multiple"
            else:
                tooltip_text = "Vidéo YouTube\nDouble-clic: Télécharger (sans ajouter à la playlist)\nDrag vers la droite: Télécharger et ajouter à la queue\nDrag vers la gauche: Télécharger et placer en premier dans la queue\nShift + Clic: Sélection multiple"
            create_tooltip(text_frame, tooltip_text)
            create_tooltip(title_label, tooltip_text)
            if metadata_label is not None:
                create_tooltip(metadata_label, tooltip_text)
            create_tooltip(duration_label, tooltip_text)
            create_tooltip(thumbnail_label, tooltip_text)
            result_frame.bind("<ButtonPress-1>", on_result_click)
            result_frame.bind("<Double-1>", on_result_double_click)
            
            # Configuration du drag-and-drop pour les vidéos
            if not is_channel:
                self.drag_drop_handler.setup_drag_drop(
                    result_frame, 
                    video_data=video, 
                    item_type="youtube"
                )
            
            # Événements de clic droit pour ajouter après la chanson en cours
            duration_label.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            text_frame.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            title_label.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            if metadata_label is not None:  # Ajouter binding pour metadata_frame s'il existe
                metadata_label.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            thumbnail_label.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            result_frame.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            

            
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
    
    def _on_result_right_click(self, event, frame):
        """Gère le clic droit sur un résultat pour afficher le menu des playlists"""
        # Initialiser le drag pour le clic droit (seulement pour les vidéos, pas les chaînes)
        if hasattr(frame, 'video_data'):
            video_url = frame.video_data.get('url', '')
            is_channel = ("https://www.youtube.com/channel/" in video_url or 
                         "https://www.youtube.com/@" in video_url)
            if not is_channel:
                self.drag_drop_handler.setup_drag_start(event, frame)
        
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
        return tools._show_pending_playlist_menu(self, video, frame, url)
    
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
        return tools._add_youtube_to_playlist(self, video, frame, playlist_name)
    
    def _create_new_playlist_dialog_youtube(self, video, frame):
        """Dialogue pour créer une nouvelle playlist et y ajouter une vidéo YouTube"""
        return tools._create_new_playlist_dialog_youtube(self, video, frame)

    def _download_and_add_to_playlist_thread(self, video, frame, playlist_name):
        """Thread pour télécharger une vidéo et l'ajouter à une playlist"""
        return services.downloading._download_and_add_to_playlist_thread(self, video, frame, playlist_name)
    
    def _add_downloaded_to_playlist(self, filepath, thumbnail_path, title, playlist_name, url=None):
        """Ajoute un fichier téléchargé à une playlist spécifique (à appeler dans le thread principal)"""
        return tools._add_downloaded_file_to_playlist(filepath, thumbnail_path, title, playlist_name, url)

    def _reset_frame_appearance(self, frame, bg_color, error=False):
        """Remet l'apparence d'un frame de manière sécurisée"""
        try:
            if frame.winfo_exists():
                frame.config(bg=bg_color)
                
                # Marquer le frame comme étant en téléchargement
                if bg_color == '#ff6666':
                    frame.is_downloading = True
                    frame.download_color = bg_color
                elif bg_color == '#4a4a4a':  # Couleur normale = fin de téléchargement
                    frame.is_downloading = False
                    frame.download_color = None
                else:
                    # Pour les autres couleurs (erreur, etc.), garder l'état actuel
                    pass
                
                # Appliquer la couleur à tous les widgets possibles (par nom d'attribut)
                widgets_to_update = ['title_label', 'duration_label', 'thumbnail_label', 'text_frame', 'count_label']
                
                for widget_name in widgets_to_update:
                    if hasattr(frame, widget_name):
                        widget = getattr(frame, widget_name)
                        if widget and widget.winfo_exists():
                            try:
                                widget.config(bg=bg_color)
                            except tk.TclError:
                                # Le widget a été détruit, ignorer
                                pass
                
                # Appliquer aussi à tous les widgets enfants directs (pour être sûr)
                try:
                    for child in frame.winfo_children():
                        if child.winfo_exists():
                            try:
                                # Essayer de changer la couleur de fond
                                child.config(bg=bg_color)
                            except (tk.TclError, AttributeError):
                                # Certains widgets n'ont pas de bg, ignorer
                                pass
                except tk.TclError:
                    # Le frame a été détruit, ignorer
                    pass
                
                # Couleurs de texte spécifiques
                if hasattr(frame, 'title_label') and frame.title_label.winfo_exists():
                    if error:
                        frame.title_label.config(fg='#333333')
                    elif bg_color == '#ff6666':  # Rouge pour téléchargement
                        frame.title_label.config(fg='#cccccc')
                    else:
                        frame.title_label.config(fg='white')
                        
                if hasattr(frame, 'duration_label') and frame.duration_label.winfo_exists():
                    if error:
                        frame.duration_label.config(fg='#666666')
                    elif bg_color == '#ff6666':  # Rouge pour téléchargement
                        frame.duration_label.config(fg='#aaaaaa')
                    else:
                        frame.duration_label.config(fg='#cccccc')
                        
        except tk.TclError:
            # Le widget a été détruit, ignorer l'erreur
            pass
    
    def _download_and_add_after_current(self, video, frame):
        """Télécharge une vidéo et l'ajoute après la chanson en cours"""
        return services.downloading._download_and_add_after_current(self, video, frame)
    
    def setup_controls(self):
        setup.setup_controls(self)

    def _refresh_playlist_display(self):
        """Rafraîchit l'affichage de la main playlist"""
        # Protection contre les appels multiples rapides
        if not hasattr(self, '_last_refresh_time'):
            self._last_refresh_time = 0
        
        current_time = time.time()
        if current_time - self._last_refresh_time < 0.1:  # 100ms de protection
            return
        self._last_refresh_time = current_time
        
        try:
            # Vérifier que le container existe encore
            if not hasattr(self, 'playlist_container'):
                return
                
            if not self.playlist_container.winfo_exists():
                return
                
            # Vider le container actuel
            for widget in self.playlist_container.winfo_children():
                try:
                    if widget.winfo_exists():
                        widget.destroy()
                except tk.TclError:
                    # Widget déjà détruit, ignorer
                    continue
            
            # Recréer tous les éléments avec les bons index
            for i, filepath in enumerate(self.main_playlist):
                self._add_main_playlist_item(filepath, song_index=i)
            
            # Remettre en surbrillance la chanson en cours si elle existe (sans scrolling automatique)
            if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
                self.select_playlist_item(index=self.current_index, auto_scroll=False)
                
        except tk.TclError as e:
            # Container détruit ou problème avec l'interface, ignorer silencieusement
            print(f"DEBUG: Erreur _refresh_playlist_display ignorée: {e}")
            pass
        except Exception as e:
            print(f"Erreur dans _refresh_playlist_display: {e}")
    
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
        return services.downloading._download_youtube_thumbnail(self, video_info, filepath)


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
    
    def _update_downloads_queue_visual(self):
        """Met à jour seulement l'affichage visuel des barres noires de queue sans recharger toute la liste"""
        return library_tab.downloads._update_downloads_queue_visual(self)

    def _load_thumbnail(self, label, url):
        """Charge et affiche la miniature"""
        return tools._load_thumbnail(self, label, url)

    def _load_circular_thumbnail(self, label, url):
        """Charge et affiche la miniature circulaire pour les chaînes"""
        return tools._load_circular_thumbnail(self, label, url)

    def _display_thumbnail(self, label, photo):
        """Affiche la miniature dans le label"""
        return tools._display_thumbnail(self, label, photo)

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
        return control.prev_track(self)

    def next_track(self):
        return control.next_track(self)
    
    def next_track_manual(self):
        """Passe à la chanson suivante (changement manuel par bouton)"""
        # Marquer le changement comme manuel
        self.track_change_is_automatic = False
        return control.next_track(self)
    
    def prev_track_manual(self):
        """Passe à la chanson précédente (changement manuel par bouton)"""
        # Marquer le changement comme manuel
        self.track_change_is_automatic = False
        return control.prev_track(self)
    
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
                    # Marquer le changement comme automatique (fin de chanson)
                    self.track_change_is_automatic = True
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
    
    def _show_artist_content(self, artist_name, video_data):
        """Affiche le contenu d'un artiste dans la zone de recherche YouTube"""
        try:
            # Vérifier si on est déjà en mode artiste avec le même artiste
            if self.artist_mode and self.current_artist_name == artist_name:
                return
            
            # Si on est déjà en mode artiste mais avec un artiste différent, nettoyer l'ancien
            if self.artist_mode and self.current_artist_name != artist_name:
                self._return_to_search()
            
            # S'assurer qu'on est sur l'onglet "Recherche"
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if current_tab != "Recherche":
                # Trouver l'index de l'onglet "Recherche" et le sélectionner
                for i in range(self.notebook.index("end")):
                    if self.notebook.tab(i, "text") == "Recherche":
                        self.notebook.select(i)
                        break
            
            # Passer en mode artiste
            self.artist_mode = True
            self.current_artist_name = artist_name
            
            # Essayer de récupérer l'URL de la chaîne depuis les métadonnées vidéo
            self.current_artist_channel_url = video_data.get('channel_url', '')
            if not self.current_artist_channel_url:
                # Fallback: construire l'URL de recherche avec plusieurs tentatives
                import urllib.parse
                # Nettoyer le nom de l'artiste pour l'URL
                clean_artist_name = artist_name.replace(' ', '').replace('　', '').replace('/', '')
                # Encoder les caractères spéciaux
                encoded_artist_name = urllib.parse.quote(clean_artist_name, safe='')
                self.current_artist_channel_url = f"https://www.youtube.com/@{encoded_artist_name}"
            
            # Sauvegarder l'état actuel des résultats
            self._save_current_search_state()
            
            # S'assurer que la zone YouTube est visible
            self._show_search_results()
            
            # Forcer la mise à jour de l'affichage
            self.root.update_idletasks()
            
            # Créer les onglets qui remplacent les résultats
            self._create_artist_tabs()
            
            # Réinitialiser le flag d'annulation des recherches artiste
            self.artist_search_cancelled = False
            
            # Lancer la recherche complète de l'artiste en arrière-plan
            self._search_artist_content()
            
            self.status_bar.config(text=f"Chargement du contenu de {artist_name}...")
            
        except Exception as e:
            print(f"Erreur lors de l'affichage du contenu d'artiste: {e}")
            self.status_bar.config(text=f"Erreur: {e}")
    
    def _save_current_search_state(self):
        """Sauvegarde l'état actuel des résultats de recherche"""
        return search_tab.results._save_current_search_state(self)

    def _create_artist_tabs(self):
        """Crée les onglets Musiques et Sorties dans la zone YouTube"""
        # Si on était déjà en mode artiste, détruire l'ancien notebook pour éviter la duplication
        if hasattr(self, 'artist_notebook') and self.artist_notebook:
            try:
                # Détruire complètement l'ancien notebook et ses éléments
                parent = self.artist_notebook.master
                parent.destroy()  # Détruire le container complet pour éviter les boutons dupliqués
                self.artist_notebook = None
            except:
                pass
        
        # Nettoyer tout le contenu de youtube_results_frame
        for widget in self.youtube_results_frame.winfo_children():
            try:
                widget.destroy()
            except:
                pass
        
        # Cacher le canvas et la scrollbar des résultats
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
            self.youtube_canvas.pack_forget()
        
        if hasattr(self, 'scrollbar') and self.scrollbar.winfo_exists():
            self.scrollbar.pack_forget()
        
        # Cacher aussi la frame thumbnail si elle est visible
        if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame.winfo_exists():
            self.thumbnail_frame.pack_forget()
        
        # Créer un frame container principal
        main_container = tk.Frame(self.youtube_results_frame, bg='#3d3d3d')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Ajouter le bouton croix avec le même style que stats.png et output.png
        if hasattr(self, 'icons') and 'cross_small' in self.icons:
            self.artist_close_btn = tk.Button(
                main_container,
                image=self.icons['cross_small'],
                bg='#3d3d3d',
                activebackground='#ff6666',
                relief='raised',
                bd=1,
                width=20,
                height=20,
                command=self._return_to_search,
                cursor='hand2',
                takefocus=0
            )
        else:
            # Fallback si l'icône n'est pas disponible
            self.artist_close_btn = tk.Button(
                main_container,
                text="✕",
                bg='#3d3d3d',
                fg='white',
                activebackground='#ff6666',
                relief='raised',
                bd=1,
                font=('TkDefaultFont', 10, 'bold'),
                width=20,
                height=20,
                command=self._return_to_search,
                cursor='hand2',
                takefocus=0
            )
        
        # Créer le notebook
        self.artist_notebook = ttk.Notebook(main_container, takefocus=0)
        self.artist_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Positionner la croix au-dessus de tout (utiliser tkraise pour la mettre au premier plan)
        self.artist_close_btn.place(in_=main_container, relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)
        self.artist_close_btn.tkraise()  # Mettre le bouton au premier plan
        
        # Ajouter un tooltip au bouton croix
        try:
            from tooltip import create_tooltip
            create_tooltip(self.artist_close_btn, "Retourner à la recherche\nQuitte l'affichage de l'artiste et retourne aux résultats de recherche\n(Raccourci: Échap)")
        except:
            pass  # Si le tooltip ne peut pas être créé, continuer
        
        # Forcer la mise à jour pour s'assurer que le notebook est visible
        self.artist_notebook.update_idletasks()
        
        # Onglet Musiques (contient les vidéos de la chaîne par ordre de sortie)
        self.musiques_frame = tk.Frame(self.artist_notebook, bg='#3d3d3d')
        self.artist_notebook.add(self.musiques_frame, text="Musiques")
        
        # Onglet Sorties (contient les albums/singles pour les chaînes sans onglets)
        self.sorties_frame = tk.Frame(self.artist_notebook, bg='#3d3d3d')
        self.artist_notebook.add(self.sorties_frame, text="Sorties")
        
        # Onglet Playlists (contient toutes les playlists de la chaîne)
        self.playlists_frame = tk.Frame(self.artist_notebook, bg='#3d3d3d')
        self.artist_notebook.add(self.playlists_frame, text="Playlists")
        
        # Messages de chargement
        self.musiques_loading = tk.Label(
            self.musiques_frame,
            text="Chargement des musiques...",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 10)
        )
        self.musiques_loading.pack(expand=True)
        
        self.sorties_loading = tk.Label(
            self.sorties_frame,
            text="Chargement des sorties...",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 10)
        )
        self.sorties_loading.pack(expand=True)
        
        self.playlists_loading = tk.Label(
            self.playlists_frame,
            text="Chargement des playlists...",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 10)
        )
        self.playlists_loading.pack(expand=True)
    
    def _search_artist_content(self):
        """Recherche complète du contenu d'un artiste : trouve l'ID puis lance les 3 recherches"""
        def search_all_content():
            try:
                # Vérifier si la recherche a été annulée avant de commencer
                if self.artist_search_cancelled:
                    return
                
                # D'abord, trouver l'ID réel de la chaîne
                channel_id = self._find_artist_channel_id()
                
                if self.artist_search_cancelled:
                    return
                
                if not channel_id:
                    print("Aucun ID de chaîne trouvé - impossible de récupérer le contenu")
                    self.root.after(0, lambda: self.status_bar.config(text="Impossible de trouver l'ID de la chaîne"))
                    return
                
                # Sauvegarder l'ID pour le réutiliser
                self.current_artist_channel_id = channel_id
                print(f"ID de chaîne trouvé et sauvegardé: {channel_id}")
                
                # Maintenant lancer les 3 recherches en parallèle avec l'ID trouvé
                self.artist_videos_thread = threading.Thread(target=self._search_artist_videos_with_id, daemon=True)
                self.artist_releases_thread = threading.Thread(target=self._search_artist_releases_with_id, daemon=True)
                self.artist_playlists_thread = threading.Thread(target=self._search_artist_playlists_with_id, daemon=True)
                
                self.artist_videos_thread.start()
                self.artist_releases_thread.start()
                self.artist_playlists_thread.start()
                
            except Exception as e:
                print(f"Erreur recherche contenu artiste: {e}")
                self.root.after(0, lambda: self.status_bar.config(text=f"Erreur: {e}"))
        
        # Lancer en arrière-plan
        main_thread = threading.Thread(target=search_all_content, daemon=True)
        main_thread.start()
    
    def _find_artist_channel_id(self):
        """Trouve l'ID réel de la chaîne YouTube pour cet artiste"""
        try:
            # Configuration pour la recherche
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                # D'abord vérifier si on a déjà un ID dans l'URL
                if hasattr(self, 'current_artist_channel_url') and self.current_artist_channel_url:
                    import re
                    channel_match = re.search(r'/channel/([^/?]+)', self.current_artist_channel_url)
                    if channel_match:
                        channel_id = channel_match.group(1)
                        print(f"ID de chaîne extrait de l'URL: {channel_id}")
                        return channel_id
                
                # Sinon, faire une recherche pour trouver la chaîne officielle
                print(f"Recherche de la chaîne officielle pour: {self.current_artist_name}")
                search_query = f"ytsearch1:{self.current_artist_name} official"
                search_results = ydl.extract_info(search_query, download=False)
                
                if search_results and 'entries' in search_results and search_results['entries']:
                    first_result = search_results['entries'][0]
                    # Essayer de trouver l'ID de la chaîne dans les métadonnées
                    if 'channel_id' in first_result:
                        channel_id = first_result['channel_id']
                        print(f"ID de chaîne trouvé via recherche: {channel_id}")
                        return channel_id
                    elif 'uploader_id' in first_result:
                        channel_id = first_result['uploader_id']
                        print(f"ID de chaîne trouvé via uploader_id: {channel_id}")
                        return channel_id
                
                print("Aucun ID de chaîne trouvé")
                return None
                
        except Exception as e:
            print(f"Erreur recherche ID chaîne: {e}")
            return None

    def _search_artist_videos_with_id(self):
        """Recherche les vidéos de l'artiste depuis l'onglet Vidéos de sa chaîne"""
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.artist_search_cancelled:
                return
            
            if not self.current_artist_channel_id:
                print("Aucun ID de chaîne disponible pour les vidéos")
                return
            
            # Vérifier le cache d'abord
            cache_key = self.current_artist_channel_id
            if cache_key in self.artist_cache and 'videos' in self.artist_cache[cache_key]:
                print("Utilisation du cache pour les vidéos")
                cached_videos = self.artist_cache[cache_key]['videos']
                self.root.after(0, lambda: self._display_artist_videos(cached_videos))
                return
            
            # Configuration pour extraire les vidéos de la chaîne (extract_flat=True pour avoir la durée)
            search_opts = {
                'extract_flat': True,  # Plus efficace et contient la durée
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                all_videos = []
                
                # Utiliser l'ID de chaîne trouvé
                base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
                videos_url = base_channel_url + '/videos'
                print(f"Extraction des vidéos depuis: {videos_url}")
                
                try:
                    channel_info = ydl.extract_info(videos_url, download=False)
                    if self.artist_search_cancelled:
                        return
                    
                    if channel_info and 'entries' in channel_info:
                        videos = list(channel_info['entries'])
                        # Filtrer et garder seulement les vidéos valides
                        videos = [v for v in videos if v and v.get('id')]
                        if videos:
                            all_videos.extend(videos[:30])  # Prendre les 30 premières
                            print(f"Trouvé {len(videos)} vidéos depuis la chaîne")
                        else:
                            print("Aucune vidéo valide trouvée sur la chaîne")
                    else:
                        print("Aucun contenu trouvé sur la chaîne")
                except Exception as e:
                    print(f"Erreur extraction vidéos de la chaîne: {e}")
                    self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des vidéos"))
                    return
                
                # Supprimer les doublons et préparer pour l'affichage
                unique_videos = {}
                for video in all_videos:
                    video_id = video.get('id', '')
                    if video_id and video_id not in unique_videos:
                        # S'assurer que les champs nécessaires sont présents
                        if not video.get('webpage_url') and video_id:
                            video['webpage_url'] = f"https://www.youtube.com/watch?v={video_id}"
                        unique_videos[video_id] = video
                
                final_videos = list(unique_videos.values())
                
                # Trier par date de sortie (les plus récentes d'abord) si disponible
                def get_upload_date(video):
                    upload_date = video.get('upload_date', '0')
                    try:
                        return int(upload_date) if upload_date.isdigit() else 0
                    except:
                        return 0
                
                final_videos.sort(key=get_upload_date, reverse=True)
                
                # Limiter à 15 vidéos max
                final_videos = final_videos[:15]
                
                # Vérifier annulation avant affichage
                if not self.artist_search_cancelled:
                    # Sauvegarder en cache
                    cache_key = self.current_artist_channel_id
                    if cache_key not in self.artist_cache:
                        self.artist_cache[cache_key] = {}
                    self.artist_cache[cache_key]['videos'] = final_videos
                    
                    # Afficher les résultats dans l'interface
                    self.root.after(0, lambda: self._display_artist_videos(final_videos))
                    
        except Exception as e:
            print(f"Erreur recherche vidéos artiste: {e}")
            self.root.after(0, lambda: self._display_videos_error(str(e)))

    def _search_artist_videos(self):
        """Ancienne fonction - maintenant redirige vers _search_artist_videos_with_id"""
        self._search_artist_videos_with_id()

    def _search_artist_releases_with_id(self):
        """Recherche les albums et singles de l'artiste depuis l'onglet releases"""
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.artist_search_cancelled:
                return
            
            if not self.current_artist_channel_id:
                print("Aucun ID de chaîne disponible pour les releases")
                return
            
            # Vérifier le cache d'abord
            cache_key = self.current_artist_channel_id
            if cache_key in self.artist_cache and 'releases' in self.artist_cache[cache_key]:
                print("Utilisation du cache pour les sorties")
                cached_releases = self.artist_cache[cache_key]['releases']
                self.root.after(0, lambda: self._display_artist_releases(cached_releases))
                return
                
            # Options pour extraire les releases de la chaîne
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                all_playlists = []
                
                # Utiliser l'ID de chaîne trouvé
                base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
                releases_url = base_channel_url + '/releases'
                print(f"Extraction des releases depuis: {releases_url}")
                
                try:
                    channel_info = ydl.extract_info(releases_url, download=False)
                    
                    if channel_info and 'entries' in channel_info:
                        playlists = list(channel_info['entries'])
                        print(f"Nombre de releases trouvées: {len(playlists)}")
                        # Garder seulement les vraies playlists/releases
                        valid_playlists = []
                        for p in playlists:
                            if self.artist_search_cancelled:
                                return
                            if p and p.get('id'):
                                # Vérifier si c'est vraiment une playlist
                                if (p.get('_type') == 'playlist' or 
                                    'playlist' in p.get('url', '') or 
                                    'list=' in p.get('url', '') or
                                    p.get('playlist_count', 0) > 0):
                                    valid_playlists.append(p)
                                    print(f"Release valide: {p.get('title', 'Sans titre')} - {p.get('playlist_count', 0)} vidéos")
                        
                        all_playlists.extend(valid_playlists[:15])  # Prendre les 15 premières
                    else:
                        print("Aucune release trouvée sur la chaîne")
                except Exception as e:
                    print(f"Erreur extraction releases de la chaîne: {e}")
                    self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des releases"))
                    return
                
                # Supprimer les doublons basés sur l'ID
                unique_playlists = {}
                for playlist in all_playlists:
                    playlist_id = playlist.get('id', '')
                    if playlist_id and playlist_id not in unique_playlists:
                        # S'assurer que les champs nécessaires sont présents
                        if not playlist.get('webpage_url') and playlist_id:
                            playlist['webpage_url'] = f"https://www.youtube.com/playlist?list={playlist_id}"
                            playlist['_type'] = 'playlist'
                        unique_playlists[playlist_id] = playlist
                
                final_playlists = list(unique_playlists.values())  # Toutes les releases
                
                # Vérifier annulation avant affichage
                if not self.artist_search_cancelled:
                    # Sauvegarder en cache
                    cache_key = self.current_artist_channel_id
                    if cache_key not in self.artist_cache:
                        self.artist_cache[cache_key] = {}
                    self.artist_cache[cache_key]['releases'] = final_playlists
                    
                    # Afficher les résultats dans l'interface
                    self.root.after(0, lambda: self._display_artist_releases(final_playlists))
                    
        except Exception as e:
            print(f"Erreur recherche releases artiste: {e}")
            self.root.after(0, lambda: self._display_releases_error(str(e)))

    def _search_artist_playlists_with_id(self):
        """Recherche les playlists de l'artiste depuis l'onglet playlists"""  
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.artist_search_cancelled:
                return
            
            if not self.current_artist_channel_id:
                print("Aucun ID de chaîne disponible pour les playlists")
                return
            
            # Vérifier le cache d'abord
            cache_key = self.current_artist_channel_id
            if cache_key in self.artist_cache and 'playlists' in self.artist_cache[cache_key]:
                print("Utilisation du cache pour les playlists")
                cached_playlists = self.artist_cache[cache_key]['playlists']
                self.root.after(0, lambda: self._display_artist_playlists(cached_playlists))
                return
                
            # Options pour extraire les playlists de la chaîne
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                all_playlists = []
                
                # Utiliser l'ID de chaîne trouvé
                base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
                playlists_url = base_channel_url + '/playlists'
                print(f"Extraction des playlists depuis: {playlists_url}")
                
                try:
                    channel_info = ydl.extract_info(playlists_url, download=False)
                    if self.artist_search_cancelled:
                        return
                    
                    print(f"Channel info type: {type(channel_info)}")
                    if channel_info:
                        print(f"Channel info keys: {list(channel_info.keys()) if isinstance(channel_info, dict) else 'Not a dict'}")
                    
                    if channel_info and 'entries' in channel_info:
                        entries = list(channel_info['entries'])
                        print(f"Nombre d'entrées trouvées: {len(entries)}")
                        
                        for i, entry in enumerate(entries):
                            if self.artist_search_cancelled:
                                return
                            if entry:
                                print(f"Entrée {i}: type={entry.get('_type')}, id={entry.get('id')}, title={entry.get('title', 'Sans titre')}")
                                # Logique plus flexible pour détecter les playlists
                                if (entry.get('_type') == 'playlist' or 
                                    'playlist' in entry.get('url', '') or 
                                    'list=' in entry.get('url', '') or
                                    entry.get('playlist_count', 0) > 0 or
                                    entry.get('id', '').startswith('PL') or  # Les IDs de playlist YouTube commencent par PL
                                    'playlist' in entry.get('title', '').lower()):
                                    all_playlists.append(entry)
                                    print(f"Playlist valide trouvée: {entry.get('title', 'Sans titre')}")
                                else:
                                    print(f"Entrée ignorée (pas une playlist): {entry.get('title', 'Sans titre')}")
                    else:
                        print("Aucune entrée trouvée dans channel_info")
                                
                    if not all_playlists:
                        print("Aucune playlist trouvée sur la chaîne")
                except Exception as e:
                    print(f"Erreur extraction playlists de la chaîne: {e}")
                    self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des playlists"))
                    return
                
                # Supprimer les doublons basés sur l'ID
                unique_playlists = {}
                for playlist in all_playlists:
                    playlist_id = playlist.get('id', '')
                    if playlist_id and playlist_id not in unique_playlists:
                        # S'assurer que les champs nécessaires sont présents
                        if not playlist.get('webpage_url') and playlist_id:
                            playlist['webpage_url'] = f"https://www.youtube.com/playlist?list={playlist_id}"
                            playlist['_type'] = 'playlist'
                        unique_playlists[playlist_id] = playlist
                
                final_playlists = list(unique_playlists.values())[:20]  # Maximum 20 playlists
                
                # Vérifier annulation avant affichage
                if not self.artist_search_cancelled:
                    # Sauvegarder en cache
                    cache_key = self.current_artist_channel_id
                    if cache_key not in self.artist_cache:
                        self.artist_cache[cache_key] = {}
                    self.artist_cache[cache_key]['playlists'] = final_playlists
                    
                    # Afficher les résultats dans l'interface
                    self.root.after(0, lambda: self._display_artist_playlists(final_playlists))
                    
        except Exception as e:
            print(f"Erreur recherche playlists artiste: {e}")
            self.root.after(0, lambda: self._display_playlists_error(str(e)))

    def _search_artist_videos(self):
        """Ancienne fonction - maintenant redirige vers _search_artist_videos_with_id"""
        self._search_artist_videos_with_id()
    
    def _search_artist_releases(self):
        """Ancienne fonction - maintenant redirige vers _search_artist_releases_with_id"""
        self._search_artist_releases_with_id()
    
    def _search_artist_releases_old(self):
        """Ancienne fonction - gardée pour référence"""
        def search_releases():
            try:
                # Vérifier si la recherche a été annulée avant de commencer
                if self.artist_search_cancelled:
                    return
                    
                # Options pour extraire les releases/playlists de la chaîne
                search_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True
                }
                
                with YoutubeDL(search_opts) as ydl:
                    all_playlists = []
                    
                    # Utiliser UNIQUEMENT l'ID de chaîne trouvé précédemment
                    if hasattr(self, 'current_artist_channel_id') and self.current_artist_channel_id:
                        # Utiliser le format officiel avec l'ID de la chaîne
                        base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
                        releases_url = base_channel_url + '/releases'
                        print(f"URL releases construite avec ID chaîne: {releases_url}")
                        
                        try:
                            if self.artist_search_cancelled:
                                return
                            print(f"Extraction des releases depuis: {releases_url}")
                            channel_info = ydl.extract_info(releases_url, download=False)
                            
                            print(f"Channel info type: {type(channel_info)}")
                            if channel_info:
                                print(f"Channel info keys: {list(channel_info.keys()) if isinstance(channel_info, dict) else 'Not a dict'}")
                            
                            if channel_info and 'entries' in channel_info:
                                playlists = list(channel_info['entries'])
                                print(f"Nombre de releases trouvées: {len(playlists)}")
                                # Garder seulement les vraies playlists/releases
                                valid_playlists = []
                                for p in playlists:
                                    if self.artist_search_cancelled:
                                        return
                                    if p and p.get('id'):
                                        # Vérifier si c'est vraiment une playlist
                                        if (p.get('_type') == 'playlist' or 
                                            'playlist' in p.get('url', '') or 
                                            'list=' in p.get('url', '') or
                                            p.get('playlist_count', 0) > 0):
                                            valid_playlists.append(p)
                                            print(f"Release valide: {p.get('title', 'Sans titre')} - {p.get('playlist_count', 0)} vidéos")
                                
                                all_playlists.extend(valid_playlists[:15])  # Prendre les 15 premières
                            else:
                                print("Aucune release trouvée sur la chaîne")
                        except Exception as e:
                            print(f"Erreur extraction releases de la chaîne: {e}")
                    else:
                        print("Aucun ID de chaîne disponible - impossible de récupérer les releases")
                        self.root.after(0, lambda: self.status_bar.config(text="ID de chaîne manquant pour les releases"))
                    
                    # Plus de recherche alternative - utiliser UNIQUEMENT le contenu de la chaîne officielle
                    if not all_playlists:
                        print("Aucune release trouvée sur la chaîne officielle")
                        self.root.after(0, lambda: self.status_bar.config(text="Aucune release trouvée sur cette chaîne"))
                    
                    # Supprimer les doublons basés sur l'ID
                    unique_playlists = {}
                    for playlist in all_playlists:
                        playlist_id = playlist.get('id', '')
                        if playlist_id and playlist_id not in unique_playlists:
                            # S'assurer que les champs nécessaires sont présents
                            if not playlist.get('webpage_url') and playlist_id:
                                # Déterminer si c'est une playlist ou une vidéo
                                if 'playlist' in playlist.get('_type', '') or 'list=' in playlist.get('url', ''):
                                    playlist['webpage_url'] = f"https://www.youtube.com/playlist?list={playlist_id}"
                                    playlist['_type'] = 'playlist'
                                else:
                                    playlist['webpage_url'] = f"https://www.youtube.com/watch?v={playlist_id}"
                            if not playlist.get('url'):
                                playlist['url'] = playlist.get('webpage_url', '')
                            unique_playlists[playlist_id] = playlist
                    
                    final_playlists = list(unique_playlists.values())
                    
                    # Vérifier annulation avant le tri et l'affichage
                    if self.artist_search_cancelled:
                        return
                    
                    # Trier par date de publication (plus récentes en premier)
                    def get_upload_date(playlist):
                        upload_date = playlist.get('upload_date', '19700101')
                        if isinstance(upload_date, str) and upload_date:
                            try:
                                return int(upload_date)
                            except:
                                return 0
                        return 0
                    
                    final_playlists.sort(key=get_upload_date, reverse=True)
                    
                    # Limiter à 10 playlists max
                    final_playlists = final_playlists[:10]
                    
                    # Vérifier annulation avant affichage
                    if not self.artist_search_cancelled:
                        # Afficher les résultats dans l'interface
                        self.root.after(0, lambda: self._display_artist_releases(final_playlists))
                    
            except Exception as e:
                print(f"Erreur recherche playlists artiste: {e}")
                if not self.artist_search_cancelled:
                    self.root.after(0, lambda: self._display_releases_error(str(e)))
        
        # Lancer en arrière-plan et enregistrer le thread
        self.artist_releases_thread = threading.Thread(target=search_releases, daemon=True)
        self.artist_releases_thread.start()
    
    def _search_artist_playlists(self):
        """Ancienne fonction - maintenant redirige vers _search_artist_playlists_with_id"""
        self._search_artist_playlists_with_id()
    
    def _search_artist_playlists_old(self):
        """Ancienne fonction - gardée pour référence"""
        def search_playlists():
            try:
                # Vérifier si la recherche a été annulée avant de commencer
                if self.artist_search_cancelled:
                    return
                    
                # Options pour extraire les playlists de la chaîne
                search_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True
                }
                 
                with YoutubeDL(search_opts) as ydl:
                    all_playlists = []
                    
                    # Vérifier annulation avant chaque étape importante
                    if self.artist_search_cancelled:
                        return
                    
                    # Utiliser UNIQUEMENT l'ID de chaîne trouvé précédemment
                    if hasattr(self, 'current_artist_channel_id') and self.current_artist_channel_id:
                        # Utiliser le format officiel avec l'ID de la chaîne
                        base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
                        playlists_url = base_channel_url + '/playlists'
                        print(f"URL playlists construite avec ID chaîne: {playlists_url}")
                        
                        try:
                            if self.artist_search_cancelled:
                                return
                            
                            # Extraire les playlists de la chaîne
                            channel_info = ydl.extract_info(playlists_url, download=False)
                            if self.artist_search_cancelled:
                                return
                            if channel_info and 'entries' in channel_info:
                                for entry in channel_info['entries']:
                                    if self.artist_search_cancelled:
                                        return
                                    if entry and entry.get('_type') == 'playlist':
                                        all_playlists.append(entry)
                                        print(f"Playlist trouvée: {entry.get('title', 'Sans titre')}")
                                        
                            if not all_playlists:
                                print("Aucune playlist trouvée sur la chaîne")
                        except Exception as e:
                            print(f"Erreur extraction playlists de la chaîne: {e}")
                    else:
                        print("Aucun ID de chaîne disponible - impossible de récupérer les playlists")
                        self.root.after(0, lambda: self.status_bar.config(text="ID de chaîne manquant pour les playlists"))
                    
                    # Plus de recherche alternative - utiliser UNIQUEMENT le contenu de la chaîne officielle
                    if not all_playlists:
                        print("Aucune playlist trouvée sur la chaîne officielle")
                        self.root.after(0, lambda: self.status_bar.config(text="Aucune playlist trouvée sur cette chaîne"))
                    
                    # Supprimer les doublons basés sur l'ID
                    unique_playlists = {}
                    for playlist in all_playlists:
                        playlist_id = playlist.get('id', '')
                        if playlist_id and playlist_id not in unique_playlists:
                            # S'assurer que les champs nécessaires sont présents
                            if not playlist.get('webpage_url') and playlist_id:
                                playlist['webpage_url'] = f"https://www.youtube.com/playlist?list={playlist_id}"
                                playlist['_type'] = 'playlist'
                            if not playlist.get('url'):
                                playlist['url'] = playlist.get('webpage_url', '')
                            unique_playlists[playlist_id] = playlist
                    
                    final_playlists = list(unique_playlists.values())
                    
                    # Vérifier annulation avant le tri et l'affichage
                    if self.artist_search_cancelled:
                        return
                    
                    # Trier par date de publication (plus récentes en premier)
                    def get_upload_date(playlist):
                        upload_date = playlist.get('upload_date', '19700101')
                        if isinstance(upload_date, str) and upload_date:
                            try:
                                return int(upload_date)
                            except:
                                return 0
                        return 0
                    
                    final_playlists.sort(key=get_upload_date, reverse=True)
                    
                    # Afficher toutes les sorties (pas de limitation)
                    
                    # Vérifier annulation avant affichage
                    if not self.artist_search_cancelled:
                        # Afficher les résultats dans l'interface
                        self.root.after(0, lambda: self._display_artist_playlists(final_playlists))
                    
            except Exception as e:
                print(f"Erreur recherche playlists artiste: {e}")
                if not self.artist_search_cancelled:
                    self.root.after(0, lambda: self._display_playlists_error(str(e)))
        
        # Lancer en arrière-plan et enregistrer le thread
        self.artist_playlists_thread = threading.Thread(target=search_playlists, daemon=True)
        self.artist_playlists_thread.start()
    
    def _display_artist_videos(self, videos):
        """Affiche les vidéos de l'artiste dans l'onglet Musiques"""
        # Vérifier si on est encore en mode artiste et que l'onglet musiques existe
        if not hasattr(self, 'musiques_frame') or not self.artist_mode:
            return  # L'utilisateur a annulé l'affichage artiste entre temps
            
        # Supprimer le message de chargement
        if hasattr(self, 'musiques_loading'):
            self.musiques_loading.destroy()
        
        if not videos:
            no_results_label = tk.Label(
                self.musiques_frame,
                text="Aucune musique trouvée",
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 10)
            )
            no_results_label.pack(expand=True)
            return
        
        # Créer un canvas scrollable dans l'onglet musiques
        canvas = tk.Canvas(self.musiques_frame, bg='#3d3d3d', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.musiques_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#3d3d3d')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaqueter le canvas et la scrollbar
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Afficher les vidéos dans le frame scrollable
        for i, video in enumerate(videos):
            self._add_artist_result(video, i, scrollable_frame)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        self.status_bar.config(text=f"{len(videos)} musiques trouvées pour {self.current_artist_name}")
    
    def _display_artist_releases(self, releases):
        """Affiche les sorties de l'artiste dans l'onglet Sorties"""
        # Vérifier si on est encore en mode artiste et que l'onglet sorties existe
        if not hasattr(self, 'sorties_frame') or not self.artist_mode:
            return  # L'utilisateur a annulé l'affichage artiste entre temps
            
        # Supprimer le message de chargement
        if hasattr(self, 'sorties_loading'):
            self.sorties_loading.destroy()
        
        if not releases:
            no_results_label = tk.Label(
                self.sorties_frame,
                text="Aucune sortie trouvée",
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 10)
            )
            no_results_label.pack(expand=True)
            return
        
        # Créer un canvas scrollable dans l'onglet sorties
        canvas = tk.Canvas(self.sorties_frame, bg='#3d3d3d', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.sorties_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#3d3d3d')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaqueter le canvas et la scrollbar
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Afficher les playlists dans le frame scrollable (onglet sorties)
        for i, playlist in enumerate(releases):
            self._add_artist_playlist_result(playlist, i, scrollable_frame, "sorties")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel_recursive(widget):
            """Bind mousewheel à un widget et tous ses enfants"""
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        bind_mousewheel_recursive(scrollable_frame)
        
        self.status_bar.config(text=f"{len(releases)} sorties trouvées pour {self.current_artist_name}")
    
    def _display_artist_playlists(self, playlists):
        """Affiche les playlists de l'artiste dans l'onglet Playlists"""
        # Vérifier si on est encore en mode artiste et que l'onglet playlists existe
        if not hasattr(self, 'playlists_frame') or not self.artist_mode:
            return  # L'utilisateur a annulé l'affichage artiste entre temps
            
        # Supprimer le message de chargement
        if hasattr(self, 'playlists_loading'):
            self.playlists_loading.destroy()
        
        if not playlists:
            no_results_label = tk.Label(
                self.playlists_frame,
                text="Aucune playlist trouvée",
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 10)
            )
            no_results_label.pack(expand=True)
            return
        
        # Créer un canvas scrollable dans l'onglet playlists
        canvas = tk.Canvas(self.playlists_frame, bg='#3d3d3d', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.playlists_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#3d3d3d')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaqueter le canvas et la scrollbar
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Afficher les playlists dans le frame scrollable (onglet playlists)
        for i, playlist in enumerate(playlists):
            self._add_artist_playlist_result(playlist, i, scrollable_frame, "playlists")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel_recursive(widget):
            """Bind mousewheel à un widget et tous ses enfants"""
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        bind_mousewheel_recursive(scrollable_frame)
        
        self.status_bar.config(text=f"{len(playlists)} playlists trouvées pour {self.current_artist_name}")
    
    def _add_artist_result(self, video, index, container):
        """Ajoute un résultat vidéo dans un onglet artiste"""
        try:
            title = video.get('title', 'Sans titre')
            duration = video.get('duration', 0)
            url = video.get('url', '')
            
            # Frame principal - même style que les résultats normaux
            result_frame = tk.Frame(
                container,
                bg='#4a4a4a',
                relief='flat',
                bd=1,
                highlightbackground='#555555',
                highlightthickness=1
            )
            result_frame.pack(fill="x", padx=3, pady=1)  # Espacement réduit
            
            # Configuration de la grille (plus compact avec 2 lignes pour titre+date/durée)
            result_frame.columnconfigure(0, minsize=60, weight=0)  # Miniature plus petite
            result_frame.columnconfigure(1, weight=1)              # Titre et date/durée
            result_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur augmentée pour 2 lignes
            
            # Miniature (plus petite)
            thumbnail_label = tk.Label(
                result_frame,
                bg='#4a4a4a',
                width=8,
                height=2,
                text="🎵",
                fg='white',
                anchor='center',
                font=('TkDefaultFont', 8)
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=3)
            thumbnail_label.grid_propagate(False)
            
            # Charger la miniature en arrière-plan
            self._load_artist_thumbnail(video, thumbnail_label)
            
            # Titre et durée (dans une frame verticale)
            text_frame = tk.Frame(result_frame, bg='#4a4a4a')
            text_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 5), pady=3)
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            text_frame.rowconfigure(1, weight=0)
            
            # Tronquer le titre s'il est trop long
            display_title = title
            if len(title) > 60:
                display_title = title[:57] + "..."
            
            title_label = tk.Label(
                text_frame,
                text=display_title,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 8),  # Police plus petite
                anchor='w',
                justify='left'
            )
            title_label.grid(row=0, column=0, sticky='ew', pady=(1, 0))
            
            # Durée sous le titre
            duration_text = time.strftime('%M:%S', time.gmtime(duration)) if duration > 0 else "?:?"
            
            duration_label = tk.Label(
                text_frame,
                text=duration_text,
                bg='#4a4a4a',
                fg='#aaaaaa',
                font=('TkDefaultFont', 7),
                anchor='w',
                justify='left'
            )
            duration_label.grid(row=1, column=0, sticky='ew', pady=(0, 1))
            
            # Stocker les données vidéo
            result_frame.video_data = video
            result_frame.title_label = title_label
            result_frame.duration_label = duration_label
            result_frame.thumbnail_label = thumbnail_label
            
            # Événements de clic pour la sélection multiple (comme dans _add_search_result)
            def on_result_click(event, frame=result_frame):
                # Initialiser le drag pour les vidéos
                self.drag_drop_handler.setup_drag_start(event, frame)
                
                # Vérifier si Shift est enfoncé pour la sélection multiple
                if event.state & 0x1:  # Shift est enfoncé
                    self.shift_selection_active = True
                    # Utiliser l'URL comme identifiant unique
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
                    # Télécharger la vidéo (sans ajouter à la playlist)
                    self._on_result_click(frame, add_to_playlist=False)
            
            # Effet hover
            def on_enter(event):
                # Vérifier l'URL pour la sélection
                video_url = result_frame.video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={result_frame.video_data.get('id')}"
                
                # Vérifier si l'élément est sélectionné
                if video_url in self.selected_items:
                    # Orange plus clair pour le hover d'un élément sélectionné
                    hover_color = '#ffb347'
                elif hasattr(result_frame, 'is_downloading') and result_frame.is_downloading:
                    # Rouge plus clair pour le hover pendant téléchargement
                    hover_color = '#ff8888'
                else:
                    # Couleur normale pour le hover
                    hover_color = '#5a5a5a'
                
                result_frame.configure(bg=hover_color)
                text_frame.configure(bg=hover_color)
                title_label.configure(bg=hover_color)
                duration_label.configure(bg=hover_color)
                thumbnail_label.configure(bg=hover_color)
            
            def on_leave(event):
                # Vérifier l'URL pour la sélection
                video_url = result_frame.video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={result_frame.video_data.get('id')}"
                
                # Vérifier si l'élément est sélectionné
                if video_url in self.selected_items:
                    # Revenir à l'orange de sélection
                    leave_color = '#ff8c00'
                elif hasattr(result_frame, 'is_downloading') and result_frame.is_downloading:
                    # Revenir au rouge de téléchargement
                    leave_color = result_frame.download_color
                else:
                    # Couleur normale
                    leave_color = '#4a4a4a'
                
                result_frame.configure(bg=leave_color)
                text_frame.configure(bg=leave_color)
                title_label.configure(bg=leave_color)
                duration_label.configure(bg=leave_color)
                thumbnail_label.configure(bg=leave_color)
            
            # Bindings pour tous les événements (comme dans _add_search_result)
            all_widgets = [result_frame, text_frame, title_label, thumbnail_label, duration_label]
            
            for widget in all_widgets:
                # Hover
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                # Clic simple (sélection multiple avec Shift)
                widget.bind("<ButtonPress-1>", on_result_click)
                # Double-clic (téléchargement)
                widget.bind("<Double-1>", on_result_double_click)
                # Clic droit (menu playlists)
                widget.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            
            # Configuration du drag-and-drop
            self.drag_drop_handler.setup_drag_drop(
                result_frame, 
                video_data=video, 
                item_type="youtube"
            )
            
            # Tooltip avec toutes les interactions
            tooltip_text = f"Vidéo de {self.current_artist_name}\nDouble-clic: Télécharger\nDrag vers la droite: Télécharger et ajouter à la queue\nDrag vers la gauche: Télécharger et placer en premier dans la queue\nShift + Clic: Sélection multiple\nClic droit: Menu playlists"
            create_tooltip(result_frame, tooltip_text)
            create_tooltip(title_label, tooltip_text)
            
        except Exception as e:
            print(f"Erreur lors de l'ajout du résultat vidéo artiste: {e}")
    
    def _load_artist_thumbnail(self, video, thumbnail_label):
        """Charge la miniature d'une vidéo d'artiste en arrière-plan"""
        def load_thumbnail():
            try:
                # Essayer différentes sources de miniatures
                thumbnail_url = None
                
                # 1. Essayer le champ 'thumbnail'
                if video.get('thumbnail'):
                    thumbnail_url = video['thumbnail']
                # 2. Essayer le champ 'thumbnails'
                elif video.get('thumbnails') and len(video['thumbnails']) > 0:
                    # Prendre la miniature de meilleure qualité disponible
                    thumbnails = video['thumbnails']
                    if len(thumbnails) > 1:
                        thumbnail_url = thumbnails[1]['url']  # Généralement meilleure qualité
                    else:
                        thumbnail_url = thumbnails[0]['url']
                # 3. Construire l'URL depuis l'ID vidéo
                elif video.get('id'):
                    thumbnail_url = f"https://img.youtube.com/vi/{video['id']}/mqdefault.jpg"
                
                if not thumbnail_url:
                    return
                
                # Télécharger l'image
                response = requests.get(thumbnail_url, timeout=10)
                if response.status_code == 200:
                    # Ouvrir l'image
                    image = Image.open(io.BytesIO(response.content))
                    
                    # Redimensionner en gardant le ratio (largeur fixe de 60px)
                    original_width, original_height = image.size
                    target_width = 60
                    target_height = int((target_width * original_height) / original_width)
                    image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    
                    # Convertir en PhotoImage
                    photo = ImageTk.PhotoImage(image)
                    
                    # Mettre à jour le label dans le thread principal
                    def update_thumbnail():
                        try:
                            if thumbnail_label.winfo_exists():
                                thumbnail_label.configure(image=photo, text="")
                                thumbnail_label.image = photo  # Garder une référence
                        except:
                            pass
                    
                    self.root.after(0, update_thumbnail)
                    
            except Exception as e:
                print(f"Erreur lors du chargement de la miniature artiste: {e}")
        
        # Lancer en arrière-plan
        threading.Thread(target=load_thumbnail, daemon=True).start()
    
    def _load_playlist_count(self, playlist, count_label):
        """Charge le nombre de vidéos d'une playlist en arrière-plan"""
        def load_count():
            try:
                playlist_url = playlist.get('url', '') or playlist.get('webpage_url', '')
                if not playlist_url:
                    self.root.after(0, lambda: count_label.config(text="Playlist"))
                    return
                
                # Options pour récupérer seulement le nombre de vidéos
                count_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True
                }
                
                with YoutubeDL(count_opts) as ydl:
                    playlist_info = ydl.extract_info(playlist_url, download=False)
                    if playlist_info and 'entries' in playlist_info:
                        video_count = len(playlist_info['entries'])
                        count_text = f"{video_count} musiques" if video_count > 0 else "Playlist vide"
                    else:
                        count_text = "Playlist"
                    
                    # Mettre à jour le label dans le thread principal
                    def update_count():
                        try:
                            if count_label.winfo_exists():
                                count_label.config(text=count_text)
                        except:
                            pass
                    
                    self.root.after(0, update_count)
                    
            except Exception as e:
                print(f"Erreur lors du chargement du nombre de vidéos: {e}")
                self.root.after(0, lambda: count_label.config(text="Playlist"))
        
        # Lancer en arrière-plan
        threading.Thread(target=load_count, daemon=True).start()
    
    def _add_artist_playlist_result(self, playlist, index, container, target_tab="sorties"):
        """Ajoute une playlist dans l'onglet Sorties ou Playlists avec double-clic pour voir le contenu"""
        try:
            title = playlist.get('title', 'Sans titre')
            # Essayer plusieurs champs pour le nombre de vidéos
            playlist_count = (playlist.get('playlist_count', 0) or 
                            playlist.get('video_count', 0) or
                            playlist.get('entry_count', 0) or
                            len(playlist.get('entries', [])))
            url = playlist.get('url', '')
            
            # Le nombre de vidéos n'est pas disponible avec extract_flat=True
            # On va le récupérer en arrière-plan
            
            # Frame principal - même style que les résultats normaux
            result_frame = tk.Frame(
                container,
                bg='#4a4a4a',
                relief='flat',
                bd=1,
                highlightbackground='#555555',
                highlightthickness=1
            )
            result_frame.pack(fill="x", padx=3, pady=1)  # Espacement réduit
            
            # Configuration de la grille (plus compact avec 2 lignes pour titre+count)
            result_frame.columnconfigure(0, minsize=60, weight=0)  # Miniature plus petite
            result_frame.columnconfigure(1, weight=1)              # Titre et nombre de vidéos
            result_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur augmentée pour 2 lignes
            
            # Miniature avec icône playlist (taille adaptative)
            thumbnail_label = tk.Label(
                result_frame,
                bg='#4a4a4a',
                text="📁",  # Icône dossier pour playlist
                fg='white',
                anchor='center',
                font=('TkDefaultFont', 12)
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=3)
            
            # Charger la miniature en arrière-plan
            self._load_artist_thumbnail(playlist, thumbnail_label)
            
            # Titre et nombre de vidéos (dans une frame verticale)
            text_frame = tk.Frame(result_frame, bg='#4a4a4a')
            text_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 5), pady=3)
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            text_frame.rowconfigure(1, weight=0)
            
            # Tronquer le titre intelligemment selon la largeur en pixels
            from tools import _truncate_text_for_display
            display_title = _truncate_text_for_display(self, title, max_width_pixels=200, font_size=8)
            
            title_label = tk.Label(
                text_frame,
                text=display_title,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 8),  # Police plus petite
                anchor='w',
                justify='left'
            )
            title_label.grid(row=0, column=0, sticky='ew', pady=(1, 0))
            
            # Nombre de musiques sous le titre (initialement "Chargement...")
            count_label = tk.Label(
                text_frame,
                text="Chargement...",
                bg='#4a4a4a',
                fg='#aaaaaa',
                font=('TkDefaultFont', 7),
                anchor='w',
                justify='left'
            )
            count_label.grid(row=1, column=0, sticky='ew', pady=(0, 1))
            
            # Charger le nombre de vidéos en arrière-plan (après création du label)
            self._load_playlist_count(playlist, count_label)
            
            # Stocker les données playlist
            result_frame.playlist_data = playlist
            result_frame.title_label = title_label
            result_frame.count_label = count_label
            result_frame.thumbnail_label = thumbnail_label
            
            # Événements de clic (double-clic pour voir le contenu de la playlist)
            def on_playlist_double_click(event, frame=result_frame):
                self._show_playlist_content(frame.playlist_data, target_tab)
            
            # Bindings pour le double-clic (inclure text_frame pour que le titre soit cliquable)
            result_frame.bind("<Double-Button-1>", on_playlist_double_click)
            title_label.bind("<Double-Button-1>", on_playlist_double_click)
            thumbnail_label.bind("<Double-Button-1>", on_playlist_double_click)
            count_label.bind("<Double-Button-1>", on_playlist_double_click)
            text_frame.bind("<Double-Button-1>", on_playlist_double_click)
            
            # Effet hover
            def on_enter(event):
                result_frame.configure(bg='#5a5a5a')
                title_label.configure(bg='#5a5a5a')
                thumbnail_label.configure(bg='#5a5a5a')
                count_label.configure(bg='#5a5a5a')
                text_frame.configure(bg='#5a5a5a')
            
            def on_leave(event):
                result_frame.configure(bg='#4a4a4a')
                title_label.configure(bg='#4a4a4a')
                thumbnail_label.configure(bg='#4a4a4a')
                count_label.configure(bg='#4a4a4a')
                text_frame.configure(bg='#4a4a4a')
            
            # Bindings pour l'effet hover (inclure text_frame)
            for widget in [result_frame, title_label, thumbnail_label, count_label, text_frame]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
            
            # Tooltip avec informations
            tooltip_text = f"Playlist: {title}\nDouble-clic pour voir le contenu"
            if playlist_count > 0:
                tooltip_text += f"\n{playlist_count} vidéos"
            create_tooltip(title_label, tooltip_text)
            
        except Exception as e:
            print(f"Erreur lors de l'ajout de la playlist artiste: {e}")
    
    def _show_playlist_content(self, playlist_data, target_tab="sorties"):
        """Affiche le contenu d'une playlist dans une nouvelle interface"""
        def load_playlist_content():
            try:
                playlist_url = playlist_data.get('url', '') or playlist_data.get('webpage_url', '')
                if not playlist_url:
                    self.root.after(0, lambda: self._show_playlist_error("URL de playlist non trouvée"))
                    return
                
                # Vérifier le cache d'abord
                if playlist_url in self.playlist_content_cache:
                    print("Utilisation du cache pour le contenu de la playlist")
                    cached_videos = self.playlist_content_cache[playlist_url]
                    playlist_title = playlist_data.get('title', 'Playlist')
                    self.root.after(0, lambda: self._display_playlist_content(cached_videos, playlist_title, target_tab))
                    return
                
                print(f"Chargement playlist: {playlist_url}")
                print(f"Type: {playlist_data.get('_type', 'unknown')}")
                
                # Si c'est une vidéo individuelle, la traiter comme telle
                if 'watch?v=' in playlist_url and 'list=' not in playlist_url:
                    # C'est une vidéo individuelle, pas une playlist
                    video_data = playlist_data.copy()
                    if not video_data.get('webpage_url'):
                        video_data['webpage_url'] = playlist_url
                    if not video_data.get('url'):
                        video_data['url'] = playlist_url
                    
                    playlist_title = playlist_data.get('title', 'Vidéo')
                    self.root.after(0, lambda: self._display_playlist_content([video_data], playlist_title, target_tab))
                    return
                
                # Options pour extraire le contenu de la playlist
                playlist_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True
                }
                
                with YoutubeDL(playlist_opts) as ydl:
                    # Extraire le contenu de la playlist
                    playlist_info = ydl.extract_info(playlist_url, download=False)

                    if playlist_info and 'entries' in playlist_info:
                        videos = list(playlist_info['entries'])
                        # Filtrer et garder seulement les vidéos valides
                        videos = [v for v in videos if v and v.get('id')]
                        
                        # S'assurer que les champs nécessaires sont présents
                        for video in videos:
                            if not video.get('webpage_url') and video.get('id'):
                                video['webpage_url'] = f"https://www.youtube.com/watch?v={video['id']}"
                            if not video.get('url'):
                                video['url'] = video.get('webpage_url', f"https://www.youtube.com/watch?v={video['id']}")
                        
                        # Sauvegarder en cache
                        self.playlist_content_cache[playlist_url] = videos
                        
                        # Afficher le contenu dans l'interface
                        playlist_title = playlist_data.get('title', 'Playlist')
                        self.root.after(0, lambda: self._display_playlist_content(videos, playlist_title, target_tab))
                    elif playlist_info:
                        # Si c'est une vidéo individuelle retournée
                        video_data = playlist_info.copy()
                        if not video_data.get('webpage_url') and video_data.get('id'):
                            video_data['webpage_url'] = f"https://www.youtube.com/watch?v={video_data['id']}"
                        if not video_data.get('url'):
                            video_data['url'] = video_data.get('webpage_url', playlist_url)
                        
                        # Sauvegarder en cache (vidéo individuelle)
                        self.playlist_content_cache[playlist_url] = [video_data]
                        
                        playlist_title = playlist_data.get('title', 'Vidéo')
                        self.root.after(0, lambda: self._display_playlist_content([video_data], playlist_title, target_tab))
                    else:
                        self.root.after(0, lambda: self._show_playlist_error("Impossible de charger le contenu"))
                        
            except Exception as e:
                print(f"Erreur chargement contenu playlist: {e}")
                self.root.after(0, lambda: self._show_playlist_error(str(e)))
        
        # Afficher un message de chargement dans l'onglet cible
        self._show_playlist_loading(playlist_data.get('title', 'Contenu'), target_tab)
        
        # Lancer en arrière-plan
        threading.Thread(target=load_playlist_content, daemon=True).start()
    
    def _show_playlist_loading(self, playlist_title, target_tab="sorties"):
        """Affiche un message de chargement pour la playlist"""
        # Choisir l'onglet cible
        target_frame = self.playlists_frame if target_tab == "playlists" else self.sorties_frame
        
        # Vider l'onglet cible et afficher le chargement
        for widget in target_frame.winfo_children():
            widget.destroy()
        
        loading_label = tk.Label(
            target_frame,
            text=f"Chargement de la playlist:\n{playlist_title}...",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        loading_label.pack(expand=True)
    
    def _display_playlist_content(self, videos, playlist_title, target_tab="sorties"):
        """Affiche le contenu d'une playlist avec la même interface que l'onglet Musiques"""
        # Choisir l'onglet cible
        target_frame = self.playlists_frame if target_tab == "playlists" else self.sorties_frame
        
        # Vider l'onglet cible
        for widget in target_frame.winfo_children():
            widget.destroy()
        
        if not videos:
            no_results_label = tk.Label(
                target_frame,
                text="Aucune vidéo trouvée dans cette playlist",
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 10)
            )
            no_results_label.pack(expand=True)
            return
        
        # Créer un frame pour le titre et le bouton retour
        header_frame = tk.Frame(target_frame, bg='#3d3d3d')
        header_frame.pack(fill="x", padx=5, pady=5)
        
        # Créer le bouton retour à côté de la croix de l'artiste (dans le container principal)
        back_command = self._return_to_playlists_tab if target_tab == "playlists" else self._return_to_playlists
        
        # Trouver le container principal (parent de target_frame)
        main_container = target_frame.master.master  # target_frame -> notebook -> main_container
        
        if hasattr(self, 'icons') and 'back' in self.icons:
            self.playlist_back_btn = tk.Button(
                main_container,
                image=self.icons['back'],
                bg='#3d3d3d',
                activebackground='#4a8fe7',
                relief='raised',
                bd=1,
                width=20,
                height=20,
                command=back_command,
                cursor='hand2',
                takefocus=0
            )
        else:
            # Fallback si l'icône n'est pas disponible
            self.playlist_back_btn = tk.Button(
                main_container,
                text="←",
                bg='#3d3d3d',
                fg='white',
                activebackground='#4a8fe7',
                relief='raised',
                bd=1,
                font=('TkDefaultFont', 10, 'bold'),
                width=20,
                height=20,
                command=back_command,
                cursor='hand2',
                takefocus=0
            )
        
        # Positionner le bouton à gauche de la croix (croix à x=-5, back à x=-40 pour plus d'espace)
        self.playlist_back_btn.place(in_=main_container, relx=1.0, rely=0.0, anchor="ne", x=-40, y=5)
        self.playlist_back_btn.tkraise()  # Mettre le bouton au premier plan
        
        # Titre de la playlist
        title_label = tk.Label(
            header_frame,
            text=f"Playlist: {playlist_title}",
            bg='#3d3d3d',
            fg='white',
            font=('TkDefaultFont', 10, 'bold')
        )
        title_label.pack(side="left", padx=(10, 0))
        
        # Créer un canvas scrollable pour les vidéos
        canvas = tk.Canvas(target_frame, bg='#3d3d3d', highlightthickness=0)
        scrollbar = ttk.Scrollbar(target_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#3d3d3d')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaqueter le canvas et la scrollbar
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Afficher les vidéos dans le frame scrollable
        for i, video in enumerate(videos):
            self._add_artist_result(video, i, scrollable_frame)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel_recursive(widget):
            """Bind mousewheel à un widget et tous ses enfants"""
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        bind_mousewheel_recursive(scrollable_frame)
        
        self.status_bar.config(text=f"{len(videos)} vidéos dans la playlist '{playlist_title}'")
    
    def _return_to_playlists(self):
        """Retourne à l'affichage des playlists dans l'onglet Sorties"""
        # Relancer la recherche des releases (playlists) pour l'onglet Sorties
        if hasattr(self, 'artist_releases_thread') and self.artist_releases_thread and self.artist_releases_thread.is_alive():
            return  # Déjà en cours
        
        # Vider l'onglet sorties (pas de message de chargement)
        for widget in self.sorties_frame.winfo_children():
            widget.destroy()
        
        # Relancer la recherche des releases
        self.artist_releases_thread = threading.Thread(target=self._search_artist_releases_with_id, daemon=True)
        self.artist_releases_thread.start()
    
    def _return_to_playlists_tab(self):
        """Retourne à l'affichage des playlists dans l'onglet Playlists"""
        # Relancer la recherche des playlists pour l'onglet Playlists
        if hasattr(self, 'artist_playlists_thread') and self.artist_playlists_thread and self.artist_playlists_thread.is_alive():
            return  # Déjà en cours
        
        # Vider l'onglet playlists (pas de message de chargement)
        for widget in self.playlists_frame.winfo_children():
            widget.destroy()
        
        # Relancer la recherche des playlists
        self.artist_playlists_thread = threading.Thread(target=self._search_artist_playlists_with_id, daemon=True)
        self.artist_playlists_thread.start()
    
    def _show_playlist_error(self, error_msg):
        """Affiche une erreur lors du chargement d'une playlist"""
        # Vider l'onglet sorties
        for widget in self.sorties_frame.winfo_children():
            widget.destroy()
        
        error_label = tk.Label(
            self.sorties_frame,
            text=f"Erreur lors du chargement de la playlist:\n{error_msg}",
            bg='#3d3d3d',
            fg='#ff6666',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        error_label.pack(expand=True)
    
    def _display_videos_error(self, error_msg):
        """Affiche une erreur dans l'onglet Musiques"""
        # Supprimer le message de chargement
        if hasattr(self, 'musiques_loading'):
            self.musiques_loading.destroy()
        
        error_label = tk.Label(
            self.musiques_frame,
            text=f"Erreur lors du chargement des musiques:\n{error_msg}",
            bg='#3d3d3d',
            fg='#ff6666',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        error_label.pack(expand=True)
    
    def _display_releases_error(self, error_msg):
        """Affiche une erreur dans l'onglet Sorties"""
        # Supprimer le message de chargement
        if hasattr(self, 'sorties_loading'):
            self.sorties_loading.destroy()
        
        error_label = tk.Label(
            self.sorties_frame,
            text=f"Erreur lors du chargement des sorties:\n{error_msg}",
            bg='#3d3d3d',
            fg='#ff6666',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        error_label.pack(expand=True)
    
    def _display_playlists_error(self, error_msg):
        """Affiche une erreur dans l'onglet Playlists"""
        # Supprimer le message de chargement
        if hasattr(self, 'playlists_loading'):
            self.playlists_loading.destroy()
        
        error_label = tk.Label(
            self.playlists_frame,
            text=f"Erreur lors du chargement des playlists:\n{error_msg}",
            bg='#3d3d3d',
            fg='#ff6666',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        error_label.pack(expand=True)
    
    def _return_to_search(self):
        """Retourne instantanément à l'affichage de recherche normal"""
        try:
            # Annuler toutes les recherches artiste en cours
            self.artist_search_cancelled = True
            
            # Sortir du mode artiste
            self.artist_mode = False
            self.current_artist_name = ""
            self.current_artist_channel_url = ""
            self.current_artist_channel_id = None
            
            # Supprimer le notebook artiste et la croix
            if hasattr(self, 'artist_notebook') and self.artist_notebook.winfo_exists():
                self.artist_notebook.destroy()
                delattr(self, 'artist_notebook')
            
            # Supprimer la croix si elle existe
            if hasattr(self, 'artist_close_btn') and self.artist_close_btn.winfo_exists():
                self.artist_close_btn.destroy()
                delattr(self, 'artist_close_btn')
            
            # Supprimer le bouton retour playlist si il existe
            if hasattr(self, 'playlist_back_btn') and self.playlist_back_btn.winfo_exists():
                self.playlist_back_btn.destroy()
                delattr(self, 'playlist_back_btn')
            
            # Restaurer l'état original des résultats de recherche
            if hasattr(self, 'saved_search_state'):
                # Restaurer la scrollbar si elle était affichée
                if (self.saved_search_state.get('scrollbar_packed', False) and 
                    hasattr(self, 'scrollbar') and self.scrollbar.winfo_exists()):
                    self.scrollbar.pack(side="right", fill="y")
                
                # Restaurer le canvas si il était affiché
                if (self.saved_search_state.get('canvas_packed', False) and 
                    hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists()):
                    self.youtube_canvas.pack(side="left", fill="both", expand=True)
                
                # Restaurer la thumbnail frame si elle était affichée
                if (self.saved_search_state.get('thumbnail_packed', False) and 
                    hasattr(self, 'thumbnail_frame') and self.thumbnail_frame.winfo_exists()):
                    self.thumbnail_frame.pack(fill='both', pady=5, padx=5, anchor="center")
            else:
                # Si pas d'état sauvegardé, afficher la thumbnail par défaut
                if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame.winfo_exists():
                    self.thumbnail_frame.pack(fill='both', pady=5, padx=5, anchor="center")
            
            # Restaurer la position de scroll si elle était sauvegardée
            if hasattr(self, 'saved_search_state') and self.saved_search_state['scroll_position']:
                try:
                    scroll_top, scroll_bottom = self.saved_search_state['scroll_position']
                    # Vérifier que le canvas existe encore avant de tenter le scroll
                    if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
                        # Utiliser after pour s'assurer que le scroll se fait après la restauration
                        self.root.after(10, lambda: self.youtube_canvas.yview_moveto(scroll_top))
                except:
                    pass
            
            # Nettoyer les références des threads
            self.artist_videos_thread = None
            self.artist_releases_thread = None  
            self.artist_playlists_thread = None
            
            # Nettoyer les références des frames
            if hasattr(self, 'musiques_frame'):
                delattr(self, 'musiques_frame')
            if hasattr(self, 'sorties_frame'):
                delattr(self, 'sorties_frame')
            if hasattr(self, 'playlists_frame'):
                delattr(self, 'playlists_frame')
            if hasattr(self, 'musiques_loading'):
                delattr(self, 'musiques_loading')
            if hasattr(self, 'sorties_loading'):
                delattr(self, 'sorties_loading')
            if hasattr(self, 'playlists_loading'):
                delattr(self, 'playlists_loading')
            
            self.status_bar.config(text="Retour à la recherche normale")
            
        except Exception as e:
            print(f"Erreur lors du retour à la recherche: {e}")
            self.status_bar.config(text=f"Erreur: {e}")
    
    def on_closing(self):
        return inputs.on_closing(self)
    def save_youtube_url_metadata(self, filepath, youtube_url, upload_date=None):
        """Sauvegarde les métadonnées YouTube étendues pour un fichier téléchargé"""
        return tools.save_youtube_url_metadata(self, filepath, youtube_url, upload_date)
    
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

    def clear_all_current_song_selections(self):
        """Nettoie la sélection dans tous les containers d'affichage"""
        return clear_all_current_song_selections(self)
    
    def clear_current_song_selection(self):
        """Nettoie la sélection dans la playlist principale"""
        return clear_current_song_selection(self)
    
    def clear_current_song_selection_in_downloads(self):
        """Nettoie la sélection dans l'onglet téléchargements"""
        return clear_current_song_selection_in_downloads(self)
    
    def clear_current_song_selection_in_playlists(self):
        """Nettoie la sélection dans l'affichage des playlists"""
        return clear_current_song_selection_in_playlists(self)

    def reset_main_playlist(self):
        return search_tab.main_playlist.reset_main_playlist(self)

if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.on_closing)
    root.mainloop()
