from search_tab import *
from scrap import anison_scrapper


class SlidingPanel:
    def __init__(self, music_player, root, frame, width, height):
        self.music_player = music_player
        self.root = root
        self.frame = frame
        self.width = width
        self.height = height
        
       
        self.subtitles_label = None
        
        self.sliding_panel = tk.Frame(frame, width=0, bg=COLOR_APP_BG, relief='sunken', bd=2)
        # Ne pas placer le panel tout de suite, attendre que les dimensions soient disponibles
        
        self.load_icons()
        self.create_sliding_panel_content()
                 
        # Variables pour l'animation
        self.animating = False
        self.panel_visible = False
        self.target_width = width  # Utiliser la largeur passée en paramètre ou 400 max
        self.animation_speed = 15
        self.sensitivity = 50  # Largeur de la zone sensible sur le côté droit de l'image
        self.initialized = False  # Flag pour savoir si le panel a été initialisé
        
        # Initialiser le positionnement après que les widgets soient créés
        self.root.after(100, self._initialize_position)
        
        # Bind des événements de souris sur l'image
        self.setup_event_bindings()
    
    def set_frame(self, frame):
        """Change le frame parent du panneau glissant"""
        self.frame = frame
        
    
    def _initialize_position(self):
        """Initialise la position du panel une fois que les dimensions sont disponibles"""
        try:
            # S'assurer que le frame parent a ses dimensions finales
            self.frame.update_idletasks()
            parent_width = self.frame.winfo_width()
            parent_height = self.frame.winfo_height()
            
            
            if parent_width <= 1:
                # Les dimensions ne sont pas encore disponibles, réessayer plus tard
                print("DEBUG: Dimensions pas encore disponibles, réessai dans 100ms")
                self.root.after(100, self._initialize_position)
                return
            
            # Positionner le panel hors écran à droite du frame parent
            self.sliding_panel.place(x=parent_width, y=0, width=0, relheight=1.0, anchor='ne')
            self.initialized = True
            print("DEBUG: Panel initialisé et positionné correctement")
            
        except Exception as e:
            print(f"DEBUG: Erreur lors de l'initialisation: {e}")
            # Réessayer en cas d'erreur
            self.root.after(100, self._initialize_position)
        
        # Timer pour vérifier la position de la souris
        self.check_mouse_position()
    
    def create_sliding_panel_content(self):
        """Crée le contenu du panneau glissant"""
        # Frame interne pour le contenu
        self.content_panel = tk.Frame(self.sliding_panel, bg=COLOR_APP_BG)
        self.content_panel.pack(fill='both', expand=True, padx=0, pady=0)
        
        self.infos_button = ctk.CTkButton(self.content_panel,
                image=self.icons["infos"],
                text="",
                cursor='hand2',
                command=self.show_infos_menu,
                fg_color=COLOR_APP_BG,
                hover_color=COLOR_APP_BG_HOVER,
                width=32,
                height=32
        )
        self.infos_button.pack(pady=(20, 10), padx=2)
        
        self.subtitles_button = ctk.CTkButton(self.content_panel,
                image=self.icons["subtitles"],
                cursor='hand2',
                command=self.toggle_subtitles,
                fg_color=COLOR_APP_BG if not self.music_player.Subtitles.subtitles_enabled else COLOR_SELECTED,
                hover_color=COLOR_APP_BG_HOVER if not self.music_player.Subtitles.subtitles_enabled else get_color("COLOR_SELECTED_HOVERED"),
                width=32,
                height=32,
                text=""
        )
        self.subtitles_button.pack(pady=10, padx=2)
        self.subtitles_button.bind("<ButtonPress-3>", self._show_infos_menus)
        
        self.switch_button = ctk.CTkButton(self.content_panel,
                image=self.icons["switch"],
                cursor='hand2',
                # command=self.show_infos_menu,
                fg_color=COLOR_APP_BG,
                hover_color=COLOR_APP_BG_HOVER,
                width=32,
                height=32,
                text=""
        )
        self.switch_button.pack(pady=10, padx=2)
        
        move_right_button = ctk.CTkButton(self.content_panel,
                image=self.icons["move_right"],
                cursor='hand2',
                command=self.move_thumbnail_right,
                fg_color=COLOR_APP_BG,
                hover_color=COLOR_APP_BG_HOVER,
                width=32,
                height=32,
                text=""
        )
        move_right_button.pack(pady=10, padx=2)
        
        move_left_button = ctk.CTkButton(self.content_panel,
                image=self.icons["move_left"],
                cursor='hand2',
                command=self.move_thumbnail_left,
                fg_color=COLOR_APP_BG,
                hover_color=COLOR_APP_BG_HOVER,
                width=32,
                height=32,
                text=""
        )
        move_left_button.pack(pady=10, padx=2)
        
        move_right_button.bind("<ButtonPress-3>", lambda e: self.reset_thumbnail_offset())
        move_left_button.bind("<ButtonPress-3>", lambda e: self.reset_thumbnail_offset())
    
    
    def setup_event_bindings(self):
        """Configure les événements de souris sur l'image"""
        self.frame.bind("<Enter>", self.on_image_enter)
        self.frame.bind("<Leave>", self.on_image_leave)
        self.frame.bind("<Motion>", self.on_image_motion)
        self.sliding_panel.bind("<Enter>", self.on_panel_enter)
        self.sliding_panel.bind("<Leave>", self.on_panel_leave)
    
    def load_icons(self):
        """Load icons for the application from the assets directory."""
        icon_names = {
            "infos": "infos.png",
            "subtitles": "subtitles.png",
            "switch": "switch.png",
            "move_right": "move_right.png",
            "move_left": "move_left.png"
        }

        # Chemin absolu vers le dossier assets
        base_path = os.path.join(self.music_player.root_path, "assets")

        self.icons = {}
        for key, filename in icon_names.items():
            try:
                path = os.path.join(base_path, filename)
                image = Image.open(path).resize((20, 20), Image.Resampling.LANCZOS)
                self.icons[key] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Erreur chargement {filename}: {e}")
    
    def on_image_enter(self, event):
        """Quand la souris entre dans l'image"""
        self.mouse_in_image = True
    
    def on_image_leave(self, event):
        """Quand la souris quitte l'image"""
        self.mouse_in_image = False
    
    def on_image_motion(self, event):
        """Quand la souris bouge dans l'image"""
        if not self.animating:
            image_width = self.frame.winfo_width()
            
            # Vérifie si la souris est dans la zone sensible du côté droit
            if event.x >= image_width - self.sensitivity:
                if not self.panel_visible:
                    self.show_panel()
            else:
                # Si la souris n'est pas dans la zone sensible et pas dans le panneau
                if self.panel_visible and not self.is_mouse_in_panel():
                    self.hide_panel()
    
    def on_panel_enter(self, event):
        """Quand la souris entre dans le panneau"""
        self.mouse_in_panel = True
    
    def on_panel_leave(self, event):
        """Quand la souris quitte le panneau"""
        self.mouse_in_panel = False
        # Vérifie si on doit fermer le panneau
        if self.panel_visible and not self.is_mouse_in_image_right_zone():
            self.hide_panel()
    
    def check_mouse_position(self):
        """Vérifie périodiquement la position de la souris"""
        if self.panel_visible and not self.animating:
            if not self.is_mouse_in_panel() and not self.is_mouse_in_image_right_zone():
                self.hide_panel()
        
        self.root.after(100, self.check_mouse_position)
    
    def is_mouse_in_image_right_zone(self):
        """Vérifie si la souris est dans la zone sensible du côté droit de l'image"""
        try:
            x, y = self.root.winfo_pointerxy()
            image_x = self.frame.winfo_rootx()
            image_y = self.frame.winfo_rooty()
            image_width = self.frame.winfo_width()
            image_height = self.frame.winfo_height()
            
            # Vérifie si la souris est dans l'image
            in_image = (image_x <= x <= image_x + image_width and 
                       image_y <= y <= image_y + image_height)
            
            if in_image:
                # Vérifie si la souris est dans la zone sensible du côté droit
                distance_from_right = (image_x + image_width) - x
                return distance_from_right <= self.sensitivity
            
            return False
        except:
            return False
    
    def is_mouse_in_panel(self):
        """Vérifie si la souris est dans le panneau"""
        try:
            x, y = self.root.winfo_pointerxy()
            panel_x = self.sliding_panel.winfo_rootx()
            panel_y = self.sliding_panel.winfo_rooty()
            panel_width = self.sliding_panel.winfo_width()
            panel_height = self.sliding_panel.winfo_height()
            
            return (panel_x <= x <= panel_x + panel_width and 
                    panel_y <= y <= panel_y + panel_height)
        except:
            return False
    
    def show_panel(self):
        """Affiche le panneau avec animation fluide"""
        if self.animating:
            return
        
        # Vérifier si le panel est initialisé
        if not self.initialized:
            print("DEBUG: Panel pas encore initialisé, attendre...")
            self.root.after(100, self.show_panel)
            return
            
        self.animating = True
        self.panel_visible = True
        
        # S'assurer que le frame parent a ses dimensions finales
        self.frame.update_idletasks()
        
        # Positionne le panneau à droite du frame parent (pas de la fenêtre root)
        parent_width = self.frame.winfo_width()
        parent_height = self.frame.winfo_height()
        
        if parent_width <= 1:
            self.animating = False
            self.panel_visible = False
            self.root.after(100, self.show_panel)
            return
        
        # Positionner le panel à droite avec une largeur de 0 pour commencer l'animation
        self.sliding_panel.place(x=parent_width, y=0, width=0, relheight=1.0, anchor='ne')
        self.sliding_panel.lift()
        
        self.animate_panel(0, self.target_width, True)
    
    def hide_panel(self):
        """Cache le panneau avec animation fluide"""
        if self.animating or not self.panel_visible:
            return
            
        self.animating = True
        
        # Utiliser target_width au lieu de winfo_width() qui peut être incorrect
        self.animate_panel(self.target_width, 0, False)
    
    def animate_panel(self, start_width, target_width, showing):
        """Animation fluide du panneau"""
        
        current_width = start_width
        
        def animation_step():
            nonlocal current_width
            delay = 50
            if showing:
                # Animation d'ouverture
                current_width += self.animation_speed
                if current_width >= target_width:
                    current_width = target_width
                    self.animating = False
                else:
                    self.root.after(delay, animation_step)
            else:
                # Animation de fermeture
                current_width -= self.animation_speed
                if current_width <= target_width:
                    current_width = target_width
                    self.animating = False
                    self.panel_visible = False
                    # Cache complètement le panneau après animation
                    self.sliding_panel.place_forget()
                else:
                    self.root.after(delay, animation_step)
            
            # Calcule la position X pour que le panneau reste aligné à droite du frame parent
            self.frame.update_idletasks()  # S'assurer que les dimensions sont à jour
            parent_width = self.frame.winfo_width()
            panel_x = parent_width - current_width
            
            # Met à jour la largeur et la position en une seule fois avec place()
            self.sliding_panel.place(x=panel_x, y=0, width=current_width, relheight=1.0, anchor='nw')
        
            
            # Forcer la mise à jour de l'affichage
            self.sliding_panel.update_idletasks()
        animation_step()
    
    def button_clicked(self, button_text):
        """Gestionnaire de clic sur les boutons"""
        print(f"Bouton cliqué: {button_text}")
    
    def force_show_panel(self):
        """Force l'affichage du panel pour debug"""
        print("DEBUG: Force show panel")
        if not self.initialized:
            print("DEBUG: Panel pas initialisé, initialisation forcée...")
            self._initialize_position()
            self.root.after(50, self.show_panel)
        else:
            self.show_panel()
        
    def show_infos_menu(self):
        """Affiche le menu des infos sur le panel"""                             
        infos_menu = tk.Menu(
            self.sliding_panel,
            tearoff=0,
            bg='white',
            fg='black',
            activebackground='#4a8fe7',
            activeforeground='white',
            relief='flat',
            bd=1
        )
        
        infos_menu.add_command(label="Source: Anison", state='disabled')
        infos_menu.add_separator()
        
        
        if len(self.music_player.main_playlist) > 0:
            current_song_path = self.music_player.main_playlist[self.music_player.current_index]
            song_name = os.path.basename(current_song_path)
            artist, album = self.music_player._get_audio_metadata(current_song_path)
            
            song_name = song_name.replace(".mp3", "")
            if artist:
                song_name = song_name.replace(artist, "")
            
            print(f"infos, song_name: {song_name}, artist: {artist}, album: {album}") # Debugsong_name, artist, album")
            infos_menu.add_command(label=f"Anime: ")

    def toggle_subtitles(self):
        """Toggle subtitles visibility"""
        self.music_player.Subtitles.subtitles_enabled = not self.music_player.Subtitles.subtitles_enabled
        if self.music_player.Subtitles.subtitles_enabled:
            self.subtitles_button.configure(fg_color=COLOR_SELECTED, hover_color=get_color("COLOR_SELECTED_HOVERED"))
        else:
            self.subtitles_button.configure(fg_color=COLOR_APP_BG, hover_color=COLOR_APP_BG_HOVER)
        
        
        # un on change sur Subtitles serait mieux..
        if self.music_player.Subtitles.subtitles_enabled:
            # Afficher les sous-titres
            self.music_player.Subtitles.show_subtitles()
        else:
            # Cacher les sous-titres
            self.music_player.Subtitles.hide_subtitles()
            self.sliding_panel.update_idletasks()
    
    def _show_infos_menus(self, event):
        self.subtitles_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                            activebackground='#4a8fe7', activeforeground='white',
                            relief='flat', bd=1)
    
        self.subtitles_menu.add_command(
            label="Available subtitles (or not)",
            state='disabled'
        )
        self.subtitles_menu.add_separator()
        
        self.automatic_subtitles_menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
                    activebackground=COLOR_SELECTED, activeforeground='white')
        
        self.manual_subtitles_menu = tk.Menu(self.root, tearoff=0, bg='#3d3d3d', fg='white', 
                    activebackground=COLOR_SELECTED, activeforeground='white')
        
        self.subtitles_menu.add_cascade(
            label="Manual subtitles",
            menu = self.automatic_subtitles_menu,
        )
        self.subtitles_menu.add_separator()
        
        self.subtitles_menu.add_cascade(
            label="Automatic subtitles",
            menu = self.automatic_subtitles_menu,
        )
        
        # Afficher le menu à la position de la souris
        try:
            self.subtitles_menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        except:
            # Fallback
            self.subtitles_menu.post(100, 100)
    
    def move_thumbnail_right(self):
        current_song_path = self.music_player.main_playlist[self.music_player.current_index]
        current_song_path_rel = os.path.relpath(current_song_path, self.music_player.downloads_folder)
        if not current_song_path_rel in self.music_player.thumbnail_offsets:
            self.music_player.thumbnail_offsets[current_song_path_rel] = 0
        
        self.music_player.thumbnail_offsets[current_song_path_rel] = max(-1, self.music_player.thumbnail_offsets[current_song_path_rel] - 0.05)
        
        
        self.music_player._show_current_song_thumbnail()
    
    
    def move_thumbnail_left(self):
        current_song_path = self.music_player.main_playlist[self.music_player.current_index]
        current_song_path_rel = os.path.relpath(current_song_path, self.music_player.downloads_folder)
        if not current_song_path_rel in self.music_player.thumbnail_offsets:
            self.music_player.thumbnail_offsets[current_song_path_rel] = 0
        
        self.music_player.thumbnail_offsets[current_song_path_rel] = min(1, self.music_player.thumbnail_offsets[current_song_path_rel] + 0.05)
        
        
        self.music_player._show_current_song_thumbnail()
    
    def reset_thumbnail_offset(self):
        current_song_path = self.music_player.main_playlist[self.music_player.current_index]
        current_song_path_rel = os.path.relpath(current_song_path, self.music_player.downloads_folder)
        if not current_song_path_rel in self.music_player.thumbnail_offsets:
            self.music_player.thumbnail_offsets[current_song_path_rel] = 0
        
        self.music_player.thumbnail_offsets[current_song_path_rel] = 0
        
        
        self.music_player._show_current_song_thumbnail()
    