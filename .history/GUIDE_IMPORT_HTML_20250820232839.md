# Guide d'utilisation - Import de fichiers HTML

## Nouvelle fonctionnalité : Import de liens YouTube depuis un fichier HTML

### Comment utiliser cette fonctionnalité :

1. **Ouvrir la fenêtre d'import** : Cliquez sur "Importer des musiques" dans l'application

2. **Glisser-déposer un fichier HTML** : 
   - Glissez un fichier `.html` directement sur la fenêtre de dialogue
   - La fenêtre passera automatiquement en mode HTML

3. **Configurer les paramètres** :
   - **Durée max (s)** : Durée maximale des vidéos à télécharger (par défaut : 600 secondes = 10 minutes)
     - Mettez `-1` pour aucune limite de durée
   - **Taille des paquets** : Nombre de vidéos téléchargées simultanément (par défaut : 10)
     - Plus petit = moins de charge système, plus lent
     - Plus grand = plus rapide, mais plus de charge système

4. **Cliquer sur "Importer"** : Le processus démarre automatiquement

### Ce qui se passe lors de l'import (traitement par vagues) :

1. **Extraction des liens** : Tous les liens YouTube et YouTube Music sont extraits du fichier HTML
2. **Traitement par vagues** : Le processus se déroule en cycles :
   - 🔍 **Vague 1** : Vérifier les durées des 10 premiers liens
   - ⬇️ **Téléchargement** : Télécharger immédiatement les vidéos valides de cette vague
   - ⏸️ **Pause** : Attendre 10 secondes pour éviter la surcharge
   - 🔍 **Vague 2** : Vérifier les 10 liens suivants
   - ⬇️ **Téléchargement** : Télécharger les vidéos valides...
   - Et ainsi de suite jusqu'à la fin
3. **Rapport JSON final** : Un fichier JSON est créé avec toutes les vidéos non téléchargées

### Fichier JSON de rapport

Le fichier JSON créé contient :
- Le chemin du fichier HTML source
- La date de création du rapport
- Le nombre total de vidéos ignorées
- Pour chaque vidéo ignorée :
  - Titre de la vidéo
  - URL de la vidéo
  - Durée (en secondes)
  - Raison de l'exclusion

**Nom du fichier** : `[nom_fichier_html]_videos_non_telechargees.json`

### Types de liens supportés :
- `https://www.youtube.com/watch?v=...`
- `https://youtube.com/watch?v=...`
- `https://music.youtube.com/watch?v=...`
- `https://youtu.be/...`

### Exemples d'utilisation :

**Cas d'usage typiques :**
- Import de playlists YouTube exportées en HTML
- Import de favoris/likes YouTube sauvegardés
- Import de listes de lecture depuis des pages web

**Paramètres recommandés :**
- **Durée max :**
  - Pour de la musique : `600` secondes (10 minutes)
  - Pour des podcasts courts : `1800` secondes (30 minutes)
  - Pour tout télécharger : `-1` (pas de limite)
- **Taille des paquets :**
  - Pour un système lent : `5` vidéos par paquet
  - Configuration standard : `10` vidéos par paquet
  - Pour un système puissant : `20` vidéos par paquet

### Notes importantes :
- Le processus peut prendre du temps selon le nombre de liens
- Les vidéos déjà téléchargées ne seront pas re-téléchargées
- Le fichier JSON permet de suivre ce qui n'a pas été téléchargé et pourquoi