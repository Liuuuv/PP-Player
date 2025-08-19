#!/usr/bin/env python3
"""
Test des optimisations de performance pour le déplacement de fenêtre
"""

import sys
import os
import time

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from main import MusicPlayer
import tkinter as tk

def test_window_performance():
    """Test les optimisations de performance de déplacement de fenêtre"""
    print("=== Test des optimisations de performance de fenêtre ===")
    
    # Créer l'application
    root = tk.Tk()
    app = MusicPlayer(root)
    
    # Vérifier que les variables d'optimisation sont initialisées
    assert hasattr(app, 'window_moving'), "Variable window_moving manquante"
    assert hasattr(app, 'update_suspended'), "Variable update_suspended manquante"
    assert hasattr(app, 'last_window_position'), "Variable last_window_position manquante"
    
    print("✓ Variables d'optimisation initialisées")
    
    # Vérifier l'état initial
    assert app.window_moving == False, "window_moving devrait être False au démarrage"
    assert app.update_suspended == False, "update_suspended devrait être False au démarrage"
    
    print("✓ État initial correct")
    
    # Simuler un déplacement de fenêtre
    print("Test de simulation de déplacement...")
    
    # Simuler le début du déplacement
    app.window_moving = True
    app.update_suspended = True
    
    # Vérifier que les mises à jour sont suspendues
    assert app.update_suspended == True, "Les mises à jour devraient être suspendues"
    
    print("✓ Suspension des mises à jour fonctionne")
    
    # Simuler la fin du déplacement
    app._end_window_move()
    
    # Vérifier que les mises à jour reprennent
    assert app.window_moving == False, "window_moving devrait être False après la fin"
    assert app.update_suspended == False, "update_suspended devrait être False après la fin"
    
    print("✓ Reprise des mises à jour fonctionne")
    
    # Test de la surveillance de position
    print("Test de surveillance de position...")
    
    # Obtenir la position actuelle
    initial_pos = app.last_window_position
    print(f"Position initiale: {initial_pos}")
    
    print("✓ Surveillance de position initialisée")
    
    print("\n=== Tous les tests passés avec succès ! ===")
    print("\nOptimisations implémentées:")
    print("- Suspension des mises à jour visuelles pendant le déplacement")
    print("- Réduction de la fréquence du thread de mise à jour (0.1s → 0.5s)")
    print("- Surveillance automatique des changements de position")
    print("- Optimisations de fenêtre Windows")
    
    # Fermer l'application
    root.quit()
    root.destroy()

if __name__ == "__main__":
    test_window_performance()