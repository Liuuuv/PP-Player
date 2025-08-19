#!/usr/bin/env python3
"""
Script de test pour vérifier le fonctionnement du drag and drop
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from drag_drop_handler import DragDropHandler
import tkinter as tk

class TestDragDrop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Drag & Drop")
        self.root.geometry("400x300")
        
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
        
        # Créer un frame de test
        self.test_frame = tk.Frame(self.root, bg='#4a4a4a', height=50)
        self.test_frame.pack(fill='x', padx=10, pady=10)
        
        # Ajouter un label
        self.test_label = tk.Label(
            self.test_frame, 
            text="Test Item - Drag moi vers la droite ou la gauche!", 
            bg='#4a4a4a', 
            fg='white'
        )
        self.test_label.pack(expand=True, fill='both')
        
        # Configurer le drag and drop
        self.drag_drop_handler.setup_drag_drop(
            self.test_frame,
            file_path="test_file.mp3",
            item_type="file"
        )
        
        # Handler de clic pour initialiser le drag
        def on_click(event):
            self.drag_drop_handler.setup_drag_start(event, self.test_frame)
            print("Drag initialisé - vous pouvez maintenant dragger!")
        
        self.test_frame.bind("<ButtonPress-1>", on_click)
        self.test_frame.bind("<ButtonPress-3>", on_click)
        self.test_label.bind("<ButtonPress-1>", on_click)
        self.test_label.bind("<ButtonPress-3>", on_click)
        
        # Ajouter des instructions
        instructions = tk.Label(
            self.root,
            text="Instructions:\n1. Cliquez sur l'élément de test\n2. Maintenez et draggez vers la droite (>100px) ou vers la gauche (<-100px)\n3. Relâchez pour tester l'action",
            justify='left',
            bg='white'
        )
        instructions.pack(fill='x', padx=10, pady=10)
        
        # Status bar pour les messages
        self.status_bar = tk.Label(self.root, text="Prêt pour le test", bg='lightgray')
        self.status_bar.pack(fill='x', side='bottom')
        
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
        print("Test du drag and drop - Fenêtre ouverte")
        print("Essayez de dragger l'élément de test!")
        self.root.mainloop()

if __name__ == "__main__":
    test = TestDragDrop()
    test.run()