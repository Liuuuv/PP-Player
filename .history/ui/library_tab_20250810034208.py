"""
Onglet de bibliothèque musicale
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk


class LibraryTab:
    """Onglet de bibliothèque musicale"""
    
    def __init__(self, parent, playlist_manager, file_service, audio_player, settings):
        self.parent = parent
        self.playlist_manager = playlist_manager
        self.file_service = file_service
        self.audio_player = audio_player
        self.settings = settings
        
        # Variables d'interface
        self.current_library_tab = "téléchargées"
        self.library_tab_buttons = {}
        self.all_downloaded_files = []
        self.search_timer = None
        
        # Créer l'interface
        self.frame = ttk.Frame(parent)
        self._create_interface()
        
        # Charger les données initiales
        self._load_initial_data()
    
    def _create_interface(self):
        """Crée l'interface de l'onglet bibliothèque"""
        # Frame principal avec onglets verticaux
        main_container = tk.Frame(self.frame, bg='#2d2d2d')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Frame pour les onglets verticaux (gauche)
        vertical_tabs_frame = tk.Frame(main_container, bg='#2d2d2d', width=150)
        vertical_tabs_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        vertical_tabs_frame.pack_propagate(False)
        
        # Frame pour le contenu (droite)
        self.library_content_frame = tk.Frame(main_container, bg='#2d2d2d')
        self.library_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Créer les boutons d'onglets verticaux
        self._create_vertical_tabs(vertical_tabs_frame)
        
        # Initialiser avec l'onglet "téléchargées"
        self.switch_library_tab("téléchargées")
    
    def _create_vertical_tabs(self, parent):
        """Crée les onglets verticaux"""
        # Onglet "Téléchargées"
        self.downloads_btn = tk.Button(
            parent,
            text=f"Téléchargées ({self.file_service.count_downloaded_files() if hasattr(self.file_service, 'count_downloaded_files') else 0})",
            command=lambda: self.switch_library_tab("téléchargées"),
            bg="#4a8fe7",
            fg="white",
            activebackground="#5a9fd8",
            relief="flat",
            bd=0,
            padx=10,
            pady=10,
            anchor="w"
        )
        self.downloads_btn.pack(fill=tk.X, pady=2)
        self.library_tab_buttons["téléchargées"] = self.downloads_btn
        
        # Onglet "Playlists"
        playlists_btn = tk.Button(
            parent,
            text="Playlists",
            command=lambda: self.switch_library_tab("playlists"),
            bg="#3d3d3d",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            padx=10,
            pady=10,
            anchor="w"
        )
        playlists_btn.pack(fill=tk.X, pady=2)
        self.library_tab_buttons["playlists"] = playlists_btn
        
        # Onglet "Ajouter des fichiers"
        add_files_btn = tk.Button(
            parent,
            text="+ Ajouter fichiers",
            command=self._add_files,
            bg="#3d3d3d",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            padx=10,
            pady=10,
            anchor="w"
        )
        add_files_btn.pack(fill=tk.X, pady=2)
    
    def switch_library_tab(self, tab_name):
        """Change d'onglet dans la bibliothèque"""
        # Mettre à jour l'apparence des boutons
        for name, button in self.library_tab_buttons.items():
            if name == tab_name:
                button.configure(bg="#4a8fe7")
            else:
                button.configure(bg="#3d3d3d")
        
        self.current_library_tab = tab_name
        
        # Vider le contenu actuel
        for widget in self.library_content_frame.winfo_children():
            widget.destroy()
        
        # Afficher le contenu selon l'onglet
        if tab_name == "téléchargées":
            self._show_downloads_content()
        elif tab_name == "playlists":
            self._show_playlists_content()
    
    def _show_downloads_content(self):
        """Affiche le contenu de l'onglet téléchargées"""
        # Frame pour la barre de recherche
        search_frame = ttk.Frame(self.library_content_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        # Champ de recherche
        self.library_search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.library_search_var,
            font=('TkDefaultFont', 11),
            bg='#4d4d4d',
            fg='white',
            insertbackground='white',
            relief='flat',
            bd=5
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self._on_library_search_change)
        
        # Bouton effacer recherche
        clear_btn = tk.Button(
            search_frame,
            text="✕",
            command=self._clear_library_search,
            bg='#3d3d3d',
            fg='white',
            activebackground='#4a4a4a',
            relief='flat',
            bd=0,
            width=3
        )
        clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
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
        
        # Bind pour la molette de souris
        self._bind_mousewheel(self.downloads_canvas)
        
        # Charger et afficher les fichiers téléchargés
        self._load_downloaded_files()
    
    def _show_playlists_content(self):
        """Affiche le contenu de l'onglet playlists"""
        # Frame pour les boutons de gestion
        buttons_frame = ttk.Frame(self.library_content_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        # Bouton créer playlist
        create_btn = tk.Button(
            buttons_frame,
            text="+ Nouvelle playlist",
            command=self._create_playlist,
            bg='#4a8fe7',
            fg='white',
            activebackground='#5a9fd8',
            relief='flat',
            bd=0,
            padx=15,
            pady=5
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
        
        # Bind pour la molette de souris
        self._bind_mousewheel(self.playlists_canvas)
        
        # Charger et afficher les playlists
        self._load_playlists()
    
    def _bind_mousewheel(self, canvas):
        """Configure la molette de souris pour le scroll"""
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Configure>", on_configure)
    
    def _load_downloaded_files(self):
        """Charge et affiche les fichiers téléchargés"""
        # Obtenir la liste des fichiers
        if hasattr(self.file_service, 'get_downloaded_files'):
            self.all_downloaded_files = self.file_service.get_downloaded_files()
        else:
            # Fallback pour compatibilité
            downloads_dir = "downloads"
            self.all_downloaded_files = []
            if os.path.exists(downloads_dir):
                for filename in os.listdir(downloads_dir):
                    if self.file_service.is_audio_file(filename):
                        self.all_downloaded_files.append(os.path.join(downloads_dir, filename))
        
        # Afficher les fichiers
        self._display_files(self.all_downloaded_files)
    
    def _display_files(self, files):
        """Affiche une liste de fichiers"""
        # Vider le container
        for widget in self.downloads_container.winfo_children():
            widget.destroy()
        
        if not files:
            no_files_label = tk.Label(
                self.downloads_container,
                text="Aucun fichier trouvé",
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 12)
            )
            no_files_label.pack(pady=50)
            return
        
        # Créer un élément pour chaque fichier
        for filepath in files:
            self._create_file_item(filepath)
        
        # Mettre à jour la région de scroll
        self.downloads_container.update_idletasks()
        self.downloads_canvas.configure(scrollregion=self.downloads_canvas.bbox("all"))
    
    def _create_file_item(self, filepath):
        """Crée un élément de fichier"""
        filename = os.path.basename(filepath)
        name_without_ext = os.path.splitext(filename)[0]
        
        # Frame principal
        item_frame = tk.Frame(
            self.downloads_container,
            bg='#4d4d4d',
            relief='flat',
            bd=1
        )
        item_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Configurer la grille
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Miniature
        thumbnail_label = tk.Label(
            item_frame,
            text="♪",
            bg='#4d4d4d',
            fg='#666666',
            font=('TkDefaultFont', 16),
            width=6,
            height=2
        )
        thumbnail_label.grid(row=0, column=0, padx=10, pady=5)
        
        # Informations du fichier
        info_frame = tk.Frame(item_frame, bg='#4d4d4d')
        info_frame.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=5)
        
        # Nom du fichier
        title_label = tk.Label(
            info_frame,
            text=name_without_ext[:60] + "..." if len(name_without_ext) > 60 else name_without_ext,
            bg='#4d4d4d',
            fg='white',
            font=('TkDefaultFont', 11, 'bold'),
            anchor='w'
        )
        title_label.pack(fill=tk.X, anchor='w')
        
        # Taille du fichier
        try:
            file_size = self.file_service.get_file_size(filepath)
            size_text = self.file_service.format_file_size(file_size)
        except:
            size_text = "Taille inconnue"
        
        size_label = tk.Label(
            info_frame,
            text=size_text,
            bg='#4d4d4d',
            fg='#cccccc',
            font=('TkDefaultFont', 9),
            anchor='w'
        )
        size_label.pack(fill=tk.X, anchor='w')
        
        # Boutons d'action
        buttons_frame = tk.Frame(info_frame, bg='#4d4d4d')
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Bouton jouer
        play_btn = tk.Button(
            buttons_frame,
            text="▶ Jouer",
            command=lambda: self._play_file(filepath),
            bg='#4a8fe7',
            fg='white',
            activebackground='#5a9fd8',
            relief='flat',
            bd=0,
            padx=10,
            pady=2
        )
        play_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Bouton ajouter à playlist
        add_btn = tk.Button(
            buttons_frame,
            text="+ Playlist",
            command=lambda: self._add_file_to_playlist(filepath),
            bg='#3d3d3d',
            fg='white',
            activebackground='#4a4a4a',
            relief='flat',
            bd=0,
            padx=10,
            pady=2
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Bouton supprimer
        delete_btn = tk.Button(
            buttons_frame,
            text="🗑",
            command=lambda: self._delete_file(filepath, item_frame),
            bg='#ff4444',
            fg='white',
            activebackground='#ff6666',
            relief='flat',
            bd=0,
            padx=8,
            pady=2
        )
        delete_btn.pack(side=tk.RIGHT)
        
        # Effet de survol
        self._add_hover_effect(item_frame, info_frame, buttons_frame, thumbnail_label, title_label, size_label)
    
    def _add_hover_effect(self, *widgets):
        """Ajoute un effet de survol aux widgets"""
        def on_enter(event):
            for widget in widgets:
                widget.configure(bg='#5d5d5d')
        
        def on_leave(event):
            for widget in widgets:
                widget.configure(bg='#4d4d4d')
        
        for widget in widgets:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def _play_file(self, filepath):
        """Joue un fichier"""
        # Ajouter à la playlist principale et jouer
        self.playlist_manager.main_playlist.clear()
        self.playlist_manager.add_to_playlist("Main Playlist", filepath)
        self.audio_player.current_index = 0
        self.audio_player.play_current_track()
    
    def _add_file_to_playlist(self, filepath):
        """Ajoute un fichier à une playlist"""
        # Pour l'instant, ajouter à la playlist principale
        self.playlist_manager.add_to_playlist("Main Playlist", filepath)
        messagebox.showinfo("Succès", "Fichier ajouté à la playlist principale")
    
    def _delete_file(self, filepath, item_frame):
        """Supprime un fichier"""
        if messagebox.askyesno("Confirmation", f"Supprimer définitivement ce fichier ?\n\n{os.path.basename(filepath)}"):
            if self.file_service.delete_file(filepath):
                item_frame.destroy()
                self.all_downloaded_files.remove(filepath)
                messagebox.showinfo("Succès", "Fichier supprimé")
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer le fichier")
    
    def _load_playlists(self):
        """Charge et affiche les playlists"""
        # Vider le container
        for widget in self.playlists_container.winfo_children():
            widget.destroy()
        
        playlists = self.playlist_manager.get_playlist_names()
        
        if len(playlists) <= 1:  # Seulement la Main Playlist
            no_playlists_label = tk.Label(
                self.playlists_container,
                text="Aucune playlist créée",
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 12)
            )
            no_playlists_label.pack(pady=50)
            return
        
        # Afficher chaque playlist (sauf Main Playlist)
        for playlist_name in playlists:
            if playlist_name != "Main Playlist":
                self._create_playlist_item(playlist_name)
        
        # Mettre à jour la région de scroll
        self.playlists_container.update_idletasks()
        self.playlists_canvas.configure(scrollregion=self.playlists_canvas.bbox("all"))
    
    def _create_playlist_item(self, playlist_name):
        """Crée un élément de playlist"""
        playlist = self.playlist_manager.get_playlist(playlist_name)
        
        # Frame principal
        item_frame = tk.Frame(
            self.playlists_container,
            bg='#4d4d4d',
            relief='flat',
            bd=1
        )
        item_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Nom de la playlist
        name_label = tk.Label(
            item_frame,
            text=playlist_name,
            bg='#4d4d4d',
            fg='white',
            font=('TkDefaultFont', 12, 'bold'),
            anchor='w'
        )
        name_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Nombre de chansons
        count_label = tk.Label(
            item_frame,
            text=f"{len(playlist)} chanson(s)",
            bg='#4d4d4d',
            fg='#cccccc',
            font=('TkDefaultFont', 10),
            anchor='w'
        )
        count_label.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Boutons
        buttons_frame = tk.Frame(item_frame, bg='#4d4d4d')
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Bouton jouer
        play_btn = tk.Button(
            buttons_frame,
            text="▶ Jouer",
            command=lambda: self._play_playlist(playlist_name),
            bg='#4a8fe7',
            fg='white',
            activebackground='#5a9fd8',
            relief='flat',
            bd=0,
            padx=10,
            pady=2
        )
        play_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Bouton supprimer
        delete_btn = tk.Button(
            buttons_frame,
            text="Supprimer",
            command=lambda: self._delete_playlist(playlist_name),
            bg='#ff4444',
            fg='white',
            activebackground='#ff6666',
            relief='flat',
            bd=0,
            padx=10,
            pady=2
        )
        delete_btn.pack(side=tk.RIGHT)
        
        # Effet de survol
        self._add_hover_effect(item_frame, name_label, count_label, buttons_frame)
    
    def _play_playlist(self, playlist_name):
        """Joue une playlist"""
        playlist = self.playlist_manager.get_playlist(playlist_name)
        if playlist:
            self.playlist_manager.main_playlist = playlist.copy()
            self.audio_player.current_index = 0
            self.audio_player.play_current_track()
    
    def _delete_playlist(self, playlist_name):
        """Supprime une playlist"""
        if messagebox.askyesno("Confirmation", f"Supprimer la playlist '{playlist_name}' ?"):
            if self.playlist_manager.delete_playlist(playlist_name):
                self._load_playlists()
                messagebox.showinfo("Succès", "Playlist supprimée")
    
    def _create_playlist(self):
        """Crée une nouvelle playlist"""
        from tkinter import simpledialog
        
        name = simpledialog.askstring("Nouvelle playlist", "Nom de la playlist:")
        if name and name.strip():
            name = name.strip()
            if self.playlist_manager.create_playlist(name):
                self._load_playlists()
                messagebox.showinfo("Succès", f"Playlist '{name}' créée")
            else:
                messagebox.showerror("Erreur", "Une playlist avec ce nom existe déjà")
    
    def _add_files(self):
        """Ajoute des fichiers à la bibliothèque"""
        files = self.file_service.select_files()
        if files:
            # Pour l'instant, on les ajoute juste à la playlist principale
            for filepath in files:
                self.playlist_manager.add_to_playlist("Main Playlist", filepath)
            
            messagebox.showinfo("Succès", f"{len(files)} fichier(s) ajouté(s) à la playlist principale")
    
    def _on_library_search_change(self, event):
        """Gère les changements dans la recherche de bibliothèque"""
        # Annuler le timer précédent
        if self.search_timer:
            self.library_content_frame.after_cancel(self.search_timer)
        
        # Programmer une nouvelle recherche avec délai
        self.search_timer = self.library_content_frame.after(300, self._perform_library_search)
    
    def _perform_library_search(self):
        """Effectue la recherche dans la bibliothèque"""
        query = self.library_search_var.get().strip()
        
        if not query:
            # Afficher tous les fichiers
            self._display_files(self.all_downloaded_files)
        else:
            # Filtrer les fichiers
            filtered_files = self.file_service.search_files(self.all_downloaded_files, query)
            self._display_files(filtered_files)
    
    def _clear_library_search(self):
        """Efface la recherche de bibliothèque"""
        self.library_search_var.set("")
        self._display_files(self.all_downloaded_files)
    
    def _load_initial_data(self):
        """Charge les données initiales"""
        pass
    
    def refresh_current_view(self):
        """Rafraîchit la vue actuelle"""
        if self.current_library_tab == "téléchargées":
            self._load_downloaded_files()
        elif self.current_library_tab == "playlists":
            self._load_playlists()
    
    def get_frame(self):
        """Retourne le frame de l'onglet"""
        return self.frame