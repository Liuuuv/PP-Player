# Module principal pour la gestion des pages d'artiste
# Ce fichier centralise toutes les fonctionnalités des pages d'artiste

# Import centralisé depuis __init__.py
from music_player import *

# Importer tous les sous-modules
from . import core, songs, releases, playlists

class ArtistTabModule:
    """Module principal pour la gestion des pages d'artiste"""
    
    def __init__(self):
        self.core = core
        self.songs = songs
        self.releases = releases
        self.playlists = playlists
    
    # ==================== FONCTIONS PRINCIPALES ====================
    
    def show_artist_content(self, music_player, artist_name, video_data):
        """Affiche le contenu d'un artiste dans la zone de recherche YouTube"""
        return self.core._show_artist_content(music_player, artist_name, video_data)
    
    def create_artist_tabs(self, music_player):
        """Crée les onglets Musiques et Sorties dans la zone YouTube"""
        return self.core._create_artist_tabs(music_player)
    
    def search_artist_content_async(self, music_player):
        """Version asynchrone et non-bloquante de la recherche d'artiste"""
        return self.core._search_artist_content_async(music_player)
    
    def find_artist_channel_id(self, music_player):
        """Trouve l'ID réel de la chaîne YouTube pour cet artiste"""
        return self.core._find_artist_channel_id(music_player)
    
    def cancel_artist_search(self, music_player):
        """Annule toutes les recherches d'artiste en cours"""
        return self.core._cancel_artist_search(music_player)
    
    # ==================== RECHERCHE DE CONTENU ====================
    
    def search_artist_videos(self, music_player):
        """Recherche les vidéos de l'artiste"""
        return self.songs._search_artist_videos_with_id(music_player)
    
    def search_artist_releases(self, music_player):
        """Recherche les albums et singles de l'artiste"""
        return self.releases._search_artist_releases_with_id(music_player)
    
    def search_artist_playlists(self, music_player):
        """Recherche les playlists de l'artiste"""
        return self.playlists._search_artist_playlists_with_id(music_player)
    
    # ==================== AFFICHAGE DU CONTENU ====================
    
    def display_artist_videos(self, music_player, videos):
        """Affiche les vidéos de l'artiste dans l'onglet Musiques"""
        return self.songs._display_artist_videos(music_player, videos)
    
    def display_artist_releases(self, music_player, releases):
        """Affiche les sorties de l'artiste dans l'onglet Sorties"""
        return self.releases._display_artist_releases(music_player, releases)
    
    def display_artist_playlists(self, music_player, playlists):
        """Affiche les playlists de l'artiste dans l'onglet Playlists"""
        return self.playlists._display_artist_playlists(music_player, playlists)
    
    # ==================== GESTION DES PLAYLISTS ====================
    
    def show_playlist_content(self, music_player, playlist_data, target_tab="sorties"):
        """Affiche le contenu d'une playlist dans une nouvelle interface"""
        return self.playlists._show_playlist_content(music_player, playlist_data, target_tab)
    
    def display_playlist_content(self, music_player, videos, playlist_title, target_tab="sorties"):
        """Affiche le contenu d'une playlist avec la même interface que l'onglet Musiques"""
        return self.playlists._display_playlist_content(music_player, videos, playlist_title, target_tab)
    
    def return_to_releases(self, music_player):
        """Retourne à l'affichage des releases dans l'onglet Sorties"""
        return self.releases._return_to_releases(music_player)
    
    def return_to_playlists(self, music_player):
        """Retourne à l'affichage des playlists dans l'onglet Playlists"""
        return self.playlists._return_to_playlists(music_player)
    
    # ==================== UTILITAIRES ====================
    
    def add_artist_result(self, music_player, video, index, container):
        """Ajoute un résultat vidéo dans un onglet artiste"""
        return self.core._add_artist_result(music_player, video, index, container)
    
    def load_artist_thumbnail(self, music_player, video, thumbnail_label):
        """Charge la miniature d'une vidéo d'artiste en arrière-plan"""
        return self.core._load_artist_thumbnail(music_player, video, thumbnail_label)
    
    def add_artist_playlist_result(self, music_player, playlist, index, container, target_tab="sorties"):
        """Ajoute une playlist dans l'onglet Sorties ou Playlists"""
        return self.core._add_artist_playlist_result(music_player, playlist, index, container, target_tab)


# Instance globale du module
artist_tab_module = ArtistTabModule()

# Fonctions d'accès direct pour compatibilité
def show_artist_content(music_player, artist_name, video_data):
    """Affiche le contenu d'un artiste"""
    return artist_tab_module.show_artist_content(music_player, artist_name, video_data)

def create_artist_tabs(music_player):
    """Crée les onglets artiste"""
    return artist_tab_module.create_artist_tabs(music_player)

def search_artist_content_async(music_player):
    """Recherche le contenu d'un artiste de manière asynchrone"""
    return artist_tab_module.search_artist_content_async(music_player)

def get_artist_tab_module():
    """Retourne l'instance du module artist_tab"""
    return artist_tab_module