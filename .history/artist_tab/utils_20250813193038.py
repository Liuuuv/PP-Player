# Utilitaires internes pour le module artist_tab
# Ce fichier contient les fonctions utilitaires nécessaires pour rendre le module complètement indépendant

# Import centralisé depuis __init__.py
from __init__ import *

def truncate_text_for_display(music_player, text, max_width_pixels=200, font_size=8):
    """
    Tronque intelligemment un texte selon la largeur en pixels disponible
    Version interne pour le module artist_tab
    """
    try:
        if not text:
            return ""
        
        # Créer une font temporaire pour mesurer le texte
        temp_font = ('TkDefaultFont', font_size)
        
        # Créer un widget temporaire pour mesurer le texte
        temp_label = tk.Label(music_player.root, font=temp_font)
        temp_label.configure(text=text)
        temp_label.update_idletasks()
        
        # Mesurer la largeur du texte
        text_width = temp_label.winfo_reqwidth()
        
        # Détruire le widget temporaire
        temp_label.destroy()
        
        # Si le texte tient dans la largeur disponible, le retourner tel quel
        if text_width <= max_width_pixels:
            return text
        
        # Sinon, tronquer progressivement
        max_chars = len(text)
        for i in range(max_chars, 0, -1):
            truncated = text[:i] + "..."
            
            # Mesurer la largeur du texte tronqué
            temp_label = tk.Label(music_player.root, font=temp_font)
            temp_label.configure(text=truncated)
            temp_label.update_idletasks()
            
            truncated_width = temp_label.winfo_reqwidth()
            temp_label.destroy()
            
            if truncated_width <= max_width_pixels:
                return truncated
        
        # Si même un caractère + "..." est trop long, retourner juste "..."
        return "..."
        
    except Exception as e:
        # En cas d'erreur, retourner le texte original ou une version tronquée simple
        if len(text) > 30:
            return text[:27] + "..."
        return text

def format_duration(duration_seconds):
    """
    Formate une durée en secondes au format MM:SS ou HH:MM:SS
    Version interne pour le module artist_tab
    """
    try:
        if not duration_seconds or duration_seconds <= 0:
            return "0:00"
        
        duration_seconds = int(float(duration_seconds))
        
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
            
    except Exception:
        return "0:00"

def format_view_count(view_count):
    """
    Formate un nombre de vues de manière lisible
    Version interne pour le module artist_tab
    """
    try:
        if not view_count:
            return "0 vues"
        
        count = int(view_count)
        
        if count >= 1_000_000_000:
            return f"{count / 1_000_000_000:.1f}B vues"
        elif count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M vues"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K vues"
        else:
            return f"{count} vues"
            
    except Exception:
        return "0 vues"

def format_upload_date(upload_date):
    """
    Formate une date d'upload de manière lisible
    Version interne pour le module artist_tab
    """
    try:
        if not upload_date:
            return ""
        
        # Si c'est déjà une chaîne formatée, la retourner
        if isinstance(upload_date, str) and len(upload_date) == 8:
            # Format YYYYMMDD
            year = upload_date[:4]
            month = upload_date[4:6]
            day = upload_date[6:8]
            return f"{day}/{month}/{year}"
        
        return str(upload_date)
        
    except Exception:
        return ""

def safe_get_nested_value(data, *keys, default=None):
    """
    Récupère une valeur imbriquée dans un dictionnaire de manière sécurisée
    Version interne pour le module artist_tab
    """
    try:
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    except Exception:
        return default

def clean_artist_name_for_url(artist_name):
    """
    Nettoie un nom d'artiste pour l'utiliser dans une URL
    Version interne pour le module artist_tab
    """
    try:
        if not artist_name:
            return ""
        
        # Supprimer les espaces et caractères spéciaux
        import re
        import urllib.parse
        
        # Nettoyer le nom
        clean_name = artist_name.replace(' ', '').replace('　', '').replace('/', '')
        # Supprimer les caractères non-alphanumériques sauf les tirets et underscores
        clean_name = re.sub(r'[^\w\-_]', '', clean_name)
        # Encoder pour l'URL
        return urllib.parse.quote(clean_name, safe='')
        
    except Exception:
        return artist_name.replace(' ', '+')

def extract_channel_id_from_url(url):
    """
    Extrait l'ID de chaîne depuis une URL YouTube
    Version interne pour le module artist_tab
    """
    try:
        if not url:
            return None
        
        import re
        
        # Chercher le pattern channel/ID
        channel_match = re.search(r'channel/([^/]+)', url)
        if channel_match:
            return channel_match.group(1)
        
        # Chercher le pattern @username
        username_match = re.search(r'@([^/]+)', url)
        if username_match:
            return username_match.group(1)
        
        return None
        
    except Exception:
        return None