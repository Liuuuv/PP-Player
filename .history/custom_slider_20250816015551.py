import tkinter as tk
from tkinter import ttk
import math

from __init__ import*

class CustomVolumeSlider(tk.Frame):
    """Slider de volume personnalisé avec affichage de la valeur lors du drag"""
    
    def __init__(self, parent, from_=0, to=100, value=50, command=None, orient='horizontal', 
                 length=160, label_text="Volume", suffix="%", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.from_ = from_
        self.to = to
        self.current_value = value
        self.command = command
        self.orient = orient
        self.length = length
        self.label_text = label_text
        self.suffix = suffix
        self.dragging = False
        
        # Configuration du style
        self.configure(bg=COLOR_BACKGROUND)
        
        # Label du titre
        self.title_label = tk.Label(self, text=label_text, bg='#2d2d2d', fg='white', font=('Arial', 9))
        self.title_label.pack(pady=(10, 2))
        
        # Frame pour le slider et la valeur
        self.slider_frame = tk.Frame(self, bg='#2d2d2d')
        self.slider_frame.pack(pady=(0, 5))
        
        # Canvas pour le slider personnalisé
        self.canvas = tk.Canvas(self.slider_frame, width=length, height=20, 
                               bg='#3d3d3d', highlightthickness=0)
        self.canvas.pack()
        
        # Label pour afficher la valeur (initialement caché)
        self.value_label = tk.Label(self, text=f"{value}{suffix}", 
                                   bg='#4a8fe7', fg='white', font=('Arial', 8, 'bold'),
                                   relief='solid', bd=1)
        
        # Variables pour le dessin
        self.track_color = '#555555'
        self.fill_color = '#4a8fe7'
        self.thumb_color = '#ffffff'
        self.thumb_hover_color = '#e0e0e0'
        self.thumb_drag_color = '#4a8fe7'
        
        self.track_height = 4
        self.thumb_radius = 8
        
        # Bindings
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Motion>', self.on_hover)
        self.canvas.bind('<Leave>', self.on_leave)
        self.canvas.bind('<Configure>', self.on_configure)
        
        # Dessiner le slider initial après un délai pour que le canvas soit configuré
        self.after(1, self.draw_slider)
    
    def draw_slider(self):
        """Dessine le slider sur le canvas"""
        self.canvas.delete('all')
        
        width = self.canvas.winfo_width() or self.length
        height = self.canvas.winfo_height() or 20
        
        # Position du track (centré verticalement)
        track_y = height // 2
        track_start_x = self.thumb_radius
        track_end_x = width - self.thumb_radius
        track_width = track_end_x - track_start_x
        
        # Dessiner le track de fond
        self.canvas.create_rectangle(
            track_start_x, track_y - self.track_height // 2,
            track_end_x, track_y + self.track_height // 2,
            fill=self.track_color, outline=''
        )
        
        # Calculer la position du thumb
        value_ratio = (self.current_value - self.from_) / (self.to - self.from_)
        thumb_x = track_start_x + (track_width * value_ratio)
        
        # Calculer la position du centre (valeur 0)
        center_ratio = (0 - self.from_) / (self.to - self.from_)
        center_x = track_start_x + (track_width * center_ratio)
        
        # Dessiner la partie remplie du track (depuis le centre vers le thumb)
        if self.current_value != 0:
            fill_start_x = min(center_x, thumb_x)
            fill_end_x = max(center_x, thumb_x)
            self.canvas.create_rectangle(
                fill_start_x, track_y - self.track_height // 2,
                fill_end_x, track_y + self.track_height // 2,
                fill=self.fill_color, outline=''
            )
        
        # Couleur du thumb selon l'état
        thumb_color = self.thumb_color
        if self.dragging:
            thumb_color = self.thumb_drag_color
        
        # Dessiner le thumb
        self.canvas.create_oval(
            thumb_x - self.thumb_radius, track_y - self.thumb_radius,
            thumb_x + self.thumb_radius, track_y + self.thumb_radius,
            fill=thumb_color, outline='#333333', width=1
        )
        
        # Stocker la position du thumb pour les interactions
        self.thumb_x = thumb_x
        self.track_y = track_y
        self.track_start_x = track_start_x
        self.track_end_x = track_end_x
    
    def get_value_from_x(self, x):
        """Convertit une position X en valeur"""
        if not hasattr(self, 'track_start_x'):
            return self.current_value
            
        # Limiter x aux bornes du track
        x = max(self.track_start_x, min(self.track_end_x, x))
        
        # Calculer la valeur
        track_width = self.track_end_x - self.track_start_x
        if track_width <= 0:
            return self.current_value
            
        ratio = (x - self.track_start_x) / track_width
        value = self.from_ + (ratio * (self.to - self.from_))
        
        # Arrondir selon le type de valeur
        if isinstance(self.from_, int) and isinstance(self.to, int):
            return int(round(value))
        else:
            return round(value, 1)
    
    def on_click(self, event):
        """Gère le clic sur le slider"""
        self.dragging = True
        new_value = self.get_value_from_x(event.x)
        self.set_value(new_value)
        self.show_value_label(event)
        
        if self.command:
            self.command(new_value)
    
    def on_drag(self, event):
        """Gère le drag du slider"""
        if self.dragging:
            new_value = self.get_value_from_x(event.x)
            self.set_value(new_value)
            self.update_value_label_position(event)
            
            if self.command:
                self.command(new_value)
    
    def on_release(self, event):
        """Gère le relâchement du clic"""
        self.dragging = False
        self.draw_slider()
        self.hide_value_label()
    
    def on_hover(self, event):
        """Gère le survol du slider"""
        if not self.dragging:
            # Vérifier si on survole le thumb
            if hasattr(self, 'thumb_x'):
                distance = abs(event.x - self.thumb_x)
                if distance <= self.thumb_radius:
                    self.canvas.configure(cursor='hand2')
                else:
                    self.canvas.configure(cursor='')
    
    def on_leave(self, event):
        """Gère la sortie du curseur du slider"""
        if not self.dragging:
            self.canvas.configure(cursor='')
    
    def on_configure(self, event):
        """Gère le redimensionnement du canvas"""
        self.draw_slider()
    
    def show_value_label(self, event):
        """Affiche le label de valeur près du curseur"""
        # Mettre à jour le texte
        self.value_label.config(text=f"{self.current_value}{self.suffix}")
        
        # Calculer la position relative au canvas
        canvas_x = event.x
        canvas_y = -25  # Au-dessus du canvas
        
        # Centrer le label sur la position X
        label_width = 40  # Largeur approximative du label
        x_offset = canvas_x - (label_width // 2)
        
        # S'assurer que le label reste dans les limites
        canvas_width = self.canvas.winfo_width() or self.length
        x_offset = max(0, min(x_offset, canvas_width - label_width))
        
        # Positionner le label relativement au canvas
        self.value_label.place(in_=self.canvas, x=x_offset, y=canvas_y)
        self.value_label.lift()
    
    def update_value_label_position(self, event):
        """Met à jour la position du label de valeur pendant le drag"""
        if self.value_label.winfo_viewable():
            # Mettre à jour le texte
            self.value_label.config(text=f"{self.current_value}{self.suffix}")
            
            # Calculer la position relative au canvas
            canvas_x = event.x
            canvas_y = -25  # Au-dessus du canvas
            
            # Centrer le label sur la position X
            label_width = 40  # Largeur approximative du label
            x_offset = canvas_x - (label_width // 2)
            
            # S'assurer que le label reste dans les limites
            canvas_width = self.canvas.winfo_width() or self.length
            x_offset = max(0, min(x_offset, canvas_width - label_width))
            
            # Positionner le label relativement au canvas
            self.value_label.place(in_=self.canvas, x=x_offset, y=canvas_y)
    
    def hide_value_label(self):
        """Cache le label de valeur"""
        self.value_label.place_forget()
    
    def set_value(self, value):
        """Définit la valeur du slider"""
        # Limiter la valeur aux bornes
        value = max(self.from_, min(self.to, value))
        self.current_value = value
        self.draw_slider()
    
    def get(self):
        """Retourne la valeur actuelle"""
        return self.current_value
    
    def set(self, value):
        """Définit la valeur (compatibilité avec ttk.Scale)"""
        self.set_value(value)
    
    def bind_right_click(self, callback):
        """Lie un callback au clic droit (compatibilité)"""
        self.canvas.bind('<Button-3>', lambda e: callback())


class CustomProgressSlider(tk.Frame):
    """Slider de progression personnalisé avec affichage du temps lors du drag"""
    
    def __init__(self, parent, from_=0, to=100, value=0, command=None, orient='horizontal', 
                 length=400, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.from_ = from_
        self.to = to
        self.current_value = value
        self.command = command
        self.orient = orient
        self.length = length
        self.dragging = False
        self.song_length = 0  # Durée totale en secondes
        
        # Configuration du style
        self.configure(bg='#2d2d2d')
        
        # Canvas pour le slider personnalisé
        self.canvas = tk.Canvas(self, width=length, height=20, 
                               bg='#3d3d3d', highlightthickness=0)
        self.canvas.pack()
        
        # Label pour afficher le temps (initialement caché)
        self.time_label = tk.Label(self, text="00:00", 
                                  bg='#4a8fe7', fg='white', font=('Arial', 8, 'bold'),
                                  relief='solid', bd=1)
        
        # Variables pour le dessin
        self.track_color = '#555555'
        self.fill_color = '#4a8fe7'
        self.thumb_color = '#ffffff'
        self.thumb_hover_color = '#e0e0e0'
        self.thumb_drag_color = '#4a8fe7'
        
        self.track_height = 4
        self.thumb_radius = 8
        
        # Bindings
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Motion>', self.on_hover)
        self.canvas.bind('<Leave>', self.on_leave)
        
        # Attendre que le widget soit affiché avant de dessiner
        self.after(10, self.draw_slider)
    
    def format_time(self, seconds):
        """Formate le temps en MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def draw_slider(self):
        """Dessine le slider"""
        try:
            self.canvas.delete("all")
            
            # S'assurer que le canvas a une taille valide
            self.canvas.update_idletasks()
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                width = self.length
                height = 20
            
            # Position du track
            track_y = height // 2
            track_start_x = self.thumb_radius
            track_end_x = width - self.thumb_radius
            track_width = track_end_x - track_start_x
            
            # Dessiner le track de fond
            self.canvas.create_rectangle(
                track_start_x, track_y - self.track_height//2,
                track_end_x, track_y + self.track_height//2,
                fill=self.track_color, outline=""
            )
            
            # Position du thumb - pendant le drag, utiliser la position de drag
            if self.dragging and hasattr(self, 'drag_thumb_x'):
                thumb_x = self.drag_thumb_x
            else:
                # Position normale basée sur la valeur
                if self.to > self.from_:
                    progress = (self.current_value - self.from_) / (self.to - self.from_)
                else:
                    progress = 0
                thumb_x = track_start_x + progress * track_width
            
            # Dessiner la partie remplie (toujours basée sur current_value, pas sur drag)
            if self.to > self.from_:
                actual_progress = (self.current_value - self.from_) / (self.to - self.from_)
            else:
                actual_progress = 0
            
            if actual_progress > 0:
                actual_fill_x = track_start_x + actual_progress * track_width
                self.canvas.create_rectangle(
                    track_start_x, track_y - self.track_height//2,
                    actual_fill_x, track_y + self.track_height//2,
                    fill=self.fill_color, outline=""
                )
            
            # Couleur du thumb selon l'état
            if self.dragging:
                thumb_color = self.thumb_drag_color
            else:
                thumb_color = self.thumb_color
            
            # Dessiner le thumb
            self.canvas.create_oval(
                thumb_x - self.thumb_radius, track_y - self.thumb_radius,
                thumb_x + self.thumb_radius, track_y + self.thumb_radius,
                fill=thumb_color, outline='#333333', width=1
            )
        
            # Stocker la position du thumb pour les interactions
            self.thumb_x = thumb_x
            
        except Exception as e:
            # En cas d'erreur, réessayer plus tard
            self.after(50, self.draw_slider)
    
    def get_value_from_x(self, x):
        """Convertit une position X en valeur"""
        width = self.canvas.winfo_width() or self.length
        track_start_x = self.thumb_radius
        track_end_x = width - self.thumb_radius
        
        # Limiter x aux bornes du track
        x = max(track_start_x, min(track_end_x, x))
        
        # Calculer la valeur
        progress = (x - track_start_x) / (track_end_x - track_start_x)
        value = self.from_ + progress * (self.to - self.from_)
        return value
    
    def on_click(self, event):
        """Gère le clic sur le slider"""
        self.dragging = True
        self.drag_thumb_x = event.x
        value = self.get_value_from_x(event.x)
        # Ne pas mettre à jour current_value pendant le drag
        self.show_time_label(event.x)
        self.draw_slider()  # Redessiner avec la nouvelle position de drag
        if self.command:
            self.command(value)
    
    def on_drag(self, event):
        """Gère le drag du slider"""
        if self.dragging:
            self.drag_thumb_x = event.x
            value = self.get_value_from_x(event.x)
            # Redessiner avec la nouvelle position de drag
            self.draw_slider()
            self.show_time_label(event.x)
            if self.command:
                self.command(value)
    
    def on_release(self, event):
        """Gère le relâchement du clic"""
        if self.dragging:
            self.dragging = False
            self.hide_time_label()
            value = self.get_value_from_x(event.x)
            # Maintenant on peut mettre à jour current_value
            self.current_value = value
            # Supprimer la position de drag
            if hasattr(self, 'drag_thumb_x'):
                delattr(self, 'drag_thumb_x')
            # Redessiner normalement
            self.draw_slider()
            if self.command:
                self.command(value)
    
    def on_hover(self, event):
        """Gère le survol du slider"""
        if not self.dragging:
            # Changer la couleur du thumb au survol
            self.draw_slider()
    
    def on_leave(self, event):
        """Gère la sortie du curseur"""
        if not self.dragging:
            self.draw_slider()
    
    def show_time_label(self, x):
        """Affiche le label de temps au-dessus du curseur"""
        if self.song_length > 0:
            time_seconds = (self.current_value / 100) * self.song_length
            time_text = self.format_time(time_seconds)
        else:
            time_text = f"{self.current_value:.0f}%"
        
        self.time_label.config(text=time_text)
        
        # Positionner le label au-dessus du curseur
        label_x = x - 20  # Centrer approximativement
        label_y = -25     # Au-dessus du slider
        
        self.time_label.place(x=label_x, y=label_y)
    
    def hide_time_label(self):
        """Cache le label de temps"""
        self.time_label.place_forget()
    
    def set_value(self, value):
        """Définit la valeur du slider"""
        new_value = max(self.from_, min(self.to, value))
        # Toujours mettre à jour la valeur
        self.current_value = new_value
        # Redessiner seulement si on n'est pas en train de dragger
        if not self.dragging:
            self.draw_slider()
    
    def get(self):
        """Retourne la valeur actuelle"""
        return self.current_value
    
    def set(self, value):
        """Définit la valeur (compatibilité avec ttk.Scale)"""
        self.set_value(value)
    
    def set_song_length(self, length_seconds):
        """Définit la durée totale de la chanson pour l'affichage du temps"""
        self.song_length = length_seconds
    
    def config(self, **kwargs):
        """Configuration du slider (compatibilité avec ttk.Scale)"""
        if 'value' in kwargs:
            # La valeur vient en secondes, nous devons la convertir en pourcentage
            value_seconds = kwargs['value']
            if hasattr(self, 'song_length') and self.song_length > 0:
                # Convertir les secondes en pourcentage (0-100)
                percentage = (value_seconds / self.song_length) * 100
                self.set_value(percentage)
            else:
                # Si pas de durée définie, utiliser la valeur directement
                self.set_value(value_seconds)
        if 'to' in kwargs:
            self.to = kwargs['to']
    
    def bind_right_click(self, callback):
        """Ajoute un binding pour le clic droit"""
        self.canvas.bind('<Button-3>', callback)