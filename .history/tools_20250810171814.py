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

def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
        style = ttk.Style()
        color_index = 0

        for child in widget.winfo_children():
            # Si c'est un ttk.Frame → appliquer un style
            if isinstance(child, ttk.Frame):
                style_name = f"Debug.TFrame{color_index}"
                style.layout(style_name, style.layout("TFrame"))
                style.configure(style_name, background=colors[color_index % len(colors)])
                child.configure(style=style_name)
                color_index += 1

            # Si c'est un tk.Frame → appliquer une couleur directement
            elif isinstance(child, tk.Frame):
                child.configure(bg=colors[color_index % len(colors)])
                color_index += 1

            # Récursif sur les enfants
            self.colorize_ttk_frames(child, colors)