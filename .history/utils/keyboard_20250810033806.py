"""
Gestion des raccourcis clavier
"""
import tkinter as tk


class KeyboardManager:
    """Gestionnaire des raccourcis clavier"""
    
    def __init__(self, root, audio_player):
        self.root = root
        self.audio_player = audio_player
        self.setup_bindings()
    
    def setup_bindings(self):
        """Configure les raccourcis clavier"""
        # Binding pour la barre d'espace (pause/play)
        self.root.bind('<KeyPress-space>', self.on_space_pressed)
        
        # Binding pour retirer le focus des champs de saisie
        self.root.bind('<Button-1>', self.on_root_click)
        
        # Autres raccourcis possibles
        self.root.bind('<Control-Right>', self.on_next_track)
        self.root.bind('<Control-Left>', self.on_previous_track)
        self.root.bind('<Control-Up>', self.on_volume_up)
        self.root.bind('<Control-Down>', self.on_volume_down)
        
        # S'assurer que la fenêtre peut recevoir le focus
        self.root.focus_set()
    
    def on_space_pressed(self, event):
        """Gère l'appui sur la barre d'espace"""
        # Vérifier si le focus n'est pas sur un champ de saisie
        focused_widget = self.root.focus_get()
        if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
            # Si le focus est sur un champ de saisie, ne pas intercepter
            return
        
        # Appeler la fonction play_pause
        self.audio_player.play_pause()
        
        # Empêcher la propagation de l'événement
        return "break"
    
    def on_root_click(self, event):
        """Gère les clics pour retirer le focus des champs de saisie"""
        clicked_widget = event.widget
        
        # Si on clique sur un champ de saisie, ne rien faire
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
        
        # Retirer le focus des champs de saisie
        focused_widget = self.root.focus_get()
        if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
            self.root.focus_set()
    
    def on_next_track(self, event):
        """Passe à la piste suivante (Ctrl+Droite)"""
        self.audio_player.next_track()
        return "break"
    
    def on_previous_track(self, event):
        """Passe à la piste précédente (Ctrl+Gauche)"""
        self.audio_player.previous_track()
        return "break"
    
    def on_volume_up(self, event):
        """Augmente le volume (Ctrl+Haut)"""
        current_volume = self.audio_player.settings.global_volume
        new_volume = min(1.0, current_volume + 0.05)
        self.audio_player.set_volume(new_volume)
        return "break"
    
    def on_volume_down(self, event):
        """Diminue le volume (Ctrl+Bas)"""
        current_volume = self.audio_player.settings.global_volume
        new_volume = max(0.0, current_volume - 0.05)
        self.audio_player.set_volume(new_volume)
        return "break"