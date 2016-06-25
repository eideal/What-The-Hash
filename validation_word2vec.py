####
#Model Validation
#Generate, clean, and train a word2vec model 
####

import psycopg2
import pickle
import string
import re

# Function to clean the text - Lowercase, remove punctuation, unicode, and links
def clean_tweet(tweet):
    printable = set(string.printable)
    punctuation = set(string.punctuation)
    tweet = filter(lambda x: x not in punctuation, tweet)
    tweet = filter(lambda x: x in printable, tweet)
    tweet = re.sub(r'http\S+', '', tweet)
    return tweet.lower()

# Connect to Attila's database of tweet text and extract only the tweet texts
conn = psycopg2.connect("host=52.40.74.90 port=5432 dbname=emoji_db user=postgres password=darkmatter")
cur = conn.cursor()
loc = "%US%"
cur.execute("""SELECT text, created_at FROM tweet_dump 
            WHERE (lang = 'en' AND time_zone LIKE %s) ORDER BY id DESC LIMIT 50000000;""", [loc])
results = cur.fetchall()
conn.close()
print('Collected 50 million tweets')

# Clean the tweets
cleaned_tweets = [clean_tweet(tweet[0]) for tweet in results]
#cleaned_tweets  = [word for sublist in cleaned_tweets for word in sublist] 
print('Done cleaning the tweets')

# Dump each word into a .txt file, each line on a unique line
f = open('validation_corpusfile.txt', 'w')
for tweet in cleaned_tweets:
    for word in tweet.split():
        f.write(word)
        f.write(' ')
    f.write('\n')    
f.close()

