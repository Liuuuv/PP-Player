import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier library_tab
from library_tab import *

def _search_artist_releases_with_id(self):
        """Recherche les albums et singles de l'artiste depuis l'onglet releases"""
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.artist_search_cancelled:
                return
            
            if not self.current_artist_channel_id:
                return
            
            # Vérifier le cache d'abord
            cache_key = self.current_artist_channel_id
            if cache_key in self.artist_cache and 'releases' in self.artist_cache[cache_key]:
                cached_releases = self.artist_cache[cache_key]['releases']
                self.root.after(0, lambda: self._display_artist_releases(cached_releases))
                return
                
            # Options pour extraire les releases de la chaîne
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                all_playlists = []
                
                # Utiliser l'ID de chaîne trouvé
                base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
                releases_url = base_channel_url + '/releases'
                print(f"Extraction des releases depuis: {releases_url}")
                
                try:
                    channel_info = ydl.extract_info(releases_url, download=False)
                    
                    if channel_info and 'entries' in channel_info:
                        playlists = list(channel_info['entries'])
                        print(f"Nombre de releases trouvées: {len(playlists)}")
                        # Garder seulement les vraies playlists/releases
                        valid_playlists = []
                        for p in playlists:
                            if self.artist_search_cancelled:
                                return
                            if p and p.get('id'):
                                # Vérifier si c'est vraiment une playlist
                                if (p.get('_type') == 'playlist' or 
                                    'playlist' in p.get('url', '') or 
                                    'list=' in p.get('url', '') or
                                    p.get('playlist_count', 0) > 0):
                                    valid_playlists.append(p)
                                    # print(f"Release valide: {p.get('title', 'Sans titre')} - {p.get('playlist_count', 0)} vidéos")
                        
                        all_playlists.extend(valid_playlists[:15])  # Prendre les 15 premières
                    else:
                        print("Aucune release trouvée sur la chaîne")
                except Exception as e:
                    print(f"Erreur extraction releases de la chaîne: {e}")
                    self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des releases"))
                    return
                
                # Supprimer les doublons basés sur l'ID
                unique_playlists = {}
                for playlist in all_playlists:
                    playlist_id = playlist.get('id', '')
                    if playlist_id and playlist_id not in unique_playlists:
                        # S'assurer que les champs nécessaires sont présents
                        if not playlist.get('webpage_url') and playlist_id:
                            playlist['webpage_url'] = f"https://www.youtube.com/playlist?list={playlist_id}"
                            playlist['_type'] = 'playlist'
                        unique_playlists[playlist_id] = playlist
                
                final_playlists = list(unique_playlists.values())  # Toutes les releases
                
                # Vérifier annulation avant affichage
                if not self.artist_search_cancelled:
                    # Sauvegarder en cache
                    cache_key = self.current_artist_channel_id
                    if cache_key not in self.artist_cache:
                        self.artist_cache[cache_key] = {}
                    self.artist_cache[cache_key]['releases'] = final_playlists
                    
                    # Afficher les résultats dans l'interface
                    self.root.after(0, lambda: self._display_artist_releases(final_playlists))
                    
        except Exception as e:
            print(f"Erreur recherche releases artiste: {e}")
            self.root.after(0, lambda: self._display_releases_error(str(e)))

