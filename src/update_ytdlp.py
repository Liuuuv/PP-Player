#!/usr/bin/env python3
"""
Script pour mettre à jour yt-dlp vers la dernière version
Les erreurs 403 sont souvent résolues avec les dernières versions
"""

import subprocess
import sys

def update_ytdlp():
    """Met à jour yt-dlp vers la dernière version"""
    try:
        print("🔄 Mise à jour de yt-dlp...")
        
        # Mettre à jour yt-dlp
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ yt-dlp mis à jour avec succès !")
            print(result.stdout)
        else:
            print("❌ Erreur lors de la mise à jour :")
            print(result.stderr)
            
        # Vérifier la version installée
        version_result = subprocess.run([
            sys.executable, '-c', 'import yt_dlp; print(f"Version yt-dlp: {yt_dlp.version.__version__}")'
        ], capture_output=True, text=True)
        
        if version_result.returncode == 0:
            print(version_result.stdout.strip())
        
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    update_ytdlp()