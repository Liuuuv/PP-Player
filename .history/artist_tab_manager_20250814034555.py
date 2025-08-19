# Gestionnaire centralisé pour toutes les fonctions liées aux pages d'artiste
# Ce fichier centralise toutes les fonctions artist_* qui étaient dans main.py

# Import centralisé depuis __init__.py
from __init__ import *
import artist_tab.core
import artist_tab.songs
import artist_tab.releases
import artist_tab.playlists
import search_tab.results

class ArtistTabManager:
    """Gestionnaire centralisé pour toutes les fonctionnalités liées aux pages d'artiste"""
    
    def __init__(self, music_player):
        self.player = music_player
        
        # Initialiser le gestionnaire de cache optimisé
        from artist_tab.cache_manager import ArtistCacheManager
        self.cache_manager = ArtistCacheManager()
        
        # Remplacer les anciens caches par le gestionnaire optimisé
        self.player.artist_cache = self.cache_manager.artist_cache
        self.player.thumbnail_cache = self.cache_manager.thumbnail_cache
        self.player.playlist_content_cache = self.cache_manager.playlist_content_cache
        
        # Programmer un nettoyage périodique du cache
        self._schedule_cache_cleanup()
    
    def _schedule_cache_cleanup(self):
        """Programme un nettoyage périodique du cache pour éviter l'accumulation"""
        def cleanup():
            try:
                self.cache_manager.clear_expired_thumbnails()
                # Reprogrammer le nettoyage dans 5 minutes
                self.player.safe_after(300000, cleanup)  # 5 minutes
            except:
                pass
        
        # Premier nettoyage dans 5 minutes
        self.player.safe_after(300000, cleanup)
    
    def cleanup_resources(self):
        """Nettoie les ressources utilisées par l'onglet artiste"""
        try:
            # Fermer les pools de threads
            if hasattr(self.player, '_thumbnail_executor'):
                self.player._thumbnail_executor.shutdown(wait=False)
            if hasattr(self.player, '_playlist_executor'):
                self.player._playlist_executor.shutdown(wait=False)
            
            # Vider les caches
            self.cache_manager.clear_all()
            
        except Exception as e:
            print(f"Erreur lors du nettoyage des ressources artiste: {e}")
        
    # ==================== GESTION DES ONGLETS ARTISTE ====================
    
    def on_artist_tab_changed(self, event):
        """Gère le changement d'onglet dans le notebook artiste"""
        try:
            if not hasattr(self.player, 'artist_notebook') or not self.player.artist_notebook.winfo_exists():
                return
            
            current_tab_id = self.player.artist_notebook.select()
            if current_tab_id:
                current_tab_text = self.player.artist_notebook.tab(current_tab_id, "text")


                # Mettre à jour les variables selon l'onglet actuel
                if current_tab_text == "Sorties":
                    self.player.playlist_content_active = self.player.artist_tab_active_sorties
                    self.player.current_artist_tab = "Sorties" if self.player.artist_tab_active_sorties else None
                elif current_tab_text == "Playlists":
                    self.player.playlist_content_active = self.player.artist_tab_active_playlists
                    self.player.current_artist_tab = "Playlists" if self.player.artist_tab_active_playlists else None
                
                # Afficher/masquer le bouton selon l'onglet actuel et son état
                self._update_back_button_visibility(current_tab_text)
                
        except Exception as e:
            print(f"Erreur dans on_artist_tab_changed: {e}")
    
    def _update_back_button_visibility(self, current_tab_text):
        """Met à jour la visibilité du bouton retour selon l'onglet actuel et son état"""
        try:
            # Afficher le bouton uniquement si on est sur un onglet avec du contenu ouvert
            should_show = False
            if current_tab_text == "Sorties" and self.player.artist_tab_active_sorties:
                should_show = True
            elif current_tab_text == "Playlists" and self.player.artist_tab_active_playlists:
                should_show = True
            
            if should_show:
                self._show_playlist_back_button()
            else:
                self._hide_playlist_back_button()

        except Exception as e:
            print(f"Erreur dans _update_back_button_visibility: {e}")
    
    def _show_playlist_back_button(self):
        """Affiche le bouton retour pour les playlists, le recrée si nécessaire"""
        try:
            # Vérifier si le bouton existe et est valide
            button_exists = (hasattr(self.player, 'artist_tab_back_btn') and 
                           self.player.artist_tab_back_btn and 
                           self.player.artist_tab_back_btn.winfo_exists())
            
            if button_exists:
                # Le bouton existe, juste le repositionner
                self.player.artist_tab_back_btn.place(in_=self.player.artist_tab_back_btn.master, relx=1.0, rely=0.0, anchor="ne", x=-40, y=5)
                self.player.artist_tab_back_btn.tkraise()
            else:
                # Le bouton n'existe pas, le recréer
                self._create_back_button()
                
        except Exception as e:
            print(f"Erreur lors de l'affichage du bouton retour: {e}")
    
    def _create_back_button(self):
        """Crée le bouton retour"""
        try:
            # Trouver le container principal (où afficher le bouton)
            if not hasattr(self.player, 'artist_notebook') or not self.player.artist_notebook.winfo_exists():
                return
                
            # Le container principal est le parent du notebook
            main_container = self.player.artist_notebook.master
            
            # Détruire l'ancien bouton s'il existe
            if hasattr(self.player, 'artist_tab_back_btn') and self.player.artist_tab_back_btn:
                try:
                    self.player.artist_tab_back_btn.destroy()
                except:
                    pass
            
            # Créer le nouveau bouton
            if hasattr(self.player, 'icons') and 'back' in self.player.icons:
                button = tk.Button(
                    main_container,
                    image=self.player.icons['back'],
                    bg='#3d3d3d',
                    activebackground='#4a8fe7',
                    relief='raised',
                    bd=1,
                    width=20,
                    height=20,
                    command=self.smart_back_action,
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
                    width=3,
                    height=1,
                    command=self.smart_back_action,
                    cursor='hand2',
                    takefocus=0
                )
            
            # Positionner le bouton
            button.place(relx=1.0, rely=0.0, anchor="ne", x=-40, y=5)
            button.tkraise()
            
            # Sauvegarder la référence
            self.player.artist_tab_back_btn = button
            
        except Exception as e:
            print(f"Erreur lors de la création du bouton retour: {e}")
    
    def _hide_playlist_back_button(self):
        """Masque le bouton retour pour les playlists"""
        try:
            if hasattr(self.player, 'artist_tab_back_btn') and self.player.artist_tab_back_btn and self.player.artist_tab_back_btn.winfo_exists():
                self.player.artist_tab_back_btn.place_forget()
        except Exception as e:
            print(f"Erreur lors du masquage du bouton retour: {e}")
    
    def _reset_playlist_content_state(self, tab_name=None):
        """Remet à zéro l'état du contenu de playlist pour un onglet spécifique ou tous"""
        if tab_name is None or tab_name == "sorties":
            self.player.artist_tab_active_sorties = False
        
        if tab_name is None or tab_name == "playlists":
            self.player.artist_tab_active_playlists = False
        
        # Mettre à jour les variables et la visibilité du bouton
        if hasattr(self.player, 'artist_notebook') and self.player.artist_notebook is not None and self.player.artist_notebook.winfo_exists():
            try:
                current_tab_id = self.player.artist_notebook.select()
                if current_tab_id:
                    current_tab_text = self.player.artist_notebook.tab(current_tab_id, "text")
                    if current_tab_text == "Sorties":
                        self.player.playlist_content_active = self.player.artist_tab_active_sorties
                    elif current_tab_text == "Playlists":
                        self.player.playlist_content_active = self.player.artist_tab_active_playlists
                    
                    # Mettre à jour la visibilité du bouton selon l'onglet actuel
                    self._update_back_button_visibility(current_tab_text)
            except:
                pass
    
    # ==================== FONCTIONS PRINCIPALES D'ARTISTE ====================
    
    def show_artist_content(self, artist_name, video_data):
        """Affiche le contenu d'un artiste dans la zone de recherche YouTube - Version optimisée non-bloquante"""
        return artist_tab.core._show_artist_content(self.player, artist_name, video_data)
    
    def create_artist_tabs(self):
        """Crée les onglets Musiques et Sorties dans la zone YouTube"""
        return artist_tab.core._create_artist_tabs(self.player)
    
    def search_artist_content_async(self):
        """Version asynchrone et non-bloquante de la recherche d'artiste"""
        return artist_tab.core._search_artist_content_async(self.player)
    
    def find_artist_channel_id(self):
        """Trouve l'ID réel de la chaîne YouTube pour cet artiste - Version optimisée"""
        return artist_tab.core._find_artist_channel_id(self.player)
    
    def cancel_artist_search(self):
        """Annule toutes les recherches d'artiste en cours"""
        return artist_tab.core._cancel_artist_search(self.player)
    
    # ==================== CALLBACKS ET GESTION D'ÉTAT ====================
    
    def on_channel_id_found(self, channel_id):
        """Appelé quand l'ID de la chaîne a été trouvé - lance les recherches de contenu"""
        return artist_tab.core._on_channel_id_found(self.player, channel_id)
    
    def on_channel_id_error(self, error_msg="Impossible de trouver l'ID de la chaîne"):
        """Appelé en cas d'erreur lors de la recherche d'ID"""
        return artist_tab.core._on_channel_id_error(self.player, error_msg)
    
    def start_parallel_searches(self):
        """Lance les 3 recherches de contenu en parallèle"""
        return artist_tab.core._start_parallel_searches(self.player)

    def show_error_in_tabs(self, error_msg):
        """Affiche un message d'erreur dans tous les onglets artiste"""
        return artist_tab.core._show_error_in_tabs(self.player, error_msg)

    def update_loading_messages(self):
        """Met à jour les messages de chargement selon l'état actuel"""
        return artist_tab.core._update_loading_messages(self.player)

    def display_results_in_batches(self, items, container, item_type, batch_size=3):
        """Affiche les résultats par petits lots de façon non-bloquante pour éviter le lag de l'interface"""
        return artist_tab.core._display_results_in_batches(self.player, items, container, item_type, batch_size)
    
    # ==================== RECHERCHE DE CONTENU ARTISTE ====================
    
    def search_artist_videos_with_id(self):
        """Recherche les vidéos de l'artiste depuis l'onglet Vidéos de sa chaîne"""
        return artist_tab.songs._search_artist_videos_with_id(self.player)

    def search_artist_videos(self):
        """Ancienne fonction - maintenant redirige vers _search_artist_videos_with_id"""
        self.search_artist_videos_with_id()

    def search_artist_releases_with_id(self):
        """Recherche les albums et singles de l'artiste depuis l'onglet releases"""
        return artist_tab.releases._search_artist_releases_with_id(self.player)

    def search_artist_playlists_with_id(self):
        """Recherche les playlists de l'artiste depuis l'onglet playlists"""  
        return artist_tab.playlists._search_artist_playlists_with_id(self.player)
    
    def search_artist_releases(self):
        """Ancienne fonction - maintenant redirige vers _search_artist_releases_with_id"""
        return self.search_artist_releases_with_id()
    
    def search_artist_releases_old(self):
        """Ancienne fonction - gardée pour référence"""
        return artist_tab.releases._search_artist_releases_old(self.player)
    
    def search_artist_playlists(self):
        """Ancienne fonction - maintenant redirige vers _search_artist_playlists_with_id"""
        return self.search_artist_playlists_with_id()
    
    def search_artist_content(self):
        """Ancienne fonction - redirige vers la nouvelle version asynchrone"""
        self.search_artist_content_async()
    
    # ==================== AFFICHAGE DU CONTENU ARTISTE ====================
    
    def display_artist_videos(self, videos):
        """Affiche les vidéos de l'artiste dans l'onglet Musiques"""
        return artist_tab.songs._display_artist_videos(self.player, videos)
    
    def display_artist_releases(self, releases):
        """Affiche les sorties de l'artiste dans l'onglet Sorties"""
        return artist_tab.releases._display_artist_releases(self.player, releases)
    
    def display_artist_playlists(self, playlists):
        """Affiche les playlists de l'artiste dans l'onglet Playlists"""
        return artist_tab.playlists._display_artist_playlists(self.player, playlists)

    def add_artist_result(self, video, index, container):
        """Ajoute un résultat vidéo dans un onglet artiste"""
        return artist_tab.core._add_artist_result(self.player, video, index, container)
    
    def load_artist_thumbnail(self, video, thumbnail_label):
        """Charge la miniature d'une vidéo d'artiste en arrière-plan"""
        return artist_tab.core._load_artist_thumbnail(self.player, video, thumbnail_label)
    
    def load_playlist_count(self, playlist, count_label):
        """Charge le nombre de vidéos d'une playlist en arrière-plan"""
        return artist_tab.core._load_playlist_count(self.player, playlist, count_label)
    
    def add_artist_playlist_result(self, playlist, index, container, target_tab="sorties"):
        """Ajoute une playlist dans l'onglet Sorties ou Playlists avec double-clic pour voir le contenu"""
        return artist_tab.core._add_artist_playlist_result(self.player, playlist, index, container, target_tab)

    # ==================== GESTION DES PLAYLISTS ARTISTE ====================

    def show_playlist_content(self, playlist_data, target_tab="sorties"):
        """Affiche le contenu d'une playlist dans une nouvelle interface"""
        return artist_tab.playlists._show_playlist_content(self.player, playlist_data, target_tab)

    def show_playlist_loading(self, playlist_title, target_tab="sorties"):
        """Affiche un message de chargement pour la playlist"""
        return artist_tab.playlists._show_playlist_loading(self.player, playlist_title, target_tab)

    def display_playlist_content(self, videos, playlist_title, target_tab="sorties"):
        """Affiche le contenu d'une playlist avec la même interface que l'onglet Musiques"""
        return artist_tab.playlists._display_playlist_content(self.player, videos, playlist_title, target_tab)

    def return_to_releases(self):
        """Retourne à l'affichage des releases dans l'onglet Sorties"""
        return artist_tab.releases._return_to_releases(self.player)
    
    def return_to_playlists(self):
        """Retourne à l'affichage des playlists dans l'onglet Playlists"""
        return artist_tab.playlists._return_to_playlists(self.player)
    
    def show_playlist_error(self, error_msg):
        """Affiche une erreur lors du chargement d'une playlist"""
        return artist_tab.playlists._show_playlist_error(self.player, error_msg)
    
    def return_to_search(self):
        """Retourne instantanément à l'affichage de recherche normal"""
        return search_tab.results._return_to_search(self.player)
    
    def smart_back_action(self):
        """Action intelligente du bouton retour selon l'onglet actuel"""
        try:
            if not hasattr(self.player, 'artist_notebook') or not self.player.artist_notebook.winfo_exists():
                return
            
            current_tab_id = self.player.artist_notebook.select()
            if current_tab_id:
                current_tab_text = self.player.artist_notebook.tab(current_tab_id, "text")
                
                # Appeler la fonction de retour appropriée selon l'onglet actuel
                if current_tab_text == "Sorties" and self.player.artist_tab_active_sorties:
                    self.return_to_releases()
                elif current_tab_text == "Playlists" and self.player.artist_tab_active_playlists:
                    self.return_to_playlists()
                    
        except Exception as e:
            print(f"Erreur dans smart_back_action: {e}")


# ==================== FONCTIONS UTILITAIRES POUR L'INTÉGRATION ====================

def init_artist_tab_manager(music_player):
    """Initialise le gestionnaire d'onglets artiste et l'attache au lecteur de musique"""
    music_player.artist_tab_manager = ArtistTabManager(music_player)
    return music_player.artist_tab_manager

def get_artist_tab_manager(music_player):
    """Récupère le gestionnaire d'onglets artiste, l'initialise si nécessaire"""
    if not hasattr(music_player, 'artist_tab_manager'):
        return init_artist_tab_manager(music_player)
    return music_player.artist_tab_manager