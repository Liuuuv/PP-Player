import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier library_tab
from library_tab import *

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
                self.root.after(0, lambda: self._display_artist_playlists(cached_playlists))
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
                    self.root.after(0, lambda: self._display_artist_playlists(final_playlists))
                    
        except Exception as e:
            print(f"Erreur recherche playlists artiste: {e}")
            self.root.after(0, lambda: self._display_playlists_error(str(e)))

def _display_artist_playlists(self, playlists):
        """Affiche les playlists de l'artiste dans l'onglet Playlists"""
        # Vérifier si on est encore en mode artiste et que l'onglet playlists existe
        if not hasattr(self, 'playlists_frame') or not self.artist_mode:
            return  # L'utilisateur a annulé l'affichage artiste entre temps
            
        # Supprimer le message de chargement
        if hasattr(self, 'playlists_loading'):
            self.playlists_loading.destroy()
        
        # Remettre l'état du contenu de playlist à zéro car on affiche maintenant la liste normale
        self._reset_playlist_content_state()
        
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
        self._display_results_in_batches(playlists, scrollable_frame, "playlists")
        
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
        """Affiche un message de chargement pour la playlist"""
        # Choisir l'onglet cible
        target_frame = self.playlists_frame if target_tab == "playlists" else self.sorties_frame
        
        # Vider l'onglet cible et afficher le chargement
        for widget in target_frame.winfo_children():
            widget.destroy()
        
        loading_label = tk.Label(
            target_frame,
            text=f"Chargement de la playlist:\n{playlist_title}...",
            bg='#3d3d3d',
            fg='#cccccc',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        loading_label.pack(expand=True)

def _return_to_playlists(self):
        """Retourne à l'affichage des playlists dans l'onglet Playlists"""
        # Remettre l'état du contenu de playlist à zéro pour l'onglet Playlists uniquement
        self._reset_playlist_content_state("playlists")
        
        # Relancer la recherche des playlists pour l'onglet Playlists
        if hasattr(self, 'artist_playlists_thread') and self.artist_playlists_thread and self.artist_playlists_thread.is_alive():
            return  # Déjà en cours
        
        # Vider l'onglet playlists (pas de message de chargement)
        for widget in self.playlists_frame.winfo_children():
            widget.destroy()
        
        # Relancer la recherche des playlists
        self.artist_playlists_thread = threading.Thread(target=self._search_artist_playlists_with_id, daemon=True)
        self.artist_playlists_thread.start()
        
        # Mettre à jour la visibilité des boutons retour
        self._update_back_buttons_visibility()

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