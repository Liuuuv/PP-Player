"""
Test réaliste de la persistance des paramètres IA
Simule l'environnement réel de l'application
"""

import os
import json
import tkinter as tk
from ai_menu_system import AIMenuSystem

class RealisticTestApp:
    """Simulation réaliste de l'application principale"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Simuler l'environnement réel
        self.downloads_folder = os.path.join(os.getcwd(), "test_downloads")
        os.makedirs(self.downloads_folder, exist_ok=True)
        self.config_file = os.path.join(self.downloads_folder, "player_config.json")
        
        print(f"📁 Dossier de test: {self.downloads_folder}")
        print(f"📄 Fichier config: {self.config_file}")

def test_realistic_scenario():
    """Test avec l'environnement réaliste"""
    print("🎯 TEST RÉALISTE : Persistance des paramètres IA")
    print("=" * 60)
    
    # Nettoyer l'environnement de test
    test_downloads = os.path.join(os.getcwd(), "test_downloads")
    config_file = os.path.join(test_downloads, "player_config.json")
    if os.path.exists(config_file):
        os.remove(config_file)
        print("🧹 Ancien fichier de config supprimé")
    
    # Étape 1 : Premier lancement
    print("\n1️⃣ Premier lancement - Configuration vide")
    app1 = RealisticTestApp()
    ai1 = AIMenuSystem(app1)
    
    print(f"   Learning initial: {ai1.ai_config['learning_enabled']}")
    print(f"   Recommendations initial: {ai1.ai_config['use_custom_recommendations']}")
    print(f"   Fichier config existe: {os.path.exists(app1.config_file)}")
    
    # Étape 2 : Utilisateur active Learning
    print("\n2️⃣ Utilisateur active Learning")
    ai1.learning_var.set(True)
    ai1.on_learning_changed()
    
    print(f"   Learning: {ai1.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai1.ai_config['use_custom_recommendations']}")
    print(f"   Fichier config existe maintenant: {os.path.exists(app1.config_file)}")
    
    # Vérifier le contenu du fichier
    if os.path.exists(app1.config_file):
        with open(app1.config_file, 'r', encoding='utf-8') as f:
            config_content = json.load(f)
        print(f"   Contenu sauvegardé: {config_content.get('ai_settings', {})}")
    
    # Étape 3 : Fermeture
    print("\n3️⃣ Fermeture de l'application")
    ai1.save_ai_config()
    app1.root.destroy()
    print("   ✅ Application fermée")
    
    # Étape 4 : Réouverture
    print("\n4️⃣ Réouverture de l'application")
    app2 = RealisticTestApp()
    print(f"   Fichier config trouvé: {os.path.exists(app2.config_file)}")
    
    if os.path.exists(app2.config_file):
        with open(app2.config_file, 'r', encoding='utf-8') as f:
            config_content = json.load(f)
        print(f"   Contenu à charger: {config_content.get('ai_settings', {})}")
    
    ai2 = AIMenuSystem(app2)
    
    print(f"   Learning restauré: {ai2.ai_config['learning_enabled']}")
    print(f"   Recommendations restauré: {ai2.ai_config['use_custom_recommendations']}")
    print(f"   Variable Learning: {ai2.learning_var.get()}")
    print(f"   Variable Recommendations: {ai2.recommendations_var.get()}")
    
    # Étape 5 : Utilisateur active aussi Recommendations
    print("\n5️⃣ Utilisateur active aussi Recommendations")
    ai2.recommendations_var.set(True)
    ai2.on_recommendations_changed()
    
    print(f"   Learning: {ai2.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai2.ai_config['use_custom_recommendations']}")
    
    # Étape 6 : Nouvelle fermeture/réouverture
    print("\n6️⃣ Nouvelle fermeture et réouverture")
    ai2.save_ai_config()
    app2.root.destroy()
    
    app3 = RealisticTestApp()
    ai3 = AIMenuSystem(app3)
    
    print(f"   Learning final: {ai3.ai_config['learning_enabled']}")
    print(f"   Recommendations final: {ai3.ai_config['use_custom_recommendations']}")
    print(f"   Variable Learning finale: {ai3.learning_var.get()}")
    print(f"   Variable Recommendations finale: {ai3.recommendations_var.get()}")
    
    # Vérification finale
    success = (
        ai3.ai_config['learning_enabled'] == True and
        ai3.ai_config['use_custom_recommendations'] == True and
        ai3.learning_var.get() == True and
        ai3.recommendations_var.get() == True
    )
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST RÉUSSI !")
        print("✅ Les paramètres IA sont parfaitement persistants")
        print("✅ L'utilisateur retrouve toujours ses paramètres")
        
        # Afficher le fichier final
        if os.path.exists(app3.config_file):
            with open(app3.config_file, 'r', encoding='utf-8') as f:
                final_config = json.load(f)
            print(f"✅ Configuration finale: {final_config.get('ai_settings', {})}")
    else:
        print("❌ TEST ÉCHOUÉ")
        print(f"   Attendu: Learning=True, Recommendations=True")
        print(f"   Obtenu: Learning={ai3.ai_config['learning_enabled']}, Recommendations={ai3.ai_config['use_custom_recommendations']}")
    
    # Nettoyer
    app3.root.destroy()
    
    return success

def cleanup_test_environment():
    """Nettoie l'environnement de test"""
    test_downloads = os.path.join(os.getcwd(), "test_downloads")
    if os.path.exists(test_downloads):
        import shutil
        shutil.rmtree(test_downloads)
        print("🧹 Environnement de test nettoyé")

if __name__ == "__main__":
    print("🚀 TEST RÉALISTE DE PERSISTANCE DES PARAMÈTRES IA")
    print("🎯 Simulation de l'environnement réel de l'application")
    print()
    
    try:
        success = test_realistic_scenario()
        
        print("\n" + "=" * 60)
        print("📋 RÉSUMÉ FINAL")
        print("=" * 60)
        
        if success:
            print("🎉 MISSION ACCOMPLIE !")
            print()
            print("✅ FONCTIONNALITÉS CONFIRMÉES :")
            print("• Sauvegarde automatique des paramètres IA")
            print("• Chargement automatique au démarrage")
            print("• Persistance parfaite entre les sessions")
            print("• Synchronisation des variables tkinter")
            print()
            print("👤 EXPÉRIENCE UTILISATEUR :")
            print("• L'utilisateur active Learning et/ou Recommendations")
            print("• Il ferme l'application")
            print("• Il rouvre l'application")
            print("• Ses paramètres sont EXACTEMENT comme il les avait laissés")
            print()
            print("🎯 RÉSULTAT : Persistance parfaite des paramètres IA !")
        else:
            print("❌ Des problèmes subsistent")
            print("⚠️ La persistance n'est pas complètement fonctionnelle")
        
    finally:
        cleanup_test_environment()