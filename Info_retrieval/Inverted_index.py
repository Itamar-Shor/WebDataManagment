from operator import countOf
import os
from utils import Tokenizer
from utils import calc_idf, calc_cosine_similarity
import json
from lxml import etree
import math

"""
inverted_index = {
    vector_lens: [lens],
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
        self.dictionary = dict()
        self.inverted_index = dict()
        self.tokenizer = Tokenizer()
        self.IDFs = dict()

    def build_dictionary(self):
        """
        :param doc_path: path to a document to extract words from.
        :return: all the relevant words - after tokenization, removing stopwords and stemming.
        """
        c = 0
        for xml_doc in self.corpus:
            data = self.load_xml(xml_doc)
            self.dictionary.update(data)

        # print(self.dictionary)

    def load_xml(self, xml_path) -> dict:
        with open(xml_path, 'r') as fd:
            xml = etree.fromstring(fd.read())

        data = dict()
        list_records = []
        records = xml.xpath("//RECORD")

        for (idx, record) in enumerate(records):
            record_num = int(record.xpath("./RECORDNUM/text()")[0])
            data[record_num] = []
            list_records.append(record_num)

            record_title = record.xpath("./TITLE/text()")[0]

            data[list_records[idx]] = data[list_records[idx]] + self.tokenizer.tokenize_string(record_title)

            extract = record.xpath("./EXTRACT/text()")
            if (len(extract) > 0):
                record_extract = extract[0]
                data[list_records[idx]] = data[list_records[idx]] + self.tokenizer.tokenize_string(record_extract)

            abstract = record.xpath("./ABSTRACT/text()")
            if (len(abstract) > 0):
                record_abstract = abstract[0]
                data[list_records[idx]] = data[list_records[idx]] + self.tokenizer.tokenize_string(record_abstract)

        return data

    def build_inverted_index(self, index_path):
        self.build_dictionary()
        count = dict()

        for doc in self.dictionary.keys():

            hashmap_vec = self.build_hash_map_vector(doc)
            # print("doc, hashmap_vec ",doc, hashmap_vec)
            for key in hashmap_vec.keys():
                if ("patients" in key): print(key)
                if key not in self.inverted_index:
                    self.inverted_index[key] = {'df': 0, 'tf_list': []}
                self.inverted_index[key]['df'] += 1
                self.inverted_index[key]['tf_list'].append((doc, hashmap_vec[key]))
                # print("dvir ",self.inverted_index[key]['tf_list'])
                if key not in count:
                    count[key] = 0
                count[key] += 1

        # Compute IDF for all tokens in H;
        for T in self.inverted_index.keys():
            if T in count:
                self.IDFs[T] = calc_idf(df=count[T], D=len(self.dictionary))
        # print("IDFs: ", self.IDFs)

        # Compute vector lengths for all documents in H;
        vectors_len = dict()
        # print(" keys: ", self.inverted_index)
        for T in self.inverted_index.keys():
            # print("dvir ",self.inverted_index[T]['tf_list'])
            for doc, tf in self.inverted_index[T]['tf_list']:
                # print("(doc, tf): ",doc, tf)
                if doc not in vectors_len:
                    vectors_len[doc] = 0.0
                I = self.IDFs[T]
                C = tf
                vectors_len[doc] += (I * C) ** 2
                # print(doc)

        for doc in self.dictionary.keys():
            vectors_len[doc] = math.sqrt(vectors_len[doc])

        self.inverted_index['vector_lens'] = vectors_len
        self.inverted_index['doc_lens'] = {doc: len(self.dictionary[doc]) for doc in self.dictionary}

        with open(index_path, "w") as outfile:
            json.dump(self.inverted_index, outfile, indent=4)

    def build_hash_map_vector(self, doc):
        hashmap_vec = dict()  # { word: occ , ...}
        words = self.dictionary[doc]
        max = 1
        for word in set(words):
            count = countOf(words, word)
            if (count > max): max = count
            hashmap_vec[word] = countOf(words, word)

        hashmap_vec = {word: hashmap_vec[word] / max for word in hashmap_vec}
        return hashmap_vec

# if __name__ == "__main__":
#     path = os.path.join(os.path.dirname(__file__), 'cfc-xml_corrected')

#     inv = InverseIndex(path)
#     inv.build_inverted_index(path)
