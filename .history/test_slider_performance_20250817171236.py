#!/usr/bin/env python3
"""
Script de test pour vérifier les performances du CustomProgressSlider optimisé
"""

import tkinter as tk
import time
from custom_slider import CustomProgressSlider

class SliderTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Performance Slider")
        self.root.geometry("600x300")
        self.root.configure(bg='#2d2d2d')
        
        # Variables de test
        self.update_count = 0
        self.start_time = time.time()
        
        # Créer le slider de test
        self.progress_slider = CustomProgressSlider(
            self.root,
            from_=0,
            to=100,
            value=0,
            length=500,
            command=self.on_slider_change
        )
        self.progress_slider.pack(pady=50)
        
        # Définir une durée de chanson pour les tests
        self.progress_slider.set_song_length(180)  # 3 minutes
        
        # Label pour afficher les stats
        self.stats_label = tk.Label(
            self.root,
            text="Updates: 0 | FPS: 0",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 12)
        )
        self.stats_label.pack(pady=10)
        
        # Boutons de test
        button_frame = tk.Frame(self.root, bg='#2d2d2d')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Test Auto Update",
            command=self.start_auto_update,
            bg='#4a8fe7',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Stop Test",
            command=self.stop_auto_update,
            bg='#e74a4a',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Force Redraw",
            command=self.force_redraw_test,
            bg='#47a047',
            fg='white',
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        # Variables pour le test automatique
        self.auto_update_running = False
        self.auto_update_job = None
        
        # Démarrer le calcul des FPS
        self.update_stats()
    
    def on_slider_change(self, value):
        """Callback appelé quand le slider change"""
        pass  # Ne rien faire pour éviter d'affecter les performances
    
    def start_auto_update(self):
        """Démarre le test de mise à jour automatique"""
        self.auto_update_running = True
        self.update_count = 0
        self.start_time = time.time()
        self.auto_update()
    
    def stop_auto_update(self):
        """Arrête le test de mise à jour automatique"""
        self.auto_update_running = False
        if self.auto_update_job:
            self.root.after_cancel(self.auto_update_job)
            self.auto_update_job = None
    
    def auto_update(self):
        """Met à jour automatiquement le slider pour tester les performances"""
        if not self.auto_update_running:
            return
        
        # Simuler une progression de lecture
        current_time = time.time()
        elapsed = current_time - self.start_time
        progress = (elapsed * 10) % 100  # Cycle de 10 secondes
        
        # Mettre à jour le slider
        self.progress_slider.set_value(progress)
        self.update_count += 1
        
        # Programmer la prochaine mise à jour (60 FPS)
        self.auto_update_job = self.root.after(16, self.auto_update)
    
    def force_redraw_test(self):
        """Test de redraw forcé"""
        print("Force redraw test...")
        start = time.time()
        self.progress_slider.force_redraw()
        end = time.time()
        print(f"Force redraw took: {(end - start) * 1000:.2f}ms")
    
    def update_stats(self):
        """Met à jour les statistiques d'affichage"""
        if self.auto_update_running and self.update_count > 0:
            elapsed = time.time() - self.start_time
            fps = self.update_count / elapsed if elapsed > 0 else 0
            self.stats_label.config(
                text=f"Updates: {self.update_count} | FPS: {fps:.1f}"
            )
        
        # Programmer la prochaine mise à jour des stats
        self.root.after(100, self.update_stats)
    
    def run(self):
        """Lance l'application de test"""
        print("=== Test Performance CustomProgressSlider ===")
        print("Instructions:")
        print("1. Cliquez sur 'Test Auto Update' pour démarrer le test")
        print("2. Observez les FPS et la fluidité du slider")
        print("3. Testez le drag du slider pendant le test")
        print("4. Cliquez sur 'Force Redraw' pour tester le redraw complet")
        print("5. Fermez la fenêtre pour terminer")
        print()
        
        self.root.mainloop()

if __name__ == "__main__":
    app = SliderTestApp()
    app.run()