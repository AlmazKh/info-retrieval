import codecs
import string
import pymorphy2
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords

# nltk.download('stopwords')
# def map_html_to_xml():
#    for elt in parse_urls_xml("index.xml"):
#        doc = "habr-{}.html".format(elt.split("/")[-2])
#        with open(os.path.join('pages_html', doc), 'r') as html:
#            a = Selector(response=html).xpath("//p/text()").getall()
#            print(a)
#
MARKS = [',', '.', ':', '?', '«', '»', '-', '(', ')', '!', '\'', "—", ';', "”", "...", "\'\'", "/**//**/",
         "“", "„", "–"]


def parse_words_from_html(html_file):
    pages_html = codecs.open(f"pages_html/{html_file}", 'r', 'utf-8')
    html = pages_html.read()
    # print(html)
    soup = BeautifulSoup(html, features='html.parser')
    # kill all script, style, meta, links, span, a, time, button, li, dt, h2, h3, legend elements
    for script in soup(
            ["script", "style", "meta", "link", "span", "a", "time", "button", "li", "dt", "h2", "h3", "legend"]):
        script.extract()  # rip it out

    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    # split to words. Тут пока со знаками препинания.
    return text.split()


def get_normal_form(text):
    tokens = word_tokenize(text)
    analyzer = pymorphy2.MorphAnalyzer()
    normalized_words = []
    for token in tokens:
        if token in string.punctuation:
            continue
        if token in MARKS:
            continue
        normalized_words.append(analyzer.parse(token)[0].normal_form)
    return normalized_words


def remove_secondary_marks(words):
    filtered_words = list(filter(lambda word: (word not in string.punctuation) and (word not in MARKS), words))
    result = []
    for word in filtered_words:
        result.append("".join(filter(lambda char: char not in MARKS, word)))
    return result


def remove_stopwords(word_tokens):
    stop_words = set(stopwords.words('russian'))
    filtered_sentences = [w.lower() for w in word_tokens if w not in stop_words]
    return filtered_sentences


def write_words_into_file(words):
    with open("words_list.txt", "w", encoding="utf-8") as file:
        for elem in remove_stopwords(remove_secondary_marks(words)):
            file.write(elem + '\n')


# def lemitization():
#    # normal_forms = get_normal_form(words)
#    file = open("output.txt", "w", encoding="utf-8")
#    for word in remove_stopwords(normal_forms):
#        file.write(word + " ")


docs_words = []
with open("index.txt", "r") as index:
    lines = index.readlines()
    docs_numb = [line[: line.find(" ")] for line in lines]
    for elt in docs_numb:
        docs_words.extend(parse_words_from_html(f"{elt}.html"))

write_words_into_file(docs_words)
