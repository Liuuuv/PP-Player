"""
Méthodes de création d'interface pour Pipi Player
Extrait de main.py pour améliorer la lisibilité
"""

def create_ui(self):
    """Crée l'interface utilisateur principale"""
    from tkinter import ttk
    import tkinter as tk
    
    # Configuration des styles
    _setup_styles()
    
    # Main Frame
    self.main_frame = ttk.Frame(self.root)
    self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Contrôles de lecture (créés en premier pour être toujours visibles en bas)
    self.setup_controls()
    
    # Création du Notebook (onglets) - prend l'espace restant
    self.notebook = ttk.Notebook(self.main_frame)
    self.notebook.pack(fill=tk.BOTH, expand=True)
    
    # Frame pour l'onglet Recherche
    self.search_tab = ttk.Frame(self.notebook)
    self.notebook.add(self.search_tab, text="Recherche")
    
    # Frame pour l'onglet Bibliothèque
    self.library_tab = ttk.Frame(self.notebook)
    self.notebook.add(self.library_tab, text="Bibliothèque")
    
    # Contenu des onglets
    self.setup_search_tab()
    self.setup_library_tab()
    
    # Lier le changement d'onglet à une fonction
    self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    # Ajouter des bindings pour retirer le focus des champs de saisie
    self.setup_focus_bindings()

def _setup_styles(self):
    """Configure les styles de l'interface"""
    from tkinter import ttk
    
    # Style de base
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background='#2d2d2d')
    style.configure('TLabel', background='#2d2d2d', foreground='white')
    style.configure('TButton', background='#3d3d3d', foreground='white')
    style.configure('TScale', background='#2d2d2d')
    
    # Style des boutons
    style.configure('TButton',
        background='#3d3d3d',
        foreground='white',
        borderwidth=0,
        focusthickness=0,
        padding=6
    )
    
    # Effets hover
    style.map('TButton',
        background=[('active', '#4a4a4a'), ('!active', '#3d3d3d')],
        relief=[('pressed', 'flat'), ('!pressed', 'flat')],
        focuscolor=[('focus', '')]
    )
    
    # Styles spéciaux
    style.configure('Downloading.TFrame', background='#ff4444')
    style.map('Downloading.TFrame', background=[('active', '#ff6666')])
    style.configure('ErrorDownloading.TFrame', background="#ffcc00")
    
    # Configuration des onglets
    style.configure('TNotebook', background='#2d2d2d', borderwidth=0)
    style.configure('TNotebook.Tab', 
                background='#3d3d3d', 
                foreground='white',
                padding=[10, 5],
                borderwidth=0)
    style.map('TNotebook.Tab',
            background=[('selected', '#4a8fe7'), ('!selected', '#3d3d3d')],
            foreground=[('selected', 'white'), ('!selected', 'white')])

def on_tab_changed(self, event):
    """Gère le changement d'onglet"""
    # Logique pour gérer le changement d'onglet
    pass

def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
    """Colorie les frames TTK pour le debug (optionnel)"""
    import random
    from tkinter import ttk
    
    if isinstance(widget, ttk.Frame):
        color = random.choice(colors)
        widget.configure(relief="solid", borderwidth=2)
        # Note: TTK ne supporte pas directement les couleurs de bordure
    
    for child in widget.winfo_children():
        self.colorize_ttk_frames(child, colors)