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
        
        # Variables pour les checkboxes (initialisées après le chargement de la config)
        self.learning_var = tk.BooleanVar(value=self.ai_config['learning_enabled'])
        self.recommendations_var = tk.BooleanVar(value=self.ai_config['use_custom_recommendations'])
        
        # Ajouter des callbacks pour synchroniser les variables avec la config
        self.learning_var.trace_add('write', self._sync_learning_var)
        self.recommendations_var.trace_add('write', self._sync_recommendations_var)
        
        # Initialiser le système d'IA si nécessaire
        self.ai_system = None
        self.ai_integration_manager = None
        self.initialize_ai_system()
        
        # Programmer la sauvegarde automatique périodique
        self.schedule_periodic_save()
        
        print(f"🤖 AI Menu: Système initialisé - Learning: {self.ai_config['learning_enabled']}, Recommendations: {self.ai_config['use_custom_recommendations']}")
    
    def load_ai_config(self):
        """Charge la configuration IA depuis le fichier de config principal"""
        try:
            print(f"🔍 AI Menu: Tentative de chargement config depuis {getattr(self.main_app, 'config_file', 'FICHIER NON DÉFINI')}")
            
            if hasattr(self.main_app, 'config_file'):
                print(f"🔍 AI Menu: Fichier config défini: {self.main_app.config_file}")
                print(f"🔍 AI Menu: Fichier existe: {os.path.exists(self.main_app.config_file)}")
                
                if os.path.exists(self.main_app.config_file):
                    with open(self.main_app.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    print(f"🔍 AI Menu: Config complète chargée: {config}")
                    
                    ai_settings = config.get('ai_settings', {})
                    print(f"🔍 AI Menu: Paramètres IA trouvés: {ai_settings}")
                    
                    # Mettre à jour seulement les clés existantes pour préserver les valeurs par défaut
                    for key, value in ai_settings.items():
                        if key in self.ai_config:
                            old_value = self.ai_config[key]
                            self.ai_config[key] = value
                            print(f"🔍 AI Menu: {key}: {old_value} -> {value}")
                    
                    # S'assurer que ai_active est cohérent avec les autres paramètres
                    self.ai_config['ai_active'] = (
                        self.ai_config['learning_enabled'] or 
                        self.ai_config['use_custom_recommendations']
                    )
                    
                    print(f"🤖 AI Menu: Configuration chargée - {self.ai_config}")
                    
                    # Vérifier si des données IA existent déjà
                    ai_data_file = os.path.join(os.path.dirname(__file__), "ai_music_data.json")
                    if os.path.exists(ai_data_file):
                        print("🤖 AI Menu: Données IA existantes détectées")
                    else:
                        print("🤖 AI Menu: Aucune donnée IA existante")
                else:
                    print("🔍 AI Menu: Fichier de config n'existe pas encore")
            else:
                print("🔍 AI Menu: Attribut config_file non défini dans main_app")
                    
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur chargement config: {e}")
            import traceback
            traceback.print_exc()
            # En cas d'erreur, utiliser les valeurs par défaut
            print("🤖 AI Menu: Utilisation des paramètres par défaut")
    
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
                
                # Sauvegarder aussi les données IA si le système est actif
                if self.ai_system and hasattr(self.ai_system, 'save_data'):
                    self.ai_system.save_data()
                    print("🤖 AI Menu: Données IA sauvegardées")
                    
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
                # text='',
                # image=self.ai_icon,
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
            
            if is_active:
                # Bouton actif : fond bleu
                self.ai_button.config(
                    bg="#4a8fe7", 
                    activebackground="#5a9fd8",
                    fg="white",
                    activeforeground="white"
                )
            else:
                # Bouton inactif : fond gris
                self.ai_button.config(
                    bg="#4a4a4a", 
                    activebackground="#5a5a5a",
                    fg="white",
                    activeforeground="white"
                )
                    
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur mise à jour bouton: {e}")
    
    def create_context_menu(self):
        """Crée le menu contextuel IA"""
        try:
            self.context_menu = tk.Menu(self.main_app.root, tearoff=0)
            
            # Option Learning avec checkbutton
            self.context_menu.add_checkbutton(
                label="Learning",
                variable=self.learning_var,
                command=self.on_learning_changed
            )
            
            # Option Recommendations avec checkbutton
            self.context_menu.add_checkbutton(
                label="Use customized recommendations",
                variable=self.recommendations_var,
                command=self.on_recommendations_changed
            )
            
            # Séparateur
            self.context_menu.add_separator()
            
            # Option pour afficher les insights IA
            self.context_menu.add_command(
                label="📊 Show AI insights",
                command=self.show_ai_insights_window
            )
            
            # Séparateur
            self.context_menu.add_separator()
            
            # Option pour reset les données
            self.context_menu.add_command(
                label="🗑️ Reset AI data",
                command=self.reset_ai_data
            )
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur création menu contextuel: {e}")
    
    def show_ai_menu(self):
        """Affiche le menu contextuel IA"""
        try:
            if hasattr(self, 'context_menu'):
                # Obtenir la position du bouton
                x = self.ai_button.winfo_rootx()
                y = self.ai_button.winfo_rooty() + self.ai_button.winfo_height()
                
                # Afficher le menu
                self.context_menu.post(x, y)
                
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur affichage menu: {e}")
    
    def show_ai_insights_window(self):
        """Affiche une fenêtre avec tous les insights IA"""
        try:
            # Créer la fenêtre d'insights
            insights_window = tk.Toplevel(self.main_app.root)
            insights_window.title("🤖 AI Insights - Ce que l'IA sait sur vous")
            insights_window.geometry("800x600")
            insights_window.configure(bg=COLOR_WINDOW_BACKGROUND)
            
            # Créer un canvas avec scrollbar pour le contenu
            canvas = tk.Canvas(insights_window, bg=COLOR_WINDOW_BACKGROUND)
            scrollbar = tk.Scrollbar(insights_window, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=COLOR_WINDOW_BACKGROUND)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Générer le contenu des insights
            self.generate_ai_insights_content(scrollable_frame)
            
            # Pack les widgets
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y")
            
            # Centrer la fenêtre
            insights_window.transient(self.main_app.root)
            insights_window.grab_set()
            
            print("🤖 AI Insights: Fenêtre d'insights ouverte")
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur ouverture insights: {e}")
    
    def generate_ai_insights_content(self, parent_frame):
        """Génère le contenu de la fenêtre d'insights"""
        try:
            # Titre principal
            title_label = tk.Label(
                parent_frame,
                text="🤖 Intelligence Artificielle - Profil Utilisateur",
                font=("Arial", 16, "bold"),
                bg=COLOR_WINDOW_BACKGROUND,
                fg="white"
            )
            title_label.pack(pady=(0, 20))
            
            # Statut de l'IA
            status_frame = tk.LabelFrame(
                parent_frame,
                text="📊 Statut de l'IA",
                bg=COLOR_WINDOW_BACKGROUND,
                fg="white",
                font=("Arial", 12, "bold")
            )
            status_frame.pack(fill="x", padx=10, pady=5)
            
            # Informations de statut
            learning_status = "✅ Activé" if self.ai_config['learning_enabled'] else "❌ Désactivé"
            recommendations_status = "✅ Activé" if self.ai_config['use_custom_recommendations'] else "❌ Désactivé"
            
            tk.Label(
                status_frame,
                text=f"Learning: {learning_status}",
                bg=COLOR_WINDOW_BACKGROUND,
                fg="white",
                font=("Arial", 10)
            ).pack(anchor="w", padx=10, pady=2)
            
            tk.Label(
                status_frame,
                text=f"Recommandations personnalisées: {recommendations_status}",
                bg=COLOR_WINDOW_BACKGROUND,
                fg="white",
                font=("Arial", 10)
            ).pack(anchor="w", padx=10, pady=2)
            
            # Données collectées
            if self.ai_system and hasattr(self.ai_system, 'user_behavior_data'):
                behavior_data = self.ai_system.user_behavior_data
                
                # Sessions d'écoute
                sessions_frame = tk.LabelFrame(
                    parent_frame,
                    text="🎵 Sessions d'écoute",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 12, "bold")
                )
                sessions_frame.pack(fill="x", padx=10, pady=5)
                
                sessions = behavior_data.get('listening_sessions', [])
                tk.Label(
                    sessions_frame,
                    text=f"Nombre total de sessions: {len(sessions)}",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 10)
                ).pack(anchor="w", padx=10, pady=2)
                
                if sessions:
                    total_songs = sum(len(session.get('songs_played', [])) for session in sessions)
                    tk.Label(
                        sessions_frame,
                        text=f"Total de chansons écoutées: {total_songs}",
                        bg=COLOR_WINDOW_BACKGROUND,
                        fg="white",
                        font=("Arial", 10)
                    ).pack(anchor="w", padx=10, pady=2)
                
                # Patterns de skip
                skips_frame = tk.LabelFrame(
                    parent_frame,
                    text="⏭️ Patterns de Skip",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 12, "bold")
                )
                skips_frame.pack(fill="x", padx=10, pady=5)
                
                skip_patterns = behavior_data.get('skip_patterns', [])
                tk.Label(
                    skips_frame,
                    text=f"Nombre total de skips: {len(skip_patterns)}",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 10)
                ).pack(anchor="w", padx=10, pady=2)
                
                if skip_patterns:
                    # Calculer le ratio moyen de skip
                    ratios = [skip.get('listening_ratio', 0) for skip in skip_patterns if 'listening_ratio' in skip]
                    if ratios:
                        avg_skip_ratio = sum(ratios) / len(ratios)
                        tk.Label(
                            skips_frame,
                            text=f"Ratio moyen d'écoute avant skip: {avg_skip_ratio:.2%}",
                            bg=COLOR_WINDOW_BACKGROUND,
                            fg="white",
                            font=("Arial", 10)
                        ).pack(anchor="w", padx=10, pady=2)
                
                # Patterns de likes
                likes_frame = tk.LabelFrame(
                    parent_frame,
                    text="❤️ Patterns de Likes",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 12, "bold")
                )
                likes_frame.pack(fill="x", padx=10, pady=5)
                
                like_patterns = behavior_data.get('like_patterns', [])
                tk.Label(
                    likes_frame,
                    text=f"Nombre total de likes: {len(like_patterns)}",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 10)
                ).pack(anchor="w", padx=10, pady=2)
                
                # Patterns temporels
                time_frame = tk.LabelFrame(
                    parent_frame,
                    text="🕐 Patterns Temporels",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 12, "bold")
                )
                time_frame.pack(fill="x", padx=10, pady=5)
                
                time_patterns = behavior_data.get('time_patterns', {})
                hourly_prefs = time_patterns.get('hourly_preferences', {})
                
                if hourly_prefs:
                    tk.Label(
                        time_frame,
                        text="Heures d'écoute préférées:",
                        bg=COLOR_WINDOW_BACKGROUND,
                        fg="white",
                        font=("Arial", 10, "bold")
                    ).pack(anchor="w", padx=10, pady=2)
                    
                    # Afficher les 3 heures les plus actives
                    sorted_hours = sorted(hourly_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
                    for hour, score in sorted_hours:
                        tk.Label(
                            time_frame,
                            text=f"  {hour}h: Score {score:.2f}",
                            bg=COLOR_WINDOW_BACKGROUND,
                            fg="white",
                            font=("Arial", 9)
                        ).pack(anchor="w", padx=20, pady=1)
                
                # Modèles ML
                models_frame = tk.LabelFrame(
                    parent_frame,
                    text="🧠 Modèles d'Intelligence Artificielle",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 12, "bold")
                )
                models_frame.pack(fill="x", padx=10, pady=5)
                
                if hasattr(self.ai_system, 'models'):
                    models = self.ai_system.models
                    
                    for model_name, model in models.items():
                        status = "✅ Entraîné" if model is not None else "❌ Non entraîné"
                        display_name = {
                            'skip_predictor': 'Prédicteur de Skip',
                            'like_predictor': 'Prédicteur de Like',
                            'mood_classifier': 'Classificateur d\'Humeur',
                            'recommendation_ranker': 'Classeur de Recommandations'
                        }.get(model_name, model_name)
                        
                        tk.Label(
                            models_frame,
                            text=f"{display_name}: {status}",
                            bg=COLOR_WINDOW_BACKGROUND,
                            fg="white",
                            font=("Arial", 10)
                        ).pack(anchor="w", padx=10, pady=2)
                
                # Statistiques détaillées par chanson
                songs_frame = tk.LabelFrame(
                    parent_frame,
                    text="🎵 Statistiques Détaillées par Chanson",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 12, "bold")
                )
                songs_frame.pack(fill="x", padx=10, pady=5)
                
                # Obtenir les meilleures chansons
                top_songs = self.ai_system.get_top_songs_statistics(limit=10)
                
                if top_songs:
                    # Créer un canvas avec scrollbar pour les chansons
                    songs_canvas = tk.Canvas(songs_frame, bg=COLOR_WINDOW_BACKGROUND, height=200)
                    songs_scrollbar = tk.Scrollbar(songs_frame, orient="vertical", command=songs_canvas.yview)
                    songs_scrollable = tk.Frame(songs_canvas, bg=COLOR_WINDOW_BACKGROUND)
                    
                    songs_scrollable.bind(
                        "<Configure>",
                        lambda e: songs_canvas.configure(scrollregion=songs_canvas.bbox("all"))
                    )
                    
                    songs_canvas.create_window((0, 0), window=songs_scrollable, anchor="nw")
                    songs_canvas.configure(yscrollcommand=songs_scrollbar.set)
                    
                    # En-têtes
                    header_frame = tk.Frame(songs_scrollable, bg=COLOR_WINDOW_BACKGROUND)
                    header_frame.pack(fill="x", padx=5, pady=2)
                    
                    tk.Label(header_frame, text="Chanson", bg=COLOR_WINDOW_BACKGROUND, fg="white", 
                            font=("Arial", 9, "bold"), width=25, anchor="w").pack(side="left")
                    tk.Label(header_frame, text="Satisfaction", bg=COLOR_WINDOW_BACKGROUND, fg="white", 
                            font=("Arial", 9, "bold"), width=10, anchor="center").pack(side="left")
                    tk.Label(header_frame, text="IA Score", bg=COLOR_WINDOW_BACKGROUND, fg="white", 
                            font=("Arial", 9, "bold"), width=10, anchor="center").pack(side="left")
                    tk.Label(header_frame, text="Skip Pred", bg=COLOR_WINDOW_BACKGROUND, fg="white", 
                            font=("Arial", 9, "bold"), width=10, anchor="center").pack(side="left")
                    tk.Label(header_frame, text="Like Pred", bg=COLOR_WINDOW_BACKGROUND, fg="white", 
                            font=("Arial", 9, "bold"), width=10, anchor="center").pack(side="left")
                    
                    # Ligne de séparation
                    separator = tk.Frame(songs_scrollable, height=1, bg="#555555")
                    separator.pack(fill="x", padx=5, pady=2)
                    
                    # Afficher chaque chanson
                    for i, song in enumerate(top_songs):
                        song_frame = tk.Frame(songs_scrollable, bg=COLOR_WINDOW_BACKGROUND)
                        song_frame.pack(fill="x", padx=5, pady=1)
                        
                        # Nom de la chanson (tronqué)
                        song_name = song['song_name']
                        if len(song_name) > 30:
                            song_name = song_name[:27] + "..."
                        
                        tk.Label(song_frame, text=f"{i+1}. {song_name}", 
                                bg=COLOR_WINDOW_BACKGROUND, fg="white", 
                                font=("Arial", 8), width=25, anchor="w").pack(side="left")
                        
                        # Score de satisfaction utilisateur
                        satisfaction = song.get('user_satisfaction_score', 0)
                        satisfaction_color = "#4CAF50" if satisfaction > 0.7 else "#FFC107" if satisfaction > 0.4 else "#F44336"
                        tk.Label(song_frame, text=f"{satisfaction:.2f}", 
                                bg=COLOR_WINDOW_BACKGROUND, fg=satisfaction_color, 
                                font=("Arial", 8), width=10, anchor="center").pack(side="left")
                        
                        # Score IA global
                        ai_score = song.get('ai_overall_score', 0.5)
                        ai_color = "#2196F3" if ai_score > 0.7 else "#9C27B0" if ai_score > 0.4 else "#607D8B"
                        tk.Label(song_frame, text=f"{ai_score:.2f}", 
                                bg=COLOR_WINDOW_BACKGROUND, fg=ai_color, 
                                font=("Arial", 8), width=10, anchor="center").pack(side="left")
                        
                        # Prédiction de skip
                        skip_pred = song.get('ai_skip_prediction', 0.5)
                        skip_color = "#F44336" if skip_pred > 0.7 else "#FF9800" if skip_pred > 0.4 else "#4CAF50"
                        tk.Label(song_frame, text=f"{skip_pred:.2f}", 
                                bg=COLOR_WINDOW_BACKGROUND, fg=skip_color, 
                                font=("Arial", 8), width=10, anchor="center").pack(side="left")
                        
                        # Prédiction de like
                        like_pred = song.get('ai_like_prediction', 0.5)
                        like_color = "#4CAF50" if like_pred > 0.7 else "#FFC107" if like_pred > 0.4 else "#F44336"
                        tk.Label(song_frame, text=f"{like_pred:.2f}", 
                                bg=COLOR_WINDOW_BACKGROUND, fg=like_color, 
                                font=("Arial", 8), width=10, anchor="center").pack(side="left")
                        
                        # Détails au survol (tooltip simulé)
                        details = (f"Plays: {song.get('play_count', 0)} | "
                                 f"Skips: {song.get('skip_count', 0)} | "
                                 f"Likes: {song.get('like_count', 0)} | "
                                 f"Avg Listen: {song.get('avg_listening_ratio', 0):.1%}")
                        
                        # Ajouter les détails comme texte plus petit
                        if i < 5:  # Seulement pour les 5 premiers pour éviter l'encombrement
                            details_label = tk.Label(song_frame, text=details, 
                                                    bg=COLOR_WINDOW_BACKGROUND, fg="#888888", 
                                                    font=("Arial", 7))
                            details_label.pack(anchor="w", padx=(30, 0))
                    
                    # Pack le canvas et scrollbar
                    songs_canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
                    songs_scrollbar.pack(side="right", fill="y", pady=5)
                    
                else:
                    tk.Label(
                        songs_frame,
                        text="Aucune statistique de chanson disponible.\nÉcoutez de la musique avec Learning activé pour générer des données.",
                        bg=COLOR_WINDOW_BACKGROUND,
                        fg="#cccccc",
                        font=("Arial", 10),
                        justify="center"
                    ).pack(pady=10)
                
                # Légende des couleurs
                legend_frame = tk.LabelFrame(
                    parent_frame,
                    text="🎨 Légende des Couleurs",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 10, "bold")
                )
                legend_frame.pack(fill="x", padx=10, pady=5)
                
                legend_text = (
                    "Satisfaction: Vert (>0.7) | Jaune (0.4-0.7) | Rouge (<0.4)\n"
                    "IA Score: Bleu (>0.7) | Violet (0.4-0.7) | Gris (<0.4)\n"
                    "Skip Pred: Rouge (élevé) | Orange (moyen) | Vert (faible)\n"
                    "Like Pred: Vert (élevé) | Jaune (moyen) | Rouge (faible)"
                )
                
                tk.Label(
                    legend_frame,
                    text=legend_text,
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="#cccccc",
                    font=("Arial", 8),
                    justify="left"
                ).pack(anchor="w", padx=10, pady=5)
            
            else:
                # Pas de données IA disponibles
                no_data_frame = tk.LabelFrame(
                    parent_frame,
                    text="⚠️ Données IA",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 12, "bold")
                )
                no_data_frame.pack(fill="x", padx=10, pady=5)
                
                tk.Label(
                    no_data_frame,
                    text="Aucune donnée IA disponible.",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="#cccccc",
                    font=("Arial", 10)
                ).pack(anchor="w", padx=10, pady=5)
                
                tk.Label(
                    no_data_frame,
                    text="Activez 'Learning' et écoutez de la musique pour commencer l'apprentissage.",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="#cccccc",
                    font=("Arial", 10)
                ).pack(anchor="w", padx=10, pady=2)
            
            # Informations techniques
            tech_frame = tk.LabelFrame(
                parent_frame,
                text="🔧 Informations Techniques",
                bg=COLOR_WINDOW_BACKGROUND,
                fg="white",
                font=("Arial", 12, "bold")
            )
            tech_frame.pack(fill="x", padx=10, pady=5)
            
            # Vérifier les dépendances ML
            try:
                import sklearn
                ml_status = "✅ Disponible"
            except ImportError:
                ml_status = "❌ Non disponible"
            
            tk.Label(
                tech_frame,
                text=f"Scikit-learn: {ml_status}",
                bg=COLOR_WINDOW_BACKGROUND,
                fg="white",
                font=("Arial", 10)
            ).pack(anchor="w", padx=10, pady=2)
            
            # Fichiers de données
            data_files = ['ai_music_data.json', 'ai_music_model.pkl']
            for filename in data_files:
                filepath = os.path.join(os.path.dirname(__file__), filename)
                exists = "✅ Existe" if os.path.exists(filepath) else "❌ Absent"
                tk.Label(
                    tech_frame,
                    text=f"{filename}: {exists}",
                    bg=COLOR_WINDOW_BACKGROUND,
                    fg="white",
                    font=("Arial", 10)
                ).pack(anchor="w", padx=10, pady=2)
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur génération insights: {e}")
            
            # Afficher l'erreur dans la fenêtre
            error_label = tk.Label(
                parent_frame,
                text=f"Erreur lors de la génération des insights: {e}",
                bg=COLOR_WINDOW_BACKGROUND,
                fg="red",
                font=("Arial", 12)
            )
            error_label.pack(pady=20)
    


    
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
                "Cette action est irréversible et l'IA repartira de zéro."
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
                messagebox.showinfo("Réinitialisation terminée", message)
                
                if hasattr(self.main_app, 'status_bar'):
                    self.main_app.status_bar.config(text="Données IA réinitialisées")
                
                print("🗑️ AI Menu: Réinitialisation des données IA terminée")
                
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur réinitialisation: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la réinitialisation: {e}")
    
    def save_ai_data_on_exit(self):
        """Sauvegarde les données IA à la fermeture de l'application"""
        try:
            print("🤖 AI Menu: Sauvegarde des données IA à la fermeture...")
            
            # Sauvegarder la configuration IA
            self.save_ai_config()
            
            # Sauvegarder la session courante si l'IA est active
            if self.ai_system and hasattr(self.ai_system, 'save_session_data'):
                self.ai_system.save_session_data()
                print("🤖 AI Menu: Session IA sauvegardée")
            
            # Sauvegarder toutes les données IA
            if self.ai_system and hasattr(self.ai_system, 'save_data'):
                self.ai_system.save_data()
                print("🤖 AI Menu: Toutes les données IA sauvegardées")
                
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur sauvegarde à la fermeture: {e}")
    
    def get_ai_status_summary(self):
        """Retourne un résumé du statut IA pour l'affichage"""
        try:
            status = {
                'learning_enabled': self.ai_config['learning_enabled'],
                'recommendations_enabled': self.ai_config['use_custom_recommendations'],
                'ai_active': self.ai_config['ai_active'],
                'system_available': self.ai_system is not None,
                'data_collected': False,
                'models_trained': False
            }
            
            if self.ai_system:
                # Vérifier si des données ont été collectées
                behavior_data = getattr(self.ai_system, 'user_behavior_data', {})
                status['data_collected'] = (
                    len(behavior_data.get('listening_sessions', [])) > 0 or
                    len(behavior_data.get('skip_patterns', [])) > 0 or
                    len(behavior_data.get('song_statistics', {})) > 0
                )
                
                # Vérifier si des modèles sont entraînés
                models = getattr(self.ai_system, 'models', {})
                status['models_trained'] = any(model is not None for model in models.values())
            
            return status
            
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur récupération statut: {e}")
            return {
                'learning_enabled': False,
                'recommendations_enabled': False,
                'ai_active': False,
                'system_available': False,
                'data_collected': False,
                'models_trained': False
            }
    
    def schedule_periodic_save(self):
        """Programme la sauvegarde automatique périodique des données IA"""
        try:
            def periodic_save():
                """Sauvegarde périodique des données IA"""
                try:
                    if self.ai_system and (self.ai_config['learning_enabled'] or self.ai_config['use_custom_recommendations']):
                        # Sauvegarder les données IA
                        if hasattr(self.ai_system, 'save_data'):
                            self.ai_system.save_data()
                            print("🤖 AI Menu: Sauvegarde automatique des données IA")
                        
                        # Sauvegarder la configuration
                        self.save_ai_config()
                        
                except Exception as e:
                    print(f"⚠️ AI Menu: Erreur sauvegarde périodique: {e}")
                
                # Programmer la prochaine sauvegarde dans 5 minutes
                if hasattr(self.main_app, 'root') and self.main_app.root.winfo_exists():
                    self.main_app.root.after(300000, periodic_save)  # 5 minutes = 300000 ms
            
            # Programmer la première sauvegarde dans 2 minutes
            if hasattr(self.main_app, 'root'):
                self.main_app.root.after(120000, periodic_save)  # 2 minutes = 120000 ms
                print("🤖 AI Menu: Sauvegarde automatique programmée (toutes les 5 minutes)")
                
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur programmation sauvegarde périodique: {e}")
    
    def _sync_learning_var(self, *args):
        """Synchronise la variable learning avec la configuration"""
        try:
            # Cette méthode est appelée automatiquement quand learning_var change
            # Elle évite les boucles infinies lors du chargement de la config
            pass
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur sync learning var: {e}")
    
    def _sync_recommendations_var(self, *args):
        """Synchronise la variable recommendations avec la configuration"""
        try:
            # Cette méthode est appelée automatiquement quand recommendations_var change
            # Elle évite les boucles infinies lors du chargement de la config
            pass
        except Exception as e:
            print(f"⚠️ AI Menu: Erreur sync recommendations var: {e}")

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