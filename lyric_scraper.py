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
from BeautifulSoup import BeautifulSoup

apikeys = []

 # Intialize DataFrames
song_cols = ["Index", "Artist", "Track", "URL", "Lyrics"]
songs = pd.DataFrame(columns = song_cols)

error_cols = ["Error", "Message", "Artist", "Track"]
errors = pd.DataFrame(columns = error_cols)

# Read API keys
with open('apikeys.txt', 'r') as keyFile:
    st = keyFile.readline()
    while st != "":
        # Must remove the \n
        apikeys += [st[:-1]]
        st = keyFile.readline()

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
        print e, artist, track
        return (None, None)
    except ValueError as e:
        print e, artist, track
        return (None, None)
    except IndexError as e: 
        print e, artist, track
        return (None, None)
        return (None, None)
    except ConnectionError as e: 
        print e, artist, track
        return (None, None)
    except UnicodeDecodeError as e: 
        print e, artist, track
        return (None, None)
    except UnboundLocalError as e: 
        print e, artist, track
        return (None, None)
    except Exception as e: 
        print e, artist, track
        return (None, None)
    '''
    except AttributeError as e:
        curr = pd.Series([type(e), e, artist, track], index=error_cols)
        errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except ValueError as e:
        curr = pd.Series([type(e), e, artist, track], index=error_cols)
        errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except IndexError as e: 
        curr = pd.Series([type(e), e, artist, track], index=error_cols)
        errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except ConnectionError as e: 
        curr = pd.Series([type(e), e, artist, track], index=error_cols)
        errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except UnicodeDecodeError as e: 
        curr = pd.Series([type(e), e, artist, track], index=error_cols)
        errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except UnboundLocalError as e: 
        curr = pd.Series([type(e), e, artist, track], index=error_cols)
        errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    except Exception as e: 
        curr = pd.Series([type(e), e, artist, track], index=error_cols)
        errors = errors.append(curr, ignore_index=True)
        print e, artist, track
        return (None, None)
    '''

start = datetime.datetime.now()
index = 0
# Start at this song (it's 1 + the last song that was written to file)
skip = 601

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
            print index
            index += 1
            time.sleep(0.1)
            if index > 1000:
            	break

stop = datetime.datetime.now()
print stop - start
#errors.to_csv("errors.csv", index=False)
#songs.to_csv("songs.csv", index=False)

with open('songs.csv', 'a') as f:
    songs.to_csv(f, header=False, index=False)

#with open('errors.csv', 'a') as f:
#    errors.to_csv(f, header=False, index=False)
