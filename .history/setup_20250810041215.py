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