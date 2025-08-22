#!/usr/bin/env python3
"""
Script de test pour vérifier le fonctionnement du lazy loading
"""

import os
import sys
import time

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_lazy_loading():
    """Test du système de lazy loading"""
    print("🧪 Test du système de lazy loading")
    print("=" * 50)
    
    # Simuler une grande liste de fichiers
    test_files = []
    for i in range(1000):
        test_files.append(f"test_file_{i:04d}.mp3")
    
    print(f"📁 {len(test_files)} fichiers de test créés")
    
    # Simuler les paramètres du lazy loading
    lazy_item_height = 60
    lazy_buffer_items = 5
    canvas_height = 400  # Hauteur simulée du canvas
    
    # Calculer les éléments visibles
    scroll_top = 0
    scroll_bottom = scroll_top + canvas_height
    
    start_index = max(0, int(scroll_top / lazy_item_height) - lazy_buffer_items)
    end_index = min(len(test_files), 
                   int(scroll_bottom / lazy_item_height) + lazy_buffer_items + 1)
    
    print(f"🔍 Éléments visibles: {start_index} à {end_index}")
    print(f"📊 Nombre d'éléments chargés: {end_index - start_index}")
    print(f"💾 Économie mémoire: {len(test_files) - (end_index - start_index)} éléments non chargés")
    print(f"📈 Pourcentage d'économie: {((len(test_files) - (end_index - start_index)) / len(test_files)) * 100:.1f}%")
    
    # Test de scroll
    print("\n🖱️ Test de scroll...")
    for scroll_position in [0, 200, 500, 800, 1200]:
        scroll_top = scroll_position
        scroll_bottom = scroll_top + canvas_height
        
        start_index = max(0, int(scroll_top / lazy_item_height) - lazy_buffer_items)
        end_index = min(len(test_files), 
                       int(scroll_bottom / lazy_item_height) + lazy_buffer_items + 1)
        
        print(f"  Position {scroll_position}px: éléments {start_index}-{end_index} ({end_index - start_index} chargés)")
    
    print("\n✅ Test terminé avec succès!")

if __name__ == "__main__":
    test_lazy_loading()