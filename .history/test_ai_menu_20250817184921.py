"""
Test du nouveau système de menu IA avec tk.Menu
"""

import tkinter as tk
from ai_menu_system import setup_ai_menu_system

def test_ai_menu():
    """Test du menu contextuel IA"""
    
    print("🧪 TEST DU MENU CONTEXTUEL IA")
    print("=" * 40)
    
    # Créer une application de test
    root = tk.Tk()
    root.title("Test Menu IA")
    root.geometry("400x300")
    root.configure(bg="#2d2d2d")
    
    class MockApp:
        def __init__(self):
            self.root = root
            self.config_file = "test_config.json"
            self.main_playlist = []
            self.current_index = 0
            self.volume = 0.5
            self.liked_songs = set()
            self.favorite_songs = set()
    
    mock_app = MockApp()
    
    # Créer le système de menu IA
    ai_menu_system = setup_ai_menu_system(mock_app)
    
    if ai_menu_system:
        # Créer un frame de test
        test_frame = tk.Frame(root, bg="#2d2d2d")
        test_frame.pack(pady=50)
        
        # Créer le bouton IA
        ai_button = ai_menu_system.create_ai_button(test_frame)
        if ai_button:
            ai_button.pack(pady=20)
            
            # Instructions
            instructions = tk.Label(
                test_frame,
                text="Cliquez sur le bouton 🤖 pour tester le menu contextuel",
                bg="#2d2d2d",
                fg="white",
                font=("Arial", 12)
            )
            instructions.pack(pady=10)
            
            # Statut
            status_label = tk.Label(
                test_frame,
                text="Statut: Menu prêt",
                bg="#2d2d2d",
                fg="#cccccc",
                font=("Arial", 10)
            )
            status_label.pack(pady=5)
            
            # Fonction pour mettre à jour le statut
            def update_status():
                learning = "✅" if ai_menu_system.is_learning_enabled() else "❌"
                recommendations = "✅" if ai_menu_system.is_recommendations_enabled() else "❌"
                active = "✅" if ai_menu_system.is_ai_active() else "❌"
                
                status_text = f"Learning: {learning} | Recommendations: {recommendations} | Active: {active}"
                status_label.config(text=status_text)
                
                # Programmer la prochaine mise à jour
                root.after(1000, update_status)
            
            # Démarrer les mises à jour de statut
            update_status()
            
            print("✅ Test configuré")
            print("📋 FONCTIONNALITÉS À TESTER:")
            print("1. Clic sur le bouton 🤖 pour ouvrir le menu")
            print("2. Cocher/décocher 'Learning'")
            print("3. Cocher/décocher 'Use customized recommendations'")
            print("4. Vérifier que le bouton devient bleu quand actif")
            print("5. Tester '📊 Show AI insights'")
            print("6. Tester '🗑️ Reset AI data'")
            print("\n🎯 Le bouton devrait changer de couleur selon l'état:")
            print("- Gris (#4a4a4a) : Inactif")
            print("- Bleu (#4a8fe7) : Actif")
            
            root.mainloop()
        else:
            print("❌ Échec création bouton IA")
            root.destroy()
    else:
        print("❌ Échec création système de menu IA")
        root.destroy()

if __name__ == "__main__":
    test_ai_menu()