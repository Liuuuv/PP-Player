# Imports communs pour le module artist_tab
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
import artist_tab.core

# Importer create_tooltip
from tooltip import create_tooltip

# Importer toutes les variables de config globales
from config import *

# Importer la configuration spécifique au module artist_tab
from . import config as artist_config

# Importer les sous-modules artist_tab pour faciliter l'accès
from . import core, songs, releases, playlists, utils

# Fonctions utilitaires pour l'accès externe
def get_artist_tab_core():
    """Retourne le module core d'artist_tab"""
    return core

def get_artist_tab_songs():
    """Retourne le module songs d'artist_tab"""
    return songs

def get_artist_tab_releases():
    """Retourne le module releases d'artist_tab"""
    return releases

def get_artist_tab_playlists():
    """Retourne le module playlists d'artist_tab"""
    return playlists