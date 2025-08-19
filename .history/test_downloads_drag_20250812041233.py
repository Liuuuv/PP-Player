#!/usr/bin/env python3
"""
Script de test pour vérifier les bindings de drag dans les téléchargements
"""

import sys
import os
import tkinter as tk

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from drag_drop_handler import DragDropHandler

class TestDownloadsDrag:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Drag Downloads")
        self.root.geometry("600x200")
        
        # Simuler les attributs nécessaires du music player
        self.main_playlist = []
        self.current_index = 0
        self.queue_items = set()
        self.current_downloads = set()
        self.pending_queue_additions = {}
        self.pending_play_after_current = {}
        self.pending_queue_first_additions = {}
        
        # Créer le gestionnaire de drag and drop
        self.drag_drop_handler = DragDropHandler(self)
        
        # Simuler la structure d'un élément de téléchargement
        self.create_download_item()
        
        # Status bar pour les messages
        self.status_bar = tk.Label(self.root, text="Testez le drag sur tous les éléments", bg='lightgray')
        self.status_bar.pack(fill='x', side='bottom')
        
    def create_download_item(self):
        """Crée un élément de téléchargement de test avec tous les widgets"""
        # Frame principal
        item_frame = tk.Frame(self.root, bg='#4a4a4a', height=60)
        item_frame.pack(fill='x', padx=10, pady=10)
        item_frame.grid_propagate(False)
        item_frame.columnconfigure(2, weight=1)
        
        # Numéro
        number_label = tk.Label(item_frame, text="1", bg='#4a4a4a', fg='white', width=3)
        number_label.grid(row=0, column=0, sticky='nsew', padx=(5, 2), pady=5)
        
        # Miniature
        thumbnail_label = tk.Label(item_frame, text="🎵", bg='#4a4a4a', fg='white', width=10, height=3)
        thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(5, 4), pady=5)
        
        # Frame de texte
        text_frame = tk.Frame(item_frame, bg='#4a4a4a')
        text_frame.grid(row=0, column=2, sticky='nsew', padx=(0, 2), pady=4)
        text_frame.columnconfigure(0, weight=1)
        
        # Titre
        title_label = tk.Label(
            text_frame, 
            text="Test Song - Drag depuis n'importe où!", 
            bg='#4a4a4a', 
            fg='white',
            anchor='nw'
        )
        title_label.grid(row=0, column=0, sticky='ew', pady=(2, 0))
        
        # Métadonnées
        metadata_label = tk.Label(
            text_frame, 
            text="Test Artist • Test Album", 
            bg='#4a4a4a', 
            fg='#cccccc',
            anchor='nw'
        )
        metadata_label.grid(row=1, column=0, sticky='ew', pady=(0, 2))
        
        # Durée
        duration_label = tk.Label(item_frame, text="3:45", bg='#4a4a4a', fg='white', width=8)
        duration_label.grid(row=0, column=3, sticky='nsew', padx=(2, 5), pady=5)
        
        # Bouton supprimer
        delete_btn = tk.Button(item_frame, text="🗑", bg='#666666', fg='white', width=3)
        delete_btn.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
        
        # Handlers de drag
        def on_left_button_press(event):
            self.drag_drop_handler.setup_drag_start(event, item_frame)
            widget_name = event.widget.__class__.__name__
            widget_text = getattr(event.widget, 'text', 'N/A')[:20]
            self.status_bar.config(text=f"Drag initialisé depuis: {widget_name} ('{widget_text}')")
            print(f"Drag initialisé depuis: {widget_name} - {widget_text}")
        
        def on_right_button_press(event):
            self.drag_drop_handler.setup_drag_start(event, item_frame)
            widget_name = event.widget.__class__.__name__
            widget_text = getattr(event.widget, 'text', 'N/A')[:20]
            self.status_bar.config(text=f"Drag droit initialisé depuis: {widget_name} ('{widget_text}')")
            print(f"Drag droit initialisé depuis: {widget_name} - {widget_text}")
        
        def on_double_click(event):
            widget_name = event.widget.__class__.__name__
            self.status_bar.config(text=f"Double-clic sur: {widget_name}")
        
        # Bindings pour tous les widgets (comme dans downloads.py)
        widgets_to_bind = [
            item_frame, text_frame, title_label, metadata_label, 
            thumbnail_label, duration_label, number_label
        ]
        
        for widget in widgets_to_bind:
            widget.bind("<ButtonPress-1>", on_left_button_press)
            widget.bind("<Double-1>", on_double_click)
            widget.bind("<ButtonPress-3>", on_right_button_press)
        
        # Configuration du drag-and-drop
        self.drag_drop_handler.setup_drag_drop(
            item_frame, 
            file_path="test_song.mp3", 
            item_type="file"
        )
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Instructions: Cliquez et draggez depuis n'importe quel élément (numéro, miniature, titre, métadonnées, durée)\nDrag vers la droite (>100px) ou vers la gauche (<-100px) pour tester",
            justify='center',
            bg='white',
            wraplength=580
        )
        instructions.pack(fill='x', padx=10, pady=5)
        
    def _set_item_colors(self, frame, color):
        """Méthode simulée pour changer les couleurs"""
        try:
            frame.config(bg=color)
            for child in frame.winfo_children():
                if hasattr(child, 'config'):
                    child.config(bg=color)
        except:
            pass
    
    def _refresh_playlist_display(self):
        """Méthode simulée pour rafraîchir l'affichage"""
        print("Rafraîchissement de l'affichage simulé")
    
    def run(self):
        print("Test du drag dans les téléchargements - Fenêtre ouverte")
        print("Essayez de dragger depuis tous les éléments!")
        self.root.mainloop()

if __name__ == "__main__":
    test = TestDownloadsDrag()
    test.run()