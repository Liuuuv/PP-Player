"""
Test spécifique pour vérifier la persistance des paramètres IA
Simule exactement le comportement utilisateur décrit
"""

import os
import json
import tkinter as tk
from ai_menu_system import AIMenuSystem

class MockMainApp:
    """Application simulée pour les tests"""
    def __init__(self, clean_config=False):
        self.root = tk.Tk()
        self.root.withdraw()  # Cacher la fenêtre de test
        self.config_file = "test_player_config.json"
        
        # Nettoyer le fichier de test seulement si demandé
        if clean_config and os.path.exists(self.config_file):
            os.remove(self.config_file)

def test_scenario_1_activate_learning():
    """Test : Utilisateur active Learning, ferme et rouvre l'app"""
    print("🧪 TEST 1 : Activation de Learning")
    print("=" * 50)
    
    # Étape 1 : Premier lancement (config vide)
    print("1️⃣ Premier lancement de l'application")
    app1 = MockMainApp(clean_config=True)  # Nettoyer au premier lancement
    ai_system1 = AIMenuSystem(app1)
    
    print(f"   Learning initial: {ai_system1.ai_config['learning_enabled']}")
    print(f"   Recommendations initial: {ai_system1.ai_config['use_custom_recommendations']}")
    
    # Étape 2 : Utilisateur active Learning
    print("\n2️⃣ Utilisateur active Learning")
    ai_system1.learning_var.set(True)
    ai_system1.on_learning_changed()
    
    print(f"   Learning après activation: {ai_system1.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai_system1.ai_config['use_custom_recommendations']}")
    
    # Étape 3 : Fermeture de l'application (sauvegarde automatique)
    print("\n3️⃣ Fermeture de l'application")
    ai_system1.save_ai_config()
    app1.root.destroy()
    print("   ✅ Configuration sauvegardée")
    
    # Étape 4 : Réouverture de l'application
    print("\n4️⃣ Réouverture de l'application")
    app2 = MockMainApp()
    ai_system2 = AIMenuSystem(app2)
    
    print(f"   Learning restauré: {ai_system2.ai_config['learning_enabled']}")
    print(f"   Recommendations restauré: {ai_system2.ai_config['use_custom_recommendations']}")
    print(f"   Variable tkinter Learning: {ai_system2.learning_var.get()}")
    print(f"   Variable tkinter Recommendations: {ai_system2.recommendations_var.get()}")
    
    # Vérification
    if (ai_system2.ai_config['learning_enabled'] == True and 
        ai_system2.ai_config['use_custom_recommendations'] == False and
        ai_system2.learning_var.get() == True and
        ai_system2.recommendations_var.get() == False):
        print("\n✅ TEST 1 RÉUSSI : Learning reste activé après redémarrage")
    else:
        print("\n❌ TEST 1 ÉCHOUÉ")
    
    app2.root.destroy()
    return ai_system2.ai_config['learning_enabled'] == True

def test_scenario_2_activate_recommendations():
    """Test : Utilisateur active Recommendations, ferme et rouvre l'app"""
    print("\n🧪 TEST 2 : Activation de Recommendations")
    print("=" * 50)
    
    # Étape 1 : Lancement avec Learning déjà activé
    print("1️⃣ Lancement avec Learning déjà activé")
    app1 = MockMainApp()
    ai_system1 = AIMenuSystem(app1)
    
    print(f"   Learning: {ai_system1.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai_system1.ai_config['use_custom_recommendations']}")
    
    # Étape 2 : Utilisateur active aussi Recommendations
    print("\n2️⃣ Utilisateur active aussi Recommendations")
    ai_system1.recommendations_var.set(True)
    ai_system1.on_recommendations_changed()
    
    print(f"   Learning: {ai_system1.ai_config['learning_enabled']}")
    print(f"   Recommendations après activation: {ai_system1.ai_config['use_custom_recommendations']}")
    
    # Étape 3 : Fermeture et réouverture
    print("\n3️⃣ Fermeture et réouverture")
    ai_system1.save_ai_config()
    app1.root.destroy()
    
    app2 = MockMainApp()
    ai_system2 = AIMenuSystem(app2)
    
    print(f"   Learning restauré: {ai_system2.ai_config['learning_enabled']}")
    print(f"   Recommendations restauré: {ai_system2.ai_config['use_custom_recommendations']}")
    print(f"   Variable tkinter Learning: {ai_system2.learning_var.get()}")
    print(f"   Variable tkinter Recommendations: {ai_system2.recommendations_var.get()}")
    
    # Vérification
    if (ai_system2.ai_config['learning_enabled'] == True and 
        ai_system2.ai_config['use_custom_recommendations'] == True and
        ai_system2.learning_var.get() == True and
        ai_system2.recommendations_var.get() == True):
        print("\n✅ TEST 2 RÉUSSI : Les deux options restent activées")
    else:
        print("\n❌ TEST 2 ÉCHOUÉ")
    
    app2.root.destroy()
    return (ai_system2.ai_config['learning_enabled'] == True and 
            ai_system2.ai_config['use_custom_recommendations'] == True)

def test_scenario_3_deactivate_learning():
    """Test : Utilisateur désactive Learning, ferme et rouvre l'app"""
    print("\n🧪 TEST 3 : Désactivation de Learning")
    print("=" * 50)
    
    # Étape 1 : Lancement avec les deux options activées
    print("1️⃣ Lancement avec les deux options activées")
    app1 = MockMainApp()
    ai_system1 = AIMenuSystem(app1)
    
    print(f"   Learning: {ai_system1.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai_system1.ai_config['use_custom_recommendations']}")
    
    # Étape 2 : Utilisateur désactive Learning
    print("\n2️⃣ Utilisateur désactive Learning")
    ai_system1.learning_var.set(False)
    ai_system1.on_learning_changed()
    
    print(f"   Learning après désactivation: {ai_system1.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai_system1.ai_config['use_custom_recommendations']}")
    
    # Étape 3 : Fermeture et réouverture
    print("\n3️⃣ Fermeture et réouverture")
    ai_system1.save_ai_config()
    app1.root.destroy()
    
    app2 = MockMainApp()
    ai_system2 = AIMenuSystem(app2)
    
    print(f"   Learning restauré: {ai_system2.ai_config['learning_enabled']}")
    print(f"   Recommendations restauré: {ai_system2.ai_config['use_custom_recommendations']}")
    print(f"   Variable tkinter Learning: {ai_system2.learning_var.get()}")
    print(f"   Variable tkinter Recommendations: {ai_system2.recommendations_var.get()}")
    
    # Vérification
    if (ai_system2.ai_config['learning_enabled'] == False and 
        ai_system2.ai_config['use_custom_recommendations'] == True and
        ai_system2.learning_var.get() == False and
        ai_system2.recommendations_var.get() == True):
        print("\n✅ TEST 3 RÉUSSI : Learning désactivé, Recommendations reste activé")
    else:
        print("\n❌ TEST 3 ÉCHOUÉ")
    
    app2.root.destroy()
    return (ai_system2.ai_config['learning_enabled'] == False and 
            ai_system2.ai_config['use_custom_recommendations'] == True)

def test_scenario_4_deactivate_all():
    """Test : Utilisateur désactive tout, ferme et rouvre l'app"""
    print("\n🧪 TEST 4 : Désactivation complète")
    print("=" * 50)
    
    # Étape 1 : Lancement avec Recommendations activé
    print("1️⃣ Lancement avec Recommendations activé")
    app1 = MockMainApp()
    ai_system1 = AIMenuSystem(app1)
    
    print(f"   Learning: {ai_system1.ai_config['learning_enabled']}")
    print(f"   Recommendations: {ai_system1.ai_config['use_custom_recommendations']}")
    
    # Étape 2 : Utilisateur désactive aussi Recommendations
    print("\n2️⃣ Utilisateur désactive aussi Recommendations")
    ai_system1.recommendations_var.set(False)
    ai_system1.on_recommendations_changed()
    
    print(f"   Learning: {ai_system1.ai_config['learning_enabled']}")
    print(f"   Recommendations après désactivation: {ai_system1.ai_config['use_custom_recommendations']}")
    print(f"   IA globalement active: {ai_system1.ai_config['ai_active']}")
    
    # Étape 3 : Fermeture et réouverture
    print("\n3️⃣ Fermeture et réouverture")
    ai_system1.save_ai_config()
    app1.root.destroy()
    
    app2 = MockMainApp()
    ai_system2 = AIMenuSystem(app2)
    
    print(f"   Learning restauré: {ai_system2.ai_config['learning_enabled']}")
    print(f"   Recommendations restauré: {ai_system2.ai_config['use_custom_recommendations']}")
    print(f"   IA globalement active: {ai_system2.ai_config['ai_active']}")
    print(f"   Variable tkinter Learning: {ai_system2.learning_var.get()}")
    print(f"   Variable tkinter Recommendations: {ai_system2.recommendations_var.get()}")
    
    # Vérification
    if (ai_system2.ai_config['learning_enabled'] == False and 
        ai_system2.ai_config['use_custom_recommendations'] == False and
        ai_system2.ai_config['ai_active'] == False and
        ai_system2.learning_var.get() == False and
        ai_system2.recommendations_var.get() == False):
        print("\n✅ TEST 4 RÉUSSI : Tout reste désactivé")
    else:
        print("\n❌ TEST 4 ÉCHOUÉ")
    
    app2.root.destroy()
    
    # Nettoyer le fichier de test
    if os.path.exists("test_player_config.json"):
        os.remove("test_player_config.json")
    
    return (ai_system2.ai_config['learning_enabled'] == False and 
            ai_system2.ai_config['use_custom_recommendations'] == False)

def verify_config_file_content():
    """Vérifie le contenu du fichier de configuration"""
    print("\n🔍 VÉRIFICATION DU FICHIER DE CONFIGURATION")
    print("=" * 50)
    
    config_file = "test_player_config.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("Contenu du fichier de configuration :")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        
        ai_settings = config.get('ai_settings', {})
        print(f"\nParamètres IA extraits :")
        print(f"  Learning: {ai_settings.get('learning_enabled', 'NON TROUVÉ')}")
        print(f"  Recommendations: {ai_settings.get('use_custom_recommendations', 'NON TROUVÉ')}")
        print(f"  IA Active: {ai_settings.get('ai_active', 'NON TROUVÉ')}")
    else:
        print("❌ Fichier de configuration non trouvé")

def main():
    """Fonction principale de test"""
    print("🚀 TEST COMPLET DE PERSISTANCE DES PARAMÈTRES IA")
    print("🎯 Objectif : Vérifier que les paramètres IA sont bien conservés")
    print("=" * 60)
    
    try:
        # Exécuter tous les tests
        test1_ok = test_scenario_1_activate_learning()
        test2_ok = test_scenario_2_activate_recommendations()
        test3_ok = test_scenario_3_deactivate_learning()
        test4_ok = test_scenario_4_deactivate_all()
        
        # Vérifier le fichier de configuration
        verify_config_file_content()
        
        # Résumé final
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        tests_results = [
            ("Activation Learning", test1_ok),
            ("Activation Recommendations", test2_ok),
            ("Désactivation Learning", test3_ok),
            ("Désactivation complète", test4_ok)
        ]
        
        all_passed = True
        for test_name, result in tests_results:
            status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 TOUS LES TESTS RÉUSSIS !")
            print("✅ Les paramètres IA sont correctement persistants")
            print("✅ L'utilisateur retrouvera toujours ses paramètres")
        else:
            print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
            print("⚠️ Il y a un problème avec la persistance")
        
        print("\n💡 UTILISATION PRATIQUE :")
        print("1. L'utilisateur active Learning et/ou Recommendations")
        print("2. Il ferme l'application")
        print("3. Il rouvre l'application")
        print("4. Ses paramètres sont exactement comme il les avait laissés")
        
    except Exception as e:
        print(f"❌ Erreur pendant les tests : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()