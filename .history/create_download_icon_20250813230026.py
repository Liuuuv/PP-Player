from PIL import Image, ImageDraw

# Créer une icône d'import simple
def create_import_icon():
    # Créer une image 32x32 avec fond transparent
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Couleur blanche pour l'icône
    color = (255, 255, 255, 255)
    
    # Dessiner une flèche vers le bas (import/téléchargement)
    # Ligne verticale
    draw.rectangle([14, 6, 18, 20], fill=color)
    
    # Pointe de la flèche
    points = [(16, 24), (10, 18), (22, 18)]
    draw.polygon(points, fill=color)
    
    # Ligne horizontale en bas (représentant le sol/destination)
    draw.rectangle([8, 26, 24, 28], fill=color)
    
    # Sauvegarder l'icône
    img.save('assets/import.png')
    print("Icône import.png créée avec succès!")

if __name__ == "__main__":
    create_import_icon()