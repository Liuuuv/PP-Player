# Script pour nettoyer les fonctions d'artiste orphelines

# Lire le fichier
with open(r'c:\Users\olivi\kDrive\projets\loisir\music_player\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fonctions à nettoyer
functions_to_clean = [
    '_search_artist_videos_with_id',
    '_search_artist_releases_with_id'
]

new_lines = []
skip_until_next_def = False
current_function = None

for i, line in enumerate(lines):
    # Vérifier si on commence une fonction qui a été redirigée
    for func_name in functions_to_clean:
        if f'def {func_name}(self):' in line:
            # Chercher la ligne avec "return artist_tab"
            next_line_idx = i + 1
            if next_line_idx < len(lines) and 'return artist_tab' in lines[next_line_idx]:
                # Garder cette ligne et la suivante (la redirection)
                new_lines.append(line)
                new_lines.append(lines[next_line_idx])
                # Marquer qu'on doit ignorer le reste jusqu'à la prochaine fonction
                skip_until_next_def = True
                current_function = func_name
                break
    else:
        # Si on est en mode "skip"
        if skip_until_next_def:
            # Chercher la prochaine fonction (def )
            if line.strip().startswith('def ') and current_function not in line:
                skip_until_next_def = False
                current_function = None
                new_lines.append(line)
            # Sinon, ignorer cette ligne
        else:
            new_lines.append(line)

# Écrire le fichier nettoyé
with open(r'c:\Users\olivi\kDrive\projets\loisir\music_player\main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fonctions d'artiste nettoyées")