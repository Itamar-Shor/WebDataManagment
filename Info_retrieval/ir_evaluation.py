import os
from lxml import etree


def load_query_db(xml_path):
    with open(xml_path, 'r') as fd:
        query_db = etree.fromstring(fd.read())


    query_items = query_db.xpath("//QUERY")
    for query_item in query_items:
        q_num = query_item.xpath("./QueryNumber/text()")
        q_text = query_item.xpath("./QueryText/text()")
        q_results = query_item.xpath(".//Item")