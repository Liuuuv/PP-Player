import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier search_tab
from search_tab import *

def _on_youtube_canvas_configure(self, event):
    """Vérifie si on doit charger plus de résultats quand le canvas change"""
    
    # TEMP
    # if self._should_load_more_results():
    #     self._load_more_search_results()

def _update_search_results_ui(self):
    """Met à jour l'apparence des résultats en fonction de l'état de téléchargement"""
    for child in self.results_container.winfo_children():
        if hasattr(child, 'video_data'):
            video = child.video_data
            url = video.get('webpage_url') or f"https://www.youtube.com/watch?v={video.get('id')}"
            
            if url in self.current_downloads:
                # Apparence de téléchargement (rouge)
                child.config(bg='#ff6666')
                child.title_label.config(bg='#ff6666', fg='#cccccc')
                child.duration_label.config(bg='#ff6666', fg='#aaaaaa')
                child.thumbnail_label.config(bg='#ff6666')
            else:
                # Apparence normale
                child.config(bg='#4a4a4a')
                child.title_label.config(bg='#4a4a4a', fg='white')
                child.duration_label.config(bg='#4a4a4a', fg='#cccccc')
                child.thumbnail_label.config(bg='#4a4a4a')