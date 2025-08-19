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

from config import *
import setup
import file_services
import inputs
import tools
import library_tab.playlists
import control
import search_tab.results

from tooltip import create_tooltip