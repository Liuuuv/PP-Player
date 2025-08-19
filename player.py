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

def _play_after_current(self, filepath):
    """Place une musique juste après celle qui joue actuellement et la lance"""
    try:
        # Ajouter à la main playlist si pas déjà présent
        self.add_to_main_playlist(filepath, show_status=False)
        
        # Si une musique joue actuellement
        if len(self.main_playlist) > 0 and self.current_index < len(self.main_playlist):
            # Trouver l'index de la musique à déplacer
            song_index = self.main_playlist.index(filepath)
            
            # Si la musique n'est pas déjà juste après la chanson en cours
            target_position = self.current_index + 1
            
            if song_index != target_position:
                # Retirer la musique de sa position actuelle
                self.main_playlist.pop(song_index)
                
                # Ajuster l'index cible si nécessaire
                if song_index < self.current_index:
                    target_position = self.current_index  # L'index actuel a diminué de 1
                
                # Insérer à la nouvelle position
                self.main_playlist.insert(target_position, filepath)
            
            # Passer à cette musique
            self.current_index = target_position
            self.play_track()
            
            # Mettre à jour l'affichage de la playlist
            self._refresh_main_playlist_display()
            
            self.status_bar.config(text=f"Lecture de: {os.path.basename(filepath)}")
        else:
            # Aucune musique en cours, juste jouer cette musique
            self.current_index = self.main_playlist.index(filepath)
            self.play_track()
            self._refresh_main_playlist_display()
            self.status_bar.config(text=f"Lecture de: {os.path.basename(filepath)}")

    except Exception as e:
        self.status_bar.config(text=f"Erreur lors de la lecture")

def _play_playlist_item(self, filepath):
        """Joue un élément de la playlist"""
        try:
            self.current_index = self.main_playlist.index(filepath)
            self.play_track()
        except ValueError:
            pass