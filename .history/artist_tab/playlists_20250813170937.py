import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier library_tab
from library_tab import *

def _search_artist_playlists_with_id(self):
        """Recherche les playlists de l'artiste depuis l'onglet playlists"""  
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.artist_search_cancelled:
                return
            
            if not self.current_artist_channel_id:
                print("Aucun ID de chaîne disponible pour les playlists")
                return
            
            # Vérifier le cache d'abord
            cache_key = self.current_artist_channel_id
            if cache_key in self.artist_cache and 'playlists' in self.artist_cache[cache_key]:
                print("Utilisation du cache pour les playlists")
                cached_playlists = self.artist_cache[cache_key]['playlists']
                self.root.after(0, lambda: self._display_artist_playlists(cached_playlists))
                return
                
            # Options pour extraire les playlists de la chaîne
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
                playlists_url = base_channel_url + '/playlists'
                print(f"Extraction des playlists depuis: {playlists_url}")
                
                try:
                    channel_info = ydl.extract_info(playlists_url, download=False)
                    if self.artist_search_cancelled:
                        return
                    
                    print(f"Channel info type: {type(channel_info)}")
                    if channel_info:
                        print(f"Channel info keys: {list(channel_info.keys()) if isinstance(channel_info, dict) else 'Not a dict'}")
                    
                    if channel_info and 'entries' in channel_info:
                        entries = list(channel_info['entries'])
                        print(f"Nombre d'entrées trouvées: {len(entries)}")
                        
                        for i, entry in enumerate(entries):
                            if self.artist_search_cancelled:
                                return
                            if entry:
                                print(f"Entrée {i}: type={entry.get('_type')}, id={entry.get('id')}, title={entry.get('title', 'Sans titre')}")
                                # Logique plus flexible pour détecter les playlists
                                if (entry.get('_type') == 'playlist' or 
                                    'playlist' in entry.get('url', '') or 
                                    'list=' in entry.get('url', '') or
                                    entry.get('playlist_count', 0) > 0 or
                                    entry.get('id', '').startswith('PL') or  # Les IDs de playlist YouTube commencent par PL
                                    'playlist' in entry.get('title', '').lower()):
                                    all_playlists.append(entry)
                                    print(f"Playlist valide trouvée: {entry.get('title', 'Sans titre')}")
                                else:
                                    print(f"Entrée ignorée (pas une playlist): {entry.get('title', 'Sans titre')}")
                    else:
                        print("Aucune entrée trouvée dans channel_info")
                                
                    if not all_playlists:
                        print("Aucune playlist trouvée sur la chaîne")
                except Exception as e:
                    print(f"Erreur extraction playlists de la chaîne: {e}")
                    self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des playlists"))
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
                
                final_playlists = list(unique_playlists.values())[:20]  # Maximum 20 playlists
                
                # Vérifier annulation avant affichage
                if not self.artist_search_cancelled:
                    # Sauvegarder en cache
                    cache_key = self.current_artist_channel_id
                    if cache_key not in self.artist_cache:
                        self.artist_cache[cache_key] = {}
                    self.artist_cache[cache_key]['playlists'] = final_playlists
                    
                    # Afficher les résultats dans l'interface
                    self.root.after(0, lambda: self._display_artist_playlists(final_playlists))
                    
        except Exception as e:
            print(f"Erreur recherche playlists artiste: {e}")
            self.root.after(0, lambda: self._display_playlists_error(str(e)))