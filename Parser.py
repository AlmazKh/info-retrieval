# для того чтобы работать с файлами на компьютере (с ОС)
import os

# библиотека scrapy и подкласс краулер для python
import scrapy
from scrapy.crawler import CrawlerProcess

# для работы с файлом типа xml
import xml.etree.ElementTree as ET


# определенная структура использования паука от scrapy
# в класс BlogSpide передается подкласс scrapy.Spider
# в классе определяются обязательные атрибуты (name, start_request() и parse())
class BlogSpider(scrapy.Spider):
    # идентифицируется паук. Уникальный в рамках проекта.
    name = 'spider'

    # устанавливает список запросов, из которых паук начнет работать
    def start_requests(self):
        # циклом for проходимся по всем url в файле index.xml
        for url in self.start_urls:
            # yield возвращает значения (список запросов с url, которые распрасены из index.xml)
            yield scrapy.Request(url=url, callback=self.parse)

    # метод, который вызван для обработки ответа, загруженного для каждого из запросов
    def parse(self, response, **kwargs):
        # url имеет вид https://habr.com/ru/news/t/542060/
        # в переменную page кладем 2й символ, то есть номер. Для каждой страницы он уникален.
        page = response.url.split("/")[-2]

        # генерируем имя файла, как "номер_старницы"
        file_name = f'{page}.html'

        # запись в переменную path_name пустого файла pages_html/habr-{page}.html через ОС
        file_name = f'{page}.html'
        path_name = os.path.join('pages_html', file_name)

        # запись в файл тела ответа (вся html страница)
        with open(path_name, 'wb') as f:
            f.write(response.body)

        # вывод сообщения, о том, что содержимое сохранено в файл
        self.log(f'Saved file {path_name}')


# метод, который возвращает массив url из xml файла
# файл index.xml создан по  по структуре тега <document>, у которого есть уникальный идентификатор id
# и тег <url>, в котором располагается url страницы
def parse_urls_xml(xml_file):
    # обращаемся к ElementTree, открывем соответсвующий xml файл
    doc = ET.parse(xml_file)

    # получаем корневой тег
    root = doc.getroot()

    # массив urls для записи в txt вид
    urls = []

    # открываем файл result.txt для записи
    with open("index.txt", "w") as result:
        # проходимся по всем элементам (документам) из index.xml
        for elt in root:
            # сохраняем url для дальнейшего парсинга страницы
            urls.append(elt[0].text)
            # записываем номер и url документа в файл index.txt
            result.write("{} {}\n".format(elt[0].text.split("/")[-2], elt[0].text))
        result.close()

    # возвращаем массив urls
    return urls


# в переменную pages_url записывем массив url-ов
pages_url = parse_urls_xml("index.xml")

# создание объекта процесса краулера (позволяет запуск нескольких краулеров одновременно)
process = CrawlerProcess()

# запуск краулера, сздание экземпляра подкласса Spider - BlogSpider
# и массив urls, для инициализации  паука
process.crawl(BlogSpider, start_urls=pages_url)

# запуск reactor, от twisted.internet.reactor (API интерфейс для потоковой передачи)
# и установка соединения
process.start()
