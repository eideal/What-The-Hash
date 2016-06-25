######################################################
# Run all the time to update the tweets database and do hashtag computation
######################################################

import time
import pickle
from update_database import get_tweets
from group_tweets import clean_tweet, generate_hashtag_dict

while True:
    # Insert last 8 hours into database
    get_tweets()
    
    # Generate the list of hashtags and their corresponding words
    dict_hash_with_tweets = generate_hashtag_dict()

    # Pickle the dictionary
    with open('hashtag_dict.pickle', 'wb') as handle:
        pickle.dump(dict_hash_with_tweets, handle)

    # Sleep for 1 hour
    time.sleep(3600)