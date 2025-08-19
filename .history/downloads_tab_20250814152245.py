# Import centralisé depuis __init__.py
from __init__ import *
import math

class DownloadItem:
    """Représente un élément de téléchargement"""
    def __init__(self, url, title, status="En attente"):
        self.url = url
        self.title = title
        self.progress = 0.0
        self.status = status
        self.completed = False
        self.error = False
        self.widget_frame = None
        self.progress_overlay = None

class DownloadManager:
    def __init__(self):
        self.download_queue = []  # Liste ordonnée des téléchargements
        self.current_download_index = -1  # Index du téléchargement en cours (-1 si aucun)
        self.download_widgets = {}  # {url: widget_data}
        
    def add_download(self, url, title):
        """Ajoute un téléchargement à la queue"""
        # Vérifier si l'URL n'est pas déjà dans la queue
        for item in self.download_queue:
            if item.url == url:
                return False
        
        download_item = DownloadItem(url, title)
        self.download_queue.append(download_item)
        return True
        
    def start_next_download(self):
        """Démarre le prochain téléchargement en attente"""
        if self.current_download_index >= 0:
            return  # Un téléchargement est déjà en cours
            
        # Trouver le prochain téléchargement en attente
        for i, item in enumerate(self.download_queue):
            if not item.completed and not item.error:
                self.current_download_index = i
                item.status = "Téléchargement..."
                return item
        
        return None
        
    def update_progress(self, url, progress, status=None):
        """Met à jour la progression d'un téléchargement"""
        for item in self.download_queue:
            if item.url == url:
                item.progress = progress
                if status:
                    item.status = status
                if progress >= 100:
                    item.completed = True
                    item.status = "Terminé"
                    # Libérer le slot de téléchargement en cours
                    if self.current_download_index >= 0:
                        self.current_download_index = -1
                return item
        return None
        
    def mark_error(self, url, error_message="Erreur"):
        """Marque un téléchargement comme ayant échoué"""
        for item in self.download_queue:
            if item.url == url:
                item.error = True
                item.status = error_message
                # Libérer le slot de téléchargement en cours
                if self.current_download_index >= 0:
                    self.current_download_index = -1
                return item
        return None
        
    def remove_completed(self):
        """Supprime les téléchargements terminés avec succès"""
        self.download_queue = [item for item in self.download_queue if not item.completed]
        # Réajuster l'index du téléchargement en cours
        if self.current_download_index >= len(self.download_queue):
            self.current_download_index = -1
            
    def get_current_download(self):
        """Retourne le téléchargement en cours"""
        if 0 <= self.current_download_index < len(self.download_queue):
            return self.download_queue[self.current_download_index]
        return None

def setup_downloads_tab(self):
    """Configure l'onglet de téléchargement"""
    # Créer l'onglet
    self.downloads_tab = ttk.Frame(self.notebook)
    self.notebook.add(self.downloads_tab, text="Téléchargements")
    
    # Initialiser le gestionnaire de téléchargements
    if not hasattr(self, 'download_manager'):
        self.download_manager = DownloadManager()
    
    # Frame principal
    main_frame = tk.Frame(self.downloads_tab, bg='#2d2d2d')
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Frame pour le header avec bouton find
    header_frame = tk.Frame(main_frame, bg='#2d2d2d')
    header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
    
    # Titre
    title_label = tk.Label(
        header_frame,
        text="Téléchargements",
        font=("Arial", 16, "bold"),
        bg='#2d2d2d',
        fg='white'
    )
    title_label.pack(side=tk.LEFT)
    
    # Bouton find pour aller au téléchargement en cours
    self.downloads_find_btn = tk.Button(
        header_frame,
        image=self.icons["find"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=4,
        pady=4,
        width=20,
        height=20,
        takefocus=0,
        command=self.scroll_to_current_download
    )
    self.downloads_find_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    # Frame pour la liste des téléchargements avec scrollbar
    list_frame = tk.Frame(main_frame, bg='#2d2d2d')
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
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

def create_download_item_widget(self, download_item):
    """Crée un widget d'élément de téléchargement dans le style des musiques téléchargées"""
    
    # Déterminer la couleur de fond selon l'état
    if download_item.completed:
        bg_color = '#3a4a3a'  # Vert pâle pour terminé
    elif download_item.error:
        bg_color = '#4a3a3a'  # Rouge pâle pour erreur
    elif download_item == self.download_manager.get_current_download():
        bg_color = COLOR_BACKGROUND_HIGHLIGHT  # Couleur normale pour en cours
    else:
        bg_color = COLOR_BACKGROUND  # Couleur normale pour en attente
    
    # Frame principal - même style que les résultats de bibliothèque
    item_frame = tk.Frame(
        self.downloads_scrollable_frame,
        bg=bg_color,
        relief='flat',
        bd=1,
        highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
        highlightthickness=1
    )
    item_frame.pack(fill="x", padx=CARD_FRAME_PADX, pady=CARD_FRAME_PADY)
    
    # Stocker la référence
    download_item.widget_frame = item_frame
    
    # Configuration de la grille (même que library_tab)
    item_frame.columnconfigure(0, minsize=4, weight=0)   # Indicateur de statut
    item_frame.columnconfigure(1, minsize=80, weight=0)  # Miniature
    item_frame.columnconfigure(2, weight=1)              # Texte
    item_frame.columnconfigure(3, minsize=60, weight=0)  # Progression
    item_frame.columnconfigure(4, minsize=40, weight=0)  # Bouton annuler
    item_frame.rowconfigure(0, minsize=50, weight=0)
    
    # 1. Indicateur de statut (trait vertical coloré)
    status_color = '#4CAF50' if download_item.completed else '#f44336' if download_item.error else '#2196F3'
    status_indicator = tk.Frame(item_frame, bg=status_color, width=3)
    status_indicator.grid(row=0, column=0, sticky='ns', padx=(2, 2), pady=2)
    status_indicator.grid_propagate(False)
    
    # 2. Miniature placeholder (même style que library_tab)
    thumbnail_label = tk.Label(
        item_frame,
        bg=bg_color,
        width=10,
        height=3,
        anchor='center',
        text="⬇" if not download_item.completed else "✓",
        fg='white',
        font=('TkDefaultFont', 12)
    )
    thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(5, 4), pady=5)
    thumbnail_label.grid_propagate(False)
    
    # 3. Frame pour le texte (titre + statut)
    text_frame = tk.Frame(item_frame, bg=bg_color)
    text_frame.grid(row=0, column=2, sticky='nsew', padx=(0, 2), pady=4)
    text_frame.columnconfigure(0, weight=1)
    
    # Titre (tronqué si nécessaire)
    max_title_length = 50
    display_title = download_item.title[:max_title_length] + "..." if len(download_item.title) > max_title_length else download_item.title
    
    title_label = tk.Label(
        text_frame,
        text=display_title,
        bg=bg_color,
        fg='white',
        font=('TkDefaultFont', 9, 'bold'),
        anchor='nw',
        justify='left'
    )
    title_label.grid(row=0, column=0, sticky='ew', pady=(2, 0))
    
    # Statut
    status_label = tk.Label(
        text_frame,
        text=download_item.status,
        bg=bg_color,
        fg='#cccccc',
        font=('TkDefaultFont', 8),
        anchor='nw',
        justify='left'
    )
    status_label.grid(row=1, column=0, sticky='ew', pady=(0, 2))
    
    # 4. Progression (pourcentage)
    progress_label = tk.Label(
        item_frame,
        text=f"{download_item.progress:.0f}%",
        bg=bg_color,
        fg='#cccccc',
        font=('TkDefaultFont', 8),
        anchor='center'
    )
    progress_label.grid(row=0, column=3, sticky='ns', padx=(0, 2), pady=8)
    
    # 5. Bouton annuler/supprimer
    if download_item.completed or download_item.error:
        btn_text = "✕"
        btn_command = lambda: self.remove_download_item(download_item)
        btn_bg = '#666666'
    else:
        btn_text = "⏹"
        btn_command = lambda: self.cancel_download_item(download_item)
        btn_bg = '#d32f2f'
    
    action_btn = tk.Button(
        item_frame,
        text=btn_text,
        command=btn_command,
        bg=btn_bg,
        fg='white',
        activebackground='#ff6666',
        relief='flat',
        bd=0,
        width=2,
        height=1,
        font=('TkDefaultFont', 8),
        takefocus=0
    )
    action_btn.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
    
    # Créer l'overlay de progression (barre verte)
    progress_overlay = tk.Frame(item_frame, bg='#4CAF50')
    progress_overlay.place(x=0, y=0, relheight=1.0, width=0)  # Largeur initiale 0
    download_item.progress_overlay = progress_overlay
    
    # Mettre à jour la barre de progression
    self.update_progress_overlay(download_item)
    
    # Stocker les références pour les mises à jour
    self.download_manager.download_widgets[download_item.url] = {
        'frame': item_frame,
        'title_label': title_label,
        'status_label': status_label,
        'progress_label': progress_label,
        'action_btn': action_btn,
        'progress_overlay': progress_overlay,
        'thumbnail_label': thumbnail_label,
        'status_indicator': status_indicator
    }
    
    return item_frame

def update_progress_overlay(self, download_item):
    """Met à jour la barre de progression verte"""
    if download_item.progress_overlay and download_item.widget_frame:
        try:
            # Forcer la mise à jour de la géométrie
            download_item.widget_frame.update_idletasks()
            
            # Calculer la largeur de la barre de progression
            frame_width = download_item.widget_frame.winfo_width()
            if frame_width <= 1:  # Si la frame n'est pas encore affichée
                # Programmer une mise à jour différée
                self.root.after(100, lambda: self.update_progress_overlay(download_item))
                return
            
            progress_width = int((download_item.progress / 100.0) * frame_width)
            
            # Mettre à jour la largeur de l'overlay
            download_item.progress_overlay.place(width=progress_width)
            
            # Ajuster la couleur selon l'état
            if download_item.completed:
                download_item.progress_overlay.configure(bg='#4CAF50')  # Vert pour terminé
            elif download_item.error:
                download_item.progress_overlay.configure(bg='#f44336')  # Rouge pour erreur
            else:
                download_item.progress_overlay.configure(bg='#2196F3')  # Bleu pour en cours
                
        except tk.TclError:
            # Widget détruit, ignorer
            pass

def update_downloads_display(self):
    """Met à jour l'affichage des téléchargements"""
    # Cacher/afficher le message "aucun téléchargement"
    if not self.download_manager.download_queue:
        self.no_downloads_label.pack(pady=50)
        # Supprimer tous les widgets de téléchargement
        for widgets in self.download_manager.download_widgets.values():
            if widgets['frame'].winfo_exists():
                widgets['frame'].destroy()
        self.download_manager.download_widgets.clear()
    else:
        self.no_downloads_label.pack_forget()
        
        # Supprimer tous les widgets existants
        for child in self.downloads_scrollable_frame.winfo_children():
            if child != self.no_downloads_label:
                child.destroy()
        self.download_manager.download_widgets.clear()
        
        # Recréer tous les widgets dans l'ordre de la queue
        for download_item in self.download_manager.download_queue:
            self.create_download_item_widget(download_item)
    
    # Mettre à jour la scrollbar
    self.downloads_scrollable_frame.update_idletasks()
    self.downloads_canvas.configure(scrollregion=self.downloads_canvas.bbox("all"))

def update_download_progress(self, url, progress, status=None):
    """Met à jour la progression d'un téléchargement"""
    download_item = self.download_manager.update_progress(url, progress, status)
    if download_item and download_item.url in self.download_manager.download_widgets:
        widgets = self.download_manager.download_widgets[download_item.url]
        
        # Mettre à jour les textes
        widgets['progress_label'].config(text=f"{download_item.progress:.0f}%")
        if status:
            widgets['status_label'].config(text=status)
        
        # Mettre à jour la barre de progression
        self.update_progress_overlay(download_item)
        
        # Mettre à jour l'apparence si terminé
        if download_item.completed:
            self.update_download_item_appearance(download_item)
    
    # Si terminé avec succès, programmer la suppression après 5 secondes
    if progress >= 100 and not (status and "erreur" in status.lower()):
        self.root.after(5000, lambda: self.remove_completed_download(url))

def update_download_item_appearance(self, download_item):
    """Met à jour l'apparence d'un élément de téléchargement selon son état"""
    if download_item.url not in self.download_manager.download_widgets:
        return
        
    widgets = self.download_manager.download_widgets[download_item.url]
    
    # Déterminer la nouvelle couleur de fond
    if download_item.completed:
        bg_color = '#3a4a3a'  # Vert pâle
        status_color = '#4CAF50'
        thumbnail_text = "✓"
    elif download_item.error:
        bg_color = '#4a3a3a'  # Rouge pâle
        status_color = '#f44336'
        thumbnail_text = "✗"
    else:
        bg_color = COLOR_BACKGROUND
        status_color = '#2196F3'
        thumbnail_text = "⬇"
    
    # Mettre à jour tous les widgets
    try:
        widgets['frame'].configure(bg=bg_color)
        widgets['status_indicator'].configure(bg=status_color)
        widgets['thumbnail_label'].configure(bg=bg_color, text=thumbnail_text)
        
        # Mettre à jour le bouton d'action
        if download_item.completed or download_item.error:
            widgets['action_btn'].configure(text="✕", bg='#666666', 
                                          command=lambda: self.remove_download_item(download_item))
        
        # Mettre à jour les labels de texte
        for child in widgets['frame'].winfo_children():
            if isinstance(child, tk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        subchild.configure(bg=bg_color)
            elif isinstance(child, tk.Label):
                child.configure(bg=bg_color)
                
    except tk.TclError:
        # Widget détruit, ignorer
        pass

def cancel_download_item(self, download_item):
    """Annule un téléchargement"""
    download_item.error = True
    download_item.status = "Annulé"
    download_item.progress = 0
    
    # Libérer le slot de téléchargement en cours
    if self.download_manager.current_download_index >= 0:
        current_item = self.download_manager.get_current_download()
        if current_item and current_item.url == download_item.url:
            self.download_manager.current_download_index = -1
    
    # Mettre à jour l'apparence
    self.update_download_item_appearance(download_item)
    
    # Programmer la suppression après 3 secondes
    self.root.after(3000, lambda: self.remove_download_item(download_item))

def remove_download_item(self, download_item):
    """Supprime un élément de téléchargement de la liste"""
    # Supprimer de la queue
    if download_item in self.download_manager.download_queue:
        index = self.download_manager.download_queue.index(download_item)
        self.download_manager.download_queue.remove(download_item)
        
        # Ajuster l'index du téléchargement en cours
        if self.download_manager.current_download_index > index:
            self.download_manager.current_download_index -= 1
        elif self.download_manager.current_download_index == index:
            self.download_manager.current_download_index = -1
    
    # Supprimer le widget
    if download_item.url in self.download_manager.download_widgets:
        widgets = self.download_manager.download_widgets[download_item.url]
        if widgets['frame'].winfo_exists():
            widgets['frame'].destroy()
        del self.download_manager.download_widgets[download_item.url]
    
    # Mettre à jour l'affichage
    self.update_downloads_display()

def remove_completed_download(self, url):
    """Supprime un téléchargement terminé"""
    for download_item in self.download_manager.download_queue:
        if download_item.url == url and download_item.completed:
            self.remove_download_item(download_item)
            break

def add_download_to_tab(self, url, title):
    """Ajoute un téléchargement à l'onglet"""
    if self.download_manager.add_download(url, title):
        self.update_downloads_display()
        return True
    return False

def scroll_to_current_download(self):
    """Scroll automatiquement vers le téléchargement en cours avec animation ease in out"""
    current_download = self.download_manager.get_current_download()
    if not current_download or not current_download.widget_frame:
        return
    
    try:
        # Calculer la position cible
        frame = current_download.widget_frame
        frame.update_idletasks()
        
        # Position de la frame dans le container
        frame_y = frame.winfo_y()
        container_height = self.downloads_scrollable_frame.winfo_height()
        canvas_height = self.downloads_canvas.winfo_height()
        
        if container_height <= canvas_height:
            return  # Pas besoin de scroller
        
        # Position cible (centrer la frame dans le canvas)
        target_y = frame_y - (canvas_height / 2) + (frame.winfo_height() / 2)
        target_fraction = max(0, min(1, target_y / (container_height - canvas_height)))
        
        # Position actuelle
        current_fraction = self.downloads_canvas.canvasy(0) / (container_height - canvas_height) if container_height > canvas_height else 0
        
        # Animation ease in out
        self.animate_scroll_to_position(current_fraction, target_fraction)
        
    except tk.TclError:
        # Widget détruit, ignorer
        pass

def animate_scroll_to_position(self, start_pos, end_pos, duration=500, steps=30):
    """Anime le scroll avec ease in out"""
    if abs(end_pos - start_pos) < 0.01:
        return  # Déjà à la bonne position
    
    def ease_in_out(t):
        """Fonction d'easing ease in out"""
        if t < 0.5:
            return 2 * t * t
        else:
            return -1 + (4 - 2 * t) * t
    
    step_duration = duration // steps
    
    def animate_step(step):
        if step > steps:
            return
        
        # Calculer la position avec easing
        t = step / steps
        eased_t = ease_in_out(t)
        current_pos = start_pos + (end_pos - start_pos) * eased_t
        
        try:
            self.downloads_canvas.yview_moveto(current_pos)
            self.root.after(step_duration, lambda: animate_step(step + 1))
        except tk.TclError:
            # Widget détruit, arrêter l'animation
            pass
    
    animate_step(0)

# Fonctions de simulation pour les tests
def simulate_download_progress(self, url):
    """Simule la progression d'un téléchargement (pour test)"""
    for download_item in self.download_manager.download_queue:
        if download_item.url == url and not download_item.completed and not download_item.error:
            current_progress = download_item.progress
            if current_progress < 100:
                new_progress = min(100, current_progress + 5)
                status = "Téléchargement..." if new_progress < 100 else "Terminé"
                self.update_download_progress(url, new_progress, status)
                
                if new_progress < 100:
                    # Continuer la simulation
                    self.root.after(200, lambda: self.simulate_download_progress(url))
            break

def add_test_downloads(self):
    """Ajoute des téléchargements de test"""
    test_downloads = [
        ("https://youtube.com/watch?v=test1", "Test Song 1 - Artist Name"),
        ("https://youtube.com/watch?v=test2", "Another Great Song - Different Artist"),
        ("https://youtube.com/watch?v=test3", "Long Title That Should Be Truncated Because It's Too Long"),
    ]
    
    for url, title in test_downloads:
        self.add_download_to_tab(url, title)
    
    # Simuler le téléchargement du premier
    if test_downloads:
        self.download_manager.start_next_download()
        self.simulate_download_progress(test_downloads[0][0])