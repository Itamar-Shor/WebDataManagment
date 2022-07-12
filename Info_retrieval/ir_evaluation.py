import os
from lxml import etree
from Information_retrieval import InformationRetrieval
import numpy as np

"""
query_db = {
    'query': <query>,
    'results': {
        <doc>: <score>,
    }
}
"""


def load_query_db(xml_path):
    with open(xml_path, 'r') as fd:
        db = etree.fromstring(fd.read())

    query_db = []
    query_items = db.xpath("//QUERY")
    for query_item in query_items:
        # q_num = query_item.xpath("./QueryNumber/text()")
        q_text = query_item.xpath("./QueryText/text()")[0]
        query_db.append({'query': q_text, 'results': {}})
        q_results = query_item.xpath(".//Item")
        for q_res in q_results:
            doc = int(q_res.xpath('./text()')[0])
            score = q_res.xpath('./@score')[0]
            query_db[-1]['results'][doc] = sum([int(i) for i in score])
    return query_db


def get_our_ret_list(ranking, index_path, question):
    retriever = InformationRetrieval()
    return retriever.get_ranking(question, ranking, index_path)[:100]


def calc_precision_recall(our_list, ideal_list):
    ret_rel_docs = 0
    for rel_doc in ideal_list:
        if rel_doc in our_list:
            ret_rel_docs += 1
    ret_docs = len(our_list)
    rel_docs = len(ideal_list)
    return (ret_rel_docs / ret_docs), (ret_rel_docs / rel_docs)


def calc_DCG(docs, n=10):
    docs_list = [item[1] for item in sorted(docs.items(), key=lambda x: x[1], reverse=True)]
    dcg = docs_list[0]
    i = 1
    for doc_idx in range(i, min(n, len(docs_list))):
        dcg += (docs_list[doc_idx] / (np.log2(i+1)))
    return dcg


def test(ranking, index_path, xml_path):
    query_db = load_query_db(xml_path)
    for query in query_db:
        our_list = get_our_ret_list(ranking, index_path, query['query'])
        ideal_list = query['results']
        precision, recall = calc_precision_recall(our_list, ideal_list)
        print(precision, recall)
        if(precision + recall != 0):
            F = (2 * precision * recall) / (precision + recall)
        else: F=0
        dcg = 0  # calc_DCG(our_list)
        idcg = 0  # calc_DCG(ideal_list)
        ndcg = 0  # dcg / idcg
        print(f"\nquery = {query['query']}\n\tprecision = {precision}\n\trecall = {recall}\n\tF = {F}\n\tNDCG = {ndcg}\n")


if __name__ == '__main__':
    path = r'cfquery.xml'
    test(ranking='bm25', index_path='vsm_inverted_index.json', xml_path=path)
