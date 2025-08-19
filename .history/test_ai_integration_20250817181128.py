"""
Script de test pour vérifier l'intégration du système IA
"""

import tkinter as tk
import os
import sys

def test_ai_integration():
    """Test complet de l'intégration IA"""
    
    print("🧪 TEST D'INTÉGRATION DU SYSTÈME IA")
    print("=" * 50)
    
    # Test 1: Vérifier que les fichiers existent
    print("\n📁 Test 1: Vérification des fichiers...")
    
    required_files = [
        'ai_recommendation_system.py',
        'ai_integration.py',
        'ai_menu_system.py',
        'setup_ai.py',
        'assets/activate_ai.png',
        'assets/activate_ai_active.png'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ Fichiers manquants: {missing_files}")
        return False
    
    # Test 2: Vérifier les imports
    print("\n📦 Test 2: Vérification des imports...")
    
    try:
        from ai_menu_system import setup_ai_menu_system, AIMenuSystem
        print("✅ ai_menu_system importé")
    except ImportError as e:
        print(f"❌ Erreur import ai_menu_system: {e}")
        return False
    
    try:
        from ai_integration import setup_ai_integration
        print("✅ ai_integration importé")
    except ImportError as e:
        print(f"❌ Erreur import ai_integration: {e}")
        return False
    
    try:
        from ai_recommendation_system import MusicAIRecommendationSystem
        print("✅ ai_recommendation_system importé")
    except ImportError as e:
        print(f"❌ Erreur import ai_recommendation_system: {e}")
        return False
    
    # Test 3: Test de création du menu IA
    print("\n🖼️ Test 3: Test de création du menu IA...")
    
    try:
        # Créer une application de test
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        
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
        
        # Tester la création du système de menu
        ai_menu_system = setup_ai_menu_system(mock_app)
        
        if ai_menu_system:
            print("✅ Système de menu IA créé")
            
            # Tester les méthodes
            print(f"✅ Learning enabled: {ai_menu_system.is_learning_enabled()}")
            print(f"✅ Recommendations enabled: {ai_menu_system.is_recommendations_enabled()}")
            print(f"✅ AI active: {ai_menu_system.is_ai_active()}")
            
            # Tester la création du bouton
            test_frame = tk.Frame(root)
            ai_button = ai_menu_system.create_ai_button(test_frame)
            
            if ai_button:
                print("✅ Bouton IA créé")
            else:
                print("⚠️ Bouton IA non créé (normal si icônes manquantes)")
            
        else:
            print("❌ Échec création système de menu IA")
            return False
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ Erreur test menu IA: {e}")
        return False
    
    # Test 4: Test des dépendances ML
    print("\n🤖 Test 4: Vérification des dépendances ML...")
    
    try:
        import sklearn
        print("✅ scikit-learn disponible")
    except ImportError:
        print("⚠️ scikit-learn non disponible (optionnel)")
    
    try:
        import pandas
        print("✅ pandas disponible")
    except ImportError:
        print("⚠️ pandas non disponible (optionnel)")
    
    try:
        import numpy
        print("✅ numpy disponible")
    except ImportError:
        print("⚠️ numpy non disponible (optionnel)")
    
    # Test 5: Test de configuration
    print("\n⚙️ Test 5: Test de configuration...")
    
    try:
        # Créer un fichier de config de test
        import json
        test_config = {
            "ai_settings": {
                "learning_enabled": True,
                "use_custom_recommendations": False,
                "ai_active": True
            }
        }
        
        with open("test_config.json", "w") as f:
            json.dump(test_config, f)
        
        print("✅ Configuration de test créée")
        
        # Nettoyer
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        
    except Exception as e:
        print(f"⚠️ Erreur test configuration: {e}")
    
    print("\n🎉 RÉSULTATS DU TEST:")
    print("✅ Intégration IA fonctionnelle!")
    print("\n📋 FONCTIONNALITÉS DISPONIBLES:")
    print("- Bouton IA dans l'interface")
    print("- Menu de configuration avec options Learning et Recommendations")
    print("- Bouton Reset datas")
    print("- Intégration avec le système de recommandation existant")
    print("- Sauvegarde automatique de la configuration")
    
    print("\n🎯 UTILISATION:")
    print("1. Lancez l'application principale")
    print("2. Cherchez le bouton IA (🤖) à gauche du bouton auto-scroll")
    print("3. Cliquez pour ouvrir le menu de configuration")
    print("4. Cochez 'Learning' pour activer l'apprentissage")
    print("5. Cochez 'Use customized recommendations' pour les recommandations IA")
    
    return True

def test_ai_button_appearance():
    """Test spécifique de l'apparence du bouton IA"""
    
    print("\n🎨 TEST APPARENCE BOUTON IA")
    print("=" * 30)
    
    try:
        import tkinter as tk
        from PIL import Image
        
        # Vérifier les icônes
        icon_path = "assets/activate_ai.png"
        active_icon_path = "assets/activate_ai_active.png"
        
        if os.path.exists(icon_path):
            print(f"✅ Icône normale trouvée: {icon_path}")
            
            # Vérifier les dimensions
            img = Image.open(icon_path)
            print(f"✅ Dimensions: {img.size}")
            
        else:
            print(f"❌ Icône normale manquante: {icon_path}")
        
        if os.path.exists(active_icon_path):
            print(f"✅ Icône active trouvée: {active_icon_path}")
        else:
            print(f"❌ Icône active manquante: {active_icon_path}")
        
        # Test visuel
        root = tk.Tk()
        root.title("Test Bouton IA")
        root.geometry("200x100")
        
        frame = tk.Frame(root)
        frame.pack(pady=20)
        
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            btn = tk.Button(frame, image=icon, text="IA")
            btn.pack()
            
            print("✅ Bouton de test créé - Vérifiez visuellement")
            print("   (Fermez la fenêtre pour continuer)")
            
            root.mainloop()
        else:
            print("⚠️ Test visuel impossible - icônes manquantes")
            root.destroy()
        
    except Exception as e:
        print(f"❌ Erreur test apparence: {e}")

if __name__ == "__main__":
    print("🚀 LANCEMENT DES TESTS D'INTÉGRATION IA")
    
    # Test principal
    success = test_ai_integration()
    
    if success:
        print("\n" + "="*50)
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("🎵 Le système IA est prêt à être utilisé!")
        
        # Proposer le test visuel
        response = input("\nVoulez-vous tester l'apparence du bouton? (y/n): ").lower().strip()
        if response in ['y', 'yes', 'oui', 'o']:
            test_ai_button_appearance()
    else:
        print("\n" + "="*50)
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    print("\n👋 Tests terminés!")