import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier library_tab
from library_tab import *

def _search_artist_videos_with_id(self):
        """Recherche les vidéos de l'artiste depuis l'onglet Vidéos de sa chaîne"""
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.artist_search_cancelled:
                return
            
            if not self.current_artist_channel_id:
                return
            
            # Vérifier le cache d'abord
            cache_key = self.current_artist_channel_id
            if cache_key in self.artist_cache and 'videos' in self.artist_cache[cache_key]:
                cached_videos = self.artist_cache[cache_key]['videos']
                self.root.after(0, lambda: self._display_artist_videos(cached_videos))
                return
            
            # Configuration pour extraire les vidéos de la chaîne (extract_flat=True pour avoir la durée)
            search_opts = {
                'extract_flat': True,  # Plus efficace et contient la durée
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                all_videos = []
                
                # Utiliser l'ID de chaîne trouvé
                base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
                videos_url = base_channel_url + '/videos'
                
                try:
                    channel_info = ydl.extract_info(videos_url, download=False)
                    if self.artist_search_cancelled:
                        return
                    
                    if channel_info and 'entries' in channel_info:
                        videos = list(channel_info['entries'])
                        # Filtrer et garder seulement les vidéos valides
                        videos = [v for v in videos if v and v.get('id')]
                        if videos:
                            all_videos.extend(videos[:30])  # Prendre les 30 premières
                        else:
                            pass
                    else:
                        pass
                except Exception as e:
                    self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des vidéos"))
                    return
                
                # Supprimer les doublons et préparer pour l'affichage
                unique_videos = {}
                for video in all_videos:
                    video_id = video.get('id', '')
                    if video_id and video_id not in unique_videos:
                        # S'assurer que les champs nécessaires sont présents
                        if not video.get('webpage_url') and video_id:
                            video['webpage_url'] = f"https://www.youtube.com/watch?v={video_id}"
                        unique_videos[video_id] = video
                
                final_videos = list(unique_videos.values())
                
                # Trier par date de sortie (les plus récentes d'abord) si disponible
                def get_upload_date(video):
                    upload_date = video.get('upload_date', '0')
                    try:
                        return int(upload_date) if upload_date.isdigit() else 0
                    except:
                        return 0
                
                final_videos.sort(key=get_upload_date, reverse=True)
                
                # Limiter à 15 vidéos max
                final_videos = final_videos[:15]
                
                # Vérifier annulation avant affichage
                if not self.artist_search_cancelled:
                    # Sauvegarder en cache
                    cache_key = self.current_artist_channel_id
                    if cache_key not in self.artist_cache:
                        self.artist_cache[cache_key] = {}
                    self.artist_cache[cache_key]['videos'] = final_videos
                    
                    # Afficher les résultats dans l'interface
                    self.root.after(0, lambda: self._display_artist_videos(final_videos))
                    
        except Exception as e:
            self.root.after(0, lambda: self._display_videos_error(str(e)))

