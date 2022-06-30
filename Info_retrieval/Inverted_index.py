import os
from utils import Tokenizer

"""
inverted_index = {
    word: {
        df: <val>,
        tf_list: [(doc, tf), (doc, tf), ...]
    }
}
"""

"""
docs_len = {
    doc: <len>,
}
"""


class InverseIndex:
    def __init__(self, corpus_path):
        self.corpus = [os.path.join(corpus_path, file) for file in os.listdir(corpus_path)]
        self.dictionary = set()
        self.inverted_index = dict()
        self.docs_len = dict()
        self.tokenizer = Tokenizer()

    def build_dictionary(self):
        """
        :param doc_path: path to a document to extract words from.
        :return: all the relevant words - after tokenization, removing stopwords and stemming.
        """
        for doc in self.corpus:
            with open(doc, 'r') as f:
                data = f.read()
                self.dictionary.update(self.tokenizer.tokenize_string(data))

    def get_corpus_size(self):
        return len(self.corpus)

    def get_df(self, word):
        return self.inverted_index[word]['df']

    def get_tf_list(self, word):
        return self.inverted_index[word]['tf_list']

    def build_inverted_index(self):
        self.build_dictionary()
