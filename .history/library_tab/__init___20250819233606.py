# Imports communs pour le module library_tab
import sys
import os

# Ajouter le répertoire parent au path pour permettre les imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer tous les modules nécessaires
import pygame
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
from mutagen.mp3 import MP3
import time
import threading
from pydub import AudioSegment
import numpy as np
from PIL import Image, ImageTk
from yt_dlp import YoutubeDL

# Importer les modules du projet
import config
import setup
import file_services
import inputs
import tools
import control

# Importer create_tooltip
from tooltip import create_tooltip

# Importer toutes les variables de config
from config import *

CONFIG = {
    'load_more_count':10,
    'enable_smart_loading': True,
    'debug_scroll': True,
    'enable_dynamic_scroll': True,
    'enable_smart_loading': True,
    'enable_dynamic_scroll': True,
}

def get_config(key):
    return CONFIG.get(key)