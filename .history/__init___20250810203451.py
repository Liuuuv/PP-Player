# __init__.py - Centralisation des imports pour le music player

# Imports système
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

# Imports des modules locaux et constantes
from config import *  # Importe GEOMETRY, COLOR_SELECTED, etc.
import setup
import file_services
import inputs
import tools
import library_tab.playlists
import search_tab
import control

# Import des utilitaires
from tooltip import create_tooltip

# Exports pour faciliter l'utilisation
__all__ = [
    # Modules système
    'pygame', 'os', 'tk', 'filedialog', 'ttk', 'simpledialog', 'messagebox',
    'MP3', 'time', 'threading', 'AudioSegment', 'np', 'Image', 'ImageTk', 'YoutubeDL',
    
    # Modules locaux
    'setup', 'file_services', 'inputs', 'tools', 'control',
    'library_tab', 'search_tab',
    
    # Utilitaires
    'create_tooltip'
]