import requests
from bs4 import BeautifulSoup
import urllib.parse

# Fonction alternative plus précise si la structure est spécifique
def search_anison_song(query):
    """
    Version alternative plus précise pour l'extraction
    """
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://anison.online/en/song?search_text={encoded_query}&section=0&category_id=0&tags=&bpm=0"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # print('soup ', soup)
        
        song_boxes = soup.find_all('div', class_=lambda x: x and 'song-box' in x)
        # print("SONG BOXES ", song_boxes)
        for song_box in song_boxes:
            result = {}
            
            animes_infos_div = song_box.find_all('div', class_='flex items-center h-full')
            for anime_infos_div in animes_infos_div:
                # print(anime_infos_div)
                anime_name_a = anime_infos_div.find('a', href=lambda x: x and 'anime/' in x)
                anime_name = anime_name_a.get_text(strip=True)
                result['anime_name'] = anime_name
            
            song_name_infos_div = song_box.find_all('div', class_=lambda x:x and 'song-name' in x)
            for song_name_infos_div in song_name_infos_div:
                song_name_span = song_name_infos_div.find_all('span', class_='select-none')
                for potential_song_name_span in song_name_span:
                    found = False
                    potential_song_name = potential_song_name_span.get_text(strip=True)
                    if potential_song_name != '' and not found:
                        result['song_name'] = potential_song_name
                        found = True
            
            artists_infos_a = song_box.find('a', class_=lambda x:x and 'block truncate' in x)
            artist = artists_infos_a.get_text(strip=True)
            result['artist'] = artist
            
            
            results.append(result)

        return results
        
    except Exception as e:
        print(f"Erreur: {e}")
        return []

# Exemple d'utilisation
if __name__ == "__main__":
    # Test avec différentes requêtes
    # test_queries = ["Gurenge", "Unravel", "Silhouette", "Pretender"]
    test_queries = ["realize"]
    
    for query in test_queries:
        print(f"🔍 Recherche: '{query}'")
        print("=" * 50)
        
        results = search_anison_song(query)
        for result in results:
            print(result)
        
        # if results:
        #     for i, result in enumerate(results, 1):
        #         print(f"{i}. {result['song']}")
        #         print(f"   Artiste: {result['artist']}")
        #         if 'anime' in result:
        #             print(f"   Anime: {result['anime']} ({result['type']})")
        #         if result['url']:
        #             print(f"   URL: {result['url']}")
        #         print()
        # else:
        #     print("Aucun résultat trouvé")
        
        print("\n")