"""
Imports et constantes pour Pipi Player
Extrait de main.py pour améliorer la lisibilité
"""

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
# from pytube import Search

# Constantes de couleurs
COLOR_SELECTED = '#5a9fd8'
COLOR_BACKGROUND = '#2d2d2d'
COLOR_BUTTON = '#3d3d3d'
COLOR_BUTTON_HOVER = '#4a4a4a'
COLOR_TAB_SELECTED = '#4a8fe7'
COLOR_DOWNLOADING = '#ff4444'
COLOR_DOWNLOADING_HOVER = '#ff6666'
COLOR_ERROR = '#ffcc00'

# Constantes de l'application
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
AUDIO_EXTENSIONS = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
DOWNLOADS_DIR = "downloads"
ASSETS_DIR = "assets"

# Configuration YouTube-DL
YDL_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'external_downloader': 'ffmpeg',
}