"""
Gestionnaire indépendant pour les téléchargements
"""

import os
import json
from pathlib import Path
from . import (
    get_library_config, ThreadSafeCache, 
    get_audio_files_in_directory, create_directory_if_not_exists,
    get_file_duration, format_duration, safe_file_operation
)

class DownloadsManager:
    """Gestionnaire indépendant pour les téléchargements"""
    
    def __init__(self, downloads_folder=None):
        # Dossier de téléchargements
        if downloads_folder is None:
            # Utiliser un dossier par défaut dans le répertoire utilisateur
            downloads_folder = os.path.join(os.path.expanduser("~"), "Music", "MusicPlayer_Downloads")
        
        self.downloads_folder = downloads_folder
        create_directory_if_not_exists(self.downloads_folder)
        
        # Caches pour les métadonnées
        self.duration_cache = ThreadSafeCache()
        self.thumbnail_cache = ThreadSafeCache()
        self.normalized_filenames = ThreadSafeCache()
        
        # Fichiers de cache
        self.cache_dir = os.path.join(self.downloads_folder, ".cache")
        create_directory_if_not_exists(self.cache_dir)
        
        self.duration_cache_file = os.path.join(self.cache_dir, "durations.json")
        self.thumbnail_cache_file = os.path.join(self.cache_dir, "thumbnails.json")
        
        # Charger les caches
        self._load_caches()
    
    def _load_caches(self):
        """Charge les caches depuis les fichiers"""
        # Cache des durées
        if os.path.exists(self.duration_cache_file):
            try:
                with open(self.duration_cache_file, 'r', encoding='utf-8') as f:
                    duration_data = json.load(f)
                    for filepath, duration in duration_data.items():
                        self.duration_cache.set(filepath, duration)
            except Exception as e:
                print(f"Erreur lors du chargement du cache des durées: {e}")
        
        # Cache des miniatures
        if os.path.exists(self.thumbnail_cache_file):
            try:
                with open(self.thumbnail_cache_file, 'r', encoding='utf-8') as f:
                    thumbnail_data = json.load(f)
                    for filepath, thumbnail_path in thumbnail_data.items():
                        if os.path.exists(thumbnail_path):
                            self.thumbnail_cache.set(filepath, thumbnail_path)
            except Exception as e:
                print(f"Erreur lors du chargement du cache des miniatures: {e}")
    
    def _save_caches(self):
        """Sauvegarde les caches dans les fichiers"""
        try:
            # Sauvegarder le cache des durées
            duration_data = {}
            for filepath in self.duration_cache.keys():
                duration = self.duration_cache.get(filepath)
                if duration is not None:
                    duration_data[filepath] = duration
            
            with open(self.duration_cache_file, 'w', encoding='utf-8') as f:
                json.dump(duration_data, f, indent=2)
            
            # Sauvegarder le cache des miniatures
            thumbnail_data = {}
            for filepath in self.thumbnail_cache.keys():
                thumbnail_path = self.thumbnail_cache.get(filepath)
                if thumbnail_path and os.path.exists(thumbnail_path):
                    thumbnail_data[filepath] = thumbnail_path
            
            with open(self.thumbnail_cache_file, 'w', encoding='utf-8') as f:
                json.dump(thumbnail_data, f, indent=2)
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des caches: {e}")
    
    def get_all_files(self):
        """Récupère tous les fichiers audio téléchargés"""
        files = get_audio_files_in_directory(self.downloads_folder)
        
        # Mettre à jour le cache des noms normalisés
        for filepath in files:
            normalized = os.path.basename(filepath).lower()
            self.normalized_filenames.set(filepath, normalized)
        
        return files
    
    def get_file_duration(self, filepath):
        """Récupère la durée d'un fichier (avec cache)"""
        # Vérifier le cache d'abord
        cached_duration = self.duration_cache.get(filepath)
        if cached_duration is not None:
            return cached_duration
        
        # Calculer la durée
        duration = get_file_duration(filepath)
        
        # Mettre en cache
        if duration is not None:
            self.duration_cache.set(filepath, duration)
        
        return duration
    
    def get_formatted_duration(self, filepath):
        """Récupère la durée formatée d'un fichier"""
        duration = self.get_file_duration(filepath)
        return format_duration(duration)
    
    def search_files(self, query):
        """Recherche des fichiers par nom"""
        if not query:
            return self.get_all_files()
        
        query_lower = query.lower()
        all_files = self.get_all_files()
        
        matching_files = []
        for filepath in all_files:
            normalized_name = self.normalized_filenames.get(filepath, "")
            if query_lower in normalized_name:
                matching_files.append(filepath)
        
        return matching_files
    
    def get_file_info(self, filepath):
        """Récupère les informations complètes d'un fichier"""
        if not os.path.exists(filepath):
            return None
        
        try:
            stat = os.stat(filepath)
            return {
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'duration': self.get_file_duration(filepath),
                'formatted_duration': self.get_formatted_duration(filepath),
                'exists': True
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des infos de {filepath}: {e}")
            return None
    
    def cleanup_cache(self):
        """Nettoie le cache des fichiers qui n'existent plus"""
        all_files = set(self.get_all_files())
        
        # Nettoyer le cache des durées
        for filepath in list(self.duration_cache.keys()):
            if filepath not in all_files:
                self.duration_cache.set(filepath, None)  # Supprimer de facto
        
        # Nettoyer le cache des miniatures
        for filepath in list(self.thumbnail_cache.keys()):
            if filepath not in all_files:
                self.thumbnail_cache.set(filepath, None)  # Supprimer de facto
        
        # Nettoyer le cache des noms normalisés
        for filepath in list(self.normalized_filenames.keys()):
            if filepath not in all_files:
                self.normalized_filenames.set(filepath, None)  # Supprimer de facto
    
    def save_and_cleanup(self):
        """Nettoie et sauvegarde les caches"""
        self.cleanup_cache()
        self._save_caches()
    
    def get_stats(self):
        """Récupère des statistiques sur les téléchargements"""
        all_files = self.get_all_files()
        total_size = 0
        total_duration = 0
        
        for filepath in all_files:
            try:
                stat = os.stat(filepath)
                total_size += stat.st_size
                
                duration = self.get_file_duration(filepath)
                if duration:
                    total_duration += duration
            except:
                continue
        
        return {
            'total_files': len(all_files),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'total_duration_seconds': total_duration,
            'total_duration_formatted': format_duration(total_duration),
            'cache_entries': {
                'durations': len(self.duration_cache.keys()),
                'thumbnails': len(self.thumbnail_cache.keys()),
                'normalized_names': len(self.normalized_filenames.keys())
            }
        }