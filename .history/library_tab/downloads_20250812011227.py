import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier library_tab
from library_tab import *



def show_downloads_content(self):
    """Affiche le contenu de l'onglet téléchargées"""
    
    # S'assurer que les données sont à jour avant l'affichage
    self._refresh_downloads_library()
    
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
    clear_btn.bind("<Button-1>", lambda event: self._clear_library_search())
    clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    # Frame pour les boutons de lecture
    buttons_frame = ttk.Frame(self.library_content_frame)
    buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    # Bouton pour jouer toutes les musiques dans l'ordre
    play_all_btn = tk.Button(
        buttons_frame,
        image=self.icons["play"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=8,
        pady=8,
        command=self.play_all_downloads_ordered,
        takefocus=0
    )
    play_all_btn.pack(side=tk.LEFT, padx=(0, 10))
    create_tooltip(play_all_btn, "Jouer toutes les musiques\nLit toutes les musiques téléchargées dans l'ordre")
    
    # Bouton pour jouer toutes les musiques en mode aléatoire
    shuffle_all_btn = tk.Button(
        buttons_frame,
        image=self.icons["shuffle"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=8,
        pady=8,
        command=self.play_all_downloads_shuffle,
        takefocus=0
    )
    shuffle_all_btn.pack(side=tk.LEFT)
    create_tooltip(shuffle_all_btn, "Jouer en mode aléatoire\nLit toutes les musiques téléchargées dans un ordre aléatoire")
    
    # Canvas avec scrollbar pour les téléchargements
    self.downloads_canvas = tk.Canvas(
        self.library_content_frame,
        bg='#3d3d3d',
        highlightthickness=0,
        takefocus=0
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
    
    # Configurer le scroll
    self.downloads_container.bind(
        "<Configure>",
        lambda e: self.downloads_canvas.configure(
            scrollregion=self.downloads_canvas.bbox("all")
        )
    )
    
    # Bind de la molette de souris
    self._bind_mousewheel(self.downloads_canvas, self.downloads_canvas)
    self._bind_mousewheel(self.downloads_container, self.downloads_canvas)
    
    # Initialiser la liste de tous les fichiers téléchargés
    self.all_downloaded_files = []
    
    # Charger et afficher les fichiers téléchargés
    self.load_downloaded_files()

def load_downloaded_files(self):
    """Charge et affiche tous les fichiers du dossier downloads"""
    downloads_dir = "downloads"
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
        return
    
    # Initialiser le système de cache
    self._init_cache_system()
    
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
    
    # Charger les caches de durées et miniatures
    self._load_duration_cache()
    self._load_thumbnail_cache()
    
    # Mettre à jour le nombre de fichiers téléchargés
    self.num_downloaded_files = len(self.all_downloaded_files)
    
    # Afficher tous les fichiers (sans filtre)
    self._display_filtered_downloads(self.all_downloaded_files)
    
    # Mettre à jour le texte du bouton
    self._update_downloads_button()

def _display_filtered_downloads(self, files_to_display):
    """Affiche une liste filtrée de fichiers téléchargés"""
    # Vider le container actuel
    for widget in self.downloads_container.winfo_children():
        widget.destroy()
    
    # Réinitialiser la référence au résultat unique
    self.search_result_frame = None
    
    # Réinitialiser les variables de progression
    if hasattr(self, 'loading_progress_label'):
        self.loading_progress_label.destroy()
        delattr(self, 'loading_progress_label')
    
    # Afficher avec chargement différé des miniatures
    for i, filepath in enumerate(files_to_display):
        frame = self._add_download_item_fast(filepath)
        
        # Si c'est le seul résultat, mémoriser le frame pour le positionnement intelligent
        if len(files_to_display) == 1:
            self.search_result_frame = frame
    
    # Lancer le chargement différé des miniatures et durées
    self._start_thumbnail_loading(files_to_display)



def _update_downloads_button(self):
    """Met à jour le texte du bouton téléchargées avec le nombre actuel"""
    if hasattr(self, 'downloads_btn'):
        self.downloads_btn.configure(text="Téléchargées " + f"({self.num_downloaded_files})")
        
def _display_files_batch(self, files_to_display, start_index, batch_size=20):
    """Affiche les fichiers par batch pour éviter de bloquer l'interface (ancienne version)"""
    end_index = min(start_index + batch_size, len(files_to_display))
    
    # Afficher le batch actuel
    for i in range(start_index, end_index):
        self._add_download_item(files_to_display[i])
    
    # Programmer le batch suivant si nécessaire
    if end_index < len(files_to_display):
        self.root.after(10, lambda: self._display_files_batch(files_to_display, end_index, batch_size))

def _display_files_batch_optimized(self, files_to_display, start_index, total_files, batch_size=50):
    """Version optimisée de l'affichage par batch"""
    end_index = min(start_index + batch_size, len(files_to_display))
    
    # Afficher le batch actuel avec chargement rapide
    for i in range(start_index, end_index):
        self._add_download_item_fast(files_to_display[i])
    
    # Mettre à jour l'indicateur de progression
    if hasattr(self, 'loading_progress_label'):
        progress = int((end_index / total_files) * 100)
        self.loading_progress_label.config(text=f"Chargement... {progress}% ({end_index}/{total_files})")
    
    # Programmer le batch suivant si nécessaire
    if end_index < len(files_to_display):
        # Délai réduit pour un chargement plus fluide
        self.root.after(5, lambda: self._display_files_batch_optimized(files_to_display, end_index, total_files, batch_size))
    else:
        # Chargement terminé, supprimer l'indicateur de progression
        if hasattr(self, 'loading_progress_label'):
            self.loading_progress_label.destroy()
            delattr(self, 'loading_progress_label')
        
        # Lancer le chargement différé des miniatures
        self._start_thumbnail_loading(files_to_display)

def _show_loading_progress(self, total_files):
    """Affiche un indicateur de progression pendant le chargement"""
    self.loading_progress_label = tk.Label(
        self.downloads_container,
        text=f"Chargement... 0% (0/{total_files})",
        bg='#3d3d3d',
        fg='#cccccc',
        font=('TkDefaultFont', 10),
        pady=20
    )
    self.loading_progress_label.pack(fill="x", padx=10, pady=10)

def _add_download_item(self, filepath):
    """Ajoute un élément téléchargé avec le même visuel que les résultats de recherche, visuel"""
    try:
        filename = os.path.basename(filepath)
        
        # Vérifier si c'est la chanson en cours de lecture
        is_current_song = (len(self.main_playlist) > 0 and 
                            self.current_index < len(self.main_playlist) and 
                            self.main_playlist[self.current_index] == filepath)
        
        # Frame principal - même style que les résultats YouTube
        bg_color = COLOR_SELECTED if is_current_song else COLOR_BACKGROUND
        item_frame = tk.Frame(
            self.downloads_container,
            bg=bg_color,  # Fond bleu si c'est la chanson en cours
            relief='flat',
            bd=1,
            highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
            highlightthickness=1
        )
        item_frame.pack(fill="x", padx=CARD_FRAME_PADX, pady=CARD_FRAME_PADY)

        # Stocker le chemin du fichier pour pouvoir le retrouver plus tard
        item_frame.filepath = filepath
        item_frame.selected = is_current_song
        
        # Vérifier si cette musique fait partie de la queue dans la main playlist
        is_in_queue = False
        if hasattr(self, 'queue_items') and hasattr(self, 'main_playlist'):
            # Chercher toutes les positions de ce fichier dans la main playlist
            for i, main_filepath in enumerate(self.main_playlist):
                if main_filepath == filepath and i in self.queue_items:
                    is_in_queue = True
                    break
        
        # Configuration de la grille en 5 colonnes : trait queue, miniature, texte, durée, bouton supprimer
        item_frame.columnconfigure(0, minsize=4, weight=0)   # Trait queue (si applicable)
        item_frame.columnconfigure(1, minsize=80, weight=0)  # Miniature
        item_frame.columnconfigure(2, weight=1)              # Texte
        item_frame.columnconfigure(3, minsize=60, weight=0)  # Durée
        item_frame.columnconfigure(4, minsize=40, weight=0)  # Bouton supprimer
        item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
        
        # 1. Trait vertical queue (colonne 0) - seulement si la musique est dans la queue
        if is_in_queue:
            queue_indicator = tk.Frame(
                item_frame,
                bg='black',  # Trait noir
                width=3
            )
            queue_indicator.grid(row=0, column=0, sticky='ns', padx=(2, 2), pady=2)
            queue_indicator.grid_propagate(False)
        
        # 2. Miniature (colonne 1)
        thumbnail_label = tk.Label(
            item_frame,
            bg=bg_color,  # Même fond que le frame parent
            width=10,
            height=3,
            anchor='center'
        )
        thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(5, 4), pady=5)
        # Forcer la taille fixe
        thumbnail_label.grid_propagate(False)
        
        # Charger la miniature (chercher un fichier image associé)
        self._load_download_thumbnail(filepath, thumbnail_label)
        
        # 3. Texte (colonne 2) - Frame contenant titre et métadonnées
        text_frame = tk.Frame(item_frame, bg=bg_color)
        text_frame.grid(row=0, column=2, sticky='nsew', padx=(0, 2), pady=4)
        text_frame.columnconfigure(0, weight=1)
        
        # Titre principal
        truncated_title = self._truncate_text_for_display(filename, max_width_pixels=310, font_family='TkDefaultFont', font_size=9)
        title_label = tk.Label(
            text_frame,
            text=truncated_title,
            bg=bg_color,
            fg='white',
            font=('TkDefaultFont', 9),
            anchor='nw',
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
                bg=bg_color,
                fg='#cccccc',
                font=('TkDefaultFont', 8),
                anchor='nw',
                justify='left'
            )
            metadata_label.grid(row=1, column=0, sticky='ew', pady=(0, 2))
        
        # 4. Durée (colonne 3)
        duration_label = tk.Label(
            item_frame,
            text=self._get_audio_duration(filepath),
            bg=bg_color,  # Même fond que le frame parent
            fg='#cccccc',
            font=('TkDefaultFont', 8),
            anchor='center'
        )
        duration_label.grid(row=0, column=3, sticky='ns', padx=(0, 2), pady=8)
        
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
            font=('TkDefaultFont', 8),
            takefocus=0
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
        create_tooltip(delete_btn, "Supprimer le fichier\nDouble-clic: Retirer de la playlist\nCtrl + Double-clic: Supprimer définitivement du disque")
        
        # Gestion des clics (simple et double)
        def on_item_click(event):
            # Vérifier si Ctrl est enfoncé pour ouvrir sur YouTube
            if event.state & 0x4:  # Ctrl est enfoncé
                self.open_music_on_youtube(filepath)
                return
            
            # Vérifier si Shift est enfoncé pour la sélection multiple
            if event.state & 0x1:  # Shift est enfoncé
                self.shift_selection_active = True
                self.toggle_item_selection(filepath, item_frame)
            else:
                # Clic normal sans Shift - ne pas effacer la sélection si elle existe
                pass
        
        def on_item_double_click(event):
            # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
            if event.state & 0x4:  # Ctrl est enfoncé
                self._delete_from_downloads(filepath, item_frame)
            elif event.state & 0x1 or self.selected_items:  # Shift est enfoncé ou mode sélection - ne rien faire
                pass
            else:
                # Comportement normal : ajouter et jouer
                self._add_download_to_playlist(filepath)
                # Jouer immédiatement
                if filepath in self.main_playlist:
                    self.current_index = self.main_playlist.index(filepath)
                    self.play_track()
        
        # Gestionnaire pour initialiser le drag sur clic gauche
        def on_left_button_press(event):
            # Initialiser le drag pour le clic gauche
            self.drag_drop_handler.setup_drag_start(event, item_frame)
            # Appeler aussi le gestionnaire de clic normal
            on_item_click(event)
        
        # Gestionnaire pour initialiser le drag sur clic droit
        def on_right_button_press(event):
            # Initialiser le drag pour le clic droit
            self.drag_drop_handler.setup_drag_start(event, item_frame)
        
        # Bindings pour les clics simples et doubles
        item_frame.bind("<ButtonPress-1>", on_left_button_press)
        item_frame.bind("<Double-1>", on_item_double_click)
        thumbnail_label.bind("<ButtonPress-1>", on_left_button_press)
        thumbnail_label.bind("<Double-1>", on_item_double_click)
        text_frame.bind("<ButtonPress-1>", on_left_button_press)
        text_frame.bind("<Double-1>", on_item_double_click)
        title_label.bind("<ButtonPress-1>", on_left_button_press)
        title_label.bind("<Double-1>", on_item_double_click)
        if metadata_text:  # Seulement si le label existe
            metadata_label.bind("<ButtonPress-1>", on_left_button_press)
            metadata_label.bind("<Double-1>", on_item_double_click)
        duration_label.bind("<ButtonPress-1>", on_left_button_press)
        duration_label.bind("<Double-1>", on_item_double_click)
        
        # Clic droit pour ouvrir le menu des playlists ou le menu de sélection
        def on_item_right_click(event):
            # Si on a des éléments sélectionnés, ouvrir le menu de sélection
            if self.selected_items:
                self.show_selection_menu(event)
            else:
                # Comportement normal : ouvrir le menu des playlists
                self._show_playlist_menu(filepath, None)
        
        # Gestionnaire combiné pour clic droit (drag + menu)
        def on_right_button_press_combined(event):
            # Initialiser le drag pour le clic droit
            on_right_button_press(event)
            # Appeler aussi le gestionnaire de clic droit normal
            on_item_right_click(event)
        
        item_frame.bind("<ButtonPress-3>", on_right_button_press_combined)
        thumbnail_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        text_frame.bind("<ButtonPress-3>", on_right_button_press_combined)
        title_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        if metadata_text:  # Seulement si le label existe
            metadata_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        duration_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        
        # Configuration du drag-and-drop
        self.drag_drop_handler.setup_drag_drop(
            item_frame, 
            file_path=filepath, 
            item_type="file"
        )
        
        # Tooltip pour expliquer les interactions
        tooltip_text = "Fichier téléchargé\nDouble-clic: Ajouter et jouer\nCtrl + Clic: Ouvrir sur YouTube\nDrag vers la droite: Ajouter à la queue (prochaines musiques)\nDrag vers la gauche: Placer en premier dans la queue\nShift + Clic: Sélection multiple\nClic droit: Ouvrir le menu des playlists"
        create_tooltip(title_label, tooltip_text)
        create_tooltip(thumbnail_label, tooltip_text)
        
    except Exception as e:
        print(f"Erreur affichage download item: {e}")

def _add_download_item_fast(self, filepath):
    """Version rapide de _add_download_item qui charge les miniatures en différé"""
    try:
        filename = os.path.basename(filepath)
        
        # Vérifier si c'est la chanson en cours de lecture
        is_current_song = (len(self.main_playlist) > 0 and 
                            self.current_index < len(self.main_playlist) and 
                            self.main_playlist[self.current_index] == filepath)
        
        # Frame principal - même style que les résultats YouTube
        bg_color = COLOR_SELECTED if is_current_song else COLOR_BACKGROUND
        item_frame = tk.Frame(
            self.downloads_container,
            bg=bg_color,
            relief='flat',
            bd=1,
            highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
            highlightthickness=1
        )
        item_frame.pack(fill="x", padx=CARD_FRAME_PADX, pady=CARD_FRAME_PADY)

        # Stocker le chemin du fichier
        item_frame.filepath = filepath
        item_frame.selected = is_current_song
        
        # Vérifier si cette musique fait partie de la queue
        is_in_queue = False
        if hasattr(self, 'queue_items') and hasattr(self, 'main_playlist'):
            for i, main_filepath in enumerate(self.main_playlist):
                if main_filepath == filepath and i in self.queue_items:
                    is_in_queue = True
                    break
        
        # Configuration de la grille
        item_frame.columnconfigure(0, minsize=4, weight=0)
        item_frame.columnconfigure(1, minsize=80, weight=0)
        item_frame.columnconfigure(2, weight=1)
        item_frame.columnconfigure(3, minsize=60, weight=0)
        item_frame.columnconfigure(4, minsize=40, weight=0)
        item_frame.rowconfigure(0, minsize=50, weight=0)
        
        # 1. Trait vertical queue
        if is_in_queue:
            queue_indicator = tk.Frame(item_frame, bg='black', width=3)
            queue_indicator.grid(row=0, column=0, sticky='ns', padx=(2, 2), pady=2)
            queue_indicator.grid_propagate(False)
        
        # 2. Miniature (placeholder d'abord)
        thumbnail_label = tk.Label(
            item_frame,
            bg=bg_color,
            width=10,
            height=3,
            anchor='center',
            text="⏵"  # Icône temporaire
        )
        thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(5, 4), pady=5)
        thumbnail_label.grid_propagate(False)
        
        # Stocker la référence pour le chargement différé
        thumbnail_label.filepath = filepath
        
        # 3. Texte - Frame contenant titre et métadonnées
        text_frame = tk.Frame(item_frame, bg=bg_color)
        text_frame.grid(row=0, column=2, sticky='nsew', padx=(0, 2), pady=4)
        text_frame.columnconfigure(0, weight=1)
        
        # Titre principal
        truncated_title = self._truncate_text_for_display(filename, max_width_pixels=310, font_family='TkDefaultFont', font_size=9)
        title_label = tk.Label(
            text_frame,
            text=truncated_title,
            bg=bg_color,
            fg='white',
            font=('TkDefaultFont', 9),
            anchor='nw',
            justify='left'
        )
        title_label.grid(row=0, column=0, sticky='ew', pady=(2, 0))
        
        # Métadonnées (artiste • album) - chargement différé
        metadata_label = tk.Label(
            text_frame,
            text="",  # Sera rempli lors du chargement différé
            bg=bg_color,
            fg='#cccccc',
            font=('TkDefaultFont', 8),
            anchor='nw',
            justify='left'
        )
        metadata_label.grid(row=1, column=0, sticky='ew', pady=(0, 2))
        
        # Stocker les références pour le chargement différé des métadonnées
        metadata_label.filepath = filepath
        
        # 4. Durée (placeholder d'abord)
        duration_label = tk.Label(
            item_frame,
            text="--:--",  # Placeholder
            bg=bg_color,
            fg='#cccccc',
            font=('TkDefaultFont', 8),
            anchor='center'
        )
        duration_label.grid(row=0, column=3, sticky='ns', padx=(0, 2), pady=8)
        
        # Stocker la référence pour le chargement différé
        duration_label.filepath = filepath
        
        # 5. Bouton de suppression
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
            font=('TkDefaultFont', 8),
            takefocus=0
        )
        delete_btn.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
        
        # Gestion des événements (version simplifiée pour la rapidité)
        def on_item_click(event):
            # Vérifier si Ctrl est enfoncé pour ouvrir sur YouTube
            if event.state & 0x4:  # Ctrl est enfoncé
                self.open_music_on_youtube(filepath)
                return
            
            # Vérifier si Shift est enfoncé pour la sélection multiple
            if event.state & 0x1:  # Shift est enfoncé
                self.shift_selection_active = True
                self.toggle_item_selection(filepath, item_frame)
            else:
                # Clic normal sans Shift - ne pas effacer la sélection si elle existe
                pass
        
        def on_item_double_click(event):
            if event.state & 0x4:
                self._delete_from_downloads(filepath, item_frame)
            elif not (event.state & 0x1 or self.selected_items):
                self._add_download_to_playlist(filepath)
                if filepath in self.main_playlist:
                    self.current_index = self.main_playlist.index(filepath)
                    self.play_track()
        
        def on_delete_double_click(event):
            if event.state & 0x4:
                self._delete_from_downloads(filepath, item_frame)
            else:
                if filepath in self.main_playlist:
                    index = self.main_playlist.index(filepath)
                    self.main_playlist.remove(filepath)
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
                    self._refresh_playlist_display()
                    self.status_bar.config(text=f"Retiré de la playlist: {os.path.basename(filepath)}")
        
        # Gestionnaire pour initialiser le drag sur clic gauche
        def on_left_button_press(event):
            # Initialiser le drag pour le clic gauche
            self.drag_drop_handler.setup_drag_start(event, item_frame)
            # Appeler aussi le gestionnaire de clic normal
            on_item_click(event)
        
        # Gestionnaire pour initialiser le drag sur clic droit
        def on_right_button_press(event):
            # Initialiser le drag pour le clic droit
            self.drag_drop_handler.setup_drag_start(event, item_frame)
        
        # Clic droit pour ouvrir le menu des playlists ou le menu de sélection
        def on_item_right_click(event):
            # Si on a des éléments sélectionnés, ouvrir le menu de sélection
            if self.selected_items:
                self.show_selection_menu(event)
            else:
                # Comportement normal : ouvrir le menu des playlists
                self._show_playlist_menu(filepath, None)
        
        # Gestionnaire combiné pour clic droit (drag + menu)
        def on_right_button_press_combined(event):
            # Initialiser le drag pour le clic droit
            on_right_button_press(event)
            # Appeler aussi le gestionnaire de clic droit normal
            on_item_right_click(event)
        
        # Bindings essentiels
        item_frame.bind("<ButtonPress-1>", on_left_button_press)
        item_frame.bind("<Double-1>", on_item_double_click)
        item_frame.bind("<ButtonPress-3>", on_right_button_press_combined)
        title_label.bind("<ButtonPress-1>", on_left_button_press)
        title_label.bind("<Double-1>", on_item_double_click)
        title_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        thumbnail_label.bind("<ButtonPress-1>", on_left_button_press)
        thumbnail_label.bind("<Double-1>", on_item_double_click)
        thumbnail_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        duration_label.bind("<ButtonPress-1>", on_left_button_press)
        duration_label.bind("<Double-1>", on_item_double_click)
        duration_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        delete_btn.bind("<Double-1>", on_delete_double_click)
        
        # Drag and drop
        self.drag_drop_handler.setup_drag_drop(item_frame, file_path=filepath, item_type="file")
        
        # Retourner le frame pour le positionnement intelligent
        return item_frame
        
    except Exception as e:
        print(f"Erreur affichage download item rapide: {e}")
        return None

def _start_thumbnail_loading(self, files_to_display):
    """Lance le chargement différé des miniatures et durées"""
    if not hasattr(self, 'thumbnail_loading_queue'):
        self.thumbnail_loading_queue = []
    
    # Ajouter tous les fichiers à la queue de chargement
    self.thumbnail_loading_queue = files_to_display.copy()
    
    # Commencer le chargement
    self._load_next_thumbnail()

def _load_next_thumbnail(self):
    """Charge la prochaine miniature dans la queue (version avec cache)"""
    if not hasattr(self, 'thumbnail_loading_queue') or not self.thumbnail_loading_queue:
        return
    
    # Prendre le prochain fichier
    filepath = self.thumbnail_loading_queue.pop(0)
    
    # Trouver les widgets correspondants
    for widget in self.downloads_container.winfo_children():
        if hasattr(widget, 'filepath') and widget.filepath == filepath:
            # Fonction récursive pour trouver tous les labels avec filepath
            def find_labels_with_filepath(parent_widget, target_filepath):
                labels = []
                for child in parent_widget.winfo_children():
                    if isinstance(child, tk.Label) and hasattr(child, 'filepath') and child.filepath == target_filepath:
                        labels.append(child)
                    elif hasattr(child, 'winfo_children'):  # Parcourir récursivement les frames
                        labels.extend(find_labels_with_filepath(child, target_filepath))
                return labels
            
            # Trouver tous les labels avec ce filepath
            all_labels = find_labels_with_filepath(widget, filepath)
            
            for label in all_labels:
                if label.cget('text') == "⏵":  # C'est le label de miniature
                    self._load_cached_thumbnail(filepath, label)
                elif label.cget('text') == "--:--":  # C'est le label de durée
                    duration = self._get_cached_duration(filepath)
                    label.config(text=duration)
                elif label.cget('text') == "":  # C'est le label de métadonnées
                    # Charger les métadonnées
                    artist, album = self._get_audio_metadata(filepath)
                    metadata_text = self._format_artist_album_info(artist, album, filepath)
                    if metadata_text:
                        label.config(text=metadata_text)
            break
    
    # Programmer le chargement suivant
    if self.thumbnail_loading_queue:
        self.root.after(5, self._load_next_thumbnail)  # Délai réduit avec le cache

def _refresh_downloads_library(self):
    """Met à jour la liste des téléchargements et le compteur"""
    try:
        # Toujours mettre à jour la liste des fichiers et le compteur, peu importe l'onglet
        downloads_dir = "downloads"
        if os.path.exists(downloads_dir):
            # Extensions audio supportées
            audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
            
            # Sauvegarder l'ancien état pour comparaison si la liste existe
            old_files = set(self.all_downloaded_files) if hasattr(self, 'all_downloaded_files') else set()
            
            # Recharger la liste
            if not hasattr(self, 'all_downloaded_files'):
                self.all_downloaded_files = []
            else:
                self.all_downloaded_files.clear()
            
            if not hasattr(self, 'normalized_filenames'):
                self.normalized_filenames = {}
            else:
                self.normalized_filenames.clear()
            
            # Vider aussi le cache de recherche étendu
            if not hasattr(self, 'extended_search_cache'):
                self.extended_search_cache = {}
            else:
                self.extended_search_cache.clear()
            
            for filename in os.listdir(downloads_dir):
                if filename.lower().endswith(audio_extensions):
                    filepath = os.path.join(downloads_dir, filename)
                    self.all_downloaded_files.append(filepath)
                    # Mettre à jour le cache
                    normalized_name = os.path.basename(filepath).lower()
                    self.normalized_filenames[filepath] = normalized_name
            
            # Mettre à jour le compteur de fichiers téléchargés
            self.num_downloaded_files = len(self.all_downloaded_files)
            
            # Mettre à jour le texte du bouton (toujours)
            self._update_downloads_button()
            
            # Vérifier s'il y a de nouveaux fichiers et si on est dans l'onglet concerné
            new_files = set(self.all_downloaded_files)
            if new_files != old_files:
                # Vérifier si on est dans l'onglet bibliothèque et sous-onglet téléchargées
                current_tab = self.notebook.tab(self.notebook.select(), "text")
                if (current_tab == "Bibliothèque" and 
                    hasattr(self, 'current_library_tab') and 
                    self.current_library_tab == "téléchargées" and
                    hasattr(self, 'downloads_container')):
                    # Mettre à jour l'affichage seulement si on est dans l'onglet
                    if hasattr(self, 'library_search_entry') and self.library_search_entry.get().strip():
                        # Relancer la recherche avec le terme actuel
                        self._perform_library_search()
                    else:
                        # Afficher tous les fichiers
                        self._display_filtered_downloads(self.all_downloaded_files)
                        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la bibliothèque: {e}")

# ==================== SYSTÈME DE CACHE ====================

def _init_cache_system(self):
    """Initialise le système de cache pour les miniatures et durées"""
    import json
    
    self.cache_dir = os.path.join("downloads", ".cache")
    self.thumbnails_cache_dir = os.path.join(self.cache_dir, "thumbnails")
    self.durations_cache_file = os.path.join(self.cache_dir, "durations.json")
    self.metadata_cache_file = os.path.join(self.cache_dir, "metadata.json")
    
    # Créer les dossiers de cache s'ils n'existent pas
    os.makedirs(self.thumbnails_cache_dir, exist_ok=True)
    
    # Initialiser les caches en mémoire
    self.duration_cache = {}
    self.thumbnail_cache = {}
    self.cache_metadata = {}

def _load_duration_cache(self):
    """Charge le cache des durées depuis le disque"""
    import json
    
    try:
        if os.path.exists(self.durations_cache_file):
            with open(self.durations_cache_file, 'r', encoding='utf-8') as f:
                self.duration_cache = json.load(f)
        else:
            self.duration_cache = {}
    except Exception as e:
        print(f"Erreur chargement cache durées: {e}")
        self.duration_cache = {}

def _save_duration_cache(self):
    """Sauvegarde le cache des durées sur le disque"""
    import json
    
    try:
        with open(self.durations_cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.duration_cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur sauvegarde cache durées: {e}")

def _load_thumbnail_cache(self):
    """Charge les métadonnées du cache des miniatures"""
    import json
    
    try:
        if os.path.exists(self.metadata_cache_file):
            with open(self.metadata_cache_file, 'r', encoding='utf-8') as f:
                self.cache_metadata = json.load(f)
        else:
            self.cache_metadata = {}
    except Exception as e:
        print(f"Erreur chargement métadonnées cache: {e}")
        self.cache_metadata = {}

def _save_thumbnail_cache_metadata(self):
    """Sauvegarde les métadonnées du cache des miniatures"""
    import json
    
    try:
        with open(self.metadata_cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache_metadata, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur sauvegarde métadonnées cache: {e}")

def _get_cached_duration(self, filepath):
    """Récupère la durée depuis le cache ou la calcule si nécessaire"""
    try:
        # Vérifier si la durée est en cache et si le fichier n'a pas été modifié
        file_mtime = os.path.getmtime(filepath)
        cache_key = os.path.abspath(filepath)
        
        if (cache_key in self.duration_cache and 
            'mtime' in self.duration_cache[cache_key] and
            self.duration_cache[cache_key]['mtime'] == file_mtime):
            return self.duration_cache[cache_key]['duration']
        
        # Calculer la durée
        duration = self._calculate_audio_duration(filepath)
        
        # Mettre en cache
        self.duration_cache[cache_key] = {
            'duration': duration,
            'mtime': file_mtime
        }
        
        # Sauvegarder le cache (de manière asynchrone pour ne pas bloquer)
        self.root.after_idle(self._save_duration_cache)
        
        return duration
        
    except Exception as e:
        print(f"Erreur cache durée pour {filepath}: {e}")
        return "??:??"

def _calculate_audio_duration(self, filepath):
    """Calcule la durée réelle d'un fichier audio"""
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

def _get_cached_thumbnail_path(self, filepath):
    """Retourne le chemin de la miniature en cache"""
    filename = os.path.basename(filepath)
    cache_filename = f"{filename}.thumb.png"
    return os.path.join(self.thumbnails_cache_dir, cache_filename)

def _is_thumbnail_cache_valid(self, filepath, cache_path):
    """Vérifie si la miniature en cache est encore valide"""
    try:
        if not os.path.exists(cache_path):
            return False
        
        # Vérifier la date de modification du fichier source
        source_mtime = os.path.getmtime(filepath)
        cache_mtime = os.path.getmtime(cache_path)
        
        # Vérifier aussi les fichiers d'image associés (thumbnails YouTube)
        base_path = os.path.splitext(filepath)[0]
        for ext in ['.jpg', '.png', '.webp']:
            img_path = base_path + ext
            if os.path.exists(img_path):
                img_mtime = os.path.getmtime(img_path)
                if img_mtime > cache_mtime:
                    return False
        
        return cache_mtime >= source_mtime
        
    except Exception as e:
        print(f"Erreur vérification cache miniature: {e}")
        return False

def _create_cached_thumbnail(self, filepath, cache_path):
    """Crée et sauvegarde une miniature en cache"""
    try:
        # Chercher une image associée d'abord
        base_path = os.path.splitext(filepath)[0]
        source_image = None
        
        for ext in ['.jpg', '.png', '.webp']:
            img_path = base_path + ext
            if os.path.exists(img_path):
                source_image = img_path
                break
        
        if source_image:
            # Charger et redimensionner l'image
            img = Image.open(source_image)
            img.thumbnail((80, 45), Image.Resampling.LANCZOS)
            
            # Sauvegarder en cache
            img.save(cache_path, "PNG")
            return True
        else:
            # Créer une miniature par défaut
            default_img = Image.new('RGB', (80, 45), color='#3d3d3d')
            default_img.save(cache_path, "PNG")
            return True
            
    except Exception as e:
        print(f"Erreur création miniature cache: {e}")
        return False

def _load_cached_thumbnail(self, filepath, label):
    """Charge une miniature depuis le cache ou la crée si nécessaire"""
    try:
        cache_path = self._get_cached_thumbnail_path(filepath)
        
        # Vérifier si le cache est valide
        if not self._is_thumbnail_cache_valid(filepath, cache_path):
            # Créer la miniature en cache
            if not self._create_cached_thumbnail(filepath, cache_path):
                # Fallback à l'ancienne méthode
                self._load_download_thumbnail_fallback(filepath, label)
                return
        
        # Charger depuis le cache
        img = Image.open(cache_path)
        photo = ImageTk.PhotoImage(img)
        label.configure(image=photo)
        label.image = photo
        
    except Exception as e:
        print(f"Erreur chargement miniature cache: {e}")
        # Fallback à l'ancienne méthode
        self._load_download_thumbnail_fallback(filepath, label)

def _load_download_thumbnail_fallback(self, filepath, label):
    """Méthode de fallback pour charger les miniatures (ancienne méthode)"""
    try:
        # Chercher une image associée
        base_path = os.path.splitext(filepath)[0]
        for ext in ['.jpg', '.png', '.webp']:
            thumbnail_path = base_path + ext
            if os.path.exists(thumbnail_path):
                img = Image.open(thumbnail_path)
                img.thumbnail((80, 45), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label.configure(image=photo)
                label.image = photo
                return
        
        # Fallback à une icône par défaut
        default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
        photo = ImageTk.PhotoImage(default_icon)
        label.configure(image=photo)
        label.image = photo
        
    except Exception as e:
        print(f"Erreur fallback miniature: {e}")
        # Icône par défaut en cas d'erreur
        default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
        photo = ImageTk.PhotoImage(default_icon)
        label.configure(image=photo)
        label.image = photo

