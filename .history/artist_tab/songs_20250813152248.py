# Fonctions pour l'onglet Musiques des artistes

# Import centralisé depuis __init__.py
from __init__ import *

def _search_artist_videos_with_id(self):
    """Recherche les vidéos de l'artiste depuis l'onglet Vidéos de sa chaîne"""
    try:
        # Vérifier si la recherche a été annulée avant de commencer
        if self.artist_search_cancelled:
            return
        
        if not self.current_artist_channel_id:
            return
        
        # Vérifier le cache d'abord
        cache_key = self.current_artist_channel_id
        if cache_key in self.artist_cache and 'videos' in self.artist_cache[cache_key]:
            cached_videos = self.artist_cache[cache_key]['videos']
            self.root.after(0, lambda: self._display_artist_videos(cached_videos))
            return
        
        # Configuration pour extraire les vidéos de la chaîne (extract_flat=True pour avoir la durée)
        search_opts = {
            'extract_flat': True,  # Plus efficace et contient la durée
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True
        }
        
        with YoutubeDL(search_opts) as ydl:
            all_videos = []
            
            # Utiliser l'ID de chaîne trouvé
            base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
            videos_url = base_channel_url + '/videos'
            
            try:
                channel_info = ydl.extract_info(videos_url, download=False)
                if self.artist_search_cancelled:
                    return
                
                if channel_info and 'entries' in channel_info:
                    videos = list(channel_info['entries'])
                    # Filtrer et garder seulement les vidéos valides
                    videos = [v for v in videos if v and v.get('id')]
                    if videos:
                        all_videos.extend(videos[:30])  # Prendre les 30 premières
                    else:
                        pass
                else:
                    pass
            except Exception as e:
                self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des vidéos"))
                return
            
            if self.artist_search_cancelled:
                return
            
            # Si aucune vidéo trouvée, essayer d'autres méthodes
            if not all_videos:
                try:
                    # Essayer une recherche normale de l'artiste (méthode de fallback)
                    search_query = f"ytsearch30:{self.current_artist_name}"
                    search_results = ydl.extract_info(search_query, download=False)
                    
                    if self.artist_search_cancelled:
                        return
                    
                    if search_results and 'entries' in search_results:
                        all_videos = list(search_results['entries'])[:30]  # Garder 30 max
                    
                except Exception as e:
                    self.root.after(0, lambda: self.status_bar.config(text="Impossible de récupérer les vidéos"))
                    return
            
            # Mettre en cache
            if cache_key not in self.artist_cache:
                self.artist_cache[cache_key] = {}
            self.artist_cache[cache_key]['videos'] = all_videos
            
            # Afficher les résultats dans l'interface
            if not self.artist_search_cancelled:
                self.root.after(0, lambda: self._display_artist_videos(all_videos))
            
    except Exception as e:
        self.root.after(0, lambda: self._show_error_in_tabs(f"Impossible de charger les musiques: {str(e)}"))

def _display_artist_videos(self, videos):
    """Affiche les vidéos de l'artiste dans l'onglet Musiques avec scrolling amélioré"""
    # Vérifier si on est encore en mode artiste et que l'onglet musiques existe
    if not hasattr(self, 'musiques_frame') or not self.artist_mode:
        return  # L'utilisateur a annulé l'affichage artiste entre temps
        
    # Supprimer le message de chargement
    if hasattr(self, 'musiques_loading'):
        self.musiques_loading.destroy()
    
    # Remettre l'état du contenu de playlist à zéro car on affiche maintenant la liste normale
    self._reset_playlist_content_state()
    
    if not videos:
        no_results_label = tk.Label(
            self.musiques_frame,
            text="Aucune musique trouvée",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 10)
        )
        no_results_label.pack(expand=True)
        return
    
    # Créer un canvas scrollable dans l'onglet musiques
    canvas = tk.Canvas(self.musiques_frame, bg='#3d3d3d', highlightthickness=0)
    scrollbar = ttk.Scrollbar(self.musiques_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#3d3d3d')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Empaqueter le canvas et la scrollbar
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    # Afficher les vidéos dans le frame scrollable par petits lots (non-bloquant)
    self._display_results_in_batches(videos, scrollable_frame, "videos")
    
    # Scrolling amélioré - fonctionne peu importe où est la souris
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def bind_mousewheel_recursive(widget):
        """Bind mousewheel à un widget et tous ses enfants de manière récursive"""
        widget.bind("<MouseWheel>", _on_mousewheel)
        widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
        
        # Appliquer récursivement à tous les enfants
        try:
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        except:
            pass  # Si le widget n'a pas d'enfants ou n'existe plus
    
    # Appliquer le scrolling à tout le contenu de l'onglet
    canvas.bind("<MouseWheel>", _on_mousewheel)
    bind_mousewheel_recursive(self.musiques_frame)
    bind_mousewheel_recursive(scrollable_frame)
    
    # S'assurer que le focus peut être pris pour le scrolling
    self.musiques_frame.focus_set()

def _add_artist_result(self, video, index, container):
    """Ajoute un résultat vidéo dans un onglet artiste"""
    try:
        title = video.get('title', 'Sans titre')
        duration = video.get('duration', 0)
        url = video.get('url', '') or f"https://www.youtube.com/watch?v={video.get('id', '')}"
        
        # Formater la durée
        duration_str = "?"
        if duration and duration > 0:
            if duration < 3600:  # Moins d'une heure
                duration_str = f"{duration//60}:{duration%60:02d}"
            else:  # Plus d'une heure
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        
        # Frame principal avec le même style que les résultats de recherche
        result_frame = tk.Frame(
            container,
            bg='#4a4a4a',
            relief='flat',
            bd=1,
            highlightbackground='#555555',
            highlightthickness=1
        )
        result_frame.pack(fill="x", padx=3, pady=1)
        
        # Configuration de la grille
        result_frame.columnconfigure(0, minsize=60, weight=0)  # Miniature
        result_frame.columnconfigure(1, weight=1)              # Titre
        result_frame.columnconfigure(2, minsize=50, weight=0)  # Durée
        result_frame.rowconfigure(0, minsize=50, weight=0)
        
        # Miniature (placeholder)
        thumbnail_label = tk.Label(
            result_frame,
            bg='#4a4a4a',
            text="🎵",
            fg='white',
            anchor='center',
            font=('TkDefaultFont', 16)
        )
        thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=3)
        
        # Charger la miniature en arrière-plan
        self._load_artist_thumbnail(video, thumbnail_label)
        
        # Tronquer le titre intelligemment
        from tools import _truncate_text_for_display
        display_title = _truncate_text_for_display(self, title, max_width_pixels=300, font_size=8)
        
        # Titre
        title_label = tk.Label(
            result_frame,
            text=display_title,
            bg='#4a4a4a',
            fg='white',
            font=('TkDefaultFont', 8),
            anchor='w',
            justify='left'
        )
        title_label.grid(row=0, column=1, sticky='ew', padx=(5, 5), pady=3)
        
        # Durée
        duration_label = tk.Label(
            result_frame,
            text=duration_str,
            bg='#4a4a4a',
            fg='#aaaaaa',
            font=('TkDefaultFont', 7),
            anchor='center'
        )
        duration_label.grid(row=0, column=2, sticky='nsew', padx=(0, 5), pady=3)
        
        # Stocker les données
        result_frame.video_data = video
        result_frame.title_label = title_label
        result_frame.duration_label = duration_label
        result_frame.thumbnail_label = thumbnail_label
        
        # Événements de clic
        def on_click(event, frame=result_frame):
            # Simple clic - ajouter à la playlist principale
            try:
                video_url = frame.video_data.get('url', '') or f"https://www.youtube.com/watch?v={frame.video_data.get('id', '')}"
                if video_url:
                    import threading
                    threading.Thread(target=lambda: self.download_and_add_to_playlist(video_url), daemon=True).start()
            except Exception as e:
                print(f"Erreur lors du clic sur vidéo artiste: {e}")
        
        # Bindings pour le clic
        result_frame.bind("<Button-1>", on_click)
        title_label.bind("<Button-1>", on_click)
        thumbnail_label.bind("<Button-1>", on_click)
        duration_label.bind("<Button-1>", on_click)
        
        # Effet hover
        def on_enter(event):
            result_frame.configure(bg='#5a5a5a')
            title_label.configure(bg='#5a5a5a')
            thumbnail_label.configure(bg='#5a5a5a')
            duration_label.configure(bg='#5a5a5a')
        
        def on_leave(event):
            result_frame.configure(bg='#4a4a4a')
            title_label.configure(bg='#4a4a4a')
            thumbnail_label.configure(bg='#4a4a4a')
            duration_label.configure(bg='#4a4a4a')
        
        # Bindings pour l'effet hover
        for widget in [result_frame, title_label, thumbnail_label, duration_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        # Tooltip
        tooltip_text = f"Titre: {title}"
        if duration_str != "?":
            tooltip_text += f"\nDurée: {duration_str}"
        tooltip_text += "\nClic pour télécharger et ajouter à la playlist"
        
        create_tooltip(title_label, tooltip_text)
        
    except Exception as e:
        print(f"Erreur lors de l'ajout du résultat artiste: {e}")