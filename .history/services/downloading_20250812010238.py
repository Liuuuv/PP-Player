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
    def download_thread():
        try:
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            self.current_downloads.add(url)
            
            # Télécharger la vidéo
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Trouver le fichier téléchargé
                filename = ydl.prepare_filename(info)
                # Remplacer l'extension par .mp3
                audio_filename = os.path.splitext(filename)[0] + '.mp3'
                
                if os.path.exists(audio_filename):
                    # Ajouter à la main playlist après la chanson en cours
                    insert_position = self.current_index + 1
                    self.main_playlist.insert(insert_position, audio_filename)
                    
                    # Mettre à jour l'affichage de la main playlist
                    self.root.after(0, lambda: self._refresh_playlist_display())
                    
                    # Télécharger la thumbnail
                    self._download_youtube_thumbnail(info, audio_filename)
                    
                    # Changer l'apparence pour indiquer le succès
                    self.root.after(0, lambda: self._set_download_success_appearance(frame))
                    
                    self.root.after(0, lambda: self.status_bar.config(
                        text=f"Ajouté après la chanson en cours: {os.path.basename(audio_filename)}"
                    ))
                else:
                    raise Exception("Fichier audio non trouvé après téléchargement")
                    
        except Exception as e:
            print(f"Erreur téléchargement: {e}")
            # En cas d'erreur, changer l'apparence
            self.root.after(0, lambda: self._set_download_error_appearance(frame))
            self.root.after(0, lambda: self.status_bar.config(text=f"Erreur téléchargement: {str(e)}"))
        finally:
            self.current_downloads.discard(url)
    
    # Lancer le téléchargement dans un thread séparé
    threading.Thread(target=download_thread, daemon=True).start()
