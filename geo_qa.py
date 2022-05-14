import sys
import defines as defs
from query import Query
from ontology import Ontology
from test import test
from urllib.parse import unquote


#   TODO:
#       6. check if estimate population needed to be parsed
#       12. check of os.path.sep is needed
#       13. what to do if the a/text() is good but the a/@href is something else??
#       14. the entity name shoud be identical to the URL ---> remove unquote??
#       15. capital of switzerlamd (see forum)
#       16. deal with weird url of form_of_gov - # (south-africa)
#       17. birth place fixes (like Volodymyr_Zelenskyy and Ukraine)
#       18. Dominican republic -- somethimes get index error in population = population_box[i].split()[0].strip().replace('.', ',')


def main():
    if len(sys.argv) < 2:
        print("Error: expected 'create' or 'question' flags, but received none!")
        exit(-1)
    if sys.argv[1] == defs.CREATE_FLAG:
        ontology_builder = Ontology(defs.ONTOLOGY_NAME)
        ontology_builder.build_ontology()
    elif sys.argv[1] == defs.QUESTION_FLAG:
        if len(sys.argv) < 3:
            print('Error: missing query string for question flag!')
            exit(-1)
        q = sys.argv[2]
        query_handler = Query(defs.ONTOLOGY_NAME)
        results = query_handler.query(q)
        if results is None:
            exit(-1)
        print(', '.join(sorted([' '.join([unquote(item.split('/')[-1], encoding='utf-8').replace('_', ' ') for item in r]) for r in results])))
    elif sys.argv[1] == 'test':
        test(defs.ONTOLOGY_NAME)
    else:
        print(f"Error: unrecognized flag received - '{sys.argv[1]}'.")
        exit(-1)


if __name__ == '__main__':
    main()
