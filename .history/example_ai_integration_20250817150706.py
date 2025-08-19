"""
Exemple d'intégration du système d'IA dans l'application musicale
Ce fichier montre comment ajouter l'IA à votre application existante
"""

# ÉTAPE 1: Ajouter cette ligne au début de votre fichier main.py ou __init__.py
# (après les autres imports)

"""
# À ajouter dans main.py ou le fichier principal:

try:
    from setup_ai import install_ai_system
    AI_AVAILABLE = True
except ImportError:
    print("⚠️ Système d'IA non disponible")
    AI_AVAILABLE = False
"""

# ÉTAPE 2: Dans la méthode __init__ de votre classe principale, ajouter:

"""
# À ajouter dans __init__ de votre classe principale:

def __init__(self):
    # ... votre code d'initialisation existant ...
    
    # Initialiser le système d'IA à la fin
    if AI_AVAILABLE:
        try:
            self.ai_enabled = install_ai_system(self, create_ui=True, show_help=False)
            if self.ai_enabled:
                print("🤖 Système d'IA activé")
            else:
                print("⚠️ Système d'IA non disponible")
        except Exception as e:
            print(f"⚠️ Erreur initialisation IA: {e}")
            self.ai_enabled = False
    else:
        self.ai_enabled = False
"""

# ÉTAPE 3: Optionnel - Ajouter des raccourcis clavier pour l'IA

"""
# À ajouter dans votre méthode de configuration des raccourcis:

def setup_keyboard_shortcuts(self):
    # ... vos raccourcis existants ...
    
    # Raccourcis IA
    if self.ai_enabled:
        self.root.bind('<Control-i>', lambda e: self.show_ai_insights())
        self.root.bind('<Control-r>', lambda e: self.ai_recommend_from_playlist())
        self.root.bind('<Control-t>', lambda e: self.train_ai_now())
"""

# ÉTAPE 4: Optionnel - Ajouter un menu IA personnalisé

"""
# À ajouter dans votre méthode de création de menu:

def create_menu(self):
    # ... votre code de menu existant ...
    
    # Menu IA personnalisé
    if self.ai_enabled:
        ai_menu = tk.Menu(self.menubar, tearoff=0)
        
        ai_menu.add_command(label="📊 Mes statistiques d'écoute", 
                           command=self.show_ai_insights)
        ai_menu.add_command(label="🎵 Recommandation intelligente", 
                           command=self.ai_recommend_from_playlist)
        ai_menu.add_separator()
        ai_menu.add_command(label="🤖 Entraîner l'IA", 
                           command=self.train_ai_now)
        ai_menu.add_command(label="⚙️ Statut de l'IA", 
                           command=self.show_ai_status)
        ai_menu.add_separator()
        ai_menu.add_command(label="🔄 Activer/Désactiver IA", 
                           command=self.toggle_ai)
        
        self.menubar.add_cascade(label="🤖 IA", menu=ai_menu)
"""

# ÉTAPE 5: Ajouter des méthodes personnalisées pour l'IA

"""
# À ajouter dans votre classe principale:

def show_ai_status(self):
    '''Affiche le statut détaillé de l'IA'''
    if not self.ai_enabled:
        self.status_bar.config(text="IA non disponible")
        return
    
    status = self.ai_status()
    insights = self.get_ai_insights()
    
    status_text = f"IA: {'✅' if status['enabled'] else '❌'} | "
    status_text += f"Sessions: {insights.get('total_sessions', 0)} | "
    status_text += f"Modèles: {'✅' if status['models_trained'] else '❌'}"
    
    self.status_bar.config(text=status_text)
    
    # Afficher plus de détails dans la console
    print("\\n🤖 STATUT DÉTAILLÉ DE L'IA:")
    print(f"  Activé: {status['enabled']}")
    print(f"  Système disponible: {status['ai_system_available']}")
    print(f"  ML disponible: {status['ml_available']}")
    print(f"  Modèles entraînés: {status['models_trained']}")
    print(f"  Sessions d'écoute: {insights.get('total_sessions', 0)}")
    print(f"  Chansons analysées: {insights.get('total_skips', 0) + insights.get('total_likes', 0)}")

def smart_next_track(self):
    '''Version intelligente de next_track qui utilise l'IA'''
    if not self.ai_enabled or not self.main_playlist:
        return self.next_track()  # Fallback vers la méthode normale
    
    # Obtenir quelques chansons candidates de la playlist
    current_pos = self.current_index
    candidates = []
    
    # Prendre les 5 prochaines chansons comme candidates
    for i in range(1, min(6, len(self.main_playlist) - current_pos)):
        next_index = (current_pos + i) % len(self.main_playlist)
        candidates.append(self.main_playlist[next_index])
    
    if candidates:
        # Demander à l'IA de choisir la meilleure
        recommended = self.get_ai_recommendation(candidates)
        if recommended and recommended in self.main_playlist:
            self.current_index = self.main_playlist.index(recommended)
            self.play_track()
            self.status_bar.config(text=f"IA a choisi: {os.path.basename(recommended)}")
            return
    
    # Fallback vers next_track normal
    self.next_track()

def ai_enhanced_shuffle(self):
    '''Mélange intelligent basé sur les préférences IA'''
    if not self.ai_enabled or not self.main_playlist:
        return self._shuffle_remaining_playlist()  # Fallback
    
    try:
        # Obtenir les scores IA pour toutes les chansons
        song_scores = []
        for song in self.main_playlist[self.current_index + 1:]:
            score = self.ai_integration_manager.ai_system.calculate_song_score(song)
            song_scores.append((song, score))
        
        # Trier par score (meilleures chansons en premier)
        song_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Reconstruire la playlist avec un mélange pondéré
        # Les meilleures chansons ont plus de chances d'être en début
        import random
        
        before_current = self.main_playlist[:self.current_index + 1]
        weighted_songs = []
        
        for i, (song, score) in enumerate(song_scores):
            # Plus le score est élevé, plus la chanson a de chances d'être placée tôt
            weight = max(1, int(score * 10))  # Score entre 0-1 devient poids 1-10
            position_bonus = max(1, len(song_scores) - i)  # Bonus pour les mieux classées
            final_weight = weight * position_bonus
            
            weighted_songs.extend([song] * final_weight)
        
        # Mélanger la liste pondérée et prendre les chansons uniques
        random.shuffle(weighted_songs)
        shuffled_unique = []
        seen = set()
        
        for song in weighted_songs:
            if song not in seen:
                shuffled_unique.append(song)
                seen.add(song)
        
        # Reconstruire la playlist
        self.main_playlist = before_current + shuffled_unique
        self._refresh_main_playlist_display()
        
        self.status_bar.config(text=f"Mélange intelligent IA appliqué ({len(shuffled_unique)} titres)")
        
    except Exception as e:
        print(f"⚠️ Erreur mélange IA: {e}")
        # Fallback vers le mélange normal
        self._shuffle_remaining_playlist()

def on_app_closing(self):
    '''Appelé quand l'application se ferme - sauvegarde les données IA'''
    if self.ai_enabled:
        try:
            # Sauvegarder la session courante
            self.ai_save_session()
            print("🤖 Données IA sauvegardées")
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde IA: {e}")
    
    # ... votre code de fermeture existant ...
    self.root.destroy()
"""

# EXEMPLE COMPLET D'INTÉGRATION

def example_integration():
    """
    Exemple complet montrant comment intégrer l'IA dans une application existante
    """
    
    import tkinter as tk
    import os
    import time
    
    # Simuler une application musicale simple
    class MusicPlayerWithAI:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Lecteur Musical avec IA")
            self.root.geometry("600x400")
            
            # Variables de base
            self.main_playlist = []
            self.current_index = 0
            self.volume = 0.5
            self.liked_songs = set()
            self.favorite_songs = set()
            
            # Interface de base
            self.create_interface()
            
            # Initialiser l'IA
            self.setup_ai()
            
            # Simuler quelques chansons pour le test
            self.simulate_playlist()
            
        def create_interface(self):
            """Crée l'interface utilisateur de base"""
            
            # Frame principal
            main_frame = tk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Titre
            title_label = tk.Label(main_frame, text="🎵 Lecteur Musical avec IA", 
                                 font=("Arial", 16, "bold"))
            title_label.pack(pady=10)
            
            # Chanson actuelle
            self.current_song_label = tk.Label(main_frame, text="Aucune chanson", 
                                             font=("Arial", 12))
            self.current_song_label.pack(pady=5)
            
            # Contrôles
            controls_frame = tk.Frame(main_frame)
            controls_frame.pack(pady=10)
            
            tk.Button(controls_frame, text="⏮️ Précédent", 
                     command=self.prev_track).pack(side=tk.LEFT, padx=5)
            tk.Button(controls_frame, text="▶️ Play/Pause", 
                     command=self.play_pause).pack(side=tk.LEFT, padx=5)
            tk.Button(controls_frame, text="⏭️ Suivant", 
                     command=self.next_track).pack(side=tk.LEFT, padx=5)
            
            # Contrôles IA (seront activés si l'IA est disponible)
            ai_frame = tk.Frame(main_frame)
            ai_frame.pack(pady=10)
            
            self.ai_buttons = []
            
            btn1 = tk.Button(ai_frame, text="🧠 Insights IA", state=tk.DISABLED)
            btn1.pack(side=tk.LEFT, padx=5)
            self.ai_buttons.append(btn1)
            
            btn2 = tk.Button(ai_frame, text="🎵 Recommandation", state=tk.DISABLED)
            btn2.pack(side=tk.LEFT, padx=5)
            self.ai_buttons.append(btn2)
            
            btn3 = tk.Button(ai_frame, text="🤖 Entraîner", state=tk.DISABLED)
            btn3.pack(side=tk.LEFT, padx=5)
            self.ai_buttons.append(btn3)
            
            # Barre de statut
            self.status_bar = tk.Label(main_frame, text="Prêt", 
                                     relief=tk.SUNKEN, anchor=tk.W)
            self.status_bar.pack(fill=tk.X, pady=(10, 0))
            
        def setup_ai(self):
            """Configure le système d'IA"""
            try:
                from setup_ai import install_ai_system
                
                self.ai_enabled = install_ai_system(self, create_ui=False, show_help=False)
                
                if self.ai_enabled:
                    # Activer les boutons IA
                    self.ai_buttons[0].config(state=tk.NORMAL, command=self.show_ai_insights)
                    self.ai_buttons[1].config(state=tk.NORMAL, command=self.ai_recommend_from_playlist)
                    self.ai_buttons[2].config(state=tk.NORMAL, command=self.train_ai_now)
                    
                    self.status_bar.config(text="🤖 IA activée et prête")
                    print("✅ IA intégrée avec succès!")
                else:
                    self.status_bar.config(text="⚠️ IA non disponible")
                    
            except Exception as e:
                print(f"⚠️ Erreur intégration IA: {e}")
                self.ai_enabled = False
                self.status_bar.config(text="❌ Erreur IA")
        
        def simulate_playlist(self):
            """Simule une playlist pour les tests"""
            # Créer des fichiers de test fictifs
            test_songs = [
                "Song 1 - Artist A.mp3",
                "Song 2 - Artist B.mp3", 
                "Song 3 - Artist A.mp3",
                "Song 4 - Artist C.mp3",
                "Song 5 - Artist B.mp3"
            ]
            
            self.main_playlist = test_songs
            self.update_display()
            
        def update_display(self):
            """Met à jour l'affichage"""
            if self.main_playlist and self.current_index < len(self.main_playlist):
                current_song = self.main_playlist[self.current_index]
                self.current_song_label.config(text=f"🎵 {current_song}")
            else:
                self.current_song_label.config(text="Aucune chanson")
        
        def play_pause(self):
            """Simule play/pause"""
            self.status_bar.config(text="▶️ Lecture simulée")
            
        def play_track(self):
            """Simule le démarrage d'une chanson"""
            self.update_display()
            if self.ai_enabled:
                # L'IA sera automatiquement notifiée via l'intégration
                pass
            
        def next_track(self):
            """Passe à la chanson suivante"""
            if self.main_playlist:
                self.current_index = (self.current_index + 1) % len(self.main_playlist)
                self.play_track()
                
        def prev_track(self):
            """Passe à la chanson précédente"""
            if self.main_playlist:
                self.current_index = (self.current_index - 1) % len(self.main_playlist)
                self.play_track()
        
        def run(self):
            """Lance l'application"""
            # Simuler quelques actions pour générer des données IA
            if self.ai_enabled:
                self.root.after(2000, self.simulate_user_behavior)
            
            self.root.mainloop()
            
        def simulate_user_behavior(self):
            """Simule le comportement utilisateur pour tester l'IA"""
            import random
            
            # Simuler quelques changements de chanson
            for i in range(3):
                self.root.after(i * 1000, self.next_track)
            
            # Simuler un like
            self.root.after(4000, lambda: self.simulate_like())
            
            # Afficher les insights après quelques actions
            self.root.after(6000, lambda: self.show_ai_insights() if self.ai_enabled else None)
            
        def simulate_like(self):
            """Simule un like"""
            if self.main_playlist and self.current_index < len(self.main_playlist):
                current_song = self.main_playlist[self.current_index]
                self.liked_songs.add(current_song)
                self.status_bar.config(text=f"❤️ {os.path.basename(current_song)} liké")
                
                # Notifier l'IA si disponible
                if self.ai_enabled and hasattr(self, 'ai_integration_manager'):
                    self.ai_integration_manager.ai_system.on_song_liked(current_song)
    
    # Lancer l'exemple
    print("🚀 Lancement de l'exemple d'intégration IA...")
    app = MusicPlayerWithAI()
    app.run()

if __name__ == "__main__":
    print("""
🤖 EXEMPLE D'INTÉGRATION DU SYSTÈME D'IA

Ce fichier montre comment intégrer le système d'IA dans votre application musicale.

Pour intégrer l'IA dans votre application existante:

1. Copiez les fichiers IA dans votre projet:
   - ai_recommendation_system.py
   - ai_integration.py  
   - setup_ai.py

2. Ajoutez l'import au début de votre fichier principal:
   from setup_ai import install_ai_system

3. Dans __init__ de votre classe principale:
   self.ai_enabled = install_ai_system(self)

4. L'IA analysera automatiquement les actions utilisateur!

Voulez-vous voir l'exemple en action? (y/n)
""")
    
    response = input().lower().strip()
    if response in ['y', 'yes', 'oui', 'o']:
        example_integration()
    else:
        print("👋 Consultez le code de ce fichier pour voir les exemples d'intégration!")