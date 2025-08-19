#!/usr/bin/env python3
"""
Script de test pour vérifier toutes les corrections
"""

import tkinter as tk
import time

def test_volume_shortcuts():
    """Teste les raccourcis de volume avec répétition"""
    root = tk.Tk()
    root.title("Test Volume avec Répétition")
    root.geometry("500x400")
    root.configure(bg='#2d2d2d')
    
    volume = 50
    volume_keys_pressed = {'up': False, 'down': False}
    volume_repeat_id = None
    
    def update_display():
        volume_label.config(text=f"Volume: {volume}%")
        progress_bar['value'] = volume
    
    def on_volume_up(event):
        nonlocal volume, volume_repeat_id
        
        # Augmenter immédiatement
        volume = min(100, volume + 5)
        update_display()
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume UP: {volume}%\n")
        log_text.see(tk.END)
        
        # Marquer comme pressée
        volume_keys_pressed['up'] = True
        
        # Annuler répétition précédente
        if volume_repeat_id:
            root.after_cancel(volume_repeat_id)
        
        # Fonction de répétition
        def repeat_up():
            nonlocal volume, volume_repeat_id
            if volume_keys_pressed['up'] and volume < 100:
                volume = min(100, volume + 5)
                update_display()
                log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume UP (répétition): {volume}%\n")
                log_text.see(tk.END)
                volume_repeat_id = root.after(150, repeat_up)
        
        # Démarrer répétition après 400ms
        volume_repeat_id = root.after(400, repeat_up)
        return "break"
    
    def on_volume_down(event):
        nonlocal volume, volume_repeat_id
        
        # Diminuer immédiatement
        volume = max(0, volume - 5)
        update_display()
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume DOWN: {volume}%\n")
        log_text.see(tk.END)
        
        # Marquer comme pressée
        volume_keys_pressed['down'] = True
        
        # Annuler répétition précédente
        if volume_repeat_id:
            root.after_cancel(volume_repeat_id)
        
        # Fonction de répétition
        def repeat_down():
            nonlocal volume, volume_repeat_id
            if volume_keys_pressed['down'] and volume > 0:
                volume = max(0, volume - 5)
                update_display()
                log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Volume DOWN (répétition): {volume}%\n")
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
    tk.Label(root, text="Test Volume avec Répétition", font=("Arial", 16, "bold"), bg='#2d2d2d', fg='white').pack(pady=10)
    
    tk.Label(root, text="Maintenez Ctrl+Alt+↑ ou Ctrl+Alt+↓ pour tester la répétition", bg='#2d2d2d', fg='white').pack(pady=5)
    
    volume_label = tk.Label(root, text=f"Volume: {volume}%", font=("Arial", 14, "bold"), bg='#2d2d2d', fg='#4a8fe7')
    volume_label.pack(pady=10)
    
    # Barre de progression
    from tkinter import ttk
    progress_bar = ttk.Progressbar(root, length=300, mode='determinate', maximum=100)
    progress_bar.pack(pady=10)
    progress_bar['value'] = volume
    
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
    
    # Message initial
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Test démarré - Maintenez les touches pour tester la répétition\n\n")
    
    tk.Button(root, text="Fermer", command=root.destroy, bg='#d32f2f', fg='white').pack(pady=10)
    
    print("=== Test Volume avec Répétition ===")
    print("Maintenez Ctrl+Alt+↑ ou Ctrl+Alt+↓ pour tester")
    print("Le volume devrait monter/descendre en continu")
    
    root.mainloop()

def test_play_pause_shortcut():
    """Teste le raccourci play/pause"""
    root = tk.Tk()
    root.title("Test Raccourci Play/Pause")
    root.geometry("400x300")
    root.configure(bg='#2d2d2d')
    
    is_playing = False
    
    def toggle_play_pause():
        nonlocal is_playing
        is_playing = not is_playing
        status_label.config(text=f"État: {'En lecture' if is_playing else 'En pause'}")
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Ctrl+Alt+P: {'Play' if is_playing else 'Pause'}\n")
        log_text.see(tk.END)
    
    def on_play_pause(event):
        toggle_play_pause()
        return "break"
    
    # Interface
    tk.Label(root, text="Test Raccourci Play/Pause", font=("Arial", 16, "bold"), bg='#2d2d2d', fg='white').pack(pady=20)
    
    tk.Label(root, text="Appuyez sur Ctrl+Alt+P pour tester", bg='#2d2d2d', fg='white').pack(pady=10)
    
    status_label = tk.Label(root, text="État: En pause", font=("Arial", 12, "bold"), bg='#2d2d2d', fg='#4a8fe7')
    status_label.pack(pady=20)
    
    # Zone de log
    log_frame = tk.Frame(root, bg='#2d2d2d')
    log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    log_text = tk.Text(log_frame, height=6, bg='#1d1d1d', fg='white', font=("Consolas", 9))
    log_text.pack(fill=tk.BOTH, expand=True)
    
    # Bindings
    root.bind('<Control-Alt-p>', on_play_pause)
    root.bind('<Control-Alt-P>', on_play_pause)
    
    root.focus_set()
    
    # Message initial
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Test démarré - Appuyez sur Ctrl+Alt+P\n\n")
    
    tk.Button(root, text="Fermer", command=root.destroy, bg='#d32f2f', fg='white').pack(pady=10)
    
    print("=== Test Raccourci Play/Pause ===")
    print("Appuyez sur Ctrl+Alt+P pour tester")
    
    root.mainloop()

def main():
    """Menu principal de test"""
    print("=== Test des Corrections ===")
    print("1. Test du volume avec répétition")
    print("2. Test du raccourci play/pause")
    print("3. Lancer l'application complète")
    print("0. Quitter")
    
    while True:
        try:
            choice = input("\nChoisissez un test (0-3): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                test_volume_shortcuts()
            elif choice == '2':
                test_play_pause_shortcut()
            elif choice == '3':
                print("Lancement de l'application complète...")
                import subprocess
                subprocess.run(['python', 'main.py'])
            else:
                print("Choix invalide. Utilisez 0, 1, 2 ou 3.")
        except KeyboardInterrupt:
            break
    
    print("\nTests terminés !")

if __name__ == "__main__":
    main()