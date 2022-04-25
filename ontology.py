import requests
import rdflib
import lxml.html
import defines as defs
import re


class Ontology:
    """
    build the ontology with web crawler and XPATH
    """

    def __init__(self, ontology_name):
        self.log = open('log.txt', 'w')
        self.ontology = rdflib.Graph()
        self.ontology_name = ontology_name
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
        # "//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href"
        for country_box in doc.xpath("(//table)[1]/tbody/tr/td[1]"):
            self.extract_country_info(
                country_box.xpath(".//a[contains(@href, '/wiki/') and not(contains(@href, ':'))]/@href")[0])

        # save the ontology
        self.log.close()
        self.ontology.serialize(self.ontology_name, format=self.ontology_name.split('.')[-1], encoding='utf-8')

    def extract_country_info(self, path):
        path = defs.WIKI_INIT + path
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
        form_of_gov = info_box.xpath(
            ".//tr[./th/descendant-or-self::*[contains(text(), 'Government')]]/td//a[not(../../sup)]//text()")

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
            # TODO: check this
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
            COUNTRY = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{country_name.strip()}")

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
                POPULATION = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{population}")
                self.ontology.add((POPULATION, self.POPULATION_OF, COUNTRY))
            else:
                self.log.write("\t (-) Error: couldn't extract population.\n")

            if area != '':
                AREA = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{area}")
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
        path = defs.WIKI_INIT + path
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
            PERSON = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{name}")
            # TODO: check this
            PLACE = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{place_of_birth[-1].replace(' ', '_')}")
            self.ontology.add((PERSON, self.BIRTH_PLACE, PLACE))
        else:
            self.log.write("\t (-) Error: couldn't extract president place of birth.\n")

        if len(date_of_birth) > 0:
            PERSON = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{name}")
            DATE = rdflib.URIRef(f"{defs.EXAMPLE_PREFIX}/{date_of_birth[0]}")
            self.ontology.add((PERSON, self.BIRTH_DATE, DATE))
        else:
            self.log.write("\t (-) Error: couldn't extract president date of birth.\n")
