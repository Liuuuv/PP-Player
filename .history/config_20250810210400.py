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


GEOMETRY = "800x700"


TEST_COLOR = '#ff0000'

## MUSIC DISPLAY
COLOR_SELECTED = '#5a9fd8'
COLOR_BACKGROUND = '#4a4a4a'