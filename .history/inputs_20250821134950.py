from __init__ import *
import download_manager
from ui_menus import _handle_pending_file_moves, _handle_pending_file_deletions
import extract_from_html
import json
import threading
import time
from simple_logger import get_logger
from simple_logs_viewer import SimpleLogsViewer
from urllib.parse import urlparse, parse_qs

def clean_youtube_url(url):
    """Nettoie une URL YouTube pour ne garder que l'ID de la vidéo"""
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

def on_escape_pressed(self, event):
    """Gère l'appui sur la touche Échap"""
    # Priorité 0: Si on est dans une playlist/sortie ouverte, revenir à la liste
    if hasattr(self, 'artist_mode') and self.artist_mode:
        # Vérifier si on est dans une playlist/sortie ouverte (bouton retour visible)
        if hasattr(self, 'artist_tab_back_btn') and self.artist_tab_back_btn and self.artist_tab_back_btn.winfo_exists():
            # Utiliser la fonction intelligente qui détermine l'action selon l'onglet actuel
            if hasattr(self, 'artist_tab_manager'):
                self.artist_tab_manager.smart_back_action()
            else:
                # Fallback: utiliser le bouton retour
                self.artist_tab_back_btn.invoke()
            return "break"
        else:
            # On est dans la vue principale artiste, quitter complètement
            self._return_to_search()
            return "break"
    
    # Vérifier si le focus est sur le champ de recherche de la bibliothèque
    focused_widget = self.root.focus_get()
    if (focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)) and
        hasattr(self, 'library_search_entry') and focused_widget == self.library_search_entry):
        # Si le champ de recherche contient du texte, le vider
        if self.library_search_entry.get().strip():
            self._clear_library_search()
        else:
            # Si le champ est vide, enlever le focus
            self.root.focus_set()
        return "break"
    
    # Vérifier si le focus est sur un autre champ de saisie
    if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
        # Si le focus est sur un champ de saisie, retirer le focus
        self.root.focus_set()
        return "break"
    
    # Priorité 1: Si on a une sélection multiple active, l'annuler
    if hasattr(self, 'selected_items') and self.selected_items:
        self.clear_selection()
        return "break"
    
    # Priorité 2: Vérifier si on est en mode artiste
    if hasattr(self, 'artist_mode') and self.artist_mode:
        # Si on est en mode artiste, retourner à la recherche normale
        self._return_to_search()
        return "break"
    
    # Priorité 3: Vérifier sur quel onglet on se trouve
    current_tab = self.notebook.tab(self.notebook.select(), "text")
    
    if current_tab == "Recherche":
        # Si on est sur l'onglet recherche, effacer la barre de recherche
        self._clear_youtube_search()
    else:
        # Si on n'est pas sur l'onglet recherche, y revenir
        # Trouver l'index de l'onglet recherche
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "Recherche":
                self.notebook.select(i)
                break
    
    # Empêcher la propagation de l'événement
    return "break"

# def _on_youtube_scroll(self, event):
#     """Gère le scroll de la molette dans les résultats YouTube"""
#     # Scroll normal
    
#     self.youtube_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
#     # Vérifier si on doit charger plus de résultats
#     if self._should_load_more_results():
#         self._load_more_search_results()

def on_space_pressed(self, event):
    """Gère l'appui sur la barre d'espace"""
    # Vérifier si le focus n'est pas sur un champ de saisie
    focused_widget = self.root.focus_get()
    if focused_widget and isinstance(focused_widget, (tk.Entry, tk.Text)):
        # Si le focus est sur un champ de saisie, ne pas intercepter la barre d'espace
        return
    
    # Appeler la fonction play_pause (même si le focus est sur une case à cocher)
    self.play_pause()
    
    # Empêcher la propagation de l'événement
    return "break"
def on_closing(self):
    # Mettre à jour les statistiques une dernière fois
    self._update_current_song_stats()
    
    # Arrêter l'animation du titre
    self._stop_text_animation(self.song_label)
    
    # Arrêter la surveillance du dossier downloads
    # if hasattr(self, 'downloads_watcher_active'):
    #     self.downloads_watcher_active = False
    
    # Nettoyer les ressources de l'onglet artiste
    if hasattr(self, 'artist_tab_manager'):
        self.artist_tab_manager.cleanup_resources()
    
    # Sauvegarder l'état des sessions en cours
    try:
        from simple_logger import get_logger
        logger = get_logger(self.downloads_folder)
        if logger.current_session and logger.current_session.get('status') == 'running':
            logger.current_session['status'] = 'interrupted'
            logger.log("INFO", "Application fermée - session interrompue")
            logger.save()
            print("Session en cours sauvegardée pour reprise ultérieure")
    except Exception as e:
        print(f"Erreur sauvegarde session: {e}")
    
    # Sauvegarder la configuration avant de fermer
    self.save_config()
    
    # Sauvegarder le cache des durées
    if hasattr(self, '_save_duration_cache'):
        try:
            self._save_duration_cache()
        except Exception as e:
            print(f"Erreur sauvegarde cache durées: {e}")
    
    # Gérer les déplacements de fichiers différés
    if hasattr(self, 'pending_file_moves'):
        _handle_pending_file_moves(self)
    
    # Gérer les suppressions de fichiers différées
    if hasattr(self, 'pending_file_deletions'):
        _handle_pending_file_deletions(self)
    
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    self.root.destroy()

def _on_mousewheel(self, event, canvas):
        """Gère le défilement avec la molette de souris"""
        # Détecter le scroll manuel sur la playlist pour désactiver l'auto-scroll
        if hasattr(self, 'main_playlist_canvas') and canvas == self.main_playlist_canvas:
            if hasattr(self, 'auto_scroll_enabled') and self.auto_scroll_enabled:
                self.manual_scroll_detected = True
                self.auto_scroll_enabled = False
                self.auto_scroll_btn.config(bg="#4a4a4a", activebackground="#5a5a5a")
                self.status_bar.config(text="Auto-scroll désactivé (scroll manuel détecté)")
        
        # Optimisation: Limiter la fréquence des événements de scroll
        if hasattr(self, '_last_scroll_time'):
            current_time = time.time()
            if current_time - self._last_scroll_time < 0.01:  # 10ms entre les scrolls
                return
            self._last_scroll_time = current_time
        else:
            self._last_scroll_time = time.time()
        
        if event.delta:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            # Pour Linux qui utilise event.num au lieu de event.delta
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        # Vérifier le scroll infini pour la playlist
        if hasattr(self, 'main_playlist_canvas') and canvas == self.main_playlist_canvas:
            if hasattr(self, '_check_infinite_scroll'):
                # Différer légèrement la vérification pour laisser le scroll se terminer
                self.root.after(50, self._check_infinite_scroll)

        ## pour detecter la fin du scroll
        # Si un timer existe déjà, on l'annule
        if self.scroll_timeout:
            self.root.after_cancel(self.scroll_timeout)

        # On redéfinit un timer (200 ms par ex.)
        self.scroll_timeout = self.root.after(200, lambda: self._on_mousewheel_end(canvas))

def _on_mousewheel_end(self, canvas):
    pass
    # print("Fin du scroll détectée")

# Raccourcis clavier globaux (fonctionnent même quand la fenêtre n'a pas le focus)
def on_global_play_pause(self, event):
    """Raccourci global Ctrl+Alt+0 (pavé numérique) pour play/pause"""
    try:
        if hasattr(self, 'play_pause'):
            self.play_pause()
        else:
            pass
    except Exception as e:
        import traceback
        traceback.print_exc()
    return "break"

def on_global_next_track(self, event):
    """Raccourci global Ctrl+Alt+N pour chanson suivante"""
    self.next_track()
    return "break"

def on_global_prev_track(self, event):
    """Raccourci global Ctrl+Alt+B pour chanson précédente"""
    self.prev_track()
    return "break"

def on_global_volume_up(self, event):
    """Raccourci global Ctrl+Alt+Up pour augmenter le volume"""
    # Initialiser les variables si nécessaire
    if not hasattr(self, '_volume_keys_pressed'):
        self._volume_keys_pressed = {'up': False, 'down': False}
    if not hasattr(self, '_volume_repeat_id'):
        self._volume_repeat_id = None
    
    # Augmenter le volume immédiatement
    current_volume = self.volume * 100
    new_volume = min(100, current_volume + 5)
    self.set_volume(new_volume)  # Met à jour le volume interne
    self.volume_slider.set(new_volume)  # Met à jour le slider visuellement
    self.status_bar.config(text=f"Volume: {int(new_volume)}%")
    
    # Marquer la touche comme pressée
    self._volume_keys_pressed['up'] = True
    
    # Annuler la répétition précédente
    if self._volume_repeat_id:
        self.root.after_cancel(self._volume_repeat_id)
    
    # Fonction de répétition
    def repeat_volume_up():
        if self._volume_keys_pressed.get('up', False):
            current_vol = self.volume * 100
            if current_vol < 100:  # Seulement si pas au maximum
                new_vol = min(100, current_vol + 5)
                self.set_volume(new_vol)  # Met à jour le volume interne
                self.volume_slider.set(new_vol)  # Met à jour le slider visuellement
                self.status_bar.config(text=f"Volume: {int(new_vol)}%")
                # Continuer la répétition
                self._volume_repeat_id = self.root.after(150, repeat_volume_up)
    
    # Démarrer la répétition après 400ms
    self._volume_repeat_id = self.root.after(400, repeat_volume_up)
    return "break"

def on_global_volume_down(self, event):
    """Raccourci global Ctrl+Alt+Down pour diminuer le volume"""
    # Initialiser les variables si nécessaire
    if not hasattr(self, '_volume_keys_pressed'):
        self._volume_keys_pressed = {'up': False, 'down': False}
    if not hasattr(self, '_volume_repeat_id'):
        self._volume_repeat_id = None
    
    # Diminuer le volume immédiatement
    current_volume = self.volume * 100
    new_volume = max(0, current_volume - 5)
    self.set_volume(new_volume)  # Met à jour le volume interne
    self.volume_slider.set(new_volume)  # Met à jour le slider visuellement
    self.status_bar.config(text=f"Volume: {int(new_volume)}%")
    
    # Marquer la touche comme pressée
    self._volume_keys_pressed['down'] = True
    
    # Annuler la répétition précédente
    if self._volume_repeat_id:
        self.root.after_cancel(self._volume_repeat_id)
    
    # Fonction de répétition
    def repeat_volume_down():
        if self._volume_keys_pressed.get('down', False):
            current_vol = self.volume * 100
            if current_vol > 0:  # Seulement si pas au minimum
                new_vol = max(0, current_vol - 5)
                self.set_volume(new_vol)  # Met à jour le volume interne
                self.volume_slider.set(new_vol)  # Met à jour le slider visuellement
                self.status_bar.config(text=f"Volume: {int(new_vol)}%")
                # Continuer la répétition
                self._volume_repeat_id = self.root.after(150, repeat_volume_down)
    
    # Démarrer la répétition après 400ms
    self._volume_repeat_id = self.root.after(400, repeat_volume_down)
    return "break"

def on_global_volume_key_release(self, event):
    """Appelé quand les touches de volume sont relâchées"""
    if not hasattr(self, '_volume_keys_pressed'):
        self._volume_keys_pressed = {'up': False, 'down': False}
    
    # Marquer la touche comme relâchée
    if event.keysym == 'Up':
        self._volume_keys_pressed['up'] = False
    elif event.keysym == 'Down':
        self._volume_keys_pressed['down'] = False
    
    # Annuler la répétition
    if hasattr(self, '_volume_repeat_id') and self._volume_repeat_id:
        self.root.after_cancel(self._volume_repeat_id)
        self._volume_repeat_id = None
    
    # Effacer le message de volume après 2 secondes
    if hasattr(self, '_volume_clear_timer'):
        self.root.after_cancel(self._volume_clear_timer)
    self._volume_clear_timer = self.root.after(2000, lambda: self.status_bar.config(text=""))
    return "break"

def show_download_dialog(self):
    """Affiche une boîte de dialogue pour importer des musiques ou playlists"""
    dialog = ImportDialog(self.root, self)
    self.root.wait_window(dialog.dialog)

class ImportDialog:
    def __init__(self, parent, music_player):
        self.music_player = music_player
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Importer des musiques")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg='#2d2d2d')
        self.dialog.resizable(False, False)
        
        # Centrer la fenêtre
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.detected_type = tk.StringVar(value="Détection automatique")
        self.html_file_path = None
        self.max_duration = tk.IntVar(value=600)
        self.is_html_mode = False
        
        # Initialiser le logger simplifié
        self.logger = get_logger(self.music_player.downloads_folder)
        
        self.create_widgets()
        self.setup_drag_drop()
        
        # Vérifier s'il y a des sessions à reprendre
        self.check_resumable_sessions()
        
    def create_widgets(self):
        # Titre
        title_label = tk.Label(
            self.dialog, 
            text="Importer des musiques", 
            font=("Arial", 14, "bold"),
            bg='#2d2d2d', 
            fg='white'
        )
        title_label.pack(pady=10)
        
        # Frame pour la détection automatique
        detection_frame = tk.Frame(self.dialog, bg='#2d2d2d')
        detection_frame.pack(pady=10)
        
        tk.Label(detection_frame, text="Type détecté:", bg='#2d2d2d', fg='white').pack(anchor='w')
        
        self.detection_label = tk.Label(
            detection_frame, 
            textvariable=self.detected_type,
            bg='#2d2d2d', 
            fg='#4a8fe7',
            font=("Arial", 10, "bold")
        )
        self.detection_label.pack(anchor='w', pady=2)
        
        # Frame pour l'URL
        self.url_frame = tk.Frame(self.dialog, bg='#2d2d2d')
        self.url_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(self.url_frame, text="URL YouTube:", bg='#2d2d2d', fg='white').pack(anchor='w')
        
        self.url_entry = tk.Entry(
            self.url_frame, 
            font=("Arial", 10),
            bg='#4a4a4a', 
            fg='white', 
            insertbackground='white'
        )
        self.url_entry.pack(fill='x', pady=5)
        self.url_entry.bind('<KeyRelease>', self.on_url_change)
        
        # Frame pour les paramètres HTML (initialement caché)
        self.html_frame = tk.Frame(self.dialog, bg='#2d2d2d')
        
        tk.Label(self.html_frame, text="Fichier HTML détecté", bg='#2d2d2d', fg='#4a8fe7', font=("Arial", 10, "bold")).pack(anchor='w')
        
        self.html_file_label = tk.Label(
            self.html_frame,
            text="Aucun fichier",
            bg='#2d2d2d',
            fg='white',
            font=("Arial", 9)
        )
        self.html_file_label.pack(anchor='w', pady=2)
        
        # Paramètre max_duration
        duration_frame = tk.Frame(self.html_frame, bg='#2d2d2d')
        duration_frame.pack(fill='x', pady=5)
        
        tk.Label(duration_frame, text="Durée max (s):", bg='#2d2d2d', fg='white').pack(side='left')
        
        self.duration_entry = tk.Entry(
            duration_frame,
            textvariable=self.max_duration,
            font=("Arial", 10),
            bg='#4a4a4a',
            fg='white',
            insertbackground='white',
            width=10
        )
        self.duration_entry.pack(side='left', padx=10)
        
        tk.Label(duration_frame, text="(-1 = pas de limite)", bg='#2d2d2d', fg='#888888', font=("Arial", 8)).pack(side='left', padx=5)
        
        # Paramètre taille des paquets
        batch_frame = tk.Frame(self.html_frame, bg='#2d2d2d')
        batch_frame.pack(fill='x', pady=5)
        
        tk.Label(batch_frame, text="Taille des paquets:", bg='#2d2d2d', fg='white').pack(side='left')
        
        self.batch_size = tk.StringVar(value="10")
        self.batch_entry = tk.Entry(
            batch_frame,
            textvariable=self.batch_size,
            font=("Arial", 10),
            bg='#4a4a4a',
            fg='white',
            insertbackground='white',
            width=10
        )
        self.batch_entry.pack(side='left', padx=10)
        
        tk.Label(batch_frame, text="(nombre de vidéos par paquet)", bg='#2d2d2d', fg='#888888', font=("Arial", 8)).pack(side='left', padx=5)
        
        # Frame pour les boutons
        button_frame = tk.Frame(self.dialog, bg='#2d2d2d')
        button_frame.pack(pady=20)
        
        self.download_btn = tk.Button(
            button_frame,
            text="Importer",
            command=self.start_download,
            bg='#4a8fe7',
            fg='white',
            font=("Arial", 10, "bold"),
            relief='flat',
            padx=20,
            pady=5,
            cursor='hand2'
        )
        self.download_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Annuler",
            command=self.dialog.destroy,
            bg='#666666',
            fg='white',
            font=("Arial", 10),
            relief='flat',
            padx=20,
            pady=5,
            cursor='hand2'
        )
        cancel_btn.pack(side='left', padx=10)
        
        # Zone de statut
        self.status_label = tk.Label(
            self.dialog,
            text="Entrez une URL YouTube ou glissez un fichier HTML",
            bg='#2d2d2d',
            fg=COLOR_TEXT,
            font=("Arial", 9)
        )
        self.status_label.pack(pady=10)
    
    def setup_drag_drop(self):
        """Configure le drag & drop pour les fichiers HTML"""
        # Ajouter un bouton pour sélectionner un fichier HTML
        html_button_frame = tk.Frame(self.dialog, bg='#2d2d2d')
        html_button_frame.pack(pady=5)
        
        self.html_select_btn = tk.Button(
            html_button_frame,
            text="📁 Sélectionner un fichier HTML",
            command=self.select_html_file,
            bg='#4a8fe7',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=3,
            cursor='hand2'
        )
        self.html_select_btn.pack()
        
        # Pour l'instant, on utilise seulement le bouton de sélection
        # Le drag & drop sera ajouté plus tard si nécessaire
        pass
    

    

    def select_html_file(self):
        """Ouvre un dialog pour sélectionner un fichier HTML"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier HTML",
            filetypes=[("Fichiers HTML", "*.html *.htm"), ("Tous les fichiers", "*.*")]
        )
        if file_path and file_path.lower().endswith(('.html', '.htm')):
            self.load_html_file(file_path)
    
    def load_html_file(self, file_path):
        """Charge un fichier HTML et passe en mode HTML"""
        self.html_file_path = file_path
        self.is_html_mode = True
        
        # Masquer le frame URL et afficher le frame HTML
        self.url_frame.pack_forget()
        self.html_frame.pack(pady=10, padx=20, fill='x')
        
        # Mettre à jour l'affichage
        filename = os.path.basename(file_path)
        self.html_file_label.config(text=f"Fichier: {filename}")
        self.detected_type.set("Fichier HTML détecté")
        self.status_label.config(text=f"Fichier HTML chargé: {filename}")
    
    def clean_youtube_url(self, url):
        """Nettoie l'URL YouTube en supprimant music. si présent"""
        if "music.youtube.com" in url:
            url = url.replace("music.youtube.com", "youtube.com")
        return url
    
    def detect_url_type(self, url):
        """Détecte automatiquement si l'URL est une vidéo ou une playlist"""
        if not url.strip():
            return "Entrez une URL"
        
        url = self.clean_youtube_url(url)
        
        if "youtube.com" not in url and "youtu.be" not in url:
            return "URL non supportée"
        
        # Détection de playlist
        if "playlist?list=" in url or "&list=" in url:
            return "Playlist détectée"
        else:
            return "Vidéo détectée"
    
    def on_url_change(self, event):
        """Appelé quand l'URL change pour détecter automatiquement le type"""
        url = self.url_entry.get()
        detected = self.detect_url_type(url)
        self.detected_type.set(detected)
        
    def start_download(self):
        if self.is_html_mode:
            # Mode HTML
            if not self.html_file_path:
                messagebox.showerror("Erreur", "Aucun fichier HTML sélectionné")
                return
            
            max_duration = self.max_duration.get()
            
            # Fermer la boîte de dialogue
            self.dialog.destroy()
            
            # Traiter le fichier HTML
            self._process_html_file(self.html_file_path, max_duration)
        else:
            # Mode URL classique
            url = self.url_entry.get().strip()
            if not url:
                messagebox.showerror("Erreur", "Veuillez entrer une URL")
                return
            
            # Nettoyer l'URL
            url = self.clean_youtube_url(url)
            
            if "youtube.com" not in url and "youtu.be" not in url:
                messagebox.showerror("Erreur", "Veuillez entrer une URL YouTube valide")
                return
            
            # Détecter le type automatiquement
            detected_type = self.detect_url_type(url)
            if "non supportée" in detected_type:
                messagebox.showerror("Erreur", "URL non supportée")
                return
            
            # Fermer la boîte de dialogue
            self.dialog.destroy()
            
            # Utiliser les fonctions existantes de téléchargement
            if "Playlist" in detected_type:
                self._download_playlist_existing(url)
            else:
                self._download_single_existing(url)
    
    def _process_html_file(self, html_file_path, max_duration):
        """Traite un fichier HTML pour extraire et télécharger les vidéos YouTube"""
        def process_in_thread():
            try:
                self.music_player.status_bar.config(text="Extraction des liens YouTube depuis le fichier HTML...")
                
                # Extraire les liens depuis le fichier HTML
                youtube_links = extract_from_html.extract_youtube_links_from_html(html_file_path)
                
                if not youtube_links:
                    self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                        text="Aucun lien YouTube trouvé dans le fichier HTML"))
                    return
                
                print(f"Trouvé {len(youtube_links)} liens YouTube.")
                print("🔄 Mise à jour de la barre de statut...")
                self.music_player.root.after(0, lambda total=len(youtube_links): 
                    self.music_player.status_bar.config(text=f"📋 Trouvé {total} liens YouTube. Préparation du traitement..."))
                
                print("🔄 Récupération de la taille des paquets...")
                # Récupérer la taille des paquets depuis l'interface
                try:
                    batch_size = int(self.batch_size.get())
                    if batch_size <= 0:
                        batch_size = 10
                    print(f"✅ Taille des paquets: {batch_size}")
                except Exception as e:
                    print(f"⚠️ Erreur récupération batch_size: {e}")
                    batch_size = 10
                
                print("🔄 Initialisation du logger...")
                # Démarrer une session de logs (optionnel)
                session_id = None
                try:
                    # Essayer d'initialiser le logger dans un thread séparé avec timeout
                    import threading
                    import queue
                    
                    result_queue = queue.Queue()
                    
                    def init_logger():
                        try:
                            sid = self.logger.start_session(html_file_path, youtube_links)
                            result_queue.put(('success', sid))
                        except Exception as e:
                            result_queue.put(('error', str(e)))
                    
                    # Lancer dans un thread
                    thread = threading.Thread(target=init_logger, daemon=True)
                    thread.start()
                    
                    # Attendre avec timeout
                    try:
                        result_type, result_value = result_queue.get(timeout=2.0)
                        if result_type == 'success':
                            session_id = result_value
                            print(f"✅ Session créée: {session_id}")
                        else:
                            print(f"⚠️ Erreur logger: {result_value}, on continue sans logs")
                    except queue.Empty:
                        print("⚠️ Timeout logger, on continue sans logs")
                        
                except Exception as e:
                    print(f"⚠️ Erreur initialisation logger: {e}, on continue sans logs")
                
                # Configurer le logger seulement s'il est initialisé
                if session_id:
                    try:
                        self.logger.set_total(len(youtube_links))
                        print("✅ Total links défini")
                    except Exception as e:
                        print(f"❌ Erreur set_total_links: {e}")
                    
                    try:
                        # Plus besoin de set_pending_urls dans le système simplifié
                        print("✅ URLs en attente définies")
                    except Exception as e:
                        print(f"❌ Erreur set_pending_urls: {e}")
                else:
                    print("⚠️ Logger non initialisé, pas de logs pour cette session")
                
                print(f"Démarrage du traitement par vagues de {batch_size} liens à la fois...")
                if session_id:
                    self.logger.log("INFO", f"Configuration: {len(youtube_links)} liens, vagues de {batch_size}, durée max: {max_duration}s")
                
                print("🔄 Lancement de la fonction _process_videos_in_waves_sequential...")
                
                # Traitement par vagues : vérifier X liens → télécharger → vérifier X suivants → télécharger...
                self._process_videos_in_waves_sequential(youtube_links, max_duration, batch_size, html_file_path, session_id)
                
                print("✅ Fonction _process_videos_in_waves_sequential lancée")
                
            except Exception as e:
                error_msg = f"Erreur lors du traitement du fichier HTML: {str(e)}"
                print(error_msg)
                self.music_player.root.after(0, lambda: self.music_player.status_bar.config(text=error_msg))
        
        # Lancer le traitement dans un thread
        threading.Thread(target=process_in_thread, daemon=True).start()
    
    def _save_skipped_videos_json(self, skipped_videos, html_file_path):
        """Sauvegarde les vidéos non téléchargées dans un fichier JSON"""
        try:
            # Créer le nom du fichier JSON basé sur le fichier HTML
            base_name = os.path.splitext(os.path.basename(html_file_path))[0]
            json_file_path = os.path.join(
                os.path.dirname(html_file_path),
                f"{base_name}_videos_non_telechargees.json"
            )
            
            # Préparer les données
            data = {
                'source_html': html_file_path,
                'date_creation': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_videos_ignorees': len(skipped_videos),
                'videos': skipped_videos
            }
            
            # Sauvegarder le fichier JSON
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Fichier JSON créé: {json_file_path}")
            self.log("INFO", f"Fichier JSON créé: {json_file_path}")
            self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                text=f"Fichier JSON créé avec {len(skipped_videos)} vidéos non téléchargées"))
            
        except Exception as e:
            print(f"Erreur lors de la création du fichier JSON: {e}")
    
    def _download_single_existing(self, url):
        """Télécharge une seule vidéo en utilisant le gestionnaire centralisé"""
        # Utiliser le gestionnaire centralisé de téléchargements
        download_manager.download_youtube_video(
            self.music_player,
            url,
            callback_on_complete=download_manager.add_to_playlist_after_download
        )
    
    def _download_playlist_existing(self, url):
        """Télécharge une playlist en utilisant les fonctions existantes avec vérification"""
        def extract_and_queue_playlist():
            try:
                self.music_player.status_bar.config(text="Extraction des informations de la playlist...")
                
                # Utiliser yt-dlp pour extraire les informations complètes de la playlist
                ydl_opts = {
                    'extract_flat': False,  # Extraire les informations complètes
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if 'entries' in info:
                        playlist_title = info.get('title', 'Playlist')
                        entries = [entry for entry in info['entries'] if entry is not None]
                        
                        self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                            text=f"Playlist trouvée: {playlist_title} ({len(entries)} vidéos)"
                        ))
                        
                        # Ajouter toutes les vidéos à l'onglet téléchargements
                        for i, entry in enumerate(entries):
                            video_url = entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            # Nettoyer l'URL pour ne garder que l'ID de la vidéo
                            video_url = clean_youtube_url(video_url)
                            video_title = entry.get('title', f'Vidéo {i+1}')
                            
                            # Ajouter à l'onglet téléchargements
                            self.music_player.root.after(0, lambda u=video_url, t=video_title, e=entry: 
                                self.music_player.add_download_to_tab(u, t, e))
                        
                        # Démarrer le téléchargement séquentiel
                        self._download_playlist_sequential(entries)
                        
                    else:
                        self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                            text="Aucune vidéo trouvée dans la playlist"
                        ))
                        
            except Exception as e:
                error_msg = str(e)
                self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                    text=f"Erreur lors de l'extraction de la playlist: {error_msg}"
                ))
        
        # Lancer dans un thread séparé
        thread = threading.Thread(target=extract_and_queue_playlist, daemon=True)
        thread.start()
    
    def _download_playlist_sequential(self, entries):
        """Télécharge les vidéos de la playlist une par une avec vérification"""
        def download_next_video(index=0):
            if index >= len(entries):
                self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                    text="Téléchargement de la playlist terminé"
                ))
                return
            
            entry = entries[index]
            video_url = entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
            # Nettoyer l'URL pour ne garder que l'ID de la vidéo
            video_url = clean_youtube_url(video_url)
            video_title = entry.get('title', f'Vidéo {index+1}')
            
            try:
                # Vérifier si le fichier existe déjà
                existing_file = self.music_player._get_existing_download(video_title)
                
                if existing_file:
                    # Le fichier existe, juste sauvegarder l'URL
                    self.music_player.save_youtube_url_metadata(existing_file, video_url)
                    self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                        text=f"Fichier existant trouvé ({index+1}/{len(entries)}): {video_title}"
                    ))
                    # Marquer comme terminé dans l'onglet téléchargements
                    self.music_player.root.after(0, lambda: self.music_player.update_download_progress(video_url, 100, "Déjà téléchargé"))
                    
                    # Passer à la vidéo suivante après un court délai
                    threading.Timer(0.5, lambda: download_next_video(index + 1)).start()
                else:
                    # Lancer le téléchargement
                    self.music_player.root.after(0, lambda: self.music_player.status_bar.config(
                        text=f"Téléchargement ({index+1}/{len(entries)}): {video_title}"
                    ))
                    
                    # Configurer pour le téléchargement
                    self.music_player.search_list = [entry]
                    
                    # Lancer le téléchargement et passer au suivant quand terminé
                    def download_and_continue():
                        try:
                            self.music_player._download_youtube_thread(video_url, True)
                            # Passer à la vidéo suivante
                            download_next_video(index + 1)
                        except Exception as e:
                            # En cas d'erreur, marquer comme échoué et continuer
                            self.music_player.root.after(0, lambda: self.music_player.download_manager.mark_error(video_url, f"Erreur: {str(e)}"))
                            download_next_video(index + 1)
                    
                    threading.Thread(target=download_and_continue, daemon=True).start()
                    
            except Exception as e:
                # En cas d'erreur, marquer comme échoué et continuer
                self.music_player.root.after(0, lambda: self.music_player.download_manager.mark_error(video_url, f"Erreur: {str(e)}"))
                download_next_video(index + 1)
        
        # Démarrer le téléchargement de la première vidéo
        download_next_video(0)
    
    def _process_videos_in_waves_sequential(self, youtube_links, max_duration, batch_size, html_file_path, session_id):
        """Traite les vidéos par vagues avec vérification groupée puis téléchargement séquentiel"""
        print("🔄 Entrée dans _process_videos_in_waves_sequential")
        
        def process_wave_thread():
            try:
                print(f"🚀 Démarrage du thread de traitement par vagues de {len(youtube_links)} liens")
                if session_id:
                    self.logger.log("INFO", f"Démarrage du traitement par vagues de {len(youtube_links)} liens")
                
                # Initialisation des variables
                all_skipped_videos = []
                total_downloaded = 0
                total_links = len(youtube_links)
                last_status_update = time.time()  # Pour limiter les mises à jour de statut
                
                # Message de démarrage détaillé
                print(f"📊 Configuration: {total_links} liens, vagues de {batch_size}, durée max: {max_duration}s")
                self.music_player.root.after(0, lambda: 
                    self.music_player.status_bar.config(text=f"🚀 Démarrage du traitement de {total_links} liens par vagues de {batch_size}..."))
                
                # Pause pour laisser l'interface se mettre à jour et éviter les conditions de course
                time.sleep(0.5)
                
                print("🔄 Début de la boucle de traitement par vagues...")
                
                # Traiter par vagues : 10 vérifications → téléchargement → 10 vérifications → téléchargement...
                for wave_start in range(0, total_links, batch_size):
                    # Vérifier si la session a été annulée
                    if session_id and self.logger.is_cancelled():
                        print("⏹️ Session annulée par l'utilisateur")
                        self.music_player.root.after(0, lambda: 
                            self.music_player.status_bar.config(text="⏹️ Traitement annulé par l'utilisateur"))
                        return
                    
                    wave_end = min(wave_start + batch_size, total_links)
                    wave_links = youtube_links[wave_start:wave_end]
                    wave_num = (wave_start // batch_size) + 1
                    total_waves = (total_links + batch_size - 1) // batch_size
                    
                    print(f"🔍 Vague {wave_num}/{total_waves} - Vérification des liens {wave_start+1}-{wave_end}")
                    self.music_player.root.after(0, lambda w=wave_num, tw=total_waves, ws=wave_start, we=wave_end: 
                        self.music_player.status_bar.config(
                            text=f"🔍 Vague {w}/{tw} - Vérification des liens {ws+1}-{we}..."))
                    
                    if session_id:
                        self.logger.log("INFO", f"Vague {wave_num}/{total_waves} - Vérification des liens {wave_start+1}-{wave_end}")
                    
                    # Pause très courte pour laisser le temps à l'interface de se mettre à jour
                    time.sleep(0.05)  # Réduit de 0.1 à 0.05
                    
                    # Phase 1 : Vérifier les durées de cette vague (10 liens max)
                    valid_videos_wave = []
                    skipped_videos_wave = []
                    
                    for i, url in enumerate(wave_links):
                        # Vérifier si la session a été annulée ou en pause
                        if session_id and self.logger.is_cancelled():
                            print("⏹️ Session annulée pendant la vérification")
                            self.music_player.root.after(0, lambda: 
                                self.music_player.status_bar.config(text="⏹️ Traitement annulé par l'utilisateur"))
                            return
                        
                        # Attendre si en pause
                        if session_id:
                            self.logger.wait_if_paused()
                        
                        try:
                            # Mettre à jour le statut de vérification seulement tous les 5 liens
                            current_check = wave_start + i + 1
                            # Réduire les prints pour éviter la surcharge console
                            if i % 10 == 0:  # Print seulement tous les 10 liens
                                print(f"🔍 Vérification {current_check}/{total_links}: {url[:80]}...")
                            if i % 5 == 0:  # Mise à jour seulement tous les 5 liens
                                self.music_player.root.after(0, lambda cc=current_check, tl=total_links: 
                                    self.music_player.status_bar.config(
                                        text=f"🔍 Vérification {cc}/{tl}..."))
                            
                            # Réduire les logs pour éviter la surcharge
                            if session_id and i % 10 == 0:  # Log seulement tous les 10 liens
                                self.logger.log("INFO", f"Vérification {current_check}/{total_links}")
                            
                            # Nettoyer l'URL
                            url = clean_youtube_url(url)
                            
                            # Extraire les informations de la vidéo avec options robustes
                            ydl_opts = {
                                'quiet': True,
                                'no_warnings': True,
                                'format': 'best[height<=720]/best',
                                'extractor_retries': 2,  # Réduire les tentatives pour aller plus vite
                                'fragment_retries': 2,
                                'retry_sleep_functions': {'http': lambda n: min(2**n, 5)},
                                'http_headers': {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                                },
                                'extractor_args': {
                                    'youtube': {
                                        'player_client': ['android', 'web'],
                                        'player_skip': ['webpage']
                                    }
                                },
                                'ignoreerrors': True,
                            }
                            
                            with YoutubeDL(ydl_opts) as ydl:
                                info = ydl.extract_info(url, download=False)
                                
                                if not info:
                                    reason = 'Impossible d\'extraire les informations (vidéo privée/supprimée?)'
                                    print(f"⚠️ Ignoré: {url[:80]} - {reason}")
                                    skipped_videos_wave.append({
                                        'title': url,
                                        'url': url,
                                        'duration': None,
                                        'reason': reason
                                    })
                                    if session_id:
                                        self.logger.log_processed(url, url, 'skipped', reason)
                                    continue
                                
                                title = info.get('title', 'Titre inconnu')
                                duration = info.get('duration', 0)
                                
                                # Vérifier la durée
                                if max_duration != -1 and duration and duration > max_duration:
                                    reason = f'Durée trop longue ({duration}s > {max_duration}s)'
                                    print(f"⚠️ Ignoré: {title} - {reason}")
                                    skipped_videos_wave.append({
                                        'title': title,
                                        'url': url,
                                        'duration': duration,
                                        'reason': reason
                                    })
                                    if session_id:
                                        self.logger.log_processed(url, title, 'skipped', reason)
                                    continue
                                
                                # Vérifier si déjà téléchargé
                                existing_file = self.music_player._get_existing_download(title)
                                if existing_file:
                                    reason = 'Fichier déjà téléchargé'
                                    print(f"⚠️ Ignoré: {title} - {reason}")
                                    skipped_videos_wave.append({
                                        'title': title,
                                        'url': url,
                                        'duration': duration,
                                        'reason': reason
                                    })
                                    if session_id:
                                        self.logger.log_processed(url, title, 'skipped', reason)
                                    continue
                                
                                # Vidéo valide pour téléchargement
                                valid_videos_wave.append((url, title, info))
                                print(f"✅ Vidéo valide: {title} ({duration}s)")
                                if session_id:
                                    self.logger.log("INFO", f"✅ Vidéo valide: {title} ({duration}s)")
                            
                        except Exception as e:
                            error_msg = str(e)
                            print(f"Erreur lors de la vérification de {url}: {e}")
                            
                            # Catégoriser les erreurs
                            if "403" in error_msg or "Forbidden" in error_msg:
                                reason = "Erreur 403 - Accès interdit (vidéo restreinte ou protection YouTube)"
                            elif "404" in error_msg or "not available" in error_msg:
                                reason = "Vidéo non disponible (supprimée ou privée)"
                            elif "format" in error_msg.lower():
                                reason = "Format non disponible (vidéo peut être restreinte)"
                            elif "private" in error_msg.lower():
                                reason = "Vidéo privée"
                            elif "deleted" in error_msg.lower():
                                reason = "Vidéo supprimée"
                            else:
                                reason = f'Erreur technique: {error_msg[:100]}...' if len(error_msg) > 100 else f'Erreur: {error_msg}'
                            
                            skipped_videos_wave.append({
                                'title': url,
                                'url': url,
                                'duration': None,
                                'reason': reason
                            })
                            if session_id:
                                self.logger.log_processed(url, url, 'failed', reason)
                            continue
                    
                    # Ajouter les vidéos ignorées de cette vague au total
                    all_skipped_videos.extend(skipped_videos_wave)
                    
                    # Phase 2 : Télécharger IMMÉDIATEMENT les vidéos valides de cette vague
                    if valid_videos_wave:
                        self.music_player.root.after(0, lambda w=wave_num, tw=total_waves, vv=len(valid_videos_wave): 
                            self.music_player.status_bar.config(
                                text=f"⬇️ Vague {w}/{tw} - Téléchargement de {vv} vidéos..."))
                        
                        if session_id:
                            self.logger.log("INFO", f"Début du téléchargement de {len(valid_videos_wave)} vidéos de la vague {wave_num}")
                        
                        # Télécharger séquentiellement les vidéos de cette vague
                        for j, (url, title, video_data) in enumerate(valid_videos_wave):
                            # Vérifier si la session a été annulée ou mise en pause
                            if session_id and self.logger.is_cancelled():
                                print("⏹️ Session annulée pendant le téléchargement")
                                self.music_player.root.after(0, lambda: 
                                    self.music_player.status_bar.config(text="⏹️ Traitement annulé par l'utilisateur"))
                                return
                            
                            # Attendre si la session est en pause (avec attente efficace)
                            if session_id:
                                self.logger.wait_if_paused()  # Attente efficace avec événement
                                
                                if self.logger.is_cancelled():
                                    return
                            
                            try:
                                current_index = wave_start + j
                                if session_id:
                                    self.logger.update_current_index(current_index)
                                
                                # Mise à jour de statut moins fréquente
                                if j % 2 == 0:  # Seulement tous les 2 téléchargements
                                    self.music_player.root.after(0, lambda w=wave_num, tw=total_waves, j=j+1, vv=len(valid_videos_wave): 
                                        self.music_player.status_bar.config(
                                            text=f"⬇️ Vague {w}/{tw} - Téléchargement {j}/{vv}..."))
                                
                                # Réduire les logs de téléchargement
                                if session_id and j % 3 == 0:  # Log seulement tous les 3 téléchargements
                                    self.logger.log("INFO", f"Téléchargement {j+1}/{len(valid_videos_wave)}: {title[:50]}...")
                                
                                # Téléchargement synchrone avec attente
                                success = self._download_video_sync(url, title, video_data)
                                
                                if success:
                                    total_downloaded += 1
                                    if session_id:
                                        self.logger.log_processed(url, title, 'success')
                                else:
                                    if session_id:
                                        self.logger.log_processed(url, title, 'failed', 'Erreur de téléchargement')
                                
                                # Pause courte entre les téléchargements (réduite)
                                time.sleep(0.5)
                                
                            except Exception as e:
                                error_msg = f"Erreur lors du téléchargement de {title}: {e}"
                                print(error_msg)
                                if session_id:
                                    self.logger.log_processed(url, title, 'failed', str(e))
                                continue
                        
                        # Pause entre les vagues (réduite)
                        if wave_end < total_links:
                            self.music_player.root.after(0, lambda: 
                                self.music_player.status_bar.config(text="⏸️ Pause entre les vagues (2s)..."))
                            time.sleep(2)
                    
                    else:
                        self.music_player.root.after(0, lambda w=wave_num, tw=total_waves: 
                            self.music_player.status_bar.config(
                                text=f"⚠️ Vague {w}/{tw} - Aucune vidéo valide trouvée"))
                        time.sleep(1)
                
                # Sauvegarder le rapport final
                if all_skipped_videos:
                    self._save_skipped_videos_json(all_skipped_videos, html_file_path)
                
                # Terminer la session
                if session_id:
                    self.logger.end_session('completed')
                
                # Message final
                self.music_player.root.after(0, lambda td=total_downloaded, tl=total_links: 
                    self.music_player.status_bar.config(
                        text=f"✅ Terminé ! {td}/{tl} vidéos téléchargées avec succès"))
                
            except Exception as e:
                if session_id:
                    self.logger.log("ERROR", f"Erreur fatale: {str(e)}")
                    self.logger.end_session('interrupted')
                self.music_player.root.after(0, lambda: 
                    self.music_player.status_bar.config(text=f"❌ Erreur: {str(e)}"))
        
        # Lancer le traitement par vagues dans un thread
        print("🚀 Lancement du thread de traitement...")
        thread = threading.Thread(target=process_wave_thread, daemon=True)
        thread.start()
        print(f"✅ Thread lancé: {thread.name}")
    
    def _download_video_sync(self, url, title, video_data):
        """Télécharge une vidéo de manière synchrone (attend la fin)"""
        try:
            # Utiliser directement le gestionnaire de téléchargement
            download_manager_instance = download_manager.DownloadManager(self.music_player)
            
            # Téléchargement synchrone
            success = download_manager_instance.download_video_sync(url, title, video_data)
            
            if success:
                print(f"✅ Téléchargement réussi: {title}")
                return True
            else:
                print(f"❌ Échec du téléchargement: {title}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur téléchargement {title}: {e}")
            return False
    
    def _download_video_simple(self, url, title, video_data):
        """Télécharge une vidéo de manière simple et directe"""
        try:
            # Utiliser directement le gestionnaire de téléchargement
            success = download_manager.download_youtube_video(
                self.music_player,
                url,
                title,
                video_data,
                callback_on_complete=self._on_video_downloaded,
                callback_params={'title': title}
            )
            return success
            
        except Exception as e:
            print(f"Erreur téléchargement simple: {e}")
            return False
    
    def _download_video_sync(self, url, title, video_data):
        """Télécharge une vidéo de manière synchrone"""
        try:
            # Utiliser le gestionnaire de téléchargement existant
            # Mais de manière synchrone
            success_flag = {'success': False}
            
            def download_callback(filepath, **kwargs):
                success_flag['success'] = True
                # Ajouter à la playlist
                try:
                    download_manager.add_to_playlist_after_download(
                        self.music_player, 
                        filepath, 
                        queue_position='last'
                    )
                except Exception as e:
                    print(f"Erreur ajout playlist: {e}")
            
            # Lancer le téléchargement
            download_manager.download_youtube_video(
                self.music_player,
                url,
                title,
                video_data,
                callback_on_complete=download_callback
            )
            
            # Attendre que le téléchargement se termine (avec timeout)
            timeout = 300  # 5 minutes max par vidéo
            start_time = time.time()
            
            while not success_flag['success'] and (time.time() - start_time) < timeout:
                time.sleep(1)
            
            return success_flag['success']
            
        except Exception as e:
            print(f"Erreur téléchargement sync: {e}")
            return False
    
    def _download_videos_in_batches(self, valid_videos, batch_size=10):
        """Télécharge les vidéos par paquets pour éviter la surcharge"""
        def download_batch_thread():
            total_videos = len(valid_videos)
            downloaded_count = 0
            
            # Diviser en paquets
            for i in range(0, total_videos, batch_size):
                batch = valid_videos[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_videos + batch_size - 1) // batch_size
                
                self.music_player.root.after(0, lambda b=batch_num, t=total_batches: 
                    self.music_player.status_bar.config(
                        text=f"Téléchargement du paquet {b}/{t} ({len(batch)} vidéos)..."))
                
                # Télécharger chaque vidéo du paquet
                for url, title, video_data in batch:
                    try:
                        # Utiliser la fonction de téléchargement individuelle
                        success = download_manager.download_youtube_video(
                            self.music_player,
                            url,
                            title,
                            video_data,
                            callback_on_complete=self._on_video_downloaded,
                            callback_params={'title': title}
                        )
                        
                        if success:
                            downloaded_count += 1
                            self.music_player.root.after(0, lambda d=downloaded_count, t=total_videos: 
                                self.music_player.status_bar.config(
                                    text=f"Téléchargement en cours... {d}/{t} vidéos"))
                        
                        # Petite pause entre les téléchargements pour éviter la surcharge
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"Erreur lors du téléchargement de {title}: {e}")
                        continue
                
                # Pause plus longue entre les paquets
                if i + batch_size < total_videos:
                    time.sleep(5)
            
            # Message final
            self.music_player.root.after(0, lambda d=downloaded_count, t=total_videos: 
                self.music_player.status_bar.config(
                    text=f"Téléchargement terminé: {d}/{t} vidéos téléchargées avec succès"))
        
        # Lancer le téléchargement par paquets dans un thread
        threading.Thread(target=download_batch_thread, daemon=True).start()
    
    def _on_video_downloaded(self, filepath, title=None):
        """Callback appelé quand une vidéo est téléchargée"""
        try:
            # Ajouter à la playlist principale
            download_manager.add_to_playlist_after_download(
                self.music_player, 
                filepath, 
                queue_position='last'
            )
            
            if title:
                print(f"✅ Téléchargé: {title}")
                
        except Exception as e:
            print(f"Erreur lors de l'ajout à la playlist: {e}")
    
    def check_resumable_sessions(self):
        """Vérifie s'il y a des sessions à reprendre au démarrage"""
        try:
            resumable_sessions = self.logger.get_resumable_sessions()
            if resumable_sessions:
                # Afficher une boîte de dialogue pour proposer la reprise
                self.show_resume_dialog(resumable_sessions)
        except Exception as e:
            print(f"Erreur vérification sessions: {e}")
    
    def show_resume_dialog(self, sessions):
        """Affiche une boîte de dialogue pour reprendre une session"""
        if not sessions:
            return
        
        resume_dialog = tk.Toplevel(self.dialog)
        resume_dialog.title("Sessions interrompues")
        resume_dialog.geometry("600x400")
        resume_dialog.configure(bg='#2d2d2d')
        resume_dialog.transient(self.dialog)
        resume_dialog.grab_set()
        
        # Titre
        tk.Label(
            resume_dialog,
            text="Sessions interrompues trouvées",
            font=("Arial", 14, "bold"),
            bg='#2d2d2d',
            fg='white'
        ).pack(pady=10)
        
        tk.Label(
            resume_dialog,
            text="Voulez-vous reprendre une session précédente ?",
            bg='#2d2d2d',
            fg='white'
        ).pack(pady=5)
        
        # Liste des sessions
        sessions_frame = tk.Frame(resume_dialog, bg='#2d2d2d')
        sessions_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Listbox avec scrollbar
        listbox_frame = tk.Frame(sessions_frame, bg='#2d2d2d')
        listbox_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side='right', fill='y')
        
        sessions_listbox = tk.Listbox(
            listbox_frame,
            bg='#3d3d3d',
            fg='white',
            selectbackground='#4a8fe7',
            yscrollcommand=scrollbar.set,
            font=("Arial", 10)
        )
        sessions_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=sessions_listbox.yview)
        
        # Remplir la liste
        for session in sessions:
            source = session.get('source', 'N/A')
            if len(source) > 60:
                source = source[:57] + '...'
            
            processed = session.get('processed', 0)
            total = session.get('total', 0)
            status = session.get('status', 'N/A')
            
            try:
                from datetime import datetime
                start_time = datetime.fromisoformat(session.get('start_time', ''))
                date_str = start_time.strftime('%d/%m/%Y %H:%M')
            except:
                date_str = 'N/A'
            
            item_text = f"{date_str} - {source} ({processed}/{total}) - {status}"
            sessions_listbox.insert(tk.END, item_text)
        
        # Boutons
        buttons_frame = tk.Frame(resume_dialog, bg='#2d2d2d')
        buttons_frame.pack(pady=10)
        
        def resume_selected():
            selection = sessions_listbox.curselection()
            if selection:
                selected_session = sessions[selection[0]]
                resume_dialog.destroy()
                self.resume_session_processing(selected_session)
        
        def skip_resume():
            resume_dialog.destroy()
        
        tk.Button(
            buttons_frame,
            text="▶️ Reprendre",
            command=resume_selected,
            bg='#28a745',
            fg='white',
            font=("Arial", 10),
            padx=20,
            pady=5
        ).pack(side='left', padx=10)
        
        tk.Button(
            buttons_frame,
            text="❌ Ignorer",
            command=skip_resume,
            bg='#dc3545',
            fg='white',
            font=("Arial", 10),
            padx=20,
            pady=5
        ).pack(side='left', padx=10)
        
        # Sélectionner la première session par défaut
        if sessions:
            sessions_listbox.selection_set(0)
    
    def resume_session_processing(self, session):
        """Reprend le traitement d'une session interrompue"""
        try:
            session_id = session.get('id')
            self.logger.load_session(session_id)
            self.logger.resume_session()
            
            # Récupérer les informations de la session
            pending_urls = session.get('pending_urls', [])
            current_index = session.get('current_index', 0)
            max_duration = 600  # Valeur par défaut
            batch_size = 10     # Valeur par défaut
            
            # Reprendre depuis l'index courant
            remaining_urls = pending_urls[current_index:]
            
            if remaining_urls:
                print(f"Reprise de la session {session_id} depuis l'index {current_index}")
                self.logger.log("INFO", f"Reprise de la session depuis l'index {current_index}")
                
                # Fermer le dialogue d'import
                self.dialog.destroy()
                
                # Relancer le traitement
                self._process_videos_in_waves_sequential(
                    remaining_urls, max_duration, batch_size, 
                    session.get('source', ''), session_id
                )
            else:
                print("Aucune URL restante à traiter")
                self.logger.end_session('completed')
                
        except Exception as e:
            print(f"Erreur reprise session: {e}")
            import tkinter.messagebox as messagebox
            messagebox.showerror("Erreur", f"Impossible de reprendre la session: {e}")

def on_global_seek_forward(self, event):
    """Raccourci global Ctrl+Alt+→ pour avancer de 5s"""
    try:
        if pygame.mixer.music.get_busy() and self.song_length > 0:
            # Avancer de 5 secondes
            new_time = min(self.song_length, self.current_time + 5)
            
            # Utiliser set_position avec la valeur en secondes
            self.set_position(new_time)
            
            # Mettre à jour le curseur visuellement avec le pourcentage
            if hasattr(self, 'progress'):
                progress_percent = (new_time / self.song_length) * 100
                self.progress.set(progress_percent)
            
            self.status_bar.config(text=f"Avancé de 5s - {new_time:.0f}s")
        else:
            pass
    except Exception as e:
        pass
        import traceback
        traceback.print_exc()
    return "break"

def on_global_seek_backward(self, event):
    """Raccourci global Ctrl+Alt+← pour reculer de 5s"""
    try:
        if pygame.mixer.music.get_busy() and self.song_length > 0:
            # Reculer de 5 secondes
            new_time = max(0, self.current_time - 5)
            
            # Utiliser set_position avec la valeur en secondes
            self.set_position(new_time)
            
            # Mettre à jour le curseur visuellement avec le pourcentage
            if hasattr(self, 'progress'):
                progress_percent = (new_time / self.song_length) * 100
                self.progress.set(progress_percent)
            
            self.status_bar.config(text=f"Reculé de 5s - {new_time:.0f}s")
        else:
            pass
    except Exception as e:
        pass
        import traceback
        traceback.print_exc()
    return "break"
