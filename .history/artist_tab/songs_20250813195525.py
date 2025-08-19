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
                
                # Supprimer les doublons et préparer pour l'affichage
                unique_videos = {}
                for video in all_videos:
                    video_id = video.get('id', '')
                    if video_id and video_id not in unique_videos:
                        # S'assurer que les champs nécessaires sont présents
                        if not video.get('webpage_url') and video_id:
                            video['webpage_url'] = f"https://www.youtube.com/watch?v={video_id}"
                        unique_videos[video_id] = video
                
                final_videos = list(unique_videos.values())
                
                # Trier par date de sortie (les plus récentes d'abord) si disponible
                def get_upload_date(video):
                    upload_date = video.get('upload_date', '0')
                    try:
                        return int(upload_date) if upload_date.isdigit() else 0
                    except:
                        return 0
                
                final_videos.sort(key=get_upload_date, reverse=True)
                
                # Limiter à 15 vidéos max
                final_videos = final_videos[:15]
                
                # Vérifier annulation avant affichage
                if not self.artist_search_cancelled:
                    # Sauvegarder en cache
                    cache_key = self.current_artist_channel_id
                    if cache_key not in self.artist_cache:
                        self.artist_cache[cache_key] = {}
                    self.artist_cache[cache_key]['videos'] = final_videos
                    
                    # Afficher les résultats dans l'interface
                    self.root.after(0, lambda: _display_artist_videos(self, final_videos))
                    
        except Exception as e:
            self.root.after(0, lambda: _display_videos_error(self, str(e)))

def _display_artist_videos(self, videos):
        """Affiche les vidéos de l'artiste dans l'onglet Musiques"""
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
        
        self.status_bar.config(text=f"{len(videos)} musiques trouvées pour {self.current_artist_name}")

def _display_videos_error(self, error_msg):
        """Affiche une erreur dans l'onglet Musiques"""
        # Supprimer le message de chargement
        if hasattr(self, 'musiques_loading'):
            self.musiques_loading.destroy()
        
        error_label = tk.Label(
            self.musiques_frame,
            text=f"Erreur lors du chargement des musiques:\n{error_msg}",
            bg='#3d3d3d',
            fg='#ff6666',
            font=('TkDefaultFont', 10),
            justify='center'
        )
        error_label.pack(expand=True)