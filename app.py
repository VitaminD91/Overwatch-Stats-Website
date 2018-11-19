from flask import Flask, render_template
import json
import requests
import time

app = Flask(__name__)
headers = { 'User-Agent': 'Python OW app 1.0' }

class Hero:
    def __init__(self, name, hours_played):
        self.name = name 
        self.hours_played = hours_played
        

@app.route('/')
def home():
    stats = get_stats('VitaminD-2419')
    return render_template('home.html', stats=stats)

@app.route('/<battletag>')
def player_stats(battletag):
    region = 'eu'
    blob = get_blob(battletag, region)
    print(blob)
    stats = blob['stats']
    heroes = blob['heroes']
    top_five = get_top_five_heroes(heroes['stats']['quickplay'])
    avatar_url = stats['quickplay']['overall_stats']['avatar']
    tier_img_url = stats['competitive']['overall_stats']['tier_image']
    return render_template('player-stats.html', battletag=battletag, avatar_url=avatar_url, tier_img_url=tier_img_url, top_five=top_five, heroes=heroes, stats=stats)



def get_top_five_heroes(heroes):
    hero_list = []
    for name, stats in heroes.items():
        hours_played = stats['general_stats']['time_played']
        hero_list.append(Hero(name, hours_played))

    hero_list.sort(key = lambda x: x.hours_played, reverse=True)

    top_five = hero_list[:5]
    return top_five
    
        




#API methods
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
    