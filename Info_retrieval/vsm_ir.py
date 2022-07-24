import sys
from Information_retrieval import InformationRetrieval
from Inverted_index import InverseIndex


CREATE_IDX = 'create_index'
QUERY = 'query'


def build_index(corpus_dir, index_path='vsm_inverted_index.json'):
    builder = InverseIndex(corpus_dir)
    # FIXME
    builder.build_inverted_index(index_path)


def retrieve(ranking, index_path, question):
    retriever = InformationRetrieval()
    retriever.get_ranking(question, ranking, index_path)


def main():
    nof_args = len(sys.argv)
    if nof_args < 2:
        print(f"Error: expected '{CREATE_IDX}' or '{QUERY}' flags, but received none!")
        exit(-1)
    if sys.argv[1] == CREATE_IDX:
        if nof_args < 3:
            print("Error: missing argument - [corpus_directory]!")
            exit(-1)
        build_index(corpus_dir=sys.argv[2])
    elif sys.argv[1] == QUERY:
        if nof_args < 5:
            print("Error: missing arguments: [ranking] [index_path] '<question>'")
            exit(-1)
        retrieve(ranking=sys.argv[2], index_path=sys.argv[3], question=sys.argv[4])
    else:
        print(f"Error: unrecognized flag received - '{sys.argv[1]}'.")
        exit(-1)


if __name__ == '__main__':
    main()
