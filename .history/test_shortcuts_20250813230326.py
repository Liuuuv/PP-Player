#!/usr/bin/env python3
"""
Script de test pour vérifier les raccourcis clavier globaux
"""

import tkinter as tk
from tkinter import messagebox

def test_shortcuts():
    root = tk.Tk()
    root.title("Test des raccourcis clavier")
    root.geometry("400x300")
    
    # Variables de test
    volume = 50
    is_playing = False
    current_track = 1
    
    def update_status():
        status_text = f"Volume: {volume}% | "
        status_text += f"État: {'En lecture' if is_playing else 'En pause'} | "
        status_text += f"Piste: {current_track}"
        status_label.config(text=status_text)
    
    def on_play_pause(event):
        nonlocal is_playing
        is_playing = not is_playing
        update_status()
        return "break"
    
    def on_next_track(event):
        nonlocal current_track
        current_track += 1
        update_status()
        return "break"
    
    def on_prev_track(event):
        nonlocal current_track
        current_track = max(1, current_track - 1)
        update_status()
        return "break"
    
    def on_volume_up(event):
        nonlocal volume
        volume = min(100, volume + 5)
        update_status()
        return "break"
    
    def on_volume_down(event):
        nonlocal volume
        volume = max(0, volume - 5)
        update_status()
        return "break"
    
    # Interface
    tk.Label(root, text="Test des raccourcis clavier", font=("Arial", 16, "bold")).pack(pady=20)
    
    instructions = """
    Raccourcis à tester:
    
    Ctrl+Alt+P : Play/Pause
    Ctrl+Alt+N : Piste suivante
    Ctrl+Alt+B : Piste précédente
    Ctrl+Alt+↑ : Volume +
    Ctrl+Alt+↓ : Volume -
    """
    
    tk.Label(root, text=instructions, justify="left", font=("Arial", 10)).pack(pady=10)
    
    status_label = tk.Label(root, text="", font=("Arial", 12, "bold"), fg="blue")
    status_label.pack(pady=20)
    
    # Bindings
    root.bind('<Control-Alt-p>', on_play_pause)
    root.bind('<Control-Alt-P>', on_play_pause)
    root.bind('<Control-Alt-n>', on_next_track)
    root.bind('<Control-Alt-N>', on_next_track)
    root.bind('<Control-Alt-b>', on_prev_track)
    root.bind('<Control-Alt-B>', on_prev_track)
    root.bind('<Control-Alt-Up>', on_volume_up)
    root.bind('<Control-Alt-Down>', on_volume_down)
    
    # Focus pour recevoir les événements clavier
    root.focus_set()
    
    # Statut initial
    update_status()
    
    root.mainloop()

if __name__ == "__main__":
    test_shortcuts()