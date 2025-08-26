import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
import threading
import sys
from packaging import version
import subprocess

class UpdateWindow:
    """Fenêtre de mise à jour autonome pour Tkinter"""
    
    def __init__(self, parent, repo_owner, repo_name, current_version, app_name="No Name declared"):
        """
        Initialise la fenêtre de mise à jour
        
        Args:
            parent: Fenêtre parente
            repo_owner: Propriétaire du dépôt GitHub
            repo_name: Nom du dépôt GitHub
            current_version: Version actuelle de l'application
            app_name: Nom de l'application (optionnel)
        """
        self.parent = parent
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.app_name = app_name
        self.latest_release_info = None
        self.downloaded_file = None
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title(f"Mise à jour - {app_name}")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.grab_set()  # Rend la fenêtre modale
        
        # Centrer la fenêtre
        self.window.transient(parent)
        self.center_window()
        
        # Initialiser l'interface
        self.setup_ui()
        
        # Vérifier les mises à jour automatiquement
        self.check_for_updates()

    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Cadre principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title = ttk.Label(main_frame, text=f"Mise à jour de {self.app_name}", 
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Version actuelle
        version_label = ttk.Label(main_frame, text=f"Version actuelle: {self.current_version}")
        version_label.pack(pady=5)
        
        # Séparateur
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Status des mises à jour
        self.status_label = ttk.Label(main_frame, text="Vérification des mises à jour...", 
                                     relief=tk.SUNKEN, padding=10, wraplength=400)
        self.status_label.pack(pady=10, fill=tk.X)
        
        # Barre de progression
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.pack(pady=5, fill=tk.X)
        
        # Étiquette de progression
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.pack(pady=5)
        
        # Cadre pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Bouton de mise à jour
        self.update_button = ttk.Button(button_frame, text="Mettre à jour", 
                                       command=self.download_update, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour ignorer
        self.ignore_button = ttk.Button(button_frame, text="Ignorer", 
                                       command=self.window.destroy)
        self.ignore_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour redémarrer (caché initialement)
        self.restart_button = ttk.Button(button_frame, text="Redémarrer", 
                                        command=self.restart_application)
        
        # Notes de version
        ttk.Label(main_frame, text="Notes de version:", font=("Arial", 10, "bold")).pack(pady=(20, 5), anchor=tk.W)
        
        # Cadre avec scrollbar pour les notes de version
        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(notes_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget pour les notes de version
        self.release_notes = tk.Text(notes_frame, height=8, width=50, yscrollcommand=scrollbar.set)
        self.release_notes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.release_notes.insert("1.0", "Les notes de version apparaîtront ici...")
        self.release_notes.config(state=tk.DISABLED)
        
        # Configurer la scrollbar
        scrollbar.config(command=self.release_notes.yview)

    def check_for_updates(self):
        """Démarrer la vérification des mises à jour"""
        thread = threading.Thread(target=self._check_for_updates_thread)
        thread.daemon = True
        thread.start()

    def _check_for_updates_thread(self):
        """Thread pour vérifier les mises à jour"""
        try:
            self._update_status("Vérification des mises à jour...", 25)
            
            # Récupérer les informations de la dernière release
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                self._update_status("Impossible de vérifier les mises à jour.", 100)
                return
                
            self.latest_release_info = response.json()
            latest_version = self.latest_release_info['tag_name'].lstrip('v')
            
            self._update_status("Comparaison des versions...", 50)
            
            # Comparer les versions
            if version.parse(latest_version) > version.parse(self.current_version):
                self._update_status(f"Version {latest_version} disponible!", 75, True)
            else:
                self._update_status("Votre application est à jour.", 100)
                
        except Exception as e:
            self._update_status(f"Erreur: {str(e)}", 100)

    def _update_status(self, message, progress, update_available=False):
        """Met à jour le statut (à appeler depuis le thread principal)"""
        def update():
            self.status_label.config(text=message)
            self.progress_bar["value"] = progress
            
            if update_available:
                self.update_button.config(state=tk.NORMAL)
                
                # Afficher les notes de version
                if self.latest_release_info:
                    self.release_notes.config(state=tk.NORMAL)
                    self.release_notes.delete("1.0", tk.END)
                    self.release_notes.insert("1.0", self.latest_release_info.get('body', 'Aucune note de version.'))
                    self.release_notes.config(state=tk.DISABLED)
        
        # S'assurer que les mises à jour UI se font dans le thread principal
        self.window.after(0, update)

    def download_update(self):
        """Démarrer le téléchargement de la mise à jour"""
        self.update_button.config(state=tk.DISABLED)
        self.ignore_button.config(state=tk.DISABLED)
        self._update_status("Préparation du téléchargement...", 0)
        
        thread = threading.Thread(target=self._download_update_thread)
        thread.daemon = True
        thread.start()

    def _download_update_thread(self):
        """Thread pour télécharger la mise à jour"""
        try:
            if not self.latest_release_info:
                self._update_status("Aucune information de mise à jour.", 100)
                return
            
            # Trouver le premier asset exécutable
            download_url = None
            asset_name = None
            for asset in self.latest_release_info['assets']:
                if asset['name'].endswith(('.exe', '.msi', '.dmg', '.deb', '.AppImage')):
                    download_url = asset['browser_download_url']
                    asset_name = asset['name']
                    break
            
            if not download_url:
                self._update_status("Aucun fichier executable trouvé.", 100)
                return
            
            # Télécharger le fichier
            local_filename = os.path.join(os.getcwd(), asset_name)
            
            self._update_progress(0, "Début du téléchargement...")
            
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            if total_size > 0:
                                progress = int((downloaded_size / total_size) * 100)
                                self._update_progress(progress, f"Téléchargement... {progress}%")
            
            self.downloaded_file = local_filename
            self._update_progress(100, "Téléchargement terminé!")
            self._download_finished(True, local_filename)
            
        except Exception as e:
            self._download_finished(False, f"Erreur lors du téléchargement: {str(e)}")

    def _update_progress(self, progress, message):
        """Met à jour la progression (à appeler depuis le thread principal)"""
        def update():
            self.progress_bar["value"] = progress
            self.progress_label.config(text=message)
        
        self.window.after(0, update)

    def _download_finished(self, success, message):
        """Quand le téléchargement est terminé (à appeler depuis le thread principal)"""
        def update():
            if success:
                self.status_label.config(text="Mise à jour téléchargée. Redémarrez pour appliquer.")
                
                # Cacher le bouton de mise à jour et afficher le bouton de redémarrage
                self.update_button.pack_forget()
                self.restart_button.pack(side=tk.LEFT, padx=5)
            else:
                self.status_label.config(text=message)
                self.update_button.config(state=tk.NORMAL)
                self.ignore_button.config(state=tk.NORMAL)
                messagebox.showerror("Erreur", message)
        
        self.window.after(0, update)

    def restart_application(self):
        """Redémarrer l'application avec le nouveau fichier"""
        if self.downloaded_file and os.path.exists(self.downloaded_file):
            try:
                # Lancer le nouveau fichier
                subprocess.Popen([self.downloaded_file])
                # Fermer l'application actuelle
                self.parent.quit()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de redémarrer: {str(e)}")
        else:
            messagebox.showerror("Erreur", "Fichier de mise à jour introuvable.")


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer une fenêtre principale exemple
    root = tk.Tk()
    root.title("Mon Application Tkinter")
    root.geometry("400x300")
    
    # Ajouter du contenu à la fenêtre principale
    label = ttk.Label(root, text="Ceci est mon application principale", font=("Arial", 16))
    label.pack(pady=50)
    
    button = ttk.Button(root, text="Vérifier les mises à jour", 
                       command=lambda: UpdateWindow(
                           root, 
                           repo_owner="votre-username", 
                           repo_name="votre-repo", 
                           current_version="1.0.0",
                           app_name="Mon Application"
                       ))
    button.pack(pady=20)
    
    # Démarrer l'application
    root.mainloop()