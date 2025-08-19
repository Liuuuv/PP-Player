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
        
        config = {
            "global_volume": self.volume,
            "volume_offsets": self.volume_offsets
        }
        
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Erreur sauvegarde config: {e}")

def _remove_from_playlist_view(self, filepath, playlist_name, event=None):
    """Supprime une musique de la playlist et rafraîchit l'affichage"""
    # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
    if event and (event.state & 0x4):  # Ctrl est enfoncé
        # Pour la suppression définitive, on utilise une approche différente
        # car on n'a pas de frame à passer
        try:
            if os.path.exists(filepath):
                # Supprimer le fichier audio
                os.remove(filepath)
                
                # Supprimer la miniature associée si elle existe
                thumbnail_path = os.path.splitext(filepath)[0] + ".jpg"
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                # Supprimer de la playlist
                if filepath in self.main_playlist:
                    self.main_playlist.remove(filepath)
                
                # Supprimer de toutes les playlists
                for pname, playlist_songs in self.playlists.items():
                    if filepath in playlist_songs:
                        playlist_songs.remove(filepath)
                
                # Sauvegarder les playlists
                self.save_playlists()
                
                # Mettre à jour le compteur
                file_services._count_downloaded_files(self)
                self._update_downloads_button()
                
                self.status_bar.config(text=f"Fichier supprimé définitivement: {os.path.basename(filepath)}")
                
                # Rafraîchir l'affichage
                self._display_playlist_songs(playlist_name)
                self._update_playlist_title(playlist_name)
                
                # Rafraîchir la bibliothèque si nécessaire
                self._refresh_downloads_library()
                
        except Exception as e:
            self.status_bar.config(text=f"Erreur suppression fichier: {str(e)}")
            print(f"Erreur suppression fichier: {e}")
    else:
        # Suppression normale de la playlist
        if playlist_name in self.playlists and filepath in self.playlists[playlist_name]:
            self.playlists[playlist_name].remove(filepath)
            self.save_playlists()
            # Rafraîchir l'affichage
            self._display_playlist_songs(playlist_name)
            # Mettre à jour le titre avec le nouveau nombre de chansons
            self._update_playlist_title(playlist_name)
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
        final_volume = max(0, min(1, final_volume))
    
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
        circular_img = self._create_circular_image(img, (70, 70))
        photo = ImageTk.PhotoImage(circular_img)
        
        self.root.after(0, lambda: self._display_thumbnail(label, photo))
    except Exception as e:
        print(f"Erreur chargement thumbnail circulaire: {e}")

def _display_thumbnail(self, label, photo):
    """Affiche la miniature dans le label"""
    label.configure(image=photo)
    label.image = photo  # Garder une référence


def _add_playlist_song_item(self, filepath, playlist_name, song_index):
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
            self.playlist_content_container,
            bg=bg_color,
            relief='flat',
            bd=1,
            highlightbackground='#5a5a5a',
            # highlightbackground=TEST_COLOR,
            highlightthickness=1
        )
        item_frame.pack(fill="x", padx=DISPLAY_PLAYLIST_PADX, pady=DISPLAY_PLAYLIST_PADY)
        
        # Stocker les informations pour pouvoir les retrouver plus tard
        item_frame.filepath = filepath
        item_frame.playlist_name = playlist_name
        item_frame.song_index = song_index
        item_frame.selected = is_current_song
        
        # Configuration de la grille en 5 colonnes : numéro, miniature, texte, durée, bouton
        item_frame.columnconfigure(0, minsize=40, weight=0)  # Numéro
        item_frame.columnconfigure(1, minsize=80, weight=0)  # Miniature
        item_frame.columnconfigure(2, weight=1)              # Texte
        item_frame.columnconfigure(3, minsize=60, weight=0)  # Durée
        item_frame.columnconfigure(4, minsize=80, weight=0)  # Bouton
        item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
        
        # 1. Numéro de la chanson (colonne 0)
        number_label = tk.Label(
            item_frame,
            text=str(song_index + 1),  # +1 pour commencer à 1 au lieu de 0
            bg=bg_color,
            fg='white',
            font=('TkDefaultFont', 10, 'bold'),
            anchor='center'
        )
        number_label.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=2)
        
        # 2. Miniature (colonne 1)
        thumbnail_label = tk.Label(
            item_frame,
            bg=bg_color,
            width=10,
            height=3,
            anchor='center'
        )
        thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=2)
        thumbnail_label.grid_propagate(False)
        
        # Charger la miniature
        self._load_download_thumbnail(filepath, thumbnail_label)
        
        # 3. Texte (colonne 2)
        truncated_title = self._truncate_text_for_display(filename)
        title_label = tk.Label(
            item_frame,
            text=truncated_title,
            bg=bg_color,
            fg='white',
            font=('TkDefaultFont', 9),
            anchor='w',
            justify='left',
            wraplength=170
        )
        title_label.grid(row=0, column=2, sticky='nsew', padx=(0, 10), pady=8)
        
        # 4. Durée (colonne 3)
        duration_label = tk.Label(
            item_frame,
            text=self._get_audio_duration(filepath),
            bg=bg_color,
            fg='#cccccc',
            font=('TkDefaultFont', 8),
            anchor='center'
        )
        duration_label.grid(row=0, column=3, sticky='ns', padx=(0, 10), pady=8)
        
        # 5. Bouton "Supprimer de la playlist" (colonne 4) avec icône delete
        remove_btn = tk.Button(
            item_frame,
            image=self.icons["delete"],  # Utiliser l'icône delete non rognée
            bg="#3d3d3d",
            activebackground='#ff6666',
            relief='flat',
            bd=0,
            padx=5,
            pady=5
        )
        remove_btn.bind("<Double-1>", lambda event: self._remove_from_playlist_view(filepath, playlist_name, event))
        remove_btn.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
        create_tooltip(remove_btn, "Supprimer de la playlist\nDouble-clic: Retirer de cette playlist\nCtrl + Double-clic: Supprimer définitivement du disque")
        
        # Gestion des clics pour la sélection multiple
        def on_playlist_content_click(event):
            # Vérifier si Shift est enfoncé pour la sélection multiple
            if event.state & 0x1:  # Shift est enfoncé
                self.shift_selection_active = True
                self.toggle_item_selection(filepath, item_frame)
            else:
                # Clic normal sans Shift - ne pas effacer la sélection si elle existe
                pass
        
        def on_playlist_content_double_click(event):
            # Vérifier si Shift est enfoncé ou si on est en mode sélection - ne rien faire
            if event.state & 0x1 or self.selected_items:  # Shift est enfoncé ou mode sélection
                pass
            else:
                # Comportement normal : lancer la playlist depuis cette musique
                self._play_playlist_from_song(playlist_name, song_index)
        
        def on_playlist_content_right_click(event):
            # Si on a des éléments sélectionnés, ouvrir le menu de sélection
            if self.selected_items:
                self.show_selection_menu(event)
            else:
                # Comportement normal : ajouter à la main playlist
                if filepath not in self.main_playlist:
                    self.main_playlist.append(filepath)
                    self._add_main_playlist_item(filepath)
                    self._refresh_playlist_display()
        
        # Bindings pour tous les éléments cliquables
        widgets_to_bind = [item_frame, number_label, thumbnail_label, title_label, duration_label]
        for widget in widgets_to_bind:
            widget.bind("<Button-1>", on_playlist_content_click)
            widget.bind("<Double-1>", on_playlist_content_double_click)
            widget.bind("<Button-3>", on_playlist_content_right_click)
        
    except Exception as e:
        print(f"Erreur affichage musique playlist: {e}")

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