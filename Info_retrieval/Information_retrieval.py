import numpy as np

import utils
import json


class InformationRetrieval:
    def __init__(self):
        self.tokenizer = utils.Tokenizer()
        self.index = None

    def get_ranking(self, query, ranking, index_path):
        with open(index_path, 'r') as fd:
            self.index = json.load(fd)
        q_key_words = self.tokenizer.tokenize_string(query)
        q_tf = dict()
        for word in q_key_words:
            if word not in q_tf:
                q_tf[word] = 0
            q_tf[word] += 1
        if ranking == 'tfidf':
            return self.rank_by_TF_IDF_score(q_tf)
        elif ranking == 'bm25':
            return self.rank_by_BM25_score(q_tf, k1=0.5, b=0.5)
        else:
            print(f"Error: got unrecognized ranking '{ranking}'.")
            return None

    def rank_by_TF_IDF_score(self, query_key_words):
        R = dict()
        L = 0  # length(Q)
        Y = dict()  # length(D)
        for word in query_key_words:
            K = query_key_words[word]  # tf(word,Q)
            I = utils.calc_idf(df=self.index[word]['df'], D=len(self.index['corpus']))
            W = K*I
            tf_list = self.index[word]['tf_list']
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

        return [self.index['corpus'][idx] for idx in sorted(R.items(), key=lambda x: x[1], reverse=True)]

    def rank_by_BM25_score(self, query_key_words, k1, b):
        R = dict()
        avgdl = np.average(self.index['doc_lens'])
        for word in query_key_words:
            tf_list = self.index[word]['tf_list']
            n = len(tf_list)
            N = len(self.index['corpus'])
            for doc, doc_tf in tf_list:
                if doc not in R:
                    R[doc] = 0.0

                D = self.index['doc_lens'][doc]

                idf = np.log(((N - n + 0.5) / (n + 0.5)) + 1)
                R[doc] += idf*((doc_tf * (k1+1)) / (doc_tf + k1*(1-b+b*(D/avgdl))))

        return [self.index['corpus'][idx] for idx in sorted(R.items(), key=lambda x: x[1], reverse=True)]
