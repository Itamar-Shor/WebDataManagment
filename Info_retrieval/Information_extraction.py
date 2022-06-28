import numpy as np

import utils
# from Inverted_index import InverseIndex
from collections import OrderedDict


class InformationExtraction:
    def __init__(self):
        self.tokenizer = utils.Tokenizer()
        self.index = None

    def get_ranking(self, query, ranking, index):
        self.index = index
        # TODO: remove words that not in the dict
        q_key_words = self.tokenizer.tokenize_string(query)
        if ranking == 'tfidf':
            return self.rank_by_TF_IDF_score(q_key_words)
        elif ranking == 'bm25':
            return self.rank_by_BM25_score(q_key_words)
        else:
            print(f"Error: got unrecognized ranking '{ranking}'.")
            return None

    def rank_by_TF_IDF_score(self, query_key_words):
        # weights = np.zeros((len(query_key_words), len(index.corpus)))
        weights = [[self.index.TF[doc][word]*self.index.IDF[word] for doc in self.index.corpus] for word in self.index.dictionary]
        d = [[weights[word][doc] for word in self.index.dictionary] for doc in self.index.corpus]
        q = None
        ranks = OrderedDict()
        for i, doc in enumerate(self.index.dictionary):
            ranks[doc] = utils.cosine_similarity(d[i], q)

        return OrderedDict(sorted(ranks.items(), key=lambda t: t[1], reverse=True)).keys()

    def rank_by_BM25_score(self, query_key_words):
        n = {q_word: 0 for q_word in query_key_words}  # number og docs containing q_word
        N = len(self.index.corpus)
        idf = {q: np.log(((N-n[q]+0.5)/(n[q]+0.5)) + 1) for q in query_key_words}
        ranks = OrderedDict()
        for i, doc in enumerate(self.index.dictionary):
            ranks[doc] = np.sum([idf[q]*(()/()) for q in query_key_words])
