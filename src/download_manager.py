#!/usr/bin/env python3
"""
Gestionnaire centralisé de téléchargements
Toutes les fonctions de téléchargement doivent passer par ce module
"""

from __init__ import *
import threading
import time

class DownloadManager:
    def __init__(self, app):
        self.app = app
    
    def download_video_sync(self, url, title, video_data, bulk_mode: bool = False):
        """Télécharge une vidéo de manière synchrone
        Args:
            bulk_mode: Si True, réduit au minimum les mises à jour UI pour éviter les lags (import HTML)
        """
        download_complete = threading.Event()
        download_success = [False]
        
        def on_complete(success):
            download_success[0] = success
            download_complete.set()
        
        # Lancer le téléchargement asynchrone
        success = download_youtube_video(self.app, url, title, video_data, on_complete, None, bulk_mode=bulk_mode)
        
        if not success:
            return False
        
        # Attendre la fin avec timeout (max 10 minutes par vidéo)
        if download_complete.wait(timeout=600):  # 10 minutes max
            return download_success[0]
        else:
            print(f"Timeout téléchargement: {title}")
            return False

def download_youtube_video(app, url, title=None, video_data=None, callback_on_complete=None, callback_params=None, bulk_mode: bool = False):
    """
    Fonction centralisée pour télécharger une vidéo YouTube
    
    Args:
        app: Instance de l'application principale
        url: URL de la vidéo YouTube
        title: Titre de la vidéo (optionnel, sera extrait si non fourni)
        video_data: Données vidéo déjà extraites (optionnel)
        callback_on_complete: Fonction à appeler une fois le téléchargement terminé
        callback_params: Paramètres pour la fonction callback
    
    Returns:
        bool: True si le téléchargement a été ajouté à la queue, False sinon
    """
    
    def download_thread():
        # Variables locales pour éviter les problèmes de closure
        title_ = title
        video_data_ = video_data
        
        try:
            # Étape 1: Extraire les informations si pas déjà fournies
            if not title_ or not video_data_:
                if not bulk_mode:
                    app.root.after(0, lambda: app.status_bar.config(text="Extraction des informations..."))
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    extracted_title = info.get('title', 'Titre inconnu')
                    if not title_:
                        title_ = extracted_title
                    if not video_data_:
                        video_data_ = info

            ## cas où le fichier est déjà téléchargé
            existing_file = app._get_existing_download(title_)
            if existing_file:
                # Trouver la thumbnail correspondante
                base_path = os.path.splitext(existing_file)[0]
                thumbnail_path = None
                for ext in ['.jpg', '.png', '.webp']:
                    possible_thumb = base_path + ext
                    if os.path.exists(possible_thumb):
                        thumbnail_path = possible_thumb
                        break
                
                # Sauvegarder l'URL YouTube même pour les fichiers existants
                app.save_youtube_url_metadata(existing_file, url)

                app.root.after(0, lambda: app._add_downloaded_file(existing_file, thumbnail_path, title_, url, False))
                if not bulk_mode:
                    app.root.after(0, lambda: app.status_bar.config(text=f"Fichier existant trouvé: {title_}"))
                # Mettre à jour la bibliothèque même pour les fichiers existants
                app.root.after(0, lambda: app._refresh_downloads_library())
                return
            else:
                app.current_downloads.add(url)

            safe_title = "".join(c for c in title_ if c.isalnum() or c in " -_")
            # Étape 2: Ajouter à l'onglet téléchargements
            download_added = False
            app.root.after(0, lambda: setattr(app, '_temp_download_result',
                app.add_download_to_tab(url, safe_title, video_data_)))

            # Attendre que l'ajout soit fait (avec timeout pour éviter les boucles infinies)
            timeout = 0
            while not hasattr(app, '_temp_download_result') and timeout < 50:  # Max 5 secondes
                time.sleep(0.1)
                timeout += 1
            
            if timeout >= 50:
                print("Timeout lors de l'ajout du téléchargement")
                return False
            
            download_added = app._temp_download_result
            delattr(app, '_temp_download_result')
            
            if not download_added:
                print(f"Téléchargement déjà en cours ou terminé: {safe_title}")
                return False
            
            app.current_download_title = safe_title
            app.current_download_url = url

            # Étape 3: Effectuer le téléchargement réel
            if not bulk_mode:
                app.root.after(0, lambda: app.status_bar.config(text=f"Téléchargement: {safe_title}"))
            
            # Créer les options de téléchargement
            # ydl_opts = app.ydl_opts.copy()
            
            downloads_dir = os.path.abspath(app.downloads_folder)
            if not os.path.exists(downloads_dir):
                try:
                    os.makedirs(downloads_dir)
                except Exception as e:
                    app.root.after(0, lambda: app.status_bar.config(text=f"Erreur création dossier: {str(e)}"))
                    return
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=720]/best',
                'outtmpl': os.path.join(downloads_dir, f'{safe_title}.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'writethumbnail': True,
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [app._download_progress_hook],
                # Options renforcées pour contourner les restrictions YouTube
                'extractor_retries': 5,
                'fragment_retries': 5,
                'retry_sleep_functions': {'http': lambda n: min(2**n, 15)},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Connection': 'keep-alive'
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web', 'ios'],
                        'player_skip': ['webpage', 'configs'],
                        'skip': ['hls', 'dash']
                    }
                },
                'ignoreerrors': False,  # Pour le téléchargement, on veut les erreurs
                'socket_timeout': 30,
            }
            
            # Fournir ffmpeg à yt_dlp si l'app l'a détecté
            if getattr(app, 'ffmpeg_dir', None):
                ydl_opts['ffmpeg_location'] = app.ffmpeg_dir
            
            # Hook de progression (optimisé pour réduire les mises à jour)
            last_progress_update = [0]  # Pour stocker la dernière progression mise à jour
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    # Extraire le pourcentage au format XX.X%
                    if 'total_bytes' in d and d['total_bytes']:
                        progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    elif '_percent_str' in d:
                        progress_str = d['_percent_str'].strip().replace('%', '')
                        try:
                            progress = float(progress_str)
                        except:
                            progress = 0
                    else:
                        progress = 0
                    
                    # Mettre à jour seulement si la progression a changé de plus de 5%
                    if abs(progress - last_progress_update[0]) >= (10 if bulk_mode else 5):
                        last_progress_update[0] = progress
                        app.root.after(0, lambda p=progress: 
                            app.download_manager.update_progress(url, p, "Téléchargement..."))
                        if not bulk_mode:
                            app.root.after(0, app.update_downloads_display)

                    
                    # Extraire la vitesse au format XXX.XXKiB/s ou XXX.XXMiB/s
                    import re
                    speed_raw = d.get('_speed_str', '0KiB/s')
                    try:
                        # Extraire la vitesse avec l'unité
                        speed_match = re.search(r'(\d+\.?\d*)(KiB/s|MiB/s|GiB/s)', speed_raw)
                        if speed_match:
                            speed_value = float(speed_match.group(1))
                            speed_unit = speed_match.group(2)
                            speed = f"{speed_value:.2f}{speed_unit}"
                        else:
                            speed = "0.00KiB/s"
                    except:
                        speed = "0.00KiB/s"
                        
                elif d['status'] == 'finished':
                    # Téléchargement terminé
                    app.root.after(0, lambda: 
                        app.download_manager.update_progress(url, 100, "Terminé"))
                    if not bulk_mode:
                        app.root.after(0, app.update_downloads_display)
                    
                    # Traitement post-téléchargement
                    filepath = d['filename']
                    if filepath.endswith('.webm') or filepath.endswith('.m4a'):
                        # Convertir en MP3
                        mp3_path = os.path.splitext(filepath)[0] + '.mp3'
                        if os.path.exists(mp3_path):
                            filepath = mp3_path
                    
                    # Sauvegarder les métadonnées
                    upload_date = video_data_.get('upload_date') if video_data_ else None
                    app.root.after(0, lambda path=filepath, u=url, date=upload_date:
                        app.save_youtube_url_metadata(path, u, date))
                    
                    # Appeler le callback si fourni
                    if callback_on_complete:
                        if callback_params:
                            app.root.after(0, lambda: callback_on_complete(True, **callback_params))
                        else:
                            app.root.after(0, lambda: callback_on_complete(True))
                    
                    # Mettre à jour les affichages
                    if not bulk_mode:
                        app.root.after(0, app._update_downloads_button)
                        app.root.after(0, app._refresh_downloads_library)
                        app.root.after(0, lambda: app.status_bar.config(text=f"Téléchargé: {safe_title}"))
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            # Télécharger
            with YoutubeDL(ydl_opts) as ydl:
                # ydl.download([url])
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                # print("downloaded_file", downloaded_file)
                final_path = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3').replace('.mp4', '.mp3')
                if not final_path.endswith('.mp3'):
                    final_path += '.mp3'
                
                thumbnail_path = os.path.splitext(final_path)[0] + ".jpg"
                if os.path.exists(downloaded_file + ".jpg"):
                    os.rename(downloaded_file + ".jpg", thumbnail_path)
                
                # Sauvegarder l'URL YouTube originale avec la date de publication
                upload_date = info.get('upload_date') if info else None
                app.save_youtube_url_metadata(final_path, url, upload_date)
                
                # Extraire et sauvegarder les métadonnées d'artiste et d'album
                app._extract_and_save_metadata(info, final_path)

                # Mettre à jour l'interface dans le thread principal
                # app.root.after(0, lambda: app._add_downloaded_file(final_path, thumbnail_path, safe_title, url, False))
                # Remettre l'apparence normale en utilisant la fonction dédiée (seulement si search_frame existe)
                
                # Marquer le téléchargement comme terminé dans l'onglet téléchargements
                app.root.after(0, lambda: app.update_download_progress(url, 100, "Terminé"))

            return True
            
        except Exception as e:
            error_msg = f"Erreur: {str(e)}"
            print(f"Erreur téléchargement {url}: {e}")
            
            # Marquer comme erreur dans l'onglet téléchargements
            app.root.after(0, lambda: app.download_manager.mark_error(url, error_msg))
            app.root.after(0, app.update_downloads_display)
            app.root.after(0, lambda: app.status_bar.config(text=error_msg))
            
            # Appeler le callback d'erreur si fourni
            if callback_on_complete:
                if callback_params:
                    app.root.after(0, lambda: callback_on_complete(False, **callback_params))
                else:
                    app.root.after(0, lambda: callback_on_complete(False))
            
            return False
    
    # Lancer le téléchargement dans un thread
    threading.Thread(target=download_thread, daemon=True).start()
    return True

def download_youtube_videos_batch(app, urls_with_info, callback_on_complete=None, callback_params=None):
    """
    Télécharge plusieurs vidéos YouTube en lot
    
    Args:
        app: Instance de l'application principale
        urls_with_info: Liste de tuples (url, title, video_data)
        callback_on_complete: Fonction à appeler pour chaque téléchargement terminé
        callback_params: Paramètres pour la fonction callback
    """
    
    def download_batch():
        downloaded_files = []
        
        for url, title, video_data in urls_with_info:
            try:
                # Utiliser la fonction de téléchargement unique
                def single_callback(filepath):
                    downloaded_files.append(filepath)
                    if callback_on_complete:
                        if callback_params:
                            callback_on_complete(filepath, **callback_params)
                        else:
                            callback_on_complete(filepath)
                
                download_youtube_video(app, url, title, video_data, single_callback)
                
                # Attendre un peu entre les téléchargements pour éviter la surcharge
                time.sleep(1)
                
            except Exception as e:
                print(f"Erreur téléchargement batch {url}: {e}")
                continue
        
        # Callback final avec tous les fichiers téléchargés
        if callback_on_complete and hasattr(callback_on_complete, '__name__') and 'batch' in callback_on_complete.__name__:
            app.root.after(0, lambda: callback_on_complete(downloaded_files))
    
    # Lancer le téléchargement batch dans un thread
    threading.Thread(target=download_batch, daemon=True).start()

def add_to_playlist_after_download(app, filepath, playlist_name=None, queue_position=None):
    """
    Callback pour ajouter un fichier à une playlist après téléchargement
    
    Args:
        app: Instance de l'application
        filepath: Chemin du fichier téléchargé
        playlist_name: Nom de la playlist (None = playlist principale)
        queue_position: Position dans la queue ('first', 'last', None)
    """
    try:
        if queue_position == 'first':
            app._safe_add_to_queue_first(filepath)
        elif queue_position == 'last':
            app._safe_add_to_queue(filepath)
        elif playlist_name:
            app._safe_add_to_specific_playlist(filepath, playlist_name)
        else:
            app._safe_add_to_main_playlist(filepath)
        
        # Rafraîchir l'affichage
        app.MainPlaylist._refresh_main_playlist_display()
        
    except Exception as e:
        print(f"Erreur ajout à la playlist après téléchargement: {e}")

def add_to_queue_after_download(app, filepath):
    """Callback spécialisé pour ajouter à la queue après téléchargement"""
    add_to_playlist_after_download(app, filepath, queue_position='last')

def add_to_queue_first_after_download(app, filepath):
    """Callback spécialisé pour ajouter en premier dans la queue après téléchargement"""
    add_to_playlist_after_download(app, filepath, queue_position='first')