
import json
import time

headers = { 'User-Agent': 'Python OW app 1.0' }
#error handling for returning None in methods -- return none at start of method emulates error(non200)

#API methods

def get_profile(battletag):
    encoded_battletag = battletag.replace("-", "%23")
    response = requests.get("https://playoverwatch.com/en-gb/search/account-by-name/" + {encoded_battletag})
    if response.status_code != 200:
        return None
    profile = json.loads(response.content)
    if profile == None:
        return None
    if len(profile) == 0:
        return None 
    return profile[0]
    
def search_players(query):
    encoded_query = query.replace("#", "%23")
    response = requests.get("https://playoverwatch.com/en-gb/search/account-by-name/" + {encoded_query})
    if response.status_code != 200:
        return None
    search_result = json.loads(response.content)
    return search_result

def get_stats(battletag, region):
    response = requests.get("https://owapi.net/api/v3/u/" + {battletag} + "/stats", headers=headers)
    if response.status_code != 200:
        return None
    stats = json.loads(response.content)
    return stats[region]['stats']

def get_heroes(battletag, region):
    response = requests.get("https://owapi.net/api/v3/u/" + {battletag} + "/heroes", headers=headers)
    if response.status_code != 200:
        return None
    heroes = json.loads(response.content)
    return heroes[region]['heroes']

def get_blob(battletag, region):
    url = "https://owapi.net/api/v3/u/" + {battletag} + "/blob"
    response = requests.get(url, headers=headers)
    #API returns error 429 when being ratelimited - wait for specified time and try again
    if response.status_code == 429:
        content = json.loads(response.content)
        time.sleep(content['retry'])
        return get_blob(battletag, region)

    if response.status_code != 200: 
        return None

    blob = json.loads(response.content)
    return blob[region]

def get_top_players():
    url = "https://owranking.azurewebsites.net/api/rankings?code=2xcjbU7snDX1HKRRpZ3uZbRo1HrdoduiujpHbmT78WWuKs4xpgrCsA=="
    response = requests.get(url, headers=headers)
    if response.status_code != 200: 
        return None
    top_players = json.loads(response.content)
    return top_players
    