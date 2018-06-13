"""A twitter bot that retweets positive tweets from cool lists."""

import sys
import os
from random import choice
from random import shuffle
import twitter
import unirest


twitter = twitter.Api(
    consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
    access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])

lists = twitter.GetListsList()

count = 200 / len(lists)
num_tweets = 25

min_tweet_len = 120

max_neg = 0.32
min_pos = 0.6


# ===================== functions =====================


def grab_tweets():
    """Returns a list of 25 random tweets from the authenticated user's lists."""

    tweets = []
    long_tweets = []

    for each in lists:
        tweets = tweets + twitter.GetListTimeline(list_id=each.id,
                                                  count=count,
                                                  include_rts=True)
    for tweet in tweets:
        if len(tweet.text) >= min_tweet_len:
            long_tweets.append(tweet)
    shuffle(long_tweets)

    if len(long_tweets) >= num_tweets:
        return long_tweets[:num_tweets]
    else:
        return long_tweets


def filter_pos_tweets(tweets):
    """Returns a list of positive tweets after running sentiment analysis."""

    pos_tweets = []

    for tweet in tweets:
        sentiment = unirest.post("https://japerk-text-processing.p.mashape.com/sentiment/",
            headers={
                "X-Mashape-Key": os.environ['X_MASHAPE_KEY'],
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
                },
            params={
                "language": "english",
                "text": tweet.text
                }
        )
        if (sentiment.body['probability']['neg'] <= max_neg) & (sentiment.body['probability']['pos'] >= min_pos):
            pos_tweets.append(tweet)
            log_sentiment(tweet, sentiment)

    return pos_tweets


def log_sentiment(tweet, sentiment):

    print "TEXT"
    print tweet.id
    print "label: " + str(sentiment.body['label'])
    print "neg: " + str(sentiment.body['probability']['neg'])
    print "pos: " + str(sentiment.body['probability']['pos'])
    print "neutral: " + str(sentiment.body['probability']['neutral'])
    print " "

    sys.stdout.flush()

    return


def choose_tweet(pos_tweets):
    """Returns a single randomly selected tweet."""

    tweet = choice(pos_tweets)

    return tweet


def like_tweets(pos_tweets):
    """Authenticated user likes all tweets in pos_tweets."""

    for tweet in pos_tweets:
        twitter.CreateFavorite(status_id=tweet.id)

    return


def retweet(tweet):
    """Authenticated user retweets tweet."""

    twitter.PostRetweet(tweet.id, trim_user=False)

    return


def run():
    """Runs the bot."""

    # Returns a list of 25 random tweets from the authenticated user's lists.
    tweets = grab_tweets()

    # Returns a list of positive tweets after running sentiment analysis.
    pos_tweets = filter_pos_tweets(tweets)

    # Returns a single randomly selected positive tweet.
    tweet = choose_tweet(pos_tweets)

    # Authenticated user retweets randomly selected positive tweet.
    retweet(tweet)

    # Authenticated user likes all positive tweets.
    like_tweets(pos_tweets)



# ===================== run =====================


run()
