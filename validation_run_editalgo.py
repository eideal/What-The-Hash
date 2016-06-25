####
# Run after validation_train.py
# Testing the algorithm with the word2vec model
# This algorithm is different from the default - we order the top 20 relevant results by popularity
####

import psycopg2
import pickle
import datetime
import operator
import re
import string
from nltk.corpus import stopwords
from group_tweets import clean_tweet, remove_stopwords, clean_tweet_and_stopwords, normalize_freq
from gensim.models.word2vec import Word2Vec

# Cache the English stopwords
cachedStopWords = stopwords.words("english")

# Function to clean the tweets
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

# Connect to database
conn = psycopg2.connect("host=52.40.74.90 port=5432 dbname=emoji_db user=postgres password=darkmatter")
cur = conn.cursor()

# Get most recent tweet data 
start_time=datetime.datetime.now()-datetime.timedelta(hours=0.1)
loc="%US%"
word="%#%"
cur.execute("""SELECT text FROM tweet_dump 
            WHERE (created_at > %s AND lang = 'en' AND time_zone LIKE %s AND text LIKE %s) 
            ORDER BY id DESC;""", [start_time,loc, word])
results = cur.fetchall()

# Close the database connection
conn.close()
print('Done pulling tweets')

# Load the pickled dictionary of hashtags and their associated words
with open('hashtag_dict.pickle') as f:
    dict_hashtags = pickle.load(f)

# Load the word2vec model
model = Word2Vec.load('validation_word2vec_model')
print('Done loading the model')

# Loop through the tweets, extract the hashtags, remove words not in word2vec model
tweet_hashtag_list = []
for tweet in results:
    text = tweet[0]
    if text.count('#') != 1: continue
    tweet_cleaned = clean_tweet_and_stopwords(text)
    hashtag = [word for word in tweet_cleaned.split() if re.search(r'^#', word)]
    tweet_cleaned = ' '.join([word for word in text.split() if word in model.vocab])
    tweet_cleaned = ' '.join([word for word in tweet_cleaned.split() if word not in hashtag])
    tweet_hashtag_list.append([tweet_cleaned, hashtag, None])
tweet_hashtag_list = tweet_hashtag_list[:500]


# Compute the number of user tweet words appearing with each hashtag
##### Have to deal with multiple tweets and multiple hashtags
#######################
def edit_dict(tweet):
    for k, v in dict_hashtags.iteritems():
        count = 0
        for word in tweet.split():
            if word in v[0]: count += 1
        v[2] = count
    
    # Alternatively to the above, I can count the total # of times the words have appeared in the hashtag (not just once per word)
    # since a word may appear multiple times for a hashtag
    #for k, v in dict_hashtags.iteritems():
    #    count = 0
    #    for word in tweet.split():
    #        count += v[0].count(word)
    #    v[3] = count
    #    print(v[3])
    
    # Normalize the total number of words in user's input appearing in hashtag text
    #n_min = min(v[3] for v in dict_hashtags.values())
    #n_max = max(v[3] for v in dict_hashtags.values())
    #for v in dict_hashtags.values():
    #    v[3] = normalize_freq(v[3], n_min, n_max)
    return dict_hashtags
    
# Compute most similar hashtags to a user tweet
similarities = {}
for i, tweet in enumerate(tweet_hashtag_list):

    if (i % 5 == 0): print 'On ', i

    dict_hashtags = edit_dict(tweet[0])

    for k, v in dict_hashtags.iteritems():
        
        text_in_new_model = [word for word in v[0] if word in model.vocab]
        
        # Deal with those where the hashtag has no words, e.g. if all its words were not in the model
        if not text_in_new_model:
            sim = 0
        # Deal with those tweets that now have no text
        if not tweet[0]:
            sim = -1
        else:
            sim = model.n_similarity(text_in_new_model, tweet[0].split())
         
            # Boost by a custom function that takes the v[1] which was normalized to [0, 1] to [0.75, 1] - handles popularity
            #sim = float(sim) * (v[1] * 0.2 + 0.8)
            
            # Boost by the fraction of words in the user's tweet that are contained in hashtag - handles relevance
            sim = float(sim) * float(v[2])/float(len(tweet[0].split()))

        # Boost by the number of times words in user's tweet have appeared in hashtag's word list
        #sim = float(sim) * float(v[3])           
        similarities[k] = sim

    # Sort the dictionary by value -> returns list of tuples [(hashtag, score), (hashtag2, score2)...]
    sorted_sim = sorted(similarities.items(), key=operator.itemgetter(1), reverse=True)

    # Grab top 20 hashtag recommendations
    # Loop through dictionary and get popularity of hashtag and append that to the tweet_hashtag_list
    sorted_sim_list = []
    for hashtag in sorted_sim[:20]:
        for k, v in dict_hashtags.iteritems():
            if k == hashtag[0]:
                sorted_sim_list.append([k, hashtag[1], v[1]])

    # Sort the top 20 relevant hashtags by their popularity
    sorted_sim_list = sorted(sorted_sim_list, key=operator.itemgetter(2), reverse=True)
            
    tweet_hashtag_list[i][2] = sorted_sim_list


# Dump a pickle of this list
with open('validation3_editalgo.pickle', 'wb') as handle:
        pickle.dump(tweet_hashtag_list, handle)






