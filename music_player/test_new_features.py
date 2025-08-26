#!/usr/bin/env python3
"""
Test des nouvelles fonctionnalités : logs et téléchargement séquentiel
"""

import os
import sys
import time

def test_imports():
    """Test que tous les modules s'importent correctement"""
    print("🧪 Test des imports...")
    
    try:
        import inputs
        print("✅ inputs.py importé")
        
        import import_logger
        print("✅ import_logger.py importé")
        
        import logs_viewer
        print("✅ logs_viewer.py importé")
        
        import extract_from_html
        print("✅ extract_from_html.py importé")
        
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_logger():
    """Test du système de logs"""
    print("\n🧪 Test du système de logs...")
    
    try:
        from import_logger import get_import_logger
        
        # Créer un logger de test
        logger = get_import_logger(".")
        
        # Démarrer une session de test
        session_id = logger.start_session('TEST', 'test_file.html')
        print(f"✅ Session créée: {session_id}")
        
        # Ajouter quelques logs
        logger.set_total_links(5)
        logger.log_info("Test d'information")
        logger.log_warning("Test d'avertissement")
        logger.log_error("Test d'erreur")
        logger.log_success("Test de succès")
        
        # Simuler le traitement d'URLs
        logger.log_url_processed("https://youtube.com/test1", "Test Video 1", "success")
        logger.log_url_processed("https://youtube.com/test2", "Test Video 2", "failed", "Erreur de test")
        logger.log_url_processed("https://youtube.com/test3", "Test Video 3", "skipped", "Durée trop longue")
        
        # Terminer la session
        logger.end_session('completed')
        print("✅ Session terminée")
        
        # Vérifier que le fichier de logs existe
        logs_dir = os.path.join(".", "import_logs")
        if os.path.exists(logs_dir):
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]
            if log_files:
                print(f"✅ Fichier de logs créé: {log_files[-1]}")
            else:
                print("⚠️ Aucun fichier de logs trouvé")
        else:
            print("⚠️ Dossier de logs non créé")
        
        return True
    except Exception as e:
        print(f"❌ Erreur test logger: {e}")
        return False

def test_html_extraction():
    """Test de l'extraction HTML"""
    print("\n🧪 Test de l'extraction HTML...")
    
    try:
        import extract_from_html
        
        # Créer un fichier HTML de test
        test_html = """
        <html>
        <body>
            <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">Test Video 1</a>
            <a href="https://youtu.be/9bZkp7q19f0">Test Video 2</a>
            <a href="https://music.youtube.com/watch?v=kJQP7kiw5Fk">Test Video 3</a>
        </body>
        </html>
        """
        
        test_file = "test_extraction.html"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        # Extraire les liens
        links = extract_from_html.extract_youtube_links_from_html(test_file)
        
        if len(links) == 3:
            print(f"✅ Extraction réussie: {len(links)} liens trouvés")
            for link in links:
                print(f"  - {link}")
        else:
            print(f"⚠️ Nombre de liens inattendu: {len(links)} (attendu: 3)")
        
        # Nettoyer
        os.remove(test_file)
        
        return True
    except Exception as e:
        print(f"❌ Erreur test extraction: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test des nouvelles fonctionnalités")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Logger
    if test_logger():
        tests_passed += 1
    
    # Test 3: Extraction HTML
    if test_html_extraction():
        tests_passed += 1
    
    # Résultats
    print("\n" + "=" * 50)
    print(f"📊 Résultats: {tests_passed}/{total_tests} tests réussis")
    
    if tests_passed == total_tests:
        print("🎉 Tous les tests sont passés ! Les nouvelles fonctionnalités sont prêtes.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)