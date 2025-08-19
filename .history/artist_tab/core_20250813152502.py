# Fonctions communes pour la gestion des pages d'artiste

# Import centralisé depuis __init__.py
from __init__ import *

# Importer les modules spécialisés
from artist_tab import songs, releases, playlists

def _add_artist_playlist_result(self, playlist, index, container, target_tab="sorties"):
        """Ajoute une playlist dans l'onglet Sorties ou Playlists avec double-clic pour voir le contenu"""
        try:
            title = playlist.get('title', 'Sans titre')
            # Essayer plusieurs champs pour le nombre de vidéos
            playlist_count = (playlist.get('playlist_count', 0) or 
                            playlist.get('video_count', 0) or
                            playlist.get('entry_count', 0) or
                            len(playlist.get('entries', [])))
            url = playlist.get('url', '')
            
            # Le nombre de vidéos n'est pas disponible avec extract_flat=True
            # On va le récupérer en arrière-plan
            
            # Frame principal - même style que les résultats normaux
            result_frame = tk.Frame(
                container,
                bg='#4a4a4a',
                relief='flat',
                bd=1,
                highlightbackground='#555555',
                highlightthickness=1
            )
            result_frame.pack(fill="x", padx=3, pady=1)  # Espacement réduit
            
            # Configuration de la grille (plus compact avec 2 lignes pour titre+count)
            result_frame.columnconfigure(0, minsize=60, weight=0)  # Miniature plus petite
            result_frame.columnconfigure(1, weight=1)              # Titre et nombre de vidéos
            result_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur augmentée pour 2 lignes
            
            # Miniature avec icône playlist (taille adaptative)
            thumbnail_label = tk.Label(
                result_frame,
                bg='#4a4a4a',
                text="📁",  # Icône dossier pour playlist
                fg='white',
                anchor='center',
                font=('TkDefaultFont', 12)
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=3)
            
            # Charger la miniature en arrière-plan
            self._load_artist_thumbnail(playlist, thumbnail_label)
            
            # Titre et nombre de vidéos (dans une frame verticale)
            text_frame = tk.Frame(result_frame, bg='#4a4a4a')
            text_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 5), pady=3)
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            text_frame.rowconfigure(1, weight=0)
            
            # Tronquer le titre intelligemment selon la largeur en pixels
            from tools import _truncate_text_for_display
            display_title = _truncate_text_for_display(self, title, max_width_pixels=200, font_size=8)
            
            title_label = tk.Label(
                text_frame,
                text=display_title,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 8),  # Police plus petite
                anchor='w',
                justify='left'
            )
            title_label.grid(row=0, column=0, sticky='ew', pady=(1, 0))
            
            # Nombre de musiques sous le titre (initialement "Chargement...")
            count_label = tk.Label(
                text_frame,
                text="Chargement...",
                bg='#4a4a4a',
                fg='#aaaaaa',
                font=('TkDefaultFont', 7),
                anchor='w',
                justify='left'
            )
            count_label.grid(row=1, column=0, sticky='ew', pady=(0, 1))
            
            # Charger le nombre de vidéos en arrière-plan (après création du label)
            self._load_playlist_count(playlist, count_label)
            
            # Stocker les données playlist
            result_frame.playlist_data = playlist
            result_frame.title_label = title_label
            result_frame.count_label = count_label
            result_frame.thumbnail_label = thumbnail_label
            
            # Événements de clic (double-clic pour voir le contenu de la playlist)
            def on_playlist_double_click(event, frame=result_frame):
                self._show_playlist_content(frame.playlist_data, target_tab)
            
            # Bindings pour le double-clic (inclure text_frame pour que le titre soit cliquable)
            result_frame.bind("<Double-Button-1>", on_playlist_double_click)
            title_label.bind("<Double-Button-1>", on_playlist_double_click)
            thumbnail_label.bind("<Double-Button-1>", on_playlist_double_click)
            count_label.bind("<Double-Button-1>", on_playlist_double_click)
            text_frame.bind("<Double-Button-1>", on_playlist_double_click)
            
            # Effet hover
            def on_enter(event):
                result_frame.configure(bg='#5a5a5a')
                title_label.configure(bg='#5a5a5a')
                thumbnail_label.configure(bg='#5a5a5a')
                count_label.configure(bg='#5a5a5a')
                text_frame.configure(bg='#5a5a5a')
            
            def on_leave(event):
                result_frame.configure(bg='#4a4a4a')
                title_label.configure(bg='#4a4a4a')
                thumbnail_label.configure(bg='#4a4a4a')
                count_label.configure(bg='#4a4a4a')
                text_frame.configure(bg='#4a4a4a')
            
            # Bindings pour l'effet hover (inclure text_frame)
            for widget in [result_frame, title_label, thumbnail_label, count_label, text_frame]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
            
            # Tooltip avec informations
            tooltip_text = f"Playlist: {title}\nDouble-clic pour voir le contenu"
            if playlist_count > 0:
                tooltip_text += f"\n{playlist_count} vidéos"
            create_tooltip(title_label, tooltip_text)
            
        except Exception as e:
            print(f"Erreur lors de l'ajout de la playlist artiste: {e}")

def _display_artist_interface(self, artist_name, video_data=None):
    """Affiche l'interface d'artiste de manière instantanée"""
    try:
        # Annuler toute recherche en cours pour éviter les conflits
        if hasattr(self, 'is_searching') and self.is_searching:
            self.search_cancelled = True
        
        # Réinitialiser le flag de recherche annulée pour l'artiste
        self.artist_search_cancelled = False
        
        # Masquer ou supprimer les éléments de recherche existants
        self._hide_search_elements()
        
        # Passer en mode artiste IMMÉDIATEMENT
        self.artist_mode = True
        self.current_artist_name = artist_name
        
        # Remettre l'état du contenu de playlist à zéro pour le nouvel artiste
        self._reset_playlist_content_state()
        
        # Essayer de récupérer l'URL de la chaîne depuis les métadonnées vidéo
        self.current_artist_channel_url = video_data.get('channel_url', '')
        if not self.current_artist_channel_url:
            # Fallback: construire l'URL de recherche avec plusieurs tentatives
            self.current_artist_channel_url = f"https://www.youtube.com/results?search_query={artist_name.replace(' ', '+')}"
        
        # Créer l'interface de manière synchrone (instantanée)
        self._create_artist_tabs()
        
        # Lancer la recherche asynchrone en arrière-plan
        self._search_artist_content_async()
        
    except Exception as e:
        print(f"Erreur lors de l'affichage de l'artiste {artist_name}: {e}")
        self.status_bar.config(text=f"Erreur lors du chargement de l'artiste: {e}")

def _hide_search_elements(self):
    """Masque les éléments de recherche pour faire place à l'interface d'artiste"""
    # Cacher le canvas et la scrollbar des résultats
    if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
        self.youtube_canvas.pack_forget()
    
    if hasattr(self, 'scrollbar') and self.scrollbar.winfo_exists():
        self.scrollbar.pack_forget()
    
    # Cacher aussi la frame thumbnail si elle est visible
    if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame.winfo_exists():
        self.thumbnail_frame.pack_forget()

def _create_artist_tabs(self):
    """Crée les onglets d'artiste de manière instantanée"""
    # Créer un frame container principal
    main_container = tk.Frame(self.youtube_results_frame, bg='#3d3d3d')
    main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Ajouter le bouton croix avec le même style que stats.png et output.png
    if hasattr(self, 'icons') and 'cross_small' in self.icons:
        self.artist_close_btn = tk.Button(
            main_container,
            image=self.icons['cross_small'],
            bg='#3d3d3d',
            activebackground='#ff6666',
            relief='raised',
            bd=1,
            width=20,
            height=20,
            command=self._return_to_search,
            cursor='hand2',
            takefocus=0
        )
    else:
        # Fallback si l'icône n'est pas disponible
        self.artist_close_btn = tk.Button(
            main_container,
            text="✕",
            bg='#3d3d3d',
            fg='white',
            activebackground='#ff6666',
            relief='raised',
            bd=1,
            font=('TkDefaultFont', 8, 'bold'),
            width=3,
            height=1,
            command=self._return_to_search,
            cursor='hand2',
            takefocus=0
        )
    
    # Tooltip pour le bouton croix
    try:
        from tooltip import create_tooltip
        create_tooltip(self.artist_close_btn, "Retourner à la recherche\nQuitte l'affichage de l'artiste et retourne aux résultats de recherche\n(Raccourci: Échap)")
    except:
        pass  # Si le tooltip ne peut pas être créé, continuer
    
    # Forcer la mise à jour pour s'assurer que le notebook est visible
    self.artist_notebook.update_idletasks() if hasattr(self, 'artist_notebook') else None
    
    # Créer le notebook
    self.artist_notebook = ttk.Notebook(main_container, takefocus=0)
    self.artist_notebook.pack(fill=tk.BOTH, expand=True)
    
    # Lier le changement d'onglet artiste pour gérer le bouton retour
    self.artist_notebook.bind("<<NotebookTabChanged>>", self.on_artist_tab_changed)
    
    # Positionner la croix au-dessus de tout (utiliser tkraise pour la mettre au premier plan)
    self.artist_close_btn.place(in_=main_container, relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)
    self.artist_close_btn.tkraise()  # Mettre le bouton au premier plan
    
    # Onglet Musiques (contient les vidéos de la chaîne par ordre de sortie)
    self.musiques_frame = tk.Frame(self.artist_notebook, bg='#3d3d3d')
    self.artist_notebook.add(self.musiques_frame, text="Musiques")
    
    # Onglet Sorties (contient les albums/singles pour les chaînes sans onglets)
    self.sorties_frame = tk.Frame(self.artist_notebook, bg='#3d3d3d')
    self.artist_notebook.add(self.sorties_frame, text="Sorties")
    
    # Onglet Playlists (contient toutes les playlists de la chaîne)
    self.playlists_frame = tk.Frame(self.artist_notebook, bg='#3d3d3d')
    self.artist_notebook.add(self.playlists_frame, text="Playlists")
    
    # Messages de chargement simples
    self.musiques_loading = tk.Label(
        self.musiques_frame,
        text="En attente...",
        bg='#3d3d3d',
        fg='#cccccc',
        font=('TkDefaultFont', 10)
    )
    self.musiques_loading.pack(expand=True)
    
    self.sorties_loading = tk.Label(
        self.sorties_frame,
        text="En attente...",
        bg='#3d3d3d',
        fg='#cccccc',
        font=('TkDefaultFont', 10)
    )
    self.sorties_loading.pack(expand=True)
    
    self.playlists_loading = tk.Label(
        self.playlists_frame,
        text="En attente...",
        bg='#3d3d3d',
        fg='#cccccc',
        font=('TkDefaultFont', 10)
    )
    self.playlists_loading.pack(expand=True)

def _search_artist_content_async(self):
    """Version asynchrone et non-bloquante de la recherche d'artiste"""
    self.status_bar.config(text=f"Recherche de l'ID de la chaîne de {self.current_artist_name}...")
    
    # Étape 1 : Trouver l'ID de la chaîne en arrière-plan
    def find_channel_id_bg():
        try:
            if self.artist_search_cancelled:
                return
                
            # Trouver l'ID de la chaîne
            channel_id = self._find_artist_channel_id()
            if self.artist_search_cancelled:
                return
                
            if channel_id:
                self.current_artist_channel_id = channel_id
                # Une fois l'ID trouvé, lancer les 3 recherches de contenu en parallèle
                self.root.after(0, self._start_parallel_searches)
            else:
                self.root.after(0, lambda: self._show_error_in_tabs("Impossible de trouver la chaîne de l'artiste"))
                
        except Exception as e:
            self.root.after(0, lambda: self._show_error_in_tabs(f"Erreur lors de la recherche de la chaîne: {str(e)}"))
    
    # Lancer la recherche d'ID de chaîne en arrière-plan
    threading.Thread(target=find_channel_id_bg, daemon=True).start()

def _start_parallel_searches(self):
    """Lance les 3 recherches de contenu en parallèle"""
    if self.artist_search_cancelled:
        return
    
    try:
        # Mettre à jour les messages de chargement
        self._update_loading_messages()
        
        # Créer et lancer les threads pour les 3 types de contenu
        self.artist_videos_thread = threading.Thread(target=songs._search_artist_videos_with_id, args=(self,), daemon=True)
        self.artist_releases_thread = threading.Thread(target=releases._search_artist_releases_with_id, args=(self,), daemon=True)
        self.artist_playlists_thread = threading.Thread(target=playlists._search_artist_playlists_with_id, args=(self,), daemon=True)
        
        self.artist_videos_thread.start()
        self.artist_releases_thread.start()
        self.artist_playlists_thread.start()
        
    except Exception as e:
        self.status_bar.config(text=f"Erreur lors du lancement des recherches: {e}")

def _find_artist_channel_id(self):
    """Trouve l'ID réel de la chaîne YouTube pour cet artiste - Version optimisée"""
    try:
        # Vérification d'annulation au début
        if self.artist_search_cancelled:
            return None
        
        # D'abord vérifier si on a déjà un ID dans l'URL (méthode rapide)
        if hasattr(self, 'current_artist_channel_url') and self.current_artist_channel_url:
            import re
            channel_match = re.search(r'/channel/([^/?]+)', self.current_artist_channel_url)
            if channel_match:
                channel_id = channel_match.group(1)
                return channel_id
        
        # Configuration optimisée pour la recherche (plus rapide)
        search_opts = {
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'skip_download': True,  # Ne pas télécharger
            'playlistend': 1,       # Prendre seulement le premier résultat
            'socket_timeout': 10    # Timeout plus court
        }
        
        # Nouvelle vérification d'annulation avant la recherche réseau
        if self.artist_search_cancelled:
            return None
        
        with YoutubeDL(search_opts) as ydl:
            # Recherche optimisée : essayer d'abord avec "official"
            search_queries = [
                f"ytsearch1:{self.current_artist_name} official",
                f"ytsearch1:{self.current_artist_name} music",
                f"ytsearch1:{self.current_artist_name}"
            ]
            
            for search_query in search_queries:
                # Vérification d'annulation à chaque tentative
                if self.artist_search_cancelled:
                    return None
                
                try:
                    search_results = ydl.extract_info(search_query, download=False)
                    
                    if search_results and 'entries' in search_results and search_results['entries']:
                        first_result = search_results['entries'][0]
                        
                        # Essayer de trouver l'ID de la chaîne dans les métadonnées
                        if 'channel_id' in first_result and first_result['channel_id']:
                            return first_result['channel_id']
                        elif 'uploader_id' in first_result and first_result['uploader_id']:
                            return first_result['uploader_id']
                        
                    # Si cette recherche n'a pas donné de résultats, essayer la suivante
                    
                except Exception as search_error:
                    # Si une recherche échoue, essayer la suivante
                    continue
            
            return None
            
    except Exception as e:
        print(f"Erreur lors de la recherche d'ID de chaîne: {e}")
        return None

def _display_results_in_batches(self, items, container, item_type, batch_size=3):
    """Affiche les résultats par petits lots de façon non-bloquante pour éviter le lag de l'interface"""
    if not items:
        return
    
    # Diviser les éléments en lots
    batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
    
    def display_batch(batch_index):
        if batch_index >= len(batches):
            # Terminé, afficher le statut final
            count = len(items)
            if item_type == "videos":
                self.status_bar.config(text=f"{count} musiques trouvées pour {self.current_artist_name}")
            elif item_type == "releases":
                self.status_bar.config(text=f"{count} sorties trouvées pour {self.current_artist_name}")
            elif item_type == "playlists":
                self.status_bar.config(text=f"{count} playlists trouvées pour {self.current_artist_name}")
            return
        
        # Vérifier si on est encore en mode artiste
        if not self.artist_mode:
            return
        
        batch = batches[batch_index]
        start_index = batch_index * batch_size
        
        # Créer les éléments du lot actuel
        for i, item in enumerate(batch):
            index = start_index + i
            try:
                if item_type == "videos":
                    songs._add_artist_result(self, item, index, container)
                elif item_type == "releases":
                    self._add_artist_playlist_result(item, index, container, "sorties")
                elif item_type == "playlists":
                    self._add_artist_playlist_result(item, index, container, "playlists")
            except Exception as e:
                print(f"Erreur lors de l'ajout de l'élément {index}: {e}")
        
        # Mettre à jour le statut de progression
        progress = (batch_index + 1) * batch_size
        total = len(items)
        if progress > total:
            progress = total
        
        if item_type == "videos":
            self.status_bar.config(text=f"Chargement des musiques... {progress}/{total}")
        elif item_type == "releases":
            self.status_bar.config(text=f"Chargement des sorties... {progress}/{total}")
        elif item_type == "playlists":
            self.status_bar.config(text=f"Chargement des playlists... {progress}/{total}")
        
        # Programmer le lot suivant avec un petit délai pour permettre à l'UI de respirer
        self.safe_after(50, lambda: display_batch(batch_index + 1))
    
    # Commencer avec le premier lot
    display_batch(0)

def _show_error_in_tabs(self, error_msg):
    """Affiche un message d'erreur dans tous les onglets artiste"""
    try:
        if hasattr(self, 'musiques_loading') and self.musiques_loading.winfo_exists():
            self.musiques_loading.config(text=f"Erreur: {error_msg}", fg='#ff6666')
        if hasattr(self, 'sorties_loading') and self.sorties_loading.winfo_exists():
            self.sorties_loading.config(text=f"Erreur: {error_msg}", fg='#ff6666')
        if hasattr(self, 'playlists_loading') and self.playlists_loading.winfo_exists():
            self.playlists_loading.config(text=f"Erreur: {error_msg}", fg='#ff6666')
    except:
        pass

def _cancel_artist_search(self):
    """Annule toutes les recherches d'artiste en cours"""
    try:
        # Marquer l'annulation
        self.artist_search_cancelled = True
        
        # Mettre à jour les messages dans les onglets
        if hasattr(self, 'musiques_loading') and self.musiques_loading.winfo_exists():
            self.musiques_loading.config(text="Recherche annulée", fg='#ffaa66')
        if hasattr(self, 'sorties_loading') and self.sorties_loading.winfo_exists():
            self.sorties_loading.config(text="Recherche annulée", fg='#ffaa66')
        if hasattr(self, 'playlists_loading') and self.playlists_loading.winfo_exists():
            self.playlists_loading.config(text="Recherche annulée", fg='#ffaa66')
        
        # Mettre à jour la barre de statut
        self.status_bar.config(text="Recherche d'artiste annulée")
        
        # Note: Les threads se termineront d'eux-mêmes grâce aux vérifications de self.artist_search_cancelled
        
    except Exception as e:
        print(f"Erreur lors de l'annulation de la recherche d'artiste: {e}")

def _update_loading_messages(self):
    """Met à jour les messages de chargement selon l'état actuel"""
    try:
        if hasattr(self, 'musiques_loading') and self.musiques_loading.winfo_exists():
            self.musiques_loading.config(text="Chargement des musiques...", fg='#cccccc')
        if hasattr(self, 'sorties_loading') and self.sorties_loading.winfo_exists():
            self.sorties_loading.config(text="Chargement des sorties...", fg='#cccccc')
        if hasattr(self, 'playlists_loading') and self.playlists_loading.winfo_exists():
            self.playlists_loading.config(text="Chargement des playlists...", fg='#cccccc')
    except:
        pass