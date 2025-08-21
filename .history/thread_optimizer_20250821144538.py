#!/usr/bin/env python3
"""
Optimiseur de thread pour le lecteur de musique
Optimise le thread update_time pour réduire l'usage CPU
"""

import time
import pygame
import tkinter as tk
import threading

class ThreadOptimizer:
    """Optimiseur pour le thread de mise à jour du temps"""
    
    def __init__(self, app):
        self.app = app
        self.last_update_time = 0
        self.last_position = -1
        self.update_counter = 0
        self.performance_mode = "normal"  # normal, eco, performance
        
    def optimized_update_time(self):
        """Version optimisée du thread update_time avec fréquence adaptative"""
        print("🚀 Thread optimisé démarré")
        
        while True:
            try:
                # Vérifier si l'application est fermée
                if hasattr(self.app, '_app_destroyed') and self.app._app_destroyed:
                    break
                
                if not pygame.mixer.get_init():
                    break
                
                current_time = time.time()
                
                # Fréquence adaptative selon l'état
                sleep_time = self._get_adaptive_sleep_time()
                
                # Mise à jour seulement si nécessaire
                needs_update = self._check_if_update_needed()
                
                if pygame.mixer.music.get_busy() and not self.app.paused and not self.app.user_dragging:
                    pygame_pos = pygame.mixer.music.get_pos() / 1000
                    
                    if pygame_pos >= 0:
                        new_position = self.app.base_position + pygame_pos
                        
                        # Mise à jour seulement si changement significatif (>0.1s)
                        if abs(new_position - self.last_position) > 0.1:
                            self.app.current_time = new_position
                            self.last_position = new_position
                            needs_update = True
                    
                    # Vérifier fin de piste
                    if self.app.current_time > self.app.song_length:
                        self.app.current_time = self.app.song_length
                        self.app.next_track()
                        needs_update = True
                    
                    # Filtrer les valeurs négatives
                    if self.app.current_time < 0:
                        self.app.current_time = 0
                
                # Mise à jour UI seulement si nécessaire et pas suspendue
                if needs_update and not getattr(self.app, 'update_suspended', False):
                    try:
                        self.app.root.after(0, self._update_ui_safe)
                    except (tk.TclError, AttributeError):
                        break
                
                # update_idletasks moins fréquent
                self.update_counter += 1
                if self._should_update_idletasks():
                    try:
                        self.app.root.after(0, lambda: self.app.root.update_idletasks())
                    except (tk.TclError, AttributeError):
                        break
                        
            except (pygame.error, AttributeError) as e:
                print(f"Erreur dans update_time optimisé (pygame): {e}")
                break
            except Exception as e:
                print(f"Erreur dans update_time optimisé: {e}")
                
            time.sleep(sleep_time)
        
        print("🛑 Thread optimisé arrêté")
    
    def _get_adaptive_sleep_time(self):
        """Calcule le temps de sleep adaptatif selon l'état"""
        if hasattr(self.app, 'update_suspended') and self.app.update_suspended:
            return 1.0  # 1 FPS pendant suspension (déplacement fenêtre)
        elif self.app.paused:
            return 0.5  # 2 FPS en pause
        elif not pygame.mixer.music.get_busy():
            return 0.25  # 4 FPS si pas de musique
        elif self.performance_mode == "eco":
            return 0.2  # 5 FPS en mode éco
        elif self.performance_mode == "performance":
            return 0.05  # 20 FPS en mode performance
        else:
            return 0.1  # 10 FPS normal
    
    def _check_if_update_needed(self):
        """Vérifie si une mise à jour est nécessaire"""
        current_time = time.time()
        
        # Forcer une mise à jour au moins toutes les secondes
        if current_time - self.last_update_time > 1.0:
            self.last_update_time = current_time
            return True
        
        # Sinon, mise à jour seulement si changement
        return False
    
    def _update_ui_safe(self):
        """Met à jour l'interface utilisateur de manière thread-safe"""
        try:
            self.app.progress.config(value=self.app.current_time)
            self.app.current_time_label.config(
                text=time.strftime('%M:%S', time.gmtime(self.app.current_time))
            )
            
            # Waveform seulement si activée
            if getattr(self.app, 'show_waveform_current', False):
                self.app.draw_waveform_around(self.app.current_time)
            else:
                if hasattr(self.app, 'waveform_canvas'):
                    self.app.waveform_canvas.delete("all")
                    
        except (tk.TclError, AttributeError):
            # Interface détruite, ignorer silencieusement
            pass

    def _update_ui(self):
        """Met à jour l'interface utilisateur (ancienne méthode, conservée pour compatibilité)"""
        self._update_ui_safe()
    
    def _should_update_idletasks(self):
        """Détermine si update_idletasks doit être appelé"""
        if getattr(self.app, 'update_suspended', False):
            return False
        
        # Moins fréquent selon le mode
        if self.performance_mode == "eco":
            return self.update_counter % 5 == 0  # Tous les 5 cycles
        elif self.performance_mode == "performance":
            return self.update_counter % 2 == 0  # Tous les 2 cycles
        else:
            return self.update_counter % 3 == 0  # Tous les 3 cycles (normal)
    
    def set_performance_mode(self, mode):
        """Change le mode de performance"""
        if mode in ["normal", "eco", "performance"]:
            self.performance_mode = mode
            print(f"🎛️ Mode de performance: {mode}")
        else:
            print(f"❌ Mode invalide: {mode}")
    
    def get_performance_stats(self):
        """Retourne les statistiques de performance"""
        return {
            'mode': self.performance_mode,
            'last_position': self.last_position,
            'update_counter': self.update_counter,
            'sleep_time': self._get_adaptive_sleep_time()
        }


class CallbackOptimizer:
    """Optimiseur pour les callbacks Tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.pending_callbacks = {}
        self.callback_counter = 0
        
    def safe_after(self, delay, callback, callback_id=None):
        """Version optimisée de root.after avec déduplication"""
        if callback_id:
            # Annuler le callback précédent avec le même ID
            if callback_id in self.pending_callbacks:
                try:
                    self.root.after_cancel(self.pending_callbacks[callback_id])
                except:
                    pass  # Callback déjà exécuté ou annulé
        
        # Créer un wrapper qui nettoie automatiquement
        def wrapper():
            if callback_id and callback_id in self.pending_callbacks:
                del self.pending_callbacks[callback_id]
            try:
                callback()
            except Exception as e:
                print(f"Erreur callback {callback_id}: {e}")
        
        # Programmer le callback
        try:
            timer_id = self.root.after(delay, wrapper)
            
            if callback_id:
                self.pending_callbacks[callback_id] = timer_id
                
            return timer_id
        except tk.TclError:
            # Interface détruite
            return None
    
    def cancel_callback(self, callback_id):
        """Annule un callback spécifique"""
        if callback_id in self.pending_callbacks:
            try:
                self.root.after_cancel(self.pending_callbacks[callback_id])
                del self.pending_callbacks[callback_id]
                return True
            except:
                pass
        return False
    
    def cancel_all_callbacks(self):
        """Annule tous les callbacks en attente"""
        cancelled_count = 0
        for callback_id, timer_id in list(self.pending_callbacks.items()):
            try:
                self.root.after_cancel(timer_id)
                cancelled_count += 1
            except:
                pass
        
        self.pending_callbacks.clear()
        print(f"🧹 {cancelled_count} callbacks annulés")
        return cancelled_count
    
    def get_pending_count(self):
        """Retourne le nombre de callbacks en attente"""
        return len(self.pending_callbacks)


def apply_thread_optimizations(app):
    """Applique les optimisations de thread à l'application"""
    print("🔧 Application des optimisations de thread...")
    
    # Créer l'optimiseur de thread
    app.thread_optimizer = ThreadOptimizer(app)
    
    # Créer l'optimiseur de callbacks
    app.callback_optimizer = CallbackOptimizer(app.root)
    
    # Remplacer le thread existant
    if hasattr(app, 'update_thread') and app.update_thread.is_alive():
        print("⚠️ Arrêt de l'ancien thread...")
        # Le thread s'arrêtera naturellement à la prochaine itération
        # car on va changer la méthode
    
    # Créer le nouveau thread optimisé
    app.update_thread = threading.Thread(
        target=app.thread_optimizer.optimized_update_time, 
        daemon=True
    )
    app.update_thread.start()
    
    # Ajouter une méthode safe_after à l'app
    app.safe_after = app.callback_optimizer.safe_after
    
    print("✅ Optimisations de thread appliquées")
    
    return app.thread_optimizer, app.callback_optimizer


if __name__ == "__main__":
    print("🧪 Test des optimisations de thread")
    print("Ce module doit être importé dans main.py")
    print("Usage: from thread_optimizer import apply_thread_optimizations")
    print("       apply_thread_optimizations(self)")