import re
import rdflib
import defines as defs


class Query:
    """
    translate natural language query to SPARQL query
    """

    def __init__(self, ontology):
        self.ontology = rdflib.Graph().parse(ontology)
        self.query2SPARQL_d = {
            re.compile(r'Who is the president of (?P<COUNTRY>.+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_FILTER_TEMPLATE.format(
                                                VAR='e',
                                                RELATION=defs.SPARQL_RELATIONS['PRESIDENT_OF']
                                            )),
            re.compile(r'Who is the prime minister of (?P<COUNTRY>.+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_FILTER_TEMPLATE.format(
                                                VAR='e',
                                                RELATION=defs.SPARQL_RELATIONS['PRIME_MINISTER_OF']
                                            )),
            re.compile(r'What is the population of (?P<COUNTRY>.+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_FILTER_TEMPLATE.format(
                                                VAR='e',
                                                RELATION=defs.SPARQL_RELATIONS['POPULATION_OF']
                                            )),
            re.compile(r'What is the area of (?P<COUNTRY>.+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_FILTER_TEMPLATE.format(
                                                VAR='e',
                                                RELATION=defs.SPARQL_RELATIONS['AREA_OF']
                                            )),
            re.compile(r'What is the form of government in (?P<COUNTRY>.+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_FILTER_TEMPLATE.format(
                                                VAR='e',
                                                RELATION=defs.SPARQL_RELATIONS['FORM_OF_GOV_IN']
                                            )),
            re.compile(r'What is the capital of (?P<COUNTRY>.+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_FILTER_TEMPLATE.format(
                                                VAR='e',
                                                RELATION=defs.SPARQL_RELATIONS['CAPITAL_OF']
                                            )),
            re.compile(r'When was the president of (?P<COUNTRY>.+) born\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_PERSONAL_FILTER_TEMPLATE.format(
                                                VAR_PERSON='m',
                                                REQ_VAR='e',
                                                COUNTRY_RELATION=defs.SPARQL_RELATIONS['PRESIDENT_OF'],
                                                REQ_RELATION=defs.SPARQL_RELATIONS['BIRTH_DATE']
                                            )),
            re.compile(r'Where was the president of (?P<COUNTRY>.+) born\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_PERSONAL_FILTER_TEMPLATE.format(
                                                VAR_PERSON='m',
                                                REQ_VAR='e',
                                                COUNTRY_RELATION=defs.SPARQL_RELATIONS['PRESIDENT_OF'],
                                                REQ_RELATION=defs.SPARQL_RELATIONS['BIRTH_PLACE']
                                            )),
            re.compile(r'When was the prime minister of (?P<COUNTRY>.+) born\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_PERSONAL_FILTER_TEMPLATE.format(
                                                VAR_PERSON='m',
                                                REQ_VAR='e',
                                                COUNTRY_RELATION=defs.SPARQL_RELATIONS['PRIME_MINISTER_OF'],
                                                REQ_RELATION=defs.SPARQL_RELATIONS['BIRTH_DATE']
                                            )),
            re.compile(r'Where was the prime minister of (?P<COUNTRY>.+) born\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?e',
                                            FILTERS=defs.COUNTRY_PERSONAL_FILTER_TEMPLATE.format(
                                                VAR_PERSON='m',
                                                REQ_VAR='e',
                                                COUNTRY_RELATION=
                                                defs.SPARQL_RELATIONS['PRIME_MINISTER_OF'],
                                                REQ_RELATION=defs.SPARQL_RELATIONS['BIRTH_PLACE']
                                            )),
            re.compile(r'Who is (?P<ENTITY>.+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='?r ?c',
                                            FILTERS=defs.ENTITY_TEMPLATE.format(
                                                COUNTRY_RELATION='r',
                                                COUNTRY='c'
                                            )),
            re.compile(r'How many (?P<FORM1>.+) are also (?P<FORM2>.+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='(count(distinct ?c) as ?count )',
                                            FILTERS=defs.GOVERNMENT_FILTER_TEMPLATE.format(
                                                COUNTRY_RELATION=defs.SPARQL_RELATIONS['FORM_OF_GOV_IN'],
                                                COUNTRY='c'
                                            )),
            re.compile(r'List all countries whose capital name contains the string (?P<STR>.+)'):
                defs.SPARQL_TEMPLATE.format(SELECT='?c',
                                            FILTERS=defs.LIST_FILTER_TEMPLATE.format(
                                                COUNTRY_RELATION=defs.SPARQL_RELATIONS['CAPITAL_OF'],
                                                COUNTRY='c',
                                                CAPITAL='d'
                                            )),
            re.compile(r'How many presidents were born in (?P<COUNTRY>.+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='(count(distinct ?p) as ?count )',
                                            FILTERS=defs.PRESIDENT_FILTER_TEMPLATE.format(
                                                PRESIDENT='p',
                                                PRESIDENT_RELATION=defs.SPARQL_RELATIONS['PRESIDENT_OF'],
                                                BORN_RELATION=defs.SPARQL_RELATIONS['BIRTH_PLACE'],
                                                COUNTRY='c'
                                            )),
            re.compile(r'How many countries have population greater than (?P<STR>\d+)\?'):
                defs.SPARQL_TEMPLATE.format(SELECT='(count(distinct ?c) as ?count )',
                                            FILTERS=defs.POPULATION_FILTER_TEMPLATE.format(
                                                COUNTRY='c',
                                                COUNTRY_RELATION=defs.SPARQL_RELATIONS['POPULATION_OF'],
                                                POPULATION='p'
                                            )),

        }

    def query_to_SPARQL(self, query):
        query = query.strip()
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
                    args[key] = f"<{defs.EXAMPLE_PREFIX}/{val}>"

            return self.query2SPARQL_d[pattern].format(**args)

        print(f"Error: unrecognized query received - '{query}'.")
        return None

    def query(self, query):
        sparql_q = self.query_to_SPARQL(query)
        if sparql_q is None:
            return None
        return self.ontology.query(sparql_q)
