#!/usr/bin/env python3
"""
Test qui reproduit exactement la structure des téléchargements
"""

import sys
import os
import tkinter as tk

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from drag_drop_handler import DragDropHandler

class TestRealStructure:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Structure Réelle")
        self.root.geometry("800x400")
        
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
        
        # Créer plusieurs éléments comme dans downloads.py
        self.create_download_items()
        
        # Status bar pour les messages
        self.status_bar = tk.Label(self.root, text="Testez le drag sur tous les éléments", bg='lightgray')
        self.status_bar.pack(fill='x', side='bottom')
        
    def create_download_items(self):
        """Crée plusieurs éléments de téléchargement comme dans downloads.py"""
        
        # Canvas avec scrollbar comme dans l'app réelle
        canvas = tk.Canvas(self.root, bg='#2d2d2d')
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2d2d2d')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Créer plusieurs éléments de test
        for i in range(5):
            self.create_single_item(scrollable_frame, f"test_song_{i}.mp3", i+1)
    
    def create_single_item(self, parent, filepath, number):
        """Crée un seul élément exactement comme dans downloads.py"""
        
        # Frame principal (exactement comme dans downloads.py)
        item_frame = tk.Frame(parent, bg='#4a4a4a', height=60)
        item_frame.pack(fill='x', padx=10, pady=2)
        item_frame.pack_propagate(False)
        item_frame.grid_propagate(False)
        
        # Configuration des colonnes pour que le texte s'étende
        item_frame.columnconfigure(0, weight=0)  # Numéro - taille fixe
        item_frame.columnconfigure(1, weight=0)  # Miniature - taille fixe  
        item_frame.columnconfigure(2, weight=1)  # Texte - s'étend
        item_frame.columnconfigure(3, weight=0)  # Durée - taille fixe
        item_frame.columnconfigure(4, weight=0)  # Bouton - taille fixe
        
        # Numéro (exactement comme dans downloads.py)
        number_label = tk.Label(item_frame, text=str(number), bg='#4a4a4a', fg='white', width=3)
        number_label.grid(row=0, column=0, sticky='nsew', padx=(5, 2), pady=5)
        
        # Miniature (exactement comme dans downloads.py)
        thumbnail_label = tk.Label(item_frame, text="🎵", bg='#4a4a4a', fg='white', width=10, height=3)
        thumbnail_label.grid(row=0, column=1, sticky='nsew', padx=(5, 4), pady=5)
        
        # Frame de texte (exactement comme dans downloads.py)
        text_frame = tk.Frame(item_frame, bg='#4a4a4a')
        text_frame.grid(row=0, column=2, sticky='nsew', padx=(0, 2), pady=4)
        text_frame.columnconfigure(0, weight=1)
        
        # Titre (exactement comme dans downloads.py)
        title_label = tk.Label(
            text_frame, 
            text=f"Test Song {number} - Drag Test", 
            bg='#4a4a4a', 
            fg='white',
            anchor='nw'
        )
        title_label.grid(row=0, column=0, sticky='ew', pady=(2, 0))
        
        # Métadonnées (exactement comme dans downloads.py)
        metadata_label = tk.Label(
            text_frame, 
            text=f"Test Artist {number} • Test Album", 
            bg='#4a4a4a', 
            fg='#cccccc',
            anchor='nw'
        )
        metadata_label.grid(row=1, column=0, sticky='ew', pady=(0, 2))
        
        # Durée (exactement comme dans downloads.py)
        duration_label = tk.Label(item_frame, text="3:45", bg='#4a4a4a', fg='white', width=8)
        duration_label.grid(row=0, column=3, sticky='nsew', padx=(2, 5), pady=5)
        
        # Bouton supprimer (exactement comme dans downloads.py)
        delete_btn = tk.Button(item_frame, text="🗑", bg='#666666', fg='white', width=3)
        delete_btn.grid(row=0, column=4, sticky='ns', padx=(0, 10), pady=8)
        
        # === HANDLERS EXACTEMENT COMME DANS DOWNLOADS.PY ===
        
        def on_item_click(event):
            print(f"📱 Clic normal sur {event.widget.__class__.__name__}")
        
        def on_item_double_click(event):
            print(f"📱 Double-clic sur {event.widget.__class__.__name__}")
        
        def on_item_right_click(event):
            print(f"📱 Clic droit normal sur {event.widget.__class__.__name__}")
        
        # Gestionnaire pour initialiser le drag sur clic gauche
        def on_left_button_press(event):
            print(f"🟢 CLIC GAUCHE DÉTECTÉ: {event.widget.__class__.__name__} - {getattr(event.widget, 'text', 'N/A')[:20]}")
            # Initialiser le drag pour le clic gauche
            self.drag_drop_handler.setup_drag_start(event, item_frame)
            print(f"   drag_enabled = {getattr(item_frame, 'drag_enabled', 'N/A')}")
            # Appeler aussi le gestionnaire de clic normal
            on_item_click(event)
        
        # Gestionnaire pour initialiser le drag sur clic droit
        def on_right_button_press(event):
            print(f"🟡 CLIC DROIT DÉTECTÉ: {event.widget.__class__.__name__}")
            # Initialiser le drag pour le clic droit
            self.drag_drop_handler.setup_drag_start(event, item_frame)
        
        def on_right_button_press_combined(event):
            # Initialiser le drag pour le clic droit
            on_right_button_press(event)
            # Appeler aussi le gestionnaire de clic droit normal
            on_item_right_click(event)
        
        # === BINDINGS EXACTEMENT COMME DANS DOWNLOADS.PY ===
        item_frame.bind("<ButtonPress-1>", on_left_button_press)
        item_frame.bind("<Double-1>", on_item_double_click)
        item_frame.bind("<ButtonPress-3>", on_right_button_press_combined)
        text_frame.bind("<ButtonPress-1>", on_left_button_press)
        text_frame.bind("<Double-1>", on_item_double_click)
        text_frame.bind("<ButtonPress-3>", on_right_button_press_combined)
        title_label.bind("<ButtonPress-1>", on_left_button_press)
        title_label.bind("<Double-1>", on_item_double_click)
        title_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        metadata_label.bind("<ButtonPress-1>", on_left_button_press)
        metadata_label.bind("<Double-1>", on_item_double_click)
        metadata_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        thumbnail_label.bind("<ButtonPress-1>", on_left_button_press)
        thumbnail_label.bind("<Double-1>", on_item_double_click)
        thumbnail_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        duration_label.bind("<ButtonPress-1>", on_left_button_press)
        duration_label.bind("<Double-1>", on_item_double_click)
        duration_label.bind("<ButtonPress-3>", on_right_button_press_combined)
        delete_btn.bind("<Double-1>", lambda e: print("🗑 Double-clic supprimer"))
        
        # === DRAG AND DROP EXACTEMENT COMME DANS DOWNLOADS.PY ===
        self.drag_drop_handler.setup_drag_drop(item_frame, file_path=filepath, item_type="file")
        
    def _set_item_colors(self, frame, color):
        """Méthode simulée pour changer les couleurs"""
        try:
            frame.config(bg=color)
            for child in frame.winfo_children():
                if hasattr(child, 'config'):
                    child.config(bg=color)
                    # Récursif pour les frames imbriquées
                    if isinstance(child, tk.Frame):
                        for grandchild in child.winfo_children():
                            if hasattr(grandchild, 'config'):
                                grandchild.config(bg=color)
        except:
            pass
    
    def _refresh_playlist_display(self):
        """Méthode simulée pour rafraîchir l'affichage"""
        print("✅ Rafraîchissement de l'affichage simulé")
    
    def run(self):
        print("🚀 Test de la structure réelle - Fenêtre ouverte")
        print("📝 Instructions:")
        print("   1. Essayez de dragger depuis tous les éléments")
        print("   2. Maintenez le bouton enfoncé et bougez la souris")
        print("   3. Drag vers la droite (>100px) ou vers la gauche (<-100px)")
        self.root.mainloop()

if __name__ == "__main__":
    test = TestRealStructure()
    test.run()