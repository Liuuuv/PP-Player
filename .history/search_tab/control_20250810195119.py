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