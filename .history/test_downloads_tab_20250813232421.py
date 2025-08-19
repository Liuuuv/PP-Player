#!/usr/bin/env python3
"""
Script de test pour l'onglet téléchargements
"""

import tkinter as tk
from tkinter import ttk
import downloads_tab

class MockMusicPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Onglet Téléchargements")
        self.root.geometry("800x600")
        self.root.configure(bg='#2d2d2d')
        
        # Créer un notebook pour simuler l'interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurer l'onglet téléchargements
        self.setup_downloads_tab()
        
        # Boutons de test
        test_frame = tk.Frame(self.root, bg='#2d2d2d')
        test_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            test_frame,
            text="Ajouter téléchargement test",
            command=self.add_test_download,
            bg='#4a8fe7',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            test_frame,
            text="Simuler progression",
            command=self.simulate_progress,
            bg='#4a8fe7',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        self.test_counter = 0
    
    def setup_downloads_tab(self):
        return downloads_tab.setup_downloads_tab(self)
    
    def add_download_to_tab(self, url, title):
        return downloads_tab.add_download_to_tab(self, url, title)
    
    def update_download_progress(self, url, progress, status=None):
        return downloads_tab.update_download_progress(self, url, progress, status)
    
    def simulate_download_progress(self, url):
        return downloads_tab.simulate_download_progress(self, url)
    
    def cancel_download(self, url):
        return downloads_tab.cancel_download(self, url)
    
    def remove_completed_download(self, url):
        return downloads_tab.remove_completed_download(self, url)
    
    def update_downloads_display(self):
        return downloads_tab.update_downloads_display(self)
    
    def create_download_item(self, url, title, progress=0.0, status="En attente..."):
        return downloads_tab.create_download_item(self, url, title, progress, status)
    
    def add_test_download(self):
        self.test_counter += 1
        url = f"https://youtube.com/watch?v=test{self.test_counter}"
        title = f"Musique de test {self.test_counter}"
        self.add_download_to_tab(url, title)
    
    def simulate_progress(self):
        # Simuler la progression pour tous les téléchargements actifs
        if hasattr(self, 'download_manager'):
            for url in list(self.download_manager.active_downloads.keys()):
                self.simulate_download_progress(url)

def test_downloads_tab():
    app = MockMusicPlayer()
    app.root.mainloop()

if __name__ == "__main__":
    test_downloads_tab()