import tkinter as tk

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
        frame.original_bg = frame.cget('bg') if hasattr(frame, 'cget') else '#4a4a4a'
        frame.add_icon_label = None
        frame.drag_file_path = file_path
        frame.drag_video_data = video_data
        frame.drag_item_type = item_type
        
        # Bindings pour le drag
        frame.bind("<B1-Motion>", lambda e: self._on_drag_motion(e, frame))
        frame.bind("<ButtonRelease-1>", lambda e: self._on_drag_release(e, frame))
        
        # Trouver tous les widgets enfants et leur ajouter les bindings
        self._setup_child_bindings(frame)
    
    def _setup_child_bindings(self, parent_frame):
        """Configure les bindings pour tous les widgets enfants"""
        for child in parent_frame.winfo_children():
            if isinstance(child, (tk.Label, tk.Frame)):
                child.bind("<B1-Motion>", lambda e, f=parent_frame: self._on_drag_motion(e, f))
                child.bind("<ButtonRelease-1>", lambda e, f=parent_frame: self._on_drag_release(e, f))
                # Récursif pour les frames imbriquées
                if isinstance(child, tk.Frame):
                    self._setup_child_bindings(child)
    
    def setup_drag_start(self, event, frame):
        """Initialise le début du drag (à appeler dans les handlers de clic)"""
        frame.drag_start_x = event.x_root
        frame.drag_start_y = event.y_root
        frame.is_dragging = False
    
    def _on_drag_motion(self, event, frame):
        """Gère le mouvement pendant le drag"""
        if not hasattr(frame, 'drag_start_x'):
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
            
            # Remettre l'apparence normale
            self._end_visual_drag(frame)
            frame.is_dragging = False
    
    def _start_visual_drag(self, frame):
        """Démarre l'effet visuel de drag"""
        # Changer la couleur de fond pour indiquer le drag (frame et tous ses enfants)
        self._set_frame_colors(frame, '#5a5a5a')
    
    def _update_drag_visual(self, frame, dx, dy):
        """Met à jour l'effet visuel pendant le drag"""
        # Changer la couleur selon la distance
        if dx > 100:  # Seuil pour l'activation
            self._set_frame_colors(frame, '#4a6a4a')  # Vert pour indiquer l'activation
        else:
            self._set_frame_colors(frame, '#5a5a5a')  # Gris pour le drag
    
    def _end_visual_drag(self, frame):
        """Termine l'effet visuel de drag"""
        # Remettre la couleur normale (frame et tous ses enfants)
        self._set_frame_colors(frame, frame.original_bg)
    
    def _set_frame_colors(self, frame, color):
        """Change la couleur de fond du frame et de tous ses enfants"""
        try:
            frame.config(bg=color)
        except:
            pass
        
        # Changer la couleur de tous les widgets enfants
        for child in frame.winfo_children():
            try:
                if hasattr(child, 'config'):
                    # Ne pas changer la couleur des boutons et icônes
                    if not isinstance(child, tk.Button) and not (hasattr(child, 'image') and child.image):
                        child.config(bg=color)
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
            print(f"Erreur lors de l'ajout à la playlist: {e}")
            self.music_player.status_bar.config(text=f"Erreur: {str(e)}")
    
    def _add_file_to_playlist(self, file_path):
        """Ajoute un fichier local à la main playlist"""
        if file_path:
            filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            
            # Si le fichier est déjà dans la playlist
            if file_path in self.music_player.main_playlist:
                # Vérifier si c'est déjà la dernière musique
                if self.music_player.main_playlist[-1] == file_path:
                    self.music_player.status_bar.config(text=f"Déjà en dernière position: {filename}")
                    return
                else:
                    # Retirer de sa position actuelle et ajouter à la fin
                    self.music_player.main_playlist.remove(file_path)
                    # Ajuster l'index courant si nécessaire
                    if hasattr(self.music_player, 'current_index'):
                        current_file = None
                        if (self.music_player.current_index < len(self.music_player.main_playlist) + 1 and 
                            self.music_player.current_index >= 0):
                            # Sauvegarder le fichier actuellement en cours
                            if self.music_player.current_index < len(self.music_player.main_playlist) + 1:
                                # Recalculer l'index après suppression
                                pass
                    
                    self.music_player.main_playlist.append(file_path)
                    self.music_player._refresh_playlist_display()
                    self.music_player.status_bar.config(text=f"Déplacé à la fin: {filename}")
            else:
                # Ajouter normalement
                self.music_player.main_playlist.append(file_path)
                self.music_player._add_main_playlist_item(file_path)
                self.music_player.status_bar.config(text=f"Ajouté à la playlist: {filename}")
            
            # Marquer que la main playlist ne provient pas d'une playlist
            self.music_player.main_playlist_from_playlist = False
    
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
        self.music_player._reset_frame_appearance(frame, '#ff6666')
        
        self.music_player.search_list = [video_data]  # Pour la compatibilité
        video_data['search_frame'] = frame
        try:
            # Télécharger ET ajouter à la playlist
            self.music_player.download_selected_youtube(None, add_to_playlist=True)
            title = video_data.get('title', 'Titre inconnu')
            self.music_player.status_bar.config(text=f"Ajout à la playlist: {title[:30]}...")
        except Exception as e:
            # En cas d'erreur, remettre l'apparence normale
            try:
                frame.config(bg='#ffcc00')  # Jaune pour erreur
            except:
                pass
    
    def _add_playlist_item_to_main(self, file_path):
        """Ajoute un élément de playlist à la main playlist"""
        if file_path and file_path not in self.music_player.main_playlist:
            self.music_player.main_playlist.append(file_path)
            self.music_player._add_main_playlist_item(file_path)
            filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            self.music_player.status_bar.config(text=f"Ajouté à la main playlist: {filename}")
            
            # Marquer que la main playlist ne provient pas d'une playlist
            self.music_player.main_playlist_from_playlist = False
        else:
            filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            self.music_player.status_bar.config(text=f"Déjà dans la main playlist: {filename}")