import requests
import re
import pandas as pd

from urllib.parse import urljoin
from bs4 import BeautifulSoup


def get_top_songs():
    chart_url = "http://www.popvortex.com/music/charts/itunes-top-400-songs.php"
    try:
        response = requests.get(chart_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
        soup = BeautifulSoup(response.text, "lxml")
        table_body = soup.find('tbody')
        song_data = table_body.find_all('tr')
        
        rows_list = []
        for songs in song_data:
            title = songs.contents[1].text.strip()
            artist = songs.contents[3].text.strip()
            # lyrics = get_lyrics(title, artist)
            dictionary = {'Title': title, 'Artist': artist}
            rows_list.append(dictionary)

        data_frame = pd.DataFrame(rows_list, columns=['Title', 'Artist'])
        data_frame.to_csv('data.csv', encoding='utf-8')
    except Exception as e:
        print('Error fetching top songs list:' + e)


def get_lyrics(title, artist):
    BASE_URL = "http://genius.com/"
    #create url using regex 
    build_url = artist + ' ' + title
    #to do: replace & with 'and' for multiple artists
    build_url = re.sub('[ ](?=[ ])|[^-_,A-Za-z0-9 ]+', '', build_url)
    build_url = build_url.replace(' ', '-')
    build_url = BASE_URL + build_url + '-lyrics'
    try:
        #scrape lyrics from web page
        response = requests.get(build_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
        soup = BeautifulSoup(response.text, "lxml")
        lyrics = soup.find('div', class_='lyrics').text.strip()
        lyrics = re.sub(r'\[[^()]*\]', '', lyrics) #remove brackets and their contents, possibility of using bracketed labels as classifiers
        return lyrics
    except Exception as e:
        #to do: implement way to use search bar and check that way (i.e. for long titles / several artists)
        return "Error fetching page, does not exist"

#def get_mp3(title, artist)
get_top_songs()