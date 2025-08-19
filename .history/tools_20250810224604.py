from __init__ import *

def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
    style = ttk.Style()
    color_index = 0

    for child in widget.winfo_children():
        # Si c'est un ttk.Frame → appliquer un style
        if isinstance(child, ttk.Frame):
            style_name = f"Debug.TFrame{color_index}"
            style.layout(style_name, style.layout("TFrame"))
            style.configure(style_name, background=colors[color_index % len(colors)])
            child.configure(style=style_name)
            color_index += 1

        # Si c'est un tk.Frame → appliquer une couleur directement
        elif isinstance(child, tk.Frame):
            child.configure(bg=colors[color_index % len(colors)])
            color_index += 1

        # Récursif sur les enfants
        self.colorize_ttk_frames(child, colors)

def save_config(self):
    """Sauvegarde la configuration (volume global et offsets de volume)"""
    try:
        import json
        
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

def _remove_from_playlist_view(self, filepath, playlist_name, event=None):
    """Supprime une musique de la playlist et rafraîchit l'affichage"""
    # Vérifier si Ctrl est enfoncé pour supprimer du dossier downloads
    if event and (event.state & 0x4):  # Ctrl est enfoncé
        # Pour la suppression définitive, on utilise une approche différente
        # car on n'a pas de frame à passer
        try:
            if os.path.exists(filepath):
                # Supprimer le fichier audio
                os.remove(filepath)
                
                # Supprimer la miniature associée si elle existe
                thumbnail_path = os.path.splitext(filepath)[0] + ".jpg"
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                # Supprimer de la playlist
                if filepath in self.main_playlist:
                    self.main_playlist.remove(filepath)
                
                # Supprimer de toutes les playlists
                for pname, playlist_songs in self.playlists.items():
                    if filepath in playlist_songs:
                        playlist_songs.remove(filepath)
                
                # Sauvegarder les playlists
                self.save_playlists()
                
                # Mettre à jour le compteur
                file_services._count_downloaded_files(self)
                self._update_downloads_button()
                
                self.status_bar.config(text=f"Fichier supprimé définitivement: {os.path.basename(filepath)}")
                
                # Rafraîchir l'affichage
                self._display_playlist_songs(playlist_name)
                self._update_playlist_title(playlist_name)
                
                # Rafraîchir la bibliothèque si nécessaire
                self._refresh_downloads_library()
                
        except Exception as e:
            self.status_bar.config(text=f"Erreur suppression fichier: {str(e)}")
            print(f"Erreur suppression fichier: {e}")
    else:
        # Suppression normale de la playlist
        if playlist_name in self.playlists and filepath in self.playlists[playlist_name]:
            self.playlists[playlist_name].remove(filepath)
            self.save_playlists()
            # Rafraîchir l'affichage
            self._display_playlist_songs(playlist_name)
            # Mettre à jour le titre avec le nouveau nombre de chansons
            self._update_playlist_title(playlist_name)
def set_volume(self, val):
    # print(f"Setting volume to {val}")
    self.volume = float(val) / 100
    self._apply_volume()
    # Sauvegarder le volume global seulement si on n'est pas en cours d'initialisation
    if not self.initializing:
        self.save_config()

def set_volume_offset(self, val):
    self.volume_offset = float(val)
    self._apply_volume()
    
    # Sauvegarder l'offset pour la musique en cours seulement si on n'est pas en cours d'initialisation
    if not self.initializing and self.main_playlist and self.current_index < len(self.main_playlist):
        current_file = self.main_playlist[self.current_index]
        self.volume_offsets[current_file] = self.volume_offset
        self.save_config()

def _apply_volume(self):
    """Applique le volume avec l'offset"""
    # Si le volume global est à 0, on n'entend rien peu importe l'offset
    if self.volume == 0:
        final_volume = 0
    else:
        # Calculer le volume final avec l'offset
        final_volume = self.volume + (self.volume_offset / 100)
        # S'assurer que le volume reste entre 0 et 1
        final_volume = max(0, min(1, final_volume))
    
    pygame.mixer.music.set_volume(final_volume)

def _reset_volume_offset(self, event):
    """Remet l'offset de volume à 0 (clic droit)"""
    self.volume_offset_slider.set(0)
    # set_volume_offset sera appelé automatiquement par le slider

def _shuffle_remaining_playlist(self):
    """Mélange aléatoirement la suite de la playlist à partir de la chanson suivante"""
    if len(self.main_playlist) <= self.current_index + 1:
        return  # Pas de chansons suivantes à mélanger
    
    import random
    
    # Sauvegarder la partie avant la chanson courante (incluse)
    before_current = self.main_playlist[:self.current_index + 1]
    
    # Récupérer la partie après la chanson courante
    after_current = self.main_playlist[self.current_index + 1:]
    
    # Mélanger la partie après la chanson courante
    random.shuffle(after_current)
    
    # Reconstituer la playlist
    self.main_playlist = before_current + after_current
    
    # Rafraîchir l'affichage de la playlist
    self._refresh_playlist_display()
    
    self.status_bar.config(text=f"Suite de la playlist mélangée ({len(after_current)} titres)")

def _load_circular_thumbnail(self, label, url):
    """Charge et affiche la miniature circulaire pour les chaînes"""
    try:
        import requests
        from io import BytesIO
        
        # Corriger l'URL si elle commence par //
        if url.startswith('//'):
            url = 'https:' + url
        
        response = requests.get(url, timeout=5)
        img_data = BytesIO(response.content)
        img = Image.open(img_data)
        
        # Créer une image circulaire plus grande
        circular_img = self._create_circular_image(img, (70, 70))
        photo = ImageTk.PhotoImage(circular_img)
        
        self.root.after(0, lambda: self._display_thumbnail(label, photo))
    except Exception as e:
        print(f"Erreur chargement thumbnail circulaire: {e}")

def _display_thumbnail(self, label, photo):
    """Affiche la miniature dans le label"""
    label.configure(image=photo)
    label.image = photo  # Garder une référence




def _load_download_thumbnail(self, filepath, label):
    """Charge la miniature pour un fichier téléchargé"""
    # Chercher une image associée (même nom mais extension image)
    base_name = os.path.splitext(filepath)[0]
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    
    thumbnail_found = False
    for ext in image_extensions:
        thumbnail_path = base_name + ext
        if os.path.exists(thumbnail_path):
            self._load_image_thumbnail(thumbnail_path, label)
            thumbnail_found = True
            break
    
    if not thumbnail_found:
        # Utiliser la miniature MP3 ou une image par défaut
        self._load_mp3_thumbnail(filepath, label)

def _truncate_text_for_display(self, text, max_width_pixels=200, max_lines=1, font_family='TkDefaultFont', font_size=9):
    """Tronque le texte pour l'affichage avec des '...' si nécessaire basé sur la largeur en pixels"""
    import tkinter.font as tkFont
    
    # Nettoyer le nom de fichier (enlever l'extension .mp3)
    if text.lower().endswith('.mp3'):
        text = text[:-4]
    
    # Créer une police pour mesurer le texte avec les paramètres fournis
    font = tkFont.Font(family=font_family, size=font_size)
    
    # Mesurer la largeur du texte complet
    text_width = font.measure(text)
    
    # Si le texte tient dans la largeur disponible, le retourner tel quel
    if text_width <= max_width_pixels:
        return text
    
    # Mesurer la largeur des "..."
    ellipsis_width = font.measure("...")
    available_width = max_width_pixels - ellipsis_width
    
    # Trouver la longueur maximale qui tient dans l'espace disponible
    truncated_text = ""
    for i, char in enumerate(text):
        test_text = text[:i+1]
        if font.measure(test_text) > available_width:
            break
        truncated_text = test_text
    
    # Si on n'a pas pu ajouter au moins un caractère, retourner juste "..."
    if not truncated_text:
        return "..."
    
    return truncated_text + "..."