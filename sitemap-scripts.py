import json
import requests
from bs4 import BeautifulSoup
from cs50 import SQL, get_int

db = SQL("sqlite:///sitemaps.db")

def main ():
    # Define competitors
    competitors = ['nbc', 'cbs', 'fox', 'cnn', 'wapo']
    # Open the database of existing URLs
    for comp in competitors:
        # Build list latest 2,000 entries in database
        exists = db.execute("SELECT * FROM ? ORDER BY modified DESC LIMIT 2000", comp)
        # Loop over urls to 1) see whether they redirect and 2) add info from the json-ld markup
        for exist in exists:
            redirect = requests.get(exist['url'])
            if redirect == 301:
                db.execute("UPDATE ? SET redirect = ? WHERE url = ?", comp, redirect.url, exist['url'])
            elif redirect == 404:
                db.execute("UPDATE ? SET redirect = ? WHERE url = ?", comp, "404 Not Found", exist['url'])
            """else:
                schema = get_ld_json(exist['url'])
                db.execute("UPDATE ? SET published = ?, modified = ?, author = ? WHERE url = ?", 
                comp, schema['datePublished'], schema['dateModified'], schema['author'][0]['name'], exist['url'])
"""

def get_ld_json(url: str) -> dict:
    parser = "html.parser"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, parser)
    return json.loads("".join(soup.find("script", {"type":"application/ld+json"}, "NewsArticle").contents))


if __name__ == "__main__":
    main()