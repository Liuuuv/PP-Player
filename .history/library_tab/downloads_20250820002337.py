"""
Module de gestion des téléchargements - Version indépendante
"""

import sys
import os
import time

# Imports locaux indépendants
from . import (
    tk, ttk, threading, Image, ImageTk,
    get_config, get_library_config,
    safe_file_operation, get_file_duration, format_duration,
    normalize_filename, is_audio_file, get_audio_files_in_directory,
    create_directory_if_not_exists, ThreadSafeCache, create_tooltip,
    debounce, log_performance
)

from .downloads_manager import DownloadsManager


class DownloadsProgressiveLoader:
    """Classe pour gérer le chargement progressif des téléchargements"""
    
    def __init__(self, parent):
        self.parent = parent
        self.files_to_display = []
        self.window_start = 0
        self.window_end = 0
        self.loading_in_progress = False
        self.load_count = 20  # Valeur par défaut
        
    def initialize(self, files_list):
        """Initialise le loader avec une liste de fichiers"""
        self.files_to_display = files_list
        self.window_start = 0
        
        # Obtenir la configuration de load_more_count (locale d'abord, puis principale)
        self.load_count = get_library_config('load_more_count', 20)
        if self.load_count == 20:  # Si pas trouvé dans config locale, essayer config principale
            self.load_count = get_config('load_more_count', 20)
            
        self.window_end = min(self.load_count, len(self.files_to_display))
        self.loading_in_progress = False
        
    def get_current_window(self):
        """Retourne la fenêtre actuelle de fichiers à afficher"""
        if not self.files_to_display:
            return []
        return self.files_to_display[self.window_start:self.window_end]
    
    def can_load_more(self):
        """Vérifie s'il y a plus de fichiers à charger"""
        return self.window_end < len(self.files_to_display)
    
    def load_more(self):
        """Charge plus de fichiers et retourne les nouveaux fichiers à ajouter"""
        if self.loading_in_progress or not self.can_load_more():
            return []
            
        self.loading_in_progress = True
        
        old_end = self.window_end
        self.window_end = min(len(self.files_to_display), self.window_end + self.load_count)
        
        new_files = self.files_to_display[old_end:self.window_end]
        
        print(f"Chargement progressif: {old_end} -> {self.window_end} ({len(new_files)} nouveaux fichiers)")
        
        # Libérer le verrou après un délai
        def reset_loading_flag():
            self.loading_in_progress = False
            
        try:
            self.parent.root.after(500, reset_loading_flag)
        except:
            reset_loading_flag()
            
        return new_files
    
    def reset(self):
        """Remet à zéro le loader"""
        self.files_to_display = []
        self.window_start = 0
        self.window_end = 0
        self.loading_in_progress = False
    
    def get_stats(self):
        """Retourne des statistiques sur le chargement"""
        return {
            'total_files': len(self.files_to_display),
            'loaded_files': self.window_end,
            'remaining_files': len(self.files_to_display) - self.window_end,
            'progress_percent': (self.window_end / len(self.files_to_display) * 100) if self.files_to_display else 0
        }

def show_downloads_content(self):
    """Affiche le contenu de l'onglet téléchargées"""
    
    # S'assurer que les données sont à jour avant l'affichage
    # Note: Ne pas appeler _refresh_downloads_library ici car elle sera appelée par load_downloaded_files
    
    # Frame pour la barre de recherche
    search_frame = ttk.Frame(self.library_content_frame)
    search_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
    
    # Barre de recherche
    self.library_search_entry = tk.Entry(
        search_frame,
        bg='#3d3d3d',
        fg='white',
        insertbackground='white',
        relief='flat',
        bd=5
    )
    self.library_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Lier l'événement de saisie pour la recherche en temps réel
    self.library_search_entry.bind('<KeyRelease>', self._on_library_search_change)
    
    # Bouton pour effacer la recherche
    clear_btn = tk.Button(
        search_frame,
        image=self.icons["cross_small"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=4,
        pady=4,
        width=20,
        height=20,
        takefocus=0
    )
    clear_btn.bind("<Button-1>", lambda event: self._clear_library_search())
    clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    # Frame pour les boutons de lecture
    buttons_frame = ttk.Frame(self.library_content_frame)
    buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    # Bouton pour jouer toutes les musiques dans l'ordre
    play_all_btn = tk.Button(
        buttons_frame,
        image=self.icons["play"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=8,
        pady=8,
        command=self.play_all_downloads_ordered,
        takefocus=0
    )
    play_all_btn.pack(side=tk.LEFT, padx=(0, 10))
    create_tooltip(play_all_btn, "Jouer toutes les musiques\nLit toutes les musiques téléchargées dans l'ordre")
    
    # Bouton pour jouer toutes les musiques en mode aléatoire
    shuffle_all_btn = tk.Button(
        buttons_frame,
        image=self.icons["shuffle"],
        bg="#3d3d3d",
        fg="white",
        activebackground="#4a4a4a",
        relief="flat",
        bd=0,
        padx=8,
        pady=8,
        command=self.play_all_downloads_shuffle,
        takefocus=0
    )
    shuffle_all_btn.pack(side=tk.LEFT)
    create_tooltip(shuffle_all_btn, "Jouer en mode aléatoire\nLit toutes les musiques téléchargées dans un ordre aléatoire")
    
    # Canvas avec scrollbar pour les téléchargements
    self.downloads_canvas = tk.Canvas(
        self.library_content_frame,
        bg='#3d3d3d',
        highlightthickness=0,
        takefocus=0
    )
    self.downloads_scrollbar = ttk.Scrollbar(
        self.library_content_frame,
        orient="vertical",
        command=self.downloads_canvas.yview
    )
    self.downloads_canvas.configure(yscrollcommand=self.downloads_scrollbar.set)
    
    self.downloads_scrollbar.pack(side="right", fill="y")
    self.downloads_canvas.pack(side="left", fill="both", expand=True)
    
    self.downloads_container = ttk.Frame(self.downloads_canvas)
    self.downloads_canvas.create_window((0, 0), window=self.downloads_container, anchor="nw")
    
    # Configurer le scroll
    self.downloads_container.bind(
        "<Configure>",
        lambda e: self.downloads_canvas.configure(
            scrollregion=self.downloads_canvas.bbox("all")
        )
    )
    
    # Bind de la molette de souris
    self._bind_mousewheel(self.downloads_canvas, self.downloads_canvas)
    self._bind_mousewheel(self.downloads_container, self.downloads_canvas)
    
    # Ajouter la détection du scroll pour le chargement progressif
    self.downloads_canvas.bind('<Configure>', self._on_downloads_canvas_configure)
    self.downloads_scrollbar.config(command=self._on_downloads_scroll)
    
    # Initialiser le gestionnaire de téléchargements indépendant
    if not hasattr(self, 'downloads_manager'):
        # Essayer d'utiliser le dossier de téléchargements existant
        downloads_folder = getattr(self, 'downloads_folder', None)
        self.downloads_manager = DownloadsManager(downloads_folder)
    
    # Initialiser le loader de chargement progressif
    if not hasattr(self, 'downloads_loader'):
        self.downloads_loader = DownloadsProgressiveLoader(self)
    
    # Charger et afficher les fichiers téléchargés
    self.load_downloaded_files()

def load_downloaded_files(self):
    """Charge et affiche tous les fichiers du dossier downloads - Version indépendante"""
    try:
        # Utiliser le gestionnaire indépendant
        self.all_downloaded_files = self.downloads_manager.get_all_files()
        
        # Mettre à jour le nombre de fichiers téléchargés
        self.num_downloaded_files = len(self.all_downloaded_files)
        
        # Afficher tous les fichiers (sans filtre)
        self._display_filtered_downloads(self.all_downloaded_files)
        
        # Mettre à jour le texte du bouton
        self._update_downloads_button()
        
        # Afficher les statistiques
        stats = self.downloads_manager.get_stats()
        print(f"📁 Téléchargements chargés: {stats['total_files']} fichiers, {stats['total_size_mb']:.1f} MB")
        
        # Forcer une mise à jour supplémentaire de la scrollbar après un délai
        if hasattr(self, 'safe_after'):
            self.safe_after(100, self._update_scrollbar)
        else:
            self.root.after(100, self._update_scrollbar)
            
    except Exception as e:
        print(f"Erreur lors du chargement des téléchargements: {e}")
        self.all_downloaded_files = []
        self.num_downloaded_files = 0

def _display_filtered_downloads(self, files_to_display_, preserve_scroll=False):
    """Affiche une liste filtrée de fichiers téléchargés avec chargement progressif"""
    print("_display_filtered_downloads appelée")
    
    # Marquer qu'on est en train de faire un refresh pour éviter la boucle infinie
    self._refreshing_downloads = True
    
    # Vider le container actuel
    try:
        # Vérifier que le container existe encore
        if hasattr(self, 'downloads_container') and self.downloads_container.winfo_exists():
            for widget in self.downloads_container.winfo_children():
                try:
                    if widget.winfo_exists():
                        widget.destroy()
                except tk.TclError:
                    # Widget déjà détruit, ignorer
                    continue
    except tk.TclError:
        # Container détruit, ignorer
        pass
    
    # Réinitialiser les variables de progression
    if hasattr(self, 'loading_progress_label'):
        self.loading_progress_label.destroy()
        delattr(self, 'loading_progress_label')
    
    # Remonter le scroll en haut après chaque recherche (sauf si preserve_scroll=True)
    if not preserve_scroll and hasattr(self, 'downloads_canvas'):
        try:
            if self.downloads_canvas.winfo_exists():
                self.downloads_canvas.yview_moveto(0.0)
        except tk.TclError:
            # Canvas détruit, ignorer
            pass
    
    # Si aucun fichier à afficher, montrer le message "Aucun résultat"
    if not files_to_display_:
        self._show_no_results_message()
        # Réinitialiser le loader
        self.downloads_loader.reset()
        # Marquer la fin du refresh
        self._refreshing_downloads = False
        return
    
    # Initialiser le loader avec la nouvelle liste de fichiers
    self.downloads_loader.initialize(files_to_display_)
    
    # Charger et afficher les premiers éléments
    initial_files = self.downloads_loader.get_current_window()
    for filepath in initial_files:
        self._add_download_item_fast(filepath)
    
    # Forcer la mise à jour de la scrollbar après l'ajout des éléments
    self._update_scrollbar()
    
    # Lancer le chargement différé des miniatures et durées pour les éléments visibles
    self._start_thumbnail_loading(initial_files, self.downloads_container)
    
    # Marquer la fin du refresh
    self._refreshing_downloads = False

def _on_downloads_scroll(self, *args):
    """Gère le scroll de la liste des téléchargements et charge plus d'éléments si nécessaire"""
    try:
        # Appliquer le scroll normal
        self.downloads_canvas.yview(*args)
        
        # Vérifier si on doit charger plus d'éléments
        if hasattr(self, 'downloads_loader') and not getattr(self, '_refreshing_downloads', False):
            self._check_load_more_downloads()
            
    except Exception as e:
        print(f"Erreur lors du scroll des téléchargements: {e}")

def _on_downloads_canvas_configure(self, event):
    """Gère la configuration du canvas des téléchargements"""
    try:
        # Mettre à jour la région de scroll
        self.downloads_canvas.configure(scrollregion=self.downloads_canvas.bbox("all"))
        
        # Vérifier si on doit charger plus d'éléments après redimensionnement
        if hasattr(self, 'downloads_loader') and not getattr(self, '_refreshing_downloads', False):
            self._check_load_more_downloads()
            
    except Exception as e:
        print(f"Erreur lors de la configuration du canvas: {e}")

def _check_load_more_downloads(self):
    """Vérifie si on doit charger plus de téléchargements basé sur la position du scroll"""
    try:
        if not hasattr(self, 'downloads_loader') or not hasattr(self, 'downloads_canvas'):
            return
            
        # Obtenir la position actuelle du scroll
        try:
            scroll_top, scroll_bottom = self.downloads_canvas.yview()
        except:
            return
            
        # Seuil pour déclencher le chargement (quand on est à 80% du bas)
        threshold = 0.8
        
        # Si on est proche du bas et qu'il y a plus de fichiers à charger
        if scroll_bottom >= threshold and self.downloads_loader.can_load_more():
            print(f"Déclenchement du chargement progressif (scroll: {scroll_bottom:.2f})")
            
            # Charger plus de fichiers
            new_files = self.downloads_loader.load_more()
            
            # Ajouter les nouveaux fichiers à l'interface
            for filepath in new_files:
                self._add_download_item_fast(filepath)
            
            # Mettre à jour la scrollbar
            self._update_scrollbar()
            
            # Lancer le chargement des miniatures pour les nouveaux éléments
            if new_files:
                self._start_thumbnail_loading(new_files, self.downloads_container)
                
            # Afficher les statistiques de chargement
            stats = self.downloads_loader.get_stats()
            print(f"Chargement progressif - Chargés: {stats['loaded_files']}/{stats['total_files']} ({stats['progress_percent']:.1f}%)")
                
    except Exception as e:
        print(f"Erreur lors de la vérification du chargement progressif: {e}")

def _restore_search_binding(self):
    """Restaure le binding de recherche après un refresh"""
    # Éviter les restaurations multiples
    if hasattr(self, '_restore_pending') and self._restore_pending:
        return
    
    self._restore_pending = True
    
    # Utiliser un délai pour s'assurer que tous les événements sont traités
    def restore_delayed():
        try:
            # Marquer la fin du refresh
            self._refreshing_downloads = False
            self._restore_pending = False
            
            # Restaurer le binding de recherche
            if hasattr(self, 'library_search_entry'):
                try:
                    # Vérifier que le widget existe encore
                    if self.library_search_entry.winfo_exists():
                        self.library_search_entry.bind('<KeyRelease>', self._on_library_search_change)
                except:
                    pass
        except:
            self._restore_pending = False
    
    # Programmer la restauration après un court délai
    if hasattr(self, 'safe_after'):
        self.safe_after(100, restore_delayed)  # Délai un peu plus long pour plus de sécurité
    else:
        self.root.after(100, restore_delayed)

def _show_no_results_message(self):
    """Affiche le message 'Aucun résultat' avec l'image none.png"""
    import tkinter as tk
    
    # Frame principal qui prend TOUTE la place disponible dans downloads_container
    no_results_frame = tk.Frame(
        self.downloads_container,
        bg='#3d3d3d',  # Couleur du thème,
        width=600,    # Même largeur qui fonctionnait
        height=self.downloads_canvas.winfo_height()
    )
    no_results_frame.pack(fill="both", padx=5, pady=5)
    no_results_frame.pack_propagate(False)
    
    # Vérifier si l'icône none.png est disponible
    has_icon = hasattr(self, 'icons') and 'none' in self.icons
    
    if has_icon:
        try:
            # Container pour l'image
            icon_frame = tk.Frame(no_results_frame, bg='#3d3d3d')
            icon_frame.pack(expand=True, pady=(20, 2))
            
            # Créer une version agrandie de l'image none.png
            from PIL import Image, ImageTk
            
            # Récupérer l'image originale depuis le PhotoImage
            original_image = self.icons['none']
            # Convertir le PhotoImage en PIL Image pour le redimensionnement
            original_pil = Image.open("assets/none.png")  # Charger depuis le fichier source
            

            enlarged_image = original_pil
            
            # Convertir de nouveau en PhotoImage pour Tkinter
            enlarged_photo = ImageTk.PhotoImage(enlarged_image)
            
            # Afficher l'image agrandie
            icon_label = tk.Label(
                icon_frame,
                image=enlarged_photo,
                bg='#3d3d3d',
                bd=0
            )
            icon_label.pack()
            
            # Garder une référence pour éviter que l'image soit supprimée par le garbage collector
            icon_label.image = enlarged_photo
        except Exception as e:
            has_icon = False
    
    if not has_icon:
        # Fallback : Emoji simple
        emoji_frame = tk.Frame(no_results_frame, bg='#3d3d3d')
        emoji_frame.pack(expand=True, pady=(20, 2))
        
        emoji_label = tk.Label(
            emoji_frame,
            text="🔍",  # Emoji loupe
            bg='#3d3d3d',
            fg='#888888',
            font=('Arial', 32),
            bd=0
        )
        emoji_label.pack()
    
    # Texte "Aucun résultat"
    text_frame = tk.Frame(no_results_frame, bg='#3d3d3d')
    text_frame.pack(expand=True, pady=(0, 5))
    
    text_label = tk.Label(
        text_frame,
        text="Aucun résultat",
        bg='#3d3d3d',
        fg='#cccccc',
        font=('Arial', 16, 'bold'),
        bd=0
    )
    text_label.pack()
    
    
    # Mettre à jour le canvas
    self.downloads_container.update_idletasks()
    self.downloads_canvas.configure(scrollregion=(0, 0, self.downloads_canvas.winfo_width(), self.downloads_canvas.winfo_height()))


def _update_downloads_button(self):
    """Met à jour le texte du bouton téléchargées avec le nombre actuel"""
    if hasattr(self, 'downloads_btn'):
        self.downloads_btn.configure(text="Téléchargées " + f"({self.num_downloaded_files})")
        
def _display_files_batch(self, files_to_display, start_index, batch_size=20):
    """Affiche les fichiers par batch pour éviter de bloquer l'interface (ancienne version)"""
    end_index = min(start_index + batch_size, len(files_to_display))
    
    # Afficher le batch actuel
    for i in range(start_index, end_index):
        self._add_download_item(files_to_display[i])
    
    # Programmer le batch suivant si nécessaire
    if end_index < len(files_to_display):
        self.safe_after(10, lambda: self._display_files_batch(files_to_display, end_index, batch_size))

def _display_files_batch_optimized(self, files_to_display, start_index, total_files, batch_size=50):
    """Version optimisée de l'affichage par batch"""
    print("_display_files_batch_optimized appelée")
    end_index = min(start_index + batch_size, len(files_to_display))
    
    # Afficher le batch actuel avec chargement rapide
    # for i in range(start_index, end_index):
    #     self._add_download_item_fast(files_to_display[i])
    
    _load_more_songs_below(self, unload=False)
    
    # Mettre à jour l'indicateur de progression
    if hasattr(self, 'loading_progress_label'):
        progress = int((end_index / total_files) * 100)
        self.loading_progress_label.config(text=f"Chargement... {progress}% ({end_index}/{total_files})")
    
    # Programmer le batch suivant si nécessaire
    if end_index < len(files_to_display):
        # Délai réduit pour un chargement plus fluide
        self.safe_after(5, lambda: self._display_files_batch_optimized(files_to_display, end_index, total_files, batch_size))
    else:
        # Chargement terminé, supprimer l'indicateur de progression
        if hasattr(self, 'loading_progress_label'):
            self.loading_progress_label.destroy()
            delattr(self, 'loading_progress_label')
        
        # Lancer le chargement différé des miniatures
        self._start_thumbnail_loading(files_to_display, self.downloads_container)

def _show_loading_progress(self, total_files):
    """Affiche un indicateur de progression pendant le chargement"""
    self.loading_progress_label = tk.Label(
        self.downloads_container,
        text=f"Chargement... 0% (0/{total_files})",
        bg='#3d3d3d',
        fg='#cccccc',
        font=('TkDefaultFont', 10),
        pady=20
    )
    self.loading_progress_label.pack(fill="x", padx=10, pady=10)


def _update_downloads_queue_visual(self):
    """Met à jour seulement l'affichage visuel des barres noires de queue sans recharger toute la liste"""
    try:
        # Vérifier si on est dans l'onglet téléchargements et qu'il y a des éléments affichés
        if not (hasattr(self, 'downloads_container') and 
                hasattr(self, 'current_library_tab') and 
                self.current_library_tab == "téléchargées"):
            return
        
        # Parcourir tous les frames d'éléments dans downloads_container
        if hasattr(self, 'downloads_container') and self.downloads_container.winfo_exists():
            for widget in self.downloads_container.winfo_children():
                try:
                    if widget.winfo_exists() and hasattr(widget, 'filepath'):  # C'est un frame d'élément de téléchargement
                        # Utiliser les méthodes seulement si elles existent
                        if hasattr(self, 'update_is_in_queue'):
                            self.update_is_in_queue(widget)
                        if hasattr(self, 'update_visibility_queue_indicator'):
                            self.update_visibility_queue_indicator(widget)
                except tk.TclError:
                    # Widget détruit, ignorer
                    continue
    except Exception as e:
        print(f"Erreur lors de la mise à jour visuelle des téléchargements: {e}")

def _refresh_downloads_library(self, preserve_scroll=False):
    """Met à jour la liste des téléchargements et le compteur"""
    try:
        # Toujours mettre à jour la liste des fichiers et le compteur, peu importe l'onglet
        downloads_dir = self.downloads_folder
        if os.path.exists(downloads_dir):
            # Extensions audio supportées
            audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
            
            # Sauvegarder l'ancien état pour comparaison si la liste existe
            old_files = set(self.all_downloaded_files) if hasattr(self, 'all_downloaded_files') else set()
            
            # Recharger la liste
            if not hasattr(self, 'all_downloaded_files'):
                self.all_downloaded_files = []
            else:
                self.all_downloaded_files.clear()
            
            if not hasattr(self, 'normalized_filenames'):
                self.normalized_filenames = {}
            else:
                self.normalized_filenames.clear()
            
            # Vider aussi le cache de recherche étendu
            if not hasattr(self, 'extended_search_cache'):
                self.extended_search_cache = {}
            else:
                self.extended_search_cache.clear()
            
            for filename in os.listdir(downloads_dir):
                if filename.lower().endswith(audio_extensions):
                    filepath = os.path.join(downloads_dir, filename)
                    self.all_downloaded_files.append(filepath)
                    # Mettre à jour le cache
                    normalized_name = os.path.basename(filepath).lower()
                    self.normalized_filenames[filepath] = normalized_name
            
            # Mettre à jour le compteur de fichiers téléchargés
            self.num_downloaded_files = len(self.all_downloaded_files)
            
            # Mettre à jour le texte du bouton (toujours)
            self._update_downloads_button()
            
            # Vérifier s'il y a de nouveaux fichiers et si on est dans l'onglet concerné
            new_files = set(self.all_downloaded_files)
            if new_files != old_files:
                # Vérifier si on est dans l'onglet bibliothèque et sous-onglet téléchargées
                current_tab = self.notebook.tab(self.notebook.select(), "text")
                if (current_tab == "Bibliothèque" and 
                    hasattr(self, 'current_library_tab') and 
                    self.current_library_tab == "téléchargées" and
                    hasattr(self, 'downloads_container')):
                    # Mettre à jour l'affichage seulement si on est dans l'onglet
                    if hasattr(self, 'library_search_entry') and self.library_search_entry.get().strip():
                        # Relancer la recherche avec le terme actuel
                        self._perform_library_search()
                    else:
                        # Afficher tous les fichiers
                        self._display_filtered_downloads(self.all_downloaded_files, preserve_scroll=preserve_scroll)
                        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la bibliothèque: {e}")
    

# ==================== SYSTÈME DE CACHE INDÉPENDANT ====================
# Le cache est maintenant géré par DownloadsManager de manière indépendante

def _add_download_item_fast(self, filepath):
    """Ajoute un élément de téléchargement à l'interface de manière rapide"""
    try:
        # Créer le frame principal pour cet élément
        item_frame = tk.Frame(
            self.downloads_container,
            bg='#3d3d3d',
            relief='flat',
            bd=1
        )
        item_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Frame pour l'image (miniature)
        img_frame = tk.Frame(item_frame, bg='#3d3d3d', width=60, height=60)
        img_frame.pack(side=tk.LEFT, padx=(5, 10), pady=5)
        img_frame.pack_propagate(False)
        
        # Label pour la miniature (sera chargée plus tard)
        thumbnail_label = tk.Label(
            img_frame,
            bg='#3d3d3d',
            text="♪",
            fg='#888888',
            font=('Arial', 20)
        )
        thumbnail_label.pack(expand=True)
        
        # Frame pour les informations textuelles
        info_frame = tk.Frame(item_frame, bg='#3d3d3d')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        
        # Nom du fichier
        filename = os.path.basename(filepath)
        name_label = tk.Label(
            info_frame,
            text=filename,
            bg='#3d3d3d',
            fg='white',
            font=('Arial', 10, 'bold'),
            anchor='w',
            justify='left'
        )
        name_label.pack(fill=tk.X, pady=(0, 2))
        
        # Frame pour la durée et les boutons
        bottom_frame = tk.Frame(info_frame, bg='#3d3d3d')
        bottom_frame.pack(fill=tk.X)
        
        # Label pour la durée (sera mis à jour plus tard)
        duration_label = tk.Label(
            bottom_frame,
            text="--:--",
            bg='#3d3d3d',
            fg='#888888',
            font=('Arial', 9),
            anchor='w'
        )
        duration_label.pack(side=tk.LEFT)
        
        # Bouton de lecture
        play_button = tk.Button(
            bottom_frame,
            text="▶",
            bg='#4a4a4a',
            fg='white',
            font=('Arial', 12),
            relief='flat',
            bd=0,
            padx=8,
            pady=2,
            command=lambda: self._play_download_file(filepath)
        )
        play_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Stocker les références pour le chargement différé
        item_frame.filepath = filepath
        item_frame.thumbnail_label = thumbnail_label
        item_frame.duration_label = duration_label
        
        # Bind pour la sélection
        def on_click(event):
            self._select_download_item(item_frame)
        
        for widget in [item_frame, info_frame, name_label]:
            widget.bind("<Button-1>", on_click)
        
        return item_frame
        
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'élément {filepath}: {e}")
        return None

def _play_download_file(self, filepath):
    """Lance la lecture d'un fichier téléchargé"""
    try:
        # Essayer d'utiliser la méthode du lecteur principal si disponible
        if hasattr(self, 'play_file'):
            self.play_file(filepath)
        elif hasattr(self, 'load_and_play'):
            self.load_and_play(filepath)
        else:
            print(f"Lecture demandée pour: {filepath}")
    except Exception as e:
        print(f"Erreur lors de la lecture de {filepath}: {e}")

def _select_download_item(self, item_frame):
    """Sélectionne un élément de téléchargement"""
    try:
        # Désélectionner tous les autres éléments
        for child in self.downloads_container.winfo_children():
            if hasattr(child, 'configure'):
                child.configure(bg='#3d3d3d')
        
        # Sélectionner cet élément
        item_frame.configure(bg='#555555')
        
        # Stocker la sélection
        self.selected_download = getattr(item_frame, 'filepath', None)
        
    except Exception as e:
        print(f"Erreur lors de la sélection: {e}")

def _start_thumbnail_loading(self, files_list, container):
    """Lance le chargement différé des miniatures et durées"""
    def load_metadata():
        try:
            for filepath in files_list:
                # Trouver le frame correspondant
                item_frame = None
                for child in container.winfo_children():
                    if hasattr(child, 'filepath') and child.filepath == filepath:
                        item_frame = child
                        break
                
                if not item_frame:
                    continue
                
                # Charger la durée via le gestionnaire indépendant
                try:
                    formatted_duration = self.downloads_manager.get_formatted_duration(filepath)
                    if hasattr(item_frame, 'duration_label'):
                        # Mettre à jour dans le thread principal
                        def update_duration():
                            try:
                                if item_frame.duration_label.winfo_exists():
                                    item_frame.duration_label.configure(text=formatted_duration)
                            except:
                                pass
                        
                        if hasattr(self, 'root') and self.root:
                            self.root.after(0, update_duration)
                except Exception as e:
                    print(f"Erreur chargement durée pour {filepath}: {e}")
                
                # Petite pause pour ne pas surcharger
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Erreur lors du chargement des métadonnées: {e}")
    
    # Lancer dans un thread séparé
    thread = threading.Thread(target=load_metadata, daemon=True)
    thread.start()

def _show_no_results_message(self):
    """Affiche un message quand il n'y a pas de résultats"""
    try:
        no_results_frame = tk.Frame(
            self.downloads_container,
            bg='#3d3d3d',
            height=200
        )
        no_results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=50)
        
        # Message principal
        message_label = tk.Label(
            no_results_frame,
            text="Aucun fichier trouvé",
            bg='#3d3d3d',
            fg='#888888',
            font=('Arial', 16, 'bold')
        )
        message_label.pack(pady=(50, 10))
        
        # Message secondaire
        sub_message_label = tk.Label(
            no_results_frame,
            text="Aucun fichier audio n'a été trouvé dans le dossier de téléchargements\nou ne correspond à votre recherche.",
            bg='#3d3d3d',
            fg='#666666',
            font=('Arial', 10),
            justify='center'
        )
        sub_message_label.pack(pady=(0, 20))
        
    except Exception as e:
        print(f"Erreur lors de l'affichage du message 'aucun résultat': {e}")

def _update_scrollbar(self):
    """Met à jour la région de scroll du canvas"""
    try:
        if hasattr(self, 'downloads_canvas') and self.downloads_canvas.winfo_exists():
            self.downloads_canvas.configure(scrollregion=self.downloads_canvas.bbox("all"))
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la scrollbar: {e}")

def _update_downloads_button(self):
    """Met à jour le texte du bouton téléchargements"""
    try:
        if hasattr(self, 'num_downloaded_files'):
            # Cette fonction sera appelée par le système principal si disponible
            pass
    except Exception as e:
        print(f"Erreur lors de la mise à jour du bouton: {e}")

def _on_library_search_change(self, event):
    """Gère les changements dans la barre de recherche"""
    try:
        query = self.library_search_entry.get().strip()
        
        # Utiliser le gestionnaire indépendant pour la recherche
        if query:
            filtered_files = self.downloads_manager.search_files(query)
        else:
            filtered_files = self.downloads_manager.get_all_files()
        
        # Afficher les résultats filtrés
        self._display_filtered_downloads(filtered_files)
        
    except Exception as e:
        print(f"Erreur lors de la recherche: {e}")

def _clear_library_search(self):
    """Efface la recherche et affiche tous les fichiers"""
    try:
        if hasattr(self, 'library_search_entry'):
            self.library_search_entry.delete(0, tk.END)
            
        # Afficher tous les fichiers
        all_files = self.downloads_manager.get_all_files()
        self._display_filtered_downloads(all_files)
        
    except Exception as e:
        print(f"Erreur lors de l'effacement de la recherche: {e}")

def play_all_downloads_ordered(self):
    """Lance la lecture de tous les téléchargements dans l'ordre"""
    try:
        all_files = self.downloads_manager.get_all_files()
        if all_files:
            print(f"Lecture de tous les téléchargements dans l'ordre: {len(all_files)} fichiers")
            # Essayer d'utiliser la méthode du lecteur principal si disponible
            if hasattr(self, 'play_playlist'):
                self.play_playlist(all_files)
            elif hasattr(self, 'play_file'):
                self.play_file(all_files[0])  # Jouer le premier fichier
        else:
            print("Aucun fichier à lire")
    except Exception as e:
        print(f"Erreur lors de la lecture ordonnée: {e}")

def play_all_downloads_shuffle(self):
    """Lance la lecture de tous les téléchargements en mode aléatoire"""
    try:
        import random
        all_files = self.downloads_manager.get_all_files()
        if all_files:
            shuffled_files = all_files.copy()
            random.shuffle(shuffled_files)
            print(f"Lecture de tous les téléchargements en mode aléatoire: {len(shuffled_files)} fichiers")
            # Essayer d'utiliser la méthode du lecteur principal si disponible
            if hasattr(self, 'play_playlist'):
                self.play_playlist(shuffled_files)
            elif hasattr(self, 'play_file'):
                self.play_file(shuffled_files[0])  # Jouer le premier fichier
        else:
            print("Aucun fichier à lire")
    except Exception as e:
        print(f"Erreur lors de la lecture aléatoire: {e}")

def _refresh_downloads_library(self, preserve_scroll=False):
    """Actualise la bibliothèque de téléchargements"""
    try:
        # Nettoyer et sauvegarder les caches
        if hasattr(self, 'downloads_manager'):
            self.downloads_manager.save_and_cleanup()
        
        # Recharger les fichiers
        if hasattr(self, 'load_downloaded_files'):
            self.load_downloaded_files()
        
        print("Bibliothèque de téléchargements actualisée")
    except Exception as e:
        print(f"Erreur lors de l'actualisation: {e}")

def _load_download_thumbnail_fallback(self, filepath, label):
    """Méthode de fallback pour charger les miniatures (ancienne méthode)"""
    try:
        # Chercher une image associée
        base_path = os.path.splitext(filepath)[0]
        for ext in ['.jpg', '.png', '.webp']:
            thumbnail_path = base_path + ext
            if os.path.exists(thumbnail_path):
                img = Image.open(thumbnail_path)
                img.thumbnail((80, 45), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label.configure(image=photo)
                label.image = photo
                return
        
        # Fallback à une icône par défaut
        default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
        photo = ImageTk.PhotoImage(default_icon)
        label.configure(image=photo)
        label.image = photo
        
    except Exception as e:
        print(f"Erreur fallback miniature: {e}")
        # Icône par défaut en cas d'erreur
        default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
        photo = ImageTk.PhotoImage(default_icon)
        label.configure(image=photo)
        label.image = photo

def play_all_downloads_ordered(self):
    """Joue toutes les musiques téléchargées dans l'ordre"""
    if not self.all_downloaded_files:
        return
    
    # Afficher un message de chargement
    self.status_bar.config(text="Chargement de la playlist...")
    
    # Désactiver temporairement les boutons pour éviter les clics multiples
    self._disable_play_buttons()
    
    # Copier la liste des fichiers téléchargés dans la playlist principale
    if len(self.main_playlist) > 0:
        self._clear_main_playlist()
    self.main_playlist.clear()
    self.main_playlist.extend(self.all_downloaded_files.copy())
    
    # Désactiver le mode aléatoire et réinitialiser l'index
    self.random_mode = False
    self.current_index = 0
    
    # Mettre à jour l'apparence du bouton random
    self.random_button.config(bg="#3d3d3d")
    
    # Démarrer la lecture immédiatement
    self.play_track()
    
    # Rafraîchir l'affichage de la playlist de manière différée pour éviter le lag
    self.root.after(50, lambda: self._refresh_main_playlist_display_async())
    
    # Réactiver les boutons et mettre à jour le statut final
    self.root.after(150, lambda: self._enable_play_buttons())
    self.root.after(200, lambda: self.status_bar.config(text=f"Lecture démarrée - {len(self.all_downloaded_files)} musiques chargées"))
    
def play_all_downloads_shuffle(self):
    """Joue toutes les musiques téléchargées en mode aléatoire"""
    if not self.all_downloaded_files:
        return
    
    # Afficher un message de chargement
    self.status_bar.config(text="Chargement de la playlist en mode aléatoire...")
    
    # Désactiver temporairement les boutons pour éviter les clics multiples
    self._disable_play_buttons()
    
    # Copier la liste des fichiers téléchargés dans la playlist principale
    if len(self.main_playlist) > 0:
        self._clear_main_playlist()
    self.main_playlist.clear()
    self.main_playlist.extend(self.all_downloaded_files.copy())
    
    # Activer le mode aléatoire et mélanger la playlist
    self.random_mode = True
    import random
    random.shuffle(self.main_playlist)
    self.current_index = 0
    
    # Mettre à jour l'apparence du bouton random
    self.random_button.config(bg="#4a8fe7")
    
    # Démarrer la lecture immédiatement
    self._refresh_main_playlist_display_async()
    self.play_track()
    
    # Rafraîchir l'affichage de la playlist de manière différée pour éviter le lag
    # self.root.after(50, lambda: self._refresh_main_playlist_display_async())
    
    # Réactiver les boutons et mettre à jour le statut final
    self.root.after(150, lambda: self._enable_play_buttons())
    self.root.after(200, lambda: self.status_bar.config(text=f"Lecture démarrée - {len(self.all_downloaded_files)} musiques chargées"))



def _get_adaptive_search_delay(self, query):
    """Calcule un délai de recherche adaptatif selon la longueur et le contenu de la requête"""
    if not query:
        return 0  # Pas de délai pour une recherche vide (affichage immédiat)
    
    query_length = len(query.strip())
    
    # Debounce différentiel selon la longueur
    if query_length <= 2:
        return 150  # Court pour éviter les recherches sur 1-2 lettres
    elif query_length <= 4:
        return 200  # Moyen pour les mots courts
    elif query_length <= 8:
        return 250  # Normal pour les mots moyens
    else:
        # return 300  # Plus long pour les recherches complexes
        return 1000  # Plus long pour les recherches complexes
    
def _on_library_search_change(self, event):
    """Appelée à chaque changement dans la barre de recherche (avec debounce différentiel)"""
    # Vérifier si on est en train de faire un refresh pour éviter la boucle infinie
    if hasattr(self, '_refreshing_downloads') and self._refreshing_downloads:
        return
    
    # Vérifier si l'application est en cours de destruction
    if hasattr(self, '_app_destroyed') and self._app_destroyed:
        return
    
    # Vérifier si le widget de recherche existe encore
    try:
        if not (hasattr(self, 'library_search_entry') and self.library_search_entry.winfo_exists()):
            return
    except:
        return
    
    # Obtenir la requête actuelle pour calculer le délai adaptatif
    current_query = self.library_search_entry.get().strip()
    
    # Éviter les recherches redondantes - ne déclencher que si le contenu a vraiment changé
    if hasattr(self, '_last_search_query') and self._last_search_query == current_query:
        return
    
    # Filtrer les touches qui ne modifient pas le contenu
    # Si on a un événement, vérifier que c'est une vraie modification de texte
    if event:
        # Touches à ignorer (touches de modification, navigation, etc.)
        ignored_keys = {
            'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R',
            'Super_L', 'Super_R', 'Meta_L', 'Meta_R', 'Win_L', 'Win_R',
            'Menu', 'Hyper_L', 'Hyper_R', 'ISO_Level3_Shift',
            'Up', 'Down', 'Left', 'Right', 'Home', 'End', 'Page_Up', 'Page_Down',
            'Insert', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'Caps_Lock', 'Num_Lock', 'Scroll_Lock', 'Pause', 'Print'
        }
        
        # Si c'est une touche à ignorer, ne pas déclencher la recherche
        if event.keysym in ignored_keys:
            return
    
    self._last_search_query = current_query
    
    # Annuler le timer précédent s'il existe
    if self.search_timer:
        try:
            self.root.after_cancel(self.search_timer)
        except:
            pass  # Ignorer les erreurs si le timer n'existe plus
    
    # Enregistrer le temps de début de recherche bibliothèque
    if current_query:  # Seulement si on a une requête
        self.library_search_start_time = time.time()
        
        # Vider le champ de recherche YouTube quand on fait une recherche dans la bibliothèque
        if hasattr(self, 'youtube_entry') and self.youtube_entry.get().strip():
            self.youtube_entry.delete(0, tk.END)
    
    adaptive_delay = self._get_adaptive_search_delay(current_query)
    
    # Programmer une nouvelle recherche après le délai adaptatif
    if hasattr(self, 'safe_after'):
        self.search_timer = self.safe_after(adaptive_delay, self._perform_library_search)
    else:
        self.search_timer = self.root.after(adaptive_delay, self._perform_library_search)

def _build_extended_search_cache(self, filepath):
    """Construit le cache de recherche étendu pour un fichier (nom + artiste + album)"""
    if filepath in self.extended_search_cache:
        return self.extended_search_cache[filepath]
    
    # Commencer avec le nom de fichier
    search_text_parts = []
    
    # Ajouter le nom de fichier
    filename = os.path.basename(filepath)
    search_text_parts.append(filename)
    
    # Ajouter les métadonnées audio (artiste et album)
    try:
        artist, album = self._get_audio_metadata(filepath)
        if artist:
            search_text_parts.append(artist)
        if album:
            search_text_parts.append(album)
    except:
        pass  # Ignorer les erreurs de lecture des métadonnées
    
    # Combiner tout en minuscules pour la recherche
    search_text = " ".join(search_text_parts).lower()
    
    # Mettre en cache
    self.extended_search_cache[filepath] = search_text
    
    return search_text

def _perform_library_search(self):
    """Effectue la recherche réelle (appelée après le délai) - version étendue incluant artiste et album"""
    # Vérifier si l'application est en cours de destruction
    if hasattr(self, '_app_destroyed') and self._app_destroyed:
        return
    
    # Vérifier si les widgets existent encore
    try:
        if not (hasattr(self, 'library_search_entry') and self.library_search_entry.winfo_exists()):
            return
    except:
        return
    
    search_term = self.library_search_entry.get().lower().strip()
    
    if not search_term:
        # Si la recherche est vide, afficher tous les fichiers
        self._display_filtered_downloads(self.all_downloaded_files)
        # print('debug: Affichage de tous les fichiers, _perform_library_search')
    else:
        # Diviser le terme de recherche en mots individuels
        search_words = search_term.split()
        
        # Filtrer les fichiers selon le terme de recherche (recherche étendue)
        filtered_files = []
        for filepath in self.all_downloaded_files:
            # Construire le texte de recherche étendu (nom + artiste + album)
            extended_search_text = self._build_extended_search_cache(filepath)
            
            # Vérifier si tous les mots de recherche sont présents dans le texte étendu
            all_words_found = all(word in extended_search_text for word in search_words)
            
            if all_words_found:
                filtered_files.append(filepath)
        
        self._display_filtered_downloads(filtered_files)
        
        # Calculer et afficher le temps de recherche bibliothèque
        if self.library_search_start_time:
            search_duration = time.time() - self.library_search_start_time
            self.last_search_time = search_duration
            self._update_stats_bar()

def _clear_library_search(self):
    """Efface la recherche et affiche tous les fichiers"""
    # Annuler le timer de recherche s'il existe
    if self.search_timer:
        try:
            self.root.after_cancel(self.search_timer)
        except:
            pass  # Ignorer les erreurs si le timer n'existe plus
        self.search_timer = None
    
    self.library_search_entry.delete(0, tk.END)
    self._display_filtered_downloads(self.all_downloaded_files)

def select_library_item(self, current_filepath):
    """Met en surbrillance l'élément sélectionné dans la bibliothèque"""
    # Vérifier si on est dans l'onglet bibliothèque et si le container existe
    if (hasattr(self, 'downloads_container') and 
        self.downloads_container.winfo_exists()):
        
        # Désélectionner tous les autres éléments et sélectionner le bon
        for child in self.downloads_container.winfo_children():
            try:
                if child.winfo_exists() and hasattr(child, 'filepath'):
                    if child.filepath == current_filepath:
                        # Sélectionner cet élément
                        child.selected = True
                        self._set_item_colors(child, '#5a9fd8')  # Couleur de surbrillance (bleu)
                    else:
                        # Désélectionner les autres
                        child.selected = False
                        self._set_item_colors(child, '#4a4a4a')  # Couleur normale
            except tk.TclError:
                # Widget détruit, ignorer
                continue

def _update_scrollbar(self):
    """Force la mise à jour de la scrollbar"""
    try:
        if hasattr(self, 'downloads_container') and hasattr(self, 'downloads_canvas'):
            if self.downloads_container.winfo_exists() and self.downloads_canvas.winfo_exists():
                # Forcer la mise à jour du layout
                self.downloads_container.update_idletasks()
                # Mettre à jour la région de scroll
                self.downloads_canvas.configure(scrollregion=self.downloads_canvas.bbox("all"))
                # S'assurer que le scroll est en haut
                self.downloads_canvas.yview_moveto(0.0)
    except tk.TclError:
        # Widgets détruits, ignorer
        pass


##

def _update_canvas_scroll_region(self):
        """Met à jour la région de scroll du canvas pour permettre le scroll avec la molette"""
        try:
            print("_update_canvas_scroll_region appelée")
            # Optimisation: Éviter les mises à jour trop fréquentes
            if hasattr(self, '_last_scroll_region_update'):
                current_time = time.time()
                min_update_interval = 0.05  # 50ms entre les mises à jour
                if current_time - self._last_scroll_region_update < min_update_interval:
                    return
            self._last_scroll_region_update = time.time()
            
            if not (hasattr(self, 'playlist_canvas') and hasattr(self, 'playlist_container')):
                return
                
            if not (self.playlist_canvas.winfo_exists() and self.playlist_container.winfo_exists()):
                return
            
            # Optimisation: Utiliser update_idletasks seulement si nécessaire
            # Vérifier si la taille a changé depuis la dernière mise à jour
            current_width = self.playlist_container.winfo_width()
            current_height = self.playlist_container.winfo_height()
            
            if (not hasattr(self, '_last_container_size') or 
                self._last_container_size != (current_width, current_height)):
                # Forcer la mise à jour de la géométrie seulement si nécessaire
                self.playlist_container.update_idletasks()
                self._last_container_size = (current_width, current_height)
            
            # Pour le système de fenêtrage, on doit simuler une région de scroll plus grande
            # que ce qui est affiché pour permettre le scroll infini
            children = self.playlist_container.winfo_children()
            children_count = len(children)
            
            if children_count > 0:
                if USE_NEW_CONFIG:
                    item_height = get_main_playlist_config('item_height_estimate')
                    total_songs = len(self.main_playlist)
                    enable_dynamic = get_main_playlist_config('enable_dynamic_scroll')
                else:
                    item_height = 60
                    total_songs = len(self.main_playlist)
                    enable_dynamic = True
                
                # Si le système intelligent est activé, adapter la région de scroll
                if (get_config('enable_smart_loading') and 
                    hasattr(self, '_last_window_start') and hasattr(self, '_last_window_end')):
                    print('1')
                    
                    # Mode intelligent : région basée sur les éléments chargés uniquement
                    start_index = getattr(self, '_last_window_start', 0)
                    end_index = getattr(self, '_last_window_end', children_count)
                    
                    # Hauteur réelle basée sur les éléments effectivement chargés
                    displayed_height = children_count * item_height
                    self.playlist_canvas.configure(scrollregion=(0, 0, 0, displayed_height))
                    
                    if get_config('debug_scroll'):
                        print(f"🧠 Scroll region intelligente: {displayed_height}px pour {children_count} éléments chargés ({start_index}-{end_index})")
                        
                elif enable_dynamic and total_songs > children_count:
                    print('2')
                    # Mode dynamique : région virtuelle pour toutes les musiques
                    # virtual_height = total_songs * item_height
                    
                    virtual_height = children_count * item_height
                    self.playlist_canvas.configure(scrollregion=(0, 0, 0, virtual_height))
                    
                    if get_config('debug_scroll'):
                        print(f"Scroll region virtuelle: {virtual_height}px pour {total_songs} musiques ({children_count} affichées)")
                else:
                    print('3')
                    # Région de scroll normale basée sur les éléments affichés
                    displayed_height = children_count * item_height
                    self.playlist_canvas.configure(scrollregion=(0, 0, 0, displayed_height))
                    
                    if get_config('debug_scroll'):
                        print(f"Scroll region normale: {displayed_height}px pour {children_count} éléments")
                
                # Configurer le système de scroll dynamique unifié
                # if get_config('enable_dynamic_scroll'):
                #     self._setup_dynamic_scroll()
                # elif enable_dynamic:
                #     self._setup_dynamic_scroll()
            else:
                # Pas d'enfants, réinitialiser la région de scroll
                self.playlist_canvas.configure(scrollregion=(0, 0, 0, 0))
                    
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la région de scroll: {e}")

def _setup_infinite_scroll(self):
        """Configure le scroll infini pour charger plus d'éléments"""
        try:
            if not hasattr(self, 'playlist_canvas'):
                return
            
            # Initialiser les variables de state pour le scroll intelligent
            self._user_is_scrolling = False
            self._user_scroll_timer = None
            self._last_current_index = getattr(self, 'current_index', 0)
            self._auto_centering = False  # Flag pour éviter les boucles
            
            # Binding pour détecter les changements de position de scroll
            # self.playlist_canvas.bind('<Configure>', self._on_playlist_canvas_configure)
            
            # IMPORTANT: Binding pour détecter les changements de position de scroll
            # C'est ce qui manquait pour synchroniser l'affichage avec la position de scroll
            def on_scroll_position_change(*args):
                """Appelée quand la position de scroll change par la souris"""
                # self._update_display_based_on_scroll_position()
                print('on_scroll_position_change appelé')
            
            # Connecter le callback à la scrollbar
            if hasattr(self, 'playlist_scrollbar') and self.playlist_scrollbar:
                self.playlist_scrollbar.config(command=lambda *args: [
                    self.playlist_canvas.yview(*args),
                    on_scroll_position_change()
                ])
            
            # Aussi connecter au canvas directement
            # self.playlist_canvas.bind('<MouseWheel>', self._on_scroll_with_update)
            # self.playlist_canvas.bind('<Button-4>', self._on_scroll_with_update)  # Linux
            # self.playlist_canvas.bind('<Button-5>', self._on_scroll_with_update)  # Linux
                
        except Exception as e:
            print(f"Erreur lors de la configuration du scroll infini: {e}")

def _setup_dynamic_scroll(self):
        """Configure le système de scroll dynamique unifié (combine infinite et progressive)"""
        try:
            if not hasattr(self, 'playlist_canvas'):
                return
            
            # Vérifier si le système est activé
            if not (get_config('enable_dynamic_scroll')):
                return
            
            # Initialiser les variables de state pour le scroll intelligent
            self._user_is_scrolling = False
            self._user_scroll_timer = None
            self._last_current_index = getattr(self, 'current_index', 0)
            self._auto_centering = False  # Flag pour éviter les boucles
            
            # Variables pour le chargement progressif
            self._last_scroll_position = 0.0
            self._progressive_loading_active = True
            
            # Initialiser les variables de fenêtrage pour la compatibilité
            if not hasattr(self, '_last_window_start'):
                _last_window_start = 0
            if not hasattr(self, '_last_window_end'):
                # Initialiser avec une fenêtre basée sur la position courante
                current_index = getattr(self, 'current_index', 0)
                initial_load = get_main_playlist_config('initial_load_after_current')
                _last_window_end = min(len(self.main_playlist) if hasattr(self, 'main_playlist') else 0, 
                                          current_index + initial_load)
            
            # Binding pour détecter les changements de position de scroll
            # def on_dynamic_scroll_change(*args):
            #     """Appelée quand la position de scroll change"""
            #     try:
            #         # Gérer le scroll infini (mise à jour de l'affichage)
            #         self._update_display_based_on_scroll_position()
                    
            #         # Gérer le chargement progressif
            #         self._on_dynamic_scroll()
                    
            #     except Exception as e:
            #         if get_config('debug_scroll'):
            #             print(f"❌ Erreur scroll dynamique: {e}")
            
            # # Connecter le callback à la scrollbar
            # if hasattr(self, 'playlist_scrollbar') and self.playlist_scrollbar:
            #     self.playlist_scrollbar.config(command=lambda *args: [
            #         self.playlist_canvas.yview(*args),
            #         on_dynamic_scroll_change()
            #     ])
            
            if get_config('debug_scroll'):
                print("✅ Système de scroll dynamique configuré")
                
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"❌ Erreur configuration scroll dynamique: {e}")

def _on_dynamic_scroll(self, event):
        """Gère le scroll dynamique (combine infinite et progressive)"""
        try:
            print("_on_dynamic_scroll appelée")
            if not (get_config('enable_dynamic_scroll')):
                return
            
            # Vérifier la position de scroll
            try:
                # Obtenir la position de scroll actuelle (0.0 = haut, 1.0 = bas)
                scroll_top, scroll_bottom = self.playlist_canvas.yview()
                scroll_position = scroll_bottom  # Position vers le bas
                
                # Seuil de déclenchement pour le chargement progressif
                threshold = get_main_playlist_config('scroll_trigger_threshold')
                
                # Si on atteint le seuil, charger plus d'éléments (chargement progressif)
                # if scroll_position >= threshold:
                #     self._load_more_on_scroll()
                
                # Vérifier si on doit charger plus d'éléments en haut ou en bas (scroll infini)
                scroll_threshold = get_main_playlist_config('scroll_threshold')
                
                # Vérifier les verrous de chargement
                loading_up = getattr(self, '_loading_up_in_progress', False)
                loading_down = getattr(self, '_loading_down_in_progress', False)
                
                if scroll_top <= scroll_threshold and not loading_up:
                    # Proche du haut, charger plus d'éléments au-dessus (si pas déjà en cours)
                    if hasattr(event, 'delta') and event.delta:
                        if get_config('debug_scroll'):
                            print("🔼 Déclenchement chargement vers le haut")
                            if event.delta >= 0:
                                self._load_more_songs_above()
                
                
                elif scroll_bottom >= (1.0 - scroll_threshold) and not loading_down:
                    # Proche du bas, charger plus d'éléments en-dessous (si pas déjà en cours)
                    if hasattr(event, 'delta') and event.delta:
                        if event.delta <= 0:
                            if get_config('debug_scroll'):
                                print("🔽 Déclenchement chargement vers le bas")
                            self._load_more_songs_below()
                
                elif loading_up or loading_down:
                    if get_config('debug_scroll'):
                        direction = "haut" if loading_up else "bas"
                        print(f"⏸️ Chargement vers le {direction} en cours, scroll ignoré")
                    
                    # self.playlist_canvas.yview()
                    # self.playlist_canvas.yview_scroll(0, "units")


                # Sauvegarder la position pour la prochaine fois
                self._last_scroll_position = scroll_position
                
            except Exception as e:
                if get_config('debug_scroll'):
                    print(f"❌ Erreur position scroll dynamique: {e}")
                    
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"❌ Erreur scroll dynamique: {e}")


def _update_display_based_on_scroll_position(self):
        """Met à jour l'affichage des musiques basé sur la position de scroll"""
        try:
            if not (hasattr(self, 'playlist_canvas') and self.playlist_canvas.winfo_exists()):
                return
            
            if not (get_config('enable_dynamic_scroll')):
                return
            
            # Obtenir la position actuelle du scroll (0.0 à 1.0)
            try:
                scroll_top, scroll_bottom = self.playlist_canvas.yview()
            except:
                return
            
            # Calculer quelle partie de la playlist devrait être visible
            total_songs = len(self.main_playlist)
            if total_songs == 0:
                return
            
            # Convertir la position de scroll en index de musique
            # scroll_top = 0.0 → première musique
            # scroll_top = 1.0 → dernière musique
            center_index = int(scroll_top * (total_songs - 1))
            center_index = max(0, min(center_index, total_songs - 1))
            
            # Calculer la nouvelle fenêtre d'affichage
            songs_before = get_main_playlist_config('songs_before_current') if USE_NEW_CONFIG else 10
            songs_after = get_main_playlist_config('songs_after_current') if USE_NEW_CONFIG else 10
            
            new_start = max(0, center_index - songs_before)
            new_end = min(total_songs, center_index + songs_after + 1)
            
            # Vérifier si on doit mettre à jour l'affichage
            current_start = getattr(self, '_last_window_start', -1)
            current_end = getattr(self, '_last_window_end', -1)
            
            # Seuil pour éviter les mises à jour trop fréquentes
            threshold = 5  # Mettre à jour seulement si on a bougé de plus de 5 éléments
            
            if (abs(new_start - current_start) > threshold or 
                abs(new_end - current_end) > threshold or
                current_start == -1):
                
                if get_config('debug_scroll'):
                    print(f"Mise à jour affichage: scroll={scroll_top:.3f}, center={center_index}, fenêtre={new_start}-{new_end}")
                
                # Mettre à jour l'affichage avec la nouvelle fenêtre
                self._update_windowed_display(new_start, new_end, center_index)
                
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur lors de la mise à jour basée sur le scroll: {e}")

def _update_windowed_display(self, start_index, end_index, center_index):
        """Met à jour l'affichage avec une nouvelle fenêtre"""
        try:
            # Sauvegarder les nouveaux paramètres de fenêtre
            _last_window_start = start_index
            _last_window_end = end_index
            
            # Vider le container actuel
            for child in self.playlist_container.winfo_children():
                child.destroy()
            
            # Ajouter les nouveaux éléments
            for i in range(start_index, end_index):
                if i < len(self.main_playlist):
                    filepath = self.main_playlist[i]
                    self._add_main_playlist_item(filepath, song_index=i)
            
            # Remettre en surbrillance la chanson en cours si elle est visible
            if (hasattr(self, 'current_index') and 
                start_index <= self.current_index < end_index):
                try:
                    # Trouver le frame correspondant à current_index
                    children = self.playlist_container.winfo_children()
                    relative_index = self.current_index - start_index
                    if 0 <= relative_index < len(children):
                        self.select_playlist_item(children[relative_index], auto_scroll=False)
                except:
                    pass
            
            # Mettre à jour la région de scroll
            self.root.after(10, self._update_canvas_scroll_region)
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'affichage fenêtré: {e}")

def _mark_user_scrolling(self):
        """Marque que l'utilisateur est en train de scroller manuellement"""
        try:
            print("_mark_user_scrolling est appelé")
            if not (get_config('detect_manual_scroll')):
                return
            
            self._user_is_scrolling = True
            
            # Annuler le timer précédent s'il existe
            if self._user_scroll_timer:
                self.root.after_cancel(self._user_scroll_timer)
            
            # Programmer un nouveau timer
            timeout = get_main_playlist_config('user_scroll_timeout') if USE_NEW_CONFIG else 3000
            self._user_scroll_timer = self.root.after(timeout, self._on_user_scroll_timeout)
            
            if get_config('debug_scroll'):
                print("Utilisateur scroll manuellement détecté")
                
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur lors du marquage du scroll utilisateur: {e}")

def _on_user_scroll_timeout(self):
        """Appelée quand l'utilisateur a fini de scroller"""
        try:
            self._user_is_scrolling = False
            self._user_scroll_timer = None
            
            if get_config('debug_scroll'):
                print("Fin du scroll utilisateur détectée")
            
            # Vérifier si on doit recentrer sur la chanson courante
            if get_config('auto_center_on_song_change'):
                self._check_and_recenter_if_needed()
                
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur lors du timeout de scroll: {e}")

def _check_and_recenter_if_needed(self):
        """Vérifie si on doit recentrer sur la chanson courante"""
        try:
            print("_check_and_recenter_if_needed est appelé")
            if not hasattr(self, 'current_index'):
                return
            
            # Vérifier si la chanson courante a changé
            current_index = self.current_index
            last_index = getattr(self, '_last_current_index', current_index)
            
            if current_index != last_index:
                # La chanson a changé, décider si on doit recentrer
                if self._should_recenter_on_song_change():
                    self._auto_center_on_current_song()
                
                # Mettre à jour l'index de référence
                self._last_current_index = current_index
                
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur lors de la vérification de recentrage: {e}")

def _should_recenter_on_song_change(self):
        """Détermine si on doit recentrer sur la nouvelle chanson courante"""
        try:
            if not (get_config('auto_center_on_song_change')):
                return False
            
            # Si l'utilisateur n'a pas scrollé ou a fini de scroller
            if not self._user_is_scrolling:
                return True
            
            # Si l'option "garder position utilisateur" est désactivée
            if not get_main_playlist_config('keep_user_position'):
                return True
            
            return False
            
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur lors de la décision de recentrage: {e}")
            return True  # Par défaut, recentrer

def _auto_center_on_current_song(self):
        """Recentre automatiquement l'affichage sur la chanson courante"""
        try:
            if not hasattr(self, 'current_index') or self._auto_centering:
                return
            
            current_index = self.current_index
            total_songs = len(self.main_playlist)
            
            if not (0 <= current_index < total_songs):
                return
            
            # Marquer qu'on fait un auto-centering pour éviter de déclencher le scroll utilisateur
            self._auto_centering = True
            
            # Calculer la nouvelle fenêtre centrée sur la chanson courante
            songs_before = get_main_playlist_config('songs_before_current') if USE_NEW_CONFIG else 10
            songs_after = get_main_playlist_config('songs_after_current') if USE_NEW_CONFIG else 10
            
            new_start = max(0, current_index - songs_before)
            new_end = min(total_songs, current_index + songs_after + 1)
            
            if get_config('debug_scroll'):
                print(f"Auto-recentrage sur chanson {current_index}, fenêtre {new_start}-{new_end}")
            
            # Mettre à jour l'affichage
            self._update_windowed_display(new_start, new_end, current_index)
            
            # Calculer la position de scroll pour centrer la chanson courante
            if total_songs > 1:
                scroll_position = current_index / (total_songs - 1)
                scroll_position = max(0.0, min(1.0, scroll_position))
                
                # Appliquer la position de scroll
                self.playlist_canvas.yview_moveto(scroll_position)
                
                if get_config('debug_scroll'):
                    print(f"Scroll positionné à {scroll_position:.3f}")
            
            # Marquer qu'on a fini l'auto-centering
            self.root.after(100, lambda: setattr(self, '_auto_centering', False))
                
        except Exception as e:
            self._auto_centering = False
            if get_config('debug_scroll'):
                print(f"Erreur lors de l'auto-recentrage: {e}")

def _calculate_smart_window(self):
        """Calcule la fenêtre intelligente à garder chargée"""
        try:
            if not (get_config('enable_smart_loading')):
                return None, None
            
            total_songs = len(self.main_playlist)
            if total_songs == 0:
                return 0, 0
            
            current_index = getattr(self, 'current_index', 0)
            current_index = max(0, min(current_index, total_songs - 1))
            
            # Zone 1: Autour de la chanson courante (garantie 10+1+10)
            songs_before = get_main_playlist_config('songs_before_current')
            songs_after = get_main_playlist_config('songs_after_current')
            
            current_start = max(0, current_index - songs_before)
            current_end = min(total_songs, current_index + songs_after + 1)
            
            # Zone 2: Autour de la position de vue utilisateur
            view_center = self._get_current_view_position()
            if view_center is not None:
                view_buffer = get_main_playlist_config('keep_buffer_around_view')
                view_start = max(0, view_center - view_buffer)
                view_end = min(total_songs, view_center + view_buffer + 1)
            else:
                view_start, view_end = current_start, current_end
            
            # Si la distance entre vue et courante est très grande, privilégier des zones séparées
            distance_view_current = abs(view_center - current_index) if view_center is not None else 0
            max_union_distance = 100  # Distance max pour faire l'union
            
            if distance_view_current <= max_union_distance:
                # Distance raisonnable : faire l'union des deux zones
                smart_start = min(current_start, view_start)
                smart_end = max(current_end, view_end)
                
                # Ajouter un buffer supplémentaire autour de la chanson courante
                buffer_current = get_main_playlist_config('keep_buffer_around_current')
                buffered_start = max(0, current_index - buffer_current)
                buffered_end = min(total_songs, current_index + buffer_current + 1)
                
                # Union finale
                final_start = min(smart_start, buffered_start)
                final_end = max(smart_end, buffered_end)
            else:
                # Distance trop grande : privilégier seulement la zone de la chanson courante
                buffer_current = get_main_playlist_config('keep_buffer_around_current')
                final_start = max(0, current_index - buffer_current)
                final_end = min(total_songs, current_index + buffer_current + 1)
                
                if get_config('debug_scroll'):
                    print(f"Distance trop grande ({distance_view_current}), privilégiant zone courante seulement")
            
            if get_config('debug_scroll'):
                print(f"Fenêtre intelligente calculée: {final_start}-{final_end} (courante: {current_index}, vue: {view_center})")
            
            return final_start, final_end
            
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur calcul fenêtre intelligente: {e}")
            return None, None

def _get_current_view_position(self):
        """Détermine la position centrale de ce que voit l'utilisateur"""
        try:
            if not hasattr(self, 'playlist_canvas') or not self.playlist_canvas.winfo_exists():
                return None
            
            # Obtenir la position de scroll actuelle
            try:
                scroll_top, scroll_bottom = self.playlist_canvas.yview()
                scroll_center = (scroll_top + scroll_bottom) / 2
            except:
                return None
            
            # Convertir en index de musique
            total_songs = len(self.main_playlist)
            if total_songs <= 1:
                return 0
            
            # scroll_center = 0.0 → première musique, 1.0 → dernière musique
            view_index = int(scroll_center * (total_songs - 1))
            view_index = max(0, min(view_index, total_songs - 1))
            
            return view_index
            
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur détection position vue: {e}")
            return None

def _smart_load_unload(self):
        """SYSTÈME HYBRIDE : Ancien système OU nouveau système progressif selon la config"""
        try:
            # Nouveau système dynamique activé ?
            # if get_config('enable_dynamic_scroll'):
            # return self._progressive_load_system()
            return self._load_more_songs_below()
            
            # # Ancien système fenêtré (si encore activé)
            # if get_config('enable_smart_loading'):
            #     return self._old_smart_load_system()
                
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"❌ Erreur système de chargement: {e}")

  

def _progressive_load_system(self):
        """NOUVEAU SYSTÈME : Chargement progressif (jamais de déchargement)"""
        try:
            if not self.main_playlist:
                return
                
            current_index = getattr(self, 'current_index', 0)
            total_songs = len(self.main_playlist)
            
            # Sécurité: Index valide
            current_index = max(0, min(current_index, total_songs - 1))
            
            if get_config('debug_scroll'):
                print(f"🎵 PROGRESSIVE LOAD: Position courante {current_index}")
                
            # Vérifier ce qui est déjà chargé
            currently_loaded = len(self.playlist_container.winfo_children()) if hasattr(self, 'playlist_container') else 0
            
            # Calculer combien charger (courante + X suivantes)
            initial_load = get_main_playlist_config('initial_load_after_current')
            target_end = min(total_songs, current_index + initial_load)
            # Premier chargement depuis la chanson courante
            start_from = current_index
            
            if currently_loaded == 0:
                # Premier chargement : depuis la chanson courante
                if get_config('debug_scroll'):
                    print(f"🆕 Premier chargement progressif: {start_from} à {target_end-1}")
            else:
                # Vérifier si on doit charger plus
                last_loaded = self._get_last_loaded_index()
                if last_loaded >= target_end:
                    if get_config('debug_scroll'):
                        print(f"✅ Chargement déjà suffisant (jusqu'à {last_loaded})")
                    return
                start_from = last_loaded
                
            # Charger de start_from jusqu'à target_end SANS décharger l'existant
            self._append_progressive_items(start_from, target_end)
            
            # Mettre à jour les variables de fenêtrage pour la compatibilité
            if not hasattr(self, '_last_window_start'):
                _last_window_start = start_from
            if not hasattr(self, '_last_window_end') or _last_window_end < target_end:
                _last_window_end = target_end
            
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"❌ Erreur chargement progressif: {e}")
                
def _get_last_loaded_index(self):
        """Trouve le dernier index chargé dans la playlist"""
        try:
            children = self.playlist_container.winfo_children()
            if not children:
                return getattr(self, 'current_index', 0)
                
            max_index = 0
            for child in children:
                if hasattr(child, 'song_index'):
                    max_index = max(max_index, child.song_index)
                    
            return max_index + 1
            
        except Exception:
            return getattr(self, 'current_index', 0)
            
def _append_progressive_items(self, start_index, end_index):
        """Ajoute des éléments progressivement SANS supprimer les existants"""
        try:
            if start_index >= end_index or start_index >= len(self.main_playlist):
                return
                
            loaded_count = 0
            
            for i in range(start_index, min(end_index, len(self.main_playlist))):
                if not self._is_index_already_loaded(i):
                    filepath = self.main_playlist[i]
                    try:
                        self._add_main_playlist_item(filepath, song_index=i)
                        loaded_count += 1
                    except Exception as e:
                        if get_config('debug_scroll'):
                            print(f"⚠️ Erreur chargement item {i}: {e}")
            
            if get_config('debug_scroll') and loaded_count > 0:
                print(f"✅ {loaded_count} nouveaux éléments chargés ({start_index}-{end_index-1})")
                total_loaded = len(self.playlist_container.winfo_children())
                print(f"📊 Total chargé: {total_loaded}/{len(self.main_playlist)}")
                
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"❌ Erreur append progressif: {e}")
                
def _is_index_already_loaded(self, index):
        """Vérifie si un index spécifique est déjà chargé"""
        try:
            children = self.playlist_container.winfo_children()
            for child in children:
                if hasattr(child, 'song_index') and child.song_index == index:
                    return True
            return False
        except Exception:
            return False

def _setup_progressive_scroll_detection(self):
        """Configure la détection de scroll pour le chargement progressif"""
        try:
            if not (get_config('enable_dynamic_scroll')):
                return
                
            if not (hasattr(self, 'playlist_canvas') and self.playlist_canvas):
                return
            
            # Nous n'utilisons plus de binding direct ici
            # Le chargement progressif est maintenant géré par _check_infinite_scroll
            # qui est appelé après chaque événement de scroll
                
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"❌ Erreur config scroll progressif: {e}")


def _force_reload_window(self, start_index, end_index):
        """Force le rechargement d'une fenêtre spécifique - PROTECTION INDEX"""
        try:
            # SÉCURITÉ : Valider les paramètres d'entrée
            if not self.main_playlist:
                return
                
            total_songs = len(self.main_playlist)
            
            # Protection absolue contre les index invalides
            start_index = max(0, min(start_index, total_songs))
            end_index = max(start_index, min(end_index, total_songs))
            
            if start_index < 0 or end_index < 0 or start_index >= total_songs:
                if get_config('debug_scroll'):
                    print(f"❌ ABORT FORCE RELOAD: Index invalides {start_index}-{end_index} (total: {total_songs})")
                return
            
            if start_index >= end_index:
                if get_config('debug_scroll'):
                    print(f"❌ ABORT FORCE RELOAD: Fenêtre vide {start_index}-{end_index}")
                return
                
            if get_config('debug_scroll'):
                print(f"🔥 FORCE RELOAD SÉCURISÉ: {start_index}-{end_index} (total: {total_songs})")
                
            # Étape 1: DÉCHARGER TOUT (vider complètement)
            try:
                children = self.playlist_container.winfo_children()
                decharges = 0
                for widget in children:
                    try:
                        if widget.winfo_exists():
                            widget.destroy()
                            decharges += 1
                    except tk.TclError:
                        continue
                
                if get_config('debug_scroll'):
                    print(f"✅ {decharges} éléments déchargés")
                    
            except Exception as e:
                if get_config('debug_scroll'):
                    print(f"⚠️ Erreur déchargement: {e}")
            
            # Étape 2: RECHARGER la fenêtre cible avec vérifications
            charges = 0
            for i in range(start_index, end_index):
                # Double vérification de sécurité
                if 0 <= i < len(self.main_playlist):
                    filepath = self.main_playlist[i]
                    try:
                        self._add_main_playlist_item(filepath, song_index=i)
                        charges += 1
                    except Exception as e:
                        if get_config('debug_scroll'):
                            print(f"⚠️ Erreur chargement item {i}: {e}")
                elif get_config('debug_scroll'):
                    print(f"⚠️ Index {i} hors limites, ignoré")
            
            if get_config('debug_scroll'):
                print(f"✅ {charges} éléments rechargés")
                non_charges = len(self.main_playlist) - charges
                if non_charges > 0:
                    print(f"🎯 {non_charges} éléments NON chargés (optimisation mémoire)")
            
            # Étape 3: Remettre en surbrillance la chanson courante
            self._highlight_current_song_in_window(start_index, end_index)
            
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"❌ Erreur force reload: {e}")

def _highlight_current_song_in_window(self, start_index, end_index):
        """Remet en surbrillance la chanson courante si elle est dans la fenêtre"""
        try:
            current_index = getattr(self, 'current_index', 0)
            
            if start_index <= current_index < end_index:
                widgets = self.playlist_container.winfo_children()
                relative_index = current_index - start_index
                
                if 0 <= relative_index < len(widgets):
                    widget = widgets[relative_index]
                    if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                        self.select_playlist_item(widget, auto_scroll=False)
                        
                        if get_config('debug_scroll'):
                            print(f"✅ Chanson courante ({current_index}) remise en surbrillance")
            
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"⚠️ Erreur highlight: {e}")

def _unload_unused_items(self, target_start, target_end, current_start, current_end):
        """Décharge les éléments qui ne sont plus nécessaires"""
        try:
            if current_start == -1 or current_end == -1:
                return  # Pas d'éléments actuellement chargés
            
            unload_threshold = get_main_playlist_config('unload_threshold')
            current_index = getattr(self, 'current_index', 0)
            
            # Trouver les éléments à décharger
            items_to_unload = []
            
            # Éléments avant la nouvelle fenêtre
            if current_start < target_start:
                for i in range(current_start, min(target_start, current_end)):
                    # Ne décharger que si assez loin de la chanson courante
                    distance_from_current = abs(i - current_index)
                    if distance_from_current > unload_threshold:
                        items_to_unload.append(i)
            
            # Éléments après la nouvelle fenêtre
            if current_end > target_end:
                for i in range(max(target_end, current_start), current_end):
                    # Ne décharger que si assez loin de la chanson courante
                    distance_from_current = abs(i - current_index)
                    if distance_from_current > unload_threshold:
                        items_to_unload.append(i)
            
            # Décharger les éléments
            if items_to_unload:
                if get_config('debug_scroll'):
                    print(f"Déchargement de {len(items_to_unload)} éléments: {items_to_unload[:5]}{'...' if len(items_to_unload) > 5 else ''}")
                
                children = self.playlist_container.winfo_children()
                for i, child in enumerate(children):
                    # Calculer l'index réel de cet enfant
                    real_index = current_start + i
                    if real_index in items_to_unload:
                        child.destroy()
            
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur déchargement: {e}")

def _load_required_items(self, target_start, target_end, current_start, current_end):
        """Charge les nouveaux éléments nécessaires"""
        try:
            # Déterminer quels éléments charger
            items_to_load = []
            
            if current_start == -1 or current_end == -1:
                # Aucun élément chargé, charger toute la fenêtre cible
                items_to_load = list(range(target_start, target_end))
            else:
                # Éléments à ajouter avant
                if target_start < current_start:
                    items_to_load.extend(range(target_start, current_start))
                
                # Éléments à ajouter après
                if target_end > current_end:
                    items_to_load.extend(range(current_end, target_end))
            
            # Charger les nouveaux éléments
            if items_to_load:
                if get_config('debug_scroll'):
                    print(f"Chargement de {len(items_to_load)} nouveaux éléments")
                
                # Vider complètement le container et recharger dans l'ordre
                for child in self.playlist_container.winfo_children():
                    child.destroy()
                
                # Charger tous les éléments dans la nouvelle fenêtre
                for i in range(target_start, target_end):
                    if i < len(self.main_playlist):
                        filepath = self.main_playlist[i]
                        self._add_main_playlist_item(filepath, song_index=i)
                
                # Remettre en surbrillance la chanson courante si visible
                current_index = getattr(self, 'current_index', 0)
                if target_start <= current_index < target_end:
                    try:
                        children = self.playlist_container.winfo_children()
                        relative_index = current_index - target_start
                        if 0 <= relative_index < len(children):
                            self.select_playlist_item(children[relative_index], auto_scroll=False)
                    except:
                        pass
            
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur chargement: {e}")


def _check_infinite_scroll(self, event):
        """Vérifie si on doit charger plus d'éléments en haut ou en bas"""
        try:
            print("_check_infinite_scroll appelé")
            # Optimisation: Éviter les appels trop fréquents
            if hasattr(self, '_last_infinite_check_time'):
                current_time = time.time()
                if current_time - self._last_infinite_check_time < 0.1:  # 100ms entre les vérifications
                    return
                self._last_infinite_check_time = current_time
            else:
                self._last_infinite_check_time = time.time()
            
            if not (hasattr(self, 'playlist_canvas') and self.playlist_canvas.winfo_exists()):
                return
            
            # Vérifier si on doit utiliser le chargement dynamique
            if get_config('enable_dynamic_scroll'):
                # Appeler la fonction de chargement dynamique
                self._on_dynamic_scroll(event)
            
            # # Vérifier si on doit utiliser le scroll infini
            # if not (get_config('enable_infinite_scroll')):
            #     return
            
            # # Obtenir la position actuelle du scroll
            # try:
            #     scroll_top, scroll_bottom = self.playlist_canvas.yview()
            # except Exception:
            #     return
            
            # threshold = get_main_playlist_config('scroll_threshold') if USE_NEW_CONFIG else 0.1
            
            # # Vérifier si on est proche du haut (charger des éléments précédents)
            # if scroll_top <= threshold:
            #     self._load_more_songs_above()
            
            # # Vérifier si on est proche du bas (charger des éléments suivants)
            # elif scroll_bottom >= (1.0 - threshold):
            #     self._load_more_songs_below()
                
        except Exception as e:
            if get_config('debug_scroll'):
                print(f"Erreur lors de la vérification du scroll infini: {e}")

def _load_more_songs_above(self):
        """Charge plus de musiques au-dessus de la fenêtre actuelle"""
        try:
            # Protection contre les chargements en boucle
            if getattr(self, '_loading_up_in_progress', False):
                if get_config('debug_scroll'):
                    print("⚠️ Chargement vers le haut déjà en cours, ignoré")
                return
            
            if not hasattr(self, '_last_window_start'):
                return
            
            current_start = _last_window_start
            if current_start <= 0:
                return  # Déjà au début
            
            # Marquer le chargement vers le haut en cours
            self._loading_up_in_progress = True
            if get_config('debug_scroll'):
                print("🔒 Verrouillage scroll vers le haut activé")
            
            load_count = get_main_playlist_config('load_more_count') if USE_NEW_CONFIG else 10
            new_start = max(0, current_start - load_count)
            
            if get_config('debug_scroll'):
                print(f"Chargement de {load_count} musiques au-dessus (index {new_start} à {current_start})")
            
            # Étendre la fenêtre vers le haut
            self._extend_window_up(new_start)
            
            # Réinitialiser le verrou après un délai
            def reset_loading_up_flag():
                self._loading_up_in_progress = False
                if get_config('debug_scroll'):
                    print("🔓 Verrouillage scroll vers le haut désactivé")
            
            # Délai pour éviter les chargements répétés
            self.root.after(MAIN_PLAYLIST_REST_TIMER_AFTER_LOADING, reset_loading_up_flag)
            
            # def reset_main_playlist_is_loading_more_items():
            #     self.main_playlist_is_loading_more_items = False
            # self.root.after(MAIN_PLAYLIST_REST_TIMER_AFTER_LOADING, reset_main_playlist_is_loading_more_items)
            
        except Exception as e:
            print(f"Erreur lors du chargement des musiques au-dessus: {e}")

# Ancienne fonction supprimée - remplacée par la classe DownloadsProgressiveLoader

def _extend_window_up(self, new_start):
        """Étend la fenêtre d'affichage vers le haut"""
        try:
            if not hasattr(self, '_last_window_start') or not hasattr(self, '_last_window_end'):
                return
            
            current_start = _last_window_start
            current_end = _last_window_end
            
            # Ajouter les nouveaux éléments au début dans l'ordre croissant
            # pour maintenir l'ordre chronologique correct
            items_added = 0
            for i in range(new_start, current_start):
                if i < len(self.main_playlist):
                    items_added +=1
                    filepath = self.main_playlist[i]
                    self._add_main_playlist_item_at_position(filepath, song_index=i, position='top')
                    if get_config('debug_scroll'):
                        print(f"  → Ajout élément {i} au début")
            
            # Mettre à jour les paramètres de fenêtre
            _last_window_start = new_start
            
            # Réorganiser tous les éléments dans l'ordre correct
            self._reorder_playlist_items()
            
            # Mettre à jour la région de scroll
            self._update_canvas_scroll_region()
            
            # Ajuster légèrement le scroll pour éviter les rechargements immédiats
            # (approche simple comme pour le scroll vers le bas)
            # items_added = current_start - new_start
            # self._simple_scroll_adjustment_after_top_load(items_added)
            
            self._adjust_scroll_after_top_load(items_added)
            
        except Exception as e:
            print(f"Erreur lors de l'extension vers le haut: {e}")

# Ancienne fonction supprimée - remplacée par la classe DownloadsProgressiveLoader

def _check_and_unload_items(self, current_index):
    """Décharge intelligemment selon les critères :
    - Décharge toutes les musiques avant la musique actuelle
    - SAUF si l'utilisateur regarde au-dessus, alors on garde quelques musiques au-dessus
    """
    try:
        if not (get_config('enable_smart_unloading')):
            return
            
        print(f"DEBUG: _check_and_unload_items appelé pour index {current_index}")
            
        # Obtenir les widgets actuellement chargés
        children = self.playlist_container.winfo_children()
        if not children:
            return
            
        # Déterminer si l'utilisateur regarde au-dessus de la musique actuelle
        user_looking_above = self._is_user_looking_above_current(current_index)
        
        # Collecter les widgets à décharger
        widgets_to_unload = []
        
        for widget in children:
            if hasattr(widget, 'song_index'):
                widget_index = widget.song_index
                
                if widget_index < current_index:
                    # Musique avant la musique actuelle
                    if user_looking_above:
                        # L'utilisateur regarde au-dessus, garder quelques musiques au-dessus
                        keep_above = 0  # Garder 3 musiques au-dessus
                        if widget_index < current_index - keep_above:
                            widgets_to_unload.append(widget)
                            print(f"DEBUG: Déchargement de l'élément {widget_index} (trop loin au-dessus)")
                    else:
                        # L'utilisateur ne regarde pas au-dessus, décharger toutes les musiques avant
                        keep_above = 0  # Garder 0 musiques au-dessus
                        if widget_index < current_index - keep_above:
                            widgets_to_unload.append(widget)
                            print(f"DEBUG: Déchargement de l'élément {widget_index} (avant la musique actuelle)")
        
        # Décharger les widgets sélectionnés
        if widgets_to_unload:
            unload_count = len(widgets_to_unload) + keep_above
            print(f"DEBUG: Déchargement de {unload_count} éléments (utilisateur regarde au-dessus: {user_looking_above})")
            
            # Sauvegarder la position de scroll actuelle avant déchargement
            try:
                scroll_top, scroll_bottom = self.playlist_canvas.yview()
                current_scroll_position = scroll_top
                print(f"DEBUG: Position scroll avant déchargement: {current_scroll_position}")
            except:
                current_scroll_position = 0.0
            
            # Calculer le nombre d'éléments déchargés du haut
            items_unloaded_from_top = 0
            min_unloaded_index = float('inf')
            max_unloaded_index = -1
            
            for widget in widgets_to_unload:
                if hasattr(widget, 'song_index'):
                    widget_index = widget.song_index
                    min_unloaded_index = min(min_unloaded_index, widget_index)
                    max_unloaded_index = max(max_unloaded_index, widget_index)
                    
            # Décharger les widgets
            for widget in widgets_to_unload:
                if widget.winfo_exists():
                    widget.destroy()
            
            # Mettre à jour les variables de fenêtrage si nécessaire
            if hasattr(self, '_last_window_start') and min_unloaded_index != float('inf'):
                # Ajuster le début de la fenêtre si on a déchargé des éléments du début
                if min_unloaded_index <= _last_window_start:
                    new_start = max_unloaded_index + 1
                    print(f"DEBUG: Ajustement _last_window_start: {_last_window_start} → {new_start}")
                    _last_window_start = new_start
            
            # Invalider le cache des index chargés
            try:
                self._invalidate_loaded_indexes_cache()
            except Exception as e:
                print(f"DEBUG: Erreur invalidation cache: {e}")
                self._loaded_indexes_cache = set()
            
            # Ajuster la position du scroll après déchargement
            self._adjust_scroll_after_unload(unload_count, current_scroll_position)
            
        else:
            print(f"DEBUG: Aucun élément à décharger")
            
            
    except Exception as e:
        print(f"DEBUG: Erreur déchargement intelligent: {e}")
        import traceback
        traceback.print_exc()

def _adjust_scroll_after_unload(self, unload_count, previous_scroll_position):
    """Ajuste la position du scroll après déchargement d'éléments"""
    try:
        if not hasattr(self, 'playlist_canvas') or not self.playlist_canvas.winfo_exists():
            return
            
        print(f"DEBUG: Ajustement scroll après déchargement de {unload_count} éléments")
        
        # Mettre à jour la région de scroll d'abord
        # self._update_canvas_scroll_region()
        
        # Attendre que la mise à jour soit effective
        self.playlist_container.update_idletasks()
        
        # Calculer la nouvelle position de scroll
        # Quand on supprime des éléments du haut, il faut remonter le scroll proportionnellement
        children = self.playlist_container.winfo_children()
        current_children_count = len(children)
        
        if current_children_count > 0:
            # Estimer la hauteur d'un élément
            item_height = get_main_playlist_config('item_height_estimate') if USE_NEW_CONFIG else 60
            
            # Calculer le décalage causé par la suppression des éléments
            # Si on a supprimé N éléments du haut, il faut remonter le scroll de N * hauteur_élément
            total_height_removed = unload_count * item_height
            
            # Obtenir la hauteur totale actuelle de la région de scroll
            try:
                scroll_region = self.playlist_canvas.cget('scrollregion')
                if scroll_region:
                    # Format: "x1 y1 x2 y2"
                    parts = scroll_region.split()
                    if len(parts) >= 4:
                        total_height = float(parts[3])
                        
                        # Calculer le pourcentage de décalage
                        if total_height > 0:
                            scroll_offset_ratio = total_height_removed / total_height
                            
                            # Ajuster la position de scroll
                            new_scroll_position = max(0.0, previous_scroll_position - scroll_offset_ratio)
                            
                            print(f"DEBUG: Ajustement scroll - Hauteur supprimée: {total_height_removed}px, "
                                  f"Hauteur totale: {total_height}px, "
                                  f"Position: {previous_scroll_position} → {new_scroll_position}")
                            
                            # Appliquer la nouvelle position
                            self.playlist_canvas.yview_moveto(new_scroll_position)
                            
                        else:
                            print("DEBUG: Hauteur totale nulle, pas d'ajustement")
                    else:
                        print("DEBUG: Format scrollregion invalide")
                else:
                    print("DEBUG: Pas de scrollregion définie")
                    
            except Exception as e:
                print(f"DEBUG: Erreur calcul ajustement scroll: {e}")
                # Fallback: essayer de maintenir une position relative
                try:
                    self.playlist_canvas.yview_moveto(max(0.0, previous_scroll_position * 0.9))
                except:
                    pass
        else:
            print("DEBUG: Aucun enfant restant, scroll en haut")
            self.playlist_canvas.yview_moveto(0.0)
            
    except Exception as e:
        print(f"DEBUG: Erreur ajustement scroll après déchargement: {e}")

def _adjust_scroll_after_top_load(self, items_added):
    """Ajuste la position du scroll après chargement d'éléments au début"""
    try:
        if not hasattr(self, 'playlist_canvas') or not self.playlist_canvas.winfo_exists():
            return
            
        if items_added <= 0:
            return
            
        print(f"DEBUG: Ajustement scroll après chargement de {items_added} éléments au début")
        
        # Mettre à jour la région de scroll d'abord
        # self._update_canvas_scroll_region()
        
        # Attendre que la mise à jour soit effective
        self.playlist_container.update_idletasks()
        
        # Calculer la nouvelle position de scroll
        # Quand on supprime des éléments du haut, il faut remonter le scroll proportionnellement
        children = self.playlist_container.winfo_children()
        current_children_count = len(children)
        
        # Obtenir la position de scroll actuelle
        try:
            scroll_top, scroll_bottom = self.playlist_canvas.yview()
            current_scroll_position = scroll_top
            
            print(f"DEBUG: Position scroll avant ajustement: {current_scroll_position}")
            
            # Mettre à jour la région de scroll d'abord
            # self._update_canvas_scroll_region()
            
            # # Attendre que la mise à jour soit effective
            # self.playlist_container.update_idletasks()
            
            # Calculer le décalage nécessaire
            # Estimer la hauteur d'un élément
            item_height = get_main_playlist_config('item_height_estimate') if USE_NEW_CONFIG else 60
            
            # Calculer la hauteur totale ajoutée
            total_height_added = items_added * item_height
            
            # Obtenir la hauteur totale actuelle de la région de scroll
            scroll_region = self.playlist_canvas.cget('scrollregion')
            if scroll_region:
                # Format: "x1 y1 x2 y2"
                parts = scroll_region.split()
                if len(parts) >= 4:
                    total_height = float(parts[3])
                    
                    if total_height > 0:
                        # Calculer le pourcentage de décalage
                        scroll_offset_ratio = total_height_added / total_height
                        
                        print(f"DEBUG: Décalage nécessaire: {scroll_offset_ratio}")
                        
                        # Ajuster la position de scroll vers le bas
                        new_scroll_position = min(1.0, current_scroll_position + scroll_offset_ratio)
                        
                        print(f"DEBUG: Ajustement scroll - Hauteur ajoutée: {total_height_added}px, "
                              f"Hauteur totale: {total_height}px, "
                              f"Position: {current_scroll_position} → {new_scroll_position}")
                        
                        # Appliquer la nouvelle position avec un petit délai pour s'assurer que tout est mis à jour
                        # def apply_scroll_adjustment():
                        #     try:
                        #         self.playlist_canvas.yview_moveto(new_scroll_position)
                        #         print(f"DEBUG: Scroll ajusté à {new_scroll_position}")
                        #     except Exception as e:
                        #         print(f"DEBUG: Erreur application scroll: {e}")
                        
                        # # Appliquer l'ajustement après un court délai
                        # self.root.after(10, apply_scroll_adjustment)
                        self.playlist_canvas.yview_moveto(new_scroll_position)
                        
                    else:
                        print("DEBUG: Hauteur totale nulle, pas d'ajustement")
                else:
                    print("DEBUG: Format scrollregion invalide")
            else:
                print("DEBUG: Pas de scrollregion définie")
                
        except Exception as e:
            print(f"DEBUG: Erreur calcul ajustement scroll après chargement haut: {e}")
            
    except Exception as e:
        print(f"DEBUG: Erreur ajustement scroll après chargement haut: {e}")

def _simple_scroll_adjustment_after_top_load(self, items_added):
    """Ajustement simple du scroll après chargement vers le haut (comme pour le bas)"""
    try:
        if not hasattr(self, 'playlist_canvas') or not self.playlist_canvas.winfo_exists():
            return
            
        if items_added <= 0:
            return
            
        # Obtenir la position actuelle
        scroll_top, scroll_bottom = self.playlist_canvas.yview()
        
        # Obtenir le seuil de déclenchement
        threshold = get_main_playlist_config('scroll_threshold') if USE_NEW_CONFIG else 0.1
        
        if get_config('debug_scroll'):
            print(f"DEBUG: Ajustement simple - Position actuelle: {scroll_top:.4f}, Seuil: {threshold}")
        
        # Si on est encore dans la zone de déclenchement, faire un petit ajustement
        if scroll_top <= threshold:
            # Ajustement minimal pour sortir de la zone de déclenchement
            # Juste assez pour éviter un rechargement immédiat
            new_position = threshold + 0.02  # Un peu au-dessus du seuil
            
            if get_config('debug_scroll'):
                print(f"DEBUG: Ajustement minimal: {scroll_top:.4f} → {new_position:.4f}")
            
            # Appliquer l'ajustement avec un délai
            def apply_minimal_adjustment():
                try:
                    self.playlist_canvas.yview_moveto(new_position)
                    if get_config('debug_scroll'):
                        print(f"DEBUG: Scroll ajusté minimalement à {new_position:.4f}")
                except Exception as e:
                    print(f"DEBUG: Erreur ajustement minimal: {e}")
            
            self.root.after(50, apply_minimal_adjustment)
        else:
            if get_config('debug_scroll'):
                print(f"DEBUG: Pas d'ajustement nécessaire (position {scroll_top:.4f} > seuil {threshold})")
            
    except Exception as e:
        print(f"DEBUG: Erreur ajustement simple scroll: {e}")

def _is_user_looking_above_current(self, current_index):
    """Détermine si l'utilisateur regarde au-dessus de la musique actuelle"""
    try:
        # Obtenir la position de scroll actuelle
        scroll_top, scroll_bottom = self.playlist_canvas.yview()
        
        # Estimer l'index du premier élément visible
        total_items = len(self.main_playlist)
        if total_items == 0:
            return False
            
        visible_start_index = int(scroll_top * total_items)
        visible_end_index = int(scroll_bottom * total_items)
        
        # L'utilisateur regarde au-dessus si la zone visible est principalement au-dessus de la musique actuelle
        if visible_end_index < current_index:
            print(f"DEBUG: Utilisateur regarde au-dessus (visible: {visible_start_index}-{visible_end_index}, actuel: {current_index})")
            return True
        elif visible_start_index < current_index and visible_end_index >= current_index:
            # La musique actuelle est partiellement visible, vérifier si l'utilisateur regarde plutôt vers le haut
            middle_visible = (visible_start_index + visible_end_index) / 2
            if middle_visible < current_index:
                print(f"DEBUG: Utilisateur regarde plutôt au-dessus (milieu visible: {middle_visible:.1f}, actuel: {current_index})")
                return True
        
        print(f"DEBUG: Utilisateur ne regarde pas au-dessus (visible: {visible_start_index}-{visible_end_index}, actuel: {current_index})")
        return False
        
    except Exception as e:
        print(f"DEBUG: Erreur détection regard utilisateur: {e}")
        return False

def _add_main_playlist_item_at_position(self, filepath, song_index=None, position='bottom'):
        """Ajoute un élément de playlist à une position spécifique (top ou bottom)"""
        try:
            if position == 'bottom':
                # Pour le bas, utiliser la fonction normale
                return self._add_main_playlist_item(filepath, song_index=song_index)
            
            elif position == 'top':
                # Pour le haut, simplement créer l'élément
                # L'ordre sera corrigé par _reorder_playlist_items() après
                item_frame = self._add_main_playlist_item(filepath, song_index=song_index)
                
                if get_config('debug_scroll'):
                    print(f"  → Élément {song_index} ajouté (ordre sera corrigé)")
                
                return item_frame
            
        except Exception as e:
            print(f"Erreur lors de l'ajout d'élément à la position {position}: {e}")
            return None

def _reorder_playlist_items(self):
        """Réorganise tous les éléments de la playlist dans l'ordre correct basé sur song_index"""
        try:
            if not hasattr(self, 'playlist_container') or not self.playlist_container.winfo_exists():
                return
            
            # Récupérer tous les enfants avec leur song_index
            children = list(self.playlist_container.winfo_children())
            indexed_children = []
            
            for child in children:
                if hasattr(child, 'song_index'):
                    indexed_children.append((child.song_index, child))
                else:
                    # Enfant sans index, le garder à la fin
                    indexed_children.append((float('inf'), child))
            
            # Trier par song_index
            indexed_children.sort(key=lambda x: x[0])
            
            if get_config('debug_scroll'):
                order_before = [child.song_index if hasattr(child, 'song_index') else '?' for child in children]
                order_after = [x[0] if x[0] != float('inf') else '?' for x in indexed_children]
                print(f"  → Réorganisation: {order_before} → {order_after}")
            
            # Réorganiser les widgets
            for i, (song_index, child) in enumerate(indexed_children):
                # Déplacer chaque widget à sa position correcte
                child.pack_forget()
                if i == 0:
                    # Premier élément
                    child.pack(fill='x', pady=2, padx=5)
                else:
                    # Insérer après l'élément précédent
                    prev_child = indexed_children[i-1][1]
                    child.pack(fill='x', pady=2, padx=5, after=prev_child)
            
        except Exception as e:
            print(f"Erreur lors de la réorganisation des éléments: {e}")

def _create_playlist_item_frame(self, filepath, song_index=None):
        """Crée un frame pour un élément de playlist"""
        try:
            # Utiliser la fonction existante qui maintenant retourne le frame
            frame = self._add_main_playlist_item(filepath, song_index=song_index)
            return frame
            
        except Exception as e:
            print(f"Erreur lors de la création du frame: {e}")
            return None

def _invalidate_loaded_indexes_cache(self):
    """Invalide le cache des index chargés"""
    if hasattr(self, '_loaded_indexes_cache'):
        print(f"DEBUG: Invalidation du cache des index chargés")
        self._loaded_indexes_cache = None

def _setup_dynamic_scroll(self):
    """Configure le système de scroll dynamique unifié (combine infinite et progressive)"""
    try:
        if not hasattr(self, 'playlist_canvas'):
            return
        
        # Vérifier si le système est activé
        if not (get_config('enable_dynamic_scroll')):
            return
        
        # Initialiser les variables de state pour le scroll intelligent
        _user_is_scrolling = False
        _user_scroll_timer = None
        _last_current_index = getattr(self, 'current_index', 0)
        _auto_centering = False  # Flag pour éviter les boucles
        
        # Variables pour le chargement progressif
        _last_scroll_position = 0.0
        _progressive_loading_active = True
        
        # Initialiser les variables de fenêtrage pour la compatibilité
        if not hasattr(self, '_last_window_start'):
            self._last_window_start = 0
        if not hasattr(self, '_last_window_end'):
            # Initialiser avec une fenêtre basée sur la position courante
            current_index = getattr(self, 'current_index', 0)
            initial_load = get_main_playlist_config('initial_load_after_current')
            self._last_window_end = min(len(self.main_playlist) if hasattr(self, 'main_playlist') else 0, 
                                        current_index + initial_load)
        
        # Binding pour détecter les changements de position de scroll
        # def on_dynamic_scroll_change(*args):
        #     """Appelée quand la position de scroll change"""
        #     try:
        #         # Gérer le scroll infini (mise à jour de l'affichage)
        #         self._update_display_based_on_scroll_position()
                
        #         # Gérer le chargement progressif
        #         self._on_dynamic_scroll()
                
        #     except Exception as e:
        #         if get_config('debug_scroll'):
        #             print(f"❌ Erreur scroll dynamique: {e}")
        
        # # Connecter le callback à la scrollbar
        # if hasattr(self, 'playlist_scrollbar') and self.playlist_scrollbar:
        #     self.playlist_scrollbar.config(command=lambda *args: [
        #         self.playlist_canvas.yview(*args),
        #         on_dynamic_scroll_change()
        #     ])
        
        if get_config('debug_scroll'):
            print("✅ Système de scroll dynamique configuré")
            
    except Exception as e:
        if get_config('debug_scroll'):
            print(f"❌ Erreur configuration scroll dynamique: {e}")