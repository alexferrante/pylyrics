import requests
import re
import pandas as pd
import aeneas
import os

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from aeneas.downloader import Downloader

HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'}
#Get the titles and artists of the top 400 songs on iTunes, generate database
def get_top_songs():
    chart_url = "http://www.popvortex.com/music/charts/itunes-top-400-songs.php"
    try:
        response = requests.get(chart_url, headers=HEADER)
        soup = BeautifulSoup(response.text, "lxml")
        table_body = soup.find('tbody')
        song_data = table_body.find_all('tr')
        rows_list = []
        for songs in song_data:
            title = re.sub(r'[-\"\'#&/@;:<>{}`+=~|.,]', '', songs.contents[1].text.strip())
            title = re.sub(r'[\(\[].*?[\)\]]', '', title)
            artist = re.sub(r'[-()\"\'#&/@;:<>{}`+=~|.,]', '', songs.contents[3].text.strip())
            get_lyrics_page(title, artist)
            dictionary = {'Title': title, 'Artist': artist}
            rows_list.append(dictionary)
        data_frame = pd.DataFrame(rows_list, columns=['Title', 'Artist'])
        data_frame.to_csv('data/data.csv', encoding='utf-8')
    except Exception as e:
        print('Error fetching top songs list')

#Use the title and artist names to get lyrics for each song from Genius
def get_lyrics_page(title, artist):
    BASE_URL = "http://genius.com"
    #create url using regex 
    #to do: jesus, condense later please 
    build_url = artist + ' ' + title
    build_url = ' '.join(build_url.split()).capitalize()
    build_url = re.sub('\s+', '-', build_url)
    build_url = BASE_URL + '/' + build_url + '-lyrics'
    #scrape lyrics from web page
    try:
        scrape_lyrics(build_url)
    except Exception as e:
        print('Error fetching page, does not exist. Attempting to search manually...') #dealing with javascript-rendered content is more complicated, reproduce AJAX calls and parse JSON 
        try:
            if len(artist.split()) > 2: 
                artist = ' '.join(artist.split()[:2])
            if len(title.split()) > 4: 
                title =  ' '.join(title.split()[:4])
            build_url = BASE_URL + "/api/search/multi?per_page=5&q=" + re.sub("\s+", "+", artist.strip()) + "+" + re.sub("\s+", "+", title.strip())
            response = requests.get(build_url, headers=HEADER)
            soup = BeautifulSoup(response.text, "lxml")
            json_data = json.loads(soup.find('p').text.strip())
            scrape_lyrics(BASE_URL+json_data["response"]["sections"][1]["hits"][0]["result"]["path"], title)
        except Exception as e:
            print('Error fetching lyrics, cannot locate')

#Retrieve lyrics from Genius page and write to a .txt file
def scrape_lyrics(url, title):
    try:
        response = requests.get(url, headers=HEADER)
        soup = BeautifulSoup(response.text, 'lxml')
        lyrics_container = soup.find('div', class_='lyrics')
        io = open('data/text/'+title+'.txt', 'w+')
        for i in lyrics_container.contents:
            try: 
                lyrics = re.sub(r'\[[^()]*\]', '', i.get_text()) #remove brackets and their contents
                io.write(lyrics)
            except Exception as e:
                pass #this is OK, exceptions are thrown by tags we don't care about
    except Exception as e:
        print('Error retrieving and writing lyrics')
    io.close()

#Use the title and artist names to get link to audio 
def get_song_url(title, artist):
    BASE_URL = "https://www.youtube.com/results?search_query="
    query_string = artist + ' ' + title
    query_string = query_string.replace(' ', '+')
    BASE_URL += query_string
    response = requests.get(BASE_URL, headers=HEADER)
    soup = BeautifulSoup(response.text, "lxml")
   
    highest_views = 0
    highest_href = ""
    for data in soup.find_all('div', class_='yt-lockup-content'): #iterate through all videos on the page, selecting the most relevant view wise
        if data.find('ol', class_='yt-lockup-playlist-items') is not None: #particular attribute of playlist items, which we dont want to look at
            pass
        elif title not in data.find('a', href=True).get('title').lower(): #extra check to make sure the correct video is selected
            pass
        else: #get href and view count, select if video is more 'relevant' than previous 
            href = data.find('a', href=True).get('href')
            count = data.find('ul', class_='yt-lockup-meta-info').contents[1].text.strip()
            count = count.split(None, 1)[0]
            count = int(re.sub('[^\d\.]', '', count))
            if count > highest_views:
                highest_views = count 
                highest_href = href
    url = "https://www.youtube.com" + highest_href
    try:
        Downloader().audio_from_youtube(url,
                                        download=True,
                                        output_file_path=u'data/audio/'+title+'.mp3'
                                        preferred_format=u'mp3'
                                        )
    except Exception as e:
        print('Error downloading song audio')

#to do: more informed use of the search bar/ checks to ensure all data is scraped
#to do: limit rate of requests (time.sleep) to a reasonable level so I dont get banned (import time, put 'time.sleep(requests p second)' in loop)
#to do: implement map sync via aeneas for forced alignment
