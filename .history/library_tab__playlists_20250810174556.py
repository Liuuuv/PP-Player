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

def _display_playlists(self):
    """Affiche toutes les playlists en grille 3x3"""
    # Vider le container actuel
    for widget in self.playlists_container.winfo_children():
        widget.destroy()
    
    # Organiser les playlists en lignes de 3 (exclure la main playlist)
    playlist_items = [(name, songs) for name, songs in self.playlists.items() if name != "Main Playlist"]
    
    for row in range(0, len(playlist_items), 2):
        # Créer un frame pour cette ligne
        row_frame = tk.Frame(self.playlists_container, bg='#3d3d3d')
        row_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Configurer les colonnes pour qu'elles soient égales
        for col in range(2):
            row_frame.columnconfigure(col, weight=1, uniform="playlist_col")
        
        # Ajouter jusqu'à 2 playlists dans cette ligne
        for col in range(2):
            playlist_index = row + col
            if playlist_index < len(playlist_items):
                playlist_name, songs = playlist_items[playlist_index]
                self._add_playlist_card(row_frame, playlist_name, songs, col)