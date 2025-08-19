"""
Système de menu IA avec options Learning et Use customized recommendations
"""

import tkinter as tk
from tkinter import messagebox
import os
import json
from __init__ import *

class AIMenuSystem:
    """Gestionnaire du menu IA avec options configurables"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.menu_window = None
        self.is_menu_open = False
        
        # Configuration IA (sauvegardée dans le config)
        self.ai_config = {
            'learning_enabled': False,
            'use_custom_recommendations': False,
            'ai_active': False  # True si au moins une option est cochée
        }
        
        # Charger la configuration existante
        self.load_ai_config()
        
        # Variables pour les checkboxes
        self.learning_var = tk.BooleanVar(value=self.ai_config['learning_enabled'])
        self.recommendations_var = tk.BooleanVar(value=self.ai_config['use_custom_recommendations'])
        
        # Initialiser le système d'IA si nécessaire
        self.ai_system = None
        self.ai_integration_manager = None
        self.initialize_ai_system()
        
        print(f"🤖 AI Menu: Système initialisé - Learning: {self.ai_config['learning_enabled']}, Recommendations: {self.ai_config['use_custom_recommendations']}")
    
    def load_ai_config(self):
        """Charge la configuration IA depuis le fichier de config principal"""
        try:
            if hasattr(self.main_app, 'config_file') and os.path.exists(self.main_app.config_file):
                with open(self.main_app.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                ai_settings = config.get('ai_settings', {})
                self.ai_config.update(ai_settings)
                
                print(f"🤖 AI Menu: Configuration chargée - {self.ai_config}")
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur chargement config: {e}")
    
    def save_ai_config(self):
        """Sauvegarde la configuration IA dans le fichier de config principal"""
        try:
            if hasattr(self.main_app, 'config_file'):
                # Charger le config existant
                config = {}
                if os.path.exists(self.main_app.config_file):
                    with open(self.main_app.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                
                # Mettre à jour les paramètres IA
                config['ai_settings'] = self.ai_config
                
                # Sauvegarder
                with open(self.main_app.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                print(f"🤖 AI Menu: Configuration sauvegardée - {self.ai_config}")
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur sauvegarde config: {e}")
    
    def initialize_ai_system(self):
        """Initialise le système d'IA si les options sont activées"""
        try:
            if self.ai_config['learning_enabled'] or self.ai_config['use_custom_recommendations']:
                if not self.ai_system:
                    # Importer et initialiser le système d'IA
                    from ai_integration import setup_ai_integration
                    self.ai_integration_manager = setup_ai_integration(self.main_app)
                    
                    if self.ai_integration_manager:
                        self.ai_system = self.ai_integration_manager.ai_system
                        print("🤖 AI Menu: Système d'IA initialisé")
                    else:
                        print("⚠️ AI Menu: Échec initialisation IA")
                        return False
                
                # Activer/désactiver selon la config
                if self.ai_config['learning_enabled']:
                    self.ai_integration_manager.enable_ai()
                else:
                    self.ai_integration_manager.disable_ai()
                
                return True
            else:
                # Désactiver l'IA si aucune option n'est cochée
                if self.ai_integration_manager:
                    self.ai_integration_manager.disable_ai()
                return False
                
        except ImportError:
            print("⚠️ AI Menu: Modules IA non disponibles")
            return False
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur initialisation IA: {e}")
            return False
    
    def create_ai_button(self, parent_frame):
        """Crée le bouton IA dans l'interface"""
        try:
            # Créer un bouton simple avec texte
            self.ai_button = tk.Button(
                parent_frame,
                text="🤖",
                command=self.show_ai_menu,
                relief=tk.FLAT,
                bg="#4a4a4a",
                fg="white",
                activebackground="#5a5a5a",
                activeforeground="white",
                bd=0,
                font=("Arial", 12),
                width=3,
                height=1,
                takefocus=0
            )
            
            # Mettre à jour l'apparence selon l'état
            self.update_button_appearance()
            
            # Créer le menu contextuel
            self.create_context_menu()
            
            return self.ai_button
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur création bouton: {e}")
            return None
    
    def update_button_appearance(self):
        """Met à jour l'apparence du bouton selon l'état de l'IA"""
        try:
            if not hasattr(self, 'ai_button'):
                return
            
            is_active = self.ai_config['learning_enabled'] or self.ai_config['use_custom_recommendations']
            
            if hasattr(self, 'ai_icon') and self.ai_icon:
                if is_active and hasattr(self, 'ai_active_icon'):
                    self.ai_button.config(image=self.ai_active_icon)
                    self.ai_button.config(bg="#4a8fe7", activebackground="#4a8fe7")
                else:
                    self.ai_button.config(image=self.ai_icon)
                    self.ai_button.config(bg=COLOR_WINDOW_BACKGROUND, activebackground=COLOR_WINDOW_BACKGROUND)
            else:
                # Mode texte
                if is_active:
                    self.ai_button.config(bg="#4a8fe7", activebackground="#4a8fe7", fg="white")
                else:
                    self.ai_button.config(bg=COLOR_WINDOW_BACKGROUND, activebackground=COLOR_WINDOW_BACKGROUND, fg="white")
                    
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur mise à jour bouton: {e}")
    
    def toggle_ai_menu(self):
        """Ouvre/ferme le menu IA"""
        if self.is_menu_open:
            self.close_ai_menu()
        else:
            self.open_ai_menu()
    
    def open_ai_menu(self):
        """Ouvre le menu de configuration IA"""
        if self.is_menu_open:
            return
        
        try:
            # Créer la fenêtre du menu
            self.menu_window = tk.Toplevel(self.main_app.root)
            self.menu_window.title("Configuration IA")
            self.menu_window.geometry("280x180")
            self.menu_window.resizable(False, False)
            
            # Style de la fenêtre
            self.menu_window.configure(bg=COLOR_WINDOW_BACKGROUND)
            
            # Positionner près du bouton
            self.position_menu_window()
            
            # Intercepter la fermeture
            self.menu_window.protocol("WM_DELETE_WINDOW", self.close_ai_menu)
            
            # Créer le contenu du menu
            self.create_menu_content()
            
            # Marquer comme ouvert
            self.is_menu_open = True
            
            # Focus sur la fenêtre
            self.menu_window.focus_set()
            self.menu_window.grab_set()  # Modal
            
            print("🤖 AI Menu: Menu ouvert")
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur ouverture menu: {e}")
            self.is_menu_open = False
    
    def position_menu_window(self):
        """Positionne la fenêtre du menu près du bouton"""
        try:
            if hasattr(self, 'ai_button'):
                # Obtenir la position du bouton
                button_x = self.ai_button.winfo_rootx()
                button_y = self.ai_button.winfo_rooty()
                button_height = self.ai_button.winfo_height()
                
                # Positionner le menu en dessous du bouton
                menu_x = button_x
                menu_y = button_y + button_height + 5
                
                self.menu_window.geometry(f"+{menu_x}+{menu_y}")
            else:
                # Position par défaut au centre de l'écran
                self.menu_window.geometry("+400+300")
                
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur positionnement: {e}")
    
    def create_menu_content(self):
        """Crée le contenu du menu de configuration"""
        try:
            # Frame principal
            main_frame = tk.Frame(self.menu_window, bg=COLOR_WINDOW_BACKGROUND)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Titre
            title_label = tk.Label(
                main_frame,
                text="🤖 Configuration IA",
                font=("Arial", 12, "bold"),
                bg=COLOR_WINDOW_BACKGROUND,
                fg="white"
            )
            title_label.pack(pady=(0, 15))
            
            # Option Learning
            learning_frame = tk.Frame(main_frame, bg=COLOR_WINDOW_BACKGROUND)
            learning_frame.pack(fill=tk.X, pady=5)
            
            self.learning_checkbox = tk.Checkbutton(
                learning_frame,
                text="Learning",
                variable=self.learning_var,
                command=self.on_learning_changed,
                bg=COLOR_WINDOW_BACKGROUND,
                fg="white",
                selectcolor=COLOR_WINDOW_BACKGROUND,
                activebackground=COLOR_WINDOW_BACKGROUND,
                activeforeground="white",
                font=("Arial", 10)
            )
            self.learning_checkbox.pack(anchor=tk.W)
            
            # Description Learning
            learning_desc = tk.Label(
                learning_frame,
                text="L'IA analyse vos habitudes d'écoute",
                font=("Arial", 8),
                bg=COLOR_WINDOW_BACKGROUND,
                fg="#cccccc"
            )
            learning_desc.pack(anchor=tk.W, padx=(20, 0))
            
            # Option Recommendations
            recommendations_frame = tk.Frame(main_frame, bg=COLOR_WINDOW_BACKGROUND)
            recommendations_frame.pack(fill=tk.X, pady=5)
            
            self.recommendations_checkbox = tk.Checkbutton(
                recommendations_frame,
                text="Use customized recommendations",
                variable=self.recommendations_var,
                command=self.on_recommendations_changed,
                bg=COLOR_WINDOW_BACKGROUND,
                fg="white",
                selectcolor=COLOR_WINDOW_BACKGROUND,
                activebackground=COLOR_WINDOW_BACKGROUND,
                activeforeground="white",
                font=("Arial", 10)
            )
            self.recommendations_checkbox.pack(anchor=tk.W)
            
            # Description Recommendations
            recommendations_desc = tk.Label(
                recommendations_frame,
                text="L'IA choisit les meilleures recommandations",
                font=("Arial", 8),
                bg=COLOR_WINDOW_BACKGROUND,
                fg="#cccccc"
            )
            recommendations_desc.pack(anchor=tk.W, padx=(20, 0))
            
            # Séparateur
            separator = tk.Frame(main_frame, height=1, bg="#555555")
            separator.pack(fill=tk.X, pady=15)
            
            # Bouton Reset
            reset_button = tk.Button(
                main_frame,
                text="🗑️ Reset datas",
                command=self.reset_ai_data,
                bg="#d32f2f",
                fg="white",
                activebackground="#b71c1c",
                activeforeground="white",
                font=("Arial", 9),
                relief=tk.FLAT,
                padx=10,
                pady=5
            )
            reset_button.pack(pady=(0, 5))
            
            # Bouton Fermer
            close_button = tk.Button(
                main_frame,
                text="Fermer",
                command=self.close_ai_menu,
                bg="#4a8fe7",
                fg="white",
                activebackground="#1976d2",
                activeforeground="white",
                font=("Arial", 9),
                relief=tk.FLAT,
                padx=15,
                pady=5
            )
            close_button.pack()
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur création contenu: {e}")
    
    def on_learning_changed(self):
        """Appelé quand l'option Learning change"""
        try:
            new_value = self.learning_var.get()
            self.ai_config['learning_enabled'] = new_value
            
            print(f"🤖 AI Menu: Learning {'activé' if new_value else 'désactivé'}")
            
            # Mettre à jour l'état actif
            self.update_ai_active_state()
            
            # Initialiser/désactiver l'IA selon le besoin
            self.initialize_ai_system()
            
            # Sauvegarder la config
            self.save_ai_config()
            
            # Mettre à jour l'apparence du bouton
            self.update_button_appearance()
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur changement Learning: {e}")
    
    def on_recommendations_changed(self):
        """Appelé quand l'option Recommendations change"""
        try:
            new_value = self.recommendations_var.get()
            self.ai_config['use_custom_recommendations'] = new_value
            
            print(f"🤖 AI Menu: Recommendations personnalisées {'activées' if new_value else 'désactivées'}")
            
            # Mettre à jour l'état actif
            self.update_ai_active_state()
            
            # Initialiser/désactiver l'IA selon le besoin
            self.initialize_ai_system()
            
            # Sauvegarder la config
            self.save_ai_config()
            
            # Mettre à jour l'apparence du bouton
            self.update_button_appearance()
            
            # Mettre à jour le système de recommandation existant
            self.update_recommendation_system()
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur changement Recommendations: {e}")
    
    def update_ai_active_state(self):
        """Met à jour l'état actif de l'IA"""
        old_state = self.ai_config['ai_active']
        new_state = self.ai_config['learning_enabled'] or self.ai_config['use_custom_recommendations']
        
        self.ai_config['ai_active'] = new_state
        
        if old_state != new_state:
            if new_state:
                print("🤖 AI Menu: IA activée")
                if hasattr(self.main_app, 'status_bar'):
                    self.main_app.status_bar.config(text="IA activée")
            else:
                print("🤖 AI Menu: IA désactivée")
                if hasattr(self.main_app, 'status_bar'):
                    self.main_app.status_bar.config(text="IA désactivée")
    
    def update_recommendation_system(self):
        """Met à jour le système de recommandation existant"""
        try:
            if hasattr(self.main_app, 'recommendation_system'):
                # Modifier le comportement du système de recommandation existant
                if self.ai_config['use_custom_recommendations'] and self.ai_system:
                    # Remplacer la méthode de sélection des recommandations
                    original_method = self.main_app.recommendation_system.filter_new_recommendations
                    
                    def ai_enhanced_filter(recommendations):
                        # Appliquer le filtre original
                        filtered = original_method(recommendations)
                        
                        # Si l'IA est activée, utiliser l'IA pour choisir les meilleures
                        if filtered and self.ai_system:
                            # Convertir les recommandations en chemins fictifs pour l'IA
                            candidate_paths = [f"temp_{rec['videoId']}.mp3" for rec in filtered]
                            
                            # Pour l'instant, retourner les recommandations dans l'ordre original
                            # TODO: Implémenter la sélection IA basée sur les métadonnées des recommandations
                            print("🤖 AI Menu: Sélection IA des recommandations (à implémenter)")
                        
                        return filtered
                    
                    # Remplacer temporairement la méthode
                    self.main_app.recommendation_system.filter_new_recommendations = ai_enhanced_filter
                    print("🤖 AI Menu: Système de recommandation amélioré par l'IA")
                
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur mise à jour système recommandation: {e}")
    
    def reset_ai_data(self):
        """Supprime toutes les données apprises par l'IA"""
        try:
            # Demander confirmation
            if messagebox.askyesno(
                "Réinitialiser l'IA",
                "Êtes-vous sûr de vouloir supprimer toutes les données apprises par l'IA ?\n\n"
                "Cette action est irréversible et l'IA repartira de zéro.",
                parent=self.menu_window
            ):
                # Supprimer les fichiers de données IA
                ai_data_files = [
                    'ai_music_data.json',
                    'ai_music_model.pkl'
                ]
                
                deleted_files = 0
                for filename in ai_data_files:
                    filepath = os.path.join(os.path.dirname(__file__), filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            deleted_files += 1
                            print(f"🗑️ AI Menu: Fichier supprimé - {filename}")
                        except Exception as e:
                            print(f"⚠️ AI Menu: Erreur suppression {filename}: {e}")
                
                # Réinitialiser le système d'IA si il existe
                if self.ai_system:
                    try:
                        # Réinitialiser les données en mémoire
                        self.ai_system.user_behavior_data = {
                            'listening_sessions': [],
                            'skip_patterns': [],
                            'like_patterns': [],
                            'favorite_patterns': [],
                            'time_patterns': {},
                            'sequence_patterns': [],
                            'volume_patterns': {},
                            'mood_indicators': {}
                        }
                        
                        self.ai_system.current_session = {
                            'start_time': time.time(),
                            'songs_played': [],
                            'skips': [],
                            'likes': [],
                            'favorites': [],
                            'volume_changes': [],
                            'listening_duration': {}
                        }
                        
                        # Réinitialiser les modèles
                        self.ai_system.models = {
                            'skip_predictor': None,
                            'like_predictor': None,
                            'mood_classifier': None,
                            'recommendation_ranker': None
                        }
                        
                        print("🤖 AI Menu: Données IA réinitialisées en mémoire")
                        
                    except Exception as e:
                        print(f"⚠️ AI Menu: Erreur réinitialisation mémoire: {e}")
                
                # Message de confirmation
                message = f"✅ Données IA réinitialisées\n{deleted_files} fichier(s) supprimé(s)"
                messagebox.showinfo("Réinitialisation terminée", message, parent=self.menu_window)
                
                if hasattr(self.main_app, 'status_bar'):
                    self.main_app.status_bar.config(text="Données IA réinitialisées")
                
                print("🗑️ AI Menu: Réinitialisation des données IA terminée")
                
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur réinitialisation: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la réinitialisation: {e}", parent=self.menu_window)
    
    def close_ai_menu(self):
        """Ferme le menu IA"""
        try:
            if self.menu_window:
                self.menu_window.grab_release()
                self.menu_window.destroy()
                self.menu_window = None
            
            self.is_menu_open = False
            print("🤖 AI Menu: Menu fermé")
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur fermeture menu: {e}")
    
    def get_ai_recommendation_for_song(self, current_song_path):
        """
        Obtient une recommandation IA pour une chanson donnée
        Utilisé par le système de recommandation existant
        """
        try:
            if not self.ai_config['use_custom_recommendations'] or not self.ai_system:
                return None
            
            # Pour l'instant, retourner None pour utiliser le système existant
            # TODO: Implémenter la logique de recommandation IA basée sur la chanson actuelle
            print(f"🤖 AI Menu: Recommandation IA demandée pour {os.path.basename(current_song_path)}")
            return None
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur recommandation IA: {e}")
            return None
    
    def is_learning_enabled(self):
        """Retourne True si l'apprentissage est activé"""
        return self.ai_config['learning_enabled']
    
    def is_recommendations_enabled(self):
        """Retourne True si les recommandations personnalisées sont activées"""
        return self.ai_config['use_custom_recommendations']
    
    def is_ai_active(self):
        """Retourne True si l'IA est active (au moins une option cochée)"""
        return self.ai_config['ai_active']

# Fonction d'intégration pour l'application principale
def setup_ai_menu_system(main_app):
    """Configure le système de menu IA pour l'application"""
    try:
        ai_menu_system = AIMenuSystem(main_app)
        
        # Stocker la référence dans l'app principale
        main_app.ai_menu_system = ai_menu_system
        
        print("🤖 AI Menu: Système de menu configuré")
        return ai_menu_system
        
    except Exception as e:
        print(f"⚠️ AI Menu: Erreur configuration: {e}")
        return None

if __name__ == "__main__":
    # Test du système de menu
    print("🧪 Test du système de menu IA")
    
    class MockApp:
        def __init__(self):
            import tkinter as tk
            self.root = tk.Tk()
            self.root.title("Test AI Menu")
            self.root.geometry("400x300")
            self.config_file = "test_config.json"
            
            # Créer un frame de test
            test_frame = tk.Frame(self.root)
            test_frame.pack(pady=20)
            
            # Status bar
            self.status_bar = tk.Label(self.root, text="Prêt", relief=tk.SUNKEN, anchor=tk.W)
            self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    mock_app = MockApp()
    ai_menu = setup_ai_menu_system(mock_app)
    
    if ai_menu:
        # Créer le bouton IA dans le frame de test
        test_frame = mock_app.root.children['!frame']
        ai_button = ai_menu.create_ai_button(test_frame)
        if ai_button:
            ai_button.pack(pady=10)
        
        # Ajouter un bouton de test
        test_button = tk.Button(test_frame, text="Test Status", 
                               command=lambda: print(f"Status: Learning={ai_menu.is_learning_enabled()}, Recommendations={ai_menu.is_recommendations_enabled()}"))
        test_button.pack(pady=5)
        
        print("✅ Test configuré - Cliquez sur le bouton IA pour tester")
        mock_app.root.mainloop()
    else:
        print("❌ Échec du test")
        mock_app.root.destroy()