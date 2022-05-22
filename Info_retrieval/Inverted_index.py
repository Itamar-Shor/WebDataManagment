import os
from utils import Tokenizer


class InverseIndex:
    def __init__(self, corpus_path):
        self.dictionary = []
        self.corpus = {}
        for file in os.listdir(corpus_path):
            self.corpus[os.path.join(corpus_path, file)] = {
                'TF': 0,
                'IDF': 0,
                'LEN': 0
            }
        self.tokenizer = Tokenizer()

    def build_dictionary(self, doc_path):
        """
        :param doc_path: path to a document to extract words from.
        :return: all the relevant words - after tokenization, removing stopwords and stemming.
        """
        with open(doc_path, 'r') as f:
            data = f.read()
            return self.tokenizer.tokenize_string(data)

    def calc_score(self, doc_path):
        """
        :param doc_path: path to a document to calc IDF/TF scores.
        :return: the IDF and TF scores of the document.
        """
        pass

    def build_inverted_index(self):
        pass