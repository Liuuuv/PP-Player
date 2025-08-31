from functools import lru_cache
import os
from collections import defaultdict
import math

class LocalSearch:
    def __init__(self, word_list):
        self.init(word_list)
    
    def init(self, word_list):
        self.words = [os.path.splitext(os.path.basename(chemin))[0] for chemin in word_list]
        
        # self.lower_words = [word.lower() for word in self.words]
        # self.word_to_index = {word.lower(): i for i, word in enumerate(self.words)}
        
        # # Cache pour les distances fréquemment calculées
        # self.levenshtein_cache = {}
        
        
        self.n = 3
        self.index = defaultdict(set)
        self.build_index(self.words)
    
    def levenshtein_distance(self, s1, s2):
        """
        Calcule la distance de Levenshtein entre deux chaînes
        (nombre minimum d'opérations pour transformer s1 en s2)
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
        
    
    @lru_cache(maxsize=1000)
    def cached_levenshtein(self, s1, s2):
        """Version avec cache de la distance de Levenshtein"""
        return self.levenshtein_distance(s1, s2)
    
    def search_optimized(self, query, max_results=-1):
        """
        Recherche optimisée avec plusieurs stratégies
        """
        query_lower = query.lower()
        results = []
        
        # print('self.word_to_index ', self.word_to_index)
        
        # Stratégie 1: Correspondance exacte
        if query_lower in self.word_to_index:
            idx = self.word_to_index[query_lower]
            return [(self.words[idx], 1.0)]
        
        # Stratégie 2: Correspondance de préfixe
        for i, word_lower in enumerate(self.lower_words):
            if word_lower.startswith(query_lower) and len(query_lower) >= 2:
                results.append((self.words[i], 0.9))
        
        # Stratégie 3: Distance de Levenshtein
        for i, word_lower in enumerate(self.lower_words):
            if abs(len(query_lower) - len(word_lower)) <= 3:  # Filtre rapide
                distance = self.cached_levenshtein(query_lower, word_lower)
                if distance <= 2:
                    similarity = 1 - (distance / max(len(query_lower), len(word_lower), 1))
                    results.append((self.words[i], similarity))
        
        # Dédupliquer et trier
        seen = set()
        final_results = []
        for word, score in results:
            if word not in seen:
                seen.add(word)
                final_results.append((word, score))

        final_results.sort(key=lambda x: x[1], reverse=True)
        
        final_results = [result+".mp3" for result, score in final_results]
        
        if max_results != -1:
            return final_results[:max_results]
        else:
            return final_results
    
    
    

    def generate_ngrams(self, text, n=3):
        """
        Génère les n-grams d'une chaîne
        """
        if len(text) < n:
            return [text]
        
        ngrams = []
        for i in range(len(text) - n + 1):
            ngrams.append(text[i:i+n])
        
        return ngrams
    
    def build_index(self, words):
        """Construit l'index des n-grams"""
        self.words = words
        for idx, word in enumerate(words):
            word_lower = word.lower()
            ngrams = self.generate_ngrams(word_lower, self.n)
            for ngram in ngrams:
                self.index[ngram].add(idx)
    
    def search(self, query, threshold=0.1):
        """Recherche avec similarité cosinus sur les n-grams"""
        query_lower = query.lower()
        query_ngrams = self.generate_ngrams(query_lower, self.n)
        
        # Vecteur de requête
        query_vector = defaultdict(int)
        for ngram in query_ngrams:
            query_vector[ngram] += 1
        
        # Calcul des scores
        results = []
        word_scores = defaultdict(float)
        
        for ngram in query_ngrams:
            print(ngram, "ngram")
            for word_idx in self.index.get(ngram, set()):
                word = self.words[word_idx]
                word_lower = word.lower()
                word_ngrams = self.generate_ngrams(word_lower, self.n)
                
                # Vecteur du mot
                word_vector = defaultdict(int)
                for w_ngram in word_ngrams:
                    word_vector[w_ngram] += 1
                
                # Similarité cosinus
                dot_product = sum(query_vector[ng] * word_vector[ng] for ng in query_vector)
                query_norm = math.sqrt(sum(val**2 for val in query_vector.values()))
                word_norm = math.sqrt(sum(val**2 for val in word_vector.values()))
                
                # print("dot_product", dot_product)
                # print("query_norm", query_norm)
                # print("word_norm", word_norm)
                if query_norm > 0 and word_norm > 0:
                    similarity = dot_product / (query_norm * word_norm)
                    # print("(word, similarity)", (word, similarity))
                    if similarity > threshold:
                        results.append((word, similarity))
        
        final = sorted(set(results), key=lambda x: x[1], reverse=True)
        final = [word+".mp3" for word, similarity in final]
        return final