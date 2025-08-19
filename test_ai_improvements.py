"""
Test des améliorations IA : analyse intelligente des skips et statistiques détaillées
"""

import tkinter as tk
from ai_menu_system import setup_ai_menu_system
import os
import time

def test_ai_improvements():
    """Test des nouvelles fonctionnalités IA"""
    
    print("🧪 TEST DES AMÉLIORATIONS IA")
    print("=" * 50)
    
    # Créer une application de test
    root = tk.Tk()
    root.title("Test Améliorations IA")
    root.geometry("500x400")
    root.configure(bg="#2d2d2d")
    
    class MockApp:
        def __init__(self):
            self.root = root
            self.config_file = "test_config.json"
            self.main_playlist = ["song1.mp3", "song2.mp3", "song3.mp3"]
            self.current_index = 1
            self.volume = 0.5
            self.liked_songs = set()
            self.favorite_songs = set()
    
    mock_app = MockApp()
    
    # Créer le système de menu IA
    ai_menu_system = setup_ai_menu_system(mock_app)
    
    if ai_menu_system:
        # Activer le learning pour initialiser le système IA
        ai_menu_system.ai_config['learning_enabled'] = True
        ai_menu_system.learning_var.set(True)
        ai_menu_system.initialize_ai_system()
        
    if ai_menu_system and ai_menu_system.ai_system:
        ai_system = ai_menu_system.ai_system
        
        # Simuler des données d'écoute pour tester
        print("\n📊 Simulation de données d'écoute...")
        
        # Simuler différents types de skips
        test_songs = [
            ("test_song_1.mp3", 0.02, True),   # Skip immédiat
            ("test_song_2.mp3", 0.12, True),   # Skip précoce
            ("test_song_3.mp3", 0.45, True),   # Skip moyen
            ("test_song_4.mp3", 0.85, True),   # Skip tardif (navigation?)
            ("test_song_5.mp3", 0.95, False),  # Écoute complète
        ]
        
        for song_path, listening_ratio, was_skipped in test_songs:
            # Simuler le début de la chanson
            ai_system.on_song_start(song_path)
            
            # Simuler la fin avec skip ou écoute complète
            ai_system.on_song_end(song_path, was_skipped=was_skipped, 
                                listening_duration=listening_ratio * 180)  # 3 min de base
            
            time.sleep(0.1)  # Petit délai pour simuler le temps
        
        # Simuler des likes
        ai_system.update_song_statistics("test_song_5.mp3", 'like', {})
        ai_system.update_song_statistics("test_song_3.mp3", 'like', {})
        
        # Simuler des prédictions IA
        for song_path in ["test_song_1.mp3", "test_song_2.mp3", "test_song_5.mp3"]:
            fake_predictions = {
                'skip_probability': 0.8 if "1" in song_path else 0.3 if "5" in song_path else 0.6,
                'like_probability': 0.2 if "1" in song_path else 0.8 if "5" in song_path else 0.4,
                'ai_score': 0.3 if "1" in song_path else 0.7 if "5" in song_path else 0.5
            }
            ai_system.update_song_statistics(song_path, 'prediction', fake_predictions)
        
        print("✅ Données de test générées")
        
        # Créer l'interface de test
        main_frame = tk.Frame(root, bg="#2d2d2d")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        title_label = tk.Label(
            main_frame,
            text="🤖 Test des Améliorations IA",
            font=("Arial", 16, "bold"),
            bg="#2d2d2d",
            fg="white"
        )
        title_label.pack(pady=(0, 20))
        
        # Bouton IA
        ai_button = ai_menu_system.create_ai_button(main_frame)
        if ai_button:
            ai_button.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Cliquez sur le bouton 🤖 puis sur '📊 Show AI insights'\npour voir les nouvelles statistiques détaillées",
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 12),
            justify="center"
        )
        instructions.pack(pady=10)
        
        # Informations sur les données de test
        info_frame = tk.LabelFrame(
            main_frame,
            text="📋 Données de Test Générées",
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 10, "bold")
        )
        info_frame.pack(fill="x", pady=10)
        
        info_text = """• test_song_1.mp3: Skip immédiat (2% écouté) - IA prédit skip élevé
• test_song_2.mp3: Skip précoce (12% écouté) - IA prédit skip moyen  
• test_song_3.mp3: Skip moyen (45% écouté) + Like - IA prédit skip moyen
• test_song_4.mp3: Skip tardif (85% écouté) - Possible navigation
• test_song_5.mp3: Écoute complète (95% écouté) + Like - IA prédit like élevé"""
        
        tk.Label(
            info_frame,
            text=info_text,
            bg="#2d2d2d",
            fg="#cccccc",
            font=("Arial", 9),
            justify="left"
        ).pack(anchor="w", padx=10, pady=5)
        
        # Fonctionnalités testées
        features_frame = tk.LabelFrame(
            main_frame,
            text="🎯 Nouvelles Fonctionnalités",
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 10, "bold")
        )
        features_frame.pack(fill="x", pady=10)
        
        features_text = """✅ Analyse intelligente des skips (immédiat, précoce, navigation, etc.)
✅ Statistiques détaillées par chanson avec scores IA
✅ Prédictions de skip et like avec codes couleur
✅ Scores de satisfaction utilisateur calculés automatiquement
✅ Interface améliorée avec tableau scrollable"""
        
        tk.Label(
            features_frame,
            text=features_text,
            bg="#2d2d2d",
            fg="#cccccc",
            font=("Arial", 9),
            justify="left"
        ).pack(anchor="w", padx=10, pady=5)
        
        print("\n🎯 FONCTIONNALITÉS À TESTER:")
        print("1. Menu contextuel avec clic droit sur le bouton IA")
        print("2. Option 'Show AI insights' pour voir les statistiques")
        print("3. Tableau des chansons avec scores colorés")
        print("4. Analyse des différents types de skip")
        print("5. Prédictions IA vs comportement utilisateur")
        
        root.mainloop()
        
    else:
        print("❌ Échec initialisation système IA")
        root.destroy()

if __name__ == "__main__":
    test_ai_improvements()