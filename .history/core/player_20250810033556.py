"""
Gestionnaire de lecture audio
"""
import pygame
import time
import threading
from mutagen.mp3 import MP3
from config.constants import (
    AUDIO_FREQUENCY, AUDIO_SIZE, AUDIO_CHANNELS, AUDIO_BUFFER,
    LOOP_MODE_OFF, LOOP_MODE_PLAYLIST, LOOP_MODE_SONG
)


class AudioPlayer:
    """Gestionnaire de lecture audio avec pygame"""
    
    def __init__(self, playlist_manager, settings):
        self.playlist_manager = playlist_manager
        self.settings = settings
        
        # Initialisation pygame
        pygame.mixer.init()
        pygame.mixer.init(
            frequency=AUDIO_FREQUENCY, 
            size=AUDIO_SIZE, 
            channels=AUDIO_CHANNELS, 
            buffer=AUDIO_BUFFER
        )
        
        # Variables de lecture
        self.current_index = 0
        self.paused = False
        self.song_length = 0
        self.current_time = 0
        self.base_position = 0
        self.user_dragging = False
        
        # Modes de lecture
        self.random_mode = False
        self.loop_mode = LOOP_MODE_OFF
        
        # Callbacks pour l'interface
        self.on_track_changed = None
        self.on_time_updated = None
        self.on_status_changed = None
        
        # Thread de mise à jour du temps
        self.update_thread = threading.Thread(target=self._update_time_loop, daemon=True)
        self.update_thread.start()
    
    def load_track(self, filepath):
        """Charge une piste audio"""
        try:
            pygame.mixer.music.load(filepath)
            
            # Obtenir la durée de la chanson
            try:
                audio = MP3(filepath)
                self.song_length = audio.info.length
            except:
                self.song_length = 0
            
            return True
        except Exception as e:
            print(f"Erreur chargement piste: {e}")
            return False
    
    def play(self, start_pos=0):
        """Lance la lecture"""
        try:
            pygame.mixer.music.play(start=start_pos)
            self.base_position = start_pos
            self.paused = False
            self._apply_volume()
            
            if self.on_status_changed:
                self.on_status_changed("playing")
            
            return True
        except Exception as e:
            print(f"Erreur lecture: {e}")
            return False
    
    def pause(self):
        """Met en pause"""
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            
            if self.on_status_changed:
                self.on_status_changed("paused")
    
    def resume(self):
        """Reprend la lecture"""
        if self.paused:
            pygame.mixer.music.play(start=self.current_time)
            self.base_position = self.current_time
            self.paused = False
            
            if self.on_status_changed:
                self.on_status_changed("playing")
    
    def stop(self):
        """Arrête la lecture"""
        pygame.mixer.music.stop()
        self.paused = False
        self.current_time = 0
        self.base_position = 0
        
        if self.on_status_changed:
            self.on_status_changed("stopped")
    
    def play_pause(self):
        """Bascule entre lecture et pause"""
        if not self.playlist_manager.main_playlist:
            return
            
        if pygame.mixer.music.get_busy() and not self.paused:
            self.pause()
        elif self.paused:
            self.resume()
        else:
            self.play_current_track()
    
    def play_current_track(self):
        """Joue la piste actuelle"""
        if not self.playlist_manager.main_playlist:
            return False
            
        if self.current_index >= len(self.playlist_manager.main_playlist):
            self.current_index = 0
            
        current_track = self.playlist_manager.main_playlist[self.current_index]
        
        if self.load_track(current_track):
            self.play()
            
            if self.on_track_changed:
                self.on_track_changed(current_track, self.current_index)
            
            return True
        return False
    
    def next_track(self):
        """Passe à la piste suivante"""
        if not self.playlist_manager.main_playlist:
            return
        
        if self.loop_mode == LOOP_MODE_SONG:
            # Rejouer la même chanson
            self.play_current_track()
            return
        
        # Passer à la chanson suivante
        if self.current_index < len(self.playlist_manager.main_playlist) - 1:
            self.current_index += 1
        elif self.loop_mode == LOOP_MODE_PLAYLIST:
            # Retour au début de la playlist
            self.current_index = 0
        else:
            # Fin de playlist
            self.stop()
            if self.on_status_changed:
                self.on_status_changed("end_of_playlist")
            return
        
        self.play_current_track()
    
    def previous_track(self):
        """Passe à la piste précédente"""
        if not self.playlist_manager.main_playlist:
            return
        
        if self.current_index > 0:
            self.current_index -= 1
        elif self.loop_mode == LOOP_MODE_PLAYLIST:
            # Aller à la fin de la playlist
            self.current_index = len(self.playlist_manager.main_playlist) - 1
        else:
            self.current_index = 0
        
        self.play_current_track()
    
    def set_position(self, position):
        """Définit la position de lecture (en secondes)"""
        if position < 0:
            position = 0
        elif position > self.song_length:
            position = self.song_length
        
        try:
            if not self.paused:
                pygame.mixer.music.play(start=position)
            self.current_time = position
            self.base_position = position
            self._apply_volume()
        except Exception as e:
            print(f"Erreur set_position: {e}")
    
    def set_volume(self, volume):
        """Définit le volume global (0.0 à 1.0)"""
        self.settings.global_volume = max(0.0, min(1.0, volume))
        self._apply_volume()
        self.settings.save_config()
    
    def _apply_volume(self):
        """Applique le volume avec l'offset spécifique au fichier"""
        if not self.playlist_manager.main_playlist:
            return
            
        current_track = self.playlist_manager.main_playlist[self.current_index]
        offset = self.settings.get_volume_offset(current_track)
        
        final_volume = self.settings.global_volume + (offset / 100)
        final_volume = max(0, min(1, final_volume))
        
        pygame.mixer.music.set_volume(final_volume)
    
    def toggle_random_mode(self):
        """Bascule le mode aléatoire"""
        self.random_mode = not self.random_mode
        
        if self.random_mode:
            self._shuffle_remaining_playlist()
    
    def toggle_loop_mode(self):
        """Bascule entre les modes de boucle"""
        self.loop_mode = (self.loop_mode + 1) % 3
        
        if self.on_status_changed:
            if self.loop_mode == LOOP_MODE_OFF:
                self.on_status_changed("loop_off")
            elif self.loop_mode == LOOP_MODE_PLAYLIST:
                self.on_status_changed("loop_playlist")
            elif self.loop_mode == LOOP_MODE_SONG:
                self.on_status_changed("loop_song")
    
    def _shuffle_remaining_playlist(self):
        """Mélange la suite de la playlist"""
        if len(self.playlist_manager.main_playlist) <= self.current_index + 1:
            return
        
        import random
        
        # Sauvegarder la partie avant la chanson courante (incluse)
        before_current = self.playlist_manager.main_playlist[:self.current_index + 1]
        
        # Récupérer et mélanger la partie après la chanson courante
        after_current = self.playlist_manager.main_playlist[self.current_index + 1:]
        random.shuffle(after_current)
        
        # Reconstituer la playlist
        self.playlist_manager.main_playlist = before_current + after_current
    
    def _update_time_loop(self):
        """Boucle de mise à jour du temps de lecture"""
        while True:
            if pygame.mixer.music.get_busy() and not self.paused and not self.user_dragging:
                self.current_time = self.base_position + pygame.mixer.music.get_pos() / 1000
                
                if self.current_time > self.song_length:
                    self.current_time = self.song_length
                
                # Vérifier si la chanson est terminée
                if self.current_time >= self.song_length and self.song_length > 0:
                    self.next_track()
                
                if self.on_time_updated:
                    self.on_time_updated(self.current_time, self.song_length)
            
            time.sleep(0.1)
    
    def is_playing(self):
        """Retourne True si une piste est en cours de lecture"""
        return pygame.mixer.music.get_busy() and not self.paused
    
    def get_current_track(self):
        """Retourne la piste actuelle"""
        if (self.playlist_manager.main_playlist and 
            0 <= self.current_index < len(self.playlist_manager.main_playlist)):
            return self.playlist_manager.main_playlist[self.current_index]
        return None
    
    def cleanup(self):
        """Nettoie les ressources"""
        pygame.mixer.music.stop()
        pygame.mixer.quit()