"""
Constantes et configuration de l'application
"""
import os

# Couleurs
COLOR_SELECTED = '#5a9fd8'
COLOR_BACKGROUND = '#2d2d2d'
COLOR_BUTTON = '#3d3d3d'
COLOR_BUTTON_HOVER = '#4a4a4a'
COLOR_TAB_SELECTED = '#4a8fe7'
COLOR_DOWNLOADING = '#ff4444'
COLOR_DOWNLOADING_HOVER = '#ff6666'
COLOR_ERROR = '#ffcc00'

# Dimensions de la fenêtre
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700

# Configuration audio
AUDIO_FREQUENCY = 44100
AUDIO_SIZE = -16
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 4096

# Extensions audio supportées
AUDIO_EXTENSIONS = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')

# Configuration de recherche
MAX_SEARCH_RESULTS = 50
RESULTS_PER_PAGE = 10
SEARCH_DELAY = 300  # millisecondes

# Dossiers
DOWNLOADS_DIR = "downloads"
ASSETS_DIR = "assets"
CONFIG_FILE = os.path.join(DOWNLOADS_DIR, "player_config.json")
PLAYLISTS_FILE = os.path.join(DOWNLOADS_DIR, "playlists.json")

# Configuration YouTube-DL
YDL_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'external_downloader': 'ffmpeg',
}

# Modes de lecture
LOOP_MODE_OFF = 0
LOOP_MODE_PLAYLIST = 1
LOOP_MODE_SONG = 2

# Volume par défaut
DEFAULT_VOLUME = 0.1
VOLUME_OFFSET_RANGE = (-50, 50)