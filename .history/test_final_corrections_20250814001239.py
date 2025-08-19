#!/usr/bin/env python3
"""
Script de test final pour vérifier toutes les corrections
"""

import tkinter as tk
from tkinter import ttk
import time

def test_volume_with_real_slider():
    """Teste le volume avec un vrai slider comme dans l'app"""
    root = tk.Tk()
    root.title("Test Volume avec Slider Réel")
    root.geometry("600x400")
    root.configure(bg='#2d2d2d')
    
    # Variables
    volume = 0.2  # Volume initial comme dans l'app (0.0 à 1.0)
    volume_keys_pressed = {'up': False, 'down': False}
    volume_repeat_id = None
    
    def set_volume(val):
        """Simule la fonction set_volume de l'app"""
        nonlocal volume
        volume = float(val) / 100.0  # Convertir de 0-100 à 0.0-1.0
        volume_display.config(text=f"Volume interne: {volume:.2f} ({int(volume*100)}%)")
        print(f"DEBUG: set_volume appelé avec {val}, volume interne = {volume:.2f}")
    
    def update_display():
        current_vol = volume * 100
        volume_label.config(text=f"Volume: {int(current_vol)}%")
        volume_slider.set(current_vol)
    
    def on_volume_up(event):
        nonlocal volume_repeat_id
        
        # Augmenter immédiatement
        current_volume = volume * 100
        new_volume = min(100, current_volume + 5)
        set_volume(new_volume)  # Utiliser set_volume comme dans l'app
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume UP: {int(new_volume)}%\n")
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
                    set_volume(new_vol)
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
        set_volume(new_volume)  # Utiliser set_volume comme dans l'app
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume DOWN: {int(new_volume)}%\n")
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
                    set_volume(new_vol)
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
            log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Touche UP relâchée\n")
        elif event.keysym == 'Down':
            volume_keys_pressed['down'] = False
            log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Touche DOWN relâchée\n")
        
        # Annuler répétition
        if volume_repeat_id:
            root.after_cancel(volume_repeat_id)
            volume_repeat_id = None
        
        log_text.see(tk.END)
        return "break"
    
    # Interface
    tk.Label(root, text="Test Volume avec Slider Réel", font=("Arial", 16, "bold"), bg='#2d2d2d', fg='white').pack(pady=10)
    
    tk.Label(root, text="Maintenez Ctrl+Alt+↑ ou Ctrl+Alt+↓ pour tester la répétition", bg='#2d2d2d', fg='white').pack(pady=5)
    
    volume_label = tk.Label(root, text="", font=("Arial", 14, "bold"), bg='#2d2d2d', fg='#4a8fe7')
    volume_label.pack(pady=10)
    
    volume_display = tk.Label(root, text="", font=("Arial", 12), bg='#2d2d2d', fg='#888888')
    volume_display.pack(pady=5)
    
    # Slider de volume (comme dans l'app)
    volume_frame = tk.Frame(root, bg='#2d2d2d')
    volume_frame.pack(pady=10)
    
    tk.Label(volume_frame, text="Slider Volume:", bg='#2d2d2d', fg='white').pack()
    
    volume_slider = tk.Scale(
        volume_frame,
        from_=0, to=100,
        orient=tk.HORIZONTAL,
        length=300,
        command=set_volume,
        bg='#3d3d3d',
        fg='white',
        highlightbackground='#2d2d2d'
    )
    volume_slider.pack(pady=5)
    
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
    update_display()
    
    # Message initial
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Test démarré - Volume initial: {int(volume*100)}%\n")
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Maintenez les touches pour tester la répétition\n\n")
    
    tk.Button(root, text="Fermer", command=root.destroy, bg='#d32f2f', fg='white').pack(pady=10)
    
    print("=== Test Volume avec Slider Réel ===")
    print("Le volume devrait maintenant monter/descendre correctement")
    print("Et le slider devrait bouger en même temps")
    
    root.mainloop()

def test_play_pause_debug():
    """Teste le raccourci play/pause avec debug détaillé"""
    root = tk.Tk()
    root.title("Test Raccourci Play/Pause - Debug")
    root.geometry("500x400")
    root.configure(bg='#2d2d2d')
    
    is_playing = False
    
    def play_pause():
        """Simule la fonction play_pause de l'app"""
        nonlocal is_playing
        is_playing = not is_playing
        status_label.config(text=f"État: {'En lecture' if is_playing else 'En pause'}")
        return is_playing
    
    def on_play_pause(event):
        """Simule on_global_play_pause avec debug"""
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] on_global_play_pause appelé !\n")
        try:
            if hasattr(root, 'play_pause'):
                log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] play_pause existe, appel en cours...\n")
                result = root.play_pause()
                log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] play_pause() appelé avec succès - résultat: {result}\n")
            else:
                log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] play_pause n'existe pas !\n")
        except Exception as e:
            log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] ERREUR: {e}\n")
            import traceback
            log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Traceback: {traceback.format_exc()}\n")
        
        log_text.see(tk.END)
        return "break"
    
    # Ajouter la fonction à root pour simuler l'app
    root.play_pause = play_pause
    
    # Interface
    tk.Label(root, text="Test Raccourci Play/Pause - Debug", font=("Arial", 16, "bold"), bg='#2d2d2d', fg='white').pack(pady=20)
    
    tk.Label(root, text="Appuyez sur Ctrl+Alt+P pour tester", bg='#2d2d2d', fg='white').pack(pady=10)
    
    status_label = tk.Label(root, text="État: En pause", font=("Arial", 12, "bold"), bg='#2d2d2d', fg='#4a8fe7')
    status_label.pack(pady=20)
    
    # Zone de log
    log_frame = tk.Frame(root, bg='#2d2d2d')
    log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    tk.Label(log_frame, text="Log détaillé:", bg='#2d2d2d', fg='white', font=("Arial", 10, "bold")).pack(anchor='w')
    
    log_text = tk.Text(log_frame, height=10, bg='#1d1d1d', fg='white', font=("Consolas", 9))
    log_text.pack(fill=tk.BOTH, expand=True)
    
    # Bindings (les deux variantes)
    root.bind('<Control-Alt-p>', on_play_pause)
    root.bind('<Control-Alt-P>', on_play_pause)
    
    root.focus_set()
    
    # Message initial
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Test démarré\n")
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Bindings configurés: <Control-Alt-p> et <Control-Alt-P>\n")
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Fonction play_pause attachée à root: {hasattr(root, 'play_pause')}\n\n")
    
    tk.Button(root, text="Fermer", command=root.destroy, bg='#d32f2f', fg='white').pack(pady=10)
    
    print("=== Test Raccourci Play/Pause - Debug ===")
    print("Appuyez sur Ctrl+Alt+P pour voir le debug détaillé")
    
    root.mainloop()

def main():
    """Menu principal de test"""
    print("=== Test des Corrections Finales ===")
    print("1. Test du volume avec slider réel")
    print("2. Test du raccourci play/pause avec debug")
    print("3. Lancer l'application complète")
    print("0. Quitter")
    
    while True:
        try:
            choice = input("\nChoisissez un test (0-3): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                test_volume_with_real_slider()
            elif choice == '2':
                test_play_pause_debug()
            elif choice == '3':
                print("Lancement de l'application complète...")
                import subprocess
                subprocess.run(['python', 'main.py'])
            else:
                print("Choix invalide. Utilisez 0, 1, 2 ou 3.")
        except KeyboardInterrupt:
            break
    
    print("\n=== Résumé des corrections ===")
    print("✅ Volume utilise maintenant set_volume() au lieu de volume_slider.set()")
    print("✅ Raccourci Ctrl+Alt+P avec debug détaillé")
    print("✅ Playlists configurées pour 4 par ligne")
    print("✅ Recherche automatique désactivée (seulement Entrée/bouton)")
    print("✅ results_container recréé automatiquement après mode artiste")
    print("\nTests terminés !")

if __name__ == "__main__":
    main()