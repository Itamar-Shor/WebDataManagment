import os
from lxml import etree
from Information_retrieval import InformationRetrieval
import numpy as np
import sys

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
            query_db[-1]['results'][doc] = sum([int(i) for i in score])  # / 4
    return query_db


def get_our_ret_list(ranking, index_path, question, k1=1.2, b=0.15):
    retriever = InformationRetrieval()
    our_l = retriever.get_ranking(question, ranking, index_path, k1=k1, b=b)[:10]
    return our_l


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
        dcg += (docs_list[doc_idx] / (np.log2(doc_idx+1)))
    return dcg


def evaluate_results(our_list, ideal_list):
    precision, recall = calc_precision_recall(our_list, ideal_list)
    if precision + recall != 0:
        F = (2 * precision * recall) / (precision + recall)
    else:
        F = 0
    # scores defined by the ideal list
    our_list_w_scores = dict()
    for doc in our_list:
        our_list_w_scores[doc] = ideal_list[doc] if doc in ideal_list else 0

    dcg = calc_DCG(our_list_w_scores)
    idcg = calc_DCG(ideal_list)
    ndcg = dcg / idcg
    return precision, recall, F, ndcg


def test(ranking, index_path, xml_path):
    query_db = load_query_db(xml_path)
    for idx, query in enumerate(query_db):
        our_list = get_our_ret_list(ranking, index_path, query['query'])
        ideal_list = query['results']
        precision, recall, F, ndcg = evaluate_results(our_list, ideal_list)
        print(f"\n[{idx}]: query = {query['query']}\n\tprecision = {precision}\n\trecall = {recall}\n\tF = {F}\n\tNDCG = {ndcg}\n")
        print(our_list)


def find_optimal_params_for_bm25(index_path, xml_path):
    k1_vals = [1.2, 1.35, 1.5, 1.65, 1.8, 1.95, 2.1, 2.2]  # between 1.2 and 2.2
    b_vals = [0.15, 0.3, 0.45, 0.6, 0.75, 0.9]  # between 0 and 1 (usually 0.75)
    query_db = load_query_db(xml_path)
    res = dict()
    max_F, max_NDCG = 0, 0
    optimal_params_F, optimal_params_NDCG = [None, None], [None, None]
    for k1 in k1_vals:
        res[k1] = dict()
        for b in b_vals:
            res[k1][b] = {
                'F_SCORE': 0,
                'NDCG': 0
            }
            for query in query_db:
                our_list = get_our_ret_list('bm25', index_path, query['query'], k1=k1, b=b)
                ideal_list = query['results']
                _, _, F, ndcg = evaluate_results(our_list, ideal_list)
                res[k1][b]['F_SCORE'] += F
                res[k1][b]['NDCG'] += ndcg

            if res[k1][b]['F_SCORE'] > max_F:
                optimal_params_F = [k1, b]
                max_F = res[k1][b]['F_SCORE']
            if res[k1][b]['NDCG'] > max_NDCG:
                optimal_params_NDCG = [k1, b]
                max_NDCG = res[k1][b]['NDCG']
    print(f"The optimal parameters considering F score are:\n\tk1 = {optimal_params_F[0]}\n\tb = {optimal_params_F[1]}")
    print(f"The optimal parameters considering NDCG are:\n\tk1 = {optimal_params_NDCG[0]}\n\tb = {optimal_params_NDCG[1]}")


if __name__ == '__main__':
    test(ranking=sys.argv[1], index_path=sys.argv[2], xml_path=sys.argv[3])
    # find_optimal_params_for_bm25(index_path=sys.argv[1], xml_path=sys.argv[2])