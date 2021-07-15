import time

import schedule

from mailer import send_mail
from tweet_handler import TweetHandler


def run():
    config_file = '../config.json'
    handler = TweetHandler(config=config_file)
    handler.compile_tweets()
    send_mail(config_file=config_file)

schedule.every().day.at("20:37:40").do(run)
print('scheduled')

while True:
    schedule.run_pending()
