#!/usr/bin/env python3
"""
Gestionnaire centralisé de téléchargements
Toutes les fonctions de téléchargement doivent passer par ce module
"""

from __init__ import *
import threading
import time

def download_youtube_video(app, url, title=None, video_data=None, callback_on_complete=None, callback_params=None):
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
        final_title = title
        final_video_data = video_data
        
        try:
            # Étape 1: Extraire les informations si pas déjà fournies
            if not final_title or not final_video_data:
                app.root.after(0, lambda: app.status_bar.config(text="Extraction des informations..."))
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    extracted_title = info.get('title', 'Titre inconnu')
                    if not final_title:
                        final_title = extracted_title
                    if not final_video_data:
                        final_video_data = info
            
            # Étape 2: Ajouter à l'onglet téléchargements
            download_added = False
            app.root.after(0, lambda: setattr(app, '_temp_download_result', 
                app.add_download_to_tab(url, final_title, final_video_data)))
            
            # Attendre que l'ajout soit fait
            while not hasattr(app, '_temp_download_result'):
                time.sleep(0.1)
            
            download_added = app._temp_download_result
            delattr(app, '_temp_download_result')
            
            if not download_added:
                print(f"Téléchargement déjà en cours ou terminé: {final_title}")
                return False
            
            # Étape 3: Effectuer le téléchargement réel
            app.root.after(0, lambda: app.status_bar.config(text=f"Téléchargement: {final_title}"))
            
            # Créer les options de téléchargement
            ydl_opts = app.ydl_opts.copy()
            
            # Hook de progression
            def progress_hook(d):
                if d['status'] == 'downloading':
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
                    
                    # Mettre à jour la progression dans l'onglet téléchargements
                    app.root.after(0, lambda p=progress: 
                        app.download_manager.update_progress(url, p, "Téléchargement..."))
                    app.root.after(0, app.update_downloads_display)
                
                elif d['status'] == 'finished':
                    # Téléchargement terminé
                    app.root.after(0, lambda: 
                        app.download_manager.update_progress(url, 100, "Terminé"))
                    app.root.after(0, app.update_downloads_display)
                    
                    # Traitement post-téléchargement
                    filepath = d['filename']
                    if filepath.endswith('.webm') or filepath.endswith('.m4a'):
                        # Convertir en MP3
                        mp3_path = os.path.splitext(filepath)[0] + '.mp3'
                        if os.path.exists(mp3_path):
                            filepath = mp3_path
                    
                    # Sauvegarder les métadonnées
                    upload_date = final_video_data.get('upload_date') if final_video_data else None
                    app.root.after(0, lambda path=filepath, u=url, date=upload_date:
                        app.save_youtube_url_metadata(path, u, date))
                    
                    # Appeler le callback si fourni
                    if callback_on_complete:
                        if callback_params:
                            app.root.after(0, lambda: callback_on_complete(filepath, **callback_params))
                        else:
                            app.root.after(0, lambda: callback_on_complete(filepath))
                    
                    # Mettre à jour les affichages
                    app.root.after(0, app._update_downloads_button)
                    app.root.after(0, app._refresh_downloads_library)
                    app.root.after(0, lambda: app.status_bar.config(text=f"Téléchargé: {final_title}"))
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            # Télécharger
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return True
            
        except Exception as e:
            error_msg = f"Erreur: {str(e)}"
            print(f"Erreur téléchargement {url}: {e}")
            
            # Marquer comme erreur dans l'onglet téléchargements
            app.root.after(0, lambda: app.download_manager.mark_error(url, error_msg))
            app.root.after(0, app.update_downloads_display)
            app.root.after(0, lambda: app.status_bar.config(text=error_msg))
            
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
        app._refresh_playlist_display()
        
    except Exception as e:
        print(f"Erreur ajout à la playlist après téléchargement: {e}")

def add_to_queue_after_download(app, filepath):
    """Callback spécialisé pour ajouter à la queue après téléchargement"""
    add_to_playlist_after_download(app, filepath, queue_position='last')

def add_to_queue_first_after_download(app, filepath):
    """Callback spécialisé pour ajouter en premier dans la queue après téléchargement"""
    add_to_playlist_after_download(app, filepath, queue_position='first')