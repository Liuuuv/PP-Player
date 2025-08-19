"""
Service de gestion des fichiers
"""
import os
import shutil
from tkinter import filedialog
from config.constants import AUDIO_EXTENSIONS


class FileService:
    """Service pour la gestion des fichiers audio"""
    
    def __init__(self):
        self.normalized_filenames = {}  # Cache des noms de fichiers normalisés
    
    def select_files(self):
        """Ouvre une boîte de dialogue pour sélectionner des fichiers audio"""
        filetypes = [
            ("Fichiers audio", " ".join(f"*{ext}" for ext in AUDIO_EXTENSIONS)),
            ("MP3", "*.mp3"),
            ("WAV", "*.wav"),
            ("OGG", "*.ogg"),
            ("FLAC", "*.flac"),
            ("M4A", "*.m4a"),
            ("Tous les fichiers", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers audio",
            filetypes=filetypes
        )
        
        return list(files) if files else []
    
    def select_folder(self):
        """Ouvre une boîte de dialogue pour sélectionner un dossier"""
        folder = filedialog.askdirectory(title="Sélectionner un dossier")
        return folder if folder else None
    
    def get_audio_files_from_folder(self, folder_path):
        """Récupère tous les fichiers audio d'un dossier"""
        audio_files = []
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(AUDIO_EXTENSIONS):
                        audio_files.append(os.path.join(root, file))
        except Exception as e:
            print(f"Erreur lecture dossier: {e}")
        
        return audio_files
    
    def is_audio_file(self, filepath):
        """Vérifie si un fichier est un fichier audio supporté"""
        return filepath.lower().endswith(AUDIO_EXTENSIONS)
    
    def file_exists(self, filepath):
        """Vérifie si un fichier existe"""
        return os.path.exists(filepath)
    
    def get_filename(self, filepath):
        """Retourne le nom du fichier sans le chemin"""
        return os.path.basename(filepath)
    
    def get_filename_without_extension(self, filepath):
        """Retourne le nom du fichier sans l'extension"""
        return os.path.splitext(os.path.basename(filepath))[0]
    
    def delete_file(self, filepath):
        """Supprime un fichier"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Erreur suppression fichier: {e}")
        return False
    
    def move_file(self, source, destination):
        """Déplace un fichier"""
        try:
            shutil.move(source, destination)
            return True
        except Exception as e:
            print(f"Erreur déplacement fichier: {e}")
        return False
    
    def copy_file(self, source, destination):
        """Copie un fichier"""
        try:
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            print(f"Erreur copie fichier: {e}")
        return False
    
    def get_file_size(self, filepath):
        """Retourne la taille d'un fichier en octets"""
        try:
            return os.path.getsize(filepath)
        except Exception as e:
            print(f"Erreur taille fichier: {e}")
        return 0
    
    def format_file_size(self, size_bytes):
        """Formate la taille d'un fichier en format lisible"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def normalize_filename(self, filename):
        """Normalise un nom de fichier pour la recherche"""
        if filename in self.normalized_filenames:
            return self.normalized_filenames[filename]
        
        import re
        # Supprimer les caractères spéciaux et convertir en minuscules
        normalized = re.sub(r'[^\w\s-]', '', filename.lower())
        normalized = re.sub(r'[-\s]+', ' ', normalized).strip()
        
        self.normalized_filenames[filename] = normalized
        return normalized
    
    def search_files(self, files, query):
        """Recherche des fichiers par nom"""
        if not query:
            return files
        
        query_normalized = self.normalize_filename(query)
        results = []
        
        for filepath in files:
            filename = self.get_filename(filepath)
            filename_normalized = self.normalize_filename(filename)
            
            if query_normalized in filename_normalized:
                results.append(filepath)
        
        return results
    
    def get_file_info(self, filepath):
        """Retourne les informations d'un fichier"""
        try:
            stat = os.stat(filepath)
            return {
                'name': self.get_filename(filepath),
                'size': stat.st_size,
                'size_formatted': self.format_file_size(stat.st_size),
                'modified': stat.st_mtime,
                'path': filepath
            }
        except Exception as e:
            print(f"Erreur info fichier: {e}")
            return None
    
    def create_directory(self, path):
        """Crée un répertoire s'il n'existe pas"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Erreur création répertoire: {e}")
        return False
    
    def clean_filename(self, filename):
        """Nettoie un nom de fichier pour le système de fichiers"""
        import re
        # Supprimer les caractères interdits
        cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Limiter la longueur
        if len(cleaned) > 200:
            cleaned = cleaned[:200]
        return cleaned.strip()