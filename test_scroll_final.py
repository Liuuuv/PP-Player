#!/usr/bin/env python3
"""
Test final du scroll - tout devrait fonctionner maintenant
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_final_scroll():
    """Test final du scroll"""
    print("=== Test final du scroll ===")
    
    try:
        from main import MusicPlayer
        import tkinter as tk
        
        # Créer une instance
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Simuler une playlist avec des éléments
        test_files = [f"test_song_{i:03d}.mp3" for i in range(30)]
        player.main_playlist = test_files
        
        print(f"📊 DEBUG: Playlist créée avec {len(player.main_playlist)} éléments")
        
        # Afficher la playlist
        player._display_main_playlist()
        
        # Vérifications finales
        scroll_region = player.playlist_canvas.cget('scrollregion')
        children_count = len(player.playlist_container.winfo_children())
        
        print(f"📏 DEBUG: Région de scroll finale: {scroll_region}")
        print(f"👶 DEBUG: Nombre d'enfants: {children_count}")
        
        # Vérifier que tout est correct
        success = True
        
        if scroll_region == '0 0 0 0' or scroll_region == '0 0 1 1':
            print("❌ DEBUG: Région de scroll incorrecte")
            success = False
        else:
            print("✅ DEBUG: Région de scroll correcte")
        
        if children_count == 0:
            print("❌ DEBUG: Aucun enfant dans le container")
            success = False
        else:
            print("✅ DEBUG: Container a des enfants")
        
        # Test de la hauteur
        try:
            x1, y1, x2, y2 = map(float, scroll_region.split())
            height = y2 - y1
            if height > 500:  # Au moins 500px pour 30 éléments
                print(f"✅ DEBUG: Hauteur suffisante: {height}px")
            else:
                print(f"❌ DEBUG: Hauteur insuffisante: {height}px")
                success = False
        except:
            print("❌ DEBUG: Erreur parsing région")
            success = False
        
        root.destroy()
        return success
        
    except Exception as e:
        print(f"❌ DEBUG: Erreur générale: {e}")
        return False

def show_final_instructions():
    """Affiche les instructions finales"""
    print("\n" + "="*60)
    print("🎉 TEST FINAL DU SCROLL")
    print("="*60)
    
    print("\n✅ CORRECTIONS APPLIQUÉES:")
    print("   1. Fonction _display_main_playlist() créée")
    print("   2. Région de scroll calculée manuellement")
    print("   3. Hauteur totale correctement configurée")
    print("   4. Éléments affichés dans le container")
    
    print("\n🧪 MAINTENANT TESTEZ DANS L'APPLICATION:")
    print("   1. Lancez votre application musicale")
    print("   2. Allez dans l'onglet 'Recherche'")
    print("   3. Ajoutez quelques musiques à la playlist")
    print("   4. Appelez player._display_main_playlist() si nécessaire")
    print("   5. Scrollez avec la molette")
    
    print("\n🎯 RÉSULTAT ATTENDU:")
    print("   🎉 LES MUSIQUES DEVRAIENT ENFIN DÉFILER !")
    print("   🖱️ Scroll normal de Tkinter fonctionnel")
    print("   📏 Région de scroll correctement configurée")
    print("   👶 Éléments visibles dans la playlist")
    
    print("\n🔧 SI ÇA NE MARCHE TOUJOURS PAS:")
    print("   → Vérifiez que _display_main_playlist() est appelée")
    print("   → Vérifiez que vous avez des musiques dans la playlist")
    print("   → Redémarrez l'application pour appliquer tous les changements")

if __name__ == "__main__":
    print("🎉 TEST FINAL DU SCROLL")
    print("="*60)
    
    success = test_final_scroll()
    
    show_final_instructions()
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 TOUTES LES CORRECTIONS APPLIQUÉES AVEC SUCCÈS !")
        print("✅ Région de scroll correcte")
        print("✅ Éléments affichés")
        print("✅ Configuration complète")
        print("🖱️ LE SCROLL DEVRAIT MAINTENANT FONCTIONNER !")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("⚠️ Il reste des problèmes à corriger")
        print(f"{'='*60}")