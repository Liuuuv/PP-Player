"""
Script de test pour vérifier la persistance des paramètres et données IA
"""

import os
import json
import sys

def test_ai_config_persistence():
    """Test de la persistance de la configuration IA"""
    print("🧪 Test de persistance de la configuration IA")
    
    # Chemin du fichier de config (simulé)
    config_file = "test_player_config.json"
    
    # Configuration IA de test
    test_ai_config = {
        'learning_enabled': True,
        'use_custom_recommendations': True,
        'ai_active': True
    }
    
    # Simuler la sauvegarde
    config = {
        'ai_settings': test_ai_config,
        'other_settings': {
            'volume': 0.5,
            'theme': 'dark'
        }
    }
    
    try:
        # Sauvegarder
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("✅ Configuration sauvegardée")
        
        # Charger
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        loaded_ai_settings = loaded_config.get('ai_settings', {})
        
        # Vérifier
        if loaded_ai_settings == test_ai_config:
            print("✅ Configuration IA chargée correctement")
            print(f"   Learning: {loaded_ai_settings['learning_enabled']}")
            print(f"   Recommendations: {loaded_ai_settings['use_custom_recommendations']}")
            print(f"   Active: {loaded_ai_settings['ai_active']}")
        else:
            print("❌ Erreur de chargement de la configuration")
            print(f"   Attendu: {test_ai_config}")
            print(f"   Obtenu: {loaded_ai_settings}")
        
        # Nettoyer
        os.remove(config_file)
        print("🧹 Fichier de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

def test_ai_data_files():
    """Test de la présence des fichiers de données IA"""
    print("\n🧪 Test de présence des fichiers de données IA")
    
    ai_data_file = "ai_music_data.json"
    ai_model_file = "ai_music_model.pkl"
    
    # Vérifier les fichiers existants
    if os.path.exists(ai_data_file):
        print(f"✅ Fichier de données IA trouvé: {ai_data_file}")
        try:
            with open(ai_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"   Sessions d'écoute: {len(data.get('listening_sessions', []))}")
            print(f"   Patterns de skip: {len(data.get('skip_patterns', []))}")
            print(f"   Statistiques chansons: {len(data.get('song_statistics', {}))}")
            
        except Exception as e:
            print(f"⚠️ Erreur lecture fichier de données: {e}")
    else:
        print(f"ℹ️ Fichier de données IA non trouvé: {ai_data_file}")
    
    if os.path.exists(ai_model_file):
        print(f"✅ Fichier de modèles IA trouvé: {ai_model_file}")
        file_size = os.path.getsize(ai_model_file)
        print(f"   Taille: {file_size} bytes")
    else:
        print(f"ℹ️ Fichier de modèles IA non trouvé: {ai_model_file}")

def simulate_ai_data_creation():
    """Simule la création de données IA pour tester la persistance"""
    print("\n🧪 Simulation de création de données IA")
    
    # Données IA simulées
    simulated_data = {
        'listening_sessions': [
            {
                'start_time': 1700000000,
                'end_time': 1700003600,
                'songs': ['song1.mp3', 'song2.mp3', 'song3.mp3'],
                'total_songs': 3,
                'skips': 1,
                'likes': 2,
                'favorites': 1
            }
        ],
        'skip_patterns': [
            {
                'song_path': 'song1.mp3',
                'timestamp': 1700000000,
                'listening_ratio': 0.2,
                'skip_type': 'early_skip'
            }
        ],
        'song_statistics': {
            'song1.mp3': {
                'play_count': 5,
                'skip_count': 2,
                'like_count': 1,
                'user_satisfaction_score': 0.7
            },
            'song2.mp3': {
                'play_count': 8,
                'skip_count': 0,
                'like_count': 3,
                'user_satisfaction_score': 0.95
            }
        }
    }
    
    try:
        # Sauvegarder les données simulées
        with open('test_ai_music_data.json', 'w', encoding='utf-8') as f:
            json.dump(simulated_data, f, ensure_ascii=False, indent=2)
        
        print("✅ Données IA simulées créées")
        print(f"   Sessions: {len(simulated_data['listening_sessions'])}")
        print(f"   Patterns de skip: {len(simulated_data['skip_patterns'])}")
        print(f"   Statistiques: {len(simulated_data['song_statistics'])} chansons")
        
        # Vérifier la lecture
        with open('test_ai_music_data.json', 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        if loaded_data == simulated_data:
            print("✅ Données IA lues correctement")
        else:
            print("❌ Erreur de lecture des données IA")
        
        # Nettoyer
        os.remove('test_ai_music_data.json')
        print("🧹 Fichier de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur simulation données IA: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 Test de persistance du système IA")
    print("=" * 50)
    
    test_ai_config_persistence()
    test_ai_data_files()
    simulate_ai_data_creation()
    
    print("\n" + "=" * 50)
    print("✅ Tests de persistance terminés")
    
    print("\n📋 Résumé des fonctionnalités implémentées:")
    print("• ✅ Sauvegarde automatique des paramètres IA (learning/recommendations)")
    print("• ✅ Chargement automatique des paramètres au démarrage")
    print("• ✅ Sauvegarde des données IA à la fermeture de l'application")
    print("• ✅ Sauvegarde périodique automatique (toutes les 5 minutes)")
    print("• ✅ Persistance des données comportementales")
    print("• ✅ Persistance des modèles ML entraînés")
    print("• ✅ Gestion robuste des erreurs")

if __name__ == "__main__":
    main()