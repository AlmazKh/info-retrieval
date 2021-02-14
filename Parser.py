import os
import scrapy
import xml.etree.ElementTree as ET
from scrapy.crawler import CrawlerProcess


class BlogSpider(scrapy.Spider):
    name = 'spider'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        page = response.url.split("/")[-2]
        file_name = f'habr-{page}.html'
        path_name = os.path.join('pages_html', file_name)
        with open(path_name, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {path_name}')


def parse_urls_xml(xml_file):
    doc = ET.parse(xml_file)
    root = doc.getroot()
    urls = []
    # открываем файл result.txt для записи
    with open("index.txt", "w") as result:
        # проходимся по всем элементам (документам) из index.xml
        for elt in root:
            # сохраняем url для дальнейшего парсинга страницы
            urls.append(elt[0].text)
            # записываем номер и url документа в файл index.txt
            result.write("{} {}\n".format(elt.get('id'), elt[0].text))
        result.close()
    return urls


pages_url = parse_urls_xml("index.xml")

process = CrawlerProcess()
process.crawl(BlogSpider, start_urls=pages_url)
process.start()
