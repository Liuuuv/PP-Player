from __init__ import *

def _reset_stats(self):
    """Remet à zéro toutes les statistiques"""
    if messagebox.askyesno("Réinitialiser les statistiques", 
                            "Êtes-vous sûr de vouloir remettre à zéro toutes les statistiques ?"):
        self.stats = {
            'songs_played': 0,
            'total_listening_time': 0.0,
            'searches_count': 0,
            'current_song_start_time': None,
            'current_song_listened_time': 0.0,
            'current_song_duration': 0.0,
            'played_songs': set()
        }
        self.save_config()
        self.status_bar.config(text="Statistiques réinitialisées")

def _update_current_song_stats(self):
    """Met à jour les statistiques de la chanson en cours"""
    try:
        if (self.stats['current_song_start_time'] is not None and 
            self.main_playlist and 
            self.current_index < len(self.main_playlist)):
            
            current_song = self.main_playlist[self.current_index]
            
            # Calculer le temps écouté depuis le début de la chanson
            if not self.paused and pygame.mixer.music.get_busy():
                elapsed_time = time.time() - self.stats['current_song_start_time']
                self.stats['current_song_listened_time'] += elapsed_time
                self.stats['total_listening_time'] += elapsed_time
                self.stats['current_song_start_time'] = time.time()
            
            # Vérifier si la chanson a été écoutée à 70% ou plus
            if (self.stats['current_song_duration'] > 0 and 
                self.stats['current_song_listened_time'] >= self.stats['current_song_duration'] * 0.7 and
                current_song not in self.stats['played_songs']):
                
                self.stats['songs_played'] += 1
                self.stats['played_songs'].add(current_song)
                # Sauvegarder immédiatement quand une chanson est comptée comme lue
                self.save_config()
                
    except Exception as e:
        print(f"Erreur mise à jour stats: {e}")
