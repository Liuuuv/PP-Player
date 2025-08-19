"""
Gestion des paramètres et configuration utilisateur
"""
import json
import os
from .constants import CONFIG_FILE, DOWNLOADS_DIR, DEFAULT_VOLUME


class Settings:
    """Gestionnaire des paramètres de l'application"""
    
    def __init__(self):
        self.global_volume = DEFAULT_VOLUME
        self.volume_offsets = {}
        
    def save_config(self):
        """Sauvegarde la configuration (volume global et offsets de volume)"""
        try:
            # Créer le dossier downloads s'il n'existe pas
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            
            config = {
                "global_volume": self.global_volume,
                "volume_offsets": self.volume_offsets
            }
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")
    
    def load_config(self):
        """Charge la configuration (volume global et offsets de volume)"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Charger le volume global
                if "global_volume" in config:
                    self.global_volume = config["global_volume"]
                
                # Charger les offsets de volume
                if "volume_offsets" in config:
                    self.volume_offsets = config["volume_offsets"]
                    
        except Exception as e:
            print(f"Erreur chargement config: {e}")
    
    def get_volume_offset(self, filepath):
        """Récupère l'offset de volume pour un fichier"""
        return self.volume_offsets.get(filepath, 0)
    
    def set_volume_offset(self, filepath, offset):
        """Définit l'offset de volume pour un fichier"""
        self.volume_offsets[filepath] = offset
        self.save_config()