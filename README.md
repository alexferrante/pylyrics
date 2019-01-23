# pylyrics

Dynamically generating a dataset based on the most popular music right now and using it to train a RNN to extract lyrics given audio

Using:
Beautiful Soup, urllib, pandas, requests (for data scraping & generic data manipulation)
aeneas (forced alignment)
CMUDictionary (translate lyrics to phonemes for training) 
Keras (recurrent neural network) 

Data sources: Genius, http://www.popvortex.com/music/charts/itunes-top-400-songs.php, YouTube
