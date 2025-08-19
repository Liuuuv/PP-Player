    def _add_main_playlist_item_to_queue(self, file_path):
        """Ajoute un élément de la main playlist à la queue (duplicate si pas la chanson en cours)"""
        if not file_path:
            return
            
        filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
        
        # Vérifier si c'est la chanson actuellement en cours de lecture
        is_current_song = (
            len(self.music_player.main_playlist) > 0 and 
            hasattr(self.music_player, 'current_index') and
            self.music_player.current_index < len(self.music_player.main_playlist) and
            self.music_player.main_playlist[self.music_player.current_index] == file_path
        )
        
        if is_current_song:
            # Si c'est la chanson en cours, comportement normal (déplacer)
            self._add_to_queue(file_path)
            self.music_player.status_bar.config(text=f"Chanson en cours déplacée vers la queue: {filename}")
        else:
            # Si ce n'est pas la chanson en cours, dupliquer dans la queue
            self._duplicate_to_queue(file_path)
            self.music_player.status_bar.config(text=f"Dupliqué dans la queue: {filename}")
        
        # Marquer que la main playlist ne provient pas d'une playlist
        self.music_player.main_playlist_from_playlist = False
    
    def _add_main_playlist_item_to_queue_first(self, file_path):
        """Ajoute un élément de la main playlist en premier dans la queue (duplicate si pas la chanson en cours)"""
        if not file_path:
            return
            
        filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
        
        # Vérifier si c'est la chanson actuellement en cours de lecture
        is_current_song = (
            len(self.music_player.main_playlist) > 0 and 
            hasattr(self.music_player, 'current_index') and
            self.music_player.current_index < len(self.music_player.main_playlist) and
            self.music_player.main_playlist[self.music_player.current_index] == file_path
        )
        
        if is_current_song:
            # Si c'est la chanson en cours, comportement normal (déplacer)
            self._add_to_queue_first(file_path)
            self.music_player.status_bar.config(text=f"Chanson en cours déplacée en premier dans la queue: {filename}")
        else:
            # Si ce n'est pas la chanson en cours, dupliquer en premier dans la queue
            self._duplicate_to_queue_first(file_path)
            self.music_player.status_bar.config(text=f"Dupliqué en premier dans la queue: {filename}")
        
        # Marquer que la main playlist ne provient pas d'une playlist
        self.music_player.main_playlist_from_playlist = False
    
    def _duplicate_to_queue(self, file_path):
        """Duplique un fichier dans la queue (sans le déplacer)"""
        if not file_path:
            return
            
        # Si une musique joue actuellement, insérer la copie dans la queue
        if (len(self.music_player.main_playlist) > 0 and 
            hasattr(self.music_player, 'current_index') and
            self.music_player.current_index < len(self.music_player.main_playlist)):
            
            # Calculer la position cible (après la chanson en cours et les autres éléments de la queue)
            target_position = self.music_player.current_index + 1
            
            # Chercher la prochaine position libre dans la queue
            # (après les musiques déjà ajoutées à la queue)
            while (target_position < len(self.music_player.main_playlist) and
                   hasattr(self.music_player, 'queue_items') and
                   self.music_player.main_playlist[target_position] in self.music_player.queue_items):
                target_position += 1
            
            # Insérer une copie de la musique à la position cible
            self.music_player.main_playlist.insert(target_position, file_path)
            
            # Marquer cette musique comme faisant partie de la queue
            if not hasattr(self.music_player, 'queue_items'):
                self.music_player.queue_items = set()
            self.music_player.queue_items.add(file_path)
            
            # Mettre à jour l'affichage de la playlist
            if hasattr(self.music_player, '_refresh_playlist_display'):
                self.music_player._refresh_playlist_display()
    
    def _duplicate_to_queue_first(self, file_path):
        """Duplique un fichier en premier dans la queue (sans le déplacer)"""
        if not file_path:
            return
            
        # Si une musique joue actuellement, insérer la copie en première position de la queue
        if (len(self.music_player.main_playlist) > 0 and 
            hasattr(self.music_player, 'current_index') and
            self.music_player.current_index < len(self.music_player.main_playlist)):
            
            # Position cible : juste après la chanson en cours (première position de la queue)
            target_position = self.music_player.current_index + 1
            
            # Insérer une copie de la musique à la première position de la queue
            self.music_player.main_playlist.insert(target_position, file_path)
            
            # Marquer cette musique comme faisant partie de la queue
            if not hasattr(self.music_player, 'queue_items'):
                self.music_player.queue_items = set()
            self.music_player.queue_items.add(file_path)
            
            # Mettre à jour l'affichage de la playlist
            if hasattr(self.music_player, '_refresh_playlist_display'):
                self.music_player._refresh_playlist_display()