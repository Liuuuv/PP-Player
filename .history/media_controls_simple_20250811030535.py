# Module simplifié pour les contrôles multimédia Windows
import asyncio
import threading
import pygame
import os

try:
    from winsdk.windows.media import SystemMediaTransportControls, MediaPlaybackStatus
    from winsdk.windows.media.playback import MediaPlayer
    WINSDK_AVAILABLE = True
except ImportError:
    print("winsdk non disponible - contrôles multimédia désactivés")
    WINSDK_AVAILABLE = False

class SimpleWindowsMediaControls:
    def __init__(self, music_player):
        self.music_player = music_player
        self.smtc = None
        self.media_player = None
        self.loop = None
        self.thread = None
        self.is_initialized = False
        
        if not WINSDK_AVAILABLE:
            return
        
        # Démarrer l'initialisation dans un thread séparé
        self.thread = threading.Thread(target=self._initialize_async, daemon=True)
        self.thread.start()
    
    def _initialize_async(self):
        """Initialise les contrôles multimédia de manière asynchrone"""
        try:
            # Créer un nouveau loop d'événements pour ce thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Exécuter l'initialisation asynchrone
            self.loop.run_until_complete(self._setup_media_controls())
            
            # Garder le loop actif pour les événements
            self.loop.run_forever()
        except Exception as e:
            print(f"Erreur initialisation contrôles multimédia: {e}")
    
    async def _setup_media_controls(self):
        """Configure les contrôles multimédia Windows"""
        try:
            # Créer un MediaPlayer pour obtenir les contrôles système
            self.media_player = MediaPlayer()
            
            # Obtenir les contrôles de transport système
            self.smtc = self.media_player.system_media_transport_controls
            
            # Activer les contrôles
            self.smtc.is_enabled = True
            self.smtc.is_play_enabled = True
            self.smtc.is_pause_enabled = True
            self.smtc.is_stop_enabled = True
            self.smtc.is_next_enabled = True
            self.smtc.is_previous_enabled = True
            
            # Configurer les gestionnaires d'événements
            self.smtc.add_button_pressed(self._on_button_pressed)
            
            # Définir le statut initial
            self.smtc.playback_status = MediaPlaybackStatus.STOPPED
            
            self.is_initialized = True
            print("Contrôles multimédia Windows initialisés avec succès")
            
        except Exception as e:
            print(f"Erreur configuration contrôles multimédia: {e}")
    
    def _on_button_pressed(self, sender, args):
        """Gestionnaire pour les boutons des contrôles multimédia"""
        try:
            button = args.button
            
            # Exécuter les actions dans le thread principal de tkinter
            if button == 0:  # Play
                self.music_player.root.after(0, self._handle_play)
            elif button == 1:  # Pause
                self.music_player.root.after(0, self._handle_pause)
            elif button == 2:  # Stop
                self.music_player.root.after(0, self._handle_stop)
            elif button == 3:  # Next
                self.music_player.root.after(0, self._handle_next)
            elif button == 4:  # Previous
                self.music_player.root.after(0, self._handle_previous)
                
        except Exception as e:
            print(f"Erreur gestionnaire bouton: {e}")
    
    def _handle_play(self):
        """Gère le bouton Play"""
        try:
            if not pygame.get_init():
                return
                
            if self.music_player.paused:
                self.music_player.play_pause()
            elif not pygame.mixer.music.get_busy() and self.music_player.main_playlist:
                self.music_player.play_pause()
        except Exception as e:
            print(f"Erreur handle_play: {e}")
    
    def _handle_pause(self):
        """Gère le bouton Pause"""
        try:
            if not pygame.get_init():
                return
                
            if pygame.mixer.music.get_busy() and not self.music_player.paused:
                self.music_player.play_pause()
        except Exception as e:
            print(f"Erreur handle_pause: {e}")
    
    def _handle_stop(self):
        """Gère le bouton Stop"""
        try:
            if not pygame.get_init():
                return
                
            pygame.mixer.music.stop()
            self.music_player.paused = False
            self.music_player.current_time = 0
            self.music_player.play_button.config(image=self.music_player.icons["play"])
            self.music_player.play_button.config(text="Play")
            self.update_playback_status(MediaPlaybackStatus.STOPPED)
        except Exception as e:
            print(f"Erreur handle_stop: {e}")
    
    def _handle_next(self):
        """Gère le bouton Suivant"""
        try:
            self.music_player.next_track()
        except Exception as e:
            print(f"Erreur handle_next: {e}")
    
    def _handle_previous(self):
        """Gère le bouton Précédent"""
        try:
            self.music_player.prev_track()
        except Exception as e:
            print(f"Erreur handle_previous: {e}")
    
    def update_playback_status(self, status):
        """Met à jour le statut de lecture"""
        if not WINSDK_AVAILABLE or not self.is_initialized or not self.smtc:
            return
            
        try:
            if self.loop and not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(self._async_update_status(status), self.loop)
        except Exception as e:
            print(f"Erreur mise à jour statut: {e}")
    
    async def _async_update_status(self, status):
        """Met à jour le statut de manière asynchrone"""
        try:
            self.smtc.playback_status = status
        except Exception as e:
            print(f"Erreur async update status: {e}")
    
    def update_media_info(self, title, artist="", album="", thumbnail_path=None):
        """Met à jour les informations du média - Version simplifiée"""
        if not WINSDK_AVAILABLE or not self.is_initialized or not self.smtc:
            return
            
        # Pour éviter les erreurs, on ne met à jour que le statut
        # Les métadonnées peuvent être ajoutées plus tard si nécessaire
        print(f"Lecture: {title}")
    
    def cleanup(self):
        """Nettoie les ressources"""
        try:
            if self.loop and not self.loop.is_closed():
                self.loop.call_soon_threadsafe(self.loop.stop)
            
            if self.smtc:
                self.smtc.is_enabled = False
                
        except Exception as e:
            print(f"Erreur cleanup contrôles multimédia: {e}")

def initialize_media_controls(music_player):
    """Initialise les contrôles multimédia pour le lecteur"""
    if not WINSDK_AVAILABLE:
        print("Contrôles multimédia Windows non disponibles")
        return None
        
    try:
        return SimpleWindowsMediaControls(music_player)
    except Exception as e:
        print(f"Erreur initialisation contrôles multimédia: {e}")
        return None