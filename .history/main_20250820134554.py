try:
    from apply_optimizations import apply_all_optimizations
    OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    OPTIMIZATIONS_AVAILABLE = False



# Import centralisé depuis __init__.py
from __init__ import *
from clear_current_selection import (
    clear_all_current_song_selections,
    clear_current_song_selection,
    clear_current_song_selection_in_downloads,
    clear_current_song_selection_in_playlists
)
from artist_tab_manager import init_artist_tab_manager
from cache_cleaner import (
    _clear_search_cache,
    _clear_artist_cache,
    _clear_thumbnail_cache,
    _clear_playlist_content_cache,
    _clear_duration_cache,
    _clear_all_caches
)

# Import du système IA
try:
    from ai_menu_system import setup_ai_menu_system
    AI_MENU_AVAILABLE = True
    print("🤖 Système de menu IA disponible")
except ImportError as e:
    print(f"⚠️ Système de menu IA non disponible: {e}")
    AI_MENU_AVAILABLE = False


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
        root.option_add("*TNotebook.takeFocus", 0)

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
        self.paused = True
        self.volume = 0.2
        self.volume_offset = 0  # Offset de volume en pourcentage (-100 à +100)
        
        self.scroll_timeout = None
        
        # Charger le dossier de téléchargements personnalisé s'il existe
        self.downloads_folder = self._load_downloads_path()
        print("self.downloads_folder:", self.downloads_folder)
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'outtmpl': os.path.join(self.downloads_folder, '%(title)s.%(ext)s'),
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
        
        # Variables pour la sélection multiple
        self.selected_items = set()  # Set des chemins de fichiers sélectionnés
        self.selected_items_order = []  # Liste ordonnée des chemins de fichiers sélectionnés (pour maintenir l'ordre de clic)
        self.selection_frames = {}  # Dictionnaire {filepath: frame} pour retrouver les frames
        self.shift_selection_active = False  # True quand on est en mode sélection Shift
        
        # Variables pour la surveillance du dossier downloads
        # self.downloads_watcher_active = False
        # self.downloads_watcher_thread = None
        # self.last_downloads_count = 0
        # self.downloads_check_interval = 2  # Vérifier toutes les 2 secondes

        self.song_length = 0
        self.current_time = 0

        self.user_dragging = False
        self.base_position = 0
        self.update_suspended = False  # True si les mises à jour sont suspendues

        self.show_waveform_current = False

        # Variables pour les modes de lecture
        self.random_mode = False
        self.loop_mode = 0  # 0: désactivé, 1: loop playlist, 2: loop chanson actuelle

        # Variables pour la gestion du volume
        self.volume_offsets = {}  # Dictionnaire {filepath: offset_volume}
        self.config_file = os.path.join(self.downloads_folder, "player_config.json")
        self.initializing = True  # Flag pour éviter de sauvegarder pendant l'initialisation

        # Variable pour le périphérique audio actuel
        self.current_audio_device = None  # Nom du périphérique audio actuel

        # Chargement des icônes
        self.icons = {}
        setup.load_icons(self)

        # Initialiser le gestionnaire de drag-and-drop
        self.drag_drop_handler = DragDropHandler(self)

        # Initialiser le gestionnaire d'onglets artiste
        init_artist_tab_manager(self)

        # UI Modern
        setup.create_ui(self)

        # Initialiser le système IA après la création de l'interface
        self.setup_ai_system()

        # Mettre à jour les sliders avec les valeurs chargées
        setup._update_volume_sliders(self)
        # self._update_volume_sliders()

        # Marquer la fin de l'initialisation
        self.initializing = False

        # Initialiser le système de recommandation
        recommendation.init_recommendation_system(self)

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
        
        # Cache pour optimiser les performances
        self.widget_cache = {}  # Cache des widgets réutilisables
        self.thumbnail_cache = {}  # Cache des miniatures chargées

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
        self.main_playlist_is_loading_more_items = False  # True si la main playlist est en cours de chargement plus d'items
        # self._last_window_start = None  # Index du début de la fenêtre
        # self._last_window_end = None  # Index de la fin de la fenêtre

        # Système de gestion des erreurs
        self.system_errors = []  # Liste des erreurs système

        # Variables pour l'animation de scroll
        self.scroll_animation_active = False  # True si une animation est en cours
        self.scroll_animation_id = None  # ID du timer d'animation

        # Variables pour l'auto-scroll
        self.auto_scroll_enabled = False  # True si l'auto-scroll est activé
        self.manual_scroll_detected = False  # True si l'utilisateur a scrollé manuellement

        # Variables pour l'animation du titre
        self.title_animation_active = False  # True si l'animation du titre est en cours
        # self.title_animation_id = None  # ID du timer d'animation du titre
        self.title_full_text = ""  # Texte complet du titre
        self.title_scroll_position = 0  # Position actuelle du défilement
        self.title_pause_counter = 0  # Compteur pour la pause entre les cycles
        
        # Variables pour l'animation du nom d'artiste
        self.artist_name_animation_active = False  # True si l'animation du nom d'artiste est en cours
        self.artist_name_animation_id = None  # ID du timer d'animation du nom d'artiste
        self.artist_name_full_text = ""  # Texte complet du nom d'artiste
        self.artist_name_scroll_position = 0  # Position actuelle du défilement
        self.artist_name_pause_counter = 0  # Compteur pour la pause entre les cycles

        # Variables pour optimiser les performances lors du déplacement de fenêtre
        self.window_moving = False  # True si la fenêtre est en cours de déplacement
        self.window_move_start_time = 0  # Timestamp du début du déplacement
        self.last_window_position = None  # Dernière position connue de la fenêtre

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

        # Variables pour la gestion du bouton retour unique dans les onglets artiste
        self.artist_tab_back_btn = None  # Bouton retour unique
        self.artist_tab_active_sorties = False  # True si du contenu de playlist est affiché dans Sorties
        self.artist_tab_active_playlists = False  # True si du contenu de playlist est affiché dans Playlists

        # Variables pour le système de recommandations
        self.recommendation_enabled = False  # True si les recommandations sont activées
        self.recommendation_mode = "sparse"  # "sparse" ou "add"
        self.last_recommendation_mode = "sparse"  # Dernier mode utilisé pour l'aperçu
        
        # Variables pour les likes et favorites
        self.liked_songs = set()  # Set des chansons likées
        self.favorite_songs = set()  # Set des chansons favorites

        # Charger les playlists sauvegardées
        self.load_playlists()

        # Initialiser le gestionnaire de fichiers
        self.init_file_tracker()

        # Charger la configuration (volume global et offsets)
        self.load_config()
        
        search_tab.main_playlist._setup_dynamic_scroll(self)

        # Initialiser le périphérique audio actuel si pas encore défini
        if self.current_audio_device is None:
            self._detect_current_audio_device()

        # Compter les fichiers téléchargés au démarrage
        self._count_downloaded_files()

        # Initialiser la surveillance du dossier downloads
        # self.init_downloads_watcher()

        # Bindings de clavier
        self.setup_keyboard_bindings()

        # Gérer la fermeture propre de l'application
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Optimisations pour le déplacement de fenêtre
        self.setup_window_move_optimization()

        if OPTIMIZATIONS_AVAILABLE:
            self.optimizers = apply_all_optimizations(self)
        
        # self.colorize_ttk_frames(root)

    def load_playlists(self):

        setup.load_playlists(self)

    def load_config(self):
        setup.load_config(self)

    def _count_downloaded_files(self):
        file_services._count_downloaded_files(self)

    def setup_keyboard_bindings(self):
        setup.setup_keyboard_bindings(self)

    def setup_ai_system(self):
        """Configure le système d'IA"""
        if AI_MENU_AVAILABLE:
            try:
                self.ai_menu_system = setup_ai_menu_system(self)
                print("🤖 Système de menu IA configuré avec succès")
                
                # Créer le bouton IA après l'initialisation du système
                self.create_ai_button_after_init()
                
            except Exception as e:
                print(f"⚠️ Erreur configuration menu IA: {e}")
                self.ai_menu_system = None
        else:
            self.ai_menu_system = None

    def create_ai_button_after_init(self):
        """Crée le bouton IA après l'initialisation du système IA"""
        if hasattr(self, 'ai_menu_system') and self.ai_menu_system:
            try:
                # Trouver le frame des boutons en cherchant le bouton auto_scroll
                def find_buttons_frame(widget):
                    """Trouve le frame des boutons récursivement"""
                    try:
                        for child in widget.winfo_children():
                            if hasattr(child, 'winfo_children'):
                                # Vérifier si ce widget contient le bouton auto_scroll
                                for grandchild in child.winfo_children():
                                    if hasattr(self, 'auto_scroll_btn') and grandchild == self.auto_scroll_btn:
                                        return child
                                
                                # Chercher récursivement
                                result = find_buttons_frame(child)
                                if result:
                                    return result
                    except:
                        pass
                    return None
                
                buttons_frame = find_buttons_frame(self.root)
                
                # Utiliser le bouton IA déjà créé dans setup.py
                if hasattr(self, 'ai_button'):
                    # Configurer le bouton existant avec le système de menu IA
                    self.ai_button.config(command=self.ai_menu_system.show_ai_menu)
                    
                    # Mettre à jour l'apparence selon l'état
                    self.ai_menu_system.ai_button = self.ai_button
                    self.ai_menu_system.update_button_appearance()
                    
                    # Créer le menu contextuel
                    self.ai_menu_system.create_context_menu()
                    
                    print("🤖 Bouton IA configuré avec succès")
                    return True
                else:
                    print("⚠️ Bouton IA non trouvé dans l'interface")
                    return False
                    
            except Exception as e:
                print(f"⚠️ Erreur création bouton IA: {e}")
                return False
        else:
            print("⚠️ Système IA non disponible pour création bouton")
            return False

    def setup_window_move_optimization(self):
        """Configure les optimisations pour le déplacement de fenêtre"""
        # Détecter le début du déplacement de fenêtre
        self.root.bind('<Button-1>', self._on_window_click)
        self.root.bind('<B1-Motion>', self._on_window_drag)
        self.root.bind('<ButtonRelease-1>', self._on_window_release)
        
        # Surveiller les changements de position de fenêtre
        self.last_window_position = (self.root.winfo_x(), self.root.winfo_y())
        self._monitor_window_position()

    def _on_window_click(self, event):
        """Détecte le début d'un potentiel déplacement de fenêtre"""
        # Vérifier si le clic est sur la barre de titre (approximativement)
        if event.y < 30:  # Zone approximative de la barre de titre
            self.window_move_start_time = time.time()

    def _on_window_drag(self, event):
        """Détecte le déplacement de fenêtre en cours"""
        if self.window_move_start_time > 0 and event.y < 30:
            if not self.window_moving:
                self.window_moving = True
                self.update_suspended = True
                # Réduire la fréquence des mises à jour pendant le déplacement

    def _on_window_release(self, event):
        """Détecte la fin du déplacement de fenêtre"""
        if self.window_moving:
            self.window_moving = False
            self.update_suspended = False
            self.window_move_start_time = 0
            # Reprendre les mises à jour normales

    def _monitor_window_position(self):
        """Surveille les changements de position de fenêtre"""
        try:
            if hasattr(self, '_app_destroyed') and self._app_destroyed:
                return
                
            current_pos = (self.root.winfo_x(), self.root.winfo_y())
            
            if self.last_window_position != current_pos:
                # La fenêtre a bougé
                if not self.window_moving:
                    self.window_moving = True
                    self.update_suspended = True
                
                self.last_window_position = current_pos
                
                # Programmer la fin du déplacement après un délai
                if hasattr(self, 'window_move_timer'):
                    self.root.after_cancel(self.window_move_timer)
                
                self.window_move_timer = self.root.after(200, self._end_window_move)
            
            # Continuer la surveillance
            self.root.after(50, self._monitor_window_position)
            
        except (tk.TclError, AttributeError):
            # Interface détruite
            pass

    def _end_window_move(self):
        """Termine l'état de déplacement de fenêtre"""
        self.window_moving = False
        self.update_suspended = False

    def safe_after(self, delay, callback):
        """Version sécurisée de self.root.after qui évite les erreurs de callbacks orphelins"""
        if hasattr(self, '_app_destroyed') and self._app_destroyed:
            return None

        def safe_callback():
            try:
                # Vérifications multiples pour éviter les erreurs
                if (not hasattr(self, '_app_destroyed') or not self._app_destroyed and 
                    hasattr(self, 'root') and self.root and 
                    hasattr(self.root, 'winfo_exists')):
                    try:
                        if self.root.winfo_exists():
                            callback()
                    except tk.TclError:
                        pass  # Widget détruit pendant l'exécution
            except (tk.TclError, AttributeError):
                pass  # Interface détruite, ignorer
            except Exception as e:
                # Ignorer les erreurs de callbacks sur widgets détruits
                if "invalid command name" not in str(e):
                    print(f"Erreur dans callback différé: {e}")

        try:
            if hasattr(self, 'root') and self.root:
                callback_id = self.root.after(delay, safe_callback)
                if hasattr(self, '_pending_callbacks'):
                    self._pending_callbacks.add(callback_id)
                return callback_id
        except (tk.TclError, AttributeError):
            pass
        return None

    def cancel_pending_callbacks(self):
        """Annule tous les callbacks en attente"""
        if not hasattr(self, '_pending_callbacks'):
            return
            
        for callback_id in list(self._pending_callbacks):
            try:
                self.root.after_cancel(callback_id)
            except:
                pass
        self._pending_callbacks.clear()

    def on_artist_tab_changed(self, event):
        """Gère le changement d'onglet dans le notebook artiste"""
        return self.artist_tab_manager.on_artist_tab_changed(event)

    def _update_back_button_visibility(self, current_tab_text):
        """Met à jour la visibilité du bouton retour selon l'onglet actuel et son état"""
        return self.artist_tab_manager._update_back_button_visibility(current_tab_text)

    def _show_playlist_back_button(self):
        """Affiche le bouton retour pour les playlists"""
        return self.artist_tab_manager._show_playlist_back_button()

    def _hide_playlist_back_button(self):
        """Masque le bouton retour pour les playlists"""
        return self.artist_tab_manager._hide_playlist_back_button()

    def _reset_playlist_content_state(self, tab_name=None):
        """Remet à zéro l'état du contenu de playlist pour un onglet spécifique ou tous"""
        return self.artist_tab_manager._reset_playlist_content_state(tab_name)


    def on_closing(self):
        """Gère la fermeture propre de l'application"""

        # Sauvegarder les données IA avant la fermeture
        try:
            if hasattr(self, 'ai_menu_system') and self.ai_menu_system:
                self.ai_menu_system.save_ai_data_on_exit()
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde IA à la fermeture: {e}")

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
    
    # Raccourcis clavier globaux
    def on_global_play_pause(self, event):
        """Raccourci global Ctrl+Alt+P pour play/pause"""
        return inputs.on_global_play_pause(self, event)
    
    def on_global_next_track(self, event):
        """Raccourci global Ctrl+Alt+N pour chanson suivante"""
        return inputs.on_global_next_track(self, event)
    
    def on_global_prev_track(self, event):
        """Raccourci global Ctrl+Alt+B pour chanson précédente"""
        return inputs.on_global_prev_track(self, event)
    
    def on_global_volume_up(self, event):
        """Raccourci global Ctrl+Alt+Up pour augmenter le volume"""
        return inputs.on_global_volume_up(self, event)
    
    def on_global_volume_down(self, event):
        """Raccourci global Ctrl+Alt+Down pour diminuer le volume"""
        return inputs.on_global_volume_down(self, event)
    
    def on_global_volume_key_release(self, event):
        """Appelé quand les touches de volume sont relâchées"""
        return inputs.on_global_volume_key_release(self, event)
    
    def on_global_seek_forward(self, event):
        """Raccourci global Ctrl+Alt+→ pour avancer de 5s"""
        return inputs.on_global_seek_forward(self, event)
    
    def on_global_seek_backward(self, event):
        """Raccourci global Ctrl+Alt+← pour reculer de 5s"""
        return inputs.on_global_seek_backward(self, event)
    
    def on_test_downloads(self, event):
        """Raccourci global Ctrl+Alt+T pour tester les téléchargements"""
        self.add_test_downloads()
        return "break"
    
    def show_download_dialog(self):
        """Affiche une boîte de dialogue pour importer des musiques ou playlists"""
        return inputs.show_download_dialog(self)
    
    # Fonctions pour l'onglet téléchargements
    def setup_downloads_tab(self):
        """Configure l'onglet de téléchargement"""
        return downloads_tab.setup_downloads_tab(self)
    
    def update_downloads_display(self):
        """Met à jour l'affichage des téléchargements"""
        return downloads_tab.update_downloads_display(self)
    
    def remove_completed_download(self, url):
        """Supprime un téléchargement terminé de l'affichage"""
        return downloads_tab.remove_completed_download(self, url)
    
    def add_download_to_tab(self, url, title, video_data=None, file_path=None):
        """Ajoute un téléchargement à l'onglet"""
        return downloads_tab.add_download_to_tab(self, url, title, video_data, file_path)
    
    def add_file_import_to_tab(self, file_path, title=None):
        """Ajoute un import de fichier à l'onglet téléchargements"""
        return downloads_tab.add_file_import_to_tab(self, file_path, title)
    
    def _load_download_thumbnail_from_file(self, label, file_path):
        """Charge et affiche la miniature d'un fichier local"""
        return downloads_tab._load_download_thumbnail_from_file(self, label, file_path)
    
    def toggle_downloads_pause(self):
        """Bascule entre pause et reprise des téléchargements"""
        return downloads_tab.toggle_downloads_pause(self)
    
    def update_download_progress(self, url, progress, status=None):
        """Met à jour la progression d'un téléchargement"""
        return downloads_tab.update_download_progress(self, url, progress, status)
    
    def simulate_download_progress(self, url):
        """Simule la progression d'un téléchargement (pour test)"""
        return downloads_tab.simulate_download_progress(self, url)
    
    # create_download_item_widget supprimée - remplacée par le système de chargement paresseux
    
    def update_download_item_appearance(self, download_item):
        """Met à jour l'apparence d'un élément de téléchargement selon son état"""
        return downloads_tab.update_download_item_appearance(self, download_item)
    
    def handle_delete_download(self, download_item):
        """Gère la suppression/annulation d'un téléchargement selon son état"""
        return downloads_tab.handle_delete_download(self, download_item)
    
    def cancel_active_download(self, download_item):
        """Annule un téléchargement actif"""
        return downloads_tab.cancel_active_download(self, download_item)
    
    def update_progress_overlay(self, download_item):
        """Met à jour la barre de progression verte en arrière-plan"""
        return downloads_tab.update_progress_overlay(self, download_item)
    
    def _update_progress_overlay_delayed(self, download_item):
        """Mise à jour différée de la barre de progression"""
        return downloads_tab._update_progress_overlay_delayed(self, download_item)
    
    def _load_download_thumbnail_from_url(self, label, url):
        """Charge et affiche la miniature d'un téléchargement depuis une URL"""
        return downloads_tab._load_download_thumbnail_from_url(self, label, url)
    
    def _update_thumbnail_label(self, label, photo):
        """Met à jour le label de miniature dans le thread principal"""
        return downloads_tab._update_thumbnail_label(self, label, photo)
    
    def remove_download_item(self, download_item):
        """Supprime un élément de téléchargement de la liste"""
        return downloads_tab.remove_download_item(self, download_item)
    
    def scroll_to_current_download(self):
        """Scroll automatiquement vers le téléchargement en cours avec animation ease in out"""
        return downloads_tab.scroll_to_current_download(self)
    
    def animate_scroll_to_position(self, start_pos, end_pos, duration=500, steps=30):
        """Anime le scroll avec ease in out"""
        return downloads_tab.animate_scroll_to_position(self, start_pos, end_pos, duration, steps)
    
    def go_to_top(self, canvas):
        return tools.go_to_top(self, canvas)
    
    def add_test_downloads(self):
        """Ajoute des téléchargements de test"""
        return downloads_tab.add_test_downloads(self)
    
    def clean_completed_downloads(self):
        """Supprime tous les téléchargements terminés avec succès"""
        return downloads_tab.clean_completed_downloads(self)
    
    # Fonctions pour le gestionnaire de fichiers
    def init_file_tracker(self):
        """Initialise le gestionnaire de fichiers"""
        return file_tracker.init_file_tracker(self)
    
    def rebuild_file_index(self):
        """Reconstruit l'index des fichiers"""
        return file_tracker.rebuild_file_index(self)
    
    def remove_deleted_file_from_playlists(self, filepath):
        """Supprime un fichier supprimé de toutes les playlists"""
        return file_tracker.remove_deleted_file_from_playlists(self, filepath)
    
    def check_missing_files(self):
        """Vérifie et nettoie les fichiers manquants"""
        return file_tracker.check_missing_files(self)
    
    def add_file_to_tracker(self, filepath, playlist_name):
        """Ajoute un fichier au tracker"""
        return file_tracker.add_file_to_tracker(self, filepath, playlist_name)
    
    def remove_file_from_tracker(self, filepath, playlist_name):
        """Supprime un fichier du tracker"""
        return file_tracker.remove_file_from_tracker(self, filepath, playlist_name)
    
    # Fonctions pour les menus contextuels
    def show_file_context_menu(self, filepath, event=None):
        """Affiche un menu contextuel pour un fichier"""
        return ui_menus.show_file_context_menu(self, filepath, event)
    
    def show_unified_context_menu(self, item, event=None, item_type="file"):
        """Affiche un menu contextuel unifié pour fichiers locaux et vidéos YouTube"""
        return ui_menus.show_unified_context_menu(self, item, event, item_type)
    
    def _add_youtube_to_playlist_unified(self, video, playlist_name):
        """Ajoute une vidéo YouTube à une playlist (télécharge d'abord si nécessaire)"""
        return ui_menus._add_youtube_to_playlist_unified(self, video, playlist_name)
    
    def _create_new_playlist_dialog_youtube_unified(self, video):
        """Crée une nouvelle playlist et y ajoute la vidéo YouTube"""
        return ui_menus._create_new_playlist_dialog_youtube_unified(self, video)
    
    def _download_youtube_video(self, video, add_to_main_playlist=False, callback=None):
        """Télécharge une vidéo YouTube"""
        return ui_menus._download_youtube_video(self, video, add_to_main_playlist, callback)

    def _open_youtube_url(self, url):
        """Ouvre une URL YouTube dans le navigateur"""
        return ui_menus._open_youtube_url(self, url)
    
    def _open_downloads_folder(self):
        """Ouvre le dossier downloads"""
        return ui_menus._open_downloads_folder(self)
    
    def _add_to_specific_playlist_with_youtube_support(self, filepath, playlist_name, youtube_item=None):
        """Ajoute un élément à une playlist spécifique (télécharge d'abord si YouTube)"""
        return ui_menus._add_to_specific_playlist_with_youtube_support(self, filepath, playlist_name, youtube_item)
    
    def _create_new_playlist_dialog_with_youtube_support(self, filepath, youtube_item=None):
        """Crée une nouvelle playlist et y ajoute l'élément (télécharge d'abord si YouTube)"""
        return ui_menus._create_new_playlist_dialog_with_youtube_support(self, filepath, youtube_item)
    
    def _open_file_location_with_youtube_support(self, filepath, youtube_item=None):
        """Ouvre le dossier contenant le fichier (downloads pour YouTube)"""
        return ui_menus._open_file_location_with_youtube_support(self, filepath, youtube_item)
    
    def _open_on_youtube_with_youtube_support(self, filepath, youtube_item=None):
        """Ouvre sur YouTube (URL directe pour YouTube, recherche pour fichier local)"""
        return ui_menus._open_on_youtube_with_youtube_support(self, filepath, youtube_item)
    
    def _download_and_add_to_playlist(self, youtube_item, playlist_name):
        """Télécharge une vidéo YouTube et l'ajoute à une playlist"""
        return ui_menus._download_and_add_to_playlist(self, youtube_item, playlist_name)
    
    def _open_file_location(self, filepath):
        """Ouvre le dossier contenant le fichier"""
        return ui_menus._open_file_location(self, filepath)
    
    def _open_on_youtube(self, filepath):
        """Ouvre la vidéo sur YouTube"""
        return ui_menus._open_on_youtube(self, filepath)

    def _open_on_youtube_from_result(self, video):
        """Ouvre la vidéo sur YouTube à partir des résultats"""
        return ui_menus._open_on_youtube_from_result(self, video)

    def _delete_file_permanently(self, filepath):
        """Supprime définitivement un fichier"""
        return ui_menus._delete_file_permanently(self, filepath)

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
        return search_tab.results._update_stats_bar(self)

    
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
            if self.current_library_tab == "téléchargées":
                self._check_and_update_downloads_queue()
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
        return search_tab.results._should_load_more_results(self)

    def _on_scrollbar_release(self, event):
        """Appelée quand on relâche la scrollbar"""
        return search_tab.results._on_scrollbar_release(self, event)

    def _check_scroll_position(self):
        """Vérifie la position du scroll et charge plus si nécessaire"""
        return search_tab.results._check_scroll_position(self)


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

    def _check_and_update_downloads_queue(self):
        """Vérifie si la queue des musiques a changé et met à jour l'affichage si nécessaire"""
        try:
            if not hasattr(self, 'queue_items'):
                return
            # Vérifier si on a une queue précédente sauvegardée
            if not hasattr(self, '_last_downloads_queue'):
                # Première fois, sauvegarder la queue actuelle
                self._last_downloads_queue = self.queue_items.copy()
                return
            # Comparer avec la queue précédente
            if self.queue_items != self._last_downloads_queue:
                # La queue a changé, mettre à jour l'affichage
                self._last_downloads_queue = self.queue_items.copy()
                # Programmer la mise à jour après que le contenu soit affiché
                if hasattr(self, 'safe_after'):
                    self.safe_after(100, self._update_downloads_queue_visual)
                else:
                    self.root.after(100, self._update_downloads_queue_visual)
        except Exception as e:
            print(f"Erreur lors de la vérification de la queue des téléchargements: {e}")

    def _update_saved_downloads_queue(self):
        """Met à jour la queue sauvegardée pour la détection de changements"""
        try:
            if hasattr(self, 'queue_items') and self.queue_items:
                self._last_downloads_queue = self.queue_items.copy()
            else:
                self._last_downloads_queue = set()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la queue sauvegardée: {e}")

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
    
    def show_errors_dialog(self):
        """Affiche une fenêtre avec les erreurs système"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Erreurs Système")
        dialog.geometry("600x400")
        dialog.configure(bg='#2d2d2d')
        dialog.resizable(True, True)
        
        # Centrer la fenêtre
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = tk.Label(
            main_frame,
            text="Erreurs Système Détectées",
            bg='#2d2d2d',
            fg='white',
            font=('TkDefaultFont', 12, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Frame pour la liste des erreurs avec scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar et Listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            list_frame,
            bg='#3d3d3d',
            fg='white',
            selectbackground='#4a8fe7',
            yscrollcommand=scrollbar.set,
            font=('Consolas', 9)
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Ajouter les erreurs
        if not self.system_errors:
            listbox.insert(tk.END, "Aucune erreur détectée.")
        else:
            for i, error in enumerate(self.system_errors):
                timestamp = time.strftime("%H:%M:%S", time.localtime(error['timestamp']))
                error_text = f"[{timestamp}] {error['message']}"
                listbox.insert(tk.END, error_text)
        
        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Bouton Clear Errors
        clear_btn = tk.Button(
            button_frame,
            text="Effacer les erreurs",
            command=lambda: self._clear_errors(listbox),
            bg='#d9534f',
            fg='white',
            activebackground='#c9302c',
            relief="flat",
            bd=0,
            padx=20,
            pady=5
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton Close
        close_btn = tk.Button(
            button_frame,
            text="Fermer",
            command=dialog.destroy,
            bg='#5bc0de',
            fg='white',
            activebackground='#46b8da',
            relief="flat",
            bd=0,
            padx=20,
            pady=5
        )
        close_btn.pack(side=tk.RIGHT)
    
    def _clear_errors(self, listbox):
        """Efface toutes les erreurs système"""
        self.system_errors.clear()
        listbox.delete(0, tk.END)
        listbox.insert(tk.END, "Aucune erreur détectée.")
    
    def show_settings_menu(self, listbox):
    
    def _is_valid_music_path(self, path):
        """Vérifie si un chemin a un format valide pour un fichier musical"""
        import re
        
        # Vérifier que le chemin n'est pas vide
        if not path or not path.strip():
            return False
        
        # Vérifier qu'il y a une extension
        if '.' not in path:
            return False
        
        # Extraire le nom de fichier (sans le chemin)
        filename = os.path.basename(path)
        
        # Vérifier le format: doit avoir un nom et une extension
        if not re.match(r'^.+\..+$', filename):
            return False
        
        # Vérifier que l'extension est valide pour un fichier audio
        valid_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma']
        file_extension = os.path.splitext(filename)[1].lower()
        
        return file_extension in valid_extensions

    def _reload_playlists(self):
        """Recharge les playlists depuis le fichier JSON"""
        return library_tab.playlists._reload_playlists(self)

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

    def _scroll_to_current_song(self, event=None, is_manual=False):
        """Fait défiler la liste de lecture vers la chanson en cours (même position que "piste suivante")"""
        return search_tab.main_playlist._scroll_to_current_song(self, event, is_manual)

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

    def _disable_play_buttons(self):
        """Désactive temporairement les boutons de lecture pour éviter les clics multiples"""
        try:
            # Trouver et désactiver les boutons de lecture dans l'onglet downloads
            if hasattr(self, 'library_content_frame'):
                for widget in self.library_content_frame.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Button):
                                # Vérifier si c'est un bouton de lecture (par sa commande)
                                try:
                                    command = child.cget('command')
                                    if (command == self.play_all_downloads_ordered or
                                        command == self.play_all_downloads_shuffle):
                                        child.config(state='disabled')
                                except:
                                    pass
        except Exception as e:
            print(f"Erreur lors de la désactivation des boutons: {e}")

    def _enable_play_buttons(self):
        """Réactive les boutons de lecture"""
        try:
            # Trouver et réactiver les boutons de lecture dans l'onglet downloads
            if hasattr(self, 'library_content_frame'):
                for widget in self.library_content_frame.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Button):
                                # Vérifier si c'est un bouton de lecture (par sa commande)
                                try:
                                    command = child.cget('command')
                                    if (command == self.play_all_downloads_ordered or
                                        command == self.play_all_downloads_shuffle):
                                        child.config(state='normal')
                                except:
                                    pass
        except Exception as e:
            print(f"Erreur lors de la réactivation des boutons: {e}")

    def _refresh_main_playlist_display_async(self):
        """Version asynchrone du rafraîchissement pour éviter les lags lors du chargement de grandes playlists"""
        return search_tab.main_playlist._refresh_main_playlist_display_async(self)

    def _refresh_full_playlist_display(self):
        """Rafraîchit complètement l'affichage de la playlist (version originale)"""
        return search_tab.main_playlist._refresh_full_playlist_display(self)

    def _refresh_windowed_playlist_display(self, force_recreate=False):
        """Rafraîchit l'affichage avec fenêtrage optimisé (n'affiche que les éléments visibles)"""
        return search_tab.main_playlist._refresh_windowed_playlist_display(self, force_recreate)

    def _preload_metadata_async(self, start_index, end_index):
        """Précharge les métadonnées des chansons dans la fenêtre visible de manière asynchrone"""
        return search_tab.main_playlist._preload_metadata_async(self, start_index, end_index)

    def _update_current_song_highlight_only(self):
        """Met à jour uniquement la surbrillance de la chanson courante sans recréer les widgets"""
        return search_tab.main_playlist._update_current_song_highlight_only(self)

    def _add_playlist_indicator(self, text, position):
        """Ajoute un indicateur visuel pour les éléments non affichés"""
        return search_tab.main_playlist._add_playlist_indicator(self, text, position)

    def _highlight_current_song_widget(self, widget):
        """Met en surbrillance le widget de la chanson courante"""
        return search_tab.main_playlist._highlight_current_song_widget(self, widget)

    # def _set_item_colors(self, item_frame, bg_color):
    #     """Change la couleur de fond d'un élément de playlist et de ses enfants"""
    #     return search_tab.main_playlist._set_item_colors(self, item_frame, bg_color)

    def _update_canvas_scroll_region(self):
        """Met à jour la région de scroll du canvas pour permettre le scroll avec la molette"""
        return search_tab.main_playlist._update_canvas_scroll_region(self)

    def _setup_infinite_scroll(self):
        """Configure le scroll infini pour charger plus d'éléments (redirige vers dynamic_scroll)"""
        return search_tab.main_playlist._setup_dynamic_scroll(self)

    # def _on_playlist_canvas_configure(self, event):
    #     """Appelée quand le canvas de playlist change de taille"""
    #     return search_tab.main_playlist._on_playlist_canvas_configure(self, event)

    def _check_infinite_scroll(self, event=None):
        """Vérifie si on doit charger plus d'éléments en haut ou en bas"""
        return search_tab.main_playlist._check_infinite_scroll(self, event)

    def _load_more_songs_above(self):
        """Charge plus de musiques au-dessus de la fenêtre actuelle"""
        return search_tab.main_playlist._load_more_songs_above(self)

    def _load_more_songs_below(self, unload=False):
        """Charge plus de musiques en-dessous de la fenêtre actuelle"""
        return search_tab.main_playlist._load_more_songs_below(self, unload=unload)

    def _extend_window_up(self, new_start):
        """Étend la fenêtre d'affichage vers le haut"""
        return search_tab.main_playlist._extend_window_up(self, new_start)

    def _extend_window_down(self, new_end):
        """Étend la fenêtre d'affichage vers le bas"""
        return search_tab.main_playlist._extend_window_down(self, new_end)

    def _add_main_playlist_item_at_position(self, filepath, song_index=None, position='bottom'):
        """Ajoute un élément de playlist à une position spécifique (top ou bottom)"""
        return search_tab.main_playlist._add_main_playlist_item_at_position(self, filepath, song_index, position)

    def _create_playlist_item_frame(self, filepath, song_index=None):
        """Crée un frame pour un élément de playlist"""
        return search_tab.main_playlist._create_playlist_item_frame(self, filepath, song_index)

    def _on_scroll_with_update(self, event):
        """Gère le scroll avec mise à jour du scroll infini"""
        return search_tab.main_playlist._on_scroll_with_update(self, event)

    def _mark_user_scrolling(self):
        """Marque que l'utilisateur est en train de scroller manuellement"""
        return search_tab.main_playlist._mark_user_scrolling(self)

    def _on_user_scroll_timeout(self):
        """Appelée quand l'utilisateur a fini de scroller"""
        return search_tab.main_playlist._on_user_scroll_timeout(self)

    def _check_and_recenter_if_needed(self):
        """Vérifie si on doit recentrer sur la chanson courante"""
        return search_tab.main_playlist._check_and_recenter_if_needed(self)

    def _should_recenter_on_song_change(self):
        """Détermine si on doit recentrer sur la nouvelle chanson courante"""
        return search_tab.main_playlist._should_recenter_on_song_change(self)

    def _auto_center_on_current_song(self):
        """Recentre automatiquement l'affichage sur la chanson courante"""
        return search_tab.main_playlist._auto_center_on_current_song(self)

    def _update_windowed_display(self, start_index, end_index, center_index):
        """Met à jour l'affichage avec une nouvelle fenêtre"""
        return search_tab.main_playlist._update_windowed_display(self, start_index, end_index, center_index)

    def _update_display_based_on_scroll_position(self):
        """Met à jour l'affichage des musiques basé sur la position de scroll"""
        return search_tab.main_playlist._update_display_based_on_scroll_position(self)

    # Méthodes de chargement/déchargement intelligent
    def _calculate_smart_window(self):
        """Calcule la fenêtre intelligente à garder chargée"""
        return search_tab.main_playlist._calculate_smart_window(self)

    def _get_current_view_position(self):
        """Détermine la position centrale de ce que voit l'utilisateur"""
        return search_tab.main_playlist._get_current_view_position(self)

    def _smart_load_unload(self):
        """Effectue le chargement/déchargement intelligent"""
        return search_tab.main_playlist._smart_load_unload(self)

    def _unload_unused_items(self, target_start, target_end, current_start, current_end):
        """Décharge les éléments qui ne sont plus nécessaires"""
        return search_tab.main_playlist._unload_unused_items(self, target_start, target_end, current_start, current_end)

    def _load_required_items(self, target_start, target_end, current_start, current_end):
        """Charge les nouveaux éléments nécessaires"""
        return search_tab.main_playlist._load_required_items(self, target_start, target_end, current_start, current_end)

    def _trigger_smart_reload_on_song_change(self):
        """Déclenche le rechargement intelligent lors d'un changement de musique"""
        return search_tab.main_playlist._trigger_smart_reload_on_song_change(self)

    # def _check_smart_reload_on_scroll(self):
    #     """Vérifie si on doit déclencher un smart reload suite au scroll"""
    #     return search_tab.main_playlist._check_smart_reload_on_scroll(self)

    def _force_reload_window(self, start_index, end_index):
        """Force le rechargement d'une fenêtre spécifique"""
        return search_tab.main_playlist._force_reload_window(self, start_index, end_index)

    def _highlight_current_song_in_window(self, start_index, end_index):
        """Remet en surbrillance la chanson courante si elle est dans la fenêtre"""
        return search_tab.main_playlist._highlight_current_song_in_window(self, start_index, end_index)

    def select_current_song_smart(self, auto_scroll=True, force_reload=False, is_manual=False):
        """Sélectionne la chanson courante avec le système intelligent"""
        return search_tab.main_playlist.select_current_song_smart(self, auto_scroll, force_reload, is_manual)

    # === SYSTÈME DE SCROLL DYNAMIQUE UNIFIÉ ===
    
    def _setup_dynamic_scroll(self):
        """Configure le système de scroll dynamique unifié"""
        return search_tab.main_playlist._setup_dynamic_scroll(self)
    
    def _on_dynamic_scroll(self, event=None):
        """Gère le scroll dynamique unifié"""
        return search_tab.main_playlist._on_dynamic_scroll(self, event)
    
    def _setup_progressive_scroll_detection(self):
        """Configure la détection de scroll progressif (redirige vers dynamic_scroll)"""
        return search_tab.main_playlist._setup_dynamic_scroll(self)
    
    def _on_progressive_scroll(self, event=None):
        """Gère le scroll progressif (redirige vers dynamic_scroll)"""
        return search_tab.main_playlist._on_dynamic_scroll(self, event)
    
    def _adjust_scroll_after_unload(self, unload_count, previous_scroll_position):
        """Ajuste la position du scroll après déchargement d'éléments"""
        return search_tab.main_playlist._adjust_scroll_after_unload(self, unload_count, previous_scroll_position)
    
    def _reorder_playlist_items(self):
        """Réorganise tous les éléments de la playlist dans l'ordre correct"""
        return search_tab.main_playlist._reorder_playlist_items(self)
    
    def _adjust_scroll_after_top_load(self, items_added):
        """Ajuste la position du scroll après chargement d'éléments au début"""
        return search_tab.main_playlist._adjust_scroll_after_top_load(self, items_added)
    
    def _simple_scroll_adjustment_after_top_load(self, items_added):
        """Ajustement simple du scroll après chargement vers le haut"""
        return search_tab.main_playlist._simple_scroll_adjustment_after_top_load(self, items_added)
    
    def _load_more_on_scroll(self):
        """Charge plus d'éléments quand on scroll vers le bas"""
        return search_tab.main_playlist._load_more_on_scroll(self)
    
    def _progressive_load_system(self):
        """NOUVEAU SYSTÈME : Chargement progressif (jamais de déchargement)"""
        return search_tab.main_playlist._progressive_load_system(self)
    
    def _old_smart_load_system(self):
        """Ancien système fenêtré 10+1+10 (conservé pour compatibilité)"""
        return search_tab.main_playlist._old_smart_load_system(self)
    
    def _get_last_loaded_index(self):
        """Trouve le dernier index chargé dans la playlist"""
        return search_tab.main_playlist._get_last_loaded_index(self)
    
    def _append_progressive_items(self, start_index, end_index):
        """Ajoute des éléments progressivement SANS supprimer les existants"""
        return search_tab.main_playlist._append_progressive_items(self, start_index, end_index)
    
    def _is_index_already_loaded(self, index):
        """Vérifie si un index spécifique est déjà chargé"""
        return search_tab.main_playlist._is_index_already_loaded(self, index)
    
    def _find_relative_index_in_loaded(self, absolute_index):
        """Trouve l'index relatif d'une chanson dans les éléments chargés"""
        return search_tab.main_playlist._find_relative_index_in_loaded(self, absolute_index)

    def _display_filtered_downloads(self, files_to_display, preserve_scroll=False):
        """Affiche une liste filtrée de fichiers téléchargés (optimisé)"""
        return library_tab.downloads._display_filtered_downloads(self, files_to_display, preserve_scroll)

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

    def _update_scrollbar(self):
        """Force la mise à jour de la scrollbar"""
        return library_tab.downloads._update_scrollbar(self)

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

    def _recreate_thumbnail_frame(self):
        """Recrée la thumbnail_frame si elle a été détruite"""
        return search_tab.results._recreate_thumbnail_frame(self)

    def _display_search_results(self, results, scroll_position=None):
        """Affiche les résultats de recherche sauvegardés après restauration"""
        return search_tab.results._display_search_results(self, results, scroll_position)

    def _restore_scroll_position(self, scroll_position):
        """Restaure la position de scroll de manière sécurisée"""
        return search_tab.results._restore_scroll_position(self, scroll_position)

    def _ensure_canvas_scrollbar_connection(self):
        """S'assure que la connexion entre le canvas et la scrollbar est correcte"""
        return search_tab.results._ensure_canvas_scrollbar_connection(self)

    def _update_canvas_scrollregion(self):
        """Force la mise à jour de la scrollregion du canvas"""
        return search_tab.results._update_canvas_scrollregion(self)

    def _display_batch_results_fast(self, batch_results):
        """Affiche rapidement un batch de résultats sans délai entre chaque"""
        return search_tab.results._display_batch_results_fast(self, batch_results)

    def _get_cached_thumbnail(self, video_id, thumbnail_url):
        """Récupère une miniature depuis le cache ou la charge si nécessaire"""
        return search_tab.results._get_cached_thumbnail(self, video_id, thumbnail_url)

    def _cache_thumbnail(self, video_id, thumbnail_image):
        """Met en cache une miniature chargée"""
        return search_tab.results._cache_thumbnail(self, video_id, thumbnail_image)



    # def _add_download_item(self, filepath):
    #     """Ajoute un élément téléchargé avec le même visuel que les résultats de recherche, visuel"""
    #     return library_tab.downloads._add_download_item(self, filepath)
    
    def _show_result_context_menu(self, item, event):
        """Affiche le menu contextuel pour un fichier avec support YouTube"""
        return ui_menus._show_result_context_menu(self, item, event)

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
                try:
                    children = self.thumbnail_frame.winfo_children()
                except tk.TclError:
                    # Erreur lors de l'accès aux enfants, ignorer
                    children = []

                for widget in children:
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

    def _create_new_playlist_dialog(self, filepath=None, is_youtube_video=False):
        """Dialogue pour créer une nouvelle playlist"""
        return tools._create_new_playlist_dialog(self, filepath, is_youtube_video)

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

    def _bind_mousewheel(self, widget, canvas, func=None):
        """Lie la molette de souris seulement quand le curseur est sur le widget"""
        widget.bind("<Enter>", lambda e: self._bind_scroll(canvas, func))
        widget.bind("<Leave>", lambda e: self._unbind_scroll(canvas))

    def _bind_scroll(self, canvas, func=None):
        """Active le défilement pour un canvas spécifique"""
        # Optimisation: Utiliser un délai pour éviter les problèmes de synchronisation
        if hasattr(self, '_scroll_binding_active') and self._scroll_binding_active:
            return
        self._scroll_binding_active = True
        
        if func is None:
            canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))
            canvas.bind_all("<Button-4>", lambda e: self._on_mousewheel(e, canvas))
            canvas.bind_all("<Button-5>", lambda e: self._on_mousewheel(e, canvas))
        else:
            canvas.bind_all("<MouseWheel>", lambda e: func(self, e))
            canvas.bind_all("<Button-4>", lambda e: func(self, e))
            canvas.bind_all("<Button-5>", lambda e: func(self, e))

    def _unbind_scroll(self, canvas):
        """Désactive le défilement pour un canvas spécifique"""
        self._scroll_binding_active = False
        
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

    def show_cache_menu(self):
        """Affiche un menu déroulant pour gérer les caches"""
        return ui_menus.show_cache_menu(self)
    
    def select_downloads_folder(self):
        """Permet de changer le dossier de téléchargements et déplacer les fichiers existants"""
        return ui_menus.select_downloads_folder(self)

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
    
    def _load_downloads_path(self):
        """Charge le chemin personnalisé du dossier de téléchargements"""
        try:
            config_file = os.path.join(os.getcwd(), "downloads_path.txt")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_path = f.read().strip()
                if custom_path and os.path.exists(custom_path):
                    return custom_path
        except Exception as e:
            print(f"Erreur lors du chargement du chemin personnalisé: {e}")
        
        # Retourner le chemin par défaut si aucun chemin personnalisé n'est trouvé
        default_path = os.path.join(os.getcwd(), "downloads")
        os.makedirs(default_path, exist_ok=True)
        return default_path

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

    def select_playlist_item(self, item_frame=None, index=None, auto_scroll=True, is_manual=False):
        """Met en surbrillance l'élément sélectionné dans la playlist

        Args:
            item_frame: Frame de l'élément à sélectionner
            index: Index de l'élément à sélectionner (alternatif à item_frame)
            auto_scroll: Si True, fait défiler automatiquement vers l'élément (défaut: True)
        """
        return search_tab.main_playlist.select_playlist_item(self, item_frame, index, auto_scroll, is_manual)

    def _set_item_colors(self, item_frame, bg_color, exclude_queue_indicator=False):
        """Change uniquement la couleur de fond des éléments d'un item de playlist"""
        return tools._set_item_colors(self, item_frame, bg_color, exclude_queue_indicator=exclude_queue_indicator)

    def _lighten_color(self, hex_color, factor=0.2):
        """Éclaircit une couleur hexadécimale d'un facteur donné"""
        return tools._lighten_color(self, hex_color, factor)
    
    def get_label_font_size(self, label):
        """Récupère la taille de police d'un label de manière sécurisée"""
        return tools.get_label_font_size(self, label)

    def get_label_font_family(self, label):
        """Récupère la famille de police d'un label de manière sécurisée"""
        return tools.get_label_font_family(self, label)

    def _smooth_scroll_to_position(self, target_position, duration=500, is_manual=False):
        """Anime le scroll vers une position cible avec une courbe ease-in-out"""
        return search_tab.main_playlist._smooth_scroll_to_position(self, target_position, duration=duration, is_manual=is_manual)

    def _check_and_unload_items(self, current_index):
        """Vérifie et décharge les éléments qui ne sont plus visibles"""
        return search_tab.main_playlist._check_and_unload_items(self, current_index)

    def _is_user_looking_above_current(self, current_index):
        """Vérifie si l'utilisateur regarde au-dessus de l'élément actuel"""
        return search_tab.main_playlist._is_user_looking_above_current(self, current_index)

    def _invalidate_loaded_indexes_cache(self):
        """Invalide le cache des index chargés"""
        return search_tab.main_playlist._invalidate_loaded_indexes_cache(self)

    def _start_text_animation(self, full_title, frame):
        """Démarre l'animation de défilement du titre si nécessaire"""
        return control._start_text_animation(self, full_title, frame)

    def _stop_text_animation(self, frame):
        """Arrête l'animation du titre"""
        return control._stop_text_animation(self, frame)

    def _reset_text_animation(self, frame):
        """Réinitialise l'animation de défilement du titre"""
        return control._reset_text_animation(self, frame)

    def _animate_title_step(self, frame):
        """Une étape de l'animation du titre"""
        return control._animate_title_step(self, frame)

    def _get_scrolled_title_text(self, full_text, scroll_pos, max_width_pixels, font_size=12, font_family='Helvetica'):
        """Génère le texte visible avec défilement à la position donnée"""
        return control._get_scrolled_title_text(self, full_text, scroll_pos, max_width_pixels, font_size=font_size, font_family=font_family)

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

    def _safe_add_to_queue_first_from_result(self, item):
        """Version sécurisée de _add_to_queue_first_from_result"""
        return tools._safe_add_to_queue_first_from_result(self, item)

    def _safe_add_to_queue(self, filepath):
        """Version sécurisée de _add_to_queue"""
        return tools._safe_add_to_queue(self, filepath)

    def _safe_add_to_queue_from_result(self, item):
        """Version sécurisée de _add_to_queue_first_from_result"""
        return tools._safe_add_to_queue_from_result(self, item)
    
    def _safe_add_to_main_playlist_from_result(self, video):
        """Version sécurisée de _add_to_main_playlist_from_result"""
        return tools._safe_add_to_main_playlist_from_result(self, video)

    def _safe_add_to_specific_playlist(self, filepath, playlist_name):
        """Version sécurisée de _add_to_specific_playlist"""
        return tools._safe_add_to_specific_playlist(self, filepath, playlist_name)

    def _add_to_playlist_from_result(self, video, playlist_name):
        """Version sécurisée de _add_to_playlist_from_result"""
        return tools._add_to_playlist_from_result(self, video, playlist_name)

    def _safe_create_new_playlist_dialog(self, filepath, is_youtube_video):
        """Version sécurisée de _create_new_playlist_dialog"""
        return tools._safe_create_new_playlist_dialog(self, filepath, is_youtube_video)

    def add_selection_to_main_playlist(self):
        """Ajoute tous les éléments sélectionnés à la fin de la main playlist dans l'ordre"""
        return tools.add_selection_to_main_playlist(self)

    def download_and_add_selection_to_main_playlist(self):
        """Télécharge les vidéos YouTube sélectionnées et les ajoute à la main playlist"""
        return tools.download_and_add_selection_to_main_playlist(self)

    def add_selection_to_queue_first(self):
        """Ajoute tous les éléments sélectionnés au début de la queue (lire ensuite)"""
        return tools.add_selection_to_queue_first(self)

    def add_selection_to_queue_last(self):
        """Ajoute tous les éléments sélectionnés à la fin de la queue (lire bientôt)"""
        return tools.add_selection_to_queue_last(self)

    def download_and_add_selection_to_queue_first(self):
        """Télécharge les vidéos YouTube sélectionnées et les ajoute au début de la queue (lire ensuite)"""
        return tools.download_and_add_selection_to_queue_first(self)

    def download_and_add_selection_to_queue_last(self):
        """Télécharge les vidéos YouTube sélectionnées et les ajoute à la fin de la queue (lire bientôt)"""
        return tools.download_and_add_selection_to_queue_last(self)

    def create_new_playlist_from_selection(self, has_youtube_videos):
        """Demande le nom d'une nouvelle playlist et y ajoute la sélection"""
        return tools.create_new_playlist_from_selection(self, has_youtube_videos)

    def update_selection_display(self):
        """Met à jour l'affichage du nombre d'éléments sélectionnés"""
        return tools.update_selection_display(self)

    def add_to_multiple_playlists(self, playlist_names):
        """Ajoute les éléments sélectionnés à plusieurs playlists"""
        return tools.add_to_multiple_playlists(self, playlist_names)

    def download_and_add_to_multiple_playlists(self, playlist_names):
        """Télécharge les vidéos YouTube sélectionnées et les ajoute à plusieurs playlists"""
        return tools.download_and_add_to_multiple_playlists(self, playlist_names)

    def _download_and_add_to_playlists(self, video_url, playlist_names):
        """Télécharge une vidéo et l'ajoute à plusieurs playlists"""
        return tools._download_and_add_to_playlists(self, video_url, playlist_names)

    def add_selection_to_playlist(self, playlist_name):
        """Ajoute tous les éléments sélectionnés à une playlist"""
        return tools.add_selection_to_playlist(self, playlist_name)

    def create_playlist_from_selection(self):
        """Crée une nouvelle playlist avec les éléments sélectionnés"""
        return library_tab.playlists.create_playlist_from_selection(self)

    # def download_and_add_selection_to_main_playlist(self):
    #     """Télécharge les vidéos YouTube sélectionnées et les ajoute à la main playlist"""
    #     return tools.download_and_add_selection_to_main_playlist(self)

    # def download_and_add_selection_to_playlist(self, playlist_name):
    #     """Télécharge les vidéos YouTube sélectionnées et les ajoute à une playlist"""
    #     youtube_urls = [item for item in self.selected_items if item.startswith("https://www.youtube.com/watch?v=")]
    #     local_files = [item for item in self.selected_items if not item.startswith("https://www.youtube.com/watch?v=")]

    #     if playlist_name not in self.playlists:
    #         return

    #     # Ajouter immédiatement les fichiers locaux
    #     added_count = 0
    #     for filepath in local_files:
    #         if filepath not in self.playlists[playlist_name]:
    #             self.playlists[playlist_name].append(filepath)
    #             added_count += 1

    #     if added_count > 0:
    #         self.save_playlists()
    #         self.status_bar.config(text=f"{added_count} fichier(s) ajouté(s) à '{playlist_name}'")

    #     # Télécharger les vidéos YouTube
    #     if youtube_urls:
    #         self.status_bar.config(text=f"Téléchargement de {len(youtube_urls)} vidéo(s) pour '{playlist_name}'...")
    #         threading.Thread(target=self._download_youtube_selection, args=(youtube_urls, playlist_name), daemon=True).start()

    #     # Effacer la sélection
    #     self.clear_selection()

    # def download_and_create_playlist_from_selection(self):
    #     """Télécharge les vidéos YouTube sélectionnées et crée une nouvelle playlist"""
    #     return tools.download_and_create_playlist_from_selection(self)

    def _download_youtube_selection(self, youtube_urls, target_playlist):
        """Télécharge une liste d'URLs YouTube et les ajoute à la playlist cible"""
        return tools._download_youtube_selection(self, youtube_urls, target_playlist)

    def _download_youtube_selection_to_queue(self, youtube_urls, queue_position):
        """Télécharge une sélection de vidéos YouTube et les ajoute à la queue"""
        return tools._download_youtube_selection_to_queue(self, youtube_urls, queue_position)

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

    def _remove_from_main_playlist(self, filepath, frame, event=None, song_index=None):
        """Supprime un élément de la main playlist"""
        return search_tab.main_playlist._remove_from_main_playlist(self, filepath, frame, event=event, song_index=song_index)

    def _delete_from_downloads(self, filepath, frame):
        """Supprime définitivement un fichier du dossier downloads"""
        return tools._delete_from_downloads(self, filepath, frame)

    def _load_image_thumbnail(self, image_path, label):
        """Charge une image normale comme thumbnail"""
        return tools._load_image_thumbnail(self, image_path, label)

    def _load_mp3_thumbnail(self, filepath, label):
        """Charge la cover art depuis un MP3 ou une thumbnail externe"""
        return tools._load_mp3_thumbnail(self, filepath, label)

    def _play_playlist_item(self, filepath):
        """Joue un élément de la playlist"""
        return tools._play_playlist_item(self, filepath)

    def play_track(self):
        return tools.play_track(self)

    def _on_mousewheel(self, event, canvas):
        """Gère le défilement avec la molette de souris"""
        # canvas.configure(state="disabled")
        return inputs._on_mousewheel(self, event, canvas)
    
    def _on_mousewheel_end(self, canvas):
        """Appelée à la fin du défilement pour mettre à jour l'affichage"""
        # canvas.configure(state="normal")
        # print("Fin du scroll détectée")
        return inputs._on_mousewheel_end(self, canvas)

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
        return search_tab.results.search_youtube(self)

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
        return search_tab.results._update_results_counter(self)

    def _create_circular_image(self, image, size=None):
        """Crée une image circulaire à partir d'une image rectangulaire"""
        if size is None:
            try:
                from search_tab.config import INTERFACE_CONFIG
                size = INTERFACE_CONFIG.get('circular_thumbnail_size', (45, 45))
            except ImportError:
                size = (45, 45)  # Valeur par défaut
        return tools._create_circular_image(self, image, size=size)

    def _safe_update_status(self, batch_number):
        """Version sécurisée de la mise à jour du statut"""
        return search_tab.results._safe_update_status(self, batch_number)

    def _safe_status_update(self, message):
        """Version sécurisée de la mise à jour du statut avec message personnalisé"""
        return search_tab.results._safe_status_update(self, message)

    def _add_search_result(self, video, index):
        """Ajoute un résultat avec un style rectangle uniforme"""
        return search_tab.results._add_search_result(self, video, index)
    
    def _display_search_results_from_cache(self, results):
        """Affiche les résultats de recherche depuis le cache avec optimisation"""
        return search_tab.results._display_search_results_from_cache(self, results)
    
    def _update_scroll_region(self):
        """Met à jour la région de scroll du canvas"""
        return search_tab.results._update_scroll_region(self)

    def _on_result_click(self, frame, add_to_playlist=True):
        """Gère le clic sur un résultat"""
        return search_tab.results._on_result_click(self, frame, add_to_playlist)

    def _on_result_right_click(self, event, frame):
        """Gère le clic droit sur un résultat pour afficher le menu des playlists"""
        return search_tab.results._on_result_right_click(self, event, frame)

    def _show_pending_playlist_menu(self, video, frame, url):
        """Affiche un menu pour ajouter une musique en cours de téléchargement à une playlist"""
        return tools._show_pending_playlist_menu(self, video, frame, url)

    def _add_to_pending_playlist(self, url, playlist_name, title):
        """Ajoute une playlist à la liste d'attente pour une URL en cours de téléchargement"""
        return tools._add_to_pending_playlist(self, url, playlist_name, title)

    def _create_new_playlist_for_pending(self, url, title):
        """Crée une nouvelle playlist et l'ajoute à la liste d'attente"""
        return tools._create_new_playlist_for_pending(self, url, title)

    def _show_youtube_playlist_menu(self, video, frame):
        """Affiche un menu déroulant pour choisir la playlist pour une vidéo YouTube"""
        return ui_menus._show_youtube_playlist_menu(self, video, frame)

    def _add_youtube_to_playlist(self, video, frame, playlist_name):
        """Ajoute une vidéo YouTube à une playlist (télécharge si nécessaire)"""
        return tools._add_youtube_to_playlist(self, video, frame, playlist_name)

    def _create_new_playlist_dialog_youtube(self, video, frame):
        """Dialogue pour créer une nouvelle playlist et y ajouter une vidéo YouTube"""
        return tools._create_new_playlist_dialog_youtube(self, video, frame)

    def _download_and_add_to_playlist_thread(self, video, frame, playlist_name):
        """Thread pour télécharger une vidéo et l'ajouter à une playlist"""
        return services.downloading._download_and_add_to_playlist_thread(self, video, frame, playlist_name)

    # def _add_downloaded_to_playlist(self, filepath, thumbnail_path, title, playlist_name, url=None):
    #     """Ajoute un fichier téléchargé à une playlist spécifique (à appeler dans le thread principal)"""
    #     return tools._add_downloaded_file_to_playlist(self, filepath, thumbnail_path, title, playlist_name, url)

    def _reset_frame_appearance(self, frame, bg_color, error=False):
        """Remet l'apparence d'un frame de manière sécurisée"""
        return tools._reset_frame_appearance(self, frame, bg_color, error)

    def _download_and_add_after_current(self, video, frame):
        """Télécharge une vidéo et l'ajoute après la chanson en cours"""
        return services.downloading._download_and_add_after_current(self, video, frame)

    def setup_controls(self):
        return setup.setup_controls(self)

    def _refresh_main_playlist_display(self, force_full_refresh=False):
        """Rafraîchit l'affichage de la main playlist"""
        return search_tab.main_playlist._refresh_main_playlist_display(self, force_full_refresh)

    def _set_download_success_appearance(self, frame):
        """Change l'apparence du frame pour indiquer un téléchargement réussi"""
        return tools._set_download_success_appearance(self, frame)

    def _set_download_error_appearance(self, frame):
        """Change l'apparence du frame pour indiquer une erreur de téléchargement"""
        return tools._set_download_error_appearance(self, frame)

    def _download_youtube_thumbnail(self, video_info, filepath):
        """Télécharge la thumbnail YouTube et l'associe au fichier audio"""
        return services.downloading._download_youtube_thumbnail(self, video_info, filepath)


    def download_selected_youtube(self, event=None, add_to_playlist=True):
        return services.downloading.download_selected_youtube(self, event, add_to_playlist)

    def _download_youtube_thread(self, url, add_to_playlist=True, callback=None):
        return tools._download_youtube_thread(self, url, add_to_playlist, callback)

    def _download_progress_hook(self, d):
        """Hook pour afficher la progression du téléchargement"""
        return tools._download_progress_hook(self, d)

    def _add_downloaded_file(self, filepath, thumbnail_path, title, url=None, add_to_playlist=True):
        """Ajoute le fichier téléchargé à la main playlist (à appeler dans le thread principal)"""
        return tools._add_downloaded_file(self, filepath, thumbnail_path, title, url, add_to_playlist)

    def _refresh_downloads_library(self, preserve_scroll=False):
        """Met à jour la liste des téléchargements dans l'onglet bibliothèque si il est actif"""
        return library_tab.downloads._refresh_downloads_library(self, preserve_scroll)

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
        return control.next_track(self)

    def prev_track_manual(self):
        """Passe à la chanson précédente (changement manuel par bouton)"""
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
            try:
                # print('OOOOOO')
                # Vérifier si l'application est fermée
                if hasattr(self, '_app_destroyed') and self._app_destroyed:
                    # print('BREAK1')
                    break
                
                
                
                # Vérifier si pygame mixer est initialisé
                if not pygame.mixer.get_init():
                    # print('BREAK2')
                    break
                # print('AAA', flush=True)
                
                # Ajuster la fréquence de mise à jour selon l'état de déplacement
                if hasattr(self, 'update_suspended') and self.update_suspended:
                    sleep_time = 0.5
                else:
                    sleep_time = 0.1

                # print('UWUWWW ', pygame.mixer.music.get_busy(), self.paused, self.user_dragging, self.current_time, self.song_length, flush=True)
                # print(f"Current time: {self.current_time}, Base position: {self.base_position}", flush=True)
                if pygame.mixer.music.get_busy() and not self.paused and not self.user_dragging:
                    pygame_pos = pygame.mixer.music.get_pos() / 1000

                    # pygame retourne -1 si la musique n'est pas encore prête
                    if pygame_pos >= 0:
                        self.current_time = self.base_position + pygame_pos
                    # Sinon garder current_time tel quel
                    
                    if round(self.current_time, 2) >= round(self.song_length, 2):
                        self.current_time = self.song_length
                        self.next_track()
                    # Filtrer les valeurs négatives
                    if self.current_time < 0:
                        self.current_time = 0
                    
                    # Suspendre les mises à jour visuelles pendant le déplacement de fenêtre
                    if not self.update_suspended:
                        try:
                            self.progress.config(value=self.current_time)
                            self.current_time_label.config(
                                text=time.strftime('%M:%S', time.gmtime(self.current_time))
                            )

                            if self.show_waveform_current:
                                self.draw_waveform_around(self.current_time)
                            else:
                                self.waveform_canvas.delete("all")
                        except (tk.TclError, AttributeError):
                            # Interface détruite, arrêter le thread
                            break
                        
                # Réduire les appels à update_idletasks pendant le déplacement
                if not self.update_suspended:
                    try:
                        self.root.update_idletasks()
                    except (tk.TclError, AttributeError):
                        # Interface détruite, arrêter le thread
                        break
                    
            except (pygame.error, AttributeError) as e:
                print(f"Erreur dans update_time, pygame.error, AttributeError: {e}")
                # Pygame fermé ou erreur, arrêter le thread
                break
            except Exception as e:
                # Autres erreurs, continuer mais afficher l'erreur
                print(f"Erreur dans update_time: {e}")
                
            time.sleep(sleep_time)


    def _show_artist_content(self, artist_name, video_data):
        """Affiche le contenu d'un artiste dans la zone de recherche YouTube - Version optimisée non-bloquante"""
        return self.artist_tab_manager.show_artist_content(artist_name, video_data)

    def _save_current_search_state(self):
        """Sauvegarde l'état actuel des résultats de recherche"""
        return search_tab.results._save_current_search_state(self)


    def _show_playlist_content(self, playlist_data, target_tab="sorties"):
        """Affiche le contenu d'une playlist dans une nouvelle interface"""
        return self.artist_tab_manager.show_playlist_content(playlist_data, target_tab)

    def _show_playlist_loading(self, playlist_title, target_tab="sorties"):
        """Affiche un message de chargement pour la playlist"""
        return self.artist_tab_manager.show_playlist_loading(playlist_title, target_tab)

    def _display_playlist_content(self, videos, playlist_title, target_tab="sorties"):
        """Affiche le contenu d'une playlist avec la même interface que l'onglet Musiques"""
        return self.artist_tab_manager.display_playlist_content(videos, playlist_title, target_tab)

    def _return_to_releases(self):
        """Retourne à l'affichage des releases dans l'onglet Sorties"""
        return self.artist_tab_manager.return_to_releases()

    def _return_to_playlists(self):
        """Retourne à l'affichage des playlists dans l'onglet Playlists"""
        return self.artist_tab_manager.return_to_playlists()

    def _show_playlist_error(self, error_msg):
        """Affiche une erreur lors du chargement d'une playlist"""
        return self.artist_tab_manager.show_playlist_error(error_msg)

    def _return_to_search(self):
        """Retourne instantanément à l'affichage de recherche normal"""
        return self.artist_tab_manager.return_to_search()

    # def init_downloads_watcher(self):
    #     """Initialise la surveillance du dossier downloads pour détecter les nouveaux fichiers"""
    #     self.downloads_watcher_active = True
    #     self.last_downloads_count = self.num_downloaded_files
        
    #     def downloads_watcher():
    #         """Thread qui surveille le dossier downloads"""
    #         while self.downloads_watcher_active:
    #             try:
    #                 # Vérifier si l'application est fermée
    #                 if hasattr(self, '_app_destroyed') and self._app_destroyed:
    #                     break
                    
    #                 # Compter les fichiers actuels
    #                 downloads_dir = "downloads"
    #                 if os.path.exists(downloads_dir):
    #                     audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
    #                     current_count = 0
    #                     for filename in os.listdir(downloads_dir):
    #                         if filename.lower().endswith(audio_extensions):
    #                             current_count += 1
                        
    #                     # Si le nombre a changé, recharger l'onglet téléchargées
    #                     if current_count != self.last_downloads_count:
    #                         old_count = self.last_downloads_count
    #                         self.last_downloads_count = current_count
    #                         self.num_downloaded_files = current_count
                            
    #                         # Mettre à jour l'interface dans le thread principal
    #                         self.safe_after(0, lambda: self._update_downloads_button())
                            
    #                         # Recharger l'onglet téléchargées si il est actuellement affiché
    #                         if hasattr(self, 'current_library_tab') and self.current_library_tab == "downloads":
    #                             self.safe_after(100, lambda: self._refresh_downloads_library(preserve_scroll=True))
                            
    #                         # Message différent selon si c'est un ajout ou une suppression
    #                         if current_count > old_count:
    #                             print(f"Nouveau fichier détecté dans downloads! Total: {current_count} (+{current_count - old_count})")
    #                         else:
    #                             print(f"Fichier supprimé du dossier downloads! Total: {current_count} ({current_count - old_count})")
                    
    #                 # Attendre avant la prochaine vérification
    #                 time.sleep(self.downloads_check_interval)
                    
    #             except Exception as e:
    #                 print(f"Erreur dans downloads_watcher: {e}")
    #                 time.sleep(self.downloads_check_interval)
        
    #     # Lancer le thread de surveillance
    #     self.downloads_watcher_thread = threading.Thread(target=downloads_watcher, daemon=True)
    #     self.downloads_watcher_thread.start()

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

    def toggle_recommendations(self):
        """Active/désactive le système de recommandations automatiques (ancienne méthode)"""
        if hasattr(self, 'recommendation_system'):
            if self.recommendation_system.enable_auto_recommendations:
                self.recommendation_system.disable_recommendations()
                self.recommendation_button.config(bg="#666666")  # Gris pour désactivé
                self.status_bar.config(text="Recommandations automatiques désactivées")
            else:
                self.recommendation_system.enable_recommendations()
                self.recommendation_button.config(bg="#3d3d3d")  # Couleur normale pour activé
                self.status_bar.config(text="Recommandations automatiques activées")
                # Lancer les recommandations pour la chanson en cours si elle existe
                # self.recommendation_system.manual_recommendations()

    def on_recommendation_left_click(self, event):
        """Gère le clic gauche sur le bouton de recommandations"""
        if self.recommendation_enabled:
            # Désactiver les recommandations
            self.recommendation_enabled = False
            self.recommendation_button.config(image=self.icons["recommendation"])
            if hasattr(self, 'recommendation_system'):
                self.recommendation_system.disable_recommendations()
            self._update_recommendation_button_icon()
            self.status_bar.config(text="Recommandations désactivées")
        else:
            # Activer les recommandations avec le dernier mode utilisé
            self.recommendation_enabled = True
            self.recommendation_mode = self.last_recommendation_mode
            self._update_recommendation_button_icon()
            if hasattr(self, 'recommendation_system'):
                self.recommendation_system.enable_recommendations()
                # self.recommendation_system.manual_recommendations()
            self.status_bar.config(text=f"Recommandations activées ({self.recommendation_mode})")

    def on_recommendation_right_click(self, event):
        """Gère le clic droit sur le bouton de recommandations - affiche le menu"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Activer les recommandations", state="disabled")
        menu.add_separator()
        
        # Variables pour les cases à cocher
        sparse_var = tk.BooleanVar()
        add_var = tk.BooleanVar()
        
        # Cocher la bonne option selon le mode actuel
        if self.recommendation_mode == "sparse":
            sparse_var.set(True)
        else:
            add_var.set(True)
        
        menu.add_checkbutton(
            label="éparses", 
            variable=sparse_var,
            command=lambda: self._set_recommendation_mode("sparse", sparse_var, add_var)
        )
        menu.add_checkbutton(
            label="à la suite", 
            variable=add_var,
            command=lambda: self._set_recommendation_mode("add", sparse_var, add_var)
        )
        
        # Afficher le menu à la position du clic
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _set_recommendation_mode(self, mode, sparse_var, add_var):
        """Définit le mode de recommandation et met à jour l'interface"""
        # S'assurer qu'une seule option est cochée
        if mode == "sparse":
            sparse_var.set(True)
            add_var.set(False)
        else:
            sparse_var.set(False)
            add_var.set(True)
        
        self.recommendation_mode = mode
        self.last_recommendation_mode = mode
        self.recommendation_enabled = True
        
        self._update_recommendation_button_icon()
        
        if hasattr(self, 'recommendation_system'):
            self.recommendation_system.enable_recommendations()
            # self.recommendation_system.manual_recommendations()
        
        self.status_bar.config(text=f"Recommandations activées ({mode})")

    def _update_recommendation_button_icon(self):
        """Met à jour l'icône du bouton de recommandations selon le mode"""
        if self.recommendation_enabled:
            if self.recommendation_mode == "sparse":
                self.recommendation_button.config(
                    image=self.icons["sparse_recommendation"],
                    bg="#4a8fe7"  # Couleur activée (bleu)
                )
            else:
                self.recommendation_button.config(
                    image=self.icons["add_recommendation"],
                    bg="#4a8fe7"  # Couleur activée (bleu)
                )
        else:
            self.recommendation_button.config(
                image=self.icons["recommendation"],
                bg="#3d3d3d"  # Couleur normale
            )

    def on_recommendation_hover_enter(self, event):
        """Gère l'entrée de la souris sur le bouton de recommandations"""
        if not self.recommendation_enabled:
            # Afficher un aperçu du dernier mode utilisé
            if self.last_recommendation_mode == "sparse":
                self.recommendation_button.config(image=self.icons["sparse_recommendation"])
            else:
                self.recommendation_button.config(image=self.icons["add_recommendation"])

    def on_recommendation_hover_leave(self, event):
        """Gère la sortie de la souris du bouton de recommandations"""
        if not self.recommendation_enabled:
            # Revenir à l'icône normale
            self.recommendation_button.config(image=self.icons["recommendation"])

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

    # Méthodes de gestion du cache
    def _clear_search_cache(self):
        """Vide le cache des recherches"""
        return _clear_search_cache(self)
    
    def _clear_artist_cache(self):
        """Vide le cache des artistes"""
        return _clear_artist_cache(self)
    
    def _clear_thumbnail_cache(self):
        """Vide le cache des miniatures"""
        return _clear_thumbnail_cache(self)
    
    def _clear_playlist_content_cache(self):
        """Vide le cache des contenus de playlists"""
        return _clear_playlist_content_cache(self)
    
    def _clear_duration_cache(self):
        """Vide le cache des durées"""
        return _clear_duration_cache(self)
    
    def _clear_all_caches(self):
        """Vide tous les caches"""
        return _clear_all_caches(self)

    def toggle_like_current_song(self):
        """Toggle le statut like de la chanson actuelle (mutuellement exclusif avec favorite)"""
        if not self.main_playlist or self.current_index >= len(self.main_playlist):
            return
        
        current_song = self.main_playlist[self.current_index]
        
        if current_song in self.liked_songs:
            # Retirer des likes
            self.liked_songs.remove(current_song)
            self.like_button.config(image=self.icons["like_empty"])
            # Retirer de la playlist Liked
            if current_song in self.playlists["Liked"]:
                self.playlists["Liked"].remove(current_song)
            self.status_bar.config(text="Retiré des titres aimés")
        else:
            # Si la chanson est dans les favoris, la retirer d'abord
            if current_song in self.favorite_songs:
                self.favorite_songs.remove(current_song)
                self.favorite_button.config(image=self.icons["favorite_empty"])
                # Retirer de la playlist Favorites
                if current_song in self.playlists["Favorites"]:
                    self.playlists["Favorites"].remove(current_song)
            
            # Ajouter aux likes
            self.liked_songs.add(current_song)
            self.like_button.config(image=self.icons["like_full"])
            # Ajouter à la playlist Liked
            if current_song not in self.playlists["Liked"]:
                self.playlists["Liked"].append(current_song)
            self.status_bar.config(text="Ajouté aux titres aimés")
        
        # Sauvegarder la configuration
        self.save_config()
        # Sauvegarder les playlists
        self.save_playlists()
        
        # Rafraîchir l'affichage des playlists si on est dans l'onglet bibliothèque
        if hasattr(self, 'current_library_tab') and self.current_library_tab == "playlists":
            self.switch_library_tab("playlists")

    def toggle_favorite_current_song(self):
        """Toggle le statut favorite de la chanson actuelle (mutuellement exclusif avec like)"""
        if not self.main_playlist or self.current_index >= len(self.main_playlist):
            return
        
        current_song = self.main_playlist[self.current_index]
        
        if current_song in self.favorite_songs:
            # Retirer des favoris
            self.favorite_songs.remove(current_song)
            self.favorite_button.config(image=self.icons["favorite_empty"])
            # Retirer de la playlist Favorites
            if current_song in self.playlists["Favorites"]:
                self.playlists["Favorites"].remove(current_song)
            self.status_bar.config(text="Retiré des favoris")
        else:
            # Si la chanson est dans les likes, la retirer d'abord
            if current_song in self.liked_songs:
                self.liked_songs.remove(current_song)
                self.like_button.config(image=self.icons["like_empty"])
                # Retirer de la playlist Liked
                if current_song in self.playlists["Liked"]:
                    self.playlists["Liked"].remove(current_song)
            
            # Ajouter aux favoris
            self.favorite_songs.add(current_song)
            self.favorite_button.config(image=self.icons["favorite_full"])
            # Ajouter à la playlist Favorites
            if current_song not in self.playlists["Favorites"]:
                self.playlists["Favorites"].append(current_song)
            self.status_bar.config(text="Ajouté aux favoris")
        
        # Sauvegarder la configuration
        self.save_config()
        # Sauvegarder les playlists
        self.save_playlists()
        
        # Rafraîchir l'affichage des playlists si on est dans l'onglet bibliothèque
        if hasattr(self, 'current_library_tab') and self.current_library_tab == "playlists":
            self.switch_library_tab("playlists")

    def update_like_favorite_buttons(self):
        """Met à jour l'état des boutons like et favorite selon la chanson actuelle"""
        if not self.main_playlist or self.current_index >= len(self.main_playlist):
            # Aucune chanson en cours, boutons vides
            if hasattr(self, 'like_button'):
                self.like_button.config(image=self.icons["like_empty"])
            if hasattr(self, 'favorite_button'):
                self.favorite_button.config(image=self.icons["favorite_empty"])
            return
        
        current_song = self.main_playlist[self.current_index]
        
        # Mettre à jour le bouton like
        if hasattr(self, 'like_button'):
            if current_song in self.liked_songs:
                self.like_button.config(image=self.icons["like_full"])
            else:
                self.like_button.config(image=self.icons["like_empty"])
        
        # Mettre à jour le bouton favorite
        if hasattr(self, 'favorite_button'):
            if current_song in self.favorite_songs:
                self.favorite_button.config(image=self.icons["favorite_full"])
            else:
                self.favorite_button.config(image=self.icons["favorite_empty"])

if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.on_closing)
    root.mainloop()
