#!/usr/bin/env python3
"""
Script de test des améliorations de performance
Mesure l'impact des optimisations sur le lecteur de musique
"""

import time
import threading
import os
import sys
import gc

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil non disponible - tests de performance limités")

class PerformanceTester:
    """Testeur de performance pour les optimisations"""
    
    def __init__(self):
        self.results = {}
        self.baseline_metrics = {}
        
    def measure_baseline(self, app):
        """Mesure les performances de base avant optimisations"""
        print("📊 Mesure des performances de base...")
        
        metrics = {}
        
        # Mesurer l'usage mémoire
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            metrics['memory_mb'] = process.memory_info().rss / 1024 / 1024
            metrics['cpu_percent'] = process.cpu_percent(interval=1)
        
        # Mesurer le temps de réponse UI
        metrics['ui_response_time'] = self._measure_ui_response_time(app)
        
        # Mesurer le temps de chargement d'une liste
        metrics['list_load_time'] = self._measure_list_load_time(app)
        
        # Compter les objets Python
        metrics['python_objects'] = len(gc.get_objects())
        
        self.baseline_metrics = metrics
        print(f"✅ Baseline établi: {metrics}")
        return metrics
    
    def measure_optimized(self, app):
        """Mesure les performances après optimisations"""
        print("📊 Mesure des performances optimisées...")
        
        metrics = {}
        
        # Laisser le temps aux optimisations de s'initialiser
        time.sleep(2)
        
        # Mesurer l'usage mémoire
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            metrics['memory_mb'] = process.memory_info().rss / 1024 / 1024
            metrics['cpu_percent'] = process.cpu_percent(interval=1)
        
        # Mesurer le temps de réponse UI
        metrics['ui_response_time'] = self._measure_ui_response_time(app)
        
        # Mesurer le temps de chargement d'une liste
        metrics['list_load_time'] = self._measure_list_load_time(app)
        
        # Compter les objets Python
        metrics['python_objects'] = len(gc.get_objects())
        
        self.results = metrics
        print(f"✅ Mesures optimisées: {metrics}")
        return metrics
    
    def _measure_ui_response_time(self, app):
        """Mesure le temps de réponse de l'interface"""
        try:
            start_time = time.time()
            
            # Simuler des actions UI
            for _ in range(10):
                app.root.update_idletasks()
                time.sleep(0.01)
            
            end_time = time.time()
            return (end_time - start_time) * 1000  # en millisecondes
            
        except Exception as e:
            print(f"Erreur mesure UI: {e}")
            return 0
    
    def _measure_list_load_time(self, app):
        """Mesure le temps de chargement d'une liste"""
        try:
            # Simuler le chargement d'une liste de fichiers
            start_time = time.time()
            
            # Si l'app a une méthode de rechargement, l'utiliser
            if hasattr(app, '_count_downloaded_files'):
                app._count_downloaded_files()
            
            end_time = time.time()
            return (end_time - start_time) * 1000  # en millisecondes
            
        except Exception as e:
            print(f"Erreur mesure chargement: {e}")
            return 0
    
    def generate_comparison_report(self):
        """Génère un rapport de comparaison"""
        if not self.baseline_metrics or not self.results:
            return "❌ Données insuffisantes pour la comparaison"
        
        report = ["📊 RAPPORT DE COMPARAISON DES PERFORMANCES", "=" * 60]
        
        # Comparaison mémoire
        if 'memory_mb' in self.baseline_metrics and 'memory_mb' in self.results:
            baseline_mem = self.baseline_metrics['memory_mb']
            optimized_mem = self.results['memory_mb']
            mem_diff = baseline_mem - optimized_mem
            mem_percent = (mem_diff / baseline_mem * 100) if baseline_mem > 0 else 0
            
            report.append(f"💾 MÉMOIRE:")
            report.append(f"  Avant: {baseline_mem:.1f}MB")
            report.append(f"  Après: {optimized_mem:.1f}MB")
            report.append(f"  Gain: {mem_diff:.1f}MB ({mem_percent:+.1f}%)")
        
        # Comparaison CPU
        if 'cpu_percent' in self.baseline_metrics and 'cpu_percent' in self.results:
            baseline_cpu = self.baseline_metrics['cpu_percent']
            optimized_cpu = self.results['cpu_percent']
            cpu_diff = baseline_cpu - optimized_cpu
            cpu_percent = (cpu_diff / baseline_cpu * 100) if baseline_cpu > 0 else 0
            
            report.append(f"🖥️ CPU:")
            report.append(f"  Avant: {baseline_cpu:.1f}%")
            report.append(f"  Après: {optimized_cpu:.1f}%")
            report.append(f"  Gain: {cpu_diff:.1f}% ({cpu_percent:+.1f}%)")
        
        # Comparaison temps de réponse UI
        if 'ui_response_time' in self.baseline_metrics and 'ui_response_time' in self.results:
            baseline_ui = self.baseline_metrics['ui_response_time']
            optimized_ui = self.results['ui_response_time']
            ui_diff = baseline_ui - optimized_ui
            ui_percent = (ui_diff / baseline_ui * 100) if baseline_ui > 0 else 0
            
            report.append(f"⚡ RÉACTIVITÉ UI:")
            report.append(f"  Avant: {baseline_ui:.1f}ms")
            report.append(f"  Après: {optimized_ui:.1f}ms")
            report.append(f"  Gain: {ui_diff:.1f}ms ({ui_percent:+.1f}%)")
        
        # Comparaison temps de chargement
        if 'list_load_time' in self.baseline_metrics and 'list_load_time' in self.results:
            baseline_load = self.baseline_metrics['list_load_time']
            optimized_load = self.results['list_load_time']
            load_diff = baseline_load - optimized_load
            load_percent = (load_diff / baseline_load * 100) if baseline_load > 0 else 0
            
            report.append(f"📂 CHARGEMENT:")
            report.append(f"  Avant: {baseline_load:.1f}ms")
            report.append(f"  Après: {optimized_load:.1f}ms")
            report.append(f"  Gain: {load_diff:.1f}ms ({load_percent:+.1f}%)")
        
        # Comparaison objets Python
        if 'python_objects' in self.baseline_metrics and 'python_objects' in self.results:
            baseline_obj = self.baseline_metrics['python_objects']
            optimized_obj = self.results['python_objects']
            obj_diff = baseline_obj - optimized_obj
            obj_percent = (obj_diff / baseline_obj * 100) if baseline_obj > 0 else 0
            
            report.append(f"🐍 OBJETS PYTHON:")
            report.append(f"  Avant: {baseline_obj:,}")
            report.append(f"  Après: {optimized_obj:,}")
            report.append(f"  Différence: {obj_diff:,} ({obj_percent:+.1f}%)")
        
        # Résumé global
        report.append("\n🎯 RÉSUMÉ:")
        improvements = []
        
        if 'memory_mb' in self.baseline_metrics and 'memory_mb' in self.results:
            mem_improvement = (self.baseline_metrics['memory_mb'] - self.results['memory_mb']) / self.baseline_metrics['memory_mb'] * 100
            if mem_improvement > 0:
                improvements.append(f"Mémoire: -{mem_improvement:.1f}%")
        
        if 'cpu_percent' in self.baseline_metrics and 'cpu_percent' in self.results:
            cpu_improvement = (self.baseline_metrics['cpu_percent'] - self.results['cpu_percent']) / self.baseline_metrics['cpu_percent'] * 100
            if cpu_improvement > 0:
                improvements.append(f"CPU: -{cpu_improvement:.1f}%")
        
        if 'ui_response_time' in self.baseline_metrics and 'ui_response_time' in self.results:
            ui_improvement = (self.baseline_metrics['ui_response_time'] - self.results['ui_response_time']) / self.baseline_metrics['ui_response_time'] * 100
            if ui_improvement > 0:
                improvements.append(f"Réactivité: +{ui_improvement:.1f}%")
        
        if improvements:
            report.append("✅ Améliorations détectées:")
            for improvement in improvements:
                report.append(f"  • {improvement}")
        else:
            report.append("⚠️ Aucune amélioration significative détectée")
        
        return "\n".join(report)

def stress_test_thread_optimization():
    """Test de stress pour l'optimisation de thread"""
    print("🧪 Test de stress - Optimisation de thread")
    
    try:
        from thread_optimizer import ThreadOptimizer
        
        # Simuler une app basique
        class MockApp:
            def __init__(self):
                self.paused = False
                self.user_dragging = False
                self.current_time = 0
                self.base_position = 0
                self.song_length = 180
                self.update_suspended = False
                self._app_destroyed = False
                
                # Mock des composants UI
                self.progress = type('MockProgress', (), {'config': lambda **kwargs: None})()
                self.current_time_label = type('MockLabel', (), {'config': lambda **kwargs: None})()
                self.show_waveform_current = False
        
        # Simuler pygame
        import types
        pygame_mock = types.ModuleType('pygame')
        pygame_mock.mixer = types.ModuleType('mixer')
        pygame_mock.mixer.get_init = lambda: True
        pygame_mock.mixer.music = types.ModuleType('music')
        pygame_mock.mixer.music.get_busy = lambda: True
        pygame_mock.mixer.music.get_pos = lambda: 5000  # 5 secondes
        
        sys.modules['pygame'] = pygame_mock
        
        mock_app = MockApp()
        optimizer = ThreadOptimizer(mock_app)
        
        # Tester différents modes
        modes = ['eco', 'normal', 'performance']
        results = {}
        
        for mode in modes:
            optimizer.set_performance_mode(mode)
            
            # Mesurer la fréquence de mise à jour
            start_time = time.time()
            sleep_time = optimizer._get_adaptive_sleep_time()
            fps = 1 / sleep_time if sleep_time > 0 else 0
            
            results[mode] = {
                'sleep_time': sleep_time,
                'fps': fps
            }
        
        print("📊 Résultats du test de thread:")
        for mode, data in results.items():
            print(f"  {mode}: {data['fps']:.1f} FPS (sleep: {data['sleep_time']:.3f}s)")
        
        return results
        
    except Exception as e:
        print(f"❌ Erreur test thread: {e}")
        return None

def stress_test_memory_optimization():
    """Test de stress pour l'optimisation mémoire"""
    print("🧪 Test de stress - Optimisation mémoire")
    
    try:
        from memory_optimizer import MemoryOptimizer
        
        # Simuler une app avec des caches
        class MockApp:
            def __init__(self):
                self.thumbnail_cache = {f"file_{i}": f"data_{i}" for i in range(150)}
                self.extended_search_cache = {f"query_{i}": f"result_{i}" for i in range(120)}
                self.artist_cache = {f"artist_{i}": f"data_{i}" for i in range(30)}
                self.playlist_content_cache = {f"playlist_{i}": f"content_{i}" for i in range(40)}
                
                # Mock root
                self.root = type('MockRoot', (), {
                    'after': lambda delay, func: None,
                    'after_cancel': lambda timer_id: None
                })()
        
        mock_app = MockApp()
        optimizer = MemoryOptimizer(mock_app)
        
        # Mesurer avant nettoyage
        initial_sizes = {
            'thumbnail_cache': len(mock_app.thumbnail_cache),
            'extended_search_cache': len(mock_app.extended_search_cache),
            'artist_cache': len(mock_app.artist_cache),
            'playlist_content_cache': len(mock_app.playlist_content_cache)
        }
        
        # Effectuer le nettoyage
        optimizer._perform_cleanup()
        
        # Mesurer après nettoyage
        final_sizes = {
            'thumbnail_cache': len(mock_app.thumbnail_cache),
            'extended_search_cache': len(mock_app.extended_search_cache),
            'artist_cache': len(mock_app.artist_cache),
            'playlist_content_cache': len(mock_app.playlist_content_cache)
        }
        
        print("📊 Résultats du test de mémoire:")
        for cache_name in initial_sizes:
            initial = initial_sizes[cache_name]
            final = final_sizes[cache_name]
            cleaned = initial - final
            print(f"  {cache_name}: {initial} → {final} (-{cleaned})")
        
        return {'initial': initial_sizes, 'final': final_sizes}
        
    except Exception as e:
        print(f"❌ Erreur test mémoire: {e}")
        return None

def run_full_performance_test():
    """Lance tous les tests de performance"""
    print("🚀 TESTS DE PERFORMANCE COMPLETS")
    print("=" * 60)
    
    results = {}
    
    # Test thread
    thread_results = stress_test_thread_optimization()
    if thread_results:
        results['thread'] = thread_results
    
    print()
    
    # Test mémoire
    memory_results = stress_test_memory_optimization()
    if memory_results:
        results['memory'] = memory_results
    
    print()
    
    # Résumé
    print("📋 RÉSUMÉ DES TESTS:")
    print("=" * 30)
    
    if 'thread' in results:
        print("✅ Optimisation thread: OK")
        eco_fps = results['thread']['eco']['fps']
        perf_fps = results['thread']['performance']['fps']
        print(f"   Plage FPS: {eco_fps:.1f} (éco) à {perf_fps:.1f} (performance)")
    
    if 'memory' in results:
        print("✅ Optimisation mémoire: OK")
        total_cleaned = sum(
            results['memory']['initial'][cache] - results['memory']['final'][cache]
            for cache in results['memory']['initial']
        )
        print(f"   Éléments nettoyés: {total_cleaned}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "thread":
            stress_test_thread_optimization()
        elif sys.argv[1] == "memory":
            stress_test_memory_optimization()
        elif sys.argv[1] == "full":
            run_full_performance_test()
        else:
            print("Usage: python test_performance_improvements.py [thread|memory|full]")
    else:
        print("🧪 TESTEUR DE PERFORMANCE")
        print("=" * 40)
        print("Ce script teste les optimisations de performance")
        print("\nCommandes disponibles:")
        print("  python test_performance_improvements.py thread  - Test thread")
        print("  python test_performance_improvements.py memory  - Test mémoire")
        print("  python test_performance_improvements.py full    - Tous les tests")
        print("\nPour intégrer dans l'app:")
        print("  from test_performance_improvements import PerformanceTester")
        print("  tester = PerformanceTester()")
        print("  tester.measure_baseline(app)")
        print("  # ... appliquer optimisations ...")
        print("  tester.measure_optimized(app)")
        print("  print(tester.generate_comparison_report())")