import tkinter as tk
from config import*

class DragDropHandler:
    """Gestionnaire universel pour le drag-and-drop de musiques vers la playlist"""
    
    def __init__(self, music_player):
        self.music_player = music_player
        
    def setup_drag_drop(self, frame, file_path=None, video_data=None, item_type="file"):
        """
        Configure le drag-and-drop pour un frame
        
        Args:
            frame: Le frame tkinter à configurer
            file_path: Chemin du fichier (pour les fichiers locaux)
            video_data: Données vidéo (pour les résultats YouTube)
            item_type: Type d'élément ("file", "youtube", "playlist_item")
        """
        # Variables pour le drag
        frame.drag_start_x = 0
        frame.drag_start_y = 0
        frame.is_dragging = False
        frame.drag_enabled = False  # Désactivé par défaut
        frame.original_bg = frame.cget('bg') if hasattr(frame, 'cget') else '#4a4a4a'
        frame.add_icon_label = None
        frame.drag_file_path = file_path
        frame.drag_video_data = video_data
        frame.drag_item_type = item_type

        # Bindings pour le drag (bouton gauche et droit)
        frame.bind("<B1-Motion>", lambda e: self._on_drag_motion(e, frame))
        frame.bind("<ButtonRelease-1>", lambda e: self._on_drag_release(e, frame))
        frame.bind("<B3-Motion>", lambda e: self._on_drag_motion(e, frame))
        frame.bind("<ButtonRelease-3>", lambda e: self._on_drag_release(e, frame))
        
        # Trouver tous les widgets enfants et leur ajouter les bindings
        self._setup_child_bindings(frame)
    
    def _setup_child_bindings(self, parent_frame):
        """Configure les bindings pour tous les widgets enfants"""
        for child in parent_frame.winfo_children():
            if isinstance(child, (tk.Label, tk.Frame)):
                child.bind("<B1-Motion>", lambda e, f=parent_frame: self._on_drag_motion(e, f))
                child.bind("<ButtonRelease-1>", lambda e, f=parent_frame: self._on_drag_release(e, f))
                child.bind("<B3-Motion>", lambda e, f=parent_frame: self._on_drag_motion(e, f))
                child.bind("<ButtonRelease-3>", lambda e, f=parent_frame: self._on_drag_release(e, f))
                # Récursif pour les frames imbriquées
                if isinstance(child, tk.Frame):
                    self._setup_child_bindings(child)
    
    def setup_drag_start(self, event, frame):
        """Initialise le début du drag (à appeler dans les handlers de clic)"""
        frame.drag_start_x = event.x_root
        frame.drag_start_y = event.y_root
        frame.is_dragging = False
        frame.drag_enabled = True
    
    def disable_drag(self, frame):
        """Désactive le drag pour un frame"""
        if hasattr(frame, 'drag_enabled'):
            frame.drag_enabled = False
    
    def _on_drag_motion(self, event, frame):
        """Gère le mouvement pendant le drag"""
        if not hasattr(frame, 'drag_start_x') or not hasattr(frame, 'drag_enabled'):
            return
            
        # Ne pas traiter le drag si il n'a pas été activé
        if not frame.drag_enabled:
            return
            
        # Calculer la distance de drag
        dx = event.x_root - frame.drag_start_x
        dy = event.y_root - frame.drag_start_y
        distance = (dx**2 + dy**2)**0.5
        
        # Commencer le drag seulement après un certain seuil
        if distance > 10 and not frame.is_dragging:
            frame.is_dragging = True
            self._start_visual_drag(frame)
        
        if frame.is_dragging:
            # Mettre à jour l'effet visuel
            self._update_drag_visual(frame, dx, dy)
    
    def _on_drag_release(self, event, frame):
        """Gère la fin du drag"""
        if hasattr(frame, 'is_dragging') and frame.is_dragging:
            # Calculer la distance de drag
            dx = event.x_root - frame.drag_start_x
            
            # Si on a dragué suffisamment vers la droite (plus de 100 pixels)
            if dx > 100:
                # Ajouter à la playlist selon le type d'élément
                self._add_dragged_item_to_playlist(frame)
            # Si on a dragué suffisamment vers la gauche (moins de -100 pixels)
            elif dx < -100:
                # Placer en premier dans la queue selon le type d'élément
                self._add_to_queue_first_dragged_item(frame)
            
            # Remettre l'apparence normale
            self._end_visual_drag(frame)
            frame.is_dragging = False
        
        # Désactiver le drag après le relâchement
        if hasattr(frame, 'drag_enabled'):
            frame.drag_enabled = False
    
    def _start_visual_drag(self, frame):
        """Démarre l'effet visuel de drag"""
        # Changer la couleur de fond pour indiquer le drag (frame et tous ses enfants)
        self._set_frame_colors(frame, '#5a5a5a')
    
    def _update_drag_visual(self, frame, dx, dy):
        """Met à jour l'effet visuel pendant le drag"""
        # Changer la couleur selon la distance et la direction
        if dx > 100:  # Drag vers la droite - ajouter à la playlist
            self._set_frame_colors(frame, '#4a6a4a')  # Vert pour indiquer l'activation
        elif dx < -100:  # Drag vers la gauche - placer en premier dans la queue
            self._set_frame_colors(frame, '#6a6a4a')  # Jaune-orange pour indiquer "premier dans la queue"
        else:
            self._set_frame_colors(frame, '#5a5a5a')  # Gris pour le drag
    
    def _end_visual_drag(self, frame):
        """Termine l'effet visuel de drag"""
        # Déterminer la couleur appropriée
        target_color = frame.original_bg
        
        # Vérifier si c'est l'élément actuellement sélectionné/en cours de lecture
        if hasattr(frame, 'selected') and frame.selected:
            target_color = '#5a9fd8'  # Couleur bleue de sélection
        elif hasattr(frame, 'filepath') and hasattr(self.music_player, 'main_playlist'):
            # Vérifier si c'est la chanson en cours de lecture
            if (len(self.music_player.main_playlist) > 0 and 
                hasattr(self.music_player, 'current_index') and
                self.music_player.current_index < len(self.music_player.main_playlist) and 
                self.music_player.main_playlist[self.music_player.current_index] == frame.filepath):
                target_color = '#5a9fd8'  # Couleur bleue pour la chanson en cours
        
        self._set_frame_colors(frame, target_color)
    
    def _set_frame_colors(self, frame, color):
        """Change la couleur de fond du frame et de tous ses enfants"""
        # Utiliser la fonction existante du music player si disponible
        if hasattr(self.music_player, '_set_item_colors'):
            self.music_player._set_item_colors(frame, color)
        else:
            # Fallback
            try:
                frame.config(bg=color)
            except:
                pass
    
    def _add_dragged_item_to_playlist(self, frame):
        """Ajoute l'élément dragué à la playlist selon son type"""
        try:
            if frame.drag_item_type == "file":
                # Fichier local
                self._add_file_to_playlist(frame.drag_file_path)
            elif frame.drag_item_type == "youtube":
                # Résultat YouTube
                self._add_youtube_to_playlist(frame.drag_video_data, frame)
            elif frame.drag_item_type == "playlist_item":
                # Élément de playlist (copier vers main playlist)
                self._add_playlist_item_to_main(frame.drag_file_path)
            
        except Exception as e:
            self.music_player.status_bar.config(text=f"Erreur: {str(e)}")
    
    def _add_file_to_playlist(self, file_path):
        """Ajoute un fichier local à la queue (juste après la chanson en cours)"""
        if file_path:
            filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            
            # Ajouter à la queue (juste après la chanson en cours)
            self._add_to_queue(file_path)
            self.music_player.status_bar.config(text=f"Ajouté à la queue: {filename}")
            
            # Marquer que la main playlist ne provient pas d'une playlist
            self.music_player.main_playlist_from_playlist = False
    
    def _add_to_queue(self, file_path):
        """Ajoute un fichier à la queue (juste après la chanson en cours)"""
        if not file_path:
            return
        
        # Vérifier si c'est la musique actuellement en cours de lecture
        is_currently_playing = False
        if (len(self.music_player.main_playlist) > 0 and 
            hasattr(self.music_player, 'current_index') and
            self.music_player.current_index < len(self.music_player.main_playlist) and 
            self.music_player.main_playlist[self.music_player.current_index] == file_path):
            is_currently_playing = True
            
        # Si c'est la musique en cours de lecture, ne rien faire
        if is_currently_playing:
            return
            
        # Vérifier si le fichier est déjà en dernière position de la queue
        if hasattr(self.music_player, 'queue_items') and self.music_player.queue_items:
            # Trouver la dernière position dans la queue
            sorted_queue_indices = sorted(self.music_player.queue_items)
            if sorted_queue_indices:
                last_queue_index = sorted_queue_indices[-1]
                # Vérifier si ce fichier est déjà en dernière position de la queue
                if (last_queue_index < len(self.music_player.main_playlist) and 
                    self.music_player.main_playlist[last_queue_index] == file_path):
                    # Le fichier est déjà en dernière position, ne pas l'ajouter
                    return
            
        # Toujours ajouter le fichier à la fin de la playlist (permet les duplicatas)
        self.music_player.main_playlist.append(file_path)
        song_index = len(self.music_player.main_playlist) - 1  # Index du fichier qu'on vient d'ajouter
        
        # Si une musique joue actuellement, réorganiser pour créer la queue
        if (len(self.music_player.main_playlist) > 0 and 
            hasattr(self.music_player, 'current_index') and
            self.music_player.current_index < len(self.music_player.main_playlist)):
            
            # Calculer la position cible (après la chanson en cours et les autres éléments de la queue)
            target_position = self.music_player.current_index + 1
            
            # Chercher la prochaine position libre dans la queue
            # (après les musiques déjà ajoutées à la queue)
            while (target_position < song_index and
                   hasattr(self.music_player, 'queue_items') and
                   target_position in self.music_player.queue_items):
                target_position += 1
            
            # Déplacer la musique de la fin vers sa position dans la queue
            if song_index != target_position:
                # Retirer la musique de la fin
                moved_file = self.music_player.main_playlist.pop(song_index)
                
                # Insérer à la position cible dans la queue
                self.music_player.main_playlist.insert(target_position, moved_file)
                
                # Mettre à jour les indices de la queue après l'insertion
                if hasattr(self.music_player, 'queue_items'):
                    updated_queue = set()
                    for queue_index in self.music_player.queue_items:
                        if queue_index >= target_position:
                            updated_queue.add(queue_index + 1)  # Incrémenter les indices après la position d'insertion
                        else:
                            updated_queue.add(queue_index)  # Garder tel quel
                    self.music_player.queue_items = updated_queue
            
            # Marquer cette position comme faisant partie de la queue
            if not hasattr(self.music_player, 'queue_items'):
                self.music_player.queue_items = set()
            # Ajouter l'index final de la musique après le déplacement
            final_index = target_position if song_index != target_position else song_index
            self.music_player.queue_items.add(final_index)
            
            # Mettre à jour l'affichage de la playlist
            if hasattr(self.music_player, '_refresh_playlist_display'):
                self.music_player._refresh_playlist_display()
            
            # Mettre à jour l'affichage visuel des téléchargements (barre noire) sans recharger
            if hasattr(self.music_player, '_update_downloads_queue_visual'):
                self.music_player._update_downloads_queue_visual()
    
    def _add_youtube_to_playlist(self, video_data, frame):
        """Ajoute une vidéo YouTube à la playlist (télécharge si nécessaire)"""
        if not video_data:
            return
            
        # Vérifier si déjà en cours de téléchargement
        url = video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={video_data.get('id')}"
        if url in self.music_player.current_downloads:
            self.music_player.status_bar.config(text="Téléchargement déjà en cours...")
            return
        
        # Changer l'apparence pour indiquer le téléchargement
        self.music_player._reset_frame_appearance(frame, TEST_COLOR)

        self.music_player.search_list = [video_data]  # Pour la compatibilité
        video_data['search_frame'] = frame
        try:
            # Télécharger ET ajouter à la queue
            self.music_player.download_selected_youtube(None, add_to_playlist=False)
            title = video_data.get('title', 'Titre inconnu')
            self.music_player.status_bar.config(text=f"Ajout à la queue: {title[:30]}...")
            
            # Marquer cette vidéo pour être ajoutée à la queue après téléchargement
            url = video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={video_data.get('id')}"
            if not hasattr(self.music_player, 'pending_queue_additions'):
                self.music_player.pending_queue_additions = {}
            self.music_player.pending_queue_additions[url] = True
        except Exception as e:
            # En cas d'erreur, remettre l'apparence normale
            try:
                frame.config(bg='#ffcc00')  # Jaune pour erreur
            except:
                pass
    
    def _add_playlist_item_to_main(self, file_path):
        """Ajoute un élément de playlist à la queue"""
        if file_path:
            filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            
            # Ajouter à la queue (juste après la chanson en cours)
            self._add_to_queue(file_path)
            self.music_player.status_bar.config(text=f"Ajouté à la queue: {filename}")
            
            # Marquer que la main playlist ne provient pas d'une playlist
            self.music_player.main_playlist_from_playlist = False
    
    def _play_after_current_dragged_item(self, frame):
        """Lit l'élément dragué après la chanson actuelle selon son type"""
        try:
            if frame.drag_item_type == "file":
                # Fichier local
                self._play_after_current_file(frame.drag_file_path)
            elif frame.drag_item_type == "youtube":
                # Résultat YouTube - télécharger d'abord puis lire
                self._play_after_current_youtube(frame.drag_video_data, frame)
            elif frame.drag_item_type == "playlist_item":
                # Élément de playlist
                self._play_after_current_file(frame.drag_file_path)
            
        except Exception as e:
            self.music_player.status_bar.config(text=f"Erreur: {str(e)}")
    
    def _play_after_current_file(self, file_path):
        """Lit un fichier local après la chanson actuelle"""
        if file_path:
            self.music_player._play_after_current(file_path)
    
    def _play_after_current_youtube(self, video_data, frame):
        """Télécharge et lit une vidéo YouTube après la chanson actuelle"""
        if not video_data:
            return
            
        # Vérifier si déjà en cours de téléchargement
        url = video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={video_data.get('id')}"
        if url in self.music_player.current_downloads:
            self.music_player.status_bar.config(text="Téléchargement déjà en cours...")
            return
        
        # Changer l'apparence pour indiquer le téléchargement
        self.music_player._reset_frame_appearance(frame, '#ff6666')
        
        # Stocker l'information que cette vidéo doit être lue après la chanson actuelle
        if not hasattr(self.music_player, 'pending_play_after_current'):
            self.music_player.pending_play_after_current = {}
        self.music_player.pending_play_after_current[url] = True
        
        self.music_player.search_list = [video_data]  # Pour la compatibilité
        video_data['search_frame'] = frame
        try:
            # Télécharger (sera ajouté à la playlist et lu après la chanson actuelle)
            self.music_player.download_selected_youtube(None, add_to_playlist=False)
            title = video_data.get('title', 'Titre inconnu')
            self.music_player.status_bar.config(text=f"Téléchargement pour lecture après chanson actuelle: {title[:30]}...")
        except Exception as e:
            # En cas d'erreur, remettre l'apparence normale
            try:
                frame.config(bg='#ffcc00')  # Jaune pour erreur
            except:
                pass
    
    def _add_to_queue_first_dragged_item(self, frame):
        """Place l'élément dragué en premier dans la queue selon son type"""
        try:
            if frame.drag_item_type == "file":
                # Fichier local
                self._add_to_queue_first_file(frame.drag_file_path)
            elif frame.drag_item_type == "youtube":
                # Résultat YouTube - télécharger d'abord puis placer en premier dans la queue
                self._add_to_queue_first_youtube(frame.drag_video_data, frame)
            elif frame.drag_item_type == "playlist_item":
                # Élément de playlist
                self._add_to_queue_first_file(frame.drag_file_path)
            
        except Exception as e:
            self.music_player.status_bar.config(text=f"Erreur: {str(e)}")
    
    def _add_to_queue_first_file(self, file_path):
        """Place un fichier local en premier dans la queue"""
        if file_path:
            filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            
            # Placer en premier dans la queue
            self._add_to_queue_first(file_path)
            self.music_player.status_bar.config(text=f"Placé en premier dans la queue: {filename}")
            
            # Marquer que la main playlist ne provient pas d'une playlist
            self.music_player.main_playlist_from_playlist = False
    
    def _add_to_queue_first_youtube(self, video_data, frame):
        """Télécharge et place une vidéo YouTube en premier dans la queue"""
        if not video_data:
            return
            
        # Vérifier si déjà en cours de téléchargement
        url = video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={video_data.get('id')}"
        if url in self.music_player.current_downloads:
            self.music_player.status_bar.config(text="Téléchargement déjà en cours...")
            return
        
        # Changer l'apparence pour indiquer le téléchargement
        self.music_player._reset_frame_appearance(frame, '#ff6666')
        
        # Stocker l'information que cette vidéo doit être placée en premier dans la queue
        if not hasattr(self.music_player, 'pending_queue_first_additions'):
            self.music_player.pending_queue_first_additions = {}
        self.music_player.pending_queue_first_additions[url] = True
        
        self.music_player.search_list = [video_data]  # Pour la compatibilité
        video_data['search_frame'] = frame
        try:
            # Télécharger (sera placé en premier dans la queue après téléchargement)
            self.music_player.download_selected_youtube(None, add_to_playlist=False)
            title = video_data.get('title', 'Titre inconnu')
            self.music_player.status_bar.config(text=f"Téléchargement pour premier dans la queue: {title[:30]}...")
        except Exception as e:
            # En cas d'erreur, remettre l'apparence normale
            try:
                frame.config(bg='#ffcc00')  # Jaune pour erreur
            except:
                pass
    
    def _add_to_queue_first(self, file_path):
        """Place un fichier en premier dans la queue (juste après la chanson en cours)"""
        if not file_path:
            return
            
        # Vérifier si c'est la musique actuellement en cours de lecture
        is_currently_playing = False
        if (len(self.music_player.main_playlist) > 0 and 
            hasattr(self.music_player, 'current_index') and
            self.music_player.current_index < len(self.music_player.main_playlist) and 
            self.music_player.main_playlist[self.music_player.current_index] == file_path):
            is_currently_playing = True
            
        # Si c'est la musique en cours de lecture, ne rien faire
        if is_currently_playing:
            return
            
        # Vérifier si le fichier est déjà en première position de la queue
        if hasattr(self.music_player, 'queue_items') and self.music_player.queue_items:
            # Trouver la première position dans la queue
            sorted_queue_indices = sorted(self.music_player.queue_items)
            if sorted_queue_indices:
                first_queue_index = sorted_queue_indices[0]
                # Vérifier si ce fichier est déjà en première position de la queue
                if (first_queue_index < len(self.music_player.main_playlist) and 
                    self.music_player.main_playlist[first_queue_index] == file_path):
                    # Le fichier est déjà en première position, ne pas l'ajouter
                    return
            
        # Toujours ajouter le fichier à la fin de la playlist (permet les duplicatas)
        self.music_player.main_playlist.append(file_path)
        song_index = len(self.music_player.main_playlist) - 1  # Index du fichier qu'on vient d'ajouter
        
        # Si une musique joue actuellement, réorganiser pour placer en premier dans la queue
        if (len(self.music_player.main_playlist) > 0 and 
            hasattr(self.music_player, 'current_index') and
            self.music_player.current_index < len(self.music_player.main_playlist)):
            
            # Position cible : juste après la chanson en cours (première position de la queue)
            target_position = self.music_player.current_index + 1
            
            # Déplacer la musique de la fin vers la première position de la queue
            if song_index != target_position:
                # Retirer la musique de la fin
                moved_file = self.music_player.main_playlist.pop(song_index)
                
                # Insérer à la première position de la queue
                self.music_player.main_playlist.insert(target_position, moved_file)
                
                # Mettre à jour les indices de la queue après l'insertion
                if hasattr(self.music_player, 'queue_items'):
                    updated_queue = set()
                    for queue_index in self.music_player.queue_items:
                        if queue_index >= target_position:
                            updated_queue.add(queue_index + 1)  # Incrémenter les indices après la position d'insertion
                        else:
                            updated_queue.add(queue_index)  # Garder tel quel
                    self.music_player.queue_items = updated_queue
            
            # Marquer cette position comme faisant partie de la queue
            if not hasattr(self.music_player, 'queue_items'):
                self.music_player.queue_items = set()
            # Ajouter l'index final de la musique après le déplacement
            final_index = target_position if song_index != target_position else song_index
            self.music_player.queue_items.add(final_index)
            
            # Mettre à jour l'affichage de la playlist
            if hasattr(self.music_player, '_refresh_playlist_display'):
                self.music_player._refresh_playlist_display()
            
            # Mettre à jour l'affichage visuel des téléchargements (barre noire) sans recharger
            if hasattr(self.music_player, '_update_downloads_queue_visual'):
                self.music_player._update_downloads_queue_visual()
