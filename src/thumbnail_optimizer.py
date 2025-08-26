#!/usr/bin/env python3
"""
Optimiseur de miniatures pour le lecteur de musique
Chargement asynchrone et cache intelligent des miniatures
"""

import threading
import queue
import time
import os
from PIL import Image, ImageTk
import tkinter as tk

class ThumbnailOptimizer:
    """Optimiseur pour le chargement asynchrone des miniatures"""
    
    def __init__(self, app, max_cache_size=100, max_workers=2):
        self.app = app
        self.max_cache_size = max_cache_size
        self.max_workers = max_workers
        
        # Cache avec métadonnées
        self.cache = {}  # {cache_key: {'image': ImageTk, 'last_used': timestamp, 'size': bytes}}
        self.cache_size_bytes = 0
        self.max_cache_size_bytes = 50 * 1024 * 1024  # 50MB max
        
        # Queue de chargement
        self.load_queue = queue.Queue()
        self.priority_queue = queue.PriorityQueue()  # Pour les miniatures prioritaires
        
        # Workers
        self.workers = []
        self.running = True
        
        # Statistiques
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'loads_completed': 0,
            'loads_failed': 0,
            'total_load_time': 0
        }
        
        self._start_workers()
    
    def _start_workers(self):
        """Démarre les threads workers"""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop, 
                name=f"ThumbnailWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        print(f"🖼️ {self.max_workers} workers de miniatures démarrés")
    
    def _worker_loop(self):
        """Boucle principale du worker"""
        while self.running:
            try:
                # Vérifier d'abord la queue prioritaire
                try:
                    priority, task = self.priority_queue.get(timeout=0.1)
                    self._process_task(task)
                    self.priority_queue.task_done()
                    continue
                except queue.Empty:
                    pass
                
                # Puis la queue normale
                try:
                    task = self.load_queue.get(timeout=0.5)
                    self._process_task(task)
                    self.load_queue.task_done()
                except queue.Empty:
                    continue
                    
            except Exception as e:
                print(f"Erreur worker miniature: {e}")
    
    def _process_task(self, task):
        """Traite une tâche de chargement"""
        filepath, callback, size, options = task
        start_time = time.time()
        
        try:
            # Charger la miniature
            thumbnail = self._load_thumbnail_sync(filepath, size, options)
            
            # Mettre à jour les statistiques
            load_time = time.time() - start_time
            self.stats['total_load_time'] += load_time
            
            if thumbnail:
                self.stats['loads_completed'] += 1
                
                # Callback dans le thread principal
                if callback:
                    self.app.root.after(0, lambda: callback(filepath, thumbnail))
            else:
                self.stats['loads_failed'] += 1
                
        except Exception as e:
            print(f"Erreur chargement miniature {filepath}: {e}")
            self.stats['loads_failed'] += 1
    
    def load_thumbnail_async(self, filepath, callback, size=(50, 50), priority=False, **options):
        """Charge une miniature de façon asynchrone"""
        if not os.path.exists(filepath):
            return False
        
        cache_key = self._get_cache_key(filepath, size, options)
        
        # Vérifier le cache d'abord
        if cache_key in self.cache:
            self.stats['cache_hits'] += 1
            self.cache[cache_key]['last_used'] = time.time()
            
            if callback:
                callback(filepath, self.cache[cache_key]['image'])
            return True
        
        self.stats['cache_misses'] += 1
        
        # Ajouter à la queue appropriée
        task = (filepath, callback, size, options)
        
        if priority:
            # Priorité basée sur le timestamp (plus récent = plus prioritaire)
            priority_value = -time.time()  # Négatif pour ordre décroissant
            self.priority_queue.put((priority_value, task))
        else:
            self.load_queue.put(task)
        
        return True
    
    def _load_thumbnail_sync(self, filepath, size, options):
        """Charge une miniature de façon synchrone"""
        try:
            cache_key = self._get_cache_key(filepath, size, options)
            
            # Différents types de miniatures selon l'extension
            if filepath.lower().endswith(('.mp3', '.wav', '.flac', '.m4a')):
                thumbnail = self._load_audio_thumbnail(filepath, size, options)
            elif filepath.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                thumbnail = self._load_image_thumbnail(filepath, size, options)
            else:
                thumbnail = self._load_default_thumbnail(size, options)
            
            if thumbnail:
                # Ajouter au cache
                self._add_to_cache(cache_key, thumbnail)
                return thumbnail
            
            return None
            
        except Exception as e:
            print(f"Erreur chargement miniature {filepath}: {e}")
            return None
    
    def _load_audio_thumbnail(self, filepath, size, options):
        """Charge la miniature d'un fichier audio"""
        try:
            # Essayer d'extraire la pochette de l'audio
            from mutagen import File
            from mutagen.id3 import ID3NoHeaderError
            
            audio_file = File(filepath)
            if audio_file and hasattr(audio_file, 'tags') and audio_file.tags:
                # Chercher les images dans les tags
                for key in audio_file.tags:
                    if hasattr(audio_file.tags[key], 'data'):
                        image_data = audio_file.tags[key].data
                        if image_data:
                            return self._create_thumbnail_from_data(image_data, size, options)
            
            # Si pas de pochette, utiliser une miniature par défaut
            return self._load_default_thumbnail(size, options, audio=True)
            
        except Exception as e:
            # En cas d'erreur, utiliser la miniature par défaut
            return self._load_default_thumbnail(size, options, audio=True)
    
    def _load_image_thumbnail(self, filepath, size, options):
        """Charge la miniature d'un fichier image"""
        try:
            with Image.open(filepath) as img:
                # Redimensionner en gardant les proportions
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Appliquer les options (rotation, filtres, etc.)
                if options.get('rotate'):
                    img = img.rotate(options['rotate'])
                
                # Convertir pour Tkinter
                return ImageTk.PhotoImage(img)
                
        except Exception as e:
            print(f"Erreur chargement image {filepath}: {e}")
            return self._load_default_thumbnail(size, options)
    
    def _create_thumbnail_from_data(self, image_data, size, options):
        """Crée une miniature à partir de données binaires"""
        try:
            from io import BytesIO
            
            img = Image.open(BytesIO(image_data))
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Appliquer les options
            if options.get('rotate'):
                img = img.rotate(options['rotate'])
            
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            print(f"Erreur création miniature depuis données: {e}")
            return self._load_default_thumbnail(size, options)
    
    def _load_default_thumbnail(self, size, options, audio=False):
        """Charge une miniature par défaut"""
        try:
            # Créer une image par défaut simple
            img = Image.new('RGB', size, color='#4a4a4a')
            
            # Ajouter un indicateur selon le type
            if audio:
                # Dessiner une note de musique simple (ou utiliser une icône)
                pass  # Pour l'instant, juste la couleur
            
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            print(f"Erreur création miniature par défaut: {e}")
            return None
    
    def _get_cache_key(self, filepath, size, options):
        """Génère une clé de cache unique"""
        # Inclure la taille du fichier et la date de modification pour détecter les changements
        try:
            stat = os.stat(filepath)
            file_info = f"{stat.st_size}_{stat.st_mtime}"
        except:
            file_info = "unknown"
        
        options_str = "_".join(f"{k}={v}" for k, v in sorted(options.items()))
        return f"{filepath}_{size}_{file_info}_{options_str}"
    
    def _add_to_cache(self, cache_key, thumbnail):
        """Ajoute une miniature au cache"""
        # Estimer la taille de l'image
        estimated_size = 1024  # Estimation basique
        
        # Vérifier si on dépasse la limite
        while (self.cache_size_bytes + estimated_size > self.max_cache_size_bytes or 
               len(self.cache) >= self.max_cache_size):
            self._remove_oldest_from_cache()
        
        # Ajouter au cache
        self.cache[cache_key] = {
            'image': thumbnail,
            'last_used': time.time(),
            'size': estimated_size
        }
        self.cache_size_bytes += estimated_size
    
    def _remove_oldest_from_cache(self):
        """Supprime l'élément le plus ancien du cache"""
        if not self.cache:
            return
        
        # Trouver l'élément le moins récemment utilisé
        oldest_key = min(self.cache.keys(), 
                        key=lambda k: self.cache[k]['last_used'])
        
        # Supprimer du cache
        removed_item = self.cache.pop(oldest_key)
        self.cache_size_bytes -= removed_item['size']
    
    def preload_thumbnails(self, filepaths, size=(50, 50), **options):
        """Précharge plusieurs miniatures"""
        for filepath in filepaths:
            self.load_thumbnail_async(filepath, None, size, priority=False, **options)
    
    def clear_cache(self):
        """Vide le cache des miniatures"""
        cleared_count = len(self.cache)
        self.cache.clear()
        self.cache_size_bytes = 0
        print(f"🧹 Cache miniatures vidé: {cleared_count} éléments supprimés")
        return cleared_count
    
    def get_cache_info(self):
        """Retourne les informations sur le cache"""
        return {
            'size': len(self.cache),
            'max_size': self.max_cache_size,
            'size_bytes': self.cache_size_bytes,
            'max_size_bytes': self.max_cache_size_bytes,
            'hit_rate': (self.stats['cache_hits'] / 
                        max(1, self.stats['cache_hits'] + self.stats['cache_misses']) * 100),
            'stats': self.stats.copy()
        }
    
    def get_performance_report(self):
        """Génère un rapport de performance"""
        info = self.get_cache_info()
        
        report = [
            "🖼️ RAPPORT MINIATURES",
            "=" * 50,
            f"📊 Cache: {info['size']}/{info['max_size']} éléments",
            f"💾 Mémoire: {info['size_bytes']/1024/1024:.1f}/{info['max_size_bytes']/1024/1024:.1f}MB",
            f"🎯 Taux de réussite cache: {info['hit_rate']:.1f}%",
            f"✅ Chargements réussis: {info['stats']['loads_completed']}",
            f"❌ Chargements échoués: {info['stats']['loads_failed']}",
        ]
        
        if info['stats']['loads_completed'] > 0:
            avg_time = info['stats']['total_load_time'] / info['stats']['loads_completed']
            report.append(f"⏱️ Temps moyen de chargement: {avg_time*1000:.1f}ms")
        
        return "\n".join(report)
    
    def shutdown(self):
        """Arrête l'optimiseur de miniatures"""
        print("🛑 Arrêt de l'optimiseur de miniatures...")
        self.running = False
        
        # Attendre que les workers se terminent
        for worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=1)
        
        # Vider les queues
        while not self.load_queue.empty():
            try:
                self.load_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.priority_queue.empty():
            try:
                self.priority_queue.get_nowait()
            except queue.Empty:
                break
        
        print("✅ Optimiseur de miniatures arrêté")


def apply_thumbnail_optimizations(app, max_cache_size=100, max_workers=2):
    """Applique les optimisations de miniatures à l'application"""
    print("🔧 Application des optimisations de miniatures...")
    
    # Créer l'optimiseur de miniatures
    app.thumbnail_optimizer = ThumbnailOptimizer(app, max_cache_size, max_workers)
    
    # Remplacer les méthodes de chargement existantes si nécessaire
    # (cela dépend de l'implémentation actuelle)
    
    print("✅ Optimisations de miniatures appliquées")
    return app.thumbnail_optimizer


if __name__ == "__main__":
    print("🧪 Test des optimisations de miniatures")
    print("Ce module doit être importé dans main.py")
    print("Usage: from thumbnail_optimizer import apply_thumbnail_optimizations")
    print("       apply_thumbnail_optimizations(self)")