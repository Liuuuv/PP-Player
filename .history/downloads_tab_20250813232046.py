# Import centralisé depuis __init__.py
from __init__ import *

class DownloadManager:
    def __init__(self):
        self.active_downloads = {}  # {url: {'title': str, 'progress': float, 'status': str}}
        self.download_widgets = {}  # {url: widget_frame}
        
    def add_download(self, url, title):
        """Ajoute un téléchargement à la liste"""
        self.active_downloads[url] = {
            'title': title,
            'progress': 0.0,
            'status': 'En attente...'
        }
        
    def update_progress(self, url, progress, status=None):
        """Met à jour la progression d'un téléchargement"""
        if url in self.active_downloads:
            self.active_downloads[url]['progress'] = progress
            if status:
                self.active_downloads[url]['status'] = status
                
    def remove_download(self, url):
        """Supprime un téléchargement terminé"""
        if url in self.active_downloads:
            del self.active_downloads[url]
        if url in self.download_widgets:
            del self.download_widgets[url]

def setup_downloads_tab(self):
    """Configure l'onglet de téléchargement"""
    # Créer l'onglet
    self.downloads_tab = ttk.Frame(self.notebook)
    self.notebook.add(self.downloads_tab, text="Téléchargements")
    
    # Initialiser le gestionnaire de téléchargements
    if not hasattr(self, 'download_manager'):
        self.download_manager = DownloadManager()
    
    # Frame principal avec scrollbar
    main_frame = tk.Frame(self.downloads_tab, bg='#2d2d2d')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Titre
    title_label = tk.Label(
        main_frame,
        text="Téléchargements en cours",
        font=("Arial", 16, "bold"),
        bg='#2d2d2d',
        fg='white'
    )
    title_label.pack(pady=(0, 10))
    
    # Frame pour la liste des téléchargements avec scrollbar
    list_frame = tk.Frame(main_frame, bg='#2d2d2d')
    list_frame.pack(fill=tk.BOTH, expand=True)
    
    # Canvas et scrollbar pour la liste
    self.downloads_canvas = tk.Canvas(list_frame, bg='#2d2d2d', highlightthickness=0)
    downloads_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.downloads_canvas.yview)
    self.downloads_scrollable_frame = tk.Frame(self.downloads_canvas, bg='#2d2d2d')
    
    self.downloads_scrollable_frame.bind(
        "<Configure>",
        lambda e: self.downloads_canvas.configure(scrollregion=self.downloads_canvas.bbox("all"))
    )
    
    self.downloads_canvas.create_window((0, 0), window=self.downloads_scrollable_frame, anchor="nw")
    self.downloads_canvas.configure(yscrollcommand=downloads_scrollbar.set)
    
    self.downloads_canvas.pack(side="left", fill="both", expand=True)
    downloads_scrollbar.pack(side="right", fill="y")
    
    # Bind mousewheel
    def _on_downloads_mousewheel(event):
        self.downloads_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    self.downloads_canvas.bind("<MouseWheel>", _on_downloads_mousewheel)
    
    # Message quand aucun téléchargement
    self.no_downloads_label = tk.Label(
        self.downloads_scrollable_frame,
        text="Aucun téléchargement en cours",
        font=("Arial", 12),
        bg='#2d2d2d',
        fg='#888888'
    )
    self.no_downloads_label.pack(pady=50)
    
    # Mettre à jour l'affichage
    self.update_downloads_display()

def create_download_item(self, url, title, progress=0.0, status="En attente..."):
    """Crée un élément de téléchargement dans l'interface"""
    # Frame pour cet élément
    item_frame = tk.Frame(
        self.downloads_scrollable_frame,
        bg='#3d3d3d',
        relief='raised',
        bd=1
    )
    item_frame.pack(fill=tk.X, pady=2, padx=5)
    
    # Frame pour le contenu
    content_frame = tk.Frame(item_frame, bg='#3d3d3d')
    content_frame.pack(fill=tk.X, padx=10, pady=8)
    
    # Titre de la vidéo
    title_label = tk.Label(
        content_frame,
        text=title[:60] + "..." if len(title) > 60 else title,
        font=("Arial", 10, "bold"),
        bg='#3d3d3d',
        fg='white',
        anchor='w'
    )
    title_label.pack(fill=tk.X)
    
    # Frame pour la barre de progression et le statut
    progress_frame = tk.Frame(content_frame, bg='#3d3d3d')
    progress_frame.pack(fill=tk.X, pady=(5, 0))
    
    # Barre de progression
    progress_bar = ttk.Progressbar(
        progress_frame,
        mode='determinate',
        length=300,
        value=progress
    )
    progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Label de pourcentage
    percent_label = tk.Label(
        progress_frame,
        text=f"{progress:.1f}%",
        font=("Arial", 9),
        bg='#3d3d3d',
        fg='white',
        width=8
    )
    percent_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    # Statut
    status_label = tk.Label(
        content_frame,
        text=status,
        font=("Arial", 9),
        bg='#3d3d3d',
        fg='#cccccc',
        anchor='w'
    )
    status_label.pack(fill=tk.X, pady=(2, 0))
    
    # Bouton d'annulation
    cancel_btn = tk.Button(
        content_frame,
        text="Annuler",
        command=lambda: self.cancel_download(url),
        bg='#d32f2f',
        fg='white',
        font=("Arial", 8),
        relief='flat',
        padx=10,
        pady=2
    )
    cancel_btn.pack(anchor='e', pady=(5, 0))
    
    # Stocker les widgets pour mise à jour
    self.download_manager.download_widgets[url] = {
        'frame': item_frame,
        'progress_bar': progress_bar,
        'percent_label': percent_label,
        'status_label': status_label,
        'cancel_btn': cancel_btn
    }
    
    return item_frame

def update_downloads_display(self):
    """Met à jour l'affichage des téléchargements"""
    # Cacher/afficher le message "aucun téléchargement"
    if not self.download_manager.active_downloads:
        self.no_downloads_label.pack(pady=50)
        # Supprimer tous les widgets de téléchargement
        for widgets in self.download_manager.download_widgets.values():
            if widgets['frame'].winfo_exists():
                widgets['frame'].destroy()
        self.download_manager.download_widgets.clear()
    else:
        self.no_downloads_label.pack_forget()
        
        # Créer ou mettre à jour les éléments
        for url, download_info in self.download_manager.active_downloads.items():
            if url not in self.download_manager.download_widgets:
                # Créer un nouvel élément
                self.create_download_item(
                    url,
                    download_info['title'],
                    download_info['progress'],
                    download_info['status']
                )
            else:
                # Mettre à jour l'élément existant
                widgets = self.download_manager.download_widgets[url]
                if widgets['frame'].winfo_exists():
                    widgets['progress_bar']['value'] = download_info['progress']
                    widgets['percent_label'].config(text=f"{download_info['progress']:.1f}%")
                    widgets['status_label'].config(text=download_info['status'])

def cancel_download(self, url):
    """Annule un téléchargement"""
    if url in self.download_manager.active_downloads:
        # Marquer comme annulé
        self.download_manager.active_downloads[url]['status'] = "Annulé"
        self.download_manager.active_downloads[url]['progress'] = 0
        
        # Supprimer après 2 secondes
        self.root.after(2000, lambda: self.remove_completed_download(url))
        
        # Mettre à jour l'affichage
        self.update_downloads_display()

def remove_completed_download(self, url):
    """Supprime un téléchargement terminé de l'affichage"""
    if url in self.download_manager.download_widgets:
        widgets = self.download_manager.download_widgets[url]
        if widgets['frame'].winfo_exists():
            widgets['frame'].destroy()
    
    self.download_manager.remove_download(url)
    self.update_downloads_display()

def add_download_to_tab(self, url, title):
    """Ajoute un téléchargement à l'onglet"""
    self.download_manager.add_download(url, title)
    self.update_downloads_display()

def update_download_progress(self, url, progress, status=None):
    """Met à jour la progression d'un téléchargement"""
    self.download_manager.update_progress(url, progress, status)
    self.update_downloads_display()
    
    # Si terminé, supprimer après 3 secondes
    if progress >= 100:
        self.root.after(3000, lambda: self.remove_completed_download(url))

def simulate_download_progress(self, url):
    """Simule la progression d'un téléchargement (pour test)"""
    if url not in self.download_manager.active_downloads:
        return
        
    current_progress = self.download_manager.active_downloads[url]['progress']
    if current_progress < 100:
        new_progress = min(100, current_progress + 2)
        status = "Téléchargement..." if new_progress < 100 else "Terminé"
        self.update_download_progress(url, new_progress, status)
        
        if new_progress < 100:
            # Continuer la simulation
            self.root.after(100, lambda: self.simulate_download_progress(url))