# Fonctions pour l'onglet Playlists des artistes

# Import centralisé depuis __init__.py
from __init__ import *

def _search_artist_playlists_with_id(self):
    """Recherche les playlists de l'artiste depuis l'onglet Playlists de sa chaîne"""
    try:
        if self.artist_search_cancelled:
            return
        
        if not self.current_artist_channel_id:
            return
        
        # Vérifier le cache d'abord
        cache_key = self.current_artist_channel_id
        if cache_key in self.artist_cache and 'playlists' in self.artist_cache[cache_key]:
            cached_playlists = self.artist_cache[cache_key]['playlists']
            self.root.after(0, lambda: self._display_artist_playlists(cached_playlists))
            return
        
        # Configuration pour extraire les playlists de la chaîne
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
            
            try:
                print(f"Extraction des playlists depuis: {playlists_url}")
                channel_info = ydl.extract_info(playlists_url, download=False)
                
                if self.artist_search_cancelled:
                    return
                
                if channel_info and 'entries' in channel_info and channel_info['entries']:
                    playlists = list(channel_info['entries'])
                    
                    # Filtrer pour garder seulement les vraies playlists
                    for p in playlists:
                        if (p and p.get('_type') in ['url', 'playlist'] and 
                            ('playlist' in p.get('url', '') or 
                             'list=' in p.get('url', '') or
                             p.get('playlist_count', 0) > 0)):
                            all_playlists.append(p)
                    
                    all_playlists = all_playlists[:20]  # Prendre les 20 premières
                else:
                    print("Aucune playlist trouvée sur la chaîne")
                
            except Exception as e:
                print(f"Erreur lors de l'extraction des playlists: {e}")
                self.root.after(0, lambda: self.status_bar.config(text="Erreur lors de l'extraction des playlists"))
                return
            
            if self.artist_search_cancelled:
                return
            
            # Mettre en cache
            if cache_key not in self.artist_cache:
                self.artist_cache[cache_key] = {}
            self.artist_cache[cache_key]['playlists'] = all_playlists
            
            # Afficher les résultats
            if not self.artist_search_cancelled:
                self.root.after(0, lambda: self._display_artist_playlists(all_playlists))
            
    except Exception as e:
        print(f"Erreur dans _search_artist_playlists_with_id: {e}")
        self.root.after(0, lambda: self._show_error_in_tabs(f"Impossible de charger les playlists: {str(e)}"))

def _display_artist_playlists(self, playlists):
    """Affiche les playlists de l'artiste dans l'onglet Playlists avec scrolling amélioré"""
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
    bind_mousewheel_recursive(self.playlists_frame)
    bind_mousewheel_recursive(scrollable_frame)
    
    # S'assurer que le focus peut être pris pour le scrolling
    self.playlists_frame.focus_set()

def _return_to_playlists_tab(self):
    """Retourne à l'affichage des playlists dans l'onglet Playlists"""
    # Remettre l'état du contenu de playlist à zéro
    self._reset_playlist_content_state()
    
    # Relancer la recherche des playlists pour l'onglet Playlists
    if hasattr(self, 'artist_playlists_thread') and self.artist_playlists_thread and self.artist_playlists_thread.is_alive():
        return  # Déjà en cours
    
    # Vider l'onglet playlists (pas de message de chargement)
    for widget in self.playlists_frame.winfo_children():
        widget.destroy()
    
    # Relancer la recherche des playlists
    self.artist_playlists_thread = threading.Thread(target=self._search_artist_playlists_with_id, daemon=True)
    self.artist_playlists_thread.start()