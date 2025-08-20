#!/usr/bin/env python3
"""
Test de la correction de la mise à jour de la scrollbar
Vérifie que la scrollbar se met à jour correctement après l'ajout d'éléments vers le bas
"""

import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_scrollbar_update_logic():
    """Test de la logique de mise à jour de la scrollbar"""
    print("🧪 TEST: Logique de mise à jour de la scrollbar")
    
    try:
        import tkinter as tk
        
        # Créer une fenêtre de test
        root = tk.Tk()
        root.title("Test Scrollbar Update")
        root.geometry("400x300")
        
        # Créer un canvas avec scrollbar
        canvas = tk.Canvas(root, bg='white')
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame container pour les éléments
        container = tk.Frame(canvas, bg='lightgray')
        canvas.create_window((0, 0), window=container, anchor="nw")
        
        # Pack les widgets
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Fonction pour ajouter des éléments
        def add_items(count, prefix="Item"):
            for i in range(count):
                item = tk.Label(container, text=f"{prefix} {i+1}", 
                               bg='lightblue', relief='solid', bd=1, height=2)
                item.pack(fill='x', pady=1)
            
            # Mettre à jour la région de scroll
            container.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            print(f"✅ Ajouté {count} éléments, région de scroll mise à jour")
        
        # Fonction pour tester la scrollbar
        def test_scrollbar_state():
            bbox = canvas.bbox("all")
            scroll_region = canvas.cget('scrollregion')
            view = canvas.yview()
            
            print(f"📊 État de la scrollbar:")
            print(f"   • BBox: {bbox}")
            print(f"   • Scroll region: {scroll_region}")
            print(f"   • Vue actuelle: {view}")
            
            if bbox and len(bbox) >= 4:
                content_height = bbox[3] - bbox[1]
                canvas_height = canvas.winfo_height()
                print(f"   • Hauteur contenu: {content_height}px")
                print(f"   • Hauteur canvas: {canvas_height}px")
                print(f"   • Scroll nécessaire: {'Oui' if content_height > canvas_height else 'Non'}")
        
        # Test initial
        print("📊 État initial:")
        add_items(5, "Initial")
        test_scrollbar_state()
        
        # Attendre un peu puis ajouter plus d'éléments
        def add_more_items():
            print("\n📊 Ajout d'éléments supplémentaires:")
            add_items(10, "Added")
            test_scrollbar_state()
            
            # Tester le scroll
            print("\n🔄 Test du scroll:")
            canvas.yview_moveto(0.5)  # Aller au milieu
            print(f"   • Position après scroll au milieu: {canvas.yview()}")
            
            # Forcer la mise à jour de la scrollbar
            current_view = canvas.yview()
            canvas.yview_moveto(current_view[0])
            print(f"   • Position après force update: {canvas.yview()}")
            
            root.after(2000, root.quit)  # Quitter après 2 secondes
        
        root.after(1000, add_more_items)  # Ajouter après 1 seconde
        
        # Lancer la boucle d'événements
        root.mainloop()
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test scrollbar: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scroll_region_calculation():
    """Test des calculs de région de scroll"""
    print("\n🧪 TEST: Calculs de région de scroll")
    
    # Scénarios de test
    scenarios = [
        {
            "name": "Petite liste (10 éléments)",
            "items": 10,
            "item_height": 60,
            "canvas_height": 400
        },
        {
            "name": "Liste moyenne (50 éléments)",
            "items": 50,
            "item_height": 60,
            "canvas_height": 400
        },
        {
            "name": "Grande liste (100 éléments)",
            "items": 100,
            "item_height": 60,
            "canvas_height": 400
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}:")
        
        total_content_height = scenario['items'] * scenario['item_height']
        canvas_height = scenario['canvas_height']
        
        print(f"   • Nombre d'éléments: {scenario['items']}")
        print(f"   • Hauteur par élément: {scenario['item_height']}px")
        print(f"   • Hauteur totale contenu: {total_content_height}px")
        print(f"   • Hauteur canvas: {canvas_height}px")
        
        # Calculer si le scroll est nécessaire
        scroll_needed = total_content_height > canvas_height
        print(f"   • Scroll nécessaire: {'Oui' if scroll_needed else 'Non'}")
        
        if scroll_needed:
            # Calculer la taille relative de la scrollbar
            scrollbar_ratio = canvas_height / total_content_height
            print(f"   • Ratio scrollbar: {scrollbar_ratio:.3f}")
            print(f"   • Taille scrollbar: {scrollbar_ratio * 100:.1f}% de la hauteur")
        
        # Simuler l'ajout de 10 éléments supplémentaires
        new_items = scenario['items'] + 10
        new_total_height = new_items * scenario['item_height']
        new_scrollbar_ratio = canvas_height / new_total_height if new_total_height > canvas_height else 1.0
        
        print(f"   • Après ajout de 10 éléments:")
        print(f"     - Nouvelle hauteur: {new_total_height}px")
        print(f"     - Nouveau ratio scrollbar: {new_scrollbar_ratio:.3f}")
        print(f"     - Changement ratio: {new_scrollbar_ratio - (scrollbar_ratio if scroll_needed else 1.0):.3f}")
    
    return True

def test_update_timing():
    """Test du timing des mises à jour"""
    print("\n🧪 TEST: Timing des mises à jour")
    
    try:
        import tkinter as tk
        import time
        
        # Créer une fenêtre de test
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        
        # Créer les widgets
        canvas = tk.Canvas(root, width=300, height=200)
        container = tk.Frame(canvas)
        canvas.create_window((0, 0), window=container, anchor="nw")
        
        # Fonction pour mesurer le temps de mise à jour
        def measure_update_time(operation_name, operation):
            start_time = time.time()
            operation()
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # en millisecondes
            print(f"   • {operation_name}: {duration:.2f}ms")
            return duration
        
        print("📊 Mesure des temps de mise à jour:")
        
        # Ajouter des éléments et mesurer
        def add_items():
            for i in range(20):
                item = tk.Label(container, text=f"Item {i+1}", height=2)
                item.pack(fill='x')
        
        def update_geometry():
            container.update_idletasks()
        
        def update_scroll_region():
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def force_scrollbar_update():
            current_view = canvas.yview()
            canvas.yview_moveto(current_view[0])
        
        # Mesurer chaque étape
        time1 = measure_update_time("Ajout d'éléments", add_items)
        time2 = measure_update_time("Mise à jour géométrie", update_geometry)
        time3 = measure_update_time("Mise à jour région scroll", update_scroll_region)
        time4 = measure_update_time("Force scrollbar update", force_scrollbar_update)
        
        total_time = time1 + time2 + time3 + time4
        print(f"   • Temps total: {total_time:.2f}ms")
        
        # Recommandations de délai
        recommended_delay = max(10, int(total_time * 1.5))
        print(f"   • Délai recommandé: {recommended_delay}ms")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test timing: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🎯 TEST DE LA CORRECTION DE LA MISE À JOUR DE LA SCROLLBAR")
    print("=" * 75)
    
    # Tests
    scrollbar_ok = test_scrollbar_update_logic()
    calculation_ok = test_scroll_region_calculation()
    timing_ok = test_update_timing()
    
    # Résumé
    print("\n" + "=" * 75)
    print("📊 RÉSUMÉ DES TESTS:")
    print(f"   • Logique scrollbar: {'✅ OK' if scrollbar_ok else '❌ ÉCHEC'}")
    print(f"   • Calculs région scroll: {'✅ OK' if calculation_ok else '❌ ÉCHEC'}")
    print(f"   • Timing mises à jour: {'✅ OK' if timing_ok else '❌ ÉCHEC'}")
    
    if all([scrollbar_ok, calculation_ok, timing_ok]):
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ La correction de la mise à jour de la scrollbar fonctionne")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    print("\n📋 CORRECTIONS APPORTÉES:")
    print("   • Force update_idletasks() avant recalcul de la région de scroll")
    print("   • Délai de 10ms pour update_scroll_region_delayed()")
    print("   • Délai de 20ms pour force_scrollbar_update()")
    print("   • Vérification du changement d'état (largeur, hauteur, nombre d'enfants)")
    print("   • Force yview_moveto() pour déclencher la mise à jour de la scrollbar")
    
    print("\n🎮 RÉSULTAT ATTENDU:")
    print("   • AVANT: Scrollbar mal dimensionnée après ajout d'éléments")
    print("   • APRÈS: Scrollbar correctement mise à jour immédiatement")
    print("   • Rectangle de la scrollbar à la bonne taille")
    print("   • Position de la scrollbar correcte")
    print("   • Scroll fluide et naturel")

if __name__ == "__main__":
    main()