from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import numpy as np
from numpy.linalg import norm
import nltk


class Tokenizer:
    def __init__(self):
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.stemmer = PorterStemmer()
        try:
            self.stop_words = set(stopwords.words("english"))
        except:
            nltk.download('stopwords')
            self.stop_words = set(stopwords.words("english"))

    def tokenize_string(self, st):
        words = self.tokenizer.tokenize(st)
        return [self.stemmer.stem(word) for word in words if word.lower() not in self.stop_words]


def calc_idf(df, D):
    return np.log2(D / df)


def calc_cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (norm(v1)*norm(v2))