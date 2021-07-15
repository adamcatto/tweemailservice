import ast
from datetime import date, datetime
import json
import os
from typing import Union, Mapping
from urllib import request

import numpy as np
import pandas as pd
import tweepy
from tweepy import API as twapi


# with open('../config.json', 'r') as f:
    # config = json.load(f)



class TweetHandler(object):
    def __init__(self, config: Union[str, Mapping]) -> None:
        if isinstance(config, str):
            with open(config, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = config

        auth_info = self.get_auth_info()
        
        ckey = auth_info['CONSUMER_KEY']
        csecret = auth_info['CONSUMER_SECRET']
        atoken = auth_info['ACCESS_TOKEN']
        asecret = auth_info['ACCESS_TOKEN_SECRET']
        
        self.auth = tweepy.OAuthHandler(ckey, csecret)
        self.auth.set_access_token(atoken, asecret)

        self.api = tweepy.API(self.auth)

        self.columns = ['username', 'timestamp', 'text_content', 'media_urls', 'is_reply']
        self.all_tweets = []

    def get_auth_info(self):
        return self.config['authentication']

    def _get_user_tweets_since_time(self, username, since):
        tweets = []
        max_tweets = self.config['systems_settings']['max_tweets']
        if not bool(max_tweets):
            max_tweets = 500
        
        if ast.literal_eval(self.config['systems_settings']['get_retweets']):
            cursor = tweepy.Cursor(self.api.user_timeline, id=username, include_entities=True)
        else:
            cursoer = tweepy.Cursor(self.api.user_timeline, q='github -filter:retweets', id=username, include_entities=True)
        for status in tweepy.Cursor(self.api.user_timeline, id=username, include_entities=True).items(max_tweets):
            if status.created_at > since:
                tweets.append(status)

        return tweets

    def get_user_tweets_since_last_time(self, username):
        since = self.config['systems_settings']['last_update_timestamp']
        since = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
        return self._get_user_tweets_since_time(username, since)


    def compile_tweets(self):
        usernames_obj = self.config['twitter_settings']['usernames_to_request']
        if isinstance(usernames_obj, list):
            for user in usernames_obj:
                print(user, type(user))
                tweets = self.get_user_tweets_since_last_time(user.strip('@'))
                self.all_tweets += tweets
        elif isinstance(usernames_obj, dict):
            for topic in usernames_obj.keys():
                topic_usernames = usernames_obj[topic]
                for user in topic_usernames:
                    tweets = self.get_user_tweets_since_last_time(user.strip('@'))
                    self.all_tweets += tweets

        rows = []

        for tweet in self.all_tweets:
            username = tweet.user.screen_name
            timestamp = tweet.created_at
            text_content = tweet.text
            media_urls = []
            if 'media' in tweet.entities:
                for image in tweet.entities['media']:
                    media_urls.append(image)
            else:
                media_urls = None
            is_reply = bool(tweet.in_reply_to_user_id)
            rows.append([username, timestamp, text_content, media_urls, is_reply])

        df = pd.DataFrame(np.array(rows), columns=self.columns)
        print(df)
        df.to_csv('../data/tweets.csv')

        self.config['systems_settings']['last_update_timestamp'] = str(datetime.now()).split('.')[0]
        self.all_tweets = []
        with open('../config.json', 'w') as f:
            json.dump(self.config, f)

        