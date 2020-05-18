"""
    Fires a simple HTTP API request to get one fact from the UselessFacts API
"""
import requests

def collect_facts():
    response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en") 
    data = response.json() 
    return data['text']