#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour analyser les fonctions artist_* dans main.py et identifier celles qui peuvent être supprimées
"""

import os
import re

def find_function_calls(directory, function_name):
    """Trouve tous les appels à une fonction dans le répertoire"""
    calls = []
    
    for root, dirs, files in os.walk(directory):
        # Ignorer les dossiers non pertinents
        if any(ignore in root for ignore in ['artist_tab', '.history', '__pycache__', '.git']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Chercher les appels directs à la fonction
                    patterns = [
                        rf'self\.{function_name}\(',
                        rf'\.{function_name}\(',
                        rf'{function_name}\('
                    ]
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Trouver le numéro de ligne
                            line_num = content[:match.start()].count('\n') + 1
                            line_content = content.split('\n')[line_num - 1].strip()
                            calls.append({
                                'file': filepath,
                                'line': line_num,
                                'content': line_content
                            })
                            
                except Exception as e:
                    print(f"Erreur lors de la lecture de {filepath}: {e}")
    
    return calls

def analyze_artist_functions():
    """Analyse toutes les fonctions artist_* dans main.py"""
    
    # Liste des fonctions artist_* dans main.py
    artist_functions = [
        '_show_artist_content',
        '_create_artist_tabs',
        '_search_artist_content_async',
        '_search_artist_content',
        '_find_artist_channel_id',
        '_on_channel_id_found',
        '_on_channel_id_error',
        '_start_parallel_searches',
        '_show_error_in_tabs',
        '_cancel_artist_search',
        '_update_loading_messages',
        '_display_results_in_batches',
        '_search_artist_videos_with_id',
        '_search_artist_videos',
        '_search_artist_releases_with_id',
        '_search_artist_releases',
        '_search_artist_releases_old',
        '_search_artist_playlists_with_id',
        '_search_artist_playlists',
        '_display_artist_videos',
        '_display_artist_releases',
        '_display_artist_playlists',
        '_add_artist_result',
        '_load_artist_thumbnail',
        '_load_playlist_count',
        '_add_artist_playlist_result',
        '_show_playlist_content',
        '_show_playlist_loading',
        '_display_playlist_content',
        '_return_to_releases',
        '_return_to_playlists',
        '_show_playlist_error',
        '_return_to_search'
    ]
    
    project_dir = r'c:\Users\olivi\kDrive\projets\loisir\music_player'
    
    print("Analyse des fonctions artist_* dans main.py")
    print("=" * 60)
    
    unused_functions = []
    used_functions = []
    
    for func in artist_functions:
        print(f"\nAnalyse de {func}:")
        calls = find_function_calls(project_dir, func)
        
        if not calls:
            print("  ✗ Aucun appel trouvé - PEUT ÊTRE SUPPRIMÉE")
            unused_functions.append(func)
        else:
            print(f"  ✓ {len(calls)} appel(s) trouvé(s):")
            used_functions.append(func)
            for call in calls:
                rel_path = os.path.relpath(call['file'], project_dir)
                print(f"    - {rel_path}:{call['line']} → {call['content']}")
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ:")
    print(f"Fonctions utilisées: {len(used_functions)}")
    print(f"Fonctions inutilisées: {len(unused_functions)}")
    
    if unused_functions:
        print("\nFonctions qui peuvent être supprimées:")
        for func in unused_functions:
            print(f"  - {func}")
    
    if used_functions:
        print("\nFonctions qui doivent être conservées:")
        for func in used_functions:
            print(f"  - {func}")
    
    return unused_functions, used_functions

if __name__ == "__main__":
    unused, used = analyze_artist_functions()