from flask import Flask, render_template, url_for, session, request, redirect, abort
import owapi
import owdatabase
import hashlib

owdatabase.initialise()
app = Flask(__name__)
app.secret_key= 'somerandomstring' 


#---Classes---#

class Hero:
    def __init__(self, name, hours_played):
        self.name = name 
        self.hours_played = hours_played

class Stats:
    def __init__(self, comp_rank=0):
        self.comp_rank = comp_rank

class Profile:
    def __init__(self, battletag, battletag_number, level, avatar_url, tier_img_url=""):
        self.battletag = battletag
        self.battletag_number = battletag_number
        self.level = level
        self.avatar_url = avatar_url
        self.tier_img_url = tier_img_url

class Overview: 
    def __init__(self, games_won, kpd, medals_gold, medals_silver, medals_bronze):
        self.games_won = games_won
        self.kpd = kpd
        self.medals_gold = medals_gold
        self.medals_silver = medals_silver
        self.medals_bronze = medals_bronze

class Records:
    def __init__(self, final_blows, eliminations, assists, obj_kills, environmental, solo_kills, all_damage, hero_damage, healing):
        self.final_blows = final_blows
        self.eliminations = eliminations
        self.assists = assists
        self.obj_kills = obj_kills
        self.environmental = environmental
        self.solo_kills = solo_kills
        self.all_damage = all_damage
        self.hero_damage = hero_damage
        self.healing = healing



#---Routes---#


@app.route('/')
def home():
    query = request.args.get('q')
    if query == None:
        return render_template('home.html')
    search_results = owapi.search_players(query)
    return render_template('home.html', search_results=search_results)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = owdatabase.get_user(username)
        h = hashlib.md5(password.encode())
        hashedpassword = h.hexdigest()
        if hashedpassword == user['password']:
            session['username'] = username
            print(f'setting user to {username}')
            return redirect('/')
        else:
            return render_template('login.html', error='Incorrect username and/or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/signup', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_repeat = request.form['password-repeat']
        battletag = request.form['battletag']
        existing_user = owdatabase.get_user(username)
        if existing_user == None:
            if password == password_repeat:
                h = hashlib.md5(password.encode())
                hashedpassword = h.hexdigest()
                owdatabase.create_user(
                    username = username,
                    password = hashedpassword,
                    battletag = battletag,
                )
                
                session['username'] = username
                if battletag == "":
                    return redirect('/')
                return redirect('/player/'+ battletag)
                

            else:
                return render_template('sign-up.html', error = 'Passwords did not match', username = username)
        else: 
            return render_template('sign-up.html', error = 'Username already taken')
    return render_template('sign-up.html')
    
    
@app.route('/player/<battletag>')
def player_stats(battletag):
    logged_in = 'username' in session
    profile = owapi.get_profile(battletag)
    if profile == None:
        abort(404)
    name = profile['name']

    if profile['isPublic'] == False:
       return render_template('player-stats.html', title=name, logged_in=logged_in, private=True)

    region = 'eu'
    blob = owapi.get_blob(battletag, region)
    stats = blob['stats']
    heroes = blob['heroes']
    level = profile['level']
    top_five = get_top_five_heroes(heroes['stats']['quickplay'])
    avatar_url = stats['quickplay']['overall_stats']['avatar']
    tier_img_url = stats['competitive']['overall_stats']['tier_image']

    btag_tokens = name.split('#')
    btag = btag_tokens[0]
    btag_number = btag_tokens[1]

    player_profile = Profile(btag, btag_number, level, avatar_url, tier_img_url)

    player_stats = Stats()
    player_stats.comp_rank = stats['competitive']['overall_stats']['comprank']
    
    games_won = stats['quickplay']['game_stats']['games_won']
    kpd = stats['quickplay']['game_stats']['kpd']
    medals_gold = stats['quickplay']['game_stats']['medals_gold']
    medals_silver = stats['quickplay']['game_stats']['medals_silver']
    medals_bronze = stats['quickplay']['game_stats']['medals_bronze']

    player_overview = Overview(games_won, kpd, medals_gold, medals_silver, medals_bronze)

    final_blows = stats['quickplay']['game_stats']['final_blows_most_in_game']
    eliminations = stats['quickplay']['game_stats']['eliminations_most_in_game']
    assists = stats['quickplay']['game_stats']['offensive_assists_most_in_game']
    obj_kills = stats['quickplay']['game_stats']['objective_kills_most_in_game']
    environmental = stats['quickplay']['game_stats']['environmental_kills_most_in_game']
    solo_kills = stats['quickplay']['game_stats']['solo_kills_most_in_game']
    all_damage = stats['quickplay']['game_stats']['all_damage_done_most_in_game']
    hero_damage = stats['quickplay']['game_stats']['hero_damage_done_most_in_game']
    healing = stats['quickplay']['game_stats']['healing_done_most_in_game']

    player_record = Records(final_blows, eliminations, assists, obj_kills, environmental, solo_kills, all_damage, hero_damage, healing)



    return render_template('player-stats.html', title=name, logged_in=logged_in, profile=player_profile, top_five=top_five, player_overview=player_overview,
    player_record=player_record, heroes=heroes, stats=player_stats)

@app.route('/search')
def search():
    query = request.args.get('q')
    if query == None:
        return render_template('search.html')
    search_results = owapi.search_players(query)
    return render_template('search.html', search_results=search_results)
        
@app.route('/top-players')
def top_players():
    top_players = owapi.get_top_players()
    return render_template('top-players.html', top_players=top_players)
    

def get_top_five_heroes(heroes):
    hero_list = []
    for name, stats in heroes.items():
        hours_played = stats['general_stats']['time_played']
        hero_list.append(Hero(name, hours_played))

    hero_list.sort(key = lambda x: x.hours_played, reverse=True)

    top_five = hero_list[:5]
    return top_five

@app.route('/set-battletag', methods=['GET', 'POST'])
def set_battletag(battletag):
    if 'username' not in session:
        abort(400)
    else:
        owdatabase.set_battletag(battletag)
        return render_template(url_for('player_stats', battletag=battletag))

@app.errorhandler(404)
def page_not_found(error):
        return "Player not found", 404