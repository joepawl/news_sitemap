import json
import requests
from bs4 import BeautifulSoup

def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)
    return json.loads("".join(soup.find("script", {"@type":"NewsArticle"}).contents))

url= 'https://www.nbcnews.com/news/world/russia-ukraine-invasion-fears-separatists-military-mobilization-putin-rcna16937'
schema = get_ld_json(url)

print(schema)