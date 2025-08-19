"""
Fenêtre principale de l'application
"""
import tkinter as tk
from tkinter import ttk
import os
from config.constants import WINDOW_WIDTH, WINDOW_HEIGHT, ASSETS_DIR
from .styles import StyleManager


class MainWindow:
    """Fenêtre principale de l'application"""
    
    def __init__(self, title="Pipi Player"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg='#2d2d2d')
        self.root.option_add("*Button.takeFocus", 0)
        
        # Gestionnaire de styles
        self.style_manager = StyleManager()
        
        # Configurer l'icône
        self._setup_icon()
        
        # Créer l'interface
        self._create_main_frame()
    
    def _setup_icon(self):
        """Configure l'icône de la fenêtre"""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "..", ASSETS_DIR, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Impossible de charger l'icône: {e}")
    
    def _create_main_frame(self):
        """Crée le frame principal"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_notebook(self):
        """Crée le notebook (onglets)"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        return self.notebook
    
    def add_tab(self, tab_frame, text):
        """Ajoute un onglet au notebook"""
        if hasattr(self, 'notebook'):
            self.notebook.add(tab_frame, text=text)
    
    def bind_tab_changed(self, callback):
        """Lie le changement d'onglet à une fonction"""
        if hasattr(self, 'notebook'):
            self.notebook.bind("<<NotebookTabChanged>>", callback)
    
    def get_root(self):
        """Retourne la fenêtre root"""
        return self.root
    
    def get_main_frame(self):
        """Retourne le frame principal"""
        return self.main_frame
    
    def get_style_manager(self):
        """Retourne le gestionnaire de styles"""
        return self.style_manager
    
    def set_close_callback(self, callback):
        """Définit la fonction à appeler à la fermeture"""
        self.root.protocol("WM_DELETE_WINDOW", callback)
    
    def mainloop(self):
        """Lance la boucle principale"""
        self.root.mainloop()
    
    def destroy(self):
        """Détruit la fenêtre"""
        self.root.destroy()