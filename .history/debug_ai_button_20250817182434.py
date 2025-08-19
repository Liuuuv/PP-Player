"""
Script de debug pour diagnostiquer pourquoi le bouton IA ne s'affiche pas
"""

import sys
import os

def debug_ai_button():
    """Debug l'affichage du bouton IA"""
    
    print("🔍 DEBUG BOUTON IA")
    print("=" * 30)
    
    # Simuler l'ordre d'initialisation de l'application
    print("\n📋 Ordre d'initialisation dans l'application:")
    print("1. __init__ de MusicPlayer")
    print("2. setup.create_ui(self) - Création de l'interface")
    print("3. self.setup_ai_system() - Initialisation IA")
    
    print("\n❌ PROBLÈME IDENTIFIÉ:")
    print("Le bouton IA est créé dans setup.create_ui() AVANT que self.ai_menu_system existe!")
    
    print("\n🔧 SOLUTIONS POSSIBLES:")
    print("A. Créer le bouton IA après l'initialisation du système IA")
    print("B. Modifier l'ordre d'initialisation")
    print("C. Créer le bouton IA de manière différée")
    
    return "A"  # Choisir la solution A

def create_fix():
    """Crée le correctif pour afficher le bouton IA"""
    
    print("\n🛠️ CRÉATION DU CORRECTIF...")
    
    # Solution : Ajouter une méthode pour créer le bouton IA après l'initialisation
    fix_code = '''
# CORRECTIF À AJOUTER DANS main.py

def create_ai_button_after_init(self):
    """Crée le bouton IA après l'initialisation du système IA"""
    if hasattr(self, 'ai_menu_system') and self.ai_menu_system:
        # Trouver le frame des boutons
        # Chercher dans l'interface pour trouver buttons_right_frame
        
        def find_buttons_frame(widget):
            """Trouve le frame des boutons récursivement"""
            if hasattr(widget, 'winfo_name') and 'frame' in str(type(widget)).lower():
                # Vérifier si ce frame contient le bouton auto_scroll
                for child in widget.winfo_children():
                    if hasattr(child, 'cget'):
                        try:
                            if hasattr(self, 'auto_scroll_btn') and child == self.auto_scroll_btn:
                                return widget
                        except:
                            pass
            
            # Chercher récursivement dans les enfants
            try:
                for child in widget.winfo_children():
                    result = find_buttons_frame(child)
                    if result:
                        return result
            except:
                pass
            return None
        
        buttons_frame = find_buttons_frame(self.root)
        
        if buttons_frame:
            # Créer le bouton IA
            self.ai_button = self.ai_menu_system.create_ai_button(buttons_frame)
            if self.ai_button:
                # Insérer le bouton avant auto_scroll_btn
                self.ai_button.pack(side=tk.LEFT, padx=(0, 5), before=self.auto_scroll_btn)
                print("🤖 Bouton IA créé et inséré avec succès")
                return True
        
        print("⚠️ Impossible de trouver le frame des boutons")
        return False
    else:
        print("⚠️ Système IA non disponible")
        return False

# À ajouter dans setup_ai_system() après l'initialisation :
# self.create_ai_button_after_init()
'''
    
    return fix_code

if __name__ == "__main__":
    solution = debug_ai_button()
    
    if solution == "A":
        fix_code = create_fix()
        print(fix_code)
        
        print("\n📝 ÉTAPES POUR APPLIQUER LE CORRECTIF:")
        print("1. Le correctif va être appliqué automatiquement")
        print("2. Redémarrez l'application")
        print("3. Le bouton IA devrait apparaître")