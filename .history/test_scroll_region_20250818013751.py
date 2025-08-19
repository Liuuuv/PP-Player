#!/usr/bin/env python3
"""
Test de la région de scroll
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_scroll_region():
    """Test de la région de scroll"""
    print("=== Test de la région de scroll ===")
    
    try:
        from main import MusicPlayer
        import tkinter as tk
        
        # Créer une instance
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Simuler une playlist avec des éléments
        test_files = [f"test_song_{i:03d}.mp3" for i in range(20)]
        player.main_playlist = test_files
        
        print(f"📊 DEBUG: Playlist créée avec {len(player.main_playlist)} éléments")
        
        # Forcer l'affichage de la playlist
        if hasattr(player, '_display_main_playlist'):
            print("🔄 DEBUG: Affichage de la playlist...")
            player._display_main_playlist()
        
        # Vérifier la région de scroll
        if hasattr(player, 'playlist_canvas'):
            scroll_region = player.playlist_canvas.cget('scrollregion')
            bbox = player.playlist_canvas.bbox("all")
            
            print(f"📏 DEBUG: Région de scroll configurée: {scroll_region}")
            print(f"📏 DEBUG: Bbox réelle: {bbox}")
            
            if scroll_region and scroll_region != '0 0 0 0':
                print("✅ DEBUG: Région de scroll non vide")
                
                # Parser la région
                try:
                    x1, y1, x2, y2 = map(float, scroll_region.split())
                    height = y2 - y1
                    print(f"📏 DEBUG: Hauteur de la région: {height}px")
                    
                    if height > 0:
                        print("✅ DEBUG: Région de scroll a une hauteur positive")
                    else:
                        print("❌ DEBUG: Région de scroll a une hauteur nulle ou négative")
                        
                except Exception as e:
                    print(f"⚠️ DEBUG: Erreur parsing région: {e}")
            else:
                print("❌ DEBUG: Région de scroll vide ou non configurée")
                print("🔧 DEBUG: Tentative de mise à jour manuelle...")
                
                # Forcer la mise à jour de la région
                player.playlist_canvas.update_idletasks()
                new_bbox = player.playlist_canvas.bbox("all")
                if new_bbox:
                    player.playlist_canvas.configure(scrollregion=new_bbox)
                    new_scroll_region = player.playlist_canvas.cget('scrollregion')
                    print(f"📏 DEBUG: Nouvelle région après mise à jour: {new_scroll_region}")
        
        # Vérifier les enfants du container
        if hasattr(player, 'playlist_container'):
            children = player.playlist_container.winfo_children()
            print(f"👶 DEBUG: Nombre d'enfants dans le container: {len(children)}")
            
            if len(children) > 0:
                print("✅ DEBUG: Container a des enfants")
                
                # Calculer la hauteur totale
                total_height = 0
                for child in children:
                    try:
                        child_height = child.winfo_reqheight()
                        total_height += child_height
                        print(f"📏 DEBUG: Enfant {type(child).__name__}: {child_height}px")
                    except:
                        pass
                
                print(f"📏 DEBUG: Hauteur totale calculée: {total_height}px")
            else:
                print("❌ DEBUG: Container vide - pas d'éléments affichés")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_scroll_region_instructions():
    """Affiche les instructions pour diagnostiquer la région de scroll"""
    print("\n" + "="*60)
    print("🔍 DIAGNOSTIC DE LA RÉGION DE SCROLL")
    print("="*60)
    
    print("\n🎯 HYPOTHÈSE:")
    print("   Le scroll ne fonctionne pas car la région de scroll")
    print("   n'est pas correctement configurée ou mise à jour")
    
    print("\n🔧 POINTS À VÉRIFIER:")
    print("   1. La région de scroll est-elle configurée ?")
    print("   2. A-t-elle une hauteur positive ?")
    print("   3. Le container a-t-il des enfants ?")
    print("   4. La hauteur totale est-elle cohérente ?")
    
    print("\n🧪 MAINTENANT TESTEZ DANS L'APPLICATION:")
    print("   1. Lancez votre application")
    print("   2. Allez dans l'onglet 'Recherche'")
    print("   3. Ajoutez quelques musiques à la playlist")
    print("   4. Ouvrez la console Python et tapez:")
    print("      >>> print(f'Région: {app.playlist_canvas.cget(\"scrollregion\")}')")
    print("      >>> print(f'Bbox: {app.playlist_canvas.bbox(\"all\")}')")
    print("      >>> print(f'Enfants: {len(app.playlist_container.winfo_children())}')")
    
    print("\n🔍 SI LA RÉGION EST VIDE OU NULLE:")
    print("   → Le problème est dans la mise à jour de la région")
    print("   → Vérifier le binding <Configure> du container")
    print("   → Vérifier _update_canvas_scroll_region()")

if __name__ == "__main__":
    print("🔍 TEST DE LA RÉGION DE SCROLL")
    print("="*60)
    
    success = test_scroll_region()
    
    show_scroll_region_instructions()
    
    if success:
        print(f"\n{'='*60}")
        print("🔍 DIAGNOSTIC DE LA RÉGION TERMINÉ")
        print("📋 Vérifiez les résultats ci-dessus")
        print("🧪 Testez maintenant dans l'application réelle")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ Erreur lors du diagnostic")
        print(f"{'='*60}")