from __init__ import*

class Subtitles:
    def __init__(self, music_player):
        self.music_player = music_player
        
        self.subtitles_label = None
        self.loaded_subtitles = None
        self.subtitles_enabled = False
    
    def parse_srt(self, srt_file):
        """Parse le fichier SRT"""
        subtitles = []
        try:
            with open(srt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\d+\n|\n*$)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for match in matches:
                index, start_str, end_str, text = match
                text = text.strip().replace('\n', ' ')
                
                # Convertir en secondes
                start_seconds = self.srt_to_seconds(start_str)
                end_seconds = self.srt_to_seconds(end_str)
                
                subtitles.append({
                    'start': start_seconds,
                    'end': end_seconds,
                    'text': text
                })
            
            return subtitles
            
        except Exception as e:
            print(f"Erreur parsing SRT: {e}")
            return []
    
    def srt_to_seconds(self, time_str):
        """Convertit le temps SRT en secondes"""
        try:
            h, m, s_ms = time_str.split(':')
            s, ms = s_ms.split(',')
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except:
            return 0
    
    def get_japanese_subtitles(self, url):
        """
        Récupère spécifiquement les sous-titres japonais
        """
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'update': True
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Chercher les sous-titres japonais
                ja_subtitles = None
                
                # D'abord dans les sous-titres manuels
                if info.get('subtitles') and 'ja' in info['subtitles']:
                    ja_subtitles = info['subtitles']['ja']
                    print("Sous-titres japonais manuels trouvés")
                
                # Sinon dans les sous-titres auto-générés
                # elif info.get('automatic_captions') and 'ja' in info['automatic_captions']:
                #     ja_subtitles = info['automatic_captions']['ja']
                #     print("Sous-titres japonais auto-générés trouvés")
                
                if not ja_subtitles:
                    print("Aucun sous-titre japonais disponible")
                    # Afficher les langues disponibles
                    available_manual = list(info.get('subtitles', {}).keys())
                    available_auto = list(info.get('automatic_captions', {}).keys())
                    print(f"Sous-titres manuels: {available_manual}")
                    print(f"Sous-titres auto: {available_auto}")
                    return []
                
                # Trouver l'URL des sous-titres JSON
                subtitle_url = None
                for sub_format in ja_subtitles:
                    if sub_format.get('ext') == 'json3' or sub_format.get('url', '').endswith('.json3'):
                        subtitle_url = sub_format.get('url')
                        break
                
                if not subtitle_url:
                    # Prendre la première URL disponible
                    subtitle_url = ja_subtitles[0].get('url')
                
                if not subtitle_url:
                    print("URL des sous-titres non trouvée")
                    return []
                
                print(f"Téléchargement des sous-titres japonais...")
                
                # Ajouter un délai pour éviter le rate limiting
                time.sleep(1)
                
                # Télécharger les sous-titres
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(subtitle_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Parser le JSON
                data = json.loads(response.text)
                events = data.get('events', [])
                subtitles = []
                
                for event in events:
                    if 'tStartMs' in event and 'dDurationMs' in event and 'segs' in event:
                        start_ms = event['tStartMs']
                        duration_ms = event['dDurationMs']
                        end_ms = start_ms + duration_ms
                        
                        # Extraire le texte japonais
                        text = ''.join(seg.get('utf8', '') for seg in event['segs'] if seg.get('utf8'))
                        
                        if text.strip():
                            subtitles.append({
                                'text': text.strip(),
                                'start_time': self.format_time(start_ms),
                                'end_time': self.format_time(end_ms),
                                'start_ms': start_ms,
                                'end_ms': end_ms,
                                'duration_ms': duration_ms
                            })
                
                print(f"{len(subtitles)} sous-titres japonais trouvés")
                return subtitles
                
        except Exception as e:
            print(f"Erreur: {e}")
            return []
    
    def format_time(self, milliseconds):
        """
        Convertit des millisecondes en format HH:MM:SS,mmm
        """
        seconds = milliseconds / 1000
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((milliseconds % 1000))
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def save_subtitles_to_srt(self, subtitles, filename):
        """
        Sauvegarde les sous-titres en format SRT
        """
        if filename.endswith(".mp3"):
            filename = filename[:-4]
        file_path = os.path.join(self.music_player.downloads_folder, f"{filename}.srt")
        with open(file_path, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles, 1):
                f.write(f"{i}\n")
                f.write(f"{sub['start_time']} --> {sub['end_time']}\n")
                f.write(f"{sub['text']}\n\n")
        print(f"Sous-titres sauvegardés dans {file_path}")
    
    def show_subtitles(self):
        """Affiche les sous-titres"""
        print("Affichage des sous-titres")
        self.subtitles_label = tk.Label(
            self.music_player.thumbnail_frame,
            text="Sous-titres",
            bg=COLOR_APP_BG,
            fg="white",
            font=("Yu Gothic", 12, "bold"),
            anchor="s"
        )
        width, height = self.music_player.thumbnail_frame.winfo_width(), self.music_player.thumbnail_frame.winfo_height()
        self.subtitles_label.place(x=width//2, y=height-30, anchor="center")
        
        if len(self.music_player.main_playlist) > 0:
            current_song = self.music_player.main_playlist[self.music_player.current_index]
            if self.loaded_subtitles is None:
                srt_file = os.path.join(self.music_player.downloads_folder, current_song.replace(".mp3",".srt"))
                print(srt_file)
                if os.path.exists(srt_file):
                    print(f"Fichier SRT trouvé : {srt_file}")
                    self.loaded_subtitles = self.parse_srt(srt_file)
                else:
                    print(f"Fichier SRT introuvable, on le créé : {srt_file}")
                    metadatas = self.music_player.get_youtube_metadata(current_song)
                    if metadatas is None:
                        print("Sous-titres: Aucun métadonnées disponibles pour le fichier: ", current_song)
                        return

                    url = metadatas.get('url')
                    if url is None:
                        print("Sous-titres: Lien YouTube introuvable")
                        return
                    
                    def dl_and_save_subtitles():
                        subtitles = self.get_japanese_subtitles(url)
                        if subtitles != []:
                            self.save_subtitles_to_srt(subtitles, current_song)
                            srt_file = os.path.join(self.music_player.downloads_folder, current_song.replace(".mp3",".srt"))
                            self.loaded_subtitles = self.parse_srt(srt_file)
                        else:
                            self.subtitles_label.config(text="Aucun sous-titre disponible")
                    
                    threading.Thread(target=dl_and_save_subtitles, daemon=True).start()
    
    def hide_subtitles(self):
        """Masque les sous-titres"""
        print("Masquage des sous-titres")
        if hasattr(self,'subtitles_label'):
            self.subtitles_label.destroy()
            self.subtitles_label = None
    
    def update_subtitles(self, current_time):
        """
        Met à jour les sous-titres en fonction de la position actuelle du lecteur
        """
        # Trouver le sous-titre actuel
        current_sub = None
        if self.loaded_subtitles is None:
            return

        found = False
        for sub in self.loaded_subtitles:
            if sub['start'] <= current_time <= sub['end']:
                current_sub = sub
                found = True
                break
        if not found:
            current_sub = ""
        
        # Afficher le sous-titre
        if current_sub and current_sub != getattr(self, 'last_sub', None):
            # print(f"\n[{current_time:.1f}s] {current_sub['text']}")
            self.subtitles_label.config(text=current_sub['text'])
            self.last_sub = current_sub
        