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

# Import direct de create_tooltip pour éviter les erreurs
try:
    from tooltip import create_tooltip
except ImportError:
    # Fonction de fallback si create_tooltip n'est pas disponible
    def create_tooltip(widget, text):
        pass

def _ensure_results_container_exists(self):
    """S'assure que le results_container existe, le recrée si nécessaire"""
    if not hasattr(self, 'results_container') or not self.results_container.winfo_exists():
        print("DEBUG: Recréation du results_container...")
        try:
            # Vérifier que youtube_canvas existe, sinon le recréer
            if not hasattr(self, 'youtube_canvas') or not self.youtube_canvas.winfo_exists():
                print("DEBUG: youtube_canvas n'existe pas, recréation...")
                _recreate_youtube_canvas(self)
            
            # Maintenant recréer le results_container
            if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
                # Recréer le results_container
                self.results_container = ttk.Frame(self.youtube_canvas)
                self.youtube_canvas.create_window((0, 0), window=self.results_container, anchor="nw")
                
                # Rebinder les événements
                self.results_container.bind(
                    "<Configure>",
                    lambda e: self.youtube_canvas.configure(
                        scrollregion=self.youtube_canvas.bbox("all")
                    )
                )
                
                # Rebinder la molette de souris
                if hasattr(self, '_bind_mousewheel'):
                    self._bind_mousewheel(self.results_container, self.youtube_canvas)
                
                print("DEBUG: results_container recréé avec succès")
            else:
                print("DEBUG: Impossible de recréer youtube_canvas")
        except Exception as e:
            print(f"DEBUG: Erreur lors de la recréation du results_container: {e}")

def _recreate_youtube_canvas(self):
    """Recrée le youtube_canvas si nécessaire"""
    try:
        # Vérifier que youtube_results_frame existe
        if not hasattr(self, 'youtube_results_frame') or not self.youtube_results_frame.winfo_exists():
            print("DEBUG: youtube_results_frame n'existe pas, impossible de recréer youtube_canvas")
            return
        
        print("DEBUG: Recréation du youtube_canvas...")
        
        # Créer le canvas
        self.youtube_canvas = tk.Canvas(
            self.youtube_results_frame,
            bg='#3d3d3d',
            highlightthickness=0
        )
        
        # Créer la scrollbar si elle n'existe pas
        if not hasattr(self, 'youtube_scrollbar') or not self.youtube_scrollbar.winfo_exists():
            self.youtube_scrollbar = ttk.Scrollbar(
                self.youtube_results_frame,
                orient="vertical",
                command=self.youtube_canvas.yview
            )
            self.youtube_scrollbar.pack(side="right", fill="y")
        
        # Configurer le canvas
        self.youtube_canvas.configure(yscrollcommand=self.youtube_scrollbar.set)
        self.youtube_canvas.pack(side="left", fill="both", expand=True)
        
        print("DEBUG: youtube_canvas recréé avec succès")
        
    except Exception as e:
        print(f"DEBUG: Erreur lors de la recréation du youtube_canvas: {e}")

def _update_search_results_ui(self):
    """Met à jour l'apparence des résultats en fonction de l'état de téléchargement"""
    # Vérifier si results_container existe (peut ne pas exister en mode artiste)
    if not hasattr(self, 'results_container') or not self.results_container.winfo_exists():
        # Essayer de recréer le results_container si nécessaire
        _ensure_results_container_exists(self)
        if not hasattr(self, 'results_container') or not self.results_container.winfo_exists():
            return
    
    try:
        children = self.results_container.winfo_children()
    except tk.TclError:
        # Erreur lors de l'accès aux enfants, ignorer
        return
        
    for child in children:
        try:
            if child.winfo_exists() and hasattr(child, 'video_data'):
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
        except tk.TclError:
            # Widget détruit, ignorer
            continue

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
        if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame is not None:
            try:
                if self.thumbnail_frame.winfo_exists():
                    self.thumbnail_frame.pack_forget()
            except Exception as e:
                pass
        
        if hasattr(self, 'scrollbar') and self.scrollbar is not None:
            try:
                if self.scrollbar.winfo_exists():
                    self.scrollbar.pack(side="right", fill="y")
            except Exception as e:
                pass
            
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas is not None:
            try:
                if self.youtube_canvas.winfo_exists():
                    self.youtube_canvas.pack(side="left", fill="both", expand=True)
            except Exception as e:
                pass
        
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
            'thumbnail_packed': False,
            'search_query': '',
            'search_results': [],
            'current_search_batch': 1,
            'has_more_results': False
        }
        
        # Sauvegarder la requête de recherche actuelle
        if hasattr(self, 'youtube_entry') and self.youtube_entry.winfo_exists():
            self.saved_search_state['search_query'] = self.youtube_entry.get().strip()
        
        # Sauvegarder les résultats de recherche actuels
        if hasattr(self, 'all_search_results'):
            self.saved_search_state['search_results'] = self.all_search_results.copy()
        
        # Sauvegarder l'état de pagination
        if hasattr(self, 'current_search_batch'):
            self.saved_search_state['current_search_batch'] = self.current_search_batch
        if hasattr(self, 'has_more_results'):
            self.saved_search_state['has_more_results'] = self.has_more_results
        
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
        
        print(f"DEBUG: État de recherche sauvegardé - Query: '{self.saved_search_state['search_query']}', Results: {len(self.saved_search_state['search_results'])}")

def _on_search_entry_change(self, event):
    """Appelée quand le contenu du champ de recherche change (avec debounce)"""
    # Éviter les recherches redondantes - ne déclencher que si le contenu a vraiment changé
    current_query = self.youtube_entry.get().strip()
    if hasattr(self, '_last_youtube_search_query') and self._last_youtube_search_query == current_query:
        return
    
    # Filtrer les touches qui ne modifient pas le contenu
    if event:
        ignored_keys = {
            'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R',
            'Super_L', 'Super_R', 'Meta_L', 'Meta_R', 'Win_L', 'Win_R',
            'Up', 'Down', 'Left', 'Right', 'Home', 'End', 'Page_Up', 'Page_Down',
            'Insert', 'Delete', 'Tab', 'Escape', 'F1', 'F2', 'F3', 'F4', 'F5',
            'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'Caps_Lock', 'Num_Lock',
            'Scroll_Lock', 'Print', 'Pause', 'Menu'
        }
        
        if event.keysym in ignored_keys:
            return
    
    # Annuler le timer précédent s'il existe
    if hasattr(self, '_search_timer') and self._search_timer:
        self.root.after_cancel(self._search_timer)
    
    # Calculer le délai adaptatif basé sur la longueur de la requête
    def get_adaptive_delay(query_length):
        if query_length == 0:
            return 0  # Immédiat pour vider
        elif query_length <= 2:
            return 500  # Plus long pour éviter les recherches sur 1-2 lettres
        elif query_length <= 4:
            return 300  # Moyen pour les mots courts
        else:
            return 200  # Plus court pour les recherches plus longues
    
    delay = get_adaptive_delay(len(current_query))
    
    # Programmer la recherche avec délai adaptatif
    self._search_timer = self.root.after(delay, lambda: _execute_search_change(self, current_query))

def _execute_search_change(self, query):
    """Exécute le changement de recherche après le délai"""
    # Vérifier que la requête n'a pas changé entre temps
    current_query = self.youtube_entry.get().strip()
    if current_query != query:
        return
    
    # Marquer cette requête comme traitée
    self._last_youtube_search_query = current_query
    
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
        return
    
    # Si on arrive ici, il y a une requête non vide
    # Ne pas lancer la recherche automatiquement - attendre Entrée ou clic sur Search
    # Juste mettre à jour la variable pour éviter les recherches redondantes
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
    
    # Utiliser la nouvelle logique centralisée pour gérer l'affichage de la miniature
    import search_tab.core
    search_tab.core.handle_search_clear(self)

def _show_current_song_thumbnail(self):
    """Affiche la miniature de la chanson en cours dans la frame dédiée"""
    print("DEBUG: === DÉBUT _show_current_song_thumbnail ===")
    
    # Utiliser la nouvelle logique centralisée pour déterminer si on doit afficher la miniature
    import search_tab.core
    if not search_tab.core.should_show_large_thumbnail(self):
        return
    
    # Vérifier que thumbnail_frame existe et est accessible
    if not hasattr(self, 'thumbnail_frame'):
        print("DEBUG: thumbnail_frame n'existe pas comme attribut")
        # Essayer de recréer la frame
        if hasattr(self, '_recreate_thumbnail_frame'):
            print("DEBUG: tentative de recréation via _recreate_thumbnail_frame")
            self._recreate_thumbnail_frame()
        else:
            print("DEBUG: impossible de recréer, _recreate_thumbnail_frame n'existe pas")
            return
        
    try:
        if not self.thumbnail_frame.winfo_exists():
            print("DEBUG: thumbnail_frame existe comme attribut mais widget détruit")
            # Essayer de recréer la frame
            if hasattr(self, '_recreate_thumbnail_frame'):
                print("DEBUG: tentative de recréation via _recreate_thumbnail_frame")
                self._recreate_thumbnail_frame()
            else:
                print("DEBUG: impossible de recréer, _recreate_thumbnail_frame n'existe pas")
                return
        else:
            print("DEBUG: thumbnail_frame existe et le widget est valide")
    except tk.TclError as e:
        print(f"DEBUG: TclError avec thumbnail_frame: {e}")
        # Thumbnail frame détruit, essayer de la recréer
        if hasattr(self, '_recreate_thumbnail_frame'):
            print("DEBUG: tentative de recréation via _recreate_thumbnail_frame")
            self._recreate_thumbnail_frame()
        else:
            print("DEBUG: impossible de recréer, _recreate_thumbnail_frame n'existe pas")
            return
    except Exception as e:
        print(f"DEBUG: Exception dans vérification thumbnail_frame: {e}")
        return
    
    # Nettoyer la frame précédente
    try:
        if self.thumbnail_frame.winfo_exists():
            children = self.thumbnail_frame.winfo_children()
            for widget in children:
                try:
                    if widget.winfo_exists():
                        widget.destroy()
                except tk.TclError:
                    continue
        else:
            return
    except tk.TclError:
        # Thumbnail frame détruit, ignorer
        return
    
    # Debug: Vérifier l'état de la playlist et de la chanson courante
    print(f"DEBUG: main_playlist length: {len(self.main_playlist)}")
    print(f"DEBUG: current_index: {self.current_index}")
    print(f"DEBUG: current_playlist_name: {getattr(self, 'current_playlist_name', 'NONE')}")
    print(f"DEBUG: playlists keys: {list(getattr(self, 'playlists', {}).keys())}")
    if hasattr(self, 'playlists') and hasattr(self, 'current_playlist_name'):
        playlist_content = self.playlists.get(self.current_playlist_name, [])
        print(f"DEBUG: playlists[current_playlist_name] length: {len(playlist_content)}")
        if len(playlist_content) > 0:
            print(f"DEBUG: playlists[current_playlist_name][0]: {playlist_content[0]}")
    
    if hasattr(self, 'main_playlist') and len(self.main_playlist) > 0:
        print(f"DEBUG: main_playlist[0]: {self.main_playlist[0]}")
        if self.current_index < len(self.main_playlist):
            print(f"DEBUG: current_song serait: {self.main_playlist[self.current_index]}")
    
    # Debug: Vérifier l'état de la musique pygame
    try:
        is_playing = pygame.mixer.music.get_busy()
        print(f"DEBUG: pygame music is busy: {is_playing}")
    except Exception as e:
        print(f"DEBUG: Erreur pygame: {e}")
        
    if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
        current_song = self.main_playlist[self.current_index]
        print(f"DEBUG: Affichage miniature pour chanson: {current_song}")
        
        try:
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
            print("DEBUG: Label miniature chanson créé et packé avec succès")
            
            # Charger la vraie miniature si elle existe (version grande et carrée)
            self._load_large_thumbnail(current_song, thumbnail_label)
            print("DEBUG: Tentative de chargement de la vraie miniature")
        except tk.TclError as e:
            # Erreur lors de la création du label, ignorer
            print(f"DEBUG: TclError lors de la création du label chanson: {e}")
        except Exception as e:
            print(f"DEBUG: Exception lors de la création du label chanson: {e}")
        
    else:
        print("DEBUG: Aucune chanson en cours, affichage miniature par défaut")
        try:
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
            print("DEBUG: Label miniature par défaut créé et packé avec succès")
        except tk.TclError as e:
            # Erreur lors de la création du label, ignorer
            print(f"DEBUG: TclError lors de la création du label par défaut: {e}")
        except Exception as e:
            print(f"DEBUG: Exception lors de la création du label par défaut: {e}")
    
    print("DEBUG: === FIN _show_current_song_thumbnail ===")

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
                try:
                    if label.winfo_exists():
                        label.configure(image=photo,
                                        text="",
                                        width=300,
                                        height=300
                        )
                        label.image = photo
                        thumbnail_found = True
                except tk.TclError:
                    # Label détruit, ignorer
                    pass
                break
            except Exception as e:
                print(f"Erreur chargement grande miniature: {e}")
                continue
    
    if not thumbnail_found:
        # Garder l'icône par défaut
        pass

def _return_to_search(self):
    """Retourne instantanément à l'affichage de recherche normal"""
    try:
        print("DEBUG: === DÉBUT _return_to_search ===")
        
        # Remettre à zéro les variables d'état des onglets artiste
        self.artist_tab_active_sorties = False
        self.artist_tab_active_playlists = False
        
        # Debug: Lister tous les widgets présents dans youtube_results_frame AVANT nettoyage
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = self.youtube_results_frame.winfo_children()
                print(f"DEBUG: Widgets dans youtube_results_frame AVANT nettoyage: {len(children)}")
                for i, child in enumerate(children):
                    try:
                        widget_class = child.__class__.__name__
                        widget_info = f"  - Widget {i}: {widget_class}"
                        if hasattr(child, 'winfo_name'):
                            widget_info += f" (name: {child.winfo_name()})"
                        if hasattr(child, 'cget'):
                            try:
                                bg = child.cget('bg')
                                widget_info += f" (bg: {bg})"
                            except:
                                pass
                        print(f"DEBUG: {widget_info}")
                    except Exception as e:
                        print(f"DEBUG:   - Widget {i}: ERREUR - {e}")
            except Exception as e:
                print(f"DEBUG: Erreur lors du listage des widgets avant: {e}")
        
        # Annuler toutes les recherches artiste en cours
        self.artist_search_cancelled = True
        
        # Annuler aussi toute recherche normale en cours pour éviter les conflits
        if hasattr(self, 'is_searching') and self.is_searching:
            self.search_cancelled = True
        
        # Sortir du mode artiste
        self.artist_mode = False
        self.current_artist_name = ""
        self.current_artist_channel_url = ""
        self.current_artist_channel_id = None
        
        # Remettre l'état du contenu de playlist à zéro
        if hasattr(self, '_reset_playlist_content_state'):
            self._reset_playlist_content_state()
        
        # Supprimer le notebook artiste et la croix
        print("DEBUG: Suppression du notebook artiste...")
        if hasattr(self, 'artist_notebook'):
            try:
                if self.artist_notebook.winfo_exists():
                    print("DEBUG: artist_notebook existe, destruction...")
                    self.artist_notebook.destroy()
                    print("DEBUG: artist_notebook détruit")
                else:
                    print("DEBUG: artist_notebook n'existe plus")
                delattr(self, 'artist_notebook')
                print("DEBUG: attribut artist_notebook supprimé")
            except Exception as e:
                print(f"DEBUG: Erreur suppression artist_notebook: {e}")
        
        # Supprimer la croix si elle existe
        print("DEBUG: Suppression du bouton croix artiste...")
        if hasattr(self, 'artist_close_btn'):
            try:
                if self.artist_close_btn.winfo_exists():
                    print("DEBUG: artist_close_btn existe, destruction...")
                    self.artist_close_btn.destroy()
                    print("DEBUG: artist_close_btn détruit")
                else:
                    print("DEBUG: artist_close_btn n'existe plus")
                delattr(self, 'artist_close_btn')
                print("DEBUG: attribut artist_close_btn supprimé")
            except Exception as e:
                print(f"DEBUG: Erreur suppression artist_close_btn: {e}")
        
        # Supprimer le bouton retour playlist si il existe
        print("DEBUG: Suppression du bouton retour playlist...")
        if hasattr(self, 'artist_tab_back_btn') and self.artist_tab_back_btn:
            try:
                if self.artist_tab_back_btn.winfo_exists():
                    print("DEBUG: artist_tab_back_btn existe, destruction...")
                    self.artist_tab_back_btn.destroy()
                    print("DEBUG: artist_tab_back_btn détruit")
                else:
                    print("DEBUG: artist_tab_back_btn n'existe plus")
                self.artist_tab_back_btn = None
                print("DEBUG: attribut artist_tab_back_btn remis à None")
            except Exception as e:
                print(f"DEBUG: Erreur suppression artist_tab_back_btn: {e}")
        
        # Debug: Lister tous les widgets présents dans youtube_results_frame APRÈS suppression des widgets artiste
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = self.youtube_results_frame.winfo_children()
                print(f"DEBUG: Widgets dans youtube_results_frame APRÈS suppression widgets artiste: {len(children)}")
                for i, child in enumerate(children):
                    try:
                        widget_class = child.__class__.__name__
                        widget_info = f"  - Widget {i}: {widget_class}"
                        if hasattr(child, 'winfo_name'):
                            widget_info += f" (name: {child.winfo_name()})"
                        if hasattr(child, 'cget'):
                            try:
                                bg = child.cget('bg')
                                widget_info += f" (bg: {bg})"
                            except:
                                pass
                        print(f"DEBUG: {widget_info}")
                    except Exception as e:
                        print(f"DEBUG:   - Widget {i}: ERREUR - {e}")
            except Exception as e:
                print(f"DEBUG: Erreur lors du listage des widgets après suppression: {e}")
        
        # CORRECTION: Nettoyer tous les frames enfants non essentiels de youtube_results_frame
        print("DEBUG: Nettoyage des frames enfants non essentiels...")
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = list(self.youtube_results_frame.winfo_children())
                for child in children:
                    try:
                        # Garder seulement les widgets essentiels
                        if (child == getattr(self, 'thumbnail_frame', None) or
                            child == getattr(self, 'youtube_canvas', None) or
                            child == getattr(self, 'scrollbar', None)):
                            print(f"DEBUG: Conservation du widget essentiel: {child.__class__.__name__}")
                            continue
                        
                        # Supprimer tous les autres frames (main_container et autres)
                        print(f"DEBUG: Suppression du widget non essentiel: {child.__class__.__name__} (name: {child.winfo_name()})")
                        child.destroy()
                        
                    except Exception as e:
                        print(f"DEBUG: Erreur lors de la suppression d'un widget: {e}")
            except Exception as e:
                print(f"DEBUG: Erreur lors du nettoyage des frames: {e}")
        
        # Debug: Lister les widgets APRÈS nettoyage complet
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = self.youtube_results_frame.winfo_children()
                print(f"DEBUG: Widgets dans youtube_results_frame APRÈS nettoyage complet: {len(children)}")
                for i, child in enumerate(children):
                    try:
                        widget_class = child.__class__.__name__
                        widget_info = f"  - Widget {i}: {widget_class}"
                        if hasattr(child, 'winfo_name'):
                            widget_info += f" (name: {child.winfo_name()})"
                        if hasattr(child, 'cget'):
                            try:
                                bg = child.cget('bg')
                                widget_info += f" (bg: {bg})"
                            except:
                                pass
                        print(f"DEBUG: {widget_info}")
                    except Exception as e:
                        print(f"DEBUG:   - Widget {i}: ERREUR - {e}")
            except Exception as e:
                print(f"DEBUG: Erreur lors du listage final: {e}")
        
        # Restaurer l'état original des résultats de recherche
        had_search_results = False
        if hasattr(self, 'saved_search_state'):
            print(f"DEBUG: Restauration de l'état de recherche - Query: '{self.saved_search_state.get('search_query', '')}', Results: {len(self.saved_search_state.get('search_results', []))}")
            
            # Restaurer les données de recherche
            saved_query = self.saved_search_state.get('search_query', '')
            saved_results = self.saved_search_state.get('search_results', [])
            saved_batch = self.saved_search_state.get('current_search_batch', 1)
            saved_has_more = self.saved_search_state.get('has_more_results', False)
            
            # Restaurer la requête dans le champ de recherche
            if saved_query and hasattr(self, 'youtube_entry') and self.youtube_entry.winfo_exists():
                self.youtube_entry.delete(0, tk.END)
                self.youtube_entry.insert(0, saved_query)
            
            # Restaurer les résultats de recherche
            if saved_results:
                self.all_search_results = saved_results.copy()
                self.current_search_batch = saved_batch
                self.has_more_results = saved_has_more
                self.current_search_query = saved_query
                
                # Récupérer la position de scroll avant de restaurer
                scroll_position = self.saved_search_state.get('scroll_position')
                
                # Réafficher les résultats avec la position de scroll
                self.root.after(50, lambda: self._display_search_results(saved_results, scroll_position))
            
            # Note: La restauration des widgets (scrollbar, canvas, thumbnail_frame) 
            # et de la position de scroll est maintenant gérée par _display_search_results() pour éviter les conflits
            
            # Nettoyer l'état sauvegardé
            delattr(self, 'saved_search_state')
            
        # S'assurer que thumbnail_frame est toujours visible après fermeture artiste
        print("DEBUG: Vérification et affichage de thumbnail_frame...")
        if hasattr(self, 'thumbnail_frame'):
            try:
                if self.thumbnail_frame.winfo_exists():
                    print("DEBUG: thumbnail_frame existe, forçage du pack...")
                    # S'assurer qu'elle soit packée et visible
                    self.thumbnail_frame.pack(fill='both', pady=5, padx=5, anchor="center")
                    self.thumbnail_frame.pack_propagate(True)
                    self.thumbnail_frame.update_idletasks()
                    print(f"DEBUG: thumbnail_frame forcée visible: {self.thumbnail_frame.winfo_ismapped()}")
                else:
                    print("DEBUG: thumbnail_frame détruite, recréation...")
                    # thumbnail_frame détruite, la recréer
                    self._recreate_thumbnail_frame()
            except tk.TclError as e:
                print(f"DEBUG: TclError avec thumbnail_frame: {e}, recréation...")
                # thumbnail_frame détruite, la recréer
                self._recreate_thumbnail_frame()
        else:
            print("DEBUG: thumbnail_frame n'existe pas, création...")
            # thumbnail_frame n'existe pas, la créer
            self._recreate_thumbnail_frame()
            
        # Si on n'avait pas de résultats de recherche, cacher le canvas et la scrollbar
        if not had_search_results:
            # Cacher le canvas YouTube s'il est visible
            if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
                self.youtube_canvas.pack_forget()
            
            # Cacher la scrollbar si elle est visible
            if hasattr(self, 'scrollbar') and self.scrollbar.winfo_exists():
                self.scrollbar.pack_forget()
        
        # Nettoyer les références des threads
        self.artist_videos_thread = None
        self.artist_releases_thread = None  
        self.artist_playlists_thread = None
        
        # Nettoyer les références des frames
        if hasattr(self, 'musiques_frame'):
            delattr(self, 'musiques_frame')
        if hasattr(self, 'sorties_frame'):
            delattr(self, 'sorties_frame')
        if hasattr(self, 'playlists_frame'):
            delattr(self, 'playlists_frame')
        if hasattr(self, 'musiques_loading'):
            delattr(self, 'musiques_loading')
        if hasattr(self, 'sorties_loading'):
            delattr(self, 'sorties_loading')
        if hasattr(self, 'playlists_loading'):
            delattr(self, 'playlists_loading')
        
        # Debug: Lister l'état FINAL des widgets dans youtube_results_frame
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = self.youtube_results_frame.winfo_children()
                print(f"DEBUG: Widgets dans youtube_results_frame ÉTAT FINAL: {len(children)}")
                for i, child in enumerate(children):
                    try:
                        widget_class = child.__class__.__name__
                        widget_info = f"  - Widget {i}: {widget_class}"
                        if hasattr(child, 'winfo_name'):
                            widget_info += f" (name: {child.winfo_name()})"
                        if hasattr(child, 'cget'):
                            try:
                                bg = child.cget('bg')
                                widget_info += f" (bg: {bg})"
                            except:
                                pass
                        # Ajouter info sur la géométrie/pack
                        if hasattr(child, 'winfo_ismapped'):
                            mapped = child.winfo_ismapped()
                            widget_info += f" (visible: {mapped})"
                        print(f"DEBUG: {widget_info}")
                    except Exception as e:
                        print(f"DEBUG:   - Widget {i}: ERREUR - {e}")
            except Exception as e:
                print(f"DEBUG: Erreur lors du listage des widgets final: {e}")
        
        # Utiliser la nouvelle logique centralisée pour gérer l'affichage de la miniature après fermeture artist_tab
        print("DEBUG: Programmation de handle_artist_tab_close dans 50ms")
        import search_tab.core
        self.root.after(50, lambda: search_tab.core.handle_artist_tab_close(self))
        
        self.status_bar.config(text="Retour à la recherche normale")
        
        print("DEBUG: === FIN _return_to_search ===")
        
    except Exception as e:
        print(f"DEBUG: ERREUR DANS _return_to_search: {e}")
        print(f"Erreur lors du retour à la recherche: {e}")
        self.status_bar.config(text=f"Erreur: {e}")

def search_youtube(self):
        # Si on est en mode artiste, fermer d'abord la page artiste
        if hasattr(self, 'artist_mode') and self.artist_mode:
            self._return_to_search()
        
        # Annuler la recherche précédente si elle est en cours
        if self.is_searching:
            self.search_cancelled = True
            # Nettoyer immédiatement les résultats pour éviter les erreurs de widgets
            self._clear_results()
            # Attendre un court moment pour que le thread précédent se termine
            self.root.after(200, lambda: self._start_new_search())
            return
        
        self._start_new_search()

def _safe_update_status(self, batch_number):
        """Version sécurisée de la mise à jour du statut"""
        if not self.search_cancelled and hasattr(self, 'status_bar'):
            try:
                # Afficher le statut avec indication s'il y a plus de résultats
                status_text = f"{self.search_results_count}/{len(self.all_search_results)} résultats affichés"
                if self.has_more_results:
                    status_text += " (plus disponibles)"
                elif len(self.all_search_results) >= self.max_search_results:
                    status_text += " (limite atteinte)"
                
                self.status_bar.config(text=status_text)
            except Exception as e:
                print(f"Erreur mise à jour statut: {e}")

def _safe_status_update(self, message):
        """Version sécurisée de la mise à jour du statut avec message personnalisé"""
        if not self.search_cancelled and hasattr(self, 'status_bar'):
            try:
                self.status_bar.config(text=message)
            except Exception as e:
                print(f"Erreur mise à jour statut: {e}")

def _add_search_result(self, video, index):
        print(f"DEBUG: Ajout du résultat de recherche {index}: {video.get('title', 'Sans titre')}")
        """Ajoute un résultat avec un style rectangle uniforme"""
        try:
            # S'assurer que results_container existe
            _ensure_results_container_exists(self)
            
            # Vérifier si la recherche a été annulée ou si les widgets n'existent plus
            if self.search_cancelled or not hasattr(self, 'results_container'):
                return
            
            # Vérifier que le container existe encore
            try:
                if not self.results_container.winfo_exists():
                    return
            except tk.TclError:
                return
                
            title = video.get('title', 'Sans titre')
            duration = video.get('duration', 0)
            url = video.get('url', '')
            
            # Déterminer le type de contenu
            is_channel = "https://www.youtube.com/channel/" in url or "https://www.youtube.com/@" in url
            
            # Frame principal - grand rectangle uniforme
            result_frame = tk.Frame(
                self.results_container,
                bg='#4a4a4a',  # Fond gris uniforme
                relief='flat',
                bd=1,
                highlightbackground=COLOR_BACKGROUND_HIGHLIGHT,
                highlightthickness=1
            )
            video['search_frame'] = result_frame
            result_frame.pack(fill="x", padx=5, pady=2)
            
            # Stocker l'URL dans le frame pour détecter les doublons
            result_frame.video_url = video.get('url', '')
            
            # Configuration de la grille en 3 colonnes : miniature, titre, durée
            # Ajuster la taille selon le type de contenu
            if is_channel:
                result_frame.columnconfigure(0, minsize=90, weight=0)  # Plus d'espace pour miniature circulaire
                result_frame.rowconfigure(0, minsize=70, weight=0)     # Plus de hauteur pour les chaînes
            else:
                result_frame.columnconfigure(0, minsize=80, weight=0)  # Miniature normale
                result_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur normale
            result_frame.columnconfigure(1, weight=1)              # Titre
            result_frame.columnconfigure(2, minsize=60, weight=0)  # Durée
            
            # 1. Miniature (colonne 0)
            if is_channel:
                # Pour les chaînes, plus d'espace et moins de padding
                thumbnail_label = tk.Label(
                    result_frame,
                    bg='#4a4a4a',
                    width=8,
                    height=4,
                    anchor='center'
                ) 
                thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=5)
            else:
                # Pour les vidéos, taille normale
                thumbnail_label = tk.Label(
                    result_frame,
                    bg='#4a4a4a',
                    width=10,
                    height=3,
                    anchor='center'
                ) 
                thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(10, 10), pady=8)
            # Forcer la taille fixe
            thumbnail_label.grid_propagate(False)
            
            # 2. Titre et métadonnées (colonne 1)
            text_frame = tk.Frame(result_frame, bg='#4a4a4a')
            text_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 10), pady=8)
            text_frame.columnconfigure(0, weight=1)
            
            # Titre principal
            title_label = tk.Label(
                text_frame,
                text=title,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 9),
                anchor='w',
                justify='left'
            )
            title_label.grid(row=0, column=0, sticky='ew', pady=(2, 0))
            
            # Métadonnées (artiste • album) - seulement pour les vidéos, pas les chaînes
            metadata_label = None  # Initialiser à None par défaut
            
            if not is_channel:
                
                # Extraire les métadonnées depuis les informations YouTube
                artist = video.get('uploader', '')
                album = video.get('album', '')
                

                
                # Créer un frame pour les métadonnées afin de rendre l'artiste cliquable
                if artist or album:
                    metadata_frame = tk.Frame(text_frame, bg='#4a4a4a')
                    metadata_frame.grid(row=1, column=0, sticky='ew', pady=(0, 2))
                    metadata_frame.columnconfigure(0, weight=1)
                    
                    # Construire le texte des métadonnées avec des labels séparés
                    parts = []
                    if artist:
                        # Label cliquable pour l'artiste
                        artist_label = tk.Label(
                            metadata_frame,
                            text=artist,
                            bg='#4a4a4a',
                            fg='#88aaff',  # Couleur bleue pour indiquer que c'est cliquable
                            font=('TkDefaultFont', 8, 'underline'),
                            anchor='w',
                            justify='left',
                            cursor='hand2'
                        )
                        artist_label.pack(side=tk.LEFT)
                        
                        # Binding pour le clic simple sur l'artiste (ouvrir l'artist_tab)
                        def on_artist_click(event, artist_name=artist, video_data=video):
                            try:
                                print(f"DEBUG: Clic sur artiste: {artist_name}")
                                print(f"DEBUG: Video data keys: {list(video_data.keys())}")
                                # Sauvegarder l'état de la recherche avant d'ouvrir l'artist_tab
                                self._save_current_search_state()
                                # Ouvrir l'artist_tab directement
                                self._show_artist_content(artist_name, video_data)
                                self.status_bar.config(text=f"Ouverture de l'onglet artiste pour {artist_name}")
                            except Exception as e:
                                print(f"DEBUG: Erreur ouverture artist_tab: {e}")
                                import traceback
                                traceback.print_exc()
                                self.status_bar.config(text=f"Erreur lors de l'ouverture de l'onglet artiste")
                        
                        artist_label.bind("<Button-1>", on_artist_click)
                        create_tooltip(artist_label, f"Clic: ouvrir l'onglet artiste pour {artist}")
                        
                        # Ajouter le séparateur si on a un album
                        if album:
                            separator_label = tk.Label(
                                metadata_frame,
                                text=" • ",
                                bg='#4a4a4a',
                                fg='#cccccc',
                                font=('TkDefaultFont', 8),
                                anchor='w'
                            )
                            separator_label.pack(side=tk.LEFT)
                    
                    # Ajouter l'album s'il existe
                    if album:
                        album_label = tk.Label(
                            metadata_frame,
                            text=album,
                            bg='#4a4a4a',
                            fg='#cccccc',
                            font=('TkDefaultFont', 8),
                            anchor='w',
                            justify='left'
                        )
                        album_label.pack(side=tk.LEFT)
                    
                    # Conserver la référence pour les bindings ultérieurs
                    metadata_label = metadata_frame  # Pour compatibilité avec le code existant
            
            # 3. Durée ou type (colonne 2)
            if is_channel:
                duration_text = "Chaîne"
                duration_color = '#ffaa00'  # Orange pour les chaînes
            else:
                duration_text = time.strftime('%M:%S', time.gmtime(duration))
                duration_color = '#cccccc'
            
            duration_label = tk.Label(
                result_frame,
                text=duration_text,
                bg='#4a4a4a',
                fg=duration_color,
                font=('TkDefaultFont', 8),
                anchor='center'
            )
            duration_label.grid(row=0, column=2, sticky='ns', padx=(0, 10), pady=8)
            
            # Stocker la référence à la vidéo
            result_frame.video_data = video
            result_frame.title_label = title_label
            result_frame.duration_label = duration_label
            result_frame.thumbnail_label = thumbnail_label
            
            # Événements de clic pour la sélection multiple
            def on_result_click(event, frame=result_frame):
                # Initialiser le drag
                if not is_channel:  # Seulement pour les vidéos
                    self.drag_drop_handler.setup_drag_start(event, frame)
                
                # Vérifier si Shift est enfoncé pour la sélection multiple
                if event.state & 0x1:  # Shift est enfoncé
                    self.shift_selection_active = True
                    # Utiliser l'URL comme identifiant unique pour les résultats YouTube
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
                    # Vérifier si c'est une chaîne
                    video_url = frame.video_data.get('url', '')
                    if "https://www.youtube.com/channel/" in video_url or "https://www.youtube.com/@" in video_url:
                        # Pour les chaînes, sauvegarder l'état et ouvrir l'artist_tab
                        self._save_current_search_state()
                        artist_name = frame.video_data.get('title', 'Artiste inconnu')
                        self._show_artist_content(artist_name, frame.video_data)
                        self.status_bar.config(text=f"Affichage du contenu de {artist_name}")
                    else:
                        # Comportement modifié : télécharger SANS ajouter à la playlist
                        self._on_result_click(frame, add_to_playlist=False)
            
            def on_result_ctrl_click(event, frame=result_frame):
                # Ctrl+clic pour ouvrir les chaînes dans le navigateur
                video_url = frame.video_data.get('url', '')
                if "https://www.youtube.com/channel/" in video_url or "https://www.youtube.com/@" in video_url:
                    import webbrowser
                    webbrowser.open(video_url)
                    self.status_bar.config(text="Chaîne ouverte dans le navigateur")
                else:
                    # Pour les vidéos, comportement normal
                    self._on_result_click(frame, add_to_playlist=True)
            
            # Bindings pour les clics simples, doubles et Ctrl+clic
            duration_label.bind("<ButtonPress-1>", on_result_click)
            duration_label.bind("<Double-1>", on_result_double_click)
            duration_label.bind("<Control-ButtonPress-1>", on_result_ctrl_click)
            text_frame.bind("<ButtonPress-1>", on_result_click)
            text_frame.bind("<Double-1>", on_result_double_click)
            text_frame.bind("<Control-ButtonPress-1>", on_result_ctrl_click)
            title_label.bind("<ButtonPress-1>", on_result_click)
            title_label.bind("<Double-1>", on_result_double_click)
            title_label.bind("<Control-ButtonPress-1>", on_result_ctrl_click)
            if metadata_label is not None:  # Ajouter binding pour metadata_frame s'il existe
                metadata_label.bind("<ButtonPress-1>", on_result_click)
                metadata_label.bind("<Double-1>", on_result_double_click)
                metadata_label.bind("<Control-ButtonPress-1>", on_result_ctrl_click)
            thumbnail_label.bind("<ButtonPress-1>", on_result_click)
            thumbnail_label.bind("<Double-1>", on_result_double_click)
            thumbnail_label.bind("<Control-ButtonPress-1>", on_result_ctrl_click)
            
            # Ajouter des tooltips pour expliquer les interactions
            if is_channel:
                tooltip_text = "Chaîne YouTube\nDouble-clic: Ouvrir l'onglet artiste\nCtrl + Clic: Ouvrir dans le navigateur\nShift + Clic: Sélection multiple"
            else:
                tooltip_text = "Vidéo YouTube\nDouble-clic: Télécharger (sans ajouter à la playlist)\nDrag vers la droite: Télécharger et ajouter à la queue\nDrag vers la gauche: Télécharger et placer en premier dans la queue\nShift + Clic: Sélection multiple"
            create_tooltip(text_frame, tooltip_text)
            create_tooltip(title_label, tooltip_text)
            if metadata_label is not None:
                create_tooltip(metadata_label, tooltip_text)
            create_tooltip(duration_label, tooltip_text)
            create_tooltip(thumbnail_label, tooltip_text)
            result_frame.bind("<ButtonPress-1>", on_result_click)
            result_frame.bind("<Double-1>", on_result_double_click)
            
            # Configuration du drag-and-drop pour les vidéos
            if not is_channel:
                self.drag_drop_handler.setup_drag_drop(
                    result_frame, 
                    video_data=video, 
                    item_type="youtube"
                )
            
            # Événements de clic droit pour ajouter après la chanson en cours
            duration_label.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            text_frame.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            title_label.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            if metadata_label is not None:  # Ajouter binding pour metadata_frame s'il existe
                metadata_label.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            thumbnail_label.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            result_frame.bind("<ButtonPress-3>", lambda e, f=result_frame: self._on_result_right_click(e, f))
            

            
            # Charger la miniature en arrière-plan
            if video.get('thumbnails'):
                thumbnail_url = video['thumbnails'][1]['url'] if len(video['thumbnails']) > 1 else video['thumbnails'][0]['url']
                if is_channel:
                    # Pour les chaînes, utiliser une miniature circulaire
                    threading.Thread(
                        target=self._load_circular_thumbnail,
                        args=(thumbnail_label, thumbnail_url),
                        daemon=True
                    ).start()
                else:
                    # Pour les vidéos, miniature normale
                    threading.Thread(
                        target=self._load_thumbnail,
                        args=(thumbnail_label, thumbnail_url),
                        daemon=True
                    ).start()
                
        except Exception as e:
            print(f"Erreur affichage résultat: {e}")

def _on_result_click(self, frame, add_to_playlist=True):
        """Gère le clic sur un résultat"""
        if hasattr(frame, 'video_data'):
            video = frame.video_data
            
            # Vérifier si déjà en cours de téléchargement
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            if url in self.current_downloads:
                self.status_bar.config(text="Téléchargement déjà en cours...")
                return
            
            # Changer l'apparence pour indiquer le téléchargement
            self._reset_frame_appearance(frame, '#ff6666')
            
            self.search_list = [frame.video_data]  # Pour la compatibilité avec download_selected_youtube
            frame.video_data['search_frame'] = frame
            try:
                self.download_selected_youtube(None, add_to_playlist)
            except Exception as e:
                # En cas d'erreur, remettre l'apparence normale
                frame.config(bg='#ffcc00')  # Jaune pour erreur
                frame.title_label.config(bg='#ffcc00', fg='#333333')
                frame.duration_label.config(bg='#ffcc00', fg='#666666')
                frame.thumbnail_label.config(bg='#ffcc00')

def _on_result_right_click(self, event, frame):
        """Gère le clic droit sur un résultat pour afficher le menu des playlists"""
        # Initialiser le drag pour le clic droit (seulement pour les vidéos, pas les chaînes)
        if hasattr(frame, 'video_data'):
            video_url = frame.video_data.get('url', '')
            is_channel = ("https://www.youtube.com/channel/" in video_url or 
                         "https://www.youtube.com/@" in video_url)
            if not is_channel:
                self.drag_drop_handler.setup_drag_start(event, frame)
        
        if hasattr(frame, 'video_data'):
            video = frame.video_data
            
            # Vérifier si déjà en cours de téléchargement
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            if url in self.current_downloads:
                # Afficher le menu pour ajouter à une playlist après téléchargement
                self._show_pending_playlist_menu(video, frame, url)
                return
            
            # Afficher le menu des playlists
            self._show_youtube_playlist_menu(video, frame)

def _safe_add_search_result(self, video, index):
    """Version sécurisée de _add_search_result qui vérifie l'annulation"""
    if not self.search_cancelled:
        self._add_search_result(video, index)

def _recreate_thumbnail_frame(self):
    """Recrée la thumbnail_frame si elle a été détruite"""
    print("DEBUG: _recreate_thumbnail_frame appelée")

    # Debug: Lister tous les widgets présents dans youtube_results_frame
    if hasattr(self, 'youtube_results_frame'):
        try:
            children = self.youtube_results_frame.winfo_children()
            print(f"DEBUG: Widgets dans youtube_results_frame AVANT recréation: {len(children)}")
            for i, child in enumerate(children):
                try:
                    widget_class = child.__class__.__name__
                    widget_info = f"  - Widget {i}: {widget_class}"
                    if hasattr(child, 'winfo_name'):
                        widget_info += f" (name: {child.winfo_name()})"
                    if hasattr(child, 'cget'):
                        try:
                            bg = child.cget('bg')
                            widget_info += f" (bg: {bg})"
                        except:
                            pass
                    print(f"DEBUG: {widget_info}")
                except Exception as e:
                    print(f"DEBUG:   - Widget {i}: ERREUR - {e}")
        except Exception as e:
            print(f"DEBUG: Erreur lors du listage des widgets: {e}")

    try:
        # Recréer la frame pour la miniature
        self.thumbnail_frame = tk.Frame(
            self.youtube_results_frame,
            bg='#3d3d3d',
            height=300,  # Hauteur fixe raisonnable pour la miniature
        )
        # Afficher la frame thumbnail
        self.thumbnail_frame.pack(fill='both', pady=5, padx=5, anchor="center")
        # Forcer la visibilité et mise à jour
        self.thumbnail_frame.pack_propagate(True)
        self.thumbnail_frame.update_idletasks()
        print("DEBUG: thumbnail_frame recréée et packée avec succès")

        # Debug: Lister tous les widgets présents APRÈS recréation
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = self.youtube_results_frame.winfo_children()
                print(f"DEBUG: Widgets dans youtube_results_frame APRÈS recréation: {len(children)}")
                for i, child in enumerate(children):
                    try:
                        widget_class = child.__class__.__name__
                        widget_info = f"  - Widget {i}: {widget_class}"
                        if hasattr(child, 'winfo_name'):
                            widget_info += f" (name: {child.winfo_name()})"
                        if hasattr(child, 'cget'):
                            try:
                                bg = child.cget('bg')
                                widget_info += f" (bg: {bg})"
                            except:
                                pass
                        print(f"DEBUG: {widget_info}")
                    except Exception as e:
                        print(f"DEBUG:   - Widget {i}: ERREUR - {e}")
            except Exception as e:
                print(f"DEBUG: Erreur lors du listage des widgets après: {e}")

    except Exception as e:
        print(f"DEBUG: Erreur lors de la recréation de thumbnail_frame: {e}")

def _on_scrollbar_release(self, event):
    """Appelée quand on relâche la scrollbar"""
    self._check_scroll_position()

def _check_scroll_position(self):
    """Vérifie la position du scroll et charge plus si nécessaire"""
    if self._should_load_more_results():
        self._load_more_search_results()

def _should_load_more_results(self):
    """Vérifie si on doit charger plus de résultats"""
    if (self.is_loading_more or 
        self.is_searching or
        not self.current_search_query or 
        self.search_results_count >= self.max_search_results or
        self.current_search_batch >= self.max_search_batchs):
        return False
    
    # Vérifier si on est proche du bas
    try:
        # Obtenir la position actuelle du scroll (0.0 à 1.0)
        scroll_top, scroll_bottom = self.youtube_canvas.yview()
        
        # Si on est à plus de 80% vers le bas, charger plus
        if scroll_bottom > 0.8:
            return True
        
        return False
    except Exception as e:
        print(f"Erreur détection scroll: {e}")
        return False

def _update_results_counter(self):
    """Met à jour le compteur de résultats affiché"""
    try:
        if hasattr(self, 'results_counter_label') and self.results_counter_label.winfo_exists():
            displayed_count = self.search_results_count
            total_count = len(self.all_search_results)
            
            # Si on a des résultats à afficher
            if total_count > 0:
                # Si on a atteint le maximum autorisé
                counter_text = f"Résultats {displayed_count}/{self.max_search_results}"
            else:
                counter_text = "Aucun résultat"
            
            self.results_counter_label.config(text=counter_text)
    except Exception as e:
        print(f"Erreur lors de la mise à jour du compteur: {e}")

def _display_search_results(self, results, scroll_position=None):
    """Affiche les résultats de recherche sauvegardés après restauration - utilise les mêmes mécanismes qu'une recherche normale"""
    try:
        print(f"DEBUG: _display_search_results appelée avec {len(results)} résultats")
        
        # Restaurer les résultats dans all_search_results pour utiliser les mécanismes normaux
        self.all_search_results = results
        self.search_results_count = 0
        
        # Utiliser exactement la même fonction que lors d'une recherche normale
        # Cela garantit que la scrollbar et le canvas sont configurés de la même manière
        self._display_batch_results(1)
        
        # Restaurer la position de scroll après que tous les résultats soient ajoutés
        if scroll_position:
            print(f"DEBUG: Restauration de la position de scroll: {scroll_position}")
            # Attendre que tous les résultats soient ajoutés
            total_delay = len(results) * SEARCH_WAIT_TIME_BETWEEN_RESULTS + 200
            self.root.after(total_delay, lambda: self._restore_scroll_position(scroll_position))
        
        print(f"DEBUG: Restauration de {len(results)} résultats programmée via _display_batch_results")
        
    except Exception as e:
        print(f"DEBUG: Erreur dans _display_search_results: {e}")
        # En cas d'erreur, au moins afficher le statut
        self._safe_status_update(f"Erreur lors de la restauration: {e}")


def _restore_scroll_position(self, scroll_position):
    """Restaure la position de scroll de manière sécurisée"""
    try:
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
            scroll_top, scroll_bottom = scroll_position
            print(f"DEBUG: Application de la position de scroll: top={scroll_top}, bottom={scroll_bottom}")
            
            # Forcer la mise à jour du canvas pour s'assurer que la scrollregion est correcte
            self.youtube_canvas.update_idletasks()
            
            # Appliquer la position de scroll
            self.youtube_canvas.yview_moveto(scroll_top)
            print("DEBUG: Position de scroll restaurée avec succès")
        else:
            print("DEBUG: Canvas non disponible pour restaurer le scroll")
    except Exception as e:
        print(f"DEBUG: Erreur lors de la restauration du scroll: {e}")

def _update_stats_bar(self):
    """Met à jour la barre de statistiques avec le temps de recherche"""
    if not hasattr(self, 'stats_bar'):
        return
        
    if self.last_search_time > 0:
        self.stats_bar.config(text=f"recherche en {self.last_search_time:.2f}s")
    else:
        self.stats_bar.config(text="")

class SearchManager:
    """
    Gestionnaire indépendant pour toutes les fonctions de recherche YouTube.
    Cette classe encapsule toute la logique de recherche pour la rendre plus modulaire.
    """
    
    def __init__(self, app_instance):
        """Initialise le gestionnaire avec une référence vers l'instance principale de l'app"""
        self.app = app_instance
        
    def search_youtube(self):
        """Point d'entrée principal pour la recherche YouTube"""
        return search_youtube(self.app)
        
    def clear_results(self):
        """Vide les résultats de recherche"""
        return _clear_results(self.app)
        
    def load_more_results(self):
        """Charge plus de résultats"""
        return _load_more_search_results(self.app)
        
    def update_results_ui(self):
        """Met à jour l'interface des résultats"""
        return _update_search_results_ui(self.app)
        
    def on_search_entry_change(self, event):
        """Gère les changements dans le champ de recherche"""
        return _on_search_entry_change(self.app, event)
        
    def clear_search(self):
        """Efface la recherche"""
        return _clear_youtube_search(self.app)
        
    def show_current_song_thumbnail(self):
        """Affiche la miniature de la chanson actuelle"""
        return _show_current_song_thumbnail(self.app)
        
    def on_filter_change(self):
        """Gère les changements de filtres"""
        return _on_filter_change(self.app)
        
    def should_load_more_results(self):
        """Vérifie s'il faut charger plus de résultats"""
        return _should_load_more_results(self.app)
        
    def update_results_counter(self):
        """Met à jour le compteur de résultats"""
        return _update_results_counter(self.app)
        
    def update_stats_bar(self):
        """Met à jour la barre de statistiques"""
        return _update_stats_bar(self.app)

def create_search_manager(app_instance):
    """
    Fonction utilitaire pour créer un gestionnaire de recherche.
    Usage: search_manager = search_tab.results.create_search_manager(self)
    """
    return SearchManager(app_instance)