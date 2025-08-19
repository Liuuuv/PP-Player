from __init__ import *


def show_output_menu(self):
    """Affiche un menu déroulant pour choisir le périphérique de sortie audio"""
    try:
        # Obtenir la liste des périphériques audio
        import pygame._sdl2.audio
        devices = pygame._sdl2.audio.get_audio_device_names()
        
        if not devices:
            messagebox.showinfo("Périphériques audio", "Aucun périphérique audio trouvé")
            return
        
        # Créer le menu déroulant
        output_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                                activebackground='#4a8fe7', activeforeground='white',
                                relief='flat', bd=1)
        
        # Ajouter un titre
        output_menu.add_command(label="Périphériques de sortie", state='disabled')
        output_menu.add_separator()
        
        # Variable partagée pour les radiobuttons
        if not hasattr(self, 'audio_device_var'):
            self.audio_device_var = tk.StringVar(value=self.current_audio_device or "")
        else:
            self.audio_device_var.set(self.current_audio_device or "")
        
        # Ajouter chaque périphérique comme radiobutton
        for device in devices:
            device_name = device.decode('utf-8') if isinstance(device, bytes) else device
            
            output_menu.add_radiobutton(
                label=device_name,
                variable=self.audio_device_var,
                value=device_name,
                command=lambda d=device, name=device_name: self.change_output_device(d, name)
            )
        
        # Afficher le menu à la position du bouton
        try:
            x = self.output_button.winfo_rootx()
            y = self.output_button.winfo_rooty() + self.output_button.winfo_height()
            output_menu.post(x, y)
        except:
            # Si erreur de positionnement, afficher au curseur
            output_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'accéder aux périphériques audio:\n{str(e)}")

def show_stats_menu(self):
    """Affiche un menu avec les statistiques d'écoute"""
    try:
        # Calculer les statistiques actuelles
        self._update_current_song_stats()
        
        # Formater le temps total d'écoute
        total_time = self.stats['total_listening_time']
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        
        if hours > 0:
            time_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            time_str = f"{minutes}m {seconds}s"
        else:
            time_str = f"{seconds}s"
        
        # Créer le menu déroulant
        stats_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                            activebackground='#4a8fe7', activeforeground='white',
                            relief='flat', bd=1)
        
        # Ajouter un titre
        stats_menu.add_command(label="📊 Statistiques d'écoute", state='disabled')
        stats_menu.add_separator()
        
        # Ajouter les statistiques
        stats_menu.add_command(label=f"🎵 Musiques lues: {self.stats['songs_played']}", state='disabled')
        stats_menu.add_command(label=f"⏱️ Temps d'écoute: {time_str}", state='disabled')
        stats_menu.add_command(label=f"🔍 Recherches: {self.stats['searches_count']}", state='disabled')
        
        stats_menu.add_separator()
        stats_menu.add_command(label="🗑️ Réinitialiser", command=self._reset_stats)
        
        # Afficher le menu à la position du bouton
        try:
            x = self.stats_button.winfo_rootx()
            y = self.stats_button.winfo_rooty() + self.stats_button.winfo_height()
            stats_menu.post(x, y)
        except:
            # Si erreur de positionnement, afficher au curseur
            stats_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'afficher les statistiques:\n{str(e)}")

def show_cache_menu(self):
    """Affiche un menu déroulant pour gérer les caches"""
    try:
        # Importer les fonctions de calcul de taille
        from cache_cleaner import (
            _get_cache_size_str, _get_search_cache_size, _get_artist_cache_size,
            _get_thumbnail_cache_size, _get_playlist_content_cache_size,
            _get_duration_cache_size, _get_total_cache_size
        )
        
        # Calculer les tailles des caches
        search_size = _get_cache_size_str(_get_search_cache_size(self))
        artist_size = _get_cache_size_str(_get_artist_cache_size(self))
        thumbnail_size = _get_cache_size_str(_get_thumbnail_cache_size(self))
        playlist_size = _get_cache_size_str(_get_playlist_content_cache_size(self))
        duration_size = _get_cache_size_str(_get_duration_cache_size(self))
        total_size = _get_cache_size_str(_get_total_cache_size(self))
        
        # Créer le menu déroulant
        cache_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                            activebackground='#4a8fe7', activeforeground='white',
                            relief='flat', bd=1)
        
        # Ajouter un titre avec la taille totale
        cache_menu.add_command(label=f"🗂️ Gestion du cache ({total_size})", state='disabled')
        cache_menu.add_separator()
        
        # Options de nettoyage du cache avec tailles
        cache_menu.add_command(
            label=f"🔍 Vider le cache des recherches ({search_size})",
            command=self._clear_search_cache
        )
        
        cache_menu.add_command(
            label=f"🎤 Vider le cache des artistes ({artist_size})",
            command=self._clear_artist_cache
        )
        
        cache_menu.add_command(
            label=f"🖼️ Vider le cache des miniatures ({thumbnail_size})",
            command=self._clear_thumbnail_cache
        )
        
        cache_menu.add_command(
            label=f"📋 Vider le cache des playlists ({playlist_size})",
            command=self._clear_playlist_content_cache
        )
        
        cache_menu.add_command(
            label=f"⏱️ Vider le cache des durées ({duration_size})",
            command=self._clear_duration_cache
        )
        
        cache_menu.add_separator()
        
        cache_menu.add_command(
            label=f"🗑️ Vider tous les caches ({total_size})",
            command=self._clear_all_caches
        )
        
        # Afficher le menu à la position du bouton
        try:
            x = self.clear_cache_button.winfo_rootx()
            y = self.clear_cache_button.winfo_rooty() + self.clear_cache_button.winfo_height()
            cache_menu.post(x, y)
        except:
            # Si erreur de positionnement, afficher au curseur
            cache_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'afficher le menu de cache:\n{str(e)}")

def show_unified_context_menu(self, item, event=None, item_type="file"):
    """Affiche le même menu contextuel pour fichiers locaux et vidéos YouTube"""
    if item_type == "youtube":
        # Pour les vidéos YouTube, on utilise le même menu mais on stocke les infos YouTube
        # pour pouvoir télécharger si nécessaire
        self._current_youtube_item = item
        
        # Créer un filepath fictif basé sur le titre pour le menu
        title = item.get('title', 'Vidéo YouTube')
        # Nettoyer le titre pour créer un nom de fichier valide
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        fake_filepath = os.path.join("downloads", f"{safe_title}.mp3")
        
        # Appeler le menu des fichiers avec le filepath fictif
        self._show_file_context_menu_with_youtube_support(fake_filepath, event, item)
    else:
        # Pour les fichiers locaux, utiliser le menu normal
        self._current_youtube_item = None
        self._show_original_file_context_menu(item, event)

def _show_file_context_menu_with_youtube_support(self, filepath, event, youtube_item):
    """Version du menu fichier qui supporte les vidéos YouTube"""
    # Créer un menu contextuel identique à celui des fichiers
    menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
                  activebackground='#4a8fe7', activeforeground='white')
    
    # Titre avec le nom du fichier (tronqué)
    filename = os.path.basename(filepath)
    if len(filename) > 30:
        filename = filename[:27] + "..."
    menu.add_command(label=f"📁 {filename}", state='disabled')
    menu.add_separator()
    
    # Ajouter les playlists existantes
    for playlist_name in self.playlists.keys():
        menu.add_command(
            label=f"➕ Ajouter à '{playlist_name}'",
            command=lambda name=playlist_name: self._add_to_specific_playlist_with_youtube_support(filepath, name, youtube_item)
        )
    
    menu.add_separator()
    
    # Option pour créer une nouvelle playlist
    menu.add_command(
        label="📝 Créer nouvelle playlist...",
        command=lambda: self._create_new_playlist_dialog_with_youtube_support(filepath, youtube_item)
    )
    
    menu.add_separator()
    
    # Options de fichier
    menu.add_command(
        label="📂 Ouvrir le dossier",
        command=lambda: self._open_file_location_with_youtube_support(filepath, youtube_item)
    )
    
    menu.add_command(
        label="🔗 Ouvrir sur YouTube",
        command=lambda: self._open_on_youtube_with_youtube_support(filepath, youtube_item)
    )
    
    menu.add_separator()
    
    # Option de suppression/téléchargement
    if youtube_item:
        menu.add_command(
            label="⬇️ Télécharger maintenant",
            command=lambda: self._download_youtube_video(youtube_item),
            foreground='#44ff44'
        )
    else:
        menu.add_command(
            label="🗑️ Supprimer définitivement",
            command=lambda: self._delete_file_permanently(filepath),
            foreground='#ff4444'
        )
    
    # Afficher le menu à la position de la souris ou de l'événement
    try:
        if event:
            menu.post(event.x_root, event.y_root)
        else:
            menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    except:
        # Fallback
        menu.post(100, 100)

def _show_original_file_context_menu(self, filepath, event=None):
    """Menu contextuel original pour les fichiers locaux"""
    # Créer un menu contextuel
    menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
                  activebackground='#4a8fe7', activeforeground='white')
    
    # Titre avec le nom du fichier (tronqué)
    filename = os.path.basename(filepath)
    if len(filename) > 30:
        filename = filename[:27] + "..."
    menu.add_command(label=f"📁 {filename}", state='disabled')
    menu.add_separator()
    
    # Ajouter les playlists existantes
    for playlist_name in self.playlists.keys():
        menu.add_command(
            label=f"➕ Ajouter à '{playlist_name}'",
            command=lambda name=playlist_name: self._add_to_specific_playlist(filepath, name)
        )
    
    menu.add_separator()
    
    # Option pour créer une nouvelle playlist
    menu.add_command(
        label="📝 Créer nouvelle playlist...",
        command=lambda: self._create_new_playlist_dialog(filepath)
    )
    
    menu.add_separator()
    
    # Options de fichier
    menu.add_command(
        label="📂 Ouvrir le dossier",
        command=lambda: self._open_file_location(filepath)
    )
    
    menu.add_command(
        label="🔗 Ouvrir sur YouTube",
        command=lambda: self._open_on_youtube(filepath)
    )
    
    menu.add_separator()
    
    # Option de suppression (en rouge)
    menu.add_command(
        label="🗑️ Supprimer définitivement",
        command=lambda: self._delete_file_permanently(filepath),
        foreground='#ff4444'
    )
    
    # Afficher le menu à la position de la souris ou de l'événement
    try:
        if event:
            menu.post(event.x_root, event.y_root)
        else:
            menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    except:
        # Fallback
        menu.post(100, 100)

def _show_youtube_playlist_menu(self, video, frame):
    """Affiche un menu déroulant pour choisir la playlist pour une vidéo YouTube (ancienne version)"""
    # Rediriger vers le menu unifié
    self.show_unified_context_menu(video, item_type="youtube")

def show_file_context_menu(self, filepath, event=None):
    """Affiche un menu contextuel pour un fichier avec options de playlist et suppression"""
    # Rediriger vers le menu unifié
    self.show_unified_context_menu(filepath, event, item_type="file")

def _add_youtube_to_playlist_unified(self, video, playlist_name):
    """Ajoute une vidéo YouTube à une playlist (télécharge d'abord si nécessaire)"""
    def add_after_download():
        # Télécharger la vidéo d'abord
        url = video.get('webpage_url', '')
        title = video.get('title', 'Vidéo YouTube')
        
        if url:
            # Marquer pour ajout à la playlist après téléchargement
            if url not in self.pending_playlist_additions:
                self.pending_playlist_additions[url] = []
            self.pending_playlist_additions[url].append(playlist_name)
            
            # Lancer le téléchargement
            self._download_youtube_video(video)
    
    # Exécuter dans un thread pour éviter de bloquer l'UI
    threading.Thread(target=add_after_download, daemon=True).start()

def _create_new_playlist_dialog_youtube_unified(self, video):
    """Crée une nouvelle playlist et y ajoute la vidéo YouTube"""
    def create_and_add():
        # Demander le nom de la playlist
        playlist_name = simpledialog.askstring(
            "Nouvelle playlist",
            "Nom de la nouvelle playlist:",
            parent=self.root
        )
        
        if playlist_name and playlist_name.strip():
            playlist_name = playlist_name.strip()
            
            # Créer la playlist si elle n'existe pas
            if playlist_name not in self.playlists:
                self.playlists[playlist_name] = []
                self.save_playlists()
            
            # Ajouter la vidéo à la playlist
            self._add_youtube_to_playlist_unified(video, playlist_name)
    
    create_and_add()

def _download_youtube_video(self, video):
    """Télécharge une vidéo YouTube"""
    url = video.get('webpage_url', '')
    title = video.get('title', 'Vidéo YouTube')
    
    if url:
        # Configurer search_list pour la compatibilité avec _download_youtube_thread
        self.search_list = [video]
        
        # Utiliser la fonction de téléchargement existante
        threading.Thread(
            target=self._download_youtube_thread,
            args=(url, True),  # url et add_to_playlist
            daemon=True
        ).start()

def _open_youtube_url(self, url):
    """Ouvre une URL YouTube dans le navigateur"""
    if url:
        import webbrowser
        webbrowser.open(url)

def _add_to_specific_playlist_with_youtube_support(self, filepath, playlist_name, youtube_item=None):
    """Ajoute un élément à une playlist spécifique (télécharge d'abord si YouTube)"""
    if youtube_item:
        # C'est une vidéo YouTube, télécharger d'abord
        self._download_and_add_to_playlist(youtube_item, playlist_name)
    else:
        # C'est un fichier local, utiliser la fonction normale
        self._add_to_specific_playlist(filepath, playlist_name)

def _create_new_playlist_dialog_with_youtube_support(self, filepath, youtube_item=None):
    """Crée une nouvelle playlist et y ajoute l'élément (télécharge d'abord si YouTube)"""
    if youtube_item:
        # C'est une vidéo YouTube
        self._create_new_playlist_dialog_youtube_unified(youtube_item)
    else:
        # C'est un fichier local
        self._create_new_playlist_dialog(filepath)

def _open_file_location_with_youtube_support(self, filepath, youtube_item=None):
    """Ouvre le dossier contenant le fichier (downloads pour YouTube)"""
    if youtube_item:
        # Pour YouTube, ouvrir le dossier downloads
        self._open_downloads_folder()
    else:
        # Pour fichier local, ouvrir son dossier
        self._open_file_location(filepath)

def _open_on_youtube_with_youtube_support(self, filepath, youtube_item=None):
    """Ouvre sur YouTube (URL directe pour YouTube, recherche pour fichier local)"""
    if youtube_item:
        # Pour YouTube, utiliser l'URL directe
        url = youtube_item.get('webpage_url', '')
        self._open_youtube_url(url)
    else:
        # Pour fichier local, rechercher sur YouTube
        self._open_on_youtube(filepath)

def _download_and_add_to_playlist(self, youtube_item, playlist_name):
    """Télécharge une vidéo YouTube et l'ajoute à une playlist"""
    url = youtube_item.get('webpage_url', '')
    if url:
        # Marquer pour ajout à la playlist après téléchargement
        if url not in self.pending_playlist_additions:
            self.pending_playlist_additions[url] = []
        self.pending_playlist_additions[url].append(playlist_name)
        
        # Lancer le téléchargement
        self._download_youtube_video(youtube_item)

def _open_downloads_folder(self):
    """Ouvre le dossier downloads"""
    try:
        import subprocess
        import platform
        
        downloads_path = os.path.join(os.getcwd(), "downloads")
        
        if platform.system() == "Windows":
            subprocess.run(['explorer', downloads_path])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', downloads_path])
        else:  # Linux
            subprocess.run(['xdg-open', downloads_path])
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier downloads:\n{str(e)}")

def _open_file_location(self, filepath):
    """Ouvre le dossier contenant le fichier"""
    try:
        import subprocess
        import platform
        
        folder_path = os.path.dirname(filepath)
        
        if platform.system() == "Windows":
            subprocess.run(['explorer', '/select,', filepath])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', '-R', filepath])
        else:  # Linux
            subprocess.run(['xdg-open', folder_path])
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier:\n{str(e)}")

def _open_on_youtube(self, filepath):
    """Ouvre la vidéo sur YouTube en recherchant le titre"""
    try:
        import webbrowser
        
        # Extraire le titre du nom de fichier
        filename = os.path.basename(filepath)
        title = os.path.splitext(filename)[0]
        
        # Nettoyer le titre pour la recherche
        search_query = title.replace("_", " ").replace("-", " ")
        
        # Créer l'URL de recherche YouTube
        youtube_search_url = f"https://www.youtube.com/results?search_query={search_query}"
        
        webbrowser.open(youtube_search_url)
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir YouTube:\n{str(e)}")

def _delete_file_permanently(self, filepath):
    """Supprime définitivement un fichier après confirmation"""
    try:
        filename = os.path.basename(filepath)
        
        # Demander confirmation
        result = messagebox.askyesno(
            "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer définitivement ce fichier ?\n\n{filename}\n\n"
            "Cette action est irréversible et le fichier sera supprimé de toutes les playlists.",
            icon='warning'
        )
        
        if result:
            # Vérifier que le fichier existe
            if not os.path.exists(filepath):
                messagebox.showwarning("Fichier introuvable", "Le fichier n'existe plus sur le disque.")
                # Supprimer quand même des playlists
                self.remove_deleted_file_from_playlists(filepath)
                return
            
            # Supprimer le fichier
            os.remove(filepath)
            
            # Supprimer des playlists et mettre à jour l'affichage
            affected_playlists = self.remove_deleted_file_from_playlists(filepath)
            
            # Message de confirmation
            if affected_playlists:
                self.status_bar.config(text=f"Fichier supprimé de {len(affected_playlists)} playlist(s)")
            else:
                self.status_bar.config(text="Fichier supprimé")
            
            # Recharger l'onglet téléchargées si nécessaire
            if hasattr(self, '_refresh_downloads_library'):
                self._refresh_downloads_library(preserve_scroll=True)
            
            # Effacer le message après 3 secondes
            self.root.after(3000, lambda: self.status_bar.config(text=""))
            
    except PermissionError:
        messagebox.showerror("Erreur", "Permission refusée. Le fichier est peut-être en cours d'utilisation.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de supprimer le fichier:\n{str(e)}")
