"""
Contrôles d'interface pour Pipi Player
Extrait de main.py pour améliorer la lisibilité
"""

def setup_controls(self):
    """Configure les contrôles de lecture"""
    from tkinter import ttk
    import tkinter as tk
    
    # Control Frame (should be at the bottom, no expand)
    control_frame = ttk.Frame(self.main_frame)
    control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
    
    # Waveform Frame (above song info)
    waveform_frame = ttk.Frame(control_frame)
    waveform_frame.pack(fill=tk.X)
    
    # Song Info
    self.song_label = ttk.Label(
        control_frame, text="No track selected", 
        font=('Helvetica', 12, 'bold')
    )
    self.song_label.pack(pady=10)
    
    # Progress Bar
    self.progress = ttk.Scale(
        control_frame, from_=0, to=100, orient=tk.HORIZONTAL,
        command=self.set_position
    )
    self.progress.pack(fill=tk.X, pady=5)
    
    # Bind progress bar events
    self.progress.bind("<Button-1>", self.on_progress_press)
    self.progress.bind("<ButtonRelease-1>", self.on_progress_release)
    self.progress.bind("<B1-Motion>", self.on_progress_drag)
    
    # Time Labels
    time_frame = ttk.Frame(control_frame)
    time_frame.pack(fill=tk.X)
    
    self.current_time_label = ttk.Label(time_frame, text="00:00")
    self.current_time_label.pack(side=tk.LEFT)
    
    self.song_length_label = ttk.Label(time_frame, text="00:00")
    self.song_length_label.pack(side=tk.RIGHT)
    
    # Conteneur horizontal pour volume offset + boutons + volume
    buttons_volume_frame = ttk.Frame(control_frame)
    buttons_volume_frame.pack(fill=tk.X, pady=20)

    # Frame volume offset à gauche (largeur fixe)
    volume_offset_frame = ttk.Frame(buttons_volume_frame, width=180)
    volume_offset_frame.grid(row=0, column=0, sticky="w")
    volume_offset_frame.grid_propagate(False)

    ttk.Label(volume_offset_frame, text="Volume Offset").pack()
    self.volume_offset_slider = ttk.Scale(
        volume_offset_frame, from_=-50, to=50, 
        command=self.set_volume_offset, value=0,
        orient='horizontal',
        length=150
    )
    self.volume_offset_slider.pack(padx=15)
    
    # Ajouter le clic droit pour remettre à 0
    self.volume_offset_slider.bind("<Button-3>", self._reset_volume_offset)

    # Frame boutons (centré)
    button_frame = ttk.Frame(buttons_volume_frame)
    button_frame.grid(row=0, column=1, padx=20)

    # Créer les boutons de contrôle
    self._create_control_buttons(button_frame)
    
    # Frame volume à droite (largeur fixe)
    volume_frame = ttk.Frame(buttons_volume_frame, width=180)
    volume_frame.grid(row=0, column=2, sticky="e")
    volume_frame.grid_propagate(False)

    ttk.Label(volume_frame, text="Volume").pack()
    self.volume_slider = ttk.Scale(
        volume_frame, from_=0, to=1, 
        command=self.set_volume, value=self.volume,
        orient='horizontal',
        length=150
    )
    self.volume_slider.pack(padx=15)
    
    # Status bar
    self.status_bar = ttk.Label(control_frame, text="Ready")
    self.status_bar.pack(pady=5)

def _create_control_buttons(self, parent):
    """Crée les boutons de contrôle"""
    import tkinter as tk
    
    # Bouton Random
    self.random_button = tk.Button(
        parent, 
        text="🔀" if not hasattr(self, 'icons') or "shuffle" not in self.icons else "",
        image=self.icons.get("shuffle", None) if hasattr(self, 'icons') else None,
        bg="#3d3d3d" if not getattr(self, 'random_mode', False) else "#4a8fe7",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        width=40,
        height=40,
        command=self.toggle_random_mode
    )
    self.random_button.grid(row=0, column=0, padx=3)
    
    # Bouton Loop
    self.loop_button = tk.Button(
        parent, 
        text="🔁" if not hasattr(self, 'icons') or "loop" not in self.icons else "",
        image=self.icons.get("loop", None) if hasattr(self, 'icons') else None,
        bg="#3d3d3d" if getattr(self, 'loop_mode', 0) == 0 else "#4a8fe7",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        width=40,
        height=40,
        command=self.toggle_loop_mode
    )
    self.loop_button.grid(row=0, column=1, padx=3)
    
    # Bouton Previous
    prev_button = tk.Button(
        parent,
        text="⏮" if not hasattr(self, 'icons') or "prev" not in self.icons else "",
        image=self.icons.get("prev", None) if hasattr(self, 'icons') else None,
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        width=50,
        height=50,
        command=self.prev_track
    )
    prev_button.grid(row=0, column=2, padx=5)
    
    # Bouton Play/Pause
    self.play_button = tk.Button(
        parent,
        text="▶" if not hasattr(self, 'icons') or "play" not in self.icons else "",
        image=self.icons.get("play", None) if hasattr(self, 'icons') else None,
        bg="#4a8fe7",
        fg="white",
        activebackground="#5a9fd8",
        relief="flat",
        bd=0,
        width=60,
        height=60,
        command=self.play_pause
    )
    self.play_button.grid(row=0, column=3, padx=5)
    
    # Bouton Next
    next_button = tk.Button(
        parent,
        text="⏭" if not hasattr(self, 'icons') or "next" not in self.icons else "",
        image=self.icons.get("next", None) if hasattr(self, 'icons') else None,
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        width=50,
        height=50,
        command=self.next_track
    )
    next_button.grid(row=0, column=4, padx=5)

def on_progress_press(self, event):
    """Début du drag de la barre de progression"""
    self.user_dragging = True

def on_progress_drag(self, event):
    """Pendant le drag de la barre de progression"""
    if self.user_dragging and hasattr(self, 'progress'):
        # Optionnel: mettre à jour la position en temps réel
        pass

def on_progress_release(self, event):
    """Fin du drag de la barre de progression"""
    self.user_dragging = False
    if hasattr(self, 'progress'):
        position = self.progress.get()
        self.set_position(position)

def _reset_volume_offset(self, event):
    """Remet l'offset de volume à 0"""
    if hasattr(self, 'volume_offset_slider'):
        self.volume_offset_slider.set(0)
        self.set_volume_offset(0)

def setup_search_tab(self):
    """Configure l'onglet de recherche YouTube"""
    from tkinter import ttk
    import tkinter as tk
    
    # Frame principal de recherche
    search_main_frame = ttk.Frame(self.search_tab)
    search_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Frame de recherche en haut
    search_input_frame = ttk.Frame(search_main_frame)
    search_input_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Champ de recherche
    ttk.Label(search_input_frame, text="Recherche YouTube:").pack(anchor=tk.W)
    
    self.search_entry = tk.Entry(
        search_input_frame,
        font=('Helvetica', 12),
        bg='#3d3d3d',
        fg='white',
        insertbackground='white'
    )
    self.search_entry.pack(fill=tk.X, pady=5)
    self.search_entry.bind('<KeyRelease>', self._on_search_entry_change)
    
    # Boutons de recherche
    search_buttons_frame = ttk.Frame(search_input_frame)
    search_buttons_frame.pack(fill=tk.X, pady=5)
    
    search_button = tk.Button(
        search_buttons_frame,
        text="🔍 Rechercher",
        bg="#4a8fe7",
        fg="white",
        command=self._perform_search
    )
    search_button.pack(side=tk.LEFT, padx=(0, 5))
    
    clear_button = tk.Button(
        search_buttons_frame,
        text="🗑 Effacer",
        bg="#3d3d3d",
        fg="white",
        command=self._clear_search
    )
    clear_button.pack(side=tk.LEFT)
    
    # Frame pour les résultats avec scrollbar
    results_frame = ttk.Frame(search_main_frame)
    results_frame.pack(fill=tk.BOTH, expand=True)
    
    # Canvas et scrollbar pour les résultats
    self.youtube_canvas = tk.Canvas(
        results_frame,
        bg='#2d2d2d',
        highlightthickness=0
    )
    
    youtube_scrollbar = ttk.Scrollbar(
        results_frame,
        orient="vertical",
        command=self.youtube_canvas.yview
    )
    
    self.youtube_canvas.configure(yscrollcommand=youtube_scrollbar.set)
    
    # Pack canvas et scrollbar
    youtube_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.youtube_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Frame pour le contenu des résultats
    self.results_container = ttk.Frame(self.youtube_canvas)
    self.youtube_canvas.create_window((0, 0), window=self.results_container, anchor="nw")
    
    # Bind pour le redimensionnement
    self.results_container.bind('<Configure>', self._on_youtube_canvas_configure)
    self.youtube_canvas.bind('<MouseWheel>', self._on_youtube_scroll)
    
    # Message initial
    initial_label = ttk.Label(
        self.results_container,
        text="Entrez un terme de recherche pour trouver de la musique sur YouTube",
        font=('Helvetica', 10)
    )
    initial_label.pack(pady=20)

def setup_library_tab(self):
    """Configure l'onglet de bibliothèque"""
    from tkinter import ttk
    import tkinter as tk
    
    # Frame principal de la bibliothèque
    library_main_frame = ttk.Frame(self.library_tab)
    library_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Frame pour les onglets verticaux à gauche
    tabs_frame = ttk.Frame(library_main_frame, width=150)
    tabs_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    tabs_frame.pack_propagate(False)
    
    # Créer les onglets verticaux
    self._create_library_tabs(tabs_frame)
    
    # Frame pour le contenu à droite
    self.library_content_frame = ttk.Frame(library_main_frame)
    self.library_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Initialiser avec l'onglet téléchargées
    self.switch_library_tab("téléchargées")

def _create_library_tabs(self, parent):
    """Crée les onglets verticaux de la bibliothèque"""
    import tkinter as tk
    
    # Dictionnaire pour stocker les boutons
    self.library_tab_buttons = {}
    
    # Onglet "Téléchargées"
    downloads_count = self._count_downloaded_files()
    self.downloads_btn = tk.Button(
        parent,
        text=f"Téléchargées ({downloads_count})",
        command=lambda: self.switch_library_tab("téléchargées"),
        bg="#4a8fe7",
        fg="white",
        activebackground="#5a9fd8",
        relief="flat",
        bd=0,
        width=18,
        height=2
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
        width=18,
        height=2
    )
    playlists_btn.pack(fill=tk.X, pady=2)
    self.library_tab_buttons["playlists"] = playlists_btn

def switch_library_tab(self, tab_name):
    """Change d'onglet dans la bibliothèque"""
    # Mettre à jour l'apparence des boutons
    for name, button in self.library_tab_buttons.items():
        if name == tab_name:
            button.config(bg="#4a8fe7")
        else:
            button.config(bg="#3d3d3d")
    
    # Vider le contenu actuel
    for widget in self.library_content_frame.winfo_children():
        widget.destroy()
    
    # Afficher le contenu selon l'onglet
    if tab_name == "téléchargées":
        self._show_downloads_content()
    elif tab_name == "playlists":
        self._show_playlists_content()

def _show_downloads_content(self):
    """Affiche le contenu des téléchargements"""
    from tkinter import ttk
    import tkinter as tk
    
    # Titre
    title_label = ttk.Label(
        self.library_content_frame,
        text="Fichiers téléchargés",
        font=('Helvetica', 14, 'bold')
    )
    title_label.pack(pady=10)
    
    # Message temporaire
    temp_label = ttk.Label(
        self.library_content_frame,
        text="Fonctionnalité en cours d'implémentation...\nLes fichiers téléchargés apparaîtront ici."
    )
    temp_label.pack(pady=20)

def _show_playlists_content(self):
    """Affiche le contenu des playlists"""
    from tkinter import ttk
    import tkinter as tk
    
    # Titre
    title_label = ttk.Label(
        self.library_content_frame,
        text="Mes Playlists",
        font=('Helvetica', 14, 'bold')
    )
    title_label.pack(pady=10)
    
    # Message temporaire
    temp_label = ttk.Label(
        self.library_content_frame,
        text="Fonctionnalité en cours d'implémentation...\nVos playlists apparaîtront ici."
    )
    temp_label.pack(pady=20)

# Méthodes de recherche (placeholders)
def _on_search_entry_change(self, event):
    """Gère les changements dans le champ de recherche"""
    pass

def _perform_search(self):
    """Lance une recherche YouTube"""
    query = getattr(self, 'search_entry', None)
    if query and hasattr(query, 'get'):
        search_text = query.get().strip()
        if search_text:
            print(f"Recherche: {search_text}")
            # TODO: Implémenter la recherche YouTube

def _clear_search(self):
    """Efface la recherche"""
    if hasattr(self, 'search_entry'):
        self.search_entry.delete(0, 'end')
    # TODO: Effacer les résultats

def _on_youtube_canvas_configure(self, event):
    """Gère le redimensionnement du canvas YouTube"""
    if hasattr(self, 'youtube_canvas'):
        self.youtube_canvas.configure(scrollregion=self.youtube_canvas.bbox("all"))

def _on_youtube_scroll(self, event):
    """Gère le défilement du canvas YouTube"""
    if hasattr(self, 'youtube_canvas'):
        self.youtube_canvas.yview_scroll(int(-1*(event.delta/120)), "units")