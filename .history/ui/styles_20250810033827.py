"""
Styles et thèmes de l'interface utilisateur
"""
from tkinter import ttk
from config.constants import *


class StyleManager:
    """Gestionnaire des styles de l'interface"""
    
    def __init__(self):
        self.style = ttk.Style()
        self.setup_styles()
    
    def setup_styles(self):
        """Configure tous les styles de l'application"""
        self.style.theme_use('clam')
        
        # Styles de base
        self._setup_base_styles()
        
        # Styles des boutons
        self._setup_button_styles()
        
        # Styles des onglets
        self._setup_notebook_styles()
        
        # Styles spéciaux
        self._setup_special_styles()
    
    def _setup_base_styles(self):
        """Configure les styles de base"""
        self.style.configure('TFrame', background=COLOR_BACKGROUND)
        self.style.configure('TLabel', 
                           background=COLOR_BACKGROUND, 
                           foreground='white')
        self.style.configure('TScale', background=COLOR_BACKGROUND)
    
    def _setup_button_styles(self):
        """Configure les styles des boutons"""
        # Style de base des boutons
        self.style.configure('TButton',
                           background=COLOR_BUTTON,
                           foreground='white',
                           borderwidth=0,
                           focusthickness=0,
                           padding=6)
        
        # Effets hover et focus
        self.style.map('TButton',
                      background=[('active', COLOR_BUTTON_HOVER), 
                                ('!active', COLOR_BUTTON)],
                      relief=[('pressed', 'flat'), ('!pressed', 'flat')],
                      focuscolor=[('focus', '')])
    
    def _setup_notebook_styles(self):
        """Configure les styles des onglets"""
        self.style.configure('TNotebook', 
                           background=COLOR_BACKGROUND, 
                           borderwidth=0)
        
        self.style.configure('TNotebook.Tab',
                           background=COLOR_BUTTON,
                           foreground='white',
                           padding=[10, 5],
                           borderwidth=0)
        
        self.style.map('TNotebook.Tab',
                      background=[('selected', COLOR_TAB_SELECTED), 
                                ('!selected', COLOR_BUTTON)],
                      foreground=[('selected', 'white'), 
                                ('!selected', 'white')])
    
    def _setup_special_styles(self):
        """Configure les styles spéciaux"""
        # Style pour les téléchargements en cours
        self.style.configure('Downloading.TFrame', 
                           background=COLOR_DOWNLOADING)
        self.style.map('Downloading.TFrame',
                      background=[('active', COLOR_DOWNLOADING_HOVER)])
        
        # Style pour les erreurs de téléchargement
        self.style.configure('ErrorDownloading.TFrame', 
                           background=COLOR_ERROR)
    
    def get_button_style(self, style_type="default"):
        """Retourne un dictionnaire de style pour les boutons tk"""
        styles = {
            "default": {
                'bg': COLOR_BUTTON,
                'fg': 'white',
                'activebackground': COLOR_BUTTON_HOVER,
                'activeforeground': 'white',
                'relief': 'flat',
                'bd': 0,
                'highlightthickness': 0
            },
            "selected": {
                'bg': COLOR_SELECTED,
                'fg': 'white',
                'activebackground': COLOR_BUTTON_HOVER,
                'activeforeground': 'white',
                'relief': 'flat',
                'bd': 0,
                'highlightthickness': 0
            },
            "tab": {
                'bg': COLOR_TAB_SELECTED,
                'fg': 'white',
                'activebackground': COLOR_BUTTON_HOVER,
                'activeforeground': 'white',
                'relief': 'flat',
                'bd': 0,
                'highlightthickness': 0
            }
        }
        
        return styles.get(style_type, styles["default"])
    
    def get_frame_style(self):
        """Retourne un dictionnaire de style pour les frames tk"""
        return {
            'bg': COLOR_BACKGROUND,
            'highlightthickness': 0
        }
    
    def get_canvas_style(self):
        """Retourne un dictionnaire de style pour les canvas"""
        return {
            'bg': COLOR_BUTTON,
            'highlightthickness': 0
        }
    
    def get_label_style(self, style_type="default"):
        """Retourne un dictionnaire de style pour les labels"""
        styles = {
            "default": {
                'bg': COLOR_BACKGROUND,
                'fg': 'white'
            },
            "title": {
                'bg': COLOR_BACKGROUND,
                'fg': 'white',
                'font': ('TkDefaultFont', 12, 'bold')
            },
            "subtitle": {
                'bg': COLOR_BACKGROUND,
                'fg': '#cccccc',
                'font': ('TkDefaultFont', 10)
            }
        }
        
        return styles.get(style_type, styles["default"])
    
    def apply_hover_effect(self, widget, enter_color=None, leave_color=None):
        """Applique un effet de survol à un widget"""
        if enter_color is None:
            enter_color = COLOR_BUTTON_HOVER
        if leave_color is None:
            leave_color = COLOR_BUTTON
        
        def on_enter(event):
            widget.configure(bg=enter_color)
        
        def on_leave(event):
            widget.configure(bg=leave_color)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)