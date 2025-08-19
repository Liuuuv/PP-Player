import pygame
import os
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
from mutagen.mp3 import MP3
import time
import threading
from pydub import AudioSegment
import numpy as np
from PIL import Image, ImageTk
from yt_dlp import YoutubeDL

def on_escape_pressed(self, event):
    """Gère l'appui sur la touche Échap"""
    # Priorité 0: Si on est dans une playlist/sortie ouverte, revenir à la liste
    if hasattr(self, 'artist_mode') and self.artist_mode:
        # Vérifier si on est dans une playlist/sortie ouverte (bouton retour visible)
        if hasattr(self, 'artist_tab_back_btn') and self.artist_tab_back_btn and self.artist_tab_back_btn.winfo_exists():
            # Utiliser la fonction intelligente qui détermine l'action selon l'onglet actuel
            if hasattr(self, 'artist_tab_manager'):
                self.artist_tab_manager.smart_back_action()
            else:
                # Fallback: utiliser le bouton retour
                self.artist_tab_back_btn.invoke()
            return "break"
        else:
            # On est dans la vue principale artiste, quitter complètement
            self._return_to_search()
            return "break"
    
    # Vérifier si le focus est sur le champ de recherche de la bibliothèque
    focused_widget = self.root.focus_get()
    if (focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)) and
        hasattr(self, 'library_search_entry') and focused_widget == self.library_search_entry):
        # Si le champ de recherche contient du texte, le vider
        if self.library_search_entry.get().strip():
            self._clear_library_search()
        else:
            # Si le champ est vide, enlever le focus
            self.root.focus_set()
        return "break"
    
    # Vérifier si le focus est sur un autre champ de saisie
    if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
        # Si le focus est sur un champ de saisie, retirer le focus
        self.root.focus_set()
        return "break"
    
    # Priorité 1: Si on a une sélection multiple active, l'annuler
    if hasattr(self, 'selected_items') and self.selected_items:
        self.clear_selection()
        return "break"
    
    # Priorité 2: Vérifier si on est en mode artiste
    if hasattr(self, 'artist_mode') and self.artist_mode:
        # Si on est en mode artiste, retourner à la recherche normale
        self._return_to_search()
        return "break"
    
    # Priorité 3: Vérifier sur quel onglet on se trouve
    current_tab = self.notebook.tab(self.notebook.select(), "text")
    
    if current_tab == "Recherche":
        # Si on est sur l'onglet recherche, effacer la barre de recherche
        self._clear_youtube_search()
    else:
        # Si on n'est pas sur l'onglet recherche, y revenir
        # Trouver l'index de l'onglet recherche
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "Recherche":
                self.notebook.select(i)
                break
    
    # Empêcher la propagation de l'événement
    return "break"

# def _on_youtube_scroll(self, event):
#     """Gère le scroll de la molette dans les résultats YouTube"""
#     # Scroll normal
    
#     self.youtube_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
#     # Vérifier si on doit charger plus de résultats
#     if self._should_load_more_results():
#         self._load_more_search_results()

def on_space_pressed(self, event):
    """Gère l'appui sur la barre d'espace"""
    # Vérifier si le focus n'est pas sur un champ de saisie
    focused_widget = self.root.focus_get()
    if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
        # Si le focus est sur un champ de saisie, ne pas intercepter la barre d'espace
        return
    
    # Appeler la fonction play_pause (même si le focus est sur une case à cocher)
    self.play_pause()
    
    # Empêcher la propagation de l'événement
    return "break"
def on_closing(self):
    # Mettre à jour les statistiques une dernière fois
    self._update_current_song_stats()
    
    # Arrêter l'animation du titre
    self._stop_title_animation()
    
    # Sauvegarder la configuration avant de fermer
    self.save_config()
    
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    self.root.destroy()

def _on_mousewheel(self, event, canvas):
        """Gère le défilement avec la molette de souris"""
        # Détecter le scroll manuel sur la playlist pour désactiver l'auto-scroll
        if hasattr(self, 'playlist_canvas') and canvas == self.playlist_canvas:
            if hasattr(self, 'auto_scroll_enabled') and self.auto_scroll_enabled:
                self.manual_scroll_detected = True
                self.auto_scroll_enabled = False
                self.auto_scroll_btn.config(bg="#4a4a4a", activebackground="#5a5a5a")
                self.status_bar.config(text="Auto-scroll désactivé (scroll manuel détecté)")
        
        if event.delta:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            # Pour Linux qui utilise event.num au lieu de event.delta
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

# Raccourcis clavier globaux (fonctionnent même quand la fenêtre n'a pas le focus)
def on_global_play_pause(self, event):
    """Raccourci global Ctrl+Alt+P pour play/pause"""
    self.play_pause()
    return "break"

def on_global_next_track(self, event):
    """Raccourci global Ctrl+Alt+N pour chanson suivante"""
    self.next_track()
    return "break"

def on_global_prev_track(self, event):
    """Raccourci global Ctrl+Alt+B pour chanson précédente"""
    self.prev_track()
    return "break"

def on_global_volume_up(self, event):
    """Raccourci global Ctrl+Alt+Up pour augmenter le volume"""
    current_volume = self.volume * 100
    new_volume = min(100, current_volume + 5)  # Augmenter de 5%
    self.volume_slider.set(new_volume)
    self.status_bar.config(text=f"Volume: {int(new_volume)}%")
    return "break"

def on_global_volume_down(self, event):
    """Raccourci global Ctrl+Alt+Down pour diminuer le volume"""
    current_volume = self.volume * 100
    new_volume = max(0, current_volume - 5)  # Diminuer de 5%
    self.volume_slider.set(new_volume)
    self.status_bar.config(text=f"Volume: {int(new_volume)}%")
    return "break"

def show_download_dialog(self):
    """Affiche une boîte de dialogue pour importer des musiques ou playlists"""
    dialog = ImportDialog(self.root, self)
    self.root.wait_window(dialog.dialog)

class ImportDialog:
    def __init__(self, parent, music_player):
        self.music_player = music_player
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Importer des musiques")
        self.dialog.geometry("500x300")
        self.dialog.configure(bg='#2d2d2d')
        self.dialog.resizable(False, False)
        
        # Centrer la fenêtre
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.download_type = tk.StringVar(value="single")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Titre
        title_label = tk.Label(
            self.dialog, 
            text="Télécharger des musiques", 
            font=("Arial", 14, "bold"),
            bg='#2d2d2d', 
            fg='white'
        )
        title_label.pack(pady=10)
        
        # Frame pour les options de type
        type_frame = tk.Frame(self.dialog, bg='#2d2d2d')
        type_frame.pack(pady=10)
        
        tk.Label(type_frame, text="Type de téléchargement:", bg='#2d2d2d', fg='white').pack(anchor='w')
        
        # Radio buttons
        single_radio = tk.Radiobutton(
            type_frame, 
            text="Une seule musique", 
            variable=self.download_type, 
            value="single",
            bg='#2d2d2d', 
            fg='white', 
            selectcolor='#4a4a4a',
            activebackground='#2d2d2d',
            activeforeground='white'
        )
        single_radio.pack(anchor='w', pady=2)
        
        playlist_radio = tk.Radiobutton(
            type_frame, 
            text="Playlist complète", 
            variable=self.download_type, 
            value="playlist",
            bg='#2d2d2d', 
            fg='white', 
            selectcolor='#4a4a4a',
            activebackground='#2d2d2d',
            activeforeground='white'
        )
        playlist_radio.pack(anchor='w', pady=2)
        
        # Frame pour l'URL
        url_frame = tk.Frame(self.dialog, bg='#2d2d2d')
        url_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(url_frame, text="URL YouTube:", bg='#2d2d2d', fg='white').pack(anchor='w')
        
        self.url_entry = tk.Entry(
            url_frame, 
            font=("Arial", 10),
            bg='#4a4a4a', 
            fg='white', 
            insertbackground='white'
        )
        self.url_entry.pack(fill='x', pady=5)
        
        # Frame pour les boutons
        button_frame = tk.Frame(self.dialog, bg='#2d2d2d')
        button_frame.pack(pady=20)
        
        download_btn = tk.Button(
            button_frame,
            text="Télécharger",
            command=self.start_download,
            bg='#4a8fe7',
            fg='white',
            font=("Arial", 10, "bold"),
            relief='flat',
            padx=20,
            pady=5
        )
        download_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Annuler",
            command=self.dialog.destroy,
            bg='#666666',
            fg='white',
            font=("Arial", 10),
            relief='flat',
            padx=20,
            pady=5
        )
        cancel_btn.pack(side='left', padx=10)
        
        # Zone de statut
        self.status_label = tk.Label(
            self.dialog,
            text="Entrez une URL YouTube pour commencer",
            bg='#2d2d2d',
            fg='#cccccc',
            font=("Arial", 9)
        )
        self.status_label.pack(pady=10)
        
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL")
            return
            
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL YouTube valide")
            return
            
        download_type = self.download_type.get()
        
        # Fermer la boîte de dialogue
        self.dialog.destroy()
        
        # Lancer le téléchargement dans un thread séparé
        thread = threading.Thread(
            target=self._download_thread, 
            args=(url, download_type), 
            daemon=True
        )
        thread.start()
        
    def _download_thread(self, url, download_type):
        """Thread de téléchargement"""
        try:
            downloads_dir = os.path.abspath("downloads")
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
                
            if download_type == "single":
                self._download_single_video(url, downloads_dir)
            else:
                self._download_playlist(url, downloads_dir)
                
        except Exception as e:
            self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                text=f"Erreur de téléchargement: {str(e)}"
            ))
            
    def _download_single_video(self, url, downloads_dir):
        """Télécharge une seule vidéo"""
        self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
            text="Téléchargement en cours..."
        ))
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Titre inconnu')
                
            self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                text=f"Téléchargé: {title}"
            ))
            
            # Recharger les fichiers téléchargés
            self.music_player.root.after(0, self.music_player.load_downloaded_files)
            
        except Exception as e:
            self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                text=f"Erreur: {str(e)}"
            ))
            
    def _download_playlist(self, url, downloads_dir):
        """Télécharge une playlist complète"""
        self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
            text="Téléchargement de la playlist en cours..."
        ))
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,  # Télécharger tous les éléments de la playlist
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if 'entries' in info:
                    count = len([entry for entry in info['entries'] if entry])
                    playlist_title = info.get('title', 'Playlist')
                    self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                        text=f"Téléchargé: {count} musiques de '{playlist_title}'"
                    ))
                else:
                    # C'est une seule vidéo, pas une playlist
                    title = info.get('title', 'Titre inconnu')
                    self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                        text=f"Téléchargé: {title}"
                    ))
            
            # Recharger les fichiers téléchargés
            self.music_player.root.after(0, self.music_player.load_downloaded_files)
            
        except Exception as e:
            self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                text=f"Erreur: {str(e)}"
            ))