# 🎵 Pipi Player - Guide d'utilisation

## 🚀 Démarrage rapide

### Méthode recommandée
```bash
python run.py
```

### Méthodes alternatives
```bash
python main_new.py
# ou
python launch.py
```

## 📁 Structure du projet

```
music_player/
├── 🚀 run.py                    # Script de démarrage recommandé
├── 🚀 main_new.py              # Point d'entrée principal
├── ⚠️  main.py                 # Ancien fichier (avec redirection)
├── 📚 main_old.py              # Référence de l'ancien code
├── 🧪 test_imports.py          # Test des imports
├── 📋 requirements.txt         # Dépendances
├── 📖 README_REFACTORING.md    # Documentation de la refactorisation
├── 📖 GUIDE_UTILISATION.md     # Ce guide
├── config/                     # Configuration
│   ├── constants.py           # Constantes globales
│   ├── settings.py            # Paramètres utilisateur
│   └── default_config.json    # Configuration par défaut
├── core/                      # Logique métier
│   ├── player.py             # Lecteur audio
│   ├── playlist.py           # Gestion des playlists
│   └── audio_utils.py        # Utilitaires audio
├── ui/                       # Interface utilisateur
│   ├── main_window.py        # Fenêtre principale
│   ├── controls.py           # Contrôles de lecture
│   ├── search_tab.py         # Onglet recherche
│   ├── library_tab.py        # Onglet bibliothèque
│   └── styles.py             # Styles et thèmes
├── services/                 # Services externes
│   ├── youtube_service.py    # YouTube
│   ├── file_service.py       # Gestion fichiers
│   └── search_service.py     # Recherche locale
└── utils/                    # Utilitaires
    └── keyboard.py           # Raccourcis clavier
```

## 🎮 Fonctionnalités

### 🎵 Lecture audio
- ▶️ Lecture/Pause (Barre d'espace)
- ⏭️ Piste suivante (Ctrl + →)
- ⏮️ Piste précédente (Ctrl + ←)
- 🔊 Contrôle du volume (Ctrl + ↑/↓)
- 🔁 Modes de boucle (désactivé/playlist/chanson)
- 🔀 Mode aléatoire

### 🔍 Recherche YouTube
- Recherche en temps réel
- Téléchargement audio MP3
- Ajout automatique à la playlist

### 📚 Bibliothèque
- Gestion des fichiers téléchargés
- Création de playlists personnalisées
- Recherche locale dans les fichiers
- Ajout de fichiers depuis l'ordinateur

### ⚙️ Configuration
- Volume global et par fichier
- Sauvegarde automatique des paramètres
- Thème sombre

## 🎯 Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Espace` | Lecture/Pause |
| `Ctrl + →` | Piste suivante |
| `Ctrl + ←` | Piste précédente |
| `Ctrl + ↑` | Volume + |
| `Ctrl + ↓` | Volume - |

## 📦 Installation des dépendances

```bash
pip install -r requirements.txt
```

### Dépendances principales
- `pygame` - Lecture audio
- `tkinter` - Interface graphique (inclus avec Python)
- `Pillow` - Traitement d'images
- `mutagen` - Métadonnées audio
- `yt-dlp` - Téléchargement YouTube
- `pydub` - Traitement audio
- `numpy` - Calculs numériques

## 🔧 Configuration

### Fichiers de configuration
- `downloads/player_config.json` - Configuration utilisateur
- `downloads/playlists.json` - Playlists sauvegardées
- `config/default_config.json` - Configuration par défaut

### Dossiers créés automatiquement
- `downloads/` - Fichiers téléchargés
- `assets/` - Ressources (icônes, images)

## 🐛 Résolution de problèmes

### L'application ne se lance pas
1. Vérifiez que Python 3.7+ est installé
2. Installez les dépendances : `pip install -r requirements.txt`
3. Utilisez le script de démarrage : `python run.py`

### Erreurs d'import
- Assurez-vous d'être dans le bon répertoire
- Vérifiez que tous les fichiers `__init__.py` sont présents

### Problèmes audio
- Vérifiez que pygame est correctement installé
- Testez avec différents formats audio (MP3, WAV, OGG)

### Téléchargements YouTube
- Vérifiez votre connexion internet
- Mettez à jour yt-dlp : `pip install --upgrade yt-dlp`

## 🔄 Migration depuis l'ancienne version

L'ancienne version (`main.py`) redirige automatiquement vers la nouvelle.
Vos playlists et configurations sont préservées.

## 🎨 Personnalisation

### Thèmes
Les couleurs sont définies dans `config/constants.py`

### Icônes
Placez vos icônes personnalisées dans le dossier `assets/`

### Extensions audio supportées
Modifiez `AUDIO_EXTENSIONS` dans `config/constants.py`

## 📞 Support

En cas de problème :
1. Consultez ce guide
2. Vérifiez les logs d'erreur
3. Testez avec `python test_imports.py`

## 🎉 Profitez de votre musique !

Pipi Player est maintenant plus robuste, modulaire et facile à maintenir.
Bonne écoute ! 🎵