"""
Service de téléchargement et recherche YouTube
"""
import os
import threading
from yt_dlp import YoutubeDL
from config.constants import YDL_OPTS, DOWNLOADS_DIR, AUDIO_EXTENSIONS


class YouTubeService:
    """Service pour la recherche et le téléchargement YouTube"""
    
    def __init__(self):
        self.ydl_opts = YDL_OPTS.copy()
        self.current_downloads = set()
        
        # Variables de recherche
        self.is_searching = False
        self.current_search_query = ""
        self.search_results_count = 0
        self.max_search_results = 50
        self.results_per_page = 10
        self.is_loading_more = False
        self.current_search_batch = 1
        self.max_search_batchs = self.max_search_results // self.results_per_page + 1
        self.all_search_results = []
        
        # Callbacks
        self.on_download_progress = None
        self.on_download_complete = None
        self.on_download_error = None
        self.on_search_results = None
    
    def search_youtube(self, query, max_results=10):
        """Recherche des vidéos sur YouTube"""
        if self.is_searching:
            return []
        
        self.is_searching = True
        self.current_search_query = query
        
        try:
            search_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch' + str(max_results) + ':',
            }
            
            with YoutubeDL(search_opts) as ydl:
                search_results = ydl.extract_info(query, download=False)
                
                if search_results and 'entries' in search_results:
                    results = []
                    for entry in search_results['entries']:
                        if entry:
                            result = {
                                'title': entry.get('title', 'Titre inconnu'),
                                'url': entry.get('url', ''),
                                'id': entry.get('id', ''),
                                'duration': entry.get('duration', 0),
                                'uploader': entry.get('uploader', 'Inconnu'),
                                'view_count': entry.get('view_count', 0)
                            }
                            results.append(result)
                    
                    self.all_search_results = results
                    if self.on_search_results:
                        self.on_search_results(results)
                    
                    return results
        
        except Exception as e:
            print(f"Erreur recherche YouTube: {e}")
            if self.on_search_results:
                self.on_search_results([])
        
        finally:
            self.is_searching = False
        
        return []
    
    def download_audio(self, url, title=None):
        """Télécharge l'audio d'une vidéo YouTube"""
        if url in self.current_downloads:
            return False
        
        self.current_downloads.add(url)
        
        def download_thread():
            try:
                # Créer le dossier de téléchargement s'il n'existe pas
                os.makedirs(DOWNLOADS_DIR, exist_ok=True)
                
                # Configuration pour le téléchargement
                download_opts = self.ydl_opts.copy()
                
                # Hook pour suivre le progrès
                def progress_hook(d):
                    if self.on_download_progress:
                        self.on_download_progress(d, url, title)
                
                download_opts['progress_hooks'] = [progress_hook]
                
                with YoutubeDL(download_opts) as ydl:
                    ydl.download([url])
                
                # Trouver le fichier téléchargé
                downloaded_file = self._find_downloaded_file(title)
                
                if downloaded_file and self.on_download_complete:
                    self.on_download_complete(downloaded_file, url, title)
                
                return True
                
            except Exception as e:
                print(f"Erreur téléchargement: {e}")
                if self.on_download_error:
                    self.on_download_error(str(e), url, title)
                return False
            
            finally:
                self.current_downloads.discard(url)
        
        # Lancer le téléchargement dans un thread séparé
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        
        return True
    
    def _find_downloaded_file(self, title):
        """Trouve le fichier téléchargé correspondant au titre"""
        if not title:
            return None
        
        try:
            # Chercher dans le dossier de téléchargement
            for filename in os.listdir(DOWNLOADS_DIR):
                if filename.lower().endswith(AUDIO_EXTENSIONS):
                    # Vérifier si le titre est dans le nom du fichier
                    if self._normalize_filename(title) in self._normalize_filename(filename):
                        return os.path.join(DOWNLOADS_DIR, filename)
        except Exception as e:
            print(f"Erreur recherche fichier téléchargé: {e}")
        
        return None
    
    def _normalize_filename(self, filename):
        """Normalise un nom de fichier pour la comparaison"""
        import re
        # Supprimer les caractères spéciaux et convertir en minuscules
        normalized = re.sub(r'[^\w\s-]', '', filename.lower())
        normalized = re.sub(r'[-\s]+', ' ', normalized).strip()
        return normalized
    
    def get_downloaded_files(self):
        """Retourne la liste des fichiers téléchargés"""
        downloaded_files = []
        
        try:
            if os.path.exists(DOWNLOADS_DIR):
                for filename in os.listdir(DOWNLOADS_DIR):
                    if filename.lower().endswith(AUDIO_EXTENSIONS):
                        filepath = os.path.join(DOWNLOADS_DIR, filename)
                        downloaded_files.append(filepath)
        except Exception as e:
            print(f"Erreur lecture dossier téléchargements: {e}")
        
        return downloaded_files
    
    def count_downloaded_files(self):
        """Compte les fichiers téléchargés"""
        try:
            if not os.path.exists(DOWNLOADS_DIR):
                os.makedirs(DOWNLOADS_DIR)
                return 0
            
            count = 0
            for filename in os.listdir(DOWNLOADS_DIR):
                if filename.lower().endswith(AUDIO_EXTENSIONS):
                    count += 1
            
            return count
        except Exception as e:
            print(f"Erreur comptage fichiers: {e}")
            return 0
    
    def is_downloading(self, url):
        """Vérifie si une URL est en cours de téléchargement"""
        return url in self.current_downloads
    
    def cancel_download(self, url):
        """Annule un téléchargement (si possible)"""
        self.current_downloads.discard(url)
    
    def clear_search_results(self):
        """Vide les résultats de recherche"""
        self.all_search_results.clear()
        self.current_search_query = ""
        self.search_results_count = 0
        self.current_search_batch = 1