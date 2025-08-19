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


def _play_from_playlist(self, filepath, playlist_name):
    """Joue une musique depuis une playlist spécifique"""
    # Ajouter à la main playlist si pas déjà présent
    self.add_to_main_playlist(filepath, show_status=False)
    
    # Jouer la musique
    self.current_index = self.main_playlist.index(filepath)
    self.play_track()

