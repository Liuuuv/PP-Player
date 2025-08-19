import tkinter as tk
from tkinter import ttk

class ToolTip:
    """
    Classe pour créer des tooltips (boîtes de texte d'aide) sur les widgets tkinter
    """
    def __init__(self, widget, text='widget info', delay=500, wraplength=180):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        
        # Bind les événements
        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
        self.widget.bind('<ButtonPress>', self.on_leave)
    
    def on_enter(self, event=None):
        """Appelé quand la souris entre dans le widget"""
        self.schedule()
    
    def on_leave(self, event=None):
        """Appelé quand la souris sort du widget"""
        self.unschedule()
        self.hide_tip()
    
    def schedule(self):
        """Programme l'affichage du tooltip après le délai"""
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show_tip)
    
    def unschedule(self):
        """Annule l'affichage programmé du tooltip"""
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    
    def show_tip(self, event=None):
        """Affiche le tooltip"""
        if self.tipwindow or not self.text:
            return
        
        # Obtenir la position de la souris
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        # Créer la fenêtre tooltip
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Style du tooltip
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"), wraplength=self.wraplength)
        label.pack(ipadx=1)
    
    def hide_tip(self):
        """Cache le tooltip"""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text, delay=500, wraplength=180):
    """
    Fonction utilitaire pour créer facilement un tooltip
    
    Args:
        widget: Le widget sur lequel ajouter le tooltip
        text: Le texte à afficher
        delay: Délai en millisecondes avant l'affichage (défaut: 500)
        wraplength: Largeur maximale du texte avant retour à la ligne (défaut: 180)
    
    Returns:
        L'instance ToolTip créée
    """
    return ToolTip(widget, text, delay, wraplength)