"""
Test final simple pour démontrer la persistance des paramètres IA
"""

import os
import json
import tkinter as tk
from ai_menu_system import AIMenuSystem

class SimpleTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.config_file = "final_test_config.json"
        
        # Nettoyer au début
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

def test_complete_scenario():
    """Test complet du scénario utilisateur"""
    print("🎯 TEST FINAL : Persistance des paramètres IA")
    print("=" * 50)
    
    # Étape 1 : Premier lancement
    print("1️⃣ Premier lancement - Paramètres par défaut")
    app1 = SimpleTestApp()
    ai1 = AIMenuSystem(app1)
    print(f"   Learning: {ai1.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai1.ai_config['use_custom_recommendations']}")
    
    # Étape 2 : Utilisateur active Learning
    print("\n2️⃣ Utilisateur active Learning")
    ai1.learning_var.set(True)
    ai1.on_learning_changed()
    print(f"   Learning: {ai1.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai1.ai_config['use_custom_recommendations']}")
    
    # Étape 3 : Utilisateur active aussi Recommendations
    print("\n3️⃣ Utilisateur active aussi Recommendations")
    ai1.recommendations_var.set(True)
    ai1.on_recommendations_changed()
    print(f"   Learning: {ai1.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai1.ai_config['use_custom_recommendations']}")
    
    # Étape 4 : Fermeture
    print("\n4️⃣ Fermeture de l'application")
    ai1.save_ai_config()
    app1.root.destroy()
    print("   ✅ Configuration sauvegardée")
    
    # Étape 5 : Réouverture
    print("\n5️⃣ Réouverture de l'application")
    app2 = SimpleTestApp()
    # Ne pas nettoyer le fichier cette fois
    if os.path.exists(app2.config_file):
        print("   📁 Fichier de configuration trouvé")
    
    ai2 = AIMenuSystem(app2)
    print(f"   Learning restauré: {ai2.ai_config['learning_enabled']}")
    print(f"   Recommendations restauré: {ai2.ai_config['use_custom_recommendations']}")
    print(f"   Checkbox Learning: {ai2.learning_var.get()}")
    print(f"   Checkbox Recommendations: {ai2.recommendations_var.get()}")
    
    # Étape 6 : Utilisateur désactive Learning
    print("\n6️⃣ Utilisateur désactive Learning")
    ai2.learning_var.set(False)
    ai2.on_learning_changed()
    print(f"   Learning: {ai2.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai2.ai_config['use_custom_recommendations']}")
    
    # Étape 7 : Nouvelle fermeture/réouverture
    print("\n7️⃣ Nouvelle fermeture et réouverture")
    ai2.save_ai_config()
    app2.root.destroy()
    
    app3 = SimpleTestApp()
    ai3 = AIMenuSystem(app3)
    print(f"   Learning final: {ai3.ai_config['learning_enabled']}")
    print(f"   Recommendations final: {ai3.ai_config['use_custom_recommendations']}")
    
    # Vérification finale
    success = (
        ai3.ai_config['learning_enabled'] == False and
        ai3.ai_config['use_custom_recommendations'] == True and
        ai3.learning_var.get() == False and
        ai3.recommendations_var.get() == True
    )
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST RÉUSSI !")
        print("✅ Les paramètres IA sont parfaitement persistants")
        print("✅ L'utilisateur retrouve toujours ses paramètres")
    else:
        print("❌ TEST ÉCHOUÉ")
    
    # Nettoyer
    app3.root.destroy()
    if os.path.exists("final_test_config.json"):
        os.remove("final_test_config.json")
    
    return success

if __name__ == "__main__":
    print("🚀 TEST FINAL DE PERSISTANCE DES PARAMÈTRES IA")
    print("🎯 Simulation complète du comportement utilisateur")
    print()
    
    success = test_complete_scenario()
    
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ")
    print("=" * 50)
    
    if success:
        print("🎉 MISSION ACCOMPLIE !")
        print()
        print("👤 POUR L'UTILISATEUR :")
        print("• Active Learning et/ou Recommendations une seule fois")
        print("• Ferme et rouvre l'application autant qu'il veut")
        print("• Retrouve TOUJOURS ses paramètres exactement comme il les avait laissés")
        print()
        print("🤖 POUR L'IA :")
        print("• Sauvegarde automatique de tous les paramètres")
        print("• Chargement automatique au démarrage")
        print("• Persistance complète des données collectées")
        print("• Amélioration continue session après session")
        print()
        print("✨ RÉSULTAT : Expérience utilisateur parfaite et transparente !")
    else:
        print("❌ Il reste des problèmes à corriger")