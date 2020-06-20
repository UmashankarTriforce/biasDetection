
import json
import pickle
import re
import string
import numpy as np
import multiprocessing as mp
# from translate import Translator
from nltk.corpus import stopwords
from nltk.corpus import words as engWords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.metrics.pairwise import linear_kernel
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
no_features = 1000
analyzer = SentimentIntensityAnalyzer()
# translator = Translator(to_lang = 'en')


def preprocess_text(line):

    if(line == '' or line == ' '):
        return " "
    words = set(engWords.words())
    wordnet_lemmatizer = WordNetLemmatizer()
    # print("before  ", line)
    # print(type(line))
    line = line.strip(" ")
    print("before", line)
    # line = translator('en', 'hi', line)
    print("after", line)
    # print("after  ", text)
    line = line.encode('ascii', 'ignore').decode('ascii')
    
    line = line.lower()
    line = re.sub("^\d+\s|\s\d+\s|\s\d+$", " ", line)
    line = re.sub(r'&amp;', ' ', line)

    stopWords = set(stopwords.words("english"))
    # print("int", line)
    tokenizedWords = word_tokenize(line)
    # print("int", tokenizedWords)
    filtText = [w for w in tokenizedWords if w not in stopWords]
#     stemmer = PorterStemmer()
    filtText = [wordnet_lemmatizer.lemmatize(w) for w in filtText]
    
#     filtText = [line for line in filtText if line in words]
    filtText = " ".join(filtText)
#     print(filtText)
#     try:
#         filtText = translator.translate(filtText).line
#     except Exception as e:
#         print(str(e))
    return filtText
    




def obtain_all_texts(data):
    texts = list(map(lambda x : x["text"], data))
    texts += list(map(lambda x : x["retweeted_status"]["text"] if("retweeted_status" in x.keys()) else " ", data))
    texts += list(map(lambda x : x["quoted_status"]["text"] if("quoted_status" in x.keys()) else " ", data))    
    return texts



if __name__ == "__main__":
    with open('../caa_raw_data.json', encoding="utf-8") as f:
        data = json.load(f)
    
    texts = obtain_all_texts(data)

    with mp.Pool() as pool:
        result = pool.map(preprocess_text, texts)


    with open("../data/preprocessed_data.pk", 'wb') as fp:
            pickle.dump(result, fp)
    print("preprocessed data secured")