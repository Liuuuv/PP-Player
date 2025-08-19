#!/usr/bin/env python3
"""
Script de test pour la boîte de dialogue d'import
"""

import tkinter as tk
from inputs import ImportDialog

class MockMusicPlayer:
    def __init__(self):
        self.status_bar = None
        
    def _download_youtube_selection(self, urls, playlist):
        print(f"Mock download: {len(urls)} URLs vers '{playlist}'")
        for url in urls:
            print(f"  - {url}")

def test_import_dialog():
    root = tk.Tk()
    root.title("Test Import Dialog")
    root.geometry("300x200")
    root.configure(bg='#2d2d2d')
    
    # Mock music player
    mock_player = MockMusicPlayer()
    
    # Status bar mock
    status_label = tk.Label(root, text="Prêt", bg='#2d2d2d', fg='white')
    status_label.pack(side='bottom', fill='x')
    mock_player.status_bar = status_label
    
    def open_import_dialog():
        dialog = ImportDialog(root, mock_player)
        root.wait_window(dialog.dialog)
    
    # Bouton pour ouvrir la boîte de dialogue
    open_btn = tk.Button(
        root,
        text="Ouvrir Import Dialog",
        command=open_import_dialog,
        bg='#4a8fe7',
        fg='white',
        font=("Arial", 12),
        relief='flat',
        padx=20,
        pady=10
    )
    open_btn.pack(expand=True)
    
    # Instructions
    instructions = tk.Label(
        root,
        text="Testez avec différents types d'URLs:\n• Vidéo YouTube\n• Playlist YouTube\n• URL YouTube Music",
        bg='#2d2d2d',
        fg='white',
        font=("Arial", 9),
        justify='left'
    )
    instructions.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_import_dialog()