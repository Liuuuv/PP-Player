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

def _show_youtube_playlist_menu(self, video, frame):
        """Affiche un menu déroulant pour choisir la playlist pour une vidéo YouTube"""
        import tkinter.ttk as ttk
        
        # Créer un menu contextuel
        menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
                      activebackground='#4a8fe7', activeforeground='white')
        
        # Ajouter les playlists existantes
        for playlist_name in self.playlists.keys():
            menu.add_command(
                label=f"Ajouter à '{playlist_name}'",
                command=lambda name=playlist_name: self._add_youtube_to_playlist(video, frame, name)
            )
        
        menu.add_separator()
        
        # Option pour créer une nouvelle playlist
        menu.add_command(
            label="Créer nouvelle playlist...",
            command=lambda: self._create_new_playlist_dialog_youtube(video, frame)
        )
        
        # Afficher le menu à la position de la souris
        try:
            menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        except:
            # Fallback
            menu.post(100, 100)

def show_file_context_menu(self, filepath, event=None):
    """Affiche un menu contextuel pour un fichier avec options de playlist et suppression"""
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
            
            # Effacer le message après 3 secondes
            self.root.after(3000, lambda: self.status_bar.config(text=""))
            
    except PermissionError:
        messagebox.showerror("Erreur", "Permission refusée. Le fichier est peut-être en cours d'utilisation.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de supprimer le fichier:\n{str(e)}")
