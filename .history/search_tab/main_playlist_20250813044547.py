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
            
            # Gestionnaire pour initialiser le drag sur clic gauche
            def on_left_button_press(event):
                # Initialiser le drag pour le clic gauche
                self.drag_drop_handler.setup_drag_start(event, item_frame)
                # Appeler aussi le gestionnaire de clic normal
                on_playlist_item_click(event)
                
            # Bindings pour clics simples et doubles
            item_frame.bind("<ButtonPress-1>", on_left_button_press)
            item_frame.bind("<Double-1>", on_playlist_item_double_click)
            thumbnail_label.bind("<ButtonPress-1>", on_left_button_press)
            thumbnail_label.bind("<Double-1>", on_playlist_item_double_click)
            text_frame.bind("<ButtonPress-1>", on_left_button_press)
            text_frame.bind("<Double-1>", on_playlist_item_double_click)
            title_label.bind("<ButtonPress-1>", on_left_button_press)
            title_label.bind("<Double-1>", on_playlist_item_double_click)
            if metadata_text:  # Ajouter le binding pour metadata_label s'il existe
                metadata_label.bind("<ButtonPress-1>", on_left_button_press)
                metadata_label.bind("<Double-1>", on_playlist_item_double_click)
            duration_label.bind("<ButtonPress-1>", on_left_button_press)
            duration_label.bind("<Double-1>", on_playlist_item_double_click)
            
            # Ajouter le binding pour le numéro si il existe
            if show_numbers:
                number_label.bind("<ButtonPress-1>", on_left_button_press)
                number_label.bind("<Double-1>", on_playlist_item_double_click)
            
            # Clic droit pour ouvrir le menu de sélection ou placer après la chanson en cours
            def on_playlist_item_right_click(event):
                # Initialiser le drag pour le clic droit
                self.drag_drop_handler.setup_drag_start(event, item_frame)
                
                # Si on a des éléments sélectionnés, ouvrir le menu de sélection
                if self.selected_items:
                    self.show_selection_menu(event)
                else:
                    # Comportement normal : placer après la chanson en cours
                    self._play_after_current(filepath)
            
            item_frame.bind("<ButtonPress-3>", on_playlist_item_right_click)
            thumbnail_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            text_frame.bind("<ButtonPress-3>", on_playlist_item_right_click)
            title_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            if metadata_text:  # Ajouter le binding pour metadata_label s'il existe
                metadata_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            duration_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            
            if show_numbers:
                number_label.bind("<ButtonPress-3>", on_playlist_item_right_click)
            
            # Configuration du drag-and-drop
            self.drag_drop_handler.setup_drag_drop(
                item_frame, 
                file_path=filepath, 
                item_type="playlist_item"
            )
            
            # CORRECTION: Forcer les bindings de motion après tous les autres bindings
            # pour éviter qu'ils soient écrasés
            def force_motion_bindings():
                widgets_to_fix = [item_frame, thumbnail_label, text_frame, title_label, duration_label]
                if metadata_text:  # Ajouter le label de métadonnées s'il existe
                    widgets_to_fix.append(metadata_label)
                if show_numbers:  # Ajouter le numéro s'il existe
                    widgets_to_fix.append(number_label)
                
                for widget in widgets_to_fix:
                    if widget and widget.winfo_exists():
                        widget.bind("<B1-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f))
                        widget.bind("<ButtonRelease-1>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f))
                        widget.bind("<B3-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f))
                        widget.bind("<ButtonRelease-3>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f))
            
            # Programmer l'exécution après que tous les bindings soient configurés
            # Utiliser un délai pour s'assurer que c'est vraiment appliqué en dernier
            self.root.after(50, force_motion_bindings)
            
            # Tooltip pour expliquer les interactions
            tooltip_text = "Musique de la playlist principale\nDouble-clic: Jouer cette musique\nCtrl + Clic: Ouvrir sur YouTube\nDrag vers la droite: Ajouter à la queue (prochaines musiques)\nDrag vers la gauche: Placer en premier dans la queue\nShift + Clic: Sélection multiple\nClic droit: Placer après la chanson en cours"
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
            print(f"🎯 DEBUG SELECT_PLAYLIST: playlist_container existe et est valide")
            
            # Accès sécurisé aux enfants pour la désélection
            try:
                children_for_deselect = self.playlist_container.winfo_children()
                print(f"🎯 DEBUG SELECT_PLAYLIST: {len(children_for_deselect)} enfants trouvés pour désélection")
            except tk.TclError as e:
                print(f"❌ DEBUG SELECT_PLAYLIST: Erreur accès enfants pour désélection: {e}")
                children_for_deselect = []
                
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
                print(f"🎯 DEBUG SELECT_PLAYLIST: Recherche de l'enfant à l'index {index}")
                try:
                    children = self.playlist_container.winfo_children()
                    print(f"🎯 DEBUG SELECT_PLAYLIST: {len(children)} enfants trouvés pour sélection")
                    if 0 <= index < len(children):
                        item_frame = children[index]
                        print(f"✅ DEBUG SELECT_PLAYLIST: item_frame trouvé à l'index {index}")
                    else:
                        print(f"❌ DEBUG SELECT_PLAYLIST: Index {index} hors limites (0-{len(children)-1})")
                except tk.TclError as e:
                    # Erreur lors de l'accès aux enfants, ignorer
                    print(f"❌ DEBUG SELECT_PLAYLIST: Erreur accès enfants pour sélection: {e}")
                    return
        else:
            print(f"❌ DEBUG SELECT_PLAYLIST: playlist_container n'existe pas ou n'est pas valide")
    except tk.TclError as e:
        # Container détruit, ignorer
        print(f"❌ DEBUG SELECT_PLAYLIST: Erreur container: {e}")
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
                    self.reset_main_playlist()

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

def _clear_main_playlist(self, event=None):
    """Vide complètement la liste de lecture principale (nécessite un double-clic)"""
    if not self.main_playlist:
        self.status_bar.config(text="La liste de lecture est déjà vide")
        return
    
    self.reset_main_playlist()

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
        self.main_playlist.append (filepath)
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