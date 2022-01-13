from bs4 import BeautifulSoup
import lxml
import requests

def scrape():
    url = 'https://animixplay.to/'
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.37"
    html_text = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(html_text.text, 'lxml')
    showsInfo = soup.find_all('div', class_ = 'details')
    shows = {}
    for show in showsInfo:
        episode = show.find('p', class_ = 'infotext').text[3:-1].split('/')
        shows[show.find('p', class_= 'name').text] = int(episode[0])

    return shows

def getCurrentSeason():
    url = 'https://myanimelist.net/anime/season'
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.37"
    html_text = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(html_text.text, 'lxml')
    showsInfo = soup.find_all('a', class_ = 'link-title')
    shows = set()
    for show in showsInfo:
        shows.add(show.text)
    return shows
