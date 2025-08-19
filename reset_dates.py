#!/usr/bin/env python3
"""
Script pour réinitialiser toutes les dates de publication YouTube stockées
car elles sont potentiellement incorrectes.
"""
import sys
import os
import json
import shutil

def reset_youtube_dates():
    """Supprime toutes les dates de publication YouTube stockées"""
    
    metadata_file = os.path.join("downloads", "youtube_urls.json")
    
    if not os.path.exists(metadata_file):
        print("❌ Aucun fichier de métadonnées trouvé")
        return
    
    # Créer une sauvegarde
    backup_file = metadata_file + ".backup"
    try:
        shutil.copy2(metadata_file, backup_file)
        print(f"✅ Sauvegarde créée: {backup_file}")
    except Exception as e:
        print(f"⚠️ Impossible de créer la sauvegarde: {e}")
    
    try:
        # Charger les métadonnées existantes
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"📋 {len(metadata)} entrées trouvées")
        
        # Compter les modifications
        modified_count = 0
        removed_dates_count = 0
        
        # Réinitialiser les données
        for filename, data in metadata.items():
            if isinstance(data, dict):
                if 'upload_date' in data:
                    del data['upload_date']
                    removed_dates_count += 1
                    modified_count += 1
                    print(f"   📅 Date supprimée pour: {filename}")
            elif isinstance(data, str):
                # Ancien format (juste l'URL), pas de date à supprimer
                print(f"   ℹ️ Ancien format conservé pour: {filename}")
        
        # Sauvegarder les modifications
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Réinitialisation terminée:")
        print(f"   📊 {len(metadata)} entrées totales")
        print(f"   🗑️ {removed_dates_count} dates supprimées")
        print(f"   ✏️ {modified_count} entrées modifiées")
        print(f"\n💡 Les dates seront récupérées lors du prochain téléchargement")
        print(f"💡 Pour les fichiers existants, seule la date de modification sera affichée")
        
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {e}")
        # Restaurer la sauvegarde en cas d'erreur
        if os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, metadata_file)
                print(f"🔄 Sauvegarde restaurée")
            except:
                pass

def clean_all_metadata():
    """Supprime complètement toutes les métadonnées YouTube (option nucléaire)"""
    
    metadata_file = os.path.join("downloads", "youtube_urls.json")
    
    if not os.path.exists(metadata_file):
        print("❌ Aucun fichier de métadonnées trouvé")
        return
    
    # Créer une sauvegarde
    backup_file = metadata_file + ".full_backup"
    try:
        shutil.copy2(metadata_file, backup_file)
        print(f"✅ Sauvegarde complète créée: {backup_file}")
    except Exception as e:
        print(f"⚠️ Impossible de créer la sauvegarde: {e}")
        return
    
    try:
        # Supprimer le fichier
        os.remove(metadata_file)
        print("🗑️ Toutes les métadonnées YouTube supprimées")
        print("💡 Un nouveau fichier sera créé lors du prochain téléchargement")
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")

if __name__ == "__main__":
    print("=== RÉINITIALISATION DES DATES YOUTUBE ===\n")
    
    # Vérifier que le dossier downloads existe
    if not os.path.exists("downloads"):
        print("❌ Le dossier 'downloads' n'existe pas")
        exit(1)
    
    print("Que voulez-vous faire ?")
    print("1. Supprimer seulement les dates de publication (recommandé)")
    print("2. Supprimer toutes les métadonnées YouTube (option nucléaire)")
    print("3. Annuler")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Suppression des dates de publication...")
        reset_youtube_dates()
    elif choice == "2":
        print("\n⚠️ ATTENTION: Cette action supprimera TOUTES les métadonnées YouTube!")
        confirm = input("Êtes-vous sûr ? (tapez 'OUI' pour confirmer): ").strip()
        if confirm.upper() == "OUI":
            print("\n🚀 Suppression complète...")
            clean_all_metadata()
        else:
            print("❌ Annulé")
    else:
        print("❌ Annulé")
    
    print("\n=== FIN ===")