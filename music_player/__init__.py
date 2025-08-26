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
# import Pmw
import customtkinter as ctk
import re
import json

from config import *
from utils import tooltip
from drag_drop_handler import DragDropHandler

from utils import setup
import file_services
import inputs
from utils import tools
import library_tab.playlists
import control
import player
import search_tab.results
import library_tab.downloads
import services.downloading
import search_tab.main_playlist
import ui_menus
import stats
import artist_tab
import artist_tab.core
import artist_tab.songs
import artist_tab.releases
import artist_tab.playlists
import downloads_tab
import file_tracker
import recommendation
import loader
import search_tab.sliding_panel
import subtitles
import update_window


# Imports communs pour le music player
# import pygame
# import os
# import tkinter as tk
# from tkinter import filedialog, ttk, simpledialog, messagebox
# from mutagen.mp3 import MP3
# import time
# import threading
# from pydub import AudioSegment
# import numpy as np
# from PIL import Image, ImageTk
# from yt_dlp import YoutubeDL
# import math
# import requests
# import io
# import webbrowser
# import Pmw
# import customtkinter as ctk
# import re
# import json

# # Imports relatifs au package
# from .config import *
# from .utils import tooltip, setup, tools
# from .drag_drop_handler import DragDropHandler

# from . import file_services, inputs, control, player, ui_menus, stats
# from . import downloads_tab, file_tracker, recommendation, loader, subtitles, update_window

# # Sous-packages
# from . import library_tab
# from .library_tab import playlists as _lt_playlists, downloads as _lt_downloads  # charge les sous-modules
# from . import search_tab
# from .search_tab import results as _st_results, main_playlist as _st_main_playlist, sliding_panel as _st_sliding_panel
# from . import artist_tab
# from .artist_tab import core as _at_core, songs as _at_songs, releases as _at_releases, playlists as _at_playlists
# from . import services
# from .services import downloading as _svc_downloading

# Remarque:
# - On importe les packages (ex: library_tab, search_tab, artist_tab) pour que
#   les chemins "library_tab.playlists" etc. restent accessibles comme avant.
# - Les imports "as _xxx" servent juste à forcer le chargement des sous-modules;
#   ils restent accessibles via library_tab.playlists, search_tab.main_playlist, etc.
