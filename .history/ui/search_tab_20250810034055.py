"""
Onglet de recherche YouTube
"""
import tkinter as tk
from tkinter import ttk
import threading
from PIL import Image, ImageTk


class SearchTab:
    """Onglet de recherche YouTube"""
    
    def __init__(self, parent, youtube_service, playlist_manager, audio_player):
        self.parent = parent
        self.youtube_service = youtube_service
        self.playlist_manager = playlist_manager
        self.audio_player = audio_player
        
        # Variables de recherche
        self.search_timer = None
        self.search_delay = 300
        
        # Créer l'interface
        self.frame = ttk.Frame(parent)
        self._create_interface()
        
        # Configurer les callbacks
        self.youtube_service.on_search_results = self._on_search_results
        self.youtube_service.on_download_progress = self._on_download_progress
        self.youtube_service.on_download_complete = self._on_download_complete
        self.youtube_service.on_download_error = self._on_download_error
    
    def _create_interface(self):
        """Crée l'interface de l'onglet recherche"""
        # Frame pour la barre de recherche
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Champ de recherche
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('TkDefaultFont', 12),
            bg='#4d4d4d',
            fg='white',
            insertbackground='white',
            relief='flat',
            bd=5
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        self.search_entry.bind('<Return>', self._on_search_enter)
        
        # Bouton de recherche
        search_button = tk.Button(
            search_frame,
            text="Rechercher",
            command=self._perform_search,
            bg='#4a8fe7',
            fg='white',
            activebackground='#5a9fd8',
            relief='flat',
            bd=0,
            padx=20
        )
        search_button.pack(side=tk.RIGHT)
        
        # Frame pour les résultats
        self._create_results_frame()
    
    def _create_results_frame(self):
        """Crée le frame pour les résultats de recherche"""
        # Canvas avec scrollbar pour les résultats
        self.results_canvas = tk.Canvas(
            self.frame,
            bg='#3d3d3d',
            highlightthickness=0
        )
        self.results_scrollbar = ttk.Scrollbar(
            self.frame,
            orient="vertical",
            command=self.results_canvas.yview
        )
        self.results_canvas.configure(yscrollcommand=self.results_scrollbar.set)
        
        self.results_scrollbar.pack(side="right", fill="y")
        self.results_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Container pour les résultats
        self.results_container = ttk.Frame(self.results_canvas)
        self.results_canvas.create_window((0, 0), window=self.results_container, anchor="nw")
        
        # Bind pour la molette de souris
        self._bind_mousewheel()
        
        # Message initial
        self._show_initial_message()
    
    def _bind_mousewheel(self):
        """Configure la molette de souris pour le scroll"""
        def on_mousewheel(event):
            self.results_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.results_canvas.bind("<MouseWheel>", on_mousewheel)
        self.results_container.bind("<MouseWheel>", on_mousewheel)
    
    def _show_initial_message(self):
        """Affiche le message initial"""
        message_label = tk.Label(
            self.results_container,
            text="Recherchez de la musique sur YouTube...",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 14)
        )
        message_label.pack(expand=True, pady=50)
    
    def _on_search_change(self, event):
        """Gère les changements dans le champ de recherche"""
        # Annuler le timer précédent
        if self.search_timer:
            self.frame.after_cancel(self.search_timer)
        
        # Programmer une nouvelle recherche avec délai
        query = self.search_var.get().strip()
        if query:
            self.search_timer = self.frame.after(self.search_delay, self._perform_search)
    
    def _on_search_enter(self, event):
        """Gère l'appui sur Entrée dans le champ de recherche"""
        self._perform_search()
    
    def _perform_search(self):
        """Lance la recherche"""
        query = self.search_var.get().strip()
        if not query:
            return
        
        # Vider les résultats précédents
        self._clear_results()
        
        # Afficher un indicateur de chargement
        self._show_loading()
        
        # Lancer la recherche dans un thread séparé
        def search_thread():
            self.youtube_service.search_youtube(query, max_results=20)
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def _clear_results(self):
        """Vide les résultats de recherche"""
        for widget in self.results_container.winfo_children():
            widget.destroy()
    
    def _show_loading(self):
        """Affiche un indicateur de chargement"""
        loading_label = tk.Label(
            self.results_container,
            text="Recherche en cours...",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 12)
        )
        loading_label.pack(pady=20)
    
    def _on_search_results(self, results):
        """Appelé quand les résultats de recherche arrivent"""
        # Vider les résultats précédents
        self._clear_results()
        
        if not results:
            no_results_label = tk.Label(
                self.results_container,
                text="Aucun résultat trouvé",
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 12)
            )
            no_results_label.pack(pady=20)
            return
        
        # Afficher les résultats
        for result in results:
            self._create_result_item(result)
        
        # Mettre à jour la région de scroll
        self.results_container.update_idletasks()
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
    
    def _create_result_item(self, result):
        """Crée un élément de résultat"""
        # Frame principal pour l'élément
        item_frame = tk.Frame(
            self.results_container,
            bg='#4d4d4d',
            relief='flat',
            bd=1
        )
        item_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Configurer la grille
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Miniature (placeholder)
        thumbnail_label = tk.Label(
            item_frame,
            text="🎵",
            bg='#4d4d4d',
            fg='#cccccc',
            font=('TkDefaultFont', 20),
            width=6,
            height=3
        )
        thumbnail_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        
        # Informations
        info_frame = tk.Frame(item_frame, bg='#4d4d4d')
        info_frame.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=5)
        
        # Titre
        title_label = tk.Label(
            info_frame,
            text=result['title'][:80] + "..." if len(result['title']) > 80 else result['title'],
            bg='#4d4d4d',
            fg='white',
            font=('TkDefaultFont', 11, 'bold'),
            anchor='w',
            justify='left'
        )
        title_label.pack(fill=tk.X, anchor='w')
        
        # Informations supplémentaires
        info_text = f"Par: {result['uploader']}"
        if result['duration']:
            minutes = result['duration'] // 60
            seconds = result['duration'] % 60
            info_text += f" • Durée: {minutes}:{seconds:02d}"
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            bg='#4d4d4d',
            fg='#cccccc',
            font=('TkDefaultFont', 9),
            anchor='w',
            justify='left'
        )
        info_label.pack(fill=tk.X, anchor='w')
        
        # Boutons d'action
        buttons_frame = tk.Frame(info_frame, bg='#4d4d4d')
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Bouton télécharger
        download_btn = tk.Button(
            buttons_frame,
            text="Télécharger",
            command=lambda: self._download_video(result, download_btn),
            bg='#4a8fe7',
            fg='white',
            activebackground='#5a9fd8',
            relief='flat',
            bd=0,
            padx=10,
            pady=2
        )
        download_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Bouton ajouter à la playlist
        add_btn = tk.Button(
            buttons_frame,
            text="+ Playlist",
            command=lambda: self._add_to_playlist(result),
            bg='#3d3d3d',
            fg='white',
            activebackground='#4a4a4a',
            relief='flat',
            bd=0,
            padx=10,
            pady=2
        )
        add_btn.pack(side=tk.LEFT)
        
        # Effet de survol
        def on_enter(event):
            item_frame.configure(bg='#5d5d5d')
            info_frame.configure(bg='#5d5d5d')
            buttons_frame.configure(bg='#5d5d5d')
            thumbnail_label.configure(bg='#5d5d5d')
            title_label.configure(bg='#5d5d5d')
            info_label.configure(bg='#5d5d5d')
        
        def on_leave(event):
            item_frame.configure(bg='#4d4d4d')
            info_frame.configure(bg='#4d4d4d')
            buttons_frame.configure(bg='#4d4d4d')
            thumbnail_label.configure(bg='#4d4d4d')
            title_label.configure(bg='#4d4d4d')
            info_label.configure(bg='#4d4d4d')
        
        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)
        for widget in [info_frame, buttons_frame, thumbnail_label, title_label, info_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def _download_video(self, result, button):
        """Lance le téléchargement d'une vidéo"""
        if self.youtube_service.is_downloading(result['url']):
            return
        
        # Changer l'apparence du bouton
        button.configure(text="Téléchargement...", state='disabled', bg='#ff6666')
        
        # Lancer le téléchargement
        self.youtube_service.download_audio(result['url'], result['title'])
    
    def _add_to_playlist(self, result):
        """Ajoute une vidéo à la playlist (après téléchargement)"""
        # Pour l'instant, on lance juste le téléchargement
        # Dans une version plus avancée, on pourrait demander à l'utilisateur
        # quelle playlist utiliser
        self.youtube_service.download_audio(result['url'], result['title'])
    
    def _on_download_progress(self, progress_data, url, title):
        """Appelé pendant le téléchargement"""
        # Mettre à jour l'interface si nécessaire
        pass
    
    def _on_download_complete(self, filepath, url, title):
        """Appelé quand un téléchargement est terminé"""
        # Ajouter à la playlist principale
        if filepath:
            self.playlist_manager.add_to_playlist("Main Playlist", filepath)
        
        # Mettre à jour l'interface
        self._update_download_button_status(url, "Téléchargé", '#4a8fe7')
    
    def _on_download_error(self, error, url, title):
        """Appelé en cas d'erreur de téléchargement"""
        self._update_download_button_status(url, "Erreur", '#ff4444')
    
    def _update_download_button_status(self, url, text, color):
        """Met à jour le statut d'un bouton de téléchargement"""
        # Trouver et mettre à jour le bouton correspondant
        # Cette implémentation est simplifiée
        pass
    
    def get_frame(self):
        """Retourne le frame de l'onglet"""
        return self.frame