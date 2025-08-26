"""
Script de configuration pour intégrer le système d'IA dans l'application musicale
À appeler depuis le fichier principal de l'application
"""

import os
import sys

def setup_ai_system(main_app):
    """
    Configure et active le système d'IA pour l'application musicale
    
    Args:
        main_app: Instance de l'application musicale principale
    
    Returns:
        bool: True si l'IA a été configurée avec succès, False sinon
    """
    
    try:
        print("🚀 Configuration du système d'IA de recommandation...")
        
        # Importer le gestionnaire d'intégration
        from ai_integration import setup_ai_integration
        
        # Configurer l'intégration
        ai_manager = setup_ai_integration(main_app)
        
        if ai_manager:
            print("✅ Système d'IA configuré avec succès!")
            
            # Afficher le statut
            status = main_app.ai_status()
            print(f"📊 Statut IA:")
            print(f"  - Activé: {status['enabled']}")
            print(f"  - Système disponible: {status['ai_system_available']}")
            print(f"  - ML disponible: {status['ml_available']}")
            print(f"  - Modèles entraînés: {status['models_trained']}")
            
            # Ajouter des méthodes utilitaires à l'application
            add_ai_utilities(main_app)
            
            # Programmer l'entraînement automatique
            schedule_auto_training(main_app)
            
            return True
        else:
            print("❌ Échec de la configuration du système d'IA")
            return False
            
    except ImportError as e:
        print(f"⚠️ Modules IA non disponibles: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur configuration IA: {e}")
        return False

def add_ai_utilities(main_app):
    """Ajoute des méthodes utilitaires IA à l'application"""
    
    def show_ai_insights():
        """Affiche les insights IA dans la console"""
        try:
            insights = main_app.get_ai_insights()
            print("\n🧠 Insights IA sur vos habitudes d'écoute:")
            print(f"📈 Sessions d'écoute: {insights.get('total_sessions', 0)}")
            print(f"⏭️ Chansons skippées: {insights.get('total_skips', 0)}")
            print(f"❤️ Chansons likées: {insights.get('total_likes', 0)}")
            print(f"⭐ Chansons favorites: {insights.get('total_favorites', 0)}")
            print(f"📊 Taux de skip: {insights.get('skip_rate', 0):.1%}")
            print(f"💖 Taux de like: {insights.get('like_rate', 0):.1%}")
            
            preferred_hours = insights.get('preferred_hours', [])
            if preferred_hours:
                print(f"🕐 Heures préférées: {', '.join(f'{h}h' for h in preferred_hours)}")
            
            if hasattr(main_app, 'status_bar'):
                main_app.status_bar.config(text="Insights IA affichés dans la console")
                
        except Exception as e:
            print(f"⚠️ Erreur affichage insights: {e}")
    
    def train_ai_now():
        """Lance l'entraînement des modèles IA maintenant"""
        try:
            print("🤖 Lancement de l'entraînement des modèles IA...")
            main_app.train_ai_models()
            if hasattr(main_app, 'status_bar'):
                main_app.status_bar.config(text="Entraînement IA lancé (voir console)")
        except Exception as e:
            print(f"⚠️ Erreur entraînement IA: {e}")
    
    def toggle_ai():
        """Active/désactive le système d'IA"""
        try:
            status = main_app.ai_status()
            if status['enabled']:
                main_app.ai_disable()
                message = "IA désactivée"
            else:
                main_app.ai_enable()
                message = "IA activée"
            
            print(f"🔄 {message}")
            if hasattr(main_app, 'status_bar'):
                main_app.status_bar.config(text=message)
                
        except Exception as e:
            print(f"⚠️ Erreur toggle IA: {e}")
    
    def ai_recommend_from_playlist():
        """Recommande la meilleure chanson de la playlist actuelle"""
        try:
            if not hasattr(main_app, 'main_playlist') or not main_app.main_playlist:
                print("⚠️ Aucune playlist disponible pour la recommandation")
                return
            
            # Prendre quelques chansons aléatoires de la playlist pour la recommandation
            import random
            candidates = random.sample(main_app.main_playlist, min(10, len(main_app.main_playlist)))
            
            recommended = main_app.get_ai_recommendation(candidates)
            if recommended:
                song_name = os.path.basename(recommended)
                print(f"🎵 IA recommande: {song_name}")
                
                # Optionnel: jouer la chanson recommandée
                if recommended in main_app.main_playlist:
                    main_app.current_index = main_app.main_playlist.index(recommended)
                    main_app.play_track()
                    
                if hasattr(main_app, 'status_bar'):
                    main_app.status_bar.config(text=f"IA recommande: {song_name}")
            else:
                print("⚠️ Aucune recommandation IA disponible")
                
        except Exception as e:
            print(f"⚠️ Erreur recommandation IA: {e}")
    
    # Ajouter les méthodes à l'application
    main_app.show_ai_insights = show_ai_insights
    main_app.train_ai_now = train_ai_now
    main_app.toggle_ai = toggle_ai
    main_app.ai_recommend_from_playlist = ai_recommend_from_playlist
    
    print("🔧 Méthodes utilitaires IA ajoutées")

def schedule_auto_training(main_app):
    """Programme l'entraînement automatique des modèles"""
    
    def check_auto_training():
        """Vérifie s'il faut lancer l'entraînement automatique"""
        try:
            if main_app.ai_should_retrain():
                print("🤖 Entraînement automatique des modèles IA...")
                main_app.train_ai_models()
        except Exception as e:
            print(f"⚠️ Erreur vérification auto-training: {e}")
        
        # Programmer la prochaine vérification dans 5 minutes
        if hasattr(main_app, 'root'):
            main_app.root.after(300000, check_auto_training)  # 5 minutes
    
    # Programmer la première vérification dans 1 minute
    if hasattr(main_app, 'root'):
        main_app.root.after(60000, check_auto_training)  # 1 minute
        print("⏰ Entraînement automatique programmé")

def create_ai_menu(main_app):
    """Crée un menu IA dans l'interface utilisateur (si possible)"""
    
    try:
        import tkinter as tk
        
        # Vérifier si l'application a une barre de menu
        if hasattr(main_app, 'menubar'):
            # Créer le menu IA
            ai_menu = tk.Menu(main_app.menubar, tearoff=0)
            
            ai_menu.add_command(label="Afficher les insights", command=main_app.show_ai_insights)
            ai_menu.add_command(label="Entraîner les modèles", command=main_app.train_ai_now)
            ai_menu.add_command(label="Recommandation IA", command=main_app.ai_recommend_from_playlist)
            ai_menu.add_separator()
            ai_menu.add_command(label="Activer/Désactiver IA", command=main_app.toggle_ai)
            
            main_app.menubar.add_cascade(label="IA", menu=ai_menu)
            print("📋 Menu IA ajouté à l'interface")
            
        # Ou créer des boutons si possible
        elif hasattr(main_app, 'root'):
            create_ai_buttons(main_app)
            
    except Exception as e:
        print(f"⚠️ Impossible de créer le menu IA: {e}")

def create_ai_buttons(main_app):
    """Crée des boutons IA dans l'interface"""
    
    try:
        import tkinter as tk
        
        # Créer un frame pour les boutons IA
        ai_frame = tk.Frame(main_app.root)
        ai_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # Bouton insights
        insights_btn = tk.Button(ai_frame, text="🧠 Insights IA", 
                               command=main_app.show_ai_insights,
                               font=("Arial", 8))
        insights_btn.pack(side=tk.LEFT, padx=2)
        
        # Bouton recommandation
        recommend_btn = tk.Button(ai_frame, text="🎵 Recommandation", 
                                command=main_app.ai_recommend_from_playlist,
                                font=("Arial", 8))
        recommend_btn.pack(side=tk.LEFT, padx=2)
        
        # Bouton toggle IA
        toggle_btn = tk.Button(ai_frame, text="🤖 Toggle IA", 
                             command=main_app.toggle_ai,
                             font=("Arial", 8))
        toggle_btn.pack(side=tk.LEFT, padx=2)
        
        print("🔘 Boutons IA ajoutés à l'interface")
        
    except Exception as e:
        print(f"⚠️ Impossible de créer les boutons IA: {e}")

def print_ai_help():
    """Affiche l'aide pour utiliser le système d'IA"""
    
    help_text = """
🤖 SYSTÈME D'IA DE RECOMMANDATION MUSICALE

📋 FONCTIONNALITÉS:
• Analyse automatique de vos habitudes d'écoute
• Détection des skips, likes, et favoris
• Prédiction de vos préférences musicales
• Recommandations personnalisées
• Insights sur vos patterns d'écoute

🎯 MÉTHODES DISPONIBLES:
• main_app.show_ai_insights() - Affiche vos statistiques d'écoute
• main_app.train_ai_now() - Lance l'entraînement des modèles
• main_app.ai_recommend_from_playlist() - Recommande une chanson
• main_app.toggle_ai() - Active/désactive l'IA
• main_app.ai_status() - Affiche le statut du système

📊 DONNÉES ANALYSÉES:
• Durée d'écoute de chaque chanson
• Fréquence des skips
• Patterns temporels (heure, jour)
• Historique des likes et favoris
• Changements de volume
• Séquences de chansons

🔧 CONFIGURATION:
• Les données sont sauvegardées automatiquement
• L'entraînement se fait automatiquement tous les 50 titres
• Les modèles s'améliorent avec l'usage

💡 CONSEILS:
• Plus vous utilisez l'application, plus l'IA devient précise
• Les recommandations s'améliorent après quelques sessions
• Utilisez les likes/favoris pour améliorer les prédictions
"""
    
    print(help_text)

# Fonction principale d'installation
def install_ai_system(main_app, create_ui=True, show_help=True):
    """
    Installation complète du système d'IA
    
    Args:
        main_app: Instance de l'application musicale
        create_ui: Créer l'interface utilisateur pour l'IA
        show_help: Afficher l'aide
    
    Returns:
        bool: True si l'installation a réussi
    """
    
    print("🚀 Installation du système d'IA de recommandation musicale...")
    
    # Configurer le système de base
    success = setup_ai_system(main_app)
    
    if success:
        # Créer l'interface utilisateur si demandé
        if create_ui:
            create_ai_menu(main_app)
        
        # Afficher l'aide si demandé
        if show_help:
            print_ai_help()
        
        print("✅ Installation du système d'IA terminée avec succès!")
        print("🎵 L'IA va maintenant analyser vos habitudes d'écoute en temps réel")
        
        return True
    else:
        print("❌ Échec de l'installation du système d'IA")
        return False

if __name__ == "__main__":
    # Test d'installation
    print("🧪 Test d'installation du système d'IA")
    
    class MockApp:
        def __init__(self):
            import tkinter as tk
            self.root = tk.Tk()
            self.root.withdraw()  # Cacher la fenêtre de test
            self.main_playlist = []
            self.current_index = 0
            self.status_bar = None
        
        def play_track(self):
            pass
    
    mock_app = MockApp()
    success = install_ai_system(mock_app, create_ui=False, show_help=True)
    
    if success:
        print("✅ Test d'installation réussi")
        # Tester quelques fonctionnalités
        status = mock_app.ai_status()
        print("Status:", status)
    else:
        print("❌ Test d'installation échoué")
    
    mock_app.root.destroy()