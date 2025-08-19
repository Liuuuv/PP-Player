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


GEOMETRY = "800x600"


TEST_COLOR = '#ff0000'

## MUSIC DISPLAY
COLOR_SELECTED = '#5a9fd8'
COLOR_BACKGROUND = '#4a4a4a'
COLOR_BACKGROUND_HIGHLIGHT = '#5a5a5a'

# autour de la carte principale
CARD_FRAME_PADX = 10
CARD_FRAME_PADY = 2


DISPLAY_PLAYLIST_PADX = 5
DISPLAY_PLAYLIST_PADY = 2


# MAX_SEARCH_RESULTS = 25
# RESULTS_PER_PAGE = 5
# FAST_DISPLAY_MODE = True
# MAX_THUMBNAIL_THREADS = 2
# SEARCH_DELAY = 300

SEARCH_WAIT_TIME_BETWEEN_RESULTS = 100  # en millisecondes

THUMBNAIL_SIZE = (80, 45)
DEFAULT_CIRC_THUMBNAIL_SIZE = (45, 45)