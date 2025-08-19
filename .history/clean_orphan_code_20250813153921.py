# Script pour nettoyer le code orphelin dans main.py

# Lire le fichier
with open(r'c:\Users\olivi\kDrive\projets\loisir\music_player\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_until_next_def = False

for i, line in enumerate(lines):
    # Si on trouve une redirection avec du code orphelin après
    if 'return artist_tab.' in line and i + 1 < len(lines) and lines[i+1].strip().startswith('try:'):
        # Garder la ligne de redirection
        new_lines.append(line)
        # Commencer à ignorer le code orphelin
        skip_until_next_def = True
    elif skip_until_next_def:
        # Chercher la prochaine fonction (def ) ou classe (class )
        if line.strip().startswith('def ') or line.strip().startswith('class '):
            skip_until_next_def = False
            new_lines.append(line)
        # Ignorer les lignes orphelines
    else:
        new_lines.append(line)

# Écrire le fichier nettoyé
with open(r'c:\Users\olivi\kDrive\projets\loisir\music_player\main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Code orphelin nettoyé")