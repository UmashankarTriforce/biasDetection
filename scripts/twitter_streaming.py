from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from os import environ as env
import json

access_token = env['access_token']
access_token_secret = env['access_token_secret']
consumer_key = env['consumer_key']
consumer_secret = env['consumer_secret']

raw_data = []
#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        data = json.loads(data)
        with open('raw_data.json', 'a') as outfile:
            json.dump(data, outfile, indent = 4)
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':

    keywords = [
            'modi',
            'namo',
            'NCR',
            ]

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords
    stream.filter(track=keywords)
