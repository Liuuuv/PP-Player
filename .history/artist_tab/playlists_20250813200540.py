# Import centralisé depuis __init__.py
from __init__ import *
from . import core

def _search_artist_playlists_with_id(self):
        """Recherche les playlists de l'artiste depuis l'onglet playlists"""  
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.artist_search_cancelled:
                return
            
            if not self.current_artist_channel_id:
                print("Aucun ID de chaîne disponible pour les playlists")
                return
            
            # Vérifier le cache d'abord
            cache_key = self.current_artist_channel_id
            if cache_key in self.artist_cache and 'playlists' in self.artist_cache[cache_key]:
                print("Utilisation du cache pour les playlists")
                cached_playlists = self.artist_cache[cache_key]['playlists']
                self.root.after(0, lambda: _display_artist_playlists(self, cached_playlists))
                return
                
            # Options pour extraire les playlists de la chaîne
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                all_playlists = []
                
                # Utiliser l'ID de chaîne trouvé
                base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
                playlists_url = base_channel_url + '/playlists'
                print(f"Extraction des playlists depuis: {playlists_url}")
                
                try:
                    channel_info = ydl.extract_info(playlists_url, download=False)
                    if self.artist_search_cancelled:
                        return
                    
                    print(f"Channel info type: {type(channel_info)}")
                    if channel_info:
                        print(f"Channel info keys: {list(channel_info.keys()) if isinstance(channel_info, dict) else 'Not a dict'}")
                    
                    if channel_info and 'entries' in channel_info:
                        entries = list(channel_info['entries'])
                        print(f"Nombre d'entrées trouvées: {len(entries)}")
                        
                        for i, entry in enumerate(entries):
                            if self.artist_search_cancelled:
                                return
                            if entry:
                                print(f"Entrée {i}: type={entry.get('_type')}, id={entry.get('id')}, title={entry.get('title', 'Sans titre')}")
                                # Logique plus flexible pour détecter les playlists
                                if (entry.get('_type') == 'playlist' or 
                                    'playlist' in entry.get('url', '') or 
                                    'list=' in entry.get('url', '') or
                                    entry.get('playlist_count', 0) > 0 or
                                    entry.get('id', '').startswith('PL') or  # Les IDs de playlist YouTube commencent par PL
                                    'playlist' in entry.get('title', '').lower()):
                                    all_playlists.append(entry)
                                    print(f"Playlist valide trouvée: {entry.get('title', 'Sans titre')}")
                                else:
                                    print(f"Entrée ignorée (pas une playlist): {entry.get('title', 'Sans titre')}")
                    else:
                        print("Aucune entrée trouvée dans channel_info")
                                
                    if not all_playlists:
                        print("Aucune playlist trouvée sur la chaîne")
                except Exception as e:
                    print(f"Erreur extraction playlists de la chaîne: {e}")
                    self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des playlists"))
                    return
                
                # Supprimer les doublons basés sur l'ID
                unique_playlists = {}
                for playlist in all_playlists:
                    playlist_id = playlist.get('id', '')
                    if playlist_id and playlist_id not in unique_playlists:
                        # S'assurer que les champs nécessaires sont présents
                        if not playlist.get('webpage_url') and playlist_id:
                            playlist['webpage_url'] = f"https://www.youtube.com/playlist?list={playlist_id}"
                            playlist['_type'] = 'playlist'
                        unique_playlists[playlist_id] = playlist
                
                final_playlists = list(unique_playlists.values())[:20]  # Maximum 20 playlists
                
                # Vérifier annulation avant affichage
                if not self.artist_search_cancelled:
                    # Sauvegarder en cache
                    cache_key = self.current_artist_channel_id
                    if cache_key not in self.artist_cache:
                        self.artist_cache[cache_key] = {}
                    self.artist_cache[cache_key]['playlists'] = final_playlists
                    
                    # Afficher les résultats dans l'interface
                    self.root.after(0, lambda: _display_artist_playlists(self, final_playlists))
                    
        except Exception as e:
            print(f"Erreur recherche playlists artiste: {e}")
            self.root.after(0, lambda: self._display_playlists_error(self, str(e)))

def _display_artist_playlists(self, playlists):
        """Affiche les playlists de l'artiste dans l'onglet Playlists"""
        # Vérifier si on est encore en mode artiste et que l'onglet playlists existe
        if not hasattr(self, 'playlists_frame') or not self.artist_mode:
            return  # L'utilisateur a annulé l'affichage artiste entre temps
            
        # Supprimer le message de chargement
        if hasattr(self, 'playlists_loading'):
            self.playlists_loading.destroy()
        
        # Remettre l'état du contenu de playlist à zéro car on affiche maintenant la liste normale
        core._reset_playlist_content_state(self)
        
        if not playlists:
            no_results_label = tk.Label(
                self.playlists_frame,
                text="Aucune playlist trouvée",
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 10)
            )
            no_results_label.pack(expand=True)
            return
        
        # Créer un canvas scrollable dans l'onglet playlists
        canvas = tk.Canvas(self.playlists_frame, bg='#3d3d3d', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.playlists_frame, orient="vertical", command=canvas.yview)
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
        
        # Afficher les playlists dans le frame scrollable par petits lots (non-bloquant)
        core._display_results_in_batches(self, playlists, scrollable_frame, "playlists")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel_recursive(widget):
            """Bind mousewheel à un widget et tous ses enfants"""
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        bind_mousewheel_recursive(scrollable_frame)
        
        self.status_bar.config(text=f"{len(playlists)} playlists trouvées pour {self.current_artist_name}")

def _show_playlist_loading(self, playlist_title, target_tab="sorties"):
        """Affiche un message de chargement pour la playlist ou sortie"""
        # Choisir l'onglet cible
        target_frame = self.playlists_frame if target_tab == "playlists" else self.sorties_frame
        
        # Déterminer le type de contenu selon l'onglet
        content_type = "playlist" if target_tab == "playlists" else "sortie"
        
        # Vider l'onglet cible et afficher le chargement
        for widget in target_frame.winfo_children():
            widget.destroy()
        
        loading_label = tk.Label(
            target_frame,
            text=f"Chargement de la {content_type}:\n{playlist_title}...",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        loading_label.pack(expand=True)

def _return_to_playlists(self):
        """Retourne à l'affichage des playlists dans l'onglet Playlists"""
        # Remettre l'état du contenu de playlist à zéro pour l'onglet Playlists uniquement
        core._reset_playlist_content_state(self, "playlists")
        
        # Relancer la recherche des playlists pour l'onglet Playlists
        if hasattr(self, 'artist_playlists_thread') and self.artist_playlists_thread and self.artist_playlists_thread.is_alive():
            return  # Déjà en cours
        
        # Vider l'onglet playlists (pas de message de chargement)
        for widget in self.playlists_frame.winfo_children():
            widget.destroy()
        
        # Relancer la recherche des playlists
        self.artist_playlists_thread = threading.Thread(target=lambda: _search_artist_playlists_with_id(self), daemon=True)
        self.artist_playlists_thread.start()
        
        # Mettre à jour la visibilité du bouton retour
        if hasattr(self, 'artist_notebook') and self.artist_notebook.winfo_exists():
            try:
                current_tab_id = self.artist_notebook.select()
                if current_tab_id:
                    current_tab_text = self.artist_notebook.tab(current_tab_id, "text")
                    self.artist_tab_manager._update_back_button_visibility(current_tab_text)
            except:
                pass

def _show_playlist_error(self, error_msg):
        """Affiche une erreur lors du chargement d'une playlist"""
        # Vider l'onglet sorties
        for widget in self.sorties_frame.winfo_children():
            widget.destroy()
        
        error_label = tk.Label(
            self.sorties_frame,
            text=f"Erreur lors du chargement de la playlist:\n{error_msg}",
            bg='#3d3d3d',
            fg='#ff6666',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        error_label.pack(expand=True)

def _display_playlists_error(self, error_msg):
        """Affiche une erreur dans l'onglet Playlists"""
        # Supprimer le message de chargement
        if hasattr(self, 'playlists_loading'):
            self.playlists_loading.destroy()
        
        error_label = tk.Label(
            self.playlists_frame,
            text=f"Erreur lors du chargement des playlists:\n{error_msg}",
            bg='#3d3d3d',
            fg='#ff6666',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        error_label.pack(expand=True)

def _display_playlist_content(self, videos, playlist_title, target_tab="sorties"):
    """Affiche le contenu d'une playlist avec la même interface que l'onglet Musiques"""
    # Choisir l'onglet cible
    target_frame = self.playlists_frame if target_tab == "playlists" else self.sorties_frame # AMELIORER
    
    # Vider l'onglet cible
    for widget in target_frame.winfo_children():
        widget.destroy()
    
    if not videos:
        no_results_label = tk.Label(
            target_frame,
            text="Aucune vidéo trouvée dans cette playlist",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 10)
        )
        no_results_label.pack(expand=True)
        return
    
    # Marquer qu'on affiche du contenu de playlist et dans quel onglet
    if target_tab == "playlists":
        self.artist_tab_active_playlists = True
        self.playlist_content_active_playlists = True
        self.current_artist_tab = "Playlists"
    else:
        self.artist_tab_active_sorties = True
        self.playlist_content_active_sorties = True
        self.current_artist_tab = "Sorties"
    
    # Mettre à jour les variables de compatibilité
    self.playlist_content_active = True
    
    # Créer un frame pour le titre et le bouton retour
    header_frame = tk.Frame(target_frame, bg='#3d3d3d')
    header_frame.pack(fill="x", padx=5, pady=5)
    
    # Créer le bouton retour à côté de la croix de l'artiste (dans le container principal)
    back_command = self._return_to_playlists if target_tab == "playlists" else self._return_to_releases
    
    # Trouver le container principal (parent de target_frame)
    main_container = target_frame.master.master  # target_frame -> notebook -> main_container
    
    # Détruire l'ancien bouton s'il existe
    if hasattr(self, 'artist_tab_back_btn') and self.artist_tab_back_btn:
        try:
            self.artist_tab_back_btn.destroy()
        except:
            pass
    
    if hasattr(self, 'icons') and 'back' in self.icons:
        button = tk.Button(
            main_container,
            image=self.icons['back'],
            bg='#3d3d3d',
            activebackground='#4a8fe7',
            relief='raised',
            bd=1,
            width=20,
            height=20,
            command=back_command,
            cursor='hand2',
            takefocus=0
        )
    else:
        # Fallback si l'icône n'est pas disponible
        button = tk.Button(
            main_container,
            text="←",
            bg='#3d3d3d',
            fg='white',
            activebackground='#4a8fe7',
            relief='raised',
            bd=1,
            font=('TkDefaultFont', 10, 'bold'),
            width=20,
            height=20,
            command=back_command,
            cursor='hand2',
            takefocus=0
        )
    
    # Assigner le bouton unique
    self.artist_tab_back_btn = button
    
    # Positionner le bouton à gauche de la croix (croix à x=-5, back à x=-40 pour plus d'espace)
    button.place(in_=main_container, relx=1.0, rely=0.0, anchor="ne", x=-40, y=5)
    button.tkraise()  # Mettre le bouton au premier plan
    
    # Titre de la playlist
    title_label = tk.Label(
        header_frame,
        text=f"Playlist: {playlist_title}",
        bg='#3d3d3d',
        fg='white',
        font=('TkDefaultFont', 10, 'bold')
    )
    title_label.pack(side="left", padx=(10, 0))
    
    # Créer un canvas scrollable pour les vidéos
    canvas = tk.Canvas(target_frame, bg='#3d3d3d', highlightthickness=0)
    scrollbar = ttk.Scrollbar(target_frame, orient="vertical", command=canvas.yview)
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
    core._display_results_in_batches(self, videos, scrollable_frame, "videos")
    
    # Bind mousewheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def bind_mousewheel_recursive(widget):
        """Bind mousewheel à un widget et tous ses enfants"""
        widget.bind("<MouseWheel>", _on_mousewheel)
        for child in widget.winfo_children():
            bind_mousewheel_recursive(child)
    
    canvas.bind("<MouseWheel>", _on_mousewheel)
    bind_mousewheel_recursive(scrollable_frame)
    
    self.status_bar.config(text=f"{len(videos)} vidéos dans la playlist '{playlist_title}'")
    
    # Mettre à jour la visibilité du bouton retour selon l'onglet actuel
    if hasattr(self, 'artist_notebook') and self.artist_notebook.winfo_exists():
        try:
            current_tab_id = self.artist_notebook.select()
            if current_tab_id:
                current_tab_text = self.artist_notebook.tab(current_tab_id, "text")
                self._update_back_button_visibility(current_tab_text)
        except:
            pass

def _show_playlist_content(self, playlist_data, target_tab="sorties"):
    """Affiche le contenu d'une playlist dans une nouvelle interface"""
    def load_playlist_content():
        try:
            playlist_url = playlist_data.get('url', '') or playlist_data.get('webpage_url', '')
            if not playlist_url:
                self.root.after(0, lambda: self._show_playlist_error("URL de playlist non trouvée"))
                return
            
            # Vérifier le cache d'abord
            if playlist_url in self.playlist_content_cache:
                print("Utilisation du cache pour le contenu de la playlist")
                cached_videos = self.playlist_content_cache[playlist_url]
                playlist_title = playlist_data.get('title', 'Playlist')
                self.root.after(0, lambda: _display_playlist_content(self, cached_videos, playlist_title, target_tab))
                return
            
            print(f"Chargement playlist: {playlist_url}")
            print(f"Type: {playlist_data.get('_type', 'unknown')}")
            
            # Si c'est une vidéo individuelle, la traiter comme telle
            if 'watch?v=' in playlist_url and 'list=' not in playlist_url:
                # C'est une vidéo individuelle, pas une playlist
                video_data = playlist_data.copy()
                if not video_data.get('webpage_url'):
                    video_data['webpage_url'] = playlist_url
                if not video_data.get('url'):
                    video_data['url'] = playlist_url
                
                playlist_title = playlist_data.get('title', 'Vidéo')
                self.root.after(0, lambda: _display_playlist_content(self, [video_data], playlist_title, target_tab))
                return
            
            # Options pour extraire le contenu de la playlist
            playlist_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            with YoutubeDL(playlist_opts) as ydl:
                # Extraire le contenu de la playlist
                playlist_info = ydl.extract_info(playlist_url, download=False)

                if playlist_info and 'entries' in playlist_info:
                    videos = list(playlist_info['entries'])
                    # Filtrer et garder seulement les vidéos valides
                    videos = [v for v in videos if v and v.get('id')]
                    
                    # S'assurer que les champs nécessaires sont présents
                    for video in videos:
                        if not video.get('webpage_url') and video.get('id'):
                            video['webpage_url'] = f"https://www.youtube.com/watch?v={video['id']}"
                        if not video.get('url'):
                            video['url'] = video.get('webpage_url', f"https://www.youtube.com/watch?v={video['id']}")
                    
                    # Sauvegarder en cache
                    self.playlist_content_cache[playlist_url] = videos
                    
                    # Afficher le contenu dans l'interface
                    playlist_title = playlist_data.get('title', 'Playlist')
                    self.root.after(0, lambda: _display_playlist_content(self, videos, playlist_title, target_tab))
                elif playlist_info:
                    # Si c'est une vidéo individuelle retournée
                    video_data = playlist_info.copy()
                    if not video_data.get('webpage_url') and video_data.get('id'):
                        video_data['webpage_url'] = f"https://www.youtube.com/watch?v={video_data['id']}"
                    if not video_data.get('url'):
                        video_data['url'] = video_data.get('webpage_url', playlist_url)
                    
                    # Sauvegarder en cache (vidéo individuelle)
                    self.playlist_content_cache[playlist_url] = [video_data]
                    
                    playlist_title = playlist_data.get('title', 'Vidéo')
                    self.root.after(0, lambda: _display_playlist_content(self, [video_data], playlist_title, target_tab))
                else:
                    self.root.after(0, lambda: _show_playlist_error(self, "Impossible de charger le contenu"))
                    
        except Exception as e:
            print(f"Erreur chargement contenu playlist: {e}")
            self.root.after(0, lambda: _show_playlist_error(self, str(e)))
    
    # Afficher un message de chargement dans l'onglet cible
    self.artist_tab_manager.show_playlist_loading(playlist_data.get('title', 'Contenu'), target_tab)
    
    # Lancer en arrière-plan
    threading.Thread(target=load_playlist_content, daemon=True).start()
