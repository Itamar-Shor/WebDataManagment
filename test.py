from query import Query
from urllib.parse import unquote

qa = {
    "Who is the president of China?": "Xi Jinping",
    "Who is the president of Portugal?": "Marcelo Rebelo de Sousa",
    "Who is the president of Guam?": "Joe Biden",
    "Who is the prime minister of Eswatini?": "Cleopas Dlamini",
    "Who is the prime minister of Tonga?": "Siaosi Sovaleni",
    "What is the population of Isle of Man?": "84,069",
    "What is the population of Tokelau?": "1,499",
    "What is the population of Djibouti?": "921,804",
    "What is the area of Mauritius?": "2,040 km squared",
    "What is the area of Luxembourg?": "2,586.4 km squared",
    "What is the area of Guadeloupe?": "1,628 km squared",
    "What is the form of government in Argentina?": "Federal republic, Presidential system, Republic",
    "What is the form of government in Sweden?": "Constitutional monarchy, Parliamentary system, Unitary state",
    "What is the form of government in Bahrain?": "Parliamentary, Semi-constitutional monarchy, Unitary state",
    "What is the form of government in North Macedonia?": "Parliamentary republic, Unitary state",
    "What is the capital of Burundi?": "Gitega",
    "What is the capital of Mongolia?": "Ulaanbaatar",
    "What is the capital of Andorra?": "Andorra la Vella",
    "What is the capital of Saint Helena, Ascension and Tristan da Cunha?": "Jamestown, Saint Helena",
    "What is the capital of Greenland?": "Nuuk",
    "List all countries whose capital name contains the string hi": "Bhutan, India, Moldova, Sint Maarten, United States",
    "List all countries whose capital name contains the string free": "Sierra Leone",
    "List all countries whose capital name contains the string alo": "Niue, Tonga",
    "List all countries whose capital name contains the string baba": "Eswatini, Ethiopia",
    "How many Absolute monarchy are also Unitary state?": "5",
    "How many Dictatorship are also Presidential system?": "5",
    "How many Dictatorship are also Authoritarian?": "3",
    "How many presidents were born in Iceland?": "1",
    "How many presidents were born in Republic of Ireland?": "0",
    "When was the president of Fiji born?": "1964-04-20",
    "When was the president of United States born?": "1942-11-20",
    "Where was the president of Indonesia born?": "Indonesia",
    "Where was the president of Uruguay born?": "Uruguay",
    "Where was the prime minister of Solomon Islands born?": "Papua New Guinea",
    "When was the prime minister of Lesotho born?": "1961-11-03",
    "Who is Denis Sassou Nguesso?": "President of Republic of the Congo",
    "Who is David Kabua?": "President of Marshall Islands",
}


def test(ontology):
    query_handler = Query(ontology)
    nof_err = 0
    for q in qa:
        results = query_handler.query(q)
        a = ''
        if results is not None:
            a = ', '.join(sorted([' '.join([unquote(item.split('/')[-1], encoding='utf-8').replace('_', ' ') for item in r]) for r in results]))
        if a != qa[q]:
            nof_err += 1
            print(f"({nof_err}) Error: question={q}.\n\texpected= {qa[q]}.\n\tactual= {a}.")
