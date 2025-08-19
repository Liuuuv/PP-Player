# Gestionnaire de cache optimisé pour les onglets artiste
import time
from collections import OrderedDict

class ArtistCacheManager:
    """Gestionnaire de cache avec limitation de taille et expiration"""
    
    def __init__(self, max_artists=15, max_thumbnails=200, thumbnail_expire_time=1800):  # 30 minutes
        self.max_artists = max_artists
        self.max_thumbnails = max_thumbnails
        self.thumbnail_expire_time = thumbnail_expire_time
        
        # Cache des données artiste avec ordre d'accès
        self.artist_cache = OrderedDict()
        
        # Cache des miniatures avec timestamps
        self.thumbnail_cache = {}
        self.thumbnail_timestamps = {}
        
        # Cache des contenus de playlists
        self.playlist_content_cache = OrderedDict()
        self.max_playlists = 30
        
        # Cache des recherches YouTube (nouveau)
        self.search_cache = OrderedDict()
        self.max_searches = 50
        self.search_expire_time = 3600  # 1 heure
        self.search_timestamps = {}
        
        # Cache des états d'interface (nouveau)
        self.interface_state_cache = {}
        self.max_interface_states = 20
    
    def get_artist_data(self, artist_id, content_type):
        """Récupère les données d'un artiste depuis le cache"""
        if artist_id in self.artist_cache:
            # Déplacer vers la fin (plus récemment utilisé)
            self.artist_cache.move_to_end(artist_id)
            return self.artist_cache[artist_id].get(content_type)
        return None
    
    def set_artist_data(self, artist_id, content_type, data):
        """Stocke les données d'un artiste dans le cache"""
        if artist_id not in self.artist_cache:
            self.artist_cache[artist_id] = {}
        
        self.artist_cache[artist_id][content_type] = data
        self.artist_cache.move_to_end(artist_id)
        
        # Nettoyer si trop d'artistes
        while len(self.artist_cache) > self.max_artists:
            self.artist_cache.popitem(last=False)
    
    def get_thumbnail(self, video_id):
        """Récupère une miniature depuis le cache"""
        if video_id in self.thumbnail_cache:
            # Vérifier l'expiration
            if time.time() - self.thumbnail_timestamps[video_id] < self.thumbnail_expire_time:
                return self.thumbnail_cache[video_id]
            else:
                # Expirée, la supprimer
                del self.thumbnail_cache[video_id]
                del self.thumbnail_timestamps[video_id]
        return None
    
    def set_thumbnail(self, video_id, thumbnail):
        """Stocke une miniature dans le cache"""
        self.thumbnail_cache[video_id] = thumbnail
        self.thumbnail_timestamps[video_id] = time.time()
        
        # Nettoyer si trop de miniatures
        if len(self.thumbnail_cache) > self.max_thumbnails:
            # Supprimer les plus anciennes
            oldest_items = sorted(self.thumbnail_timestamps.items(), key=lambda x: x[1])
            for video_id, _ in oldest_items[:self.max_thumbnails // 4]:  # Supprimer 25%
                if video_id in self.thumbnail_cache:
                    del self.thumbnail_cache[video_id]
                del self.thumbnail_timestamps[video_id]
    
    def get_playlist_content(self, playlist_url):
        """Récupère le contenu d'une playlist depuis le cache"""
        if playlist_url in self.playlist_content_cache:
            self.playlist_content_cache.move_to_end(playlist_url)
            return self.playlist_content_cache[playlist_url]
        return None
    
    def set_playlist_content(self, playlist_url, content):
        """Stocke le contenu d'une playlist dans le cache"""
        self.playlist_content_cache[playlist_url] = content
        self.playlist_content_cache.move_to_end(playlist_url)
        
        # Nettoyer si trop de playlists
        while len(self.playlist_content_cache) > self.max_playlists:
            self.playlist_content_cache.popitem(last=False)
    
    def clear_expired_thumbnails(self):
        """Nettoie les miniatures expirées"""
        current_time = time.time()
        expired_ids = [
            video_id for video_id, timestamp in self.thumbnail_timestamps.items()
            if current_time - timestamp > self.thumbnail_expire_time
        ]
        
        for video_id in expired_ids:
            if video_id in self.thumbnail_cache:
                del self.thumbnail_cache[video_id]
            del self.thumbnail_timestamps[video_id]
    
    def get_cache_stats(self):
        """Retourne les statistiques du cache"""
        return {
            'artists': len(self.artist_cache),
            'thumbnails': len(self.thumbnail_cache),
            'playlists': len(self.playlist_content_cache)
        }
    
    def clear_all(self):
        """Vide tous les caches"""
        self.artist_cache.clear()
        self.thumbnail_cache.clear()
        self.thumbnail_timestamps.clear()
        self.playlist_content_cache.clear()