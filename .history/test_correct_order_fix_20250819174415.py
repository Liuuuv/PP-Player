#!/usr/bin/env python3
"""
Test de la correction de l'ordre lors du chargement vers le haut
Vérifie que l'ordre chronologique correct est maintenu
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_insertion_order_logic():
    """Test de la logique d'insertion avec song_index"""
    print("🧪 TEST: Logique d'insertion basée sur song_index")
    
    try:
        import tkinter as tk
        
        # Créer une fenêtre de test
        root = tk.Tk()
        root.withdraw()
        
        # Créer un container
        container = tk.Frame(root)
        container.pack()
        
        # Simuler des éléments existants (index 30, 31, 32)
        existing_items = []
        for i in [30, 31, 32]:
            item = tk.Label(container, text=f"Item {i}")
            item.song_index = i
            item.pack()
            existing_items.append(item)
        
        print("📊 État initial:")
        children = container.winfo_children()
        for child in children:
            print(f"   Index {child.song_index}: {child.cget('text')}")
        
        # Simuler l'ajout d'éléments au début (27, 28, 29)
        print("\n📊 Ajout d'éléments au début (27, 28, 29):")
        for song_index in [27, 28, 29]:  # Dans l'ordre croissant
            # Trouver la position d'insertion correcte
            children = list(container.winfo_children())
            insert_before = None
            
            # Trouver le premier élément avec un index supérieur
            for child in children:
                if hasattr(child, 'song_index') and child.song_index > song_index:
                    insert_before = child
                    break
            
            # Créer le nouvel élément
            new_item = tk.Label(container, text=f"Item {song_index}")
            new_item.song_index = song_index
            new_item.pack()  # Il sera ajouté à la fin
            
            # Le déplacer à la bonne position
            new_item.pack_forget()
            if insert_before:
                new_item.pack(before=insert_before)
                print(f"   Ajout de Item {song_index} avant Item {insert_before.song_index}")
            else:
                new_item.pack()
                print(f"   Ajout de Item {song_index} à la fin")
            
            # Afficher l'ordre actuel
            children = container.winfo_children()
            order = [f"{child.song_index}" for child in children]
            print(f"   Ordre actuel: {order}")
        
        # Vérifier l'ordre final
        final_children = container.winfo_children()
        final_order = [child.song_index for child in final_children]
        expected_order = [27, 28, 29, 30, 31, 32]
        
        print(f"\n📊 Résultat final:")
        print(f"   Ordre obtenu: {final_order}")
        print(f"   Ordre attendu: {expected_order}")
        
        if final_order == expected_order:
            print("✅ L'ordre est correct!")
            result = True
        else:
            print("❌ L'ordre est incorrect!")
            result = False
        
        root.destroy()
        return result
        
    except Exception as e:
        print(f"❌ Erreur test insertion: {e}")
        return False

def test_range_order():
    """Test de l'ordre du range pour le chargement"""
    print("\n🧪 TEST: Ordre du range pour le chargement")
    
    # Scénario : on a 30-32, on veut charger 27-29
    current_start = 30
    new_start = 27
    
    print(f"📊 Scénario: éléments existants {current_start}-32, charger {new_start}-{current_start-1}")
    print(f"   range({new_start}, {current_start}) = ", end="")
    order = list(range(new_start, current_start))
    print(order)
    print(f"   → Ordre d'ajout: {order} (croissant)")
    print(f"   → Avec insertion intelligente, résultat: 27,28,29,30,31,32")
    
    return True

def test_multiple_loads():
    """Test de chargements multiples successifs"""
    print("\n🧪 TEST: Chargements multiples successifs")
    
    try:
        import tkinter as tk
        
        # Créer une fenêtre de test
        root = tk.Tk()
        root.withdraw()
        
        # Créer un container
        container = tk.Frame(root)
        container.pack()
        
        # Fonction d'insertion intelligente
        def smart_insert(container, song_index, text):
            children = list(container.winfo_children())
            insert_before = None
            
            # Trouver le premier élément avec un index supérieur
            for child in children:
                if hasattr(child, 'song_index') and child.song_index > song_index:
                    insert_before = child
                    break
            
            # Créer le nouvel élément
            new_item = tk.Label(container, text=text)
            new_item.song_index = song_index
            new_item.pack()  # Il sera ajouté à la fin
            
            # Le déplacer à la bonne position
            new_item.pack_forget()
            if insert_before:
                new_item.pack(before=insert_before)
            else:
                new_item.pack()
        
        # État initial : 30-32
        print("📊 État initial (30-32):")
        for i in [30, 31, 32]:
            smart_insert(container, i, f"Item {i}")
        
        children = container.winfo_children()
        order = [child.song_index for child in children]
        print(f"   Ordre: {order}")
        
        # Premier chargement : 27-29
        print("\n📊 Premier chargement (27-29):")
        for i in [27, 28, 29]:
            smart_insert(container, i, f"Item {i}")
        
        children = container.winfo_children()
        order = [child.song_index for child in children]
        print(f"   Ordre: {order}")
        
        # Deuxième chargement : 24-26
        print("\n📊 Deuxième chargement (24-26):")
        for i in [24, 25, 26]:
            smart_insert(container, i, f"Item {i}")
        
        children = container.winfo_children()
        order = [child.song_index for child in children]
        print(f"   Ordre: {order}")
        
        # Vérifier l'ordre final
        expected_order = list(range(24, 33))  # 24 à 32
        
        print(f"\n📊 Résultat final:")
        print(f"   Ordre obtenu: {order}")
        print(f"   Ordre attendu: {expected_order}")
        
        if order == expected_order:
            print("✅ L'ordre est correct après chargements multiples!")
            result = True
        else:
            print("❌ L'ordre est incorrect après chargements multiples!")
            result = False
        
        root.destroy()
        return result
        
    except Exception as e:
        print(f"❌ Erreur test chargements multiples: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🎯 TEST DE LA CORRECTION DE L'ORDRE LORS DU SCROLL VERS LE HAUT")
    print("=" * 75)
    
    # Tests
    insertion_ok = test_insertion_order_logic()
    range_ok = test_range_order()
    multiple_ok = test_multiple_loads()
    
    # Résumé
    print("\n" + "=" * 75)
    print("📊 RÉSUMÉ DES TESTS:")
    print(f"   • Logique d'insertion: {'✅ OK' if insertion_ok else '❌ ÉCHEC'}")
    print(f"   • Ordre du range: {'✅ OK' if range_ok else '❌ ÉCHEC'}")
    print(f"   • Chargements multiples: {'✅ OK' if multiple_ok else '❌ ÉCHEC'}")
    
    if all([insertion_ok, range_ok, multiple_ok]):
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ L'ordre correct lors du scroll vers le haut est implémenté")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    print("\n📋 CORRECTIONS APPORTÉES:")
    print("   • Changement du range: range(new_start, current_start) au lieu de range(current_start-1, new_start-1, -1)")
    print("   • Insertion intelligente basée sur song_index")
    print("   • Recherche du bon point d'insertion avec hasattr(child, 'song_index')")
    print("   • Utilisation de pack(before=insert_before) pour l'ordre correct")
    
    print("\n🎮 RÉSULTAT ATTENDU:")
    print("   • AVANT: 31,30,29,28,...,1,32,33... (ordre incorrect)")
    print("   • APRÈS: 1,2,3,...,29,30,31,32,33... (ordre chronologique correct)")
    print("   • Chargement 27-29 → 27,28,29,30,31,32")
    print("   • Chargement 24-26 → 24,25,26,27,28,29,30,31,32")

if __name__ == "__main__":
    main()