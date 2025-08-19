# Fonctions pour l'onglet Sorties des artistes

# Import centralisé depuis __init__.py
from __init__ import *

def _search_artist_releases_with_id(self):
    """Recherche les sorties de l'artiste depuis l'onglet Releases de sa chaîne"""
    try:
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
        
        # Configuration pour extraire les releases de la chaîne
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
            
            try:
                print(f"Extraction des releases depuis: {releases_url}")
                channel_info = ydl.extract_info(releases_url, download=False)
                
                if self.artist_search_cancelled:
                    return
                
                if channel_info:
                    print(f"Channel info type: {type(channel_info)}")
                    print(f"Channel info keys: {list(channel_info.keys()) if isinstance(channel_info, dict) else 'Not a dict'}")
                    
                    if 'entries' in channel_info and channel_info['entries']:
                        entries = channel_info['entries']
                        print(f"Nombre d'entrées trouvées: {len(entries)}")
                        
                        for i, entry in enumerate(entries):
                            print(f"Entrée {i}: type={entry.get('_type', 'unknown')}, id={entry.get('id', 'no-id')}, title={entry.get('title', 'no-title')[:50]}")
                            
                            # Filtrer pour garder seulement les vraies playlists
                            if (entry and entry.get('_type') == 'url' and 
                                entry.get('ie_key') == 'YoutubeTab' and
                                ('playlist' in entry.get('url', '') or 
                                 'list=' in entry.get('url', '') or
                                 entry.get('playlist_count', 0) > 0)):
                                print(f"Release valide trouvée: {entry.get('title', 'Sans titre')}")
                                all_playlists.append(entry)
                        
                        print(f"Nombre de releases trouvées: {len(all_playlists)}")
                        
                        # Limite les résultats
                        all_playlists = all_playlists[:15]  # Prendre les 15 premières
                    else:
                        print("Aucune entrée trouvée dans les releases")
                
            except Exception as e:
                print(f"Erreur lors de l'extraction des releases: {e}")
                self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des sorties"))
                return
            
            if self.artist_search_cancelled:
                return
            
            # Mettre en cache
            if cache_key not in self.artist_cache:
                self.artist_cache[cache_key] = {}
            self.artist_cache[cache_key]['releases'] = all_playlists
            
            # Afficher les résultats
            if not self.artist_search_cancelled:
                self.root.after(0, lambda: self._display_artist_releases(all_playlists))
            
    except Exception as e:
        print(f"Erreur dans _search_artist_releases_with_id: {e}")
        self.root.after(0, lambda: self._show_error_in_tabs(f"Impossible de charger les sorties: {str(e)}"))

def _display_artist_releases(self, releases):
    """Affiche les sorties de l'artiste dans l'onglet Sorties avec scrolling amélioré"""
    # Vérifier si on est encore en mode artiste et que l'onglet sorties existe
    if not hasattr(self, 'sorties_frame') or not self.artist_mode:
        return  # L'utilisateur a annulé l'affichage artiste entre temps
        
    # Supprimer le message de chargement
    if hasattr(self, 'sorties_loading'):
        self.sorties_loading.destroy()
    
    # Remettre l'état du contenu de playlist à zéro car on affiche maintenant la liste normale
    self._reset_playlist_content_state()
    
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
    self._display_results_in_batches(releases, scrollable_frame, "releases")
    
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
    bind_mousewheel_recursive(self.sorties_frame)
    bind_mousewheel_recursive(scrollable_frame)
    
    # S'assurer que le focus peut être pris pour le scrolling
    self.sorties_frame.focus_set()

def _return_to_playlists(self):
    """Retourne à l'affichage des playlists dans l'onglet Sorties"""
    # Remettre l'état du contenu de playlist à zéro
    self._reset_playlist_content_state()
    
    # Relancer la recherche des releases (playlists) pour l'onglet Sorties
    if hasattr(self, 'artist_releases_thread') and self.artist_releases_thread and self.artist_releases_thread.is_alive():
        return  # Déjà en cours
    
    # Vider l'onglet sorties (pas de message de chargement)
    for widget in self.sorties_frame.winfo_children():
        widget.destroy()
    
    # Relancer la recherche des releases
    self.artist_releases_thread = threading.Thread(target=self._search_artist_releases_with_id, daemon=True)
    self.artist_releases_thread.start()