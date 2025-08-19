# Fonctions communes pour la gestion des pages d'artiste

# Import centralisé depuis __init__.py
from __init__ import *

# Importer les modules spécialisés
from artist_tab import songs, releases, playlists

def _add_artist_playlist_result(self, playlist, index, container, target_tab="sorties"):
        """Ajoute une playlist dans l'onglet Sorties ou Playlists avec double-clic pour voir le contenu"""
        try:
            title = playlist.get('title', 'Sans titre')
            # Essayer plusieurs champs pour le nombre de vidéos
            playlist_count = (playlist.get('playlist_count', 0) or 
                            playlist.get('video_count', 0) or
                            playlist.get('entry_count', 0) or
                            len(playlist.get('entries', [])))
            url = playlist.get('url', '')
            
            # Le nombre de vidéos n'est pas disponible avec extract_flat=True
            # On va le récupérer en arrière-plan
            
            # Frame principal - même style que les résultats normaux
            result_frame = tk.Frame(
                container,
                bg='#4a4a4a',
                relief='flat',
                bd=1,
                highlightbackground='#555555',
                highlightthickness=1
            )
            result_frame.pack(fill="x", padx=3, pady=1)  # Espacement réduit
            
            # Configuration de la grille (plus compact avec 2 lignes pour titre+count)
            result_frame.columnconfigure(0, minsize=60, weight=0)  # Miniature plus petite
            result_frame.columnconfigure(1, weight=1)              # Titre et nombre de vidéos
            result_frame.rowconfigure(0, minsize=50, weight=0)     # Hauteur augmentée pour 2 lignes
            
            # Miniature avec icône playlist (taille adaptative)
            thumbnail_label = tk.Label(
                result_frame,
                bg='#4a4a4a',
                text="📁",  # Icône dossier pour playlist
                fg='white',
                anchor='center',
                font=('TkDefaultFont', 12)
            )
            thumbnail_label.grid(row=0, column=0, sticky='nsew', padx=(5, 5), pady=3)
            
            # Charger la miniature en arrière-plan
            self._load_artist_thumbnail(playlist, thumbnail_label)
            
            # Titre et nombre de vidéos (dans une frame verticale)
            text_frame = tk.Frame(result_frame, bg='#4a4a4a')
            text_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 5), pady=3)
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)
            text_frame.rowconfigure(1, weight=0)
            
            # Tronquer le titre intelligemment selon la largeur en pixels
            from tools import _truncate_text_for_display
            display_title = _truncate_text_for_display(self, title, max_width_pixels=200, font_size=8)
            
            title_label = tk.Label(
                text_frame,
                text=display_title,
                bg='#4a4a4a',
                fg='white',
                font=('TkDefaultFont', 8),  # Police plus petite
                anchor='w',
                justify='left'
            )
            title_label.grid(row=0, column=0, sticky='ew', pady=(1, 0))
            
            # Nombre de musiques sous le titre (initialement "Chargement...")
            count_label = tk.Label(
                text_frame,
                text="Chargement...",
                bg='#4a4a4a',
                fg='#aaaaaa',
                font=('TkDefaultFont', 7),
                anchor='w',
                justify='left'
            )
            count_label.grid(row=1, column=0, sticky='ew', pady=(0, 1))
            
            # Charger le nombre de vidéos en arrière-plan (après création du label)
            self._load_playlist_count(playlist, count_label)
            
            # Stocker les données playlist
            result_frame.playlist_data = playlist
            result_frame.title_label = title_label
            result_frame.count_label = count_label
            result_frame.thumbnail_label = thumbnail_label
            
            # Événements de clic (double-clic pour voir le contenu de la playlist)
            def on_playlist_double_click(event, frame=result_frame):
                self._show_playlist_content(frame.playlist_data, target_tab)
            
            # Bindings pour le double-clic (inclure text_frame pour que le titre soit cliquable)
            result_frame.bind("<Double-Button-1>", on_playlist_double_click)
            title_label.bind("<Double-Button-1>", on_playlist_double_click)
            thumbnail_label.bind("<Double-Button-1>", on_playlist_double_click)
            count_label.bind("<Double-Button-1>", on_playlist_double_click)
            text_frame.bind("<Double-Button-1>", on_playlist_double_click)
            
            # Effet hover
            def on_enter(event):
                result_frame.configure(bg='#5a5a5a')
                title_label.configure(bg='#5a5a5a')
                thumbnail_label.configure(bg='#5a5a5a')
                count_label.configure(bg='#5a5a5a')
                text_frame.configure(bg='#5a5a5a')
            
            def on_leave(event):
                result_frame.configure(bg='#4a4a4a')
                title_label.configure(bg='#4a4a4a')
                thumbnail_label.configure(bg='#4a4a4a')
                count_label.configure(bg='#4a4a4a')
                text_frame.configure(bg='#4a4a4a')
            
            # Bindings pour l'effet hover (inclure text_frame)
            for widget in [result_frame, title_label, thumbnail_label, count_label, text_frame]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
            
            # Tooltip avec informations
            tooltip_text = f"Playlist: {title}\nDouble-clic pour voir le contenu"
            if playlist_count > 0:
                tooltip_text += f"\n{playlist_count} vidéos"
            create_tooltip(title_label, tooltip_text)
            
        except Exception as e:
            print(f"Erreur lors de l'ajout de la playlist artiste: {e}")