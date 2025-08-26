#!/usr/bin/env python3
"""
Optimiseur de mémoire pour le lecteur de musique
Surveille et optimise l'usage mémoire de l'application
"""

import gc
import os
import time
import threading
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil non disponible - monitoring mémoire limité")

class MemoryOptimizer:
    """Optimiseur de mémoire avec nettoyage automatique"""
    
    def __init__(self, app):
        self.app = app
        self.memory_threshold = 500 * 1024 * 1024  # 500MB par défaut
        self.cleanup_timer = None
        self.monitoring_active = False
        self.cleanup_stats = {
            'cleanups_performed': 0,
            'memory_freed_mb': 0,
            'last_cleanup': None
        }
        
        # Configuration des caches
        self.cache_limits = {
            'thumbnail_cache': 50,
            'extended_search_cache': 100,
            'artist_cache': 20,
            'playlist_content_cache': 30,
            'search_cache': 50,
            'normalized_filenames': 200
        }
        
    def start_monitoring(self, check_interval_seconds=30):
        """Démarre la surveillance mémoire"""
        if not PSUTIL_AVAILABLE:
            print("⚠️ Surveillance mémoire désactivée (psutil non disponible)")
            return False
            
        self.monitoring_active = True
        self.check_interval = check_interval_seconds * 1000  # Convertir en ms
        self._schedule_cleanup()
        print(f"🔍 Surveillance mémoire démarrée (seuil: {self.memory_threshold/1024/1024:.0f}MB)")
        return True
    
    def stop_monitoring(self):
        """Arrête la surveillance mémoire"""
        self.monitoring_active = False
        if self.cleanup_timer:
            try:
                self.app.root.after_cancel(self.cleanup_timer)
            except:
                pass
        print("🛑 Surveillance mémoire arrêtée")
    
    def _schedule_cleanup(self):
        """Programme le nettoyage périodique"""
        if not self.monitoring_active:
            return
            
        self._cleanup_if_needed()
        
        # Programmer le prochain nettoyage
        try:
            self.cleanup_timer = self.app.root.after(
                self.check_interval, 
                self._schedule_cleanup
            )
        except:
            # Interface détruite
            self.monitoring_active = False
    
    def _cleanup_if_needed(self):
        """Nettoie la mémoire si nécessaire"""
        if not PSUTIL_AVAILABLE:
            return
            
        try:
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss
            memory_mb = memory_usage / 1024 / 1024
            
            if memory_usage > self.memory_threshold:
                print(f"🧹 Nettoyage mémoire déclenché (usage: {memory_mb:.1f}MB)")
                
                # Effectuer le nettoyage
                freed_mb = self._perform_cleanup()
                
                # Mettre à jour les statistiques
                self.cleanup_stats['cleanups_performed'] += 1
                self.cleanup_stats['memory_freed_mb'] += freed_mb
                self.cleanup_stats['last_cleanup'] = time.time()
                
                print(f"✅ Mémoire libérée: {freed_mb:.1f}MB")
            
        except Exception as e:
            print(f"Erreur nettoyage mémoire: {e}")
    
    def _perform_cleanup(self):
        """Effectue le nettoyage de mémoire"""
        if not PSUTIL_AVAILABLE:
            return 0
            
        try:
            # Mesurer la mémoire avant
            initial_memory = psutil.Process(os.getpid()).memory_info().rss
            
            # Nettoyer les différents caches
            self._cleanup_thumbnail_cache()
            self._cleanup_search_caches()
            self._cleanup_artist_cache()
            self._cleanup_misc_caches()
            
            # Forcer le garbage collection
            collected = gc.collect()
            if collected > 0:
                print(f"🗑️ Garbage collection: {collected} objets supprimés")
            
            # Mesurer la mémoire après
            final_memory = psutil.Process(os.getpid()).memory_info().rss
            freed_mb = (initial_memory - final_memory) / 1024 / 1024
            
            return max(0, freed_mb)  # Ne pas retourner de valeur négative
            
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
            return 0
    
    def _cleanup_thumbnail_cache(self):
        """Nettoie le cache des miniatures"""
        if not hasattr(self.app, 'thumbnail_cache'):
            return
            
        cache = self.app.thumbnail_cache
        limit = self.cache_limits['thumbnail_cache']
        
        if len(cache) > limit:
            # Trier par dernière utilisation (si disponible)
            items = list(cache.items())
            
            # Si pas de timestamp, supprimer les plus anciens
            items_to_remove = len(items) - limit
            for key, _ in items[:items_to_remove]:
                del cache[key]
            
            print(f"🖼️ Cache miniatures: {items_to_remove} éléments supprimés")
    
    def _cleanup_search_caches(self):
        """Nettoie les caches de recherche"""
        caches_to_clean = [
            ('extended_search_cache', 'extended_search_cache'),
            ('search_cache', 'search_cache'),
            ('normalized_filenames', 'normalized_filenames')
        ]
        
        for attr_name, cache_name in caches_to_clean:
            if hasattr(self.app, attr_name):
                cache = getattr(self.app, attr_name)
                limit = self.cache_limits.get(cache_name, 100)
                
                if len(cache) > limit:
                    items_to_remove = len(cache) - limit
                    items = list(cache.items())
                    
                    for key, _ in items[:items_to_remove]:
                        del cache[key]
                    
                    print(f"🔍 Cache {cache_name}: {items_to_remove} éléments supprimés")
    
    def _cleanup_artist_cache(self):
        """Nettoie le cache des artistes"""
        if not hasattr(self.app, 'artist_cache'):
            return
            
        cache = self.app.artist_cache
        limit = self.cache_limits['artist_cache']
        
        if len(cache) > limit:
            items_to_remove = len(cache) - limit
            items = list(cache.items())
            
            for key, _ in items[:items_to_remove]:
                del cache[key]
            
            print(f"👥 Cache artistes: {items_to_remove} éléments supprimés")
    
    def _cleanup_misc_caches(self):
        """Nettoie les autres caches"""
        # Cache des contenus de playlist
        if hasattr(self.app, 'playlist_content_cache'):
            cache = self.app.playlist_content_cache
            limit = self.cache_limits['playlist_content_cache']
            
            if len(cache) > limit:
                items_to_remove = len(cache) - limit
                items = list(cache.items())
                
                for key, _ in items[:items_to_remove]:
                    del cache[key]
                
                print(f"📋 Cache playlists: {items_to_remove} éléments supprimés")
        
        # Nettoyer les callbacks en attente si disponible
        if hasattr(self.app, 'callback_optimizer'):
            pending = self.app.callback_optimizer.get_pending_count()
            if pending > 50:  # Trop de callbacks en attente
                cancelled = self.app.callback_optimizer.cancel_all_callbacks()
                print(f"⏰ Callbacks nettoyés: {cancelled}")
    
    def force_cleanup(self):
        """Force un nettoyage immédiat"""
        print("🧹 Nettoyage forcé de la mémoire...")
        freed_mb = self._perform_cleanup()
        print(f"✅ Nettoyage terminé: {freed_mb:.1f}MB libérés")
        return freed_mb
    
    def get_memory_info(self):
        """Retourne les informations sur l'usage mémoire"""
        info = {
            'psutil_available': PSUTIL_AVAILABLE,
            'monitoring_active': self.monitoring_active,
            'threshold_mb': self.memory_threshold / 1024 / 1024,
            'cleanup_stats': self.cleanup_stats.copy()
        }
        
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()
                info.update({
                    'current_usage_mb': memory_info.rss / 1024 / 1024,
                    'virtual_memory_mb': memory_info.vms / 1024 / 1024,
                    'cpu_percent': process.cpu_percent()
                })
            except:
                pass
        
        # Informations sur les caches
        cache_info = {}
        for attr_name, limit in self.cache_limits.items():
            if hasattr(self.app, attr_name):
                cache = getattr(self.app, attr_name)
                cache_info[attr_name] = {
                    'size': len(cache) if hasattr(cache, '__len__') else 0,
                    'limit': limit
                }
        
        info['caches'] = cache_info
        return info
    
    def set_memory_threshold(self, threshold_mb):
        """Définit le seuil de mémoire en MB"""
        self.memory_threshold = threshold_mb * 1024 * 1024
        print(f"🎛️ Seuil mémoire mis à jour: {threshold_mb}MB")
    
    def set_cache_limit(self, cache_name, limit):
        """Définit la limite d'un cache spécifique"""
        if cache_name in self.cache_limits:
            self.cache_limits[cache_name] = limit
            print(f"📊 Limite cache {cache_name}: {limit}")
        else:
            print(f"❌ Cache inconnu: {cache_name}")
    
    def get_performance_report(self):
        """Génère un rapport de performance mémoire"""
        info = self.get_memory_info()
        
        report = ["📊 RAPPORT MÉMOIRE", "=" * 50]
        
        if info['psutil_available']:
            report.append(f"💾 Usage actuel: {info.get('current_usage_mb', 0):.1f}MB")
            report.append(f"🎯 Seuil configuré: {info['threshold_mb']:.0f}MB")
            report.append(f"🖥️ CPU: {info.get('cpu_percent', 0):.1f}%")
        else:
            report.append("⚠️ Monitoring détaillé non disponible")
        
        report.append(f"🧹 Nettoyages effectués: {info['cleanup_stats']['cleanups_performed']}")
        report.append(f"💾 Mémoire totale libérée: {info['cleanup_stats']['memory_freed_mb']:.1f}MB")
        
        if info['cleanup_stats']['last_cleanup']:
            last_cleanup = time.time() - info['cleanup_stats']['last_cleanup']
            report.append(f"⏰ Dernier nettoyage: il y a {last_cleanup/60:.1f} minutes")
        
        report.append("\n📋 ÉTAT DES CACHES:")
        for cache_name, cache_info in info['caches'].items():
            size = cache_info['size']
            limit = cache_info['limit']
            percentage = (size / limit * 100) if limit > 0 else 0
            status = "🔴" if percentage > 90 else "🟡" if percentage > 70 else "🟢"
            report.append(f"  {status} {cache_name}: {size}/{limit} ({percentage:.0f}%)")
        
        return "\n".join(report)


def apply_memory_optimizations(app, threshold_mb=500, check_interval=30):
    """Applique les optimisations mémoire à l'application"""
    print("🔧 Application des optimisations mémoire...")
    
    # Créer l'optimiseur de mémoire
    app.memory_optimizer = MemoryOptimizer(app)
    app.memory_optimizer.set_memory_threshold(threshold_mb)
    
    # Démarrer la surveillance
    success = app.memory_optimizer.start_monitoring(check_interval)
    
    if success:
        print("✅ Optimisations mémoire appliquées")
    else:
        print("⚠️ Optimisations mémoire partiellement appliquées")
    
    return app.memory_optimizer


if __name__ == "__main__":
    print("🧪 Test des optimisations mémoire")
    print("Ce module doit être importé dans main.py")
    print("Usage: from memory_optimizer import apply_memory_optimizations")
    print("       apply_memory_optimizations(self, threshold_mb=500)")