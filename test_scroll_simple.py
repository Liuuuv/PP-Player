#!/usr/bin/env python3
"""
Test simple du scroll sans fenêtrage
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_simple_scroll():
    """Test du scroll sans système de fenêtrage"""
    print("=== Test du scroll simple (sans fenêtrage) ===")
    
    try:
        from search_tab.config import get_main_playlist_config, update_main_playlist_config
        
        # Vérifier que le scroll infini est désactivé
        infinite_scroll = get_main_playlist_config('enable_infinite_scroll')
        print(f"📊 DEBUG: Scroll infini: {infinite_scroll}")
        
        if infinite_scroll:
            print("⚠️ ATTENTION: Le scroll infini est encore activé")
            print("🔧 Désactivation du scroll infini...")
            update_main_playlist_config(enable_infinite_scroll=False)
            print("✅ Scroll infini désactivé")
        else:
            print("✅ Scroll infini déjà désactivé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def show_simple_test_instructions():
    """Affiche les instructions pour le test simple"""
    print("\n" + "="*60)
    print("🧪 TEST SIMPLE DU SCROLL")
    print("="*60)
    
    print("\n🎯 OBJECTIF:")
    print("   Vérifier si le scroll fonctionne normalement SANS notre système")
    print("   de fenêtrage pour identifier si le problème vient de là")
    
    print("\n🔧 CHANGEMENT EFFECTUÉ:")
    print("   ❌ Scroll infini DÉSACTIVÉ temporairement")
    print("   ✅ Retour au scroll normal de Tkinter")
    
    print("\n🧪 INSTRUCTIONS DE TEST:")
    print("   1. Lancez votre application musicale")
    print("   2. Allez dans l'onglet 'Recherche'")
    print("   3. Scrollez avec la molette dans la playlist")
    print("   4. Observez si les musiques défilent NORMALEMENT")
    
    print("\n📊 RÉSULTATS POSSIBLES:")
    print("   ✅ SI ça marche → Le problème était dans notre système de fenêtrage")
    print("   ❌ SI ça ne marche pas → Le problème est plus profond (région de scroll)")
    
    print("\n🔍 MESSAGES DE DEBUG À OBSERVER:")
    print("   • Vous devriez voir moins de messages de debug")
    print("   • Pas de messages '_update_windowed_display'")
    print("   • Scroll normal de Tkinter seulement")
    
    print("\n⚡ APRÈS LE TEST:")
    print("   • Rapportez si le scroll fonctionne ou non")
    print("   • Je réactiverai le système avec les corrections nécessaires")

if __name__ == "__main__":
    print("🧪 TEST SIMPLE DU SCROLL (SANS FENÊTRAGE)")
    print("="*60)
    
    success = test_simple_scroll()
    
    show_simple_test_instructions()
    
    if success:
        print(f"\n{'='*60}")
        print("✅ CONFIGURATION DE TEST SIMPLE PRÊTE")
        print("🧪 Testez maintenant le scroll dans l'application")
        print("📋 Rapportez si ça fonctionne ou non")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ Erreur lors de la configuration du test")
        print(f"{'='*60}")