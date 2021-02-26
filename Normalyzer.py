import codecs
import string

import pymorphy2
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords

# при первом запуске необходимо прогнать строки ниже для подгрузки необходимых модулей
# nltk.download('stopwords')
# nltk.download('punkt')

# список символов, которые удаются из текста
MARKS = [',', '.', ':', '?', '«', '»', '-', '(', ')', '!', '\'', "—", ';', "”", "...", "\'\'", "/**//**/",
         "“", "„", "–"]


# парсинг текста из html
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
    # находим токены для каждого слова
    tokens = word_tokenize(text)
    analyzer = pymorphy2.MorphAnalyzer()
    normalized_words = []
    for token in tokens:
        # пропускаем, если символ относится к знакам пунктуации
        if token in string.punctuation:
            continue
        # пропускаем, если символ относится к знакам из нашего списка выше
        if token in MARKS:
            continue
        # получаем одну из начальных форм слова
        normalized_words.append(analyzer.parse(token)[0].normal_form)
    return normalized_words


def remove_secondary_marks(words):
    # удаление знаков, которые являются элементами списка слов
    filtered_words = list(filter(lambda word: (word not in string.punctuation) and (word not in MARKS), words))
    result = []
    # удаление знаков, которые являются символами слов
    for word in filtered_words:
        result.append("".join(filter(lambda char: char not in MARKS, word)))
    return result


# удаление всех предлогов, союзов и тд
# перевод всех слов прошедших фильтрацию к нижнему регистру
def remove_stopwords(word_tokens):
    stop_words = set(stopwords.words('russian'))
    filtered_sentences = [w.lower() for w in word_tokens if w not in stop_words]
    return filtered_sentences


# удаление чисел, каких-то кривых составных слов из символов, букв и чисел - всего, что не является набором букв
def remove_numbers_and_etc(words):
    return filter(lambda word: word.isalpha(), words)


def write_words_into_file(words):
    with open("words_list.txt", "w", encoding="utf-8") as file:
        # записываем, удаляя предлоги, союз, знаки, числа и все непонятные символы
        for elem in remove_numbers_and_etc(remove_stopwords(remove_secondary_marks(words))):
            file.write(elem + '\n')


def lemitization():
    # считываем все слова из ранее полученного файла
    with open("words_list.txt", "r", encoding="utf-8") as lst:
        words = lst.readlines()
    # словарь, где ключ - начальная форма слова, а значение - список вариаций этого слова, которые встретились в данных
    lem_dict = {}
    for word in words:
        # получаем начальную форму слова
        normal_form = get_normal_form(word.strip())
        if normal_form:
            # если такое слово еще не встречалось,создаем ключ с нормальной формой и помещаем само слово как значение
            if normal_form[0] not in lem_dict.keys():
                lem_dict[normal_form[0]] = [word.strip()]
            # если такое слово встречалось ранее, добавляем его вариацию в список значений
            else:
                lem_dict[normal_form[0]].append(word.strip())

    # записываем полученные результаты в формате:
    # "начальная форма слова: токен токен ..."
    # знак ":" служит разделителем между ключом и значениями
    file = open("output.txt", "w", encoding="utf-8")
    for word, tokens in lem_dict.items():
        file.write(f"{word}:")
        [file.write(f" {tok}") for tok in set(tokens)]
        file.write("\n")
    file.close()


# для создания файла со списком слов (words_list.txt) нужно прогнать закомментированный код
# docs_words = []
# with open("index.txt", "r") as index:
#     lines = index.readlines()
#     docs_numb = [line[: line.find(" ")] for line in lines]
#     for elt in docs_numb:
#         docs_words.extend(parse_words_from_html(f"{elt}.html"))
# write_words_into_file(docs_words)
lemitization()
