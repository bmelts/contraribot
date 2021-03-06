# -*- coding: utf-8 -*-

import os
import random
import re
import signal
import sys
from threading import Timer
from htmlentitydefs import name2codepoint
import requests
from twython import Twython, TwythonStreamer

searches = ['i can','i will','i\'ll','i can\'t','i cannot','i won\'t']
opposites = {
    'can': 'CAN’T',
    'will': 'WON’T',
    'i\'ll': 'I WON’T',
    'i’ll': 'I WON’T',
    'can\'t': 'CAN',
    'can’t': 'CAN',
    'cannot': 'CAN',
    'can not': 'CAN',
    'won\'t': 'WILL',
    'won’t': 'WILL',
    'will not': 'WILL'
}
search_regex = re.compile(r'(%s)\b' % '|'.join(sorted(searches, None, len, True)), re.IGNORECASE)
opposite_regex = re.compile(r'\b(%s)\b' % '|'.join(sorted(opposites.keys(), None, len, True)), re.IGNORECASE)
html_decode = re.compile('&(%s);' % '|'.join(name2codepoint))
minutes_between_posts = int(os.environ['MINUTES_BETWEEN_POSTS'])

twitter = Twython(os.environ['APP_KEY'],
                  os.environ['APP_SECRET'],
                  os.environ['OAUTH_TOKEN'],
                  os.environ['OAUTH_TOKEN_SECRET'])

class ContraribotStreamer(TwythonStreamer):
    tweet = None
    tweet_count = 0
    timer = None

    def on_success(self, data):
        if 'entities' in data:
            entities = data['entities']
            # filter out tweets with urls, attached media, or @mentions - let's not spam
            if (('urls' in entities and entities['urls'])
                or ('media' in entities and entities['media'])
                or ('user_mentions' in entities and entities['user_mentions'])):
                return

        if 'text' in data:
            text = html_decode.sub(lambda m: unichr(name2codepoint[m.group(1)]), data['text']).encode('utf-8')
            if search_regex.match(text):
                text = opposite_regex.sub(lambda m: opposites[m.group(1).lower()], text)
                if random.randint(0,self.tweet_count) == 0 and len(text) <= 140:
                    self.tweet = text
                self.tweet_count += 1

    def on_error(self, status_code, data):
        print status_code

    def post_tweet(self):
        if self.tweet:
            try:
                twitter.update_status(status=self.tweet)
            except:
                pass
        self.tweet = None
        self.tweet_count = 0
        self.timer = Timer(minutes_between_posts * 60, self.post_tweet)
        self.timer.start()

streamer = ContraribotStreamer(os.environ['APP_KEY'],
                               os.environ['APP_SECRET'],
                               os.environ['OAUTH_TOKEN'],
                               os.environ['OAUTH_TOKEN_SECRET'])

streamer.timer = Timer(10, streamer.post_tweet)
streamer.timer.start()

def sigint(signal, frame):
    streamer.timer.cancel()
    streamer.disconnect()

signal.signal(signal.SIGINT, sigint)

while True:
    try:
        streamer.statuses.filter(track=','.join(searches))
    except requests.exceptions.ChunkedEncodingError:
        print '***idgi***'