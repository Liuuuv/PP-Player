"""
Script de lancement simple pour tester la nouvelle architecture
"""
import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Lancement de Pipi Player (version refactorisée)...")
    from main_new import main
    main()
except Exception as e:
    print(f"Erreur lors du lancement: {e}")
    import traceback
    traceback.print_exc()
    input("Appuyez sur Entrée pour fermer...")