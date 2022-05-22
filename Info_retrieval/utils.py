from nltk.stem import PorterStemmer
import json
from nltk.tokenize import word_tokenize


class Tokenizer:
    def __init__(self):
        self.stemmer = PorterStemmer()
        with open(r'stop_words_english.json', 'r') as f:
            self.stop_words = json.load(f)

    def tokenize_string(self, st):
        words = word_tokenize(st)
        return {self.stemmer.stem(word) for word in words if word not in self.stop_words}
