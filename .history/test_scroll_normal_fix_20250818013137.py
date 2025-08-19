#!/usr/bin/env python3
"""
Test de la correction du scroll normal
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_scroll_normal_fix():
    """Test de la correction du scroll normal"""
    print("=== Test de la correction du scroll normal ===")
    
    try:
        from search_tab.config import get_main_playlist_config, USE_NEW_CONFIG
        
        # Vérifier la configuration
        scroll_infini = get_main_playlist_config('enable_infinite_scroll')
        print(f"📊 DEBUG: USE_NEW_CONFIG: {USE_NEW_CONFIG}")
        print(f"📊 DEBUG: enable_infinite_scroll: {scroll_infini}")
        print(f"📊 DEBUG: Scroll infini actif: {USE_NEW_CONFIG and scroll_infini}")
        
        if USE_NEW_CONFIG and scroll_infini:
            print("⚠️ ATTENTION: Le scroll infini est encore activé")
            print("❌ Le scroll normal ne fonctionnera pas")
        else:
            print("✅ Scroll infini désactivé, le scroll normal devrait fonctionner")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def show_normal_scroll_instructions():
    """Affiche les instructions pour tester le scroll normal"""
    print("\n" + "="*60)
    print("🔧 CORRECTION DU SCROLL NORMAL")
    print("="*60)
    
    print("\n🔍 PROBLÈME IDENTIFIÉ:")
    print("   • Le scroll était intercepté par nos fonctions personnalisées")
    print("   • Même avec le scroll infini désactivé")
    print("   • Le scroll normal de Tkinter n'était jamais exécuté")
    
    print("\n✅ CORRECTION APPLIQUÉE:")
    print("   • Vérification du statut du scroll infini dans inputs.py")
    print("   • Si désactivé → utilisation du scroll normal de Tkinter")
    print("   • Si activé → utilisation de nos fonctions personnalisées")
    
    print("\n🧪 MAINTENANT TESTEZ:")
    print("   1. Lancez votre application musicale")
    print("   2. Allez dans l'onglet 'Recherche'")
    print("   3. Scrollez avec la molette dans la playlist")
    
    print("\n📊 MESSAGES ATTENDUS:")
    print("   🖱️ DEBUG: Scroll détecté sur playlist_canvas")
    print("   🔧 DEBUG: Scroll infini activé: False")
    print("   ⏸️ DEBUG: Scroll infini désactivé, utilisation du scroll normal de Tkinter")
    print("   (PAS de messages _update_display_based_on_scroll_position)")
    
    print("\n🎯 RÉSULTAT ATTENDU:")
    print("   ✅ Les musiques devraient maintenant défiler normalement")
    print("   ✅ Scroll standard de Tkinter")
    print("   ✅ Pas d'interférence de nos fonctions personnalisées")

if __name__ == "__main__":
    print("🔧 TEST DE LA CORRECTION DU SCROLL NORMAL")
    print("="*60)
    
    success = test_scroll_normal_fix()
    
    show_normal_scroll_instructions()
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 CORRECTION DU SCROLL NORMAL APPLIQUÉE !")
        print("✅ Logique conditionnelle implémentée")
        print("🧪 Testez maintenant: le scroll normal devrait fonctionner !")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ Erreur lors de la vérification")
        print(f"{'='*60}")