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
    print("⚠️⚠️ PAS DE USE_NEW_CONFIG⚠️⚠️ ")
    USE_NEW_CONFIG = False


class MainPlaylist:
    def __init__(self, music_player):
        self.music_player = music_player
        
    def _add_main_playlist_item(self, filepath, thumbnail_path=None, song_index=None, placement:int=None):
            """Ajoute un élément à la main playlist avec un style rectangle uniforme"""
            try:
                # Vérifier que le main_playlist_container existe et est accessible
                if not (hasattr(self.music_player, 'main_playlist_container') and self.music_player.main_playlist_container.winfo_exists()):
                    # Si le container n'est pas accessible, ne pas essayer d'ajouter l'élément visuel
                    # Cela peut arriver quand on ajoute depuis un autre onglet
                    print("Le container n'est pas accessible. Ne pas ajouter l'élément.")
                    return
                song_index = placement
                
                filename = os.path.basename(filepath)
                
                # Vérifier si c'est la chanson en cours de lecture (seulement pour les fichiers locaux)
                is_current_song = False
                if filepath:
                    is_current_song = (len(self.music_player.main_playlist) > 0 and 
                                        self.music_player.current_index < len(self.music_player.main_playlist) and 
                                        self.music_player.main_playlist[self.music_player.current_index] == filepath)
                    
                    # print('is_current_song infooos ', )
                
                bg_color = COLOR_SELECTED if is_current_song else COLOR_BACKGROUND
                
                # 1. Frame principal - grand rectangle uniforme
                item_frame = tk.Frame(
                    self.music_player.main_playlist_container,
                    bg=bg_color,
                    relief='flat',
                    bd=0,
                    highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
                    highlightthickness=1,
                )
                
                if placement is not None:
                    item_frame.place(y=placement * (MAIN_PLAYLIST_MAX_ITEM_HEIGHT + 2*DISPLAY_PLAYLIST_PADY), x=0)
                else:
                    item_frame.pack(fill='x', padx=MAIN_PLAYLIST_PADX, pady=MAIN_PLAYLIST_PADY)
                
                
                item_frame.selected = is_current_song
                item_frame.config(height=MAIN_PLAYLIST_MAX_ITEM_HEIGHT)
                item_frame.pack_propagate(False)
                item_frame.filepath = filepath
                
                # Déterminer si on affiche les numéros (seulement si provient d'une playlist)
                show_numbers = self.music_player.main_playlist_from_playlist
                # Utiliser l'index fourni ou calculer l'index actuel
                if song_index is not None:
                    current_song_index = song_index
                else:
                    current_song_index = len(self.music_player.main_playlist) - 1  # Index de la chanson actuelle (dernière ajoutée)
                
                item_frame.song_index = song_index
                
                # Vérifier si cette position spécifique fait partie de la queue
                is_in_queue = (hasattr(self.music_player, 'queue_items') and current_song_index in self.music_player.queue_items)
                item_frame.is_in_queue = is_in_queue
                
                
                # Configuration de la grille en 6 colonnes : trait queue, numéro, miniature, titre, durée, bouton
                item_frame.columnconfigure(0, minsize=4, weight=0)   # Trait queue (si applicable)
                item_frame.columnconfigure(1, minsize=10, weight=0)  # Numéro
                item_frame.columnconfigure(2, minsize=80, weight=0)  # Miniature
                item_frame.columnconfigure(3, minsize=150, weight=1) # Titre
                item_frame.columnconfigure(4, minsize=60, weight=0)  # Durée
                item_frame.columnconfigure(5, minsize=80, weight=0)  # Bouton
                item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
                
                # Trait vertical queue (colonne 0) - seulement si la musique est dans la queue
                # if is_in_queue:
                queue_indicator = tk.Frame(
                    item_frame,
                    bg=bg_color,  # Trait noir
                    width=QUEUE_LINE_WIDTH
                )
                queue_indicator.grid(row=0, column=0, sticky='ns', padx=QUEUE_LINE_PADX, pady=QUEUE_LINE_PADY)
                queue_indicator.grid_propagate(False)
                item_frame.queue_indicator = queue_indicator
                
                if is_in_queue:
                    self.music_player.show_queue_indicator(item_frame)
                
                # Numéro de la chanson (colonne 1)
                number_label = tk.Label(
                    item_frame,
                    text=str(current_song_index + 1) if show_numbers else "",  # +1 pour commencer à 1 au lieu de 0
                    bg=bg_color,
                    fg='white',
                    font=('TkDefaultFont', 10, 'bold'),
                    anchor='center'
                )
                number_label.grid(row=0, column=1, sticky='nsew', padx=(10, 5), pady=2)
                
                # Miniature (colonne 2)
                thumbnail_label = tk.Label(
                    item_frame,
                    bg=bg_color,
                    width=2,
                    height=2,
                    anchor='center',
                    text="⏵",  # Icône temporaire
                    font=('TkDefaultFont', 13, 'bold')
                )
                thumbnail_label.grid(row=0, column=2, sticky='nsew', padx=(5, 4), pady=2)
                thumbnail_label.grid_propagate(False)
                

                
                # Charger la miniature
                # if thumbnail_path and os.path.exists(thumbnail_path):
                #     self.music_player._load_image_thumbnail(thumbnail_path, thumbnail_label)
                # else:
                #     self.music_player._load_mp3_thumbnail(filepath, thumbnail_label)

                thumbnail_label.filepath = filepath
                
                # Frame pour le texte (titre + métadonnées) (colonne 1 + col_offset)
                text_frame = tk.Frame(item_frame, bg=bg_color)
                text_frame.grid(row=0, column=3, sticky='nsew', padx=(0, 2), pady=4)
                text_frame.columnconfigure(0, weight=1)
                
                # Titre principal
                metadatas = self.music_player.get_youtube_metadata(item_frame.filepath)
                if metadatas is None:
                    self.music_player.save_youtube_url_metadata(item_frame.filepath)
                
                metadatas = self.music_player.get_youtube_metadata(item_frame.filepath)
                if metadatas.get('main_playlist_truncated_title') is None:
                    self.music_player.save_youtube_url_metadata(item_frame.filepath)
                
                metadatas = self.music_player.get_youtube_metadata(item_frame.filepath)
                truncated_title = metadatas.get('main_playlist_truncated_title')
                if metadatas.get('full_title') is None:
                    self.music_player.save_youtube_url_metadata(item_frame.filepath)
                
                full_title = self.music_player.get_youtube_metadata(item_frame.filepath).get('full_title')
                
                # truncated_title = self.music_player._truncate_text_for_display(filename, max_width_pixels=MAIN_PLAYLIST_TITLE_MAX_WIDTH, font_family='TkDefaultFont', font_size=9)
                title_label = tk.Label(
                    text_frame,
                    text=truncated_title,
                    bg=bg_color,
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
                title_label.full_text = full_title  # Texte complet du titre
                title_label.pause_cycles = MAIN_PLAYLIST_TITLE_ANIMATION_PAUSE
                
                # Métadonnées (artiste • album • date)
                # artist, album = self.music_player._get_audio_metadata(filepath)
                
                # Créer un frame pour les métadonnées pour pouvoir séparer l'artiste
                metadata_container = tk.Frame(text_frame, bg=bg_color)
                metadata_container.grid(row=1, column=0, sticky='ew', pady=(0, 2))
                metadata_container.columnconfigure(0, weight=0)  # Artiste
                metadata_container.columnconfigure(1, weight=1)  # Reste des métadonnées
                
                # Label artiste cliquable (s'il existe)
                # artist_label = None
                
                # truncated_artist = self.music_player._truncate_text_for_display(artist, max_width_pixels=MAIN_PLAYLIST_ARTIST_MAX_WIDTH, font_family='TkDefaultFont', font_size=8)
                artist_label = tk.Label(
                    metadata_container,
                    text="", # Sera rempli lors du chargement différé
                    bg=bg_color,
                    fg=COLOR_ARTIST_NAME,
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
                def on_artist_click(event, file_path=filepath):
                    # Essayer d'obtenir les métadonnées YouTube pour récupérer l'URL de la chaîne
                    video_data = {}
                    artist, _ = self.music_player._get_audio_metadata(filepath)
                    try:
                        if not artist:
                            return
                        youtube_metadata = self.music_player.get_youtube_metadata(file_path)
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
                        clean_artist = artist.replace(' ', '').replace('　', '').replace('/', '')
                        encoded_artist = urllib.parse.quote(clean_artist, safe='')
                        video_data['channel_url'] = f"https://www.youtube.com/@{encoded_artist}"
                    
                    self.music_player._save_current_search_state()
                    self.music_player._show_artist_content(artist, video_data)
                
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
                #         youtube_metadata = self.music_player.get_youtube_metadata(filepath)
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
                #     metadata_text = self.music_player._format_artist_album_info(artist, album, filepath)
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
                duration_label = tk.Label(
                    item_frame,
                    text='--:--',
                    bg=bg_color,
                    fg='#cccccc',
                    font=('TkDefaultFont', 8),
                    anchor='center'
                )
                duration_label.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
                duration_label.filepath = filepath

                item_frame.song_index = current_song_index  # Stocker l'index réel
                
                # Stocker les références pour le chargement différé des métadonnées
                artist_label.filepath = filepath
                
                def on_playlist_item_click(event):
                    # Vérifier si Ctrl est enfoncé pour ouvrir sur YouTube
                    if event.state & 0x4:  # Ctrl est enfoncé
                        self.music_player.open_music_on_youtube(filepath)
                        return
                    
                    # Initialiser le drag
                    self.music_player.drag_drop_handler.setup_drag_start(event, item_frame)
                    
                    # Vérifier si Shift est enfoncé pour la sélection multiple
                    if event.state & 0x1:  # Shift est enfoncé
                        self.music_player.shift_selection_active = True
                        self.music_player.toggle_item_selection(filepath, item_frame)
                    else:
                        # Clic normal sans Shift - ne pas effacer la sélection si elle existe
                        pass
                
                def on_playlist_item_double_click(event):
                    # Vérifier si Shift est enfoncé ou si on est en mode sélection - ne rien faire
                    if event.state & 0x1 or self.music_player.selected_items:  # Shift est enfoncé ou mode sélection
                        pass
                    else:
                        # Comportement normal : jouer la musique
                        self.music_player.current_index = current_song_index  # Utiliser l'index réel stocké
                        self.music_player.on_song_change()
                        self.music_player.play_track()
                
                # Gestionnaire pour initialiser le drag sur clic gauche
                def on_left_button_press(event):
                    # Initialiser le drag pour le clic gauche
                    self.music_player.drag_drop_handler.setup_drag_start(event, item_frame)
                    # Appeler aussi le gestionnaire de clic normal
                    on_playlist_item_click(event)
                
                
                
                def on_enter(event):
                    """Rend l'item plus clair au survol"""
                    
                    # if not item_frame.selected:  # Ne pas changer la couleur si l'item est sélectionné
                    if item_frame.is_dragging:
                        return  # Ne pas changer la couleur si on est en train de drag
                    
                    bg_color = COLOR_SELECTED if item_frame.selected else COLOR_BACKGROUND
                    # Calculer une couleur plus claire
                    hover_color = self.music_player._lighten_color(bg_color, HOVER_LIGHT_PERCENTAGE)
                    if item_frame.is_in_queue:
                        self.music_player._set_item_colors(item_frame, hover_color, exclude_queue_indicator=True)
                    else:
                        self.music_player._set_item_colors(item_frame, hover_color, exclude_queue_indicator=False)
                    
                    self.music_player._start_text_animation(artist_label.full_text, artist_label)
                    self.music_player._start_text_animation(title_label.full_text, title_label)
                    
                    

                def on_leave(event):
                    """Restaure la couleur originale quand la souris quitte l'item"""
                    # if not item_frame.selected:  # Ne pas changer la couleur si l'item est sélectionné
                    
                    if item_frame.is_dragging:
                        return  # Ne pas changer la couleur si on est en train de drag
                    
                    bg_color = COLOR_SELECTED if item_frame.selected else COLOR_BACKGROUND
                    if item_frame.is_in_queue:
                        self.music_player._set_item_colors(item_frame, bg_color, exclude_queue_indicator=True)
                    else:
                        self.music_player._set_item_colors(item_frame, bg_color, exclude_queue_indicator=False)
                        
                    self.music_player._reset_text_animation(artist_label)
                    self.music_player._reset_text_animation(title_label)
                
                # Clic droit pour ouvrir le menu de sélection ou le menu contextuel
                def on_playlist_item_right_click(event):
                    # Initialiser le drag pour le clic droit
                    self.music_player.drag_drop_handler.setup_drag_start(event, item_frame)
                    
                    # Si on a des éléments sélectionnés, ouvrir le menu de sélection
                    if self.music_player.selected_items:
                        self.music_player.show_selection_menu(event)
                    else:
                        # Comportement normal : ouvrir le menu contextuel pour un seul fichier
                        self.music_player._show_single_file_menu(event, filepath, container=self.music_player.main_playlist_container, item=item_frame)
                
                item_frame.is_hovered = False
                item_frame.hover_check_id = None
                def check_mouse_in_item():
                    """Vérifie si la souris est toujours dans la zone de l'item"""
                    try:
                        if not item_frame.winfo_exists():
                            return
                        
                        # Ne pas vérifier le hover si un drag est en cours
                        if hasattr(item_frame, 'is_dragging') and item_frame.is_dragging:
                            # Programmer la prochaine vérification
                            item_frame.hover_check_id = item_frame.after(10, check_mouse_in_item)
                            return
                        
                        # Obtenir la position de la souris par rapport à l'écran
                        mouse_x = item_frame.winfo_pointerx()
                        mouse_y = item_frame.winfo_pointery()
                        
                        # Obtenir les coordonnées de l'item_frame
                        frame_x = item_frame.winfo_rootx()
                        frame_y = item_frame.winfo_rooty()
                        frame_width = item_frame.winfo_width()
                        frame_height = item_frame.winfo_height()
                        
                        # Vérifier si la souris est dans la zone de l'item
                        mouse_in_item = (frame_x <= mouse_x <= frame_x + frame_width and 
                                    frame_y <= mouse_y <= frame_y + frame_height)
                        
                        # Si l'état a changé
                        if mouse_in_item != item_frame.is_hovered:
                            item_frame.is_hovered = mouse_in_item
                            if mouse_in_item:
                                on_enter(None)
                            else:
                                on_leave(None)
                        
                        # Programmer la prochaine vérification si la souris est dans l'item
                        if mouse_in_item:
                            item_frame.hover_check_id = item_frame.after(10, check_mouse_in_item)
                        else:
                            item_frame.hover_check_id = None
                            
                    except tk.TclError:
                        # Widget détruit
                        pass
                
                def on_motion(event):
                    """Déclenché quand la souris bouge dans l'item ou ses enfants"""
                    # Ne pas déclencher on_enter si un drag est en cours
                    if hasattr(item_frame, 'is_dragging') and item_frame.is_dragging:
                        return
                    
                    
                    if not item_frame.is_hovered:
                        item_frame.is_hovered = True
                        on_enter(event)
                    
                    # Annuler la vérification précédente et en programmer une nouvelle
                    if item_frame.hover_check_id:
                        item_frame.after_cancel(item_frame.hover_check_id)
                    item_frame.hover_check_id = item_frame.after(100, check_mouse_in_item)
                                
                widgets_to_bind = [item_frame, number_label, thumbnail_label, text_frame, 
                                title_label, duration_label, artist_label, metadata_container]
                
                for widget in widgets_to_bind:
                    # Binder les clics sur tous les enfants pour qu'ils remontent à l'item_frame
                    widget.bind("<ButtonPress-1>", on_playlist_item_click, add='+')
                    widget.bind("<Double-1>", on_playlist_item_double_click, add='+')
                    widget.bind("<ButtonPress-3>", on_playlist_item_right_click, add='+')
                    # Binder le motion sur tous les enfants
                    widget.bind("<Motion>", on_motion, add='+')
                    
                    widget.bind("<B1-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f), add='+')
                    widget.bind("<ButtonRelease-1>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f), add='+')
                    widget.bind("<B3-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f), add='+')
                    widget.bind("<ButtonRelease-3>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f), add='+')
                                
                item_frame.bind("<ButtonPress-1>", on_playlist_item_click)
                item_frame.bind("<Double-1>", on_playlist_item_double_click)
                item_frame.bind("<ButtonPress-3>", on_playlist_item_right_click, add='+')
                item_frame.bind("<Motion>", on_motion)
                
                item_frame.bind("<B1-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f))
                item_frame.bind("<ButtonRelease-1>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f))
                item_frame.bind("<B3-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f))
                item_frame.bind("<ButtonRelease-3>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f))
                
                # item_frame.bind("<ButtonPress-3>", on_playlist_item_right_click)
                # thumbnail_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
                # text_frame.bind("<ButtonPress-3>", on_playlist_item_right_click)
                # title_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
                # Ajouter les bindings pour le clic droit sur les labels de métadonnées s'ils existent
                # duration_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
                
                # if show_numbers:
                #     number_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
                
                # Configuration du drag-and-drop
                self.music_player.drag_drop_handler.setup_drag_drop(
                    item_frame, 
                    file_path=filepath, 
                    item_type="file"
                )
                
                # Tooltip pour expliquer les interactions
                tooltip_text = "Musique de la playlist principale\nDouble-clic: Jouer cette musique\nCtrl + Clic: Ouvrir sur YouTube\nDrag vers la droite: Ajouter à la queue (prochaines musiques)\nDrag vers la gauche: Placer en premier dans la queue\nShift + Clic: Sélection multiple\nClic droit: Ouvrir le menu contextuel"
                tooltip.create_tooltip(text_frame, tooltip_text)
                tooltip.create_tooltip(title_label, tooltip_text)
                # Ajouter les tooltips pour les labels de métadonnées s'ils existent
                # if artist:
                #     tooltip.create_tooltip(artist_label, tooltip_text)
                #     if other_metadata_label:
                #         tooltip.create_tooltip(other_metadata_label, tooltip_text)
                # else:
                #     # Pas d'artiste, utiliser le label de métadonnées normal
                #     if 'metadata_label' in locals():
                #         tooltip.create_tooltip(metadata_label, tooltip_text)
                # tooltip.create_tooltip(thumbnail_label, tooltip_text)
                
                # Retourner le frame créé pour pouvoir l'utiliser
                return item_frame

            except Exception as e:
                print(f"Erreur affichage playlist item: {e}")
                return None



    
    def _display_main_playlist(self, files_to_display, preserve_scroll=False):
        """Affiche la main playlist"""
        # Marquer qu'on est en train de faire un refresh pour éviter la boucle infinie
        # print("_display_main_playlist appelée")
        
        files_to_display = self.music_player.main_playlist.copy()
        
        # Vider le container actuel
        try:
            # Vérifier que le container existe encore
            if hasattr(self, 'main_playlist_container') and self.music_player.main_playlist_container.winfo_exists():
                for widget in self.music_player.main_playlist_container.winfo_children():
                    try:
                        if widget.winfo_exists():
                            widget.destroy()
                    except tk.TclError:
                        # Widget déjà détruit, ignorer
                        continue
        except tk.TclError:
            # Container détruit, ignorer
            pass
        
        
        # Remonter le scroll en haut après chaque recherche (sauf si preserve_scroll=True)
        if not preserve_scroll and hasattr(self.music_player, 'main_playlist_canvas'):
            try:
                if self.music_player.main_playlist_canvas.winfo_exists():
                    self.music_player.main_playlist_canvas.yview_moveto(0.0)
            except tk.TclError:
                # Canvas détruit, ignorer
                pass
        
        # Si aucun fichier à afficher, montrer le message "Aucun résultat"
        # if not files_to_display:
        #     _show_no_results_message(self)
        #     # Marquer la fin du refresh
        #     self._refreshing_downloads = False
        #     return
        
        # Afficher avec chargement différé des miniatures
        # item_list = []
        self.music_player.main_playlist_all_widgets = {}
        self.music_player.main_playlist_visible_widgets = {}
        limit = 30
        for i, filepath in enumerate(files_to_display):
            # if i >= limit:
            #     break
            # self._add_download_item_fast(filepath)
            
            # item = self._add_song_item_empty(filepath, self.downloads_container)
            
            # self._load_song_item(item, self.downloads_container)
            # if i >= limit:
            #     item_list.append(item)
            # self.visible_widgets[i] = item
            
            # self.all_widgets[i] = item
            self.music_player.main_playlist_all_widgets[i] = filepath
        
        
        # Forcer la mise à jour de la scrollbar après l'ajout des éléments
        # self._update_scrollbar()
        
        
        # from library_tab.downloads import _update_visible_items
        # self.root.after(3000, lambda a=self: _update_visible_items(self))
        
        self.music_player.root.after(0, lambda: (self._update_visible_items(), self.on_canvas_scroll_end()))
        # self._update_visible_items()
        
        # Lancer le chargement différé des miniatures et durées
        # self.music_player._start_thumbnail_loading(files_to_display, self.music_player.main_playlist_container)
    
    def on_canvas_scroll_end(self):
        files_to_display = [item.filepath for item in self.music_player.main_playlist_visible_widgets.values()]
        self.music_player._start_thumbnail_loading(files_to_display, self.music_player.main_playlist_container)
    
    def _update_visible_items(self):
        """Met à jour les widgets visibles"""
        start_index, end_index = self._calculate_visible_range()
        # print('start end ', start_index, end_index)
        
        # Supprimer les widgets qui ne sont plus visibles
        for idx in list(self.music_player.main_playlist_visible_widgets.keys()):
            if idx < start_index or idx >= end_index:
                self.music_player._unload_song_item(self.music_player.main_playlist_visible_widgets[idx], self.music_player.downloads_container)
                self.music_player.main_playlist_visible_widgets.pop(idx)
        
        # Créer les widgets qui deviennent visibles
        for idx in range(start_index, end_index):
            # print('nyan ', idx, self.visible_widgets)
            if idx not in self.music_player.main_playlist_visible_widgets.keys():
                # threading.Thread(target=lambda :self._load_song_item(self.all_widgets[idx], self.downloads_container), daemon=True).start()
                # self.visible_widgets[idx] = self.all_widgets[idx]
                
                item = self._add_main_playlist_item(self.music_player.main_playlist_all_widgets[idx], placement=idx)
                # item = self._add_song_item(self.all_widgets[idx], self.downloads_container, placement=50)
                self.music_player.main_playlist_visible_widgets[idx] = item
    
    def _calculate_visible_range(self):
        """Calcule la plage d'éléments visibles"""
        # Obtenir les coordonnées visibles du canvas
        canvas = self.music_player.main_playlist_canvas
        bbox = canvas.bbox("all")
        if not bbox:
            return 0, 0
        
        
        height = (MAIN_PLAYLIST_MAX_ITEM_HEIGHT + 2 * MAIN_PLAYLIST_PADY) * len(self.music_player.main_playlist)
        self.music_player.main_playlist_container.config(height=height)
        
        canvas_height = canvas.winfo_height()
        canvas_height = 600 if canvas_height == 1 else canvas_height # pour que ça affiche bien au début
        scroll_pos = canvas.canvasy(0)  # Position verticale en pixels
        
        # print("_calculate_visible_range" ,scroll_pos, canvas_height)
        # Calcul des indices
        start_index = max(0, int(scroll_pos / (MAIN_PLAYLIST_MAX_ITEM_HEIGHT + 2 *MAIN_PLAYLIST_PADY)) - MAIN_PLAYLIST_TOP_ITEM_BUFFERING)  # -2 pour le buffering
        end_index = min(len(self.music_player.main_playlist_all_widgets), int((scroll_pos + canvas_height) / (MAIN_PLAYLIST_MAX_ITEM_HEIGHT  + 2 *MAIN_PLAYLIST_PADY)) + MAIN_PLAYLIST_BOTTOM_ITEM_BUFFERING) # +3
        
        return start_index, end_index
            

    def select_playlist_item(self, item_frame=None, index=None, auto_scroll=True, is_manual=False):
        """Met en surbrillance l'élément sélectionné dans la playlist
        
        Args:
            item_frame: Frame de l'élément à sélectionner
            index: Index de l'élément à sélectionner (alternatif à item_frame)
            auto_scroll: Si True, fait défiler automatiquement vers l'élément (défaut: True)
        """
        # print("select_playlist_item appelée")
        # Protection contre les appels multiples rapides
        if not hasattr(self.music_player, '_last_select_time'):
            self.music_player._last_select_time = 0
        
        current_time = time.time()
        if current_time - self.music_player._last_select_time < 0.05:  # 50ms de protection
            return
        self.music_player._last_select_time = current_time
        # Désélectionner tous les autres éléments
        try:
            if hasattr(self.music_player, 'main_playlist_container') and self.music_player.main_playlist_container.winfo_exists():
                # Accès sécurisé aux enfants pour la désélection
                try:
                    children_for_deselect = self.music_player.main_playlist_container.winfo_children()
                except tk.TclError:
                    children_for_deselect = []

                for child in children_for_deselect:
                    try:
                        if child.winfo_exists() and hasattr(child, 'selected'):
                            child.selected = False
                            self.music_player._set_item_colors(child, COLOR_BACKGROUND)  # Couleur normale
                    except tk.TclError:
                        # Widget détruit, ignorer
                        continue

        except tk.TclError:
            # Container détruit, ignorer
            return
        
        if index in self.music_player.main_playlist_visible_widgets:
            item_frame = self.music_player.main_playlist_visible_widgets[index]
            
        else:
            if self.load_missing_items(index): # True si on a ajouté des éléments
                files_to_display = [item.filepath for item in self.music_player.main_playlist_visible_widgets.values()]
                self.music_player._start_thumbnail_loading(files_to_display, self.music_player.main_playlist_container)
            item_frame = self.music_player.main_playlist_visible_widgets[index]
        
        # Sélectionner l'élément courant si fourni
        if item_frame:
            item_frame.update_idletasks()
            try:
                if item_frame.winfo_exists():
                    item_frame.selected = True
                    self.music_player._set_item_colors(item_frame, COLOR_SELECTED)  # Couleur de surbrillance (bleu)
                    
                    
                    # Faire défiler avec animation pour que l'élément soit visible (seulement si auto_scroll=True)
                    if auto_scroll:
                        try:
                            # Vérifier que tous les widgets existent encore
                            if (hasattr(self.music_player, 'main_playlist_container') and self.music_player.main_playlist_container.winfo_exists() and
                                hasattr(self.music_player, 'main_playlist_canvas') and self.music_player.main_playlist_canvas.winfo_exists()):
                                
                                container_height = self.music_player.main_playlist_container.winfo_height()
                                if container_height > 0:
                                    
                                    item_y = item_frame.winfo_y()
                                    target_position = item_y / container_height
                                    self._smooth_scroll_to_position(target_position, is_manual=is_manual, callback=self._refresh_main_playlist_display)
                                    
                                else:
                                    # Fallback si la hauteur n'est pas disponible
                                    item_y = item_frame.winfo_y()
                                    container_height = self.music_player.main_playlist_container.winfo_height()
                                    if container_height > 0:
                                        self.music_player.main_playlist_canvas.yview_moveto(item_y / container_height)
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

    def load_missing_items(self, index, callback=None):
        """Charge les éléments manquants de la playlist si besoin"""
        
        try:
            scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
            top_y = self.music_player.main_playlist_container.winfo_height() * scroll_top
            top_index = int(top_y // (MAIN_PLAYLIST_MAX_ITEM_HEIGHT + 2 * MAIN_PLAYLIST_PADY))
            
            index_offset = int(self.music_player.main_playlist_canvas.winfo_height() / (MAIN_PLAYLIST_MAX_ITEM_HEIGHT  + 2 *MAIN_PLAYLIST_PADY)) + MAIN_PLAYLIST_BOTTOM_ITEM_BUFFERING # pour qu'une fois qu'on a scroll, on ait toujours plus qu'une musique affichée
            
            # print("scroll_top top_y", scroll_top, top_y)
            # print('top current', top_index, index)
            
            start_index = min(top_index, index)
            end_index = max(top_index, index)
            
            end_index = min(len(self.music_player.main_playlist) - 1, end_index + index_offset)
            
            # print('start end indexes', start_index, end_index)
            
            if end_index == start_index:
                return False
            
            if end_index - start_index > MAX_SCROLL_LOADING_SONGS:
                for idx in [start_index, end_index]:
                    if not idx in self.music_player.main_playlist_visible_widgets:
                        if not idx in self.music_player.main_playlist_all_widgets:
                            print('ID ', idx, 'pas dans self.music_player.main_playlist_all_widgets')
                        
                        item = self._add_main_playlist_item(self.music_player.main_playlist_all_widgets[idx], placement=idx)
                        self.music_player.main_playlist_visible_widgets[idx] = item
                    # print('IDX LOADED', idx)
                return False
            
            for idx in range(start_index, end_index + 1):
                if not idx in self.music_player.main_playlist_visible_widgets:
                    if not idx in self.music_player.main_playlist_all_widgets:
                        print('ID ', idx, 'pas dans self.music_player.main_playlist_all_widgets')
                    
                    item = self._add_main_playlist_item(self.music_player.main_playlist_all_widgets[idx], placement=idx)
                    self.music_player.main_playlist_visible_widgets[idx] = item
                # print('IDX LOADED', idx)
            
            if callback:
                callback()
            
            return True
            
        except Exception as e:
            print(f"DEBUG: Erreur lors du chargement des éléments manquants de la playlist: {e}")

    def _remove_from_main_playlist(self, filepath, frame, event=None, song_index=None):
        """Supprime un élément de la main playlist"""
        try:
            # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
            if event and (event.state & 0x4):  # Ctrl est enfoncé
                self.music_player._delete_from_downloads(filepath, frame)
            else:
                # Suppression normale de la playlist
                # Utiliser l'index fourni ou trouver l'index de l'élément à supprimer
                if song_index is not None:
                    index = song_index
                else:
                    index = self.music_player.main_playlist.index(filepath)
                
                # Supprimer de la liste
                self.music_player.main_playlist.pop(index)
                
                # Mettre à jour la queue : supprimer l'index supprimé et décrémenter les indices supérieurs
                if hasattr(self.music_player, 'queue_items'):
                    # Supprimer l'index supprimé s'il était dans la queue
                    if index in self.music_player.queue_items:
                        self.music_player.queue_items.discard(index)
                    
                    # Décrémenter tous les indices supérieurs à celui supprimé
                    updated_queue = set()
                    for queue_index in self.music_player.queue_items:
                        if queue_index > index:
                            updated_queue.add(queue_index - 1)  # Décrémenter l'index
                        else:
                            updated_queue.add(queue_index)  # Garder tel quel
                    self.music_player.queue_items = updated_queue
                
                # Mettre à jour l'index courant si nécessaire
                if index < self.music_player.current_index:
                    self.music_player.current_index -= 1
                elif index == self.music_player.current_index:
                    pygame.mixer.music.stop()
                    self.music_player.current_index = min(index, len(self.music_player.main_playlist) - 1)
                    self.music_player.on_song_change()
                    if len(self.music_player.main_playlist) > 0:
                        self.music_player.play_track()
                    else:
                        self.reset_main_playlist()
                
                if frame.selected:
                    frame.selected = False

                # Si la playlist devient vide, réinitialiser le flag
                if len(self.music_player.main_playlist) == 0:
                    self.music_player.main_playlist_from_playlist = False
                
                # Rafraîchir complètement l'affichage de la playlist pour éviter les incohérences
                self._refresh_main_playlist_display()
                
                self.music_player.status_bar.config(text=f"Piste supprimée de la main playlist")
        except ValueError:
            pass
        except Exception as e:
            self.music_player.status_bar.config(text=f"Erreur suppression: {e}")

    def _clear_main_playlist(self, event=None):
        """Vide complètement la liste de lecture principale (nécessite un double-clic)"""
        if not self.music_player.main_playlist:
            self.music_player.status_bar.config(text="La liste de lecture est déjà vide")
            return
        
        self.reset_main_playlist()
        self.music_player.go_to_top(self.music_player.main_playlist_canvas)

    def _scroll_to_current_song(self, event=None, is_manual=False):
        """Bouton find.png : Compatible ancien et nouveau système"""
        if not self.music_player.main_playlist or self.music_player.current_index >= len(self.music_player.main_playlist):
            self.music_player.status_bar.config(text="Aucune musique en cours de lecture")
            return
        
        try:
            
            self.select_playlist_item(index=self.music_player.current_index, auto_scroll=True, is_manual=is_manual)
            
            total_songs = len(self.music_player.main_playlist)
            self.music_player.status_bar.config(text=f"Navigation vers la chanson {self.music_player.current_index + 1}/{total_songs}")
            
        except Exception as e:
            print(f"Erreur lors du scroll vers la chanson actuelle: {e}")
            self.music_player.status_bar.config(text="Erreur lors de la navigation")

    def select_current_song_smart(self, auto_scroll=True, force_reload=False, is_manual=False):
        """Auto-scroll intelligent : Compatible ancien et nouveau système"""
        # print("select_current_song_smart appelé")
        try:
            self.select_playlist_item(index=self.music_player.current_index, auto_scroll=auto_scroll)
                
        except Exception as e:
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur select current smart: {e}")

    def _find_relative_index_in_loaded(self, absolute_index):
            """Trouve l'index relatif d'une chanson dans les éléments chargés"""
            try:
                children = self.music_player.main_playlist_container.winfo_children()
                for i, child in enumerate(children):
                    if hasattr(child, 'song_index') and child.song_index == absolute_index:
                        return i
                return None
            except Exception:
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
        print(f"add_to_main_playlist appelée: Ajout de {filepath} à la main playlist add_to_main_playlist ", allow_duplicates, filepath in self.music_player.main_playlist)

        full_filepath = os.path.join(self.music_player.downloads_folder, filepath)
        if allow_duplicates or filepath not in self.music_player.main_playlist:
            self.music_player.main_playlist.append(full_filepath)
            # self._add_main_playlist_item(full_filepath, thumbnail_path, song_index)
            self.music_player._update_downloads_queue_visual()
            self._refresh_main_playlist_display()
            
            if show_status:
                self.music_player.status_bar.config(text=f"Ajouté à la liste de lecture principale: {filepath}")
            return True
        else:
            if show_status:
                self.music_player.status_bar.config(text=f"Déjà dans la liste de lecture principale: {filepath}")
            return False

    def _smooth_scroll_to_position(self, target_position, duration=500, is_manual=False, callback=None):
        """Anime le scroll vers une position cible avec une courbe ease-in-out"""
        try:
            # Vérifier que le canvas existe encore avant de commencer
            if not (hasattr(self.music_player, 'main_playlist_canvas') and self.music_player.main_playlist_canvas.winfo_exists()):
                print("_smooth_scroll_to_position, non1")
                return
                
            # Annuler toute animation en cours
            if hasattr(self.music_player, 'scroll_animation_id') and self.music_player.scroll_animation_id:
                try:
                    self.music_player.root.after_cancel(self.music_player.scroll_animation_id)
                except:
                    pass
                self.music_player.scroll_animation_id = None
            
            # Si une animation est déjà en cours, l'arrêter
            if hasattr(self.music_player, 'scroll_animation_active') and self.music_player.scroll_animation_active:
                self.music_player.scroll_animation_active = False
            
            # Obtenir la position actuelle du scroll
            try:
                # Vérifier que le canvas existe encore
                if not (hasattr(self.music_player, 'main_playlist_canvas') and self.music_player.main_playlist_canvas.winfo_exists()):
                    print("_smooth_scroll_to_position, non2")
                    return
                current_top, current_bottom = self.music_player.main_playlist_canvas.yview()
                start_position = current_top
            except tk.TclError:
                # Canvas détruit, ignorer
                return
            except Exception:
                # En cas d'autre erreur, faire un scroll instantané si possible
                print(f"❌ Erreur smooth_scroll_to_position, on tente scroll instantané: {e}")
                try:
                    if hasattr(self.music_player, 'main_playlist_canvas') and self.music_player.main_playlist_canvas.winfo_exists():
                        self.music_player.main_playlist_canvas.yview_moveto(target_position)
                except tk.TclError:
                    # Canvas détruit, ignorer
                    pass
                return
            
            # Si on est déjà à la bonne position, ne rien faire
            # if abs(start_position - target_position) < 0.001:
            if start_position == target_position:
                return
            
            
            # Paramètres de l'animation
            start_time = time.time() * 1000  # Temps en millisecondes
            distance = target_position - start_position
            
            self.music_player.scroll_animation_active = True
            
            def ease_in_out_cubic(t):
                """Fonction d'easing cubic ease-in-out"""
                if t < 0.5:
                    return 4 * t * t * t
                else:
                    return 1 - pow(-2 * t + 2, 3) / 2
            
            def animate_step():
                if not self.music_player.scroll_animation_active:
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
                    if not (hasattr(self.music_player, 'main_playlist_canvas') and self.music_player.main_playlist_canvas.winfo_exists()):
                        self.music_player.scroll_animation_active = False
                        return
                        
                    self.music_player.main_playlist_canvas.yview_moveto(current_position)
                except tk.TclError:
                    # Canvas détruit, arrêter l'animation
                    self.music_player.scroll_animation_active = False
                    return
                except Exception:
                    # En cas d'autre erreur, arrêter l'animation
                    self.music_player.scroll_animation_active = False
                    return
                
                # Continuer l'animation si pas terminée
                if progress < 1.0:
                    self.music_player.scroll_animation_id = self.music_player.root.after(16, animate_step)  # ~60 FPS
                else:
                    self.music_player.scroll_animation_active = False
                    self.music_player.scroll_animation_id = None
                    if callback is not None:
                        callback()
            
            # Démarrer l'animation
            animate_step()
        except Exception as e:
            print(f"Erreur lors de l'animation du scroll: {e}")

    def reset_main_playlist(self):
        # Arrêter la lecture si une musique est en cours
        if hasattr(self.music_player, 'paused') and not self.music_player.paused:
            pygame.mixer.music.stop()
        
        # Décharger la musique
        pygame.mixer.music.unload()
        
        # Vider la liste principale et la playlist "Main Playlist"
        self.music_player.main_playlist.clear()
        if "Main Playlist" in self.music_player.playlists:
            self.music_player.playlists["Main Playlist"].clear()
        self.music_player.current_index = 0
        self.music_player.on_song_change()
        
        # Vider la queue
        if hasattr(self.music_player, 'queue_items'):
            self.music_player.queue_items.clear()
        
        # Vider l'affichage de la playlist
        try:
            if hasattr(self.music_player, 'main_playlist_container') and self.music_player.main_playlist_container.winfo_exists():
                for widget in self.music_player.main_playlist_container.winfo_children():
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
        self.music_player.clear_all_current_song_selections()
        
        # Réinitialiser les variables de fenêtrage optimisé
        if hasattr(self.music_player, '_last_window_start'):
            delattr(self.music_player, '_last_window_start')
        if hasattr(self.music_player, '_last_window_end'):
            delattr(self.music_player, '_last_window_end')
        
        # Réinitialiser les variables d'optimisation
        if hasattr(self.music_player, '_last_select_time'):
            self.music_player._last_select_time = 0
        
        # Mettre à jour l'affichage
        self.music_player.status_bar.config(text="Up next vidée")
        
        # Réinitialiser l'affichage de la chanson actuelle
        if hasattr(self.music_player, 'song_label'):
            self.music_player.song_label.config(text="No track selected")
        if hasattr(self.music_player, 'song_metadata_label'):
            self.music_player.song_metadata_label.config(text="")
        
        # Changer l'image
        self.music_player.clear_thumbnail_label()
        
        # Mettre à jour les contrôles
        if hasattr(self.music_player, 'time_slider'):
            self.music_player.time_slider.set(0)
        if hasattr(self.music_player, 'time_label'):
            self.music_player.time_label.config(text="00:00 / 00:00")

    def _refresh_main_playlist_display(self, force_full_refresh=False):
            """Rafraîchit l'affichage de la main playlist avec optimisation par fenêtrage"""
            # print("_refresh_main_playlist_display appelée")
            # Protection contre les appels multiples rapides
            if not hasattr(self.music_player, '_last_refresh_time'):
                self.music_player._last_refresh_time = 0
            
            current_time = time.time()
            if not force_full_refresh and current_time - self.music_player._last_refresh_time < 0.1:  # 100ms de protection
                return
            self.music_player._last_refresh_time = current_time
            
            try:
                # Vérifier que le container existe encore
                if not hasattr(self.music_player, 'main_playlist_container'):
                    return
                    
                if not self.music_player.main_playlist_container.winfo_exists():
                    return
                
                
                # self._refresh_full_playlist_display()
                
                
                
                
                # Vider le container actuel
                try:
                    children = self.music_player.main_playlist_container.winfo_children()
                except tk.TclError:
                    children = []
                    
                for widget in children:
                    try:
                        if widget.winfo_exists():
                            widget.destroy()
                    except tk.TclError:
                        continue
                
                self._display_main_playlist(self.music_player.main_playlist, preserve_scroll=True)
                
                # Remettre en surbrillance la chanson en cours si elle existe
                # if len(self.music_player.main_playlist) > 0 and self.music_player.current_index < len(self.music_player.main_playlist):
                #     try:
                #         self.select_playlist_item(index=self.music_player.current_index, auto_scroll=False)
                #     except tk.TclError:
                #         pass
                
                # Mettre à jour la région de scroll du canvas
                # Différer légèrement pour s'assurer que la géométrie est calculée
                if USE_NEW_CONFIG:
                    delay = get_main_playlist_config('scroll_update_delay')
                else:
                    delay = 10
                # self.music_player.root.after(delay, lambda: self._update_canvas_scroll_region())
                
                    
            except tk.TclError as e:
                # Container détruit ou problème avec l'interface, ignorer silencieusement
                pass
            except Exception as e:
                print(f"Erreur lors du rafraîchissement de la playlist: {e}")

    def _refresh_full_playlist_display(self):
            print("_refresh_full_playlist_display appelée NON UTILISEE")
            """Rafraîchit complètement l'affichage de la playlist (version originale)"""
            return
            try:
                # Vider le container actuel
                try:
                    children = self.music_player.main_playlist_container.winfo_children()
                except tk.TclError:
                    children = []
                    
                for widget in children:
                    try:
                        if widget.winfo_exists():
                            widget.destroy()
                    except tk.TclError:
                        continue
                
                # Recréer tous les éléments avec les bons index
                # for i, filepath in enumerate(self.music_player.main_playlist):
                #     self._add_main_playlist_item(filepath, song_index=i)
                
                self._display_main_playlist(self.music_player.main_playlist, preserve_scroll=True)
                
                # Remettre en surbrillance la chanson en cours si elle existe
                if len(self.music_player.main_playlist) > 0 and self.music_player.current_index < len(self.music_player.main_playlist):
                    try:
                        self.select_playlist_item(index=self.music_player.current_index, auto_scroll=False)
                    except tk.TclError:
                        pass
                
                # Mettre à jour la région de scroll du canvas
                # Différer légèrement pour s'assurer que la géométrie est calculée
                # if USE_NEW_CONFIG:
                #     delay = get_main_playlist_config('scroll_update_delay')
                # else:
                #     delay = 10
                # self.music_player.root.after(delay, lambda: self._update_canvas_scroll_region())
                        
            except Exception as e:
                print(f"Erreur lors du rafraîchissement complet: {e}")

    def _refresh_windowed_playlist_display(self, force_recreate=False):
            """Rafraîchit l'affichage avec fenêtrage optimisé (n'affiche que les éléments visibles)"""
            print("_refresh_windowed_playlist_display appelé")
            return
            try:
                # Optimisation: Éviter les rafraîchissements trop fréquents
                if not force_recreate and hasattr(self.music_player, '_last_refresh_time'):
                    current_time = time.time()
                    min_refresh_interval = 0.05  # 50ms entre les rafraîchissements
                    if current_time - self.music_player._last_refresh_time < min_refresh_interval:
                        return
                self.music_player._last_refresh_time = time.time()
                
                # Vérifier si on doit faire un auto-recentrage sur la chanson courante
                if (USE_NEW_CONFIG and get_main_playlist_config('auto_center_on_song_change') and
                    hasattr(self.music_player, 'current_index') and not force_recreate):
                    
                    current_index = self.music_player.current_index
                    last_index = getattr(self.music_player, '_last_current_index', current_index)
                    
                    # Si la chanson a changé et que l'utilisateur ne scroll pas
                    if (current_index != last_index and 
                        not getattr(self.music_player, '_user_is_scrolling', False) and
                        not getattr(self.music_player, '_auto_centering', False)):
                        
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
                        start_index = max(0, self.music_player.current_index - songs_before)
                        end_index = min(len(self.music_player.main_playlist), self.music_player.current_index + songs_after + 1)
                else:
                    # Système classique
                    songs_before = get_main_playlist_config('songs_before_current') if USE_NEW_CONFIG else 10
                    songs_after = get_main_playlist_config('songs_after_current') if USE_NEW_CONFIG else 10
                    start_index = max(0, self.music_player.current_index - songs_before)
                    end_index = min(len(self.music_player.main_playlist), self.music_player.current_index + songs_after + 1)
                
                # Vérifier si on peut réutiliser l'affichage existant (optimisation)
                # Mais seulement si le container a des enfants (pas après un clear) et pas de force_recreate
                can_reuse = (not force_recreate and
                            hasattr(self.music_player, '_last_window_start') and hasattr(self.music_player, '_last_window_end') and
                            self.music_player._last_window_start == start_index and self.music_player._last_window_end == end_index and
                            hasattr(self.music_player, 'main_playlist_container') and self.music_player.main_playlist_container.winfo_exists() and
                            len(self.music_player.main_playlist_container.winfo_children()) > 0)
                
                if can_reuse:
                    # Juste mettre à jour la surbrillance sans recréer les widgets
                    self._update_current_song_highlight_only()
                    return
                
                # Sauvegarder les paramètres de fenêtre pour la prochaine fois
                self.music_player._last_window_start = start_index
                self.music_player._last_window_end = end_index
                
                # Vider le container actuel
                try:
                    children = self.music_player.main_playlist_container.winfo_children()
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
                    if i < len(self.music_player.main_playlist):
                        filepath = self.music_player.main_playlist[i]
                        self._add_main_playlist_item(filepath, song_index=i)
                
                # Précharger les métadonnées des éléments suivants de manière asynchrone
                playlist_size = len(self.music_player.main_playlist)  # Correction erreur Pylance
                if get_config("enable_preloading", True) and end_index < len(self.music_player.main_playlist):
                    preload_size = get_preload_size(playlist_size)
                    if preload_size > 0:
                        next_batch_start = end_index
                        next_batch_end = min(len(self.music_player.main_playlist), end_index + preload_size)
                        self._preload_metadata_async(next_batch_start, next_batch_end)
                
                # Les indicateurs de fin sont également supprimés
                
                # Remettre en surbrillance la chanson en cours si elle est dans la fenêtre
                if (len(self.music_player.main_playlist) > 0 and 
                    self.music_player.current_index < len(self.music_player.main_playlist) and
                    start_index <= self.music_player.current_index < end_index):
                    try:
                        # Trouver le widget correspondant à l'index courant
                        widgets = self.music_player.main_playlist_container.winfo_children()
                        # Calculer la position relative dans la fenêtre (sans indicateurs)
                        relative_index = self.music_player.current_index - start_index
                        
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
                    self._update_canvas_scroll_region()
                    self._setup_infinite_scroll()  # Configurer le scroll infini
                    # Force le chargement/déchargement intelligent immédiatement
                    if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading'):
                        self._smart_load_unload()
                    self._trigger_smart_reload_on_song_change()  # Déclencher le smart reload
                
                self.music_player.root.after(delay, setup_scroll)
                        
            except Exception as e:
                print(f"Erreur lors du rafraîchissement par fenêtrage: {e}")

    def _update_current_song_highlight_only(self):
            """Met à jour uniquement la surbrillance de la chanson courante sans recréer les widgets"""
            try:
                if not (hasattr(self.music_player, 'main_playlist_container') and self.music_player.main_playlist_container.winfo_exists()):
                    return
                    
                # Désélectionner tous les éléments
                children = self.music_player.main_playlist_container.winfo_children()
                for child in children:
                    try:
                        if child.winfo_exists() and hasattr(child, 'config'):
                            self.music_player._set_item_colors(child, '#4a4a4a')  # Couleur normale
                    except:
                        continue
                
                # Calculer la position de la chanson courante dans la fenêtre affichée
                if (hasattr(self.music_player, '_last_window_start') and hasattr(self.music_player, '_last_window_end') and
                    self.music_player._last_window_start <= self.music_player.current_index < self.music_player._last_window_end):
                    
                    relative_index = self.music_player.current_index - self.music_player._last_window_start
                    # Ajouter 1 si on a un indicateur du début
                    if self.music_player._last_window_start > 0:
                        relative_index += 1
                    
                    if 0 <= relative_index < len(children):
                        widget = children[relative_index]
                        if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                            self._highlight_current_song_widget(widget)
                            
            except Exception as e:
                print(f"Erreur lors de la mise à jour de la surbrillance: {e}")

    def _add_playlist_indicator(self, text, position):
            """Ajoute un indicateur visuel pour les éléments non affichés"""
            try:
                indicator_frame = tk.Frame(
                    self.music_player.main_playlist_container,
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
                        new_index = max(0, self.music_player.current_index - jump_size)
                    else:
                        # Aller vers la fin - sauter vers le bas
                        new_index = min(len(self.music_player.main_playlist) - 1, self.music_player.current_index + jump_size)
                    
                    if 0 <= new_index < len(self.music_player.main_playlist):
                        self.music_player.current_index = new_index
                        self.music_player.on_song_change()
                        self.music_player.play_track()
                        # Forcer le rafraîchissement pour afficher la nouvelle fenêtre
                        self.music_player.root.after(50, lambda: self._refresh_main_playlist_display(force_full_refresh=False))
                
                indicator_label.bind("<Button-1>", on_indicator_click)
                indicator_label.config(cursor="hand2")
                
                # Ajouter un tooltip pour expliquer la fonctionnalité
                try:
                    if position == "top":
                        tooltip.create_tooltip(indicator_label, "Cliquez pour remonter de 15 chansons")
                    else:
                        tooltip.create_tooltip(indicator_label, "Cliquez pour descendre de 15 chansons")
                except:
                    pass  # Si tooltip.create_tooltip n'est pas disponible, ignorer
                
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
                self.music_player._set_item_colors(widget, COLOR_SELECTED)
            except Exception as e:
                print(f"Erreur lors de la mise en surbrillance: {e}")

    def _refresh_main_playlist_display_async(self):
            """Version asynchrone du rafraîchissement pour éviter les lags lors du chargement de grandes playlists"""
            try:
                print("_refresh_main_playlist_display_async appelé")
                # Forcer un rafraîchissement complet si les variables de fenêtrage n'existent pas
                # (cas d'un rechargement après clear)
                force_refresh = not (hasattr(self.music_player, '_last_window_start') and hasattr(self.music_player, '_last_window_end'))
                
                # Utiliser le système de fenêtrage optimisé
                self._refresh_main_playlist_display(force_full_refresh=force_refresh)
                # self._refresh_main_playlist_display(force_full_refresh=False)
                
                # Mettre à jour le message de statut
                if hasattr(self.music_player, 'status_bar'):
                    total_songs = len(self.music_player.main_playlist)
                    if total_songs > 50:
                        self.music_player.status_bar.config(text=f"Playlist chargée ({total_songs} musiques) - Affichage optimisé")
                    else:
                        self.music_player.status_bar.config(text=f"Playlist chargée ({total_songs} musiques)")
                        
            except Exception as e:
                print(f"Erreur lors du rafraîchissement asynchrone: {e}")
                if hasattr(self.music_player, 'status_bar'):
                    self.music_player.status_bar.config(text="Erreur lors du chargement de la playlist")


    def get_playlist_navigation_info(self):
            """Retourne des informations sur la navigation dans la playlist pour l'interface"""
            try:
                if len(self.music_player.main_playlist) <= 50:
                    return {
                        'total_songs': len(self.music_player.main_playlist),
                        'current_index': self.music_player.current_index,
                        'windowed': False,
                        'window_info': None
                    }
                
                window_size = 30
                half_window = window_size // 2
                start_index = max(0, self.music_player.current_index - half_window)
                end_index = min(len(self.music_player.main_playlist), self.music_player.current_index + half_window + 1)
                
                return {
                    'total_songs': len(self.music_player.main_playlist),
                    'current_index': self.music_player.current_index,
                    'windowed': True,
                    'window_info': {
                        'start': start_index,
                        'end': end_index,
                        'size': end_index - start_index,
                        'songs_before': start_index,
                        'songs_after': len(self.music_player.main_playlist) - end_index
                    }
                }
            except Exception as e:
                print(f"Erreur lors de la récupération des infos de navigation: {e}")
                return None

    def _preload_metadata_async(self, start_index, end_index):
            """Précharge les métadonnées des chansons dans la fenêtre visible de manière asynchrone"""
            def preload_worker():
                try:
                    for i in range(start_index, min(end_index, len(self.music_player.main_playlist))):
                        if i < len(self.music_player.main_playlist):
                            filepath = self.music_player.main_playlist[i]
                            # Précharger les métadonnées en arrière-plan
                            try:
                                self.music_player._get_audio_metadata(filepath)
                                self.music_player._get_audio_duration(filepath)
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
                playlist_size = len(self.music_player.main_playlist)
                
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

    def _update_canvas_scroll_region(self):
            """Met à jour la région de scroll du canvas pour permettre le scroll avec la molette"""
            try:
                print("_update_canvas_scroll_region appelée")
                # Optimisation: Éviter les mises à jour trop fréquentes
                if hasattr(self.music_player, '_last_scroll_region_update'):
                    current_time = time.time()
                    min_update_interval = 0.05  # 50ms entre les mises à jour
                    if current_time - self.music_player._last_scroll_region_update < min_update_interval:
                        return
                self.music_player._last_scroll_region_update = time.time()
                
                if not (hasattr(self.music_player, 'main_playlist_canvas') and hasattr(self.music_player, 'main_playlist_container')):
                    return
                    
                if not (self.music_player.main_playlist_canvas.winfo_exists() and self.music_player.main_playlist_container.winfo_exists()):
                    return
                
                # Optimisation: Utiliser update_idletasks seulement si nécessaire
                # Vérifier si la taille a changé depuis la dernière mise à jour
                current_width = self.music_player.main_playlist_container.winfo_width()
                current_height = self.music_player.main_playlist_container.winfo_height()
                
                if (not hasattr(self.music_player, '_last_container_size') or 
                    self.music_player._last_container_size != (current_width, current_height)):
                    # Forcer la mise à jour de la géométrie seulement si nécessaire
                    self.music_player.main_playlist_container.update_idletasks()
                    self.music_player._last_container_size = (current_width, current_height)
                
                # Pour le système de fenêtrage, on doit simuler une région de scroll plus grande
                # que ce qui est affiché pour permettre le scroll infini
                children = self.music_player.main_playlist_container.winfo_children()
                children_count = len(children)
                
                if children_count > 0:
                    if USE_NEW_CONFIG:
                        item_height = get_main_playlist_config('item_height_estimate')
                        total_songs = len(self.music_player.main_playlist)
                        enable_dynamic = get_main_playlist_config('enable_dynamic_scroll')
                    else:
                        item_height = 60
                        total_songs = len(self.music_player.main_playlist)
                        enable_dynamic = True
                    
                    # Si le système intelligent est activé, adapter la région de scroll
                    if (USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading') and 
                        hasattr(self.music_player, '_last_window_start') and hasattr(self.music_player, '_last_window_end')):
                        print('_update_canvas_scroll_region 1')
                        
                        # Mode intelligent : région basée sur les éléments chargés uniquement
                        start_index = getattr(self.music_player, '_last_window_start', 0)
                        end_index = getattr(self.music_player, '_last_window_end', children_count)
                        
                        # Hauteur réelle basée sur les éléments effectivement chargés
                        displayed_height = children_count * item_height
                        self.music_player.main_playlist_canvas.configure(scrollregion=(0, 0, 0, displayed_height))
                        
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            print(f"🧠 Scroll region intelligente: {displayed_height}px pour {children_count} éléments chargés ({start_index}-{end_index})")
                            
                    elif enable_dynamic and total_songs > children_count:
                        print('_update_canvas_scroll_region 2')
                        # Mode dynamique : région virtuelle pour toutes les musiques
                        # virtual_height = total_songs * item_height
                        
                        virtual_height = children_count * item_height
                        self.music_player.main_playlist_canvas.configure(scrollregion=(0, 0, 0, virtual_height))
                        
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            print(f"Scroll region virtuelle: {virtual_height}px pour {total_songs} musiques ({children_count} affichées)")
                    else:
                        print('_update_canvas_scroll_region 3')
                        # Région de scroll normale basée sur les éléments affichés
                        displayed_height = children_count * item_height
                        self.music_player.main_playlist_canvas.configure(scrollregion=(0, 0, 0, displayed_height))
                        
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            print(f"Scroll region normale: {displayed_height}px pour {children_count} éléments")
                    
                    # Configurer le système de scroll dynamique unifié
                    # if USE_NEW_CONFIG and get_main_playlist_config('enable_dynamic_scroll'):
                    #     self._setup_dynamic_scroll()
                    # elif enable_dynamic:
                    #     self._setup_dynamic_scroll()
                else:
                    # Pas d'enfants, réinitialiser la région de scroll
                    self.music_player.main_playlist_canvas.configure(scrollregion=(0, 0, 0, 0))
                        
            except Exception as e:
                print(f"Erreur lors de la mise à jour de la région de scroll: {e}")

    def _setup_infinite_scroll(self):
            """Configure le scroll infini pour charger plus d'éléments"""
            try:
                if not hasattr(self.music_player, 'main_playlist_canvas'):
                    return
                
                # Initialiser les variables de state pour le scroll intelligent
                self.music_player._user_is_scrolling = False
                self.music_player._user_scroll_timer = None
                self.music_player._last_current_index = getattr(self.music_player, 'current_index', 0)
                self.music_player._auto_centering = False  # Flag pour éviter les boucles
                
                # Binding pour détecter les changements de position de scroll
                # self.music_player.main_playlist_canvas.bind('<Configure>', self.music_player._on_playlist_canvas_configure)
                
                # IMPORTANT: Binding pour détecter les changements de position de scroll
                # C'est ce qui manquait pour synchroniser l'affichage avec la position de scroll
                def on_scroll_position_change(*args):
                    """Appelée quand la position de scroll change par la souris"""
                    # self._update_display_based_on_scroll_position()
                    print('on_scroll_position_change appelé')
                
                # Connecter le callback à la scrollbar
                if hasattr(self.music_player, 'playlist_scrollbar') and self.music_player.playlist_scrollbar:
                    self.music_player.playlist_scrollbar.configure(command=lambda *args: [
                        self.music_player.main_playlist_canvas.yview(*args),
                        on_scroll_position_change()
                    ])
                
                # Aussi connecter au canvas directement
                # self.music_player.main_playlist_canvas.bind('<MouseWheel>', self.music_player._on_scroll_with_update)
                # self.music_player.main_playlist_canvas.bind('<Button-4>', self.music_player._on_scroll_with_update)  # Linux
                # self.music_player.main_playlist_canvas.bind('<Button-5>', self.music_player._on_scroll_with_update)  # Linux
                    
            except Exception as e:
                print(f"Erreur lors de la configuration du scroll infini: {e}")

    def _setup_dynamic_scroll(self):
            """Configure le système de scroll dynamique unifié (combine infinite et progressive)"""
            print("_setup_dynamic_scroll appelée")
            try:
                if not hasattr(self.music_player, 'main_playlist_canvas'):
                    return
                
                # Vérifier si le système est activé
                if not (USE_NEW_CONFIG and get_main_playlist_config('enable_dynamic_scroll')):
                    return
                
                # Initialiser les variables de state pour le scroll intelligent
                self.music_player._user_is_scrolling = False
                self.music_player._user_scroll_timer = None
                self.music_player._last_current_index = getattr(self.music_player, 'current_index', 0)
                self.music_player._auto_centering = False  # Flag pour éviter les boucles
                
                # Variables pour le chargement progressif
                self.music_player._last_scroll_position = 0.0
                self.music_player._progressive_loading_active = True
                
                # Initialiser les variables de fenêtrage pour la compatibilité
                if not hasattr(self.music_player, '_last_window_start'):
                    self.music_player._last_window_start = 0
                if not hasattr(self.music_player, '_last_window_end'):
                    # Initialiser avec une fenêtre basée sur la position courante
                    current_index = getattr(self.music_player, 'current_index', 0)
                    initial_load = get_main_playlist_config('initial_load_after_current')
                    self.music_player._last_window_end = min(len(self.music_player.main_playlist) if hasattr(self.music_player, 'main_playlist') else 0, 
                                            current_index + initial_load)
                
                # Binding pour détecter les changements de position de scroll
                # def on_dynamic_scroll_change(*args):
                #     """Appelée quand la position de scroll change"""
                #     try:
                #         # Gérer le scroll infini (mise à jour de l'affichage)
                #         self._update_display_based_on_scroll_position()
                        
                #         # Gérer le chargement progressif
                #         self._on_dynamic_scroll()
                        
                #     except Exception as e:
                #         if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                #             print(f"❌ Erreur scroll dynamique: {e}")
                
                # # Connecter le callback à la scrollbar
                # if hasattr(self.music_player, 'playlist_scrollbar') and self.music_player.playlist_scrollbar:
                #     self.music_player.playlist_scrollbar.config(command=lambda *args: [
                #         self.music_player.main_playlist_canvas.yview(*args),
                #         on_dynamic_scroll_change()
                #     ])
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print("✅ Système de scroll dynamique configuré")
                    
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"❌ Erreur configuration scroll dynamique: {e}")

    def _on_dynamic_scroll(self, event):
            """Gère le scroll dynamique (combine infinite et progressive)"""
            try:
                print("_on_dynamic_scroll appelée")
                if not (USE_NEW_CONFIG and get_main_playlist_config('enable_dynamic_scroll')):
                    return
                
                # Vérifier la position de scroll
                try:
                    # Obtenir la position de scroll actuelle (0.0 = haut, 1.0 = bas)
                    scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
                    scroll_position = scroll_bottom  # Position vers le bas
                    
                    # Seuil de déclenchement pour le chargement progressif
                    threshold = get_main_playlist_config('scroll_trigger_threshold')
                    
                    # Si on atteint le seuil, charger plus d'éléments (chargement progressif)
                    # if scroll_position >= threshold:
                    #     self.music_player._load_more_on_scroll()
                    
                    # Vérifier si on doit charger plus d'éléments en haut ou en bas (scroll infini)
                    scroll_threshold = get_main_playlist_config('scroll_threshold')
                    
                    # Vérifier les verrous de chargement
                    loading_up = getattr(self.music_player, '_loading_up_in_progress', False)
                    loading_down = getattr(self.music_player, '_loading_down_in_progress', False)
                    
                    if scroll_top <= scroll_threshold and not loading_up:
                        # Proche du haut, charger plus d'éléments au-dessus (si pas déjà en cours)
                        if hasattr(event, 'delta') and event.delta:
                            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                                print("🔼 Déclenchement chargement vers le haut")
                                if event.delta >= 0:
                                    self._load_more_songs_above()
                    
                    
                    elif scroll_bottom >= (1.0 - scroll_threshold) and not loading_down:
                        # Proche du bas, charger plus d'éléments en-dessous (si pas déjà en cours)
                        if hasattr(event, 'delta') and event.delta:
                            if event.delta <= 0:
                                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                                    print("🔽 Déclenchement chargement vers le bas")
                                self._load_more_songs_below()
                    
                    elif loading_up or loading_down:
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            direction = "haut" if loading_up else "bas"
                            print(f"⏸️ Chargement vers le {direction} en cours, scroll ignoré")
                        
                        # self.music_player.main_playlist_canvas.yview()
                        # self.music_player.main_playlist_canvas.yview_scroll(0, "units")


                    # Sauvegarder la position pour la prochaine fois
                    self.music_player._last_scroll_position = scroll_position
                    
                except Exception as e:
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"❌ Erreur position scroll dynamique: {e}")
                        
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"❌ Erreur scroll dynamique: {e}")

# def _on_scroll_with_update(self.music_player, event):
#         """Gère le scroll avec mise à jour de l'affichage"""
#         try:
#             print('scroooolll')
#             # Marquer que l'utilisateur est en train de scroller (sauf si c'est un auto-centering)
#             if not getattr(self.music_player, '_auto_centering', False):
#                 self._mark_user_scrolling()
            
#             # Appeler d'abord le scroll normal
#             if hasattr(self.music_player, '_on_mousewheel'):
#                 self.music_player._on_mousewheel(event, self.music_player.main_playlist_canvas)
            
#             # Puis mettre à jour l'affichage basé sur la nouvelle position
#             self.music_player.root.after(50, self._update_display_based_on_scroll_position)
            
#             # Déclencher le smart reload si la position de vue a significativement changé
#             self.music_player.root.after(100, self.music_player._check_smart_reload_on_scroll)
            
#         except Exception as e:
#             if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
#                 print(f"Erreur lors du scroll avec mise à jour: {e}")

    def _update_display_based_on_scroll_position(self):
            """Met à jour l'affichage des musiques basé sur la position de scroll"""
            try:
                if not (hasattr(self.music_player, 'main_playlist_canvas') and self.music_player.main_playlist_canvas.winfo_exists()):
                    return
                
                if not (USE_NEW_CONFIG and get_main_playlist_config('enable_dynamic_scroll')):
                    return
                
                # Obtenir la position actuelle du scroll (0.0 à 1.0)
                try:
                    scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
                except:
                    return
                
                # Calculer quelle partie de la playlist devrait être visible
                total_songs = len(self.music_player.main_playlist)
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
                current_start = getattr(self.music_player, '_last_window_start', -1)
                current_end = getattr(self.music_player, '_last_window_end', -1)
                
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
            print("_update_windowed_display est appelé NONONONON")
            return
            """Met à jour l'affichage avec une nouvelle fenêtre"""
            try:
                # Sauvegarder les nouveaux paramètres de fenêtre
                self.music_player._last_window_start = start_index
                self.music_player._last_window_end = end_index
                
                # Vider le container actuel
                for child in self.music_player.main_playlist_container.winfo_children():
                    child.destroy()
                
                # Ajouter les nouveaux éléments
                for i in range(start_index, end_index):
                    if i < len(self.music_player.main_playlist):
                        filepath = self.music_player.main_playlist[i]
                        self._add_main_playlist_item(filepath, song_index=i)
                
                # Remettre en surbrillance la chanson en cours si elle est visible
                if (hasattr(self.music_player, 'current_index') and 
                    start_index <= self.music_player.current_index < end_index):
                    try:
                        # Trouver le frame correspondant à current_index
                        children = self.music_player.main_playlist_container.winfo_children()
                        relative_index = self.music_player.current_index - start_index
                        if 0 <= relative_index < len(children):
                            self.select_playlist_item(children[relative_index], auto_scroll=False)
                    except:
                        pass
                
                # Mettre à jour la région de scroll
                self.music_player.root.after(10, self._update_canvas_scroll_region)
                
            except Exception as e:
                print(f"Erreur lors de la mise à jour de l'affichage fenêtré: {e}")

    def _mark_user_scrolling(self):
            """Marque que l'utilisateur est en train de scroller manuellement"""
            try:
                print("_mark_user_scrolling est appelé")
                if not (USE_NEW_CONFIG and get_main_playlist_config('detect_manual_scroll')):
                    return
                
                self.music_player._user_is_scrolling = True
                
                # Annuler le timer précédent s'il existe
                if self.music_player._user_scroll_timer:
                    self.music_player.root.after_cancel(self.music_player._user_scroll_timer)
                
                # Programmer un nouveau timer
                timeout = get_main_playlist_config('user_scroll_timeout') if USE_NEW_CONFIG else 3000
                self.music_player._user_scroll_timer = self.music_player.root.after(timeout, self._on_user_scroll_timeout)
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print("Utilisateur scroll manuellement détecté")
                    
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Erreur lors du marquage du scroll utilisateur: {e}")

    def _on_user_scroll_timeout(self):
            """Appelée quand l'utilisateur a fini de scroller"""
            try:
                self.music_player._user_is_scrolling = False
                self.music_player._user_scroll_timer = None
                
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
                if not hasattr(self.music_player, 'current_index'):
                    return
                
                # Vérifier si la chanson courante a changé
                current_index = self.music_player.current_index
                last_index = getattr(self.music_player, '_last_current_index', current_index)
                
                if current_index != last_index:
                    # La chanson a changé, décider si on doit recentrer
                    if self._should_recenter_on_song_change():
                        self._auto_center_on_current_song()
                    
                    # Mettre à jour l'index de référence
                    self.music_player._last_current_index = current_index
                    
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Erreur lors de la vérification de recentrage: {e}")

    def _should_recenter_on_song_change(self):
            """Détermine si on doit recentrer sur la nouvelle chanson courante"""
            try:
                if not (USE_NEW_CONFIG and get_main_playlist_config('auto_center_on_song_change')):
                    return False
                
                # Si l'utilisateur n'a pas scrollé ou a fini de scroller
                if not self.music_player._user_is_scrolling:
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
                if not hasattr(self.music_player, 'current_index') or self.music_player._auto_centering:
                    return
                
                current_index = self.music_player.current_index
                total_songs = len(self.music_player.main_playlist)
                
                if not (0 <= current_index < total_songs):
                    return
                
                # Marquer qu'on fait un auto-centering pour éviter de déclencher le scroll utilisateur
                self.music_player._auto_centering = True
                
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
                    self.music_player.main_playlist_canvas.yview_moveto(scroll_position)
                    
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"Scroll positionné à {scroll_position:.3f}")
                
                # Marquer qu'on a fini l'auto-centering
                self.music_player.root.after(100, lambda: setattr(self.music_player, '_auto_centering', False))
                    
            except Exception as e:
                self.music_player._auto_centering = False
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Erreur lors de l'auto-recentrage: {e}")

    def _calculate_smart_window(self):
            """Calcule la fenêtre intelligente à garder chargée"""
            try:
                if not (USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading')):
                    return None, None
                
                total_songs = len(self.music_player.main_playlist)
                if total_songs == 0:
                    return 0, 0
                
                current_index = getattr(self.music_player, 'current_index', 0)
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
                if not hasattr(self.music_player, 'main_playlist_canvas') or not self.music_player.main_playlist_canvas.winfo_exists():
                    return None
                
                # Obtenir la position de scroll actuelle
                try:
                    scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
                    scroll_center = (scroll_top + scroll_bottom) / 2
                except:
                    return None
                
                # Convertir en index de musique
                total_songs = len(self.music_player.main_playlist)
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
                # Nouveau système dynamique activé ?
                # if USE_NEW_CONFIG and get_main_playlist_config('enable_dynamic_scroll'):
                # return self._progressive_load_system()
                return self._load_more_songs_below()
                
                # # Ancien système fenêtré (si encore activé)
                # if USE_NEW_CONFIG and get_main_playlist_config('enable_smart_loading'):
                #     return self.music_player._old_smart_load_system()
                    
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"❌ Erreur système de chargement: {e}")



    def _progressive_load_system(self):
            """NOUVEAU SYSTÈME : Chargement progressif (jamais de déchargement)"""
            try:
                if not self.music_player.main_playlist:
                    return
                    
                current_index = getattr(self.music_player, 'current_index', 0)
                total_songs = len(self.music_player.main_playlist)
                
                # Sécurité: Index valide
                current_index = max(0, min(current_index, total_songs - 1))
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"🎵 PROGRESSIVE LOAD: Position courante {current_index}")
                    
                # Vérifier ce qui est déjà chargé
                currently_loaded = len(self.music_player.main_playlist_container.winfo_children()) if hasattr(self.music_player, 'main_playlist_container') else 0
                
                # Calculer combien charger (courante + X suivantes)
                initial_load = get_main_playlist_config('initial_load_after_current')
                target_end = min(total_songs, current_index + initial_load)
                # Premier chargement depuis la chanson courante
                start_from = current_index
                
                if currently_loaded == 0:
                    # Premier chargement : depuis la chanson courante
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"🆕 Premier chargement progressif: {start_from} à {target_end-1}")
                else:
                    # Vérifier si on doit charger plus
                    last_loaded = self.music_player._get_last_loaded_index()
                    if last_loaded >= target_end:
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            print(f"✅ Chargement déjà suffisant (jusqu'à {last_loaded})")
                        return
                    start_from = last_loaded
                    
                # Charger de start_from jusqu'à target_end SANS décharger l'existant
                self._append_progressive_items(start_from, target_end)
                
                # Mettre à jour les variables de fenêtrage pour la compatibilité
                if not hasattr(self.music_player, '_last_window_start'):
                    self.music_player._last_window_start = start_from
                if not hasattr(self.music_player, '_last_window_end') or self.music_player._last_window_end < target_end:
                    self.music_player._last_window_end = target_end
                
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"❌ Erreur chargement progressif: {e}")
                
    def _get_last_loaded_index(self):
            """Trouve le dernier index chargé dans la playlist"""
            try:
                children = self.music_player.main_playlist_container.winfo_children()
                if not children:
                    return getattr(self.music_player, 'current_index', 0)
                    
                max_index = 0
                for child in children:
                    if hasattr(child, 'song_index'):
                        max_index = max(max_index, child.song_index)
                        
                return max_index + 1
                
            except Exception:
                return getattr(self.music_player, 'current_index', 0)
            
    def _append_progressive_items(self, start_index, end_index):
            print("_update_windowed_display appelée")
            return
            """Ajoute des éléments progressivement SANS supprimer les existants"""
            try:
                if start_index >= end_index or start_index >= len(self.music_player.main_playlist):
                    return
                    
                loaded_count = 0
                
                for i in range(start_index, min(end_index, len(self.music_player.main_playlist))):
                    if not self._is_index_already_loaded(i):
                        filepath = self.music_player.main_playlist[i]
                        try:
                            self._add_main_playlist_item(filepath, song_index=i)
                            loaded_count += 1
                        except Exception as e:
                            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                                print(f"⚠️ Erreur chargement item {i}: {e}")
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll') and loaded_count > 0:
                    print(f"✅ {loaded_count} nouveaux éléments chargés ({start_index}-{end_index-1})")
                    total_loaded = len(self.music_player.main_playlist_container.winfo_children())
                    print(f"📊 Total chargé: {total_loaded}/{len(self.music_player.main_playlist)}")
                    
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"❌ Erreur append progressif: {e}")
                
    def _is_index_already_loaded(self, index):
            """Vérifie si un index spécifique est déjà chargé"""
            try:
                children = self.music_player.main_playlist_container.winfo_children()
                for child in children:
                    if hasattr(child, 'song_index') and child.song_index == index:
                        return True
                return False
            except Exception:
                return False

    def _setup_progressive_scroll_detection(self):
            """Configure la détection de scroll pour le chargement progressif"""
            try:
                if not (USE_NEW_CONFIG and get_main_playlist_config('enable_dynamic_scroll')):
                    return
                    
                if not (hasattr(self.music_player, 'main_playlist_canvas') and self.music_player.main_playlist_canvas):
                    return
                
                # Nous n'utilisons plus de binding direct ici
                # Le chargement progressif est maintenant géré par _check_infinite_scroll
                # qui est appelé après chaque événement de scroll
                    
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"❌ Erreur config scroll progressif: {e}")

# def _on_progressive_scroll(self.music_player, event=None):
#         """Gère le scroll pour le chargement progressif"""
#         try:
#             print("_on_progressive_scroll appelé")
#             if not (USE_NEW_CONFIG and get_main_playlist_config('enable_dynamic_scroll')):
#                 return
            
#             # Vérifier la position de scroll
#             try:
#                 # Obtenir la position de scroll actuelle (0.0 = haut, 1.0 = bas)
#                 scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
#                 scroll_position = scroll_bottom  # Position vers le bas
                
#                 # Seuil de déclenchement (90% vers le bas par défaut)
#                 threshold = get_main_playlist_config('scroll_trigger_threshold')
                
#                 # Si on atteint le seuil, charger plus d'éléments
#                 if scroll_position >= threshold:
#                     print("self.music_player.main_playlist_is_loading_more_items ", self.music_player.main_playlist_is_loading_more_items)
#                     if not self.music_player.main_playlist_is_loading_more_items:                        
#                         self.music_player._load_more_on_scroll()
#                         self.music_player._check_and_unload_items(self.music_player.current_index)
#                         self.music_player.main_playlist_is_loading_more_items = True
                        
                        
                        
                        

#             except Exception as e:
#                 print(f"❌ Erreur lors du scroll progressif: {e}")

#         except Exception:
#             pass

    def _load_more_on_scroll(self):
            """Charge plus d'éléments quand on scroll vers le bas"""
            try:
                return
                # if not self.music_player.main_playlist:
                #     return
                
                # # Trouver le dernier élément chargé
                # last_loaded = self.music_player._get_last_loaded_index() - 1  # -1 car get_last_loaded_index retourne l'index suivant
                # total_songs = len(self.music_player.main_playlist)
                
                # # Si on a déjà tout chargé, ne rien faire
                # if last_loaded >= total_songs - 1:
                #     if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                #         print("✅ Toutes les musiques déjà chargées")
                #     return
                
                # # Calculer combien charger de plus
                # load_more_count = get_main_playlist_config('load_more_count')
                # start_from = last_loaded + 1
                # end_at = min(total_songs, start_from + load_more_count)
                
                self._load_more_songs_below()
                
                
                # if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                #     print(f"📈 SCROLL LOAD MORE: Charger {start_from} à {end_at-1} (+{end_at-start_from} musiques)")
                
                # # Charger les éléments supplémentaires
                # self._append_progressive_items(start_from, end_at)
                
                # # Mettre à jour la région de scroll pour refléter les nouveaux éléments
                # self.music_player.root.after(10, self._update_canvas_scroll_region)
                
                # def reset_main_playlist_is_loading_more_items():
                #     self.music_player.main_playlist_is_loading_more_items = False
                # self.music_player.root.after(MAIN_PLAYLIST_REST_TIMER_AFTER_LOADING, reset_main_playlist_is_loading_more_items)

                # self._extend_window_down(end_at)
                def reset_main_playlist_is_loading_more_items():
                    self.music_player.main_playlist_is_loading_more_items = False
                self.music_player.root.after(MAIN_PLAYLIST_REST_TIMER_AFTER_LOADING, reset_main_playlist_is_loading_more_items)
            except Exception as e:
                # if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"❌ Erreur chargement supplémentaire: {e}")

    def _force_reload_window(self, start_index, end_index):
            print("_force_reload_window appelé")
            return
            """Force le rechargement d'une fenêtre spécifique - PROTECTION INDEX"""
            try:
                # SÉCURITÉ : Valider les paramètres d'entrée
                if not self.music_player.main_playlist:
                    return
                    
                total_songs = len(self.music_player.main_playlist)
                
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
                    children = self.music_player.main_playlist_container.winfo_children()
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
                    if 0 <= i < len(self.music_player.main_playlist):
                        filepath = self.music_player.main_playlist[i]
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
                    non_charges = len(self.music_player.main_playlist) - charges
                    if non_charges > 0:
                        print(f"🎯 {non_charges} éléments NON chargés (optimisation mémoire)")
                
                # Étape 3: Remettre en surbrillance la chanson courante
                self._highlight_current_song_in_window(start_index, end_index)
                
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"❌ Erreur force reload: {e}")

    def _highlight_current_song_in_window(self, start_index, end_index):
            """Remet en surbrillance la chanson courante si elle est dans la fenêtre"""
            print("_highlight_current_song_in_window appelé PAS UTILSIEE")
            return
            try:
                current_index = getattr(self.music_player, 'current_index', 0)
                
                if start_index <= current_index < end_index:
                    widgets = self.music_player.main_playlist_container.winfo_children()
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
                current_index = getattr(self.music_player, 'current_index', 0)
                
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
                    
                    children = self.music_player.main_playlist_container.winfo_children()
                    for i, child in enumerate(children):
                        # Calculer l'index réel de cet enfant
                        real_index = current_start + i
                        if real_index in items_to_unload:
                            child.destroy()
                
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Erreur déchargement: {e}")

    def _load_required_items(self, target_start, target_end, current_start, current_end):
            print("_load_required_items appelé")
            return
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
                    for child in self.music_player.main_playlist_container.winfo_children():
                        child.destroy()
                    
                    # Charger tous les éléments dans la nouvelle fenêtre
                    for i in range(target_start, target_end):
                        if i < len(self.music_player.main_playlist):
                            filepath = self.music_player.main_playlist[i]
                            self._add_main_playlist_item(filepath, song_index=i)
                    
                    # Remettre en surbrillance la chanson courante si visible
                    current_index = getattr(self.music_player, 'current_index', 0)
                    if target_start <= current_index < target_end:
                        try:
                            children = self.music_player.main_playlist_container.winfo_children()
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
            print('non')
            return
    
    def on_canvas_scroll(self):
        self._update_visible_items()


    def _check_infinite_scroll(self, event):
            print("_check_infinite_scroll appelé")
            return
            """Vérifie si on doit charger plus d'éléments en haut ou en bas"""
            try:
                # Optimisation: Éviter les appels trop fréquents
                if hasattr(self.music_player, '_last_infinite_check_time'):
                    current_time = time.time()
                    if current_time - self.music_player._last_infinite_check_time < 0.1:  # 100ms entre les vérifications
                        return
                    self.music_player._last_infinite_check_time = current_time
                else:
                    self.music_player._last_infinite_check_time = time.time()
                
                if not (hasattr(self.music_player, 'main_playlist_canvas') and self.music_player.main_playlist_canvas.winfo_exists()):
                    return
                
                # Vérifier si on doit utiliser le chargement dynamique
                if USE_NEW_CONFIG and get_main_playlist_config('enable_dynamic_scroll'):
                    # Appeler la fonction de chargement dynamique
                    self._on_dynamic_scroll(event)
                
                # # Vérifier si on doit utiliser le scroll infini
                # if not (USE_NEW_CONFIG and get_main_playlist_config('enable_infinite_scroll')):
                #     return
                
                # # Obtenir la position actuelle du scroll
                # try:
                #     scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
                # except Exception:
                #     return
                
                # threshold = get_main_playlist_config('scroll_threshold') if USE_NEW_CONFIG else 0.1
                
                # # Vérifier si on est proche du haut (charger des éléments précédents)
                # if scroll_top <= threshold:
                #     self.music_player._load_more_songs_above()
                
                # # Vérifier si on est proche du bas (charger des éléments suivants)
                # elif scroll_bottom >= (1.0 - threshold):
                #     self.music_player._load_more_songs_below()
                    
            except Exception as e:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Erreur lors de la vérification du scroll infini: {e}")

    def _load_more_songs_above(self):
            """Charge plus de musiques au-dessus de la fenêtre actuelle"""
            try:
                # Protection contre les chargements en boucle
                if getattr(self.music_player, '_loading_up_in_progress', False):
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print("⚠️ Chargement vers le haut déjà en cours, ignoré")
                    return
                
                if not hasattr(self.music_player, '_last_window_start'):
                    return
                
                current_start = self.music_player._last_window_start
                if current_start <= 0:
                    return  # Déjà au début
                
                # Marquer le chargement vers le haut en cours
                self.music_player._loading_up_in_progress = True
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print("🔒 Verrouillage scroll vers le haut activé")
                
                load_count = get_main_playlist_config('load_more_count') if USE_NEW_CONFIG else 10
                new_start = max(0, current_start - load_count)
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Chargement de {load_count} musiques au-dessus (index {new_start} à {current_start})")
                
                # Étendre la fenêtre vers le haut
                self._extend_window_up(new_start)
                
                # Réinitialiser le verrou après un délai
                def reset_loading_up_flag():
                    self.music_player._loading_up_in_progress = False
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print("🔓 Verrouillage scroll vers le haut désactivé")
                
                # Délai pour éviter les chargements répétés
                self.music_player.root.after(MAIN_PLAYLIST_REST_TIMER_AFTER_LOADING, reset_loading_up_flag)
                
                # def reset_main_playlist_is_loading_more_items():
                #     self.music_player.main_playlist_is_loading_more_items = False
                # self.music_player.root.after(MAIN_PLAYLIST_REST_TIMER_AFTER_LOADING, reset_main_playlist_is_loading_more_items)
                
            except Exception as e:
                print(f"Erreur lors du chargement des musiques au-dessus: {e}")

    def _load_more_songs_below(self, unload=False):
            """Charge plus de musiques en-dessous de la fenêtre actuelle"""
            print("_load_more_songs_below appelé")
            try:
                # Protection contre les chargements en boucle
                if getattr(self.music_player, '_loading_down_in_progress', False):
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print("⚠️ Chargement vers le bas déjà en cours, ignoré")
                    return
                
                if not hasattr(self.music_player, '_last_window_end'):
                    return
                
                current_end = self.music_player._last_window_end
                if current_end >= len(self.music_player.main_playlist):
                    return  # Déjà à la fin
                
                # Marquer le chargement vers le bas en cours
                self.music_player._loading_down_in_progress = True
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print("🔒 Verrouillage scroll vers le bas activé")
                
                load_count = get_main_playlist_config('load_more_count') if USE_NEW_CONFIG else 10
                new_end = min(len(self.music_player.main_playlist), current_end + load_count)
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"Chargement de {load_count} musiques en-dessous (index {current_end} à {new_end})")
                
                # Étendre la fenêtre vers le bas
                self._extend_window_down(new_end)
                if unload:
                    self._check_and_unload_items(self.music_player.current_index)

                print("_load_more_songs_below appelé", current_end, load_count, new_end)
                
                # Réinitialiser le verrou après un délai
                def reset_loading_down_flag():
                    self.music_player._loading_down_in_progress = False
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print("🔓 Verrouillage scroll vers le bas désactivé")
                
                # Délai pour éviter les chargements répétés
                self.music_player.root.after(MAIN_PLAYLIST_REST_TIMER_AFTER_LOADING, reset_loading_down_flag)

            except Exception as e:
                print(f"Erreur lors du chargement des musiques en-dessous: {e}")

    def _extend_window_up(self, new_start):
            print("_extend_window_up appelé")
            return
            """Étend la fenêtre d'affichage vers le haut"""
            try:
                if not hasattr(self.music_player, '_last_window_start') or not hasattr(self.music_player, '_last_window_end'):
                    return
                
                current_start = self.music_player._last_window_start
                current_end = self.music_player._last_window_end
                
                # Ajouter les nouveaux éléments au début dans l'ordre croissant
                # pour maintenir l'ordre chronologique correct
                items_added = 0
                for i in range(new_start, current_start):
                    if i < len(self.music_player.main_playlist):
                        items_added +=1
                        filepath = self.music_player.main_playlist[i]
                        self._add_main_playlist_item_at_position(filepath, song_index=i, position='top')
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            print(f"  → Ajout élément {i} au début")
                
                # Mettre à jour les paramètres de fenêtre
                self.music_player._last_window_start = new_start
                
                # Réorganiser tous les éléments dans l'ordre correct
                self._reorder_playlist_items()
                
                # Mettre à jour la région de scroll
                self._update_canvas_scroll_region()
                
                # Ajuster légèrement le scroll pour éviter les rechargements immédiats
                # (approche simple comme pour le scroll vers le bas)
                # items_added = current_start - new_start
                # self._simple_scroll_adjustment_after_top_load(items_added)
                
                self._adjust_scroll_after_top_load(items_added)
                
            except Exception as e:
                print(f"Erreur lors de l'extension vers le haut: {e}")

    def _extend_window_down(self, new_end):
            """Étend la fenêtre d'affichage vers le bas"""
            print("_extend_window_down appelée")
            return
            try:
                print("_extend_window_down appelée")
                if not hasattr(self.music_player, '_last_window_start') or not hasattr(self.music_player, '_last_window_end'):
                    print("_last_window_start ou _last_window_end manquant")
                    return
                
                current_start = self.music_player._last_window_start
                current_end = self.music_player._last_window_end
                
                # Ajouter les nouveaux éléments à la fin
                for i in range(current_end, new_end):
                    if i < len(self.music_player.main_playlist):
                        filepath = self.music_player.main_playlist[i]
                        # self._add_main_playlist_item_at_position(filepath, song_index=i, position='bottom')
                        self._add_main_playlist_item(filepath, song_index=i)
                
                # Mettre à jour les paramètres de fenêtre
                self.music_player._last_window_end = new_end
                
                # Mettre à jour la région de scroll
                # self._update_canvas_scroll_region()
                
                
            except Exception as e:
                print(f"Erreur lors de l'extension vers le bas: {e}")

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
            children = self.music_player.main_playlist_container.winfo_children()
            if not children:
                return
                
            # Déterminer si l'utilisateur regarde au-dessus de la musique actuelle
            user_looking_above = self._is_user_looking_above_current(current_index)
            
            # Collecter les widgets à décharger
            widgets_to_unload = []
            
            for widget in children:
                if hasattr(widget, 'song_index'):
                    widget_index = widget.song_index
                    
                    if widget_index < current_index:
                        # Musique avant la musique actuelle
                        if user_looking_above:
                            # L'utilisateur regarde au-dessus, garder quelques musiques au-dessus
                            keep_above = 0  # Garder 3 musiques au-dessus
                            if widget_index < current_index - keep_above:
                                widgets_to_unload.append(widget)
                                print(f"DEBUG: Déchargement de l'élément {widget_index} (trop loin au-dessus)")
                        else:
                            # L'utilisateur ne regarde pas au-dessus, décharger toutes les musiques avant
                            keep_above = 0  # Garder 0 musiques au-dessus
                            if widget_index < current_index - keep_above:
                                widgets_to_unload.append(widget)
                                print(f"DEBUG: Déchargement de l'élément {widget_index} (avant la musique actuelle)")
            
            # Décharger les widgets sélectionnés
            if widgets_to_unload:
                unload_count = len(widgets_to_unload) + keep_above
                print(f"DEBUG: Déchargement de {unload_count} éléments (utilisateur regarde au-dessus: {user_looking_above})")
                
                # Sauvegarder la position de scroll actuelle avant déchargement
                try:
                    scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
                    current_scroll_position = scroll_top
                    print(f"DEBUG: Position scroll avant déchargement: {current_scroll_position}")
                except:
                    current_scroll_position = 0.0
                
                # Calculer le nombre d'éléments déchargés du haut
                items_unloaded_from_top = 0
                min_unloaded_index = float('inf')
                max_unloaded_index = -1
                
                for widget in widgets_to_unload:
                    if hasattr(widget, 'song_index'):
                        widget_index = widget.song_index
                        min_unloaded_index = min(min_unloaded_index, widget_index)
                        max_unloaded_index = max(max_unloaded_index, widget_index)
                        
                # Décharger les widgets
                for widget in widgets_to_unload:
                    if widget.winfo_exists():
                        widget.destroy()
                
                # Mettre à jour les variables de fenêtrage si nécessaire
                if hasattr(self.music_player, '_last_window_start') and min_unloaded_index != float('inf'):
                    # Ajuster le début de la fenêtre si on a déchargé des éléments du début
                    if min_unloaded_index <= self.music_player._last_window_start:
                        new_start = max_unloaded_index + 1
                        print(f"DEBUG: Ajustement _last_window_start: {self.music_player._last_window_start} → {new_start}")
                        self.music_player._last_window_start = new_start
                
                # Invalider le cache des index chargés
                try:
                    self.music_player._invalidate_loaded_indexes_cache()
                except Exception as e:
                    print(f"DEBUG: Erreur invalidation cache: {e}")
                    self.music_player._loaded_indexes_cache = set()
                
                # Ajuster la position du scroll après déchargement
                self._adjust_scroll_after_unload(unload_count, current_scroll_position)
                
            else:
                print(f"DEBUG: Aucun élément à décharger")
                
                
        except Exception as e:
            print(f"DEBUG: Erreur déchargement intelligent: {e}")
            import traceback
            traceback.print_exc()

    def _adjust_scroll_after_unload(self, unload_count, previous_scroll_position):
        """Ajuste la position du scroll après déchargement d'éléments"""
        try:
            if not hasattr(self.music_player, 'main_playlist_canvas') or not self.music_player.main_playlist_canvas.winfo_exists():
                return
                
            print(f"DEBUG: Ajustement scroll après déchargement de {unload_count} éléments")
            
            # Mettre à jour la région de scroll d'abord
            # self.._update_canvas_scroll_region()
            
            # Attendre que la mise à jour soit effective
            self.music_player.main_playlist_container.update_idletasks()
            
            # Calculer la nouvelle position de scroll
            # Quand on supprime des éléments du haut, il faut remonter le scroll proportionnellement
            children = self.music_player.main_playlist_container.winfo_children()
            current_children_count = len(children)
            
            if current_children_count > 0:
                # Estimer la hauteur d'un élément
                item_height = get_main_playlist_config('item_height_estimate') if USE_NEW_CONFIG else 60
                
                # Calculer le décalage causé par la suppression des éléments
                # Si on a supprimé N éléments du haut, il faut remonter le scroll de N * hauteur_élément
                total_height_removed = unload_count * item_height
                
                # Obtenir la hauteur totale actuelle de la région de scroll
                try:
                    scroll_region = self.music_player.main_playlist_canvas.cget('scrollregion')
                    if scroll_region:
                        # Format: "x1 y1 x2 y2"
                        parts = scroll_region.split()
                        if len(parts) >= 4:
                            total_height = float(parts[3])
                            
                            # Calculer le pourcentage de décalage
                            if total_height > 0:
                                scroll_offset_ratio = total_height_removed / total_height
                                
                                # Ajuster la position de scroll
                                new_scroll_position = max(0.0, previous_scroll_position - scroll_offset_ratio)
                                
                                print(f"DEBUG: Ajustement scroll - Hauteur supprimée: {total_height_removed}px, "
                                    f"Hauteur totale: {total_height}px, "
                                    f"Position: {previous_scroll_position} → {new_scroll_position}")
                                
                                # Appliquer la nouvelle position
                                self.music_player.main_playlist_canvas.yview_moveto(new_scroll_position)
                                
                            else:
                                print("DEBUG: Hauteur totale nulle, pas d'ajustement")
                        else:
                            print("DEBUG: Format scrollregion invalide")
                    else:
                        print("DEBUG: Pas de scrollregion définie")
                        
                except Exception as e:
                    print(f"DEBUG: Erreur calcul ajustement scroll: {e}")
                    # Fallback: essayer de maintenir une position relative
                    try:
                        self.music_player.main_playlist_canvas.yview_moveto(max(0.0, previous_scroll_position * 0.9))
                    except:
                        pass
            else:
                print("DEBUG: Aucun enfant restant, scroll en haut")
                self.music_player.main_playlist_canvas.yview_moveto(0.0)
                
        except Exception as e:
            print(f"DEBUG: Erreur ajustement scroll après déchargement: {e}")

    def _adjust_scroll_after_top_load(self, items_added):
        """Ajuste la position du scroll après chargement d'éléments au début"""
        try:
            if not hasattr(self.music_player, 'main_playlist_canvas') or not self.music_player.main_playlist_canvas.winfo_exists():
                return
                
            if items_added <= 0:
                return
                
            print(f"DEBUG: Ajustement scroll après chargement de {items_added} éléments au début")
            
            # Mettre à jour la région de scroll d'abord
            # self._update_canvas_scroll_region()
            
            # Attendre que la mise à jour soit effective
            self.music_player.main_playlist_container.update_idletasks()
            
            # Calculer la nouvelle position de scroll
            # Quand on supprime des éléments du haut, il faut remonter le scroll proportionnellement
            children = self.music_player.main_playlist_container.winfo_children()
            current_children_count = len(children)
            
            # Obtenir la position de scroll actuelle
            try:
                scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
                current_scroll_position = scroll_top
                
                print(f"DEBUG: Position scroll avant ajustement: {current_scroll_position}")
                
                # Mettre à jour la région de scroll d'abord
                # self._update_canvas_scroll_region()
                
                # # Attendre que la mise à jour soit effective
                # self.music_player.main_playlist_container.update_idletasks()
                
                # Calculer le décalage nécessaire
                # Estimer la hauteur d'un élément
                item_height = get_main_playlist_config('item_height_estimate') if USE_NEW_CONFIG else 60
                
                # Calculer la hauteur totale ajoutée
                total_height_added = items_added * item_height
                
                # Obtenir la hauteur totale actuelle de la région de scroll
                scroll_region = self.music_player.main_playlist_canvas.cget('scrollregion')
                if scroll_region:
                    # Format: "x1 y1 x2 y2"
                    parts = scroll_region.split()
                    if len(parts) >= 4:
                        total_height = float(parts[3])
                        
                        if total_height > 0:
                            # Calculer le pourcentage de décalage
                            scroll_offset_ratio = total_height_added / total_height
                            
                            print(f"DEBUG: Décalage nécessaire: {scroll_offset_ratio}")
                            
                            # Ajuster la position de scroll vers le bas
                            new_scroll_position = min(1.0, current_scroll_position + scroll_offset_ratio)
                            
                            print(f"DEBUG: Ajustement scroll - Hauteur ajoutée: {total_height_added}px, "
                                f"Hauteur totale: {total_height}px, "
                                f"Position: {current_scroll_position} → {new_scroll_position}")
                            
                            # Appliquer la nouvelle position avec un petit délai pour s'assurer que tout est mis à jour
                            # def apply_scroll_adjustment():
                            #     try:
                            #         self.music_player.main_playlist_canvas.yview_moveto(new_scroll_position)
                            #         print(f"DEBUG: Scroll ajusté à {new_scroll_position}")
                            #     except Exception as e:
                            #         print(f"DEBUG: Erreur application scroll: {e}")
                            
                            # # Appliquer l'ajustement après un court délai
                            # self.music_player.root.after(10, apply_scroll_adjustment)
                            self.music_player.main_playlist_canvas.yview_moveto(new_scroll_position)
                            
                        else:
                            print("DEBUG: Hauteur totale nulle, pas d'ajustement")
                    else:
                        print("DEBUG: Format scrollregion invalide")
                else:
                    print("DEBUG: Pas de scrollregion définie")
                    
            except Exception as e:
                print(f"DEBUG: Erreur calcul ajustement scroll après chargement haut: {e}")
                
        except Exception as e:
            print(f"DEBUG: Erreur ajustement scroll après chargement haut: {e}")

    def _simple_scroll_adjustment_after_top_load(self, items_added):
        """Ajustement simple du scroll après chargement vers le haut (comme pour le bas)"""
        try:
            if not hasattr(self.music_player, 'main_playlist_canvas') or not self.music_player.main_playlist_canvas.winfo_exists():
                return
                
            if items_added <= 0:
                return
                
            # Obtenir la position actuelle
            scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
            
            # Obtenir le seuil de déclenchement
            threshold = get_main_playlist_config('scroll_threshold') if USE_NEW_CONFIG else 0.1
            
            if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                print(f"DEBUG: Ajustement simple - Position actuelle: {scroll_top:.4f}, Seuil: {threshold}")
            
            # Si on est encore dans la zone de déclenchement, faire un petit ajustement
            if scroll_top <= threshold:
                # Ajustement minimal pour sortir de la zone de déclenchement
                # Juste assez pour éviter un rechargement immédiat
                new_position = threshold + 0.02  # Un peu au-dessus du seuil
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"DEBUG: Ajustement minimal: {scroll_top:.4f} → {new_position:.4f}")
                
                # Appliquer l'ajustement avec un délai
                def apply_minimal_adjustment():
                    try:
                        self.music_player.main_playlist_canvas.yview_moveto(new_position)
                        if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                            print(f"DEBUG: Scroll ajusté minimalement à {new_position:.4f}")
                    except Exception as e:
                        print(f"DEBUG: Erreur ajustement minimal: {e}")
                
                self.music_player.root.after(50, apply_minimal_adjustment)
            else:
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    print(f"DEBUG: Pas d'ajustement nécessaire (position {scroll_top:.4f} > seuil {threshold})")
                
        except Exception as e:
            print(f"DEBUG: Erreur ajustement simple scroll: {e}")

    def _is_user_looking_above_current(self, current_index):
        """Détermine si l'utilisateur regarde au-dessus de la musique actuelle"""
        try:
            # Obtenir la position de scroll actuelle
            scroll_top, scroll_bottom = self.music_player.main_playlist_canvas.yview()
            
            # Estimer l'index du premier élément visible
            total_items = len(self.music_player.main_playlist)
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

    def _add_main_playlist_item_at_position(self, filepath, song_index=None, position='bottom'):
            print("_add_main_playlist_item_at_position appelée")
            return
            """Ajoute un élément de playlist à une position spécifique (top ou bottom)"""
            try:
                if position == 'bottom':
                    # Pour le bas, utiliser la fonction normale
                    return self._add_main_playlist_item(filepath, song_index=song_index)
                
                elif position == 'top':
                    # Pour le haut, simplement créer l'élément
                    # L'ordre sera corrigé par _reorder_playlist_items() après
                    item_frame = self._add_main_playlist_item(filepath, song_index=song_index)
                    
                    if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                        print(f"  → Élément {song_index} ajouté (ordre sera corrigé)")
                    
                    return item_frame
                
            except Exception as e:
                print(f"Erreur lors de l'ajout d'élément à la position {position}: {e}")
                return None

    def _reorder_playlist_items(self):
            """Réorganise tous les éléments de la playlist dans l'ordre correct basé sur song_index"""
            try:
                if not hasattr(self.music_player, 'main_playlist_container') or not self.music_player.main_playlist_container.winfo_exists():
                    return
                
                # Récupérer tous les enfants avec leur song_index
                children = list(self.music_player.main_playlist_container.winfo_children())
                indexed_children = []
                
                for child in children:
                    if hasattr(child, 'song_index'):
                        indexed_children.append((child.song_index, child))
                    else:
                        # Enfant sans index, le garder à la fin
                        indexed_children.append((float('inf'), child))
                
                # Trier par song_index
                indexed_children.sort(key=lambda x: x[0])
                
                if USE_NEW_CONFIG and get_main_playlist_config('debug_scroll'):
                    order_before = [child.song_index if hasattr(child, 'song_index') else '?' for child in children]
                    order_after = [x[0] if x[0] != float('inf') else '?' for x in indexed_children]
                    print(f"  → Réorganisation: {order_before} → {order_after}")
                
                # Réorganiser les widgets
                for i, (song_index, child) in enumerate(indexed_children):
                    # Déplacer chaque widget à sa position correcte
                    child.pack_forget()
                    if i == 0:
                        # Premier élément
                        child.pack(fill='x', pady=2, padx=5)
                    else:
                        # Insérer après l'élément précédent
                        prev_child = indexed_children[i-1][1]
                        child.pack(fill='x', pady=2, padx=5, after=prev_child)
                
            except Exception as e:
                print(f"Erreur lors de la réorganisation des éléments: {e}")

    def _create_playlist_item_frame(self, filepath, song_index=None):
            """Crée un frame pour un élément de playlist"""
            print("_create_playlist_item_frame appelée")
            return
            try:
                # Utiliser la fonction existante qui maintenant retourne le frame
                frame = self._add_main_playlist_item(filepath, song_index=song_index)
                return frame
                
            except Exception as e:
                print(f"Erreur lors de la création du frame: {e}")
                return None
