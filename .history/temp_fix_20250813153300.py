# Script temporaire pour nettoyer le fichier main.py

# Lire le fichier
with open(r'c:\Users\olivi\kDrive\projets\loisir\music_player\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trouver les lignes à supprimer (du code orphelin dans _search_artist_videos)
start_line = None
end_line = None

for i, line in enumerate(lines):
    if 'def _search_artist_videos(self):' in line and '# Vérifier si la recherche a été annulée' in lines[i+1]:
        start_line = i
        print(f"Début du code orphelin trouvé à la ligne {i+1}")
    elif start_line is not None and 'def _search_artist_videos(self):' in line and 'maintenant redirige vers' in lines[i+1]:
        end_line = i
        print(f"Fin du code orphelin trouvée à la ligne {i}")
        break

if start_line is not None and end_line is not None:
    # Supprimer les lignes orphelines
    new_lines = lines[:start_line] + lines[end_line:]
    
    # Écrire le fichier nettoyé
    with open(r'c:\Users\olivi\kDrive\projets\loisir\music_player\main.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Code orphelin supprimé (lignes {start_line+1} à {end_line})")
else:
    print("Code orphelin non trouvé")