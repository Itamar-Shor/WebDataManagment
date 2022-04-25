####################################################################
# URLs
####################################################################
EXAMPLE_PREFIX = r'http://example.org'
ONTOLOGY_NAME = 'ontology.nt'
WIKI_BASE_PAGE = r'https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)'
WIKI_INIT = r'https://en.wikipedia.org'

####################################################################
# SPARQL filters
####################################################################
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
# run flags
####################################################################
CREATE_FLAG = 'create'
QUESTION_FLAG = 'question'
