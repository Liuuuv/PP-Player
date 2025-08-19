"""
Système d'IA de recommandation musicale basé sur le machine learning
Analyse les comportements utilisateur pour prédire et recommander la meilleure musique
"""

import os
import json
import time
import numpy as np
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import pickle
import hashlib

# Machine Learning imports
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    import pandas as pd
    ML_AVAILABLE = True
    print("🤖 IA: Modules ML disponibles")
except ImportError as e:
    print(f"⚠️ IA: Modules ML non disponibles: {e}")
    print("💡 IA: Installation recommandée: pip install scikit-learn pandas")
    ML_AVAILABLE = False

class MusicAIRecommendationSystem:
    """
    Système d'IA avancé pour recommandations musicales basé sur l'analyse comportementale
    """
    
    def __init__(self, main_app, data_file="ai_music_data.json", model_file="ai_music_model.pkl"):
        self.main_app = main_app
        self.data_file = os.path.join(os.path.dirname(__file__), data_file)
        self.model_file = os.path.join(os.path.dirname(__file__), model_file)
        
        # Données comportementales
        self.user_behavior_data = {
            'listening_sessions': [],  # Sessions d'écoute complètes
            'skip_patterns': [],       # Patterns de skip
            'like_patterns': [],       # Patterns de like
            'favorite_patterns': [],   # Patterns de favoris
            'time_patterns': {},       # Patterns temporels (heure, jour)
            'sequence_patterns': [],   # Séquences de chansons écoutées
            'volume_patterns': {},     # Patterns de volume par chanson
            'mood_indicators': {},     # Indicateurs d'humeur basés sur le comportement
            'song_statistics': {}      # Statistiques détaillées par chanson
        }
        
        # Métriques de session courante
        self.current_session = {
            'start_time': time.time(),
            'songs_played': [],
            'skips': [],
            'likes': [],
            'favorites': [],
            'volume_changes': [],
            'listening_duration': {}
        }
        
        # Modèles ML
        self.models = {
            'skip_predictor': None,      # Prédit si une chanson sera skippée
            'like_predictor': None,      # Prédit si une chanson sera likée
            'mood_classifier': None,     # Classifie l'humeur de l'utilisateur
            'recommendation_ranker': None # Classe les recommandations
        }
        
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.is_training = False
        
        # Chargement des données existantes
        self.load_data()
        
        # Variables de tracking
        self.last_song_start_time = None
        self.last_song_path = None
        self.skip_threshold = 0.3  # Considéré comme skip si < 30% écouté
        
        print("🤖 IA: Système de recommandation initialisé")
        
    def load_data(self):
        """Charge les données comportementales existantes"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_behavior_data.update(data)
                print(f"🤖 IA: Données chargées - {len(self.user_behavior_data['listening_sessions'])} sessions")
            
            # Charger les modèles ML
            if ML_AVAILABLE and os.path.exists(self.model_file):
                with open(self.model_file, 'rb') as f:
                    model_data = pickle.load(f)
                    self.models = model_data.get('models', self.models)
                    self.scaler = model_data.get('scaler', self.scaler)
                print("🤖 IA: Modèles ML chargés")
                
        except Exception as e:
            print(f"⚠️ IA: Erreur chargement données: {e}")
    
    def save_data(self):
        """Sauvegarde les données comportementales"""
        try:
            # Sauvegarder les données comportementales
            with open(self.data_file, 'w', encoding='utf-8') as f:
                # Convertir les sets en listes pour JSON
                data_to_save = {}
                for key, value in self.user_behavior_data.items():
                    if isinstance(value, set):
                        data_to_save[key] = list(value)
                    else:
                        data_to_save[key] = value
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            
            # Sauvegarder les modèles ML
            if ML_AVAILABLE and any(model is not None for model in self.models.values()):
                with open(self.model_file, 'wb') as f:
                    pickle.dump({
                        'models': self.models,
                        'scaler': self.scaler
                    }, f)
                    
            print("🤖 IA: Données sauvegardées")
        except Exception as e:
            print(f"⚠️ IA: Erreur sauvegarde: {e}")
    
    def extract_song_features(self, song_path):
        """Extrait les caractéristiques d'une chanson pour l'analyse ML"""
        try:
            features = {}
            
            # Caractéristiques basiques du fichier
            features['file_size'] = os.path.getsize(song_path) if os.path.exists(song_path) else 0
            features['filename_length'] = len(os.path.basename(song_path))
            
            # Hash du nom pour identifier la chanson de manière unique
            song_hash = hashlib.md5(song_path.encode()).hexdigest()[:8]
            features['song_id'] = song_hash
            
            # Métadonnées audio si disponibles
            try:
                import mutagen
                audio_file = mutagen.File(song_path)
                if audio_file:
                    features['duration'] = audio_file.info.length if hasattr(audio_file.info, 'length') else 0
                    features['bitrate'] = getattr(audio_file.info, 'bitrate', 0)
                    
                    # Tags
                    features['has_artist'] = 1 if audio_file.get('TPE1') or audio_file.get('ARTIST') else 0
                    features['has_album'] = 1 if audio_file.get('TALB') or audio_file.get('ALBUM') else 0
                    features['has_title'] = 1 if audio_file.get('TIT2') or audio_file.get('TITLE') else 0
                else:
                    features.update({'duration': 0, 'bitrate': 0, 'has_artist': 0, 'has_album': 0, 'has_title': 0})
            except:
                features.update({'duration': 0, 'bitrate': 0, 'has_artist': 0, 'has_album': 0, 'has_title': 0})
            
            # Caractéristiques temporelles
            current_time = datetime.now()
            features['hour'] = current_time.hour
            features['day_of_week'] = current_time.weekday()
            features['is_weekend'] = 1 if current_time.weekday() >= 5 else 0
            
            # Historique de la chanson
            song_history = self.get_song_history(song_path)
            features['play_count'] = song_history['play_count']
            features['skip_count'] = song_history['skip_count']
            features['like_count'] = song_history['like_count']
            features['avg_listening_ratio'] = song_history['avg_listening_ratio']
            
            # Position dans la playlist
            if hasattr(self.main_app, 'main_playlist') and hasattr(self.main_app, 'current_index'):
                playlist_size = len(self.main_app.main_playlist)
                if playlist_size > 0:
                    features['playlist_position'] = self.main_app.current_index / playlist_size
                    features['playlist_size'] = playlist_size
                else:
                    features['playlist_position'] = 0
                    features['playlist_size'] = 0
            else:
                features['playlist_position'] = 0
                features['playlist_size'] = 0
            
            return features
            
        except Exception as e:
            print(f"⚠️ IA: Erreur extraction features pour {song_path}: {e}")
            return {}
    
    def get_song_history(self, song_path):
        """Récupère l'historique d'une chanson"""
        history = {
            'play_count': 0,
            'skip_count': 0,
            'like_count': 0,
            'avg_listening_ratio': 0.0
        }
        
        try:
            # Compter dans les sessions d'écoute
            listening_ratios = []
            for session in self.user_behavior_data['listening_sessions']:
                for song_data in session.get('songs', []):
                    if song_data.get('path') == song_path:
                        history['play_count'] += 1
                        listening_ratios.append(song_data.get('listening_ratio', 0))
            
            # Compter les skips
            for skip in self.user_behavior_data['skip_patterns']:
                if skip.get('song_path') == song_path:
                    history['skip_count'] += 1
            
            # Compter les likes
            for like in self.user_behavior_data['like_patterns']:
                if like.get('song_path') == song_path:
                    history['like_count'] += 1
            
            # Calculer la moyenne d'écoute
            if listening_ratios:
                history['avg_listening_ratio'] = np.mean(listening_ratios)
                
        except Exception as e:
            print(f"⚠️ IA: Erreur récupération historique: {e}")
        
        return history
    
    def on_song_start(self, song_path):
        """Appelé quand une chanson commence"""
        print(f"🤖 IA: Début chanson - {os.path.basename(song_path)}")
        
        # Finaliser la chanson précédente si nécessaire
        if self.last_song_path and self.last_song_start_time:
            self.on_song_end(self.last_song_path, was_skipped=True)
        
        self.last_song_path = song_path
        self.last_song_start_time = time.time()
        
        # Ajouter à la session courante
        self.current_session['songs_played'].append({
            'path': song_path,
            'start_time': self.last_song_start_time,
            'features': self.extract_song_features(song_path)
        })
        
        # Prédire le comportement de l'utilisateur
        self.predict_user_behavior(song_path)
    
    def on_song_end(self, song_path, was_skipped=False, listening_duration=None):
        """Appelé quand une chanson se termine"""
        if not self.last_song_start_time:
            return
            
        end_time = time.time()
        total_duration = end_time - self.last_song_start_time
        
        # Calculer le ratio d'écoute
        if listening_duration is None:
            listening_duration = total_duration
            
        # Obtenir la durée réelle de la chanson
        try:
            import mutagen
            audio_file = mutagen.File(song_path)
            actual_duration = audio_file.info.length if audio_file and hasattr(audio_file.info, 'length') else total_duration
        except:
            actual_duration = total_duration
        
        listening_ratio = min(listening_duration / actual_duration, 1.0) if actual_duration > 0 else 0
        
        print(f"🤖 IA: Fin chanson - {os.path.basename(song_path)}")
        print(f"🤖 IA: Ratio d'écoute: {listening_ratio:.2f} ({'skip' if was_skipped or listening_ratio < self.skip_threshold else 'complète'})")
        
        # Enregistrer les données
        song_data = {
            'path': song_path,
            'start_time': self.last_song_start_time,
            'end_time': end_time,
            'listening_duration': listening_duration,
            'total_duration': actual_duration,
            'listening_ratio': listening_ratio,
            'was_skipped': was_skipped or listening_ratio < self.skip_threshold,
            'features': self.extract_song_features(song_path)
        }
        
        # Ajouter aux patterns appropriés
        if song_data['was_skipped']:
            # Analyser le type de skip de manière plus intelligente
            skip_analysis = self.analyze_skip_context(song_path, listening_ratio, was_skipped)
            
            skip_data = {
                'song_path': song_path,
                'timestamp': end_time,
                'listening_ratio': listening_ratio,
                'skip_reason': skip_analysis['reason'],
                'skip_type': skip_analysis['type'],
                'confidence': skip_analysis['confidence'],
                'context': skip_analysis['context']
            }
            
            self.user_behavior_data['skip_patterns'].append(skip_data)
            
            # Mettre à jour les statistiques de la chanson
            self.update_song_statistics(song_path, 'skip', skip_data)
            
            print(f"🤖 IA: Skip détecté - {skip_analysis['type']} ({skip_analysis['confidence']:.0%} confiance)")
        
        # Mettre à jour la session courante
        if self.current_session['songs_played']:
            self.current_session['songs_played'][-1].update(song_data)
        
        # Réinitialiser
        self.last_song_path = None
        self.last_song_start_time = None
        
        # Sauvegarder périodiquement
        if len(self.current_session['songs_played']) % 5 == 0:
            self.save_session_data()
    
    def on_song_liked(self, song_path):
        """Appelé quand une chanson est likée"""
        print(f"🤖 IA: Like détecté - {os.path.basename(song_path)}")
        
        like_data = {
            'song_path': song_path,
            'timestamp': time.time(),
            'features': self.extract_song_features(song_path)
        }
        
        self.user_behavior_data['like_patterns'].append(like_data)
        self.current_session['likes'].append(like_data)
        
        # Analyser le pattern de like
        self.analyze_like_pattern(song_path)
    
    def on_song_favorited(self, song_path):
        """Appelé quand une chanson est mise en favoris"""
        print(f"🤖 IA: Favori détecté - {os.path.basename(song_path)}")
        
        favorite_data = {
            'song_path': song_path,
            'timestamp': time.time(),
            'features': self.extract_song_features(song_path)
        }
        
        self.user_behavior_data['favorite_patterns'].append(favorite_data)
        self.current_session['favorites'].append(favorite_data)
        
        # Analyser le pattern de favori
        self.analyze_favorite_pattern(song_path)
    
    def on_volume_changed(self, song_path, old_volume, new_volume):
        """Appelé quand le volume est changé"""
        volume_change = {
            'song_path': song_path,
            'timestamp': time.time(),
            'old_volume': old_volume,
            'new_volume': new_volume,
            'change_ratio': new_volume / old_volume if old_volume > 0 else 1.0
        }
        
        self.current_session['volume_changes'].append(volume_change)
        
        # Analyser si c'est un indicateur d'humeur
        if new_volume > old_volume * 1.2:
            print("🤖 IA: Volume augmenté significativement - possible indicateur d'appréciation")
        elif new_volume < old_volume * 0.8:
            print("🤖 IA: Volume diminué significativement - possible indicateur de désintérêt")
    
    def predict_user_behavior(self, song_path):
        """Prédit le comportement de l'utilisateur pour une chanson"""
        if not ML_AVAILABLE or not any(model is not None for model in self.models.values()):
            return
        
        try:
            features = self.extract_song_features(song_path)
            if not features:
                return
            
            # Convertir en format ML
            feature_vector = self.features_to_vector(features)
            if feature_vector is None:
                return
            
            feature_vector = feature_vector.reshape(1, -1)
            
            # Prédictions
            predictions = {}
            
            if self.models['skip_predictor'] is not None:
                skip_prob = self.models['skip_predictor'].predict_proba(feature_vector)[0]
                predictions['skip_probability'] = skip_prob[1] if len(skip_prob) > 1 else 0
                print(f"🤖 IA: Probabilité de skip: {predictions['skip_probability']:.2f}")
            
            if self.models['like_predictor'] is not None:
                like_prob = self.models['like_predictor'].predict_proba(feature_vector)[0]
                predictions['like_probability'] = like_prob[1] if len(like_prob) > 1 else 0
                print(f"🤖 IA: Probabilité de like: {predictions['like_probability']:.2f}")
            
            if self.models['mood_classifier'] is not None:
                mood = self.models['mood_classifier'].predict(feature_vector)[0]
                predictions['predicted_mood'] = mood
                print(f"🤖 IA: Humeur prédite: {mood}")
            
            return predictions
            
        except Exception as e:
            print(f"⚠️ IA: Erreur prédiction: {e}")
            return None
    
    def features_to_vector(self, features):
        """Convertit les features en vecteur numérique pour ML"""
        try:
            # Liste des features numériques attendues
            expected_features = [
                'file_size', 'filename_length', 'duration', 'bitrate',
                'has_artist', 'has_album', 'has_title', 'hour', 'day_of_week',
                'is_weekend', 'play_count', 'skip_count', 'like_count',
                'avg_listening_ratio', 'playlist_position', 'playlist_size'
            ]
            
            vector = []
            for feature in expected_features:
                value = features.get(feature, 0)
                # Normaliser certaines valeurs
                if feature == 'file_size':
                    value = value / 1000000  # MB
                elif feature == 'duration':
                    value = value / 300  # Normaliser par 5 minutes
                elif feature == 'bitrate':
                    value = value / 320  # Normaliser par 320 kbps
                
                vector.append(float(value))
            
            return np.array(vector)
            
        except Exception as e:
            print(f"⚠️ IA: Erreur conversion features: {e}")
            return None
    
    def train_models(self):
        """Entraîne les modèles ML avec les données collectées"""
        if not ML_AVAILABLE:
            print("⚠️ IA: ML non disponible pour l'entraînement")
            return
        
        if self.is_training:
            print("🤖 IA: Entraînement déjà en cours")
            return
        
        print("🤖 IA: Début de l'entraînement des modèles...")
        self.is_training = True
        
        def train_thread():
            try:
                # Préparer les données d'entraînement
                training_data = self.prepare_training_data()
                if not training_data:
                    print("⚠️ IA: Pas assez de données pour l'entraînement")
                    return
                
                # Entraîner le prédicteur de skip
                self.train_skip_predictor(training_data)
                
                # Entraîner le prédicteur de like
                self.train_like_predictor(training_data)
                
                # Entraîner le classificateur d'humeur
                self.train_mood_classifier(training_data)
                
                # Sauvegarder les modèles
                self.save_data()
                
                print("🤖 IA: Entraînement terminé avec succès!")
                
            except Exception as e:
                print(f"⚠️ IA: Erreur pendant l'entraînement: {e}")
            finally:
                self.is_training = False
        
        threading.Thread(target=train_thread, daemon=True).start()
    
    def prepare_training_data(self):
        """Prépare les données pour l'entraînement ML"""
        try:
            training_data = {
                'features': [],
                'skip_labels': [],
                'like_labels': [],
                'mood_labels': []
            }
            
            # Collecter les données des sessions d'écoute
            for session in self.user_behavior_data['listening_sessions']:
                for song_data in session.get('songs', []):
                    features = song_data.get('features', {})
                    if not features:
                        continue
                    
                    feature_vector = self.features_to_vector(features)
                    if feature_vector is None:
                        continue
                    
                    training_data['features'].append(feature_vector)
                    
                    # Labels pour skip
                    was_skipped = song_data.get('was_skipped', False)
                    training_data['skip_labels'].append(1 if was_skipped else 0)
                    
                    # Labels pour like (chercher dans les patterns de like)
                    song_path = song_data.get('path', '')
                    is_liked = any(like['song_path'] == song_path for like in self.user_behavior_data['like_patterns'])
                    training_data['like_labels'].append(1 if is_liked else 0)
                    
                    # Labels pour mood (basé sur le comportement)
                    listening_ratio = song_data.get('listening_ratio', 0)
                    if listening_ratio > 0.8:
                        mood = 'positive'
                    elif listening_ratio < 0.3:
                        mood = 'negative'
                    else:
                        mood = 'neutral'
                    training_data['mood_labels'].append(mood)
            
            print(f"🤖 IA: {len(training_data['features'])} échantillons préparés pour l'entraînement")
            return training_data if len(training_data['features']) >= 10 else None
            
        except Exception as e:
            print(f"⚠️ IA: Erreur préparation données: {e}")
            return None
    
    def train_skip_predictor(self, training_data):
        """Entraîne le modèle de prédiction de skip"""
        try:
            X = np.array(training_data['features'])
            y = np.array(training_data['skip_labels'])
            
            if len(np.unique(y)) < 2:
                print("⚠️ IA: Pas assez de variété dans les données de skip")
                return
            
            # Normaliser les features
            X_scaled = self.scaler.fit_transform(X)
            
            # Diviser les données
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
            
            # Entraîner le modèle
            self.models['skip_predictor'] = RandomForestClassifier(n_estimators=100, random_state=42)
            self.models['skip_predictor'].fit(X_train, y_train)
            
            # Évaluer
            y_pred = self.models['skip_predictor'].predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"🤖 IA: Prédicteur de skip entraîné - Précision: {accuracy:.2f}")
            
        except Exception as e:
            print(f"⚠️ IA: Erreur entraînement skip predictor: {e}")
    
    def train_like_predictor(self, training_data):
        """Entraîne le modèle de prédiction de like"""
        try:
            X = np.array(training_data['features'])
            y = np.array(training_data['like_labels'])
            
            if len(np.unique(y)) < 2:
                print("⚠️ IA: Pas assez de variété dans les données de like")
                return
            
            X_scaled = self.scaler.transform(X)
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
            
            self.models['like_predictor'] = GradientBoostingClassifier(n_estimators=100, random_state=42)
            self.models['like_predictor'].fit(X_train, y_train)
            
            y_pred = self.models['like_predictor'].predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"🤖 IA: Prédicteur de like entraîné - Précision: {accuracy:.2f}")
            
        except Exception as e:
            print(f"⚠️ IA: Erreur entraînement like predictor: {e}")
    
    def train_mood_classifier(self, training_data):
        """Entraîne le classificateur d'humeur"""
        try:
            X = np.array(training_data['features'])
            y = np.array(training_data['mood_labels'])
            
            if len(np.unique(y)) < 2:
                print("⚠️ IA: Pas assez de variété dans les données d'humeur")
                return
            
            X_scaled = self.scaler.transform(X)
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
            
            self.models['mood_classifier'] = LogisticRegression(random_state=42, max_iter=1000)
            self.models['mood_classifier'].fit(X_train, y_train)
            
            y_pred = self.models['mood_classifier'].predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"🤖 IA: Classificateur d'humeur entraîné - Précision: {accuracy:.2f}")
            
        except Exception as e:
            print(f"⚠️ IA: Erreur entraînement mood classifier: {e}")
    
    def recommend_best_song(self, candidate_songs):
        """Recommande la meilleure chanson parmi une liste de candidats"""
        if not candidate_songs:
            return None
        
        print(f"🤖 IA: Analyse de {len(candidate_songs)} chansons candidates")
        
        best_song = None
        best_score = -1
        
        for song_path in candidate_songs:
            score = self.calculate_song_score(song_path)
            print(f"🤖 IA: {os.path.basename(song_path)} - Score: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_song = song_path
        
        if best_song:
            print(f"🤖 IA: Meilleure recommandation: {os.path.basename(best_song)} (Score: {best_score:.3f})")
        
        return best_song
    
    def calculate_song_score(self, song_path):
        """Calcule un score de recommandation pour une chanson"""
        try:
            features = self.extract_song_features(song_path)
            if not features:
                return 0.0
            
            score = 0.0
            
            # Score basé sur l'historique
            history = self.get_song_history(song_path)
            
            # Bonus pour les chansons avec un bon ratio d'écoute
            score += history['avg_listening_ratio'] * 0.3
            
            # Malus pour les chansons souvent skippées
            if history['play_count'] > 0:
                skip_ratio = history['skip_count'] / history['play_count']
                score -= skip_ratio * 0.2
            
            # Bonus pour les chansons likées
            if history['like_count'] > 0:
                score += min(history['like_count'] * 0.1, 0.3)
            
            # Score basé sur les prédictions ML
            if ML_AVAILABLE and any(model is not None for model in self.models.values()):
                predictions = self.predict_user_behavior(song_path)
                if predictions:
                    # Bonus si faible probabilité de skip
                    if 'skip_probability' in predictions:
                        score += (1 - predictions['skip_probability']) * 0.2
                    
                    # Bonus si haute probabilité de like
                    if 'like_probability' in predictions:
                        score += predictions['like_probability'] * 0.2
            
            # Score basé sur le contexte temporel
            current_hour = datetime.now().hour
            
            # Analyser les patterns temporels pour cette chanson
            temporal_score = self.get_temporal_score(song_path, current_hour)
            score += temporal_score * 0.1
            
            # Normaliser le score entre 0 et 1
            score = max(0, min(1, score))
            
            return score
            
        except Exception as e:
            print(f"⚠️ IA: Erreur calcul score pour {song_path}: {e}")
            return 0.0
    
    def get_temporal_score(self, song_path, current_hour):
        """Calcule un score basé sur les patterns temporels"""
        try:
            # Analyser quand cette chanson a été écoutée dans le passé
            hour_plays = defaultdict(int)
            total_plays = 0
            
            for session in self.user_behavior_data['listening_sessions']:
                for song_data in session.get('songs', []):
                    if song_data.get('path') == song_path:
                        song_features = song_data.get('features', {})
                        hour = song_features.get('hour', current_hour)
                        hour_plays[hour] += 1
                        total_plays += 1
            
            if total_plays == 0:
                return 0.5  # Score neutre si pas d'historique
            
            # Score basé sur la fréquence d'écoute à cette heure
            current_hour_plays = hour_plays.get(current_hour, 0)
            return current_hour_plays / total_plays
            
        except Exception as e:
            print(f"⚠️ IA: Erreur calcul score temporel: {e}")
            return 0.5
    
    def analyze_like_pattern(self, song_path):
        """Analyse le pattern de like pour une chanson"""
        try:
            features = self.extract_song_features(song_path)
            
            # Analyser les caractéristiques communes des chansons likées
            liked_features = []
            for like in self.user_behavior_data['like_patterns']:
                if 'features' in like:
                    liked_features.append(like['features'])
            
            if len(liked_features) >= 3:
                # Analyser les patterns (durée, heure, etc.)
                durations = [f.get('duration', 0) for f in liked_features]
                hours = [f.get('hour', 12) for f in liked_features]
                
                avg_duration = np.mean(durations) if durations else 0
                preferred_hours = max(set(hours), key=hours.count) if hours else 12
                
                print(f"🤖 IA: Pattern de like détecté - Durée moyenne: {avg_duration:.0f}s, Heure préférée: {preferred_hours}h")
                
        except Exception as e:
            print(f"⚠️ IA: Erreur analyse pattern like: {e}")
    
    def analyze_favorite_pattern(self, song_path):
        """Analyse le pattern de favoris pour une chanson"""
        try:
            print(f"🤖 IA: Analyse du pattern de favori pour {os.path.basename(song_path)}")
            
            # Les favoris indiquent une très forte préférence
            # Augmenter le poids de cette chanson dans les recommandations futures
            
        except Exception as e:
            print(f"⚠️ IA: Erreur analyse pattern favori: {e}")
    
    def save_session_data(self):
        """Sauvegarde les données de la session courante"""
        try:
            if self.current_session['songs_played']:
                session_data = {
                    'start_time': self.current_session['start_time'],
                    'end_time': time.time(),
                    'songs': self.current_session['songs_played'].copy(),
                    'total_songs': len(self.current_session['songs_played']),
                    'skips': len(self.current_session['skips']),
                    'likes': len(self.current_session['likes']),
                    'favorites': len(self.current_session['favorites'])
                }
                
                self.user_behavior_data['listening_sessions'].append(session_data)
                
                # Garder seulement les 100 dernières sessions
                if len(self.user_behavior_data['listening_sessions']) > 100:
                    self.user_behavior_data['listening_sessions'] = self.user_behavior_data['listening_sessions'][-100:]
                
                print(f"🤖 IA: Session sauvegardée - {session_data['total_songs']} chansons")
                
                # Réinitialiser la session courante
                self.current_session = {
                    'start_time': time.time(),
                    'songs_played': [],
                    'skips': [],
                    'likes': [],
                    'favorites': [],
                    'volume_changes': [],
                    'listening_duration': {}
                }
                
                self.save_data()
                
        except Exception as e:
            print(f"⚠️ IA: Erreur sauvegarde session: {e}")
    
    def get_ai_insights(self):
        """Retourne des insights sur les habitudes d'écoute de l'utilisateur"""
        try:
            insights = {
                'total_sessions': len(self.user_behavior_data['listening_sessions']),
                'total_skips': len(self.user_behavior_data['skip_patterns']),
                'total_likes': len(self.user_behavior_data['like_patterns']),
                'total_favorites': len(self.user_behavior_data['favorite_patterns']),
                'skip_rate': 0,
                'like_rate': 0,
                'preferred_hours': [],
                'model_accuracy': {}
            }
            
            # Calculer les taux
            total_songs = sum(len(session.get('songs', [])) for session in self.user_behavior_data['listening_sessions'])
            if total_songs > 0:
                insights['skip_rate'] = insights['total_skips'] / total_songs
                insights['like_rate'] = insights['total_likes'] / total_songs
            
            # Analyser les heures préférées
            hours = []
            for session in self.user_behavior_data['listening_sessions']:
                for song in session.get('songs', []):
                    features = song.get('features', {})
                    if 'hour' in features:
                        hours.append(features['hour'])
            
            if hours:
                from collections import Counter
                hour_counts = Counter(hours)
                insights['preferred_hours'] = [hour for hour, count in hour_counts.most_common(3)]
            
            print("🤖 IA: Insights générés:")
            print(f"  - Sessions: {insights['total_sessions']}")
            print(f"  - Taux de skip: {insights['skip_rate']:.2%}")
            print(f"  - Taux de like: {insights['like_rate']:.2%}")
            print(f"  - Heures préférées: {insights['preferred_hours']}")
            
            return insights
            
        except Exception as e:
            print(f"⚠️ IA: Erreur génération insights: {e}")
            return {}
    
    def should_retrain_models(self):
        """Détermine s'il faut réentraîner les modèles"""
        try:
            # Réentraîner si on a assez de nouvelles données
            total_songs = sum(len(session.get('songs', [])) for session in self.user_behavior_data['listening_sessions'])
            
            # Réentraîner tous les 50 chansons écoutées
            return total_songs > 0 and total_songs % 50 == 0
            
        except Exception as e:
            print(f"⚠️ IA: Erreur vérification réentraînement: {e}")
            return False
    
    def cleanup_old_data(self):
        """Nettoie les anciennes données pour optimiser les performances"""
        try:
            # Garder seulement les données des 30 derniers jours
            cutoff_time = time.time() - (30 * 24 * 3600)
            
            # Nettoyer les patterns de skip
            self.user_behavior_data['skip_patterns'] = [
                skip for skip in self.user_behavior_data['skip_patterns']
                if skip.get('timestamp', 0) > cutoff_time
            ]
            
            # Nettoyer les patterns de like
            self.user_behavior_data['like_patterns'] = [
                like for like in self.user_behavior_data['like_patterns']
                if like.get('timestamp', 0) > cutoff_time
            ]
            
            # Nettoyer les patterns de favoris
            self.user_behavior_data['favorite_patterns'] = [
                fav for fav in self.user_behavior_data['favorite_patterns']
                if fav.get('timestamp', 0) > cutoff_time
            ]
            
            print("🤖 IA: Nettoyage des anciennes données effectué")
            
        except Exception as e:
            print(f"⚠️ IA: Erreur nettoyage données: {e}")

# Fonction d'intégration avec l'application principale
def integrate_ai_system(main_app):
    """Intègre le système d'IA avec l'application principale"""
    try:
        # Créer l'instance du système d'IA
        ai_system = MusicAIRecommendationSystem(main_app)
        
        # Stocker la référence dans l'app principale
        main_app.ai_recommendation_system = ai_system
        
        print("🤖 IA: Système intégré avec succès à l'application")
        return ai_system
        
    except Exception as e:
        print(f"⚠️ IA: Erreur intégration: {e}")
        return None

if __name__ == "__main__":
    # Test du système
    print("🤖 Test du système d'IA de recommandation musicale")
    
    class MockApp:
        def __init__(self):
            self.main_playlist = []
            self.current_index = 0
    
    mock_app = MockApp()
    ai_system = MusicAIRecommendationSystem(mock_app)
    
    # Test des fonctionnalités de base
    test_song = "test_song.mp3"
    ai_system.on_song_start(test_song)
    time.sleep(1)
    ai_system.on_song_end(test_song, was_skipped=False, listening_duration=30)
    ai_system.on_song_liked(test_song)
    
    # Afficher les insights
    insights = ai_system.get_ai_insights()
    print("Insights:", insights)