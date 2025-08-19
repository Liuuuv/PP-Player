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
        try:
            # Vérifier que youtube_canvas existe, sinon le recréer
            if not hasattr(self, 'youtube_canvas') or not self.youtube_canvas.winfo_exists():
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
                
                pass
            else:
                pass
        except Exception as e:
            pass

def _recreate_youtube_canvas(self):
    """Recrée le youtube_canvas si nécessaire"""
    try:
        # Vérifier que youtube_results_frame existe
        if not hasattr(self, 'youtube_results_frame') or not self.youtube_results_frame.winfo_exists():
            return
        
        # Créer le canvas
        self.youtube_canvas = tk.Canvas(
            self.youtube_results_frame,
            bg='#3d3d3d',
            highlightthickness=0
        )
        
        # Créer la scrollbar si elle n'existe pas
        if not hasattr(self, 'scrollbar') or not self.scrollbar.winfo_exists():
            self.scrollbar = ttk.Scrollbar(
                self.youtube_results_frame,
                orient="vertical",
                command=self.youtube_canvas.yview
            )
            self.scrollbar.pack(side="right", fill="y")
        
        # Configurer le canvas avec la scrollbar ET la détection de scroll
        # Utiliser la même fonction que dans setup.py pour détecter le scroll
        def on_canvas_scroll(*args):
            self.scrollbar.set(*args)
            # Optimisation : vérifier le scroll moins fréquemment
            if hasattr(self, 'safe_after'):
                self.safe_after(50, self._check_scroll_position)  # 50ms au lieu de 1ms
            else:
                self.youtube_canvas.after_idle(self._check_scroll_position)
        
        self.youtube_canvas.configure(yscrollcommand=on_canvas_scroll)
        self.youtube_canvas.pack(side="left", fill="both", expand=True)
        
    except Exception as e:
        pass

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
    """Affiche un lot de résultats avec taille configurable"""
    # Vérifier si la recherche a été annulée
    if self.search_cancelled:
        return
    
    # Utiliser la configuration centralisée pour la taille des lots
    try:
        from search_tab.config import get_display_config
        batch_size = get_display_config('batch_size') or 10
    except ImportError:
        batch_size = 10
        
    start_index = (batch_number - 1) * batch_size
    end_index = min(start_index + batch_size, len(self.all_search_results))
    
    # Si c'est le premier lot, afficher le canvas de résultats
    if batch_number == 1 and end_index > start_index:
        if not self.search_cancelled:
            self.root.after(0, self._show_search_results)
    
    # Afficher les résultats de ce lot - optimisé pour la vitesse
    batch_results = []
    for i in range(start_index, end_index):
        # Vérifier l'annulation à chaque itération
        if self.search_cancelled:
            return
            
        if i < len(self.all_search_results):
            video = self.all_search_results[i]
            batch_results.append((video, i))
            self.search_results_count += 1
    
    # Afficher tous les résultats du batch en une fois avec un délai configurable
    if batch_results and not self.search_cancelled:
        try:
            from search_tab.config import get_display_config
            batch_delay = get_display_config('batch_delay') or 8
        except ImportError:
            batch_delay = 8
        self.root.after(batch_delay, lambda: self._display_batch_results_fast(batch_results))
    
    # Mettre à jour le statut seulement si pas annulé
    if not self.search_cancelled:
        self.root.after(0, lambda: self._safe_update_status(batch_number))
        # Mettre à jour le compteur de résultats
        self.root.after(0, self._update_results_counter)

def _display_batch_results_fast(self, batch_results):
    """Affiche rapidement un batch de résultats sans délai entre chaque"""
    if self.search_cancelled:
        return
    
    for i, (video, idx) in enumerate(batch_results):
        if self.search_cancelled:
            return
        
        # Afficher avec un délai configurable pour éviter de bloquer l'UI
        try:
            from search_tab.config import get_display_config
            wait_time = get_display_config('wait_time_between_results') or 20
        except ImportError:
            wait_time = 20
        delay = i * (wait_time // 4)  # Diviser par 4 pour avoir un délai raisonnable
        self.root.after(delay, lambda v=video, index=idx: self._safe_add_search_result(v, index))

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
        # Masquer la thumbnail frame
        if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame is not None:
            try:
                if self.thumbnail_frame.winfo_exists():
                    self.thumbnail_frame.pack_forget()
                else:
                    pass
            except Exception as e:
                pass
        else:
            pass
        
        # Afficher la scrollbar
        if hasattr(self, 'scrollbar') and self.scrollbar is not None:
            try:
                if self.scrollbar.winfo_exists():
                    self.scrollbar.pack(side="right", fill="y")
                else:
                    pass
            except Exception as e:
                pass
        else:
            pass
            
        # Afficher le canvas
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas is not None:
            try:
                if self.youtube_canvas.winfo_exists():
                    self.youtube_canvas.pack(side="left", fill="both", expand=True)
                    # S'assurer que la connexion canvas-scrollbar est correcte
                    self._ensure_canvas_scrollbar_connection()
                else:
                    pass
            except Exception as e:
                pass
        else:
            pass
        
        # Vérifier le container de résultats
        if hasattr(self, 'results_container'):
            if self.results_container and self.results_container.winfo_exists():
                children = self.results_container.winfo_children()
            else:
                pass
        else:
            pass
        
        # Mettre à jour le compteur de résultats
        self._update_results_counter()
    except Exception as e:
        print(f"Erreur lors de l'affichage des résultats: {e}")
        import traceback
        traceback.print_exc()

def _ensure_canvas_scrollbar_connection(self):
    """S'assure que la connexion entre le canvas et la scrollbar est correcte"""
    try:
        if hasattr(self, 'youtube_canvas') and hasattr(self, 'scrollbar'):
            if (self.youtube_canvas and self.youtube_canvas.winfo_exists() and 
                self.scrollbar and self.scrollbar.winfo_exists()):
                # Reconfigurer la connexion avec détection de scroll
                def on_canvas_scroll(*args):
                    self.scrollbar.set(*args)
                    # Optimisation : vérifier le scroll moins fréquemment
                    if hasattr(self, 'safe_after'):
                        self.safe_after(50, self._check_scroll_position)  # 50ms au lieu de 1ms
                    else:
                        self.youtube_canvas.after_idle(self._check_scroll_position)
                
                self.youtube_canvas.configure(yscrollcommand=on_canvas_scroll)
                self.scrollbar.configure(command=self.youtube_canvas.yview)
            else:
                # Déconnecter le canvas de toute scrollbar détruite
                if self.youtube_canvas and self.youtube_canvas.winfo_exists():
                    self.youtube_canvas.configure(yscrollcommand="")
    except Exception as e:
        pass

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
    # Vérifier si on est en bas du scroll
    try:
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
            # Obtenir la position de scroll actuelle
            scroll_top, scroll_bottom = self.youtube_canvas.yview()
            
            # Si on est proche du bas (90% ou plus), charger plus de résultats
            if scroll_bottom > 0.9:
                if self._should_load_more_results():
                    self._load_more_search_results()
    except Exception as e:
        print(f"Erreur dans _on_youtube_canvas_configure: {e}")

def _start_new_search(self):
    """Démarre une nouvelle recherche après avoir annulé la précédente"""
    query = self.youtube_entry.get().strip()
    if not query:
        # Si la recherche est vide, afficher la miniature
        self._clear_results()
        self._show_current_song_thumbnail()
        return
    
    # D'abord essayer de restaurer depuis le cache
    if _try_restore_from_cache(self, query):
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
                
                # Sauvegarder automatiquement dans le cache après une recherche réussie
                self.root.after(500, lambda: _save_current_search_state(self))
            
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
        """Sauvegarde l'état actuel des résultats de recherche dans le cache"""
        search_state = {
            'scroll_position': None,
            'canvas_packed': False,
            'scrollbar_packed': False,
            'thumbnail_packed': False,
            'search_query': '',
            'search_results': [],
            'current_search_batch': 1,
            'has_more_results': False,
            'search_results_count': 0,
            'timestamp': time.time()
        }
        
        # Sauvegarder la requête de recherche actuelle
        if hasattr(self, 'youtube_entry') and self.youtube_entry.winfo_exists():
            search_state['search_query'] = self.youtube_entry.get().strip()
        
        # Sauvegarder les résultats de recherche actuels
        if hasattr(self, 'all_search_results'):
            search_state['search_results'] = self.all_search_results.copy()
        
        # Sauvegarder l'état de pagination
        if hasattr(self, 'current_search_batch'):
            search_state['current_search_batch'] = self.current_search_batch
        if hasattr(self, 'has_more_results'):
            search_state['has_more_results'] = self.has_more_results
        if hasattr(self, 'search_results_count'):
            search_state['search_results_count'] = self.search_results_count
        if hasattr(self, 'total_available_results'):
            search_state['total_available_results'] = self.total_available_results
        
        # Sauvegarder la position de scroll
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
            try:
                scroll_top, scroll_bottom = self.youtube_canvas.yview()
                search_state['scroll_position'] = (scroll_top, scroll_bottom)
                search_state['canvas_packed'] = bool(self.youtube_canvas.winfo_manager())
            except:
                pass
        
        # Sauvegarder l'état de la scrollbar
        if hasattr(self, 'scrollbar') and self.scrollbar.winfo_exists():
            search_state['scrollbar_packed'] = bool(self.scrollbar.winfo_manager())
        
        # Sauvegarder l'état de la thumbnail frame
        if hasattr(self, 'thumbnail_frame') and self.thumbnail_frame.winfo_exists():
            search_state['thumbnail_packed'] = bool(self.thumbnail_frame.winfo_manager())
        
        # Sauvegarder dans le cache local ET dans le cache manager
        self.saved_search_state = search_state
        
        # Sauvegarder dans le cache manager si disponible
        if (hasattr(self, 'artist_tab_manager') and 
            hasattr(self.artist_tab_manager, 'cache_manager') and 
            search_state['search_query']):
            
            # Utiliser la requête comme clé de cache
            cache_key = f"search_{search_state['search_query']}"
            self.artist_tab_manager.cache_manager.set_search_results(cache_key, search_state)
            
            # Aussi sauvegarder l'état d'interface
            interface_key = f"interface_{search_state['search_query']}"
            interface_state = {
                'scroll_position': search_state['scroll_position'],
                'canvas_packed': search_state['canvas_packed'],
                'scrollbar_packed': search_state['scrollbar_packed'],
                'thumbnail_packed': search_state['thumbnail_packed']
            }
            self.artist_tab_manager.cache_manager.set_interface_state(interface_key, interface_state)
        


def _try_restore_from_cache(self, search_query):
    """Tente de restaurer une recherche depuis le cache"""
    if not search_query.strip():
        return False
    
    # Vérifier si on a le cache manager
    if not (hasattr(self, 'artist_tab_manager') and 
            hasattr(self.artist_tab_manager, 'cache_manager')):
        return False
    
    cache_manager = self.artist_tab_manager.cache_manager
    cache_key = f"search_{search_query.strip()}"
    
    # Essayer de récupérer depuis le cache
    cached_state = cache_manager.get_search_results(cache_key)
    if not cached_state:
        return False
    
    try:
        # Restaurer les données de recherche
        self.all_search_results = cached_state['search_results'].copy()
        self.current_search_batch = cached_state.get('current_search_batch', 1)
        self.has_more_results = cached_state.get('has_more_results', False)
        self.search_results_count = cached_state.get('search_results_count', len(self.all_search_results))
        self.total_available_results = cached_state.get('total_available_results', len(self.all_search_results))
        self.current_search_query = search_query.strip()  # Important pour permettre le chargement de plus de résultats
        
        # Restaurer l'état d'interface
        interface_key = f"interface_{search_query.strip()}"
        interface_state = cache_manager.get_interface_state(interface_key)
        
        # Afficher les résultats immédiatement avec optimisation pour le cache
        try:
            self._display_search_results_from_cache(self.all_search_results)
        except Exception as e:
            import traceback
            traceback.print_exc()
        
        # Restaurer la position de scroll si disponible
        if interface_state and interface_state.get('scroll_position'):
            def restore_scroll():
                try:
                    if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
                        scroll_top, scroll_bottom = interface_state['scroll_position']
                        self.youtube_canvas.yview_moveto(scroll_top)
                except Exception as e:
                    pass
            
            # Restaurer le scroll après un court délai
            self.safe_after(100, restore_scroll)
        
        # Mettre à jour le statut avec indicateur de cache
        result_count = len(self.all_search_results)
        try:
            from search_tab.config import get_ui_message
            status_text = get_ui_message('cache_restored', count=result_count)
        except ImportError:
            status_text = f"⚡ {result_count} résultats restaurés instantanément (cache)"
        self._safe_status_update(status_text)
        
        # Changer temporairement la couleur du statut pour indiquer le cache
        def reset_status_color():
            try:
                if hasattr(self, 'status_bar'):
                    from search_tab.config import get_ui_color
                    normal_color = get_ui_color('normal_text_color') or 'white'
                    self.status_bar.config(fg=normal_color)
            except:
                pass
        
        # Couleur pour indiquer le cache
        try:
            if hasattr(self, 'status_bar'):
                from search_tab.config import get_ui_color
                cache_color = get_ui_color('cache_indicator_color') or '#00ff00'
                cache_duration = get_ui_color('cache_indicator_duration') or 3000
                self.status_bar.config(fg=cache_color)
                # Revenir à la couleur normale après la durée configurée
                self.safe_after(cache_duration, reset_status_color)
        except:
            pass
        
        return True
        
    except Exception as e:
        return False

def _display_search_results_from_cache(self, results):
    """Affiche les résultats de recherche depuis le cache avec optimisation"""
    
    if not results:
        return
    
    # Nettoyer d'abord
    self._clear_results()
    
    # S'assurer que le container existe
    _ensure_results_container_exists(self)
    
    # Utiliser la configuration centralisée pour l'affichage depuis le cache
    try:
        from search_tab.config import get_display_config
        batch_size = get_display_config('cache_batch_size') or 15
        delay = get_display_config('cache_batch_delay') or 2
    except ImportError:
        batch_size = 15  # Valeur par défaut
        delay = 2
    
    def display_batch(batch_start):
        try:
            batch_end = min(batch_start + batch_size, len(results))
            
            # Vérifier que le container existe
            if not hasattr(self, 'results_container') or not self.results_container.winfo_exists():
                _ensure_results_container_exists(self)
            
            # Afficher le lot actuel
            for i in range(batch_start, batch_end):
                if i < len(results):
                    video = results[i]
                    try:
                        self._add_search_result(video, i)
                    except Exception as e:
                        pass
            
            # Mettre à jour le compteur
            self.search_results_count = batch_end
            
            # Programmer le lot suivant s'il y en a un
            if batch_end < len(results):
                self.safe_after(delay, lambda: display_batch(batch_end))
            else:
                # Affichage terminé
                # Mettre à jour la scrollregion
                self._update_scroll_region()
                # Afficher les résultats
                self._show_search_results()
                
        except Exception as e:
            print(f"Erreur affichage lot depuis cache: {e}")
            import traceback
            traceback.print_exc()
    
    # Démarrer l'affichage
    display_batch(0)

def _update_scroll_region(self):
    """Met à jour la région de scroll du canvas"""
    try:
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
            bbox = self.youtube_canvas.bbox("all")
            if bbox:
                self.youtube_canvas.configure(scrollregion=bbox)
    except Exception as e:
        print(f"Erreur mise à jour scroll region: {e}")

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
    
    # Utiliser la nouvelle logique centralisée pour déterminer si on doit afficher la miniature
    import search_tab.core
    if not search_tab.core.should_show_large_thumbnail(self):
        return
    
    # Vérifier que thumbnail_frame existe et est accessible
    if not hasattr(self, 'thumbnail_frame'):
        # Essayer de recréer la frame
        if hasattr(self, '_recreate_thumbnail_frame'):
            self._recreate_thumbnail_frame()
        else:
            return
        
    try:
        if not self.thumbnail_frame.winfo_exists():
            # Essayer de recréer la frame
            if hasattr(self, '_recreate_thumbnail_frame'):
                self._recreate_thumbnail_frame()
            else:
                return
        else:
            pass
    except tk.TclError as e:
        # Thumbnail frame détruit, essayer de la recréer
        if hasattr(self, '_recreate_thumbnail_frame'):
            self._recreate_thumbnail_frame()
        else:
            return
    except Exception as e:
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
    
    if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
        current_song = self.main_playlist[self.current_index]
        
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
            
            # Charger la vraie miniature si elle existe (version grande et carrée)
            self._load_large_thumbnail(current_song, thumbnail_label)
        except tk.TclError as e:
            # Erreur lors de la création du label, ignorer
            pass
        except Exception as e:
            pass
        
    else:
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
        except tk.TclError as e:
            # Erreur lors de la création du label, ignorer
            pass
        except Exception as e:
            pass

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
        
        # Remettre à zéro les variables d'état des onglets artiste
        self.artist_tab_active_sorties = False
        self.artist_tab_active_playlists = False
        
        # Debug: Lister tous les widgets présents dans youtube_results_frame AVANT nettoyage
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = self.youtube_results_frame.winfo_children()
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
                    except Exception as e:
                        pass
            except Exception as e:
                pass
        
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
        if hasattr(self, 'artist_notebook'):
            try:
                if self.artist_notebook.winfo_exists():
                    self.artist_notebook.destroy()
                else:
                    pass
                delattr(self, 'artist_notebook')
            except Exception as e:
                pass
        
        # Supprimer la croix si elle existe
        if hasattr(self, 'artist_close_btn'):
            try:
                if self.artist_close_btn.winfo_exists():
                    self.artist_close_btn.destroy()
                else:
                    pass
                delattr(self, 'artist_close_btn')
            except Exception as e:
                pass
        
        # Supprimer le bouton retour playlist si il existe
        if hasattr(self, 'artist_tab_back_btn') and self.artist_tab_back_btn:
            try:
                if self.artist_tab_back_btn.winfo_exists():
                    self.artist_tab_back_btn.destroy()
                else:
                self.artist_tab_back_btn = None
            except Exception as e:
        
        # Debug: Lister tous les widgets présents dans youtube_results_frame APRÈS suppression des widgets artiste
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = self.youtube_results_frame.winfo_children()
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
                    except Exception as e:
            except Exception as e:
        
        # CORRECTION: Nettoyer tous les frames enfants non essentiels de youtube_results_frame
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = list(self.youtube_results_frame.winfo_children())
                for child in children:
                    try:
                        # Garder seulement les widgets essentiels
                        if (child == getattr(self, 'thumbnail_frame', None) or
                            child == getattr(self, 'youtube_canvas', None) or
                            child == getattr(self, 'scrollbar', None)):
                            continue
                        
                        # Supprimer tous les autres frames (main_container et autres)
                        child.destroy()
                        
                    except Exception as e:
            except Exception as e:
        
        # Debug: Lister les widgets APRÈS nettoyage complet
        if hasattr(self, 'youtube_results_frame'):
            try:
                children = self.youtube_results_frame.winfo_children()
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
                    except Exception as e:
            except Exception as e:
        
        # Restaurer l'état original des résultats de recherche
        had_search_results = False
        if hasattr(self, 'saved_search_state'):
            
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
        if hasattr(self, 'thumbnail_frame'):
            try:
                if self.thumbnail_frame.winfo_exists():
                    # S'assurer qu'elle soit packée et visible
                    self.thumbnail_frame.pack(fill='both', pady=5, padx=5, anchor="center")
                    self.thumbnail_frame.pack_propagate(True)
                    self.thumbnail_frame.update_idletasks()
                else:
                    # thumbnail_frame détruite, la recréer
                    self._recreate_thumbnail_frame()
            except tk.TclError as e:
                # thumbnail_frame détruite, la recréer
                self._recreate_thumbnail_frame()
        else:
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
                    except Exception as e:
            except Exception as e:
        
        # Utiliser la nouvelle logique centralisée pour gérer l'affichage de la miniature après fermeture artist_tab
        import search_tab.core
        self.root.after(50, lambda: search_tab.core.handle_artist_tab_close(self))
        
        self.status_bar.config(text="Retour à la recherche normale")
        
        
    except Exception as e:
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
        """Ajoute un résultat de recherche en utilisant la fonction unifiée"""
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
            
            # Utiliser la fonction unifiée pour afficher le résultat de recherche
            self._add_song_item(video, self.results_container, video_index=index, item_type="search_result")
            
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
                if hasattr(frame, 'title_label'):
                    frame.title_label.config(bg='#ffcc00', fg='#333333')
                if hasattr(frame, 'duration_label'):
                    frame.duration_label.config(bg='#ffcc00', fg='#666666')
                if hasattr(frame, 'thumbnail_label'):
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
            
            # Afficher le menu pour choisir où ajouter la vidéo
            self._show_playlist_menu(video, frame)

def _reset_frame_appearance(self, frame, color):
    """Remet l'apparence d'un frame de résultat à la normale"""
    try:
        frame.config(bg=color)
        if hasattr(frame, 'title_label'):
            frame.title_label.config(bg=color)
        if hasattr(frame, 'duration_label'):
            frame.duration_label.config(bg=color)
        if hasattr(frame, 'thumbnail_label'):
            frame.thumbnail_label.config(bg=color)
    except Exception as e:
        print(f"Erreur reset frame appearance: {e}")

def _show_playlist_menu(self, video, frame):
    """Affiche le menu pour choisir dans quelle playlist ajouter la vidéo"""
    try:
        # Créer le menu contextuel
        menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white', 
                      activebackground='#4a4a4a', activeforeground='white')
        
        # Option pour ajouter à la main playlist
        menu.add_command(
            label="Ajouter à la liste de lecture",
            command=lambda: self._on_result_click(frame, add_to_playlist=True)
        )
        
        menu.add_separator()
        
        # Options pour ajouter aux playlists existantes
        for playlist_name in self.playlists.keys():
            if playlist_name != "Main Playlist":  # Éviter la duplication
                menu.add_command(
                    label=f"Ajouter à '{playlist_name}'",
                    command=lambda pn=playlist_name: self._add_video_to_playlist(video, frame, pn)
                )
        
        menu.add_separator()
        
        # Option pour télécharger sans ajouter à une playlist
        menu.add_command(
            label="Télécharger seulement",
            command=lambda: self._on_result_click(frame, add_to_playlist=False)
        )
        
        # Afficher le menu
        menu.tk_popup(frame.winfo_rootx(), frame.winfo_rooty())
        
    except Exception as e:
        print(f"Erreur affichage menu playlist: {e}")

def _add_video_to_playlist(self, video, frame, playlist_name):
    """Ajoute une vidéo à une playlist spécifique"""
    try:
        # Vérifier si déjà en cours de téléchargement
        url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
        if url in self.current_downloads:
            # Ajouter à la liste d'attente pour cette playlist
            if url not in self.pending_playlist_additions:
                self.pending_playlist_additions[url] = []
            if playlist_name not in self.pending_playlist_additions[url]:
                self.pending_playlist_additions[url].append(playlist_name)
            self.status_bar.config(text=f"Sera ajouté à '{playlist_name}' après téléchargement")
            return
        
        # Changer l'apparence pour indiquer le téléchargement
        self._reset_frame_appearance(frame, '#ff6666')
        
        # Ajouter à la liste d'attente pour cette playlist
        if url not in self.pending_playlist_additions:
            self.pending_playlist_additions[url] = []
        if playlist_name not in self.pending_playlist_additions[url]:
            self.pending_playlist_additions[url].append(playlist_name)
        
        # Lancer le téléchargement
        self.search_list = [video]
        video['search_frame'] = frame
        self.download_selected_youtube(None, add_to_playlist=False)  # Ne pas ajouter à la main playlist
        
    except Exception as e:
        print(f"Erreur ajout vidéo à playlist: {e}")
        # En cas d'erreur, remettre l'apparence normale
        frame.config(bg='#ffcc00')  # Jaune pour erreur

def _show_pending_playlist_menu(self, video, frame, url):
    """Affiche le menu pour ajouter à une playlist après téléchargement"""
    try:
        # Créer le menu contextuel
        menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white', 
                      activebackground='#4a4a4a', activeforeground='white')
        
        # Options pour ajouter aux playlists existantes
        for playlist_name in self.playlists.keys():
            # Vérifier si déjà en attente pour cette playlist
            already_pending = (url in self.pending_playlist_additions and 
                             playlist_name in self.pending_playlist_additions[url])
            
            label = f"{'✓ ' if already_pending else ''}Ajouter à '{playlist_name}'"
            menu.add_command(
                label=label,
                command=lambda pn=playlist_name: self._toggle_pending_playlist(url, pn)
            )
        
        # Afficher le menu
        menu.tk_popup(frame.winfo_rootx(), frame.winfo_rooty())
        
    except Exception as e:
        print(f"Erreur affichage menu playlist en attente: {e}")

def _toggle_pending_playlist(self, url, playlist_name):
    """Active/désactive l'ajout en attente à une playlist"""
    try:
        if url not in self.pending_playlist_additions:
            self.pending_playlist_additions[url] = []
        
        if playlist_name in self.pending_playlist_additions[url]:
            # Retirer de la liste d'attente
            self.pending_playlist_additions[url].remove(playlist_name)
            if not self.pending_playlist_additions[url]:
                del self.pending_playlist_additions[url]
            self.status_bar.config(text=f"Retiré de l'attente pour '{playlist_name}'")
        else:
            # Ajouter à la liste d'attente
            self.pending_playlist_additions[url].append(playlist_name)
            self.status_bar.config(text=f"Sera ajouté à '{playlist_name}' après téléchargement")
            
    except Exception as e:
        print(f"Erreur toggle playlist en attente: {e}")

def _save_current_search_state(self):
    """Sauvegarde l'état actuel de la recherche pour pouvoir y revenir"""
    try:
        # Sauvegarder l'état de la recherche
        pass  # Implémentation à ajouter si nécessaire
    except Exception as e:
        print(f"Erreur sauvegarde état recherche: {e}")

def _restore_search_scroll_position(self):
    """Restaure la position de scroll après une recherche"""
    try:
        # Restaurer la position de scroll
        pass  # Implémentation à ajouter si nécessaire
    except Exception as e:

def _update_scrollregion(self):
    """Met à jour la région de scroll du canvas"""
    try:
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
            self.youtube_canvas.update_idletasks()
            bbox = self.youtube_canvas.bbox("all")
            if bbox:
                self.youtube_canvas.configure(scrollregion=bbox)
    except Exception as e:

def _restore_scroll_position(self, scroll_position):
    """Restaure la position de scroll de manière sécurisée"""
    try:
        if hasattr(self, 'youtube_canvas') and self.youtube_canvas.winfo_exists():
            scroll_top, scroll_bottom = scroll_position
            
            # Forcer la mise à jour du canvas pour s'assurer que la scrollregion est correcte
            self.youtube_canvas.update_idletasks()
            
            # Vérifier la scrollregion actuelle
            scrollregion = self.youtube_canvas.cget('scrollregion')
            
            # Appliquer la position de scroll
            self.youtube_canvas.yview_moveto(scroll_top)
        else:
    except Exception as e:

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
        """Gestionnaire pour les changements dans le champ de recherche"""
        return _on_search_entry_change(self.app, event)

def _safe_add_search_result(self, video, index):
    """Ajoute un résultat de recherche de manière sécurisée"""
    try:
        if hasattr(self, 'search_cancelled') and self.search_cancelled:
            return
        self._add_search_result(video, index)
    except Exception as e:
        print(f"Erreur ajout résultat sécurisé: {e}")

def _update_results_counter(self):
    """Met à jour le compteur de résultats"""
    try:
        if hasattr(self, 'results_counter_label') and self.results_counter_label.winfo_exists():
            count = len(self.all_search_results) if hasattr(self, 'all_search_results') else 0
            self.results_counter_label.config(text=f"{count} résultats")
    except Exception as e:
        print(f"Erreur mise à jour compteur: {e}")

def _should_load_more_results(self):
    """Détermine s'il faut charger plus de résultats"""
    try:
        if not hasattr(self, 'has_more_results') or not self.has_more_results:
            return False
        if hasattr(self, 'is_loading_more') and self.is_loading_more:
            return False
        return True
    except Exception as e:
        print(f"Erreur vérification chargement: {e}")
        return False
