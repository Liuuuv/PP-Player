#!/usr/bin/env python3
"""
Script de test pour toutes les nouvelles fonctionnalités
"""

import tkinter as tk
from tkinter import messagebox
import time

def test_keyboard_shortcuts():
    """Teste les raccourcis clavier"""
    root = tk.Tk()
    root.title("Test des raccourcis clavier")
    root.geometry("500x400")
    root.configure(bg='#2d2d2d')
    
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
        print(f"Raccourci Ctrl+Alt+P: {'Play' if is_playing else 'Pause'}")
        return "break"
    
    def on_next_track(event):
        nonlocal current_track
        current_track += 1
        update_status()
        print(f"Raccourci Ctrl+Alt+N: Piste {current_track}")
        return "break"
    
    def on_prev_track(event):
        nonlocal current_track
        current_track = max(1, current_track - 1)
        update_status()
        print(f"Raccourci Ctrl+Alt+B: Piste {current_track}")
        return "break"
    
    def on_volume_up(event):
        nonlocal volume
        volume = min(100, volume + 5)
        update_status()
        print(f"Raccourci Ctrl+Alt+↑: Volume {volume}%")
        return "break"
    
    def on_volume_down(event):
        nonlocal volume
        volume = max(0, volume - 5)
        update_status()
        print(f"Raccourci Ctrl+Alt+↓: Volume {volume}%")
        return "break"
    
    # Interface
    title_label = tk.Label(
        root, 
        text="Test des raccourcis clavier", 
        font=("Arial", 16, "bold"),
        bg='#2d2d2d',
        fg='white'
    )
    title_label.pack(pady=20)
    
    instructions = """
    Raccourcis à tester:
    
    Ctrl+Alt+P : Play/Pause
    Ctrl+Alt+N : Piste suivante
    Ctrl+Alt+B : Piste précédente
    Ctrl+Alt+↑ : Volume +5%
    Ctrl+Alt+↓ : Volume -5%
    
    Les actions s'affichent dans la console
    """
    
    instructions_label = tk.Label(
        root, 
        text=instructions, 
        justify="left", 
        font=("Arial", 10),
        bg='#2d2d2d',
        fg='white'
    )
    instructions_label.pack(pady=10)
    
    status_label = tk.Label(
        root, 
        text="", 
        font=("Arial", 12, "bold"), 
        fg="#4a8fe7",
        bg='#2d2d2d'
    )
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
    
    # Bouton pour fermer
    close_btn = tk.Button(
        root,
        text="Fermer",
        command=root.destroy,
        bg='#d32f2f',
        fg='white',
        font=("Arial", 10),
        padx=20,
        pady=5
    )
    close_btn.pack(pady=20)
    
    print("=== Test des raccourcis clavier ===")
    print("Utilisez les raccourcis dans la fenêtre de test")
    
    root.mainloop()

def test_import_dialog():
    """Teste la boîte de dialogue d'import"""
    print("\n=== Test de la boîte de dialogue d'import ===")
    
    # URLs de test
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H9EB2XA4",
        "https://music.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H9EB2XA4",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://invalid-url.com"
    ]
    
    # Simuler la détection d'URL
    def clean_youtube_url(url):
        if "music.youtube.com" in url:
            url = url.replace("music.youtube.com", "youtube.com")
        return url
    
    def detect_url_type(url):
        if not url.strip():
            return "Entrez une URL"
        
        url = clean_youtube_url(url)
        
        if "youtube.com" not in url and "youtu.be" not in url:
            return "URL non supportée"
        
        if "playlist?list=" in url or "&list=" in url:
            return "Playlist détectée"
        else:
            return "Vidéo détectée"
    
    for url in test_urls:
        cleaned = clean_youtube_url(url)
        detected = detect_url_type(url)
        print(f"URL: {url}")
        print(f"  Nettoyée: {cleaned}")
        print(f"  Type détecté: {detected}")
        print()

def main():
    """Fonction principale de test"""
    print("=== Test des nouvelles fonctionnalités ===")
    
    # Test de détection d'URL
    test_import_dialog()
    
    # Demander si l'utilisateur veut tester les raccourcis
    response = input("Voulez-vous tester les raccourcis clavier ? (o/n): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        test_keyboard_shortcuts()
    
    print("\n=== Tests terminés ===")
    print("Pour tester l'onglet téléchargements, lancez: python test_downloads_tab.py")
    print("Pour tester l'application complète, lancez: python main.py")

if __name__ == "__main__":
    main()