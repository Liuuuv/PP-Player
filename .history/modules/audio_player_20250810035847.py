"""
Lecteur audio pour Pipi Player
Extrait de main.py pour améliorer la lisibilité
"""

def play_pause(self):
    """Lecture/pause de la musique"""
    import pygame
    
    if not self.main_playlist:
        return
        
    if pygame.mixer.music.get_busy() and not self.paused:
        pygame.mixer.music.pause()
        self.paused = True
        if hasattr(self, 'play_button'):
            if hasattr(self, 'icons') and "play" in self.icons:
                self.play_button.config(image=self.icons["play"])
            self.play_button.config(text="Play")
    elif self.paused:
        pygame.mixer.music.play(start=self.current_time)
        self.base_position = self.current_time
        self.paused = False
        if hasattr(self, 'play_button'):
            if hasattr(self, 'icons') and "pause" in self.icons:
                self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")
    else:
        self.paused = False
        if hasattr(self, 'play_button'):
            if hasattr(self, 'icons') and "pause" in self.icons:
                self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")
        self.play_track()

def play_track(self):
    """Joue la piste actuelle"""
    try:
        import pygame
        import os
        import time
        from mutagen.mp3 import MP3
        
        if not self.main_playlist or self.current_index >= len(self.main_playlist):
            return
            
        song = self.main_playlist[self.current_index]
        
        # Vérifier que le fichier existe
        if not os.path.exists(song):
            print(f"Fichier introuvable: {song}")
            return
            
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(start=0)
        self.base_position = 0
        
        # Charger l'offset de volume spécifique à cette musique
        self.volume_offset = self.volume_offsets.get(song, 0)
        
        # Mettre à jour le slider d'offset si il existe
        if hasattr(self, 'volume_offset_slider'):
            self.volume_offset_slider.set(self.volume_offset)
        
        # Appliquer le volume avec l'offset
        self._apply_volume()
        
        self.paused = False
        
        # Mettre à jour les boutons
        if hasattr(self, 'play_button'):
            if hasattr(self, 'icons') and "pause" in self.icons:
                self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")
        
        # Mettre à jour les informations de la chanson
        try:
            audio = MP3(song)
            self.song_length = audio.info.length
            
            if hasattr(self, 'progress'):
                self.progress.config(to=self.song_length)
            
            if hasattr(self, 'song_length_label'):
                self.song_length_label.config(text=time.strftime(
                    '%M:%S', time.gmtime(self.song_length))
                )
            
            if hasattr(self, 'song_label'):
                self.song_label.config(text=os.path.basename(song))
                
        except Exception as e:
            print(f"Erreur lecture métadonnées: {e}")
            self.song_length = 0
        
        # Mettre à jour la barre de statut
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"Lecture: {os.path.basename(song)}")
        elif hasattr(self, 'status_bar'):
            self.status_bar.config(text="Playing")

    except Exception as e:
        print(f"Erreur lecture: {e}")
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"Erreur: {str(e)}")
        elif hasattr(self, 'status_bar'):
            self.status_bar.config(text=f"Erreur: {str(e)}")

def next_track(self):
    """Passe à la piste suivante"""
    if not self.main_playlist:
        return
    
    if self.current_index < len(self.main_playlist) - 1:
        self.current_index += 1
    else:
        # Si on est à la fin, revenir au début selon le mode de boucle
        if self.loop_mode == 1:  # Loop playlist
            self.current_index = 0
        else:
            return  # Ne pas jouer si pas en mode loop
    
    self.play_track()

def prev_track(self):
    """Passe à la piste précédente"""
    if not self.main_playlist:
        return
    
    if self.current_index > 0:
        self.current_index -= 1
    else:
        # Si on est au début, aller à la fin selon le mode de boucle
        if self.loop_mode == 1:  # Loop playlist
            self.current_index = len(self.main_playlist) - 1
        else:
            return  # Ne pas jouer si pas en mode loop
    
    self.play_track()

def set_volume(self, volume):
    """Définit le volume global"""
    self.volume = float(volume)
    self._apply_volume()
    
    # Sauvegarder la configuration si on n'est pas en initialisation
    if not getattr(self, 'initializing', False):
        self.save_config()

def set_volume_offset(self, offset):
    """Définit l'offset de volume pour la chanson actuelle"""
    if not self.main_playlist or self.current_index >= len(self.main_playlist):
        return
    
    song = self.main_playlist[self.current_index]
    self.volume_offset = float(offset)
    self.volume_offsets[song] = self.volume_offset
    
    self._apply_volume()
    
    # Sauvegarder la configuration si on n'est pas en initialisation
    if not getattr(self, 'initializing', False):
        self.save_config()

def _apply_volume(self):
    """Applique le volume avec l'offset"""
    import pygame
    
    # Calculer le volume final (global + offset)
    final_volume = self.volume + (self.volume_offset / 100.0)
    
    # S'assurer que le volume reste dans les limites [0, 1]
    final_volume = max(0.0, min(1.0, final_volume))
    
    # Appliquer le volume
    pygame.mixer.music.set_volume(final_volume)

def update_time(self):
    """Thread de mise à jour du temps de lecture"""
    import time
    import pygame
    
    while True:
        try:
            if pygame.mixer.music.get_busy() and not self.paused and not self.user_dragging:
                # Calculer le temps actuel
                self.current_time = self.base_position + (time.time() - pygame.mixer.music.get_pos() / 1000.0)
                
                # Mettre à jour la barre de progression
                if hasattr(self, 'progress') and self.song_length > 0:
                    self.progress.set(self.current_time)
                
                # Mettre à jour le label de temps
                if hasattr(self, 'current_time_label'):
                    self.current_time_label.config(text=time.strftime(
                        '%M:%S', time.gmtime(self.current_time))
                    )
                
                # Vérifier si la chanson est terminée
                if self.current_time >= self.song_length:
                    if self.loop_mode == 2:  # Loop chanson actuelle
                        self.play_track()
                    else:
                        self.next_track()
            
            time.sleep(0.1)  # Mise à jour 10 fois par seconde
            
        except Exception as e:
            print(f"Erreur update_time: {e}")
            time.sleep(1)

def toggle_random_mode(self):
    """Active/désactive le mode aléatoire"""
    self.random_mode = not self.random_mode
    
    if hasattr(self, 'random_button'):
        if self.random_mode:
            self.random_button.config(bg="#4a8fe7")
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Mode aléatoire activé")
        else:
            self.random_button.config(bg="#3d3d3d")
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Mode aléatoire désactivé")

def toggle_loop_mode(self):
    """Cycle entre les modes de boucle"""
    self.loop_mode = (self.loop_mode + 1) % 3
    
    if hasattr(self, 'loop_button'):
        if self.loop_mode == 0:
            # Pas de boucle
            self.loop_button.config(bg="#3d3d3d")
            if hasattr(self, 'icons') and "loop" in self.icons:
                self.loop_button.config(image=self.icons["loop"])
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Mode boucle désactivé")
        elif self.loop_mode == 1:
            # Loop playlist
            self.loop_button.config(bg="#4a8fe7")
            if hasattr(self, 'icons') and "loop" in self.icons:
                self.loop_button.config(image=self.icons["loop"])
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Mode boucle playlist activé")
        elif self.loop_mode == 2:
            # Loop chanson actuelle
            self.loop_button.config(bg="#4a8fe7")
            if hasattr(self, 'icons') and "loop1" in self.icons:
                self.loop_button.config(image=self.icons["loop1"])
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Mode boucle chanson activé")

def set_position(self, position):
    """Définit la position de lecture"""
    import pygame
    
    if self.song_length > 0:
        self.current_time = float(position)
        self.base_position = self.current_time
        
        # Redémarrer la lecture à la nouvelle position
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.play(start=self.current_time)

def _update_volume_sliders(self):
    """Met à jour les sliders de volume avec les valeurs chargées"""
    # Mettre à jour le slider de volume global
    if hasattr(self, 'volume_slider'):
        self.volume_slider.set(self.volume)
    
    # Mettre à jour le slider d'offset de volume
    if hasattr(self, 'volume_offset_slider'):
        self.volume_offset_slider.set(self.volume_offset)