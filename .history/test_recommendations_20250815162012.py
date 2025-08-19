#!/usr/bin/env python3
"""
Script de test pour le système de recommandation
"""

from __init__ import *
import recommendation

def test_recommendation_system():
    """Test du système de recommandation"""
    print("=== Test du système de recommandation ===\n")
    
    # Test 1: Test de base avec un video_id connu
    print("1. Test de récupération des recommandations...")
    try:
        recommendation.test_recommendations("SRF8d_wPXSI")
        print("✓ Test de base réussi\n")
    except Exception as e:
        print(f"✗ Erreur test de base: {e}\n")
    
    # Test 2: Test avec un autre video_id
    print("2. Test avec un autre video_id...")
    try:
        recommendation.test_recommendations("l1hVhzcOiic")  # ID de la chanson a子 - Blue gill
        print("✓ Test avec autre video_id réussi\n")
    except Exception as e:
        print(f"✗ Erreur test autre video_id: {e}\n")
    
    # Test 3: Test d'extraction d'ID depuis une URL
    print("3. Test d'extraction d'ID depuis URL...")
    try:
        from ytmusicapi import YTMusic
        ytmusic = YTMusic()
        
        # Simuler une classe avec la méthode get_youtube_metadata
        class MockApp:
            def get_youtube_metadata(self, filepath):
                return {
                    'url': 'https://youtube.com/watch?v=SRF8d_wPXSI',
                    'upload_date': '20230101'
                }
        
        mock_app = MockApp()
        rec_system = recommendation.RecommendationSystem(mock_app)
        
        video_id = rec_system.extract_video_id_from_filepath("test.mp3")
        print(f"Video ID extrait: {video_id}")
        
        if video_id == "SRF8d_wPXSI":
            print("✓ Extraction d'ID réussie\n")
        else:
            print("✗ Extraction d'ID échouée\n")
            
    except Exception as e:
        print(f"✗ Erreur extraction ID: {e}\n")
    
    # Test 4: Test de filtrage des recommandations
    print("4. Test de filtrage des recommandations...")
    try:
        # Simuler des recommandations
        recommendations = [
            {'title': 'Test 1', 'videoId': 'abc123', 'url': 'https://youtube.com/watch?v=abc123'},
            {'title': 'Test 2', 'videoId': 'def456', 'url': 'https://youtube.com/watch?v=def456'},
            {'title': 'Test 3', 'videoId': 'ghi789', 'url': 'https://youtube.com/watch?v=ghi789'},
        ]
        
        # Simuler une app avec playlist existante
        class MockAppWithPlaylist:
            def __init__(self):
                self.main_playlist = ["song1.mp3", "song2.mp3"]
            
            def get_youtube_metadata(self, filepath):
                if filepath == "song1.mp3":
                    return {'url': 'https://youtube.com/watch?v=abc123'}
                return None
        
        mock_app = MockAppWithPlaylist()
        rec_system = recommendation.RecommendationSystem(mock_app)
        
        filtered = rec_system.filter_new_recommendations(recommendations)
        print(f"Recommandations filtrées: {len(filtered)}/{len(recommendations)}")
        
        # Vérifier que abc123 a été filtré
        video_ids = [rec['videoId'] for rec in filtered]
        if 'abc123' not in video_ids and len(filtered) == 2:
            print("✓ Filtrage réussi\n")
        else:
            print("✗ Filtrage échoué\n")
            
    except Exception as e:
        print(f"✗ Erreur filtrage: {e}\n")
    
    print("=== Fin des tests ===")

if __name__ == "__main__":
    test_recommendation_system()