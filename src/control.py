# Import centralisé depuis __init__.py
from __init__ import *



def play_pause(self):
    if not self.main_playlist:
        return
        
    if pygame.mixer.music.get_busy() and not self.paused:
        pygame.mixer.music.pause()
        self.paused = True
        self.play_button.config(image=self.icons["play"])
        self.play_button.config(text="Play")
        # Arrêter l'animation du titre pendant la pause
        # self._stop_text_animation(self.song_label)
        # Mettre en pause le suivi des statistiques
        self._pause_song_stats_tracking()
    elif self.paused:
        # pygame.mixer.music.unpause()
        # Recharger la musique avant de la jouer à une position spécifique
        if self.main_playlist and self.current_index < len(self.main_playlist):
            song = self.main_playlist[self.current_index]
            pygame.mixer.music.load(song)
        pygame.mixer.music.play(start=self.current_time)
        self.base_position = self.current_time
        self.paused = False
        self.play_button.config(image=self.icons["pause"])
        self.play_button.config(text="Pause")
        # Redémarrer l'animation du titre si nécessaire
        if self.main_playlist and self.current_index < len(self.main_playlist):
            song_path = self.main_playlist[self.current_index]
            song_name = os.path.basename(song_path)
            if song_name.lower().endswith('.mp3'):
                song_name = song_name[:-4]
            # self._start_text_animation(song_name, self.song_label)
            
            # Mettre à jour les métadonnées
            if hasattr(self, 'song_metadata_label'):
                artist, album = self._get_audio_metadata(song_path)
                metadata_text = self._format_artist_album_info(artist, album, song_path)
                self.song_metadata_label.config(text=metadata_text)
        # Reprendre le suivi des statistiques
        self._resume_song_stats_tracking()

    else:
        self.paused = False
        self.play_button.config(image=self.icons["pause"])
        self.play_button.config(text="Pause")
        self.play_track()

def play_selected(self, event):
    if self.playlist_box.curselection():
        self.current_index = self.playlist_box.curselection()[0]
        self.on_song_change()
        self.play_track()
        
        # Déclencher le système de chargement/déchargement intelligent
        if hasattr(self.MainPlaylist, '_trigger_smart_reload_on_song_change'):
            try:
                self.safe_after(50, self.MainPlaylist._trigger_smart_reload_on_song_change)
            except:
                pass

def prev_track(self):
    if not self.main_playlist:
        return
    
    # Nettoyer la queue si la chanson actuelle en faisait partie
    if (hasattr(self, 'queue_items') and 
        self.current_index < len(self.main_playlist) and
        self.current_index in self.queue_items):
        self.queue_items.discard(self.current_index)
    
    self.current_index = (self.current_index - 1) % len(self.main_playlist)
    self.on_song_change()
    self.play_track()
    
    # Déclencher le système de chargement/déchargement intelligent
    if hasattr(self.MainPlaylist, '_trigger_smart_reload_on_song_change'):
        try:
            self.safe_after(50, self.MainPlaylist._trigger_smart_reload_on_song_change)
        except:
            pass
    
    # Auto-scroll si activé, pas de scroll manuel détecté, ET changement automatique
    if (hasattr(self, 'auto_scroll_enabled') and self.auto_scroll_enabled and 
        not getattr(self, 'manual_scroll_detected', False)):
        # Utiliser la fonction intelligente compatible avec le système de chargement
        self.safe_after(100, lambda: self.MainPlaylist.select_current_song_smart(auto_scroll=True))
    


def next_track(self):
    if not self.main_playlist:
        return
    
    # Mode loop chanson : rejouer la même chanson
    if self.loop_mode == 2:
        self.play_track()
        return
    
    # Si on est à la dernière chanson et que le mode loop playlist n'est pas activé
    if self.current_index >= len(self.main_playlist) - 1 and self.loop_mode != 1:
        # Arrêter la lecture
        pygame.mixer.music.stop()
        # self.status_bar.config(text="Fin de la playlist")
        return
    
    # Nettoyer la queue si la chanson actuelle en faisait partie
    if (hasattr(self, 'queue_items') and 
        self.current_index < len(self.main_playlist) and
        self.current_index in self.queue_items):
        self.queue_items.discard(self.current_index)
    
    # Passer à la chanson suivante (avec boucle playlist si mode loop playlist activé)
    self.current_index = (self.current_index + 1) % len(self.main_playlist)
    self.on_song_change()
    self.play_track()
    
    # Déclencher le système de chargement/déchargement intelligent
    if hasattr(self.MainPlaylist, '_trigger_smart_reload_on_song_change'):
        try:
            self.safe_after(50, self.MainPlaylist._trigger_smart_reload_on_song_change)
        except:
            pass
    
    # Auto-scroll si activé, pas de scroll manuel détecté, ET changement automatique
    if (hasattr(self, 'auto_scroll_enabled') and self.auto_scroll_enabled and 
        not getattr(self, 'manual_scroll_detected', False)):
        # Utiliser la fonction intelligente compatible avec le système de chargement
        self.safe_after(100, lambda: self.MainPlaylist.select_current_song_smart(auto_scroll=True))


def on_progress_press(self, val):
    if not self.main_playlist:
        return
    self.user_dragging = True
    self.drag_start_time = self.current_time
    

def on_progress_drag(self, val):
    if not self.main_playlist:
        return
    if self.user_dragging:
        pos = self.progress.get()  # En secondes
        self.current_time_label.config(
            text=time.strftime('%M:%S', time.gmtime(pos))
        )

def on_progress_release(self, event):
    if not self.main_playlist:
        return
    # Récupère la valeur actuelle de la progress bar
    pos = self.progress.get()
    # Change la position de la musique (en secondes)
    try:
        if not self.paused:
            # Recharger la musique avant de la jouer à une position spécifique
            if self.main_playlist and self.current_index < len(self.main_playlist):
                song = self.main_playlist[self.current_index]
                pygame.mixer.music.load(song)
            pygame.mixer.music.play(start=pos)
        self._apply_volume()
        self.current_time = pos
        self.base_position = pos  # Important : mettre à jour la position de base


            
        self.user_dragging = False
        # self.base_position = pos
    except Exception as e:
        self.status_bar.config(text=f"Erreur position: {e}")


def set_position(self, val):
    pos = float(val)
    self.base_position = pos
    if self.user_dragging:
        return
    try:
        # Vérifier si la musique était en pause avant de repositionner
        was_paused = hasattr(self, 'paused') and self.paused
        
        # Recharger la musique avant de la jouer à une position spécifique
        if self.main_playlist and self.current_index < len(self.main_playlist):
            song = self.main_playlist[self.current_index]
            pygame.mixer.music.load(song)
        pygame.mixer.music.play(start=pos)
        
        # Si la musique était en pause, la remettre en pause après repositionnement
        if was_paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_button.config(image=self.icons["play"], text="Play")
        else:
            self.paused = False
            self.play_button.config(image=self.icons["pause"], text="Pause")
    except Exception as e:
        self.status_bar.config(text=f"Erreur set_pos: {e}")

def toggle_loop_mode(self):
    """Cycle entre les 3 modes de boucle : désactivé -> loop playlist -> loop chanson -> désactivé"""
    self.loop_mode = (self.loop_mode + 1) % 3
    
    # Mettre à jour l'apparence du bouton selon le mode
    if self.loop_mode == 0:
        # Désactivé
        self.loop_button.configure(fg_color="#3d3d3d", image=self.icons["loop"])
        self.status_bar.config(text="Mode boucle désactivé")
    elif self.loop_mode == 1:
        # Loop playlist
        self.loop_button.configure(fg_color="#4a8fe7", image=self.icons["loop"])
        self.status_bar.config(text="Mode boucle playlist activé")
    elif self.loop_mode == 2:
        # Loop chanson actuelle
        self.loop_button.configure(fg_color="#4a8fe7", image=self.icons["loop1"])
        self.status_bar.config(text="Mode boucle chanson activé")

def toggle_random_mode(self):
    """Active/désactive le mode aléatoire"""
    self.random_mode = not self.random_mode
    
    # Mettre à jour l'apparence du bouton
    if self.random_mode:
        self.random_button.configure(fg_color="#4a8fe7")
        self.status_bar.config(text="Mode aléatoire activé")
        # Mélanger la suite de la playlist à partir de la chanson suivante
        self._shuffle_remaining_playlist()
    else:
        self.random_button.configure(fg_color="#3d3d3d")
        self.status_bar.config(text="Mode aléatoire désactivé")

def _start_text_animation(self, full_title, frame):
    """Démarre l'animation de défilement du titre si nécessaire"""
    # Arrêter toute animation en cours
    self._stop_text_animation(frame)
    
    # Vérifier si le titre est tronqué
    # truncated_title = tools._truncate_text_for_display(self, full_title, max_width_pixels=400, font_family='Helvetica', font_size=12)
    truncated_title = tools._truncate_text_for_display(self, full_title, max_width_pixels=frame.max_width, font_family=self.get_label_font_family(frame), font_size=self.get_label_font_size(frame))

    # Si le titre n'est pas tronqué, pas besoin d'animation
    if not truncated_title.endswith("..."):
        try:
            if frame.winfo_exists():
                frame.config(text=truncated_title)
        except tk.TclError:
            # Label détruit, ignorer
            pass
        return
    
    # Initialiser les variables d'animation
    # self.title_full_text = full_title
    # self.title_scroll_position = 0
    # self.title_pause_counter = 60  # Pause initiale plus longue (3 secondes à 20fps)
    # self.title_animation_active = True
    frame.full_text = full_title
    frame.scroll_position = 0
    if not hasattr(frame, 'pause_counter'):
        frame.pause_counter = 60  # Pause initiale plus longue (3 secondes à 20fps)
    frame.animation_active = True
    
    # Afficher le titre tronqué au début
    # try:
    #     if hasattr(self, 'song_label') and self.song_label.winfo_exists():
    #         self.song_label.config(text=truncated_title)
    # except tk.TclError:
    #     # Label détruit, ignorer
    #     pass
    try:
        if frame.winfo_exists():
            frame.config(text=truncated_title)
    except tk.TclError:
        # Label détruit, ignorer
        pass
    
    # Démarrer l'animation
    self._animate_title_step(frame)
    
def _stop_text_animation(self, frame):
    """Arrête l'animation du titre"""
    # if self.title_animation_id:
    #     self.root.after_cancel(self.title_animation_id)
    #     self.title_animation_id = None
    # self.title_animation_active = False
    if frame.animation_id:
        self.root.after_cancel(frame.animation_id)
        frame.animation_id = None
    frame.animation_active = False

def _animate_title_step(self, frame):
    """Une étape de l'animation du titre"""
    # if not self.title_animation_active:
    #     return
    if not frame.animation_active:
        return
    
    # Paramètres d'animation
    # max_width_pixels = 400
    if hasattr(frame, 'pause_cycles'):
        pause_cycles = frame.pause_cycles  # Pause plus longue entre les cycles (4 secondes à 20fps)
    else:
        pause_cycles = 80  # Valeur par défaut

    # Si on est en pause
    if frame.pause_counter > 0:
        frame.pause_counter -= 1
        frame.animation_id = self.root.after(50, lambda: self._animate_title_step(frame))  # 20 FPS pendant la pause
        return
    
    # Calculer le texte visible actuel
    visible_text = self._get_scrolled_title_text(frame.full_text, frame.scroll_position, frame.max_width, font_family=self.get_label_font_family(frame), font_size=self.get_label_font_size(frame))

    # Mettre à jour le label
    try:
        if frame.winfo_exists():
            frame.config(text=visible_text)
        else:
            # Label n'existe plus, arrêter l'animation
            frame.animation_active = False
            return
    except tk.TclError:
        # Label détruit, arrêter l'animation
        frame.animation_active = False
        return
    
    # Avancer la position de défilement
    frame.scroll_position += 1

    # Si on a fait un tour complet, recommencer avec une pause
    if frame.scroll_position >= len(frame.full_text) + 8:  # +8 pour les espaces ajoutés
        frame.scroll_position = 0
        frame.pause_counter = pause_cycles
        # Afficher le titre tronqué normal pendant la pause
        font_size = self.get_label_font_size(frame)
        truncated_title = tools._truncate_text_for_display(self, frame.full_text, max_width_pixels=frame.max_width, font_family=self.get_label_font_family(frame), font_size=font_size)
        frame.config(text=truncated_title)

    # Programmer la prochaine étape
    frame.animation_id = self.root.after(100, lambda: self._animate_title_step(frame))  # 10 FPS pour le défilement

def _reset_text_animation(self, frame):
    """Réinitialise l'animation du texte"""
    self._stop_text_animation(frame)
    frame.scroll_position = 0
    frame.pause_counter = DOWNLOADS_LABEL_ANIMATION_STARTUP
    frame.animation_id = None
    
    truncated_title = tools._truncate_text_for_display(self, frame.full_text, max_width_pixels=frame.max_width, font_family=self.get_label_font_family(frame), font_size=self.get_label_font_size(frame))
    frame.config(text=truncated_title)

def _get_scrolled_title_text(self, full_text, scroll_pos, max_width_pixels, font_family='Helvetica', font_size=12):
    """Génère le texte visible avec défilement à la position donnée"""
    import tkinter.font as tkFont
    
    # Créer la police pour mesurer
    font = tkFont.Font(family=font_family, size=font_size)
    ellipsis_width = font.measure("...")
    available_width = max_width_pixels - ellipsis_width
    
    # Créer le texte étendu pour le défilement circulaire
    # On ajoute plus d'espaces pour créer une transition fluide avec plus d'espace
    extended_text = full_text + "        " + full_text
    
    # S'assurer que scroll_pos ne dépasse pas la longueur du texte étendu
    if scroll_pos >= len(extended_text):
        scroll_pos = 0
    
    # Commencer à partir de la position de défilement
    scrolled_text = extended_text[scroll_pos:]
    
    # Si on n'a plus assez de texte, recommencer depuis le début
    if len(scrolled_text) < 10:  # Seuil minimum pour éviter les fins de texte
        scrolled_text = extended_text
    
    # Trouver la longueur maximale qui tient dans l'espace disponible
    visible_text = ""
    for i, char in enumerate(scrolled_text):
        test_text = scrolled_text[:i+1]
        if font.measure(test_text) > available_width:
            break
        visible_text = test_text
    
    # Si on n'a pas pu ajouter au moins un caractère, retourner juste "..."
    if not visible_text:
        return "..."
    
    return visible_text + "..."
