#!/usr/bin/env python3
"""
Script pour réinitialiser toutes les dates fausses dans les métadonnées YouTube
"""
import os
import json

def reset_youtube_dates():
    """Supprime toutes les dates de publication fausses des métadonnées YouTube"""
    
    metadata_file = os.path.join("downloads", "youtube_urls.json")
    
    if not os.path.exists(metadata_file):
        print("❌ Aucun fichier de métadonnées trouvé")
        return
    
    try:
        print("🔄 Chargement des métadonnées existantes...")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"📊 {len(metadata)} entrées trouvées")
        
        reset_count = 0
        for filename, data in metadata.items():
            if isinstance(data, dict) and 'upload_date' in data:
                # Supprimer la date de publication fausse
                del data['upload_date']
                reset_count += 1
                print(f"   ✅ Date supprimée pour: {filename}")
        
        if reset_count > 0:
            print(f"\n💾 Sauvegarde des métadonnées nettoyées...")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {reset_count} dates réinitialisées avec succès!")
        else:
            print("ℹ️ Aucune date à réinitialiser")
            
    except Exception as e:
        print(f"❌ Erreur lors du reset: {e}")

if __name__ == "__main__":
    print("=== RESET DES DATES YOUTUBE ===")
    reset_youtube_dates()
    print("=== TERMINÉ ===")