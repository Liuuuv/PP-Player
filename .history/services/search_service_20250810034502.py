"""
Service de recherche pour les fichiers locaux
"""
import os
import re
# from fuzzywuzzy import fuzz  # Optionnel, utilisation de difflib à la place
import difflib
from config.constants import AUDIO_EXTENSIONS


class SearchService:
    """Service de recherche pour les fichiers audio locaux"""
    
    def __init__(self):
        self.search_cache = {}
        self.normalized_cache = {}
    
    def search_files(self, files, query, fuzzy_threshold=60):
        """Recherche des fichiers par nom avec support fuzzy"""
        if not query or not files:
            return files
        
        query = query.strip().lower()
        if not query:
            return files
        
        results = []
        
        for filepath in files:
            filename = os.path.basename(filepath)
            score = self._calculate_match_score(filename, query)
            
            if score >= fuzzy_threshold:
                results.append((filepath, score))
        
        # Trier par score décroissant
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [filepath for filepath, score in results]
    
    def _calculate_match_score(self, filename, query):
        """Calcule le score de correspondance entre un nom de fichier et une requête"""
        # Normaliser le nom de fichier
        normalized_filename = self._normalize_text(filename)
        normalized_query = self._normalize_text(query)
        
        # Score exact
        if normalized_query in normalized_filename:
            return 100
        
        # Score fuzzy avec difflib
        fuzzy_score = difflib.SequenceMatcher(None, normalized_query, normalized_filename).ratio() * 100
        
        # Score fuzzy sur les mots individuels
        filename_words = normalized_filename.split()
        query_words = normalized_query.split()
        
        word_scores = []
        for query_word in query_words:
            best_word_score = 0
            for filename_word in filename_words:
                word_score = difflib.SequenceMatcher(None, query_word, filename_word).ratio() * 100
                best_word_score = max(best_word_score, word_score)
            word_scores.append(best_word_score)
        
        # Score moyen des mots
        avg_word_score = sum(word_scores) / len(word_scores) if word_scores else 0
        
        # Score final (combinaison des différents scores)
        final_score = max(fuzzy_score, avg_word_score * 0.8)
        
        return final_score
    
    def _normalize_text(self, text):
        """Normalise un texte pour la recherche"""
        if text in self.normalized_cache:
            return self.normalized_cache[text]
        
        # Supprimer l'extension
        text = os.path.splitext(text)[0]
        
        # Convertir en minuscules
        text = text.lower()
        
        # Supprimer les caractères spéciaux et remplacer par des espaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        self.normalized_cache[text] = text
        return text
    
    def search_by_artist(self, files, artist_query):
        """Recherche des fichiers par artiste"""
        # Cette fonction nécessiterait l'extraction des métadonnées
        # Pour l'instant, on fait une recherche simple dans le nom
        return self.search_files(files, artist_query)
    
    def search_by_album(self, files, album_query):
        """Recherche des fichiers par album"""
        # Cette fonction nécessiterait l'extraction des métadonnées
        # Pour l'instant, on fait une recherche simple dans le nom
        return self.search_files(files, album_query)
    
    def search_by_genre(self, files, genre_query):
        """Recherche des fichiers par genre"""
        # Cette fonction nécessiterait l'extraction des métadonnées
        # Pour l'instant, on fait une recherche simple dans le nom
        return self.search_files(files, genre_query)
    
    def filter_by_duration(self, files, min_duration=None, max_duration=None):
        """Filtre les fichiers par durée"""
        if not min_duration and not max_duration:
            return files
        
        filtered_files = []
        
        for filepath in files:
            try:
                from mutagen import File
                audio_file = File(filepath)
                
                if audio_file and hasattr(audio_file, 'info'):
                    duration = audio_file.info.length
                    
                    if min_duration and duration < min_duration:
                        continue
                    if max_duration and duration > max_duration:
                        continue
                    
                    filtered_files.append(filepath)
                    
            except Exception:
                # Si on ne peut pas lire les métadonnées, on inclut le fichier
                filtered_files.append(filepath)
        
        return filtered_files
    
    def filter_by_file_size(self, files, min_size=None, max_size=None):
        """Filtre les fichiers par taille"""
        if not min_size and not max_size:
            return files
        
        filtered_files = []
        
        for filepath in files:
            try:
                file_size = os.path.getsize(filepath)
                
                if min_size and file_size < min_size:
                    continue
                if max_size and file_size > max_size:
                    continue
                
                filtered_files.append(filepath)
                
            except Exception:
                # Si on ne peut pas lire la taille, on inclut le fichier
                filtered_files.append(filepath)
        
        return filtered_files
    
    def get_search_suggestions(self, files, partial_query, max_suggestions=5):
        """Génère des suggestions de recherche basées sur les fichiers existants"""
        if not partial_query or not files:
            return []
        
        partial_query = partial_query.lower().strip()
        suggestions = set()
        
        for filepath in files:
            filename = os.path.basename(filepath)
            normalized_filename = self._normalize_text(filename)
            
            # Extraire les mots qui commencent par la requête partielle
            words = normalized_filename.split()
            for word in words:
                if word.startswith(partial_query) and len(word) > len(partial_query):
                    suggestions.add(word)
                    if len(suggestions) >= max_suggestions:
                        break
            
            if len(suggestions) >= max_suggestions:
                break
        
        return sorted(list(suggestions))
    
    def clear_cache(self):
        """Vide le cache de recherche"""
        self.search_cache.clear()
        self.normalized_cache.clear()
    
    def get_file_statistics(self, files):
        """Retourne des statistiques sur les fichiers"""
        if not files:
            return {}
        
        stats = {
            'total_files': len(files),
            'total_size': 0,
            'extensions': {},
            'avg_size': 0
        }
        
        for filepath in files:
            try:
                # Taille du fichier
                file_size = os.path.getsize(filepath)
                stats['total_size'] += file_size
                
                # Extension
                ext = os.path.splitext(filepath)[1].lower()
                stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1
                
            except Exception:
                continue
        
        # Taille moyenne
        if stats['total_files'] > 0:
            stats['avg_size'] = stats['total_size'] / stats['total_files']
        
        return stats