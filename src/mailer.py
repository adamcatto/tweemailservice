from datetime import date
from email.message import EmailMessage
import json
import os
import smtplib
import ssl

import pandas as pd


def send_mail(config_file):
    print('starting to send...')
    with open(config_file, 'r') as f:
        config = json.load(f)

    tweets_df = pd.read_csv('../data/tweets.csv')
    payload = ''

    email_account = config['user_credentials']['email_account']
    email_password = config['user_credentials']['email_password']
    # print(email_account, email_password)

    """
    server = smtplib.SMTP('localhost', 1025)
    server.login(email_account, email_password)
    server.connect("smtp.gmail.com",465)
    server.ehlo()
    server.starttls()
    
    s=smtplib.SMTP_SSL("smtp.gmail.com", 465)
    s.ehlo()
    s.starttls()
    s.login("email@gmail.com", "password")
    """

    context = ssl.create_default_context()
    port=465
    smtp_server = "smtp.gmail.com"
    columns = ['username', 'timestamp', 'text_content', 'media_urls', 'is_reply']

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(email_account, email_password)

        msg = EmailMessage()
        msg.set_content(payload)
        SUBJECT = 'Subject: Daily Tweets: ' + str(date.today())
        msg['Subject'] = SUBJECT
        msg['To'] = email_account
        msg['From'] = email_account

        for tweet in tweets_df.itertuples():
            # print(tweet)
            print(tweet)
            tweet = tweet[2:]
            payload += str({k: v for k, v in zip(tweet, columns)})
            payload += '\n\n'

        msg.set_content(payload)

        server.send_message(msg)

    print('sent!')
