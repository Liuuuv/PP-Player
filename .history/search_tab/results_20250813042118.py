import sys
import os
import time
import threading
import tkinter as tk

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier search_tab
from search_tab import *

def _update_search_results_ui(self):
    """Met à jour l'apparence des résultats en fonction de l'état de téléchargement"""
    # Vérifier si results_container existe (peut ne pas exister en mode artiste)
    if not hasattr(self, 'results_container') or not self.results_container.winfo_exists():
        return
    
    for child in self.results_container.winfo_children():
        if hasattr(child, 'video_data'):
            video = child.video_data
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            
            if url in self.current_downloads:
                # Apparence de téléchargement (rouge)
                child.config(bg='#ff6666')
                child.title_label.config(bg='#ff6666', fg='#cccccc')
                child.duration_label.config(bg='#ff6666', fg='#aaaaaa')
                child.thumbnail_label.config(bg='#ff6666')
            else:
                # Apparence normale
                child.config(bg='#4a4a4a')
                child.title_label.config(bg='#4a4a4a', fg='white')
                child.duration_label.config(bg='#4a4a4a', fg='#cccccc')
                child.thumbnail_label.config(bg='#4a4a4a')

def _load_more_search_results(self):
    """Charge plus de résultats pour la recherche actuelle (avec lazy loading)"""
    if (self.is_loading_more or 
        self.is_searching or
        self.search_cancelled or
        not self.current_search_query):
        return
    
    # Vérifier si on a encore des résultats locaux à afficher
    if self.search_results_count < len(self.all_search_results):
        self.is_loading_more = True
        self.current_search_batch += 1
        
        self.status_bar.config(text=f"Chargement du lot {self.current_search_batch}...")
        
        # Afficher le prochain lot depuis les résultats déjà stockés
        if not self.search_cancelled:
            self._display_batch_results(self.current_search_batch)
        
        self.is_loading_more = False
        
    # Si on a affiché tous les résultats locaux et qu'il y en a potentiellement plus
    elif self.has_more_results and self.total_available_results < self.max_search_results:
        self.is_loading_more = True
        self.status_bar.config(text="Recherche de plus de résultats...")
        
        # Enregistrer le temps de début pour le chargement de plus de résultats
        fetch_start_time = time.time()
        
        # Lancer une recherche pour plus de résultats en arrière-plan
        threading.Thread(
            target=self._fetch_more_results, 
            args=(self.current_search_query, self.total_available_results + self.lazy_load_increment, fetch_start_time),
            daemon=True
        ).start()

def _fetch_more_results(self, query, total_count, start_time=None):
    """Récupère plus de résultats depuis YouTube"""
    try:
        if self.search_cancelled:
            return
            
        search_opts = {
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
            'max_downloads': total_count,  # Chercher jusqu'au nombre total demandé
            'ignoreerrors': True
        }
        
        with YoutubeDL(search_opts) as ydl:
            if self.search_cancelled:
                return
                
            # Rechercher plus de résultats
            results = ydl.extract_info(f"ytsearch{total_count}:{query}", download=False)
            
            if self.search_cancelled:
                return
            
            if results and 'entries' in results:
                # Filtrer les nouveaux résultats
                all_filtered = self._filter_search_results(results['entries'])
                
                # Ne garder que les nouveaux résultats (ceux qu'on n'avait pas déjà)
                existing_urls = {result.get('url', '') for result in self.all_search_results}
                new_results = [r for r in all_filtered if r.get('url', '') not in existing_urls]
                
                if new_results and not self.search_cancelled:
                    # Ajouter les nouveaux résultats
                    self.all_search_results.extend(new_results)
                    self.total_available_results = len(self.all_search_results)
                    
                    # Vérifier s'il y a encore plus de résultats
                    self.has_more_results = len(results['entries']) >= total_count and len(self.all_search_results) < self.max_search_results
                    
                    # Afficher les nouveaux résultats
                    self.root.after(0, lambda: self._display_new_results(new_results))
                    
                    # Afficher le temps de chargement si disponible
                    if start_time:
                        fetch_duration = time.time() - start_time
                        self.last_search_time = fetch_duration  # Mettre à jour le temps de la dernière recherche
                        self.root.after(0, lambda: self._safe_status_update(
                            f"Chargement terminé - {len(new_results)} nouveaux résultats"
                        ))
                        self.root.after(0, self._update_stats_bar)
                else:
                    # Plus de nouveaux résultats
                    self.has_more_results = False
                    if start_time:
                        fetch_duration = time.time() - start_time
                        self.last_search_time = fetch_duration  # Mettre à jour le temps de la dernière recherche
                        self.root.after(0, lambda: self._safe_status_update(
                            f"Tous les résultats chargés"
                        ))
                        self.root.after(0, self._update_stats_bar)
                    else:
                        self.root.after(0, lambda: self._safe_status_update("Tous les résultats chargés"))
                    
    except Exception as e:
        if not self.search_cancelled:
            self.root.after(0, lambda: self._safe_status_update(f"Erreur chargement: {e}"))
    finally:
        self.is_loading_more = False

def _display_batch_results(self, batch_number):
    """Affiche un lot de 10 résultats"""
    # Vérifier si la recherche a été annulée
    if self.search_cancelled:
        return
        
    start_index = (batch_number - 1) * 10
    end_index = min(start_index + 10, len(self.all_search_results))
    
    # Si c'est le premier lot, afficher le canvas de résultats
    if batch_number == 1 and end_index > start_index:
        if not self.search_cancelled:
            self.root.after(0, self._show_search_results)
    
    # Afficher les résultats de ce lot
    for i in range(start_index, end_index):
        # Vérifier l'annulation à chaque itération
        if self.search_cancelled:
            return
            
        if i < len(self.all_search_results):
            video = self.all_search_results[i]
            if not self.search_cancelled:
                self.root.after(SEARCH_WAIT_TIME_BETWEEN_RESULTS, lambda v=video, idx=i: self._safe_add_search_result(v, idx))
                self.search_results_count += 1
    
    # Mettre à jour le statut seulement si pas annulé
    if not self.search_cancelled:
        self.root.after(0, lambda: self._safe_update_status(batch_number))
        # Mettre à jour le compteur de résultats
        self.root.after(0, self._update_results_counter)

def _display_new_results(self, new_results):
    """Affiche les nouveaux résultats obtenus"""
    if self.search_cancelled:
        return
        
    start_index = len(self.all_search_results) - len(new_results)
    for i, result in enumerate(new_results):
        if self.search_cancelled:
            break
        self.root.after(30 * i, lambda r=result, idx=start_index + i: self._safe_add_search_result(r, idx))
        self.search_results_count += 1
    
    # Mettre à jour le statut
    self.root.after(0, lambda: self._safe_status_update(f"{self.search_results_count} résultats affichés"))
    # Mettre à jour le compteur de résultats
    self.root.after(0, self._update_results_counter)

def _clear_results(self):
        """Vide le container de résultats et gère l'affichage des frames"""
        try:
            if hasattr(self, 'results_container') and self.results_container.winfo_exists():
                for widget in self.results_container.winfo_children():
                    try:
                        widget.destroy()
                    except:
                        pass
            
            if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
                self.youtube_canvas.yview_moveto(0)  # Remet le scroll en haut
                self.youtube_canvas.pack_forget()
            
            if hasattr(self, 'scrollbar') and self.scrollbar.winfo_exists():
                self.scrollbar.pack_forget()
            
            # Effacer le texte du compteur de résultats
            if hasattr(self, 'results_counter_label') and self.results_counter_label.winfo_exists():
                self.results_counter_label.config(text="")
                
            if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame.winfo_exists():
                self.thumbnail_frame.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Erreur lors du nettoyage des résultats: {e}")

def _show_search_results(self):
    """Affiche le canvas de résultats et masque la frame thumbnail"""
    try:
        if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame.winfo_exists():
            self.thumbnail_frame.pack_forget()
        
        if hasattr(self, 'scrollbar') and self.scrollbar.winfo_exists():
            self.scrollbar.pack(side="right", fill="y")
            
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
            self.youtube_canvas.pack(side="left", fill="both", expand=True)
        
        # Mettre à jour le compteur de résultats
        self._update_results_counter()
    except Exception as e:
        print(f"Erreur lors de l'affichage des résultats: {e}")

def _on_filter_change(self):
    """Appelée quand les cases à cocher changent"""
    # Si on a des résultats de recherche stockés, les refiltrer et réafficher
    if hasattr(self, 'all_raw_search_results') and self.all_raw_search_results:
        # Refiltrer les résultats bruts avec les nouveaux critères
        filtered_results = self._filter_search_results(self.all_raw_search_results)
        self.all_search_results = filtered_results[:self.max_search_results]
        
        # Effacer les résultats actuels
        self._clear_results()
        
        # Réinitialiser les compteurs
        self.search_results_count = 0
        self.current_search_batch = 1
        
        # Si aucun résultat après filtrage, afficher la miniature
        if not self.all_search_results:
            self.status_bar.config(text="Aucun résultat avec ces filtres")
            self._show_current_song_thumbnail()
            return
        
        # Afficher les résultats filtrés
        self._show_search_results()
        self._display_batch_results(1)

def _on_youtube_canvas_configure(self, event):
    """Vérifie si on doit charger plus de résultats quand le canvas change"""
    if self._should_load_more_results():
        self._load_more_search_results()

def _start_new_search(self):
    """Démarre une nouvelle recherche après avoir annulé la précédente"""
    query = self.youtube_entry.get().strip()
    if not query:
        # Si la recherche est vide, afficher la miniature
        self._clear_results()
        self._show_current_song_thumbnail()
        return
    
    # Incrémenter le compteur de recherches
    self.stats['searches_count'] += 1
    
    # Enregistrer le temps de début de recherche
    self.search_start_time = time.time()
    
    # Nouvelle recherche - réinitialiser les compteurs et flags
    self.search_cancelled = False
    self.current_search_query = query
    self.search_results_count = 0
    self.is_loading_more = False
    self.current_search_batch = 1
    self.all_search_results = []  # Stocker tous les résultats filtrés
    self.all_raw_search_results = []  # Stocker tous les résultats bruts
    
    # Réinitialiser le compteur de résultats
    if hasattr(self, 'results_counter_label'):
        self.results_counter_label.config(text="")
    
    # Effacer les résultats précédents
    self._clear_results()
    self.search_list = []
    self.status_bar.config(text="Recherche en cours...")
    self.root.update()
    
    self.is_searching = True
    
    # Lancer une recherche initiale de 10 résultats
    self.current_search_thread = threading.Thread(target=self._perform_initial_search, args=(query,), daemon=True)
    self.current_search_thread.start()

def _filter_search_results(self, entries):
    """Filtre les résultats selon les cases à cocher Artists et Tracks"""
    if not entries:
        return []
    
    filtered_results = []
    show_artists = getattr(self, 'show_artists', None)
    show_tracks = getattr(self, 'show_tracks', None)
    
    # Si les variables n'existent pas encore (première recherche), tout afficher
    if show_artists is None or show_tracks is None:
        show_artists_val = True
        show_tracks_val = True
    else:
        show_artists_val = show_artists.get()
        show_tracks_val = show_tracks.get()
    
    for entry in entries:
        if not entry:
            continue
                    
        url = entry.get('url', '')
        duration = entry.get('duration', 0)
        
        # Identifier le type de contenu
        is_video = "https://www.youtube.com/watch?v=" in url
        is_channel = "https://www.youtube.com/channel/" in url or "https://www.youtube.com/@" in url
        
        # Filtrer selon les préférences
        if is_video and show_tracks_val and duration <= 600.0:  # Vidéos (tracks) max 10 minutes
            filtered_results.append(entry)
        elif is_channel and show_artists_val:  # Chaînes (artists)
            filtered_results.append(entry)
    return filtered_results

def _perform_initial_search(self, query):
    """Effectue une recherche initiale de 10 résultats seulement"""
    try:
        # Vérifier si la recherche a été annulée avant de commencer
        if self.search_cancelled:
            return
            
        search_opts = {
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
            'max_downloads': self.initial_search_count,  # Chercher seulement 10 résultats initialement
            'ignoreerrors': True
        }
        
        with YoutubeDL(search_opts) as ydl:
            # Vérifier l'annulation avant la recherche
            if self.search_cancelled:
                return
                
            # Recherche initiale de 10 résultats
            results = ydl.extract_info(f"ytsearch{self.initial_search_count}:{query}", download=False)
            
            # Vérifier l'annulation après la recherche
            if self.search_cancelled:
                return
            
            if not results or 'entries' not in results:
                if not self.search_cancelled:
                    self.root.after(0, lambda: self._safe_status_update("Aucun résultat trouvé"))
                    self.root.after(0, self._show_current_song_thumbnail)
                return
            
            # Vérifier l'annulation avant le traitement des résultats
            if self.search_cancelled:
                return
            
            # Nettoyer le container
            if not self.search_cancelled:
                self.root.after(0, self._clear_results)
            
            # Stocker les résultats bruts pour le filtrage ultérieur
            self.all_raw_search_results = results['entries']
            
            # Filtrer selon les cases à cocher
            filtered_results = self._filter_search_results(results['entries'])
            
            # Vérifier l'annulation après le filtrage
            if self.search_cancelled:
                return
            
            # video_results = [
            #     entry for entry in results['entries']
            #     if (entry and entry.get('duration', 0) <= 600.0)  # Durée max de 10 minutes
            # ]
            
            # Stocker les résultats initiaux
            self.all_search_results = filtered_results
            
            # Indiquer qu'il y a potentiellement plus de résultats si on a obtenu le nombre maximum demandé
            self.has_more_results = len(results['entries']) >= self.initial_search_count
            self.total_available_results = len(self.all_search_results)
            
            # Si aucun résultat après filtrage, afficher la miniature
            if not self.all_search_results:
                if not self.search_cancelled:
                    self.root.after(0, lambda: self._safe_status_update("Aucun résultat trouvé"))
                    self.root.after(0, self._show_current_song_thumbnail)
                return
            
            # Vérifier l'annulation avant l'affichage
            if self.search_cancelled:
                return
            
            # Afficher les résultats initiaux
            self._display_batch_results(1)
            
            # Calculer et afficher le temps de recherche
            if self.search_start_time and not self.search_cancelled:
                search_duration = time.time() - self.search_start_time
                self.last_search_time = search_duration
                self.root.after(0, lambda: self._safe_status_update(
                    f"Recherche terminée - {len(self.all_search_results)} résultats trouvés"
                ))
                self.root.after(0, self._update_stats_bar)
            
    except Exception as e:
        if not self.search_cancelled:
            error_msg = f"Erreur recherche: {e}"
            self.root.after(0, lambda: self._safe_status_update(error_msg))
    finally:
        # Ne réinitialiser les flags que si la recherche n'a pas été annulée
        if not self.search_cancelled:
            self.is_searching = False
            self.is_loading_more = False
        self.current_search_thread = None
        
def _save_current_search_state(self):
        """Sauvegarde l'état actuel des résultats de recherche"""
        self.saved_search_state = {
            'scroll_position': None,
            'canvas_packed': False,
            'scrollbar_packed': False,
            'thumbnail_packed': False
        }
        
        # Sauvegarder la position de scroll
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
            try:
                scroll_top, scroll_bottom = self.youtube_canvas.yview()
                self.saved_search_state['scroll_position'] = (scroll_top, scroll_bottom)
                # Vérifier si le canvas est actuellement affiché
                self.saved_search_state['canvas_packed'] = bool(self.youtube_canvas.winfo_manager())
            except:
                pass
        
        # Sauvegarder l'état de la scrollbar
        if hasattr(self, 'scrollbar') and self.scrollbar.winfo_exists():
            self.saved_search_state['scrollbar_packed'] = bool(self.scrollbar.winfo_manager())
        
        # Sauvegarder l'état de la thumbnail frame
        if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame.winfo_exists():
            self.saved_search_state['thumbnail_packed'] = bool(self.thumbnail_frame.winfo_manager())

def _on_search_entry_change(self, event):
    """Appelée quand le contenu du champ de recherche change"""
    query = self.youtube_entry.get().strip()
    
    # Si le champ devient vide, afficher la miniature seulement s'il y a une chanson en cours
    if not query:
        # Annuler toute recherche en cours
        if self.is_searching:
            self.search_cancelled = True
        
        # Vider les résultats de recherche
        self._clear_results()
        
        # Réinitialiser les variables de recherche
        self.current_search_query = ""
        self.search_results_count = 0
        self.current_search_batch = 1
        self.all_search_results = []
        self.is_searching = False
        self.is_loading_more = False
        self.search_cancelled = False
        self.current_search_thread = None
        
        # Afficher la miniature de la chanson en cours seulement s'il y en a une
        if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
            self._show_current_song_thumbnail()
        else:
            # Nettoyer complètement la frame thumbnail s'il n'y a pas de chanson
            if hasattr(self, 'thumbnail_frame'):
                try:
                    # Vérifier que la frame existe encore et est valide
                    if self.thumbnail_frame and self.thumbnail_frame.winfo_exists():
                        for widget in self.thumbnail_frame.winfo_children():
                            widget.destroy()
                except (tk.TclError, AttributeError):
                    # La frame n'existe plus ou est invalide, l'ignorer
                    pass

def _clear_youtube_search(self):
    """Efface la recherche YouTube et vide les résultats"""
    # Si on est en mode artiste, juste vider le champ de recherche sans revenir à la recherche normale
    if hasattr(self, 'artist_mode') and self.artist_mode:
        self.youtube_entry.delete(0, tk.END)
        return  # Ne pas fermer les onglets artiste
    
    # Annuler toute recherche en cours
    if self.is_searching:
        self.search_cancelled = True
        
    self.youtube_entry.delete(0, tk.END)
    
    # Vider les résultats de recherche en utilisant la fonction appropriée
    self._clear_results()
    
    # Réinitialiser les variables de recherche
    self.current_search_query = ""
    self.search_results_count = 0
    self.current_search_batch = 1
    self.all_search_results = []
    self.is_searching = False
    self.is_loading_more = False
    self.search_cancelled = False
    self.current_search_thread = None
    
    # Afficher la miniature de la chanson en cours quand il n'y a pas de résultats
    self._show_current_song_thumbnail()

def _show_current_song_thumbnail(self):
    """Affiche la miniature de la chanson en cours dans la frame dédiée"""
    # Vérifier que thumbnail_frame existe
    if not hasattr(self, 'thumbnail_frame'):
        return
    
    # Nettoyer la frame précédente
    try:
        if self.thumbnail_frame.winfo_exists():
            for widget in self.thumbnail_frame.winfo_children():
                try:
                    if widget.winfo_exists():
                        widget.destroy()
                except tk.TclError:
                    continue
    except tk.TclError:
        # Thumbnail frame détruit, ignorer
        return
        
    if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
        current_song = self.main_playlist[self.current_index]
        
        # Label pour la miniature - collé au côté gauche
        thumbnail_label = tk.Label(
            self.thumbnail_frame,
            bg='#3d3d3d',
            text="♪",
            fg='#666666',
            font=('TkDefaultFont', 60),
            width=300,
            height=300
        )
        # Pack à gauche sans padding pour coller au bord
        thumbnail_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Charger la vraie miniature si elle existe (version grande et carrée)
        self._load_large_thumbnail(current_song, thumbnail_label)
        
    else:
        # Aucune chanson en cours - juste une grande icône musicale
        no_song_label = tk.Label(
            self.thumbnail_frame,
            text="♪",
            bg='#3d3d3d',
            fg='#666666',
            font=('TkDefaultFont', 60),
            width=300,
            height=300
        )
        # Pack à gauche sans padding pour coller au bord
        no_song_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)

def _load_large_thumbnail(self, filepath, label):
    """Charge une grande miniature carrée pour l'affichage principal"""
    # Chercher une image associée (même nom mais extension image)
    base_name = os.path.splitext(filepath)[0]
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    
    thumbnail_found = False
    for ext in image_extensions:
        thumbnail_path = base_name + ext
        if os.path.exists(thumbnail_path):
            try:
                img = Image.open(thumbnail_path)
                
                # Créer une image carrée en cropant au centre
                width, height = img.size
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                right = left + size
                bottom = top + size
                
                # Crop au centre pour faire un carré
                img_cropped = img.crop((left, top, right, bottom))

                # Redimensionner à une grande taille (370x370)
                img_resized = img_cropped.resize((370, 370), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img_resized)
                label.configure(image=photo,
                                text="",
                                width=300,
                                height=300
                )
                label.image = photo
                thumbnail_found = True
                break
            except Exception as e:
                print(f"Erreur chargement grande miniature: {e}")
                continue
    
    if not thumbnail_found:
        # Garder l'icône par défaut
        pass
