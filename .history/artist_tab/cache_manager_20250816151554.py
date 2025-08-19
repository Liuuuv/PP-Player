# Gestionnaire de cache optimisé pour les onglets artiste
import time
import json
import os
from collections import OrderedDict

class ArtistCacheManager:
    """Gestionnaire de cache avec limitation de taille et expiration"""
    
    def __init__(self, downloads_folder=None):
        # Importer la configuration centralisée
        try:
            from search_tab.config import get_cache_config, get_artist_config
            self.max_artists = get_artist_config('max_artists_cache') or 15
            self.max_thumbnails = get_cache_config('max_thumbnails', 'thumbnail') or 200
            self.thumbnail_expire_time = get_cache_config('thumbnail_expire_time', 'thumbnail') or 1800
        except ImportError:
            # Valeurs par défaut si la config n'est pas disponible
            self.max_artists = 15
            self.max_thumbnails = 200
            self.thumbnail_expire_time = 1800
        
        # Cache des données artiste avec ordre d'accès
        self.artist_cache = OrderedDict()
        
        # Cache des miniatures avec timestamps
        self.thumbnail_cache = {}
        self.thumbnail_timestamps = {}
        
        # Cache des contenus de playlists
        self.playlist_content_cache = OrderedDict()
        try:
            from search_tab.config import get_artist_config
            self.max_playlists = get_artist_config('max_playlists_cache') or 30
        except ImportError:
            self.max_playlists = 30
        
        # Cache des recherches YouTube avec configuration centralisée
        self.search_cache = OrderedDict()
        try:
            from search_tab.config import get_cache_config
            self.max_searches = get_cache_config('max_searches', 'search') or 50
            self.search_expire_time = get_cache_config('search_expire_time', 'search') or 3600
            self.max_interface_states = get_cache_config('max_interface_states', 'search') or 20
            cache_file = get_cache_config('cache_file', 'search') or 'downloads/search_cache.json'
        except ImportError:
            # Valeurs par défaut
            self.max_searches = 50
            self.search_expire_time = 3600
            self.max_interface_states = 20
            cache_file = 'downloads/search_cache.json'
        
        self.search_timestamps = {}
        
        # Cache des états d'interface
        self.interface_state_cache = {}
        
        # Statistiques d'utilisation pour le préchargement intelligent
        self.search_usage_stats = {}  # {query: {'count': int, 'last_used': timestamp}}
        
        # Fichier de sauvegarde du cache
        self.cache_file = cache_file
        
        # Charger le cache depuis le disque
        self.load_cache_from_disk()
    
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
            'playlists': len(self.playlist_content_cache),
            'searches': len(self.search_cache),
            'interface_states': len(self.interface_state_cache)
        }
    
    def get_search_results(self, search_query):
        """Récupère les résultats de recherche depuis le cache"""
        if search_query in self.search_cache:
            # Vérifier l'expiration
            if time.time() - self.search_timestamps[search_query] < self.search_expire_time:
                self.search_cache.move_to_end(search_query)
                # Mettre à jour les statistiques d'utilisation
                self._update_usage_stats(search_query)
                return self.search_cache[search_query]
            else:
                # Expirée, la supprimer
                del self.search_cache[search_query]
                del self.search_timestamps[search_query]
        return None
    
    def set_search_results(self, search_query, results):
        """Stocke les résultats de recherche dans le cache"""
        self.search_cache[search_query] = results
        self.search_timestamps[search_query] = time.time()
        self.search_cache.move_to_end(search_query)
        
        # Nettoyer si trop de recherches
        while len(self.search_cache) > self.max_searches:
            oldest_query = next(iter(self.search_cache))
            del self.search_cache[oldest_query]
            if oldest_query in self.search_timestamps:
                del self.search_timestamps[oldest_query]
    
    def get_interface_state(self, state_key):
        """Récupère un état d'interface depuis le cache"""
        return self.interface_state_cache.get(state_key)
    
    def set_interface_state(self, state_key, state_data):
        """Stocke un état d'interface dans le cache"""
        self.interface_state_cache[state_key] = state_data
        
        # Nettoyer si trop d'états
        if len(self.interface_state_cache) > self.max_interface_states:
            # Supprimer le plus ancien
            oldest_key = next(iter(self.interface_state_cache))
            del self.interface_state_cache[oldest_key]
    
    def clear_expired_searches(self):
        """Nettoie les recherches expirées"""
        current_time = time.time()
        expired_queries = [
            query for query, timestamp in self.search_timestamps.items()
            if current_time - timestamp > self.search_expire_time
        ]
        
        for query in expired_queries:
            if query in self.search_cache:
                del self.search_cache[query]
            del self.search_timestamps[query]
    
    def _update_usage_stats(self, search_query):
        """Met à jour les statistiques d'utilisation d'une recherche"""
        if search_query not in self.search_usage_stats:
            self.search_usage_stats[search_query] = {'count': 0, 'last_used': 0}
        
        self.search_usage_stats[search_query]['count'] += 1
        self.search_usage_stats[search_query]['last_used'] = time.time()
    
    def get_popular_searches(self, limit=10):
        """Retourne les recherches les plus populaires"""
        # Trier par nombre d'utilisations et récence
        sorted_searches = sorted(
            self.search_usage_stats.items(),
            key=lambda x: (x[1]['count'], x[1]['last_used']),
            reverse=True
        )
        return [query for query, stats in sorted_searches[:limit]]
    
    def should_preload_search(self, search_query):
        """Détermine si une recherche devrait être préchargée basé sur l'usage personnel"""
        if search_query in self.search_usage_stats:
            stats = self.search_usage_stats[search_query]
            
            # Utiliser la configuration centralisée
            try:
                from search_tab.config import get_preload_config
                min_count = get_preload_config('min_usage_count') or 2
                recency_hours = get_preload_config('preload_recency_hours') or 24
            except ImportError:
                min_count = 2
                recency_hours = 24
            
            # Précharger si utilisée assez souvent et récemment
            return (stats['count'] >= min_count and 
                    time.time() - stats['last_used'] < recency_hours * 3600)
        return False
    
    def get_searches_to_preload(self, limit=None):
        """Retourne les recherches personnelles à précharger"""
        if limit is None:
            try:
                from search_tab.config import get_preload_config
                limit = get_preload_config('max_preload_searches') or 3
            except ImportError:
                limit = 3
        
        candidates = []
        for query, stats in self.search_usage_stats.items():
            if self.should_preload_search(query):
                # Pas encore en cache ou expirée
                if not self.get_search_results(query):
                    candidates.append((query, stats['count'], stats['last_used']))
        
        # Trier par fréquence et récence
        candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return [query for query, count, last_used in candidates[:limit]]
    
    def _make_json_serializable(self, obj):
        """Rend un objet sérialisable en JSON en filtrant les objets non-sérialisables"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items() 
                   if not str(type(v)).startswith("<class 'tkinter")}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj 
                   if not str(type(item)).startswith("<class 'tkinter")]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, tuple):
            return list(obj)  # Convertir les tuples en listes
        else:
            # Pour les autres types, essayer de les convertir en string ou les ignorer
            try:
                # Vérifier si c'est un widget Tkinter
                if hasattr(obj, 'winfo_exists'):
                    return None  # Ignorer les widgets Tkinter
                return str(obj)
            except:
                return None
    
    def save_cache_to_disk(self):
        """Sauvegarde le cache des recherches sur disque"""
        try:
            # Créer le dossier downloads s'il n'existe pas
            os.makedirs("downloads", exist_ok=True)
            
            # Préparer les données à sauvegarder (seulement les recherches, pas les miniatures)
            cache_data = {
                'search_cache': self._make_json_serializable(dict(self.search_cache)),
                'search_timestamps': self._make_json_serializable(self.search_timestamps),
                'interface_state_cache': self._make_json_serializable(self.interface_state_cache),
                'search_usage_stats': self._make_json_serializable(self.search_usage_stats),
                'version': '1.1',
                'saved_at': time.time()
            }
            
            # Sauvegarder en JSON
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"Erreur sauvegarde cache: {e}")
    
    def load_cache_from_disk(self):
        """Charge le cache des recherches depuis le disque"""
        try:
            if not os.path.exists(self.cache_file):
                return
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Vérifier la version (accepter 1.0 et 1.1)
            version = cache_data.get('version', '1.0')
            if version not in ['1.0', '1.1']:
                return
            
            # Charger les recherches
            if 'search_cache' in cache_data:
                self.search_cache = OrderedDict(cache_data['search_cache'])
            
            if 'search_timestamps' in cache_data:
                self.search_timestamps = cache_data['search_timestamps']
            
            if 'interface_state_cache' in cache_data:
                self.interface_state_cache = cache_data['interface_state_cache']
            
            # Charger les statistiques d'utilisation (nouveau dans v1.1)
            if 'search_usage_stats' in cache_data:
                self.search_usage_stats = cache_data['search_usage_stats']
            
            # Nettoyer les recherches expirées
            self.clear_expired_searches()
            
        except Exception as e:
            print(f"Erreur chargement cache: {e}")
    
    def clear_all(self):
        """Vide tous les caches"""
        self.artist_cache.clear()
        self.thumbnail_cache.clear()
        self.thumbnail_timestamps.clear()
        self.playlist_content_cache.clear()
        self.search_cache.clear()
        self.search_timestamps.clear()
        self.interface_state_cache.clear()
        
        # Supprimer le fichier de cache
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
        except:
            pass