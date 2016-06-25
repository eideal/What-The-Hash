#####
# Generate the corpus of Twitter tweet text that I'll use to train the word2vec model
#####

import psycopg2
import pickle

# Connect to Attila's database of tweet text and extract only the tweet texts
conn = psycopg2.connect("host=52.40.74.90 port=5432 dbname=emoji_db user=postgres password=darkmatter")
cur = conn.cursor()
loc = "%US%"
cur.execute("""SELECT text FROM tweet_dump 
            WHERE (lang = 'en' AND time_zone LIKE %s) ORDER BY id DESC LIMIT 50000000;""", [loc])
results = cur.fetchall() # returns a list
conn.close()

# Pickle the list of text
with open('bigram_twitter_corpus.pickle', 'wb') as handle:
        pickle.dump(results, handle)






