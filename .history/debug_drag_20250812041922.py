#!/usr/bin/env python3
"""
Script pour déboguer le drag and drop dans l'application réelle
"""

import tkinter as tk
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Patcher le DragDropHandler pour ajouter du debug
original_setup_drag_start = None
original_on_drag_motion = None

def patch_drag_drop_handler():
    """Ajoute du debug au DragDropHandler"""
    global original_setup_drag_start, original_on_drag_motion
    
    try:
        from drag_drop_handler import DragDropHandler
        
        # Sauvegarder les méthodes originales
        original_setup_drag_start = DragDropHandler.setup_drag_start
        original_on_drag_motion = DragDropHandler._on_drag_motion
        
        def debug_setup_drag_start(self, event, frame):
            print(f"🟢 DRAG START: widget={event.widget.__class__.__name__}, frame={frame.__class__.__name__}")
            result = original_setup_drag_start(self, event, frame)
            print(f"   drag_enabled = {getattr(frame, 'drag_enabled', 'N/A')}")
            return result
        
        def debug_on_drag_motion(self, event, frame):
            if hasattr(frame, 'drag_enabled') and frame.drag_enabled:
                print(f"🔵 DRAG MOTION: widget={event.widget.__class__.__name__}, frame={frame.__class__.__name__}, enabled=True")
            else:
                print(f"🔴 DRAG MOTION: widget={event.widget.__class__.__name__}, frame={frame.__class__.__name__}, enabled=False")
            return original_on_drag_motion(self, event, frame)
        
        # Remplacer les méthodes
        DragDropHandler.setup_drag_start = debug_setup_drag_start
        DragDropHandler._on_drag_motion = debug_on_drag_motion
        
        print("✅ DragDropHandler patché avec debug")
        
    except Exception as e:
        print(f"❌ Erreur lors du patch: {e}")

def patch_downloads():
    """Ajoute du debug aux téléchargements"""
    try:
        from library_tab import downloads
        
        # Patcher la fonction qui crée les handlers
        original_add_download_item_fast = downloads._add_download_item_fast
        
        def debug_add_download_item_fast(self, filepath):
            print(f"📁 Création item téléchargement: {os.path.basename(filepath)}")
            return original_add_download_item_fast(self, filepath)
        
        downloads._add_download_item_fast = debug_add_download_item_fast
        
        print("✅ Downloads patché avec debug")
        
    except Exception as e:
        print(f"❌ Erreur lors du patch downloads: {e}")

if __name__ == "__main__":
    print("🔧 Application du patch de debug...")
    patch_drag_drop_handler()
    patch_downloads()
    
    print("🚀 Lancement de l'application avec debug...")
    
    # Importer et lancer l'application
    from main import MusicPlayer
    import tkinter as tk
    
    root = tk.Tk()
    app = MusicPlayer(root)
    
    print("📝 Instructions:")
    print("   1. Allez dans l'onglet Bibliothèque > Téléchargées")
    print("   2. Essayez de dragger depuis différents endroits sur une musique")
    print("   3. Regardez les messages de debug dans la console")
    
    root.mainloop()