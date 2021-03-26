import math
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from Normalyzer import parse_words_from_html, remove_secondary_marks, remove_stopwords, remove_numbers_and_etc
from TermsGenerator import prettify

DOCS_NUMB = 100


def get_words_count_from_docs():
    docs_words_amount = {}
    with open("index.txt", "r") as index:
        lines = index.readlines()
        docs_numb = [line[: line.find(" ")] for line in lines]
        for elt in docs_numb:
            # создаем словарь формата -> номер документа: количество слов
            docs_words_amount[elt] = list(remove_numbers_and_etc(
                remove_stopwords(remove_secondary_marks(parse_words_from_html(f"{elt}.html"))))).__len__()
    return docs_words_amount


def compute_tf(in_doc, all_doc):
    return in_doc / float(all_doc)


def compute_idf(numb):
    return math.log10(DOCS_NUMB / float(numb))


def count_tf_idf():
    terms = ElementTree.parse("terms.xml")
    top = Element('terms_tf_idf')
    root = terms.getroot()
    docs_word_count = get_words_count_from_docs()
    for term in root.findall('term'):
        child = SubElement(top, "term", dict({'value': term.get('value')}))
        current_docs_count = 0
        for doc in term:
            current_docs_count += 1
        for doc in term:
            tf = round(compute_tf(float(doc.get('count')), docs_word_count[doc.get('id')]), 15)
            idf = round(compute_idf(current_docs_count), 15)
            tf_idf = tf * idf
            SubElement(child, "doc",
                       dict({'id': str(doc.get('id')), 'idf': str(idf), 'tf-idf': str(tf_idf)}))
    w = open("terms_tf_idf.xml", "w", encoding="utf-8")
    print(prettify(top), file=w)


count_tf_idf()
