from __init__ import *
from ytmusicapi import YTMusic
import re
import threading
import time
import random
import file_services
import download_manager

class RecommendationSystem:
    """Système de recommandation basé sur YouTube Music"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.ytmusic = YTMusic()  # Session anonyme
        self.is_processing = False
        self.last_processed_song = None
        
        # Configuration de base
        self.recommendations_count = 3
        self.enable_auto_recommendations = False
        
        # Variables pour le mode sparse
        self.songs_played_since_last_recommendation = 0
        self.next_recommendation_threshold = random.randint(
            RECOMMENDATION_SPARSE_MIN_SONGS, 
            RECOMMENDATION_SPARSE_MAX_SONGS
        )
        
        # Variables pour le mode add
        self.current_song_recommendations_added = 0
        self.current_song_for_add_mode = None
        
    def extract_video_id_from_filepath(self, filepath):
        """Extrait l'ID vidéo YouTube depuis les métadonnées du fichier"""
        try:
            # Récupérer les métadonnées YouTube du fichier
            metadata = self.main_app.get_youtube_metadata(filepath)
            if metadata and metadata.get('url'):
                youtube_url = metadata['url']
                # Extraire l'ID vidéo de l'URL
                video_id_match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', youtube_url)
                if video_id_match:
                    return video_id_match.group(1)
            return None
        except Exception as e:
            print(f"Erreur extraction video_id: {e}")
            return None
    
    def get_recommendations_for_video(self, video_id):
        """Récupère les recommandations YouTube Music pour une vidéo"""
        try:
            if not video_id:
                return []
            
            print(f"Récupération des recommandations pour video_id: {video_id}")
            
            # Obtenir la playlist d'autoplay
            autoplay_playlist = self.ytmusic.get_watch_playlist(video_id)
            
            if not autoplay_playlist or 'tracks' not in autoplay_playlist:
                print("Aucune recommandation trouvée")
                return []
            
            recommendations = []
            for track in autoplay_playlist['tracks']:
                if track.get('videoId') and track.get('title'):
                    recommendations.append({
                        'title': track['title'],
                        'videoId': track['videoId'],
                        'url': f"https://youtube.com/watch?v={track['videoId']}",
                        'artists': track.get('artists', [])
                    })
            
            print(f"Trouvé {len(recommendations)} recommandations")
            return recommendations
            
        except Exception as e:
            print(f"Erreur récupération recommandations: {e}")
            return []
    
    def filter_new_recommendations(self, recommendations):
        """Filtre les recommandations pour éviter les doublons avec la playlist actuelle"""
        try:
            # Récupérer les URLs YouTube déjà présentes dans la playlist
            existing_video_ids = set()
            
            for filepath in self.main_app.main_playlist:
                metadata = self.main_app.get_youtube_metadata(filepath)
                if metadata and metadata.get('url'):
                    video_id_match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', metadata['url'])
                    if video_id_match:
                        existing_video_ids.add(video_id_match.group(1))
            
            # Filtrer les recommandations
            filtered_recommendations = []
            for rec in recommendations:
                if rec['videoId'] not in existing_video_ids:
                    filtered_recommendations.append(rec)
                    if len(filtered_recommendations) >= self.recommendations_count:
                        break
            
            # Utiliser l'IA pour sélectionner les meilleures recommandations si activé
            if (hasattr(self.main_app, 'ai_menu_system') and 
                self.main_app.ai_menu_system and 
                self.main_app.ai_menu_system.is_recommendations_enabled() and
                filtered_recommendations):
                
                try:
                    filtered_recommendations = self.apply_ai_recommendation_selection(filtered_recommendations)
                    print("🤖 Sélection IA appliquée aux recommandations")
                except Exception as e:
                    print(f"⚠️ Erreur sélection IA: {e}")
            
            print(f"Recommandations filtrées: {len(filtered_recommendations)}/{len(recommendations)}")
            return filtered_recommendations
            
        except Exception as e:
            print(f"Erreur filtrage recommandations: {e}")
            return recommendations[:self.recommendations_count]
    
    def download_recommendations(self, recommendations):
        """Télécharge les recommandations en utilisant le gestionnaire centralisé"""
        if not recommendations:
            return

        print(f"Téléchargement de {len(recommendations)} recommandations...")

        # Déterminer le callback selon le mode de recommandation
        recommendation_mode = getattr(self.main_app, 'recommendation_mode', 'sparse')
        
        if recommendation_mode == "sparse":
            # Mode sparse: ajouter à la queue
            callback = download_manager.add_to_queue_after_download
            message_prefix = "recommandation éparse ajoutée à la queue"
        else:
            # Mode add: ajouter à la playlist principale
            # callback = download_manager.add_to_playlist_after_download
            callback = download_manager.add_to_queue_after_download
            message_prefix = "recommandation(s) ajoutée(s) à la playlist (mode add)"
        
        # Compteur pour les téléchargements terminés
        self.recommendation_downloads_completed = 0
        self.recommendation_downloads_total = len(recommendations)
        
        def on_recommendation_complete(filepath):
            """Callback appelé quand une recommandation est téléchargée"""
            self.recommendation_downloads_completed += 1
            
            # Appeler le callback approprié selon le mode
            callback(self.main_app, filepath)
            
            # Mettre à jour le message de statut
            if self.recommendation_downloads_completed == self.recommendation_downloads_total:
                # Tous les téléchargements terminés
                message = f"{self.recommendation_downloads_completed} {message_prefix}"
                self.main_app.root.after(0, lambda msg=message:
                    self.main_app.status_bar.config(text=msg))
                
                # Marquer le traitement comme terminé
                self.is_processing = False
            else:
                # Téléchargements en cours
                message = f"Recommandations: {self.recommendation_downloads_completed}/{self.recommendation_downloads_total}"
                self.main_app.root.after(0, lambda msg=message:
                    self.main_app.status_bar.config(text=msg))
        
        # Lancer les téléchargements
        for rec in recommendations:
            try:
                download_manager.download_youtube_video(
                    self.main_app,
                    rec['url'],
                    rec['title'],
                    callback_on_complete=on_recommendation_complete
                )
            except Exception as e:
                print(f"Erreur lancement téléchargement recommandation {rec['title']}: {e}")
                # Décrémenter le total si le téléchargement n'a pas pu être lancé
                self.recommendation_downloads_total -= 1
        
    
    def process_recommendations_for_current_song(self):
        """Traite les recommandations pour la chanson en cours selon le mode configuré"""
        if self.is_processing or not self.enable_auto_recommendations:
            return
        
        try:
            # Vérifier qu'il y a une chanson en cours
            if (not self.main_app.main_playlist or 
                self.main_app.current_index >= len(self.main_app.main_playlist)):
                return
            
            current_song = self.main_app.main_playlist[self.main_app.current_index]
            
            # Déterminer le mode de recommandation
            recommendation_mode = getattr(self.main_app, 'recommendation_mode', 'sparse')
            
            if recommendation_mode == "sparse":
                self._process_sparse_mode(current_song)
            elif recommendation_mode == "add":
                self._process_add_mode(current_song)
            
        except Exception as e:
            print(f"Erreur process_recommendations_for_current_song: {e}")
            self.is_processing = False

    def _process_sparse_mode(self, current_song):
        """Traite les recommandations en mode éparse"""
        # Éviter de traiter la même chanson plusieurs fois
        if current_song == self.last_processed_song:
            return
        
        self.last_processed_song = current_song
        self.songs_played_since_last_recommendation += 1
        
        print(f"Mode sparse: {self.songs_played_since_last_recommendation}/{self.next_recommendation_threshold} chansons")
        
        # Vérifier si on doit ajouter une recommandation
        if self.songs_played_since_last_recommendation >= self.next_recommendation_threshold:
            print("Seuil atteint, ajout d'une recommandation en mode sparse")
            self._add_single_recommendation(current_song)
            
            # Réinitialiser le compteur et définir un nouveau seuil
            self.songs_played_since_last_recommendation = 0
            self.next_recommendation_threshold = random.randint(
                RECOMMENDATION_SPARSE_MIN_SONGS, 
                RECOMMENDATION_SPARSE_MAX_SONGS
            )
            print(f"Nouveau seuil: {self.next_recommendation_threshold} chansons")

    def _process_add_mode(self, current_song):
        """Traite les recommandations en mode add"""
        # Si c'est une nouvelle chanson, réinitialiser le compteur
        if current_song != self.current_song_for_add_mode:
            self.current_song_for_add_mode = current_song
            self.current_song_recommendations_added = 0
            print(f"Mode add: Nouvelle chanson, compteur réinitialisé")
        
        # Vérifier si on peut encore ajouter des recommandations pour cette chanson
        if self.current_song_recommendations_added < RECOMMENDATION_ADD_MAX_LIMIT:
            remaining = RECOMMENDATION_ADD_MAX_LIMIT - self.current_song_recommendations_added
            batch_size = min(RECOMMENDATION_ADD_BATCH_SIZE, remaining)
            
            print(f"Mode add: Ajout de {batch_size} recommandations ({self.current_song_recommendations_added}/{RECOMMENDATION_ADD_MAX_LIMIT})")
            self._add_batch_recommendations(current_song, batch_size)
            
            self.current_song_recommendations_added += batch_size

    def _add_single_recommendation(self, current_song):
        """Ajoute une seule recommandation"""
        self.is_processing = True
        
        def process_thread():
            try:
                video_id = self.extract_video_id_from_filepath(current_song)
                if not video_id:
                    print("Aucun video_id trouvé pour cette chanson")
                    return
                
                recommendations = self.get_recommendations_for_video(video_id)
                if not recommendations:
                    print("Aucune recommandation disponible")
                    return
                
                filtered_recommendations = self.filter_new_recommendations(recommendations)
                if not filtered_recommendations:
                    print("Toutes les recommandations sont déjà dans la playlist")
                    return
                
                # Prendre seulement la première recommandation
                single_recommendation = [filtered_recommendations[0]]
                self.download_recommendations(single_recommendation)

                
            except Exception as e:
                print(f"Erreur ajout recommandation unique: {e}")
            finally:
                self.is_processing = False
        
        threading.Thread(target=process_thread, daemon=True).start()
        
        

    def _add_batch_recommendations(self, current_song, batch_size):
        """Ajoute un batch de recommandations"""
        self.is_processing = True
        
        def process_thread():
            try:
                video_id = self.extract_video_id_from_filepath(current_song)
                if not video_id:
                    print("Aucun video_id trouvé pour cette chanson")
                    return
                
                recommendations = self.get_recommendations_for_video(video_id)
                if not recommendations:
                    print("Aucune recommandation disponible")
                    return
                
                filtered_recommendations = self.filter_new_recommendations(recommendations)
                if not filtered_recommendations:
                    print("Toutes les recommandations sont déjà dans la playlist")
                    return
                
                # Prendre le nombre demandé de recommandations
                batch_recommendations = filtered_recommendations[:batch_size]
                self.download_recommendations(batch_recommendations)
                
            except Exception as e:
                print(f"Erreur ajout batch recommandations: {e}")
            finally:
                self.is_processing = False
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    def enable_recommendations(self):
        """Active le système de recommandations automatiques"""
        self.enable_auto_recommendations = True
        print("Système de recommandations activé")
    
    def disable_recommendations(self):
        """Désactive le système de recommandations automatiques"""
        self.enable_auto_recommendations = False
        print("Système de recommandations désactivé")
    
    def manual_recommendations(self):
        """Lance manuellement les recommandations pour la chanson en cours"""
        if not self.enable_auto_recommendations:
            self.enable_auto_recommendations = True
        self.last_processed_song = None  # Force le retraitement
        self.process_recommendations_for_current_song()

# Fonction d'intégration avec le lecteur principal
def init_recommendation_system(main_app):
    """Initialise le système de recommandation et l'intègre au lecteur"""
    main_app.recommendation_system = RecommendationSystem(main_app)
    
    # Sauvegarder la fonction play_track originale
    original_play_track = main_app.play_track
    
    def enhanced_play_track():
        """Version améliorée de play_track avec recommandations"""
        # Appeler la fonction originale
        result = original_play_track()
        
        # Déclencher les recommandations si activées
        if (hasattr(main_app, 'recommendation_system') and 
            main_app.recommendation_system.enable_auto_recommendations):
            # Petit délai pour laisser la musique commencer
            def delayed_recommendations():
                time.sleep(1)  # Attendre 1 seconde
                main_app.recommendation_system.process_recommendations_for_current_song()
            
            threading.Thread(target=delayed_recommendations, daemon=True).start()
        
        return result
    
    # Remplacer la fonction play_track
    main_app.play_track = enhanced_play_track
    
    print("Système de recommandation initialisé et intégré")
    return main_app.recommendation_system

# Fonction utilitaire pour tester le système
def test_recommendations(video_id="SRF8d_wPXSI"):
    """Fonction de test pour le système de recommandations"""
    try:
        ytmusic = YTMusic()
        autoplay_playlist = ytmusic.get_watch_playlist(video_id)
        
        print(f"Test avec video_id: {video_id}")
        print("Titres dans la playlist :")
        
        if autoplay_playlist and 'tracks' in autoplay_playlist:
            for i, track in enumerate(autoplay_playlist['tracks'][:5]):  # Afficher les 5 premiers
                print(f"{i+1}. {track['title']} - {track['videoId']}")
                print(f"   https://youtube.com/watch?v={track['videoId']}")
        else:
            print("Aucune recommandation trouvée")
            
    except Exception as e:
        print(f"Erreur test: {e}")

if __name__ == "__main__":
    # Test du système si exécuté directement
    test_recommendations()