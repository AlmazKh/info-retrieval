import math
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

import numpy as np

from Normalyzer import remove_stopwords, get_normal_form
from TermsGenerator import prettify, sanitize, get_doc_url

docs_numb = {}
with open("index.txt", "r") as index:
    lines = index.readlines()
    numb = [line[: line.find(" ")] for line in lines]
    for i in range(1, 101):
        docs_numb[numb[i-1]] = i


def create_matrix_and_query(req):
    terms = ElementTree.parse("terms_tf_idf.xml")
    root = terms.getroot()
    matrix = np.zeros((len(root.findall('term')), 101))
    y = 0
    q = np.zeros(len(root.findall('term')))
    for term in root.findall('term'):
        if term.get('value') in req:
            q[y] = 1
        else:
            q[y] = 0
        for doc in term:
            matrix[y][int(docs_numb[doc.get('id')])] = float(doc.get('tf-idf'))
        y += 1
    return matrix, q


def svd_matrix(matrix):
    return np.linalg.svd(matrix, full_matrices=False, compute_uv=True)


def refactor_matrix_with_k(U, S, V):
    k = 3
    Uk_ = U[:U.shape[0], :k]
    Sk = S[:k]
    Vk = V[:V.shape[0], :k]
    Vk_T_ = np.transpose(Vk)
    Sk_1_ = np.zeros((len(Sk), len(Sk)))
    for i in range(len(Sk)):
        Sk_1_[i][i] = 1.0 / Sk[i]
    return Uk_, Sk_1_, Vk_T_


def create_resp_with_sim(requests):
    top = Element('responses')
    table_with_sim = dict()
    for req in requests:
        clean_req = remove_stopwords(get_normal_form(sanitize(req)))
        matrix, q = create_matrix_and_query(clean_req)
        child = SubElement(top, "request", dict({'value': req}))
        U, S, V = svd_matrix(matrix)
        Uk, Sk_1, Vk_T = refactor_matrix_with_k(U, S, V)
        new_q = np.dot(q, Uk).dot(Sk_1)
        for i in range(100):
            score_first = 0
            multipl_q = 0
            multipl_d = 0
            sim = 0
            for j in range(len(new_q)):
                score_first += new_q[j] * Vk_T[j][i]
                multipl_q += pow(new_q[j], 2)
                multipl_d += pow(Vk_T[j][i], 2)
                sim = score_first / math.sqrt(multipl_q) / math.sqrt(multipl_d)
            table_with_sim.update({i + 1: sim})
        sorted_dict = {k: v for k, v in sorted(table_with_sim.items(), key=lambda it_: it_[1], reverse=True)}
        number = 1
        sorted_dict_iter = iter(sorted_dict)
        for el in sorted_dict_iter:
            if number > 10:
                break
            SubElement(child, "response",
                       dict({'number': str(number), 'sim': str(table_with_sim.get(el)),
                             'url': str(get_doc_url()[numb[el + 1]])}))
            number += 1

    w = open("svd_lsi.xml", "w", encoding="utf-8")
    print(prettify(top), file=w)


requests = ["разработчики", "сиди дома"]

create_resp_with_sim(requests)
