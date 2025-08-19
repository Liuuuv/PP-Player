# Import centralisé depuis __init__.py
from __init__ import *

def _search_artist_releases_with_id(self):
        """Recherche les albums et singles de l'artiste depuis l'onglet releases"""
        try:
            # Vérifier si la recherche a été annulée avant de commencer
            if self.artist_search_cancelled:
                return
            
            if not self.current_artist_channel_id:
                return
            
            # Vérifier le cache d'abord
            cache_key = self.current_artist_channel_id
            if cache_key in self.artist_cache and 'releases' in self.artist_cache[cache_key]:
                cached_releases = self.artist_cache[cache_key]['releases']
                self.root.after(0, lambda: self._display_artist_releases(cached_releases))
                return
                
            # Options pour extraire les releases de la chaîne
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
                releases_url = base_channel_url + '/releases'
                print(f"Extraction des releases depuis: {releases_url}")
                
                try:
                    channel_info = ydl.extract_info(releases_url, download=False)
                    
                    if channel_info and 'entries' in channel_info:
                        playlists = list(channel_info['entries'])
                        print(f"Nombre de releases trouvées: {len(playlists)}")
                        # Garder seulement les vraies playlists/releases
                        valid_playlists = []
                        for p in playlists:
                            if self.artist_search_cancelled:
                                return
                            if p and p.get('id'):
                                # Vérifier si c'est vraiment une playlist
                                if (p.get('_type') == 'playlist' or 
                                    'playlist' in p.get('url', '') or 
                                    'list=' in p.get('url', '') or
                                    p.get('playlist_count', 0) > 0):
                                    valid_playlists.append(p)
                                    # print(f"Release valide: {p.get('title', 'Sans titre')} - {p.get('playlist_count', 0)} vidéos")
                        
                        all_playlists.extend(valid_playlists[:15])  # Prendre les 15 premières
                    else:
                        print("Aucune release trouvée sur la chaîne")
                except Exception as e:
                    print(f"Erreur extraction releases de la chaîne: {e}")
                    self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des releases"))
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
                
                final_playlists = list(unique_playlists.values())  # Toutes les releases
                
                # Vérifier annulation avant affichage
                if not self.artist_search_cancelled:
                    # Sauvegarder en cache
                    cache_key = self.current_artist_channel_id
                    if cache_key not in self.artist_cache:
                        self.artist_cache[cache_key] = {}
                    self.artist_cache[cache_key]['releases'] = final_playlists
                    
                    # Afficher les résultats dans l'interface
                    self.root.after(0, lambda: _display_artist_releases(self, final_playlists))
                    
        except Exception as e:
            print(f"Erreur recherche releases artiste: {e}")
            self.root.after(0, lambda: _display_releases_error(self, str(e)))

def _search_artist_releases_old(self):
        """Ancienne fonction - gardée pour référence"""
        def search_releases():
            try:
                # Vérifier si la recherche a été annulée avant de commencer
                if self.artist_search_cancelled:
                    return
                    
                # Options pour extraire les releases/playlists de la chaîne
                search_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True
                }
                
                with YoutubeDL(search_opts) as ydl:
                    all_playlists = []
                    
                    # Utiliser UNIQUEMENT l'ID de chaîne trouvé précédemment
                    if hasattr(self, 'current_artist_channel_id') and self.current_artist_channel_id:
                        # Utiliser le format officiel avec l'ID de la chaîne
                        base_channel_url = f"https://www.youtube.com/channel/{self.current_artist_channel_id}"
                        releases_url = base_channel_url + '/releases'
                        print(f"URL releases construite avec ID chaîne: {releases_url}")
                        
                        try:
                            if self.artist_search_cancelled:
                                return
                            print(f"Extraction des releases depuis: {releases_url}")
                            channel_info = ydl.extract_info(releases_url, download=False)
                            
                            print(f"Channel info type: {type(channel_info)}")
                            if channel_info:
                                print(f"Channel info keys: {list(channel_info.keys()) if isinstance(channel_info, dict) else 'Not a dict'}")
                            
                            if channel_info and 'entries' in channel_info:
                                playlists = list(channel_info['entries'])
                                print(f"Nombre de releases trouvées: {len(playlists)}")
                                # Garder seulement les vraies playlists/releases
                                valid_playlists = []
                                for p in playlists:
                                    if self.artist_search_cancelled:
                                        return
                                    if p and p.get('id'):
                                        # Vérifier si c'est vraiment une playlist
                                        if (p.get('_type') == 'playlist' or 
                                            'playlist' in p.get('url', '') or 
                                            'list=' in p.get('url', '') or
                                            p.get('playlist_count', 0) > 0):
                                            valid_playlists.append(p)
                                            print(f"Release valide: {p.get('title', 'Sans titre')} - {p.get('playlist_count', 0)} vidéos")
                                
                                all_playlists.extend(valid_playlists[:15])  # Prendre les 15 premières
                            else:
                                print("Aucune release trouvée sur la chaîne")
                        except Exception as e:
                            print(f"Erreur extraction releases de la chaîne: {e}")
                    else:
                        print("Aucun ID de chaîne disponible - impossible de récupérer les releases")
                        self.root.after(0, lambda: self.status_bar.config(text="ID de chaîne manquant pour les releases"))
                    
                    # Plus de recherche alternative - utiliser UNIQUEMENT le contenu de la chaîne officielle
                    if not all_playlists:
                        print("Aucune release trouvée sur la chaîne officielle")
                        self.root.after(0, lambda: self.status_bar.config(text="Aucune release trouvée sur cette chaîne"))
                    
                    # Supprimer les doublons basés sur l'ID
                    unique_playlists = {}
                    for playlist in all_playlists:
                        playlist_id = playlist.get('id', '')
                        if playlist_id and playlist_id not in unique_playlists:
                            # S'assurer que les champs nécessaires sont présents
                            if not playlist.get('webpage_url') and playlist_id:
                                # Déterminer si c'est une playlist ou une vidéo
                                if 'playlist' in playlist.get('_type', '') or 'list=' in playlist.get('url', ''):
                                    playlist['webpage_url'] = f"https://www.youtube.com/playlist?list={playlist_id}"
                                    playlist['_type'] = 'playlist'
                                else:
                                    playlist['webpage_url'] = f"https://www.youtube.com/watch?v={playlist_id}"
                            if not playlist.get('url'):
                                playlist['url'] = playlist.get('webpage_url', '')
                            unique_playlists[playlist_id] = playlist
                    
                    final_playlists = list(unique_playlists.values())
                    
                    # Vérifier annulation avant le tri et l'affichage
                    if self.artist_search_cancelled:
                        return
                    
                    # Trier par date de publication (plus récentes en premier)
                    def get_upload_date(playlist):
                        upload_date = playlist.get('upload_date', '19700101')
                        if isinstance(upload_date, str) and upload_date:
                            try:
                                return int(upload_date)
                            except:
                                return 0
                        return 0
                    
                    final_playlists.sort(key=get_upload_date, reverse=True)
                    
                    # Limiter à 10 playlists max
                    final_playlists = final_playlists[:10]
                    
                    # Vérifier annulation avant affichage
                    if not self.artist_search_cancelled:
                        # Afficher les résultats dans l'interface
                        self.root.after(0, lambda: self._display_artist_releases(final_playlists))
                    
            except Exception as e:
                print(f"Erreur recherche playlists artiste: {e}")
                if not self.artist_search_cancelled:
                    self.root.after(0, lambda: _display_releases_error(self, str(e)))
        
        # Lancer en arrière-plan et enregistrer le thread
        self.artist_releases_thread = threading.Thread(target=search_releases, daemon=True)
        self.artist_releases_thread.start()

def _display_artist_releases(self, releases):
        """Affiche les sorties de l'artiste dans l'onglet Sorties"""
        # Vérifier si on est encore en mode artiste et que l'onglet sorties existe
        if not hasattr(self, 'sorties_frame') or not self.artist_mode:
            return  # L'utilisateur a annulé l'affichage artiste entre temps
            
        # Supprimer le message de chargement
        if hasattr(self, 'sorties_loading'):
            self.sorties_loading.destroy()
        
        # Remettre l'état du contenu de playlist à zéro car on affiche maintenant la liste normale
        self._reset_playlist_content_state()
        print("_display_artist_releases debug")

        if not releases:
            no_results_label = tk.Label(
                self.sorties_frame,
                text="Aucune sortie trouvée",
                bg='#3d3d3d',
                fg='#cccccc',
                font=('TkDefaultFont', 10)
            )
            no_results_label.pack(expand=True)
            return
        
        # Créer un canvas scrollable dans l'onglet sorties
        canvas = tk.Canvas(self.sorties_frame, bg='#3d3d3d', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.sorties_frame, orient="vertical", command=canvas.yview)
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
        core._display_results_in_batches(self, releases, scrollable_frame, "releases")
        
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
        
        self.status_bar.config(text=f"{len(releases)} sorties trouvées pour {self.current_artist_name}")

def _return_to_releases(self):
        """Retourne à l'affichage des releases dans l'onglet Sorties"""

        # Remettre l'état du contenu de playlist à zéro pour l'onglet Sorties uniquement
        self._reset_playlist_content_state("sorties")
        
        # Relancer la recherche des releases (playlists) pour l'onglet Sorties
        if hasattr(self, 'artist_releases_thread') and self.artist_releases_thread and self.artist_releases_thread.is_alive():
            return  # Déjà en cours
        
        # Vider l'onglet sorties (pas de message de chargement)
        for widget in self.sorties_frame.winfo_children():
            widget.destroy()
        
        # Relancer la recherche des releases
        self.artist_releases_thread = threading.Thread(target=self._search_artist_releases_with_id, daemon=True)
        self.artist_releases_thread.start()
        
        # Mettre à jour la visibilité du bouton retour
        if hasattr(self, 'artist_notebook') and self.artist_notebook.winfo_exists():
            try:
                current_tab_id = self.artist_notebook.select()
                if current_tab_id:
                    current_tab_text = self.artist_notebook.tab(current_tab_id, "text")
                    self._update_back_button_visibility(current_tab_text)
            except:
                pass

def _display_releases_error(self, error_msg):
        """Affiche une erreur dans l'onglet Sorties"""
        # Supprimer le message de chargement
        if hasattr(self, 'sorties_loading'):
            self.sorties_loading.destroy()
        
        error_label = tk.Label(
            self.sorties_frame,
            text=f"Erreur lors du chargement des sorties:\n{error_msg}",
            bg='#3d3d3d',
            fg='#ff6666',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        error_label.pack(expand=True)