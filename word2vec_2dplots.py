from matplotlib import pylab
from sklearn.decomposition import PCA
from gensim.models import Word2Vec
from sklearn.manifold import TSNE

## Function to reduce 200-dimension word2vec model down to 2D for visualizing word similarities
def plot(words):
    embeddings = [model[w] for w in words]

    pca = PCA(n_components = 2)
    two_d_embeddings = pca.fit_transform(embeddings)

    pylab.figure(figsize=(5,5))
    for i, label in enumerate(words):
        x, y = two_d_embeddings[i,:]
        pylab.scatter(x,y)
        pylab.annotate(label, xy=(x,y), xytext=(28, 2), 
            textcoords = 'offset points', ha='right', va='bottom')
    pylab.savefig('testplot19.png')

model = Word2Vec.load('bigram_model_updated')

#plot('cake pizza salad cat horse dog car motorcycle train'.split())

