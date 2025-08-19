import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importer depuis le __init__.py du dossier search_tab
from search_tab import *

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

def _load_more_search_results(self):
    """Charge plus de résultats pour la recherche actuelle (avec lazy loading)"""
    if (self.is_loading_more or 
        self.is_searching or
        self.search_cancelled or
        not self.current_search_query):
        return
    
    # Vérifier si on a encore des résultats locaux à afficher
    if self.search_results_count < len(self.all_search_results):
        self.is_loading_more = True
        self.current_search_batch += 1
        
        self.status_bar.config(text=f"Chargement du lot {self.current_search_batch}...")
        
        # Afficher le prochain lot depuis les résultats déjà stockés
        if not self.search_cancelled:
            self._display_batch_results(self.current_search_batch)
        
        self.is_loading_more = False
        
    # Si on a affiché tous les résultats locaux et qu'il y en a potentiellement plus
    elif self.has_more_results and self.total_available_results < self.max_search_results:
        self.is_loading_more = True
        self.status_bar.config(text="Recherche de plus de résultats...")
        
        # Enregistrer le temps de début pour le chargement de plus de résultats
        fetch_start_time = time.time()
        
        # Lancer une recherche pour plus de résultats en arrière-plan
        threading.Thread(
            target=self._fetch_more_results, 
            args=(self.current_search_query, self.total_available_results + self.lazy_load_increment, fetch_start_time),
            daemon=True
        ).start()