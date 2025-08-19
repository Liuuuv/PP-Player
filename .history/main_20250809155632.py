import pygame
import os
import tkinter as tk
from tkinter import filedialog, ttk
from mutagen.mp3 import MP3
import time
import threading
from pydub import AudioSegment
import numpy as np
from PIL import Image, ImageTk
from yt_dlp import YoutubeDL
# from pytube import Search

from waveforms import*


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("PipiProut")
        self.root.geometry("800x700")
        self.root.configure(bg='#2d2d2d')
        
        # Initialisation pygame
        pygame.mixer.init()
        
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        # Récupérer les données audio pour visualisation
        samples = pygame.sndarray.array(pygame.mixer.music)
        self.waveform_data = None
        
        # Variables
        self.playlist = []
        self.current_index = 0
        self.paused = False
        self.volume = 0.3
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'outtmpl': os.path.join("downloads", '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # Ajout pour le streaming progressif
            'external_downloader': 'ffmpeg',
            'external_downloader_args': ['-ss', '0', '-to', '10'],  # Télécharge d'abord les 10 premières secondes
            # Optimisations pour la recherche
            # 'extract_flat': True,
            # 'simulate': True,
            # 'skip_download': True,
        }
        self.is_searching = False
        

        self.song_length = 0
        self.current_time = 0
        
        self.user_dragging = False
        self.base_position = 0
        
        self.show_waveform_current = False
        
        # Chargement des icônes
        self.icons = {}
        self.load_icons()
        
        # UI Modern
        self.create_ui()
        
        # Thread de mise à jour
        self.update_thread = threading.Thread(target=self.update_time, daemon=True)
        self.update_thread.start()
        
        self.current_downloads = set()  # Pour suivre les URLs en cours de téléchargement

    def create_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#2d2d2d')
        style.configure('TLabel', background='#2d2d2d', foreground='white')
        style.configure('TButton', background='#3d3d3d', foreground='white')
        style.configure('TScale', background='#2d2d2d')
        
        # config +
        style = ttk.Style()
        style.theme_use('clam')

        # Style de base des boutons
        style.configure('TButton',
            background='#3d3d3d',
            foreground='white',
            borderwidth=0,
            focusthickness=0,
            padding=6
        )

        # Réduction de l'effet hover (état 'active')
        style.map('TButton',
            background=[('active', '#4a4a4a'), ('!active', '#3d3d3d')],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')],
            focuscolor=[('focus', '')]
        )

        # Main Frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top Frame (Youtube search)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ## Youtube Search Frame
        youtube_frame = ttk.Frame(top_frame)
        youtube_frame.pack(fill=tk.X)

        self.youtube_entry = tk.Entry(youtube_frame)
        self.youtube_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.youtube_entry.bind('<Return>', lambda event: self.search_youtube())

        search_btn = ttk.Button(youtube_frame, text="Rechercher", command=self.search_youtube)
        search_btn.pack(side=tk.LEFT)
        
        # Middle Frame (Playlist and results)
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Playlist Frame (left side - takes all vertical space)
        playlist_frame = ttk.Frame(middle_frame)
        playlist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas et Scrollbar pour la playlist
        self.playlist_canvas = tk.Canvas(
            playlist_frame,
            bg='#3d3d3d',
            highlightthickness=0
        )
        self.playlist_scrollbar = ttk.Scrollbar(
            playlist_frame,
            orient="vertical",
            command=self.playlist_canvas.yview
        )
        self.playlist_canvas.configure(yscrollcommand=self.playlist_scrollbar.set)

        self.playlist_scrollbar.pack(side="right", fill="y")
        self.playlist_canvas.pack(side="left", fill="both", expand=True)

        self.playlist_container = ttk.Frame(self.playlist_canvas)
        self.playlist_canvas.create_window((0, 0), window=self.playlist_container, anchor="nw")

        self.playlist_container.bind(
            "<Configure>",
            lambda e: self.playlist_canvas.configure(
                scrollregion=self.playlist_canvas.bbox("all")
            )
        )
        self._bind_mousewheel(self.playlist_canvas, self.playlist_canvas)
        self._bind_mousewheel(self.playlist_container, self.playlist_canvas)
        
        # Youtube Results Frame (right side - fixed width)
        youtube_results_frame = ttk.Frame(middle_frame, width=350)
        youtube_results_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Canvas avec Scrollbar pour les résultats YouTube
        self.youtube_canvas = tk.Canvas(
            youtube_results_frame,
            bg='#3d3d3d',
            highlightthickness=0
        )
        
        self.scrollbar = ttk.Scrollbar(
            youtube_results_frame,
            orient="vertical",
            command=self.youtube_canvas.yview
        )
        self.youtube_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.youtube_canvas.pack(side="left", fill="both", expand=True)

        self.results_container = ttk.Frame(self.youtube_canvas)
        self.youtube_canvas.create_window((0, 0), window=self.results_container, anchor="nw")

        self.results_container.bind(
            "<Configure>",
            lambda e: self.youtube_canvas.configure(
                scrollregion=self.youtube_canvas.bbox("all")
            )
        )
        
        self._bind_mousewheel(self.youtube_canvas, self.youtube_canvas)
        self._bind_mousewheel(self.results_container, self.youtube_canvas)
        
        # Bottom Frame (Controls)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Control Frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.BOTH, expand=True)
        
        # Song Info
        self.song_label = ttk.Label(
            control_frame, text="No track selected", 
            font=('Helvetica', 12, 'bold')
        )
        self.song_label.pack(pady=10)
        
        # Progress Bar
        self.progress = ttk.Scale(
            control_frame, from_=0, to=100, orient=tk.HORIZONTAL,
            command=self.set_position
        )
        self.progress.pack(fill=tk.X, pady=5)
        
        self.progress.bind("<Button-1>", self.on_progress_press)   # début drag
        self.progress.bind("<ButtonRelease-1>", self.on_progress_release)  # fin drag
        self.progress.bind("<B1-Motion>", self.on_progress_drag) # pendant drag
        
        # Time Labels
        time_frame = ttk.Frame(control_frame)
        time_frame.pack(fill=tk.X)
        
        self.current_time_label = ttk.Label(time_frame, text="00:00")
        self.current_time_label.pack(side=tk.LEFT)
        
        self.song_length_label = ttk.Label(time_frame, text="00:00")
        self.song_length_label.pack(side=tk.RIGHT)
        
        # Conteneur horizontal pour boutons + volume
        buttons_volume_frame = ttk.Frame(control_frame)
        buttons_volume_frame.pack(fill=tk.X, pady=20)

        # Frame boutons (centré)
        button_frame = ttk.Frame(buttons_volume_frame)
        button_frame.grid(row=0, column=1, padx=20)

        # Boutons avec grid (centré dans button_frame)
        ttk.Button(button_frame, image=self.icons["add"], command=self.add_to_playlist).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, image=self.icons["prev"], command=self.prev_track).grid(row=0, column=1, padx=5)
        self.play_button = ttk.Button(button_frame, image=self.icons["play"], command=self.play_pause)
        self.play_button.grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, image=self.icons["next"], command=self.next_track).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, image=self.icons["hey"]).grid(row=0, column=4, padx=5)

        # Frame volume à droite
        volume_frame = ttk.Frame(buttons_volume_frame)
        volume_frame.grid(row=0, column=2, sticky="e")

        ttk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT)
        self.volume_slider = ttk.Scale(
            volume_frame, from_=0, to=100, 
            command=self.set_volume, value=self.volume*100,
            orient='horizontal'
        )
        self.volume_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)

        # Ajouter une colonne vide à gauche pour centrer (optionnel)
        buttons_volume_frame.grid_columnconfigure(0, weight=1)
        buttons_volume_frame.grid_columnconfigure(1, weight=0)  # bouton centré
        buttons_volume_frame.grid_columnconfigure(2, weight=0)  # volume
        buttons_volume_frame.grid_columnconfigure(3, weight=1)

        
        # Status Bar
        self.status_bar = ttk.Label(
            control_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(10,0))
        
        # Waveform Canvas
        self.waveform_canvas = tk.Canvas(bottom_frame, height=80, bg='#2d2d2d', highlightthickness=0)
        self.waveform_canvas.pack(fill=tk.X, pady=(0, 10))
        
        # self.colorize_ttk_frames(root)

    
    def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
        style = ttk.Style()
        color_index = 0

        for child in widget.winfo_children():
            if isinstance(child, ttk.Frame):
                style_name = f"Debug.TFrame{color_index}"
                # Copier le layout standard "TFrame"
                style.layout(style_name, style.layout("TFrame"))
                style.configure(style_name, background=colors[color_index % len(colors)])
                child.configure(style=style_name)
                color_index += 1

            # Appel récursif sur les enfants
            self.colorize_ttk_frames(child, colors)

        
        
    
    # def add_to_playlist(self):
    #     files = filedialog.askopenfilenames(
    #         filetypes=[("Fichiers Audio", "*.mp3 *.wav *.ogg *.flac"), ("Tous fichiers", "*.*")]
    #     )
    #     for file in files:
    #         self.playlist.append(file)
    #         self.playlist_box.insert(tk.END, os.path.basename(file))
    #     self.status_bar.config(text=f"{len(files)} track added")
    
    def _bind_mousewheel(self, widget, canvas):
        """Lie la molette de souris seulement quand le curseur est sur le widget"""
        widget.bind("<Enter>", lambda e: self._bind_scroll(canvas))
        widget.bind("<Leave>", lambda e: self._unbind_scroll(canvas))

    def _bind_scroll(self, canvas):
        """Active le défilement pour un canvas spécifique"""
        canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind_all("<Button-4>", lambda e: self._on_mousewheel(e, canvas))
        canvas.bind_all("<Button-5>", lambda e: self._on_mousewheel(e, canvas))

    def _unbind_scroll(self, canvas):
        """Désactive le défilement pour un canvas spécifique"""
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
    
    def add_to_playlist(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Fichiers Audio", "*.mp3 *.wav *.ogg *.flac"), ("Tous fichiers", "*.*")]
        )
        for file in files:
            self.playlist.append(file)
            self._add_playlist_item(file)
        self.status_bar.config(text=f"{len(files)} track added")

    def _add_playlist_item(self, filepath, thumbnail_path=None):
        """Ajoute un élément à la playlist avec miniature et bouton de suppression"""
        try:
            filename = os.path.basename(filepath)
            
            # Tronquer le texte si trop long (max 30 caractères)
            max_length = 25
            display_text = (filename[:max_length] + '...') if len(filename) > max_length else filename
            
            # 1. Frame principal pour l'item
            item_frame = ttk.Frame(
                self.playlist_container,
                style='TFrame',
                padding=(5, 2)
            )
            item_frame.pack(fill='x', pady=1)
            
            
            
            # 2. Configuration de la grille en 3 colonnes
            item_frame.columnconfigure(0, minsize=80, weight=0)  # Miniature
            item_frame.columnconfigure(1, weight=0)              # Texte
            item_frame.columnconfigure(2, minsize=40, weight=1)  # Bouton

            # 3. Miniature (colonne 0)
            thumbnail_label = tk.Label(
                item_frame,
                bg='#3d3d3d',
                width=80,
                height=45
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsw', padx=(0, 2))
            
            # Charger la miniature
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._load_image_thumbnail(thumbnail_path, thumbnail_label)
            else:
                self._load_mp3_thumbnail(filepath, thumbnail_label)

            # 4. Texte (colonne 1)
            text_frame = ttk.Frame(item_frame)
            text_frame.grid(row=0, column=1, sticky='nsew')
            
            title_label = tk.Label(
                text_frame,
                text=display_text,
                bg='#3d3d3d',
                fg='white',
                anchor='w',
                justify='left'
            )
            title_label.pack(side='left', fill='x', expand=True)

            # 5. Bouton de suppression (colonne 2)
            delete_btn = tk.Button(
                item_frame,
                image=self.icons["delete"],
                bg='#3d3d3d',
                activebackground='#4d4d4d',
                relief='flat',
                borderwidth=0
            )
            delete_btn.grid(row=0, column=2, sticky='e', padx=5, ipadx=3, ipady=3)

            # Utiliser un vrai lambda avec event
            delete_btn.bind("<Double-1>", lambda e, f=filepath, frame=item_frame: self._remove_playlist_item(f, frame))
            # item_frame.create_window(10, 25, anchor='w', window=delete_btn)

            item_frame.filepath = filepath
            
            def on_item_click():
                self.current_index = self.playlist.index(filepath)
                self.play_track()
                
            item_frame.bind("<Double-1>", lambda e: on_item_click())
            thumbnail_label.bind("<Double-1>", lambda e: on_item_click())
            title_label.bind("<Double-1>", lambda e: on_item_click())

        except Exception as e:
            print(f"Erreur affichage playlist item: {e}")
    
    def select_playlist_item(self, item_frame=None, index=None):
        """Met en surbrillance l'élément sélectionné dans la playlist"""
        # Désélectionner tous les autres éléments
        for child in self.playlist_container.winfo_children():
            if hasattr(child, 'selected'):
                child.selected = False
                child.configure(style='TFrame')
                for subchild in child.winfo_children():
                    if isinstance(subchild, (tk.Label, tk.Frame, tk.Button)):
                        subchild.config(bg='#3d3d3d')
        
        # Si on a fourni un index plutôt qu'un frame
        if index is not None:
            children = self.playlist_container.winfo_children()
            if 0 <= index < len(children):
                item_frame = children[index]
        
        # Sélectionner l'élément courant si fourni
        if item_frame:
            item_frame.selected = True
            item_frame.configure(style='Hover.TFrame')
            for child in item_frame.winfo_children():
                if isinstance(child, (tk.Label, tk.Frame, tk.Button)):
                    child.config(bg='#4a4a4a')
            
            # Faire défiler pour que l'élément soit visible
            self.playlist_canvas.yview_moveto(item_frame.winfo_y() / self.playlist_container.winfo_height())

    
    def _remove_playlist_item(self, filepath, frame):
        """Supprime un élément de la playlist"""
        try:
            # Trouver l'index de l'élément à supprimer
            index = self.playlist.index(filepath)
            
            # Supprimer de la liste
            self.playlist.pop(index)
            
            # Supprimer de l'affichage
            frame.destroy()
            
            
            # Mettre à jour l'index courant si nécessaire
            if index < self.current_index:
                self.current_index -= 1
            elif index == self.current_index:
                pygame.mixer.music.stop()
                self.current_index = min(index, len(self.playlist) - 1)
                if len(self.playlist) > 0:
                    self.play_track()
            
            self.status_bar.config(text=f"Piste supprimée")
        except ValueError:
            pass
        except Exception as e:
            self.status_bar.config(text=f"Erreur suppression: {e}")
    
    def _load_image_thumbnail(self, image_path, label):
        """Charge une image normale comme thumbnail"""
        try:
            img = Image.open(image_path)
            img.thumbnail((80, 45), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label.configure(image=photo)
            label.image = photo
        except Exception as e:
            print(f"Erreur chargement image thumbnail: {e}")
            # Fallback à une icône par défaut
            default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
            photo = ImageTk.PhotoImage(default_icon)
            label.configure(image=photo)
            label.image = photo

    def _load_mp3_thumbnail(self, filepath, label):
        """Charge la cover art depuis un MP3 ou une thumbnail externe"""
        try:
            # D'abord vérifier s'il existe une thumbnail externe (pour les vidéos YouTube)
            base_path = os.path.splitext(filepath)[0]
            for ext in ['.jpg', '.png', '.webp']:
                thumbnail_path = base_path + ext
                if os.path.exists(thumbnail_path):
                    self._load_image_thumbnail(thumbnail_path, label)
                    return
            
            # # Sinon, essayer de charger depuis les tags ID3
            # if filepath.lower().endswith('.mp3'):
            #     from mutagen.mp3 import MP3
            #     from mutagen.id3 import ID3
            #     audio = MP3(filepath, ID3=ID3)
            #     if 'APIC:' in audio.tags:
            #         apic = audio.tags['APIC:'].data
            #         img = Image.open(io.BytesIO(apic))
            #         img.thumbnail((80, 45), Image.Resampling.LANCZOS)
            #         photo = ImageTk.PhotoImage(img)
            #         label.configure(image=photo)
            #         label.image = photo
            #         return
            
            # Fallback à une icône par défaut
            default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
            photo = ImageTk.PhotoImage(default_icon)
            label.configure(image=photo)
            label.image = photo
            
        except Exception as e:
            print(f"Erreur chargement thumbnail MP3: {e}")
            # Fallback à une icône par défaut
            default_icon = Image.new('RGB', (80, 45), color='#3d3d3d')
            photo = ImageTk.PhotoImage(default_icon)
            label.configure(image=photo)
            label.image = photo

    def _play_playlist_item(self, filepath):
        """Joue un élément de la playlist"""
        try:
            self.current_index = self.playlist.index(filepath)
            self.play_track()
        except ValueError:
            pass

    def play_track(self):
        try:
            song = self.playlist[self.current_index]
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(start=0)
            self.base_position = 0
            pygame.mixer.music.set_volume(self.volume)
            
            self.paused = False
            self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")
            
            # Mettre en surbrillance la piste courante
            self.select_playlist_item(index=self.current_index)
            
            # Update info
            audio = MP3(song)
            self.song_length = audio.info.length
            self.progress.config(to=self.song_length)
            self.song_length_label.config(text=time.strftime(
                '%M:%S', time.gmtime(self.song_length))
            )
            
            self.song_label.config(text=os.path.basename(song))
            self.status_bar.config(text="Playing")
            
            self.generate_waveform_preview(song)

        except Exception as e:
            self.status_bar.config(text=f"Erreur: {str(e)}")

    def _on_mousewheel(self, event, canvas):
        """Gère le défilement avec la molette de souris"""
        if event.delta:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            # Pour Linux qui utilise event.num au lieu de event.delta
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
    
    # def search_youtube(self):
    #     query = self.youtube_entry.get()
    #     self.youtube_results.delete(0, tk.END)
    #     with YoutubeDL(self.ydl_opts) as ydl:
    #         try:
    #             results = ydl.extract_info(f"ytsearch2:{query}", download=False)['entries']
    #             self.search_list = results
    #             for video in results:
    #                 self.youtube_results.insert(tk.END, video.get('title'))
    #             self.status_bar.config(text=f"{len(results)} résultats trouvés")
    #         except Exception as e:
    #             self.status_bar.config(text=f"Erreur recherche: {e}")
    
    def search_youtube(self):
        if self.is_searching:
            return
        
        # Effacer les résultats précédents
        # self.youtube_results.delete(0, tk.END)
        self._clear_results()  # Utilisez la méthode qui vide le container
        self.search_list = []
        self.status_bar.config(text="Recherche en cours...")
        self.root.update()  # Forcer la mise à jour de l'interface
        
        query = self.youtube_entry.get()
        if not query:
            return
            
        self.is_searching = True
        # self.youtube_results.delete(0, tk.END)
        self._clear_results()  # Utilisez la méthode qui vide le container
        self.status_bar.config(text="Recherche en cours...")
        
        # Lancer la recherche dans un thread séparé
        threading.Thread(target=self._perform_search, args=(query,), daemon=True).start()


    def _perform_search(self, query):
        try:
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
                'max_downloads': 10,
                'ignoreerrors': True
            }
            
            with YoutubeDL(search_opts) as ydl:
                results = ydl.extract_info(f"ytsearch10:{query}", download=False)
                
                if not results or 'entries' not in results:
                    self.root.after(0, lambda: self.status_bar.config(text="Aucun résultat trouvé"))
                    return
                    
                # Nettoyer le container avant d'ajouter de nouveaux résultats
                self.root.after(0, self._clear_results)
                
                # Filtrer pour ne garder que les vidéos (pas les playlists/chaines)
                video_results = [
                    entry for entry in results['entries']
                    if "https://www.youtube.com/watch?v=" in entry.get('url')  # Seulement les vidéos
                    and entry.get('duration',0) <= 600.0  # Durée max de 10 minutes
                ]
                
                # Afficher les résultats
                for i, video in enumerate(video_results):
                    self.root.after(0, lambda v=video, idx=i: self._add_search_result(v, idx))
                    
                self.root.after(0, lambda: self.status_bar.config(
                    text=f"{len(video_results)} vidéos trouvées"
                ))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_bar.config(text=f"Erreur recherche: {e}"))
        finally:
            self.is_searching = False

    def _clear_results(self):
        """Vide le container de résultats"""
        for widget in self.results_container.winfo_children():
            widget.destroy()
        self.youtube_canvas.yview_moveto(0)  # Remet le scroll en haut

    # def _add_search_result(self, video, index):
    #     """Ajoute un résultat à la liste et scroll si nécessaire"""
    #     title = video.get('title', 'Sans titre')
    #     self.youtube_results.insert(tk.END, title)
        
    #     # Faire défiler vers le bas si c'est un des derniers résultats
    #     if index >= 5:
    #         self.youtube_results.see(tk.END)
    
    def _add_search_result(self, video, index):
        """Ajoute un résultat avec thumbnail"""
        try:
            title = video.get('title', 'Sans titre')
            duration = video.get('duration', 0)
            
            
            # Créer un frame pour chaque résultat
            result_frame = ttk.Frame(
                self.results_container,
                style='TFrame'
            )
            video['search_frame'] = result_frame
            result_frame.pack(fill="x", padx=5, pady=2)
            
            # Label pour la miniature (vide au début)
            thumbnail_label = tk.Label(
                result_frame,
                bg='#3d3d3d',
                width=80,
                height=45
            )
            thumbnail_label.pack(side="left")
            
            # Frame pour le texte
            text_frame = ttk.Frame(result_frame)
            text_frame.pack(side="left", fill="x", expand=True)
            
            # Titre
            title_label = tk.Label(
                text_frame,
                text=title,
                bg='#3d3d3d',
                fg='white',
                anchor='w',
                justify='left'
            )
            title_label.pack(fill="x")
            
            # Durée
            duration_label = tk.Label(
                text_frame,
                text=time.strftime('%M:%S', time.gmtime(duration)),
                bg='#3d3d3d',
                fg='#aaaaaa',
                anchor='w'
            )
            duration_label.pack(fill="x")
            
            
            
            # Configurer le style pour le survol
            # duration_label.bind("<Enter>", lambda e, f=result_frame: f.configure(style='Hover.TFrame'))
            # duration_label.bind("<Leave>", lambda e, f=result_frame: f.configure(style='TFrame'))
            # title_label.bind("<Enter>", lambda e, f=result_frame: f.configure(style='Hover.TFrame'))
            # title_label.bind("<Leave>", lambda e, f=result_frame: f.configure(style='TFrame'))
            # thumbnail_label.bind("<Enter>", lambda e, f=result_frame: f.configure(style='Hover.TFrame'))
            # thumbnail_label.bind("<Leave>", lambda e, f=result_frame: f.configure(style='TFrame'))
            
            
            
            
            # Stocker la référence à la vidéo
            result_frame.video_data = video
            result_frame.title_label = title_label
            result_frame.duration_label = duration_label
            
            duration_label.bind("<Double-1>", lambda e, f=result_frame: self._on_result_click(f))
            title_label.bind("<Double-1>", lambda e, f=result_frame: self._on_result_click(f))
            thumbnail_label.bind("<Double-1>", lambda e, f=result_frame: self._on_result_click(f))
            # result_frame.bind("<Double-1>", lambda e, f=result_frame: self._on_result_click(f))
            
            # Charger la miniature en arrière-plan
            if video.get('thumbnails'):
                threading.Thread(
                    target=self._load_thumbnail,
                    args=(thumbnail_label, video['thumbnails'][1]['url']) if len(video['thumbnails']) > 1 else (thumbnail_label, video['thumbnails'][0]['url']),
                    daemon=True
                ).start()
            
            # Configurer le style en fonction de l'état de téléchargement
            # url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            # if url in self.current_downloads:
            #     print(url, "en Dl")
            #     result_frame.configure(style='Downloading.TFrame')
            #     title_label.config(fg='#aaaaaa')  # Texte grisé
            #     duration_label.config(fg='#888888')
                
        except Exception as e:
            print(f"Erreur affichage résultat: {e}")
    
    def _on_result_click(self, frame):
        video = frame.video_data
        # Configurer le style en fonction de l'état de téléchargement
        url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
        if url in self.current_downloads:
            print(url, "en Dl")
            frame.configure(style='Downloading.TFrame')
            frame.title_label.config(fg='#aaaaaa')  # Texte grisé
            frame.duration_label.config(fg='#888888')
        
        """Gère le clic sur un résultat"""
        if hasattr(frame, 'video_data'):
            self.search_list = [frame.video_data]  # Pour la compatibilité avec download_selected_youtube
            frame.video_data['search_frame'] = frame
            try:
                self.download_selected_youtube(None)
            except Exception as e:
                frame.configure(style='ErrorDownloading.TFrame')
            frame.configure(style='Downloading.TFrame')
    
    def _download_youtube_thumbnail(self, video_info, filepath):
        """Télécharge la thumbnail YouTube et l'associe au fichier audio"""
        try:
            if not video_info.get('thumbnails'):
                return
                
            # Prendre la meilleure qualité disponible
            thumbnail_url = video_info['thumbnails'][-1]['url']
            
            import requests
            from io import BytesIO
            
            response = requests.get(thumbnail_url, timeout=5)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            
            # Sauvegarder la thumbnail dans le même dossier que l'audio
            thumbnail_path = os.path.splitext(filepath)[0] + ".jpg"
            img.save(thumbnail_path)
            
            return thumbnail_path
            
        except Exception as e:
            print(f"Erreur téléchargement thumbnail: {e}")
            return None


    def download_selected_youtube(self, event=None):
        if not self.search_list:
            return
        
        video = self.search_list[0]
        url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
        
        # Vérifier si cette URL est déjà en cours de téléchargement
        if url in self.current_downloads:
            self.status_bar.config(text="Ce téléchargement est déjà en cours")
            return
        
        # Créer un thread pour le téléchargement
        download_thread = threading.Thread(
            target=self._download_youtube_thread,
            args=(url,),  # Passer l'URL en argument
            daemon=True
        )
        download_thread.start()

    def _download_youtube_thread(self, url):
        try:
            video = self.search_list[0]
            title = video['title']
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            
            # Ajouter l'URL aux téléchargements en cours
            self.current_downloads.add(url)
            print(self.current_downloads, "current _download_youtube_thread")
            self._update_search_results_ui()
            

            # Vérifier si le fichier existe déjà
            existing_file = self._get_existing_download(title)
            if existing_file:
                # Trouver la thumbnail correspondante
                base_path = os.path.splitext(existing_file)[0]
                thumbnail_path = None
                for ext in ['.jpg', '.png', '.webp']:
                    possible_thumb = base_path + ext
                    if os.path.exists(possible_thumb):
                        thumbnail_path = possible_thumb
                        break
                
                self.root.after(0, lambda: self._add_downloaded_file(existing_file, thumbnail_path, title))
                self.root.after(0, lambda: self.status_bar.config(text=f"Fichier existant trouvé: {title}"))
                video['search_frame'].configure(style='TFrame')  # Remettre le style normal
                self.current_downloads.remove(url)  # Retirer de la liste quand terminé
                self._update_search_results_ui()
                return
                
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
            
            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, lambda: self.status_bar.config(text=f"Téléchargement de {safe_title}..."))
            
            downloads_dir = os.path.abspath("downloads")
            if not os.path.exists(downloads_dir):
                try:
                    os.makedirs(downloads_dir)
                except Exception as e:
                    self.root.after(0, lambda: self.status_bar.config(text=f"Erreur création dossier: {str(e)}"))
                    return

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(downloads_dir, f'{safe_title}.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'writethumbnail': True,
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._download_progress_hook],
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                print("downloaded_file", downloaded_file)
                final_path = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3').replace('.mp4', '.mp3')
                if not final_path.endswith('.mp3'):
                    final_path += '.mp3'
                
                thumbnail_path = os.path.splitext(final_path)[0] + ".jpg"
                if os.path.exists(downloaded_file + ".jpg"):
                    os.rename(downloaded_file + ".jpg", thumbnail_path)
                
                # Mettre à jour l'interface dans le thread principal
                self.root.after(0, lambda: self._add_downloaded_file(final_path, thumbnail_path, safe_title))
                video['search_frame'].configure(style='TFrame')  # Remettre le style normal
        
        except Exception as e:
            self.root.after(0, lambda e=e: self.status_bar.config(text=f"Erreur: {str(e)}"))
            if 'search_frame' in video:
                video['search_frame'].configure(style='ErrorDownloading.TFrame')
        finally:
            # S'assurer que l'URL est retirée même en cas d'erreur
            if url in self.current_downloads:
                self.current_downloads.remove(url)
                self._update_search_results_ui()
                

    def _download_progress_hook(self, d):
        """Hook pour afficher la progression du téléchargement"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '?')
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Téléchargement... {percent} à {speed}"
            ))

    def _add_downloaded_file(self, filepath, thumbnail_path, title):
        """Ajoute le fichier téléchargé à la playlist (à appeler dans le thread principal)"""
        # Vérifier si le fichier est déjà dans la playlist
        if filepath not in self.playlist:
            self.playlist.append(filepath)
            self._add_playlist_item(filepath, thumbnail_path)
            self.status_bar.config(text=f"{title} ajouté à la playlist")
        else:
            self.status_bar.config(text=f"{title} est déjà dans la playlist")

    def _load_thumbnail(self, label, url):
        """Charge et affiche la miniature"""
        try:
            import requests
            from io import BytesIO
            
            response = requests.get(url, timeout=5)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img.thumbnail((80, 45), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.root.after(0, lambda: self._display_thumbnail(label, photo))
        except Exception as e:
            print(f"Erreur chargement thumbnail: {e}")

    def _display_thumbnail(self, label, photo):
        """Affiche la miniature dans le label"""
        label.configure(image=photo)
        label.image = photo  # Garder une référence
    
    
    def _get_existing_download(self, title):
        """Vérifie si un fichier existe déjà dans downloads avec un titre similaire"""
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
        downloads_dir = os.path.abspath("downloads")
        
        if not os.path.exists(downloads_dir):
            return None
        
        # Chercher les fichiers correspondants
        for filename in os.listdir(downloads_dir):
            # Comparer les noms normalisés (sans extension et caractères spéciaux)
            base_name = os.path.splitext(filename)[0]
            normalized_base = "".join(c for c in base_name if c.isalnum() or c in " -_")
            
            if normalized_base.startswith(safe_title[:20]) or safe_title.startswith(normalized_base[:20]):
                filepath = os.path.join(downloads_dir, filename)
                # Vérifier que c'est bien un fichier audio
                if filepath.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                    return filepath
        return None

    def _update_search_results_ui(self):
        """Met à jour l'apparence des résultats en fonction de l'état de téléchargement"""
        for child in self.results_container.winfo_children():
            if hasattr(child, 'video_data'):
                video = child.video_data
                url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
                
                if url in self.current_downloads:
                    child.configure(style='Downloading.TFrame')
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Label):
                            subchild.config(fg='#aaaaaa')
                else:
                    child.configure(style='TFrame')
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Label):
                            subchild.config(fg='white')

    def generate_waveform_preview(self, filepath, resolution=5000):
        try:
            audio = AudioSegment.from_file(filepath)
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)

            samples = samples[::len(samples)//resolution or 1]
            self.waveform_data = samples / max(abs(samples).max(), 1)  # Normalisé
        except Exception as e:
            self.status_bar.config(text=f"Erreur waveform preview: {e}")
            self.waveform_data = None
    
    def play_pause(self):
        if not self.playlist:
            return
            
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_button.config(image=self.icons["play"])
            self.play_button.config(text="Play")
        elif self.paused:
            # pygame.mixer.music.unpause()
            pygame.mixer.music.play(start=self.current_time)
            self.base_position = self.current_time
            self.paused = False
            self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")

        else:
            self.paused = False
            self.play_button.config(image=self.icons["pause"])
            self.play_button.config(text="Pause")
            self.play_track()
    
    # def play_track(self):
    #     try:
    #         song = self.playlist[self.current_index]
    #         pygame.mixer.music.load(song)
    #         pygame.mixer.music.play(start=0)
    #         self.base_position = 0
    #         pygame.mixer.music.set_volume(self.volume)
            
    #         # Update info
    #         audio = MP3(song)
    #         self.song_length = audio.info.length
    #         self.progress.config(to=self.song_length)
    #         self.song_length_label.config(text=time.strftime(
    #             '%M:%S', time.gmtime(self.song_length)
    #         )
    #         )
            
    #         self.song_label.config(text=os.path.basename(song))
    #         self.play_button.config(text="Pause")
    #         self.paused = False
    #         self.status_bar.config(text="Playing")
            
    #         # Highlight current track
    #         self.playlist_box.selection_clear(0, tk.END)
    #         self.playlist_box.selection_set(self.current_index)
    #         self.playlist_box.activate(self.current_index)
            
    #         self.generate_waveform_preview(song)

    #     except Exception as e:
    #         self.status_bar.config(text=f"Erreur: {str(e)}")


    def play_selected(self, event):
        if self.playlist_box.curselection():
            self.current_index = self.playlist_box.curselection()[0]
            self.play_track()
    
    def prev_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_track()

    def next_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_track()
    
    
    def show_waveform_on_clicked(self):
        self.show_waveform_current = not self.show_waveform_current

        if self.show_waveform_current:
            self.draw_waveform_around(self.current_time)
            self.show_waveform_btn.config(bg="#4a8fe7", activebackground="#4a8fe7")
        else:
            self.waveform_canvas.delete("all")
            self.show_waveform_btn.config(bg="#3d3d3d", activebackground="#4a4a4a")

    def draw_waveform_around(self, time_sec, window_sec=5):
        if self.waveform_data is None:
            return

        total_length = self.song_length
        if total_length == 0:
            return

        center_index = int((time_sec / total_length) * len(self.waveform_data))
        half_window = int((window_sec / total_length) * len(self.waveform_data)) // 2

        start = max(0, center_index - half_window)
        end = min(len(self.waveform_data), center_index + half_window)

        display_data = self.waveform_data[start:end]
        self.waveform_canvas.delete("all")
        width = self.waveform_canvas.winfo_width()
        height = self.waveform_canvas.winfo_height()
        mid = height // 2
        scale = height // 2

        step = width / len(display_data) if len(display_data) > 0 else 1
        
        ## version segments verticaux
        for i, val in enumerate(display_data):
            x = i * step
            y = val * scale
            self.waveform_canvas.create_line(x, mid - y, x, mid + y, fill="#66ccff")
        
        ## version interpolation linéaire
        # points = []
        # for i, val in enumerate(display_data):
        #     x = i * step
        #     y = mid - val * scale
        #     points.append((x, y))

        # for i in range(1, len(points)):
        #     x1, y1 = points[i - 1]
        #     x2, y2 = points[i]
        #     self.waveform_canvas.create_line(x1, y1, x2, y2, fill="#66ccff", width=1)


        self.waveform_canvas.create_line(
            width // 2, 0, width // 2, height, fill="#ff4444", width=2
        )

    
    def load_icons(self):

        icon_names = {
            "add": "add.png",
            "prev": "prev.png",
            "play": "play.png",
            "next": "next.png",
            "hey": "hey.png",
            "pause": "pause.png",
            "delete": "delete.png"
        }

        # Chemin absolu vers le dossier assets
        base_path = os.path.join(os.path.dirname(__file__), "assets")

        self.icons = {}
        for key, filename in icon_names.items():
            try:
                path = os.path.join(base_path, filename)
                image = Image.open(path).resize((32, 32), Image.Resampling.LANCZOS)
                self.icons[key] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Erreur chargement {filename}: {e}")
        
    
    def set_volume(self, val):
        self.volume = float(val) / 100
        pygame.mixer.music.set_volume(self.volume)
    
    def on_progress_press(self, event):
        self.user_dragging = True
        self.drag_start_time = self.current_time
    
    def on_progress_drag(self, event):
        if self.user_dragging:
            pos = self.progress.get()  # En secondes
            self.current_time_label.config(
                text=time.strftime('%M:%S', time.gmtime(pos))
            )
            self.draw_waveform_around(pos)

    def on_progress_release(self, event):
        # Récupère la valeur actuelle de la progress bar
        pos = self.progress.get()
        # Change la position de la musique (en secondes)
        try:
            if not self.paused:
                pygame.mixer.music.play(start=pos)
            pygame.mixer.music.set_volume(self.volume)
            self.current_time = pos
            
            if self.show_waveform_current:
                self.draw_waveform_around(self.current_time)
            else:
                self.waveform_canvas.delete("all")
                
            self.user_dragging = False
            # self.base_position = pos
        except Exception as e:
            self.status_bar.config(text=f"Erreur position: {e}")
        
        
    
    # def set_position(self, val):
    #     return
    #     if pygame.mixer.music.get_busy() and not self.paused:
    #         pygame.mixer.music.set_pos(float(val))
    #         self.current_time = float(val)
    
    def set_position(self, val):
        pos = float(val)
        self.base_position = pos
        if self.user_dragging:
            return
        try:
            pygame.mixer.music.play(start=pos)
            self.play_button.config(image=self.icons["pause"], text="Pause")
        except Exception as e:
            self.status_bar.config(text=f"Erreur set_pos: {e}")
        
            
    
    def update_time(self):
        while True:
            if pygame.mixer.music.get_busy() and not self.paused and not self.user_dragging:
                self.current_time = self.base_position + pygame.mixer.music.get_pos() / 1000
                
                if self.current_time > self.song_length:
                    self.current_time = self.song_length
                    self.next_track()
                # pygame retourne -1 si la musique est finie, donc on filtre
                if self.current_time < 0:
                    self.current_time = 0
                self.progress.config(value=self.current_time)
                self.current_time_label.config(
                    text=time.strftime('%M:%S', time.gmtime(self.current_time))
                )
                
                if self.show_waveform_current:
                    self.draw_waveform_around(self.current_time)
            self.root.update()
            time.sleep(0.05)
            # print(self.current_time)
    
    def on_closing(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    player = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", player.on_closing)
    root.mainloop()