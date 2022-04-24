import sys
import re
import requests
import rdflib
import lxml.html

EXAMPLE_PREFIX = r'http://example.org'
ONTOLOGY_NAME = 'ontology.nt'
WIKI_BASE_PAGE = r'https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)'
WIKI_INIT = r'https://en.wikipedia.org'
CREATE_FLAG = 'create'
QUESTION_FLAG = 'question'

COUNTRY_FILTER_TEMPLATE = '?{VAR} {RELATION} {{COUNTRY}} .'
COUNTRY_PERSONAL_FILTER_TEMPLATE = '?{VAR_PERSON} {COUNTRY_RELATION} {{COUNTRY}} .' \
                                   '?{VAR_PERSON} {REQ_RELATION} ?{REQ_VAR} .'
ENTITY_TEMPLATE = '{{ENTITY}} ?{COUNTRY_RELATION} ?{COUNTRY} .' \
                  ' FILTER regex(str(?{COUNTRY_RELATION}), "president|prime_minister", "i").'
GOVERNMENT_FILTER_TEMPLATE = '{{FORM1}} {COUNTRY_RELATION} ?{COUNTRY} .' \
                             '{{FORM2}} {COUNTRY_RELATION} ?{COUNTRY} .'
LIST_FILTER_TEMPLATE = '?{CAPITAL} {COUNTRY_RELATION} ?{COUNTRY} .' \
                       ' FILTER regex(str(?{CAPITAL}), "{{STR}}", "i") .'
PRESIDENT_FILTER_TEMPLATE = '?{PRESIDENT} {PRESIDENT_RELATION} ?{COUNTRY} .' \
                            '?{PRESIDENT} {BORN_RELATION} {{COUNTRY}} .'

POPULATION_FILTER_TEMPLATE = r'?{POPULATION} {COUNTRY_RELATION} ?{COUNTRY} .' \
                             r' BIND(REPLACE(STR(?{POPULATION}), "(http://example.org/)|(,)", "", "i") AS ?x) .' \
                             r' BIND(REPLACE(STR(?x), ",", "", "i") AS ?num) .' \
                             r' FILTER (xsd:integer(?num) >= {{STR}}).'


SPARQL_TEMPLATE = 'select {SELECT} ' \
                  'where {{{{' \
                  '{FILTERS}' \
                  '}}}}'

#   TODO:
#       4. check if all queries are case insensitive?
#       5. check if approximately birth date needed to be parsed as well
#       6. check if estimate population needed to be parsed
#       7. (and problam with other_unit(**** km) ---> American_Samoa)

####################################################################
# SPARQL relations
####################################################################
SPARQL_RELATIONS = {
    'PRESIDENT_OF': f'<{EXAMPLE_PREFIX}/President_of>',
    'PRIME_MINISTER_OF': f'<{EXAMPLE_PREFIX}/Prime_minister_of>',
    'POPULATION_OF': f'<{EXAMPLE_PREFIX}/population_of>',
    'AREA_OF': f'<{EXAMPLE_PREFIX}/area_of>',
    'FORM_OF_GOV_IN': f'<{EXAMPLE_PREFIX}/form_of_government_in>',
    'CAPITAL_OF': f'<{EXAMPLE_PREFIX}/capital_of>',
    'BIRTH_DATE': f'<{EXAMPLE_PREFIX}/birth_date>',
    'BIRTH_PLACE': f'<{EXAMPLE_PREFIX}/birth_place>'
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
        self.query2SPARQL_d = {
            re.compile(r'Who is the president of (?P<COUNTRY>.+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS['PRESIDENT_OF'])
                                       ),
            re.compile(r'Who is the prime minister of (?P<COUNTRY>.+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS[
                                                                                  'PRIME_MINISTER_OF'])
                                       ),
            re.compile(r'What is the population of (?P<COUNTRY>.+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS[
                                                                                  'POPULATION_OF'])
                                       ),
            re.compile(r'What is the area of (?P<COUNTRY>.+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS['AREA_OF'])
                                       ),
            re.compile(r'What is the form of government in (?P<COUNTRY>.+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS[
                                                                                  'FORM_OF_GOV_IN'])
                                       ),
            re.compile(r'What is the capital of (?P<COUNTRY>.+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_FILTER_TEMPLATE.format(VAR='e',
                                                                              RELATION=SPARQL_RELATIONS['CAPITAL_OF'])
                                       ),
            re.compile(r'When was the president of (?P<COUNTRY>.+) born\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_PERSONAL_FILTER_TEMPLATE.format(
                                           VAR_PERSON='m',
                                           REQ_VAR='e',
                                           COUNTRY_RELATION=SPARQL_RELATIONS['PRESIDENT_OF'],
                                           REQ_RELATION=SPARQL_RELATIONS['BIRTH_DATE'])
                                       ),
            re.compile(r'Where was the president of (?P<COUNTRY>.+) born\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_PERSONAL_FILTER_TEMPLATE.format(
                                           VAR_PERSON='m',
                                           REQ_VAR='e',
                                           COUNTRY_RELATION=SPARQL_RELATIONS['PRESIDENT_OF'],
                                           REQ_RELATION=SPARQL_RELATIONS['BIRTH_PLACE'])
                                       ),
            re.compile(r'When was the prime minister of (?P<COUNTRY>.+) born\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_PERSONAL_FILTER_TEMPLATE.format(
                                           VAR_PERSON='m',
                                           REQ_VAR='e',
                                           COUNTRY_RELATION=SPARQL_RELATIONS['PRIME_MINISTER_OF'],
                                           REQ_RELATION=SPARQL_RELATIONS['BIRTH_DATE'])
                                       ),
            re.compile(r'Where was the prime minister of (?P<COUNTRY>.+) born\?'):
                SPARQL_TEMPLATE.format(SELECT='?e',
                                       FILTERS=COUNTRY_PERSONAL_FILTER_TEMPLATE.format(
                                           VAR_PERSON='m',
                                           REQ_VAR='e',
                                           COUNTRY_RELATION=
                                           SPARQL_RELATIONS['PRIME_MINISTER_OF'],
                                           REQ_RELATION=SPARQL_RELATIONS['BIRTH_PLACE'])
                                       ),
            re.compile(r'Who is (?P<ENTITY>.+)\?'):
                SPARQL_TEMPLATE.format(SELECT='?r ?c',
                                       FILTERS=ENTITY_TEMPLATE.format(
                                           COUNTRY_RELATION='r',
                                           COUNTRY='c')
                                       ),

            re.compile(r'How many (?P<FORM1>.+) are also (?P<FORM2>.+)\?'):
                SPARQL_TEMPLATE.format(SELECT='(count(distinct ?c) as ?count )',
                                       FILTERS=GOVERNMENT_FILTER_TEMPLATE.format(
                                           COUNTRY_RELATION=SPARQL_RELATIONS['FORM_OF_GOV_IN'],
                                           COUNTRY='c')
                                       ),
            re.compile(r'List all countries whose capital name contains the string (?P<STR>.+)'):
                SPARQL_TEMPLATE.format(SELECT='?c',
                                       FILTERS=LIST_FILTER_TEMPLATE.format(
                                           COUNTRY_RELATION=SPARQL_RELATIONS['CAPITAL_OF'],
                                           COUNTRY='c',
                                           CAPITAL='d')
                                       ),
            re.compile(r'How many presidents were born in (?P<COUNTRY>.+)\?'):
                SPARQL_TEMPLATE.format(SELECT='(count(distinct ?p) as ?count )',
                                       FILTERS=PRESIDENT_FILTER_TEMPLATE.format(
                                           PRESIDENT='p',
                                           PRESIDENT_RELATION=SPARQL_RELATIONS['PRESIDENT_OF'],
                                           BORN_RELATION=SPARQL_RELATIONS['BIRTH_PLACE'],
                                           COUNTRY='c')
                                       ),
            re.compile(r'How many countries have population greater than (?P<STR>\d+)\?'):
                SPARQL_TEMPLATE.format(SELECT='(count(distinct ?c) as ?count )',
                                       FILTERS=POPULATION_FILTER_TEMPLATE.format(
                                           COUNTRY='c',
                                           COUNTRY_RELATION=SPARQL_RELATIONS['POPULATION_OF'],
                                           POPULATION='p')
                                       ),

        }

    def query_to_SPARQL(self, query):
        query = query.strip()
        print(query)
        args = {}

        for pattern in self.query2SPARQL_d:
            match = pattern.search(query)
            if match is None:
                continue
            for key, val in match.groupdict().items():
                val = val.strip().replace(' ', '_')
                if key == "STR":
                    args[key] = val
                else:
                    args[key] = f"<{EXAMPLE_PREFIX}/{val}>"

            return self.query2SPARQL_d[pattern].format(**args)

        print(f"Error: unrecognized query received - '{query}.'")
        return None

    def query(self, query):
        sparql_q = self.query_to_SPARQL(query)
        if sparql_q is None:
            return None
        print(f"SPARQL query is: {sparql_q}")
        return self.ontology.query(sparql_q)


####################################################################
# ontology class
####################################################################
class Ontology:
    """
    build the ontology with web crawler and XPATH
    """

    def __init__(self, ontology_name):
        self.log = open('log.txt', 'w')
        self.ontology = rdflib.Graph()
        self.ontology_name = ontology_name
        # add relations
        self.PRESIDENT_OF = rdflib.URIRef(SPARQL_RELATIONS['PRESIDENT_OF'][1:-1])
        self.PRIME_MINISTER_OF = rdflib.URIRef(SPARQL_RELATIONS['PRIME_MINISTER_OF'][1:-1])
        self.POPULATION_OF = rdflib.URIRef(SPARQL_RELATIONS['POPULATION_OF'][1:-1])
        self.AREA_OF = rdflib.URIRef(SPARQL_RELATIONS['AREA_OF'][1:-1])
        self.FORM_OF_GOV_IN = rdflib.URIRef(SPARQL_RELATIONS['FORM_OF_GOV_IN'][1:-1])
        self.CAPITAL_OF = rdflib.URIRef(SPARQL_RELATIONS['CAPITAL_OF'][1:-1])
        self.BIRTH_DATE = rdflib.URIRef(SPARQL_RELATIONS['BIRTH_DATE'][1:-1])
        self.BIRTH_PLACE = rdflib.URIRef(SPARQL_RELATIONS['BIRTH_PLACE'][1:-1])

    def build_ontology(self):
        r = requests.get(WIKI_BASE_PAGE)
        doc = lxml.html.fromstring(r.content)
        # "//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href"
        for country_box in doc.xpath("(//table)[1]/tbody/tr/td[1]"):
            self.extract_country_info(country_box.xpath(".//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href")[0])

        # save the ontology
        self.log.close()
        self.ontology.serialize(self.ontology_name, format=self.ontology_name.split('.')[-1], encoding='utf-8')

    def extract_country_info(self, path):
        path = WIKI_INIT + path
        print(f'path {path}')
        r = requests.get(path)
        doc = lxml.html.fromstring(r.content)
        country_name = doc.xpath("//h1[1]/text()")[0].replace(" ", "_")
        country_name = re.sub(r'\(.*\)', '', country_name).strip()

        self.log.write(f"{path} ({country_name}):\n")

        if country_name[0] == '/':
            country_name = country_name[1:]

        capital, form_of_gov, president_box, president_page, president_name, prime_minister_page, \
        prime_minister_name, population, area = [''] * 9

        info_box = doc.xpath("//table[contains(@class, 'infobox') or contains(@class, 'vcard')][1]")[0]

        # extract fields
        # TODO: maybe add descendant-or-self::*
        capital_box = info_box.xpath(".//tr[./th[text() = 'Capital']]//a/text()")
        if len(capital_box) > 0:
            capital = re.sub(r'\(.*\)', '', capital_box[0]).strip().replace(" ", "_")

        forms = []
        form_of_gov = info_box.xpath(".//tr[./th/descendant-or-self::*[contains(text(), 'Government')]]/td//a[not(../../sup)]//text()")

        for form in form_of_gov:
            forms.append(form.strip().replace(" ", "_"))

        president_box = info_box.xpath(".//tr[./th/descendant-or-self::*[text() = 'President']]/td")
        if len(president_box) > 0:
            president_page = president_box[0].xpath(
                ".//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href")
            president_name = president_box[0].xpath(".//text()[1]")[0].strip().replace(" ", "_")

        prime_minister_box = info_box.xpath(".//tr[./th//a[text() = 'Prime Minister']]/td")
        if len(prime_minister_box) > 0:
            prime_minister_page = prime_minister_box[0].xpath(
                ".//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href")
            prime_minister_name = prime_minister_box[0].xpath(".//text()[1]")[0].strip().replace(" ", "_")

        # dealing with case that the number is on the same row (Channel_Islands)
        population_box = info_box.xpath(
            ".//tr[./th/descendant-or-self::*[contains(text(), 'Population')]]/td//text()")
        if len(population_box) == 0:
            population_box = info_box.xpath(
                ".//tr[./th/descendant-or-self::*[contains(text(), 'Population')]]/following-sibling::tr[1]/td//text()")
        if len(population_box) > 0:
            # to get rid of '('
            i = 0
            while i < len(population_box):
                if population_box[i] != '\n':
                    break
                i += 1
            # ignore Estimate
            if i < len(population_box) and '-' not in population_box[i]:
                population = population_box[i].split()[0].strip().replace('.', ',')
                print(population)

        area_box = info_box.xpath(
            ".//tr[./th/descendant-or-self::*[contains(text(), 'Area')]]/following-sibling::tr[1]/td/text()")
        if len(area_box) > 0:
            # deal with &nbsp
            area = re.sub(r'\s+', '_', area_box[0].strip() + ' squared')

        # declare entities and add connections to the graph
        if country_name != '':
            COUNTRY = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{country_name.strip()}")

            if capital != '':
                CAPITAL = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{capital}")
                self.ontology.add((CAPITAL, self.CAPITAL_OF, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract capital.\n")

            if len(form_of_gov) > 0:
                for form in forms:
                    FORM_OF_GOV = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{form}")
                    self.ontology.add((FORM_OF_GOV, self.FORM_OF_GOV_IN, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract form of government.\n")

            if president_name != '':
                PRESIDENT = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{president_name}")
                self.ontology.add((PRESIDENT, self.PRESIDENT_OF, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract president name.\n")

            if prime_minister_name != '':
                PRIME_MINISTER = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{prime_minister_name}")
                self.ontology.add((PRIME_MINISTER, self.PRIME_MINISTER_OF, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract prime minister name.\n")

            if population != '':
                POPULATION = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{population}")
                self.ontology.add((POPULATION, self.POPULATION_OF, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract population.\n")

            if area != '':
                AREA = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{area}")
                self.ontology.add((AREA, self.AREA_OF, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract area.\n")

        else:
            self.log.write("\t (-) Error: couldn't extract country name.\n")

        if len(president_page) > 0:
            self.extract_person_info(president_page[0], president_name)
        else:
            self.log.write("\t (-) Error: couldn't extract president page.\n")

        if len(prime_minister_page) > 0:
            self.extract_person_info(prime_minister_page[0], prime_minister_name)
        else:
            self.log.write("\t (-) Error: couldn't extract prime minister page.\n")

    def extract_person_info(self, path, name):
        path = WIKI_INIT + path
        r = requests.get(path)
        doc = lxml.html.fromstring(r.content)
        info_box = doc.xpath("//table[contains(@class, 'infobox')]")
        if len(info_box) == 0:
            self.log.write("\t (-) Error: couldn't find infobox in president page.\n")
            return

        date_of_birth, place_of_birth = [''] * 2
        birth_box = info_box[0].xpath(".//tr[./th[contains(text(), 'Born')]]/td")
        if len(birth_box) > 0:
            date_of_birth = birth_box[0].xpath(".//span[contains(@class, 'bday')]/text()")
            place_of_birth = birth_box[0].xpath("./a/text()")

        if len(place_of_birth) > 0:
            PERSON = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{name}")
            # TODO: check this
            PLACE = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{place_of_birth[-1].replace(' ', '_')}")
            self.ontology.add((PERSON, self.BIRTH_PLACE, PLACE))
        else:
            self.log.write("\t (-) Error: couldn't extract president place of birth.\n")

        if len(date_of_birth) > 0:
            PERSON = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{name}")
            DATE = rdflib.URIRef(f"{EXAMPLE_PREFIX}/{date_of_birth[0]}")
            self.ontology.add((PERSON, self.BIRTH_DATE, DATE))
        else:
            self.log.write("\t (-) Error: couldn't extract president date of birth.\n")


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
        results = query_handler.query(q)

        print(', '.join(sorted([' '.join([item.split('/')[-1].replace('_', ' ') for item in r]) for r in results])))
    else:
        print(f'Error: unrecognized flag received - {sys.argv[1]}.')
        exit(-1)


if __name__ == '__main__':
    main()
