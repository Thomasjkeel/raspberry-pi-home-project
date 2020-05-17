import requests

def collect_facts():
    response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en") 
    data = response.json() 
    return data['text']