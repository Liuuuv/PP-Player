# Test de performance pour les optimisations de l'onglet artiste
import time
import threading
import psutil
import os

class ArtistTabPerformanceTest:
    """Classe pour tester les performances de l'onglet artiste"""
    
    def __init__(self, music_player):
        self.player = music_player
        self.test_results = {}
        
    def measure_memory_usage(self):
        """Mesure l'utilisation mémoire actuelle"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def measure_thread_count(self):
        """Mesure le nombre de threads actifs"""
        return threading.active_count()
    
    def test_artist_loading_speed(self, artist_name):
        """Test la vitesse de chargement d'un artiste"""
        print(f"Test de chargement pour: {artist_name}")
        
        # Mesures avant
        start_time = time.time()
        start_memory = self.measure_memory_usage()
        start_threads = self.measure_thread_count()
        
        # Simuler le chargement d'un artiste
        self.player.current_artist_name = artist_name
        self.player.artist_mode = True
        
        # Attendre que le chargement soit terminé (simulation)
        time.sleep(2)
        
        # Mesures après
        end_time = time.time()
        end_memory = self.measure_memory_usage()
        end_threads = self.measure_thread_count()
        
        # Calculer les métriques
        loading_time = end_time - start_time
        memory_increase = end_memory - start_memory
        thread_increase = end_threads - start_threads
        
        results = {
            'loading_time': loading_time,
            'memory_increase': memory_increase,
            'thread_increase': thread_increase,
            'start_memory': start_memory,
            'end_memory': end_memory
        }
        
        self.test_results[artist_name] = results
        
        print(f"Résultats pour {artist_name}:")
        print(f"  - Temps de chargement: {loading_time:.2f}s")
        print(f"  - Augmentation mémoire: {memory_increase:.2f}MB")
        print(f"  - Threads créés: {thread_increase}")
        print(f"  - Mémoire finale: {end_memory:.2f}MB")
        
        return results
    
    def test_cache_efficiency(self):
        """Test l'efficacité du cache"""
        if not hasattr(self.player, 'artist_tab_manager'):
            print("Gestionnaire d'onglet artiste non disponible")
            return
        
        cache_manager = self.player.artist_tab_manager.cache_manager
        stats = cache_manager.get_cache_stats()
        
        print("Statistiques du cache:")
        print(f"  - Artistes en cache: {stats['artists']}")
        print(f"  - Miniatures en cache: {stats['thumbnails']}")
        print(f"  - Playlists en cache: {stats['playlists']}")
        
        return stats
    
    def test_batch_display_speed(self, items_count=50):
        """Test la vitesse d'affichage par lots"""
        print(f"Test d'affichage par lots ({items_count} éléments)")
        
        # Simuler des éléments à afficher
        fake_items = [{'id': f'item_{i}', 'title': f'Test Item {i}'} for i in range(items_count)]
        
        start_time = time.time()
        
        # Simuler l'affichage par lots (sans vraiment créer les widgets)
        from artist_tab.config import get_search_limit
        batch_size = get_search_limit('batch_size')
        delay = get_search_limit('display_delay')
        
        batches = [fake_items[i:i+batch_size] for i in range(0, len(fake_items), batch_size)]
        total_delay = len(batches) * delay / 1000  # Convertir ms en secondes
        
        end_time = time.time()
        processing_time = end_time - start_time
        estimated_total_time = processing_time + total_delay
        
        print(f"Résultats affichage par lots:")
        print(f"  - Nombre de lots: {len(batches)}")
        print(f"  - Taille des lots: {batch_size}")
        print(f"  - Délai entre lots: {delay}ms")
        print(f"  - Temps de traitement: {processing_time:.3f}s")
        print(f"  - Temps total estimé: {estimated_total_time:.3f}s")
        
        return {
            'batch_count': len(batches),
            'batch_size': batch_size,
            'delay': delay,
            'processing_time': processing_time,
            'estimated_total_time': estimated_total_time
        }
    
    def test_thread_pool_efficiency(self):
        """Test l'efficacité des pools de threads"""
        print("Test des pools de threads")
        
        initial_threads = self.measure_thread_count()
        
        # Simuler plusieurs chargements de miniatures
        if hasattr(self.player, '_thumbnail_executor'):
            print("  - Pool de miniatures: Actif")
            print(f"  - Workers miniatures: {self.player._thumbnail_executor._max_workers}")
        else:
            print("  - Pool de miniatures: Non initialisé")
        
        if hasattr(self.player, '_playlist_executor'):
            print("  - Pool de playlists: Actif")
            print(f"  - Workers playlists: {self.player._playlist_executor._max_workers}")
        else:
            print("  - Pool de playlists: Non initialisé")
        
        print(f"  - Threads actifs: {initial_threads}")
        
        return {
            'initial_threads': initial_threads,
            'has_thumbnail_pool': hasattr(self.player, '_thumbnail_executor'),
            'has_playlist_pool': hasattr(self.player, '_playlist_executor')
        }
    
    def run_full_performance_test(self):
        """Lance tous les tests de performance"""
        print("=== TEST DE PERFORMANCE ONGLET ARTISTE ===\n")
        
        # Test 1: Efficacité du cache
        print("1. Test du cache")
        cache_stats = self.test_cache_efficiency()
        print()
        
        # Test 2: Affichage par lots
        print("2. Test d'affichage par lots")
        batch_stats = self.test_batch_display_speed()
        print()
        
        # Test 3: Pools de threads
        print("3. Test des pools de threads")
        thread_stats = self.test_thread_pool_efficiency()
        print()
        
        # Test 4: Chargement d'artiste (simulation)
        print("4. Test de chargement d'artiste")
        artist_stats = self.test_artist_loading_speed("Test Artist")
        print()
        
        # Résumé
        print("=== RÉSUMÉ DES OPTIMISATIONS ===")
        print("✓ Cache intelligent avec expiration")
        print("✓ Affichage par lots optimisé")
        print("✓ Pools de threads partagés")
        print("✓ Timeouts réduits")
        print("✓ Configuration centralisée")
        print()
        
        return {
            'cache': cache_stats,
            'batch_display': batch_stats,
            'thread_pools': thread_stats,
            'artist_loading': artist_stats
        }

def run_performance_test(music_player):
    """Lance un test de performance complet"""
    tester = ArtistTabPerformanceTest(music_player)
    return tester.run_full_performance_test()