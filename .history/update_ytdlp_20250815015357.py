#!/usr/bin/env python3
"""
Script pour mettre à jour yt-dlp à la dernière version
"""

import subprocess
import sys

def update_ytdlp():
    """Met à jour yt-dlp à la dernière version"""
    try:
        print("Mise à jour de yt-dlp...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ yt-dlp mis à jour avec succès")
            print(result.stdout)
        else:
            print("✗ Erreur lors de la mise à jour de yt-dlp")
            print(result.stderr)
            
    except Exception as e:
        print(f"✗ Erreur: {e}")

if __name__ == "__main__":
    update_ytdlp()