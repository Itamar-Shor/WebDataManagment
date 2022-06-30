import numpy as np

import utils
from Inverted_index import InverseIndex
from collections import OrderedDict


class InformationExtraction:
    def __init__(self):
        self.tokenizer = utils.Tokenizer()
        self.index = None

    def get_ranking(self, query, ranking, index: InverseIndex):
        self.index = index
        q_key_words = self.tokenizer.tokenize_string(query)
        q_tf = dict()
        for word in q_key_words:
            if word not in q_tf:
                q_tf[word] = 0
            q_tf[word] += 1
        if ranking == 'tfidf':
            return self.rank_by_TF_IDF_score(q_tf)
        elif ranking == 'bm25':
            return self.rank_by_BM25_score(q_tf)
        else:
            print(f"Error: got unrecognized ranking '{ranking}'.")
            return None

    def rank_by_TF_IDF_score(self, query_key_words):
        R = dict()
        L = 0  # length(Q)
        Y = dict()  # length(D)
        for word in query_key_words:
            K = query_key_words[word]  # tf(word,Q)
            I = utils.calc_idf(df=self.index.get_df(word), D=self.index.get_corpus_size)
            W = K*I
            tf_list = self.index.get_tf_list(word)
            for doc, doc_tf in tf_list:
                # doc was not previously retrieved
                if doc not in R:
                    R[doc] = 0.0
                    Y[doc] = 0.0

                R[doc] += W*I*doc_tf
                Y[doc] += (I*doc_tf)**2
            L += (W**2)

        L = np.sqrt(L)
        for doc in R:
            R[doc] = R[doc] / (L*Y[doc])

        return [item for item in sorted(R.items(), key=lambda x: x[1], reverse=True)]

    def rank_by_BM25_score(self, query_key_words, k1, b):
        R = dict()
        for word in query_key_words:
            tf_list = self.index.get_tf_list(word)
            n = len(tf_list)
            D = self.index.get_corpus_size
            for doc, doc_tf in tf_list:
                if doc not in R:
                    R[doc] = 0.0

                idf = np.log(((D - n + 0.5) / (n + 0.5)) + 1)
                R[doc] += idf*((doc_tf * (k1+1)) / (doc_tf + k1*(1-b+b*(0x0000000001))))

        return [item for item in sorted(R.items(), key=lambda x: x[1], reverse=True)]