import sys
import re
import requests
import rdflib
import lxml.html

EXAMPLE_PREFIX = ''
ONTOLOGY_NAME = 'ontology.nt'
WIKI_BASE_PAGE = r'https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)'
WIKI_INIT = r'https://en.wikipedia.org'
CREATE_FLAG = 'create'
QUESTION_FLAG = 'question'

COUNTRY_FILTER_TEMPLATE = '?{VAR} {RELATION} {{COUNTRY}} .'
COUNTRY_PERSONAL_FILTER_TEMPLATE = '?{VAR_PERSON} {COUNTRY_RELATION} {{COUNTRY}} .' \
                                   '?{VAR_PERSON} {REQ_RELATION} ?{REQ_VAR} .'

SPARQL_TEMPLATE = 'SELECT {SELECT} ' \
                  'WHERE {' \
                  '{FILTERS}' \
                  '}'

####################################################################
# SPARQL relations
####################################################################
SPARQL_RELATIONS = {
    'PRESIDENT_OF': f'{EXAMPLE_PREFIX}/president_of',
    'PRIME_MINISTER_OF': f'{EXAMPLE_PREFIX}/prime_minister_of',
    'POPULATION_OF': f'{EXAMPLE_PREFIX}/population_of',
    'AREA_OF': f'{EXAMPLE_PREFIX}/area_of',
    'FORM_OF_GOV_IN': f'{EXAMPLE_PREFIX}/form_of_government_in',
    'CAPITAL_OF': f'{EXAMPLE_PREFIX}/capital_of',
    'BIRTH_DATE': f'{EXAMPLE_PREFIX}/birth_date',
    'BIRTH_PLACE': f'{EXAMPLE_PREFIX}/birth_place'
}


####################################################################
# query class
####################################################################
class Query:
    """
    translate natural language query to SPARQL query
    """

    def __init__(self, ontology):
        self.ontology = rdflib.Graph().parse(ontology)
        self.query2SPARQL = {
            re.compile(r'Who is the president of (?P<COUNTRY>\w+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS['PRESIDENT_OF'])
                                       ),
            re.compile(r'Who is the prime minister of (?P<COUNTRY>\w+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS[
                                                                                  'PRIME_MINISTER_OF'])
                                       ),
            re.compile(r'What is the population of (?P<COUNTRY>\w+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS[
                                                                                  'POPULATION_OF'])
                                       ),
            re.compile(r'What is the area of (?P<COUNTRY>\w+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS['AREA_OF'])
                                       ),
            re.compile(r'What is the form of government in (?P<COUNTRY>\w+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS[
                                                                                  'FORM_OF_GOV_IN'])
                                       ),
            re.compile(r'What is the capital of (?P<COUNTRY>\w+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS['CAPITAL_OF'])
                                       ),
            re.compile(r'When was the president of (?P<COUNTRY>\w+) born\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_PERSONAL_FILTER_TEMPLATE.format(VAR_PERSON='m',
                                                                                       REQ_VAR='e',
                                                                                       COUNTRY_RELATION=
                                                                                       SPARQL_RELATIONS['PRESIDENT_OF'],
                                                                                       REQ_RELATION=SPARQL_RELATIONS[
                                                                                           'BIRTH_DATE'])
                                       ),
            re.compile(r'Where was the president of (?P<COUNTRY>\w+) born\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_PERSONAL_FILTER_TEMPLATE.format(VAR_PERSON='m',
                                                                                       REQ_VAR='e',
                                                                                       COUNTRY_RELATION=
                                                                                       SPARQL_RELATIONS['PRESIDENT_OF'],
                                                                                       REQ_RELATION=SPARQL_RELATIONS[
                                                                                           'BIRTH_PLACE'])
                                       ),
            re.compile(r'When was the prime minister of (?P<COUNTRY>\w+) born\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_PERSONAL_FILTER_TEMPLATE.format(VAR_PERSON='m',
                                                                                       REQ_VAR='e',
                                                                                       COUNTRY_RELATION=
                                                                                       SPARQL_RELATIONS[
                                                                                           'PRIME_MINISTER_OF'],
                                                                                       REQ_RELATION=SPARQL_RELATIONS[
                                                                                           'BIRTH_DATE'])
                                       ),
            re.compile(r'Where was the prime minister of (?P<COUNTRY>\w+) born\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_PERSONAL_FILTER_TEMPLATE.format(VAR_PERSON='m',
                                                                                       REQ_VAR='e',
                                                                                       COUNTRY_RELATION=
                                                                                       SPARQL_RELATIONS[
                                                                                           'PRIME_MINISTER_OF'],
                                                                                       REQ_RELATION=SPARQL_RELATIONS[
                                                                                           'BIRTH_PLACE'])
                                       ),
            re.compile(r'Who is (?P<ENTITY>\w+)\?'): '',
            re.compile(r'How many (?P<GOVERNMENT1>\w+) are also (?P<GOVERNMENT2>\w+)\?'): '',
            re.compile(r'List all countries whose capital name contains the string (?P<VAR>\w+)'): '',
            re.compile(r'How many presidents were born in (?P<COUNTRY>\w+)\?'): '',
        }

    def query_to_SPARQL(self, query):
        query = query.strip()
        for pattern in self.query2SPARQL:
            match = pattern.search(query)
            if match is None:
                continue
            args = match.groupdict()
            return self.query2SPARQL[pattern].format(**args)
        print(f"Error: unrecognized query received - '{query}.'")

    def query(self, query):
        sparql_q = self.query_to_SPARQL[query]
        return self.ontology.query(sparql_q)


####################################################################
# ontology class
####################################################################
class Ontology:
    """
    build the ontology with web crawler and XPATH
    """

    def __init__(self, ontology_name):
        self.ontology = rdflib.Graph()
        self.ontology_name = ontology_name
        # add relations
        self.PRESIDENT_OF = rdflib.URIRef(SPARQL_RELATIONS['PRESIDENT_OF'])
        self.PRIME_MINISTER_OF = rdflib.URIRef(SPARQL_RELATIONS['PRIME_MINISTER_OF'])
        self.POPULATION_OF = rdflib.URIRef(SPARQL_RELATIONS['POPULATION_OF'])
        self.AREA_OF = rdflib.URIRef(SPARQL_RELATIONS['AREA_OF'])
        self.FORM_OF_GOV_IN = rdflib.URIRef(SPARQL_RELATIONS['FORM_OF_GOV_IN'])
        self.CAPITAL_OF = rdflib.URIRef(SPARQL_RELATIONS['CAPITAL_OF'])
        self.BIRTH_DATE = rdflib.URIRef(SPARQL_RELATIONS['BIRTH_DATE'])
        self.BIRTH_PLACE = rdflib.URIRef(SPARQL_RELATIONS['BIRTH_PLACE'])

    def build_ontology(self):
        r = requests.get(WIKI_BASE_PAGE)
        doc = lxml.html.fromstring(r.content)
        for country_page in doc.xpath(
                "(//table)[1]/tbody/tr/td[1]//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href"):
            self.extract_country_info(country_page)

        # save the ontology
        self.ontology.serialize(self.ontology_name, format=self.ontology_name.split('.')[-1])

    def extract_country_info(self, path):
        path = WIKI_INIT + path
        print(f'path {path}')
        r = requests.get(path)
        doc = lxml.html.fromstring(r.content)
        country_name = doc.xpath("//h1[1]/text()")[0].replace(" ", "_")

        if country_name[0] == '/':
            country_name = country_name[1:]

        capital, form_of_gov, president_box, president_page, president_name, prime_minister_page, prime_minister_name = [
                                                                                                                            ''] * 7

        # vcard for new zealand
        info_box = doc.xpath("//table[contains(@class, 'infobox') or  contains(@class, 'vcard')][1]")[0]

        # extract fields
        capital_box = info_box.xpath("//tr[./th[contains(text(), 'Capital')]]//a/text()")
        if len(capital_box) > 0:
            capital = capital_box[0].replace(" ", "_")

        forms = []
        form_of_gov = info_box.xpath("//tr[./th//a[contains(text(), 'Government')]]/td/a//text()")

        for form in form_of_gov:
            forms.append(form.replace(" ", "_"))
        form_of_gov = '_'.join(forms)

        president_box = info_box.xpath("//tr[./th//a[contains(text(), 'President')]]/td")
        if len(president_box) > 0:
            president_page = info_box.xpath("//tr[./th//a[contains(text(), 'President')]]/td//a//@href")
            president_name = info_box.xpath("//tr[./th//a[contains(text(), 'President')]]/td//a//text()")[0].replace(
                " ", "_")

        prime_minister_box = info_box.xpath("//tr[./th//a[contains(text(), 'Prime Minister')]]/td")

        if len(prime_minister_box) > 0:
            prime_minister_page = info_box.xpath("//tr[./th//a[contains(text(), 'Prime Minister')]]/td//a//@href")
            prime_minister_name = info_box.xpath("//tr[./th//a[contains(text(), 'Prime Minister')]]/td//text()[1]")[
                0].replace(" ", "_")

        # declare entities and add connections to the graph
        if country_name != '':
            COUNTRY = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{country_name}")

            if capital != '':
                CAPITAL = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{capital}")
                self.ontology.add((CAPITAL, self.CAPITAL_OF, COUNTRY))
            if form_of_gov != '':
                FORM_OF_GOV = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{form_of_gov}")
                self.ontology.add((FORM_OF_GOV, self.FORM_OF_GOV_IN, COUNTRY))
            if president_name != '':
                PRESIDENT = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{president_name}")
                self.ontology.add((PRESIDENT, self.PRESIDENT_OF, COUNTRY))
            if prime_minister_name != '':
                PRIME_MINISTER = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{prime_minister_name}")
                self.ontology.add((PRIME_MINISTER, self.PRIME_MINISTER_OF, COUNTRY))

    def extract_president_info(self, path):
        r = requests.get(path)
        doc = lxml.html.fromstring(r.content)
        info_box = doc.xpath("//table[contains(@class, 'infobox')]")[0]


####################################################################
# Main
####################################################################
def main():
    if len(sys.argv) < 2:
        print("Error: expected create or question flags but received none!")
        exit(-1)
    if sys.argv[1] == CREATE_FLAG:
        ontology_builder = Ontology(ONTOLOGY_NAME)
        ontology_builder.build_ontology()
    elif sys.argv[1] == QUESTION_FLAG:
        if len(sys.argv) < 3:
            print('Error: missing query string for question flag.')
            exit(-1)
        q = sys.argv[2]
        query_handler = Query(ONTOLOGY_NAME)
        print(query_handler.query(q))
    else:
        print(f'Error: unrecognized flag received - {sys.argv[1]}.')
        exit(-1)


if __name__ == '__main__':
    main()
