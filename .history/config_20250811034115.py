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

## OPTIMISATIONS DE RECHERCHE
# Paramètres de performance pour éviter les saccades
SEARCH_OPTIMIZATION = {
    # Threads de miniatures
    'max_thumbnail_threads': 2,  # Nombre max de threads pour charger les miniatures (1-5)
    
    # Affichage des résultats
    'fast_display_mode': True,  # True = affichage par lots, False = progressif
    'progressive_delay_ms': 30,  # Délai entre chaque résultat en mode progressif (10-100ms)
    'thumbnail_load_delay_ms': 200,  # Délai avant chargement des miniatures (0-500ms)
    
    # Recherche YouTube
    'max_search_results': 15,  # Nombre max de résultats par recherche (10-30)
    'search_delay_ms': 300,  # Délai avant lancement de la recherche (100-1000ms)
    'results_per_page': 10,  # Résultats par page/lot (5-15)
    
    # Scroll et interface
    'scroll_check_interval_ms': 200,  # Fréquence de vérification du scroll (100-500ms)
    'use_low_priority_threads': True,  # Réduire la priorité des threads de miniatures
    
    # Modes prédéfinis
    'performance_mode': 'balanced',  # 'performance', 'balanced', 'quality'
}

# Modes prédéfinis
PERFORMANCE_MODES = {
    'performance': {  # Mode haute performance - minimum de saccades
        'max_thumbnail_threads': 1,
        'fast_display_mode': True,
        'progressive_delay_ms': 10,
        'thumbnail_load_delay_ms': 300,
        'max_search_results': 10,
        'search_delay_ms': 500,
        'results_per_page': 5,
        'scroll_check_interval_ms': 300,
        'use_low_priority_threads': True,
    },
    'balanced': {  # Mode équilibré - bon compromis
        'max_thumbnail_threads': 2,
        'fast_display_mode': True,
        'progressive_delay_ms': 30,
        'thumbnail_load_delay_ms': 200,
        'max_search_results': 15,
        'search_delay_ms': 300,
        'results_per_page': 10,
        'scroll_check_interval_ms': 200,
        'use_low_priority_threads': True,
    },
    'quality': {  # Mode qualité - plus de résultats, plus fluide
        'max_thumbnail_threads': 3,
        'fast_display_mode': False,
        'progressive_delay_ms': 50,
        'thumbnail_load_delay_ms': 100,
        'max_search_results': 20,
        'search_delay_ms': 200,
        'results_per_page': 10,
        'scroll_check_interval_ms': 150,
        'use_low_priority_threads': False,
    }
}