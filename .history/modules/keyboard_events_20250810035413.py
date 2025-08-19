"""
Gestion des événements clavier pour Pipi Player
Extrait de main.py pour améliorer la lisibilité
"""

def setup_keyboard_bindings(self):
    """Configure les raccourcis clavier"""
    # Binding pour la barre d'espace (pause/play)
    self.root.bind('<KeyPress-space>', self.on_space_pressed)
    
    # Binding pour retirer le focus des champs de saisie quand on clique ailleurs
    self.root.bind('<Button-1>', self.on_root_click)
    
    # S'assurer que la fenêtre peut recevoir le focus pour les événements clavier
    self.root.focus_set()

def on_space_pressed(self, event):
    """Gère l'appui sur la barre d'espace"""
    import tkinter as tk
    
    # Vérifier si le focus n'est pas sur un champ de saisie
    focused_widget = self.root.focus_get()
    if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
        # Si le focus est sur un champ de saisie, ne pas intercepter la barre d'espace
        return
    
    # Appeler la fonction play_pause
    self.play_pause()
    
    # Empêcher la propagation de l'événement
    return "break"

def on_root_click(self, event):
    """Gère les clics sur la fenêtre principale pour retirer le focus des champs de saisie"""
    import tkinter as tk
    
    # Obtenir le widget qui a été cliqué
    clicked_widget = event.widget
    
    # Si on clique sur un champ de saisie, ne rien faire (laisser le focus)
    if isinstance(clicked_widget, (tk.Entry, tk.Text)):
        return
    
    # Vérifier si on clique sur un parent d'un champ de saisie
    parent = clicked_widget
    while parent:
        if isinstance(parent, (tk.Entry, tk.Text)):
            return
        try:
            parent = parent.master
        except:
            break
    
    # Si on arrive ici, on n'a pas cliqué sur un champ de saisie
    # Retirer le focus de tous les champs de saisie
    focused_widget = self.root.focus_get()
    if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
        self.root.focus_set()  # Donner le focus à la fenêtre principale

def setup_focus_bindings(self):
    """Configure les bindings pour retirer le focus des champs de saisie"""
    import tkinter as tk
    
    def remove_focus(event):
        """Retire le focus des champs de saisie"""
        focused_widget = self.root.focus_get()
        if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
            self.root.focus_set()
    
    # Ajouter le binding sur les éléments principaux
    widgets_to_bind = [
        self.main_frame,
        self.notebook,
        self.search_tab,
        self.library_tab
    ]
    
    for widget in widgets_to_bind:
        if hasattr(self, widget.__class__.__name__.lower()) or widget:
            widget.bind('<Button-1>', remove_focus)
    
    # Ajouter aussi sur les canvas et containers qui seront créés
    def bind_canvas_focus():
        """Bind les canvas après leur création"""
        canvas_widgets = []
        
        # Ajouter les canvas s'ils existent
        if hasattr(self, 'playlist_canvas'):
            canvas_widgets.append(self.playlist_canvas)
        if hasattr(self, 'youtube_canvas'):
            canvas_widgets.append(self.youtube_canvas)
        if hasattr(self, 'downloads_canvas'):
            canvas_widgets.append(self.downloads_canvas)
        if hasattr(self, 'playlists_canvas'):
            canvas_widgets.append(self.playlists_canvas)
        
        for canvas in canvas_widgets:
            canvas.bind('<Button-1>', remove_focus)
    
    # Programmer le binding des canvas après un court délai pour s'assurer qu'ils sont créés
    self.root.after(100, bind_canvas_focus)