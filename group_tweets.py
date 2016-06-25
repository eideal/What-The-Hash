########
# Store hashtags with their cleaned tweets, popularity value
########

import psycopg2
import pandas as pd
import string
import re
import collections
import datetime
import numpy as np
import operator
from gensim.models.word2vec import Word2Vec
from update_database import connect_to_db
from nltk.corpus import stopwords
from math import log10
#import matplotlib.pyplot as plt

# Cache the English stopwords
cachedStopWords = stopwords.words("english")

# Function to clean the tweets
# Remove all non-ASCII characters, links, @, punctuation in tweets - except for the #
def clean_tweet(tweet):
    tweet = re.sub(r"@\S+", "", tweet)
    printable = set(string.printable)
    punctuation = set(string.punctuation)
    punctuation.remove('#')
    tweet = filter(lambda x: x not in punctuation, tweet)
    tweet = filter(lambda x: x in printable, tweet)
    tweet = re.sub(r'http\S+', '', tweet)
    return tweet.lower()

def remove_stopwords(tweet):
    tweet = ' '.join([word for word in tweet.split() if word not in cachedStopWords])
    return tweet

def clean_tweet_and_stopwords(tweet):
    tweet = re.sub(r"@\S+", "", tweet)
    printable = set(string.printable)
    punctuation = set(string.punctuation)
    punctuation.remove('#')
    tweet = filter(lambda x: x not in punctuation, tweet)
    tweet = filter(lambda x: x in printable, tweet)
    tweet = re.sub(r'http\S+', '', tweet)
    tweet = ' '.join([word for word in tweet.split() if word not in cachedStopWords])
    return tweet.lower()

def normalize_freq(freq, n_min, n_max):
    return float(freq - n_min)/float(n_max - n_min)

def generate_hashtag_dict():

    #conn = psycopg2.connect("host=localhost dbname=tweets_db user=ideal password=some13thing")
    conn = connect_to_db()
    cur = conn.cursor()
    
    # Pull all tweets from the database
    cur.execute("""SELECT * FROM tweets;""")
    results = cur.fetchall()
    conn.close()
    
    # Convert to pandas data frame
    tweets = pd.DataFrame(results)
    
    # Name the columns
    tweets.columns = ['text']
    
    # Form the dictionary of hashtags in all tweets
    hashtag_list = []
    for i, row in tweets.iterrows():
        text = clean_tweet(row['text'])
        words = text.split()
        hashtags = [word for word in words if re.search(r'^#.[A-Za-z]+', word)]
        hashtag_list.append(hashtags)
    
    hashtag_list = [tag for sublist in hashtag_list for tag in sublist]
    hashtags = collections.Counter(hashtag_list)
    
    # Remove all hashtags that have <= 2 tweets associated to them
    important_hashtags = {k:v for k, v in hashtags.items() if v > 2}
    
    # Remove the rt hashtag '#rt'
    del important_hashtags['#rt']
    
    # Remove links, @ from tweets, keep the hashtags
    #tweets['text'] = tweets['text'].apply(clean_tweet)
    tweets['text'] = tweets['text'].apply(clean_tweet_and_stopwords)

    # Remove stopwords from tweets
    print('Done cleaning the tweets!')
    
    #--------------------------------------------------
    # Make the dictionary of hashtags, where values are the words belonging to tweets associated to the hashtag
    
    #model = Word2Vec.load('twitter27B200d')
    model = Word2Vec.load('bigram_model_updated')
    print('Finished loading the word2vec model...')
    
    # Initialize dictionary, where values are lists
    dict_hash_with_tweets = collections.defaultdict(list)
    
    # Fill dictionary with {#hashtag: [words from tweets containing that hashtag]}
    for tweet in tweets['text']:
        hashtags = [word for word in tweet.split() if re.search(r'^#', word)]
        for hashtag in hashtags:
            if not hashtag in important_hashtags.keys(): continue
            tweet_wo_hashtag = list(set(tweet.split()) - set(hashtags))
            
            # Remove words if they aren't in the trained vocabulary
            tweet_wo_hashtag = [word for word in tweet_wo_hashtag if word in model.vocab]
            
            # If the hashtag isn't in the dict, initialize an empty list as first arg and 0 as its second arg
            # The empty list will be filled with its corresponding tweet words and the second element
            # will be a count of the number of tweets the hashtag was in. The third element counts the # of words in 
            # user's tweet that appears in the hashtag word list. The fourth element counts the total # of times the words
            # in the user's tweet appears in the hashtag word list (there can be a lot of repeats). Note this 4th element was not used.
            if not dict_hash_with_tweets[hashtag]:
                dict_hash_with_tweets[hashtag] = [[], 0, 0, 0]
            dict_hash_with_tweets[hashtag][0] += tweet_wo_hashtag
            dict_hash_with_tweets[hashtag][1] += 1
    
    # Loop through dictionary and delete elements that have an empty list
    problem_hashtags = []
    for k, v in dict_hash_with_tweets.iteritems():
        if not v[0]: problem_hashtags.append(k)
    for hashtag in problem_hashtags:
        del dict_hash_with_tweets[hashtag]

    # Loop through dictionary and take the log of the number of tweets each hashtag has appeared in
    for v in dict_hash_with_tweets.values():
        v[1] = log10(v[1])

    #Normalize the hashtag frequency
    #list_of_normalized_pop = [] # a list of normalized hashtag popularities so I can histogram the distribution
    n_min = min(v[1] for v in dict_hash_with_tweets.values())
    n_max = max(v[1] for v in dict_hash_with_tweets.values())

    for v in dict_hash_with_tweets.values():
        v[1] = normalize_freq(v[1], n_min, n_max)
    #    list_of_normalized_pop.append(v[1])
    #plt.hist(list_of_normalized_pop, bins=[0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 1])
    #plt.savefig('hashtag_popularity_normalized.png')

    print('Done making the dictonary of hashtags and tweet count...')

    # Return the dictionary {'#hashtag': [['word1', 'word2', 'word3'], num_tweets_appeared_in]}
    return dict_hash_with_tweets






