import requests
import json
import time

headers = { 'User-Agent': 'Python OW app 1.0' }

#API methods

def get_profile(battletag):
    encoded_battletag = battletag.replace("-", "%23")
    response = requests.get(f"https://playoverwatch.com/en-gb/search/account-by-name/{encoded_battletag}")
    if response.status_code != 200:
        return None
    profile = json.loads(response.content)
    print(profile)
    if profile[0] == None:
        return None
    return profile[0]
    

def get_stats(battletag, region):
    response = requests.get(f"https://owapi.net/api/v3/u/{battletag}/stats", headers=headers)
    if response.status_code != 200:
        return None
    stats = json.loads(response.content)
    return stats[region]['stats']

def get_heroes(battletag, region):
    response = requests.get(f"https://owapi.net/api/v3/u/{battletag}/heroes", headers=headers)
    if response.status_code != 200:
        return None
    heroes = json.loads(response.content)
    return heroes[region]['heroes']

def get_blob(battletag, region):
    url = f"https://owapi.net/api/v3/u/{battletag}/blob"
    response = requests.get(url, headers=headers)
    print(url)
    print(response)
    #API returns error 429 when being ratelimited - wait for specified time and try again
    if response.status_code == 429:
        content = json.loads(response.content)
        time.sleep(content['retry'])
        return get_blob(battletag, region)

    if response.status_code != 200: 
        return None

    blob = json.loads(response.content)
    return blob[region]
    