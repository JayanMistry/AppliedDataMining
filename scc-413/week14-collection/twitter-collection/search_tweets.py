#!/usr/bin/env python3

import sys
import time

from twython import Twython, TwythonError, TwythonRateLimitError #https://github.com/ryanmcgrath/twython

from twitter_auth import *
import tweets_json

def search_twitter(search_term, limit):
    #Authorize use of Twitter API with supplied credentials (from twitter_auth).
    twitter = Twython(consumer_key, consumer_secret, access_token, access_secret)

    tweets = []

    try:
        #count=100 is the maximum allowed
        #tweet_mode="extended" allows for full text tweets, rather than truncated (i.e. over 140 chars)
        #https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html
        search_results = twitter.search(q=search_term,tweet_mode="extended",count=100)
	#search_results = twitter.search(q='from:LancasterUni AND snow ',tweet_mode="extended",count=100)
	#search_results = twitter.search(q='#lovelancaster AND snow',tweet_mode="extended",count=100)
	#geocode = '-2.7868366,54.0044766,1000mi' # latitude,longitude,distance(mi/km)
	#search_results = twitter.search(q=search_term,tweet_mode="extended",count=100, geocode=geocode)
        tweets.extend(search_results['statuses'])
        print(tweets)

        #save the id of the oldest tweet less one, this is the starting point for collecting further tweets.
        oldest = tweets[-1]['id'] - 1
        #keep grabbing tweets until there are no tweets left to grab.
        while len(search_results['statuses']) > 0 and len(tweets) < limit:
            try:
                #all subsequent requests use the max_id param to prevent duplicates
                search_results = twitter.search(q=search_term,tweet_mode="extended",count=100,max_id=oldest)
                tweets.extend(search_results['statuses'])
                oldest = tweets[-1]['id'] - 1
                print("...%s tweets downloaded so far" % (len(tweets)))
            except TwythonRateLimitError as e:
                #We have hit the rate limit, so we need to take a break.
                remainder = float(twitter.get_lastfunction_header(header='x-rate-limit-reset')) - time.time()
                #Drop twitter API connection
                #del twitter
                print("sleeping for %d seconds" % remainder)
                #Pause until we can go again.
                time.sleep(remainder)
                #Renew twitter API connection
                twitter = Twython(consumer_key, consumer_secret, access_token, access_secret)
                continue

    except TwythonError as e:
        print(e)

    return tweets[:limit]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: %s search_term limit" % sys.argv[0])
        sys.exit (1)

    search_term = sys.argv[1]
    limit = int(sys.argv[2])
    tweets = search_twitter(search_term, limit)
    #tweets_json.to_full_json(tweets, filepath="%s_tweets.txt" % search_term)
    tweets_json.to_minimal_json(tweets, filepath="%s_tweets.txt" % search_term)
