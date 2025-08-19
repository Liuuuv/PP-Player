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
            # Remettre l'apparence normale
            video['search_frame'].config(bg='#4a4a4a')
            video['search_frame'].title_label.config(bg='#4a4a4a', fg='white')
            video['search_frame'].duration_label.config(bg='#4a4a4a', fg='#cccccc')
            video['search_frame'].thumbnail_label.config(bg='#4a4a4a')
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
            # Remettre l'apparence normale
            video['search_frame'].config(bg='#4a4a4a')
            video['search_frame'].title_label.config(bg='#4a4a4a', fg='white')
            video['search_frame'].duration_label.config(bg='#4a4a4a', fg='#cccccc')
            video['search_frame'].thumbnail_label.config(bg='#4a4a4a')
    
    except Exception as e:
        self.root.after(0, lambda e=e: self.status_bar.config(text=f"Erreur: {str(e)}"))
        if 'search_frame' in video:
            # Apparence d'erreur (jaune)
            video['search_frame'].config(bg='#ffcc00')
            video['search_frame'].title_label.config(bg='#ffcc00', fg='#333333')
            video['search_frame'].duration_label.config(bg='#ffcc00', fg='#666666')
            video['search_frame'].thumbnail_label.config(bg='#ffcc00')
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
            print(f"Debug: Compteur mis à jour: {counter_text}")  # Debug
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

def select_playlist_content_item(self, current_filepath):
    """Met en surbrillance l'élément sélectionné dans l'affichage du contenu d'une playlist"""
    # Vérifier si on est en train de visualiser une playlist et si le container existe
    if (hasattr(self, 'playlist_content_container') and 
        self.playlist_content_container.winfo_exists() and
        hasattr(self, 'current_viewing_playlist')):
        
        # Désélectionner tous les autres éléments et sélectionner le bon
        for child in self.playlist_content_container.winfo_children():
            if hasattr(child, 'filepath'):
                if child.filepath == current_filepath:
                    # Sélectionner cet élément
                    child.selected = True
                    self._set_item_colors(child, '#5a9fd8')  # Couleur de surbrillance (bleu)
                else:
                    # Désélectionner les autres
                    child.selected = False
                    self._set_item_colors(child, '#4a4a4a')  # Couleur normale
