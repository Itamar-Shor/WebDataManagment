import requests
import rdflib
import lxml.html
import defines as defs
import re
import os


class Ontology:
    """
    build the ontology with web crawler and XPATH
    """

    def __init__(self, ontology_name):
        self.log = open('log.txt', 'w')
        self.ontology = rdflib.Graph()
        self.ontology_name = ontology_name
        self.countries = []
        # add relations
        self.PRESIDENT_OF = rdflib.URIRef(defs.SPARQL_RELATIONS['PRESIDENT_OF'][1:-1])
        self.PRIME_MINISTER_OF = rdflib.URIRef(defs.SPARQL_RELATIONS['PRIME_MINISTER_OF'][1:-1])
        self.POPULATION_OF = rdflib.URIRef(defs.SPARQL_RELATIONS['POPULATION_OF'][1:-1])
        self.AREA_OF = rdflib.URIRef(defs.SPARQL_RELATIONS['AREA_OF'][1:-1])
        self.FORM_OF_GOV_IN = rdflib.URIRef(defs.SPARQL_RELATIONS['FORM_OF_GOV_IN'][1:-1])
        self.CAPITAL_OF = rdflib.URIRef(defs.SPARQL_RELATIONS['CAPITAL_OF'][1:-1])
        self.BIRTH_DATE = rdflib.URIRef(defs.SPARQL_RELATIONS['BIRTH_DATE'][1:-1])
        self.BIRTH_PLACE = rdflib.URIRef(defs.SPARQL_RELATIONS['BIRTH_PLACE'][1:-1])

    def build_ontology(self):
        r = requests.get(defs.WIKI_BASE_PAGE)
        doc = lxml.html.fromstring(r.content)
        # create countries list
        for country_box in doc.xpath("(//table)[1]/tbody/tr/td[1]"):
            self.countries.append(
                country_box.xpath(".//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href")[0])

        for country_path in self.countries:
            self.extract_country_info(country_path)

        # save the ontology
        self.log.close()
        self.ontology.serialize(self.ontology_name, format=self.ontology_name.split('.')[-1], encoding='utf-8')

    def extract_country_info(self, path):
        path = defs.WIKI_INIT + path
        print(f'path {path}')
        r = requests.get(path)
        doc = lxml.html.fromstring(r.content)
        # TODO: extract name from URL!
        country_name = os.path.split(path)[1].replace(" ", "_")

        self.log.write(f"{path} ({country_name}):\n")

        capital, form_of_gov, president_box, president_page, president_name, prime_minister_page, \
        prime_minister_name, population, area = [''] * 9

        info_box = doc.xpath("//table[contains(@class, 'infobox') or contains(@class, 'vcard')][1]")[0]

        # extract fields
        # TODO: maybe add descendant-or-self::*
        capital_box = info_box.xpath(".//tr[./th[text() = 'Capital']]//a/@href")
        if len(capital_box) > 0:
            capital = os.path.split(capital_box[0])[1]

        forms = []
        form_of_gov = info_box.xpath(
            ".//tr[./th/descendant-or-self::*[contains(text(), 'Government')]]/td//a[not(../../sup)]//@href")

        for form in form_of_gov:
            forms.append(os.path.split(form)[1])

        president_box = info_box.xpath(".//tr[./th/descendant-or-self::*[text() = 'President']]/td")
        if len(president_box) > 0:
            president_page = president_box[0].xpath(
                ".//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href")
            president_name = os.path.split(president_page[0])[1]

        prime_minister_box = info_box.xpath(".//tr[./th//a[text() = 'Prime Minister']]/td")
        if len(prime_minister_box) > 0:
            prime_minister_page = prime_minister_box[0].xpath(
                ".//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href")
            prime_minister_name = os.path.split(prime_minister_page[0])[1]

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
            # TODO: handle with Eritrea
            if i < len(population_box) and '-' not in population_box[i]:
                population = population_box[i].split()[0].strip().replace('.', ',')

        area_box = info_box.xpath(
            ".//tr[./th/descendant-or-self::*[contains(text(), 'Area')]]/following-sibling::tr[1]/td/text()")
        if len(area_box) > 0:
            # deal with &nbsp
            area = re.sub(r'[^0-9,\.\-]', '', area_box[0].split('(')[-1].strip()) + '_km_squared'

        # declare entities and add connections to the graph
        if country_name != '':
            COUNTRY = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{country_name}")

            if capital != '':
                CAPITAL = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{capital}")
                self.ontology.add((CAPITAL, self.CAPITAL_OF, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract capital.\n")

            if len(form_of_gov) > 0:
                for form in forms:
                    FORM_OF_GOV = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{form}")
                    self.ontology.add((FORM_OF_GOV, self.FORM_OF_GOV_IN, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract form of government.\n")

            if president_name != '':
                PRESIDENT = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{president_name}")
                self.ontology.add((PRESIDENT, self.PRESIDENT_OF, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract president name.\n")

            if prime_minister_name != '':
                PRIME_MINISTER = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{prime_minister_name}")
                self.ontology.add((PRIME_MINISTER, self.PRIME_MINISTER_OF, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract prime minister name.\n")

            if population != '':
                print(population)
                POPULATION = rdflib.Literal(population)
                self.ontology.add((COUNTRY, self.POPULATION_OF, POPULATION))
            else:
                self.log.write("\t (-) Error: couldn't extract population.\n")

            if area != '':
                AREA = rdflib.Literal(area)
                self.ontology.add((COUNTRY, self.AREA_OF, AREA))
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
        path = defs.WIKI_INIT + path
        r = requests.get(path)
        doc = lxml.html.fromstring(r.content)
        info_box = doc.xpath("//table[contains(@class, 'infobox')]")
        if len(info_box) == 0:
            self.log.write("\t (-) Error: couldn't find infobox in president page.\n")
            return

        date_of_birth, place_of_birth, place_of_birth_href, place_of_birth_text = [''] * 4
        birth_box = info_box[0].xpath(".//tr[./th[contains(text(), 'Born')]]/td")
        if len(birth_box) > 0:
            date_of_birth = birth_box[0].xpath(".//span[contains(@class, 'bday')]/text()")
            place_of_birth_href = birth_box[0].xpath("./a/@href")
            place_of_birth_text = birth_box[0].xpath("./text()")

        # option 1: extract from href
        if len(place_of_birth_href) > 0:
            # check of country is in the list of countries we work with
            if place_of_birth_href[-1] in self.countries:
                PERSON = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{name}")
                place_of_birth = os.path.split(place_of_birth_href[-1])[1]
                PLACE = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{place_of_birth}")
                self.ontology.add((PERSON, self.BIRTH_PLACE, PLACE))

        # option 2: extract from text
        if len(place_of_birth) == 0 and len(place_of_birth_text) > 0:
            place_of_birth = place_of_birth_text[-1].replace(',', '').strip().replace(" ", "_")
            if '/wiki/' + place_of_birth in self.countries:
                PERSON = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{name}")
                PLACE = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{place_of_birth}")
                self.ontology.add((PERSON, self.BIRTH_PLACE, PLACE))
        else:
            self.log.write("\t (-) Error: couldn't extract president place of birth.\n")

        if len(date_of_birth) > 0:
            PERSON = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{name}")
            DATE = rdflib.Literal(date_of_birth[0])
            self.ontology.add((PERSON, self.BIRTH_DATE, DATE))
        else:
            self.log.write("\t (-) Error: couldn't extract president date of birth.\n")
