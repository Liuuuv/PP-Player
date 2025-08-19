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



def setup_window_icon(self):
    """Set up the window icon for the main application window."""
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Impossible de charger l'icône: {e}")

def load_icons(self):
    """Load icons for the application from the assets directory."""
    icon_names = {
        "add": "add.png",
        "prev": "prev.png",
        "play": "play.png",
        "next": "next.png",
        "hey": "hey.png",
        "pause": "pause.png",
        "delete": "delete.png",
        "back": "back.png",
        "loop": "loop.png",
        "loop1": "loop1.png",
        "shuffle": "shuffle.png",
        "rename": "rename.png"
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