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

def show_playlists_content(self):
                """Affiche le contenu de l'onglet playlists"""
                
                # Frame pour les boutons de gestion
                management_frame = ttk.Frame(self.library_content_frame)
                management_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
                
                # Bouton créer nouvelle playlist
                create_btn = tk.Button(
                    management_frame,
                    # text="➕",
                    image=self.icons["add"],
                    command=lambda: self._create_new_playlist_dialog(),
                    bg='#4d4d4d',
                    fg="white",
                    activebackground="#5a9fd8",
                    relief="flat",
                    bd=0,
                    padx=15,
                    pady=8,
                    font=('TkDefaultFont', 14)
                )
                create_btn.pack(side=tk.LEFT, padx=(0, 10))
                
                # Canvas avec scrollbar pour les playlists
                self.playlists_canvas = tk.Canvas(
                    self.library_content_frame,
                    bg='#3d3d3d',
                    highlightthickness=0
                )
                self.playlists_scrollbar = ttk.Scrollbar(
                    self.library_content_frame,
                    orient="vertical",
                    command=self.playlists_canvas.yview
                )
                self.playlists_canvas.configure(yscrollcommand=self.playlists_scrollbar.set)
                
                self.playlists_scrollbar.pack(side="right", fill="y")
                self.playlists_canvas.pack(side="left", fill="both", expand=True)
                
                self.playlists_container = ttk.Frame(self.playlists_canvas)
                self.playlists_canvas.create_window((0, 0), window=self.playlists_container, anchor="nw")
                
                self.playlists_container.bind(
                    "<Configure>",
                    lambda e: self.playlists_canvas.configure(
                        scrollregion=self.playlists_canvas.bbox("all")
                    )
                )
                
                self._bind_mousewheel(self.playlists_canvas, self.playlists_canvas)
                self._bind_mousewheel(self.playlists_container, self.playlists_canvas)
                
                # Charger et afficher les playlists
                self._display_playlists()