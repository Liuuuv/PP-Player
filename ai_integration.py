"""
Module d'intégration du système d'IA avec l'application musicale
Connecte les événements de l'application avec le système d'IA de recommandation
"""

import os
import time
from ai_recommendation_system import MusicAIRecommendationSystem

class AIIntegrationManager:
    """
    Gestionnaire d'intégration entre l'application musicale et le système d'IA
    """
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.ai_system = None
        self.is_enabled = True
        
        # Variables de tracking
        self.last_volume = None
        self.current_song_start_time = None
        
        # Initialiser le système d'IA
        self.initialize_ai_system()
        
        # Connecter les événements
        self.connect_events()
        
        print("🔗 AI Integration: Gestionnaire d'intégration initialisé")
    
    def initialize_ai_system(self):
        """Initialise le système d'IA"""
        try:
            self.ai_system = MusicAIRecommendationSystem(self.main_app)
            print("🔗 AI Integration: Système d'IA initialisé")
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur initialisation IA: {e}")
            self.is_enabled = False
    
    def connect_events(self):
        """Connecte les événements de l'application avec le système d'IA"""
        if not self.is_enabled or not self.ai_system:
            return
        
        try:
            # Sauvegarder les méthodes originales
            self._original_play_track = self.main_app.play_track
            self._original_next_track = self.main_app.next_track
            self._original_set_volume = getattr(self.main_app, 'set_volume', None)
            
            # Remplacer par nos versions avec tracking IA
            self.main_app.play_track = self._ai_play_track
            self.main_app.next_track = self._ai_next_track
            
            if self._original_set_volume:
                self.main_app.set_volume = self._ai_set_volume
            
            # Connecter les événements de like/favoris si ils existent
            self._connect_like_favorite_events()
            
            print("🔗 AI Integration: Événements connectés")
            
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur connexion événements: {e}")
    
    def _connect_like_favorite_events(self):
        """Connecte les événements de like et favoris"""
        try:
            # Chercher les méthodes de like/favoris dans l'application
            if hasattr(self.main_app, 'toggle_like'):
                self._original_toggle_like = self.main_app.toggle_like
                self.main_app.toggle_like = self._ai_toggle_like
            
            if hasattr(self.main_app, 'toggle_favorite'):
                self._original_toggle_favorite = self.main_app.toggle_favorite
                self.main_app.toggle_favorite = self._ai_toggle_favorite
            
            # Chercher d'autres méthodes possibles
            for attr_name in dir(self.main_app):
                if 'like' in attr_name.lower() and callable(getattr(self.main_app, attr_name)):
                    print(f"🔗 AI Integration: Méthode like trouvée: {attr_name}")
                if 'favorite' in attr_name.lower() and callable(getattr(self.main_app, attr_name)):
                    print(f"🔗 AI Integration: Méthode favorite trouvée: {attr_name}")
                    
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur connexion like/favorite: {e}")
    
    def _ai_play_track(self, *args, **kwargs):
        """Version IA de play_track qui track le début des chansons"""
        try:
            # Finaliser la chanson précédente si nécessaire
            if (self.current_song_start_time and 
                hasattr(self.main_app, 'main_playlist') and 
                hasattr(self.main_app, 'current_index') and
                self.main_app.main_playlist and 
                self.main_app.current_index < len(self.main_app.main_playlist)):
                
                previous_song = self.main_app.main_playlist[self.main_app.current_index]
                listening_duration = time.time() - self.current_song_start_time
                self.ai_system.on_song_end(previous_song, was_skipped=False, listening_duration=listening_duration)
            
            # Appeler la méthode originale
            result = self._original_play_track(*args, **kwargs)
            
            # Tracker le début de la nouvelle chanson
            if (hasattr(self.main_app, 'main_playlist') and 
                hasattr(self.main_app, 'current_index') and
                self.main_app.main_playlist and 
                self.main_app.current_index < len(self.main_app.main_playlist)):
                
                current_song = self.main_app.main_playlist[self.main_app.current_index]
                self.ai_system.on_song_start(current_song)
                self.current_song_start_time = time.time()
            
            return result
            
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur _ai_play_track: {e}")
            return self._original_play_track(*args, **kwargs)
    
    def _ai_next_track(self, *args, **kwargs):
        """Version IA de next_track qui détecte les skips"""
        try:
            # Détecter si c'est un skip (chanson pas finie)
            was_skipped = False
            listening_duration = 0
            
            if (self.current_song_start_time and 
                hasattr(self.main_app, 'main_playlist') and 
                hasattr(self.main_app, 'current_index') and
                self.main_app.main_playlist and 
                self.main_app.current_index < len(self.main_app.main_playlist)):
                
                current_song = self.main_app.main_playlist[self.main_app.current_index]
                listening_duration = time.time() - self.current_song_start_time
                
                # Déterminer si c'est un skip basé sur la durée écoutée
                try:
                    import mutagen
                    audio_file = mutagen.File(current_song)
                    if audio_file and hasattr(audio_file.info, 'length'):
                        song_duration = audio_file.info.length
                        listening_ratio = listening_duration / song_duration if song_duration > 0 else 0
                        was_skipped = listening_ratio < 0.8  # Skip si moins de 80% écouté
                    else:
                        was_skipped = listening_duration < 30  # Skip si moins de 30 secondes
                except:
                    was_skipped = listening_duration < 30
                
                # Notifier l'IA
                self.ai_system.on_song_end(current_song, was_skipped=was_skipped, listening_duration=listening_duration)
            
            # Appeler la méthode originale
            result = self._original_next_track(*args, **kwargs)
            
            # Tracker le début de la nouvelle chanson
            if (hasattr(self.main_app, 'main_playlist') and 
                hasattr(self.main_app, 'current_index') and
                self.main_app.main_playlist and 
                self.main_app.current_index < len(self.main_app.main_playlist)):
                
                new_song = self.main_app.main_playlist[self.main_app.current_index]
                self.ai_system.on_song_start(new_song)
                self.current_song_start_time = time.time()
            
            return result
            
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur _ai_next_track: {e}")
            return self._original_next_track(*args, **kwargs)
    
    def _ai_set_volume(self, val, *args, **kwargs):
        """Version IA de set_volume qui track les changements de volume"""
        try:
            old_volume = self.last_volume or getattr(self.main_app, 'volume', 0.5)
            
            # Appeler la méthode originale
            result = self._original_set_volume(val, *args, **kwargs)
            
            new_volume = float(val) / 100 if isinstance(val, (int, float)) else val
            
            # Notifier l'IA du changement de volume
            if (hasattr(self.main_app, 'main_playlist') and 
                hasattr(self.main_app, 'current_index') and
                self.main_app.main_playlist and 
                self.main_app.current_index < len(self.main_app.main_playlist)):
                
                current_song = self.main_app.main_playlist[self.main_app.current_index]
                self.ai_system.on_volume_changed(current_song, old_volume, new_volume)
            
            self.last_volume = new_volume
            return result
            
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur _ai_set_volume: {e}")
            return self._original_set_volume(val, *args, **kwargs)
    
    def _ai_toggle_like(self, *args, **kwargs):
        """Version IA de toggle_like qui track les likes"""
        try:
            # Appeler la méthode originale
            result = self._original_toggle_like(*args, **kwargs)
            
            # Notifier l'IA du like
            if (hasattr(self.main_app, 'main_playlist') and 
                hasattr(self.main_app, 'current_index') and
                self.main_app.main_playlist and 
                self.main_app.current_index < len(self.main_app.main_playlist)):
                
                current_song = self.main_app.main_playlist[self.main_app.current_index]
                
                # Vérifier si la chanson a été likée ou unlikée
                if hasattr(self.main_app, 'liked_songs'):
                    if current_song in self.main_app.liked_songs:
                        self.ai_system.on_song_liked(current_song)
                        print(f"🔗 AI Integration: Like détecté pour {os.path.basename(current_song)}")
            
            return result
            
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur _ai_toggle_like: {e}")
            return self._original_toggle_like(*args, **kwargs)
    
    def _ai_toggle_favorite(self, *args, **kwargs):
        """Version IA de toggle_favorite qui track les favoris"""
        try:
            # Appeler la méthode originale
            result = self._original_toggle_favorite(*args, **kwargs)
            
            # Notifier l'IA du favori
            if (hasattr(self.main_app, 'main_playlist') and 
                hasattr(self.main_app, 'current_index') and
                self.main_app.main_playlist and 
                self.main_app.current_index < len(self.main_app.main_playlist)):
                
                current_song = self.main_app.main_playlist[self.main_app.current_index]
                
                # Vérifier si la chanson a été mise en favoris
                if hasattr(self.main_app, 'favorite_songs'):
                    if current_song in self.main_app.favorite_songs:
                        self.ai_system.on_song_favorited(current_song)
                        print(f"🔗 AI Integration: Favori détecté pour {os.path.basename(current_song)}")
            
            return result
            
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur _ai_toggle_favorite: {e}")
            return self._original_toggle_favorite(*args, **kwargs)
    
    def get_ai_recommendation(self, candidate_songs):
        """Obtient une recommandation IA parmi une liste de chansons candidates"""
        if not self.is_enabled or not self.ai_system:
            return candidate_songs[0] if candidate_songs else None
        
        try:
            return self.ai_system.recommend_best_song(candidate_songs)
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur recommandation: {e}")
            return candidate_songs[0] if candidate_songs else None
    
    def train_ai_models(self):
        """Lance l'entraînement des modèles IA"""
        if not self.is_enabled or not self.ai_system:
            print("⚠️ AI Integration: IA non disponible pour l'entraînement")
            return
        
        try:
            self.ai_system.train_models()
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur entraînement: {e}")
    
    def get_ai_insights(self):
        """Obtient les insights IA sur les habitudes d'écoute"""
        if not self.is_enabled or not self.ai_system:
            return {}
        
        try:
            return self.ai_system.get_ai_insights()
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur insights: {e}")
            return {}
    
    def should_retrain_models(self):
        """Vérifie s'il faut réentraîner les modèles"""
        if not self.is_enabled or not self.ai_system:
            return False
        
        try:
            return self.ai_system.should_retrain_models()
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur vérification réentraînement: {e}")
            return False
    
    def cleanup_old_data(self):
        """Nettoie les anciennes données IA"""
        if not self.is_enabled or not self.ai_system:
            return
        
        try:
            self.ai_system.cleanup_old_data()
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur nettoyage: {e}")
    
    def save_session(self):
        """Sauvegarde la session courante"""
        if not self.is_enabled or not self.ai_system:
            return
        
        try:
            self.ai_system.save_session_data()
        except Exception as e:
            print(f"⚠️ AI Integration: Erreur sauvegarde session: {e}")
    
    def enable_ai(self):
        """Active le système d'IA"""
        self.is_enabled = True
        if not self.ai_system:
            self.initialize_ai_system()
        print("🔗 AI Integration: IA activée")
    
    def disable_ai(self):
        """Désactive le système d'IA"""
        self.is_enabled = False
        print("🔗 AI Integration: IA désactivée")
    
    def get_status(self):
        """Retourne le statut du système d'IA"""
        return {
            'enabled': self.is_enabled,
            'ai_system_available': self.ai_system is not None,
            'ml_available': hasattr(self.ai_system, 'ML_AVAILABLE') and self.ai_system.ML_AVAILABLE if self.ai_system else False,
            'models_trained': any(model is not None for model in self.ai_system.models.values()) if self.ai_system else False
        }

# Fonction d'intégration principale
def setup_ai_integration(main_app):
    """Configure l'intégration IA avec l'application principale"""
    try:
        ai_manager = AIIntegrationManager(main_app)
        
        # Stocker la référence dans l'app principale
        main_app.ai_integration_manager = ai_manager
        
        # Ajouter des méthodes de convenance à l'app principale
        main_app.get_ai_recommendation = ai_manager.get_ai_recommendation
        main_app.train_ai_models = ai_manager.train_ai_models
        main_app.get_ai_insights = ai_manager.get_ai_insights
        main_app.ai_should_retrain = ai_manager.should_retrain_models
        main_app.ai_cleanup = ai_manager.cleanup_old_data
        main_app.ai_save_session = ai_manager.save_session
        main_app.ai_enable = ai_manager.enable_ai
        main_app.ai_disable = ai_manager.disable_ai
        main_app.ai_status = ai_manager.get_status
        
        print("🔗 AI Integration: Intégration configurée avec succès")
        return ai_manager
        
    except Exception as e:
        print(f"⚠️ AI Integration: Erreur configuration: {e}")
        return None

if __name__ == "__main__":
    # Test de l'intégration
    print("🔗 Test de l'intégration IA")
    
    class MockApp:
        def __init__(self):
            self.main_playlist = ["song1.mp3", "song2.mp3"]
            self.current_index = 0
            self.volume = 0.5
            self.liked_songs = set()
            self.favorite_songs = set()
        
        def play_track(self):
            print("Mock: play_track appelé")
        
        def next_track(self):
            print("Mock: next_track appelé")
            self.current_index = (self.current_index + 1) % len(self.main_playlist)
        
        def set_volume(self, val):
            print(f"Mock: set_volume appelé avec {val}")
            self.volume = val
    
    mock_app = MockApp()
    ai_manager = setup_ai_integration(mock_app)
    
    if ai_manager:
        # Test des fonctionnalités
        print("Status:", mock_app.ai_status())
        
        # Simuler quelques actions
        mock_app.play_track()
        time.sleep(1)
        mock_app.next_track()
        
        # Obtenir des insights
        insights = mock_app.get_ai_insights()
        print("Insights:", insights)