#!/usr/bin/env python3
"""
Test de la correction avec réorganisation automatique
Vérifie que l'ordre chronologique correct est maintenu avec _reorder_playlist_items
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_reorder_function():
    """Test de la fonction de réorganisation"""
    print("🧪 TEST: Fonction de réorganisation _reorder_playlist_items")
    
    try:
        import tkinter as tk
        
        # Créer une fenêtre de test
        root = tk.Tk()
        root.withdraw()
        
        # Créer un container
        container = tk.Frame(root)
        container.pack()
        
        # Créer des éléments dans le désordre (simuler le problème actuel)
        disorder_indexes = [28, 18, 19, 20, 8, 9, 10, 1, 2, 3, 29, 30]
        items = []
        
        print("📊 Création d'éléments dans le désordre:")
        for song_index in disorder_indexes:
            item = tk.Label(container, text=f"Item {song_index}")
            item.song_index = song_index
            item.pack()
            items.append(item)
            print(f"   Ajout Item {song_index}")
        
        # Afficher l'ordre avant réorganisation
        children = container.winfo_children()
        order_before = [child.song_index for child in children]
        print(f"\n📊 Ordre avant réorganisation: {order_before}")
        
        # Fonction de réorganisation (copie de celle du code)
        def reorder_playlist_items(container):
            # Récupérer tous les enfants avec leur song_index
            children = list(container.winfo_children())
            indexed_children = []
            
            for child in children:
                if hasattr(child, 'song_index'):
                    indexed_children.append((child.song_index, child))
                else:
                    # Enfant sans index, le garder à la fin
                    indexed_children.append((float('inf'), child))
            
            # Trier par song_index
            indexed_children.sort(key=lambda x: x[0])
            
            print(f"📊 Ordre après tri: {[x[0] for x in indexed_children]}")
            
            # Réorganiser les widgets
            for i, (song_index, child) in enumerate(indexed_children):
                # Déplacer chaque widget à sa position correcte
                child.pack_forget()
                if i == 0:
                    # Premier élément
                    child.pack(fill='x', pady=2, padx=5)
                else:
                    # Insérer après l'élément précédent
                    prev_child = indexed_children[i-1][1]
                    child.pack(fill='x', pady=2, padx=5, after=prev_child)
        
        # Appliquer la réorganisation
        print("\n🔄 Application de la réorganisation...")
        reorder_playlist_items(container)
        
        # Vérifier l'ordre après réorganisation
        children = container.winfo_children()
        order_after = [child.song_index for child in children]
        expected_order = sorted(disorder_indexes)
        
        print(f"\n📊 Résultat:")
        print(f"   Ordre obtenu: {order_after}")
        print(f"   Ordre attendu: {expected_order}")
        
        if order_after == expected_order:
            print("✅ La réorganisation fonctionne correctement!")
            result = True
        else:
            print("❌ La réorganisation ne fonctionne pas!")
            result = False
        
        root.destroy()
        return result
        
    except Exception as e:
        print(f"❌ Erreur test réorganisation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pack_after_logic():
    """Test de la logique pack(after=...)"""
    print("\n🧪 TEST: Logique pack(after=...)")
    
    try:
        import tkinter as tk
        
        # Créer une fenêtre de test
        root = tk.Tk()
        root.withdraw()
        
        # Créer un container
        container = tk.Frame(root)
        container.pack()
        
        # Créer des éléments dans l'ordre
        items = []
        for i in [1, 3, 5]:  # Créer 1, 3, 5
            item = tk.Label(container, text=f"Item {i}")
            item.pack()
            items.append(item)
        
        print("📊 État initial:")
        children = container.winfo_children()
        for child in children:
            print(f"   {child.cget('text')}")
        
        # Insérer 2 entre 1 et 3
        print("\n📊 Insertion de Item 2 après Item 1:")
        item2 = tk.Label(container, text="Item 2")
        item2.pack(after=items[0])  # Après Item 1
        
        children = container.winfo_children()
        order = [child.cget('text') for child in children]
        print(f"   Ordre: {order}")
        
        # Insérer 4 entre 3 et 5
        print("\n📊 Insertion de Item 4 après Item 3:")
        item4 = tk.Label(container, text="Item 4")
        item4.pack(after=items[1])  # Après Item 3
        
        children = container.winfo_children()
        order = [child.cget('text') for child in children]
        print(f"   Ordre: {order}")
        
        expected_order = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
        if order == expected_order:
            print("✅ pack(after=...) fonctionne correctement!")
            result = True
        else:
            print("❌ pack(after=...) ne fonctionne pas comme attendu!")
            result = False
        
        root.destroy()
        return result
        
    except Exception as e:
        print(f"❌ Erreur test pack after: {e}")
        return False

def test_scenario_simulation():
    """Simulation du scénario problématique"""
    print("\n🧪 TEST: Simulation du scénario problématique")
    
    try:
        import tkinter as tk
        
        # Créer une fenêtre de test
        root = tk.Tk()
        root.withdraw()
        
        # Créer un container
        container = tk.Frame(root)
        container.pack()
        
        # Fonction de réorganisation
        def reorder_items(container):
            children = list(container.winfo_children())
            indexed_children = [(child.song_index, child) for child in children if hasattr(child, 'song_index')]
            indexed_children.sort(key=lambda x: x[0])
            
            for i, (song_index, child) in enumerate(indexed_children):
                child.pack_forget()
                if i == 0:
                    child.pack(fill='x', pady=2, padx=5)
                else:
                    prev_child = indexed_children[i-1][1]
                    child.pack(fill='x', pady=2, padx=5, after=prev_child)
        
        # Fonction d'ajout d'élément
        def add_item(container, song_index):
            item = tk.Label(container, text=f"Item {song_index}")
            item.song_index = song_index
            item.pack()
            return item
        
        # Scénario : État initial (28 actuelle, 29, 30)
        print("📊 État initial (28, 29, 30):")
        for i in [28, 29, 30]:
            add_item(container, i)
        
        children = container.winfo_children()
        order = [child.song_index for child in children]
        print(f"   Ordre: {order}")
        
        # Premier chargement : 18-27
        print("\n📊 Premier chargement (18-27):")
        for i in range(18, 28):
            add_item(container, i)
        reorder_items(container)
        
        children = container.winfo_children()
        order = [child.song_index for child in children]
        print(f"   Ordre après réorganisation: {order}")
        
        # Deuxième chargement : 8-17
        print("\n📊 Deuxième chargement (8-17):")
        for i in range(8, 18):
            add_item(container, i)
        reorder_items(container)
        
        children = container.winfo_children()
        order = [child.song_index for child in children]
        print(f"   Ordre après réorganisation: {order}")
        
        # Troisième chargement : 1-7
        print("\n📊 Troisième chargement (1-7):")
        for i in range(1, 8):
            add_item(container, i)
        reorder_items(container)
        
        children = container.winfo_children()
        order = [child.song_index for child in children]
        expected_order = list(range(1, 31))  # 1 à 30
        
        print(f"\n📊 Résultat final:")
        print(f"   Ordre obtenu: {order}")
        print(f"   Ordre attendu: {expected_order}")
        
        if order == expected_order:
            print("✅ Le scénario fonctionne correctement!")
            result = True
        else:
            print("❌ Le scénario ne fonctionne pas!")
            result = False
        
        root.destroy()
        return result
        
    except Exception as e:
        print(f"❌ Erreur simulation scénario: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🎯 TEST DE LA CORRECTION AVEC RÉORGANISATION AUTOMATIQUE")
    print("=" * 75)
    
    # Tests
    reorder_ok = test_reorder_function()
    pack_ok = test_pack_after_logic()
    scenario_ok = test_scenario_simulation()
    
    # Résumé
    print("\n" + "=" * 75)
    print("📊 RÉSUMÉ DES TESTS:")
    print(f"   • Fonction de réorganisation: {'✅ OK' if reorder_ok else '❌ ÉCHEC'}")
    print(f"   • Logique pack(after=...): {'✅ OK' if pack_ok else '❌ ÉCHEC'}")
    print(f"   • Simulation scénario: {'✅ OK' if scenario_ok else '❌ ÉCHEC'}")
    
    if all([reorder_ok, pack_ok, scenario_ok]):
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ La correction avec réorganisation automatique fonctionne")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    print("\n📋 NOUVELLE APPROCHE:")
    print("   • Simplification de _add_main_playlist_item_at_position()")
    print("   • Ajout de _reorder_playlist_items() pour réorganiser après chargement")
    print("   • Utilisation de pack(after=prev_child) pour l'ordre séquentiel")
    print("   • Tri automatique basé sur song_index")
    
    print("\n🎮 RÉSULTAT ATTENDU:")
    print("   • AVANT: 18,19,...,27,8,9,...,17,1,2,...,7,28,29,30... (désordre)")
    print("   • APRÈS: 1,2,3,...,7,8,9,...,17,18,19,...,27,28,29,30... (ordre correct)")
    print("   • Réorganisation automatique après chaque chargement vers le haut")

if __name__ == "__main__":
    main()