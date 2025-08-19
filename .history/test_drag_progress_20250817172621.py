#!/usr/bin/env python3
"""
Test simple pour vérifier que la barre bleue continue d'avancer pendant le drag
"""

import tkinter as tk
import time
from custom_slider import CustomProgressSlider

class DragProgressTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Progression Pendant Drag")
        self.root.geometry("600x300")
        self.root.configure(bg='#2d2d2d')
        
        # Variables
        self.start_time = time.time()
        self.running = False
        
        # Titre
        tk.Label(
            self.root,
            text="Test : La barre bleue doit continuer d'avancer pendant le drag",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 14, 'bold')
        ).pack(pady=20)
        
        # Slider
        self.slider = CustomProgressSlider(
            self.root,
            from_=0,
            to=100,
            value=0,
            length=500
        )
        self.slider.pack(pady=30)
        
        # Info
        self.info_label = tk.Label(
            self.root,
            text="Progression: 0%",
            bg='#2d2d2d',
            fg='#4a8fe7',
            font=('Arial', 12, 'bold')
        )
        self.info_label.pack(pady=10)
        
        # Instructions
        tk.Label(
            self.root,
            text="1. Cliquez sur 'Démarrer'\n2. Faites un drag sur le slider\n3. La barre bleue doit continuer d'avancer",
            bg='#2d2d2d',
            fg='#cccccc',
            font=('Arial', 10),
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Boutons
        button_frame = tk.Frame(self.root, bg='#2d2d2d')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Démarrer",
            command=self.start,
            bg='#47a047',
            fg='white',
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="Arrêter",
            command=self.stop,
            bg='#e74a4a',
            fg='white',
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="Reset",
            command=self.reset,
            bg='#4a8fe7',
            fg='white',
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT, padx=10)
    
    def start(self):
        """Démarre la progression automatique"""
        self.running = True
        self.start_time = time.time()
        self.update_progress()
    
    def stop(self):
        """Arrête la progression"""
        self.running = False
    
    def reset(self):
        """Remet à zéro"""
        self.running = False
        self.slider.set_value(0)
        self.info_label.config(text="Progression: 0%")
    
    def update_progress(self):
        """Met à jour la progression"""
        if not self.running:
            return
        
        # Progression de 2% par seconde (50 secondes pour 100%)
        elapsed = time.time() - self.start_time
        progress = min(100, elapsed * 2)
        
        # Mettre à jour le slider
        self.slider.set_value(progress)
        self.info_label.config(text=f"Progression: {progress:.1f}%")
        
        # Continuer si pas fini
        if progress < 100:
            self.root.after(50, self.update_progress)  # 20 FPS
        else:
            self.running = False
            self.info_label.config(text="Progression: 100% - Terminé!")
    
    def run(self):
        print("=== Test Progression Pendant Drag ===")
        print("Instructions:")
        print("1. Cliquez sur 'Démarrer' pour lancer la progression automatique")
        print("2. Pendant que la barre progresse, faites un drag du thumb")
        print("3. Vérifiez que la barre bleue continue d'avancer même pendant le drag")
        print("4. Le thumb doit suivre votre souris, mais la barre bleue doit progresser")
        print()
        
        self.root.mainloop()

if __name__ == "__main__":
    app = DragProgressTest()
    app.run()