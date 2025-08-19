import sys
import os
import time
import threading

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier search_tab
from search_tab import *

# Importer la configuration des optimisations
try:
    from playlist_config import should_use_windowing, get_window_size, get_preload_size, get_config
except ImportError:
    # Fallback si le fichier de config n'existe pas
    def should_use_windowing(size): return size > 50
    def get_window_size(size): return min(30, size)
    def get_preload_size(size): return min(20, size // 5) if size > 50 else 0
    def get_config(key, default=None): return default

# Importer la nouvelle configuration centralisée
try:
    from search_tab.config import (
        get_main_playlist_config, should_use_windowing as config_should_use_windowing,
        get_optimal_window_size, get_optimal_preload_size
    )
    USE_NEW_CONFIG = True
except ImportError:
    USE_NEW_CONFIG = False

def _add_main_playlist_item(self, filepath, thumbnail_path=None, song_index=None):
        """Ajoute un élément à la main playlist avec un style rectangle uniforme"""
        try:
            # Vérifier que le playlist_container existe et est accessible
            if not (hasattr(self, 'playlist_container') and self.playlist_container.winfo_exists()):
                # Si le container n'est pas accessible, ne pas essayer d'ajouter l'élément visuel
                # Cela peut arriver quand on ajoute depuis un autre onglet
                return
                
            filename = os.path.basename(filepath)
            
            # 1. Frame principal - grand rectangle uniforme
            item_frame = tk.Frame(
                self.playlist_container,
                bg='#4a4a4a',  # Fond gris uniforme
                relief='flat',
                bd=0,
                highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
                highlightthickness=1,
            )
            item_frame.pack(fill='x', pady=2, padx=5)
            item_frame.selected = False
            
            # Déterminer si on affiche les numéros (seulement si provient d'une playlist)
            show_numbers = self.main_playlist_from_playlist
            # Utiliser l'index fourni ou calculer l'index actuel
            if song_index is not None:
                current_song_index = song_index
            else:
                current_song_index = len(self.main_playlist) - 1  # Index de la chanson actuelle (dernière ajoutée)
            
            # Vérifier si cette position spécifique fait partie de la queue
            is_in_queue = (hasattr(self, 'queue_items') and current_song_index in self.queue_items)
            item_frame.is_in_queue = is_in_queue
            
            number_label = None
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
                        width=QUEUE_LINE_WIDTH
                    )
                    queue_indicator.grid(row=0, column=0, sticky='ns', padx=QUEUE_LINE_PADX, pady=QUEUE_LINE_PADY)
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
                        width=QUEUE_LINE_WIDTH
                    )
                    queue_indicator.grid(row=0, column=0, sticky='ns', padx=QUEUE_LINE_PADX, pady=QUEUE_LINE_PADY)
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
            truncated_title = self._truncate_text_for_display(filename, max_width_pixels=MAIN_PLAYLIST_TITLE_MAX_WIDTH, font_family='TkDefaultFont', font_size=9)
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
            title_label.animation_id = None  # ID de l'animation pour le titre
            title_label.scroll_position = 0  # Position de défilement actuelle
            title_label.pause_counter = MAIN_PLAYLIST_TITLE_ANIMATION_STARTUP  # Compteur pour la pause entre les cycles
            title_label.max_width = MAIN_PLAYLIST_TITLE_MAX_WIDTH  # Largeur maximale du titre
            title_label.animation_active = False  # Animation en cours
            title_label.full_text = title_label.cget('text')  # Texte complet du titre
            title_label.pause_cycles = MAIN_PLAYLIST_TITLE_ANIMATION_PAUSE
            
            # Métadonnées (artiste • album • date)
            artist, album = self._get_audio_metadata(filepath)
            
            # Créer un frame pour les métadonnées pour pouvoir séparer l'artiste
            metadata_container = tk.Frame(text_frame, bg='#4a4a4a')
            metadata_container.grid(row=1, column=0, sticky='ew', pady=(0, 2))
            metadata_container.columnconfigure(0, weight=0)  # Artiste
            metadata_container.columnconfigure(1, weight=1)  # Reste des métadonnées
            
            # Label artiste cliquable (s'il existe)
            if artist:
                truncated_artist = self._truncate_text_for_display(artist, max_width_pixels=MAIN_PLAYLIST_ARTIST_MAX_WIDTH, font_family='TkDefaultFont', font_size=8)
                artist_label = tk.Label(
                    metadata_container,
                    text=truncated_artist,
                    bg='#4a4a4a',
                    fg='#cccccc',
                    font=('TkDefaultFont', 8),
                    anchor='w',
                    cursor='hand2'  # Curseur main pour indiquer que c'est cliquable
                )
                artist_label.grid(row=0, column=0, sticky='w')
                artist_label.animation_id = None  # ID de l'animation pour le titre
                artist_label.scroll_position = 0  # Position de défilement actuelle
                artist_label.pause_counter = MAIN_PLAYLIST_ARTIST_ANIMATION_STARTUP  # Compteur pour la pause entre les cycles
                artist_label.max_width = MAIN_PLAYLIST_ARTIST_MAX_WIDTH  # Largeur maximale du titre
                artist_label.animation_active = False  # Animation en cours
                artist_label.full_text = artist_label.cget('text')  # Texte complet de l'artiste
                artist_label.pause_cycles = MAIN_PLAYLIST_ARTIST_ANIMATION_PAUSE
                
                # Fonction pour gérer le clic sur l'artiste
                def on_artist_click(event, artist_name=artist, file_path=filepath):
                    # Essayer d'obtenir les métadonnées YouTube pour récupérer l'URL de la chaîne
                    video_data = {}
                    try:
                        youtube_metadata = self.get_youtube_metadata(file_path)
                        if youtube_metadata:
                            # Essayer d'obtenir l'URL de la chaîne depuis les métadonnées
                            channel_url = (youtube_metadata.get('channel_url') or 
                                         youtube_metadata.get('uploader_url') or 
                                         youtube_metadata.get('channel'))
                            if channel_url:
                                video_data['channel_url'] = channel_url
                    except Exception:
                        pass
                    
                    # Si pas d'URL trouvée, utiliser le fallback
                    if 'channel_url' not in video_data:
                        import urllib.parse
                        # Nettoyer le nom de l'artiste pour l'URL
                        clean_artist = artist_name.replace(' ', '').replace('　', '').replace('/', '')
                        encoded_artist = urllib.parse.quote(clean_artist, safe='')
                        video_data['channel_url'] = f"https://www.youtube.com/@{encoded_artist}"
                    
                    self._show_artist_content(artist_name, video_data)
                
                # Bind du clic sur l'artiste
                artist_label.bind("<Button-1>", on_artist_click)
                
                # Créer le reste des métadonnées (album • date)
                other_metadata_label = None
                # other_parts = []
                # if album:
                #     other_parts.append(album)
                
                # # Ajouter la date si le filepath est fourni
                # if filepath and os.path.exists(filepath):
                #     date_str = None
                #     try:
                #         # Essayer d'obtenir la date de publication YouTube
                #         youtube_metadata = self.get_youtube_metadata(filepath)
                #         if youtube_metadata and youtube_metadata.get('upload_date'):
                #             upload_date = youtube_metadata['upload_date']
                #             # Convertir la date YouTube (format: YYYYMMDD) en format lisible
                #             import datetime
                #             date_obj = datetime.datetime.strptime(upload_date, "%Y%m%d")
                #             date_str = date_obj.strftime("%d/%m/%y")
                #     except Exception:
                #         pass
                    
                #     # Ajouter la date si elle existe
                #     if date_str:
                #         other_parts.append(date_str)
                
                # # Afficher le reste des métadonnées s'il y en a
                # if other_parts:
                #     separator_and_rest = " • " + " • ".join(other_parts)
                #     other_metadata_label = tk.Label(
                #         metadata_container,
                #         text=separator_and_rest,
                #         bg='#4a4a4a',
                #         fg='#cccccc',
                #         font=('TkDefaultFont', 8),
                #         anchor='w'
                #     )
                #     other_metadata_label.grid(row=0, column=1, sticky='w')
                    
                #     # Stocker la référence pour les bindings
                #     other_metadata_label.filepath = filepath
                # else:
                #     other_metadata_label = None
            # else:
            #     # Pas d'artiste, afficher les métadonnées normalement
            #     metadata_text = self._format_artist_album_info(artist, album, filepath)
            #     if metadata_text:
            #         metadata_label = tk.Label(
            #             metadata_container,
            #             text=metadata_text,
            #             bg='#4a4a4a',
            #             fg='#cccccc',
            #             font=('TkDefaultFont', 8),
            #             anchor='w',
            #             justify='left'
            #         )
            #         metadata_label.grid(row=0, column=0, sticky='ew')
            #         artist_label = None
            #         other_metadata_label = None
            #     else:
            #         artist_label = None
            #         other_metadata_label = None
            
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
            delete_btn.bind("<Double-1>", lambda event, f=filepath, frame=item_frame, idx=current_song_index: self._remove_from_main_playlist(f, frame, event, idx))
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
            
            # Gestionnaire pour initialiser le drag sur clic gauche
            def on_left_button_press(event):
                # Initialiser le drag pour le clic gauche
                self.drag_drop_handler.setup_drag_start(event, item_frame)
                # Appeler aussi le gestionnaire de clic normal
                on_playlist_item_click(event)
            
            
            
            def on_enter(event):
                """Rend l'item plus clair au survol"""
                 
                # if not item_frame.selected:  # Ne pas changer la couleur si l'item est sélectionné
                if item_frame.is_dragging:
                    return  # Ne pas changer la couleur si on est en train de drag
                
                bg_color = COLOR_SELECTED if item_frame.selected else COLOR_BACKGROUND
                # Calculer une couleur plus claire
                hover_color = self._lighten_color(bg_color, HOVER_LIGHT_PERCENTAGE)
                if item_frame.is_in_queue:
                    self._set_item_colors(item_frame, hover_color, exclude_queue_indicator=True)
                else:
                    self._set_item_colors(item_frame, hover_color, exclude_queue_indicator=False)
                if artist:
                    self._start_text_animation(artist_label.full_text, artist_label)
                self._start_text_animation(title_label.full_text, title_label)
                
                

            def on_leave(event):
                """Restaure la couleur originale quand la souris quitte l'item"""
                # if not item_frame.selected:  # Ne pas changer la couleur si l'item est sélectionné
                
                if item_frame.is_dragging:
                    return  # Ne pas changer la couleur si on est en train de drag
                
                bg_color = COLOR_SELECTED if item_frame.selected else COLOR_BACKGROUND
                if item_frame.is_in_queue:
                    self._set_item_colors(item_frame, bg_color, exclude_queue_indicator=True)
                else:
                    self._set_item_colors(item_frame, bg_color, exclude_queue_indicator=False)
                if artist:
                    self._reset_text_animation(artist_label)
                self._reset_text_animation(title_label)
            
            # Clic droit pour ouvrir le menu de sélection ou le menu contextuel
            def on_playlist_item_right_click(event):
                # Initialiser le drag pour le clic droit
                self.drag_drop_handler.setup_drag_start(event, item_frame)
                
                # Si on a des éléments sélectionnés, ouvrir le menu de sélection
                if self.selected_items:
                    self.show_selection_menu(event)
                else:
                    # Comportement normal : ouvrir le menu contextuel pour un seul fichier
                    self._show_single_file_menu(event, filepath)
                
            # Bindings pour clics simples et doubles
            # item_frame.bind("<ButtonPress-1>", on_left_button_press)
            # item_frame.bind("<Double-1>", on_playlist_item_double_click)
            # thumbnail_label.bind("<ButtonPress-1>", on_left_button_press)
            # thumbnail_label.bind("<Double-1>", on_playlist_item_double_click)
            # text_frame.bind("<ButtonPress-1>", on_left_button_press)
            # text_frame.bind("<Double-1>", on_playlist_item_double_click)
            # title_label.bind("<ButtonPress-1>", on_left_button_press)
            # title_label.bind("<Double-1>", on_playlist_item_double_click)
            
            # Ajouter les bindings pour les labels de métadonnées s'ils existent
            # if artist:
            #     # Pour l'artiste, on ne veut pas le binding normal car il a son propre clic
            #     # Mais on veut quand même les autres bindings (drag, etc.)
            #     if other_metadata_label:
            #         other_metadata_label.bind("<ButtonPress-1>", on_left_button_press)
            #         other_metadata_label.bind("<Double-1>", on_playlist_item_double_click)
            # else:
            #     # Pas d'artiste, utiliser le label de métadonnées normal
            #     if 'metadata_label' in locals():
            #         metadata_label.bind("<ButtonPress-1>", on_left_button_press)
            #         metadata_label.bind("<Double-1>", on_playlist_item_double_click)
            
            duration_label.bind("<ButtonPress-1>", on_left_button_press)
            duration_label.bind("<Double-1>", on_playlist_item_double_click)
            
            # Ajouter le binding pour le numéro si il existe
            if show_numbers:
                number_label.bind("<ButtonPress-1>", on_left_button_press)
                number_label.bind("<Double-1>", on_playlist_item_double_click)
            
            
            widgets_to_bind = [item_frame, number_label, thumbnail_label, text_frame, 
                               title_label, duration_label]
            for widget in widgets_to_bind:
                if widget is None:
                    continue
                widget.bind("<ButtonPress-1>", on_left_button_press)
                widget.bind("<Double-1>", on_playlist_item_double_click)
                widget.bind("<ButtonPress-3>", on_playlist_item_right_click)
                # Ajouter les événements de survol
                widget.bind("<Leave>", on_leave)
                widget.bind("<Enter>", on_enter)
                
                # Ajouter un gestionnaire pour la molette de souris qui transmet l'événement directement au canvas
                if hasattr(self, 'playlist_canvas') and self.playlist_canvas:
                    # Fonction locale pour transmettre l'événement
                    def forward_wheel(event, canvas=self.playlist_canvas):
                        # Optimisation: Limiter la fréquence des événements
                        if hasattr(self, '_last_wheel_time'):
                            current_time = time.time()
                            if current_time - self._last_wheel_time < 0.01:  # 10ms entre les scrolls
                                return "break"
                            self._last_wheel_time = current_time
                        else:
                            self._last_wheel_time = time.time()
                            
                        # Traiter l'événement directement
                        if hasattr(event, 'delta') and event.delta:
                            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                        else:
                            if hasattr(event, 'num'):
                                if event.num == 4:
                                    canvas.yview_scroll(-1, "units")
                                elif event.num == 5:
                                    canvas.yview_scroll(1, "units")
                                
                        # Vérifier le scroll infini avec un délai
                        if hasattr(self, '_check_infinite_scroll'):
                            self.root.after(50, self._check_infinite_scroll)
                            
                        # Empêcher la propagation pour éviter le double traitement
                        return "break"
                    
                    # Lier les événements de la molette
                    widget.bind("<MouseWheel>", forward_wheel, add="+")
                    widget.bind("<Button-4>", forward_wheel, add="+")  # Linux
                    widget.bind("<Button-5>", forward_wheel, add="+")  # Linux
                
                # # Ajouter un gestionnaire pour la molette de souris qui transmet l'événement directement au canvas
                # if hasattr(self, 'playlist_canvas') and self.playlist_canvas:
                #     # Fonction locale pour transmettre l'événement
                #     def forward_wheel(event, canvas=self.playlist_canvas):
                #         if event.delta:
                #             canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                #         else:
                #             if event.num == 4:
                #                 canvas.yview_scroll(-1, "units")
                #             elif event.num == 5:
                #                 canvas.yview_scroll(1, "units")
                #         # Vérifier le scroll infini
                #         if hasattr(self, '_check_infinite_scroll'):
                #             self.root.after(50, self._check_infinite_scroll)
                #         return "break"  # Empêcher la propagation
                    
                #     widget.bind("<MouseWheel>", forward_wheel)
                #     widget.bind("<Button-4>", forward_wheel)  # Linux
                #     widget.bind("<Button-5>", forward_wheel)  # Linux
                
            
            
            
            # item_frame.bind("<ButtonPress-3>", on_playlist_item_right_click)
            # thumbnail_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            # text_frame.bind("<ButtonPress-3>", on_playlist_item_right_click)
            # title_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            # Ajouter les bindings pour le clic droit sur les labels de métadonnées s'ils existent
            # if artist:
            #     # Pour l'artiste, on veut quand même le clic droit normal
            #     artist_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            #     if other_metadata_label:
            #         other_metadata_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            # else:
                # # Pas d'artiste, utiliser le label de métadonnées normal
                # if 'metadata_label' in locals():
                #     metadata_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            # duration_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            
            # if show_numbers:
            #     number_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            
            # Configuration du drag-and-drop
            self.drag_drop_handler.setup_drag_drop(
                item_frame, 
                file_path=filepath, 
                item_type="playlist_item"
            )
            
            # CORRECTION: Forcer les bindings de motion après tous les autres bindings
            # pour éviter qu'ils soient écrasés
            # def force_motion_bindings():
            #     widgets_to_fix = [item_frame, thumbnail_label, text_frame, title_label, duration_label]
            #     # Ajouter les labels de métadonnées s'ils existent
            #     if artist:
            #         widgets_to_fix.append(artist_label)
            #         if other_metadata_label:
            #             widgets_to_fix.append(other_metadata_label)
            #     else:
            #         # Pas d'artiste, utiliser le label de métadonnées normal
            #         if 'metadata_label' in locals():
            #             widgets_to_fix.append(metadata_label)
            #     if show_numbers:  # Ajouter le numéro s'il existe
            #         widgets_to_fix.append(number_label)
                
            #     for widget in widgets_to_fix:
            #         if widget and widget.winfo_exists():
            #             widget.bind("<B1-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f))
            #             widget.bind("<ButtonRelease-1>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f))
            #             widget.bind("<B3-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f))
            #             widget.bind("<ButtonRelease-3>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f))
            
            # Programmer l'exécution après que tous les bindings soient configurés
            # Utiliser un délai pour s'assurer que c'est vraiment appliqué en dernier
            # self.root.after(50, force_motion_bindings)
            
            # Tooltip pour expliquer les interactions
            tooltip_text = "Musique de la playlist principale\nDouble-clic: Jouer cette musique\nCtrl + Clic: Ouvrir sur YouTube\nDrag vers la droite: Ajouter à la queue (prochaines musiques)\nDrag vers la gauche: Placer en premier dans la queue\nShift + Clic: Sélection multiple\nClic droit: Ouvrir le menu contextuel"
            create_tooltip(text_frame, tooltip_text)
            create_tooltip(title_label, tooltip_text)
            # Ajouter les tooltips pour les labels de métadonnées s'ils existent
            # if artist:
            #     create_tooltip(artist_label, tooltip_text)
            #     if other_metadata_label:
            #         create_tooltip(other_metadata_label, tooltip_text)
            # else:
            #     # Pas d'artiste, utiliser le label de métadonnées normal
            #     if 'metadata_label' in locals():
            #         create_tooltip(metadata_label, tooltip_text)
            # create_tooltip(thumbnail_label, tooltip_text)
            
            # Retourner le frame créé pour pouvoir l'utiliser
            return item_frame

        except Exception as e:
            print(f"Erreur affichage playlist item: {e}")
            return None

def select_playlist_item(self, item_frame=None, index=None, auto_scroll=True):
    """Met en surbrillance l'élément sélectionné dans la playlist
    
    Args:
        item_frame: Frame de l'élément à sélectionner
        index: Index de l'élément à sélectionner (alternatif à item_frame)
        auto_scroll: Si True, fait défiler automatiquement vers l'élément (défaut: True)
    """
    # Protection contre les appels multiples rapides
    if not hasattr(self, '_last_select_time'):
        self._last_select_time = 0
    
    current_time = time.time()
    if current_time - self._last_select_time < 0.05:  # 50ms de protection
        return
    self._last_select_time = current_time
    # Désélectionner tous les autres éléments
    try:
        if hasattr(self, 'playlist_container') and self.playlist_container.winfo_exists():
            # Accès sécurisé aux enfants pour la désélection
            try:
                children_for_deselect = self.playlist_container.winfo_children()
            except tk.TclError:
                children_for_deselect = []
            # if len(children_for_deselect) > 0:
            #     for child in children_for_deselect:
            #         print(child.filepath)
            # print('SELECT_PLAYLIST_ITEM ', [child.filepath for child in children_for_deselect])
            for child in children_for_deselect:
                try:
                    if child.winfo_exists() and hasattr(child, 'selected'):
                        child.selected = False
                        self._set_item_colors(child, '#4a4a4a')  # Couleur normale
                except tk.TclError:
                    # Widget détruit, ignorer
                    continue
            
            # Si on a fourni un index plutôt qu'un frame
            if index is not None:
                try:
                    children = self.playlist_container.winfo_children()
                    
                    # Vérifier si l'index fourni pourrait être un index absolu dans la playlist
                    # au lieu d'un index relatif dans la fenêtre chargée
                    if (USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading') and 
                        hasattr(self, '_last_window_start') and hasattr(self, '_last_window_end')):
                        
                        start_index = self._last_window_start
                        end_index = self._last_window_end
                        
                        # Si l'index semble être un index absolu (hors limites des enfants chargés)
                        if index >= len(children):
                            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                                print(f"⚠️  Index {index} semble absolu, fenêtre chargée: {start_index}-{end_index}")
                            
                            # Si l'index absolu est dans la fenêtre chargée, convertir en relatif
                            if start_index <= index < end_index:
                                relative_index = index - start_index
                                if 0 <= relative_index < len(children):
                                    index = relative_index
                                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                                        print(f"✅ Converti en index relatif: {index}")
                                else:
                                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                                        print(f"❌ Index relatif {relative_index} hors limites")
                                    return
                            else:
                                # L'index absolu n'est pas dans la fenêtre chargée
                                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                                    print(f"❌ Index absolu {index} pas dans fenêtre chargée, impossible de sélectionner")
                                return
                    
                    # Maintenant, index devrait être un index relatif valide
                    if 0 <= index < len(children):
                        item_frame = children[index]
                    else:
                        return
                        
                except tk.TclError:
                    # Erreur lors de l'accès aux enfants, ignorer
                    return
    except tk.TclError:
        # Container détruit, ignorer
        return
    
    # Sélectionner l'élément courant si fourni
    if item_frame:
        try:
            if item_frame.winfo_exists():
                item_frame.selected = True
                self._set_item_colors(item_frame, '#5a9fd8')  # Couleur de surbrillance (bleu)
                
                # Faire défiler avec animation pour que l'élément soit visible (seulement si auto_scroll=True)
                if auto_scroll:
                    try:
                        # Vérifier que tous les widgets existent encore
                        if (hasattr(self, 'playlist_container') and self.playlist_container.winfo_exists() and
                            hasattr(self, 'playlist_canvas') and self.playlist_canvas.winfo_exists()):
                            
                            container_height = self.playlist_container.winfo_height()
                            if container_height > 0:
                                item_y = item_frame.winfo_y()
                                target_position = item_y / container_height
                                self._smooth_scroll_to_position(target_position)
                            else:
                                # Fallback si la hauteur n'est pas disponible
                                item_y = item_frame.winfo_y()
                                container_height = self.playlist_container.winfo_height()
                                if container_height > 0:
                                    self.playlist_canvas.yview_moveto(item_y / container_height)
                    except tk.TclError as e:
                        # Widgets détruits pendant l'opération, ignorer silencieusement
                        print(f"DEBUG: Erreur scroll ignorée (widgets détruits): {e}")
                        pass
                    except Exception as e:
                        # Autres erreurs, ignorer aussi
                        print(f"DEBUG: Erreur animation scroll ignorée: {e}")
                        pass
        except tk.TclError:
            # item_frame détruit, ignorer
            pass

def _remove_from_main_playlist(self, filepath, frame, event=None, song_index=None):
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
                    self.reset_main_playlist()
            
            if frame.selected:
                frame.selected = False

            # Si la playlist devient vide, réinitialiser le flag
            if len(self.main_playlist) == 0:
                self.main_playlist_from_playlist = False
            
            # Rafraîchir complètement l'affichage de la playlist pour éviter les incohérences
            self._refresh_main_playlist_display()
            
            self.status_bar.config(text=f"Piste supprimée de la main playlist")
    except ValueError:
        pass
    except Exception as e:
        self.status_bar.config(text=f"Erreur suppression: {e}")

def _clear_main_playlist(self, event=None):
    """Vide complètement la liste de lecture principale (nécessite un double-clic)"""
    if not self.main_playlist:
        self.status_bar.config(text="La liste de lecture est déjà vide")
        return
    
    self.reset_main_playlist()

def _scroll_to_current_song(self, event=None):
    """Bouton find.png : Compatible ancien et nouveau système"""
    if not self.main_playlist or self.current_index >= len(self.main_playlist):
        self.status_bar.config(text="Aucune musique en cours de lecture")
        return
    
    try:
        # Définir un flag pour indiquer que le bouton find.png vient d'être utilisé
        # Ce flag sera utilisé par _check_and_unload_items pour prioriser le déchargement
        # des éléments avant la musique actuelle
        self._just_used_find_button = True
        
        print(f"DEBUG: FIND BUTTON: Vers chanson {self.current_index}")
        
        # NOUVEAU SYSTÈME PROGRESSIF
        if USE_NEW_CONFIG and get_main_playlist_config('enable_progressive_loading'):
            # Vérifier si la chanson courante est déjà chargée
            if self._is_index_already_loaded(self.current_index):
                print(f"DEBUG: Chanson {self.current_index} déjà chargée, scroll direct")
                
                # Scroll direct vers la chanson déjà chargée
                relative_index = self._find_relative_index_in_loaded(self.current_index)
                if relative_index is not None:
                    self.select_playlist_item(index=relative_index, auto_scroll=True)
                    
                    total_songs = len(self.main_playlist)
                    self.status_bar.config(text=f"🎯 Navigation vers la chanson {self.current_index + 1}/{total_songs}")
                    
                    # Décharger les éléments avant la musique actuelle
                    if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_unloading'):
                        print(f"DEBUG: Déchargement des éléments avant la musique actuelle après scroll direct")
                        # Attendre un peu pour s'assurer que le scroll est terminé
                        self.root.after(100, lambda: self._check_and_unload_items(self.current_index))
                    
                    print(f"DEBUG: Find scroll direct progressif: chanson {self.current_index} (relatif: {relative_index})")
                    return
            
            # Chanson pas encore chargée : déclencher le chargement progressif
            print(f"DEBUG: Chanson {self.current_index} non chargée, chargement progressif requis")
            
            # Déclencher le chargement progressif depuis cette position
            self._progressive_load_system()
            
            # Scroll après chargement
            def scroll_after_progressive_load():
                try:
                    relative_index = self._find_relative_index_in_loaded(self.current_index)
                    if relative_index is not None:
                        print(f"DEBUG: Chanson {self.current_index} maintenant chargée, scroll vers position relative {relative_index}")
                        self.select_playlist_item(index=relative_index, auto_scroll=True)
                        
                        total_songs = len(self.main_playlist)
                        self.status_bar.config(text=f"🎯 Navigation vers la chanson {self.current_index + 1}/{total_songs}")
                        
                        # Décharger les éléments après avoir recentré
                        if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_unloading'):
                            print(f"DEBUG: Déchargement des éléments avant la musique actuelle après chargement progressif")
                            # Attendre un peu pour s'assurer que le scroll est terminé
                            self.root.after(100, lambda: self._check_and_unload_items(self.current_index))
                        
                        print(f"DEBUG: Find scroll après chargement progressif: chanson {self.current_index}")
                    else:
                        print(f"DEBUG: Chanson {self.current_index} toujours non chargée après chargement progressif")
                        
                        # Forcer le chargement direct de la musique actuelle
                        try:
                            # Charger la musique actuelle et quelques éléments autour
                            preserve_before = get_main_playlist_config('preserve_items_before_current')
                            preserve_after = get_main_playlist_config('preserve_items_after_current')
                            preserve_start = max(0, self.current_index - preserve_before)
                            preserve_end = min(len(self.main_playlist) - 1, self.current_index + preserve_after)
                            
                            print(f"DEBUG: Forçage du chargement de la musique actuelle et des éléments autour ({preserve_start}-{preserve_end})")
                            
                            # Charger la musique actuelle et quelques éléments autour
                            self._append_progressive_items(preserve_start, preserve_end + 1)
                            
                            # Réessayer de trouver l'index relatif
                            relative_index = self._find_relative_index_in_loaded(self.current_index)
                            if relative_index is not None:
                                print(f"DEBUG: Chanson {self.current_index} maintenant chargée après forçage, scroll vers position relative {relative_index}")
                                self.select_playlist_item(index=relative_index, auto_scroll=True)
                                
                                # Décharger les éléments après avoir recentré
                                if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_unloading'):
                                    print(f"DEBUG: Déchargement des éléments avant la musique actuelle après forçage")
                                    # Attendre un peu pour s'assurer que le scroll est terminé
                                    self.root.after(100, lambda: self._check_and_unload_items(self.current_index))
                            else:
                                print(f"DEBUG: ERREUR CRITIQUE: Impossible de charger la musique actuelle {self.current_index} même après forçage!")
                        except Exception as e:
                            print(f"DEBUG: Erreur forçage chargement: {e}")
                            import traceback
                            traceback.print_exc()
                except Exception as e:
                    print(f"DEBUG: Erreur find scroll après chargement progressif: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Attendre un peu plus longtemps pour s'assurer que le chargement progressif a eu le temps de s'exécuter
            self.root.after(100, scroll_after_progressive_load)
            
        # ANCIEN SYSTÈME FENÊTRÉ
        elif USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading'):
            # [Code ancien conservé]
            if (hasattr(self, '_last_window_start') and hasattr(self, '_last_window_end')):
                start_index = self._last_window_start
                end_index = self._last_window_end
                
                if start_index <= self.current_index < end_index:
                    relative_index = self.current_index - start_index
                    self.select_playlist_item(index=relative_index, auto_scroll=True)
                    
                    total_songs = len(self.main_playlist)
                    self.status_bar.config(text=f"🎯 Navigation vers la chanson {self.current_index + 1}/{total_songs}")
                    return
            
            songs_before = get_main_playlist_config('songs_before_current')
            songs_after = get_main_playlist_config('songs_after_current')
            start_index = max(0, self.current_index - songs_before)
            end_index = min(len(self.main_playlist), self.current_index + songs_after + 1)
            
            self._force_reload_window(start_index, end_index)
            
            def scroll_after_reload():
                try:
                    relative_index = self.current_index - start_index
                    self.select_playlist_item(index=relative_index, auto_scroll=True)
                    
                    total_songs = len(self.main_playlist)
                    self.status_bar.config(text=f"🎯 Navigation vers la chanson {self.current_index + 1}/{total_songs}")
                except Exception as e:
                    pass
            
            self.root.after(50, scroll_after_reload)
            
        else:
            # Système classique (sans intelligence)
            self.select_playlist_item(index=self.current_index, auto_scroll=True)
            
            total_songs = len(self.main_playlist)
            self.status_bar.config(text=f"Navigation vers la chanson {self.current_index + 1}/{total_songs}")
        
    except Exception as e:
        print(f"Erreur lors du scroll vers la chanson actuelle: {e}")
        self.status_bar.config(text="Erreur lors de la navigation")

def select_current_song_smart(self, auto_scroll=True, force_reload=False):
    """Auto-scroll intelligent : Compatible ancien et nouveau système"""
    try:
        if not self.main_playlist or self.current_index >= len(self.main_playlist):
            return
            
        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
            print(f"🎮 AUTO-SCROLL SMART: Vers chanson {self.current_index}")
        
        # NOUVEAU SYSTÈME PROGRESSIF
        if USE_NEW_CONFIG and get_main_playlist_config('enable_progressive_loading'):
            # Vérifier si la chanson courante est déjà chargée
            if self._is_index_already_loaded(self.current_index):
                # Chanson déjà chargée : scroll direct vers elle
                relative_index = self._find_relative_index_in_loaded(self.current_index)
                if relative_index is not None:
                    self.select_playlist_item(index=relative_index, auto_scroll=auto_scroll)
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"✅ Auto-scroll progressif direct: chanson {self.current_index} (relatif: {relative_index})")
                    return
            
            # Chanson pas encore chargée : déclencher le chargement progressif
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"🎵 Auto-scroll progressif: Chargement requis pour chanson {self.current_index}")
            
            # Déclencher le chargement progressif depuis cette position
            self._progressive_load_system()
            
            # Auto-scroll après chargement
            def auto_scroll_after_progressive_load():
                try:
                    relative_index = self._find_relative_index_in_loaded(self.current_index)
                    if relative_index is not None:
                        self.select_playlist_item(index=relative_index, auto_scroll=auto_scroll)
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            print(f"✅ Auto-scroll après chargement progressif: chanson {self.current_index}")
                except Exception as e:
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"❌ Erreur auto-scroll après chargement progressif: {e}")
            
            self.root.after(50, auto_scroll_after_progressive_load)
            
        # ANCIEN SYSTÈME FENÊTRÉ
        elif USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading'):
            # [Ancien code conservé pour compatibilité]
            if (hasattr(self, '_last_window_start') and hasattr(self, '_last_window_end') and not force_reload):
                start_index = self._last_window_start
                end_index = self._last_window_end
                
                if start_index <= self.current_index < end_index:
                    relative_index = self.current_index - start_index
                    self.select_playlist_item(index=relative_index, auto_scroll=auto_scroll)
                    return
            
            songs_before = get_main_playlist_config('songs_before_current')
            songs_after = get_main_playlist_config('songs_after_current')
            start_index = max(0, self.current_index - songs_before)
            end_index = min(len(self.main_playlist), self.current_index + songs_after + 1)
            self._force_reload_window(start_index, end_index)
            
            def auto_scroll_after_reload():
                try:
                    relative_index = self.current_index - start_index
                    self.select_playlist_item(index=relative_index, auto_scroll=auto_scroll)
                except Exception as e:
                    pass
            self.root.after(50, auto_scroll_after_reload)
            
        else:
            # Système classique avec animation
            self.select_playlist_item(index=self.current_index, auto_scroll=auto_scroll)
            
    except Exception as e:
        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
            print(f"❌ Erreur select current smart: {e}")

def _find_relative_index_in_loaded(self, absolute_index):
        """Trouve l'index relatif d'une chanson dans les éléments chargés"""
        try:
            children = self.playlist_container.winfo_children()
            print(f"DEBUG: Recherche de l'index relatif pour la chanson {absolute_index} parmi {len(children)} éléments chargés")
            
            # Vérifier s'il y a des doublons
            index_count = {}
            for child in children:
                if hasattr(child, 'song_index'):
                    index = child.song_index
                    if index in index_count:
                        index_count[index] += 1
                    else:
                        index_count[index] = 1
            
            duplicates = [idx for idx, count in index_count.items() if count > 1]
            if duplicates:
                print(f"DEBUG: ATTENTION: Doublons détectés pour les index: {duplicates}")
                
                # Supprimer les doublons
                for index in duplicates:
                    count = 0
                    for child in list(children):  # Utiliser une copie pour éviter les problèmes de modification pendant l'itération
                        if hasattr(child, 'song_index') and child.song_index == index:
                            count += 1
                            if count > 1:  # Garder le premier, supprimer les autres
                                print(f"DEBUG: Suppression du doublon pour l'index {index}")
                                child.destroy()
                
                # Mettre à jour la liste des enfants après suppression des doublons
                children = self.playlist_container.winfo_children()
                print(f"DEBUG: Après suppression des doublons: {len(children)} éléments")
                
                # Invalider le cache
                self._invalidate_loaded_indexes_cache()
            
            # Rechercher l'index relatif
            for i, child in enumerate(children):
                if hasattr(child, 'song_index'):
                    print(f"DEBUG: Élément {i} a l'index absolu {child.song_index}")
                    if child.song_index == absolute_index:
                        print(f"DEBUG: Trouvé! Index relatif {i} pour index absolu {absolute_index}")
                        return i
            
            print(f"DEBUG: Index absolu {absolute_index} non trouvé dans les éléments chargés")
            return None
        except Exception as e:
            print(f"DEBUG: Erreur recherche index relatif: {e}")
            import traceback
            traceback.print_exc()
            return None

def add_to_main_playlist(self, filepath, thumbnail_path=None, song_index=None, show_status=True, allow_duplicates=False):
    """Fonction centralisée pour ajouter une musique à la main playlist
    
    Args:
        filepath: Chemin vers le fichier audio
        thumbnail_path: Chemin vers la miniature (optionnel)
        song_index: Index spécifique pour la chanson (optionnel)
        show_status: Afficher le message de statut (défaut: True)
        allow_duplicates: Permettre les doublons (défaut: False)
    """
    print(f"Ajout de {filepath} à la main playlist add_to_main_playlist")
    if allow_duplicates or filepath not in self.main_playlist:
        self.main_playlist.append(filepath)
        self._add_main_playlist_item(filepath, thumbnail_path, song_index)
        self._update_downloads_queue_visual()
        
        if show_status:
            self.status_bar.config(text=f"Ajouté à la liste de lecture principale: {os.path.basename(filepath)}")
        return True
    else:
        if show_status:
            self.status_bar.config(text=f"Déjà dans la liste de lecture principale: {os.path.basename(filepath)}")
        return False

def _smooth_scroll_to_position(self, target_position, duration=500):
    """Anime le scroll vers une position cible avec une courbe ease-in-out"""
    # Vérifier que le canvas existe encore avant de commencer
    if not (hasattr(self, 'playlist_canvas') and self.playlist_canvas.winfo_exists()):
        return
        
    # Annuler toute animation en cours
    if hasattr(self, 'scroll_animation_id') and self.scroll_animation_id:
        try:
            self.root.after_cancel(self.scroll_animation_id)
        except:
            pass
        self.scroll_animation_id = None
    
    # Si une animation est déjà en cours, l'arrêter
    if hasattr(self, 'scroll_animation_active') and self.scroll_animation_active:
        self.scroll_animation_active = False
    
    # Obtenir la position actuelle du scroll
    try:
        # Vérifier que le canvas existe encore
        if not (hasattr(self, 'playlist_canvas') and self.playlist_canvas.winfo_exists()):
            return
            
        current_top, current_bottom = self.playlist_canvas.yview()
        start_position = current_top
    except tk.TclError:
        # Canvas détruit, ignorer
        return
    except Exception:
        # En cas d'autre erreur, faire un scroll instantané si possible
        try:
            if hasattr(self, 'playlist_canvas') and self.playlist_canvas.winfo_exists():
                self.playlist_canvas.yview_moveto(target_position)
        except tk.TclError:
            # Canvas détruit, ignorer
            pass
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
            # Vérifier que le canvas existe encore
            if not (hasattr(self, 'playlist_canvas') and self.playlist_canvas.winfo_exists()):
                self.scroll_animation_active = False
                return
                
            self.playlist_canvas.yview_moveto(current_position)
        except tk.TclError:
            # Canvas détruit, arrêter l'animation
            self.scroll_animation_active = False
            return
        except Exception:
            # En cas d'autre erreur, arrêter l'animation
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

def reset_main_playlist(self):
    # Arrêter la lecture si une musique est en cours
    if hasattr(self, 'paused') and not self.paused:
        pygame.mixer.music.stop()
    
    # Décharger la musique
    pygame.mixer.music.unload()
    
    # Vider la liste principale et la playlist "Main Playlist"
    self.main_playlist.clear()
    if "Main Playlist" in self.playlists:
        self.playlists["Main Playlist"].clear()
    self.current_index = 0
    
    # Vider la queue
    if hasattr(self, 'queue_items'):
        self.queue_items.clear()
    
    # Vider l'affichage de la playlist
    try:
        if hasattr(self, 'playlist_container') and self.playlist_container.winfo_exists():
            for widget in self.playlist_container.winfo_children():
                try:
                    if widget.winfo_exists():
                        widget.destroy()
                except tk.TclError:
                    # Widget déjà détruit, ignorer
                    continue
    except tk.TclError:
        # Container détruit, ignorer
        pass
    
    # Nettoyer la sélection dans tous les containers
    self.clear_all_current_song_selections()
    
    # Réinitialiser les variables de fenêtrage optimisé
    if hasattr(self, '_last_window_start'):
        delattr(self, '_last_window_start')
    if hasattr(self, '_last_window_end'):
        delattr(self, '_last_window_end')
    
    # Réinitialiser les variables d'optimisation
    if hasattr(self, '_last_select_time'):
        self._last_select_time = 0
    
    # Mettre à jour l'affichage
    self.status_bar.config(text="Liste de lecture vidée")
    
    # Réinitialiser l'affichage de la chanson actuelle
    if hasattr(self, 'song_label'):
        self.song_label.config(text="No track selected")
    if hasattr(self, 'song_metadata_label'):
        self.song_metadata_label.config(text="")
    
    # Changer l'image
    self.clear_thumbnail_label()
    
    # Mettre à jour les contrôles
    if hasattr(self, 'time_slider'):
        self.time_slider.set(0)
    if hasattr(self, 'time_label'):
        self.time_label.config(text="00:00 / 00:00")

def _refresh_main_playlist_display(self, force_full_refresh=False):
        """Rafraîchit l'affichage de la main playlist avec optimisation par fenêtrage"""
        print
        # Protection contre les appels multiples rapides
        if not hasattr(self, '_last_refresh_time'):
            self._last_refresh_time = 0
        
        current_time = time.time()
        if not force_full_refresh and current_time - self._last_refresh_time < 0.1:  # 100ms de protection
            return
        self._last_refresh_time = current_time
        
        try:
            # Vérifier que le container existe encore
            if not hasattr(self, 'playlist_container'):
                return
                
            if not self.playlist_container.winfo_exists():
                return
            
            playlist_size = len(self.main_playlist)
            
            # Utiliser la nouvelle configuration si disponible
            if USE_NEW_CONFIG:
                optimizations_enabled = get_main_playlist_config('enable_optimizations')
                use_windowing = config_should_use_windowing(playlist_size)
            else:
                # Fallback vers l'ancienne configuration
                optimizations_enabled = get_config("enable_optimizations", True)
                use_windowing = should_use_windowing(playlist_size)

            # Décider du mode d'affichage selon la taille et la configuration
            if not optimizations_enabled or not use_windowing:
                # Optimisations désactivées ou petite playlist : affichage complet
                self._refresh_full_playlist_display()
                return
            
            # Grande playlist : utiliser le fenêtrage optimisé même avec force_full_refresh
            # Le force_full_refresh ne fait que forcer la recréation des widgets, pas l'affichage complet
            self._refresh_windowed_playlist_display(force_recreate=force_full_refresh)
                
        except tk.TclError as e:
            # Container détruit ou problème avec l'interface, ignorer silencieusement
            pass
        except Exception as e:
            print(f"Erreur lors du rafraîchissement de la playlist: {e}")

def _refresh_full_playlist_display(self):
        """Rafraîchit complètement l'affichage de la playlist (version originale)"""
        try:
            # Vider le container actuel
            try:
                children = self.playlist_container.winfo_children()
            except tk.TclError:
                children = []
                
            for widget in children:
                try:
                    if widget.winfo_exists():
                        widget.destroy()
                except tk.TclError:
                    continue
            
            # Recréer tous les éléments avec les bons index
            for i, filepath in enumerate(self.main_playlist):
                self._add_main_playlist_item(filepath, song_index=i)
            
            # Remettre en surbrillance la chanson en cours si elle existe
            if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
                try:
                    self.select_playlist_item(index=self.current_index, auto_scroll=False)
                except tk.TclError:
                    pass
            
            # Mettre à jour la région de scroll du canvas
            # Différer légèrement pour s'assurer que la géométrie est calculée
            if USE_NEW_CONFIG:
                delay = get_main_playlist_config('scroll_update_delay')
            else:
                delay = 10
            self.root.after(delay, lambda: self._update_scroll_region_after_unload())
                    
        except Exception as e:
            print(f"Erreur lors du rafraîchissement complet: {e}")

def _refresh_windowed_playlist_display(self, force_recreate=False):
        """Rafraîchit l'affichage avec fenêtrage optimisé (n'affiche que les éléments visibles)"""
        try:
            # Optimisation: Éviter les rafraîchissements trop fréquents
            if not force_recreate and hasattr(self, '_last_refresh_time'):
                current_time = time.time()
                min_refresh_interval = 0.05  # 50ms entre les rafraîchissements
                if current_time - self._last_refresh_time < min_refresh_interval:
                    return
            self._last_refresh_time = time.time()
            
            # Vérifier si on doit faire un auto-recentrage sur la chanson courante
            if (USE_NEW_CONFIG and get_main_playlist_config('auto_center_on_song_change') and
                hasattr(self, 'current_index') and not force_recreate):
                
                current_index = self.current_index
                last_index = getattr(self, '_last_current_index', current_index)
                
                # Si la chanson a changé et que l'utilisateur ne scroll pas
                if (current_index != last_index and 
                    not getattr(self, '_user_is_scrolling', False) and
                    not getattr(self, '_auto_centering', False)):
                    
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"Chanson changée de {last_index} à {current_index}, auto-recentrage")
                    
                    # Déclencher le smart reload avant l'auto-recentrage
                    self._trigger_smart_reload_on_song_change()
                    
                    # Faire un auto-recentrage au lieu du rafraîchissement normal
                    self._auto_center_on_current_song()
                    return
            
            # Utiliser le système de chargement intelligent au lieu du calcul manuel
            if (USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading')):
                # Utiliser le système intelligent
                smart_start, smart_end = self._calculate_smart_window()
                if smart_start is not None and smart_end is not None:
                    start_index, end_index = smart_start, smart_end
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"Utilisation fenêtre intelligente: {start_index}-{end_index}")
                else:
                    # Fallback vers le système classique
                    songs_before = get_main_playlist_config('songs_before_current') if USE_NEW_CONFIG else 10
                    songs_after = get_main_playlist_config('songs_after_current') if USE_NEW_CONFIG else 10
                    start_index = max(0, self.current_index - songs_before)
                    end_index = min(len(self.main_playlist), self.current_index + songs_after + 1)
            else:
                # Système classique
                songs_before = get_main_playlist_config('songs_before_current') if USE_NEW_CONFIG else 10
                songs_after = get_main_playlist_config('songs_after_current') if USE_NEW_CONFIG else 10
                start_index = max(0, self.current_index - songs_before)
                end_index = min(len(self.main_playlist), self.current_index + songs_after + 1)
            
            # Vérifier si on peut réutiliser l'affichage existant (optimisation)
            # Mais seulement si le container a des enfants (pas après un clear) et pas de force_recreate
            can_reuse = (not force_recreate and
                        hasattr(self, '_last_window_start') and hasattr(self, '_last_window_end') and
                        self._last_window_start == start_index and self._last_window_end == end_index and
                        hasattr(self, 'playlist_container') and self.playlist_container.winfo_exists() and
                        len(self.playlist_container.winfo_children()) > 0)
            
            if can_reuse:
                # Juste mettre à jour la surbrillance sans recréer les widgets
                self._update_current_song_highlight_only()
                return
            
            # Sauvegarder les paramètres de fenêtre pour la prochaine fois
            self._last_window_start = start_index
            self._last_window_end = end_index
            
            # Vider le container actuel
            try:
                children = self.playlist_container.winfo_children()
            except tk.TclError:
                children = []
                
            for widget in children:
                try:
                    if widget.winfo_exists():
                        widget.destroy()
                except tk.TclError:
                    continue
            
            # Les indicateurs sont supprimés pour un affichage plus propre
            
            # Afficher les éléments dans la fenêtre
            for i in range(start_index, end_index):
                if i < len(self.main_playlist):
                    filepath = self.main_playlist[i]
                    self._add_main_playlist_item(filepath, song_index=i)
            
            # Précharger les métadonnées des éléments suivants de manière asynchrone
            playlist_size = len(self.main_playlist)  # Correction erreur Pylance
            if get_config("enable_preloading", True) and end_index < len(self.main_playlist):
                preload_size = get_preload_size(playlist_size)
                if preload_size > 0:
                    next_batch_start = end_index
                    next_batch_end = min(len(self.main_playlist), end_index + preload_size)
                    self._preload_metadata_async(next_batch_start, next_batch_end)
            
            # Les indicateurs de fin sont également supprimés
            
            # Remettre en surbrillance la chanson en cours si elle est dans la fenêtre
            if (len(self.main_playlist) > 0 and 
                self.current_index < len(self.main_playlist) and
                start_index <= self.current_index < end_index):
                try:
                    # Trouver le widget correspondant à l'index courant
                    widgets = self.playlist_container.winfo_children()
                    # Calculer la position relative dans la fenêtre (sans indicateurs)
                    relative_index = self.current_index - start_index
                    
                    if 0 <= relative_index < len(widgets):
                        widget = widgets[relative_index]
                        if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                            self._highlight_current_song_widget(widget)
                except Exception:
                    pass
            
            # Mettre à jour la région de scroll du canvas pour permettre le scroll
            # Différer légèrement pour s'assurer que la géométrie est calculée
            if USE_NEW_CONFIG:
                delay = get_main_playlist_config('scroll_update_delay')
            else:
                delay = 10
            def setup_scroll():
                self._update_scroll_region_after_unload()
                # Force le chargement/déchargement intelligent immédiatement
                if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading'):
                    self._smart_load_unload()
                self._trigger_smart_reload_on_song_change()  # Déclencher le smart reload
            
            self.root.after(delay, setup_scroll)
                    
        except Exception as e:
            print(f"Erreur lors du rafraîchissement par fenêtrage: {e}")

def _update_current_song_highlight_only(self):
        """Met à jour uniquement la surbrillance de la chanson courante sans recréer les widgets"""
        try:
            if not (hasattr(self, 'playlist_container') and self.playlist_container.winfo_exists()):
                return
                
            # Désélectionner tous les éléments
            children = self.playlist_container.winfo_children()
            for child in children:
                try:
                    if child.winfo_exists() and hasattr(child, 'config'):
                        self._set_item_colors(child, '#4a4a4a')  # Couleur normale
                except:
                    continue
            
            # Calculer la position de la chanson courante dans la fenêtre affichée
            if (hasattr(self, '_last_window_start') and hasattr(self, '_last_window_end') and
                self._last_window_start <= self.current_index < self._last_window_end):
                
                relative_index = self.current_index - self._last_window_start
                # Ajouter 1 si on a un indicateur du début
                if self._last_window_start > 0:
                    relative_index += 1
                
                if 0 <= relative_index < len(children):
                    widget = children[relative_index]
                    if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                        self._highlight_current_song_widget(widget)
                        
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la surbrillance: {e}")

# def _set_item_colors(self, item_frame, bg_color):
#         """Change la couleur de fond d'un élément de playlist et de ses enfants"""
#         try:
#             if hasattr(item_frame, 'config'):
#                 item_frame.config(bg=bg_color)
                
#             # Changer aussi la couleur des enfants
#             for child in item_frame.winfo_children():
#                 try:
#                     if hasattr(child, 'config') and hasattr(child, 'cget'):
#                         # Ne pas changer les indicateurs de queue (couleur noire)
#                         if child.cget('bg') != 'black':
#                             child.config(bg=bg_color)
                            
#                         # Récursif pour les sous-enfants
#                         for subchild in child.winfo_children():
#                             try:
#                                 if hasattr(subchild, 'config') and hasattr(subchild, 'cget'):
#                                     if subchild.cget('bg') != 'black':
#                                         subchild.config(bg=bg_color)
#                             except:
#                                 pass
#                 except:
#                     pass
#         except Exception as e:
#             print(f"Erreur lors du changement de couleur: {e}")

def _add_playlist_indicator(self, text, position):
        """Ajoute un indicateur visuel pour les éléments non affichés"""
        try:
            indicator_frame = tk.Frame(
                self.playlist_container,
                bg='#2a2a2a',
                relief='flat',
                bd=0,
                height=30
            )
            indicator_frame.pack(fill='x', pady=1, padx=5)
            indicator_frame.pack_propagate(False)
            
            indicator_label = tk.Label(
                indicator_frame,
                text=text,
                bg='#2a2a2a',
                fg='#888888',
                font=('TkDefaultFont', 9, 'italic'),
                anchor='center'
            )
            indicator_label.pack(expand=True, fill='both')
            
            # Ajouter un clic pour naviguer
            def on_indicator_click(event):
                jump_size = get_config("jump_size", 15)
                if position == "top":
                    # Aller vers le début - sauter vers le haut
                    new_index = max(0, self.current_index - jump_size)
                else:
                    # Aller vers la fin - sauter vers le bas
                    new_index = min(len(self.main_playlist) - 1, self.current_index + jump_size)
                
                if 0 <= new_index < len(self.main_playlist):
                    self.current_index = new_index
                    self.play_track()
                    # Forcer le rafraîchissement pour afficher la nouvelle fenêtre
                    self.root.after(50, lambda: self._refresh_main_playlist_display(force_full_refresh=False))
            
            indicator_label.bind("<Button-1>", on_indicator_click)
            indicator_label.config(cursor="hand2")
            
            # Ajouter un tooltip pour expliquer la fonctionnalité
            try:
                if position == "top":
                    create_tooltip(indicator_label, "Cliquez pour remonter de 15 chansons")
                else:
                    create_tooltip(indicator_label, "Cliquez pour descendre de 15 chansons")
            except:
                pass  # Si create_tooltip n'est pas disponible, ignorer
            
        except Exception as e:
            print(f"Erreur lors de l'ajout de l'indicateur: {e}")

def _highlight_current_song_widget(self, widget):
        """Met en surbrillance le widget de la chanson courante"""
        # try:
        #     if hasattr(widget, 'config'):
        #         widget.config(bg=COLOR_BACKGROUND_HIGHLIGHT)
        #         # Mettre en surbrillance tous les enfants aussi
        #         for child in widget.winfo_children():
        #             if hasattr(child, 'config') and hasattr(child, 'cget'):
        #                 try:
        #                     if child.cget('bg') != 'black':  # Ne pas changer les indicateurs de queue
        #                         child.config(bg=COLOR_BACKGROUND_HIGHLIGHT)
        #                 except:
        #                     pass
        # except Exception as e:
        #     print(f"Erreur lors de la mise en surbrillance: {e}")
        
        try:
            self._set_item_colors(widget, COLOR_SELECTED)
        except Exception as e:
            print(f"Erreur lors de la mise en surbrillance: {e}")

def _refresh_main_playlist_display_async(self):
        """Version asynchrone du rafraîchissement pour éviter les lags lors du chargement de grandes playlists"""
        try:
            print("_refresh_main_playlist_display_async appelé")
            # Forcer un rafraîchissement complet si les variables de fenêtrage n'existent pas
            # (cas d'un rechargement après clear)
            force_refresh = not (hasattr(self, '_last_window_start') and hasattr(self, '_last_window_end'))
            
            # Utiliser le système de fenêtrage optimisé
            self._refresh_main_playlist_display(force_full_refresh=force_refresh)
            # self._refresh_main_playlist_display(force_full_refresh=False)
            
            # Mettre à jour le message de statut
            if hasattr(self, 'status_bar'):
                total_songs = len(self.main_playlist)
                if total_songs > 50:
                    self.status_bar.config(text=f"Playlist chargée ({total_songs} musiques) - Affichage optimisé")
                else:
                    self.status_bar.config(text=f"Playlist chargée ({total_songs} musiques)")
                    
        except Exception as e:
            print(f"Erreur lors du rafraîchissement asynchrone: {e}")
            if hasattr(self, 'status_bar'):
                self.status_bar.config(text="Erreur lors du chargement de la playlist")

def _scroll_to_current_song_optimized(self):
        """Scroll optimisé vers la chanson courante dans une grande playlist"""
        try:
            if len(self.main_playlist) <= 50:
                # Pour les petites playlists, utiliser le scroll normal
                self._scroll_to_current_song()
                return
            
            # Pour les grandes playlists, vérifier si la chanson courante est visible
            if (hasattr(self, '_last_window_start') and hasattr(self, '_last_window_end')):
                if not (self._last_window_start <= self.current_index < self._last_window_end):
                    # La chanson courante n'est pas visible, rafraîchir la fenêtre
                    self._refresh_main_playlist_display(force_full_refresh=False)
                else:
                    # La chanson est visible, juste mettre à jour la surbrillance
                    self._update_current_song_highlight_only()
            else:
                # Première fois, rafraîchir normalement
                self._refresh_main_playlist_display(force_full_refresh=False)
                
        except Exception as e:
            print(f"Erreur lors du scroll optimisé: {e}")

def get_playlist_navigation_info(self):
        """Retourne des informations sur la navigation dans la playlist pour l'interface"""
        try:
            if len(self.main_playlist) <= 50:
                return {
                    'total_songs': len(self.main_playlist),
                    'current_index': self.current_index,
                    'windowed': False,
                    'window_info': None
                }
            
            window_size = 30
            half_window = window_size // 2
            start_index = max(0, self.current_index - half_window)
            end_index = min(len(self.main_playlist), self.current_index + half_window + 1)
            
            return {
                'total_songs': len(self.main_playlist),
                'current_index': self.current_index,
                'windowed': True,
                'window_info': {
                    'start': start_index,
                    'end': end_index,
                    'size': end_index - start_index,
                    'songs_before': start_index,
                    'songs_after': len(self.main_playlist) - end_index
                }
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des infos de navigation: {e}")
            return None

def _preload_metadata_async(self, start_index, end_index):
        """Précharge les métadonnées des chansons dans la fenêtre visible de manière asynchrone"""
        def preload_worker():
            try:
                for i in range(start_index, min(end_index, len(self.main_playlist))):
                    if i < len(self.main_playlist):
                        filepath = self.main_playlist[i]
                        # Précharger les métadonnées en arrière-plan
                        try:
                            self._get_audio_metadata(filepath)
                            self._get_audio_duration(filepath)
                            # Petite pause pour ne pas surcharger le système
                            time.sleep(0.01)
                        except Exception:
                            continue
            except Exception as e:
                print(f"Erreur lors du préchargement des métadonnées: {e}")
        
        # Lancer le préchargement dans un thread séparé
        threading.Thread(target=preload_worker, daemon=True).start()

def _optimize_playlist_performance(self):
        """Optimise les performances de la playlist selon sa taille"""
        try:
            playlist_size = len(self.main_playlist)
            
            if playlist_size <= 20:
                # Petite playlist : pas d'optimisation nécessaire
                return "small"
            elif playlist_size <= 50:
                # Playlist moyenne : optimisations légères
                return "medium"
            elif playlist_size <= 200:
                # Grande playlist : fenêtrage activé
                return "large"
            else:
                # Très grande playlist : optimisations maximales
                return "xlarge"
                
        except Exception as e:
            print(f"Erreur lors de l'optimisation des performances: {e}")
            return "medium"

def _update_canvas_scroll_region_and_restore(self, position):
        """Met à jour la région de scroll et restaure la position spécifiée
        
        Args:
            position: Position de scroll à restaurer (entre 0 et 1)
        """
        try:
            # Mettre à jour la région de scroll
            self._update_canvas_scroll_region(preserve_position=False)
            
            # Restaurer la position de scroll
            self.root.after(10, lambda: self.playlist_canvas.yview_moveto(position))
            print(f"DEBUG: Position de scroll restaurée à {position:.3f}")
        except Exception as e:
            print(f"DEBUG: Erreur restauration position scroll: {e}")
            
def _update_canvas_scroll_region(self, preserve_position=True):
        """Met à jour la région de scroll du canvas pour permettre le scroll avec la molette
        
        Args:
            preserve_position: Si True, préserve la position de scroll actuelle (défaut: True)
        """
        try:
            # Optimisation: Éviter les mises à jour trop fréquentes
            if hasattr(self, '_last_scroll_region_update'):
                current_time = time.time()
                min_update_interval = 0.05  # 50ms entre les mises à jour
                if current_time - self._last_scroll_region_update < min_update_interval:
                    return
            self._last_scroll_region_update = time.time()
            
            if not (hasattr(self, 'playlist_canvas') and hasattr(self, 'playlist_container')):
                return
                
            if not (self.playlist_canvas.winfo_exists() and self.playlist_container.winfo_exists()):
                return
            
            # Sauvegarder la position de scroll actuelle si demandé
            current_scroll_position = None
            if preserve_position:
                try:
                    scroll_top, scroll_bottom = self.playlist_canvas.yview()
                    current_scroll_position = scroll_top
                    print(f"DEBUG: Position de scroll actuelle sauvegardée: {scroll_top:.3f}")
                except Exception as e:
                    print(f"DEBUG: Erreur sauvegarde position scroll: {e}")
            
            # Optimisation: Utiliser update_idletasks seulement si nécessaire
            # Vérifier si la taille a changé depuis la dernière mise à jour
            current_width = self.playlist_container.winfo_width()
            current_height = self.playlist_container.winfo_height()
            
            if (not hasattr(self, '_last_container_size') or 
                self._last_container_size != (current_width, current_height)):
                # Forcer la mise à jour de la géométrie seulement si nécessaire
                self.playlist_container.update_idletasks()
                self._last_container_size = (current_width, current_height)
            
            # Pour le système de fenêtrage, on doit simuler une région de scroll plus grande
            # que ce qui est affiché pour permettre le scroll infini
            children = self.playlist_container.winfo_children()
            children_count = len(children)
            
            if children_count > 0:
                if USE_NEW_CONFIG:
                    item_height = get_main_playlist_config('item_height_estimate')
                    total_songs = len(self.main_playlist)
                    enable_infinite = get_main_playlist_config('enable_infinite_scroll')
                else:
                    item_height = 60
                    total_songs = len(self.main_playlist)
                    enable_infinite = True
                
                # Toujours utiliser une région de scroll virtuelle basée sur le nombre total de musiques
                # Cela permet d'avoir une scrollbar qui représente correctement la taille totale
                virtual_height = total_songs * item_height
                self.playlist_canvas.configure(scrollregion=(0, 0, 0, virtual_height))
                
                # Calculer la position virtuelle des éléments chargés
                if (USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading') and 
                    hasattr(self, '_last_window_start') and hasattr(self, '_last_window_end')):
                    
                    start_index = getattr(self, '_last_window_start', 0)
                    end_index = getattr(self, '_last_window_end', children_count)
                    
                    # Calculer la position virtuelle des éléments chargés
                    start_position = start_index / total_songs if total_songs > 0 else 0
                    end_position = end_index / total_songs if total_songs > 0 else 1
                    
                    print(f"DEBUG: Scroll region virtuelle: {virtual_height}px pour {total_songs} musiques totales")
                    print(f"DEBUG: Éléments chargés: {children_count} ({start_index}-{end_index}), position virtuelle: {start_position:.3f}-{end_position:.3f}")
                else:
                    print(f"DEBUG: Scroll region virtuelle: {virtual_height}px pour {total_songs} musiques ({children_count} affichées)")
                
                # Configurer le système de scroll (infini classique OU progressif)
                if USE_NEW_CONFIG and get_main_playlist_config('enable_progressive_loading'):
                    self._setup_progressive_scroll_detection()
                elif enable_infinite:
                    self._setup_infinite_scroll()
            else:
                # Pas d'enfants, réinitialiser la région de scroll
                self.playlist_canvas.configure(scrollregion=(0, 0, 0, 0))
                print(f"DEBUG: Aucun élément, région de scroll réinitialisée")
            
            # Restaurer la position de scroll si demandé
            if preserve_position and current_scroll_position is not None:
                try:
                    # Attendre un peu pour que la nouvelle région de scroll soit appliquée
                    self.root.after(10, lambda pos=current_scroll_position: self.playlist_canvas.yview_moveto(pos))
                    print(f"DEBUG: Position de scroll restaurée à {current_scroll_position:.3f}")
                except Exception as e:
                    print(f"DEBUG: Erreur restauration position scroll: {e}")
                    
        except Exception as e:
            print(f"DEBUG: Erreur mise à jour région de scroll: {e}")
            import traceback
            traceback.print_exc()

def _setup_infinite_scroll(self):
        """Configure le scroll infini pour charger plus d'éléments"""
        try:
            if not hasattr(self, 'playlist_canvas'):
                return
            
            # Initialiser les variables de state pour le scroll intelligent
            self._user_is_scrolling = False
            self._user_scroll_timer = None
            self._last_current_index = getattr(self, 'current_index', 0)
            self._auto_centering = False  # Flag pour éviter les boucles
            
            # Binding pour détecter les changements de position de scroll
            # self.playlist_canvas.bind('<Configure>', self._on_playlist_canvas_configure)
            
            # IMPORTANT: Binding pour détecter les changements de position de scroll
            # C'est ce qui manquait pour synchroniser l'affichage avec la position de scroll
            def on_scroll_position_change(*args):
                """Appelée quand la position de scroll change par la souris"""
                # self._update_display_based_on_scroll_position()
                print('on_scroll_position_change appelé')
            
            # Connecter le callback à la scrollbar
            if hasattr(self, 'playlist_scrollbar') and self.playlist_scrollbar:
                self.playlist_scrollbar.config(command=lambda *args: [
                    self.playlist_canvas.yview(*args),
                    on_scroll_position_change()
                ])
            
            # Aussi connecter au canvas directement
            # self.playlist_canvas.bind('<MouseWheel>', self._on_scroll_with_update)
            # self.playlist_canvas.bind('<Button-4>', self._on_scroll_with_update)  # Linux
            # self.playlist_canvas.bind('<Button-5>', self._on_scroll_with_update)  # Linux
                
        except Exception as e:
            print(f"Erreur lors de la configuration du scroll infini: {e}")

# def _on_scroll_with_update(self, event):
#         """Gère le scroll avec mise à jour de l'affichage"""
#         try:
#             print('scroooolll')
#             # Marquer que l'utilisateur est en train de scroller (sauf si c'est un auto-centering)
#             if not getattr(self, '_auto_centering', False):
#                 self._mark_user_scrolling()
            
#             # Appeler d'abord le scroll normal
#             if hasattr(self, '_on_mousewheel'):
#                 self._on_mousewheel(event, self.playlist_canvas)
            
#             # Puis mettre à jour l'affichage basé sur la nouvelle position
#             self.root.after(50, self._update_display_based_on_scroll_position)
            
#             # Déclencher le smart reload si la position de vue a significativement changé
#             self.root.after(100, self._check_smart_reload_on_scroll)
            
#         except Exception as e:
#             if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
#                 print(f"Erreur lors du scroll avec mise à jour: {e}")

def _update_display_based_on_scroll_position(self):
        """Met à jour l'affichage des musiques basé sur la position de scroll"""
        try:
            if not (hasattr(self, 'playlist_canvas') and self.playlist_canvas.winfo_exists()):
                return
            
            if not (USE_NEW_CONFIG and get_main_playlist_config('enable_infinite_scroll')):
                return
            
            # Obtenir la position actuelle du scroll (0.0 à 1.0)
            try:
                scroll_top, scroll_bottom = self.playlist_canvas.yview()
            except:
                return
            
            # Calculer quelle partie de la playlist devrait être visible
            total_songs = len(self.main_playlist)
            if total_songs == 0:
                return
            
            # Convertir la position de scroll en index de musique
            # scroll_top = 0.0 → première musique
            # scroll_top = 1.0 → dernière musique
            center_index = int(scroll_top * (total_songs - 1))
            center_index = max(0, min(center_index, total_songs - 1))
            
            # Calculer la nouvelle fenêtre d'affichage
            songs_before = get_main_playlist_config('songs_before_current') if USE_NEW_CONFIG else 10
            songs_after = get_main_playlist_config('songs_after_current') if USE_NEW_CONFIG else 10
            
            new_start = max(0, center_index - songs_before)
            new_end = min(total_songs, center_index + songs_after + 1)
            
            # Vérifier si on doit mettre à jour l'affichage
            current_start = getattr(self, '_last_window_start', -1)
            current_end = getattr(self, '_last_window_end', -1)
            
            # Seuil pour éviter les mises à jour trop fréquentes
            threshold = 5  # Mettre à jour seulement si on a bougé de plus de 5 éléments
            
            if (abs(new_start - current_start) > threshold or 
                abs(new_end - current_end) > threshold or
                current_start == -1):
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Mise à jour affichage: scroll={scroll_top:.3f}, center={center_index}, fenêtre={new_start}-{new_end}")
                
                # Mettre à jour l'affichage avec la nouvelle fenêtre
                self._update_windowed_display(new_start, new_end, center_index)
                
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur lors de la mise à jour basée sur le scroll: {e}")

def _update_windowed_display(self, start_index, end_index, center_index):
        """Met à jour l'affichage avec une nouvelle fenêtre"""
        try:
            # Sauvegarder les nouveaux paramètres de fenêtre
            self._last_window_start = start_index
            self._last_window_end = end_index
            
            # Vider le container actuel
            for child in self.playlist_container.winfo_children():
                child.destroy()
            
            # Ajouter les nouveaux éléments
            for i in range(start_index, end_index):
                if i < len(self.main_playlist):
                    filepath = self.main_playlist[i]
                    self._add_main_playlist_item(filepath, song_index=i)
            
            # Remettre en surbrillance la chanson en cours si elle est visible
            if (hasattr(self, 'current_index') and 
                start_index <= self.current_index < end_index):
                try:
                    # Trouver le frame correspondant à current_index
                    children = self.playlist_container.winfo_children()
                    relative_index = self.current_index - start_index
                    if 0 <= relative_index < len(children):
                        self.select_playlist_item(children[relative_index], auto_scroll=False)
                except:
                    pass
            
            # Mettre à jour la région de scroll en préservant la position
            self._update_scroll_region_after_unload()
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'affichage fenêtré: {e}")

def _mark_user_scrolling(self):
        """Marque que l'utilisateur est en train de scroller manuellement"""
        try:
            print("_mark_user_scrolling est appelé")
            if not (USE_NEW_CONFIG and get_main_playlist_config('detect_manual_scroll')):
                return
            
            self._user_is_scrolling = True
            
            # Annuler le timer précédent s'il existe
            if self._user_scroll_timer:
                self.root.after_cancel(self._user_scroll_timer)
            
            # Programmer un nouveau timer
            timeout = get_main_playlist_config('user_scroll_timeout') if USE_NEW_CONFIG else 3000
            self._user_scroll_timer = self.root.after(timeout, self._on_user_scroll_timeout)
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print("Utilisateur scroll manuellement détecté")
                
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur lors du marquage du scroll utilisateur: {e}")

def _on_user_scroll_timeout(self):
        """Appelée quand l'utilisateur a fini de scroller"""
        try:
            self._user_is_scrolling = False
            self._user_scroll_timer = None
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print("Fin du scroll utilisateur détectée")
            
            # Vérifier si on doit recentrer sur la chanson courante
            if USE_NEW_CONFIG and get_main_playlist_config('auto_center_on_song_change'):
                self._check_and_recenter_if_needed()
                
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur lors du timeout de scroll: {e}")

def _check_and_recenter_if_needed(self):
        """Vérifie si on doit recentrer sur la chanson courante"""
        try:
            print("_check_and_recenter_if_needed est appelé")
            if not hasattr(self, 'current_index'):
                return
            
            # Vérifier si la chanson courante a changé
            current_index = self.current_index
            last_index = getattr(self, '_last_current_index', current_index)
            
            if current_index != last_index:
                # La chanson a changé, décider si on doit recentrer
                if self._should_recenter_on_song_change():
                    self._auto_center_on_current_song()
                
                # Mettre à jour l'index de référence
                self._last_current_index = current_index
                
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur lors de la vérification de recentrage: {e}")

def _should_recenter_on_song_change(self):
        """Détermine si on doit recentrer sur la nouvelle chanson courante"""
        try:
            if not (USE_NEW_CONFIG and get_main_playlist_config('auto_center_on_song_change')):
                return False
            
            # Si l'utilisateur n'a pas scrollé ou a fini de scroller
            if not self._user_is_scrolling:
                return True
            
            # Si l'option "garder position utilisateur" est désactivée
            if not get_main_playlist_config('keep_user_position'):
                return True
            
            return False
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur lors de la décision de recentrage: {e}")
            return True  # Par défaut, recentrer

def _auto_center_on_current_song(self):
        """Recentre automatiquement l'affichage sur la chanson courante"""
        try:
            if not hasattr(self, 'current_index') or self._auto_centering:
                return
            
            current_index = self.current_index
            total_songs = len(self.main_playlist)
            
            if not (0 <= current_index < total_songs):
                return
            
            # Marquer qu'on fait un auto-centering pour éviter de déclencher le scroll utilisateur
            self._auto_centering = True
            
            # Calculer la nouvelle fenêtre centrée sur la chanson courante
            songs_before = get_main_playlist_config('songs_before_current') if USE_NEW_CONFIG else 10
            songs_after = get_main_playlist_config('songs_after_current') if USE_NEW_CONFIG else 10
            
            new_start = max(0, current_index - songs_before)
            new_end = min(total_songs, current_index + songs_after + 1)
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Auto-recentrage sur chanson {current_index}, fenêtre {new_start}-{new_end}")
            
            # Mettre à jour l'affichage
            self._update_windowed_display(new_start, new_end, current_index)
            
            # Calculer la position de scroll pour centrer la chanson courante
            if total_songs > 1:
                scroll_position = current_index / (total_songs - 1)
                scroll_position = max(0.0, min(1.0, scroll_position))
                
                # Appliquer la position de scroll
                self.playlist_canvas.yview_moveto(scroll_position)
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Scroll positionné à {scroll_position:.3f}")
            
            # DÉSACTIVÉ: Déchargement automatique après recentrage
            # Le déchargement ne se fait que lors du chargement de nouvelles musiques ou après "find"
            
            # Marquer qu'on a fini l'auto-centering
            self.root.after(100, lambda: setattr(self, '_auto_centering', False))
                
        except Exception as e:
            self._auto_centering = False
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur lors de l'auto-recentrage: {e}")

def _calculate_smart_window(self):
        """Calcule la fenêtre intelligente à garder chargée"""
        try:
            if not (USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading')):
                return None, None
            
            total_songs = len(self.main_playlist)
            if total_songs == 0:
                return 0, 0
            
            current_index = getattr(self, 'current_index', 0)
            current_index = max(0, min(current_index, total_songs - 1))
            
            # Zone 1: Autour de la chanson courante (garantie 10+1+10)
            songs_before = get_main_playlist_config('songs_before_current')
            songs_after = get_main_playlist_config('songs_after_current')
            
            current_start = max(0, current_index - songs_before)
            current_end = min(total_songs, current_index + songs_after + 1)
            
            # Zone 2: Autour de la position de vue utilisateur
            view_center = self._get_current_view_position()
            if view_center is not None:
                view_buffer = get_main_playlist_config('keep_buffer_around_view')
                view_start = max(0, view_center - view_buffer)
                view_end = min(total_songs, view_center + view_buffer + 1)
            else:
                view_start, view_end = current_start, current_end
            
            # Si la distance entre vue et courante est très grande, privilégier des zones séparées
            distance_view_current = abs(view_center - current_index) if view_center is not None else 0
            max_union_distance = 100  # Distance max pour faire l'union
            
            if distance_view_current <= max_union_distance:
                # Distance raisonnable : faire l'union des deux zones
                smart_start = min(current_start, view_start)
                smart_end = max(current_end, view_end)
                
                # Ajouter un buffer supplémentaire autour de la chanson courante
                buffer_current = get_main_playlist_config('keep_buffer_around_current')
                buffered_start = max(0, current_index - buffer_current)
                buffered_end = min(total_songs, current_index + buffer_current + 1)
                
                # Union finale
                final_start = min(smart_start, buffered_start)
                final_end = max(smart_end, buffered_end)
            else:
                # Distance trop grande : privilégier seulement la zone de la chanson courante
                buffer_current = get_main_playlist_config('keep_buffer_around_current')
                final_start = max(0, current_index - buffer_current)
                final_end = min(total_songs, current_index + buffer_current + 1)
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Distance trop grande ({distance_view_current}), privilégiant zone courante seulement")
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Fenêtre intelligente calculée: {final_start}-{final_end} (courante: {current_index}, vue: {view_center})")
            
            return final_start, final_end
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur calcul fenêtre intelligente: {e}")
            return None, None

def _get_current_view_position(self):
        """Détermine la position centrale de ce que voit l'utilisateur"""
        try:
            if not hasattr(self, 'playlist_canvas') or not self.playlist_canvas.winfo_exists():
                return None
            
            # Obtenir la position de scroll actuelle
            try:
                scroll_top, scroll_bottom = self.playlist_canvas.yview()
                scroll_center = (scroll_top + scroll_bottom) / 2
            except:
                return None
            
            # Convertir en index de musique
            total_songs = len(self.main_playlist)
            if total_songs <= 1:
                return 0
            
            # scroll_center = 0.0 → première musique, 1.0 → dernière musique
            view_index = int(scroll_center * (total_songs - 1))
            view_index = max(0, min(view_index, total_songs - 1))
            
            return view_index
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur détection position vue: {e}")
            return None

def _smart_load_unload(self):
        """SYSTÈME HYBRIDE : Ancien système OU nouveau système progressif selon la config"""
        try:
            # Nouveau système progressif activé ?
            if USE_NEW_CONFIG and get_main_playlist_config('enable_progressive_loading'):
                return self._progressive_load_system()
            
            # Ancien système fenêtré (si encore activé)
            if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading'):
                return self._old_smart_load_system()
                
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur système de chargement: {e}")

def _progressive_load_system(self):
        """NOUVEAU SYSTÈME : Chargement progressif avec déchargement intelligent"""
        try:
            if not self.main_playlist:
                return
                
            current_index = getattr(self, 'current_index', 0)
            total_songs = len(self.main_playlist)
            
            # Sécurité: Index valide
            current_index = max(0, min(current_index, total_songs - 1))
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"🎵 PROGRESSIVE LOAD: Position courante {current_index}")
                
            # Vérifier ce qui est déjà chargé
            currently_loaded = len(self.playlist_container.winfo_children()) if hasattr(self, 'playlist_container') else 0
            
            # DÉSACTIVÉ: Déchargement automatique dans progressive load
            # Le déchargement ne se fait que lors du chargement de nouvelles musiques ou après "find"
            
            # Vérifier si la musique actuelle est visible
            current_song_visible = self._is_index_already_loaded(current_index)
            
            if not current_song_visible:
                # La musique actuelle n'est pas visible, charger autour d'elle
                items_before = 2  # Charger 2 musiques avant
                items_after = 3   # Charger 3 musiques après
                
                start_index = max(0, current_index - items_before)
                end_index = min(total_songs, current_index + items_after + 1)
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"🎯 Musique actuelle {current_index} non visible, chargement {start_index}-{end_index-1}")
                
                # Effacer tout et recharger autour de la musique actuelle
                self._clear_playlist_display()
                self._append_progressive_items(start_index, end_index)
                
                # Mettre à jour les paramètres de fenêtre
                self._last_window_start = start_index
                self._last_window_end = end_index
                
                return
            
            # Si la musique actuelle est visible, ne rien faire sauf si on scroll en bas
            if currently_loaded == 0:
                # Premier chargement : autour de la chanson courante
                items_before = 2
                items_after = 3
                start_from = max(0, current_index - items_before)
                target_end = min(total_songs, current_index + items_after + 1)
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"🆕 Premier chargement autour de la musique actuelle: {start_from} à {target_end-1}")
                
                self._append_progressive_items(start_from, target_end)
                
                # Mettre à jour les paramètres de fenêtre
                self._last_window_start = start_from
                self._last_window_end = target_end
            else:
                # Ne charger que si on scroll en bas (géré par _check_infinite_scroll)
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"✅ Musique actuelle {current_index} visible, pas de chargement supplémentaire")
                return
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur chargement progressif: {e}")

def _old_smart_load_system(self):
        """Ancien système fenêtré 10+1+10 (conservé pour compatibilité)"""
        try:
            if not self.main_playlist:
                return
                
            current_index = getattr(self, 'current_index', 0)
            total_songs = len(self.main_playlist)
            current_index = max(0, min(current_index, total_songs - 1))
            
            songs_before = get_main_playlist_config('songs_before_current') 
            songs_after = get_main_playlist_config('songs_after_current')
            
            target_start = max(0, current_index - songs_before)
            target_end = min(total_songs, current_index + songs_after + 1)
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"🔄 ANCIEN SYSTÈME: Chanson {current_index}, fenêtre {target_start}-{target_end}")
            
            self._force_reload_window(target_start, target_end)
            self._last_window_start = target_start
            self._last_window_end = target_end
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur ancien système: {e}")
                
def _get_last_loaded_index(self):
        """Trouve le dernier index chargé dans la playlist"""
        try:
            children = self.playlist_container.winfo_children()
            if not children:
                return getattr(self, 'current_index', 0)
                
            max_index = 0
            for child in children:
                if hasattr(child, 'song_index'):
                    max_index = max(max_index, child.song_index)
                    
            return max_index + 1
            
        except Exception:
            return getattr(self, 'current_index', 0)
            
def _append_progressive_items(self, start_index, end_index):
        """Ajoute des éléments progressivement SANS supprimer les existants"""
        try:
            print(f"DEBUG: _append_progressive_items appelé pour {start_index} à {end_index-1}")
            
            if start_index >= end_index or start_index >= len(self.main_playlist):
                print(f"DEBUG: Indices invalides: start={start_index}, end={end_index}, len={len(self.main_playlist)}")
                return
                
            loaded_count = 0
            
            # Forcer la mise à jour du cache des index chargés
            try:
                self._invalidate_loaded_indexes_cache()
            except Exception as e:
                print(f"DEBUG: Erreur invalidation cache: {e}")
                # Créer le cache s'il n'existe pas
                self._loaded_indexes_cache = set()
            
            # Vérifier les doublons dans les éléments déjà chargés
            already_loaded_indexes = set()
            for child in self.playlist_container.winfo_children():
                if hasattr(child, 'song_index'):
                    already_loaded_indexes.add(child.song_index)
            
            # Vérifier s'il y a des doublons
            duplicate_count = len(already_loaded_indexes) - len(self.playlist_container.winfo_children())
            if duplicate_count > 0:
                print(f"DEBUG: ATTENTION: {duplicate_count} doublons détectés dans les index chargés!")
                
                # Supprimer les doublons
                index_count = {}
                for child in self.playlist_container.winfo_children():
                    if hasattr(child, 'song_index'):
                        index = child.song_index
                        if index in index_count:
                            index_count[index] += 1
                            # Si c'est un doublon, le supprimer
                            if index_count[index] > 1:
                                print(f"DEBUG: Suppression du doublon pour l'index {index}")
                                child.destroy()
                        else:
                            index_count[index] = 1
                
                # Réinitialiser le cache
                self._invalidate_loaded_indexes_cache()
            
            # Vérifier si l'index actuel est dans la plage à charger
            current_index = getattr(self, 'current_index', 0)
            if current_index >= start_index and current_index < end_index:
                print(f"DEBUG: L'index actuel {current_index} est dans la plage à charger")
                # S'assurer que l'index actuel est chargé en priorité
                if not self._is_index_already_loaded(current_index):
                    try:
                        filepath = self.main_playlist[current_index]
                        print(f"DEBUG: Chargement prioritaire de l'élément actuel {current_index}: {os.path.basename(filepath)}")
                        self._add_main_playlist_item(filepath, song_index=current_index)
                        loaded_count += 1
                        # Ajouter au cache
                        if hasattr(self, '_loaded_indexes_cache') and self._loaded_indexes_cache is not None:
                            self._loaded_indexes_cache.add(current_index)
                            print(f"DEBUG: Index actuel {current_index} ajouté au cache")
                    except Exception as e:
                        print(f"DEBUG: Erreur chargement item actuel {current_index}: {e}")
                        import traceback
                        traceback.print_exc()
            
            # Collecter tous les éléments à charger (sauf l'index actuel déjà chargé)
            items_to_load = []
            for i in range(start_index, min(end_index, len(self.main_playlist))):
                if i != current_index and not self._is_index_already_loaded(i):
                    items_to_load.append(i)
            
            # Trier les éléments par index pour maintenir l'ordre
            items_to_load.sort()
            
            # Charger les éléments dans l'ordre
            for i in items_to_load:
                filepath = self.main_playlist[i]
                try:
                    print(f"DEBUG: Chargement de l'élément {i}: {os.path.basename(filepath)}")
                    
                    # Déterminer où insérer l'élément pour maintenir l'ordre
                    insert_position = self._find_insert_position(i)
                    frame = self._add_main_playlist_item_ordered(filepath, song_index=i, insert_position=insert_position)
                    
                    if frame:
                        loaded_count += 1
                        # Ajouter au cache pour éviter les doublons dans cette même session
                        if hasattr(self, '_loaded_indexes_cache') and self._loaded_indexes_cache is not None:
                            self._loaded_indexes_cache.add(i)
                            print(f"DEBUG: Index {i} ajouté au cache")
                except Exception as e:
                    print(f"DEBUG: Erreur chargement item {i}: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"DEBUG: {loaded_count} nouveaux éléments chargés ({start_index}-{end_index-1})")
            total_loaded = len(self.playlist_container.winfo_children())
            print(f"DEBUG: Total chargé: {total_loaded}/{len(self.main_playlist)}")
            
            # Vérifier si l'index actuel est maintenant chargé
            if self._is_index_already_loaded(current_index):
                print(f"DEBUG: L'index actuel {current_index} est maintenant chargé")
            else:
                print(f"DEBUG: ATTENTION: L'index actuel {current_index} n'est toujours pas chargé!")
                # Forcer le chargement de l'index actuel
                if current_index < len(self.main_playlist):
                    try:
                        filepath = self.main_playlist[current_index]
                        print(f"DEBUG: Forçage du chargement de l'élément actuel {current_index}: {os.path.basename(filepath)}")
                        self._add_main_playlist_item(filepath, song_index=current_index)
                        # Ajouter au cache
                        if hasattr(self, '_loaded_indexes_cache') and self._loaded_indexes_cache is not None:
                            self._loaded_indexes_cache.add(current_index)
                    except Exception as e:
                        print(f"DEBUG: Erreur forçage chargement item actuel {current_index}: {e}")
                        import traceback
                        traceback.print_exc()
            
            # Invalider le cache après avoir ajouté des éléments
            try:
                self._invalidate_loaded_indexes_cache()
            except Exception as e:
                print(f"DEBUG: Erreur invalidation cache final: {e}")
                
        except Exception as e:
            print(f"DEBUG: Erreur append progressif: {e}")
            import traceback
            traceback.print_exc()
                
def _is_index_already_loaded(self, index):
        """Vérifie si un index spécifique est déjà chargé"""
        try:
            # Vérification directe (plus fiable que le cache)
            children = self.playlist_container.winfo_children()
            for child in children:
                if hasattr(child, 'song_index') and child.song_index == index:
                    print(f"DEBUG: Index {index} trouvé directement dans les éléments chargés")
                    return True
            
            # Si on n'a pas trouvé directement, vérifier dans le cache
            if not hasattr(self, '_loaded_indexes_cache') or self._loaded_indexes_cache is None:
                # Initialiser ou rafraîchir le cache
                self._loaded_indexes_cache = set()
                for child in children:
                    if hasattr(child, 'song_index'):
                        self._loaded_indexes_cache.add(child.song_index)
                print(f"DEBUG: Cache des index chargés initialisé avec {len(self._loaded_indexes_cache)} éléments")
            
            # Vérifier dans le cache
            is_loaded = index in self._loaded_indexes_cache
            print(f"DEBUG: Vérification si index {index} est chargé (via cache): {is_loaded}")
            
            # Si le cache dit que c'est chargé mais qu'on ne l'a pas trouvé directement,
            # c'est que le cache est incorrect
            if is_loaded:
                print(f"DEBUG: ATTENTION: Incohérence détectée - l'index {index} est dans le cache mais pas dans les éléments chargés")
                # Invalider le cache
                self._invalidate_loaded_indexes_cache()
                return False
                
            return is_loaded
        except Exception as e:
            print(f"DEBUG: Erreur vérification index chargé: {e}")
            import traceback
            traceback.print_exc()
            return False
            
def _invalidate_loaded_indexes_cache(self):
        """Invalide le cache des index chargés"""
        if hasattr(self, '_loaded_indexes_cache'):
            print(f"DEBUG: Invalidation du cache des index chargés")
            self._loaded_indexes_cache = None

def _setup_progressive_scroll_detection(self):
        """Configure la détection de scroll pour le chargement progressif"""
        try:
            if not (USE_NEW_CONFIG and get_main_playlist_config('enable_progressive_loading')):
                return
                
            if not (hasattr(self, 'playlist_canvas') and self.playlist_canvas):
                return
            
            # Nous n'utilisons plus de binding direct ici
            # Le chargement progressif est maintenant géré par _check_infinite_scroll
            # qui est appelé après chaque événement de scroll
            
            # Configurer une vérification périodique pour s'assurer que la musique actuelle est chargée
            if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_unloading'):
                self._setup_current_song_check()
                
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur config scroll progressif: {e}")
                
def _setup_current_song_check(self):
        """Configure une vérification périodique pour s'assurer que la musique actuelle est chargée"""
        try:
            # Fonction de vérification périodique
            def check_current_song_loaded():
                try:
                    if hasattr(self, 'current_index') and self.main_playlist:
                        current_index = self.current_index
                        if 0 <= current_index < len(self.main_playlist):
                            # Vérifier si la musique actuelle est chargée
                            if not self._is_index_already_loaded(current_index):
                                # Forcer le chargement/déchargement
                                self._check_and_unload_items(current_index)
                            
                            # DÉSACTIVÉ: Chargement automatique de la musique suivante
                            # Cette logique est désactivée pour éviter le chargement automatique
                            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                                print(f"DEBUG: Chargement automatique de la musique suivante désactivé")
                except Exception as e:
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"❌ Erreur vérification musique courante: {e}")
                
                # Reprogrammer la vérification
                if hasattr(self, 'root') and self.root.winfo_exists():
                    self.root.after(2000, check_current_song_loaded)  # Vérifier toutes les 2 secondes
            
            # Démarrer la vérification périodique
            self.root.after(2000, check_current_song_loaded)
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur configuration vérification musique courante: {e}")

def _on_progressive_scroll(self, event=None):
        """Gère le scroll pour le chargement progressif"""
        try:
            if not (USE_NEW_CONFIG and get_main_playlist_config('enable_progressive_loading')):
                return
            
            # Vérifier la position de scroll
            try:
                # Obtenir la position de scroll actuelle (0.0 = haut, 1.0 = bas)
                scroll_top, scroll_bottom = self.playlist_canvas.yview()
                scroll_position = scroll_bottom  # Position vers le bas
                
                # Seuil de déclenchement (90% vers le bas par défaut)
                threshold = get_main_playlist_config('scroll_trigger_threshold')
                
                # Si on atteint le seuil, charger plus d'éléments
                if scroll_position >= threshold:
                    self._load_more_on_scroll()
                    
            except Exception:
                pass
                
        except Exception:
            pass

def _load_more_on_scroll(self):
        """DÉSACTIVÉ - Charge plus d'éléments quand on scroll vers le bas"""
        # Cette fonction est désactivée pour éviter le chargement automatique
        # Le chargement est maintenant géré uniquement par _check_infinite_scroll
        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
            print("DEBUG: _load_more_on_scroll désactivé - utiliser _check_infinite_scroll")
        return
        
        try:
            if not self.main_playlist:
                return
                
            # Trouver le dernier élément chargé
            last_loaded = self._get_last_loaded_index() - 1  # -1 car get_last_loaded_index retourne l'index suivant
            total_songs = len(self.main_playlist)
            
            # Si on a déjà tout chargé, vérifier si on doit charger depuis le début (boucle)
            if last_loaded >= total_songs - 1:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print("🔄 Fin de playlist atteinte, chargement depuis le début")
                
                # Charger depuis le début de la playlist (boucle)
                load_more_count = get_main_playlist_config('load_more_on_scroll')
                
                # Vérifier si les premiers éléments sont déjà chargés
                first_loaded = False
                for i in range(min(load_more_count, total_songs)):
                    if self._is_index_already_loaded(i):
                        first_loaded = True
                        break
                
                # Si les premiers éléments ne sont pas chargés, les charger
                if not first_loaded:
                    self._append_progressive_items(0, load_more_count)
                    
                    # Définir un flag pour indiquer qu'on a chargé depuis le début
                    self._scrolling_below_current = True
                    
                    # Vérifier si on doit décharger des éléments (trop d'éléments chargés)
                    current_index = getattr(self, 'current_index', 0)
                    if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_unloading'):
                        self._check_and_unload_items(current_index)
                    
                    # Sauvegarder la position de scroll actuelle
                    try:
                        scroll_top, scroll_bottom = self.playlist_canvas.yview()
                        print(f"DEBUG: Position de scroll avant mise à jour: {scroll_top:.3f}")
                        
                        # Mettre à jour la région de scroll et restaurer la position
                        self.root.after(10, lambda pos=scroll_top: self._update_canvas_scroll_region_and_restore(pos))
                    except Exception as e:
                        print(f"DEBUG: Erreur sauvegarde position scroll: {e}")
                        # Fallback
                        self.root.after(10, lambda: self._update_canvas_scroll_region(preserve_position=True))
                    
                return
            
            # Calculer combien charger de plus
            load_more_count = get_main_playlist_config('load_more_on_scroll')
            start_from = last_loaded + 1
            end_at = min(total_songs, start_from + load_more_count)
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"📈 SCROLL LOAD MORE: Charger {start_from} à {end_at-1} (+{end_at-start_from} musiques)")
            
            # Charger les éléments supplémentaires
            self._append_progressive_items(start_from, end_at)
            
            # Définir un flag pour indiquer que l'utilisateur scrolle vers le bas
            # Ce flag sera utilisé par _check_and_unload_items pour prioriser le déchargement
            # des éléments avant la musique actuelle
            current_index = getattr(self, 'current_index', 0)
            if start_from > current_index:
                # L'utilisateur scrolle en dessous de la musique actuelle
                self._scrolling_below_current = True
            else:
                self._scrolling_below_current = False
            
            # Vérifier si on doit décharger des éléments (trop d'éléments chargés)
            if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_unloading'):
                self._check_and_unload_items(current_index)
            
            # Mettre à jour la région de scroll pour refléter les nouveaux éléments en préservant la position
            self._update_scroll_region_after_unload()
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur chargement supplémentaire: {e}")

def _update_scroll_region_after_unload(self):
        """Met à jour la région de scroll après le déchargement d'éléments"""
        try:
            # Sauvegarder la position de scroll actuelle
            scroll_top, scroll_bottom = self.playlist_canvas.yview()
            print(f"DEBUG: Position de scroll avant déchargement: {scroll_top:.3f}")
            
            # Mettre à jour la région de scroll et restaurer la position
            self.root.after(10, lambda pos=scroll_top: self._update_canvas_scroll_region_and_restore(pos))
        except Exception as e:
            print(f"DEBUG: Erreur sauvegarde position scroll: {e}")
            # Fallback
            self.root.after(10, lambda: self._update_canvas_scroll_region(preserve_position=True))
            
def _check_and_unload_items(self, current_index):
        """Décharge intelligemment selon les critères :
        - Décharge toutes les musiques avant la musique actuelle
        - SAUF si l'utilisateur regarde au-dessus, alors on garde quelques musiques au-dessus
        """
        try:
            if not (USE_NEW_CONFIG and get_main_playlist_config('enable_smart_unloading')):
                return
                
            print(f"DEBUG: _check_and_unload_items appelé pour index {current_index}")
                
            # Obtenir les widgets actuellement chargés
            children = self.playlist_container.winfo_children()
            if not children:
                return
                
            # Déterminer si l'utilisateur regarde au-dessus de la musique actuelle
            user_looking_above = self._is_user_looking_above_current(current_index)
            
            # Si on vient d'utiliser le bouton find, forcer le déchargement des musiques avant
            just_used_find = getattr(self, '_just_used_find_button', False)
            if just_used_find:
                print(f"DEBUG: Bouton find utilisé, déchargement forcé des musiques avant la musique actuelle")
                user_looking_above = False  # Forcer le déchargement même si l'utilisateur regarde au-dessus
                self._just_used_find_button = False  # Réinitialiser le flag
            
            # Collecter les widgets à décharger
            widgets_to_unload = []
            
            for widget in children:
                if hasattr(widget, 'song_index'):
                    widget_index = widget.song_index
                    
                    if widget_index < current_index:
                        # Musique avant la musique actuelle
                        if user_looking_above:
                            # L'utilisateur regarde au-dessus, garder quelques musiques au-dessus
                            keep_above = 3  # Garder 3 musiques au-dessus
                            if widget_index < current_index - keep_above:
                                widgets_to_unload.append(widget)
                                print(f"DEBUG: Déchargement de l'élément {widget_index} (trop loin au-dessus)")
                        else:
                            # L'utilisateur ne regarde pas au-dessus, décharger toutes les musiques avant
                            widgets_to_unload.append(widget)
                            print(f"DEBUG: Déchargement de l'élément {widget_index} (avant la musique actuelle)")
            
            # Décharger les widgets sélectionnés
            if widgets_to_unload:
                unload_count = len(widgets_to_unload)
                print(f"DEBUG: Déchargement de {unload_count} éléments (utilisateur regarde au-dessus: {user_looking_above})")
                
                for widget in widgets_to_unload:
                    if widget.winfo_exists():
                        widget.destroy()
                        
                # Invalider le cache des index chargés
                try:
                    self._invalidate_loaded_indexes_cache()
                except Exception as e:
                    print(f"DEBUG: Erreur invalidation cache: {e}")
                    self._loaded_indexes_cache = set()
            else:
                print(f"DEBUG: Aucun élément à décharger")
                
        except Exception as e:
            print(f"DEBUG: Erreur déchargement intelligent: {e}")
            import traceback
            traceback.print_exc()

def _is_user_looking_above_current(self, current_index):
        """Détermine si l'utilisateur regarde au-dessus de la musique actuelle"""
        try:
            # Obtenir la position de scroll actuelle
            scroll_top, scroll_bottom = self.playlist_canvas.yview()
            
            # Estimer l'index du premier élément visible
            total_items = len(self.main_playlist)
            if total_items == 0:
                return False
                
            visible_start_index = int(scroll_top * total_items)
            visible_end_index = int(scroll_bottom * total_items)
            
            # L'utilisateur regarde au-dessus si la zone visible est principalement au-dessus de la musique actuelle
            if visible_end_index < current_index:
                print(f"DEBUG: Utilisateur regarde au-dessus (visible: {visible_start_index}-{visible_end_index}, actuel: {current_index})")
                return True
            elif visible_start_index < current_index and visible_end_index >= current_index:
                # La musique actuelle est partiellement visible, vérifier si l'utilisateur regarde plutôt vers le haut
                middle_visible = (visible_start_index + visible_end_index) / 2
                if middle_visible < current_index:
                    print(f"DEBUG: Utilisateur regarde plutôt au-dessus (milieu visible: {middle_visible:.1f}, actuel: {current_index})")
                    return True
            
            print(f"DEBUG: Utilisateur ne regarde pas au-dessus (visible: {visible_start_index}-{visible_end_index}, actuel: {current_index})")
            return False
            
        except Exception as e:
            print(f"DEBUG: Erreur détection regard utilisateur: {e}")
            return False

def _force_reload_window(self, start_index, end_index):
        """Force le rechargement d'une fenêtre spécifique - PROTECTION INDEX"""
        try:
            # SÉCURITÉ : Valider les paramètres d'entrée
            if not self.main_playlist:
                return
                
            total_songs = len(self.main_playlist)
            
            # Protection absolue contre les index invalides
            start_index = max(0, min(start_index, total_songs))
            end_index = max(start_index, min(end_index, total_songs))
            
            if start_index < 0 or end_index < 0 or start_index >= total_songs:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"❌ ABORT FORCE RELOAD: Index invalides {start_index}-{end_index} (total: {total_songs})")
                return
            
            if start_index >= end_index:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"❌ ABORT FORCE RELOAD: Fenêtre vide {start_index}-{end_index}")
                return
                
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"🔥 FORCE RELOAD SÉCURISÉ: {start_index}-{end_index} (total: {total_songs})")
                
            # Étape 1: DÉCHARGER TOUT (vider complètement)
            try:
                children = self.playlist_container.winfo_children()
                decharges = 0
                for widget in children:
                    try:
                        if widget.winfo_exists():
                            widget.destroy()
                            decharges += 1
                    except tk.TclError:
                        continue
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"✅ {decharges} éléments déchargés")
                    
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"⚠️ Erreur déchargement: {e}")
            
            # Étape 2: RECHARGER la fenêtre cible avec vérifications
            charges = 0
            for i in range(start_index, end_index):
                # Double vérification de sécurité
                if 0 <= i < len(self.main_playlist):
                    filepath = self.main_playlist[i]
                    try:
                        self._add_main_playlist_item(filepath, song_index=i)
                        charges += 1
                    except Exception as e:
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            print(f"⚠️ Erreur chargement item {i}: {e}")
                elif USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"⚠️ Index {i} hors limites, ignoré")
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"✅ {charges} éléments rechargés")
                non_charges = len(self.main_playlist) - charges
                if non_charges > 0:
                    print(f"🎯 {non_charges} éléments NON chargés (optimisation mémoire)")
            
            # Étape 3: Remettre en surbrillance la chanson courante
            self._highlight_current_song_in_window(start_index, end_index)
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur force reload: {e}")

def _highlight_current_song_in_window(self, start_index, end_index):
        """Remet en surbrillance la chanson courante si elle est dans la fenêtre"""
        try:
            current_index = getattr(self, 'current_index', 0)
            
            if start_index <= current_index < end_index:
                widgets = self.playlist_container.winfo_children()
                relative_index = current_index - start_index
                
                if 0 <= relative_index < len(widgets):
                    widget = widgets[relative_index]
                    if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                        self.select_playlist_item(widget, auto_scroll=False)
                        
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            print(f"✅ Chanson courante ({current_index}) remise en surbrillance")
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"⚠️ Erreur highlight: {e}")

def _unload_unused_items(self, target_start, target_end, current_start, current_end):
        """Décharge les éléments qui ne sont plus nécessaires"""
        try:
            if current_start == -1 or current_end == -1:
                return  # Pas d'éléments actuellement chargés
            
            unload_threshold = get_main_playlist_config('unload_threshold')
            current_index = getattr(self, 'current_index', 0)
            
            # Trouver les éléments à décharger
            items_to_unload = []
            
            # Éléments avant la nouvelle fenêtre
            if current_start < target_start:
                for i in range(current_start, min(target_start, current_end)):
                    # Ne décharger que si assez loin de la chanson courante
                    distance_from_current = abs(i - current_index)
                    if distance_from_current > unload_threshold:
                        items_to_unload.append(i)
            
            # Éléments après la nouvelle fenêtre
            if current_end > target_end:
                for i in range(max(target_end, current_start), current_end):
                    # Ne décharger que si assez loin de la chanson courante
                    distance_from_current = abs(i - current_index)
                    if distance_from_current > unload_threshold:
                        items_to_unload.append(i)
            
            # Décharger les éléments
            if items_to_unload:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Déchargement de {len(items_to_unload)} éléments: {items_to_unload[:5]}{'...' if len(items_to_unload) > 5 else ''}")
                
                children = self.playlist_container.winfo_children()
                for i, child in enumerate(children):
                    # Calculer l'index réel de cet enfant
                    real_index = current_start + i
                    if real_index in items_to_unload:
                        child.destroy()
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur déchargement: {e}")

def _load_required_items(self, target_start, target_end, current_start, current_end):
        """Charge les nouveaux éléments nécessaires"""
        try:
            # Déterminer quels éléments charger
            items_to_load = []
            
            if current_start == -1 or current_end == -1:
                # Aucun élément chargé, charger toute la fenêtre cible
                items_to_load = list(range(target_start, target_end))
            else:
                # Éléments à ajouter avant
                if target_start < current_start:
                    items_to_load.extend(range(target_start, current_start))
                
                # Éléments à ajouter après
                if target_end > current_end:
                    items_to_load.extend(range(current_end, target_end))
            
            # Charger les nouveaux éléments
            if items_to_load:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Chargement de {len(items_to_load)} nouveaux éléments")
                
                # Vider complètement le container et recharger dans l'ordre
                for child in self.playlist_container.winfo_children():
                    child.destroy()
                
                # Charger tous les éléments dans la nouvelle fenêtre
                for i in range(target_start, target_end):
                    if i < len(self.main_playlist):
                        filepath = self.main_playlist[i]
                        self._add_main_playlist_item(filepath, song_index=i)
                
                # Remettre en surbrillance la chanson courante si visible
                current_index = getattr(self, 'current_index', 0)
                if target_start <= current_index < target_end:
                    try:
                        children = self.playlist_container.winfo_children()
                        relative_index = current_index - target_start
                        if 0 <= relative_index < len(children):
                            self.select_playlist_item(children[relative_index], auto_scroll=False)
                    except:
                        pass
            
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Erreur chargement: {e}")

def _trigger_smart_reload_on_song_change(self):
        """Déclenche le rechargement intelligent lors d'un changement de musique - VERSION DIRECTE"""
        try:
            if not (USE_NEW_CONFIG and get_main_playlist_config('reload_on_song_change')):
                return
            
            if not self.main_playlist:
                return
                
            current_index = getattr(self, 'current_index', 0)
            last_index = getattr(self, '_last_smart_reload_index', current_index)
            
            # Vérifier si la chanson a changé OU forcer si pas encore initialisé
            force_reload = not hasattr(self, '_last_smart_reload_index')
            song_changed = current_index != last_index
            
            if song_changed or force_reload:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    if force_reload:
                        print(f"🚀 PREMIER SMART RELOAD: Initialisation pour chanson {current_index}")
                    else:
                        print(f"🎵 CHANGEMENT MUSIQUE: {last_index} → {current_index}, déclenchement smart reload")
                
                # FORCER le rechargement immédiatement
                self._smart_load_unload()
                
                # Mettre à jour l'index de référence
                self._last_smart_reload_index = current_index
                
                # Forcer la mise à jour de la région de scroll en préservant la position
                self._update_scroll_region_after_unload()
                
            elif USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Pas de changement de musique, pas de smart reload nécessaire")
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur trigger smart reload: {e}")

# def _check_smart_reload_on_scroll(self):
#         """Vérifie si on doit déclencher un smart reload suite au scroll"""
#         try:
#             print("")
#             if not (USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading')):
#                 return
            
#             current_view = self._get_current_view_position()
#             if current_view is None:
#                 return
            
#             last_view = getattr(self, '_last_smart_reload_view', current_view)
            
#             # Déclencher seulement si la vue a bougé de plus de 5 éléments
#             view_threshold = 5
#             if abs(current_view - last_view) > view_threshold:
#                 if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
#                     print(f"Vue changée significativement ({last_view} → {current_view}), smart reload")
                
#                 self._smart_load_unload()
#                 self._last_smart_reload_view = current_view
                
#         except Exception as e:
#             if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
#                 print(f"Erreur check smart reload scroll: {e}")

# def _on_playlist_canvas_configure(self, event):
#         """Appelée quand le canvas de playlist change de taille"""
        
#         try:
#             print("_on_playlist_canvas_configure appelé")
#             # Vérifier si on doit charger plus d'éléments
#             self._check_infinite_scroll()
#         except Exception as e:
#             print(f"Erreur lors de la configuration du canvas: {e}")

def _check_infinite_scroll(self):
        """Vérifie si on doit charger plus d'éléments - SEULEMENT quand nécessaire"""
        try:
            # Optimisation: Éviter les appels trop fréquents
            if hasattr(self, '_last_infinite_check_time'):
                current_time = time.time()
                if current_time - self._last_infinite_check_time < 0.1:  # 100ms entre les vérifications
                    return
                self._last_infinite_check_time = current_time
            else:
                self._last_infinite_check_time = time.time()
            
            if not (hasattr(self, 'playlist_canvas') and self.playlist_canvas.winfo_exists()):
                return
            
            # Vérifier si la musique actuelle est visible
            current_index = getattr(self, 'current_index', 0)
            if not (hasattr(self, 'main_playlist') and self.main_playlist and current_index < len(self.main_playlist)):
                return
                
            # Vérifier si la musique actuelle est chargée
            current_is_loaded = self._is_index_already_loaded(current_index)
            
            # CAS 1: Si la musique actuelle n'est pas chargée, la charger
            if not current_is_loaded:
                print(f"DEBUG: Musique actuelle (index {current_index}) non visible, rechargement")
                # Charger seulement autour de la musique actuelle
                items_before = 2
                items_after = 3
                start_index = max(0, current_index - items_before)
                end_index = min(len(self.main_playlist), current_index + items_after + 1)
                
                print(f"DEBUG: Chargement forcé autour de la musique actuelle ({start_index}-{end_index-1})")
                
                # Effacer tout et recharger autour de la musique actuelle
                self._clear_playlist_display()
                self._append_progressive_items(start_index, end_index)
                
                # Mettre à jour les paramètres de fenêtre
                self._last_window_start = start_index
                self._last_window_end = end_index
                
                return
            
            # CAS 2: Vérifier si on scroll en bas et qu'on a besoin de charger plus
            try:
                scroll_top, scroll_bottom = self.playlist_canvas.yview()
                
                # Charger plus seulement si on est proche du bas (scroll_bottom > 0.9)
                if scroll_bottom > 0.9:
                    print(f"DEBUG: Proche du bas (scroll: {scroll_bottom:.3f}), chargement des éléments suivants")
                    
                    # Obtenir le dernier index chargé
                    last_loaded = self._get_last_loaded_index()
                    if last_loaded is not None and last_loaded < len(self.main_playlist) - 1:
                        # Charger quelques éléments supplémentaires
                        load_more = 5  # Charger 5 éléments de plus
                        end_index = min(len(self.main_playlist), last_loaded + load_more + 1)
                        
                        print(f"DEBUG: Chargement supplémentaire de {last_loaded + 1} à {end_index - 1}")
                        self._append_progressive_items(last_loaded + 1, end_index)
                        
                        # Mettre à jour la fenêtre
                        if hasattr(self, '_last_window_end'):
                            self._last_window_end = end_index
                else:
                    # Pas besoin de charger plus
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"DEBUG: Pas de chargement nécessaire (scroll: {scroll_bottom:.3f})")
                        
            except Exception as e:
                print(f"DEBUG: Erreur vérification scroll: {e}")
                
        except Exception as e:
            print(f"DEBUG: Erreur _check_infinite_scroll: {e}")
            import traceback
            traceback.print_exc()

def _load_more_songs_above(self):
        """Charge plus de musiques au-dessus de la fenêtre actuelle"""
        try:
            if not hasattr(self, '_last_window_start'):
                return
            
            current_start = self._last_window_start
            if current_start <= 0:
                return  # Déjà au début
            
            load_count = get_main_playlist_config('load_more_count') if USE_NEW_CONFIG else 10
            new_start = max(0, current_start - load_count)
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Chargement de {load_count} musiques au-dessus (index {new_start} à {current_start})")
            
            # Étendre la fenêtre vers le haut
            self._extend_window_up(new_start)
            
        except Exception as e:
            print(f"Erreur lors du chargement des musiques au-dessus: {e}")

def _load_more_songs_below(self):
        """Charge plus de musiques en-dessous de la fenêtre actuelle"""
        try:
            if not hasattr(self, '_last_window_end'):
                return
            
            current_end = self._last_window_end
            if current_end >= len(self.main_playlist):
                return  # Déjà à la fin
            
            load_count = get_main_playlist_config('load_more_count') if USE_NEW_CONFIG else 10
            new_end = min(len(self.main_playlist), current_end + load_count)
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"Chargement de {load_count} musiques en-dessous (index {current_end} à {new_end})")
            
            # Étendre la fenêtre vers le bas
            self._extend_window_down(new_end)
            
        except Exception as e:
            print(f"Erreur lors du chargement des musiques en-dessous: {e}")

def _extend_window_up(self, new_start):
        """Étend la fenêtre d'affichage vers le haut"""
        try:
            if not hasattr(self, '_last_window_start') or not hasattr(self, '_last_window_end'):
                return
            
            current_start = self._last_window_start
            current_end = self._last_window_end
            
            # Ajouter les nouveaux éléments au début
            for i in range(new_start, current_start):
                if i < len(self.main_playlist):
                    filepath = self.main_playlist[i]
                    self._add_main_playlist_item_at_position(filepath, song_index=i, position='top')
            
            # Mettre à jour les paramètres de fenêtre
            self._last_window_start = new_start
            
            # Mettre à jour la région de scroll en préservant la position
            self._update_scroll_region_after_unload()
        except Exception as e:
            print(f"Erreur lors de l'extension vers le haut: {e}")

def _extend_window_down(self, new_end):
        """Étend la fenêtre d'affichage vers le bas"""
        try:
            if not hasattr(self, '_last_window_start') or not hasattr(self, '_last_window_end'):
                return
            
            current_start = self._last_window_start
            current_end = self._last_window_end
            
            # Ajouter les nouveaux éléments à la fin
            for i in range(current_end, new_end):
                if i < len(self.main_playlist):
                    filepath = self.main_playlist[i]
                    self._add_main_playlist_item_at_position(filepath, song_index=i, position='bottom')
            
            # Mettre à jour les paramètres de fenêtre
            self._last_window_end = new_end
            
            # Mettre à jour la région de scroll en préservant la position
            self._update_scroll_region_after_unload()
            
        except Exception as e:
            print(f"Erreur lors de l'extension vers le bas: {e}")

def _add_main_playlist_item_at_position(self, filepath, song_index=None, position='bottom'):
        """Ajoute un élément de playlist à une position spécifique (top ou bottom)"""
        try:
            # Pour l'instant, utilisons la fonction existante qui gère déjà le pack()
            # La fonction _add_main_playlist_item fait déjà le pack() automatiquement
            item_frame = self._add_main_playlist_item(filepath, song_index=song_index)
            
            # Si on veut l'insérer en haut et qu'il y a déjà des éléments
            if position == 'top' and item_frame and self.playlist_container.winfo_children():
                # Déplacer le frame au début
                children = self.playlist_container.winfo_children()
                if len(children) > 1:  # S'il y a plus d'un enfant
                    # Réorganiser l'ordre
                    item_frame.pack_forget()
                    item_frame.pack(side=tk.TOP, fill=tk.X, padx=2, pady=1, before=children[0])
            
            return item_frame
            
        except Exception as e:
            print(f"Erreur lors de l'ajout d'élément à la position {position}: {e}")
            return None

def _create_playlist_item_frame(self, filepath, song_index=None):
        """Crée un frame pour un élément de playlist"""
        try:
            # Utiliser la fonction existante qui maintenant retourne le frame
            frame = self._add_main_playlist_item(filepath, song_index=song_index)
            return frame
            
        except Exception as e:
            print(f"Erreur lors de la création du frame: {e}")
            return None

def _find_insert_position(self, song_index):
        """Trouve la position d'insertion pour maintenir l'ordre des index"""
        try:
            children = self.playlist_container.winfo_children()
            if not children:
                return None  # Insérer à la fin
            
            # Trouver la position où insérer pour maintenir l'ordre croissant des index
            for i, child in enumerate(children):
                if hasattr(child, 'song_index'):
                    if child.song_index > song_index:
                        return child  # Insérer avant cet élément
            
            return None  # Insérer à la fin
            
        except Exception as e:
            print(f"DEBUG: Erreur recherche position insertion: {e}")
            return None

def _add_main_playlist_item_ordered(self, filepath, song_index=None, insert_position=None):
        """Ajoute un élément de playlist à la position correcte pour maintenir l'ordre"""
        try:
            # Créer l'élément sans l'ajouter au container
            frame = self._add_main_playlist_item(filepath, song_index=song_index)
            
            if frame and insert_position:
                # Réorganiser pour maintenir l'ordre
                frame.pack_forget()
                frame.pack(side=tk.TOP, fill=tk.X, padx=2, pady=1, before=insert_position)
                print(f"DEBUG: Élément {song_index} inséré avant l'élément {getattr(insert_position, 'song_index', 'inconnu')}")
            elif frame:
                print(f"DEBUG: Élément {song_index} ajouté à la fin")
            
            return frame
            
        except Exception as e:
            print(f"DEBUG: Erreur ajout élément ordonné: {e}")
            # Fallback: utiliser la méthode normale
            return self._add_main_playlist_item(filepath, song_index=song_index)
