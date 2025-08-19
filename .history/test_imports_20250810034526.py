"""
Test des imports de la nouvelle architecture
"""
import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test tous les imports"""
    try:
        print("Test des imports...")
        
        # Config
        from config.constants import COLOR_SELECTED, WINDOW_WIDTH
        from config.settings import Settings
        print("✅ Config imports OK")
        
        # Core
        from core.playlist import PlaylistManager
        from core.audio_utils import AudioUtils
        print("✅ Core imports OK")
        
        # Services
        from services.youtube_service import YouTubeService
        from services.file_service import FileService
        from services.search_service import SearchService
        print("✅ Services imports OK")
        
        # UI
        from ui.main_window import MainWindow
        from ui.styles import StyleManager
        print("✅ UI imports OK")
        
        # Utils
        from utils.keyboard import KeyboardManager
        print("✅ Utils imports OK")
        
        print("\n🎉 Tous les imports fonctionnent correctement !")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_imports()