from flask import Flask, render_template, url_for, session, request, redirect
import owapi
import owdatabase

owdatabase.initialise()
app = Flask(__name__)
app.secret_key= 'somerandomstring' 



class Hero:
    def __init__(self, name, hours_played):
        self.name = name 
        self.hours_played = hours_played

class Stats:
    def __init__(self, comp_rank=0):
        self.comp_rank = comp_rank

class Profile:
    def __init__(self, battletag, level, avatar_url, tier_img_url=""):
        self.battletag = battletag
        self.level = level
        self.avatar_url = avatar_url
        self.tier_img_url = tier_img_url


@app.route('/')
def home():
    return redirect(url_for('player_stats', battletag='VitaminD-2419'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = owdatabase.get_user(username)
        if password == user['password']:
            session['username'] = request.form['username']
            print(f'setting user to {username}')
            return redirect('/')
        else:
            return render_template('login.html', error='Incorrect username and/or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('/'))
    
@app.route('/player/<battletag>')
def player_stats(battletag):
    region = 'eu'
    blob = owapi.get_blob(battletag, region)
    stats = blob['stats']
    heroes = blob['heroes']
    top_five = get_top_five_heroes(heroes['stats']['quickplay'])
    profile = owapi.get_profile(battletag)
    name = profile['name']
    level = profile['level']
    avatar_url = stats['quickplay']['overall_stats']['avatar']
    tier_img_url = stats['competitive']['overall_stats']['tier_image']

    player_profile = Profile(name, level, avatar_url, tier_img_url)

    player_stats = Stats()
    player_stats.comp_rank = stats['competitive']['overall_stats']['comprank']

    test = owapi.get_profile(battletag) 


    return render_template('player-stats.html', title=name, profile=player_profile, top_five=top_five, heroes=heroes, stats=player_stats)



def get_top_five_heroes(heroes):
    hero_list = []
    for name, stats in heroes.items():
        hours_played = stats['general_stats']['time_played']
        hero_list.append(Hero(name, hours_played))

    hero_list.sort(key = lambda x: x.hours_played, reverse=True)

    top_five = hero_list[:5]
    return top_five
    
    