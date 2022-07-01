from nltk.stem import PorterStemmer
import json
from nltk.tokenize import word_tokenize
import numpy as np
from numpy.linalg import norm
import nltk


class Tokenizer:
    def __init__(self):
        # nltk.download()
        self.stemmer = PorterStemmer()
        with open(r'stop_words_english.json', 'r', errors='ignore') as f:
            self.stop_words = json.load(f)

    def tokenize_string(self, st):
        words = word_tokenize(st)
        # TODO: maybe ignore numbers
        return [self.stemmer.stem(word) for word in words if word not in self.stop_words]


def calc_idf(df, D):
    return np.log2(D / df)


def calc_cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (norm(v1)*norm(v2))