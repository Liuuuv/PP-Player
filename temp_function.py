def _check_and_unload_items(self, current_index):
        """Vérifie et décharge les éléments qui sont trop loin de l'index actuel"""
        try:
            if not hasattr(self, 'playlist_container') or not self.playlist_container.winfo_exists():
                return
                
            # Vérifier si on a des éléments à décharger
            children = self.playlist_container.winfo_children()
            if not children:
                return
                
            # Calculer combien d'éléments préserver autour de l'index actuel
            preserve_before = get_main_playlist_config('preserve_items_before_current')
            preserve_after = get_main_playlist_config('preserve_items_after_current')
            
            # Calculer les limites de préservation
            preserve_start = max(0, current_index - preserve_before)
            preserve_end = min(len(self.main_playlist) - 1, current_index + preserve_after)
            
            # Collecter les widgets à décharger
            widgets_before_current = []
            widgets_after_current = []
            
            for widget in children:
                if hasattr(widget, 'song_index'):
                    if widget.song_index < preserve_start:
                        widgets_before_current.append(widget)
                    elif widget.song_index > preserve_end:
                        widgets_after_current.append(widget)
            
            # Vérifier si on a des widgets à décharger
            if not (widgets_before_current or widgets_after_current):
                return
                
            # Déterminer quels widgets décharger en priorité
            # Si l'utilisateur vient d'utiliser le bouton "find", préserver les éléments autour de la musique actuelle
            if getattr(self, '_just_used_find_button', False):
                # Décharger de manière équilibrée
                widgets_to_unload = widgets_before_current + widgets_after_current
                print(f"DEBUG: Déchargement équilibré après utilisation du bouton find")
            # Si l'utilisateur scrolle en dessous de la musique actuelle, préserver les éléments en dessous
            elif getattr(self, '_scrolling_below_current', False):
                widgets_to_unload = widgets_before_current
                print(f"DEBUG: PRÉSERVATION: Conservation des éléments en dessous car l'utilisateur scrolle vers le bas")
            # Si l'utilisateur scrolle au-dessus de la musique actuelle, préserver les éléments au-dessus
            elif getattr(self, '_scrolling_above_current', False):
                widgets_to_unload = widgets_after_current
                print(f"DEBUG: PRÉSERVATION: Conservation des éléments au-dessus car l'utilisateur les regarde")
            else:
                # Décharger de manière équilibrée
                widgets_to_unload = widgets_before_current + widgets_after_current
                print(f"DEBUG: Déchargement équilibré")
            
            if widgets_to_unload:
                unload_count = len(widgets_to_unload)
                print(f"DEBUG: Déchargement de {unload_count} éléments (préservation {preserve_start}-{preserve_end})")
                print(f"DEBUG: - {len(widgets_before_current)} éléments avant la musique actuelle")
                print(f"DEBUG: - {len(widgets_after_current)} éléments après la musique actuelle")
                
                for widget in widgets_to_unload:
                    if widget.winfo_exists():
                        if hasattr(widget, 'song_index'):
                            print(f"DEBUG: Déchargement de l'élément {widget.song_index}")
                        widget.destroy()
                        
            # Réinitialiser les flags après utilisation
            if getattr(self, '_just_used_find_button', False):
                self._just_used_find_button = False
                print(f"DEBUG: Flag _just_used_find_button réinitialisé")
            if getattr(self, '_scrolling_below_current', False):
                self._scrolling_below_current = False
                print(f"DEBUG: Flag _scrolling_below_current réinitialisé")
                
            # Invalider le cache des index chargés
            try:
                self._invalidate_loaded_indexes_cache()
            except Exception as e:
                print(f"DEBUG: Erreur invalidation cache dans _check_and_unload_items: {e}")
                # Créer le cache s'il n'existe pas
                self._loaded_indexes_cache = set()
                
            # Mettre à jour la région de scroll en préservant la position
            self._update_scroll_region_after_unload()
                
        except Exception as e:
            print(f"DEBUG: Erreur déchargement intelligent: {e}")
            import traceback
            traceback.print_exc()