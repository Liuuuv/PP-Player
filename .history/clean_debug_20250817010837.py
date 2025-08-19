import re

# Lire le fichier
with open(r'c:\Users\olivi\kDrive\projets\loisir\music_player\search_tab\results.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Patterns à supprimer (lignes de debug orphelines)
patterns_to_remove = [
    r'^\s+Widgets dans youtube_results_frame.*$',
    r'^\s+Suppression du.*$',
    r'^\s+attribut.*supprimé.*$',
    r'^\s+.*existe, destruction.*$',
    r'^\s+.*détruit.*$',
    r'^\s+.*remis à None.*$',
    r'^\s+Conservation du widget.*$',
    r'^\s+Erreur lors.*$',
    r'^\s+Nettoyage des frames.*$',
    r'^\s+Vérification et affichage.*$',
    r'^\s+thumbnail_frame.*$',
    r'^\s+Programmation de handle.*$',
    r'^\s+=== FIN.*$',
    r'^\s+ERREUR DANS.*$',
    r'^\s+Restauration de l.*état.*$',
    r'^\s+Grande scrollregion.*$',
    r'^\s+Application de la position.*$',
    r'^\s+Scrollregion actuelle.*$',
    r'^\s+Position de scroll restaurée.*$',
    r'^\s+Canvas non disponible.*$',
    r'^\s+Erreur lors de la restauration du scroll.*$'
]

lines = content.split('\n')
cleaned_lines = []

for line in lines:
    should_remove = False
    for pattern in patterns_to_remove:
        if re.match(pattern, line):
            should_remove = True
            break
    
    if not should_remove:
        cleaned_lines.append(line)

# Écrire le fichier nettoyé
with open(r'c:\Users\olivi\kDrive\projets\loisir\music_player\search_tab\results.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(cleaned_lines))

print('Nettoyage terminé')