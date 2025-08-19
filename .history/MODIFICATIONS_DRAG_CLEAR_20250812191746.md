# Modifications du drag et du clear playlist

## Modifications apportées

### 1. Drag gauche ajoute maintenant à la playlist (comme drag droite)

#### Fichier : `drag_drop_handler.py`

**Ligne 98-100** : Modification de la logique de drag gauche
```python
# AVANT
elif dx < -100:
    # Placer en premier dans la queue selon le type d'élément
    self._add_to_queue_first_dragged_item(frame)

# APRÈS
elif dx < -100:
    # Ajouter à la playlist selon le type d'élément (même comportement que drag droite)
    self._add_dragged_item_to_playlist(frame)
```

**Ligne 120-121** : Modification du feedback visuel
```python
# AVANT
elif dx < -100:  # Drag vers la gauche - placer en premier dans la queue
    self._set_frame_colors(frame, '#6a6a4a')  # Jaune-orange pour indiquer "premier dans la queue"

# APRÈS
elif dx < -100:  # Drag vers la gauche - ajouter à la playlist (même comportement)
    self._set_frame_colors(frame, '#4a6a4a')  # Vert pour indiquer l'activation (même couleur que drag droite)
```

### 2. Amélioration de la miniature lors du clear playlist

#### Fichier : `main.py`

**Ligne 521-538** : Modification de `_clear_main_playlist()`
```python
# AVANT
# Afficher une icône musicale par défaut (pas de chanson en cours)
no_song_label = tk.Label(
    self.thumbnail_frame,
    text="♪",
    bg='#3d3d3d',
    fg='#666666',
    font=('Arial', 48)
)
no_song_label.pack(expand=True)

# APRÈS
# Afficher une icône musicale par défaut identique à celle du lancement
no_song_label = tk.Label(
    self.thumbnail_frame,
    text="♪",
    bg='#3d3d3d',
    fg='#666666',
    font=('TkDefaultFont', 60),
    width=300,
    height=300
)
# Pack à gauche sans padding pour coller au bord (comme au lancement)
no_song_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
```

## Comportement résultant

### Drag et drop
- **Drag droite** (`dx > 100`) : Ajoute à la playlist ✅ (inchangé)
- **Drag gauche** (`dx < -100`) : Ajoute à la playlist ✅ (nouveau comportement)
- **Feedback visuel** : Les deux directions montrent maintenant la même couleur verte (#4a6a4a)

### Clear playlist
- **Unload musique** : `pygame.mixer.music.unload()` ✅ (déjà implémenté)
- **Miniature** : Identique à celle du lancement du programme ✅ (nouveau)
  - Police : `('TkDefaultFont', 60)`
  - Taille : `width=300, height=300`
  - Positionnement : `pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)`

## Avantages

1. **Cohérence** : Drag gauche et droite ont maintenant le même comportement
2. **Simplicité** : Plus besoin de se rappeler quelle direction fait quoi
3. **Interface** : La miniature après clear est maintenant identique à celle du lancement
4. **Expérience utilisateur** : Plus intuitive et cohérente

## Tests
Un fichier de test `test_drag_improvements.py` a été créé pour vérifier le bon fonctionnement des modifications.