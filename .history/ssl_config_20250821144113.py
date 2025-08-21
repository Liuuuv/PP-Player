"""
Configuration SSL pour éviter les erreurs de connexion
"""

import ssl
import urllib3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_ssl_context():
    """Crée un contexte SSL plus permissif"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

def get_robust_session():
    """Crée une session requests robuste avec retry et SSL permissif"""
    session = requests.Session()
    
    # Configuration des retries
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    # Adapter avec retry
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Désactiver la vérification SSL
    session.verify = False
    
    return session

def safe_get(url, timeout=10, **kwargs):
    """Effectue une requête GET sécurisée avec fallbacks"""
    session = get_robust_session()
    
    try:
        response = session.get(url, timeout=timeout, **kwargs)
        return response
    except Exception as e:
        print(f"Erreur requête {url}: {e}")
        return None