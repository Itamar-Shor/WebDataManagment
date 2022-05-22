from utils import Tokenizer


class InformationExtraction:
    def __init__(self):
        self.tokenizer = Tokenizer()

    def get_ranking(self, query, ranking, index_path):
        q_key_words = self.tokenizer.tokenize_string(query)
        if ranking == 'tfidf':
            return self.rank_by_TF_IDF_score(q_key_words, index_path)
        elif ranking == 'bm25':
            return self.rank_by_BM25_score(q_key_words, index_path)
        else:
            print(f"Error: got unrecognized ranking '{ranking}'.")
            return None

    def rank_by_TF_IDF_score(self, query_key_words, index_path):
        pass

    def rank_by_BM25_score(self, query_key_words, index_path):
        pass
