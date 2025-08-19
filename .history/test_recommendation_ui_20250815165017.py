#!/usr/bin/env python3
"""
Script de test pour l'interface utilisateur des recommandations
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import os

class TestRecommendationUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Recommandation UI")
        self.root.geometry("400x300")
        self.root.configure(bg='#2d2d2d')
        
        # Variables d'état
        self.recommendation_enabled = False
        self.recommendation_mode = "sparse"
        self.last_recommendation_mode = "sparse"
        
        # Charger les icônes
        self.load_icons()
        
        # Créer l'interface
        self.create_ui()
        
    def load_icons(self):
        """Charge les icônes de recommandation"""
        self.icons = {}
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        
        icon_files = [
            "recommendation.png",
            "sparse_recommendation.png", 
            "add_recommendation.png"
        ]
        
        for icon_file in icon_files:
            try:
                path = os.path.join(assets_dir, icon_file)
                if os.path.exists(path):
                    image = Image.open(path).resize((32, 32), Image.Resampling.LANCZOS)
                    key = icon_file.replace('.png', '')
                    self.icons[key] = ImageTk.PhotoImage(image)
                    print(f"Icône chargée: {key}")
                else:
                    print(f"Icône manquante: {path}")
            except Exception as e:
                print(f"Erreur chargement {icon_file}: {e}")
    
    def create_ui(self):
        """Crée l'interface de test"""
        # Frame principale
        main_frame = tk.Frame(self.root, bg='#2d2d2d')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Titre
        title_label = tk.Label(
            main_frame, 
            text="Test du bouton de recommandations",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=10)
        
        # Frame pour le bouton
        button_frame = tk.Frame(main_frame, bg='#2d2d2d')
        button_frame.pack(pady=20)
        
        # Bouton de recommandations
        self.recommendation_button = tk.Button(
            button_frame,
            image=self.icons.get("recommendation"),
            bg="#3d3d3d",
            fg="white",
            activebackground="#4a4a4a",
            relief="flat",
            bd=0,
            width=40,
            height=40,
            cursor='hand2'
        )
        self.recommendation_button.pack()
        
        # Bind des événements
        self.recommendation_button.bind("<Button-1>", self.on_recommendation_left_click)
        self.recommendation_button.bind("<Button-3>", self.on_recommendation_right_click)
        self.recommendation_button.bind("<Enter>", self.on_recommendation_hover_enter)
        self.recommendation_button.bind("<Leave>", self.on_recommendation_hover_leave)
        
        # Labels d'information
        self.status_label = tk.Label(
            main_frame,
            text="État: Désactivé",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 10)
        )
        self.status_label.pack(pady=5)
        
        self.mode_label = tk.Label(
            main_frame,
            text="Mode: sparse",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 10)
        )
        self.mode_label.pack(pady=5)
        
        # Instructions
        instructions = tk.Text(
            main_frame,
            height=8,
            width=50,
            bg='#3d3d3d',
            fg='white',
            font=('Arial', 9)
        )
        instructions.pack(pady=10)
        
        instructions.insert('1.0', """Instructions de test:

1. Clic gauche: Active/désactive les recommandations
2. Clic droit: Ouvre le menu de sélection du mode
3. Survol: Aperçu du dernier mode quand désactivé
4. Menu: Sélectionner "éparses" ou "à la suite"

États attendus:
- Désactivé: Icône grise (R)
- Éparses: Icône verte (S)  
- À la suite: Icône bleue (A)""")
        
        instructions.config(state='disabled')
    
    def on_recommendation_left_click(self, event):
        """Gère le clic gauche"""
        if self.recommendation_enabled:
            # Désactiver
            self.recommendation_enabled = False
            self.recommendation_button.config(image=self.icons.get("recommendation"))
            self.status_label.config(text="État: Désactivé")
            print("Recommandations désactivées")
        else:
            # Activer avec le dernier mode
            self.recommendation_enabled = True
            self.recommendation_mode = self.last_recommendation_mode
            self._update_button_icon()
            self.status_label.config(text=f"État: Activé ({self.recommendation_mode})")
            print(f"Recommandations activées ({self.recommendation_mode})")
    
    def on_recommendation_right_click(self, event):
        """Gère le clic droit - menu contextuel"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Activer les recommandations", state="disabled")
        menu.add_separator()
        
        # Variables pour les cases à cocher
        sparse_var = tk.BooleanVar()
        add_var = tk.BooleanVar()
        
        # Cocher selon le mode actuel
        if self.recommendation_mode == "sparse":
            sparse_var.set(True)
        else:
            add_var.set(True)
        
        menu.add_checkbutton(
            label="éparses",
            variable=sparse_var,
            command=lambda: self._set_mode("sparse", sparse_var, add_var)
        )
        menu.add_checkbutton(
            label="à la suite",
            variable=add_var,
            command=lambda: self._set_mode("add", sparse_var, add_var)
        )
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _set_mode(self, mode, sparse_var, add_var):
        """Définit le mode de recommandation"""
        # Une seule option cochée
        if mode == "sparse":
            sparse_var.set(True)
            add_var.set(False)
        else:
            sparse_var.set(False)
            add_var.set(True)
        
        self.recommendation_mode = mode
        self.last_recommendation_mode = mode
        self.recommendation_enabled = True
        
        self._update_button_icon()
        self.status_label.config(text=f"État: Activé ({mode})")
        self.mode_label.config(text=f"Mode: {mode}")
        print(f"Mode défini: {mode}")
    
    def _update_button_icon(self):
        """Met à jour l'icône du bouton"""
        if self.recommendation_enabled:
            if self.recommendation_mode == "sparse":
                icon_key = "sparse_recommendation"
            else:
                icon_key = "add_recommendation"
        else:
            icon_key = "recommendation"
        
        self.recommendation_button.config(image=self.icons.get(icon_key))
    
    def on_recommendation_hover_enter(self, event):
        """Survol - aperçu du mode"""
        if not self.recommendation_enabled:
            if self.last_recommendation_mode == "sparse":
                icon_key = "sparse_recommendation"
            else:
                icon_key = "add_recommendation"
            self.recommendation_button.config(image=self.icons.get(icon_key))
            print(f"Aperçu: {self.last_recommendation_mode}")
    
    def on_recommendation_hover_leave(self, event):
        """Fin du survol"""
        if not self.recommendation_enabled:
            self.recommendation_button.config(image=self.icons.get("recommendation"))
    
    def run(self):
        """Lance l'interface de test"""
        print("=== Test de l'interface de recommandations ===")
        print("Testez les différentes interactions avec le bouton")
        self.root.mainloop()

if __name__ == "__main__":
    test_ui = TestRecommendationUI()
    test_ui.run()