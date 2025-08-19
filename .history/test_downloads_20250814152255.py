#!/usr/bin/env python3
"""
Script de test pour l'onglet téléchargements
Utilise Ctrl+Alt+T pour ajouter des téléchargements de test
"""

import tkinter as tk
from main import MusicPlayer

def main():
    root = tk.Tk()
    app = MusicPlayer(root)
    
    # Ajouter des téléchargements de test après un court délai
    def add_test_downloads():
        print("Ajout de téléchargements de test...")
        app.add_test_downloads()
        print("Téléchargements de test ajoutés. Utilisez Ctrl+Alt+T pour en ajouter d'autres.")
    
    # Programmer l'ajout après 2 secondes
    root.after(2000, add_test_downloads)
    
    print("Application lancée. Utilisez Ctrl+Alt+T pour ajouter des téléchargements de test.")
    print("Allez dans l'onglet 'Téléchargements' pour voir les résultats.")
    
    root.mainloop()

if __name__ == "__main__":
    main()