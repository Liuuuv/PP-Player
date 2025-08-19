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
    downloaded_count = 0
    total_count = len(youtube_urls)
    
    for i, url in enumerate(youtube_urls):
        try:
            # Trouver la frame correspondante pour obtenir les infos de la vidéo
            video_data = None
            for filepath, frame in self.selection_frames.items():
                if filepath == url and hasattr(frame, 'video_data'):
                    video_data = frame.video_data
                    break
            
            if not video_data:
                continue
            
            # Mettre à jour le statut
            self.root.after(0, lambda i=i, total=total_count: self.status_bar.config(
                text=f"Téléchargement {i+1}/{total}: {video_data.get('title', 'Sans titre')[:30]}..."
            ))
            
            # Télécharger la vidéo
            title = video_data.get('title', 'Sans titre')
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
            
            downloads_dir = os.path.abspath("downloads")
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(downloads_dir, f'{safe_title}.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                final_path = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3').replace('.mp4', '.mp3')
                if not final_path.endswith('.mp3'):
                    final_path += '.mp3'
                
                # Ajouter à la playlist cible
                if target_playlist == "Main Playlist":
                    self.root.after(0, lambda: self.add_to_main_playlist(final_path, show_status=False))
                    self.root.after(0, self._refresh_playlist_display)
                else:
                    if target_playlist in self.playlists and final_path not in self.playlists[target_playlist]:
                        self.playlists[target_playlist].append(final_path)
                        self.root.after(0, self.save_playlists)
                
                downloaded_count += 1
                
        except Exception as e:
            print(f"Erreur téléchargement {url}: {e}")
    
    # Mettre à jour le statut final
    if target_playlist == "Main Playlist":
        self.root.after(0, lambda: self.status_bar.config(
            text=f"{downloaded_count}/{total_count} vidéo(s) téléchargée(s) et ajoutée(s) à la liste de lecture"
        ))
    else:
        self.root.after(0, lambda: self.status_bar.config(
            text=f"{downloaded_count}/{total_count} vidéo(s) téléchargée(s) et ajoutée(s) à '{target_playlist}'"
        ))
    
    # Mettre à jour le nombre de fichiers téléchargés
    self.root.after(0, file_services._count_downloaded_files(self))
    self.root.after(0, self._update_downloads_button)
    
    # Rafraîchir la bibliothèque (peu importe l'onglet actuel)
    self.root.after(0, self._refresh_downloads_library)
