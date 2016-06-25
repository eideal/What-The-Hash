####
# Ran after validation_word2vec.py
# Train the validation word2vec model
# June 11
####

import os
import pickle
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

# Open the file
sentences = LineSentence('validation_corpusfile.txt')
print('Done parsing the sentences...')

# Train the word2vec model on the corpusfile.txt, 50 million tweets
model = Word2Vec(sentences, size=200, window=5, min_count=5, workers=4)
print('Done training the validation word2vec model...')

# Dump model on disk
model.save('validation_word2vec_model')


# Test the model
#tweet1 = 'hillary clinton president'
#tweet2 = 'clinton bernie sanders'
#tweet3 = 'duck babies'
#hillary = 'hillary' in model.vocab
#print(hillary)
#sim1 = model.n_similarity(tweet1.split(), tweet2.split())
#sim2 = model.n_similarity(tweet1.split(), tweet3.split())
#sim3 = model.n_similarity(tweet2.split(), tweet3.split())
#print('sim1 is: ', sim1)
#print('sim2 is: ', sim2)
#print('sim3 is: ', sim3) 


