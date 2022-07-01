from operator import countOf
import os
from utils import Tokenizer
from utils import calc_idf, calc_cosine_similarity

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
        # self.corpus = [self.corpus[0]]
        self.dictionary = dict() # { doc: words, ...}
        self.inverted_index = dict()
        self.docs_len = dict()
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
                self.dictionary[doc] = self.tokenizer.tokenize_string(data)

    def get_corpus_size(self):
        return len(self.corpus)

    def get_df(self, word):
        return self.inverted_index[word]['df']

    def get_tf_list(self, word):
        return self.inverted_index[word]['tf_list']

    def build_inverted_index(self):
        self.build_dictionary()
        count = dict()
        
        for doc in self.corpus:
            hashmap_vec = self.build_hash_map_vector(doc)
            for key in hashmap_vec.keys():
                if key not in self.inverted_index:
                    self.inverted_index[key] = {'df': 0, 'tf_list': []}
                self.inverted_index[key]['df'] += 1
                self.inverted_index[key]['tf_list'].append((doc, hashmap_vec[key]))
                if key not in count:
                    count[key] = 0
                count[key] += 1
        
        
        # Compute IDF for all tokens in H;
        for T in self.inverted_index.keys():
            self.IDFs[T] = calc_idf(count[T], len(self.corpus))
        #print("IDFs: ", self.IDFs)
        
        # Compute vector lengths for all documents in H;
        for doc in self.corpus:
            self.docs_len[doc] = 0.0
        for T in self.inverted_index.keys():
            for (doc, tf) in self.inverted_index[T]['tf_list']:
                I = self.IDFs[T]
                C = tf
                self.docs_len[doc] += (I*C)**2
        for doc in self.corpus:
            self.docs_len[doc] = self.docs_len[doc] ** 0.5
        print("docs_len: ", self.docs_len)
            
            
        
    
    def build_hash_map_vector(self, doc):
        hashmap_vec = dict() # { word: occ , ...}
        words = self.dictionary[doc]
        for word in set(words):
            hashmap_vec[word] = countOf(words, word)
        return hashmap_vec


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), 'cfc-xml_corrected')
    
    inv = InverseIndex(path)
    inv.build_dictionary()
    inv.build_inverted_index()
    