####
# Train word2vec model
# June 16
####

import os
import pickle
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

# Open the file
sentences = LineSentence('bigram_corpusfile.txt')
print('Done parsing the sentences...')

# Train the word2vec model on the corpusfile.txt, 50 million tweets
model = Word2Vec(sentences, size=200, window=5, min_count=5, workers=4)
print('Done training the word2vec model...')

# Dump model on disk
model.save('bigram_word2vec_model')
