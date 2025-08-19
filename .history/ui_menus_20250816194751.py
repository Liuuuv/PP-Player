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
    # if item_type == "youtube":
    #     # Pour les vidéos YouTube, on utilise le même menu mais on stocke les infos YouTube
    #     # pour pouvoir télécharger si nécessaire
    #     self._current_youtube_item = item
        
    #     # Créer un filepath fictif basé sur le titre pour le menu
    #     title = item.get('title', 'Vidéo YouTube')
    #     # Nettoyer le titre pour créer un nom de fichier valide
    #     safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    #     fake_filepath = os.path.join("downloads", f"{safe_title}.mp3")
        
    #     # Appeler le menu des fichiers avec le filepath fictif
    #     self._show_result_context_menu(fake_filepath, event, item)
    # else:
    #     # Pour les fichiers locaux, utiliser le menu normal
    #     self._current_youtube_item = None
    #     self._show_original_file_context_menu(item, event)

    self._current_youtube_item = item
    self._show_result_context_menu(item, event)

# def _show_result_context_menu(self, filepath, event, youtube_item):
def _show_result_context_menu(self, item, event):
    """Version du menu fichier qui supporte les vidéos YouTube"""
    # # Créer un menu contextuel identique à celui des fichiers
    # menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
    #               activebackground='#4a8fe7', activeforeground='white')
    
    # # Titre avec le nom du fichier (tronqué)
    # filename = os.path.basename(filepath)
    # if len(filename) > 30:
    #     filename = filename[:27] + "..."
    # menu.add_command(label=f"📁 {filename}", state='disabled')
    # menu.add_separator()
    
    # # Ajouter les playlists existantes
    # for playlist_name in self.playlists.keys():
    #     menu.add_command(
    #         label=f"➕ Ajouter à '{playlist_name}'",
    #         command=lambda name=playlist_name: self._add_to_specific_playlist_with_youtube_support(filepath, name, youtube_item)
    #     )
    
    # menu.add_separator()
    
    # # Option pour créer une nouvelle playlist
    # menu.add_command(
    #     label="📝 Créer nouvelle playlist...",
    #     command=lambda: self._create_new_playlist_dialog_with_youtube_support(filepath, youtube_item)
    # )
    
    # menu.add_separator()
    
    # # Options de fichier
    # menu.add_command(
    #     label="📂 Ouvrir le dossier",
    #     command=lambda: self._open_file_location_with_youtube_support(filepath, youtube_item)
    # )
    
    # menu.add_command(
    #     label="🔗 Ouvrir sur YouTube",
    #     command=lambda: self._open_on_youtube_with_youtube_support(filepath, youtube_item)
    # )
    
    # menu.add_separator()
    
    # # Option de suppression/téléchargement
    # if youtube_item:
    #     menu.add_command(
    #         label="⬇️ Télécharger maintenant",
    #         command=lambda: self._download_youtube_video(youtube_item),
    #         foreground='#44ff44'
    #     )
    # else:
    #     menu.add_command(
    #         label="🗑️ Supprimer définitivement",
    #         command=lambda: self._delete_file_permanently(filepath),
    #         foreground='#ff4444'
    #     )
    
    # # Afficher le menu à la position de la souris ou de l'événement
    # try:
    #     if event:
    #         menu.post(event.x_root, event.y_root)
    #     else:
    #         menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    # except:
    #     # Fallback
    #     menu.post(100, 100)
    
    
    # Créer le menu contextuel
    context_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                            activebackground='#4a8fe7', activeforeground='white',
                            relief='flat', bd=1)
    
    title_text = f"Ajouter à:"
    context_menu.add_command(label=title_text, state='disabled')
    context_menu.add_separator()
        
    # Options pour la queue et la main playlist
    context_menu.add_command(
        label="📄 Ajouter à la liste de lecture",
        command=lambda i=item: self._download_youtube_video(i, add_to_main_playlist=True)
    )
    context_menu.add_command(
        label="⏭️ Lire ensuite",
        command=lambda i=item: self._safe_add_to_queue_first_from_result(i)
    )
    context_menu.add_command(
        label="⏰ Lire bientôt", 
        command=lambda i=item: self._safe_add_to_queue_from_result(i)
    )
    context_menu.add_separator()
    
    # Ajouter les playlists existantes
    for playlist_name in self.playlists.keys():
        if playlist_name != "Main Playlist":
            context_menu.add_command(
                label=f"➕ Ajouter à '{playlist_name}'",
                command=lambda name=playlist_name: self._add_to_specific_playlist_with_youtube_support(filepath, name, youtube_item)
            )

    context_menu.add_separator()

    # Option pour créer une nouvelle playlist
    context_menu.add_command(
        label="📝 Créer nouvelle playlist...",
        command=lambda: self._create_new_playlist_dialog_with_youtube_support(filepath, youtube_item)
    )
    
    # Options de fichier
    context_menu.add_command(
        label="📂 Ouvrir le dossier",
        command=lambda: self._open_file_location_with_youtube_support(filepath, youtube_item)
    )

    context_menu.add_command(
        label="🔗 Ouvrir sur YouTube",
        command=lambda: self._open_on_youtube_with_youtube_support(filepath, youtube_item)
    )

    context_menu.add_separator()

    # Option de suppression/téléchargement
    context_menu.add_command(
        label="⬇️ Télécharger maintenant",
        command=lambda: self._download_youtube_video(item, add_to_main_playlist=False),
        foreground='#44ff44'
    )
    # else:
    #     menu.add_command(
    #         label="🗑️ Supprimer définitivement",
    #         command=lambda: self._delete_file_permanently(filepath),
    #         foreground='#ff4444'
    #     )
    
    # Afficher le menu à la position de la souris ou de l'événement
    try:
        if event:
            context_menu.post(event.x_root, event.y_root)
        else:
            context_menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    except:
        # Fallback
        context_menu.post(100, 100)

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

def _download_youtube_video(self, frame, add_to_main_playlist=False):
    """Télécharge une vidéo YouTube"""

    video = frame.video_data
    url = video.get('url', '')

    title = frame.get('title', 'Vidéo YouTube')
    print("DEBUG BOUAAAA, ", url, title)
    
    if url:
        
        # Configurer search_list pour la compatibilité avec _download_youtube_thread
        self.search_list = [frame.video_data]
        
        # Utiliser la fonction de téléchargement existante
        threading.Thread(
            target=self._download_youtube_thread,
            args=(url, add_to_main_playlist),  # url et add_to_playlist
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
    print('_download_and_add_to_playlist')
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
        
        downloads_path = self.downloads_folder
        
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

def select_downloads_folder(self):
    """Permet de changer le dossier de téléchargements et déplacer les fichiers existants"""
    try:
        # Demander à l'utilisateur de choisir un nouveau dossier
        new_folder = filedialog.askdirectory(
            title="Choisir le nouveau dossier de téléchargements",
            initialdir=os.path.expanduser("~")
        )
        
        if not new_folder:
            return  # L'utilisateur a annulé
        
        # Vérifier que le dossier choisi n'est pas le dossier actuel
        current_downloads_folder = os.path.join(os.getcwd(), "downloads")
        if os.path.abspath(new_folder) == os.path.abspath(current_downloads_folder):
            messagebox.showinfo("Information", "Le dossier sélectionné est déjà le dossier de téléchargements actuel.")
            return
        
        # Vérifier s'il y a des fichiers à déplacer
        files_to_move = 0
        if os.path.exists(current_downloads_folder):
            try:
                for root, dirs, files in os.walk(current_downloads_folder):
                    files_to_move += len(files)
            except:
                files_to_move = "plusieurs"
        
        # Demander confirmation pour le déplacement
        if files_to_move > 0:
            result = messagebox.askyesno(
                "Confirmation de déplacement",
                f"Voulez-vous déplacer tous les téléchargements et caches existants vers :\n\n{new_folder}\n\n"
                f"Fichiers à déplacer : {files_to_move}\n"
                "Cette opération peut prendre du temps selon la quantité de fichiers.\n\n"
                "Note: Certains fichiers de cache peuvent ne pas être déplaçables s'ils sont en cours d'utilisation.",
                icon='question'
            )
        else:
            result = messagebox.askyesno(
                "Confirmation de changement",
                f"Changer le dossier de téléchargements vers :\n\n{new_folder}\n\n"
                "Aucun fichier existant à déplacer.",
                icon='question'
            )
        
        if not result:
            return
        
        # Créer le nouveau dossier downloads s'il n'existe pas
        # Normaliser le chemin pour éviter les mélanges de séparateurs
        new_downloads_folder = os.path.normpath(os.path.join(new_folder, "downloads"))
        os.makedirs(new_downloads_folder, exist_ok=True)
        
        # Déplacer tous les fichiers du dossier downloads actuel
        if os.path.exists(current_downloads_folder) and files_to_move > 0:
            # Afficher un message de progression
            self.status_bar.config(text="Déplacement des fichiers en cours...")
            self.root.update()
            
            _move_folder_contents(current_downloads_folder, new_downloads_folder)
        
        # Vérification spéciale pour le fichier playlists.json
        old_playlists_file = os.path.join(current_downloads_folder, "playlists.json")
        new_playlists_file = os.path.join(new_downloads_folder, "playlists.json")
        
        if os.path.exists(old_playlists_file):
            try:
                # Copier et mettre à jour les chemins dans playlists.json
                _update_playlists_paths(old_playlists_file, new_playlists_file, current_downloads_folder, new_downloads_folder)
                print(f"Fichier playlists.json copié et mis à jour vers le nouveau dossier")
            except Exception as e:
                print(f"Erreur lors de la mise à jour du fichier playlists.json: {e}")
                # En cas d'erreur, au moins copier le fichier
                try:
                    import shutil
                    shutil.copy2(old_playlists_file, new_playlists_file)
                    print(f"Fichier playlists.json copié (sans mise à jour des chemins)")
                except Exception as e2:
                    print(f"Erreur lors de la copie du fichier playlists.json: {e2}")
        
        # Mettre à jour la configuration pour utiliser le nouveau dossier
        _update_downloads_path_config(self, new_downloads_folder)
        
        # Message de succès
        success_msg = f"Dossier de téléchargements changé vers : {os.path.basename(new_downloads_folder)}"
        self.status_bar.config(text=success_msg)
        
        # Afficher une boîte de dialogue de confirmation
        messagebox.showinfo(
            "Changement effectué",
            f"Le dossier de téléchargements a été changé avec succès.\n\n"
            f"Nouveau dossier : {new_downloads_folder}\n\n"
            "L'application utilisera maintenant ce dossier pour tous les nouveaux téléchargements."
        )
        
        # Effacer le message après 5 secondes
        self.root.after(5000, lambda: self.status_bar.config(text=""))
        
        # Rafraîchir les onglets pour refléter les changements
        if hasattr(self, '_refresh_downloads_library'):
            self._refresh_downloads_library()
        if hasattr(self, '_refresh_playlists_library'):
            self._refresh_playlists_library()
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de changer le dossier de téléchargements:\n{str(e)}")
        self.status_bar.config(text="Erreur lors du changement de dossier")

def _move_folder_contents(source_folder, destination_folder):
    """Déplace tout le contenu d'un dossier vers un autre avec gestion des erreurs d'accès"""
    import shutil
    import time
    
    if not os.path.exists(source_folder):
        return
    
    # Créer le dossier de destination s'il n'existe pas
    os.makedirs(destination_folder, exist_ok=True)
    
    errors = []
    
    # Déplacer tous les fichiers et dossiers
    for item in os.listdir(source_folder):
        source_path = os.path.join(source_folder, item)
        destination_path = os.path.join(destination_folder, item)
        
        try:
            if os.path.isdir(source_path):
                # Gestion spéciale pour le dossier .cache
                if item == ".cache":
                    _move_cache_folder_safely(source_path, destination_path)
                else:
                    # Si c'est un dossier normal, le déplacer récursivement
                    if os.path.exists(destination_path):
                        # Si le dossier existe déjà, fusionner le contenu
                        _move_folder_contents(source_path, destination_path)
                        try:
                            os.rmdir(source_path)  # Supprimer le dossier source vide
                        except OSError:
                            pass  # Ignorer si le dossier n'est pas vide
                    else:
                        shutil.move(source_path, destination_path)
            else:
                # Si c'est un fichier, le déplacer
                if os.path.exists(destination_path):
                    # Si le fichier existe déjà, ajouter un suffixe
                    base, ext = os.path.splitext(destination_path)
                    counter = 1
                    while os.path.exists(f"{base}_{counter}{ext}"):
                        counter += 1
                    destination_path = f"{base}_{counter}{ext}"
                
                # Essayer plusieurs fois en cas d'erreur temporaire
                for attempt in range(3):
                    try:
                        shutil.move(source_path, destination_path)
                        break
                    except PermissionError:
                        if attempt < 2:
                            time.sleep(0.5)  # Attendre un peu avant de réessayer
                        else:
                            # Essayer de copier puis supprimer
                            try:
                                shutil.copy2(source_path, destination_path)
                                os.remove(source_path)
                                break
                            except Exception as copy_error:
                                errors.append(f"Impossible de déplacer {item}: {copy_error}")
                    except Exception as move_error:
                        if attempt == 2:
                            errors.append(f"Erreur lors du déplacement de {item}: {move_error}")
                        
        except Exception as e:
            errors.append(f"Erreur lors du traitement de {item}: {e}")
    
    # Supprimer le dossier source s'il est vide
    try:
        if os.path.exists(source_folder) and not os.listdir(source_folder):
            os.rmdir(source_folder)
    except:
        pass
    
    # Afficher les erreurs s'il y en a
    if errors:
        error_msg = "Certains fichiers n'ont pas pu être déplacés:\n" + "\n".join(errors[:5])
        if len(errors) > 5:
            error_msg += f"\n... et {len(errors) - 5} autres erreurs"
        print(error_msg)

def _move_cache_folder_safely(source_cache, destination_cache):
    """Déplace le dossier cache de manière sécurisée"""
    import shutil
    
    try:
        # Créer le dossier de destination
        os.makedirs(destination_cache, exist_ok=True)
        
        # Essayer de déplacer le contenu plutôt que le dossier entier
        if os.path.exists(source_cache):
            for cache_item in os.listdir(source_cache):
                source_item = os.path.join(source_cache, cache_item)
                dest_item = os.path.join(destination_cache, cache_item)
                
                try:
                    if os.path.isdir(source_item):
                        if os.path.exists(dest_item):
                            # Fusionner les dossiers
                            _move_folder_contents(source_item, dest_item)
                        else:
                            shutil.move(source_item, dest_item)
                    else:
                        # Pour les fichiers, essayer de les copier puis les supprimer
                        if not os.path.exists(dest_item):
                            try:
                                shutil.copy2(source_item, dest_item)
                                os.remove(source_item)
                            except PermissionError:
                                # Si on ne peut pas supprimer, au moins on a copié
                                print(f"Fichier copié mais non supprimé: {cache_item}")
                except Exception as e:
                    print(f"Erreur avec le fichier cache {cache_item}: {e}")
            
            # Essayer de supprimer le dossier source s'il est vide
            try:
                if not os.listdir(source_cache):
                    os.rmdir(source_cache)
            except:
                pass
                
    except Exception as e:
        print(f"Erreur lors du déplacement du cache: {e}")
        # En cas d'échec, créer au moins le dossier de destination
        os.makedirs(destination_cache, exist_ok=True)

def _update_downloads_path_config(self, new_downloads_folder):
    """Met à jour la configuration pour utiliser le nouveau dossier de téléchargements"""
    try:
        # Normaliser le chemin pour utiliser les séparateurs corrects du système
        normalized_path = os.path.normpath(new_downloads_folder)
        
        # Mettre à jour les options yt-dlp
        self.ydl_opts['outtmpl'] = os.path.join(normalized_path, '%(title)s.%(ext)s')
        
        # Sauvegarder le nouveau chemin dans un fichier de configuration
        config_file = os.path.join(os.getcwd(), "downloads_path.txt")
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(normalized_path)
        
        # Mettre à jour toutes les références au dossier downloads dans l'application
        self.downloads_folder = normalized_path
        
        # Réinitialiser le système de cache avec le nouveau dossier
        if hasattr(self, '_init_cache_system'):
            self._init_cache_system()
        
        # Recharger les playlists depuis le nouveau dossier
        self.load_playlists()
        
        # Rafraîchir l'affichage des playlists si l'onglet est visible
        if hasattr(self, '_refresh_playlists_library'):
            self._refresh_playlists_library()
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la configuration: {e}")

def _update_playlists_paths(old_playlists_file, new_playlists_file, old_downloads_folder, new_downloads_folder):
    """Copie le fichier playlists.json vers le nouveau dossier (les chemins relatifs n'ont pas besoin d'être modifiés)"""
    import shutil
    
    try:
        # Comme les playlists utilisent maintenant des chemins relatifs,
        # il suffit de copier le fichier tel quel
        shutil.copy2(old_playlists_file, new_playlists_file)
        print(f"Fichier playlists.json copié vers le nouveau dossier (chemins relatifs conservés)")
        
    except Exception as e:
        print(f"Erreur lors de la copie du fichier playlists.json: {e}")
        raise
