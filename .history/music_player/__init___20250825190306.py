# Imports communs pour le music player
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
import math
import requests
import io
import webbrowser
import Pmw
import customtkinter as ctk
import re
import json

from .config import *
from .utils import tooltip
from .drag_drop_handler import DragDropHandler

from .utils import setup
from .utils import tools
from . import file_services, inputs, control, player, ui_menus, stats, downloads_tab, file_tracker, recommendation, loader, subtitles, update_window
from . import library_tab, search_tab, services, artist_tab

# Ensure submodules are loaded and accessible as attributes on their packages
import importlib as _importlib
for _mod in [
    'music_player.library_tab.playlists',
    'music_player.library_tab.downloads',
    'music_player.search_tab.results',
    'music_player.search_tab.main_playlist',
    'music_player.search_tab.sliding_panel',
    'music_player.artist_tab.core',
    'music_player.artist_tab.songs',
    'music_player.artist_tab.releases',
    'music_player.artist_tab.playlists',
    'music_player.services.downloading',
]:
    try:
        _importlib.import_module(_mod)
    except Exception:
        pass

del _importlib