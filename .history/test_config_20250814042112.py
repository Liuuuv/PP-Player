#!/usr/bin/env python3
# Script de test pour la configuration centralisée

print("=== TEST DE LA CONFIGURATION CENTRALISÉE ===")

try:
    from search_tab.config import (
        print_config_summary,
        get_display_config,
        get_cache_config,
        get_artist_config,
        get_ui_message,
        get_ui_color,
        validate_search_config
    )
    
    print("✅ Import de la configuration réussi")
    
    # Test des fonctions utilitaires
    print("\n=== TEST DES FONCTIONS UTILITAIRES ===")
    
    batch_size = get_display_config('batch_size')
    print(f"✅ Taille des lots: {batch_size}")
    
    max_searches = get_cache_config('max_searches', 'search')
    print(f"✅ Max recherches en cache: {max_searches}")
    
    artist_width = get_artist_config('max_width_artist_name')
    print(f"✅ Largeur max nom artiste: {artist_width}px")
    
    cache_message = get_ui_message('cache_restored', count=42)
    print(f"✅ Message cache: {cache_message}")
    
    cache_color = get_ui_color('cache_indicator_color')
    print(f"✅ Couleur cache: {cache_color}")
    
    # Test de validation
    print("\n=== TEST DE VALIDATION ===")
    errors = validate_search_config()
    if errors:
        print("❌ Erreurs de configuration:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration valide")
    
    # Afficher le résumé complet
    print("\n=== RÉSUMÉ COMPLET ===")
    print_config_summary()
    
    print("\n🎉 TOUS LES TESTS RÉUSSIS !")
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Erreur: {e}")