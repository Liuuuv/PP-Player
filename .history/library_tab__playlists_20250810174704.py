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


def _add_playlist_card(self, parent_frame, playlist_name, songs, column):
    """Ajoute une carte de playlist avec miniatures"""
    try:
        # Frame principal pour la carte de playlist
        card_frame = tk.Frame(
            parent_frame,
            bg='#4a4a4a',
            relief='flat',
            bd=1,
            highlightbackground='#5a5a5a',
            highlightthickness=1
        )
        card_frame.grid(row=0, column=column, sticky='nsew', padx=10, pady=5)
        
        # Configuration de la grille de la carte
        card_frame.columnconfigure(0, weight=1)
        card_frame.rowconfigure(0, weight=1)  # Zone des miniatures
        card_frame.rowconfigure(1, weight=0)  # Titre
        card_frame.rowconfigure(2, weight=0)  # Nombre de chansons
        card_frame.rowconfigure(3, weight=0)  # Boutons
        
        # 1. Zone des miniatures (2x2 grid) - taille fixe pour uniformité
        thumbnails_frame = tk.Frame(card_frame, bg='#4a4a4a', width=220, height=220)
        thumbnails_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        thumbnails_frame.grid_propagate(False)  # Maintenir la taille fixe
        
        # Configurer la grille 2x2 pour les miniatures
        for i in range(2):
            thumbnails_frame.columnconfigure(i, weight=1)
            thumbnails_frame.rowconfigure(i, weight=1)
        
        # Ajouter les 4 premières miniatures (ou moins si pas assez de chansons)
        for i in range(4):
            row = i // 2
            col = i % 2
            
            thumbnail_label = tk.Label(
                thumbnails_frame,
                bg='#3d3d3d',
                relief='flat'
            )
            thumbnail_label.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
            
            # Charger la miniature si la chanson existe
            if i < len(songs):
                self._load_playlist_thumbnail_large(songs[i], thumbnail_label)
            else:
                # Miniature vide
                thumbnail_label.config(text="♪", fg='#666666', font=('TkDefaultFont', 20))
        
        # 2. Titre de la playlist
        title_label = tk.Label(
            card_frame,
            text=playlist_name,
            bg='#4a4a4a',
            fg='white',
            font=('TkDefaultFont', 11, 'bold'),
            anchor='center'
        )
        title_label.grid(row=1, column=0, sticky='ew', padx=10, pady=(5, 2))
        
        # 3. Nombre de chansons
        count_label = tk.Label(
            card_frame,
            text=f"{len(songs)} titres",
            bg='#4a4a4a',
            fg='#cccccc',
            font=('TkDefaultFont', 9),
            anchor='center'
        )
        count_label.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 5))
        
        # 4. Boutons
        buttons_frame = tk.Frame(card_frame, bg='#4a4a4a')
        buttons_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=(0, 5))
        
        # Bouton renommer - icône complète
        rename_btn = tk.Button(
            buttons_frame,
            image=self.icons["rename"],
            command=lambda name=playlist_name: self._rename_playlist_dialog(name),
            bg="#ffa500",
            fg="white",
            activebackground="#ffb733",
            relief="flat",
            bd=0,
            width=self.icons["rename"].width(),
            height=self.icons["rename"].height(),
        )
        rename_btn.pack(side=tk.LEFT, padx=2)
        
        # Bouton supprimer - icône complète
        delete_btn = tk.Button(
            buttons_frame,
            image=self.icons["delete"],
            bg="#ff4444",
            fg="white",
            activebackground="#ff6666",
            relief="flat",
            bd=0,
            width=self.icons["delete"].width(),
            height=self.icons["delete"].height(),
        )
        delete_btn.pack(side=tk.RIGHT, padx=2)
        
        # Double-clic pour supprimer
        delete_btn.bind("<Double-1>", lambda e, name=playlist_name: self._delete_playlist_dialog(name))
        
        # Double-clic pour voir le contenu de la playlist
        def on_playlist_double_click():
            self._show_playlist_content_in_tab(playlist_name)
        
        card_frame.bind("<Double-1>", lambda e: on_playlist_double_click())
        thumbnails_frame.bind("<Double-1>", lambda e: on_playlist_double_click())
        title_label.bind("<Double-1>", lambda e: on_playlist_double_click())
        count_label.bind("<Double-1>", lambda e: on_playlist_double_click())
        
    except Exception as e:
        print(f"Erreur affichage playlist card: {e}")

def _load_playlist_thumbnail_large(self, filepath, label):
    """Charge une miniature carrée plus grande pour une chanson dans une playlist"""
    try:
        # Chercher une image associée (même nom mais extension image)
        base_name = os.path.splitext(filepath)[0]
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        thumbnail_found = False
        for ext in image_extensions:
            thumbnail_path = base_name + ext
            if os.path.exists(thumbnail_path):
                # Charger l'image
                image = Image.open(thumbnail_path)
                
                # Créer une image carrée en cropant au centre
                width, height = image.size
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                right = left + size
                bottom = top + size
                
                # Crop au centre pour faire un carré
                img_cropped = image.crop((left, top, right, bottom))
                
                # Redimensionner à une taille plus grande (100x100)
                img_resized = img_cropped.resize((100, 100), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img_resized)
                label.configure(image=photo, text="")
                label.image = photo
                thumbnail_found = True
                break
        
        if not thumbnail_found:
            # Utiliser une icône par défaut plus grande
            label.config(text="♪", fg='#666666', font=('TkDefaultFont', 20))
            
    except Exception as e:
        print(f"Erreur chargement thumbnail playlist: {e}")
        label.config(text="♪", fg='#666666', font=('TkDefaultFont', 20))