from __init__ import *

def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
    style = ttk.Style()
    color_index = 0

    for child in widget.winfo_children():
        # Si c'est un ttk.Frame → appliquer un style
        if isinstance(child, ttk.Frame):
            style_name = f"Debug.TFrame{color_index}"
            style.layout(style_name, style.layout("TFrame"))
            style.configure(style_name, background=colors[color_index % len(colors)])
            child.configure(style=style_name)
            color_index += 1

        # Si c'est un tk.Frame → appliquer une couleur directement
        elif isinstance(child, tk.Frame):
            child.configure(bg=colors[color_index % len(colors)])
            color_index += 1

        # Récursif sur les enfants
        self.colorize_ttk_frames(child, colors)

def save_config(self):
    """Sauvegarde la configuration (volume global et offsets de volume)"""
    try:
        import json
        
        # Créer le dossier downloads s'il n'existe pas
        os.makedirs("downloads", exist_ok=True)
        
        # Convertir le set en liste pour la sérialisation JSON
        played_songs_list = list(self.stats['played_songs']) if 'played_songs' in self.stats else []
        
        config = {
            "global_volume": self.volume,
            "volume_offsets": self.volume_offsets,
            "audio_device": self.current_audio_device,
            "stats": {
                "songs_played": self.stats.get('songs_played', 0),
                "total_listening_time": self.stats.get('total_listening_time', 0.0),
                "searches_count": self.stats.get('searches_count', 0),
                "played_songs": played_songs_list
            }
        }
        
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Erreur sauvegarde config: {e}")


def set_volume(self, val):
    # print(f"Setting volume to {val}")
    self.volume = float(val) / 100
    self._apply_volume()
    # Sauvegarder le volume global seulement si on n'est pas en cours d'initialisation
    if not self.initializing:
        self.save_config()

def set_volume_offset(self, val):
    self.volume_offset = float(val)
    self._apply_volume()
    
    # Sauvegarder l'offset pour la musique en cours seulement si on n'est pas en cours d'initialisation
    if not self.initializing and self.main_playlist and self.current_index < len(self.main_playlist):
        current_file = self.main_playlist[self.current_index]
        self.volume_offsets[current_file] = self.volume_offset
        self.save_config()

def _apply_volume(self):
    """Applique le volume avec l'offset"""
    # Si le volume global est à 0, on n'entend rien peu importe l'offset
    if self.volume == 0:
        final_volume = 0
    else:
        # Calculer le volume final avec l'offset
        final_volume = self.volume + (self.volume_offset / 100)
        # S'assurer que le volume reste entre 0 et 1
        final_volume = max(0, min(1.0, final_volume))
    
    pygame.mixer.music.set_volume(final_volume)

def _reset_volume_offset(self, event):
    """Remet l'offset de volume à 0 (clic droit)"""
    self.volume_offset_slider.set(0)
    # set_volume_offset sera appelé automatiquement par le slider

def _shuffle_remaining_playlist(self):
    """Mélange aléatoirement la suite de la playlist à partir de la chanson suivante"""
    if len(self.main_playlist) <= self.current_index + 1:
        return  # Pas de chansons suivantes à mélanger
    
    import random
    
    # Sauvegarder la partie avant la chanson courante (incluse)
    before_current = self.main_playlist[:self.current_index + 1]
    
    # Récupérer la partie après la chanson courante
    after_current = self.main_playlist[self.current_index + 1:]
    
    # Mélanger la partie après la chanson courante
    random.shuffle(after_current)
    
    # Reconstituer la playlist
    self.main_playlist = before_current + after_current
    
    # Rafraîchir l'affichage de la playlist
    self._refresh_playlist_display()
    
    self.status_bar.config(text=f"Suite de la playlist mélangée ({len(after_current)} titres)")

def _load_circular_thumbnail(self, label, url):
    """Charge et affiche la miniature circulaire pour les chaînes"""
    try:
        import requests
        from io import BytesIO
        
        # Corriger l'URL si elle commence par //
        if url.startswith('//'):
            url = 'https:' + url
        
        response = requests.get(url, timeout=5)
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        
        # Créer une image circulaire plus grande
        size = min(THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1])
        circular_img = self._create_circular_image(img, (size, size))
        photo = ImageTk.PhotoImage(circular_img)
        
        self.root.after(0, lambda: self._display_thumbnail(label, photo))
    except Exception as e:
        print(f"Erreur chargement thumbnail circulaire: {e}")

def _display_thumbnail(self, label, photo):
    """Affiche la miniature dans le label"""
    try:
        # Vérifier si le widget existe encore avant de l'utiliser
        if label.winfo_exists():
            label.configure(image=photo)
            label.image = photo  # Garder une référence
    except tk.TclError:
        # Le widget a été détruit, ignorer silencieusement
        pass
    except Exception as e:
        print(f"Erreur affichage thumbnail: {e}")




def _load_download_thumbnail(self, filepath, label):
    """Charge la miniature pour un fichier téléchargé"""
    # Chercher une image associée (même nom mais extension image)
    base_name = os.path.splitext(filepath)[0]
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    
    thumbnail_found = False
    for ext in image_extensions:
        thumbnail_path = base_name + ext
        if os.path.exists(thumbnail_path):
            self._load_image_thumbnail(thumbnail_path, label)
            thumbnail_found = True
            break
    
    if not thumbnail_found:
        # Utiliser la miniature MP3 ou une image par défaut
        self._load_mp3_thumbnail(filepath, label)

def _truncate_text_for_display(self, text, max_width_pixels=200, max_lines=1, font_family='TkDefaultFont', font_size=9):
    """Tronque le texte pour l'affichage avec des '...' si nécessaire basé sur la largeur en pixels"""
    import tkinter.font as tkFont
    
    # Nettoyer le nom de fichier (enlever l'extension .mp3)
    if text.lower().endswith('.mp3'):
        text = text[:-4]
    
    # Créer une police pour mesurer le texte avec les paramètres fournis
    font = tkFont.Font(family=font_family, size=font_size)
    
    # Mesurer la largeur du texte complet
    text_width = font.measure(text)
    
    # Si le texte tient dans la largeur disponible, le retourner tel quel
    if text_width <= max_width_pixels:
        return text
    
    # Mesurer la largeur des "..."
    ellipsis_width = font.measure("...")
    available_width = max_width_pixels - ellipsis_width
    
    # Trouver la longueur maximale qui tient dans l'espace disponible
    truncated_text = ""
    for i, char in enumerate(text):
        test_text = text[:i+1]
        if font.measure(test_text) > available_width:
            break
        truncated_text = test_text
    
    # Si on n'a pas pu ajouter au moins un caractère, retourner juste "..."
    if not truncated_text:
        return "..."
    
    return truncated_text + "..."


def _get_existing_download(self, title):
    """Vérifie si un fichier existe déjà dans downloads avec un titre similaire"""
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
    downloads_dir = os.path.abspath("downloads")
    
    if not os.path.exists(downloads_dir):
        return None
    
    # Chercher les fichiers correspondants
    for filename in os.listdir(downloads_dir):
        # Comparer les noms normalisés (sans extension et caractères spéciaux)
        base_name = os.path.splitext(filename)[0]
        normalized_base = "".join(c for c in base_name if c.isalnum() or c in " -_")
        
        if normalized_base.startswith(safe_title[:20]) or safe_title.startswith(normalized_base[:20]):
            filepath = os.path.join(downloads_dir, filename)
            # Vérifier que c'est bien un fichier audio
            if filepath.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                return filepath
    return None

def _load_thumbnail(self, label, url):
    """Charge et affiche la miniature"""
    try:
        import requests
        from io import BytesIO
        
        # Vérifier si le widget existe encore avant de commencer le téléchargement
        try:
            if not label.winfo_exists():
                return
        except tk.TclError:
            # Le widget a été détruit
            return
        
        # Corriger l'URL si elle commence par //
        if url.startswith('//'):
            url = 'https:' + url
        
        response = requests.get(url, timeout=5)
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # Vérifier à nouveau avant d'afficher
        try:
            if label.winfo_exists():
                self.root.after(0, lambda: self._display_thumbnail(label, photo))
        except tk.TclError:
            # Le widget a été détruit entre temps
            pass
    except Exception as e:
        print(f"Erreur chargement thumbnail: {e}")


def _add_downloaded_file(self, filepath, thumbnail_path, title, url=None, add_to_playlist=True):
    """Ajoute le fichier téléchargé à la main playlist (à appeler dans le thread principal)"""
    # Vérifier si on doit ajouter à la playlist
    if add_to_playlist:
        added = self.add_to_main_playlist(filepath, thumbnail_path, show_status=False)
        if added:
            self.status_bar.config(text=f"{title} ajouté à la main playlist")
            # Marquer que la main playlist ne provient pas d'une playlist (ajout individuel)
            self.main_playlist_from_playlist = False
        else:
            self.status_bar.config(text=f"{title} est déjà dans la main playlist")
    else:
        self.status_bar.config(text=f"{title} téléchargé (non ajouté à la playlist)")
    
    print('_add_downloaded_file', title)
    # Vérifier s'il faut ajouter à la queue
    if url and hasattr(self, 'pending_queue_additions') and url in self.pending_queue_additions:
        # Ajouter à la queue via le drag drop handler
        if hasattr(self, 'drag_drop_handler'):
            self.drag_drop_handler._add_to_queue(filepath)
            self.status_bar.config(text=f"{title} ajouté à la queue")
        # Nettoyer la liste d'attente pour cette URL
        del self.pending_queue_additions[url]
    
    # Vérifier s'il faut lire après la chanson actuelle
    if url and hasattr(self, 'pending_play_after_current') and url in self.pending_play_after_current:
        # Lire après la chanson actuelle
        self._play_after_current(filepath)
        # Nettoyer la liste d'attente pour cette URL
        del self.pending_play_after_current[url]
    
    # Vérifier s'il faut placer en premier dans la queue
    if url and hasattr(self, 'pending_queue_first_additions') and url in self.pending_queue_first_additions:
        # Placer en premier dans la queue via le drag drop handler
        if hasattr(self, 'drag_drop_handler'):
            self.drag_drop_handler._add_to_queue_first(filepath)
            self.status_bar.config(text=f"{title} placé en premier dans la queue")
        # Nettoyer la liste d'attente pour cette URL
        del self.pending_queue_first_additions[url]
    
    # Vérifier s'il y a des playlists en attente pour cette URL
    if url and url in self.pending_playlist_additions:
        pending_playlists = self.pending_playlist_additions[url]
        for playlist_name in pending_playlists:
            if playlist_name == "Main Playlist":
                # La Main Playlist a déjà été gérée ci-dessus, ne rien faire
                pass
            elif playlist_name in self.playlists:
                if filepath not in self.playlists[playlist_name]:
                    self.playlists[playlist_name].append(filepath)
                    self.status_bar.config(text=f"{title} ajouté à '{playlist_name}' (en attente)")
        
        # Sauvegarder les playlists si des ajouts ont été faits
        if pending_playlists:
            self.save_playlists()
        
        # Nettoyer la liste d'attente pour cette URL
        del self.pending_playlist_additions[url]
    
    # Mettre à jour le compteur de fichiers téléchargés
    file_services._count_downloaded_files(self)
    self._update_downloads_button()
    
    # Mettre à jour la liste des téléchargements dans l'onglet bibliothèque
    self._refresh_downloads_library()


def _download_progress_hook(self, d):
    """Hook pour afficher la progression du téléchargement"""
    if d['status'] == 'downloading':
        # Extraire le pourcentage au format XX.X%
        percent_raw = d.get('_percent_str', '0.0%')
        try:
            # Extraire seulement les chiffres et le point décimal
            import re
            percent_match = re.search(r'(\d+\.?\d*)%', percent_raw)
            percent = f"{float(percent_match.group(1)):.1f}%" if percent_match else "0.0%"
        except:
            percent = "0.0%"
        
        # Extraire la vitesse au format XXX.XXKiB/s ou XXX.XXMiB/s
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
        
        title = self.current_download_title if self.current_download_title else "fichier"
        self.root.after(0, lambda: self.status_bar.config(
            text=f"Téléchargement de {title} ({percent} - {speed})"
        ))

def _download_youtube_thread(self, url, add_to_playlist=True):
    try:
        video = self.search_list[0]
        title = video['title']
        url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
        
        # Ajouter l'URL aux téléchargements en cours
        self.current_downloads.add(url)
        # print(self.current_downloads, "current _download_youtube_thread")
        self._update_search_results_ui()
        

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
            
            # Sauvegarder l'URL YouTube même pour les fichiers existants
            self.save_youtube_url_metadata(existing_file, url)
            
            self.root.after(0, lambda: self._add_downloaded_file(existing_file, thumbnail_path, title, url, add_to_playlist))
            self.root.after(0, lambda: self.status_bar.config(text=f"Fichier existant trouvé: {title}"))
            # Mettre à jour la bibliothèque même pour les fichiers existants
            self.root.after(0, lambda: self._refresh_downloads_library())
            # Remettre l'apparence normale en utilisant la fonction dédiée
            self.root.after(0, lambda: self._reset_frame_appearance(video['search_frame'], '#4a4a4a'))
            self.current_downloads.remove(url)  # Retirer de la liste quand terminé
            self._update_search_results_ui()
            return
            
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
        
        # Stocker le titre pour l'affichage de progression
        self.current_download_title = safe_title
        
        # Mettre à jour l'interface dans le thread principal
        self.root.after(0, lambda: self.status_bar.config(text=f"Téléchargement de {safe_title}..."))
        
        downloads_dir = os.path.abspath("downloads")
        if not os.path.exists(downloads_dir):
            try:
                os.makedirs(downloads_dir)
            except Exception as e:
                self.root.after(0, lambda: self.status_bar.config(text=f"Erreur création dossier: {str(e)}"))
                return

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
            'progress_hooks': [self._download_progress_hook],
            # 'extract_flat': False,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            
            print("downloaded_file", downloaded_file)
            final_path = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3').replace('.mp4', '.mp3')
            if not final_path.endswith('.mp3'):
                final_path += '.mp3'
            
            thumbnail_path = os.path.splitext(final_path)[0] + ".jpg"
            if os.path.exists(downloaded_file + ".jpg"):
                os.rename(downloaded_file + ".jpg", thumbnail_path)
            
            # Sauvegarder l'URL YouTube originale avec la date de publication
            upload_date = info.get('upload_date') if info else None
            self.save_youtube_url_metadata(final_path, url, upload_date)
            
            # Extraire et sauvegarder les métadonnées d'artiste et d'album
            self._extract_and_save_metadata(info, final_path)
            
            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, lambda: self._add_downloaded_file(final_path, thumbnail_path, safe_title, url, add_to_playlist))
            # Remettre l'apparence normale en utilisant la fonction dédiée
            self.root.after(0, lambda: self._reset_frame_appearance(video['search_frame'], '#4a4a4a'))
    
    except Exception as e:
        self.root.after(0, lambda e=e: self.status_bar.config(text=f"Erreur: {str(e)}"))
        if 'search_frame' in video:
            # Apparence d'erreur (jaune) en utilisant la fonction dédiée
            self.root.after(0, lambda: self._reset_frame_appearance(video['search_frame'], '#ffcc00', error=True))
    finally:
        # S'assurer que l'URL est retirée même en cas d'erreur
        if url in self.current_downloads:
            self.current_downloads.remove(url)
            self._update_search_results_ui()
        # Réinitialiser le titre de téléchargement
        self.current_download_title = ""

def _update_results_counter(self):
    """Met à jour le compteur de résultats affiché"""
    try:
        if hasattr(self, 'results_counter_label') and self.results_counter_label.winfo_exists():
            displayed_count = self.search_results_count
            total_count = len(self.all_search_results)
            
            # Si on a des résultats à afficher
            if total_count > 0:
                # Si on a atteint le maximum autorisé
                counter_text = f"Résultats {displayed_count}/{self.max_search_results}"
            else:
                counter_text = "Aucun résultat"
            
            self.results_counter_label.config(text=counter_text)
    except Exception as e:
        print(f"Erreur lors de la mise à jour du compteur: {e}")

def _create_circular_image(self, image, size=(60, 60)):
    """Crée une image circulaire à partir d'une image rectangulaire"""
    try:
        # Redimensionner l'image
        image = image.resize(size, Image.Resampling.LANCZOS)
        
        # Créer un masque circulaire
        mask = Image.new('L', size, 0)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        # Appliquer le masque
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(image, (0, 0))
        output.putalpha(mask)
        
        return output
    except Exception as e:
        print(f"Erreur création image circulaire: {e}")
        return image

def _extract_and_save_metadata(self, info, filepath):
    """Extrait les métadonnées depuis les informations YouTube et les sauvegarde dans le fichier MP3"""
    try:
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TPE2
        from mutagen.mp3 import MP3
        
        
        # Extraire les informations depuis YouTube
        title = info.get('title', '')
        artist = info.get('uploader', '')
        album = info.get('album', '')
        
       
        
        # Essayer d'extraire l'artiste et l'album depuis le titre et les métadonnées YouTube
        # print("Debug: _extract_and_save_metadata", info)
        
        # Sauvegarder les métadonnées dans le fichier MP3
        if artist or album:
            try:
                # Charger le fichier MP3
                audio_file = MP3(filepath, ID3=ID3)
                
                # Ajouter les tags ID3 s'ils n'existent pas
                if audio_file.tags is None:
                    audio_file.add_tags()
                
                # Sauvegarder l'artiste
                if artist:
                    audio_file.tags['TPE1'] = TPE1(encoding=3, text=artist)
                    print(f"Métadonnées: Artiste '{artist}' ajouté à {os.path.basename(filepath)}")
                
                # Sauvegarder l'album
                if album:
                    audio_file.tags['TALB'] = TALB(encoding=3, text=album)
                    print(f"Métadonnées: Album '{album}' ajouté à {os.path.basename(filepath)}")
                
                # Sauvegarder le titre nettoyé
                clean_title = title
                if artist and clean_title.startswith(artist):
                    # Enlever l'artiste du début du titre s'il y est
                    clean_title = clean_title[len(artist):].lstrip(' -:').strip()
                
                if clean_title:
                    audio_file.tags['TIT2'] = TIT2(encoding=3, text=clean_title)
                
                # Sauvegarder les modifications
                audio_file.save()
                
            except Exception as e:
                print(f"Erreur lors de la sauvegarde des métadonnées: {e}")
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des métadonnées: {e}")

def open_music_on_youtube(self, filepath):
        """Ouvre une musique sur YouTube - directement si l'URL est connue, sinon par recherche"""
        try:
            import webbrowser
            import urllib.parse
            
            # D'abord, essayer de récupérer l'URL originale
            youtube_url = self.get_youtube_url_from_metadata(filepath)
            
            if youtube_url:
                # Ouvrir directement la vidéo YouTube originale
                webbrowser.open(youtube_url)
                filename = os.path.basename(filepath)
                title = os.path.splitext(filename)[0]
                self.status_bar.config(text=f"Vidéo YouTube ouverte: {title[:50]}...")
            else:
                # Fallback: recherche YouTube
                filename = os.path.basename(filepath)
                title = os.path.splitext(filename)[0]
                
                # Nettoyer le titre pour la recherche
                search_query = title.replace("_", " ").replace("-", " ")
                
                # Encoder l'URL pour la recherche YouTube
                encoded_query = urllib.parse.quote_plus(search_query)
                youtube_search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
                
                # Ouvrir dans le navigateur
                webbrowser.open(youtube_search_url)
                
                # Afficher un message de confirmation
                self.status_bar.config(text=f"Recherche YouTube ouverte pour: {title[:50]}...")
            
        except Exception as e:
            self.status_bar.config(text=f"Erreur lors de l'ouverture YouTube: {str(e)}")

def remove_youtube_url_metadata(self, filepath):
    """Supprime l'URL YouTube des métadonnées quand un fichier est supprimé"""
    try:
        import json
        metadata_file = os.path.join("downloads", "youtube_urls.json")
        
        if not os.path.exists(metadata_file):
            return
            
        # Charger les métadonnées existantes
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        filename = os.path.basename(filepath)
        
        # Supprimer l'entrée si elle existe
        if filename in metadata:
            del metadata[filename]
            
            # Sauvegarder les métadonnées mises à jour
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"URL YouTube supprimée des métadonnées: {filename}")
        
    except Exception as e:
        print(f"Erreur suppression métadonnées YouTube: {e}")

def get_youtube_metadata(self, filepath):
    """Récupère toutes les métadonnées YouTube pour un fichier téléchargé"""
    try:
        import json
        metadata_file = os.path.join("downloads", "youtube_urls.json")
        
        if not os.path.exists(metadata_file):
            return None
            
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        filename = os.path.basename(filepath)
        file_metadata = metadata.get(filename)
        
        # Convertir l'ancien format au nouveau format si nécessaire
        if isinstance(file_metadata, str):
            return {'url': file_metadata, 'upload_date': None}
        elif isinstance(file_metadata, dict):
            return file_metadata
        else:
            return None
        
    except Exception as e:
        print(f"Erreur lecture métadonnées YouTube étendues: {e}")
        return None

def get_youtube_url_from_metadata(self, filepath):
    """Récupère l'URL YouTube originale pour un fichier téléchargé"""
    try:
        import json
        metadata_file = os.path.join("downloads", "youtube_urls.json")
        
        if not os.path.exists(metadata_file):
            return None
            
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        filename = os.path.basename(filepath)
        file_metadata = metadata.get(filename)
        
        # Compatibilité avec l'ancien format (chaîne) et nouveau format (dictionnaire)
        if isinstance(file_metadata, dict):
            return file_metadata.get('url')
        else:
            return file_metadata  # Ancien format (chaîne directe)
        
    except Exception as e:
        print(f"Erreur lecture métadonnées YouTube: {e}")
        return None

def save_youtube_url_metadata(self, filepath, youtube_url, upload_date=None):
    """Sauvegarde les métadonnées YouTube étendues pour un fichier téléchargé"""
    try:
        import json
        metadata_file = os.path.join("downloads", "youtube_urls.json")
        
        # Charger les métadonnées existantes
        metadata = {}
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except:
                metadata = {}
        
        # Ajouter les nouvelles métadonnées (maintien compatibilité avec ancien format)
        filename = os.path.basename(filepath)
        
        # Si c'est déjà au nouveau format (dictionnaire), mettre à jour
        if isinstance(metadata.get(filename), dict):
            metadata[filename]['url'] = youtube_url
            if upload_date:
                metadata[filename]['upload_date'] = upload_date
        else:
            # Créer une nouvelle entrée au format étendu
            metadata[filename] = {
                'url': youtube_url,
                'upload_date': upload_date
            }
        
        # Sauvegarder
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Erreur sauvegarde métadonnées YouTube: {e}")

def _add_downloaded_to_playlist(self, filepath, thumbnail_path, title, playlist_name, url=None):
    """Ajoute un fichier téléchargé à une playlist spécifique (à appeler dans le thread principal)"""
    if playlist_name == "Main Playlist":
        # Pour la main playlist, utiliser la nouvelle fonction centralisée
        added = self.add_to_main_playlist(filepath, thumbnail_path, show_status=False)
        if added:
            self.status_bar.config(text=f"{title} ajouté à la liste principale")
            # Marquer que la main playlist ne provient pas d'une playlist (ajout individuel)
            self.main_playlist_from_playlist = False
        else:
            self.status_bar.config(text=f"{title} est déjà dans la liste principale")
    else:
        # Pour les autres playlists
        if filepath not in self.playlists[playlist_name]:
            self.playlists[playlist_name].append(filepath)
            self.save_playlists()
            self.status_bar.config(text=f"{title} ajouté à '{playlist_name}'")
        else:
            self.status_bar.config(text=f"{title} est déjà dans '{playlist_name}'")
    
    # Vérifier s'il y a d'autres playlists en attente pour cette URL
    if url and url in self.pending_playlist_additions:
        pending_playlists = self.pending_playlist_additions[url]
        for pending_playlist_name in pending_playlists:
            if pending_playlist_name != playlist_name:
                if pending_playlist_name == "Main Playlist":
                    # Gérer spécialement la Main Playlist
                    added = self.add_to_main_playlist(filepath, thumbnail_path, show_status=False)
                    if added:
                        self.status_bar.config(text=f"{title} aussi ajouté à la liste principale (en attente)")
                        self.main_playlist_from_playlist = False
                elif pending_playlist_name in self.playlists:
                    # Gérer les autres playlists
                    if filepath not in self.playlists[pending_playlist_name]:
                        self.playlists[pending_playlist_name].append(filepath)
                        self.status_bar.config(text=f"{title} aussi ajouté à '{pending_playlist_name}' (en attente)")
        
        # Sauvegarder les playlists si des ajouts ont été faits
        if pending_playlists:
            self.save_playlists()
        
        # Nettoyer la liste d'attente pour cette URL
        del self.pending_playlist_additions[url]
    
    # Mettre à jour le compteur de fichiers téléchargés
    file_services._count_downloaded_files(self)
    self._update_downloads_button()
    
    # Mettre à jour la liste des téléchargements dans l'onglet bibliothèque
    self._refresh_downloads_library()

def _add_youtube_to_playlist(self, video, frame, playlist_name):
    """Ajoute une vidéo YouTube à une playlist (télécharge si nécessaire)"""
    title = video.get('title', 'Titre inconnu')
    
    # Vérifier si le fichier existe déjà
    existing_file = self._get_existing_download(title)
    if existing_file:
        # Le fichier existe déjà, l'ajouter directement à la playlist
        if playlist_name == "Main Playlist":
            self.add_to_main_playlist(existing_file)
        else:
            if existing_file not in self.playlists[playlist_name]:
                self.playlists[playlist_name].append(existing_file)
                self.save_playlists()
                self.status_bar.config(text=f"Ajouté à '{playlist_name}': {os.path.basename(existing_file)}")
            else:
                self.status_bar.config(text=f"Déjà dans '{playlist_name}': {os.path.basename(existing_file)}")
    else:
        # Le fichier n'existe pas, le télécharger puis l'ajouter
        self.status_bar.config(text=f"Téléchargement de {title} pour '{playlist_name}'...")
        
        # Changer l'apparence pour indiquer le téléchargement
        self._reset_frame_appearance(frame, '#ff6666')
        
        # Lancer le téléchargement dans un thread
        threading.Thread(
            target=self._download_and_add_to_playlist_thread,
            args=(video, frame, playlist_name),
            daemon=True
        ).start()

def _create_new_playlist_dialog_youtube(self, video, frame):
    """Dialogue pour créer une nouvelle playlist et y ajouter une vidéo YouTube"""
    playlist_name = simpledialog.askstring(
        "Nouvelle playlist",
        "Nom de la nouvelle playlist:",
        parent=self.root
    )
    
    if playlist_name and playlist_name.strip():
        playlist_name = playlist_name.strip()
        if playlist_name not in self.playlists:
            self.playlists[playlist_name] = []
            self.save_playlists()
            self.status_bar.config(text=f"Playlist '{playlist_name}' créée")
            
            # Ajouter la vidéo à la nouvelle playlist
            self._add_youtube_to_playlist(video, frame, playlist_name)
        else:
            self.status_bar.config(text=f"La playlist '{playlist_name}' existe déjà")

def _set_item_colors(self, item_frame, bg_color):
    """Change uniquement la couleur de fond des éléments d'un item de playlist"""
    def set_colors_recursive(widget, color):
        # Changer seulement la couleur de fond, pas le texte ni les boutons
        if hasattr(widget, 'config'):
            try:
                # Ne changer que le fond, pas les autres propriétés
                if not isinstance(widget, tk.Button):  # Exclure les boutons
                    widget.config(bg=color)
            except:
                pass  # Certains widgets ne supportent pas bg
        
        # Appliquer récursivement aux enfants
        try:
            for child in widget.winfo_children():
                set_colors_recursive(child, color)
        except:
            pass
    
    set_colors_recursive(item_frame, bg_color)

def select_song_item(self, song_item, container):
    """Met en surbrillance l'élément sélectionné dans la liste des chansons"""
    # Vérifier que le container existe
    try:
        if not container.winfo_exists():
            return
    except tk.TclError:
        return
        
    # Désélectionner tous les autres éléments et sélectionner le bon
    try:
        children = container.winfo_children()
    except tk.TclError:
        # Container détruit, ignorer
        return
        
    for child in children:
        try:
            if not child.winfo_exists():
                continue
                
            if child == song_item:
                # Sélectionner cet élément
                child.selected = True
                self._set_item_colors(child, COLOR_SELECTED)  # Couleur de surbrillance (bleu)
            else:
                # Désélectionner les autres
                child.selected = False
                self._set_item_colors(child, COLOR_BACKGROUND)  # Couleur normale
        except tk.TclError:
            # Widget détruit, ignorer
            continue

def select_song_item_from_filepath(self, filepath, container):
    """Met en surbrillance l'élément sélectionné dans la liste des chansons"""
    # Vérifier que le container existe
    try:
        if not container.winfo_exists():
            return
    except tk.TclError:
        return
        
    # Désélectionner tous les autres éléments et sélectionner le bon
    try:
        children = container.winfo_children()
    except tk.TclError:
        # Container détruit, ignorer
        return
        
    for child in children:
        try:
            if not child.winfo_exists():
                continue
                
            if hasattr(child, 'filepath'):
                if child.filepath == filepath:
                    # Sélectionner cet élément
                    child.selected = True
                    self._set_item_colors(child, COLOR_SELECTED)  # Couleur de surbrillance (bleu)
                else:
                    # Désélectionner les autres
                    child.selected = False
                    self._set_item_colors(child, COLOR_BACKGROUND)  # Couleur normale
        except tk.TclError:
            # Widget détruit, ignorer
            continue

# def select_playlist_content_item(self, current_filepath):
    
#     """Met en surbrillance l'élément sélectionné dans l'affichage du contenu d'une playlist"""
    
#     # Vérifier si on est en train de visualiser une playlist et si le container existe
#     if (hasattr(self, 'playlist_content_container') and 
#         self.playlist_content_container.winfo_exists() and
#         hasattr(self, 'current_viewing_playlist')):
        
#         # Désélectionner tous les autres éléments et sélectionner le bon
#         for child in self.playlist_content_container.winfo_children():
#             if hasattr(child, 'filepath'):
#                 if child.filepath == current_filepath:
#                     # Sélectionner cet élément
#                     child.selected = True
#                     self._set_item_colors(child, '#5a9fd8')  # Couleur de surbrillance (bleu)
#                 else:
#                     # Désélectionner les autres
#                     child.selected = False
#                     self._set_item_colors(child, '#4a4a4a')  # Couleur normale

def _delete_from_downloads(self, filepath, frame):
    """Supprime définitivement un fichier du dossier downloads"""
    try:
        if os.path.exists(filepath):
            # Vérifier si le fichier est actuellement en cours de lecture
            is_currently_playing = (filepath in self.main_playlist and 
                                    self.current_index < len(self.main_playlist) and 
                                    self.main_playlist[self.current_index] == filepath)
            
            if is_currently_playing:
                # Arrêter la lecture et libérer le fichier
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                # Nettoyer la sélection car on supprime la chanson en cours
                self.clear_all_current_song_selections()
            
            # Supprimer le fichier audio
            os.remove(filepath)
            
            # Supprimer les miniatures associées si elles existent
            base_path = os.path.splitext(filepath)[0]
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                thumbnail_path = base_path + ext
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
            
            # Supprimer l'URL YouTube des métadonnées
            self.remove_youtube_url_metadata(filepath)
            
            # Supprimer de la playlist
            if filepath in self.main_playlist:
                index = self.main_playlist.index(filepath)
                self.main_playlist.remove(filepath)
                
                # Mettre à jour l'index courant si nécessaire
                if index < self.current_index:
                    self.current_index -= 1
                elif index == self.current_index:
                    # Le fichier en cours a été supprimé, passer au suivant
                    if len(self.main_playlist) > 0:
                        # Ajuster l'index si on est à la fin de la playlist
                        if self.current_index >= len(self.main_playlist):
                            self.current_index = len(self.main_playlist) - 1
                        # Jouer la chanson suivante (ou la précédente si on était à la fin)
                        self.play_track()
                    else:
                        # Plus de chansons dans la playlist
                        self.current_index = 0
                        # Nettoyer la sélection car il n'y a plus de chanson en cours
                        self.clear_all_current_song_selections()
                        self._show_current_song_thumbnail()
                        self.status_bar.config(text="Playlist vide")
            
            # Supprimer de toutes les playlists
            for playlist_name, playlist_songs in self.playlists.items():
                if filepath in playlist_songs:
                    playlist_songs.remove(filepath)
            
            # Sauvegarder les playlists
            self.save_playlists()
            
            # Détruire l'élément de l'interface
            frame.destroy()
            
            # Mettre à jour le compteur
            file_services._count_downloaded_files(self)
            self._update_downloads_button()
            
            self.status_bar.config(text=f"Fichier supprimé définitivement: {os.path.basename(filepath)}")
            
            # Rafraîchir la bibliothèque si nécessaire
            self._refresh_downloads_library()
            
    except Exception as e:
        self.status_bar.config(text=f"Erreur suppression fichier: {str(e)}")
        print(f"Erreur suppression fichier: {e}")

def download_and_create_playlist_from_selection(self):
    """Télécharge les vidéos YouTube sélectionnées et crée une nouvelle playlist"""
    if not self.selected_items:
        return
    
    # Demander le nom de la nouvelle playlist
    playlist_name = tk.simpledialog.askstring(
        "Nouvelle playlist",
        "Nom de la nouvelle playlist:",
        parent=self.root
    )
    
    if playlist_name and playlist_name.strip():
        playlist_name = playlist_name.strip()
        
        # Vérifier que le nom n'existe pas déjà
        if playlist_name in self.playlists:
            tk.messagebox.showerror("Erreur", f"Une playlist nommée '{playlist_name}' existe déjà.")
            return
        
        youtube_urls = [item for item in self.selected_items if item.startswith("https://www.youtube.com/watch?v=")]
        local_files = [item for item in self.selected_items if not item.startswith("https://www.youtube.com/watch?v=")]
        
        # Créer la nouvelle playlist avec les fichiers locaux
        self.playlists[playlist_name] = list(local_files)
        self.save_playlists()
        
        # Télécharger les vidéos YouTube
        if youtube_urls:
            self.status_bar.config(text=f"Téléchargement de {len(youtube_urls)} vidéo(s) pour la nouvelle playlist '{playlist_name}'...")
            threading.Thread(target=self._download_youtube_selection, args=(youtube_urls, playlist_name), daemon=True).start()
        else:
            self.status_bar.config(text=f"Playlist '{playlist_name}' créée avec {len(local_files)} musique(s)")
        
        # Effacer la sélection
        self.clear_selection()
        
        # Rafraîchir l'affichage des playlists si on est dans l'onglet playlists
        if hasattr(self, 'current_library_tab') and self.current_library_tab == "playlists":
            self._display_playlists()

def _should_load_more_results(self):
    """Vérifie si on doit charger plus de résultats"""
    if (self.is_loading_more or 
        self.is_searching or
        not self.current_search_query or 
        self.search_results_count >= self.max_search_results or
        self.current_search_batch >= self.max_search_batchs):
        return False
    
    # Vérifier si on est proche du bas
    try:
        # Obtenir la position actuelle du scroll (0.0 à 1.0)
        scroll_top, scroll_bottom = self.youtube_canvas.yview()
        
        # Si on est à plus de 80% vers le bas, charger plus
        if scroll_bottom > 0.8:
            return True
        
        return False
    except Exception as e:
        print(f"Erreur détection scroll: {e}")
        return False

def play_track(self):
    try:
        song = self.main_playlist[self.current_index]
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(start=0)
        self.base_position = 0
        
        # Enlever cette musique de la queue si elle y est
        if (hasattr(self, 'queue_items') and 
            self.current_index in self.queue_items):
            self.queue_items.discard(self.current_index)
        
        # Démarrer le suivi des statistiques pour cette chanson
        self._start_song_stats_tracking(song)
        
        # Charger l'offset de volume spécifique à cette musique
        self.volume_offset = self.volume_offsets.get(song, 0)
        # Mettre à jour le slider d'offset
        if hasattr(self, 'volume_offset_slider'):
            self.volume_offset_slider.set(self.volume_offset)
        
        # Appliquer le volume avec l'offset
        self._apply_volume()
        
        self.paused = False
        self.play_button.config(image=self.icons["pause"])
        self.play_button.config(text="Pause")
        
        # Mettre en surbrillance la piste courante dans la playlist (sans scrolling automatique)
        try:
            self.select_playlist_item(index=self.current_index, auto_scroll=False)
        except tk.TclError:
            # Playlist container non accessible, ignorer
            pass
        
        # Mettre en surbrillance la piste courante dans la bibliothèque aussi
        self.select_library_item_from_filepath(song)
        
        # Mettre en surbrillance la piste courante dans l'affichage du contenu de playlist si on y est
        self.select_playlist_content_item_from_filepath(song)
        
        # Mettre à jour la miniature dans la zone de recherche si elle est vide
        try:
            if (not self.current_search_query and 
                hasattr(self, 'results_container') and self.results_container.winfo_exists()):
                
                # Vérifier le nombre d'enfants de manière sécurisée
                try:
                    children = self.results_container.winfo_children()
                    children_count = len(children)
                except tk.TclError:
                    # Erreur lors de l'accès aux enfants, ignorer
                    children = []
                    children_count = 0
                
                if children_count <= 1:
                    # Vider d'abord la zone
                    for widget in children:
                        try:
                            if widget.winfo_exists():
                                widget.destroy()
                        except tk.TclError:
                            continue
                    # Afficher la nouvelle miniature
                    self._show_current_song_thumbnail()
        except tk.TclError:
            # Results container non accessible, ignorer
            pass
        
        # Update info
        audio = MP3(song)
        self.song_length = audio.info.length
        self.progress.config(to=self.song_length)
        self.song_length_label.config(text=time.strftime(
            '%M:%S', time.gmtime(self.song_length))
        )

        # Obtenir le nom du fichier sans extension
        song_name = os.path.basename(song)[:-4] if os.path.basename(song).lower().endswith('.mp3') else os.path.basename(song)
        
        # Obtenir les métadonnées
        artist, album = self._get_audio_metadata(song)
        metadata_text = self._format_artist_album_info(artist, album, song)
        
        # Démarrer l'animation du titre (seulement le titre)
        self._start_title_animation(song_name)
        
        # Mettre à jour les métadonnées séparément
        try:
            if hasattr(self, 'song_metadata_label') and self.song_metadata_label.winfo_exists():
                self.song_metadata_label.config(text=metadata_text)
        except tk.TclError:
            # Label détruit, ignorer
            pass

        self.status_bar.config(text="Playing")
        
        self.generate_waveform_preview(song)

    except Exception as e:
        self.status_bar.config(text=f"Erreur: {str(e)}")

def add_selection_to_playlist(self, playlist_name):
    """Ajoute tous les éléments sélectionnés à une playlist"""
    if playlist_name not in self.playlists:
        return
    
    added_count = 0
    for filepath in self.selected_items:
        if filepath not in self.playlists[playlist_name]:
            self.playlists[playlist_name].append(filepath)
            added_count += 1
    
    # Sauvegarder les playlists
    self.save_playlists()
    
    # Afficher un message de confirmation
    self.status_bar.config(text=f"{added_count} musique(s) ajoutée(s) à '{playlist_name}'")
    
    # Effacer la sélection
    self.clear_selection()

def _show_pending_playlist_menu(self, video, frame, url):
    """Affiche un menu pour ajouter une musique en cours de téléchargement à une playlist"""
    import tkinter.ttk as ttk
    
    title = video.get('title', 'Titre inconnu')
    
    # Créer un menu contextuel
    menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
                    activebackground='#4a8fe7', activeforeground='white')
    
    menu.add_command(
        label=f"📥 {title[:30]}{'...' if len(title) > 30 else ''}",
        state='disabled'
    )
    menu.add_separator()
    
    # Vérifier quelles playlists sont déjà en attente pour cette URL
    pending_playlists = self.pending_playlist_additions.get(url, [])
    
    # Ajouter les playlists existantes
    for playlist_name in self.playlists.keys():
        if playlist_name in pending_playlists:
            menu.add_command(
                label=f"✓ '{playlist_name}' (en attente)",
                state='disabled'
            )
        else:
            menu.add_command(
                label=f"Ajouter à '{playlist_name}' après téléchargement",
                command=lambda name=playlist_name: self._add_to_pending_playlist(url, name, title)
            )
    
    menu.add_separator()
    
    # Option pour créer une nouvelle playlist
    menu.add_command(
        label="Créer nouvelle playlist...",
        command=lambda: self._create_new_playlist_for_pending(url, title)
    )
    
    # Afficher le menu à la position de la souris
    try:
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    except:
        # Fallback
        menu.post(100, 100)

def add_selection_to_queue_last(self):
    """Ajoute tous les éléments sélectionnés à la fin de la queue (lire bientôt)"""
    if not self.selected_items:
        return
        
    added_count = 0
    
    # Initialiser queue_items si nécessaire
    if not hasattr(self, 'queue_items'):
        self.queue_items = set()
    
    # Trouver la dernière position de la queue ou utiliser la fin de la playlist
    if self.queue_items:
        # Trouver l'index le plus élevé dans la queue
        last_queue_position = max(self.queue_items) + 1
    else:
        # Pas de queue existante, insérer après la chanson courante
        last_queue_position = self.current_index + 1 if len(self.main_playlist) > 0 else 0
    
    # Assurer que la position est dans les limites
    last_queue_position = min(last_queue_position, len(self.main_playlist))
    
    # Ajouter chaque fichier à la fin de la queue
    for i, filepath in enumerate(self.selected_items_order):
        if not filepath.startswith("https://"):
            # Ajouter à la main playlist s'il n'y est pas déjà
            if filepath not in self.main_playlist:
                # Insérer à la position de fin de queue
                current_insert_pos = last_queue_position + i
                self.main_playlist.insert(current_insert_pos, filepath)
                
                # Mettre à jour les indices de la queue (décaler ceux qui viennent après)
                updated_queue = set()
                for queue_index in self.queue_items:
                    if queue_index >= current_insert_pos:
                        updated_queue.add(queue_index + 1)
                    else:
                        updated_queue.add(queue_index)
                self.queue_items = updated_queue
                
                # Ajouter cette position à la queue
                self.queue_items.add(current_insert_pos)
                added_count += 1
                
                # Ajuster l'index courant si nécessaire
                if current_insert_pos <= self.current_index:
                    self.current_index += 1
            else:
                # Le fichier existe déjà, trouver sa position et l'ajouter à la queue
                existing_index = self.main_playlist.index(filepath)
                self.queue_items.add(existing_index)
    
    # Rafraîchir l'affichage
    self._refresh_playlist_display()
    
    # Afficher le statut
    if added_count > 0:
        self.status_bar.config(text=f"Ajouté {added_count} élément(s) en queue (lire bientôt)")
    else:
        self.status_bar.config(text="Éléments ajoutés à la queue")
        
    # Effacer la sélection (différé pour éviter les conflits d'interface)
    self.safe_after(100, self.clear_selection)
    
    # Marquer que la main playlist ne provient pas d'une playlist
    self.main_playlist_from_playlist = False

def add_selection_to_queue_first(self):
    """Ajoute tous les éléments sélectionnés au début de la queue (lire ensuite)"""
    print("DEBUG: add_selection_to_queue_first appelé")
    if not self.selected_items:
        return
        
    added_count = 0
    
    # Position d'insertion : juste après la chanson actuelle
    if len(self.main_playlist) == 0:
        # Pas de playlist, ajouter normalement
        for filepath in self.selected_items_order:
            if not filepath.startswith("https://"):
                if self.add_to_main_playlist(filepath, show_status=False):
                    added_count += 1
    else:
        insert_position = self.current_index + 1
        
        # Initialiser queue_items si nécessaire
        if not hasattr(self, 'queue_items'):
            self.queue_items = set()
        
        # Ajouter chaque fichier dans l'ordre à la position d'insertion
        for i, filepath in enumerate(self.selected_items_order):
            if not filepath.startswith("https://"):
                # Ajouter à la main playlist s'il n'y est pas déjà
                if filepath not in self.main_playlist:
                    # Insérer à la position courante
                    current_insert_pos = insert_position + i
                    self.main_playlist.insert(current_insert_pos, filepath)
                    
                    # Mettre à jour les indices de la queue (décaler ceux qui viennent après)
                    updated_queue = set()
                    for queue_index in self.queue_items:
                        if queue_index >= current_insert_pos:
                            updated_queue.add(queue_index + 1)
                        else:
                            updated_queue.add(queue_index)
                    self.queue_items = updated_queue
                    
                    # Ajouter cette position à la queue
                    self.queue_items.add(current_insert_pos)
                    added_count += 1
                    
                    # Ajuster l'index courant si nécessaire
                    if current_insert_pos <= self.current_index:
                        self.current_index += 1
                else:
                    # Le fichier existe déjà, trouver sa position et l'ajouter à la queue
                    existing_index = self.main_playlist.index(filepath)
                    self.queue_items.add(existing_index)
    
    # Rafraîchir l'affichage
    self._refresh_playlist_display()
    
    # Afficher le statut
    if added_count > 0:
        self.status_bar.config(text=f"Ajouté {added_count} élément(s) en queue (lire ensuite)")
    else:
        self.status_bar.config(text="Éléments ajoutés à la queue")
        
    # Effacer la sélection (différé pour éviter les conflits d'interface)
    self.safe_after(100, self.clear_selection)
    
    # Marquer que la main playlist ne provient pas d'une playlist
    self.main_playlist_from_playlist = False

def _add_song_item(self, filepath, container, playlist_name=None, song_index=None):
    """Ajoute une musique dans la playlist affichée, visuel"""
    try:
        filename = os.path.basename(filepath)
        
        # Vérifier si c'est la chanson en cours de lecture
        is_current_song = (len(self.main_playlist) > 0 and 
                            self.current_index < len(self.main_playlist) and 
                            self.main_playlist[self.current_index] == filepath)
        
        # Frame principal - même style que les téléchargements
        bg_color = COLOR_SELECTED if is_current_song else COLOR_BACKGROUND
        item_frame = tk.Frame(
            container,
            bg=bg_color,
            relief='flat',
            bd=1,
            highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
            highlightthickness=1,
            
        )
        item_frame.selected = is_current_song

        if hasattr(self, 'playlist_content_container') and container == self.playlist_content_container:
            padx = DISPLAY_PLAYLIST_PADX
            pady = DISPLAY_PLAYLIST_PADY
        elif container == self.downloads_container:
            padx = CARD_FRAME_PADX
            pady = CARD_FRAME_PADY
        else:
            padx = 5
            pady = 5

        item_frame.pack(fill="x", padx=padx, pady=pady)

        # Stocker les informations pour pouvoir les retrouver plus tard
        item_frame.filepath = filepath
        item_frame.selected = is_current_song
        
        if hasattr(self, 'playlist_content_container') and container == self.playlist_content_container:
            if playlist_name is not None and song_index is not None:
                item_frame.playlist_name = playlist_name
                item_frame.song_index = song_index
            else:
                print("_add_song_item pour playlist, playlist_name ou song_index manquant")

        # Vérifier si cette musique fait partie de la queue dans la main playlist
        is_in_queue = False
        if hasattr(self, 'queue_items') and hasattr(self, 'main_playlist'):
            # Chercher toutes les positions de ce fichier dans la main playlist
            for i, main_filepath in enumerate(self.main_playlist):
                if main_filepath == filepath and i in self.queue_items:
                    is_in_queue = True
                    break
        
        # Configuration de la grille en 6 colonnes : trait queue, numéro, miniature, texte, durée, bouton
        item_frame.columnconfigure(0, minsize=4, weight=0)   # Trait queue (si applicable)
        item_frame.columnconfigure(1, minsize=0, weight=0)  # Numéro
        item_frame.columnconfigure(2, minsize=80, weight=0)  # Miniature
        item_frame.columnconfigure(3, weight=1)              # Texte
        item_frame.columnconfigure(4, minsize=60, weight=0)  # Durée
        item_frame.columnconfigure(5, minsize=80, weight=0)  # Bouton
        item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
        
        # 1. Trait vertical queue (colonne 0) - seulement si la musique est dans la queue
        # if is_in_queue:
        #     queue_indicator = tk.Frame(
        #         item_frame,
        #         bg='black',  # Trait noir
        #         width=3
        #     )
        #     queue_indicator.grid(row=0, column=0, sticky='ns', padx=(2, 2), pady=2)
        #     queue_indicator.grid_propagate(False)

        queue_indicator = tk.Frame(
            item_frame,
            bg=COLOR_BACKGROUND,
            width=3
        )
        queue_indicator.grid(row=0, column=0, sticky='ns', padx=(0, 2), pady=0)
        queue_indicator.grid_propagate(False)
        
            
        item_frame.queue_indicator = queue_indicator
        item_frame.is_in_queue = is_in_queue
        
        if is_in_queue:
            self.show_queue_indicator(item_frame)

        # 2. Numéro de la chanson (colonne 1)
        number_label = tk.Label(
            item_frame,
            text=str(song_index + 1) if song_index is not None else "",  # +1 pour commencer à 1 au lieu de 0
            bg=bg_color,
            fg='white',
            font=('TkDefaultFont', 10, 'bold'),
            anchor='center'
        )
        number_label.grid(row=0, column=1, sticky='nsew', padx=(10, 5), pady=2)
        
        # 3. Miniature (colonne 2)
        thumbnail_label = tk.Label(
            item_frame,
            bg=bg_color,
            width=10,
            height=3,
            anchor='center',
            text="⏵"  # Icône temporaire
        )
        thumbnail_label.grid(row=0, column=2, sticky='nsew', padx=(5, 4), pady=2)
        thumbnail_label.grid_propagate(False)
        
        # Stocker la référence pour le chargement différé
        thumbnail_label.filepath = filepath
        
        # # Charger la miniature
        # self._load_download_thumbnail(filepath, thumbnail_label)
        
        # 4. Texte (colonne 3) - Frame contenant titre et métadonnées
        text_frame = tk.Frame(item_frame, bg=bg_color)
        text_frame.grid(row=0, column=3, sticky='nsew', padx=(0, 2), pady=4)
        text_frame.columnconfigure(0, weight=1)
        
        # Titre principal
        truncated_title = self._truncate_text_for_display(filename, max_width_pixels=328, font_family='TkDefaultFont', font_size=9)
        title_label = tk.Label(
            text_frame,
            text=truncated_title,
            bg=bg_color,
            fg='white',
            font=('TkDefaultFont', 9),
            anchor='nw',
            justify='left'
        )
        title_label.grid(row=0, column=0, sticky='ew', pady=(2, 0))
        
        # Métadonnées (artiste • album • date)
        artist, album = self._get_audio_metadata(filepath)
        
        # Frame pour les métadonnées avec artiste cliquable
        metadata_frame = tk.Frame(text_frame, bg=bg_color)
        metadata_frame.grid(row=1, column=0, sticky='ew', pady=(0, 2))
        metadata_frame.columnconfigure(0, weight=0)  # Artiste
        metadata_frame.columnconfigure(1, weight=1)  # Autres infos
        
        # Label pour l'artiste (cliquable)
        artist_label = tk.Label(
            metadata_frame,
            text="",  # Sera rempli lors du chargement différé
            bg=bg_color,
            fg='#4da6ff',  # Couleur bleue pour indiquer que c'est cliquable
            font=('TkDefaultFont', 8, 'underline'),
            anchor='nw',
            justify='left',
            cursor='hand2'
        )
        artist_label.grid(row=0, column=0, sticky='w')
        
        # Label pour les autres métadonnées (album • date)
        other_metadata_label = tk.Label(
            metadata_frame,
            text="",  # Sera rempli lors du chargement différé
            bg=bg_color,
            fg='#cccccc',
            font=('TkDefaultFont', 8),
            anchor='nw',
            justify='left'
        )
        other_metadata_label.grid(row=0, column=1, sticky='w', padx=(5, 0))
        
        # Stocker les références pour le chargement différé des métadonnées
        artist_label.filepath = filepath
        other_metadata_label.filepath = filepath
        
        # Fonction pour gérer le clic sur l'artiste
        def on_artist_click(event):
            # Récupérer les métadonnées pour obtenir l'artiste
            artist, _ = self._get_audio_metadata(filepath)
            if artist:
                # Essayer d'obtenir les métadonnées YouTube pour récupérer l'URL de la chaîne
                video_data = {}
                try:
                    youtube_metadata = self.get_youtube_metadata(filepath)
                    if youtube_metadata:
                        # Essayer d'obtenir l'URL de la chaîne depuis les métadonnées
                        channel_url = (youtube_metadata.get('channel_url') or 
                                     youtube_metadata.get('uploader_url') or 
                                     youtube_metadata.get('channel'))
                        if channel_url:
                            video_data['channel_url'] = channel_url
                except Exception:
                    pass
                
                # Si pas d'URL trouvée, utiliser le fallback
                if 'channel_url' not in video_data:
                    import urllib.parse
                    # Nettoyer le nom de l'artiste pour l'URL
                    clean_artist = artist.replace(' ', '').replace('　', '').replace('/', '')
                    encoded_artist = urllib.parse.quote(clean_artist, safe='')
                    video_data['channel_url'] = f"https://www.youtube.com/@{encoded_artist}"
                
                self._show_artist_content(artist, video_data)
        
        # Bind du clic sur l'artiste
        artist_label.bind("<Button-1>", on_artist_click)
        
        # 5. Durée (colonne 4)
        duration_label = tk.Label(
            item_frame,
            text=self._get_audio_duration(filepath),
            bg=bg_color,
            fg='#cccccc',
            font=('TkDefaultFont', 8),
            anchor='center'
        )
        duration_label.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
        
        # 6. Bouton "Supprimer de la playlist" (colonne 5) avec icône delete
        # remove_btn = tk.Button(
        #     item_frame,
        #     image=self.icons["delete"],  # Utiliser l'icône delete non rognée
        #     bg=bg_color,
        #     activebackground='#ff6666',
        #     relief='flat',
        #     bd=0,
        #     padx=5,
        #     pady=5,
        #     takefocus=0
        # )
        delete_btn = tk.Button(
            item_frame,
            image=self.icons['delete'],
            bg=bg_color,
            fg='white',
            activebackground='#ff6666',
            relief='flat',
            bd=0,
            width=self.icons['delete'].width(),
            height=self.icons['delete'].height(),
            font=('TkDefaultFont', 8),
            takefocus=0
        )
        
        delete_btn.grid(row=0, column=5, sticky='ns', padx=(0, 10), pady=8)
        create_tooltip(delete_btn, "Supprimer de la playlist\nDouble-clic: Retirer de cette playlist\nCtrl + Double-clic: Supprimer définitivement du disque")
        
        # Gestion des clics pour la sélection multiple
        def on_item_left_click(event):
            # Initialiser le drag pour le clic gauche
            self.drag_drop_handler.setup_drag_start(event, item_frame)
            
            # Vérifier si Ctrl est enfoncé pour ouvrir sur YouTube
            if event.state & 0x4:  # Ctrl est enfoncé
                self.open_music_on_youtube(filepath)
                return
            
            # Initialiser le drag
            # self.drag_drop_handler.setup_drag_start(event, item_frame)
            
            # Vérifier si Shift est enfoncé pour la sélection multiple
            if event.state & 0x1:  # Shift est enfoncé
                self.shift_selection_active = True
                self.toggle_item_selection(filepath, item_frame)
            else:
                # Clic normal sans Shift - ne pas effacer la sélection si elle existe
                pass
        
        def on_item_left_double_click(event):
            # Vérifier si Shift est enfoncé ou si on est en mode sélection - ne rien faire
            if event.state & 0x1 or self.selected_items:  # Shift est enfoncé ou mode sélection
                pass
            else:
                if hasattr(self, 'playlist_content_container') and container == self.playlist_content_container:
                    # Comportement normal : lancer la playlist depuis cette musique
                    self._play_playlist_from_song(playlist_name, song_index)
                elif container == self.downloads_container:
                    self._add_download_to_playlist(filepath)
                    if filepath in self.main_playlist:
                        self.current_index = self.main_playlist.index(filepath)
                        self.play_track()
        
        def on_item_right_click(event):
            try:
                # Désactiver temporairement l'initialisation du drag pour le clic droit
                # car cela pourrait causer des conflits avec le menu contextuel
                # print("DEBUG: Avant setup_drag_start")
                # self.drag_drop_handler.setup_drag_start(event, item_frame)
                # print("DEBUG: Après setup_drag_start")
                
                # Si on a des éléments sélectionnés, ouvrir le menu de sélection
                if self.selected_items:
                    self.show_selection_menu(event)
                else:
                    print("DEBUG: Appel de _show_single_file_menu")
                    # Ouvrir le menu contextuel pour choisir où ajouter la musique
                    self._show_single_file_menu(event, filepath)
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        # # Gestionnaire pour initialiser le drag sur clic gauche
        # def on_left_button_press(event):
        #     # Initialiser le drag pour le clic gauche
        #     self.drag_drop_handler.setup_drag_start(event, item_frame)
        #     # Appeler aussi le gestionnaire de clic normal
        #     on_item_click(event)
        
        # Wrapper pour logger tous les clics droits
        def debug_right_click_wrapper(event):
            return on_item_right_click(event)
        
        # Bindings pour tous les éléments cliquables (sauf l'artiste qui a son propre binding)
        widgets_to_bind = [item_frame, number_label, thumbnail_label, text_frame, title_label, duration_label, metadata_frame, other_metadata_label]
        
        for widget in widgets_to_bind:
            widget.bind("<ButtonPress-1>", on_item_left_click)
            widget.bind("<Double-1>", on_item_left_double_click)
            widget.bind("<ButtonPress-3>", debug_right_click_wrapper)
        
        def on_delete_double_click_download(event):
            if event.state & 0x4:
                self._delete_from_downloads(filepath, item_frame)
            else:
                if filepath in self.main_playlist:
                    index = self.main_playlist.index(filepath)
                    self.main_playlist.remove(filepath)
                    if index < self.current_index:
                        self.current_index -= 1
                    elif index == self.current_index:
                        pygame.mixer.music.stop()
                        self.current_index = min(index, len(self.main_playlist) - 1)
                        if len(self.main_playlist) > 0:
                            self.play_track()
                        else:
                            pygame.mixer.music.unload()
                            self._show_current_song_thumbnail()
                    self._refresh_playlist_display()
                    self.status_bar.config(text=f"Retiré de la playlist: {os.path.basename(filepath)}")
        
        
        if hasattr(self, 'playlist_content_container') and container == self.playlist_content_container:
            delete_btn.bind("<Double-1>", lambda event: self._remove_from_playlist_view(filepath, playlist_name, event))
        elif container == self.downloads_container:
            delete_btn.bind("<Double-1>", on_delete_double_click_download)
        else:
            print("_add_song_item > delete_btn.bind, Container inconnu")

        # Configuration du drag-and-drop
        self.drag_drop_handler.setup_drag_drop(item_frame, file_path=filepath, item_type="playlist_item")
        
        if hasattr(self, 'playlist_content_container') and container == self.playlist_content_container:
            self.drag_drop_handler.setup_drag_drop(item_frame, file_path=filepath, item_type="playlist_item")
        elif container == self.downloads_container:
            self.drag_drop_handler.setup_drag_drop(item_frame, file_path=filepath, item_type="file")
        else:
            print("_add_song_item > self.drag_drop_handler.setup_drag_drop, Container inconnu")
        
        # CORRECTION: Forcer les bindings de motion après tous les autres bindings
        # pour éviter qu'ils soient écrasés
        def force_motion_bindings():
            widgets_to_fix = [item_frame, number_label, thumbnail_label, text_frame, title_label, duration_label, metadata_frame, other_metadata_label]
            
            for widget in widgets_to_fix:
                if widget and widget.winfo_exists():
                    widget.bind("<B1-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f))
                    widget.bind("<ButtonRelease-1>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f))
                    widget.bind("<B3-Motion>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_motion(e, f))
                    widget.bind("<ButtonRelease-3>", lambda e, f=item_frame: self.drag_drop_handler._on_drag_release(e, f))
        
        # Programmer l'exécution après que tous les bindings soient configurés
        # Utiliser un délai pour s'assurer que c'est vraiment appliqué en dernier
        self.root.after(50, force_motion_bindings)
        
        # Tooltip pour expliquer les interactions
        # tooltip_text = f"Musique de playlist\nDouble-clic: Lancer la playlist depuis cette musique\nCtrl + Clic: Ouvrir sur YouTube\nDrag vers la droite: Ajouter à la queue\nDrag vers la gauche: Placer en premier dans la queue\nShift + Clic: Sélection multiple\nClic droit: Ajouter à la main playlist"
        tooltip_text = "blabla à écrire"
        create_tooltip(title_label, tooltip_text)
        create_tooltip(thumbnail_label, tooltip_text)
        
        # Tooltip spécifique pour l'artiste cliquable
        create_tooltip(artist_label, "Cliquer pour voir les musiques et sorties de cet artiste")

    except Exception as e:
        if hasattr(self, 'playlist_content_container') and container == self.playlist_content_container:
            print(f"Erreur affichage musique playlist: {e}")
        elif container == self.downloads_container:
            print(f"Erreur affichage musique téléchargées: {e}")
        else:
            print(f"Erreur affichage musique quelque part inconnu: {e}")

def _start_thumbnail_loading(self, files_to_display, container):
    """Lance le chargement différé des miniatures et durées"""
    # Annuler le chargement précédent s'il existe
    if hasattr(self, 'thumbnail_loading_timer_id') and self.thumbnail_loading_timer_id:
        self.root.after_cancel(self.thumbnail_loading_timer_id)
        self.thumbnail_loading_timer_id = None
    
    if not hasattr(self, 'thumbnail_loading_queue'):
        self.thumbnail_loading_queue = []
    
    # Ajouter tous les fichiers à la queue de chargement
    self.thumbnail_loading_queue = files_to_display.copy()
    
    # Commencer le chargement
    self._load_next_thumbnail(container)

def _load_next_thumbnail(self, container):
    """Charge la prochaine miniature dans la queue (version avec cache)"""
    if not hasattr(self, 'thumbnail_loading_queue') or not self.thumbnail_loading_queue:
        return
    
    # Vérifier si le container existe encore
    try:
        if not container.winfo_exists():
            # Container détruit, arrêter le chargement et nettoyer
            self.thumbnail_loading_queue = []
            self.thumbnail_loading_timer_id = None
            return
    except tk.TclError:
        # Container détruit, arrêter le chargement et nettoyer
        self.thumbnail_loading_queue = []
        self.thumbnail_loading_timer_id = None
        return
    
    # Prendre le prochain fichier
    filepath = self.thumbnail_loading_queue.pop(0)
    
    # Trouver les widgets correspondants
    try:
        for widget in container.winfo_children():
            if hasattr(widget, 'filepath') and widget.filepath == filepath:
                # Fonction récursive pour trouver tous les labels avec filepath
                def find_labels_with_filepath(parent_widget, target_filepath):
                    labels = []
                    for child in parent_widget.winfo_children():
                        if isinstance(child, tk.Label) and hasattr(child, 'filepath') and child.filepath == target_filepath:
                            labels.append(child)
                        elif hasattr(child, 'winfo_children'):  # Parcourir récursivement les frames
                            labels.extend(find_labels_with_filepath(child, target_filepath))
                    return labels
                
                # Trouver tous les labels avec ce filepath
                all_labels = find_labels_with_filepath(widget, filepath)
                
                for label in all_labels:
                    if label.cget('text') == "⏵":  # C'est le label de miniature
                        self._load_cached_thumbnail(filepath, label)
                    elif label.cget('text') == "--:--":  # C'est le label de durée
                        duration = self._get_cached_duration(filepath)
                        label.config(text=duration)
                    elif label.cget('text') == "":  # C'est un label de métadonnées
                        # Vérifier si c'est le label d'artiste ou d'autres métadonnées
                        if label.cget('fg') == '#4da6ff':  # C'est le label d'artiste (couleur bleue)
                            artist, _ = self._get_audio_metadata(filepath)
                            if artist:
                                label.config(text=artist)
                        elif label.cget('fg') == '#cccccc':  # C'est le label d'autres métadonnées
                            artist, album = self._get_audio_metadata(filepath)
                            # Créer le texte des autres métadonnées (album • date)
                            other_parts = []
                            if album:
                                other_parts.append(album)
                            
                            # Ajouter la date si le filepath est fourni
                            if os.path.exists(filepath):
                                date_str = None
                                try:
                                    # Essayer d'obtenir la date de publication YouTube
                                    youtube_metadata = self.get_youtube_metadata(filepath)
                                    if youtube_metadata and youtube_metadata.get('upload_date'):
                                        upload_date = youtube_metadata['upload_date']
                                        import datetime
                                        date_obj = datetime.datetime.strptime(upload_date, "%Y%m%d")
                                        date_str = date_obj.strftime("%d/%m/%y")
                                except Exception:
                                    pass
                                
                                if date_str:
                                    other_parts.append(date_str)
                            
                            other_metadata_text = " • ".join(other_parts) if other_parts else ""
                            if other_metadata_text:
                                # Ajouter le séparateur • au début si on a des données
                                label.config(text="• " + other_metadata_text)
                break
    except tk.TclError:
        # Erreur lors de l'accès aux widgets, probablement détruits
        self.thumbnail_loading_queue = []
        self.thumbnail_loading_timer_id = None
        return
    
    # Programmer le chargement suivant
    if self.thumbnail_loading_queue:
        self.thumbnail_loading_timer_id = self.root.after(5, lambda: self._load_next_thumbnail(container))  # Délai réduit avec le cache
    else:
        # Chargement terminé, réinitialiser l'ID du timer
        self.thumbnail_loading_timer_id = None

def hide_queue_indicator(self, song_item):
    """Cache l'indicateur de queue"""
    print(f"DEBUG: hide_queue_indicator {song_item.filepath}")
    if not(hasattr(song_item, 'queue_indicator') and hasattr(song_item, 'is_in_queue')):    # Lorsqu'on display toutes les musiques au début
        return
    
    # is_current_song = (len(self.main_playlist) > 0 and 
    #                         self.current_index < len(self.main_playlist) and 
    #                         self.main_playlist[self.current_index] == song_item.filepath)

    song_item.queue_indicator.config(bg=COLOR_SELECTED if song_item.selected else COLOR_BACKGROUND)

def show_queue_indicator(self, song_item):
    """Affiche l'indicateur de queue"""
    song_item.queue_indicator.config(bg='black')
    # print(f"DEBUG: bg: {song_item.queue_indicator.cget('bg')}, show_queue_indicator {song_item.filepath}")

def update_is_in_queue(self, song_frame):
    """Vérifier si cette musique fait partie de la queue dans la main playlist"""
    is_in_queue = False
    if hasattr(self, 'queue_items') and hasattr(self, 'main_playlist'):
        # Chercher toutes les positions de ce fichier dans la main playlist
        for i, main_filepath in enumerate(self.main_playlist):
            if main_filepath == song_frame.filepath and i in self.queue_items:
                is_in_queue = True
                break
    song_frame.is_in_queue = is_in_queue

    # print(f"DEBUG: {is_in_queue}, {song_frame.filepath}")

def update_visibility_queue_indicator(self, song_frame):
    """Met à jour la visibilité de l'indicateur de queue pour une chanson donnée"""
    # print(f"DEBUG: is_in_queue: {song_frame.is_in_queue}, update_visibility_queue_indicator {song_frame.filepath}")
    if song_frame.is_in_queue:
        self.show_queue_indicator(song_frame)
    else:
        self.hide_queue_indicator(song_frame)

def _update_stats_bar(self):
    """Met à jour la barre de statistiques avec le temps de recherche"""
    if not hasattr(self, 'stats_bar'):
        return
        
    if self.last_search_time > 0:
        self.stats_bar.config(text=f"recherche en {self.last_search_time:.2f}s")
    else:
        self.stats_bar.config(text="")

def _get_audio_duration(self, filepath):
        """Récupère la durée d'un fichier audio"""
        try:
            if filepath.lower().endswith('.mp3'):
                audio = MP3(filepath)
                duration = audio.info.length
            else:
                # Pour les autres formats, utiliser pydub
                audio = AudioSegment.from_file(filepath)
                duration = len(audio) / 1000.0  # pydub donne en millisecondes
            
            return time.strftime('%M:%S', time.gmtime(duration))
        except:
            return "??:??"

def _get_audio_metadata(self, filepath):
    """Récupère les métadonnées d'un fichier audio (artiste et album)"""
    try:
        if filepath.lower().endswith('.mp3'):
            from mutagen.id3 import ID3
            audio = MP3(filepath)
            
            # Extraire l'artiste
            artist = None
            if 'TPE1' in audio:  # Artist
                artist = str(audio['TPE1'])
            elif 'TPE2' in audio:  # Album artist
                artist = str(audio['TPE2'])
            
            # Extraire l'album
            album = None
            if 'TALB' in audio:  # Album
                album = str(audio['TALB'])
            
            return artist, album
        else:
            # Pour les autres formats, utiliser mutagen générique
            from mutagen import File
            audio = File(filepath)
            if audio is None:
                return None, None
            
            # Extraire l'artiste (différents tags possibles)
            artist = None
            for tag in ['ARTIST', 'artist', 'Artist']:
                if tag in audio:
                    artist = audio[tag][0] if isinstance(audio[tag], list) else str(audio[tag])
                    break
            
            # Extraire l'album
            album = None
            for tag in ['ALBUM', 'album', 'Album']:
                if tag in audio:
                    album = audio[tag][0] if isinstance(audio[tag], list) else str(audio[tag])
                    break
            
            return artist, album
    except:
        return None, None

def _format_artist_album_info(self, artist, album, filepath=None):
    """Formate les informations d'artiste, d'album et de date pour l'affichage"""
    parts = []
    
    # Ajouter l'artiste s'il existe
    if artist:
        parts.append(artist)
    
    # Ajouter l'album s'il existe
    if album:
        parts.append(album)
    
    # Ajouter la date si le filepath est fourni
    if filepath and os.path.exists(filepath):
        date_str = None
        
        try:
            # Essayer d'abord d'obtenir la date de publication YouTube
            youtube_metadata = self.get_youtube_metadata(filepath)
            if youtube_metadata and youtube_metadata.get('upload_date'):
                upload_date = youtube_metadata['upload_date']
                # Convertir la date YouTube (format: YYYYMMDD) en format lisible
                import datetime
                date_obj = datetime.datetime.strptime(upload_date, "%Y%m%d")
                date_str = date_obj.strftime("%d/%m/%y")
        except Exception as e:
            print(f"Erreur conversion date YouTube: {e}")
        
        # # Si pas de date YouTube, utiliser la date de modification du fichier
        # if not date_str:
        #     try:
        #         import datetime
        #         mtime = os.path.getmtime(filepath)
        #         date_obj = datetime.datetime.fromtimestamp(mtime)
        #         date_str = date_obj.strftime("%d/%m/%y")
        #     except:
        #         pass  # Ignorer les erreurs de date
        
        # Ajouter la date si elle existe
        if date_str:
            parts.append(date_str)
    
    # Joindre les parties avec le séparateur •
    return " • ".join(parts) if parts else ""

def _add_to_specific_playlist(self, filepath, playlist_name):
    """Ajoute un fichier à une playlist spécifique"""
    if playlist_name == "Main Playlist":
        # Pour la main playlist, utiliser la nouvelle fonction centralisée
        self.add_to_main_playlist(filepath)
    else:
        # Pour les autres playlists
        if filepath not in self.playlists[playlist_name]:
            self.playlists[playlist_name].append(filepath)
            self.status_bar.config(text=f"Ajouté à '{playlist_name}': {os.path.basename(filepath)}")
            self.save_playlists()  # Sauvegarder
        else:
            self.status_bar.config(text=f"Déjà dans '{playlist_name}': {os.path.basename(filepath)}")

def _create_new_playlist_dialog(self, filepath=None, is_youtube_video=False):
    """Dialogue pour créer une nouvelle playlist"""
    dialog = tk.Toplevel(self.root)
    dialog.title("Nouvelle Playlist")
    dialog.geometry("300x150")
    dialog.configure(bg='#2d2d2d')
    dialog.resizable(False, False)
    
    # Centrer la fenêtre
    dialog.transient(self.root)
    dialog.grab_set()
    
    # Label
    label = tk.Label(dialog, text="Nom de la nouvelle playlist:", 
                    bg='#2d2d2d', fg='white', font=('TkDefaultFont', 10))
    label.pack(pady=20)
    
    # Entry
    entry = tk.Entry(dialog, bg='#3d3d3d', fg='white', insertbackground='white',
                    relief='flat', bd=5, font=('TkDefaultFont', 10))
    entry.pack(pady=10, padx=20, fill=tk.X)
    entry.focus()
    
    # Frame pour les boutons
    button_frame = tk.Frame(dialog, bg='#2d2d2d')
    button_frame.pack(pady=20)
    
    def create_playlist():
        name = entry.get().strip()
        if name and name not in self.playlists:
            self.playlists[name] = []
            if filepath:
                if is_youtube_video:
                    # Pour les vidéos YouTube, télécharger et ajouter à la playlist
                    self._download_and_add_to_playlists(filepath, [name])
                    self.status_bar.config(text=f"Playlist '{name}' créée, téléchargement en cours...")
                else:
                    # Pour les fichiers locaux, ajouter directement
                    self.playlists[name].append(filepath)
                    self.status_bar.config(text=f"Playlist '{name}' créée et fichier ajouté")
            else:
                self.status_bar.config(text=f"Playlist '{name}' créée")
            
            # Rafraîchir l'affichage des playlists si on est dans l'onglet playlists
            if hasattr(self, 'current_library_tab') and self.current_library_tab == "playlists":
                self._display_playlists()
            
            # Sauvegarder les playlists
            self.save_playlists()
            
            dialog.destroy()
        elif name in self.playlists:
            self.status_bar.config(text=f"Playlist '{name}' existe déjà")
        else:
            self.status_bar.config(text="Nom de playlist invalide")
    
    def cancel():
        dialog.destroy()
    
    # Boutons
    create_btn = tk.Button(button_frame, text="Créer", command=create_playlist,
                            bg="#4a8fe7", fg="white", activebackground="#5a9fd8",
                            relief="flat", bd=0, padx=20, pady=5, takefocus=0)
    create_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="Annuler", command=cancel,
                            bg="#666666", fg="white", activebackground="#777777",
                            relief="flat", bd=0, padx=20, pady=5, takefocus=0)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
    # Bind Enter key
    entry.bind('<Return>', lambda e: create_playlist())
    dialog.bind('<Escape>', lambda e: cancel())

def add_to_playlist(self):
    files = filedialog.askopenfilenames(
        filetypes=[("Fichiers Audio", "*.mp3 *.wav *.ogg *.flac"), ("Tous fichiers", "*.*")]
    )
    for file in files:
        self.add_to_main_playlist(file, show_status=False)
    
    # Marquer que la main playlist ne provient pas d'une playlist (ajout individuel)
    self.main_playlist_from_playlist = False
    
    self.status_bar.config(text=f"{len(files)} track added to main playlist")

def change_output_device(self, selected_device, device_name):
    """Change le périphérique de sortie audio"""
    try:
        # Arrêter la musique actuelle
        was_playing = pygame.mixer.music.get_busy() and not self.paused
        current_pos = self.current_time if was_playing else 0
        
        # Réinitialiser pygame mixer avec le nouveau périphérique
        pygame.mixer.quit()
        pygame.mixer.init(devicename=selected_device, frequency=44100, size=-16, channels=2, buffer=4096)
        
        # Reprendre la lecture si nécessaire
        if was_playing and self.main_playlist and self.current_index < len(self.main_playlist):
            current_song = self.main_playlist[self.current_index]
            pygame.mixer.music.load(current_song)
            pygame.mixer.music.play(start=current_pos)
            self._apply_volume()
        
        # Sauvegarder le nouveau périphérique
        self.current_audio_device = device_name
        
        # Mettre à jour la variable des radiobuttons si elle existe
        if hasattr(self, 'audio_device_var'):
            self.audio_device_var.set(device_name)
        
        self.save_config()
        
        self.status_bar.config(text=f"Périphérique changé: {device_name}")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de changer le périphérique:\n{str(e)}")

def _detect_current_audio_device(self):
    """Détecte le périphérique audio actuellement utilisé"""
    try:
        import pygame._sdl2.audio
        devices = pygame._sdl2.audio.get_audio_device_names()
        
        if devices:
            # Par défaut, prendre le premier périphérique (souvent le défaut du système)
            default_device = devices[0]
            self.current_audio_device = default_device.decode('utf-8') if isinstance(default_device, bytes) else default_device
            
    except Exception as e:
        print(f"Erreur détection périphérique audio: {e}")
        self.current_audio_device = "Périphérique par défaut"

def _truncate_text_to_width(self, text, font, max_width):
    """Tronque le texte pour qu'il tienne dans la largeur spécifiée"""
    import tkinter.font as tkFont
    
    # Créer un objet font pour mesurer le texte
    if isinstance(font, str):
        font_obj = tkFont.Font(family=font)
    elif isinstance(font, tuple):
        font_obj = tkFont.Font(family=font[0], size=font[1] if len(font) > 1 else 10)
    else:
        font_obj = tkFont.Font()
    
    # Si le texte tient déjà, le retourner tel quel
    if font_obj.measure(text) <= max_width:
        return text
    
    # Sinon, tronquer progressivement
    ellipsis = "..."
    ellipsis_width = font_obj.measure(ellipsis)
    available_width = max_width - ellipsis_width
    
    if available_width <= 0:
        return ellipsis
    
    # Recherche dichotomique pour trouver la longueur optimale
    left, right = 0, len(text)
    result = text
    
    while left <= right:
        mid = (left + right) // 2
        test_text = text[:mid]
        
        if font_obj.measure(test_text) <= available_width:
            result = test_text + ellipsis
            left = mid + 1
        else:
            right = mid - 1
    
    return result

def toggle_item_selection(self, filepath, frame):
    """Ajoute ou retire un élément de la sélection multiple"""
    if filepath in self.selected_items:
        # Désélectionner
        self.selected_items.remove(filepath)
        if filepath in self.selected_items_order:
            self.selected_items_order.remove(filepath)
        if filepath in self.selection_frames:
            del self.selection_frames[filepath]
        
        # Vérifier que l'index est valide avant d'accéder à la playlist
        if (self.main_playlist and 
            0 <= self.current_index < len(self.main_playlist) and 
            filepath == self.main_playlist[self.current_index]):
            self._set_item_colors(frame, COLOR_SELECTED)
        else:
            self._set_item_colors(frame, '#4a4a4a')  # Couleur normale
    else:
        # Sélectionner
        self.selected_items.add(filepath)
        self.selected_items_order.append(filepath)  # Maintenir l'ordre de sélection
        self.selection_frames[filepath] = frame
        self._set_item_colors(frame, '#ff8c00')  # Couleur orange pour la sélection multiple
    
    # Mettre à jour l'affichage du nombre d'éléments sélectionnés
    self.update_selection_display()
    # print(self.selected_items_order)  # Afficher la liste ordonnée au lieu du set

def clear_selection(self):
    """Efface toute la sélection multiple"""
    try:
        # Vérifier que l'interface est encore valide
        if not (hasattr(self, 'root') and self.root.winfo_exists()):
            return
            
        for filepath in list(self.selected_items):
            if filepath in self.selection_frames:
                frame = self.selection_frames[filepath]
                try:
                    # Vérifier que le frame existe encore
                    if frame.winfo_exists():
                        # Vérifier que l'index est valide avant d'accéder à la playlist
                        if (self.main_playlist and 
                            0 <= self.current_index < len(self.main_playlist) and 
                            filepath == self.main_playlist[self.current_index]):
                            self._set_item_colors(frame, COLOR_SELECTED)
                        else:
                            self._set_item_colors(frame, '#4a4a4a')  # Couleur normale
                except tk.TclError:
                    # Frame détruit, ignorer
                    pass
        
        self.selected_items.clear()
        self.selected_items_order.clear()  # Vider aussi la liste ordonnée
        self.selection_frames.clear()
        self.shift_selection_active = False
        
        # Mettre à jour l'affichage du nombre d'éléments sélectionnés
        self.update_selection_display()
        
    except Exception as e:
        # En cas d'erreur, au moins nettoyer les structures de données
        self.selected_items.clear()
        self.selected_items_order.clear()
        self.selection_frames.clear()
        self.shift_selection_active = False

def _show_single_file_menu(self, event, filepath):
    """Affiche un menu contextuel pour un seul fichier"""
    # Vérifier si c'est une vidéo YouTube non téléchargée
    is_youtube_video = filepath.startswith("https://www.youtube.com/watch?v=")
    
    # Créer le menu contextuel
    context_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                            activebackground='#4a8fe7', activeforeground='white',
                            relief='flat', bd=1)
    
    # Ajouter un titre
    filename = os.path.basename(filepath) if not is_youtube_video else "Vidéo YouTube"
    title_text = f"Télécharger et ajouter à:" if is_youtube_video else f"Ajouter à:"
    context_menu.add_command(label=title_text, state='disabled')
    context_menu.add_separator()
    
    # Options pour la queue et la main playlist (seulement pour les fichiers locaux)
    if not is_youtube_video:
        context_menu.add_command(
            label="📄 Ajouter à la liste de lecture",
            command=lambda f=filepath: self._safe_add_to_main_playlist(f)
        )
        context_menu.add_command(
            label="⏭️ Lire ensuite",
            command=lambda f=filepath: self._safe_add_to_queue_first(f)
        )
        context_menu.add_command(
            label="⏰ Lire bientôt", 
            command=lambda f=filepath: self._safe_add_to_queue(f)
        )
        context_menu.add_separator()
    
    # Ajouter les playlists existantes (sauf Main Playlist)
    for playlist_name in self.playlists.keys():
        if playlist_name != "Main Playlist":
            if is_youtube_video:
                context_menu.add_command(
                    label=playlist_name,
                    command=lambda p=playlist_name: self._download_and_add_to_playlists(filepath, [p])
                )
            else:
                context_menu.add_command(
                    label=playlist_name,
                    command=lambda p=playlist_name, f=filepath: self._safe_add_to_specific_playlist(f, p)
                )
    
    # Ajouter une option pour créer une nouvelle playlist
    context_menu.add_separator()
    context_menu.add_command(
        label="Créer nouvelle playlist...",
        command=lambda f=filepath, yt=is_youtube_video: self._safe_create_new_playlist_dialog(f, yt)
    )
    
    # Afficher le menu à la position de la souris
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

def _safe_add_to_main_playlist(self, filepath):
    """Version sécurisée de add_to_main_playlist"""
    try:
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.add_to_main_playlist(filepath)
            if hasattr(self, '_refresh_playlist_display'):
                self._refresh_playlist_display()
    except tk.TclError:
        pass  # Widget détruit, ignorer silencieusement

def _safe_add_to_queue_first(self, filepath):
    """Version sécurisée de _add_to_queue_first"""
    try:
        if hasattr(self, 'root') and self.root.winfo_exists() and hasattr(self, 'drag_drop_handler'):
            self.drag_drop_handler._add_to_queue_first(filepath)
    except tk.TclError:
        pass  # Widget détruit, ignorer silencieusement

def _safe_add_to_queue(self, filepath):
    """Version sécurisée de _add_to_queue"""
    try:
        if hasattr(self, 'root') and self.root.winfo_exists() and hasattr(self, 'drag_drop_handler'):
            self.drag_drop_handler._add_to_queue(filepath)
    except tk.TclError:
        pass  # Widget détruit, ignorer silencieusement

def _safe_add_to_specific_playlist(self, filepath, playlist_name):
    """Version sécurisée de _add_to_specific_playlist"""
    try:
        if hasattr(self, 'root') and self.root.winfo_exists():
            self._add_to_specific_playlist(filepath, playlist_name)
    except tk.TclError:
        pass  # Widget détruit, ignorer silencieusement

def _safe_create_new_playlist_dialog(self, filepath, is_youtube_video):
    """Version sécurisée de _create_new_playlist_dialog"""
    try:
        if hasattr(self, 'root') and self.root.winfo_exists():
            self._create_new_playlist_dialog(filepath, is_youtube_video)
    except tk.TclError:
        pass  # Widget détruit, ignorer silencieusement

def show_selection_menu(self, event):
    """Affiche un menu contextuel pour sélectionner les playlists"""
    print(f"DEBUG: show_selection_menu appelé avec {len(self.selected_items) if self.selected_items else 0} éléments sélectionnés")
    
    if not self.selected_items:
        print("DEBUG: Aucun élément sélectionné, retour")
        return
    
    # Vérifier que l'interface est prête avant d'afficher le menu
    try:
        if not (hasattr(self, 'root') and self.root.winfo_exists()):
            print("DEBUG: Root n'existe pas")
            return
        # Vérifier qu'au moins un des containers existe (downloads, playlist content, ou playlists)
        has_downloads_container = hasattr(self, 'downloads_container') and self.downloads_container.winfo_exists()
        has_playlist_content_container = hasattr(self, 'playlist_content_container') and self.playlist_content_container.winfo_exists()
        has_playlists_container = hasattr(self, 'playlists_container') and self.playlists_container.winfo_exists()
        has_playlist_container = hasattr(self, 'playlist_container') and self.playlist_container.winfo_exists()
        
        if not (has_downloads_container or has_playlist_content_container or has_playlists_container or has_playlist_container):
            print("DEBUG: Aucun container valide trouvé")
            print(f"DEBUG: downloads_container: {hasattr(self, 'downloads_container')}")
            print(f"DEBUG: playlist_content_container: {hasattr(self, 'playlist_content_container')}")
            print(f"DEBUG: playlists_container: {hasattr(self, 'playlists_container')}")
            print(f"DEBUG: playlist_container: {hasattr(self, 'playlist_container')}")
            return
        # Vérifier si on vient juste de changer d'onglet (laisser le temps de se stabiliser)
        if hasattr(self, '_library_tab_ready') and not self._library_tab_ready:
            print("DEBUG: Onglet pas prêt, différer")
            # Différer l'affichage du menu si l'onglet n'est pas encore prêt
            self.safe_after(100, lambda: self.show_selection_menu(event))
            return
    except tk.TclError as e:
        print(f"DEBUG: TclError dans show_selection_menu: {e}")
        return  # Interface pas prête, ignorer
    
    # Vérifier si on a des vidéos YouTube non téléchargées dans la sélection
    has_youtube_videos = any(item.startswith("https://www.youtube.com/watch?v=") for item in self.selected_items)
    
    # Créer le menu contextuel
    context_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                            activebackground='#4a8fe7', activeforeground='white',
                            relief='flat', bd=1)
    
    # Ajouter un titre avec le nombre d'éléments sélectionnés
    title_text = f"Télécharger et ajouter {len(self.selected_items)} élément(s) à:" if has_youtube_videos else f"Ajouter {len(self.selected_items)} élément(s) à:"
    context_menu.add_command(label=title_text, state='disabled')
    context_menu.add_separator()
    
    # Nouvelles options pour la queue et la main playlist
    if not has_youtube_videos:  # Ces options ne fonctionnent que pour les fichiers locaux
        context_menu.add_command(
            label="📄 Ajouter à la liste de lecture",
            command=self.add_selection_to_main_playlist
        )
        context_menu.add_command(
            label="⏭️ Lire ensuite",
            command=self.add_selection_to_queue_first
        )
        context_menu.add_command(
            label="⏰ Lire bientôt", 
            command=self.add_selection_to_queue_last
        )
        context_menu.add_separator()
    
    # Ajouter les playlists existantes (sauf Main Playlist)
    for playlist_name in self.playlists.keys():
        if playlist_name != "Main Playlist":
            if has_youtube_videos:
                context_menu.add_command(
                    label=playlist_name,
                    command=lambda p=playlist_name: self.download_and_add_to_multiple_playlists([p])
                )
            else:
                context_menu.add_command(
                    label=playlist_name,
                    command=lambda p=playlist_name: self.add_to_multiple_playlists([p])
                )
    
    # Ajouter une option pour créer une nouvelle playlist
    context_menu.add_separator()
    context_menu.add_command(
        label="Créer nouvelle playlist...",
        command=lambda: self.create_new_playlist_from_selection(has_youtube_videos)
    )
    
    # Ajouter une option pour annuler la sélection
    context_menu.add_separator()
    context_menu.add_command(
        label="Annuler la sélection",
        command=self.clear_selection
    )
    
    # Afficher le menu à la position de la souris
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

def add_selection_to_main_playlist(self):
    """Ajoute tous les éléments sélectionnés à la fin de la main playlist dans l'ordre"""
    print("DEBUG: add_selection_to_main_playlist appelé")
    
    # Marquer qu'on est en train de faire une opération de sélection multiple
    self._selection_operation_in_progress = True
    
    if not self.selected_items:
        print("DEBUG: Aucun élément sélectionné dans add_selection_to_main_playlist")
        return
    
    # Vérifier que l'interface est stable avant de procéder
    try:
        if not (hasattr(self, 'root') and self.root.winfo_exists()):
            print("DEBUG: Root n'existe pas dans add_selection_to_main_playlist")
            return
        if not (hasattr(self, 'downloads_container') and self.downloads_container.winfo_exists()):
            print("DEBUG: downloads_container n'existe pas dans add_selection_to_main_playlist")
            return
    except tk.TclError as e:
        print(f"DEBUG: TclError dans add_selection_to_main_playlist: {e}")
        return  # Interface pas prête, ignorer
        
    added_count = 0
    
    for filepath in self.selected_items_order:
        # Vérifier que c'est bien un fichier local (pas une URL YouTube)
        if not filepath.startswith("https://"):
            # Ajouter directement à la playlist sans déclencher les mises à jour visuelles
            if filepath not in self.main_playlist:
                self.main_playlist.append(filepath)
                self._add_main_playlist_item(filepath)
                added_count += 1
    
    # Rafraîchir l'affichage seulement de la playlist, pas des téléchargements
    self._refresh_playlist_display()
    
    # Mettre à jour les indicateurs visuels de queue SEULEMENT si on est dans l'onglet téléchargements
    if (hasattr(self, 'current_library_tab') and 
        self.current_library_tab == "téléchargées" and 
        hasattr(self, 'downloads_container')):
        try:
            self._update_downloads_queue_visual()
        except Exception as e:
            print(f"DEBUG: Erreur lors de la mise à jour visuelle: {e}")
    
    # Afficher le statut
    if added_count > 0:
        self.status_bar.config(text=f"Ajouté {added_count} élément(s) à la liste de lecture")
    else:
        self.status_bar.config(text="Aucun élément n'a été ajouté (déjà présents)")
        
    # Effacer la sélection (différé pour éviter les conflits d'interface)
    self.safe_after(100, self.clear_selection)
    
    # Marquer que la main playlist ne provient pas d'une playlist
    self.main_playlist_from_playlist = False
    
    # Marquer que l'opération de sélection multiple est terminée
    self._selection_operation_in_progress = False
    print("DEBUG: add_selection_to_main_playlist terminé")

def create_new_playlist_from_selection(self, has_youtube_videos):
    """Demande le nom d'une nouvelle playlist et y ajoute la sélection"""
    from tkinter import simpledialog
    
    playlist_name = simpledialog.askstring(
        "Nouvelle playlist",
        "Nom de la nouvelle playlist:",
        parent=self.root
    )
    
    if playlist_name and playlist_name.strip():
        playlist_name = playlist_name.strip()
        if has_youtube_videos:
            self.download_and_add_to_multiple_playlists([playlist_name])
        else:
            self.add_to_multiple_playlists([playlist_name])

def update_selection_display(self):
    """Met à jour l'affichage du nombre d'éléments sélectionnés"""
    if hasattr(self, 'selection_label'):
        if self.selected_items:
            count = len(self.selected_items)
            text = f"{count} élément{'s' if count > 1 else ''} sélectionné{'s' if count > 1 else ''}"
            self.selection_label.config(text=text)
        else:
            self.selection_label.config(text="")