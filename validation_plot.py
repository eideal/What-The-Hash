####
# Run after validation_run.py
# Plotting the validation output
####

import pickle
import re
from gensim.models.word2vec import Word2Vec
import matplotlib.pyplot as plt

# Load the validation list of tweet-hashtag-ranked returned hashtags
# This is a subset of 500 tweets
with open('validation3_bigram.pickle') as f:
    validation = pickle.load(f)
print('Done loading the validation data...')

# Load the word2vec model
#model = Word2Vec.load('validation_word2vec_model')
model = Word2Vec.load('bigram_word2vec_model')
print('Done loading the model...')

# Loop through the tweets, skipping those that don't have words or that have sim = 0 for all hashtags
# Reference validation_run for why these conditions exist
sim_top_truth = []
rank_truth_equals_recom = []
count_truth_in_recom = 0
for i, tweet in enumerate(validation):
    
    if not tweet[0] or not tweet[1]:
        continue
    if tweet[2][0][1] == 0:
        continue

    else:
        tweet_text = tweet[0]
        actual_hashtag = tweet[1][0]
        list_of_recom_hashtags = tweet[2]
        recom_hashtags = [hashtag[0] for hashtag in list_of_recom_hashtags]

        if actual_hashtag in recom_hashtags:
            count_truth_in_recom += 1
            rank_truth_equals_recom.append(recom_hashtags.index(actual_hashtag))

        # Remove the hashtag
        truth_hashtag = re.sub(r'#', '', actual_hashtag)
        # Top recommended hashtag is the hashtag I recommended as being the best match
        top_recom_hashtag = list_of_recom_hashtags[0][0]
        # Remove the hashtag
        top_recom_hashtag = re.sub(r'#', '', top_recom_hashtag)

        # Compute similarity between top recommendation and truth hashtag
        if truth_hashtag in model.vocab and top_recom_hashtag in model.vocab:
            sim = model.similarity(truth_hashtag, top_recom_hashtag)
            sim_top_truth.append(sim)

print(float(count_truth_in_recom)/float(len(validation))) # ~60%

# Histogram the similarities
#plt.hist(sim_top_truth, bins=[-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
#plt.title("Similarity between top recommended hashtag and actual")
#plt.xlabel("Word2Vec similarity")
#plt.ylabel("Frequency")
#plt.show()
#plt.savefig('sim_top_truth_bigrams.png')

# Histogram the ranks
plt.hist(rank_truth_equals_recom, bins=range(100))
plt.title("Rank of truth hashtag in recommendations")
plt.xlabel("Rank")
plt.ylabel("Frequency")
#plt.show()
plt.savefig('rank_truth_equals_recom_bigrams.png')







