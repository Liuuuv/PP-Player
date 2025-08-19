"""
Fonctions de base pour le téléchargement et l'ajout à la playlist
Ces fonctions font une seule chose chacune et peuvent être combinées selon les besoins
"""

import os
import threading
from yt_dlp import YoutubeDL


def download_youtube_video(self, url, title=None):
    """
    Télécharge une vidéo YouTube et retourne le chemin du fichier audio
    
    Args:
        url: URL de la vidéo YouTube
        title: Titre de la vidéo (optionnel, sera extrait si non fourni)
    
    Returns:
        dict: {
            'success': bool,
            'filepath': str,
            'thumbnail_path': str,
            'title': str,
            'error': str (si success=False)
        }
    """
    try:
        # Extraire les infos si le titre n'est pas fourni
        if not title:
            with YoutubeDL({**self.ydl_opts, 'skip_download': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Titre inconnu')
        
        # Vérifier si le fichier existe déjà
        existing_file = self._get_existing_download(title)
        if existing_file:
            # Trouver la thumbnail correspondante
            base_path = os.path.splitext(existing_file)[0]
            thumbnail_path = None
            for ext in ['.jpg', '.png', '.webp']:
                possible_thumb = base_path + ext
                if os.path.exists(possible_thumb):
                    thumbnail_path = possible_thumb
                    break
            
            return {
                'success': True,
                'filepath': existing_file,
                'thumbnail_path': thumbnail_path,
                'title': title,
                'already_exists': True
            }
        
        # Préparer le téléchargement
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        downloads_dir = os.path.abspath("downloads")
        
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        
        # Options de téléchargement
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(downloads_dir, f'{safe_title}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        # Télécharger
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            
            # Construire le chemin final
            final_path = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3').replace('.mp4', '.mp3')
            if not final_path.endswith('.mp3'):
                final_path += '.mp3'
            
            # Gérer la thumbnail
            thumbnail_path = os.path.splitext(final_path)[0] + ".jpg"
            if os.path.exists(downloaded_file + ".jpg"):
                os.rename(downloaded_file + ".jpg", thumbnail_path)
            
            # Sauvegarder les métadonnées
            upload_date = info.get('upload_date') if info else None
            self.save_youtube_url_metadata(final_path, url, upload_date)
            self._extract_and_save_metadata(info, final_path)
            
            return {
                'success': True,
                'filepath': final_path,
                'thumbnail_path': thumbnail_path,
                'title': safe_title,
                'already_exists': False
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def add_file_to_main_playlist(self, filepath, show_status=True):
    """
    Ajoute un fichier à la main playlist
    
    Args:
        filepath: Chemin vers le fichier
        show_status: Afficher le message de statut
    
    Returns:
        bool: True si ajouté, False si déjà présent
    """
    if filepath not in self.main_playlist:
        self.main_playlist.append(filepath)
        if show_status:
            self.status_bar.config(text=f"Ajouté à la main playlist: {os.path.basename(filepath)}")
        return True
    else:
        if show_status:
            self.status_bar.config(text=f"Déjà dans la main playlist: {os.path.basename(filepath)}")
        return False


def add_file_to_playlist(self, filepath, playlist_name, show_status=True):
    """
    Ajoute un fichier à une playlist spécifique
    
    Args:
        filepath: Chemin vers le fichier
        playlist_name: Nom de la playlist
        show_status: Afficher le message de statut
    
    Returns:
        bool: True si ajouté, False si déjà présent
    """
    # Créer la playlist si elle n'existe pas
    if playlist_name not in self.playlists:
        self.playlists[playlist_name] = []
    
    if filepath not in self.playlists[playlist_name]:
        self.playlists[playlist_name].append(filepath)
        if show_status:
            self.status_bar.config(text=f"Ajouté à '{playlist_name}': {os.path.basename(filepath)}")
        return True
    else:
        if show_status:
            self.status_bar.config(text=f"Déjà dans '{playlist_name}': {os.path.basename(filepath)}")
        return False


def add_file_to_queue(self, filepath, position='last'):
    """
    Ajoute un fichier à la queue
    
    Args:
        filepath: Chemin vers le fichier
        position: 'first' ou 'last'
    """
    if hasattr(self, 'drag_drop_handler'):
        if position == 'first':
            self.drag_drop_handler._add_to_queue_first(filepath)
        else:
            self.drag_drop_handler._add_to_queue(filepath)


def play_file_after_current(self, filepath):
    """
    Insère un fichier pour qu'il soit lu après la chanson actuelle
    
    Args:
        filepath: Chemin vers le fichier
    """
    insert_position = self.current_index + 1
    self.main_playlist.insert(insert_position, filepath)


def refresh_ui_after_changes(self):
    """
    Rafraîchit l'interface utilisateur après des modifications
    """
    # Mettre à jour le compteur de fichiers téléchargés
    self._count_downloaded_files()
    self._update_downloads_button()
    
    # Rafraîchir les affichages
    self.load_downloaded_files()
    self._refresh_playlist_display()
    self._refresh_downloads_library()
    
    # Sauvegarder les playlists
    self.save_playlists()


def download_youtube_video_async(self, url, title=None, callback=None):
    """
    Télécharge une vidéo YouTube de manière asynchrone
    
    Args:
        url: URL de la vidéo YouTube
        title: Titre de la vidéo (optionnel)
        callback: Fonction à appeler avec le résultat
    """
    def download_thread():
        result = download_youtube_video(self, url, title)
        if callback:
            self.root.after(0, lambda: callback(result))
    
    threading.Thread(target=download_thread, daemon=True).start()


def download_multiple_youtube_videos(self, urls, callback=None):
    """
    Télécharge plusieurs vidéos YouTube
    
    Args:
        urls: Liste des URLs à télécharger
        callback: Fonction appelée pour chaque résultat (url, result)
    
    Returns:
        list: Liste des résultats de téléchargement
    """
    results = []
    
    for i, url in enumerate(urls):
        try:
            # Mettre à jour le statut
            self.safe_after(0, lambda i=i: self.status_bar.config(
                text=f"Téléchargement {i+1}/{len(urls)}..."
            ))
            
            result = download_youtube_video(self, url)
            results.append(result)
            
            if callback:
                self.safe_after(0, lambda: callback(url, result))
                
        except Exception as e:
            result = {'success': False, 'error': str(e)}
            results.append(result)
            if callback:
                self.safe_after(0, lambda: callback(url, result))
    
    return results


def download_multiple_youtube_videos_async(self, urls, progress_callback=None, completion_callback=None):
    """
    Télécharge plusieurs vidéos YouTube de manière asynchrone
    
    Args:
        urls: Liste des URLs à télécharger
        progress_callback: Fonction appelée pour chaque résultat (url, result)
        completion_callback: Fonction appelée à la fin avec tous les résultats
    """
    def download_thread():
        results = download_multiple_youtube_videos(self, urls, progress_callback)
        if completion_callback:
            self.root.after(0, lambda: completion_callback(results))
    
    threading.Thread(target=download_thread, daemon=True).start()