#!/usr/bin/env python3
import os
import sys
import json
import shutil
import requests
import tempfile
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import re
import subprocess
import time

class AutoUpdater:
    def __init__(self, current_version, parent=None):
        self.current_version = current_version
        self.repo_owner = "Liuuuv"
        self.repo_name = "PP-Player"
        self.github_api = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        
        # Fichiers à préserver lors de la mise à jour
        self.config_files_to_preserve = ["player_config.json", "ai_music_data.json"]
        
        # Dossiers à préserver
        self.folders_to_preserve = ["assets", "logs", "ffmpeg"]
        
        # Fichiers/dossiers à exclure complètement (ne seront pas touchés)
        self.exclude_from_update = ["logs", "player_config.json", "ai_music_data.json"]
        
        # Référence à la fenêtre parente
        self.parent = parent
        
        # Variables d'état
        self.latest_release = None
        self.update_available = False
        self.is_running = False
        self.window = None
        
    def show_window(self):
        """Ouvre la fenêtre de mise à jour"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return
            
        self.is_running = True
        
        if self.parent:
            self.window = tk.Toplevel(self.parent)
            self.window.transient(self.parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("Mise à jour PP Player")
        self.window.geometry("700x600")
        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        self.center_window()
        
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        title_label = ttk.Label(main_frame, text="PP Player - Mise à jour", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        version_label = ttk.Label(main_frame, 
                                 text=f"Version actuelle: v{self.current_version}",
                                 font=("Arial", 10))
        version_label.grid(row=1, column=0, pady=(0, 15), sticky=tk.W)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 15), sticky=tk.W)
        
        self.check_button = ttk.Button(button_frame, text="Vérifier les mises à jour", 
                                      command=self.start_update_check)
        self.check_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.update_button = ttk.Button(button_frame, text="Installer la mise à jour", 
                                       command=self.start_update_process, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(main_frame, text="Cliquez sur 'Vérifier les mises à jour' pour commencer")
        self.status_label.grid(row=3, column=0, pady=(0, 10), sticky=tk.W)
        
        notes_label = ttk.Label(main_frame, text="Notes de version:", font=("Arial", 11, "bold"))
        notes_label.grid(row=4, column=0, pady=(10, 5), sticky=tk.W)
        
        self.release_notes_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                                           width=80, height=20,
                                                           font=("Arial", 9))
        self.release_notes_text.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.release_notes_text.insert(tk.END, "Les notes de version s'afficheront ici après la vérification.")
        self.release_notes_text.config(state=tk.DISABLED)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
    def on_closing(self):
        """Gère la fermeture de la fenêtre"""
        self.is_running = False
        if self.window:
            self.window.destroy()
            self.window = None
        
    def safe_after(self, delay_ms, func, *args):
        if self.is_running and self.window and self.window.winfo_exists():
            self.window.after(delay_ms, func, *args)
        
    def start_update_check(self):
        self.check_button.config(state=tk.DISABLED)
        self.status_label.config(text="Vérification des mises à jour...")
        self.progress.start()
        
        thread = threading.Thread(target=self.check_for_updates_thread)
        thread.daemon = True
        thread.start()
    
    def check_for_updates_thread(self):
        try:
            response = requests.get(self.github_api, timeout=10)
            response.raise_for_status()
            
            self.latest_release = response.json()
            latest_version = self.latest_release['tag_name'].lstrip('v')
            
            self.safe_after(0, self.update_ui_after_check, latest_version)
            
        except Exception as e:
            self.safe_after(0, self.show_error, f"Erreur lors de la vérification: {str(e)}")
    
    def update_ui_after_check(self, latest_version):
        if not self.is_running or not self.window or not self.window.winfo_exists():
            return
            
        self.progress.stop()
        
        if self.is_newer_version(latest_version):
            self.update_available = True
            self.status_label.config(text=f"Nouvelle version disponible: v{latest_version}")
            self.update_button.config(state=tk.NORMAL)
            
            release_notes = self.latest_release.get('body', 'Aucune note de version disponible.')
            self.display_release_notes(release_notes)
        else:
            self.update_available = False
            self.status_label.config(text="Vous avez déjà la dernière version")
            self.update_button.config(state=tk.DISABLED)
            
            self.safe_after(0, self.fetch_current_version_release_notes)
    
    def fetch_current_version_release_notes(self):
        try:
            releases_api = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases"
            response = requests.get(releases_api, timeout=10)
            response.raise_for_status()
            
            releases = response.json()
            
            current_release = None
            for release in releases:
                if release['tag_name'].lstrip('v') == self.current_version:
                    current_release = release
                    break
            
            if current_release:
                release_notes = current_release.get('body', 'Aucune note de version disponible pour cette version.')
                self.display_release_notes(f"Notes de version de la version actuelle (v{self.current_version}):\n\n{release_notes}")
            else:
                self.display_release_notes(f"Aucune information de release trouvée pour la version v{self.current_version}.")
                
        except Exception as e:
            self.display_release_notes(f"Impossible de récupérer les notes de version: {str(e)}")
    
    def display_release_notes(self, notes):
        if not self.is_running or not self.window or not self.window.winfo_exists():
            return
            
        self.release_notes_text.config(state=tk.NORMAL)
        self.release_notes_text.delete(1.0, tk.END)
        
        formatted_notes = notes.replace('##', '\n##').replace('###', '\n###')
        formatted_notes = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', formatted_notes)
        
        self.release_notes_text.insert(tk.END, formatted_notes)
        self.release_notes_text.config(state=tk.DISABLED)
    
    def is_newer_version(self, latest_version):
        return latest_version != self.current_version
    
    def start_update_process(self):
        if not self.update_available or not self.latest_release:
            return
        
        result = messagebox.askyesno("Confirmation", 
                                    f"Voulez-vous installer la version {self.latest_release['tag_name']}?\n\nL'application sera fermée et redémarrée automatiquement.")
        if not result:
            return
        
        self.check_button.config(state=tk.DISABLED)
        self.update_button.config(state=tk.DISABLED)
        self.status_label.config(text="Préparation de la mise à jour...")
        self.progress.start()
        
        thread = threading.Thread(target=self.prepare_update)
        thread.daemon = True
        thread.start()
    
    def prepare_update(self):
        """Prépare la mise à jour en téléchargeant et créant un script de mise à jour"""
        try:
            # Télécharger la mise à jour
            zip_path = self.download_update(self.latest_release)
            if not zip_path:
                self.safe_after(0, self.show_error, "Échec du téléchargement")
                return
            
            # Créer un script de mise à jour qui s'exécutera après la fermeture
            update_success = self.create_update_script(zip_path)
            
            if update_success:
                self.safe_after(0, self.finalize_preparation)
            else:
                self.safe_after(0, self.show_error, "Échec de la préparation de la mise à jour")
                
        except Exception as e:
            self.safe_after(0, self.show_error, f"Erreur lors de la préparation: {str(e)}")
    
    def create_update_script(self, zip_path):
        """Crée un script batch qui s'exécutera après la fermeture de l'app"""
        try:
            # Déterminer le chemin de l'exécutable actuel
            current_exe = sys.executable if hasattr(sys, 'frozen') else None
            
            # Créer un script de mise à jour
            script_content = self.generate_update_script_content(zip_path, current_exe)
            
            # Sauvegarder le script
            script_path = os.path.join(tempfile.gettempdir(), "ppplayer_update.bat")
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur création script: {e}")
            return False
    
    def generate_update_script_content(self, zip_path, current_exe):
        """Génère le contenu du script batch de mise à jour"""
        script_lines = [
            "@echo off",
            "chcp 65001 >nul",
            "echo Mise à jour PP Player en cours...",
            "timeout /t 2 /nobreak >nul",
            "",
            "# Attendre que l'application se ferme",
            ":wait_loop",
            f"tasklist /FI \"IMAGENAME eq {os.path.basename(current_exe)}\" 2>nul | find /I \"{os.path.basename(current_exe)}\" >nul",
            "if %errorlevel% == 0 (",
            "    echo En attente de la fermeture de l'application...",
            "    timeout /t 1 /nobreak >nul",
            "    goto wait_loop",
            ")",
            "",
            "# Sauvegarder les fichiers importants",
            "echo Sauvegarde des configurations...",
            f"xcopy \"player_config.json\" \"%TEMP%\\ppplayer_backup\\\" /Y /I 2>nul",
            f"xcopy \"ai_music_data.json\" \"%TEMP%\\ppplayer_backup\\\" /Y /I 2>nul",
            f"xcopy \"logs\\*\" \"%TEMP%\\ppplayer_backup\\logs\\\" /Y /E /I 2>nul",
            f"xcopy \"assets\\*\" \"%TEMP%\\ppplayer_backup\\assets\\\" /Y /E /I 2>nul",
            f"xcopy \"ffmpeg\\*\" \"%TEMP%\\ppplayer_backup\\ffmpeg\\\" /Y /E /I 2>nul",
            "",
            "# Supprimer les anciens fichiers (sauf ceux à exclure)",
            "echo Nettoyage des anciens fichiers...",
            "for /f \"delims=\" %%i in ('dir /b /a-d') do (",
            "    if not \"%%i\"==\"player_config.json\" if not \"%%i\"==\"ai_music_data.json\" del /f /q \"%%i\" 2>nul",
            ")",
            "for /f \"delims=\" %%i in ('dir /b /ad') do (",
            "    if not \"%%i\"==\"logs\" if not \"%%i\"==\"assets\" if not \"%%i\"==\"ffmpeg\" rd /s /q \"%%i\" 2>nul",
            ")",
            "",
            "# Extraire la nouvelle version",
            "echo Extraction de la nouvelle version...",
            f"\"C:\\Program Files\\7-Zip\\7z.exe\" x \"{zip_path}\" -o. -y >nul",
            "if %errorlevel% neq 0 (",
            "    echo Utilisation de l'extracteur Windows...",
            f"    tar -xf \"{zip_path}\" --force-local 2>nul",
            ")",
            "",
            "# Restaurer les fichiers sauvegardés",
            "echo Restauration des configurations...",
            f"xcopy \"%TEMP%\\ppplayer_backup\\player_config.json\" \".\\\" /Y 2>nul",
            f"xcopy \"%TEMP%\\ppplayer_backup\\ai_music_data.json\" \".\\\" /Y 2>nul",
            f"xcopy \"%TEMP%\\ppplayer_backup\\logs\\*\" \".\\logs\\\" /Y /E /I 2>nul",
            f"xcopy \"%TEMP%\\ppplayer_backup\\assets\\*\" \".\\assets\\\" /Y /E /I 2>nul",
            f"xcopy \"%TEMP%\\ppplayer_backup\\ffmpeg\\*\" \".\\ffmpeg\\\" /Y /E /I 2>nul",
            "",
            "# Nettoyer",
            "echo Nettoyage...",
            f"del /f /q \"{zip_path}\" 2>nul",
            "rd /s /q \"%TEMP%\\ppplayer_backup\" 2>nul",
            "",
            "# Redémarrer l'application",
            "echo Redémarrage de l'application...",
            f"start \"\" \"PPPlayer.exe\"",
            "",
            "# Supprimer ce script",
            "del /f /q \"%~f0\"",
            "exit"
        ]
        
        return "\n".join(script_lines)
    
    def finalize_preparation(self):
        """Finalise la préparation et demande de fermer l'application"""
        if not self.is_running or not self.window:
            return
            
        self.progress.stop()
        
        result = messagebox.askyesno("Mise à jour prête", 
                                    "La mise à jour est prête à être installée.\n\n"
                                    "L'application va maintenant se fermer pour appliquer les changements.\n"
                                    "Souhaitez-vous continuer?")
        
        if result:
            # Lancer le script de mise à jour et fermer l'application
            self.launch_update_script()
        else:
            self.status_label.config(text="Mise à jour annulée")
            self.check_button.config(state=tk.NORMAL)
            self.update_button.config(state=tk.DISABLED)
    
    def launch_update_script(self):
        """Lance le script de mise à jour et ferme l'application"""
        try:
            script_path = os.path.join(tempfile.gettempdir(), "ppplayer_update.bat")
            
            if os.path.exists(script_path):
                # Lancer le script en arrière-plan
                subprocess.Popen([script_path], shell=True, 
                                creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Fermer l'application
                self.safe_after(1000, self.quit_application)
                
        except Exception as e:
            print(f"❌ Erreur lancement script: {e}")
            self.show_error("Erreur lors du lancement de la mise à jour")
    
    def quit_application(self):
        """Ferme proprement l'application"""
        if self.parent:
            self.parent.quit()
        else:
            self.window.quit()
    
    def download_update(self, release_data):
        """Télécharge la dernière version"""
        try:
            zip_asset = None
            for asset in release_data.get('assets', []):
                if asset['name'].endswith('.zip'):
                    zip_asset = asset
                    break
            
            if not zip_asset:
                return False
            
            download_url = zip_asset['browser_download_url']
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            temp_dir = tempfile.gettempdir()
            zip_path = os.path.join(temp_dir, f"ppplayer_update_{release_data['tag_name']}.zip")
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return zip_path
            
        except Exception as e:
            print(f"❌ Erreur téléchargement: {e}")
            return False
    
    def show_error(self, message):
        if not self.is_running or not self.window or not self.window.winfo_exists():
            return
            
        self.progress.stop()
        self.check_button.config(state=tk.NORMAL)
        self.update_button.config(state=tk.DISABLED)
        self.status_label.config(text="Erreur")
        messagebox.showerror("Erreur", message)