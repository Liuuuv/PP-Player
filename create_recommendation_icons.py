#!/usr/bin/env python3
"""
Script pour créer les icônes de recommandation temporaires
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(filename, text, color):
    """Crée une icône simple avec du texte"""
    # Créer une image 32x32 avec fond transparent
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Dessiner un cercle de fond
    draw.ellipse([2, 2, 30, 30], fill=color, outline=(255, 255, 255, 255), width=2)
    
    # Essayer d'ajouter du texte (simple)
    try:
        # Utiliser une police par défaut
        font = ImageFont.load_default()
        
        # Calculer la position pour centrer le texte
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (32 - text_width) // 2
        y = (32 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    except:
        # Si le texte ne fonctionne pas, dessiner juste des formes
        if "sparse" in filename:
            # Dessiner des points épars
            draw.ellipse([8, 8, 12, 12], fill=(255, 255, 255, 255))
            draw.ellipse([20, 12, 24, 16], fill=(255, 255, 255, 255))
            draw.ellipse([12, 20, 16, 24], fill=(255, 255, 255, 255))
        elif "add" in filename:
            # Dessiner un plus
            draw.rectangle([14, 8, 18, 24], fill=(255, 255, 255, 255))
            draw.rectangle([8, 14, 24, 18], fill=(255, 255, 255, 255))
        else:
            # Icône de base - dessiner une note de musique simple
            draw.ellipse([10, 20, 18, 28], fill=(255, 255, 255, 255))
            draw.rectangle([17, 8, 19, 22], fill=(255, 255, 255, 255))
    
    return img

def main():
    """Crée les icônes de recommandation"""
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    
    # Créer le dossier assets s'il n'existe pas
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    # Créer les icônes
    icons = [
        ("recommendation.png", "R", (100, 100, 100)),  # Gris pour désactivé
        ("sparse_recommendation.png", "S", (50, 150, 50)),  # Vert pour éparse
        ("add_recommendation.png", "A", (50, 50, 150))  # Bleu pour à la suite
    ]
    
    for filename, text, color in icons:
        filepath = os.path.join(assets_dir, filename)
        icon = create_icon(filename, text, color)
        icon.save(filepath)
        print(f"Icône créée: {filepath}")
    
    print("Toutes les icônes ont été créées avec succès!")

if __name__ == "__main__":
    main()