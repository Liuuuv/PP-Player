"""
Gestionnaire de configuration pour Pipi Player
Extrait de main.py pour améliorer la lisibilité
"""

def load_playlists(self):
    """Charge les playlists depuis le fichier JSON"""
    try:
        import json
        import os
        playlists_file = os.path.join("downloads", "playlists.json")
        
        if os.path.exists(playlists_file):
            with open(playlists_file, 'r', encoding='utf-8') as f:
                loaded_playlists = json.load(f)
            
            # Ajouter les playlists chargées (en gardant la main playlist)
            for name, songs in loaded_playlists.items():
                # Vérifier que les fichiers existent encore
                existing_songs = [song for song in songs if os.path.exists(song)]
                if existing_songs:  # Seulement ajouter si il y a des chansons valides
                    self.playlists[name] = existing_songs
                    
    except Exception as e:
        print(f"Erreur chargement playlists: {e}")

def save_playlists(self):
    """Sauvegarde les playlists dans un fichier JSON"""
    try:
        import json
        import os
        
        # Créer le dossier downloads s'il n'existe pas
        os.makedirs("downloads", exist_ok=True)
        
        # Filtrer les playlists non vides (sauf la main playlist)
        playlists_to_save = {}
        for name, songs in self.playlists.items():
            if songs:  # Seulement sauvegarder les playlists non vides
                playlists_to_save[name] = songs
        
        playlists_file = os.path.join("downloads", "playlists.json")
        with open(playlists_file, 'w', encoding='utf-8') as f:
            json.dump(playlists_to_save, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Erreur sauvegarde playlists: {e}")

def save_config(self):
    """Sauvegarde la configuration (volume global et offsets de volume)"""
    try:
        import json
        import os
        
        # Créer le dossier downloads s'il n'existe pas
        os.makedirs("downloads", exist_ok=True)
        
        config = {
            "global_volume": self.volume,
            "volume_offsets": self.volume_offsets
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Erreur sauvegarde config: {e}")

def load_config(self):
    """Charge la configuration (volume global et offsets de volume)"""
    try:
        import json
        import os
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Charger le volume global
            if "global_volume" in config:
                self.volume = config["global_volume"]
            
            # Charger les offsets de volume
            if "volume_offsets" in config:
                self.volume_offsets = config["volume_offsets"]
                
    except Exception as e:
        print(f"Erreur chargement config: {e}")

def load_icons(self):
    """Charge les icônes depuis le dossier assets"""
    import os
    from PIL import Image, ImageTk
    
    # Dossier des icônes
    assets_dir = "assets"
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Dossier {assets_dir} créé. Ajoutez vos icônes ici.")
        return
    
    # Liste des icônes à charger
    icon_files = {
        'play': 'play.png',
        'pause': 'pause.png',
        'next': 'next.png',
        'prev': 'prev.png',
        'stop': 'stop.png',
        'volume': 'volume.png',
        'random': 'random.png',
        'loop': 'loop.png',
        'loop1': 'loop1.png'
    }
    
    # Charger chaque icône
    for icon_name, filename in icon_files.items():
        icon_path = os.path.join(assets_dir, filename)
        try:
            if os.path.exists(icon_path):
                # Charger et redimensionner l'icône
                img = Image.open(icon_path)
                img = img.resize((20, 20), Image.Resampling.LANCZOS)
                self.icons[icon_name] = ImageTk.PhotoImage(img)
            else:
                # Créer une icône par défaut (texte)
                self.icons[icon_name] = self._create_text_icon(icon_name)
        except Exception as e:
            print(f"Erreur chargement icône {icon_name}: {e}")
            self.icons[icon_name] = self._create_text_icon(icon_name)

def _create_text_icon(self, text):
    """Crée une icône texte par défaut"""
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    
    # Créer une image 20x20
    img = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Texte par défaut selon l'icône
    icon_texts = {
        'play': '▶',
        'pause': '⏸',
        'next': '⏭',
        'prev': '⏮',
        'stop': '⏹',
        'volume': '🔊',
        'random': '🔀',
        'loop': '🔁',
        'loop1': '🔂'
    }
    
    display_text = icon_texts.get(text, text[:2])
    
    try:
        # Essayer d'utiliser une police par défaut
        font = ImageFont.load_default()
        draw.text((2, 2), display_text, fill='white', font=font)
    except:
        # Si ça échoue, utiliser le texte simple
        draw.text((2, 8), display_text, fill='white')
    
    return ImageTk.PhotoImage(img)