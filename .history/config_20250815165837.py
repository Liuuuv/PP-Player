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


# GEOMETRY = "800x700"
GEOMETRY = "1200x800"


TEST_COLOR = "#9000ff"

## MUSIC DISPLAY
COLOR_SELECTED = '#5a9fd8'
COLOR_BACKGROUND = '#4a4a4a'
COLOR_BACKGROUND_HIGHLIGHT = '#5a5a5a'
COLOR_ERROR = "#ffc72d"  # Couleur d'erreur orange-jaune utilisée partout
COLOR_DOWNLOAD = '#ff6666'

# autour de la carte principale (réduit pour 4 playlists par ligne)
CARD_FRAME_PADX = 5
CARD_FRAME_PADY = 2


DISPLAY_PLAYLIST_PADX = 5
DISPLAY_PLAYLIST_PADY = 2


# Paramètres de recherche déplacés vers search_tab/config.py
# Voir search_tab/config.py pour tous les paramètres de recherche YouTube

VIRTUALISATION_THRESHOLD = 10  # nombre d'éléments à partir duquel la virtualisation s'active

QUEUE_LINE_WIDTH = 5
QUEUE_LINE_PADX = (0, 2)
QUEUE_LINE_PADY = 0

COLOR_ARTIST_NAME = "#dcdcdc"
COLOR_METADATAS = "#dadada"
COLOR_TEXT = '#cccccc'


HOVER_LIGHT_PERCENTAGE = 0.1  # 10% plus clair

COLORDRAG_RIGHT_HALF = "#424f45"
COLORDRAG_RIGHT = '#4a6a4a'
COLORDRAG_LEFT_HALF = "#525248"
COLORDRAG_LEFT = '#6a6a4a'

# Configuration des recommandations
RECOMMENDATION_SPARSE_MIN_SONGS = 2  # Minimum de chansons avant d'ajouter une recommandation en mode éparse
RECOMMENDATION_SPARSE_MAX_SONGS = 4  # Maximum de chansons avant d'ajouter une recommandation en mode éparse
RECOMMENDATION_ADD_BATCH_SIZE = 2    # Nombre de recommandations à ajouter par batch en mode "add"
RECOMMENDATION_ADD_MAX_LIMIT = 6     # Limite maximale de recommandations en mode "add"