#####
# Clean and split the corpus of Twitter tweet text that I'l use to train the word2vec model
#####

import os
import pickle
import string
import re
from nltk import bigrams

# Clean the text
# Lowercase, remove punctuation, unicode, and links
def clean_tweet(tweet):
    printable = set(string.printable)
    punctuation = set(string.punctuation)
    tweet = filter(lambda x: x not in punctuation, tweet)
    tweet = filter(lambda x: x in printable, tweet)
    tweet = re.sub(r'http\S+', '', tweet)
    return tweet.lower()

def get_bigrams_from_tweet(tweet):
    # Return a list of bigram tuples
    tweet_split = tweet.split()
    return list(bigrams(tweet_split))

# Load the pickled list of Tweet text
# Tweets are from the US and Canada and are written in English
with open('bigram_twitter_corpus.pickle') as f:
        tweets_list = pickle.load(f)

# Clean the tweets
cleaned_tweets = [clean_tweet(tweet[0]) for tweet in tweets_list]
print('Finished cleaning the tweets')

# Dump each word into a .txt file, each line on a unique line
f = open('bigram_corpusfile.txt', 'w')
for tweet in cleaned_tweets:
    for word in tweet.split():
        f.write(word)
        f.write(' ')
    f.write('\n')

    tweet_bigrams = get_bigrams_from_tweet(tweet)
    for bigram in tweet_bigrams:
        f.write(' '.join(bigram))
        f.write('\n')
          
f.close()





