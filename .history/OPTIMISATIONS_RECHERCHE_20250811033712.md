# Optimisations pour éviter les saccades lors des recherches

## Problèmes identifiés
1. **Trop de threads simultanés** : 5 threads de miniatures causaient une surcharge
2. **Affichage progressif trop lent** : Délai de 100ms entre chaque résultat
3. **Mises à jour fréquentes** : Le statut était mis à jour après chaque résultat
4. **Vérifications de scroll trop fréquentes** : Pas de limitation de fréquence
5. **Appels à `root.update()`** : Causaient des blocages de l'interface

## Optimisations appliquées

### 1. Réduction du nombre de threads de miniatures
- **Avant** : 5 threads simultanés
- **Après** : 2 threads simultanés
- **Impact** : Réduit la charge CPU et les conflits de ressources

### 2. Mode d'affichage rapide
- **Nouveau** : `fast_display_mode = True` par défaut
- **Fonctionnement** : Affiche tous les résultats d'un lot d'un coup au lieu d'un par un
- **Avantage** : Élimine les délais entre les résultats

### 3. Optimisation de l'affichage progressif
- **Avant** : Délai de 100ms entre chaque résultat
- **Après** : Délai de 30ms entre chaque résultat
- **Impact** : Affichage plus fluide en mode progressif

### 4. Limitation des vérifications de scroll
- **Nouveau** : Limitation à une vérification toutes les 200ms
- **Impact** : Évite les appels excessifs lors du scroll

### 5. Remplacement de `root.update()`
- **Avant** : `root.update()` bloquant
- **Après** : `root.update_idletasks()` non-bloquant
- **Impact** : Évite les blocages de l'interface

### 6. Réduction du nombre de résultats
- **Avant** : 20 résultats par recherche
- **Après** : 15 résultats par recherche
- **Impact** : Moins de charge réseau et de traitement

### 7. Chargement différé des miniatures
- **Nouveau** : Délai de 200ms avant le chargement des miniatures
- **Impact** : L'interface s'affiche d'abord, les miniatures se chargent ensuite

### 8. Priorité réduite des threads
- **Nouveau** : Threads de miniatures avec priorité `BELOW_NORMAL`
- **Impact** : N'interfèrent pas avec l'interface utilisateur

### 9. Mise à jour optimisée du canvas
- **Nouveau** : Utilisation de `root.after_idle()` pour les mises à jour
- **Impact** : Mises à jour différées quand l'interface est libre

## Fonctions utilitaires ajoutées

### `toggle_display_mode()`
Permet de basculer entre le mode rapide et progressif

### `optimize_search_performance()`
Active le mode haute performance :
- 1 seul thread de miniature
- Mode rapide activé
- 10 résultats maximum
- Délai de recherche augmenté à 500ms

### `restore_default_performance()`
Restaure les paramètres par défaut

## Utilisation

Les optimisations sont **activées par défaut**. Pour les personnaliser :

```python
# Activer le mode haute performance
player.optimize_search_performance()

# Basculer le mode d'affichage
player.toggle_display_mode()

# Restaurer les paramètres par défaut
player.restore_default_performance()
```

## Résultats attendus

- **Réduction significative des saccades** lors des recherches
- **Interface plus réactive** pendant le chargement
- **Utilisation CPU réduite** grâce aux threads limités
- **Expérience utilisateur améliorée** avec un affichage plus fluide