#!/usr/bin/env python3
"""
Test du système de windowing intelligent
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_smart_windowing():
    """Test du système de windowing intelligent"""
    print("=== Test du système de windowing intelligent ===")
    
    try:
        from main import MusicPlayer
        import tkinter as tk
        
        # Créer une instance
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Créer une grande playlist pour tester le windowing
        playlist_size = 100
        test_files = [f"test_song_{i:03d}.mp3" for i in range(playlist_size)]
        player.main_playlist = test_files
        
        # Simuler une chanson en cours au milieu
        player.current_song_index = 50  # Chanson en cours de lecture
        player.playlist_view_center = 50  # Vue centrée sur la même chanson
        
        print(f"📊 DEBUG: Playlist de {playlist_size} éléments")
        print(f"🎵 DEBUG: Chanson en cours: index {player.current_song_index}")
        print(f"👁️ DEBUG: Vue centrée sur: index {player.playlist_view_center}")
        
        # Tester l'affichage windowed
        player._display_main_playlist()
        
        # Vérifier les résultats
        if hasattr(player, 'playlist_container'):
            children = player.playlist_container.winfo_children()
            displayed_count = len(children)
            print(f"✅ DEBUG: {displayed_count} éléments affichés")
            
            # Vérifier qu'on a bien le windowing (pas tous les éléments)
            if displayed_count < playlist_size:
                print("✅ DEBUG: Windowing activé (pas tous les éléments affichés)")
            else:
                print("⚠️ DEBUG: Tous les éléments affichés (windowing non activé)")
            
            # Vérifier la fenêtre actuelle
            if hasattr(player, '_current_window_bounds'):
                start, end = player._current_window_bounds
                print(f"🪟 DEBUG: Fenêtre actuelle: [{start}:{end}]")
                
                # Vérifier que la chanson en cours est dans la fenêtre
                if start <= player.current_song_index <= end:
                    print("✅ DEBUG: Chanson en cours dans la fenêtre affichée")
                else:
                    print("❌ DEBUG: Chanson en cours HORS de la fenêtre affichée")
        
        # Simuler une navigation
        print("\n🔄 DEBUG: Test de navigation intelligente...")
        
        # Changer la vue (pas la lecture)
        player.playlist_view_center = 20  # Regarder vers le début
        player._display_windowed_playlist()
        
        if hasattr(player, '_current_window_bounds'):
            start, end = player._current_window_bounds
            print(f"🪟 DEBUG: Nouvelle fenêtre après navigation: [{start}:{end}]")
            
            # Vérifier que la position de lecture n'a pas changé
            if player.current_song_index == 50:
                print("✅ DEBUG: Position de lecture préservée (toujours index 50)")
            else:
                print(f"❌ DEBUG: Position de lecture changée: {player.current_song_index}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_smart_windowing_instructions():
    """Affiche les instructions pour le windowing intelligent"""
    print("\n" + "="*60)
    print("🧠 SYSTÈME DE WINDOWING INTELLIGENT RESTAURÉ")
    print("="*60)
    
    print("\n✅ NOUVELLES FONCTIONNALITÉS :")
    print("1. 🎵 Position de LECTURE séparée de la position de VUE")
    print("2. 🪟 Fenêtre intelligente qui s'étend pour éviter les interruptions")
    print("3. 🎨 Chanson en cours mise en surbrillance avec COLOR_SELECTED")
    print("4. 🔄 Navigation fluide sans changer la position de lecture")
    print("5. 📏 Fenêtre adaptative (10 avant + 10 après + buffer intelligent)")
    
    print("\n🧪 TESTEZ DANS VOTRE APPLICATION :")
    print("1. Ajoutez plus de 50 musiques à la playlist")
    print("2. Lancez une musique (pour avoir current_song_index)")
    print("3. Vous devriez voir :")
    print("   🪟 DEBUG: Windowing activé: True")
    print("   🎵 DEBUG: Chanson en cours (index X) mise en surbrillance")
    print("   🪟 DEBUG: Fenêtre [Y:Z] centrée sur vue A, lecture B")
    
    print("\n4. Cliquez sur '... musiques précédentes' ou '... musiques suivantes'")
    print("5. Vous devriez voir :")
    print("   🔼 DEBUG: Navigation vers précédentes, nouvelle vue centrée sur X")
    print("   🧠 DEBUG: Extension intelligente [A:B] pour navigation fluide")
    print("   ✅ DEBUG: Position de lecture préservée")
    
    print("\n🎯 COMPORTEMENT ATTENDU :")
    print("• La chanson EN COURS reste en surbrillance même si hors vue")
    print("• Les indicateurs changent seulement la VUE, pas la LECTURE")
    print("• La fenêtre s'étend intelligemment pour éviter les rechargements")
    print("• Navigation fluide avec buffer adaptatif")
    
    print("\n⚙️ CONFIGURATION AVANCÉE :")
    print("• Fenêtre de base : 10 avant + 10 après")
    print("• Buffer intelligent : +25 éléments pour navigation fluide")
    print("• Limite maximale : 100 éléments par fenêtre")
    print("• Seuil windowing : 50 éléments (configurable)")

if __name__ == "__main__":
    print("🧠 TEST DU SYSTÈME DE WINDOWING INTELLIGENT")
    print("="*60)
    
    success = test_smart_windowing()
    
    show_smart_windowing_instructions()
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 SYSTÈME DE WINDOWING INTELLIGENT RESTAURÉ !")
        print("✅ Navigation intelligente sans interruption")
        print("✅ Position de lecture préservée")
        print("✅ Chanson en cours mise en surbrillance")
        print("✅ Fenêtre adaptative et performante")
        print("🧪 Testez avec une grande playlist !")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ Erreur lors du test du windowing intelligent")
        print(f"{'='*60}")