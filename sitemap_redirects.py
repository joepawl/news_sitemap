import requests
from cs50 import SQL

db = SQL("sqlite:///sitemaps.db")
competitors = ['nbc', 'cbs', 'fox', 'cnn', 'wapo']

def redirect_check ():
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

redirect_check()
