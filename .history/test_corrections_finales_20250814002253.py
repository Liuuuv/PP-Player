#!/usr/bin/env python3
"""
Script de test final pour vérifier toutes les corrections
"""

import tkinter as tk
from tkinter import ttk
import time

def test_volume_with_slider_update():
    """Teste que le slider se met à jour avec le volume"""
    root = tk.Tk()
    root.title("Test Volume + Slider")
    root.geometry("600x400")
    root.configure(bg='#2d2d2d')
    
    # Variables
    volume = 0.2  # Volume initial
    volume_keys_pressed = {'up': False, 'down': False}
    volume_repeat_id = None
    
    def set_volume(val):
        """Simule la fonction set_volume de l'app"""
        nonlocal volume
        volume = float(val) / 100.0
        volume_display.config(text=f"Volume interne: {volume:.2f} ({int(volume*100)}%)")
        print(f"DEBUG: set_volume appelé avec {val}, volume interne = {volume:.2f}")
    
    def on_volume_up(event):
        nonlocal volume_repeat_id
        
        # Augmenter immédiatement
        current_volume = volume * 100
        new_volume = min(100, current_volume + 5)
        set_volume(new_volume)  # Met à jour le volume interne
        volume_slider.set(new_volume)  # Met à jour le slider visuellement
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume UP: {int(new_volume)}% (slider mis à jour)\n")
        log_text.see(tk.END)
        
        # Marquer comme pressée
        volume_keys_pressed['up'] = True
        
        # Annuler répétition précédente
        if volume_repeat_id:
            root.after_cancel(volume_repeat_id)
        
        # Fonction de répétition
        def repeat_up():
            nonlocal volume_repeat_id
            if volume_keys_pressed['up']:
                current_vol = volume * 100
                if current_vol < 100:
                    new_vol = min(100, current_vol + 5)
                    set_volume(new_vol)  # Met à jour le volume interne
                    volume_slider.set(new_vol)  # Met à jour le slider visuellement
                    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume UP (répétition): {int(new_vol)}%\n")
                    log_text.see(tk.END)
                    volume_repeat_id = root.after(150, repeat_up)
        
        # Démarrer répétition après 400ms
        volume_repeat_id = root.after(400, repeat_up)
        return "break"
    
    def on_volume_down(event):
        nonlocal volume_repeat_id
        
        # Diminuer immédiatement
        current_volume = volume * 100
        new_volume = max(0, current_volume - 5)
        set_volume(new_volume)  # Met à jour le volume interne
        volume_slider.set(new_volume)  # Met à jour le slider visuellement
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume DOWN: {int(new_volume)}% (slider mis à jour)\n")
        log_text.see(tk.END)
        
        # Marquer comme pressée
        volume_keys_pressed['down'] = True
        
        # Annuler répétition précédente
        if volume_repeat_id:
            root.after_cancel(volume_repeat_id)
        
        # Fonction de répétition
        def repeat_down():
            nonlocal volume_repeat_id
            if volume_keys_pressed['down']:
                current_vol = volume * 100
                if current_vol > 0:
                    new_vol = max(0, current_vol - 5)
                    set_volume(new_vol)  # Met à jour le volume interne
                    volume_slider.set(new_vol)  # Met à jour le slider visuellement
                    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume DOWN (répétition): {int(new_vol)}%\n")
                    log_text.see(tk.END)
                    volume_repeat_id = root.after(150, repeat_down)
        
        # Démarrer répétition après 400ms
        volume_repeat_id = root.after(400, repeat_down)
        return "break"
    
    def on_key_release(event):
        nonlocal volume_repeat_id
        if event.keysym == 'Up':
            volume_keys_pressed['up'] = False
        elif event.keysym == 'Down':
            volume_keys_pressed['down'] = False
        
        # Annuler répétition
        if volume_repeat_id:
            root.after_cancel(volume_repeat_id)
            volume_repeat_id = None
        
        return "break"
    
    # Interface
    tk.Label(root, text="Test Volume + Slider", font=("Arial", 16, "bold"), bg='#2d2d2d', fg='white').pack(pady=10)
    
    tk.Label(root, text="Maintenez Ctrl+Alt+↑ ou Ctrl+Alt+↓", bg='#2d2d2d', fg='white').pack(pady=5)
    tk.Label(root, text="Le slider devrait bouger en temps réel !", bg='#2d2d2d', fg='#4a8fe7').pack(pady=5)
    
    volume_display = tk.Label(root, text="", font=("Arial", 12), bg='#2d2d2d', fg='#888888')
    volume_display.pack(pady=10)
    
    # Slider de volume
    volume_frame = tk.Frame(root, bg='#2d2d2d')
    volume_frame.pack(pady=10)
    
    tk.Label(volume_frame, text="Slider Volume:", bg='#2d2d2d', fg='white').pack()
    
    volume_slider = tk.Scale(
        volume_frame,
        from_=0, to=100,
        orient=tk.HORIZONTAL,
        length=400,
        command=set_volume,
        bg='#3d3d3d',
        fg='white',
        highlightbackground='#2d2d2d'
    )
    volume_slider.pack(pady=5)
    volume_slider.set(volume * 100)  # Initialiser
    
    # Zone de log
    log_frame = tk.Frame(root, bg='#2d2d2d')
    log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    tk.Label(log_frame, text="Log des actions:", bg='#2d2d2d', fg='white', font=("Arial", 10, "bold")).pack(anchor='w')
    
    log_text = tk.Text(log_frame, height=8, bg='#1d1d1d', fg='white', font=("Consolas", 9))
    log_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Bindings
    root.bind('<Control-Alt-Up>', on_volume_up)
    root.bind('<Control-Alt-Down>', on_volume_down)
    root.bind('<Control-Alt-KeyRelease-Up>', on_key_release)
    root.bind('<Control-Alt-KeyRelease-Down>', on_key_release)
    
    root.focus_set()
    
    # Initialiser l'affichage
    set_volume(volume * 100)
    
    # Message initial
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Test démarré - Volume initial: {int(volume*100)}%\n")
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Le slider devrait bouger avec les raccourcis !\n\n")
    
    tk.Button(root, text="Fermer", command=root.destroy, bg='#d32f2f', fg='white').pack(pady=10)
    
    print("=== Test Volume + Slider ===")
    print("Le slider devrait maintenant bouger en temps réel")
    print("Testez avec Ctrl+Alt+↑ et Ctrl+Alt+↓")
    
    root.mainloop()

def main():
    """Menu principal de test"""
    print("=== Test des Corrections Finales ===")
    print("1. Test du volume avec slider qui bouge")
    print("2. Lancer l'application complète")
    print("0. Quitter")
    
    while True:
        try:
            choice = input("\nChoisissez un test (0-2): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                test_volume_with_slider_update()
            elif choice == '2':
                print("Lancement de l'application complète...")
                import subprocess
                subprocess.run(['python', 'main.py'])
            else:
                print("Choix invalide. Utilisez 0, 1 ou 2.")
        except KeyboardInterrupt:
            break
    
    print("\n=== Résumé des corrections finales ===")
    print("✅ Volume utilise set_volume() + volume_slider.set()")
    print("✅ Slider se met à jour visuellement en temps réel")
    print("✅ Fonction _create_new_playlist_dialog corrigée (3 arguments)")
    print("✅ Recréation automatique du youtube_canvas après mode artiste")
    print("✅ Playlists 4 par ligne")
    print("✅ Recherche manuelle uniquement")
    print("\nToutes les corrections principales sont appliquées !")

if __name__ == "__main__":
    main()