import pygame
import os
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
from mutagen.mp3 import MP3
import time
import threading
import numpy as np
from PIL import Image, ImageTk
from yt_dlp import YoutubeDL


class FileServices:
    def __init__(self, music_player):
        self.music_player = music_player

    def _count_downloaded_files(self):
        """Compte les fichiers téléchargés sans les afficher"""
        downloads_dir = self.music_player.downloads_folder
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
            self.music_player.num_downloaded_files = 0
            return
        
        # Extensions audio supportées
        audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')
        
        # Compter les fichiers
        count = 0
        for filename in os.listdir(downloads_dir):
            if filename.lower().endswith(audio_extensions):
                count += 1
        
        self.music_player.num_downloaded_files = count
        