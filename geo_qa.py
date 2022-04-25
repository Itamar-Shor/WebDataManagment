import sys
import defines as defs
from query import Query
from ontology import Ontology


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
        print(', '.join(sorted([' '.join([item.split('/')[-1].replace('_', ' ') for item in r]) for r in results])))
    else:
        print(f"Error: unrecognized flag received - '{sys.argv[1]}'.")
        exit(-1)


if __name__ == '__main__':
    main()
