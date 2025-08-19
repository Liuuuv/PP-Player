"""
Contrôles de lecture de l'interface utilisateur
"""
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from mutagen.mp3 import MP3


class ControlsManager:
    """Gestionnaire des contrôles de lecture"""
    
    def __init__(self, parent_frame, audio_player, settings):
        self.parent_frame = parent_frame
        self.audio_player = audio_player
        self.settings = settings
        
        # Variables d'interface
        self.icons = {}
        self.user_dragging = False
        
        # Charger les icônes
        self._load_icons()
        
        # Créer l'interface
        self._create_controls()
    
    def _load_icons(self):
        """Charge les icônes pour les boutons"""
        try:
            assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
            icon_files = {
                "play": "play.png",
                "pause": "pause.png",
                "next": "next.png",
                "previous": "previous.png",
                "loop": "loop.png",
                "loop1": "loop1.png",
                "shuffle": "shuffle.png",
                "volume": "volume.png"
            }
            
            for name, filename in icon_files.items():
                icon_path = os.path.join(assets_dir, filename)
                if os.path.exists(icon_path):
                    image = Image.open(icon_path)
                    image = image.resize((20, 20), Image.Resampling.LANCZOS)
                    self.icons[name] = ImageTk.PhotoImage(image)
                else:
                    # Icône par défaut (texte)
                    self.icons[name] = None
        except Exception as e:
            print(f"Erreur chargement icônes: {e}")
    
    def _create_controls(self):
        """Crée l'interface des contrôles"""
        # Frame principal des contrôles (en bas)
        self.control_frame = ttk.Frame(self.parent_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Frame pour les informations de la chanson
        self._create_song_info()
        
        # Frame pour la barre de progression
        self._create_progress_bar()
        
        # Frame pour les boutons de contrôle
        self._create_control_buttons()
        
        # Frame pour le volume
        self._create_volume_controls()
    
    def _create_song_info(self):
        """Crée l'affichage des informations de la chanson"""
        info_frame = ttk.Frame(self.control_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Miniature de la chanson
        self.thumbnail_label = tk.Label(
            info_frame,
            text="♪",
            bg='#2d2d2d',
            fg='#666666',
            font=('TkDefaultFont', 20),
            width=8,
            height=3
        )
        self.thumbnail_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Informations textuelles
        text_frame = ttk.Frame(info_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.song_label = ttk.Label(
            text_frame,
            text="Aucune chanson sélectionnée",
            font=('TkDefaultFont', 12, 'bold')
        )
        self.song_label.pack(anchor=tk.W)
        
        self.artist_label = ttk.Label(
            text_frame,
            text="",
            font=('TkDefaultFont', 10)
        )
        self.artist_label.pack(anchor=tk.W)
    
    def _create_progress_bar(self):
        """Crée la barre de progression"""
        progress_frame = ttk.Frame(self.control_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Temps actuel
        self.time_label = ttk.Label(progress_frame, text="0:00")
        self.time_label.pack(side=tk.LEFT)
        
        # Barre de progression
        self.progress_var = tk.DoubleVar()
        self.progress_scale = ttk.Scale(
            progress_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self._on_progress_change
        )
        self.progress_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        # Bind pour le drag
        self.progress_scale.bind("<Button-1>", self._on_progress_click)
        self.progress_scale.bind("<B1-Motion>", self._on_progress_drag)
        self.progress_scale.bind("<ButtonRelease-1>", self._on_progress_release)
        
        # Temps total
        self.duration_label = ttk.Label(progress_frame, text="0:00")
        self.duration_label.pack(side=tk.RIGHT)
    
    def _create_control_buttons(self):
        """Crée les boutons de contrôle"""
        buttons_frame = ttk.Frame(self.control_frame)
        buttons_frame.pack(pady=(0, 10))
        
        # Bouton précédent
        self.prev_button = tk.Button(
            buttons_frame,
            image=self.icons.get("previous"),
            text="⏮" if not self.icons.get("previous") else "",
            command=self.audio_player.previous_track,
            bg='#3d3d3d',
            fg='white',
            activebackground='#4a4a4a',
            relief='flat',
            bd=0,
            width=3 if not self.icons.get("previous") else None
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton play/pause
        self.play_button = tk.Button(
            buttons_frame,
            image=self.icons.get("play"),
            text="▶" if not self.icons.get("play") else "",
            command=self.audio_player.play_pause,
            bg='#3d3d3d',
            fg='white',
            activebackground='#4a4a4a',
            relief='flat',
            bd=0,
            width=3 if not self.icons.get("play") else None
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton suivant
        self.next_button = tk.Button(
            buttons_frame,
            image=self.icons.get("next"),
            text="⏭" if not self.icons.get("next") else "",
            command=self.audio_player.next_track,
            bg='#3d3d3d',
            fg='white',
            activebackground='#4a4a4a',
            relief='flat',
            bd=0,
            width=3 if not self.icons.get("next") else None
        )
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton shuffle
        self.shuffle_button = tk.Button(
            buttons_frame,
            image=self.icons.get("shuffle"),
            text="🔀" if not self.icons.get("shuffle") else "",
            command=self.audio_player.toggle_random_mode,
            bg='#3d3d3d',
            fg='white',
            activebackground='#4a4a4a',
            relief='flat',
            bd=0,
            width=3 if not self.icons.get("shuffle") else None
        )
        self.shuffle_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton loop
        self.loop_button = tk.Button(
            buttons_frame,
            image=self.icons.get("loop"),
            text="🔁" if not self.icons.get("loop") else "",
            command=self.audio_player.toggle_loop_mode,
            bg='#3d3d3d',
            fg='white',
            activebackground='#4a4a4a',
            relief='flat',
            bd=0,
            width=3 if not self.icons.get("loop") else None
        )
        self.loop_button.pack(side=tk.LEFT, padx=5)
    
    def _create_volume_controls(self):
        """Crée les contrôles de volume"""
        volume_frame = ttk.Frame(self.control_frame)
        volume_frame.pack(fill=tk.X)
        
        # Icône volume
        volume_icon = tk.Label(
            volume_frame,
            image=self.icons.get("volume"),
            text="🔊" if not self.icons.get("volume") else "",
            bg='#2d2d2d',
            fg='white'
        )
        volume_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        # Slider de volume
        self.volume_var = tk.DoubleVar()
        self.volume_scale = ttk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self._on_volume_change
        )
        self.volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Label du volume
        self.volume_label = ttk.Label(volume_frame, text="10%")
        self.volume_label.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _on_progress_click(self, event):
        """Gère le clic sur la barre de progression"""
        self.user_dragging = True
        self.audio_player.user_dragging = True
    
    def _on_progress_drag(self, event):
        """Gère le glissement sur la barre de progression"""
        pass  # La valeur est automatiquement mise à jour
    
    def _on_progress_release(self, event):
        """Gère le relâchement sur la barre de progression"""
        self.user_dragging = False
        self.audio_player.user_dragging = False
        
        # Définir la nouvelle position
        progress_percent = self.progress_var.get()
        new_position = (progress_percent / 100) * self.audio_player.song_length
        self.audio_player.set_position(new_position)
    
    def _on_progress_change(self, value):
        """Appelé quand la barre de progression change"""
        if not self.user_dragging:
            return
        
        # Mettre à jour l'affichage du temps pendant le drag
        progress_percent = float(value)
        current_time = (progress_percent / 100) * self.audio_player.song_length
        self.time_label.config(text=self._format_time(current_time))
    
    def _on_volume_change(self, value):
        """Gère le changement de volume"""
        volume = float(value) / 100
        self.audio_player.set_volume(volume)
        self.volume_label.config(text=f"{int(float(value))}%")
    
    def update_track_info(self, track_path):
        """Met à jour les informations de la piste"""
        if not track_path:
            self.song_label.config(text="Aucune chanson sélectionnée")
            self.artist_label.config(text="")
            self.thumbnail_label.config(text="♪", image="")
            return
        
        # Nom du fichier
        filename = os.path.basename(track_path)
        name_without_ext = os.path.splitext(filename)[0]
        self.song_label.config(text=name_without_ext)
        
        # Essayer d'extraire l'artiste des métadonnées
        try:
            audio = MP3(track_path)
            artist = audio.get('TPE1', [''])[0] if 'TPE1' in audio else ''
            self.artist_label.config(text=artist)
        except:
            self.artist_label.config(text="")
        
        # Charger la miniature
        self._load_thumbnail(track_path)
    
    def _load_thumbnail(self, track_path):
        """Charge la miniature de la piste"""
        try:
            # Chercher une image associée
            base_name = os.path.splitext(track_path)[0]
            image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            
            for ext in image_extensions:
                thumbnail_path = base_name + ext
                if os.path.exists(thumbnail_path):
                    image = Image.open(thumbnail_path)
                    image = image.resize((60, 45), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.thumbnail_label.configure(image=photo, text="")
                    self.thumbnail_label.image = photo
                    return
            
            # Pas d'image trouvée
            self.thumbnail_label.config(text="♪", image="")
            
        except Exception as e:
            print(f"Erreur chargement miniature: {e}")
            self.thumbnail_label.config(text="♪", image="")
    
    def update_time_display(self, current_time, total_time):
        """Met à jour l'affichage du temps"""
        if not self.user_dragging:
            # Mettre à jour la barre de progression
            if total_time > 0:
                progress = (current_time / total_time) * 100
                self.progress_var.set(progress)
            
            # Mettre à jour les labels de temps
            self.time_label.config(text=self._format_time(current_time))
            self.duration_label.config(text=self._format_time(total_time))
    
    def update_status(self, status):
        """Met à jour le statut du lecteur"""
        if status == "playing":
            if self.icons.get("pause"):
                self.play_button.config(image=self.icons["pause"], text="")
            else:
                self.play_button.config(text="⏸")
        elif status in ["paused", "stopped"]:
            if self.icons.get("play"):
                self.play_button.config(image=self.icons["play"], text="")
            else:
                self.play_button.config(text="▶")
        
        # Mettre à jour les boutons de mode
        self._update_mode_buttons()
    
    def _update_mode_buttons(self):
        """Met à jour l'apparence des boutons de mode"""
        # Bouton shuffle
        if self.audio_player.random_mode:
            self.shuffle_button.config(bg="#4a8fe7")
        else:
            self.shuffle_button.config(bg="#3d3d3d")
        
        # Bouton loop
        if self.audio_player.loop_mode == 0:
            self.loop_button.config(bg="#3d3d3d")
            if self.icons.get("loop"):
                self.loop_button.config(image=self.icons["loop"])
        elif self.audio_player.loop_mode == 1:
            self.loop_button.config(bg="#4a8fe7")
            if self.icons.get("loop"):
                self.loop_button.config(image=self.icons["loop"])
        elif self.audio_player.loop_mode == 2:
            self.loop_button.config(bg="#4a8fe7")
            if self.icons.get("loop1"):
                self.loop_button.config(image=self.icons["loop1"])
    
    def update_volume_display(self):
        """Met à jour l'affichage du volume"""
        volume_percent = self.settings.global_volume * 100
        self.volume_var.set(volume_percent)
        self.volume_label.config(text=f"{int(volume_percent)}%")
    
    def _format_time(self, seconds):
        """Formate le temps en mm:ss"""
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"