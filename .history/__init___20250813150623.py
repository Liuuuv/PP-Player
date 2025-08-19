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

from config import *
from tooltip import create_tooltip
from drag_drop_handler import DragDropHandler

import setup
import file_services
import inputs
import tools
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
