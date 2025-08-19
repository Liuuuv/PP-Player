import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier library_tab
from library_tab import *

def show_playlists_content(self):
    """Affiche le contenu de l'onglet playlists"""
    
    # Frame pour les boutons de gestion
    management_frame = ttk.Frame(self.library_content_frame)
    management_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
    
    # Bouton créer nouvelle playlist
    create_btn = tk.Button(
        management_frame,
        # text="➕",
        image=self.icons["add"],
        command=lambda: self._create_new_playlist_dialog(),
        bg='#4d4d4d',
        fg="white",
        activebackground="#5a9fd8",
        relief="flat",
        bd=0,
        padx=15,
        pady=8,
        font=('TkDefaultFont', 14)
    )
    create_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Canvas avec scrollbar pour les playlists
    self.playlists_canvas = tk.Canvas(
        self.library_content_frame,
        bg='#3d3d3d',
        highlightthickness=0
    )
    self.playlists_scrollbar = ttk.Scrollbar(
        self.library_content_frame,
        orient="vertical",
        command=self.playlists_canvas.yview
    )
    self.playlists_canvas.configure(yscrollcommand=self.playlists_scrollbar.set)
    
    self.playlists_scrollbar.pack(side="right", fill="y")
    self.playlists_canvas.pack(side="left", fill="both", expand=True)
    
    self.playlists_container = ttk.Frame(self.playlists_canvas)
    self.playlists_canvas.create_window((0, 0), window=self.playlists_container, anchor="nw")
    
    self.playlists_container.bind(
        "<Configure>",
        lambda e: self.playlists_canvas.configure(
            scrollregion=self.playlists_canvas.bbox("all")
        )
    )
    
    self._bind_mousewheel(self.playlists_canvas, self.playlists_canvas)
    self._bind_mousewheel(self.playlists_container, self.playlists_canvas)
    
    # Charger et afficher les playlists
    self._display_playlists()

def _display_playlists(self):
    """Affiche toutes les playlists en grille 3x3"""
    # Vider le container actuel
    for widget in self.playlists_container.winfo_children():
        widget.destroy()
    
    # Organiser les playlists en lignes de 3 (exclure la main playlist)
    playlist_items = [(name, songs) for name, songs in self.playlists.items() if name != "Main Playlist"]
    
    for row in range(0, len(playlist_items), 2):
        # Créer un frame pour cette ligne
        row_frame = tk.Frame(self.playlists_container, bg='#3d3d3d')
        row_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Configurer les colonnes pour qu'elles soient égales
        for col in range(2):
            row_frame.columnconfigure(col, weight=1, uniform="playlist_col")
        
        # Ajouter jusqu'à 2 playlists dans cette ligne
        for col in range(2):
            playlist_index = row + col
            if playlist_index < len(playlist_items):
                playlist_name, songs = playlist_items[playlist_index]
                self._add_playlist_card(row_frame, playlist_name, songs, col)


def _add_playlist_card(self, parent_frame, playlist_name, songs, column):
    """Ajoute une carte de playlist avec miniatures"""
    try:
        # Frame principal pour la carte de playlist
        card_frame = tk.Frame(
            parent_frame,
            bg='#4a4a4a',
            relief='flat',
            bd=1,
            highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
            highlightthickness=1
        )
        card_frame.grid(row=0, column=column, sticky='nsew', padx=CARD_FRAME_PADX, pady=CARD_FRAME_PADY)
        
        
        # Configuration de la grille de la carte
        card_frame.columnconfigure(0, weight=1)
        card_frame.rowconfigure(0, weight=1)  # Zone des miniatures
        card_frame.rowconfigure(1, weight=0)  # Titre
        card_frame.rowconfigure(2, weight=0)  # Nombre de chansons
        card_frame.rowconfigure(3, weight=0)  # Boutons
        
        # 1. Zone des miniatures (2x2 grid) - taille fixe pour uniformité
        thumbnails_frame = tk.Frame(card_frame, bg='#4a4a4a', width=220, height=220)
        thumbnails_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        thumbnails_frame.grid_propagate(False)  # Maintenir la taille fixe
        
        # Configurer la grille 2x2 pour les miniatures
        for i in range(2):
            thumbnails_frame.columnconfigure(i, weight=1)
            thumbnails_frame.rowconfigure(i, weight=1)
        
        # Ajouter les 4 premières miniatures (ou moins si pas assez de chansons)
        for i in range(4):
            row = i // 2
            col = i % 2
            
            thumbnail_label = tk.Label(
                thumbnails_frame,
                bg='#3d3d3d',
                relief='flat'
            )
            thumbnail_label.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
            
            # Charger la miniature si la chanson existe
            if i < len(songs):
                self._load_playlist_thumbnail_large(songs[i], thumbnail_label)
            else:
                # Miniature vide
                thumbnail_label.config(text="♪", fg='#666666', font=('TkDefaultFont', 20))
        
        # 2. Titre de la playlist
        title_label = tk.Label(
            card_frame,
            text=playlist_name,
            bg='#4a4a4a',
            fg='white',
            font=('TkDefaultFont', 11, 'bold'),
            anchor='center'
        )
        title_label.grid(row=1, column=0, sticky='ew', padx=10, pady=(5, 2))
        
        # 3. Nombre de chansons
        count_label = tk.Label(
            card_frame,
            text=f"{len(songs)} titres",
            bg='#4a4a4a',
            fg='#cccccc',
            font=('TkDefaultFont', 9),
            anchor='center'
        )
        count_label.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 5))
        
        # 4. Boutons
        buttons_frame = tk.Frame(card_frame, bg='#4a4a4a')
        buttons_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=(0, 5))
        
        # Bouton renommer - icône complète
        rename_btn = tk.Button(
            buttons_frame,
            image=self.icons["rename"],
            command=lambda name=playlist_name: self._rename_playlist_dialog(name),
            bg="#ffa500",
            fg="white",
            activebackground="#ffb733",
            relief="flat",
            bd=0,
            width=self.icons["rename"].width(),
            height=self.icons["rename"].height(),
        )
        rename_btn.pack(side=tk.LEFT, padx=2)
        
        # Bouton supprimer - icône complète
        delete_btn = tk.Button(
            buttons_frame,
            image=self.icons["delete"],
            bg="#ff4444",
            fg="white",
            activebackground="#ff6666",
            relief="flat",
            bd=0,
            width=self.icons["delete"].width(),
            height=self.icons["delete"].height(),
        )
        delete_btn.pack(side=tk.RIGHT, padx=2)
        
        # Double-clic pour supprimer
        delete_btn.bind("<Double-1>", lambda e, name=playlist_name: self._delete_playlist_dialog(name))
        
        # Double-clic pour voir le contenu de la playlist
        def on_playlist_double_click():
            self._show_playlist_content_in_tab(playlist_name)
        
        card_frame.bind("<Double-1>", lambda e: on_playlist_double_click())
        thumbnails_frame.bind("<Double-1>", lambda e: on_playlist_double_click())
        title_label.bind("<Double-1>", lambda e: on_playlist_double_click())
        count_label.bind("<Double-1>", lambda e: on_playlist_double_click())
        
    except Exception as e:
        print(f"Erreur affichage playlist card: {e}")

def _load_playlist_thumbnail_large(self, filepath, label):
    """Charge une miniature carrée plus grande pour une chanson dans une playlist"""
    try:
        # Chercher une image associée (même nom mais extension image)
        base_name = os.path.splitext(filepath)[0]
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        thumbnail_found = False
        for ext in image_extensions:
            thumbnail_path = base_name + ext
            if os.path.exists(thumbnail_path):
                # Charger l'image
                image = Image.open(thumbnail_path)
                
                # Créer une image carrée en cropant au centre
                width, height = image.size
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                right = left + size
                bottom = top + size
                
                # Crop au centre pour faire un carré
                img_cropped = image.crop((left, top, right, bottom))
                
                # Redimensionner à une taille plus grande (100x100)
                img_resized = img_cropped.resize((100, 100), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img_resized)
                label.configure(image=photo, text="")
                label.image = photo
                thumbnail_found = True
                break
        
        if not thumbnail_found:
            # Utiliser une icône par défaut plus grande
            label.config(text="♪", fg='#666666', font=('TkDefaultFont', 20))
            
    except Exception as e:
        print(f"Erreur chargement thumbnail playlist: {e}")
        label.config(text="♪", fg='#666666', font=('TkDefaultFont', 20))

def _load_playlist_thumbnail(self, filepath, label):
    """Charge une miniature pour une chanson dans une playlist"""
    try:
        # Chercher une image associée (même nom mais extension image)
        base_name = os.path.splitext(filepath)[0]
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        thumbnail_found = False
        for ext in image_extensions:
            thumbnail_path = base_name + ext
            if os.path.exists(thumbnail_path):
                # Charger et redimensionner l'image
                image = Image.open(thumbnail_path)
                image = image.resize((75, 56), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                label.configure(image=photo, text="")
                label.image = photo
                thumbnail_found = True
                break
        
        if not thumbnail_found:
            # Utiliser une icône par défaut
            label.config(text="♪", fg='#666666', font=('TkDefaultFont', 12))
            
    except Exception as e:
        print(f"Erreur chargement thumbnail playlist: {e}")
        label.config(text="♪", fg='#666666', font=('TkDefaultFont', 12))

def save_playlists(self):
    """Sauvegarde les playlists dans un fichier JSON"""
    try:
        import json
        playlists_file = os.path.join("downloads", "playlists.json")
        
        # Créer le dossier downloads s'il n'existe pas
        os.makedirs("downloads", exist_ok=True)
        
        # Sauvegarder toutes les playlists sauf la main playlist
        playlists_to_save = {name: songs for name, songs in self.playlists.items() if name != "Main Playlist"}
        
        with open(playlists_file, 'w', encoding='utf-8') as f:
            json.dump(playlists_to_save, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Erreur sauvegarde playlists: {e}")

def _rename_playlist_dialog(self, old_name):
    """Dialogue pour renommer une playlist"""
    dialog = tk.Toplevel(self.root)
    dialog.title("Renommer Playlist")
    dialog.geometry("300x150")
    dialog.configure(bg='#2d2d2d')
    dialog.resizable(False, False)
    
    # Centrer la fenêtre
    dialog.transient(self.root)
    dialog.grab_set()
    
    # Label
    label = tk.Label(dialog, text=f"Nouveau nom pour '{old_name}':", 
                    bg='#2d2d2d', fg='white', font=('TkDefaultFont', 10))
    label.pack(pady=20)
    
    # Entry avec le nom actuel
    entry = tk.Entry(dialog, bg='#3d3d3d', fg='white', insertbackground='white',
                    relief='flat', bd=5, font=('TkDefaultFont', 10))
    entry.pack(pady=10, padx=20, fill=tk.X)
    entry.insert(0, old_name)
    entry.select_range(0, tk.END)
    entry.focus()
    
    # Frame pour les boutons
    button_frame = tk.Frame(dialog, bg='#2d2d2d')
    button_frame.pack(pady=20)
    
    def rename_playlist():
        new_name = entry.get().strip()
        if new_name and new_name != old_name and new_name not in self.playlists:
            # Renommer la playlist
            self.playlists[new_name] = self.playlists.pop(old_name)
            self.status_bar.config(text=f"Playlist renommée: '{old_name}' → '{new_name}'")
            self._display_playlists()  # Rafraîchir l'affichage
            self.save_playlists()  # Sauvegarder
            dialog.destroy()
        elif new_name in self.playlists:
            self.status_bar.config(text=f"Playlist '{new_name}' existe déjà")
        elif new_name == old_name:
            dialog.destroy()  # Pas de changement
        else:
            self.status_bar.config(text="Nom de playlist invalide")
    
    def cancel():
        dialog.destroy()
    
    # Boutons
    rename_btn = tk.Button(button_frame, text="Renommer", command=rename_playlist,
                            bg="#ffa500", fg="white", activebackground="#ffb733",
                            relief="flat", bd=0, padx=20, pady=5)
    rename_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="Annuler", command=cancel,
                            bg="#666666", fg="white", activebackground="#777777",
                            relief="flat", bd=0, padx=20, pady=5)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
    # Bind Enter key
    entry.bind('<Return>', lambda e: rename_playlist())
    dialog.bind('<Escape>', lambda e: cancel())

def _delete_playlist_dialog(self, playlist_name):
    """Dialogue pour confirmer la suppression d'une playlist"""
    dialog = tk.Toplevel(self.root)
    dialog.title("Supprimer Playlist")
    dialog.geometry("350x150")
    dialog.configure(bg='#2d2d2d')
    dialog.resizable(False, False)
    
    # Centrer la fenêtre
    dialog.transient(self.root)
    dialog.grab_set()
    
    # Label de confirmation
    label = tk.Label(dialog, text=f"Êtes-vous sûr de vouloir supprimer\nla playlist '{playlist_name}' ?", 
                    bg='#2d2d2d', fg='white', font=('TkDefaultFont', 10),
                    justify=tk.CENTER)
    label.pack(pady=30)
    
    # Frame pour les boutons
    button_frame = tk.Frame(dialog, bg='#2d2d2d')
    button_frame.pack(pady=20)
    
    def delete_playlist():
        del self.playlists[playlist_name]
        self.status_bar.config(text=f"Playlist '{playlist_name}' supprimée")
        self._display_playlists()  # Rafraîchir l'affichage
        self.save_playlists()  # Sauvegarder
        dialog.destroy()
    
    def cancel():
        dialog.destroy()
    
    # Boutons
    delete_btn = tk.Button(button_frame, text="Supprimer",
                            bg="#3d3d3d", fg="white", activebackground="#ff6666",
                            relief="flat", bd=0, padx=20, pady=5)
    delete_btn.bind("<Double-1>", lambda event: delete_playlist())
    delete_btn.pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(button_frame, text="Annuler", command=cancel,
                            bg="#666666", fg="white", activebackground="#777777",
                            relief="flat", bd=0, padx=20, pady=5)
    cancel_btn.pack(side=tk.LEFT, padx=5)
    
    # Bind Escape key
    dialog.bind('<Escape>', lambda e: cancel())

def _show_playlist_content_window(self, playlist_name):
    """Affiche le contenu d'une playlist dans une fenêtre avec le même style que les téléchargements"""
    dialog = tk.Toplevel(self.root)
    dialog.title(f"Playlist: {playlist_name}")
    dialog.geometry("800x600")
    dialog.configure(bg='#2d2d2d')
    
    # Centrer la fenêtre
    dialog.transient(self.root)
    
    # Titre
    title_label = tk.Label(dialog, text=f"Playlist: {playlist_name}", 
                            bg='#2d2d2d', fg='white', font=('Helvetica', 14, 'bold'))
    title_label.pack(pady=10)
    
    # Canvas avec scrollbar pour les musiques
    canvas = tk.Canvas(
        dialog,
        bg='#3d3d3d',
        highlightthickness=0
    )
    scrollbar = ttk.Scrollbar(
        dialog,
        orient="vertical",
        command=canvas.yview
    )
    canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    
    container = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=container, anchor="nw")
    
    container.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    # Bind mousewheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind("<MouseWheel>", _on_mousewheel)
    container.bind("<MouseWheel>", _on_mousewheel)
    
    # Afficher les musiques de la playlist
    songs = self.playlists.get(playlist_name, [])
    for filepath in songs:
        self._add_playlist_song_item(container, filepath, playlist_name)
    
    # Bouton fermer
    close_btn = tk.Button(dialog, text="Fermer", command=dialog.destroy,
                            bg="#666666", fg="white", activebackground="#777777",
                            relief="flat", bd=0, padx=20, pady=5)
    close_btn.pack(pady=10)

def _display_playlist_songs(self, playlist_name):
        """Affiche les musiques d'une playlist avec le même style que les téléchargements"""
        if playlist_name not in self.playlists:
            return
        
        # Vider le container actuel
        for widget in self.playlist_content_container.winfo_children():
            widget.destroy()
        
        songs = self.playlists[playlist_name]
        
        for i, filepath in enumerate(songs):
            self._add_playlist_song_item(filepath, playlist_name, i)

def _back_to_playlists(self):
    """Retourne à l'affichage des playlists"""
    self.current_viewing_playlist = None
    
    # Nettoyer complètement le contenu actuel
    for widget in self.library_content_frame.winfo_children():
        widget.destroy()
    
    # Réafficher le contenu des playlists
    self.show_playlists_content()


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
            highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
            # highlightbackground=TEST_COLOR,
            highlightthickness=1,
            
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
        thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(5, 4), pady=2)
        thumbnail_label.grid_propagate(False)
        
        # Charger la miniature
        self._load_download_thumbnail(filepath, thumbnail_label)
        
        # 3. Texte (colonne 2)
        truncated_title = self._truncate_text_for_display(filename, max_width_pixels=328, font_family='TkDefaultFont', font_size=9)
        title_label = tk.Label(
            item_frame,
            text=truncated_title,
            bg=bg_color,
            fg='white',
            font=('TkDefaultFont', 9),
            anchor='w',
            justify='left',
            wraplength=0
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

def _remove_from_playlist_view(self, filepath, playlist_name, event=None):
    """Supprime une musique de la playlist et rafraîchit l'affichage"""
    # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
    if event and (event.state & 0x4):  # Ctrl est enfoncé
        # Pour la suppression définitive, on utilise une approche différente
        # car on n'a pas de frame à passer
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
                
                # Supprimer le fichier audio
                os.remove(filepath)
                
                # Supprimer la miniature associée si elle existe
                thumbnail_path = os.path.splitext(filepath)[0] + ".jpg"
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                # Supprimer de la playlist et gérer la lecture
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
                            self._show_current_song_thumbnail()
                            self.status_bar.config(text="Playlist vide")
                
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