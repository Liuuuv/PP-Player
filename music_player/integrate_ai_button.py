"""
Script d'intégration pour ajouter le bouton IA à l'interface existante
À utiliser pour modifier votre fichier principal
"""

def integrate_ai_button_to_main_app():
    """
    Instructions pour intégrer le bouton IA dans votre application principale
    """
    
    integration_code = '''
# ========== INTÉGRATION DU BOUTON IA ==========
# À ajouter dans votre fichier principal (main.py ou équivalent)

# 1. IMPORTS (à ajouter au début du fichier)
try:
    from ai_menu_system import setup_ai_menu_system
    AI_MENU_AVAILABLE = True
except ImportError:
    print("⚠️ Système de menu IA non disponible")
    AI_MENU_AVAILABLE = False

# 2. DANS __INIT__ DE VOTRE CLASSE PRINCIPALE (après l'initialisation de l'interface)
def __init__(self):
    # ... votre code d'initialisation existant ...
    
    # Initialiser le système de menu IA
    if AI_MENU_AVAILABLE:
        try:
            self.ai_menu_system = setup_ai_menu_system(self)
            print("🤖 Système de menu IA initialisé")
        except Exception as e:
            print(f"⚠️ Erreur initialisation menu IA: {e}")
            self.ai_menu_system = None
    else:
        self.ai_menu_system = None

# 3. MODIFICATION DE LA CRÉATION DES BOUTONS DE CONTRÔLE
# Trouvez où vous créez les boutons comme auto_scroll et ajoutez le bouton IA

def create_control_buttons(self, parent_frame):
    """Exemple de création des boutons de contrôle avec le bouton IA"""
    
    # ... vos boutons existants ...
    
    # Bouton IA (à placer à gauche du bouton auto_scroll)
    if self.ai_menu_system:
        self.ai_button = self.ai_menu_system.create_ai_button(parent_frame)
        if self.ai_button:
            self.ai_button.pack(side=tk.LEFT, padx=2)
    
    # Bouton auto_scroll (votre code existant)
    # self.auto_scroll_button = tk.Button(...)
    # self.auto_scroll_button.pack(side=tk.LEFT, padx=2)

# 4. INTÉGRATION AVEC LE SYSTÈME DE RECOMMANDATION EXISTANT
# Si vous avez un système de recommandation, modifiez-le pour utiliser l'IA

def get_recommendations_with_ai(self, video_id):
    """Version améliorée qui utilise l'IA si activée"""
    
    # Obtenir les recommandations normales
    recommendations = self.get_recommendations_for_video(video_id)  # votre méthode existante
    
    # Si l'IA est activée pour les recommandations personnalisées
    if (self.ai_menu_system and 
        self.ai_menu_system.is_recommendations_enabled() and 
        recommendations):
        
        try:
            # Utiliser l'IA pour sélectionner les meilleures recommandations
            # Pour l'instant, on garde l'ordre original mais on pourrait améliorer
            print("🤖 Sélection IA des recommandations activée")
            
            # TODO: Implémenter la sélection IA basée sur les métadonnées
            # des recommandations et les préférences apprises
            
        except Exception as e:
            print(f"⚠️ Erreur sélection IA: {e}")
    
    return recommendations

# 5. INTÉGRATION AVEC LE TRACKING DES ACTIONS UTILISATEUR
# Modifiez vos méthodes existantes pour notifier l'IA

def play_track(self):
    """Version modifiée qui notifie l'IA"""
    
    # Votre code existant
    # ... code de lecture de la chanson ...
    
    # Notifier l'IA si l'apprentissage est activé
    if (self.ai_menu_system and 
        self.ai_menu_system.is_learning_enabled() and
        hasattr(self.ai_menu_system, 'ai_integration_manager')):
        
        try:
            # L'intégration IA se fait automatiquement via ai_integration.py
            # Pas besoin de code supplémentaire ici
            pass
        except Exception as e:
            print(f"⚠️ Erreur notification IA: {e}")

def next_track(self):
    """Version modifiée qui détecte les skips pour l'IA"""
    
    # Votre code existant
    # ... code de passage à la chanson suivante ...
    
    # L'IA détecte automatiquement les skips via l'intégration
    # Pas besoin de code supplémentaire

# 6. MÉTHODES UTILITAIRES POUR L'IA (optionnel)

def show_ai_status(self):
    """Affiche le statut de l'IA dans la barre de statut"""
    if self.ai_menu_system:
        learning = "✅" if self.ai_menu_system.is_learning_enabled() else "❌"
        recommendations = "✅" if self.ai_menu_system.is_recommendations_enabled() else "❌"
        
        status_text = f"IA: Learning {learning} | Recommendations {recommendations}"
        self.status_bar.config(text=status_text)
    else:
        self.status_bar.config(text="IA non disponible")

# 7. RACCOURCIS CLAVIER POUR L'IA (optionnel)

def setup_ai_keyboard_shortcuts(self):
    """Configure les raccourcis clavier pour l'IA"""
    if self.ai_menu_system:
        # Ctrl+Alt+A pour ouvrir le menu IA
        self.root.bind('<Control-Alt-a>', lambda e: self.ai_menu_system.toggle_ai_menu())
        
        # Ctrl+Alt+S pour afficher le statut IA
        self.root.bind('<Control-Alt-s>', lambda e: self.show_ai_status())

# ========== FIN DE L'INTÉGRATION ==========
'''
    
    return integration_code

def create_integration_example():
    """Crée un exemple d'intégration complète"""
    
    example_code = '''
# EXEMPLE COMPLET D'INTÉGRATION DANS VOTRE CLASSE PRINCIPALE

import tkinter as tk
from tkinter import ttk
# ... vos autres imports ...

# Import IA
try:
    from ai_menu_system import setup_ai_menu_system
    AI_MENU_AVAILABLE = True
except ImportError:
    AI_MENU_AVAILABLE = False

class YourMusicPlayer:
    def __init__(self):
        # ... votre initialisation existante ...
        
        # Créer l'interface
        self.create_interface()
        
        # Initialiser l'IA à la fin
        self.setup_ai_system()
    
    def create_interface(self):
        """Crée l'interface utilisateur"""
        # ... votre code d'interface existant ...
        
        # Frame pour les boutons de contrôle
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(...)
        
        # Créer les boutons de contrôle
        self.create_control_buttons()
    
    def create_control_buttons(self):
        """Crée les boutons de contrôle incluant le bouton IA"""
        
        # Bouton IA (NOUVEAU - à placer avant auto_scroll)
        if hasattr(self, 'ai_menu_system') and self.ai_menu_system:
            self.ai_button = self.ai_menu_system.create_ai_button(self.control_frame)
            if self.ai_button:
                self.ai_button.pack(side=tk.LEFT, padx=2)
        
        # Vos boutons existants (auto_scroll, etc.)
        # self.auto_scroll_button = tk.Button(...)
        # self.auto_scroll_button.pack(side=tk.LEFT, padx=2)
    
    def setup_ai_system(self):
        """Configure le système d'IA"""
        if AI_MENU_AVAILABLE:
            try:
                self.ai_menu_system = setup_ai_menu_system(self)
                
                # Recréer les boutons pour inclure le bouton IA
                if hasattr(self, 'control_frame'):
                    # Détruire les boutons existants
                    for widget in self.control_frame.winfo_children():
                        widget.destroy()
                    
                    # Recréer avec le bouton IA
                    self.create_control_buttons()
                
                print("🤖 Système IA configuré avec succès")
                
            except Exception as e:
                print(f"⚠️ Erreur configuration IA: {e}")
                self.ai_menu_system = None
        else:
            self.ai_menu_system = None
    
    # ... le reste de vos méthodes existantes ...
'''
    
    return example_code

def find_integration_points():
    """Aide à trouver les points d'intégration dans le code existant"""
    
    points = '''
# POINTS D'INTÉGRATION À CHERCHER DANS VOTRE CODE

1. CRÉATION DES BOUTONS DE CONTRÔLE
   Cherchez des lignes comme :
   - tk.Button(..., image=self.icons["auto_scroll"], ...)
   - self.auto_scroll_button = tk.Button(...)
   - Boutons dans un Frame de contrôle
   
   → Ajoutez le bouton IA AVANT le bouton auto_scroll

2. INITIALISATION DE L'INTERFACE
   Cherchez :
   - def __init__(self):
   - self.create_interface()
   - self.setup_ui()
   
   → Ajoutez self.setup_ai_system() à la fin

3. SYSTÈME DE RECOMMANDATION EXISTANT
   Cherchez :
   - RecommendationSystem
   - get_recommendations
   - filter_new_recommendations
   
   → Modifiez pour utiliser l'IA si activée

4. MÉTHODES DE LECTURE
   Cherchez :
   - def play_track(self):
   - def next_track(self):
   - def toggle_like(self):
   
   → L'intégration IA se fait automatiquement

5. CONFIGURATION/SAUVEGARDE
   Cherchez :
   - save_config()
   - load_config()
   - config.json
   
   → La config IA est automatiquement intégrée
'''
    
    return points

if __name__ == "__main__":
    print("🔧 GUIDE D'INTÉGRATION DU BOUTON IA")
    print("=" * 50)
    
    print("\n📋 ÉTAPES D'INTÉGRATION:")
    print("1. Copiez les fichiers IA dans votre projet")
    print("2. Ajoutez les imports dans votre fichier principal")
    print("3. Modifiez la création des boutons de contrôle")
    print("4. Initialisez le système IA")
    print("5. Testez le bouton et le menu")
    
    print("\n🔍 POINTS D'INTÉGRATION:")
    print(find_integration_points())
    
    print("\n💻 CODE D'INTÉGRATION:")
    print(integrate_ai_button_to_main_app())
    
    print("\n📝 EXEMPLE COMPLET:")
    print(create_integration_example())
    
    print("\n✅ FICHIERS NÉCESSAIRES:")
    print("- ai_recommendation_system.py")
    print("- ai_integration.py") 
    print("- ai_menu_system.py")
    print("- setup_ai.py")
    print("- assets/activate_ai.png")
    print("- assets/activate_ai_active.png")
    
    print("\n🎯 RÉSULTAT ATTENDU:")
    print("- Bouton IA à gauche du bouton auto_scroll")
    print("- Clic ouvre un menu avec 2 options cochables")
    print("- Bouton devient bleu si au moins une option cochée")
    print("- Option 'Learning' active l'apprentissage IA")
    print("- Option 'Recommendations' utilise l'IA pour choisir")
    print("- Bouton 'Reset datas' remet l'IA à zéro")