import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier library_tab
from library_tab import *



def _download_youtube_selection(self, youtube_urls, target_playlist):
    """Télécharge une liste d'URLs YouTube et les ajoute à la playlist cible"""
    def on_download_complete(results):
        downloaded_count = len([r for r in results if r['success']])
        total_count = len(youtube_urls)
        
        # Ajouter tous les fichiers téléchargés à la playlist
        for result in results:
            if result['success']:
                if target_playlist == "Main Playlist":
                    self.add_file_to_main_playlist(result['filepath'], show_status=False)
                else:
                    self.add_file_to_playlist(result['filepath'], target_playlist, show_status=False)
        
        # Rafraîchir l'interface
        self.refresh_ui_after_changes()
        
        # Mettre à jour le statut final
        if target_playlist == "Main Playlist":
            self.status_bar.config(
                text=f"{downloaded_count}/{total_count} vidéo(s) téléchargée(s) et ajoutée(s) à la liste de lecture"
            )
        else:
            self.status_bar.config(
                text=f"{downloaded_count}/{total_count} vidéo(s) téléchargée(s) et ajoutée(s) à '{target_playlist}'"
            )
    
    # Télécharger toutes les vidéos de manière asynchrone
    self.download_multiple_youtube_videos_async(youtube_urls, completion_callback=on_download_complete)

def _download_youtube_thumbnail(self, video_info, filepath):
    """Télécharge la thumbnail YouTube et l'associe au fichier audio"""
    try:
        if not video_info.get('thumbnails'):
            return
            
        # Prendre la meilleure qualité disponible
        thumbnail_url = video_info['thumbnails'][-1]['url']
        
        import requests
        from io import BytesIO
        
        response = requests.get(thumbnail_url, timeout=5)
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        
        # Sauvegarder la thumbnail dans le même dossier que l'audio
        thumbnail_path = os.path.splitext(filepath)[0] + ".jpg"
        img.save(thumbnail_path)
        
        return thumbnail_path
        
    except Exception as e:
        print(f"Erreur téléchargement thumbnail: {e}")
        return None

def _download_and_add_after_current(self, video, frame):
    """Télécharge une vidéo et l'ajoute après la chanson en cours"""
    url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
    title = video.get('title', 'Titre inconnu')
    
    def on_download_complete(result):
        if result['success']:
            # Ajouter après la chanson en cours
            self.play_file_after_current(result['filepath'])
            self._refresh_playlist_display()
            
            # Changer l'apparence pour indiquer le succès
            self._set_download_success_appearance(frame)
            self.status_bar.config(text=f"Ajouté après la chanson en cours: {os.path.basename(result['filepath'])}")
        else:
            # En cas d'erreur, changer l'apparence
            self._set_download_error_appearance(frame)
            self.status_bar.config(text=f"Erreur téléchargement: {result.get('error', 'Erreur inconnue')}")
    
    # Télécharger de manière asynchrone
    self.download_youtube_video_async(url, title, on_download_complete)

def _download_and_add_to_playlist_thread(self, video, frame, playlist_name):
    """Thread pour télécharger une vidéo et l'ajouter à une playlist"""
    url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
    title = video.get('title', 'Titre inconnu')
    
    def on_download_complete(result):
        if result['success']:
            # Ajouter à la playlist spécifiée
            self.add_file_to_playlist(result['filepath'], playlist_name)
            self.refresh_ui_after_changes()
            
            # Remettre l'apparence normale
            self._reset_frame_appearance(frame, '#4a4a4a')
            self.status_bar.config(text=f"Ajouté à '{playlist_name}': {os.path.basename(result['filepath'])}")
        else:
            # Apparence d'erreur (jaune)
            self._reset_frame_appearance(frame, '#ffcc00', error=True)
            self.status_bar.config(text=f"Erreur: {result.get('error', 'Erreur inconnue')}")
    
    # Télécharger de manière asynchrone
    self.download_youtube_video_async(url, title, on_download_complete)

def download_selected_youtube(self, event=None, add_to_playlist=True):
    if not self.search_list:
        return
    
    video = self.search_list[0]
    url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
    title = video.get('title', 'Titre inconnu')
    
    # Vérifier si cette URL est déjà en cours de téléchargement
    if url in self.current_downloads:
        self.status_bar.config(text="Ce téléchargement est déjà en cours")
        return
    
    def on_download_complete(result):
        if result['success']:
            if add_to_playlist:
                self.add_file_to_main_playlist(result['filepath'])
            else:
                self.status_bar.config(text=f"Téléchargé: {os.path.basename(result['filepath'])}")
            self.refresh_ui_after_changes()
        else:
            self.status_bar.config(text=f"Erreur téléchargement: {result.get('error', 'Erreur inconnue')}")
    
    # Télécharger de manière asynchrone
    self.download_youtube_video_async(url, title, on_download_complete)
