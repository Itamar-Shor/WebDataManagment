from operator import countOf
import os
from utils import Tokenizer
from utils import calc_idf, calc_cosine_similarity
import json

"""
inverted_index = {
    corpus: [file_paths],
    doc_lens: [lens],
    word: {
        df: <val>,
        tf_list: [(doc, tf), (doc, tf), ...]
    }
    .
    .
    .
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
        # self.corpus = [self.corpus[0]]
        self.dictionary = []
        self.inverted_index = {'corpus': self.corpus}
        self.tokenizer = Tokenizer()
        self.IDFs = dict()

    def build_dictionary(self):
        """
        :param doc_path: path to a document to extract words from.
        :return: all the relevant words - after tokenization, removing stopwords and stemming.
        """
        for doc in self.corpus:
            with open(doc, 'r') as f:
                data = f.read()
                self.dictionary.append(self.tokenizer.tokenize_string(data))

    def build_inverted_index(self, index_path):
        self.build_dictionary()
        count = dict()

        for doc_idx in range(len(self.corpus)):
            hashmap_vec = self.build_hash_map_vector(doc_idx)
            for key in hashmap_vec.keys():
                if key not in self.inverted_index:
                    self.inverted_index[key] = {'df': 0, 'tf_list': []}
                self.inverted_index[key]['df'] += 1
                self.inverted_index[key]['tf_list'].append((doc_idx, hashmap_vec[key]))
                if key not in count:
                    count[key] = 0
                count[key] += 1

        # Compute IDF for all tokens in H;
        for T in self.inverted_index.keys():
            self.IDFs[T] = calc_idf(count[T], len(self.corpus))
        # print("IDFs: ", self.IDFs)

        # Compute vector lengths for all documents in H;
        docs_len = [0.0 for _ in self.corpus]
        for T in self.inverted_index.keys():
            for (doc_idx, tf) in self.inverted_index[T]['tf_list']:
                I = self.IDFs[T]
                C = tf
                docs_len[doc_idx] += (I * C) ** 2
        for doc_idx in range(len(self.corpus)):
            docs_len[doc_idx] = docs_len[doc_idx] ** 0.5
        print("docs_len: ", docs_len)

        self.inverted_index['doc_lens'] = docs_len

        with open(index_path, "w") as outfile:
            json.dump(self.inverted_index, outfile, indent=4)

    def build_hash_map_vector(self, doc_idx):
        hashmap_vec = dict()  # { word: occ , ...}
        words = self.dictionary[doc_idx]
        for word in set(words):
            hashmap_vec[word] = countOf(words, word)
        return hashmap_vec


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), 'cfc-xml_corrected')

    inv = InverseIndex(path)
    inv.build_inverted_index()
