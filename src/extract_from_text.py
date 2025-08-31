import re
from urllib.parse import urlparse, parse_qs


def clean_youtube_url(url):
    """Nettoie une URL YouTube pour ne garder que le bon lien de la vidéo"""
    if not url:
        return url
    
    try:
        # Parser l'URL
        parsed = urlparse(url)
        
        # Vérifier si c'est une URL YouTube
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            # Extraire l'ID de la vidéo
            if 'youtu.be' in parsed.netloc:
                # Format court: https://youtu.be/VIDEO_ID
                video_id = parsed.path.lstrip('/')
            else:
                # Format long: https://www.youtube.com/watch?v=VIDEO_ID
                query_params = parse_qs(parsed.query)
                video_id = query_params.get('v', [None])[0]
            
            if video_id:
                # Retourner l'URL nettoyée
                return f"https://www.youtube.com/watch?v={video_id}"
        
        # Si ce n'est pas YouTube, retourner l'URL originale
        return url
    except Exception:
        # En cas d'erreur, retourner l'URL originale
        return url

def extract_youtube_links_from_text(text_file_path, compress_method=""):
    """
    Fonction utilitaire pour extraire les liens YouTube depuis un fichier text
    
    Args:
        text_file_path: Chemin vers le fichier text (json ou txt)
        
    Returns:
        list: Liste des liens YouTube uniques trouvés
    """
    try:
        
        # Lire le fichier par chunks pour gérer les gros fichiers
        # chunk_size = 1024 * 1024  # 1MB chunks
        chunk_size = 1024 * 1024 - 1  # 1MB chunks (un poil moins pour que ça soit divisible par 11)
        links_found = []
        
        with open(text_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                
                # Extraire tous les blocs de 11 caractères
                for i in range(0, len(chunk), 11):
                    id = chunk[i:i+11]
                    links_found.append(id)
        
        # Nettoyer et retourner les liens uniques
        links_found = [f"https://www.youtube.com/watch?v={id}" for id in links_found]
        # unique_links = list(set(links_found))
        return links_found
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des liens: {str(e)}")
        return []