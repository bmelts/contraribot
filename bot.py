import os
from twython import TwythonStreamer

class ContraribotStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print data['text'].encode('utf-8')

    def on_error(self, status_code, data):
        print status_code

twitter = TwythonStreamer(os.environ['APP_KEY'],
                          os.environ['APP_SECRET'],
                          os.environ['OAUTH_TOKEN'],
                          os.environ['OAUTH_TOKEN_SECRET'])
twitter.statuses.filter(track='poop')