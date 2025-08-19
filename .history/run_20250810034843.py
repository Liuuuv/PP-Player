#!/usr/bin/env python3
"""
Script de démarrage robuste pour Pipi Player
"""
import sys
import os
import traceback

def setup_environment():
    """Configure l'environnement d'exécution"""
    # Ajouter le répertoire courant au path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Créer les dossiers nécessaires
    required_dirs = ['downloads', 'assets']
    for dir_name in required_dirs:
        dir_path = os.path.join(current_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Dossier créé: {dir_path}")

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    required_modules = [
        'pygame',
        'tkinter',
        'PIL',
        'mutagen',
        'yt_dlp',
        'pydub',
        'numpy'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
            elif module == 'tkinter':
                import tkinter
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Modules manquants:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nInstallez-les avec:")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def main():
    """Point d'entrée principal"""
    print("🎵 Pipi Player - Version Refactorisée")
    print("=" * 50)
    
    try:
        # Configuration de l'environnement
        setup_environment()
        
        # Vérification des dépendances
        if not check_dependencies():
            input("\nAppuyez sur Entrée pour fermer...")
            return
        
        # Import et lancement de l'application
        print("Chargement de l'application...")
        
        from main_new import PipiPlayer
        
        print("Lancement de l'interface...")
        app = PipiPlayer()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Application fermée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        print("\nDétails de l'erreur:")
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()