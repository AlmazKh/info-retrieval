import copy
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from Normalyzer import parse_words_from_html, MARKS, remove_stopwords, get_normal_form


def write_xml(terms, docs):
    top = Element('terms')
    # проходимся по словарям и ведем подсчет сколько раз, какое слово и в каком документе встретилось
    # записываем полученные результаты в terms.xml
    for term_key, term_forms in terms.items():
        child = SubElement(top, "term", dict({'value': str(term_key)}))
        for number, words in docs.items():
            count = 0
            for word in words:
                if word.lower() in term_forms:
                    count += 1
            if count > 0:
                SubElement(child, "doc", dict({'id': str(number), 'count': str(count)}))
    w = open("terms.xml", "w", encoding="utf-8")
    print(prettify(top), file=w)


# приводим terms.xml к красивому виду
def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def search(searching_word):
    terms = ElementTree.parse("terms.xml")
    root = terms.getroot()
    docs = []

    for term in root.findall('term'):
        if term.get('value') == searching_word:
            docs_count_for_term = dict()
            for doc in term:
                docs_count_for_term.update({doc.get('id'): doc.get('count')})
            docs.append(docs_count_for_term)
    return docs


def check_not(request):
    i = 0
    word_with_not = []
    for item in request:
        if item[0] == "-":
            word_with_not.append(i)
        i += 1
    return word_with_not


def not_operation(request, docs_array):
    i = 0
    copy_of_docs_array = copy.deepcopy(docs_array)
    for splited in request.split(' '):
        if str.startswith(splited, '-'):
            if copy_of_docs_array[i] is not None:
                list_id = dopolnenie_(copy_of_docs_array[i].keys())
                copy_of_docs_array[i].clear()
                for id in list_id:
                    copy_of_docs_array[i].update({id: 0})
        i += 1

    i = 0
    for splited in request.split(' '):
        if str.startswith(splited, '-'):
            if docs_array[i] is not None:
                dopolnenie = list(docs_array[i].keys())
                for elem in list(copy_of_docs_array):
                    if elem is not None:
                        for dop in list(dopolnenie):
                            elem.pop(dop, [])
        i += 1
    return copy_of_docs_array


def dopolnenie_(lst1):
    global docs_numb
    list_id = []
    for i in docs_numb:
        if i not in lst1:
            list_id.append(i)
    return list_id


def and_operation(docs_array_after_not):
    response = []
    count = dict()
    value = 0
    i = 0
    for elem in docs_array_after_not:
        if elem is not None:
            for it in elem.values():
                value += int(it)
            count.update({i: value})
            value = 0
        i += 1

    count = {k: v for k, v in sorted(count.items(), key=lambda it_: it_[1])}

    iter_count = iter(count)
    if docs_array_after_not[next(iter(count))] is not None:
        response = list(docs_array_after_not[next(iter(count))].keys())
    for item in iter_count:
        if docs_array_after_not[item] is not None:
            response = intersection(response, docs_array_after_not[item].keys())
    return response


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def sanitize(words):
    return str.replace(words, '-', '')


def request_processing(request):
    req_without_ = remove_stopwords(get_normal_form(sanitize(request)))
    docs_ = []

    for word in req_without_:
        searched = search(word)
        if len(searched) == 0:
            docs_ += [None]
        docs_ += search(word)
    return not_operation(request, docs_.copy())


# получаем словарь в виде номера документа и url страниц
# для выдачи подробного ответа пользователю
def get_doc_url():
    global url
    with open("index.txt", "r") as index:
        urls = {}
        for line in index.readlines():
            urls[line.split()[0]] = line.split()[1]
    return urls


def write_response(requests):
    top = Element('responses')
    docs_urls = get_doc_url()
    for req in requests:
        child_req = SubElement(top, "request", dict({'value': req}))
        response = and_operation(request_processing(req))
        for doc in response:
            u = docs_urls.get(doc)
            SubElement(child_req, "doc", dict({'id': str(doc), 'url': str(u)}))
    w = open("response.xml", "w", encoding="utf-8")
    print(prettify(top), file=w)


# восстанавливаем словарь формата -> начальная форма слова: [Формы, которые встречались ранее]
words_dict = {}
with open("output.txt", "r", encoding="utf-8") as file:
    for line in file.readlines():
        words_dict[line[:line.find(":")]] = line[line.find(":") + 1:].strip().split()

# собираем весь текст со страниц
docs_words = {}
with open("index.txt", "r") as index:
    lines = index.readlines()
    docs_numb = [line[: line.find(" ")] for line in lines]
    for elt in docs_numb:
        # создаем словарь формата -> номер документа: текст
        docs_words[elt] = ["".join(filter(lambda char: char not in MARKS, word)) for word in
                           parse_words_from_html(f"{elt}.html")]

# для генерации terms.xml
# write_xml(words_dict, docs_words)

# прописываем запросы в виде элементов списка
# знак "-" перед словом это дополнение (NOT)
requests = ["-разработчики открыть сервис", "лучше сиди дома",
            "обслуживающий по -улице заболеешь",
            "нашёл -уязвимость я тестировщик", "настройка системы",
            "-разработчики мозги дания хуан"]

# каждый запрос обрабатывается и прогоняется через алгоритм
# ответ записывается в файл response.xml
write_response(requests)
