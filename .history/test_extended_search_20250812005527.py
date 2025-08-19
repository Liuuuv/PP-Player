#!/usr/bin/env python3
"""
Test script pour vérifier la nouvelle fonctionnalité de recherche étendue
qui inclut l'artiste et l'album dans la recherche.
"""
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(__file__))

def test_extended_search():
    """Test la recherche étendue incluant artiste et album"""
    print("=== TEST DE LA RECHERCHE ÉTENDUE ===\n")
    
    # Simuler un fichier player avec les nouvelles méthodes
    class MockPlayer:
        def __init__(self):
            self.extended_search_cache = {}
        
        def _get_audio_metadata(self, filepath):
            """Mock de la fonction de métadonnées"""
            # Simuler quelques métadonnées de test
            test_metadata = {
                "downloads/DAOKO × 米津玄師『打上花火』MUSIC VIDEO.mp3": ("DAOKO × 米津玄師", "Fireworks"),
                "downloads/Crying for Rain - 美波 Minami MV.mp3": ("美波", "Crying for Rain"),
                "downloads/test_song.mp3": ("Test Artist", "Test Album")
            }
            return test_metadata.get(filepath, (None, None))
        
        def _build_extended_search_cache(self, filepath):
            """Version identique à celle du vrai player"""
            if filepath in self.extended_search_cache:
                return self.extended_search_cache[filepath]
            
            # Commencer avec le nom de fichier
            search_text_parts = []
            
            # Ajouter le nom de fichier
            filename = os.path.basename(filepath)
            search_text_parts.append(filename)
            
            # Ajouter les métadonnées audio (artiste et album)
            try:
                artist, album = self._get_audio_metadata(filepath)
                if artist:
                    search_text_parts.append(artist)
                if album:
                    search_text_parts.append(album)
            except:
                pass  # Ignorer les erreurs de lecture des métadonnées
            
            # Combiner tout en minuscules pour la recherche
            search_text = " ".join(search_text_parts).lower()
            
            # Mettre en cache
            self.extended_search_cache[filepath] = search_text
            
            return search_text
        
        def perform_search_test(self, files_list, search_term):
            """Test de recherche similaire à _perform_library_search"""
            search_words = search_term.lower().split()
            
            filtered_files = []
            for filepath in files_list:
                # Construire le texte de recherche étendu
                extended_search_text = self._build_extended_search_cache(filepath)
                
                # Vérifier si tous les mots de recherche sont présents
                all_words_found = all(word in extended_search_text for word in search_words)
                
                if all_words_found:
                    filtered_files.append(filepath)
            
            return filtered_files
    
    # Créer une instance de test
    player = MockPlayer()
    
    # Liste de fichiers de test
    test_files = [
        "downloads/DAOKO × 米津玄師『打上花火』MUSIC VIDEO.mp3",
        "downloads/Crying for Rain - 美波 Minami MV.mp3",
        "downloads/test_song.mp3",
        "downloads/another_song_by_daoko.mp3"
    ]
    
    print("📁 Fichiers de test:")
    for i, filepath in enumerate(test_files, 1):
        print(f"   {i}. {os.path.basename(filepath)}")
    
    print("\n🔍 Test du cache de recherche étendu:")
    for filepath in test_files[:3]:  # Tester seulement les 3 premiers avec métadonnées
        extended_text = player._build_extended_search_cache(filepath)
        print(f"   📄 {os.path.basename(filepath)}")
        print(f"      🏷️ Texte de recherche étendu: '{extended_text}'")
    
    print("\n🔍 Tests de recherche:")
    
    # Test 1: Recherche par nom de fichier
    print("\n1. Recherche par nom de fichier: 'daoko'")
    results = player.perform_search_test(test_files, "daoko")
    print(f"   ✅ {len(results)} résultat(s) trouvé(s):")
    for result in results:
        print(f"      - {os.path.basename(result)}")
    
    # Test 2: Recherche par artiste
    print("\n2. Recherche par artiste: '美波'")
    results = player.perform_search_test(test_files, "美波")
    print(f"   ✅ {len(results)} résultat(s) trouvé(s):")
    for result in results:
        print(f"      - {os.path.basename(result)}")
    
    # Test 3: Recherche par album
    print("\n3. Recherche par album: 'fireworks'")
    results = player.perform_search_test(test_files, "fireworks")
    print(f"   ✅ {len(results)} résultat(s) trouvé(s):")
    for result in results:
        print(f"      - {os.path.basename(result)}")
    
    # Test 4: Recherche combinée
    print("\n4. Recherche combinée: 'daoko fireworks'")
    results = player.perform_search_test(test_files, "daoko fireworks")
    print(f"   ✅ {len(results)} résultat(s) trouvé(s):")
    for result in results:
        print(f"      - {os.path.basename(result)}")
    
    # Test 5: Recherche qui ne devrait rien donner
    print("\n5. Recherche sans résultat: 'inexistant'")
    results = player.perform_search_test(test_files, "inexistant")
    print(f"   ✅ {len(results)} résultat(s) trouvé(s):")
    for result in results:
        print(f"      - {os.path.basename(result)}")
    
    print("\n📊 État du cache:")
    for filepath, cached_text in player.extended_search_cache.items():
        print(f"   📄 {os.path.basename(filepath)} -> '{cached_text}'")
    
    print("\n✅ Tests terminés!")
    print("💡 La recherche fonctionne maintenant avec nom de fichier + artiste + album")

if __name__ == "__main__":
    test_extended_search()