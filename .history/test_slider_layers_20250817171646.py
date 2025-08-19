#!/usr/bin/env python3
"""
Script de test pour vérifier que :
1. Le thumb est au-dessus de la barre de progression bleue
2. La barre bleue continue de progresser pendant le drag
"""

import tkinter as tk
import time
from custom_slider import CustomProgressSlider

class SliderLayerTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Layers et Progression Continue")
        self.root.geometry("700x400")
        self.root.configure(bg='#2d2d2d')
        
        # Variables de test
        self.start_time = time.time()
        self.auto_progress_running = False
        self.auto_progress_job = None
        
        # Titre
        title_label = tk.Label(
            self.root,
            text="Test du Slider : Layers et Progression Continue",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Instructions :\n" +
                 "1. Cliquez sur 'Démarrer Auto-Progression' pour simuler la lecture\n" +
                 "2. Pendant que la barre bleue progresse, faites un drag du thumb\n" +
                 "3. Vérifiez que le thumb reste visible au-dessus de la barre bleue\n" +
                 "4. Vérifiez que la barre bleue continue de progresser pendant le drag",
            bg='#2d2d2d',
            fg='#cccccc',
            font=('Arial', 10),
            justify=tk.LEFT
        )
        instructions.pack(pady=10)
        
        # Créer le slider de test
        self.progress_slider = CustomProgressSlider(
            self.root,
            from_=0,
            to=100,
            value=0,
            length=600,
            command=self.on_slider_change
        )
        self.progress_slider.pack(pady=30)
        
        # Définir une durée de chanson pour les tests
        self.progress_slider.set_song_length(180)  # 3 minutes
        
        # Labels d'information
        info_frame = tk.Frame(self.root, bg='#2d2d2d')
        info_frame.pack(pady=20)
        
        self.progress_label = tk.Label(
            info_frame,
            text="Progression Auto: 0%",
            bg='#2d2d2d',
            fg='#4a8fe7',
            font=('Arial', 12, 'bold')
        )
        self.progress_label.pack()
        
        self.drag_label = tk.Label(
            info_frame,
            text="Position Drag: N/A",
            bg='#2d2d2d',
            fg='#e74a4a',
            font=('Arial', 12, 'bold')
        )
        self.drag_label.pack()
        
        # Boutons de contrôle
        button_frame = tk.Frame(self.root, bg='#2d2d2d')
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(
            button_frame,
            text="Démarrer Auto-Progression",
            command=self.start_auto_progress,
            bg='#47a047',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="Arrêter Auto-Progression",
            command=self.stop_auto_progress,
            bg='#e74a4a',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_slider,
            bg='#4a8fe7',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20
        ).pack(side=tk.LEFT, padx=10)
        
        # Bind les événements du slider pour le debug
        self.progress_slider.canvas.bind('<Button-1>', self.on_drag_start, add='+')
        self.progress_slider.canvas.bind('<B1-Motion>', self.on_drag_motion, add='+')
        self.progress_slider.canvas.bind('<ButtonRelease-1>', self.on_drag_end, add='+')
    
    def on_slider_change(self, value):
        """Callback appelé quand le slider change"""
        pass  # Ne rien faire pour ne pas interférer
    
    def on_drag_start(self, event):
        """Callback quand le drag commence"""
        self.drag_label.config(text="Position Drag: Début du drag", fg='#e74a4a')
    
    def on_drag_motion(self, event):
        """Callback pendant le drag"""
        if hasattr(self.progress_slider, 'dragging') and self.progress_slider.dragging:
            drag_value = self.progress_slider.get_value_from_x(event.x)
            self.drag_label.config(
                text=f"Position Drag: {drag_value:.1f}%", 
                fg='#e74a4a'
            )
    
    def on_drag_end(self, event):
        """Callback quand le drag se termine"""
        self.drag_label.config(text="Position Drag: Drag terminé", fg='#888888')
        # Remettre à jour après un délai pour voir l'effet
        self.root.after(1000, lambda: self.drag_label.config(text="Position Drag: N/A"))
    
    def start_auto_progress(self):
        """Démarre la progression automatique"""
        self.auto_progress_running = True
        self.start_time = time.time()
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.auto_progress()
    
    def stop_auto_progress(self):
        """Arrête la progression automatique"""
        self.auto_progress_running = False
        if self.auto_progress_job:
            self.root.after_cancel(self.auto_progress_job)
            self.auto_progress_job = None
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_label.config(text="Progression Auto: Arrêtée")
    
    def auto_progress(self):
        """Met à jour automatiquement la progression"""
        if not self.auto_progress_running:
            return
        
        # Calculer la progression (cycle de 20 secondes)
        elapsed = time.time() - self.start_time
        progress = (elapsed * 5) % 100  # 5% par seconde, cycle de 20s
        
        # Mettre à jour le slider (ceci devrait continuer même pendant le drag)
        self.progress_slider.set_value(progress)
        
        # Mettre à jour le label
        self.progress_label.config(text=f"Progression Auto: {progress:.1f}%")
        
        # Programmer la prochaine mise à jour (30 FPS pour fluidité)
        self.auto_progress_job = self.root.after(33, self.auto_progress)
    
    def reset_slider(self):
        """Remet le slider à zéro"""
        self.stop_auto_progress()
        self.progress_slider.set_value(0)
        self.progress_label.config(text="Progression Auto: 0%")
        self.drag_label.config(text="Position Drag: N/A")
    
    def run(self):
        """Lance l'application de test"""
        print("=== Test Layers et Progression Continue ===")
        print("Vérifications à effectuer :")
        print("1. Le thumb blanc doit toujours être visible au-dessus de la barre bleue")
        print("2. Pendant le drag, la barre bleue doit continuer de progresser")
        print("3. Le thumb doit suivre la souris pendant le drag")
        print("4. Après le drag, le thumb doit revenir à la position de progression")
        print()
        
        self.root.mainloop()

if __name__ == "__main__":
    app = SliderLayerTestApp()
    app.run()