import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier library_tab
from library_tab import *



def show_downloads_content(self):
    """Affiche le contenu de l'onglet téléchargées"""
    
    # Frame pour la barre de recherche
    search_frame = ttk.Frame(self.library_content_frame)
    search_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
    
    # Barre de recherche
    self.library_search_entry = tk.Entry(
        search_frame,
        bg='#3d3d3d',
        fg='white',
        insertbackground='white',
        relief='flat',
        bd=5
    )
    self.library_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Lier l'événement de saisie pour la recherche en temps réel
    self.library_search_entry.bind('<KeyRelease>', self._on_library_search_change)
    
    # Bouton pour effacer la recherche
    clear_btn = tk.Button(
        search_frame,
        image=self.icons["cross_small"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=4,
        pady=4,
        width=20,
        height=20
    )
    clear_btn.bind("<Button-1>", lambda event: self._clear_library_search())
    clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    # Frame pour les boutons de lecture
    buttons_frame = ttk.Frame(self.library_content_frame)
    buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    # Bouton pour jouer toutes les musiques dans l'ordre
    play_all_btn = tk.Button(
        buttons_frame,
        image=self.icons["play"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=8,
        pady=8,
        command=self.play_all_downloads_ordered
    )
    play_all_btn.pack(side=tk.LEFT, padx=(0, 10))
    create_tooltip(play_all_btn, "Jouer toutes les musiques\nLit toutes les musiques téléchargées dans l'ordre")
    
    # Bouton pour jouer toutes les musiques en mode aléatoire
    shuffle_all_btn = tk.Button(
        buttons_frame,
        image=self.icons["shuffle"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=8,
        pady=8,
        command=self.play_all_downloads_shuffle
    )
    shuffle_all_btn.pack(side=tk.LEFT)
    create_tooltip(shuffle_all_btn, "Jouer en mode aléatoire\nLit toutes les musiques téléchargées dans un ordre aléatoire")
    
    # Canvas avec scrollbar pour les téléchargements
    self.downloads_canvas = tk.Canvas(
        self.library_content_frame,
        bg='#3d3d3d',
        highlightthickness=0
    )
    self.downloads_scrollbar = ttk.Scrollbar(
        self.library_content_frame,
        orient="vertical",
        command=self.downloads_canvas.yview
    )
    self.downloads_canvas.configure(yscrollcommand=self.downloads_scrollbar.set)
    
    self.downloads_scrollbar.pack(side="right", fill="y")
    self.downloads_canvas.pack(side="left", fill="both", expand=True)
    
    self.downloads_container = ttk.Frame(self.downloads_canvas)
    self.downloads_canvas.create_window((0, 0), window=self.downloads_container, anchor="nw")
    
    self.downloads_container.bind(
        "<Configure>",
        lambda e: self.downloads_canvas.configure(
            scrollregion=self.downloads_canvas.bbox("all")
        )
    )
    
    self._bind_mousewheel(self.downloads_canvas, self.downloads_canvas)
    self._bind_mousewheel(self.downloads_container, self.downloads_canvas)
    
    # Initialiser la liste de tous les fichiers téléchargés
    self.all_downloaded_files = []
    
    # Charger et afficher les fichiers téléchargés
    self.load_downloaded_files()

def load_downloaded_files(self):
    """Charge et affiche tous les fichiers du dossier downloads"""
    downloads_dir = "downloads"
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
        return
    
    # Extensions audio supportées
    audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
    
    # Vider la liste actuelle et le cache
    self.all_downloaded_files = []
    self.normalized_filenames = {}
    
    # Parcourir le dossier downloads et stocker tous les fichiers
    for filename in os.listdir(downloads_dir):
        if filename.lower().endswith(audio_extensions):
            filepath = os.path.join(downloads_dir, filename)
            self.all_downloaded_files.append(filepath)
            
            # Créer le cache du nom normalisé pour accélérer les recherches
            normalized_name = os.path.basename(filepath).lower()
            self.normalized_filenames[filepath] = normalized_name
    
    # Mettre à jour le nombre de fichiers téléchargés
    self.num_downloaded_files = len(self.all_downloaded_files)
    
    # Afficher tous les fichiers (sans filtre)
    self._display_filtered_downloads(self.all_downloaded_files)
    
    # Mettre à jour le texte du bouton
    self._update_downloads_button()

def _display_filtered_downloads(self, files_to_display):
    """Affiche une liste filtrée de fichiers téléchargés (optimisé)"""
    # Vider le container actuel
    for widget in self.downloads_container.winfo_children():
        widget.destroy()
    
    # Afficher les fichiers filtrés par batch pour améliorer les performances
    if len(files_to_display) > 50:  # Si beaucoup de fichiers, les afficher par batch
        self._display_files_batch(files_to_display, 0)
    else:
        # Afficher directement si peu de fichiers
        for filepath in files_to_display:
            self._add_download_item(filepath)

def _update_downloads_button(self):
    """Met à jour le texte du bouton téléchargées avec le nombre actuel"""
    if hasattr(self, 'downloads_btn'):
        self.downloads_btn.configure(text="Téléchargées " + f"({self.num_downloaded_files})")
        
def _display_files_batch(self, files_to_display, start_index, batch_size=20):
    """Affiche les fichiers par batch pour éviter de bloquer l'interface"""
    end_index = min(start_index + batch_size, len(files_to_display))
    
    # Afficher le batch actuel
    for i in range(start_index, end_index):
        self._add_download_item(files_to_display[i])
    
    # Programmer le batch suivant si nécessaire
    if end_index < len(files_to_display):
        self.root.after(10, lambda: self._display_files_batch(files_to_display, end_index, batch_size))

def _add_download_item(self, filepath):
    """Ajoute un élément téléchargé avec le même visuel que les résultats de recherche, visuel"""
    try:
        filename = os.path.basename(filepath)
        
        # Vérifier si c'est la chanson en cours de lecture
        is_current_song = (len(self.main_playlist) > 0 and 
                            self.current_index < len(self.main_playlist) and 
                            self.main_playlist[self.current_index] == filepath)
        
        # Frame principal - même style que les résultats YouTube
        bg_color = '#5a9fd8' if is_current_song else '#4a4a4a'
        item_frame = tk.Frame(
            self.downloads_container,
            bg=bg_color,  # Fond bleu si c'est la chanson en cours
            relief='flat',
            bd=1,
            highlightbackground='#5a5a5a',
            highlightthickness=1
        )
        item_frame.pack(fill="x", padx=5, pady=2)
        
        # Stocker le chemin du fichier pour pouvoir le retrouver plus tard
        item_frame.filepath = filepath
        item_frame.selected = is_current_song
        
        # Configuration de la grille en 5 colonnes : miniature, texte, durée, bouton ajouter, bouton supprimer
        item_frame.columnconfigure(0, minsize=80, weight=0)  # Miniature
        item_frame.columnconfigure(1, weight=1)              # Texte
        item_frame.columnconfigure(2, minsize=60, weight=0)  # Durée
        item_frame.columnconfigure(3, minsize=80, weight=0)  # Bouton ajouter
        item_frame.columnconfigure(4, minsize=40, weight=0)  # Bouton supprimer
        item_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur fixe
        
        # 1. Miniature (colonne 0)
        thumbnail_label = tk.Label(
            item_frame,
            bg=bg_color,  # Même fond que le frame parent
            width=10,
            height=3,
            anchor='center'
        )
        thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(10, 10), pady=8)
        # Forcer la taille fixe
        thumbnail_label.grid_propagate(False)
        
        # Charger la miniature (chercher un fichier image associé)
        self._load_download_thumbnail(filepath, thumbnail_label)
        
        # 2. Texte (colonne 1)
        truncated_title = self._truncate_text_for_display(filename)
        title_label = tk.Label(
            item_frame,
            text=truncated_title,
            bg=bg_color,  # Même fond que le frame parent
            fg='white',
            font=('TkDefaultFont', 9),
            anchor='w',
            justify='left',
            wraplength=170  # Même largeur que dans la liste de lecture
        )
        title_label.grid(row=0, column=1, sticky='nsew', padx=(0, 10), pady=8)
        
        # 3. Durée (colonne 2)
        duration_label = tk.Label(
            item_frame,
            text=self._get_audio_duration(filepath),
            bg=bg_color,  # Même fond que le frame parent
            fg='#cccccc',
            font=('TkDefaultFont', 8),
            anchor='center'
        )
        duration_label.grid(row=0, column=2, sticky='ns', padx=(0, 10), pady=8)
        
        # 4. Bouton "Ajouter à la liste de lecture" (colonne 3)
        add_btn = tk.Button(
            item_frame,
            text="▼",
            bg="#4a8fe7",
            fg="white",
            activebackground="#5a9fd8",
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            font=('TkDefaultFont', 8)
        )
        add_btn.grid(row=0, column=3, sticky='ns', padx=(0, 10), pady=8)
        
        # Configurer la commande après création pour avoir la référence du bouton
        add_btn.config(command=lambda f=filepath, btn=add_btn: self._show_playlist_menu(f, btn))
        create_tooltip(add_btn, "Ajouter à une playlist\nCliquez pour choisir dans quelle playlist ajouter cette chanson")
        
        # Stocker la référence du bouton pour le menu
        add_btn.filepath = filepath
        
        # 5. Bouton de suppression (colonne 4)
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
            font=('TkDefaultFont', 8)
        )
        delete_btn.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
        
        # Fonction pour gérer la suppression avec double-clic
        def on_delete_double_click(event):
            # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
            if event.state & 0x4:  # Ctrl est enfoncé
                self._delete_from_downloads(filepath, item_frame)
            else:
                # Suppression normale : retirer de la playlist seulement
                if filepath in self.main_playlist:
                    index = self.main_playlist.index(filepath)
                    self.main_playlist.remove(filepath)
                    
                    # Mettre à jour l'index courant si nécessaire
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
                    
                    # Rafraîchir l'affichage de la playlist principale
                    self._refresh_playlist_display()
                    
                    self.status_bar.config(text=f"Retiré de la playlist: {os.path.basename(filepath)}")
        
        delete_btn.bind("<Double-1>", on_delete_double_click)
        create_tooltip(delete_btn, "Supprimer le fichier\nDouble-clic: Retirer de la playlist\nCtrl + Double-clic: Supprimer définitivement du disque")
        
        # Gestion des clics (simple et double)
        def on_item_click(event):
            # Vérifier si Shift est enfoncé pour la sélection multiple
            if event.state & 0x1:  # Shift est enfoncé
                self.shift_selection_active = True
                self.toggle_item_selection(filepath, item_frame)
            else:
                # Clic normal sans Shift - ne pas effacer la sélection si elle existe
                pass
        
        def on_item_double_click(event):
            # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
            if event.state & 0x4:  # Ctrl est enfoncé
                self._delete_from_downloads(filepath, item_frame)
            elif event.state & 0x1 or self.selected_items:  # Shift est enfoncé ou mode sélection - ne rien faire
                pass
            else:
                # Comportement normal : ajouter et jouer
                self._add_download_to_playlist(filepath)
                # Jouer immédiatement
                if filepath in self.main_playlist:
                    self.current_index = self.main_playlist.index(filepath)
                    self.play_track()
        
        # Bindings pour les clics simples et doubles
        item_frame.bind("<Button-1>", on_item_click)
        item_frame.bind("<Double-1>", on_item_double_click)
        thumbnail_label.bind("<Button-1>", on_item_click)
        thumbnail_label.bind("<Double-1>", on_item_double_click)
        title_label.bind("<Button-1>", on_item_click)
        title_label.bind("<Double-1>", on_item_double_click)
        duration_label.bind("<Button-1>", on_item_click)
        duration_label.bind("<Double-1>", on_item_double_click)
        
        # Clic droit pour placer après la chanson en cours ou ouvrir le menu de sélection
        def on_item_right_click(event):
            # Si on a des éléments sélectionnés, ouvrir le menu de sélection
            if self.selected_items:
                self.show_selection_menu(event)
            else:
                # Comportement normal : placer après la chanson en cours
                self._play_after_current(filepath)
        
        item_frame.bind("<Button-3>", on_item_right_click)
        thumbnail_label.bind("<Button-3>", on_item_right_click)
        title_label.bind("<Button-3>", on_item_right_click)
        duration_label.bind("<Button-3>", on_item_right_click)
        
    except Exception as e:
        print(f"Erreur affichage download item: {e}")