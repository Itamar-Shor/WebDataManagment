import numpy as np
import utils
import json


def calc_tf_for_query(q_tokens):
    q_tf = dict()
    for word in q_tokens:
        if word not in q_tf:
            q_tf[word] = 0
        q_tf[word] += 1
    max_freq = q_tf[max(q_tf, key=q_tf.get)]
    return {term: (q_tf[term] / max_freq) for term in q_tf}


class InformationRetrieval:
    def __init__(self):
        self.tokenizer = utils.Tokenizer()
        self.index = None
        self.N = 15
        self.result_path = 'ranked_query_docs.txt'

    def get_ranking(self, query, ranking, index_path, k1=1.2, b=0.15):
        with open(index_path, 'r') as fd:
            self.index = json.load(fd)
        q_key_words = self.tokenizer.tokenize_string(query)

        if ranking == 'tfidf':
            ranked_docs = self.rank_by_TF_IDF_score(q_key_words)[:self.N]
        elif ranking == 'bm25':
            # TODO: set k1 and b
            ranked_docs = self.rank_by_BM25_score(q_key_words, k1=k1, b=b)[:self.N]
        else:
            print(f"Error: got unrecognized ranking '{ranking}'.")
            return

        with open(self.result_path, 'w') as fd:
            fd.write('\n'.join(ranked_docs))

    def rank_by_TF_IDF_score(self, query_key_words):
        R = dict()
        L = 0  # length(Q)
        q_tf = calc_tf_for_query(query_key_words)
        for word in q_tf:
            K = q_tf[word]  # tf(word,Q)
            if word not in self.index:
                continue

            I = utils.calc_idf(df=self.index[word]['df'], D=len(self.index['doc_lens']))
            W = K*I  # query weight
            tf_list = self.index[word]['tf_list']
            for doc, doc_tf in tf_list:
                # doc was not previously retrieved
                if doc not in R:
                    R[doc] = 0.0
                R[doc] += W*I*doc_tf

            L += (W**2)

        L = np.sqrt(L)
        for doc in R:
            Y = self.index['vector_lens'][f"{doc}"]
            R[doc] = R[doc] / (L * Y)

        return [str(idx[0]) for idx in sorted(R.items(), key=lambda x: x[1], reverse=True)]

    def rank_by_BM25_score(self, query_key_words, k1, b):
        R = dict()
        avgdl = np.average(list(self.index['doc_lens'].values()))
        for word in query_key_words:
            if word not in self.index:
                continue
            tf_list = self.index[word]['tf_list']
            n = len(tf_list)
            N = len(self.index['doc_lens'])
            for doc, doc_tf in tf_list:
                if doc not in R:
                    R[doc] = 0.0

                D = self.index['doc_lens'][f"{doc}"]

                idf = np.log(((N - n + 0.5) / (n + 0.5)) + 1)
                R[doc] += idf*((doc_tf * (k1+1)) / (doc_tf + k1*(1-b+b*(D/avgdl))))

        return [str(idx[0]) for idx in sorted(R.items(), key=lambda x: x[1], reverse=True)]

    def parse_ranked_list_from_file(self):
        with open(self.result_path, 'r') as fd:
            lines = fd.read().splitlines()
            retrieved_documents = [int(line.rstrip()) for line in lines]
        return retrieved_documents
