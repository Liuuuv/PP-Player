"""
Script pour créer l'icône activate_ai.png dans le même style que les autres icônes
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_ai_icon():
    """Crée l'icône activate_ai.png dans le style des autres icônes"""
    
    # Dimensions standard (même que les autres icônes)
    size = 24
    
    # Créer une image avec fond transparent
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleur principale (gris clair comme les autres icônes)
    color = (200, 200, 200, 255)  # Gris clair
    active_color = (74, 143, 231, 255)  # Bleu comme auto_scroll actif
    
    # Dessiner un cerveau stylisé / circuit IA
    # Base du cerveau (forme ovale)
    brain_left = 2
    brain_top = 3
    brain_right = size - 2
    brain_bottom = size - 3
    
    # Contour du cerveau
    draw.ellipse([brain_left, brain_top, brain_right, brain_bottom], 
                outline=color, width=2, fill=None)
    
    # Lignes de circuit à l'intérieur pour représenter l'IA
    # Ligne horizontale centrale
    draw.line([brain_left + 4, size//2, brain_right - 4, size//2], 
              fill=color, width=1)
    
    # Lignes verticales
    draw.line([size//2, brain_top + 4, size//2, brain_bottom - 4], 
              fill=color, width=1)
    
    # Petits cercles aux intersections (neurones)
    center_x, center_y = size//2, size//2
    
    # Cercle central
    draw.ellipse([center_x-1, center_y-1, center_x+1, center_y+1], 
                fill=color)
    
    # Cercles aux extrémités
    draw.ellipse([brain_left + 3, center_y-1, brain_left + 5, center_y+1], 
                fill=color)
    draw.ellipse([brain_right - 5, center_y-1, brain_right - 3, center_y+1], 
                fill=color)
    draw.ellipse([center_x-1, brain_top + 3, center_x+1, brain_top + 5], 
                fill=color)
    draw.ellipse([center_x-1, brain_bottom - 5, center_x+1, brain_bottom - 3], 
                fill=color)
    
    # Sauvegarder l'icône normale
    assets_path = os.path.join(os.path.dirname(__file__), 'assets')
    if not os.path.exists(assets_path):
        os.makedirs(assets_path)
    
    img.save(os.path.join(assets_path, 'activate_ai.png'))
    print("✅ Icône activate_ai.png créée")
    
    # Créer aussi une version active (bleue)
    img_active = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw_active = ImageDraw.Draw(img_active)
    
    # Même dessin mais en bleu
    draw_active.ellipse([brain_left, brain_top, brain_right, brain_bottom], 
                       outline=active_color, width=2, fill=None)
    
    draw_active.line([brain_left + 4, size//2, brain_right - 4, size//2], 
                    fill=active_color, width=1)
    draw_active.line([size//2, brain_top + 4, size//2, brain_bottom - 4], 
                    fill=active_color, width=1)
    
    draw_active.ellipse([center_x-1, center_y-1, center_x+1, center_y+1], 
                       fill=active_color)
    draw_active.ellipse([brain_left + 3, center_y-1, brain_left + 5, center_y+1], 
                       fill=active_color)
    draw_active.ellipse([brain_right - 5, center_y-1, brain_right - 3, center_y+1], 
                       fill=active_color)
    draw_active.ellipse([center_x-1, brain_top + 3, center_x+1, brain_top + 5], 
                       fill=active_color)
    draw_active.ellipse([center_x-1, brain_bottom - 5, center_x+1, brain_bottom - 3], 
                       fill=active_color)
    
    img_active.save(os.path.join(assets_path, 'activate_ai_active.png'))
    print("✅ Icône activate_ai_active.png créée")

if __name__ == "__main__":
    try:
        create_ai_icon()
        print("🎨 Icônes IA créées avec succès!")
    except Exception as e:
        print(f"❌ Erreur création icônes: {e}")
        print("💡 Assurez-vous que Pillow est installé: pip install Pillow")