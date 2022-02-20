from bs4 import BeautifulSoup
import requests
from cs50 import SQL

# TODO: Scrape the JSON (json-schema.py) and use that to populate modified field
# TODO: Consider srapping db columns for year, etc. and creating function that parses modified

def main():
    # Define dictionary of competitors and sitemap URLs
    # 'nyt': 'https://www.nytimes.com/sitemaps/new/news-1.xml.gz' -- have some issues with that one
    competitors = {'nbc': 'https://www.nbcnews.com/sitemap/nbcnews/sitemap-news', 'fox': 'https://www.foxnews.com/sitemap.xml?type=news', 
        'cnn': 'https://www.cnn.com/sitemaps/cnn/news.xml', 'wapo': 'https://www.washingtonpost.com/arcio/news-sitemap/', 
        'cbs': 'https://www.cbsnews.com/xml-sitemap/news.xml'}

    # Open the database of existing URLs
    db = SQL("sqlite:///sitemaps.db")

    for comp in competitors.keys():
        file = competitors[comp]
        location = requests.get(file)
        soup = BeautifulSoup(location.text, "xml")

        # Read URLs into a list
        url = [el for el in soup.find_all('loc') if not el.prefix]
        url = [url[x].get_text() for x in range(len(url))]

        # Read titles into a list
        title = soup.find_all('news:title')
        title = [title[x].get_text() for x in range(len(title))]

        # Read modifieds into a list and break them out into component integers
        modified = soup.find_all('publication_date')
        modified = [modified[x].get_text() for x in range(len(modified))]
        # Use this as a function to break down timestamp string if needed


        # Put sitemap data into a list of dictionaries
        entries = []
        for x in range(len(url)):
            entries.append({'url': url[x], 'title': title[x], 'modified': modified[x]})
        
        # Build list latest 2,000 URLs in database
        existing = db.execute("SELECT * FROM ? ORDER BY modified DESC LIMIT 2000", comp)
        existingUrls = [existing[x]['url'] for x in range(len(existing))]
        
        for entry in entries:
            # If the sitemap entry isn't in the list of the last 2,000 URLs, add it to the db
            if entry['url'] not in existingUrls:
                db.execute("INSERT INTO ? (url, title, modified, titleChanges, timestampUpdates) VALUES(?, ?, ?, ?, ?)",
                comp, entry['url'], entry['title'], entry['modified'], 0, 0)
            else:
                for exists in existing:
                    if entry['url'] == exists['url']:
                        # If the titles of matching URLs don't match, write to db
                        if entry['title'] != exists['title']:
                            db.execute("UPDATE ? SET title = ?, titleChanges = ? WHERE url = ?",
                            comp, entry['title'], exists['titleChanges'] + 1, exists['url'])
                            # Try creating a new db based on the url
                            try:
                                db.execute("CREATE TABLE ? (title TEXT, modified TEXT)",
                                exists['url'])
                                db.execute("INSERT INTO ? (title) VALUES(?)",
                                exists['url'], exists['title'])
                            except:
                                pass
                            db.execute("INSERT INTO ? (title) VALUES(?)",
                            exists['url'], entry['title'])
                        if entry['modified'] != exists['modified']:
                            db.execute("UPDATE ? SET modified = ?, timestampUpdates = ? WHERE url = ?",
                            comp, entry['modified'], exists['timestampUpdates'] + 1, exists['url'])
                            # Try creating a new db based on the url
                            try:
                                db.execute("CREATE TABLE ? (title TEXT, modified TEXT)",
                                exists['url'])
                                db.execute("INSERT INTO ? (modified) VALUES(?)",
                                exists['url'], exists['modified'])
                            except:
                                pass


def processTime(timestamp):
    year = []
    month = []
    day = []
    hour = []
    minute = []
    for x in range(len(timestamp)):
        year.append(int(timestamp[x][0:4]))
        month.append(int(timestamp[x][5:7]))
        day.append(int(timestamp[x][8:10]))
        hour.append(int(timestamp[x][11:13]))
        minute.append(int(timestamp[x][14:16]))

if __name__ == "__main__":
    main()
