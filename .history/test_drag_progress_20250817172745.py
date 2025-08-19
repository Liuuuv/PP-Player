#!/usr/bin/env python3
"""
Test simple pour vérifier que la barre bleue continue de progresser pendant le drag
"""

import tkinter as tk
import time
from custom_slider import CustomProgressSlider

class TestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Progression Pendant Drag")
        self.root.geometry("600x300")
        self.root.configure(bg='#2d2d2d')
        
        # Variables
        self.start_time = time.time()
        self.running = False
        
        # Instructions
        tk.Label(
            self.root,
            text="Test : La barre bleue doit continuer de progresser même pendant le drag du thumb",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 12, 'bold')
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
        
        # Label de debug
        self.debug_label = tk.Label(
            self.root,
            text="Progression: 0%",
            bg='#2d2d2d',
            fg='#4a8fe7',
            font=('Arial', 10)
        )
        self.debug_label.pack(pady=10)
    
    def start(self):
        self.running = True
        self.start_time = time.time()
        self.update_progress()
    
    def stop(self):
        self.running = False
    
    def update_progress(self):
        if not self.running:
            return
        
        # Progression de 10% par seconde
        elapsed = time.time() - self.start_time
        progress = (elapsed * 10) % 100
        
        # Mettre à jour le slider
        self.slider.set_value(progress)
        
        # Mettre à jour le debug
        self.debug_label.config(text=f"Progression: {progress:.1f}%")
        
        # Continuer
        self.root.after(50, self.update_progress)  # 20 FPS
    
    def run(self):
        print("Instructions:")
        print("1. Cliquez sur 'Démarrer'")
        print("2. Faites un drag du thumb et maintenez-le")
        print("3. Vérifiez que la barre bleue continue de progresser")
        print("4. Le thumb doit rester à la position de drag")
        print("5. La barre bleue doit refléter la vraie progression")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = TestApp()
    app.run()