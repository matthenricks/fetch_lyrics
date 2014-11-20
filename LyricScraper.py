
# coding: utf-8

## Include all the imports

# In[1]:

import numpy
import pandas as pd
import requests
import time
import json
import csv
import datetime
import string 
import re
import urllib2
import pymongo
from BeautifulSoup import BeautifulSoup


## Generate API Keys

# In[5]:

badURL = []
apikeys = []

for ind in range(1,100):
    uri = "http://www.lyricsnmusic.com/api_keys/"+str(ind+1000)
    r = requests.get(uri)
    if (r.status_code == 200):
        soup = BeautifulSoup(r.text)
        node = soup.find('div', attrs={'class':'grid_6 push_1'})
        node = node.find('p').text
        apikeys += [str.strip(str(node[15:]))]
    else:
        badURL += [uri]
    time.sleep(0.5)

print "\nRESULTS"
print "apikeys", len(apikeys)
print "badURL", len(badURL)

with open('apikeys.txt', 'a') as keyFile:
    for key in apikeys:
        keyFile.write(key)
        keyFile.write("\n")


## Get API Key

# In[2]:

apikeys = []

with open('apikeys.txt', 'r') as keyFile:
    st = keyFile.readline()
    while st != "":
        # Must remove the \n
        apikeys += [st[:-1]]
        st = keyFile.readline()


# In[3]:

apikeys[:5]


## Song and LyricError Class

# In[4]:

# Intialize DataFrames

from json import JSONEncoder 

class Song:
    def __init__(self, index, artist, track, url, lyrics):
        self.index = index
        self.artist = artist
        self.track = track
        self.url = url
        self.lyrics = lyrics
    
    def __str__(self): 
        result = "Artist: " + self.artist
        result += ", Track: " + self.track 
        result += ", URL: " + self.url
        return result 
    
    def __repr__(self): 
        return self.__str__()
    
    def jsonable(self):
        return self.__dict__

class LyricError: 
    def __init__(self, index, artist, track, errorType, errorMessage):
        self.index = index
        self.artist = artist
        self.track = track
        self.errorType = errorType
        self.errorMessage = errorMessage
        
    def __str__(self):
        result = "Artist: " + self.artist
        result += ", Track: " + self.track 
        result += ", ErrorType: " + self.errorType
        result += ", Msg: " + self.errorMessage
        return result 
    
    def __repr__(self): 
        return self.__str__()
    
    def jsonable(self):
        return self.__dict__
    
def ComplexHandler(Obj):
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj))


## Pandas Lyrics Store

# In[4]:

# lyrics&music API
song_base = "http://api.lyricsnmusic.com/songs?api_key="
apikey = apikeys[28]

def stripPuncEscape(input_string):
    """ Removes all escape sequences, replaces \r\n with " ", and removes punctuation """
    delete = ""
    i=1
    while (i<0x20):
        delete += chr(i)
        i += 1
    t = input_string.replace("\r\n", " ")
    # If need ASCII encoding
    #t = re.sub(u"(\u2018|\u2019)", "'", t)
    t = t.translate(None, string.punctuation)
    t = t.translate(None, delete)
    return t

# Go with the first entry
def findSongAPI(artist, track):
    artist = urllib2.quote(artist.encode("utf-8"))
    track = urllib2.quote(track.encode("utf-8"))
    song_url = song_base+apikey+"&artist="+artist+"&track="+track
    r = requests.get(song_url)
    lyric_url = None
    lyrics = None

    try: 
        lyric_url = r.json()[0]['url']
        song = requests.get(lyric_url.encode())
        soup = BeautifulSoup(song.text)
        soup = soup.find('pre', attrs={'itemprop':'description'})
        lyrics = soup.text.encode('utf-8')
        lyrics = stripPuncEscape(lyrics)
        return (lyric_url, lyrics)
    except AttributeError as e:
        #curr = pd.Series([type(e), e, artist, track], index=error_cols)
        #errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except ValueError as e:
        #curr = pd.Series([type(e), e, artist, track], index=error_cols)
        #errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except IndexError as e: 
        #curr = pd.Series([type(e), e, artist, track], index=error_cols)
        #errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except ConnectionError as e: 
        #curr = pd.Series([type(e), e, artist, track], index=error_cols)
        #errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except UnicodeDecodeError as e: 
        #curr = pd.Series([type(e), e, artist, track], index=error_cols)
        #errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except UnboundLocalError as e: 
        #curr = pd.Series([type(e), e, artist, track], index=error_cols)
        #errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except Exception as e: 
        #curr = pd.Series([type(e), e, artist, track], index=error_cols)
        #errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)


# Start by pulling in the song and artist data from the csv file

# In[11]:

# Intialize DataFrames
song_cols = ["Index", "Artist", "Track", "URL", "Lyrics"]
songs = pd.DataFrame(columns = song_cols)

#error_cols = ["Error", "Message", "Artist", "Track"]
#errors = pd.DataFrame(columns = error_cols)

start = datetime.datetime.now()
index = 0
skip = 0

with open('BillboardMusic.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    #print reader.fieldnames

    for row in reader:
        if index < skip: 
            index += 1
        else: 
            artist = row['Artist']
            track = row['Track']
            url, lyrics = findSongAPI(artist, track)
            artist = artist.replace(",", "")
            track = track.replace(",", "")
            curr = pd.Series([index, artist, track, url, lyrics], index=song_cols)
            songs = songs.append(curr, ignore_index=True)
            #print index
            index += 1
            time.sleep(0.1)
            if index > 5: 
                break


# In[92]:

#stop = datetime.datetime.now()
#print stop - start
#errors.to_csv("errors.csv", index=False)
#songs.to_csv("songs.csv", index=False)


# In[ ]:

# Trying to debug why errors dataframe is failing, no avail

e = ValueError("Value")
curr = pd.Series([type(e), e, "", ""], index=error_cols)
errors = errors.append(curr, ignore_index=True)


# In[83]:

songs = songs.drop(songs.index[[0,1,2]])


# In[104]:

with open('songs.csv', 'a') as f:
    songs.to_csv(f, header=False, index=False)


## MongoDB Lyrics Store

# In[5]:

# Database: lyrics
# Collection: songs
# Collection: errors

from pymongo import MongoClient 
client = MongoClient('localhost', 27017)
db = client.lyrics
top_songs = db.songs
errors = db.errors


# In[6]:

# Intialize DataFrames

from json import JSONEncoder 

class Song:
    def __init__(self, index, artist, track, url, lyrics):
        self.index = index
        self.artist = artist
        self.track = track
        self.url = url
        self.lyrics = lyrics
    
    def __str__(self): 
        result = "Artist: " + self.artist
        result += ", Track: " + self.track 
        result += ", URL: " + self.url
        return result 
    
    def __repr__(self): 
        return self.__str__()
    
    def jsonable(self):
        return self.__dict__

class LyricError: 
    def __init__(self, index, artist, track, errorType, errorMessage):
        self.index = index
        self.artist = artist
        self.track = track
        self.errorType = errorType
        self.errorMessage = errorMessage
        
    def __str__(self):
        result = "Artist: " + self.artist
        result += ", Track: " + self.track 
        result += ", ErrorType: " + self.errorType
        result += ", Msg: " + self.errorMessage
        return result 
    
    def __repr__(self): 
        return self.__str__()
    
    def jsonable(self):
        return self.__dict__
    
def ComplexHandler(Obj):
    if hasattr(Obj, 'jsonable'):
        return Obj.jsonable()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj))


# In[10]:

# lyrics&music API
song_base = "http://api.lyricsnmusic.com/songs?api_key="
apikey = apikeys[28]

def stripPuncEscape(input_string):
    """ Removes all escape sequences, replaces \r\n with " ", and removes punctuation """
    delete = ""
    i=1
    while (i<0x20):
        delete += chr(i)
        i += 1
    t = input_string.replace("\r\n", " ")
    # If need ASCII encoding
    #t = re.sub(u"(\u2018|\u2019)", "'", t)
    t = t.translate(None, string.punctuation)
    t = t.translate(None, delete)
    return t

# Go with the first entry
def findSongAPI(index, artist, track):
    artist = urllib2.quote(artist.encode("utf-8"))
    track = urllib2.quote(track.encode("utf-8"))
    song_url = song_base+apikey+"&artist="+artist+"&track="+track
    r = requests.get(song_url)
    lyric_url = None
    lyrics = None

    try: 
        lyric_url = r.json()[0]['url']
        song = requests.get(lyric_url.encode())
        soup = BeautifulSoup(song.text)
        soup = soup.find('pre', attrs={'itemprop':'description'})
        lyrics = soup.text.encode('utf-8')
        lyrics = stripPuncEscape(lyrics)
        return (lyric_url, lyrics)
    except AttributeError as e:
        curr_error = LyricError(index, artist, track, type(e), e)
        errors.insert(curr_error.__dict__)
        return (None, None)
    except ValueError as e:
        curr_error = LyricError(index, artist, track, type(e), e)
        errors.insert(curr_error.__dict__)
        return (None, None)
    except IndexError as e: 
        curr_error = LyricError(index, artist, track, type(e), e)
        errors.insert(curr_error.__dict__)
        return (None, None)
    except ConnectionError as e: 
        curr_error = LyricError(index, artist, track, type(e), e)
        errors.insert(curr_error.__dict__)
        return (None, None)
    except UnicodeDecodeError as e: 
        curr_error = LyricError(index, artist, track, type(e), e)
        errors.insert(curr_error.__dict__)
        return (None, None)
    except UnboundLocalError as e: 
        curr_error = LyricError(index, artist, track, type(e), e)
        errors.insert(curr_error.__dict__)
        return (None, None)
    except Exception as e: 
        curr_error = LyricError(index, artist, track, type(e), e)
        errors.insert(curr_error.__dict__)
        return (None, None)


# In[ ]:

start = datetime.datetime.now()
index = 0
skip = 0

with open('BillboardMusic.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    #print reader.fieldnames

    for row in reader:
        if index < skip: 
            index += 1
        else: 
            artist = row['Artist']
            track = row['Track']
            url, lyrics = findSongAPI(index, artist, track)
            artist = artist.replace(",", "")
            track = track.replace(",", "")
            curr_song = Song(index, artist, track, url, lyrics)
            top_songs.insert(curr_song.__dict__)
            print index
            index += 1
            time.sleep(0.1)


# In[21]:

# Query from MongoDB
# http://blog.juncoapps.com/2012/09/13/use-python-to-readwrite-to-a-mongodb-collection-convert-objects-to-and-from-dictionaries/

# doesn't work because of the '_id'
songs = []

for song in top_lyrics.find():
    tmp = Song(**song)
    songs.append(tmp)
    
for song in songs: 
    print song
    
    


# In[ ]:



