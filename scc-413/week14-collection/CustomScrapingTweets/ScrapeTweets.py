# To run this code, first edit config.py with your configuration, then:
#
# mkdir data
# python twitter_stream_download.py -q apple -d data
# python ScrapeTweets.py -q 00554785485257804yyyrTT84rrrR -d data
#  
# It will produce the list of tweets for the query "apple" 
# in the file data/stream_apple.json

import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import argparse
import string
import config
import json
import sys
import re


class MyListener(tweepy.StreamListener):
    """Custom StreamListener for streaming data."""

    def __init__(self, data_dir, query):
        query_fname = format_filename(config.search_term)
        self.outfile = "%s/stream_%s.json" % ('data', query_fname)


    def on_data(self, data):
        try:
            stepper = 0
            with open(self.outfile, 'a') as f:
                print('writing')
                f.write(data)
                print('printing')
                sys.exit()
                #d = json.loads(data)
                #file = open('data/TweetText', 'a') 
                stepper= stepper+1
                print('Writing text to files')       
                #file.write(formatTweet(d['text']))
                print('no',stepper)                
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
            time.sleep(5)
        return True

    def on_error(self, status):
        print(status)
        return True
    
                


def dostuff(data):
    start = data.index('text')
    end = data.index('source')
    print('TEST',list(data[start:end]))

def formatTweet(tweet):
    if ('RT @' in tweet):
        print('RT @ HERE')
        befor_keyowrd, keyword, tweet = tweet.partition(':')
        print ('after_keyword: ', tweet.encode("utf-8"))
    Formattedtweet = lambda tweet: re.compile('\#').sub('', re.compile('RT @').sub('@', tweet, count=1).strip())
    result = (Formattedtweet(tweet))
    result = result.replace('*','')
    result = re.sub(r"http\S+", "", result)
    result = re.sub(r"https\S+", "", result)
    result = re.sub(r"@\S+", "", result)
    #print (result)
    return result
        

def format_filename(fname):
    """Convert file name into a safe string.

    Arguments:
        fname -- the file name to convert
    Return:
        String -- converted file name
    """
    return ''.join(convert_valid(one_char) for one_char in fname)


def convert_valid(one_char):
    """Convert a character into '_' if invalid.
    
    Arguments:
        one_char -- the char to convert
    Return:
        Character -- converted char
    """
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    if one_char in valid_chars:
        return one_char
    else:
        return '_'
		

		
@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw))
    return status


def RemoveRetweetsandHashtags(tweet):
    tweet.replace('#', '')
    if ('RT @' in tweet):
        print('RT @ HERE')
        befor_keyowrd, keyword, tweet = tweet.partition(':')
        print ('after_keyword: ', tweet.encode("utf-8"))
    return tweet
    


if __name__ == '__main__':
    #oo = 'RT @iDropNews: Enter @pussy the iDrop New#s #Apple TV Giveaway for your chance to win! #applenews https:\/\/t.co\/Q0qEFVGt60'
    #oo = 'APPL LEAD - Indigenous Liaison and @pus Investigations Analyst **Amendment Close Date Extended**.. #government #eluta https:\/\/t.co\/3wNPTUFJ7g'
    #RemoveRetweetsandHashtags(oo)
    #formatTweet(oo)
    #sys.exit()
    #formatTweets()
    #parser = get_parser()
    #args = parser.parse_args()
    auth = OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_secret)
    api = tweepy.API(auth)
    twitter_stream = Stream(auth, MyListener(config.data_directory, config.search_term))
    twitter_stream.filter(languages=["en"], track=[config.search_term])

    #twitter_stream.filter(track=["Medical Dossier"])
