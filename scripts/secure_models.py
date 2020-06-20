import json
import pickle
import re
import string
import numpy as np
import multiprocessing as mp
from googletrans import Translator
from nltk.corpus import stopwords
from nltk.corpus import words as engWords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.metrics.pairwise import linear_kernel
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer



with open("../data/preprocessed_data.pk", 'rb') as fp:
        result = pickle.load(fp)
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english')
result = list(set(result))
tf = tf_vectorizer.fit_transform(result)
tf_feature_names = tf_vectorizer.get_feature_names()


# tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=no_features, tokenizer = word_tokenize, stop_words='english')
# result = list(set(result))
# tfidf = tfidf_vectorizer.fit_transform(result)
# tfidf_feature_names = tfidf_vectorizer.get_feature_names()


# Run LDA
no_topics = 3
# nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
lda = LatentDirichletAllocation(n_components=no_topics, max_iter=10, learning_method='online', learning_offset=50.,random_state=0).fit(tf)

with open("../data/lda_data.pk", 'wb') as fp:
    pickle.dump([tf_vectorizer, tf, lda], fp)
print('LDA models secured')
