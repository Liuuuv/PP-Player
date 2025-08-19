#!/usr/bin/env python3
"""
Script de test pour vérifier l'annulation de recherche
"""

import tkinter as tk
import time
import threading

def test_search_cancellation():
    """Test simple pour vérifier l'annulation de recherche"""
    print("=== Test d'annulation de recherche ===")
    print("1. Lancez le programme principal")
    print("2. Allez dans l'onglet 'Recherche'")
    print("3. Tapez une recherche (ex: 'music')")
    print("4. Pendant que la recherche est en cours, tapez une nouvelle recherche")
    print("5. Vérifiez que la première recherche est annulée et que la nouvelle commence")
    print("6. Vous devriez voir 'Recherche en cours...' dans la barre de statut")
    print("7. Les résultats de la première recherche ne devraient pas apparaître")
    print("\nSi tout fonctionne correctement :")
    print("- Pas d'erreur TclError")
    print("- La première recherche s'arrête")
    print("- La nouvelle recherche commence")
    print("- Les widgets sont correctement nettoyés")

if __name__ == "__main__":
    test_search_cancellation()