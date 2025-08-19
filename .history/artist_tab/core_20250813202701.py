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
            _load_artist_thumbnail(self, playlist, thumbnail_label)
            
            # Titre et nombre de vidéos (dans une frame verticale)
            text_frame = tk.Frame(result_frame, bg='#4a4a4a')
            text_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 5), pady=3)
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            text_frame.rowconfigure(1, weight=0)
            
            # Tronquer le titre intelligemment selon la largeur en pixels
            from . import utils
            display_title = utils.truncate_text_for_display(self, title, max_width_pixels=200, font_size=8)
            
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
            _load_playlist_count(self, playlist, count_label)
            
            # Stocker les données playlist
            result_frame.playlist_data = playlist
            result_frame.title_label = title_label
            result_frame.count_label = count_label
            result_frame.thumbnail_label = thumbnail_label
            
            # Événements de clic (double-clic pour voir le contenu de la playlist)
            def on_playlist_double_click(event, frame=result_frame):
                # Appeler via le gestionnaire pour maintenir la compatibilité
                self.artist_tab_manager.show_playlist_content(frame.playlist_data, target_tab)
            
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
        _reset_playlist_content_state(self)
        
        # Essayer de récupérer l'URL de la chaîne depuis les métadonnées vidéo
        self.current_artist_channel_url = video_data.get('channel_url', '')
        if not self.current_artist_channel_url:
            # Fallback: construire l'URL de recherche avec plusieurs tentatives
            self.current_artist_channel_url = f"https://www.youtube.com/results?search_query={artist_name.replace(' ', '+')}"
        
        # Créer l'interface de manière synchrone (instantanée)
        _create_artist_tabs(self)
        
        # Lancer la recherche asynchrone en arrière-plan
        _search_artist_content_async(self)
        
    except Exception as e:
        print(f"Erreur lors de l'affichage de l'artiste {artist_name}: {e}")
        self.status_bar.config(text=f"Erreur lors du chargement de l'artiste: {e}")

def _hide_search_elements(self):
    """Masque les éléments de recherche pour faire place à l'interface d'artiste"""
    # Cacher le canvas et la scrollbar des résultats
    if hasattr(self, 'youtube_canvas') and self.youtube_canvas is not None:
        try:
            if self.youtube_canvas.winfo_exists():
                self.youtube_canvas.pack_forget()
        except:
            pass
    
    if hasattr(self, 'scrollbar') and self.scrollbar is not None:
        try:
            if self.scrollbar.winfo_exists():
                self.scrollbar.pack_forget()
        except:
            pass
    
    # Cacher aussi la frame thumbnail si elle est visible
    if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame is not None:
        try:
            if self.thumbnail_frame.winfo_exists():
                self.thumbnail_frame.pack_forget()
        except:
            pass


def _search_artist_content_async(self):
    """Version asynchrone et non-bloquante de la recherche d'artiste"""
    self.status_bar.config(text=f"Recherche de l'ID de la chaîne de {self.current_artist_name}...")
    
    # Étape 1 : Trouver l'ID de la chaîne en arrière-plan
    def find_channel_id_bg():
        try:
            if self.artist_search_cancelled:
                return
            
            channel_id = _find_artist_channel_id(self)
            
            if self.artist_search_cancelled:
                return
            
            # Mettre à jour l'interface via le thread principal
            if channel_id:
                self.root.after(0, lambda: _on_channel_id_found(self, channel_id))
            else:
                self.root.after(0, lambda: _on_channel_id_error(self))
                
        except Exception as e:
            self.root.after(0, lambda: _on_channel_id_error(self, str(e)))
    
    # Lancer la recherche d'ID en arrière-plan
    threading.Thread(target=find_channel_id_bg, daemon=True).start()

def _find_artist_channel_id(self):
    """Trouve l'ID de chaîne YouTube de l'artiste"""
    try:
        if self.artist_search_cancelled:
            return None
        
        # Essayer d'extraire l'ID depuis l'URL de chaîne si disponible
        if self.current_artist_channel_url:
            import re
            channel_id_match = re.search(r'channel/([^/]+)', self.current_artist_channel_url)
            if channel_id_match:
                return channel_id_match.group(1)
        
        # Sinon, faire une recherche pour trouver la chaîne
        search_opts = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True
        }
        
        with YoutubeDL(search_opts) as ydl:
            # Rechercher la chaîne de l'artiste
            search_query = f"ytsearch1:{self.current_artist_name} channel"
            search_results = ydl.extract_info(search_query, download=False)
            
            if search_results and 'entries' in search_results and search_results['entries']:
                first_result = search_results['entries'][0]
                channel_id = first_result.get('channel_id')
                if channel_id:
                    return channel_id
                
                # Si pas d'ID direct, essayer d'extraire depuis l'URL
                channel_url = first_result.get('channel_url', '')
                if channel_url:
                    import re
                    channel_id_match = re.search(r'channel/([^/]+)', channel_url)
                    if channel_id_match:
                        return channel_id_match.group(1)
        
        return None
        
    except Exception as e:
        print(f"Erreur lors de la recherche de l'ID de chaîne: {e}")
        return None

def _show_artist_content(self, artist_name, video_data):
    """Affiche le contenu d'un artiste dans la zone de recherche YouTube - Version optimisée non-bloquante"""
    try:
        # Vérifier si on est déjà en mode artiste avec le même artiste
        if self.artist_mode and self.current_artist_name == artist_name:
            return
        
        # Si on est déjà en mode artiste mais avec un artiste différent, nettoyer l'ancien
        if self.artist_mode and self.current_artist_name != artist_name:
            self._return_to_search()
        
        # S'assurer qu'on est sur l'onglet "Recherche"
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab != "Recherche":
            # Trouver l'index de l'onglet "Recherche" et le sélectionner
            for i in range(self.notebook.index("end")):
                if self.notebook.tab(i, "text") == "Recherche":
                    self.notebook.select(i)
                    break
        
        # Passer en mode artiste IMMÉDIATEMENT
        self.artist_mode = True
        self.current_artist_name = artist_name
        
        # Remettre l'état du contenu de playlist à zéro pour le nouvel artiste
        _reset_playlist_content_state(self)
        
        # Essayer de récupérer l'URL de la chaîne depuis les métadonnées vidéo
        self.current_artist_channel_url = video_data.get('channel_url', '')
        if not self.current_artist_channel_url:
            # Fallback: construire l'URL de recherche avec plusieurs tentatives
            import urllib.parse
            # Nettoyer le nom de l'artiste pour l'URL
            clean_artist_name = artist_name.replace(' ', '').replace('　', '').replace('/', '')
            # Encoder les caractères spéciaux
            encoded_artist_name = urllib.parse.quote(clean_artist_name, safe='')
            self.current_artist_channel_url = f"https://www.youtube.com/@{encoded_artist_name}"
        
        # Sauvegarder l'état actuel des résultats
        self._save_current_search_state()
        
        # S'assurer que la zone YouTube est visible
        self._show_search_results()
        
        # Créer les onglets IMMÉDIATEMENT (UI d'abord, contenu après)
        _create_artist_tabs(self)
        
        # Forcer la mise à jour de l'affichage pour montrer l'interface immédiatement
        self.root.update_idletasks()
        
        # Afficher un message de préparation
        self.status_bar.config(text=f"Préparation de la page de {artist_name}...")
        
        # Réinitialiser le flag d'annulation des recherches artiste
        self.artist_search_cancelled = False
        
        # Lancer la recherche complète de l'artiste en arrière-plan avec un délai minimal
        # pour permettre à l'UI de se dessiner
        self.safe_after(50, lambda: _search_artist_content_async(self))
        
    except Exception as e:
        print(f"Erreur lors de l'affichage du contenu d'artiste: {e}")
        self.status_bar.config(text=f"Erreur: {e}")

def _load_artist_thumbnail(self, video, thumbnail_label):
    """Charge la miniature d'une vidéo d'artiste en arrière-plan"""
    try:
        thumbnail_url = video.get('thumbnail', '')
        if not thumbnail_url:
            return
        
        def load_thumbnail():
            try:
                import requests
                from PIL import Image, ImageTk
                import io
                
                response = requests.get(thumbnail_url, timeout=5)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    image = image.resize((50, 38), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Mettre à jour l'interface dans le thread principal
                    self.root.after(0, lambda: self._update_thumbnail_label(thumbnail_label, photo))
                    
            except Exception as e:
                pass  # Ignorer les erreurs de chargement de miniatures
        
        # Lancer le chargement en arrière-plan
        threading.Thread(target=load_thumbnail, daemon=True).start()
        
    except Exception as e:
        pass  # Ignorer les erreurs

def _update_thumbnail_label(self, label, photo):
    """Met à jour le label de miniature avec la photo chargée"""
    try:
        if label.winfo_exists():
            label.configure(image=photo, text="")
            label.image = photo  # Garder une référence
    except:
        pass

def _reset_playlist_content_state(self, tab_name=None):
    """Remet l'état du contenu de playlist à zéro pour l'onglet spécifié"""
    try:
        if tab_name is None or tab_name == "sorties":
            self.artist_tab_active_sorties = False
        
        if tab_name is None or tab_name == "playlists":
            self.artist_tab_active_playlists = False
        
        # Mettre à jour les variables et la visibilité du bouton
        if hasattr(self, 'artist_notebook') and self.artist_notebook is not None and self.artist_notebook.winfo_exists():
            try:
                current_tab_id = self.artist_notebook.select()
                if current_tab_id:
                    current_tab_text = self.artist_notebook.tab(current_tab_id, "text")
                    if current_tab_text == "Sorties":
                        self.playlist_content_active = self.artist_tab_active_sorties
                    elif current_tab_text == "Playlists":
                        self.playlist_content_active = self.artist_tab_active_playlists
                    
                    # Mettre à jour la visibilité du bouton retour après changement d'état
                    if hasattr(self, 'artist_tab_manager'):
                        self.artist_tab_manager._update_back_button_visibility(current_tab_text)
                        
                        # Si on vient de fermer un onglet mais que l'autre a encore du contenu,
                        # s'assurer que le bouton retour sera disponible quand on changera d'onglet
                        if tab_name is not None:  # On a fermé un onglet spécifique
                            # Vérifier si l'autre onglet a encore du contenu
                            other_tab_has_content = False
                            if tab_name == "sorties" and self.artist_tab_active_playlists:
                                other_tab_has_content = True
                            elif tab_name == "playlists" and self.artist_tab_active_sorties:
                                other_tab_has_content = True
                            
                            # Si l'autre onglet a du contenu, s'assurer que le bouton sera recréé
                            if other_tab_has_content:
                                # Le bouton sera recréé automatiquement lors du changement d'onglet
                                # grâce à on_artist_tab_changed
                                pass
            except:
                pass
    except:
        pass
    # try:
    #     # Réinitialiser l'état pour les deux onglets
    #     self.artist_tab_active_sorties = False
    #     self.artist_tab_active_playlists = False
    #     self.playlist_content_active = False
    #     self.current_artist_tab = None
        
    #     # Masquer le bouton retour s'il existe
    #     if hasattr(self, 'playlist_back_btn') and self.artist_tab_back_btn is not None:
    #         try:
    #             if self.artist_tab_back_btn.winfo_exists():
    #                 self.artist_tab_back_btn.place_forget()
    #         except:
    #             pass
    # except:
    #     pass

def _save_current_search_state(self):
    """Sauvegarde l'état actuel des résultats de recherche"""
    try:
        # Sauvegarder le contenu actuel de la zone de recherche
        if hasattr(self, 'youtube_results_frame'):
            self.original_search_content = []
            for widget in self.youtube_results_frame.winfo_children():
                self.original_search_content.append(widget)
    except:
        pass

def _show_search_results(self):
    """S'assure que la zone de recherche YouTube est visible"""
    try:
        # S'assurer que la zone YouTube est visible
        if hasattr(self, 'youtube_results_frame'):
            self.youtube_results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    except:
        pass

def _return_to_search(self):
    """Retourne à l'affichage de recherche normal"""
    try:
        # Annuler toutes les recherches d'artiste en cours
        self.artist_search_cancelled = True
        
        # Sortir du mode artiste
        self.artist_mode = False
        self.current_artist_name = ""
        self.current_artist_channel_url = ""
        self.current_artist_channel_id = None
        
        # Remettre l'état du contenu de playlist à zéro
        _reset_playlist_content_state(self)
        
        # Nettoyer la zone YouTube
        for widget in self.youtube_results_frame.winfo_children():
            try:
                widget.destroy()
            except:
                pass
        
        # Restaurer l'affichage de recherche normal
        if hasattr(self, 'original_search_content') and self.original_search_content:
            # Restaurer le contenu sauvegardé
            for widget in self.original_search_content:
                try:
                    widget.pack(fill=tk.BOTH, expand=True)
                except:
                    pass
        else:
            # Recréer l'interface de recherche de base
            _setup_youtube_search_interface(self)
        
        # Mettre à jour la barre de statut
        self.status_bar.config(text="Retour à la recherche")
        
    except Exception as e:
        print(f"Erreur lors du retour à la recherche: {e}")

def _setup_youtube_search_interface(self):
    """Recrée l'interface de recherche YouTube de base"""
    try:
        # Recréer le canvas et la scrollbar pour les résultats
        if not hasattr(self, 'youtube_canvas') or not self.youtube_canvas.winfo_exists():
            self.youtube_canvas = tk.Canvas(self.youtube_results_frame, bg='#3d3d3d', highlightthickness=0)
            self.scrollbar = ttk.Scrollbar(self.youtube_results_frame, orient="vertical", command=self.youtube_canvas.yview)
            self.youtube_canvas.configure(yscrollcommand=self.scrollbar.set)
            
            # Empaqueter
            self.scrollbar.pack(side="right", fill="y")
            self.youtube_canvas.pack(side="left", fill="both", expand=True)
        
        # Afficher un message par défaut
        if hasattr(self, 'youtube_canvas'):
            self.youtube_canvas.delete("all")
            self.youtube_canvas.create_text(
                200, 100,
                text="Effectuez une recherche pour voir les résultats",
                fill='#cccccc',
                font=('TkDefaultFont', 10)
            )
    except Exception as e:
        print(f"Erreur lors de la recréation de l'interface de recherche: {e}")

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

def _start_parallel_searches(self):
        """Lance les 3 recherches de contenu de manière échelonnée pour éviter le lag"""
        if self.artist_search_cancelled:
            return
        
        try:
            # Mettre à jour les messages de chargement
            _update_loading_messages(self)
            
            # Lancer les recherches de manière échelonnée avec des délais pour éviter le lag
            # Commencer par les vidéos (plus important)
            self.artist_videos_thread = threading.Thread(target=lambda: songs._search_artist_videos_with_id(self), daemon=True)
            self.artist_videos_thread.start()
            
            # Lancer les sorties après un petit délai
            self.safe_after(500, lambda: self._start_releases_search())
            
            # Lancer les playlists après un délai plus long
            self.safe_after(1000, lambda: self._start_playlists_search())
            
        except Exception as e:
            self.status_bar.config(text=f"Erreur lors du lancement des recherches: {e}")

def _start_releases_search(self):
    """Lance la recherche des sorties avec vérification d'annulation"""
    if not self.artist_search_cancelled:
        self.artist_releases_thread = threading.Thread(target=lambda: releases._search_artist_releases_with_id(self), daemon=True)
        self.artist_releases_thread.start()

def _start_playlists_search(self):
    """Lance la recherche des playlists avec vérification d'annulation"""
    if not self.artist_search_cancelled:
        self.artist_playlists_thread = threading.Thread(target=lambda: playlists._search_artist_playlists_with_id(self), daemon=True)
        self.artist_playlists_thread.start()
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
            'socket_timeout': 5,    # Timeout encore plus court
            'retries': 1,           # Moins de tentatives
            'fragment_retries': 1   # Moins de tentatives pour les fragments
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
                        _add_artist_result(self, item, index, container)
                    elif item_type == "releases":
                        _add_artist_playlist_result(self, item, index, container, "sorties")
                    elif item_type == "playlists":
                        _add_artist_playlist_result(self, item, index, container, "playlists")
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

def _create_artist_tabs(self):
        """Crée les onglets Musiques et Sorties dans la zone YouTube"""
        
        # Si on était déjà en mode artiste, détruire l'ancien notebook pour éviter la duplication
        if hasattr(self, 'artist_notebook') and self.artist_notebook:
            print("DEBUG: Destruction ancien notebook")
            try:
                # Détruire complètement l'ancien notebook et ses éléments
                parent = self.artist_notebook.master
                parent.destroy()  # Détruire le container complet pour éviter les boutons dupliqués
                self.artist_notebook = None
            except Exception as e:
                print(f"DEBUG: Erreur destruction notebook: {e}")
        
        # Nettoyer tout le contenu de youtube_results_frame
        for widget in self.youtube_results_frame.winfo_children():
            try:
                widget.destroy()
            except:
                pass
        
        # Cacher le canvas et la scrollbar des résultats
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas is not None:
            try:
                if self.youtube_canvas.winfo_exists():
                    self.youtube_canvas.pack_forget()
            except:
                pass
        
        if hasattr(self, 'scrollbar') and self.scrollbar is not None:
            try:
                if self.scrollbar.winfo_exists():
                    self.scrollbar.pack_forget()
            except:
                pass
        
        # Cacher aussi la frame thumbnail si elle est visible
        if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame is not None:
            try:
                if self.thumbnail_frame.winfo_exists():
                    self.thumbnail_frame.pack_forget()
            except:
                pass
        
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
                font=('TkDefaultFont', 10, 'bold'),
                width=20,
                height=20,
                command=self._return_to_search,
                cursor='hand2',
                takefocus=0
            )
        
        # Créer le notebook
        self.artist_notebook = ttk.Notebook(main_container, takefocus=0)
        self.artist_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Lier le changement d'onglet artiste pour gérer le bouton retour
        self.artist_notebook.bind("<<NotebookTabChanged>>", self.on_artist_tab_changed)
        
        # Positionner la croix au-dessus de tout (utiliser tkraise pour la mettre au premier plan)
        self.artist_close_btn.place(in_=main_container, relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)
        self.artist_close_btn.tkraise()  # Mettre le bouton au premier plan
        
        # Ajouter un tooltip au bouton croix
        try:
            from tooltip import create_tooltip
            create_tooltip(self.artist_close_btn, "Retourner à la recherche\nQuitte l'affichage de l'artiste et retourne aux résultats de recherche\n(Raccourci: Échap)")
        except:
            pass  # Si le tooltip ne peut pas être créé, continuer
        
        # Forcer la mise à jour pour s'assurer que le notebook est visible
        self.artist_notebook.update_idletasks()
        
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

def _on_channel_id_found(self, channel_id):
    """Appelé quand l'ID de la chaîne a été trouvé - lance les recherches de contenu"""
    if self.artist_search_cancelled:
        return
        
    # Sauvegarder l'ID
    self.current_artist_channel_id = channel_id
    
    # Mettre à jour le statut
    self.status_bar.config(text=f"Chargement du contenu de {self.current_artist_name}...")
    
    # Lancer les 3 recherches en parallèle avec un petit délai pour permettre à l'UI de respirer
    self.safe_after(100, lambda: _start_parallel_searches(self))

def _on_channel_id_error(self, error_msg="Impossible de trouver l'ID de la chaîne"):
        """Appelé en cas d'erreur lors de la recherche d'ID"""
        if self.artist_search_cancelled:
            return
            
        self.status_bar.config(text=f"Erreur: {error_msg}")
        
        # Afficher un message d'erreur dans les onglets
        _show_error_in_tabs(self, error_msg)

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
            'socket_timeout': 5,    # Timeout encore plus court
            'retries': 1,           # Moins de tentatives
            'fragment_retries': 1   # Moins de tentatives pour les fragments
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

def _add_artist_result(self, video, index, container):
        """Ajoute un résultat vidéo dans un onglet artiste"""
        try:
            title = video.get('title', 'Sans titre')
            duration = video.get('duration', 0)
            url = video.get('url', '')
            
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
            
            # Configuration de la grille (plus compact avec 2 lignes pour titre+date/durée)
            result_frame.columnconfigure(0, minsize=60, weight=0)  # Miniature plus petite
            result_frame.columnconfigure(1, weight=1)              # Titre et date/durée
            result_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur augmentée pour 2 lignes
            
            # Miniature (plus petite)
            thumbnail_label = tk.Label(
                result_frame,
                bg='#4a4a4a',
                width=8,
                height=2,
                text="🎵",
                fg='white',
                anchor='center',
                font=('TkDefaultFont', 8)
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=3)
            thumbnail_label.grid_propagate(False)
            
            # Charger la miniature en arrière-plan
            _load_artist_thumbnail(self, video, thumbnail_label)
            
            # Titre et durée (dans une frame verticale)
            text_frame = tk.Frame(result_frame, bg='#4a4a4a')
            text_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 5), pady=3)
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            text_frame.rowconfigure(1, weight=0)
            
            # Tronquer le titre s'il est trop long
            display_title = title
            if len(title) > 60:
                display_title = title[:57] + "..."
            
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
            
            # Durée sous le titre
            duration_text = time.strftime('%M:%S', time.gmtime(duration)) if duration > 0 else "?:?"
            
            duration_label = tk.Label(
                text_frame,
                text=duration_text,
                bg='#4a4a4a',
                fg='#aaaaaa',
                font=('TkDefaultFont', 7),
                anchor='w',
                justify='left'
            )
            duration_label.grid(row=1, column=0, sticky='ew', pady=(0, 1))
            
            # Stocker les données vidéo
            result_frame.video_data = video
            result_frame.title_label = title_label
            result_frame.duration_label = duration_label
            result_frame.thumbnail_label = thumbnail_label
            
            # Événements de clic pour la sélection multiple (comme dans _add_search_result)
            def on_result_click(event, frame=result_frame):
                # Initialiser le drag pour les vidéos
                self.drag_drop_handler.setup_drag_start(event, frame)
                
                # Vérifier si Shift est enfoncé pour la sélection multiple
                if event.state & 0x1:  # Shift est enfoncé
                    self.shift_selection_active = True
                    # Utiliser l'URL comme identifiant unique
                    video_url = frame.video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={frame.video_data.get('id')}"
                    self.toggle_item_selection(video_url, frame)
                else:
                    # Clic normal sans Shift - ne pas effacer la sélection si elle existe
                    pass
            
            def on_result_double_click(event, frame=result_frame):
                # Vérifier si Shift est enfoncé - ne rien faire sur double-clic avec Shift
                if event.state & 0x1:  # Shift est enfoncé
                    pass
                else:
                    # Télécharger la vidéo (sans ajouter à la playlist)
                    self._on_result_click(frame, add_to_playlist=False)
            
            # Effet hover
            def on_enter(event):
                # Vérifier l'URL pour la sélection
                video_url = result_frame.video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={result_frame.video_data.get('id')}"
                
                # Vérifier si l'élément est sélectionné
                if video_url in self.selected_items:
                    # Orange plus clair pour le hover d'un élément sélectionné
                    hover_color = '#ffb347'
                elif hasattr(result_frame, 'is_downloading') and result_frame.is_downloading:
                    # Rouge plus clair pour le hover pendant téléchargement
                    hover_color = '#ff8888'
                else:
                    # Couleur normale pour le hover
                    hover_color = '#5a5a5a'
                
                result_frame.configure(bg=hover_color)
                text_frame.configure(bg=hover_color)
                title_label.configure(bg=hover_color)
                duration_label.configure(bg=hover_color)
                thumbnail_label.configure(bg=hover_color)
            
            def on_leave(event):
                # Vérifier l'URL pour la sélection
                video_url = result_frame.video_data.get('webpage_url') or f"https://www.youtube.com/watch?v={result_frame.video_data.get('id')}"
                
                # Vérifier si l'élément est sélectionné
                if video_url in self.selected_items:
                    # Revenir à l'orange de sélection
                    leave_color = '#ff8c00'
                elif hasattr(result_frame, 'is_downloading') and result_frame.is_downloading:
                    # Revenir au rouge de téléchargement
                    leave_color = result_frame.download_color
                else:
                    # Couleur normale
                    leave_color = '#4a4a4a'
                
                result_frame.configure(bg=leave_color)
                text_frame.configure(bg=leave_color)
                title_label.configure(bg=leave_color)
                duration_label.configure(bg=leave_color)
                thumbnail_label.configure(bg=leave_color)
            
            # Bindings pour tous les événements (comme dans _add_search_result)
            all_widgets = [result_frame, text_frame, title_label, thumbnail_label, duration_label]
            
            for widget in all_widgets:
                # Hover
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                # Clic simple (sélection multiple avec Shift)
                widget.bind("<ButtonPress-1>", on_result_click)
                # Double-clic (téléchargement)
                widget.bind("<Double-1>", on_result_double_click)
                # Clic droit (menu playlists)
                widget.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            
            # Configuration du drag-and-drop
            self.drag_drop_handler.setup_drag_drop(
                result_frame, 
                video_data=video, 
                item_type="youtube"
            )
            
            # Tooltip avec toutes les interactions
            tooltip_text = f"Vidéo de {self.current_artist_name}\nDouble-clic: Télécharger\nDrag vers la droite: Télécharger et ajouter à la queue\nDrag vers la gauche: Télécharger et placer en premier dans la queue\nShift + Clic: Sélection multiple\nClic droit: Menu playlists"
            create_tooltip(result_frame, tooltip_text)
            create_tooltip(title_label, tooltip_text)
            
        except Exception as e:
            print(f"Erreur lors de l'ajout du résultat vidéo artiste: {e}")
def _load_artist_thumbnail(self, video, thumbnail_label):
        """Charge la miniature d'une vidéo d'artiste en arrière-plan"""
        def load_thumbnail():
            try:
                # Essayer différentes sources de miniatures
                thumbnail_url = None
                
                # 1. Essayer le champ 'thumbnail'
                if video.get('thumbnail'):
                    thumbnail_url = video['thumbnail']
                # 2. Essayer le champ 'thumbnails'
                elif video.get('thumbnails') and len(video['thumbnails']) > 0:
                    # Prendre la miniature de meilleure qualité disponible
                    thumbnails = video['thumbnails']
                    if len(thumbnails) > 1:
                        thumbnail_url = thumbnails[1]['url']  # Généralement meilleure qualité
                    else:
                        thumbnail_url = thumbnails[0]['url']
                # 3. Construire l'URL depuis l'ID vidéo
                elif video.get('id'):
                    thumbnail_url = f"https://img.youtube.com/vi/{video['id']}/mqdefault.jpg"
                
                if not thumbnail_url:
                    return
                
                # Télécharger l'image
                response = requests.get(thumbnail_url, timeout=10)
                if response.status_code == 200:
                    # Ouvrir l'image
                    image = Image.open(io.BytesIO(response.content))
                    
                    # Redimensionner en gardant le ratio (largeur fixe de 60px)
                    original_width, original_height = image.size
                    target_width = 60
                    target_height = int((target_width * original_height) / original_width)
                    image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    
                    # Convertir en PhotoImage
                    photo = ImageTk.PhotoImage(image)
                    
                    # Mettre à jour le label dans le thread principal
                    def update_thumbnail():
                        try:
                            if thumbnail_label.winfo_exists():
                                thumbnail_label.configure(image=photo, text="")
                                thumbnail_label.image = photo  # Garder une référence
                        except:
                            pass
                    
                    self.root.after(0, update_thumbnail)
                    
            except Exception as e:
                print(f"Erreur lors du chargement de la miniature artiste: {e}")
        
        # Lancer en arrière-plan
        threading.Thread(target=load_thumbnail, daemon=True).start()

def _load_playlist_count(self, playlist, count_label):
        """Charge le nombre de vidéos d'une playlist en arrière-plan"""
        def load_count():
            try:
                playlist_url = playlist.get('url', '') or playlist.get('webpage_url', '')
                if not playlist_url:
                    self.root.after(0, lambda: count_label.config(text="Playlist"))
                    return
                
                # Options pour récupérer seulement le nombre de vidéos
                count_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True
                }
                
                with YoutubeDL(count_opts) as ydl:
                    playlist_info = ydl.extract_info(playlist_url, download=False)
                    if playlist_info and 'entries' in playlist_info:
                        video_count = len(playlist_info['entries'])
                        count_text = f"{video_count} musiques" if video_count > 0 else "Playlist vide"
                    else:
                        count_text = "Playlist"
                    
                    # Mettre à jour le label dans le thread principal
                    def update_count():
                        try:
                            if count_label.winfo_exists():
                                count_label.config(text=count_text)
                        except:
                            pass
                    
                    self.root.after(0, update_count)
                    
            except Exception as e:
                print(f"Erreur lors du chargement du nombre de vidéos: {e}")
                self.root.after(0, lambda: count_label.config(text="Playlist"))
        
        # Lancer en arrière-plan
        threading.Thread(target=load_count, daemon=True).start()