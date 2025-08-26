import pandas as pd
from bs4 import BeautifulSoup
import requests

def get_song_lyrics(url):
    '''
        アーティストごとの歌詞リストを作成する関数
    '''
    song_lyric_list = []
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    # links = soup.find_all('td', class_='side td1')
    lyric = soup.find('div', itemprop='text')
    lyric = lyric.text
    lyric = lyric.replace('\n','')
    song_lyrics = lyric.replace('\u3000','')
    # song_lyrics = [line.lstrip() for line in song_lyrics]
    song_lyrics = song_lyrics.lstrip()
    song_lyrics = [elem.strip() for elem in song_lyrics.split(',') if elem.strip()]

    
    
    return song_lyrics

# lyrics = get_song_lyrics("https://www.uta-net.com/global/en/lyric/352226")
# print(lyrics)




import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_uta_net(query, search_type="song"):
    """
    Recherche une chanson ou un artiste sur Uta-Net avec contournement GDPR
    """
    base_url = "https://www.uta-net.com"
    
    # Encoder la requête pour l'URL
    encoded_query = urllib.parse.quote(query)
    
    # Construire l'URL de recherche
    # if search_type == "song":
    #     search_url = f"{base_url}/search/?Aselect=1&Keyword={encoded_query}&Bselect=4"
    # else:  # artist
    #     search_url = f"{base_url}/search/?Aselect=2&Keyword={encoded_query}&Bselect=4"
    if search_type == "song":
        search_url = f"{base_url}/search/?Keyword={query}&Aselect=2&Bselect=3"
    
    try:
        # Headers pour simuler un navigateur réel
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Cookies pour indiquer que nous ne sommes pas dans l'UE
        cookies = {
            'NOT_GDPR_AREA': '1'
        }
        
        # Faire la requête avec les cookies et headers
        response = requests.get(search_url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
        
        print("link ",search_url)
        
        # Vérifier si on a été redirigé vers la page GDPR
        if "EUからのアクセスですか?" in response.text or "Access from EU?" in response.text:
            print("Blocage GDPR détecté, tentative de contournement...")
            return handle_gdpr_blockade(base_url, search_url, headers)
        
        # Parser le HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)
        results = []
        
        if search_type == "song":
            # Recherche de chansons - sélecteur mis à jour
            song_rows = soup.select('table.sl_table tr')
            for row in song_rows:
                link_tag = row.find('a', href=lambda x: x and '/song/' in x)
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    artist_tag = row.find('td', class_='td2') or row.find('span', class_='artist')
                    artist = artist_tag.get_text(strip=True) if artist_tag else "Artiste inconnu"
                    
                    results.append({
                        'type': 'song',
                        'title': title,
                        'artist': artist,
                        'url': f"{base_url}{link_tag['href']}",
                        'song_id': link_tag['href'].split('/')[-2]
                    })
        
        else:  # Recherche d'artistes
            artist_rows = soup.select('table.artist_table tr, table.sl_table tr')
            for row in artist_rows:
                link_tag = row.find('a', href=lambda x: x and '/artist/' in x)
                if link_tag:
                    artist_name = link_tag.get_text(strip=True)
                    
                    results.append({
                        'type': 'artist',
                        'name': artist_name,
                        'url': f"{base_url}{link_tag['href']}",
                        'artist_id': link_tag['href'].split('/')[-2]
                    })
        
        return results
        
    except Exception as e:
        print(f"Erreur lors de la recherche: {e}")
        return []

def handle_gdpr_blockade(base_url, search_url, headers):
    """
    Gère le blocage GDPR en simulant le comportement du bouton
    """
    try:
        # D'abord, on visite la page d'accueil pour obtenir le cookie
        home_response = requests.get(base_url, headers=headers, timeout=10)
        
        # Ensuite, on envoie une requête pour simuler le clic sur "Non, pas depuis l'UE"
        gdpr_url = f"{base_url}/gdpr_confirm.php"  # URL hypothétique
        payload = {
            'gdpr_confirm': '0',
            'redirect_url': search_url
        }
        
        # Utiliser une session pour maintenir les cookies
        session = requests.Session()
        session.headers.update(headers)
        session.cookies.set('NOT_GDPR_AREA', '1')
        
        # Essayer d'accéder directement avec le cookie
        response = session.get(search_url, timeout=10)
        
        if "EUからのアクセスですか?" in response.text:
            print("Impossible de contourner le blocage GDPR")
            return []
        
        return parse_search_results(response.text, search_type="song")
        
    except Exception as e:
        print(f"Erreur lors du contournement GDPR: {e}")
        return []

def parse_search_results(html_content, search_type="song"):
    """
    Parse le HTML des résultats de recherche
    """
    print("PARSE_SEARCH_RESULTS")
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    base_url = "https://www.uta-net.com"
    
    if search_type == "song":
        song_rows = soup.select('.search-result-item, .song-list-item, tr')
        for row in song_rows:
            link_tag = row.find('a', href=lambda x: x and '/song/' in x)
            if link_tag:
                title = link_tag.get_text(strip=True)
                artist_tag = row.find(class_='artist-name') or row.find('td', class_='td2')
                artist = artist_tag.get_text(strip=True) if artist_tag else "Artiste inconnu"
                
                results.append({
                    'type': 'song',
                    'title': title,
                    'artist': artist,
                    'url': f"{base_url}{link_tag['href']}",
                    'song_id': link_tag['href'].split('/')[-2]
                })
    
    return results

def get_artist_songs(artist_url):
    """
    Récupère toutes les chansons d'un artiste
    
    Args:
        artist_url (str): URL de la page artiste
    
    Returns:
        list: Liste des chansons de l'artiste
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(artist_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        songs = []
        
        # Trouver les liens des chansons
        song_links = soup.find_all('a', href=lambda x: x and '/song/' in x)
        
        for link in song_links:
            songs.append({
                'title': link.get_text(strip=True),
                'url': f"https://www.uta-net.com{link['href']}",
                'song_id': link['href'].split('/')[-2]
            })
        
        return songs
        
    except Exception as e:
        print(f"Erreur: {e}")
        return []

print(search_uta_net("カワキヲアメク", search_type="song"))