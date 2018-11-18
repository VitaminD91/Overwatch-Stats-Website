from flask import Flask, render_template
import json
import requests

app = Flask(__name__)
headers = { 'User-Agent': 'Python OW app 1.0' }

@app.route('/')
def home():
    return render_template('home.html')

def get_stats(battletag):
    response = requests.get(f"https://owapi.net/api/v3/u/{battletag}/stats", headers=headers)
    if response.status_code != 200:
        return None
    return response
    

    