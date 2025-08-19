# Import centralisé depuis __init__.py
from __init__ import *
import math
from io import BytesIO

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
                return None  # Déjà existant
        
        download_item = DownloadItem(url, title)
        self.download_queue.append(download_item)
        return download_item  # Retourner l'objet créé
        
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
    
    # Frame pour les boutons à droite
    buttons_frame = tk.Frame(header_frame, bg='#2d2d2d')
    buttons_frame.pack(side=tk.RIGHT)
    
    # Bouton pour nettoyer les téléchargements terminés
    clean_btn = tk.Button(
        buttons_frame,
        image=self.icons["clear_small"],
        bg="#d32f2f",
        fg="white",
        activebackground="#f44336",
        relief="flat",
        bd=0,
        width=20,
        height=20,
        takefocus=0,
        command=self.clean_completed_downloads,
        cursor='hand2'
    )
    clean_btn.pack(side=tk.RIGHT, padx=(5, 5))
    
    # Bouton pause pour mettre en pause/reprendre les téléchargements
    self.downloads_pause_btn = tk.Button(
        buttons_frame,
        image=self.icons["pause_small"],
        bg="#ff9800",
        fg="white",
        activebackground="#ffb74d",
        relief="flat",
        bd=0,
        width=20,
        height=20,
        takefocus=0,
        command=self.toggle_downloads_pause,
        cursor='hand2'
    )
    self.downloads_pause_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    # Variable pour l'état de pause
    self.downloads_paused = False
    
    # Bouton find pour aller au téléchargement en cours
    self.downloads_find_btn = tk.Button(
        buttons_frame,
        image=self.icons["find_small"],
        bg="#4a8fe7",
        fg="white",
        activebackground="#5a9fd8",
        relief="flat",
        bd=0,
        width=20,
        height=20,
        takefocus=0,
        command=self.scroll_to_current_download,
        cursor='hand2'
    )
    self.downloads_find_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
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
        bg_color = '#4a5a4a'  # Vert pâle pour terminé
    elif download_item.error:
        bg_color = COLOR_ERROR  # Orange-jaune pour erreur
    elif download_item == self.download_manager.get_current_download():
        bg_color = '#4a5a4a'  # Vert pour en cours
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
    
    # Configuration de la grille - plus d'espace horizontal et bouton delete plus large
    item_frame.columnconfigure(0, minsize=4, weight=0)   # Indicateur de statut
    item_frame.columnconfigure(1, minsize=100, weight=0) # Miniature plus large
    item_frame.columnconfigure(2, weight=1)              # Texte (prend l'espace restant)
    item_frame.columnconfigure(3, minsize=80, weight=0)  # Progression plus large
    item_frame.columnconfigure(4, minsize=50, weight=0)  # Bouton annuler plus large
    item_frame.rowconfigure(0, minsize=60, weight=0)     # Plus de hauteur
    
    # 1. Indicateur de statut (trait vertical coloré)
    status_color = '#4CAF50' if download_item.completed else '#f44336' if download_item.error else '#2196F3'
    status_indicator = tk.Frame(item_frame, bg=status_color, width=3)
    status_indicator.grid(row=0, column=0, sticky='ns', padx=(2, 2), pady=2)
    status_indicator.grid_propagate(False)
    
    # 2. Miniature de la vidéo - plus grande et mieux adaptée
    thumbnail_label = tk.Label(
        item_frame,
        bg=bg_color,
        width=12,
        height=4,
        anchor='center',
        text="⬇" if not download_item.completed else "✓",
        fg='white',
        font=('TkDefaultFont', 14)
    )
    thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(8, 8), pady=8)
    thumbnail_label.grid_propagate(False)
    
    # Charger la miniature de la vidéo si disponible
    if hasattr(download_item, 'video_data') and download_item.video_data:
        thumbnail_url = None
        if 'thumbnails' in download_item.video_data and download_item.video_data['thumbnails']:
            thumbnail_url = download_item.video_data['thumbnails'][-1]['url']
        elif 'thumbnail' in download_item.video_data:
            thumbnail_url = download_item.video_data['thumbnail']
        
        if thumbnail_url:
            self._load_download_thumbnail_from_url(thumbnail_label, thumbnail_url)
    elif hasattr(download_item, 'file_path') and download_item.file_path:
        # Pour les imports/fichiers locaux, charger la miniature locale
        self._load_download_thumbnail_from_file(thumbnail_label, download_item.file_path)
    
    # 3. Frame pour le texte (titre + statut)
    text_frame = tk.Frame(item_frame, bg=bg_color)
    text_frame.grid(row=0, column=2, sticky='nsew', padx=(0, 2), pady=4)
    text_frame.columnconfigure(0, weight=1)
    
    # Titre (tronqué si nécessaire) - plus de place pour le titre
    max_title_length = 60
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
        fg=COLOR_TEXT,
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
        fg=COLOR_TEXT,
        font=('TkDefaultFont', 8),
        anchor='center'
    )
    progress_label.grid(row=0, column=3, sticky='ns', padx=(0, 2), pady=8)
    
    # 5. Bouton supprimer avec icône delete.png - plus grand pour éviter le rognage
    delete_btn = tk.Button(
        item_frame,
        image=self.icons["delete"],
        command=lambda: self.handle_delete_download(download_item),
        bg=bg_color,
        activebackground='#ff6666',
        relief='flat',
        bd=0,
        width=30,
        height=30,
        takefocus=0,
        cursor='hand2'
    )
    delete_btn.grid(row=0, column=4, sticky='ns', padx=(5, 15), pady=15)
    
    # Créer l'overlay de progression (barre verte en arrière-plan)
    progress_overlay = tk.Frame(item_frame, bg='#1b5e20')  # Vert plus visible
    progress_overlay.place(x=0, y=0, relheight=1.0, width=0)  # Largeur initiale 0
    
    # Stocker les références pour les mises à jour
    self.download_manager.download_widgets[download_item.url] = {
        'frame': item_frame,
        'title_label': title_label,
        'status_label': status_label,
        'progress_label': progress_label,
        'delete_btn': delete_btn,
        'thumbnail_label': thumbnail_label,
        'status_indicator': status_indicator,
        'progress_overlay': progress_overlay
    }
    
    # Mettre à jour la barre de progression
    self.update_progress_overlay(download_item)
    
    # S'assurer que tous les widgets texte sont au-dessus de l'overlay
    for child in item_frame.winfo_children():
        if isinstance(child, (tk.Label, tk.Button)) and child != progress_overlay:
            child.lift()
    
    return item_frame

def handle_delete_download(self, download_item):
    """Gère la suppression/annulation d'un téléchargement selon son état"""
    current_download = self.download_manager.get_current_download()
    
    if download_item == current_download:
        # Téléchargement en cours - annuler
        self.cancel_active_download(download_item)
    elif download_item.completed or download_item.error:
        # Téléchargement terminé ou en erreur - supprimer de la liste
        self.remove_download_item(download_item)
    else:
        # Téléchargement en attente - supprimer de la queue
        self.remove_download_item(download_item)

def cancel_active_download(self, download_item):
    """Annule un téléchargement actif"""
    # Marquer comme annulé
    download_item.error = True
    download_item.status = "Annulé par l'utilisateur"
    
    # Libérer le slot de téléchargement en cours
    if self.download_manager.current_download_index >= 0:
        self.download_manager.current_download_index = -1
    
    # Supprimer de la liste des téléchargements en cours du système principal
    if hasattr(self, 'current_downloads') and download_item.url in self.current_downloads:
        self.current_downloads.remove(download_item.url)
    
    # Mettre à jour l'apparence
    self.update_download_item_appearance(download_item)
    
    # Programmer la suppression après 3 secondes
    self.root.after(3000, lambda: self.remove_download_item(download_item))

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
    
    # Les téléchargements terminés avec succès restent affichés
    # Ils ne sont plus supprimés automatiquement

def update_progress_overlay(self, download_item):
    """Met à jour la barre de progression verte en arrière-plan"""
    # Appeler directement la mise à jour
    self._update_progress_overlay_delayed(download_item)

def _update_progress_overlay_delayed(self, download_item):
    """Mise à jour différée de la barre de progression"""
    if download_item.url not in self.download_manager.download_widgets:
        return
        
    widgets = self.download_manager.download_widgets[download_item.url]
    progress_overlay = widgets.get('progress_overlay')
    
    if not progress_overlay:
        return
        
    try:
        # Calculer la largeur de progression avec une valeur correcte
        progress_value = max(0, min(100, download_item.progress))  # S'assurer que c'est entre 0 et 100
        
        if download_item.completed:
            relwidth = 1.0  # 100% si terminé
            bg_color = '#2e7d32'  # Vert plus visible pour terminé
        elif download_item.error:
            relwidth = 0.0  # 0% si erreur
            bg_color = COLOR_ERROR  # Rouge plus visible pour erreur
        else:
            relwidth = progress_value / 100.0  # Pourcentage en décimal
            bg_color = '#1b5e20'  # Vert plus visible pour en cours
        
        # Mettre à jour avec relwidth au lieu de width fixe
        progress_overlay.place(x=0, y=0, relheight=1.0, relwidth=relwidth)
        progress_overlay.configure(bg=bg_color)
        
        # Debug: afficher la progression
        # print(f"DEBUG: Progression {download_item.title[:20]}: {progress_value}% -> relwidth={relwidth}")
            
    except tk.TclError:
        # Widget détruit, ignorer
        pass

def update_download_item_appearance(self, download_item):
    """Met à jour l'apparence d'un élément de téléchargement selon son état"""
    if download_item.url not in self.download_manager.download_widgets:
        return
        
    widgets = self.download_manager.download_widgets[download_item.url]
    
    # Déterminer la nouvelle couleur de fond
    if download_item.completed:
        bg_color = '#4a5a4a'  # Vert pâle pour terminé
        status_color = '#4CAF50'
        thumbnail_text = "✓"
    elif download_item.error:
        bg_color = COLOR_ERROR  # Orange-jaune pour erreur
        status_color = '#f44336'
        thumbnail_text = "✗"
    else:
        bg_color = '#4a5a4a'  # Vert pour en cours
        status_color = '#2196F3'
        thumbnail_text = "⬇"
    
    # Mettre à jour tous les widgets
    try:
        widgets['frame'].configure(bg=bg_color)
        widgets['status_indicator'].configure(bg=status_color)
        # Ne changer le texte de la miniature que si aucune image n'est chargée
        if not hasattr(widgets['thumbnail_label'], 'image') or not widgets['thumbnail_label'].image:
            widgets['thumbnail_label'].configure(bg=bg_color, text=thumbnail_text)
        else:
            widgets['thumbnail_label'].configure(bg=bg_color)
        widgets['delete_btn'].configure(bg=bg_color)
        
        # Mettre à jour les labels de texte
        for child in widgets['frame'].winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=bg_color)
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        subchild.configure(bg=bg_color)
            elif isinstance(child, tk.Label):
                child.configure(bg=bg_color)
                
    except tk.TclError:
        # Widget détruit, ignorer
        pass



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

def clean_completed_downloads(self):
    """Supprime tous les téléchargements terminés avec succès"""
    completed_items = [item for item in self.download_manager.download_queue if item.completed]
    
    for item in completed_items:
        self.remove_download_item(item)
    
    # Mettre à jour l'affichage
    self.update_downloads_display()
    
    # Afficher un message de confirmation
    if completed_items:
        self.root.after(0, lambda: self.status_bar.config(
            text=f"{len(completed_items)} téléchargement(s) terminé(s) supprimé(s)"
        ))
    else:
        self.root.after(0, lambda: self.status_bar.config(
            text="Aucun téléchargement terminé à supprimer"
        ))

def _load_download_thumbnail_from_url(self, label, url):
    """Charge et affiche la miniature d'un téléchargement"""
    def load_thumbnail():
        try:
            import requests
            from io import BytesIO
            
            # Vérifier si le widget existe encore
            try:
                if not label.winfo_exists():
                    return
            except tk.TclError:
                return
            
            response = requests.get(url, timeout=5)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            
            # Redimensionner pour s'adapter au label
            img = img.resize((80, 45), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Mettre à jour dans le thread principal
            self.root.after(0, lambda: self._update_thumbnail_label(label, photo))
            
        except Exception as e:
            print(f"Erreur chargement miniature téléchargement: {e}")
    
    # Charger dans un thread séparé
    threading.Thread(target=load_thumbnail, daemon=True).start()

def _update_thumbnail_label(self, label, photo):
    """Met à jour le label de miniature dans le thread principal"""
    try:
        if label.winfo_exists():
            label.configure(image=photo, text="")
            label.image = photo  # Garder une référence
    except tk.TclError:
        pass

def _load_download_thumbnail_from_file(self, label, file_path):
    """Charge et affiche la miniature d'un fichier local"""
    def load_thumbnail():
        try:
            # Vérifier si le widget existe encore
            try:
                if not label.winfo_exists():
                    return
            except tk.TclError:
                return
            
            # Chercher une image associée (même nom mais extension image)
            base_name = os.path.splitext(file_path)[0]
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            
            thumbnail_path = None
            for ext in image_extensions:
                possible_path = base_name + ext
                if os.path.exists(possible_path):
                    thumbnail_path = possible_path
                    break
            
            if thumbnail_path:
                # Charger l'image locale
                img = Image.open(thumbnail_path)
                # Redimensionner pour s'adapter au label
                img = img.resize((100, 56), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Mettre à jour dans le thread principal
                self.root.after(0, lambda: self._update_thumbnail_label(label, photo))
            else:
                # Essayer de charger la miniature depuis les métadonnées MP3
                try:
                    from mutagen.mp3 import MP3
                    from mutagen.id3 import ID3NoHeaderError
                    
                    audio = MP3(file_path)
                    if audio.tags and 'APIC:' in audio.tags:
                        artwork = audio.tags['APIC:'].data
                        img = Image.open(BytesIO(artwork))
                        img = img.resize((100, 56), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        self.root.after(0, lambda: self._update_thumbnail_label(label, photo))
                except:
                    pass  # Pas de miniature disponible
                    
        except Exception as e:
            print(f"Erreur chargement miniature fichier local: {e}")
    
    # Charger dans un thread séparé
    threading.Thread(target=load_thumbnail, daemon=True).start()

def add_download_to_tab(self, url, title, video_data=None, file_path=None):
    """Ajoute un téléchargement à l'onglet"""
    download_item = self.download_manager.add_download(url, title)
    if download_item:
        # Ajouter les données vidéo si disponibles
        if video_data:
            download_item.video_data = video_data
        # Ajouter le chemin de fichier pour les imports
        if file_path:
            download_item.file_path = file_path
        self.update_downloads_display()
        return True
    return False

def add_file_import_to_tab(self, file_path, title=None):
    """Ajoute un import de fichier à l'onglet téléchargements"""
    if not title:
        title = os.path.basename(file_path)
    
    # Utiliser le chemin du fichier comme URL unique
    url = f"file://{file_path}"
    download_item = self.download_manager.add_download(url, title)
    if download_item:
        download_item.file_path = file_path
        download_item.progress = 100  # Import instantané
        download_item.completed = True
        download_item.status = "Importé"
        self.update_downloads_display()
        return True
    return False

def toggle_downloads_pause(self):
    """Bascule entre pause et reprise des téléchargements"""
    self.downloads_paused = not self.downloads_paused
    
    if self.downloads_paused:
        # Mettre en pause
        self.downloads_pause_btn.configure(
            image=self.icons["play_small"],
            bg="#4CAF50",
            activebackground="#66BB6A"
        )
        # Arrêter le téléchargement en cours si il y en a un
        current_download = self.download_manager.get_current_download()
        if current_download:
            current_download.status = "En pause"
            self.update_download_item_appearance(current_download)
        
        self.status_bar.config(text="Téléchargements mis en pause")
    else:
        # Reprendre
        self.downloads_pause_btn.configure(
            image=self.icons["pause_small"],
            bg="#ff9800",
            activebackground="#ffb74d"
        )
        # Reprendre le téléchargement
        current_download = self.download_manager.get_current_download()
        if current_download:
            current_download.status = "Téléchargement..."
            self.update_download_item_appearance(current_download)
        
        self.status_bar.config(text="Téléchargements repris")

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