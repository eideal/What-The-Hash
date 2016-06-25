from WhatTheHash import app
from flask import render_template
import pandas as pd
import operator
import pickle
from flask import request
from group_tweets import clean_tweet, remove_stopwords, clean_tweet_and_stopwords, normalize_freq
from gensim.models.word2vec import Word2Vec

@app.route('/')
@app.route('/input')
def tweet_input():
    return render_template('home.html')

@app.route('/output')
def tweet_output():

    #pull 'tweet_input' from input field and store it
    patient = request.args.get('tweet')
    patient_cleaned = clean_tweet_and_stopwords(patient)

    # Load the pickled dictionary
    with open('./WhatTheHash/hashtag_dict.pickle') as f:
        dict_hashtags = pickle.load(f)

    # Load the Word2Vec model
    model = Word2Vec.load('./WhatTheHash/bigram_model_updated')

    # Remove words from user's tweet that are not in the model's vocabulary
    patient_cleaned = ' '.join([word for word in patient_cleaned.split() if word in model.vocab])

    # Compute the number of user tweet words appearing with each hashtag
    for k, v in dict_hashtags.iteritems():
        count = 0
        for word in patient_cleaned.split():
            if word in v[0]: count += 1
        v[2] = count

    # Alternatively to the above, I can count the total # of times the words have appeared in the hashtag (not just once per word)
    # since a word may appear multiple times for a hashtag
    for k, v in dict_hashtags.iteritems():
        count = 0
        for word in patient_cleaned.split():
            count += v[0].count(word)
        v[3] = count

    
    # Compute most similar hashtags to a user tweet
    similarities = {}
    for k, v in dict_hashtags.iteritems():

        # Relative popularity information
        if v[1] <= 0.13: hashtag_pop = 1
        if v[1] > 0.13 and v[1] <= 0.38: hashtag_pop = 2
        if v[1] > 0.38 and v[1] <= 0.55: hashtag_pop = 3
        if v[1] > 0.55 and v[1] <= 0.75: hashtag_pop = 4
        if v[1] > 0.75: hashtag_pop = 5

        # Compute similarity score
        sim = model.n_similarity(v[0], patient_cleaned.split())

        # Boost by a custom function that takes the v[1] which was normalized to [0, 1] to [0.8, 1]
        # Handles hashtag popularity
        sim = float(sim) * (v[1] * 0.2 + 0.8)

        # Boost by the fraction of words in the user's tweet that are contained in hashtag
        # Handles relevance
        sim = float(sim) * float(v[2])/float(len(patient_cleaned.split()))   

        similarities[k] = [sim, hashtag_pop]

    # Sort the dictionary by value -> returns list of tuples [(hashtag, score), (hashtag2, score2)...]
    sorted_sim = sorted(similarities.items(), key=operator.itemgetter(1), reverse=True)

    # Take top 10 results to display
    sorted_sim = sorted_sim[:10]

    return render_template('results.html', hashtags=sorted_sim, user_input=patient)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


