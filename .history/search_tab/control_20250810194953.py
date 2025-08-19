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