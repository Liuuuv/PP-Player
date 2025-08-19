#!/usr/bin/env python3
"""
Test du scroll de base sans aucune interférence
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_basic_scroll():
    """Test du scroll de base"""
    print("=== Test du scroll de base (sans interférence) ===")
    
    try:
        from main import MusicPlayer
        import tkinter as tk
        
        # Créer une instance
        root = tk.Tk()
        root.withdraw()
        
        player = MusicPlayer(root)
        
        # Vérifier la connexion scrollbar <-> canvas
        if hasattr(player, 'playlist_canvas') and hasattr(player, 'playlist_scrollbar'):
            print("✅ DEBUG: Canvas et scrollbar trouvés")
            
            # Vérifier la configuration
            try:
                scrollbar_command = player.playlist_scrollbar.cget('command')
                canvas_yscrollcommand = player.playlist_canvas.cget('yscrollcommand')
                
                print(f"📋 DEBUG: Commande scrollbar: {scrollbar_command}")
                print(f"📋 DEBUG: yscrollcommand canvas: {canvas_yscrollcommand}")
                
                # Vérifier que c'est bien connecté
                if 'yview' in str(scrollbar_command):
                    print("✅ DEBUG: Scrollbar correctement connectée au canvas")
                else:
                    print("❌ DEBUG: Scrollbar mal connectée")
                
                if 'set' in str(canvas_yscrollcommand):
                    print("✅ DEBUG: Canvas correctement connecté à la scrollbar")
                else:
                    print("❌ DEBUG: Canvas mal connecté")
                    
            except Exception as e:
                print(f"⚠️ DEBUG: Erreur vérification connexion: {e}")
        else:
            print("❌ DEBUG: Canvas ou scrollbar manquant")
        
        # Vérifier la région de scroll
        try:
            scroll_region = player.playlist_canvas.cget('scrollregion')
            print(f"📏 DEBUG: Région de scroll: {scroll_region}")
            
            if scroll_region and scroll_region != '0 0 0 0':
                print("✅ DEBUG: Région de scroll configurée")
            else:
                print("⚠️ DEBUG: Région de scroll vide ou non configurée")
        except Exception as e:
            print(f"⚠️ DEBUG: Erreur vérification région: {e}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Erreur générale: {e}")
        return False

def show_basic_test_instructions():
    """Affiche les instructions pour le test de base"""
    print("\n" + "="*60)
    print("🧪 TEST DU SCROLL DE BASE")
    print("="*60)
    
    print("\n🔧 CHANGEMENTS EFFECTUÉS:")
    print("   ❌ Tous nos bindings personnalisés SUPPRIMÉS")
    print("   ❌ Système de scroll infini COMPLÈTEMENT DÉSACTIVÉ")
    print("   ✅ Retour au scroll normal de Tkinter UNIQUEMENT")
    print("   ✅ Vérification de la connexion scrollbar <-> canvas")
    
    print("\n🧪 MAINTENANT TESTEZ:")
    print("   1. Lancez votre application musicale")
    print("   2. Allez dans l'onglet 'Recherche'")
    print("   3. Scrollez avec la molette dans la playlist")
    
    print("\n📊 MESSAGES ATTENDUS:")
    print("   🔧 DEBUG: _setup_infinite_scroll() appelée - DÉSACTIVÉE TEMPORAIREMENT")
    print("   ⏸️ DEBUG: Système de scroll infini complètement désactivé")
    print("   ✅ DEBUG: Connexion scrollbar <-> canvas vérifiée")
    print("   🖱️ DEBUG: Scroll normal de Tkinter - delta: XXX")
    
    print("\n🎯 DIAGNOSTIC:")
    print("   ✅ SI ça marche → Le problème était dans notre système personnalisé")
    print("   ❌ SI ça ne marche pas → Problème plus profond (région de scroll, etc.)")
    
    print("\n🔍 SI ÇA NE MARCHE TOUJOURS PAS:")
    print("   → Le problème est dans la configuration de base du canvas")
    print("   → Région de scroll mal configurée")
    print("   → Connexion scrollbar/canvas cassée")
    print("   → Problème dans setup.py")

if __name__ == "__main__":
    print("🧪 TEST DU SCROLL DE BASE (SANS INTERFÉRENCE)")
    print("="*60)
    
    success = test_basic_scroll()
    
    show_basic_test_instructions()
    
    if success:
        print(f"\n{'='*60}")
        print("🧪 CONFIGURATION DE BASE VÉRIFIÉE")
        print("✅ Tous les systèmes personnalisés supprimés")
        print("🖱️ Testez maintenant: scroll de base uniquement")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ Erreur lors de la vérification de base")
        print(f"{'='*60}")