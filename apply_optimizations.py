#!/usr/bin/env python3
"""
Script d'application des optimisations avancées
Applique toutes les optimisations de performance au lecteur de musique
"""

import sys
import os
import time

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def apply_all_optimizations(app, config=None):
    """Applique toutes les optimisations à l'application"""
    
    if config is None:
        config = {
            'thread_optimization': True,
            'memory_optimization': True,
            'thumbnail_optimization': True,
            'memory_threshold_mb': 500,
            'memory_check_interval': 30,
            'thumbnail_cache_size': 100,
            'thumbnail_workers': 2
        }
    
    print("🚀 APPLICATION DES OPTIMISATIONS AVANCÉES")
    print("=" * 60)
    
    optimizers = {}
    
    # 1. Optimisations de thread
    if config.get('thread_optimization', True):
        try:
            from thread_optimizer import apply_thread_optimizations
            thread_opt, callback_opt = apply_thread_optimizations(app)
            optimizers['thread'] = thread_opt
            optimizers['callback'] = callback_opt
            print("✅ Optimisations de thread appliquées")
        except Exception as e:
            print(f"❌ Erreur optimisations thread: {e}")
    
    # 2. Optimisations mémoire
    if config.get('memory_optimization', True):
        try:
            from memory_optimizer import apply_memory_optimizations
            memory_opt = apply_memory_optimizations(
                app, 
                threshold_mb=config.get('memory_threshold_mb', 500),
                check_interval=config.get('memory_check_interval', 30)
            )
            optimizers['memory'] = memory_opt
            print("✅ Optimisations mémoire appliquées")
        except Exception as e:
            print(f"❌ Erreur optimisations mémoire: {e}")
    
    # 3. Optimisations miniatures
    if config.get('thumbnail_optimization', True):
        try:
            from thumbnail_optimizer import apply_thumbnail_optimizations
            thumbnail_opt = apply_thumbnail_optimizations(
                app,
                max_cache_size=config.get('thumbnail_cache_size', 100),
                max_workers=config.get('thumbnail_workers', 2)
            )
            optimizers['thumbnail'] = thumbnail_opt
            print("✅ Optimisations miniatures appliquées")
        except Exception as e:
            print(f"❌ Erreur optimisations miniatures: {e}")
    
    # Ajouter les optimiseurs à l'app pour accès ultérieur
    app.optimizers = optimizers
    
    # Ajouter des méthodes utilitaires à l'app
    app.get_performance_report = lambda: get_performance_report(app)
    app.force_cleanup = lambda: force_cleanup(app)
    app.optimize_for_mode = lambda mode: optimize_for_mode(app, mode)
    
    print("=" * 60)
    print("🎉 OPTIMISATIONS APPLIQUÉES AVEC SUCCÈS!")
    print("=" * 60)
    
    # Afficher un rapport initial
    time.sleep(1)  # Laisser le temps aux optimiseurs de s'initialiser
    print(get_performance_report(app))
    
    return optimizers

def get_performance_report(app):
    """Génère un rapport de performance complet"""
    if not hasattr(app, 'optimizers'):
        return "❌ Aucune optimisation appliquée"
    
    reports = ["📊 RAPPORT DE PERFORMANCE GLOBAL", "=" * 60]
    
    # Rapport thread
    if 'thread' in app.optimizers:
        try:
            thread_stats = app.optimizers['thread'].get_performance_stats()
            reports.append("🧵 THREAD:")
            reports.append(f"  Mode: {thread_stats['mode']}")
            reports.append(f"  Fréquence: {1/thread_stats['sleep_time']:.1f} FPS")
            reports.append(f"  Cycles: {thread_stats['update_counter']}")
        except:
            reports.append("🧵 THREAD: Erreur récupération stats")
    
    # Rapport mémoire
    if 'memory' in app.optimizers:
        try:
            memory_report = app.optimizers['memory'].get_performance_report()
            reports.append(memory_report)
        except:
            reports.append("💾 MÉMOIRE: Erreur récupération stats")
    
    # Rapport miniatures
    if 'thumbnail' in app.optimizers:
        try:
            thumbnail_report = app.optimizers['thumbnail'].get_performance_report()
            reports.append(thumbnail_report)
        except:
            reports.append("🖼️ MINIATURES: Erreur récupération stats")
    
    # Rapport callbacks
    if 'callback' in app.optimizers:
        try:
            pending = app.optimizers['callback'].get_pending_count()
            reports.append(f"⏰ CALLBACKS: {pending} en attente")
        except:
            reports.append("⏰ CALLBACKS: Erreur récupération stats")
    
    return "\n".join(reports)

def force_cleanup(app):
    """Force un nettoyage complet"""
    if not hasattr(app, 'optimizers'):
        return "❌ Aucune optimisation disponible"
    
    results = ["🧹 NETTOYAGE FORCÉ", "=" * 30]
    
    # Nettoyage mémoire
    if 'memory' in app.optimizers:
        try:
            freed = app.optimizers['memory'].force_cleanup()
            results.append(f"💾 Mémoire libérée: {freed:.1f}MB")
        except Exception as e:
            results.append(f"💾 Erreur nettoyage mémoire: {e}")
    
    # Nettoyage cache miniatures
    if 'thumbnail' in app.optimizers:
        try:
            cleared = app.optimizers['thumbnail'].clear_cache()
            results.append(f"🖼️ Miniatures supprimées: {cleared}")
        except Exception as e:
            results.append(f"🖼️ Erreur nettoyage miniatures: {e}")
    
    # Nettoyage callbacks
    if 'callback' in app.optimizers:
        try:
            cancelled = app.optimizers['callback'].cancel_all_callbacks()
            results.append(f"⏰ Callbacks annulés: {cancelled}")
        except Exception as e:
            results.append(f"⏰ Erreur nettoyage callbacks: {e}")
    
    return "\n".join(results)

def optimize_for_mode(app, mode):
    """Optimise l'application pour un mode spécifique"""
    if not hasattr(app, 'optimizers'):
        return "❌ Aucune optimisation disponible"
    
    modes = {
        'eco': {
            'description': 'Mode économique (faible CPU/mémoire)',
            'thread_mode': 'eco',
            'memory_threshold': 300,
            'thumbnail_cache': 30
        },
        'normal': {
            'description': 'Mode normal (équilibré)',
            'thread_mode': 'normal',
            'memory_threshold': 500,
            'thumbnail_cache': 100
        },
        'performance': {
            'description': 'Mode performance (réactivité maximale)',
            'thread_mode': 'performance',
            'memory_threshold': 800,
            'thumbnail_cache': 200
        }
    }
    
    if mode not in modes:
        return f"❌ Mode invalide. Modes disponibles: {', '.join(modes.keys())}"
    
    config = modes[mode]
    results = [f"🎛️ OPTIMISATION POUR MODE: {mode.upper()}", 
               f"📝 {config['description']}", "=" * 40]
    
    # Configurer le thread
    if 'thread' in app.optimizers:
        try:
            app.optimizers['thread'].set_performance_mode(config['thread_mode'])
            results.append(f"🧵 Thread: mode {config['thread_mode']}")
        except Exception as e:
            results.append(f"🧵 Erreur thread: {e}")
    
    # Configurer la mémoire
    if 'memory' in app.optimizers:
        try:
            app.optimizers['memory'].set_memory_threshold(config['memory_threshold'])
            results.append(f"💾 Mémoire: seuil {config['memory_threshold']}MB")
        except Exception as e:
            results.append(f"💾 Erreur mémoire: {e}")
    
    # Configurer les miniatures
    if 'thumbnail' in app.optimizers:
        try:
            app.optimizers['thumbnail'].max_cache_size = config['thumbnail_cache']
            results.append(f"🖼️ Miniatures: cache {config['thumbnail_cache']}")
        except Exception as e:
            results.append(f"🖼️ Erreur miniatures: {e}")
    
    return "\n".join(results)

def create_optimization_menu(app):
    """Crée un menu d'optimisation dans l'interface"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        def show_performance_report():
            report = get_performance_report(app)
            messagebox.showinfo("Rapport de Performance", report)
        
        def force_cleanup_ui():
            result = force_cleanup(app)
            messagebox.showinfo("Nettoyage Effectué", result)
        
        def set_eco_mode():
            result = optimize_for_mode(app, 'eco')
            messagebox.showinfo("Mode Éco", result)
        
        def set_normal_mode():
            result = optimize_for_mode(app, 'normal')
            messagebox.showinfo("Mode Normal", result)
        
        def set_performance_mode():
            result = optimize_for_mode(app, 'performance')
            messagebox.showinfo("Mode Performance", result)
        
        # Ajouter au menu principal si disponible
        if hasattr(app, 'menubar'):
            perf_menu = tk.Menu(app.menubar, tearoff=0)
            perf_menu.add_command(label="📊 Rapport de Performance", command=show_performance_report)
            perf_menu.add_separator()
            perf_menu.add_command(label="🧹 Nettoyage Forcé", command=force_cleanup_ui)
            perf_menu.add_separator()
            perf_menu.add_command(label="🔋 Mode Éco", command=set_eco_mode)
            perf_menu.add_command(label="⚖️ Mode Normal", command=set_normal_mode)
            perf_menu.add_command(label="🚀 Mode Performance", command=set_performance_mode)
            
            app.menubar.add_cascade(label="⚡ Optimisations", menu=perf_menu)
            print("✅ Menu d'optimisation ajouté")
        else:
            print("⚠️ Impossible d'ajouter le menu (menubar non trouvé)")
            
    except Exception as e:
        print(f"❌ Erreur création menu optimisation: {e}")

def test_optimizations():
    """Teste les optimisations sans application réelle"""
    print("🧪 TEST DES OPTIMISATIONS")
    print("=" * 40)
    
    # Test d'import des modules
    modules_to_test = [
        'thread_optimizer',
        'memory_optimizer', 
        'thumbnail_optimizer'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}: OK")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
        except Exception as e:
            print(f"⚠️ {module_name}: {e}")
    
    print("\n🎯 Pour appliquer les optimisations:")
    print("   from apply_optimizations import apply_all_optimizations")
    print("   apply_all_optimizations(self)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_optimizations()
    else:
        print("🚀 SCRIPT D'OPTIMISATION DU LECTEUR DE MUSIQUE")
        print("=" * 60)
        print("Ce script doit être importé dans main.py")
        print("\nUsage dans MusicPlayer.__init__():")
        print("  from apply_optimizations import apply_all_optimizations")
        print("  apply_all_optimizations(self)")
        print("\nPour tester les modules:")
        print("  python apply_optimizations.py test")
        print("\nFonctionnalités ajoutées à l'app:")
        print("  - self.get_performance_report()")
        print("  - self.force_cleanup()")
        print("  - self.optimize_for_mode('eco'|'normal'|'performance')")