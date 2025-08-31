import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import time
import os
import json
from urllib.parse import urlparse, parse_qs

def clean_youtube_url(url):
    """Nettoie une URL YouTube pour ne garder que le bon lien de la vidéo"""
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

class YouTubeLinkExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Extracteur de Liens YouTube - Gros Fichiers")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Variables
        self.file_path = tk.StringVar()
        self.links_count = tk.IntVar(value=0)
        self.unique_count = tk.IntVar(value=0)
        self.processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Arial", 10))
        
        # Titre
        title_frame = tk.Frame(self.root, bg="#f0f0f0")
        title_frame.pack(pady=10)
        
        tk.Label(title_frame, text="Extracteur de Liens YouTube", 
                font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#333").pack()
        
        tk.Label(title_frame, text="Prend en charge les fichiers HTML de plus de 200 000 lignes", 
                font=("Arial", 10), bg="#f0f0f0", fg="#666").pack()
        
        # Frame de sélection de fichier
        file_frame = tk.LabelFrame(self.root, text="Sélection du fichier", 
                                  font=("Arial", 12, "bold"), bg="#f0f0f0")
        file_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Entry(file_frame, textvariable=self.file_path, 
                font=("Arial", 10), state="readonly", width=70).pack(
                side="left", padx=10, pady=10, fill="x", expand=True)
        
        ttk.Button(file_frame, text="Parcourir", command=self.browse_file).pack(
                side="right", padx=10, pady=10)
        
        # Frame des statistiques
        stats_frame = tk.Frame(self.root, bg="#f0f0f0")
        stats_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(stats_frame, text="Liens trouvés:", 
                font=("Arial", 10, "bold"), bg="#f0f0f0").pack(side="left", padx=10)
        tk.Label(stats_frame, textvariable=self.links_count, 
                font=("Arial", 10), bg="#f0f0f0", fg="green").pack(side="left", padx=5)
        
        tk.Label(stats_frame, text="Liens uniques:", 
                font=("Arial", 10, "bold"), bg="#f0f0f0").pack(side="left", padx=20)
        tk.Label(stats_frame, textvariable=self.unique_count, 
                font=("Arial", 10), bg="#f0f0f0", fg="blue").pack(side="left", padx=5)
        
        # Barre de progression
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill="x", padx=20, pady=5)
        
        # Frame des boutons
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        
        self.extract_btn = ttk.Button(button_frame, text="Extraire les liens", 
                                     command=self.start_extraction)
        self.extract_btn.pack(side="left", padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="Sauvegarder les liens", 
                                  command=self.save_links, state="disabled")
        self.save_btn.pack(side="left", padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Effacer les résultats", 
                                   command=self.clear_results)
        self.clear_btn.pack(side="left", padx=5)
        
        # Zone de texte pour les résultats
        results_frame = tk.LabelFrame(self.root, text="Liens YouTube trouvés", 
                                     font=("Arial", 12, "bold"), bg="#f0f0f0")
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, 
                                                    font=("Consolas", 9))
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Prêt")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief="sunken", anchor="w", bg="#f0f0f0", fg="#555")
        status_bar.pack(side="bottom", fill="x")
        
        # Stockage des liens
        self.all_links = []
        self.unique_links = []
        
    def browse_file(self):
        if self.processing:
            messagebox.showwarning("En cours", "Veuillez attendre la fin de l'extraction.")
            return
            
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier HTML",
            filetypes=[("Fichiers HTML", "*.html"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            self.file_path.set(file_path)
            self.clear_results()
            self.update_status(f"Fichier sélectionné: {os.path.basename(file_path)}")
    
    def start_extraction(self):
        if not self.file_path.get():
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner un fichier.")
            return
            
        if self.processing:
            return
            
        # Démarrer l'extraction dans un thread séparé
        self.processing = True
        self.extract_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.progress.start()
        self.update_status("Extraction en cours...")
        
        thread = threading.Thread(target=self.extract_links)
        thread.daemon = True
        thread.start()
        
        # Vérifier la fin du thread
        self.check_thread(thread)
    
    def check_thread(self, thread):
        if thread.is_alive():
            self.root.after(100, lambda: self.check_thread(thread))
        else:
            self.processing = False
            self.extract_btn.config(state="normal")
            self.progress.stop()
            
            if self.all_links:
                self.save_btn.config(state="normal")
                self.update_status(f"Extraction terminée! {len(self.all_links)} liens trouvés, {len(self.unique_links)} uniques.")
            else:
                self.update_status("Aucun lien YouTube trouvé.")
    
    def extract_links(self):
        start_time = time.time()
        file_path = self.file_path.get()
        
        try:
            # Compiler le pattern regex pour les URLs YouTube
            pattern = re.compile(
                r'https?://(?:www\.)?(?:(?:music\.)?youtube\.com/(?:watch\?v=|embed/)|youtu\.be/)[^\"\'\s<>]+', 
                re.IGNORECASE
            )
            
            # Lire le fichier par chunks pour gérer les gros fichiers
            chunk_size = 1024 * 1024  # 1MB chunks
            links_found = []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                chunk_number = 0
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Trouver les liens dans ce chunk
                    matches = pattern.findall(chunk)
                    links_found.extend(matches)
                    
                    chunk_number += 1
                    # Mettre à jour le statut occasionnellement
                    if chunk_number % 10 == 0:
                        self.update_status(f"Extraction en cours... {chunk_number} chunks traités")
            
            # Mettre à jour l'interface
            self.all_links = links_found
            self.unique_links = list(set(links_found))
            
            # Mettre à jour les compteurs
            self.links_count.set(len(self.all_links))
            self.unique_count.set(len(self.unique_links))
            
            # Afficher les premiers liens
            self.results_text.delete(1.0, tk.END)
            for i, link in enumerate(self.unique_links[:50]):  # Afficher seulement les 50 premiers
                self.results_text.insert(tk.END, f"{i+1}. {link}\n")
            
            if len(self.unique_links) > 50:
                self.results_text.insert(tk.END, f"\n... et {len(self.unique_links) - 50} autres liens")
            
            end_time = time.time()
            print(f"Temps d'exécution: {end_time - start_time:.2f} secondes")
            
        except Exception as e:
            self.update_status(f"Erreur: {str(e)}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite: {str(e)}")
    
    def save_links(self):
        if not self.unique_links:
            messagebox.showwarning("Aucun lien", "Aucun lien à sauvegarder.")
            return
            
        save_path = filedialog.asksaveasfilename(
            title="Enregistrer les liens",
            defaultextension=".txt",
            filetypes=[("Fichier texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as file:
                    file.write(f"Liens YouTube extraits le {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    file.write(f"Total: {len(self.unique_links)} liens uniques\n\n")
                    
                    for i, link in enumerate(self.unique_links, 1):
                        file.write(f"{i}. {link}\n")
                
                self.update_status(f"Liens sauvegardés dans: {save_path}")
                messagebox.showinfo("Succès", f"{len(self.unique_links)} liens sauvegardés avec succès!")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.links_count.set(0)
        self.unique_count.set(0)
        self.all_links = []
        self.unique_links = []
        self.save_btn.config(state="disabled")
        self.update_status("Prêt")
    
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

def extract_youtube_links_from_html(html_file_path):
    """
    Fonction utilitaire pour extraire les liens YouTube depuis un fichier HTML
    
    Args:
        html_file_path: Chemin vers le fichier HTML
        
    Returns:
        list: Liste des liens YouTube uniques trouvés
    """
    try:
        # Compiler le pattern regex pour les URLs YouTube
        pattern = re.compile(
            r'https?://(?:www\.)?(?:(?:music\.)?youtube\.com/(?:watch\?v=|embed/)|youtu\.be/)[^\"\'\s<>]+', 
            re.IGNORECASE
        )
        
        # Lire le fichier par chunks pour gérer les gros fichiers
        chunk_size = 1024 * 1024  # 1MB chunks
        links_found = []
        
        with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                
                # Trouver les liens dans ce chunk
                matches = pattern.findall(chunk)
                links_found.extend(matches)
        
        # Nettoyer et retourner les liens uniques
        cleaned_links = [clean_youtube_url(link) for link in links_found]
        unique_links = list(set(cleaned_links))
        return unique_links
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des liens: {str(e)}")
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeLinkExtractor(root)
    root.mainloop()
    
# C:\Users\olivi\Downloads\Vidéos _J'aime_ - YouTube 1100