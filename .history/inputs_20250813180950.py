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

def on_escape_pressed(self, event):
    """Gère l'appui sur la touche Échap"""
    # Priorité 0: Si on est dans une playlist/sortie ouverte, revenir à la liste
    if hasattr(self, 'artist_mode') and self.artist_mode:
        # Vérifier si on est dans une playlist/sortie ouverte (bouton retour visible)
        if hasattr(self, 'playlist_back_btn') and self.artist_tab_back_btn.winfo_exists():
            # On est dans une playlist/sortie, revenir à la liste
            self.artist_tab_back_btn.invoke()  # Simuler un clic sur le bouton retour
            return "break"
        else:
            # On est dans la vue principale artiste, quitter complètement
            self._return_to_search()
            return "break"
    
    # Vérifier si le focus est sur le champ de recherche de la bibliothèque
    focused_widget = self.root.focus_get()
    if (focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)) and
        hasattr(self, 'library_search_entry') and focused_widget == self.library_search_entry):
        # Si le champ de recherche contient du texte, le vider
        if self.library_search_entry.get().strip():
            self._clear_library_search()
        else:
            # Si le champ est vide, enlever le focus
            self.root.focus_set()
        return "break"
    
    # Vérifier si le focus est sur un autre champ de saisie
    if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
        # Si le focus est sur un champ de saisie, retirer le focus
        self.root.focus_set()
        return "break"
    
    # Priorité 1: Si on a une sélection multiple active, l'annuler
    if hasattr(self, 'selected_items') and self.selected_items:
        self.clear_selection()
        return "break"
    
    # Priorité 2: Vérifier si on est en mode artiste
    if hasattr(self, 'artist_mode') and self.artist_mode:
        # Si on est en mode artiste, retourner à la recherche normale
        self._return_to_search()
        return "break"
    
    # Priorité 3: Vérifier sur quel onglet on se trouve
    current_tab = self.notebook.tab(self.notebook.select(), "text")
    
    if current_tab == "Recherche":
        # Si on est sur l'onglet recherche, effacer la barre de recherche
        self._clear_youtube_search()
    else:
        # Si on n'est pas sur l'onglet recherche, y revenir
        # Trouver l'index de l'onglet recherche
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "Recherche":
                self.notebook.select(i)
                break
    
    # Empêcher la propagation de l'événement
    return "break"

# def _on_youtube_scroll(self, event):
#     """Gère le scroll de la molette dans les résultats YouTube"""
#     # Scroll normal
    
#     self.youtube_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
#     # Vérifier si on doit charger plus de résultats
#     if self._should_load_more_results():
#         self._load_more_search_results()

def on_space_pressed(self, event):
    """Gère l'appui sur la barre d'espace"""
    # Vérifier si le focus n'est pas sur un champ de saisie
    focused_widget = self.root.focus_get()
    if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
        # Si le focus est sur un champ de saisie, ne pas intercepter la barre d'espace
        return
    
    # Appeler la fonction play_pause (même si le focus est sur une case à cocher)
    self.play_pause()
    
    # Empêcher la propagation de l'événement
    return "break"
def on_closing(self):
    # Mettre à jour les statistiques une dernière fois
    self._update_current_song_stats()
    
    # Arrêter l'animation du titre
    self._stop_title_animation()
    
    # Sauvegarder la configuration avant de fermer
    self.save_config()
    
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    self.root.destroy()

def _on_mousewheel(self, event, canvas):
        """Gère le défilement avec la molette de souris"""
        # Détecter le scroll manuel sur la playlist pour désactiver l'auto-scroll
        if hasattr(self, 'playlist_canvas') and canvas == self.playlist_canvas:
            if hasattr(self, 'auto_scroll_enabled') and self.auto_scroll_enabled:
                self.manual_scroll_detected = True
                self.auto_scroll_enabled = False
                self.auto_scroll_btn.config(bg="#4a4a4a", activebackground="#5a5a5a")
                self.status_bar.config(text="Auto-scroll désactivé (scroll manuel détecté)")
        
        if event.delta:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            # Pour Linux qui utilise event.num au lieu de event.delta
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")