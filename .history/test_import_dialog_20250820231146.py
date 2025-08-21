#!/usr/bin/env python3
"""
Test de la nouvelle boîte de dialogue d'import avec support HTML
"""

import tkinter as tk
from inputs import ImportDialog

class MockMusicPlayer:
    """Mock de l'application principale pour les tests"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Cacher la fenêtre principale
        
        # Mock des attributs nécessaires
        self.status_bar = tk.Label(self.root, text="Test")
        
    def show_dialog(self):
        dialog = ImportDialog(self.root, self)
        self.root.wait_window(dialog.dialog)

if __name__ == "__main__":
    app = MockMusicPlayer()
    app.show_dialog()
    app.root.destroy()