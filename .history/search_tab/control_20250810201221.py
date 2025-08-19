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

def generate_waveform_preview(self, filepath):
    """Génère les données audio brutes pour la waveform (sans sous-échantillonnage)"""
    try:
        audio = AudioSegment.from_file(filepath)
        samples = np.array(audio.get_array_of_samples())
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)

        # Stocker les données brutes normalisées (sans sous-échantillonnage)
        self.waveform_data_raw = samples / max(abs(samples).max(), 1)
        self.waveform_data = None  # Sera calculé dynamiquement
    except Exception as e:
        self.status_bar.config(text=f"Erreur waveform preview: {e}")
        self.waveform_data_raw = None
        self.waveform_data = None

def get_adaptive_waveform_data(self, canvas_width=None):
    """Génère des données waveform adaptées à la durée de la musique"""
    if self.waveform_data_raw is None:
        return None
        
    # Calculer la résolution basée sur la durée de la musique
    # Plus la musique est longue, plus on a besoin de résolution pour voir les détails
    if self.song_length > 0:
        # 100 échantillons par seconde de musique (résolution fixe)
        target_resolution = int(self.song_length * 100)
        # Limiter entre 1000 et 20000 échantillons pour des performances raisonnables
        target_resolution = max(20000, min(1000, target_resolution))
    else:
        target_resolution = 1000  # Valeur par défaut
    
    # Sous-échantillonner les données brutes
    if len(self.waveform_data_raw) > target_resolution:
        step = len(self.waveform_data_raw) // target_resolution
        return self.waveform_data_raw[::step]
    else:
        return self.waveform_data_raw

def play_pause(self):
    if not self.main_playlist:
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

def play_selected(self, event):
    if self.playlist_box.curselection():
        self.current_index = self.playlist_box.curselection()[0]
        self.play_track()

def prev_track(self):
    if not self.main_playlist:
        return
    self.current_index = (self.current_index - 1) % len(self.main_playlist)
    self.play_track()

def next_track(self):
    if not self.main_playlist:
        return
    
    # Mode loop chanson : rejouer la même chanson
    if self.loop_mode == 2:
        self.play_track()
        return
    
    # Si on est à la dernière chanson et que le mode loop playlist n'est pas activé
    if self.current_index >= len(self.main_playlist) - 1 and self.loop_mode != 1:
        # Arrêter la lecture
        pygame.mixer.music.stop()
        self.status_bar.config(text="Fin de la playlist")
        return
    
    # Passer à la chanson suivante (avec boucle playlist si mode loop playlist activé)
    self.current_index = (self.current_index + 1) % len(self.main_playlist)
    self.play_track()

def show_waveform_on_clicked(self):
    self.show_waveform_current = not self.show_waveform_current

    if self.show_waveform_current:
        self.waveform_canvas.config(height=80)
        self.waveform_canvas.pack(fill=tk.X, pady=(0, 10))
        self.draw_waveform_around(self.current_time)
        self.show_waveform_btn.config(bg="#4a8fe7", activebackground="#4a8fe7")
    else:
        self.waveform_canvas.delete("all")
        self.waveform_canvas.config(height=0)
        self.waveform_canvas.pack(fill=tk.X, pady=0)
        self.show_waveform_btn.config(bg="#3d3d3d", activebackground="#4a4a4a")

def draw_waveform_around(self, time_sec, window_sec=5):
    if self.waveform_data_raw is None:
        return
    
    print(self.waveform_data_raw, 'debug')

    total_length = self.song_length
    if total_length == 0:
        return

    # Générer les données adaptées à la durée de la musique (résolution fixe)
    adaptive_data = self.get_adaptive_waveform_data()
    if adaptive_data is None:
        return

    center_index = int((time_sec / total_length) * len(adaptive_data))
    half_window = int((window_sec / total_length) * len(adaptive_data)) // 2

    start = max(0, center_index - half_window)
    end = min(len(adaptive_data), center_index + half_window)

    display_data = adaptive_data[start:end]
    self.waveform_canvas.delete("all")
    width = self.waveform_canvas.winfo_width()
    height = self.waveform_canvas.winfo_height()
    
    # Si le canvas n'a pas encore de largeur valide, on attend
    if width <= 1:
        self.waveform_canvas.update_idletasks()
        width = self.waveform_canvas.winfo_width()
    
    # Si toujours pas de largeur valide, on utilise une valeur par défaut
    if width <= 1:
        width = 600  # largeur par défaut
        
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


    # Calculer la position exacte du trait rouge dans la fenêtre
    # time_sec est la position actuelle, on calcule sa position relative dans la fenêtre affichée
    if total_length > 0:
        # Position relative de time_sec dans la fenêtre affichée
        window_start_time = (start / len(adaptive_data)) * total_length
        window_end_time = (end / len(adaptive_data)) * total_length
        window_duration = window_end_time - window_start_time
        
        if window_duration > 0:
            relative_pos = (time_sec - window_start_time) / window_duration
            red_line_x = relative_pos * width
            # S'assurer que la ligne reste dans les limites du canvas
            red_line_x = max(0, min(width, red_line_x))
        else:
            red_line_x = width // 2
    else:
        red_line_x = width // 2
    
    
    
    self.waveform_canvas.create_line(
        red_line_x, 0, red_line_x, height, fill="#ff4444", width=2
    )

def on_progress_press(self, event):
    if not self.main_playlist:
        return
    self.user_dragging = True
    self.drag_start_time = self.current_time
    # Remember if waveform was already visible before clicking/dragging
    self.waveform_was_visible = self.show_waveform_current
    # Show waveform for any interaction with progress bar (click or drag)
    if not self.show_waveform_current:
        self.show_waveform_current = True
        self.waveform_canvas.config(height=80)
        self.waveform_canvas.pack(fill=tk.X, pady=(0, 10))
        # Force canvas update before drawing
        self.waveform_canvas.update_idletasks()
        # Draw waveform at current position for immediate feedback
        pos = self.progress.get()
        self.draw_waveform_around(pos)

def on_progress_drag(self, event):
    if not self.main_playlist:
        return
    if self.user_dragging:
        pos = self.progress.get()  # En secondes
        self.current_time_label.config(
            text=time.strftime('%M:%S', time.gmtime(pos))
        )
        self.draw_waveform_around(pos)

def on_progress_release(self, event):
    if not self.main_playlist:
        return
    # Récupère la valeur actuelle de la progress bar
    pos = self.progress.get()
    # Change la position de la musique (en secondes)
    try:
        if not self.paused:
            pygame.mixer.music.play(start=pos)
        pygame.mixer.music.set_volume(self.volume)
        self.current_time = pos
        self.base_position = pos  # Important : mettre à jour la position de base
        
        # Hide waveform if it wasn't visible before dragging
        if not self.waveform_was_visible:
            self.show_waveform_current = False
            # Don't delete the waveform content, just hide the canvas
            self.waveform_canvas.config(height=0)
            self.waveform_canvas.pack(fill=tk.X, pady=0)
        else:
            # Keep waveform visible and update it
            self.draw_waveform_around(self.current_time)
            
        self.user_dragging = False
        # self.base_position = pos
    except Exception as e:
        self.status_bar.config(text=f"Erreur position: {e}")

def on_waveform_canvas_resize(self, event):
    """Appelé quand le canvas waveform change de taille (désactivé car fenêtre non redimensionnable)"""
    # Fonction désactivée car la fenêtre n'est plus redimensionnable
    # et la résolution de la waveform ne dépend plus de la taille du canvas
    pass

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