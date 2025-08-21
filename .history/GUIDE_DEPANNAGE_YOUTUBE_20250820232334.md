# 🔧 Guide de dépannage - Erreurs YouTube

## 🚨 Erreurs courantes et solutions

### Erreur 403 Forbidden
**Symptômes :** `HTTP Error 403: Forbidden`

**Causes possibles :**
- YouTube a renforcé ses protections anti-bot
- Version obsolète de yt-dlp
- Trop de requêtes simultanées

**Solutions :**
1. **Mettre à jour yt-dlp** (recommandé) :
   ```bash
   python update_ytdlp.py
   ```
   
2. **Réduire la taille des paquets** :
   - Dans l'interface, mettre "Taille des paquets" à `3` ou `5`
   - Cela réduit la charge sur les serveurs YouTube

3. **Attendre et réessayer** :
   - YouTube peut temporairement bloquer les requêtes
   - Attendre 10-15 minutes puis réessayer

### Erreur "Requested format is not available"
**Symptômes :** `Requested format is not available`

**Causes possibles :**
- Vidéo avec restrictions de format
- Vidéo en direct ou premium

**Solutions :**
1. **Automatique** : Le système utilise maintenant des formats plus flexibles
2. **Vérifier le rapport JSON** : Les vidéos problématiques sont listées avec la raison

### Vidéos privées/supprimées
**Symptômes :** Vidéos qui ne se téléchargent pas

**Solutions :**
1. **Vérifier le rapport JSON** : `[nom_fichier]_videos_non_telechargees.json`
2. **Nettoyer la liste** : Supprimer les liens morts du fichier HTML source

## 🛠️ Améliorations implémentées

### Options robustes de téléchargement
- ✅ Formats multiples : `m4a`, `webm`, `mp3`
- ✅ Retry automatique : 5 tentatives avec délai progressif
- ✅ Headers HTTP complets pour éviter la détection
- ✅ Clients multiples : Android, Web, iOS

### Gestion d'erreurs améliorée
- ✅ Catégorisation des erreurs dans le rapport JSON
- ✅ Continuation automatique en cas d'erreur
- ✅ Messages d'erreur explicites

### Téléchargement par paquets
- ✅ Évite la surcharge des serveurs YouTube
- ✅ Pauses intelligentes entre les téléchargements
- ✅ Taille configurable selon la performance du système

## 📊 Paramètres recommandés selon les problèmes

### Si beaucoup d'erreurs 403 :
- **Taille des paquets** : `3`
- **Durée max** : `300` (5 minutes) pour commencer
- **Action** : Mettre à jour yt-dlp d'abord

### Si système lent :
- **Taille des paquets** : `5`
- **Durée max** : `600` (10 minutes)

### Si système rapide et stable :
- **Taille des paquets** : `15-20`
- **Durée max** : `-1` (pas de limite)

## 🔄 Maintenance régulière

### Mise à jour hebdomadaire recommandée :
```bash
python update_ytdlp.py
```

### Nettoyage des fichiers temporaires :
- Supprimer les fichiers `.part` dans le dossier de téléchargement
- Vider le cache du navigateur si vous utilisez des exports HTML récents

## 📞 Si les problèmes persistent

1. **Vérifier la connectivité** : Tester l'accès à YouTube dans le navigateur
2. **Vérifier les logs** : Regarder la console Python pour les erreurs détaillées
3. **Tester avec une seule vidéo** : Utiliser l'import URL simple d'abord
4. **Vérifier l'espace disque** : S'assurer d'avoir assez d'espace libre

---

**💡 Astuce :** Le rapport JSON créé après chaque import contient des informations détaillées sur pourquoi certaines vidéos n'ont pas pu être téléchargées. C'est votre meilleur outil de diagnostic !