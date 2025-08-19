import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier library_tab
from library_tab import *



def show_downloads_content(self):
    """Affiche le contenu de l'onglet téléchargées"""
    
    # S'assurer que les données sont à jour avant l'affichage
    self._refresh_downloads_library()
    
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
    
    # Initialiser la liste de tous les fichiers téléchargés
    self.all_downloaded_files = []
    
    # Charger et afficher les fichiers téléchargés
    self.load_downloaded_files()

def load_downloaded_files(self):
    """Charge et affiche tous les fichiers du dossier downloads"""
    downloads_dir = self.downloads_folder
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
        return
    
    # Initialiser le système de cache
    self._init_cache_system()
    
    # Extensions audio supportées
    audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
    
    # Vider la liste actuelle et le cache
    self.all_downloaded_files = []
    self.normalized_filenames = {}
    
    # Parcourir le dossier downloads et stocker tous les fichiers
    for filename in os.listdir(downloads_dir):
        if filename.lower().endswith(audio_extensions):
            filepath = os.path.join(downloads_dir, filename)
            self.all_downloaded_files.append(filepath)
            
            # Créer le cache du nom normalisé pour accélérer les recherches
            normalized_name = os.path.basename(filepath).lower()
            self.normalized_filenames[filepath] = normalized_name
    
    # Charger les caches de durées et miniatures
    self._load_duration_cache()
    self._load_thumbnail_cache()
    
    # Mettre à jour le nombre de fichiers téléchargés
    self.num_downloaded_files = len(self.all_downloaded_files)
    
    # Afficher tous les fichiers (sans filtre)
    self._display_filtered_downloads(self.all_downloaded_files)
    
    # Mettre à jour le texte du bouton
    self._update_downloads_button()
    
    # Forcer une mise à jour supplémentaire de la scrollbar après un délai
    # pour s'assurer qu'elle est correctement initialisée
    if hasattr(self, 'safe_after'):
        self.safe_after(100, self._update_scrollbar)
    else:
        self.root.after(100, self._update_scrollbar)

def _display_filtered_downloads(self, files_to_display, preserve_scroll=False):
    """Affiche une liste filtrée de fichiers téléchargés"""
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
    if not files_to_display:
        _show_no_results_message(self)
        # Marquer la fin du refresh
        self._refreshing_downloads = False
        return
    
    # Afficher avec chargement différé des miniatures
    for filepath in files_to_display:
        self._add_download_item_fast(filepath)
    
    # Forcer la mise à jour de la scrollbar après l'ajout des éléments
    self._update_scrollbar()
    
    # Lancer le chargement différé des miniatures et durées
    self._start_thumbnail_loading(files_to_display, self.downloads_container)
    
    # Marquer la fin du refresh
    self._refreshing_downloads = False

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
    end_index = min(start_index + batch_size, len(files_to_display))
    
    # Afficher le batch actuel avec chargement rapide
    for i in range(start_index, end_index):
        self._add_download_item_fast(files_to_display[i])
    
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
                        self.update_is_in_queue(widget)
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
    

# ==================== SYSTÈME DE CACHE ====================

def _init_cache_system(self):
    """Initialise le système de cache pour les miniatures et durées"""
    import json
    
    self.cache_dir = os.path.join(self.downloads_folder, ".cache")
    self.thumbnails_cache_dir = os.path.join(self.cache_dir, "thumbnails")
    self.durations_cache_file = os.path.join(self.cache_dir, "durations.json")
    self.metadata_cache_file = os.path.join(self.cache_dir, "metadata.json")
    
    # Créer les dossiers de cache s'ils n'existent pas
    os.makedirs(self.thumbnails_cache_dir, exist_ok=True)
    
    # Initialiser les caches en mémoire
    self.duration_cache = {}
    self.thumbnail_cache = {}
    self.cache_metadata = {}

def _load_duration_cache(self):
    """Charge le cache des durées depuis le disque"""
    import json
    
    try:
        if os.path.exists(self.durations_cache_file):
            with open(self.durations_cache_file, 'r', encoding='utf-8') as f:
                self.duration_cache = json.load(f)
        else:
            self.duration_cache = {}
    except Exception as e:
        print(f"Erreur chargement cache durées: {e}")
        self.duration_cache = {}

def _save_duration_cache(self):
    """Sauvegarde le cache des durées sur le disque"""
    import json
    
    try:
        with open(self.durations_cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.duration_cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur sauvegarde cache durées: {e}")

def _load_thumbnail_cache(self):
    """Charge les métadonnées du cache des miniatures"""
    import json
    
    try:
        if os.path.exists(self.metadata_cache_file):
            with open(self.metadata_cache_file, 'r', encoding='utf-8') as f:
                self.cache_metadata = json.load(f)
        else:
            self.cache_metadata = {}
    except Exception as e:
        print(f"Erreur chargement métadonnées cache: {e}")
        self.cache_metadata = {}

def _save_thumbnail_cache_metadata(self):
    """Sauvegarde les métadonnées du cache des miniatures"""
    import json
    
    try:
        with open(self.metadata_cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache_metadata, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur sauvegarde métadonnées cache: {e}")

def _get_cached_duration(self, filepath):
    """Récupère la durée depuis le cache ou la calcule si nécessaire"""
    try:
        # Vérifier si la durée est en cache et si le fichier n'a pas été modifié
        file_mtime = os.path.getmtime(filepath)
        cache_key = os.path.abspath(filepath)
        
        if (cache_key in self.duration_cache and 
            'mtime' in self.duration_cache[cache_key] and
            self.duration_cache[cache_key]['mtime'] == file_mtime):
            return self.duration_cache[cache_key]['duration']
        
        # Calculer la durée
        duration = self._calculate_audio_duration(filepath)
        
        # Mettre en cache
        self.duration_cache[cache_key] = {
            'duration': duration,
            'mtime': file_mtime
        }
        
        # Sauvegarder le cache (de manière asynchrone pour ne pas bloquer)
        if hasattr(self, 'safe_after'):
            self.safe_after(1, self._save_duration_cache)
        else:
            self.root.after_idle(self._save_duration_cache)
        
        return duration
        
    except Exception as e:
        print(f"Erreur cache durée pour {filepath}: {e}")
        return "??:??"

def _calculate_audio_duration(self, filepath):
    """Calcule la durée réelle d'un fichier audio"""
    try:
        if filepath.lower().endswith('.mp3'):
            audio = MP3(filepath)
            duration = audio.info.length
        else:
            # Pour les autres formats, utiliser pydub
            audio = AudioSegment.from_file(filepath)
            duration = len(audio) / 1000.0  # pydub donne en millisecondes
        
        return time.strftime('%M:%S', time.gmtime(duration))
    except:
        return "??:??"

def _get_cached_thumbnail_path(self, filepath):
    """Retourne le chemin de la miniature en cache"""
    filename = os.path.basename(filepath)
    cache_filename = f"{filename}.thumb.png"
    return os.path.join(self.thumbnails_cache_dir, cache_filename)

def _is_thumbnail_cache_valid(self, filepath, cache_path):
    """Vérifie si la miniature en cache est encore valide"""
    try:
        if not os.path.exists(cache_path):
            return False
        
        # Vérifier la date de modification du fichier source
        source_mtime = os.path.getmtime(filepath)
        cache_mtime = os.path.getmtime(cache_path)
        
        # Vérifier aussi les fichiers d'image associés (thumbnails YouTube)
        base_path = os.path.splitext(filepath)[0]
        for ext in ['.jpg', '.png', '.webp']:
            img_path = base_path + ext
            if os.path.exists(img_path):
                img_mtime = os.path.getmtime(img_path)
                if img_mtime > cache_mtime:
                    return False
        
        return cache_mtime >= source_mtime
        
    except Exception as e:
        print(f"Erreur vérification cache miniature: {e}")
        return False

def _create_cached_thumbnail(self, filepath, cache_path):
    """Crée et sauvegarde une miniature en cache"""
    try:
        # Chercher une image associée d'abord
        base_path = os.path.splitext(filepath)[0]
        source_image = None
        
        for ext in ['.jpg', '.png', '.webp']:
            img_path = base_path + ext
            if os.path.exists(img_path):
                source_image = img_path
                break
        
        if source_image:
            # Charger et redimensionner l'image
            img = Image.open(source_image)
            img.thumbnail((80, 45), Image.Resampling.LANCZOS)
            
            # Sauvegarder en cache
            img.save(cache_path, "PNG")
            return True
        else:
            # Créer une miniature par défaut
            default_img = Image.new('RGB', (80, 45), color='#3d3d3d')
            default_img.save(cache_path, "PNG")
            return True
            
    except Exception as e:
        print(f"Erreur création miniature cache: {e}")
        return False

def _load_cached_thumbnail(self, filepath, label):
    """Charge une miniature depuis le cache ou la crée si nécessaire"""
    try:
        cache_path = self._get_cached_thumbnail_path(filepath)
        
        # Vérifier si le cache est valide
        if not self._is_thumbnail_cache_valid(filepath, cache_path):
            # Créer la miniature en cache
            if not self._create_cached_thumbnail(filepath, cache_path):
                # Fallback à l'ancienne méthode
                self._load_download_thumbnail_fallback(filepath, label)
                return
        
        # Charger depuis le cache
        img = Image.open(cache_path)
        photo = ImageTk.PhotoImage(img)
        label.configure(image=photo)
        label.image = photo
        
    except Exception as e:
        print(f"Erreur chargement miniature cache: {e}")
        # Fallback à l'ancienne méthode
        self._load_download_thumbnail_fallback(filepath, label)

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