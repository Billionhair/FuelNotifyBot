
import requests
from bs4 import BeautifulSoup

def fetch_news(queries):
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for query in queries:
        url = f"https://www.google.com/search?q={query}"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for g in soup.find_all('div', class_='BVG0Nb'):
            title = g.get_text()
            link = g.find_parent('a')['href']
            results.append({'title': title, 'link': link})
    return results
