import requests
from django.conf import settings
from django.core.cache import cache

def get_headers():
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.TMDB_BEARER_TOKEN}"
    }

def fetch_trending(media_type='all', time_window='day', page=1):
    url = f"{settings.TMDB_BASE_URL}/3/trending/{media_type}/{time_window}?language=en-US&page={page}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def search_tmdb(query, page=1):
    url = f"{settings.TMDB_BASE_URL}/3/search/multi?query={query}&include_adult=false&language=en-US&page={page}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def discover_movies(genre_id=None, language=None, provider_id=None, year=None, sort_by=None, page=1):
    url = f"{settings.TMDB_BASE_URL}/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={page}"
    if genre_id:
        url += f"&with_genres={genre_id}"
    if language:
        url += f"&with_original_language={language}"
    if provider_id:
        url += f"&with_watch_providers={provider_id}&watch_region=US"
    if year:
        url += f"&primary_release_year={year}"
    if sort_by:
        url += f"&sort_by={sort_by}"
    else:
        url += "&sort_by=popularity.desc"
        
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def discover_tv(genre_id=None, language=None, provider_id=None, year=None, sort_by=None, page=1):
    url = f"{settings.TMDB_BASE_URL}/3/discover/tv?include_adult=false&include_video=false&language=en-US&page={page}"
    if genre_id:
        url += f"&with_genres={genre_id}"
    if language:
        url += f"&with_original_language={language}"
    if provider_id:
        url += f"&with_watch_providers={provider_id}&watch_region=US"
    if year:
        url += f"&first_air_date_year={year}"
    if sort_by:
        url += f"&sort_by={sort_by}"
    else:
        url += "&sort_by=popularity.desc"
        
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_movie_details(tmdb_id):
    url = f"{settings.TMDB_BASE_URL}/3/movie/{tmdb_id}?language=en-US&append_to_response=credits"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

def get_tv_details(tmdb_id):
    url = f"{settings.TMDB_BASE_URL}/3/tv/{tmdb_id}?language=en-US&append_to_response=credits"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

def get_tv_season(tmdb_id, season_number):
    url = f"{settings.TMDB_BASE_URL}/3/tv/{tmdb_id}/season/{season_number}?language=en-US&append_to_response=credits"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

def get_tv_episode(tmdb_id, season_number, episode_number):
    url = f"{settings.TMDB_BASE_URL}/3/tv/{tmdb_id}/season/{season_number}/episode/{episode_number}?language=en-US"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

# Helpers for Navbar
def get_genres():
    genres = cache.get('tmdb_genres')
    if not genres:
        url = f"{settings.TMDB_BASE_URL}/3/genre/movie/list?language=en"
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            genres = response.json().get('genres', [])
            cache.set('tmdb_genres', genres, 86400) # cache for 1 day
        else:
            genres = []
    return genres

def get_languages():
    # Hardcoded top 10 popular languages
    return [
        {'iso_639_1': 'en', 'english_name': 'English'},
        {'iso_639_1': 'hi', 'english_name': 'Hindi'},
        {'iso_639_1': 'es', 'english_name': 'Spanish'},
        {'iso_639_1': 'fr', 'english_name': 'French'},
        {'iso_639_1': 'de', 'english_name': 'German'},
        {'iso_639_1': 'ja', 'english_name': 'Japanese'},
        {'iso_639_1': 'ko', 'english_name': 'Korean'},
        {'iso_639_1': 'it', 'english_name': 'Italian'},
        {'iso_639_1': 'zh', 'english_name': 'Chinese'},
        {'iso_639_1': 'pt', 'english_name': 'Portuguese'},
    ]

def get_providers():
    providers = cache.get('tmdb_providers')
    if not providers:
        url = f"{settings.TMDB_BASE_URL}/3/watch/providers/movie?language=en-US&watch_region=US"
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            results = response.json().get('results', [])
            # only keep the popular ones
            providers = sorted(results, key=lambda x: x.get('display_priority', 100))[:20]
            cache.set('tmdb_providers', providers, 86400)
        else:
            providers = []
    return providers
